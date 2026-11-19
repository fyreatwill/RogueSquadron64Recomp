#!/usr/bin/env python3
"""s7632 class DD second source: clang -ast-dump walk of the lib/rt64 hot files (same scope and row schema as
tools/s7632_dd_scan.py, independent extraction).

Rows: print / getenv / getenv-static / store / copy / call, each with gate ONCE | ENV | BUDGET | SIG | ALWAYS from the
ancestor IfStmt conditions (then-branch only), earlier `if (C) return;` siblings, and static-initialiser lambdas.
  env tokens   static / file VarDecls whose initialiser subtree calls getenv (fixpoint: or reads an env token),
               functions whose body calls getenv and spans <= 14 lines, locals initialised from either
  ENV          the condition reads an env token NOT directly under a logical-not '!' (and not `tok == 0`)
  BUDGET       the condition holds a ++ and a < / > comparison
  SIG          the condition holds `==` against an IntegerLiteral >= 1000
Reuses the streaming tree builder of tools/s7631_rp_ast.py.  Output JSON {tu, failed, rows}.  --plant FILE.cpp adds a control."""
import json, os, re, shlex, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7631_rp_ast as base

ROOT = base.ROOT
RT = base.RT
HOT = [os.path.join(RT, f) for f in ("hle/rt64_interpreter.cpp", "gbi/rt64_gbi_rdp.cpp", "hle/rt64_rdp.cpp", "hle/rt64_rdp_tmem.cpp")]
DIAGNAME = re.compile(r"^(?:g_|s_|k_)?(?:rs64|s\d{3,5}|S\d{4})|ring|hist|probe|diag|dump|trace", re.I)
PRINTF = {"rs64_diag_fprintf", "fprintf", "printf", "fputs", "puts", "fflush", "fwrite"}
FNK = base.FNK
EXTRA = []

def build_first(lines):
    """base.build, but a node's file:line is the FIRST location on its dump line (macro expansions such as the s7447
    `#define fprintf(...) rs64_diag_fprintf(...)` end in include/rs64_diag_route.h; their start is the call site)."""
    cur, cline, stack = None, 0, []
    for l in lines:
        m = re.match(r"^([| `-]*)(\w+)", l)
        if not m: continue
        depth = len(m.group(1)) // 2
        # clang elides the file when it equals the previously PRINTED one, so every loc updates `cur` in order; the node
        # takes its range begin, or for a Decl the name loc printed after the range (a `__forceinline` begin is a macro file)
        gt = l.find("> ")
        pick = None
        for x in base.LOC.finditer(l):
            if x.group(2): cur = x.group(1).rsplit(":", 2)[0]; ln_ = int(x.group(2))
            elif x.group(3): ln_ = int(x.group(3))
            else: ln_ = cline if pick is None else pick[1]
            if pick is None or (gt >= 0 and x.start() >= gt and "Decl" in l[:x.start()] and pick[2] < gt): pick = (cur, ln_, x.start())
            cline = ln_
        if pick is not None: nfile, nline = pick[0], pick[1]
        else: nfile, nline = cur, cline
        if depth == 0: continue
        n = base.Node(m.group(2), l[len(m.group(1)):], nfile, nline)
        if depth == 1:
            if stack: yield stack[0]
            stack = [n]; continue
        del stack[depth - 1:]
        if stack: stack[-1].kids.append(n)
        stack.append(n)
    if stack: yield stack[0]

def hot(f):
    f = os.path.normpath(f) if f else ""
    return f in HOT or f in EXTRA

def nm(t):
    m = re.search(r" (\w+) '", t); return m.group(1) if m else "?"

def ref(t):
    m = re.search(r"DeclRefExpr .*?(Var|ParmVar|Function|CXXMethod) (0x\w+) '(\w+)'", t)
    return (m.group(1), m.group(2), m.group(3)) if m else None

def lines_of(n):
    m = re.search(r"<([^<>]*)>", n.text)
    if not m: return None
    ends = re.findall(r"(?:line|\.\w+):(\d+):\d+", m.group(1))
    return (n.line, int(ends[-1]) if ends and m.group(1).count(",") else n.line)

def sub(n):
    stk = [n]
    while stk:
        x = stk.pop(); yield x; stk += x.kids

class TU:
    def __init__(s): s.rows, s.env, s.hotfns, s.nonlocal_, s.envfn = [], set(), set(), {}, set()

