#!/usr/bin/env python3
"""s7631 class RP second source: clang -ast-dump taint scan of lib/rt64/src (minus contrib / imgui / tools).

A value is RDRAM-tainted when its expression subtree contains: a MemberExpr / DeclRefExpr named RDRAM / rdram / memory
(the State::RDRAM base, the processDisplayLists `memory` param), a call of fromRDRAM() / getRDRAM(), any node whose type
is `DisplayList *` (every DisplayList* in rt64 is derived from &memory[dlStart] or fromRDRAM, except the pending-command
buffer, which the census classifies), or a DeclRefExpr to a LOCAL VarDecl already tainted (tracked by decl address).
A STORE row is emitted when a tainted value is written somewhere that can outlive the call:
  member   BinaryOperator '=' whose LHS is a MemberExpr, or a CXXCtorInitializer of a field
  global   '=' / init of a VarDecl with static / tls / file storage
  deref    '=' whose LHS is UnaryOperator '*' (caller-owned slot, e.g. `*dl = ...`)
  array    '=' whose LHS is an ArraySubscriptExpr on a non-local
  push     push_back / emplace_back / insert / push / emplace / assign on a non-local container (member or static)
  return   ReturnStmt of a tainted value (info row: the caller decides where it lives)
Output JSON {tu, failed, rows:[{file,line,kind,name,fn}]}.  --plant FILE.cpp adds a self-contained control TU."""
import json, os, re, shlex, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT = os.path.join(ROOT, "lib/rt64/src")
LOC = re.compile(r"(?:<|, |> )((?:/[^:<>,]+?):(\d+):\d+|line:(\d+):\d+|col:\d+)")
FNK = ("FunctionDecl", "CXXMethodDecl", "CXXConstructorDecl", "CXXDestructorDecl", "CXXConversionDecl")
BASE = re.compile(r"(?:MemberExpr .*[.>](RDRAM|rdram)\b|DeclRefExpr .*(?:Var|ParmVar) 0x\w+ '(RDRAM|rdram|memory)' )")
CALL = re.compile(r"MemberExpr .*[.>](fromRDRAM|getRDRAM) 0x")
DLT = re.compile(r"'(?:const )?(?:RT64::)?DisplayList \*")
PUSH = re.compile(r"MemberExpr .*[.>](push_back|emplace_back|insert|push|emplace|assign) 0x")
EXTRA = []

def in_scope(f):
    f = os.path.normpath(f)
    if f in EXTRA: return True
    if not f.startswith(RT + "/"): return False
    r = os.path.relpath(f, RT)
    return not re.match(r"(contrib|imgui|tools)/", r)

class Node:
    __slots__ = ("kind", "text", "kids", "file", "line")
    def __init__(s, kind, text, file, line):
        s.kind, s.text, s.kids, s.file, s.line = kind, text, [], file, line

def build(lines):
    """stream clang text dump -> top-level decls (children of TranslationUnitDecl), yielded one by one."""
    cur, cline, stack = None, 0, []
    for l in lines:
        m = re.match(r"^([| `-]*)(\w+)", l)
        if not m: continue
        depth = len(m.group(1)) // 2
        for x in LOC.finditer(l):
            if x.group(2): cur = x.group(1).rsplit(":", 2)[0]; cline = int(x.group(2))
            elif x.group(3): cline = int(x.group(3))
        if depth == 0: continue
        n = Node(m.group(2), l[len(m.group(1)):], cur, cline)
        if depth == 1:
            if stack: yield stack[0]
            stack = [n]; continue
        del stack[depth - 1:]
        if stack: stack[-1].kids.append(n)
        stack.append(n)
    if stack: yield stack[0]

SYS = ("/Applications/", "/Library/", "/usr/", "/opt/")

def addr(t):
    m = re.match(r"\w+ (0x[0-9a-f]+)", t); return m.group(1) if m else None

