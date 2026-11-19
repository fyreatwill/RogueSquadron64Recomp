#!/usr/bin/env python3
"""s7631 class RP first source (regex): RDRAM-derived pointer stores in lib/rt64/src (minus contrib / imgui / tools).

Per function body (a `{` preceded by `)` + qualifiers, not if/for/while/switch/catch), statements are split on ';'.
Taint tokens: fromRDRAM( / getRDRAM( / &RDRAM[ / &memory[ / &rdram[ / RDRAM + / memory + / rdram + / a bare RDRAM /
rdram RHS, *dl / dl (DisplayList pointers), and any local whose initialiser is tainted (one function, in order).
Each tainted store whose LHS is not a plain function local becomes a row:
  member (x.f / p->f / this->f / bare identifier not declared in the function), global (static / thread_local decl in a
  function, or a file-scope initialiser), deref (*p = ...), array (a[i] = ... on a non-local), push (.push_back( etc. on a
  non-local with a tainted argument), return (info).
Output JSON {files, rows:[{file,line,kind,name}]}.  --plant FILE adds a control file."""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT = os.path.join(ROOT, "lib/rt64/src")
TAINT = re.compile(r"\b(?:fromRDRAM|getRDRAM)\s*\(|&\s*(?:\w+(?:->|\.))*(?:RDRAM|memory|rdram)\s*\[|"
                   r"\b(?:RDRAM|memory|rdram)\s*\+|^\s*(?:\([^()]*\)\s*)?(?:(?:\w+(?:->|\.))*)(?:RDRAM|rdram)\s*$")
PUSH = re.compile(r"^(.*?)(?:\.|->)(push_back|emplace_back|insert|push|emplace|assign)\s*\((.*)\)\s*$", re.S)
CTRL = {"if", "for", "while", "switch", "catch", "return", "sizeof", "else", "do"}
PTRDECL = re.compile(r"(?:^|[,(])\s*(?:const\s+)?(?:struct\s+)?[\w:]+(?:<[^;{}]*?>)?\s*(?:const\s*)?(\*+|&)\s*(?:const\s+)?(\w+)\s*(?=[=;,)\[{]|$)")
DECL = re.compile(r"^\s*(?:(static|thread_local)\s+)?(?:constexpr\s+)?(?:const\s+)?(?:volatile\s+)?(?:struct\s+)?"
                  r"(?:auto|[\w:]+(?:<[^;{}]*?>)?)(?:\s+|\s*(?:const\s*)?[*&]+\s*)(?:const\s+)?(\w+)\s*(?:\[[^\]]*\])?\s*(?:=|\{)(.*)$", re.S)

PN = re.compile(r"(?m)(?:^|[;{(,])\s*(?:(?:const|static|thread_local|volatile|struct|extern|inline|mutable)\s+)*"
                r"[\w:]+(?:<[^;{}]*?>)?\s*(?:const\s*)?\*+\s*(?:const\s+)?(\w+)\s*(?=[=;,\[{)])")

def clean(t):
    t = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), t, flags=re.S)
    t = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', t)
    t = re.sub(r"'(?:\\.|[^'\\\n])'", "''", t)
    t = re.sub(r"//[^\n]*", "", t)
    t = re.sub(r"^[ \t]*#[^\n]*(?:\\\n[^\n]*)*", lambda m: "\n" * m.group(0).count("\n"), t, flags=re.M)
    return t

def match_brace(t, i):
    d = 0
    for j in range(i, len(t)):
        if t[j] == "{": d += 1
        elif t[j] == "}":
            d -= 1
            if d == 0: return j
    return len(t) - 1

def functions(t):
    """(param_text, body_start, body_end) for every outermost function / method / lambda body."""
    out, i = [], 0
    pat = re.compile(r"\)\s*(?:const\s*)?(?:override\s*)?(?:noexcept\s*)?(?:->\s*[\w:<>*&\s]+?)?\s*(?::[^;{]*?)?\{")
    while True:
        m = pat.search(t, i)
        if not m: break
        # find the matching '(' and the word before it
        j, d = m.start(), 0
        while j >= 0:
            if t[j] == ")": d += 1
            elif t[j] == "(":
                d -= 1
                if d == 0: break
            j -= 1
        w = re.search(r"(\w+)\s*$", t[:j])
        if w and w.group(1) in CTRL or ":" in t[m.start():m.end()] and "::" not in t[m.start():m.end()] and False:
            i = m.end(); continue
        b = m.end() - 1
        e = match_brace(t, b)
        out.append((t[j:m.start() + 1], b, e))
        i = e + 1
    return out