def calls_getenv(n):
    return any(x.kind == "DeclRefExpr" and re.search(r"Function 0x\w+ 'getenv'", x.text) for x in sub(n))

from s7632_dd_scan import EXTERN_ENV

def prepass(tops, tu):
    """env tokens and hot function names over the whole TU (top decls are yielded once; keep them)."""
    for top in tops:
        for x in sub(top):
            if x.kind in FNK and hot(x.file) and any(k.kind == "CompoundStmt" for k in x.kids):
                tu.hotfns.add(nm(x.text))
                body = [k for k in x.kids if k.kind == "CompoundStmt"][-1]
                lr = lines_of(body)
                if calls_getenv(body) and lr and lr[1] - lr[0] <= 14: tu.env.add(nm(x.text))
    for _ in range(3):
        for top in tops:
            for x in sub(top):
                if x.kind == "VarDecl" and x.kids:
                    st = re.search(r"\b(static|tls)\b", x.text) or x is top or (x.file and False)
                    if not st: continue
                    init = x.kids[-1]
                    if calls_getenv(init) or any((r := ref(y.text)) and r[2] in tu.env for y in sub(init) if y.kind == "DeclRefExpr"):
                        tu.env.add(nm(x.text))
    tu.env.discard("?"); tu.env |= EXTERN_ENV
    # default-ON toggles: a static whose initialiser lambda returns a logical-not ('!(e && *e == '0')', '!e || ..') at top level
    for top in tops:
        for x in sub(top):
            if x.kind == "VarDecl" and x.kids and re.search(r"\b(static|tls)\b", x.text) and calls_getenv(x.kids[-1]):
                for y in sub(x.kids[-1]):
                    if y.kind == "ReturnStmt" and y.kids:
                        z = y.kids[0]
                        while z.kind in ("ImplicitCastExpr", "ParenExpr", "ExprWithCleanups") and z.kids: z = z.kids[0]
                        if (z.kind == "UnaryOperator" and "'!'" in z.text) or (z.kind == "BinaryOperator" and z.text.rstrip().endswith("'||'")
                                and z.kids and z.kids[0].kind in ("UnaryOperator", "ImplicitCastExpr") and "'!'" in " ".join(k.text for k in sub(z.kids[0]))):
                            tu.env.discard(nm(x.text))

def cond_gate(conds, tu, lenv):
    env = tu.env | lenv
    g = []
    for c in conds:
        if c == "@ONCE": g.append("ONCE"); continue
        inv = isinstance(c, tuple)
        if inv: c = c[1]
        # walk with parent so polarity is visible
        pos, negs, budget_pp, budget_cmp, sig = False, False, False, False, False
        stk = [(c, None)]
        while stk:
            x, par = stk.pop()
            if x.kind == "DeclRefExpr":
                r = ref(x.text)
                if r and (r[2] in env or r[2] == "getenv"):
                    p = par
                    neg = False
                    # climb through implicit casts / call wrappers recorded in the parent chain
                    if p is not None and p[0].kind == "UnaryOperator" and "'!'" in p[0].text: neg = True
                    if p is not None and p[0].kind == "BinaryOperator" and "'=='" in p[0].text and \
                       any(k.kind == "IntegerLiteral" and re.search(r" 0$", k.text.rstrip()) for k in sub(p[0])): neg = True
                    if not neg: pos = True
                    else: negs = True
            if x.kind == "UnaryOperator" and ("'++'" in x.text): budget_pp = True
            if x.kind == "BinaryOperator" and re.search(r"'(<|>|<=|>=)'$", x.text.rstrip()): budget_cmp = True
            if x.kind == "BinaryOperator" and x.text.rstrip().endswith("'=='"):
                for k in sub(x):
                    if k.kind == "IntegerLiteral":
                        m = re.search(r" (\d+)$", k.text.rstrip())
                        if m and int(m.group(1)) >= 1000: sig = True
            # parent pointer skips transparent wrappers so `!f()` / `!(x)` keep the '!' as parent
            if x.kind in ("ImplicitCastExpr", "ParenExpr", "CallExpr", "CXXMemberCallExpr", "ExprWithCleanups") and par is not None:
                np = par
            else:
                np = (x,)
            for k in x.kids: stk.append((k, np))
        if inv:  # early-return guard: following code runs when the condition is false -> gated iff it reads !tok
            if negs: g.append("ENV")
            elif budget_pp and budget_cmp: g.append("BUDGET")
            continue
        if pos: g.append("ENV")
        elif budget_pp and budget_cmp: g.append("BUDGET")
        elif sig: g.append("SIG")
    for k in ("ONCE", "ENV", "BUDGET", "SIG"):
        if k in g: return k
    return "ALWAYS"