def scan_tree(root, rows):
    local_vars, tainted, static_vars = set(), set(), set()

    def is_t(n):
        stk = [n]
        while stk:
            x = stk.pop()
            if BASE.search(x.text) or CALL.search(x.text): return True
            if x.kind not in ("CStyleCastExpr", "CXXReinterpretCastExpr", "ImplicitCastExpr") and DLT.search(x.text) \
               and x.kind not in ("CXXNullPtrLiteralExpr", "IntegerLiteral", "GNUNullExpr") and "nullptr" not in x.text:
                return True
            m = re.search(r"DeclRefExpr .*Var (0x\w+) '", x.text)
            if m and m.group(1) in tainted: return True
            stk += x.kids
        return False

    def nulls(n):  # nullptr / 0 stores do not carry a value
        x = n
        while x.kind in ("ImplicitCastExpr", "CStyleCastExpr", "ParenExpr") and x.kids: x = x.kids[0]
        return x.kind in ("CXXNullPtrLiteralExpr", "GNUNullExpr", "IntegerLiteral")

    def lhs_kind(n):
        x = n
        while x.kind in ("ImplicitCastExpr", "ParenExpr") and x.kids: x = x.kids[0]
        if x.kind == "MemberExpr":
            m = re.search(r"[.>](\w+) 0x", x.text); return "member", m.group(1) if m else "?"
        if x.kind == "UnaryOperator" and "'*'" in x.text:
            inner = name_of(x); return "deref", inner
        if x.kind == "ArraySubscriptExpr":
            base = x.kids[0] if x.kids else x
            k, nm = lhs_kind(base)
            return ("array", nm) if k != "local" else ("local", nm)
        if x.kind == "DeclRefExpr":
            m = re.search(r"Var (0x\w+) '(\w+)'", x.text)
            if m:
                if m.group(1) in local_vars: return "local", m.group(1)
                return "global", m.group(2)
        return "other", x.kind

    def name_of(n):
        stk = [n]
        while stk:
            x = stk.pop(0)
            m = re.search(r"(?:Var|ParmVar) 0x\w+ '(\w+)'", x.text) or re.search(r"MemberExpr .*[.>](\w+) 0x", x.text)
            if m: return m.group(1)
            stk += x.kids
        return "?"

    def ptr(n):  # first quoted type on the node line is the expression type
        m = re.search(r"'([^']*)'(?::'([^']*)')?", n.text)
        ty = (m.group(1) + " " + (m.group(2) or "")) if m else ""
        return bool("*" in ty or re.search(r"\bu?intptr_t\b", ty))

    def emit(n, kind, name, fn):
        if n.file and in_scope(n.file):
            rows.append(dict(file=os.path.relpath(os.path.normpath(n.file), ROOT) if not os.path.normpath(n.file) in EXTRA
                             else "PLANT/" + os.path.basename(n.file), line=n.line, kind=kind, name=name, fn=fn))

    def walk(n, fn, infn):
        k = n.kind
        if k in FNK:
            m = re.search(r" (\w+) '", n.text); fn = m.group(1) if m else "?"; infn = True
        if k == "LambdaExpr": infn = True
        if k == "ParmVarDecl": local_vars.add(addr(n.text))
        if k == "VarDecl":
            a = addr(n.text)
            st = re.search(r"\b(static|tls)\b", n.text) or not infn
            m = re.search(r" (\w+) '([^']*)'", n.text); nm = m.group(1) if m else "?"
            init = [c for c in n.kids if c.kind not in ("FullComment",)]
            if st:
                static_vars.add(a)
                if init and is_t(init[-1]) and not nulls(init[-1]) and "*" in (m.group(2) if m else ""):
                    emit(n, "global", nm, fn)
            else:
                local_vars.add(a)
                if init and is_t(init[-1]): tainted.add(a)
        elif k == "BinaryOperator" and n.text.rstrip().endswith("'='") and len(n.kids) == 2:
            lk, nm = lhs_kind(n.kids[0])
            if ptr(n) and is_t(n.kids[1]) and not nulls(n.kids[1]):
                if lk == "local": tainted.add(nm)
                elif lk != "other" or True:
                    emit(n, lk, nm, fn)
        elif k == "CXXCtorInitializer" and n.kids:
            m = re.search(r"Field 0x\w+ '(\w+)'", n.text)
            if m and ptr(n.kids[-1]) and is_t(n.kids[-1]) and not nulls(n.kids[-1]): emit(n, "member", m.group(1), fn)
        elif k == "CXXMemberCallExpr" and n.kids and PUSH.search(n.kids[0].text):
            obj = n.kids[0].kids[0] if n.kids[0].kids else None
            lk, nm = lhs_kind(obj) if obj else ("other", "?")
            if lk != "local" and any(ptr(a) and is_t(a) for a in n.kids[1:]): emit(n, "push", nm, fn)
        elif k == "ReturnStmt" and n.kids and infn:
            if ptr(n.kids[0]) and is_t(n.kids[0]) and not nulls(n.kids[0]): emit(n, "return", fn, fn)
        for c in n.kids: walk(c, fn, infn)

    fnret = {}
    walk(root, None, False)

def run_one(e):
    if isinstance(e, str):
        a = ["clang++", "-std=c++17", e]
        cwd = os.path.dirname(e)
    else:
        args = e.get("arguments") or shlex.split(e["command"])
        a, skip = [], False
        for x in args:
            if skip: skip = False; continue
            if x == "-o": skip = True; continue
            if x == "-c": continue
            a.append(x)
        cwd = e["directory"]
    a += ["-fsyntax-only", "-Xclang", "-ast-dump", "-fno-color-diagnostics", "-w"]
    p = subprocess.Popen(a, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, errors="replace")
    rows = []
    for top in build(p.stdout):
        if top.file and top.file.startswith(SYS): continue
        scan_tree(top, rows)
    rc = p.wait()
    return (e if isinstance(e, str) else e["file"]), rc, rows

def iter_files(n):
    stk = [n]
    seen = 0
    while stk and seen < 4000:
        x = stk.pop(); seen += 1
        if x.file: yield x.file
        stk += x.kids

def main():
    a = sys.argv[1:]
    d = json.load(open(os.path.join(ROOT, "build/compile_commands.json")))
    seen, ents = set(), []
    for e in d:
        f = os.path.normpath(os.path.join(e["directory"], e["file"]))
        if in_scope(f) and f not in seen and f.endswith((".cpp", ".mm")):
            seen.add(f); ents.append(e)
    if "--only" in a:
        k = a[a.index("--only") + 1]; ents = [e for e in ents if k in e["file"]]
    if "--plant" in a:
        pf = os.path.abspath(a[a.index("--plant") + 1]); EXTRA.append(os.path.normpath(pf)); ents.append(pf)
    rows, fails = [], []
    with ThreadPoolExecutor(int(os.environ.get("J", "6"))) as ex:
        for f, rc, r in ex.map(run_one, ents):
            if rc != 0: fails.append(os.path.relpath(f, ROOT) if not isinstance(f, str) or f.startswith("/") else f)
            rows += r
    ded = {(r["file"], r["line"], r["kind"], r["name"]): r for r in rows}
    rows = sorted(ded.values(), key=lambda r: (r["file"], r["line"], r["kind"], r["name"]))
    sys.stderr.write("tu=%d failed=%d rows=%d\n" % (len(ents), len(fails), len(rows)))
    o = a[a.index("--out") + 1] if "--out" in a else None
    s = json.dumps(dict(tu=len(ents), failed=fails, rows=rows), indent=0)
    (open(o, "w").write(s) if o else sys.stdout.write(s))

if __name__ == "__main__":
    main()