def stmts(body, off):
    start, d, s0 = off, 0, 0
    for k, ch in enumerate(body):
        if ch in "{};" and d == 0:
            cur = body[s0:k]
            if cur.strip(): yield start, cur
            start, s0 = off + k + 1, k + 1
            continue
        if ch == "(": d += 1
        elif ch == ")": d = max(0, d - 1)

def tainted(expr, locals_t):
    if TAINT.search(expr): return True
    if re.search(r"\bDisplayList\s*\*", expr) and not re.search(r"pendingCommand", expr): return True
    return any(re.search(r"\b%s\b" % re.escape(v), expr) for v in locals_t)

def scan_file(path, label, rows):
    raw = open(path, errors="replace").read()
    t = clean(raw)
    import bisect
    nl = [k for k, ch in enumerate(t) if ch == "\n"]
    line = lambda pos: bisect.bisect_left(nl, pos) + 1
    fns = functions(t)
    for params, b, e in fns:
        body = t[b + 1:e]
        decl = set(x[1] for x in PTRDECL.findall(params))
        decl |= set(re.findall(r"\b(\w+)\s*(?:,\s*\w+\s*)?\)?\s*$", params)) if False else set()
        for w in re.findall(r"(\w+)\s*(?=[,)=])", params): decl.add(w)
        locals_t = set(x for x in decl if re.search(r"\bDisplayList\s*\*+\s*&?\s*%s\b" % x, params) or x in ("RDRAM", "memory", "rdram"))
        for pos, s in stmts(body, b + 1):
            s2 = s.strip()
            if not s2: continue
            for lam in re.finditer(r"\[[^\]]*\]\s*\(([^)]*)\)", s2):  # lambda params are locals
                for w in re.findall(r"(\w+)\s*(?=[,)]|$)", lam.group(1)): decl.add(w)
            st_pos = pos + (len(s) - len(s.lstrip()))
            ln = line(st_pos)
            if re.match(r"return\b", s2):
                ex = s2[6:]
                if ex.strip() and tainted(ex, locals_t) and not re.match(r"^\s*(nullptr|0|NULL|true|false)\s*$", ex):
                    rows.append(dict(file=label, line=ln, kind="return", name=s2[:60]))
                continue
            dm = re.match(r"^(?:(?:static|thread_local|const|volatile|struct)\s+)*[\w:]+(?:<[^;{}]*?>)?(?:\s+|\s*[*&]+\s*)(\w+)\s*(?:\[[^\]]*\])?\s*$", s2)
            if dm and dm.group(1) not in CTRL:
                decl.add(dm.group(1)); continue
            m = DECL.match(s2)
            if m and "==" not in s2.split("=", 1)[0] + "=" and not re.match(r"^\s*(?:\w+(?:->|\.))", s2):
                stc, nm, rhs = m.group(1), m.group(2), m.group(3)
                if nm in CTRL or nm in ("delete", "new"):
                    pass
                else:
                    decl.add(nm)
                    if tainted(rhs, locals_t) and not re.match(r"^\s*(nullptr|0|NULL)\s*\}?\s*$", rhs):
                        if stc and "*" in s2.split(nm, 1)[0]: rows.append(dict(file=label, line=ln, kind="global", name=nm))
                        elif "*" in s2.split(nm, 1)[0] or re.match(r"^\s*(const\s+)?auto\b", s2): locals_t.add(nm)
                    continue
            pm = PUSH.match(s2)
            if pm:
                obj = pm.group(1).strip()
                base = re.match(r"^(?:this->)?(\w+)", obj)
                if tainted(pm.group(3), locals_t) and not (base and base.group(1) in decl and "->" not in obj and "." not in obj):
                    rows.append(dict(file=label, line=ln, kind="push", name=re.split(r"->|\.", obj)[-1]))
                continue
            am = re.match(r"^(.*?[^=!<>+\-*/%&|^])=(?!=)(.*)$", s2, re.S)
            if not am: continue
            lhs, rhs = am.group(1).strip(), am.group(2)
            if not tainted(rhs, locals_t) or re.match(r"^\s*(nullptr|0|NULL)\s*$", rhs): continue
            if re.match(r"^\s*\w+\s*\[[^\]]*\]\s*$", rhs): continue  # element read = scalar copy, not a pointer
            if not (TAINT.search(rhs) or re.search(r"\*|\bDisplayList\b", rhs)) \
               and not any(re.search(r"\b%s\b" % re.escape(v), rhs) for v in locals_t):
                continue
            if lhs.startswith("*"):
                rows.append(dict(file=label, line=ln, kind="deref", name=lhs.lstrip("*( ").split(")")[0].strip())); continue
            if re.search(r"->|\.", lhs):
                rows.append(dict(file=label, line=ln, kind="member", name=re.split(r"->|\.", lhs)[-1].strip())); continue
            am2 = re.match(r"^(\w+)\s*\[", lhs)
            if am2:
                if am2.group(1) not in decl: rows.append(dict(file=label, line=ln, kind="array", name=am2.group(1)))
                continue
            if re.match(r"^\w+$", lhs):
                if lhs in decl: locals_t.add(lhs)
                else: rows.append(dict(file=label, line=ln, kind="member", name=lhs))
    # file-scope initialisers outside every function body
    mask = list(t)
    for _, b, e in fns:
        for k in range(b, e + 1): mask[k] = ";" if mask[k] != "\n" else "\n"
    ft = "".join(mask)
    for m in re.finditer(r"[^;{}]*?(\*+)\s*(\w+)\s*=\s*([^;{}]+);", ft):
        if tainted(m.group(3), set()) and not re.match(r"^\s*(nullptr|0|NULL)\s*$", m.group(3)):
            rows.append(dict(file=label, line=line(m.start(2)), kind="global", name=m.group(2)))