def is_return_only(n):
    if n.kind == "ReturnStmt": return True
    return n.kind == "CompoundStmt" and len(n.kids) == 1 and n.kids[0].kind == "ReturnStmt"

def if_parts(n):
    k = [c for c in n.kids if c.kind not in ("FullComment",)]
    if "has_else" in n.text and len(k) >= 3: return k[-3], k[-2], k[-1]
    if len(k) >= 2: return k[-2], k[-1], None
    return None, None, None

def scan_fn(fnode, tu, fname):
    locals_, lenv = set(), set()
    def base_var(x):
        while True:
            if x.kind in ("ImplicitCastExpr", "ParenExpr", "CXXOperatorCallExpr") and x.kids:
                x = x.kids[0] if x.kind != "CXXOperatorCallExpr" else (x.kids[1] if len(x.kids) > 1 else x.kids[0]); continue
            if x.kind in ("MemberExpr", "ArraySubscriptExpr", "UnaryOperator") and x.kids: x = x.kids[0]; continue
            break
        if x.kind == "DeclRefExpr":
            r = ref(x.text)
            if r and r[0] == "Var" and r[1] not in locals_: return r[2]
        return None
    def emit(n, kind, name, conds):
        if n.file and hot(n.file):
            lab = "PLANT/" + os.path.basename(n.file) if os.path.normpath(n.file) in EXTRA else os.path.relpath(os.path.normpath(n.file), ROOT)
            tu.rows.append(dict(file=lab, line=n.line, fn=fname, kind=kind, name=name, gate=cond_gate(conds, tu, lenv)))
    def walk(n, conds, in_static_init):
        k = n.kind
        if k == "CXXRecordDecl": return  # lambda closure class: its operator() body is walked via the LambdaExpr
        if k == "ParmVarDecl": locals_.add(base.addr(n.text))
        if k == "VarDecl":
            st = re.search(r"\b(static|tls)\b", n.text)
            if not st:
                locals_.add(base.addr(n.text))
                if n.kids and (calls_getenv(n.kids[-1]) or any((r := ref(y.text)) and r[2] in tu.env for y in sub(n.kids[-1]) if y.kind == "DeclRefExpr")):
                    lenv.add(nm(n.text))
                if "&" in (re.search(r"'([^']*)'", n.text).group(1) if re.search(r"'([^']*)'", n.text) else "") and n.kids:
                    b = base_var(n.kids[-1])
                    if b and DIAGNAME.search(b) and any(y.kind == "ArraySubscriptExpr" for y in sub(n.kids[-1])): emit(n, "store", b, conds)
            if st and n.kids:
                init = n.kids[-1]
                c2 = conds + ["@ONCE"] if any(y.kind == "LambdaExpr" for y in sub(init)) else conds
                for y in sub(init):
                    if y.kind == "CallExpr" and y.kids and calls_getenv(y.kids[0]) and c2 is conds:
                        emit(y, "getenv-static", "getenv", conds)
                for c in n.kids: walk(c, c2, True)
                return
        if k == "IfStmt":
            c, t, e = if_parts(n)
            if c is not None:
                walk(c, conds, in_static_init)
                walk(t, conds + [c], in_static_init)
                if e is not None: walk(e, conds, in_static_init)
                pre = [x for x in n.kids if x not in (c, t, e)]
                for x in pre: walk(x, conds, in_static_init)
                return
        if k == "CompoundStmt":
            g = []
            for ch in n.kids:
                walk(ch, conds + g, in_static_init)
                if ch.kind == "IfStmt" and "has_else" not in ch.text:
                    c, t, _ = if_parts(ch)
                    if t is not None and is_return_only(t): g.append(("NOT", c))
            return
        if k == "CallExpr" and n.kids:
            r = None
            for y in sub(n.kids[0]):
                if y.kind == "DeclRefExpr": r = ref(y.text); break
                if y.kind == "UnresolvedLookupExpr":  # dependent call inside a template pattern
                    mu = re.search(r"= '(\w+)'", y.text)
                    if mu: r = ("Function", "0", mu.group(1)); break
            if r and r[0] in ("Function", "CXXMethod"):
                if r[2] in PRINTF: emit(n, "print", r[2], conds)
                elif r[2] == "getenv":
                    if not in_static_init or "@ONCE" in conds: emit(n, "getenv", "getenv", conds)
                elif r[2] in ("memcpy", "memmove") and len(n.kids) > 1:
                    b = base_var(n.kids[1])
                    if b and DIAGNAME.search(b): emit(n, "copy", b, conds)
                elif r[2] != fname: emit(n, "call", r[2], conds)  # census keeps callees that own rows
        if k == "CXXMemberCallExpr" and n.kids:
            m = re.search(r"MemberExpr .*[.>](assign|swap|push_back|emplace_back|insert|resize) 0x", n.kids[0].text)
            if m and n.kids[0].kids:
                b = base_var(n.kids[0].kids[0])
                if b and DIAGNAME.search(b): emit(n, "copy", b, conds)
            mm = re.search(r"MemberExpr .*[.>](\w+) 0x", n.kids[0].text)
            if mm and not m and mm.group(1) != fname: emit(n, "call", mm.group(1), conds)
        if (k == "BinaryOperator" and n.text.rstrip().endswith("'='")) or k == "CompoundAssignOperator" or \
           (k == "UnaryOperator" and re.search(r"'(\+\+|--)'", n.text)):
            if n.kids:
                b = base_var(n.kids[0])
                if b and DIAGNAME.search(b): emit(n, "store", b, conds)
        for ch in n.kids: walk(ch, conds, in_static_init)
    body = [k for k in fnode.kids if k.kind == "CompoundStmt"]
    for p in fnode.kids:
        if p.kind == "ParmVarDecl": locals_.add(base.addr(p.text))
    if body: walk(body[-1], [], False)