def main():
    a = sys.argv[1:]
    files = sorted(f for f in glob.glob(RT + "/**/*", recursive=True)
                   if f.endswith((".cpp", ".h", ".mm")) and not re.match(r"(contrib|imgui|tools)/", os.path.relpath(f, RT)))
    rows = []
    for f in files: scan_file(f, os.path.relpath(f, ROOT), rows)
    if "--plant" in a:
        pf = a[a.index("--plant") + 1]; scan_file(pf, "PLANT/" + os.path.basename(pf), rows)
    # pointer-typed names: a member / global / array row survives only when its name is declared pointer-typed somewhere
    # in scope (scalar copies of guest words, e.g. leftOrigin = (*dl)->p0(..), are not pointer stores)
    pn = set()
    for f in files:
        t = clean(open(f, errors="replace").read())
        pn |= set(PN.findall(t)) | set(re.findall(r",\s*\*+\s*(\w+)", t))
        pn |= set(re.findall(r"\b(?:std::)?(?:vector|deque|array|list)<[^;{}<>]*\*\s*(?:,[^;{}<>]*)?>\s*(\w+)", t))
    if "--plant" in a:
        pt = clean(open(pf).read()); pn |= set(PN.findall(pt)) | set(re.findall(r",\s*\*+\s*(\w+)", pt))
    rows = [r for r in rows if r["kind"] not in ("member", "global", "array") or r["name"] in pn]
    ded = {(r["file"], r["line"], r["kind"], r["name"]): r for r in rows}
    rows = sorted(ded.values(), key=lambda r: (r["file"], r["line"]))
    sys.stderr.write("files=%d rows=%d\n" % (len(files), len(rows)))
    o = a[a.index("--out") + 1] if "--out" in a else None
    s = json.dumps(dict(files=len(files), rows=rows), indent=0)
    (open(o, "w").write(s) if o else sys.stdout.write(s))

if __name__ == "__main__":
    main()