def run_one(e):
    if isinstance(e, str): a, cwd = ["clang++", "-std=c++17", e], os.path.dirname(e)
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
    tops = [t for t in build_first(p.stdout) if not (t.file and t.file.startswith(base.SYS))]
    rc = p.wait()
    tu = TU(); prepass(tops, tu)
    def outer(n):  # outermost function bodies only: lambda operator() / local-class methods stay with their parent
        if n.kind in FNK:
            if hot(n.file) and any(k.kind == "CompoundStmt" for k in n.kids): scan_fn(n, tu, nm(n.text))
            return
        for k in n.kids: outer(k)
    for top in tops: outer(top)
    return (e if isinstance(e, str) else e["file"]), rc, tu.rows, sorted(tu.env)

def main():
    a = sys.argv[1:]
    if "--hot" in a:  # same option as tools/s7632_dd_scan.py
        HOT[:] = [os.path.normpath(os.path.join(ROOT, f)) for f in a[a.index("--hot") + 1].split(",")]
    d = json.load(open(os.path.join(ROOT, "build/compile_commands.json")))
    ents, seen = [], set()
    for e in d:
        f = os.path.normpath(os.path.join(e["directory"], e["file"]))
        if f in HOT and f not in seen: seen.add(f); ents.append(e)
    if "--plant" in a:
        pf = os.path.abspath(a[a.index("--plant") + 1]); EXTRA.append(os.path.normpath(pf)); ents.append(pf)
    rows, fails, envs = [], [], set()
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(5) as ex:
        for f, rc, r, en in ex.map(run_one, ents):
            if rc != 0: fails.append(f)
            rows += r; envs |= set(en)
    ded = {(r["file"], r["line"], r["kind"], r["name"]): r for r in rows}
    rows = sorted(ded.values(), key=lambda r: (r["file"], r["line"], r["kind"]))
    sys.stderr.write("tu=%d failed=%d envtok=%d rows=%d\n" % (len(ents), len(fails), len(envs), len(rows)))
    o = a[a.index("--out") + 1] if "--out" in a else None
    s = json.dumps(dict(tu=len(ents), failed=fails, envtok=sorted(envs), rows=rows), indent=0)
    (open(o, "w").write(s) if o else sys.stdout.write(s))

if __name__ == "__main__":
    main()
