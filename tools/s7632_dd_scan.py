#!/usr/bin/env python3
"""s7632 class DD first source (regex): diagnostic work in lib/rt64 per-list / per-command hot paths.

Hot files (everything reached per RDP list or per RDP command on the default LLE path):
  hle/rt64_interpreter.cpp (processRDPLists + helpers; processDisplayLists is HLE-only, the census marks it),
  gbi/rt64_gbi_rdp.cpp (the rdpGBI handlers), hle/rt64_rdp.cpp (RDP::setColorImage/loadTile/...), hle/rt64_rdp_tmem.cpp.
Op rows per function body:
  print   fprintf / printf / fputs / puts / fflush / fwrite
  getenv  a getenv( call (uncached unless the statement is a static initialiser -> kind getenv-static)
  store   = / op= / ++ / -- on a DIAG-named non-local (DIAGNAME below), incl. array elements
  copy    .assign( / .swap( / .push_back( / .insert( / memcpy( into a DIAG-named object
  call    a call to another function defined in the hot files (the census propagates gates through these)
Each row carries gate = ENV | BUDGET | SIG | ALWAYS from its enclosing conditions (block headers, braceless if prefixes,
and earlier `if (C) return;` guards in the same function):
  ONCE    inside a `static X = [..]{..}()` initialiser lambda (runs once per process)
  ENV     a condition reads an env token un-negated (`!tok` selects the default path and does not gate): a static initialised from getenv, a short function containing getenv, a local
          initialised from one, or a literal getenv( call
  BUDGET  a condition carries a post-increment counter (n++ < K) -> work bounded to K events per phase / run
  SIG     a condition compares (==) with a literal >= 0x10000 or a decimal >= 1000 (bad-value signature, e.g. 0x130393 / 1033)
  ALWAYS  none of the above
Output JSON {rows:[{file,line,fn,kind,name,gate}]}.  --plant FILE adds a control file (treated as hot)."""
import bisect, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT = os.path.join(ROOT, "lib/rt64/src")
HOT = ["hle/rt64_interpreter.cpp", "gbi/rt64_gbi_rdp.cpp", "hle/rt64_rdp.cpp", "hle/rt64_rdp_tmem.cpp"]
DIAGNAME = re.compile(r"^(?:g_|s_|k_)?(?:rs64|s\d{3,5}|S\d{4})|ring|hist|probe|diag|dump|trace", re.I)
CTRL = {"if", "for", "while", "switch", "catch", "return", "sizeof", "else", "do", "case", "default", "alignof", "decltype"}
PRINT = re.compile(r"\b(?:std::)?(fprintf|printf|fputs|puts|fflush|fwrite)\s*\(")
# globals set from getenv OUTSIDE the hot files (src/rsp/dpc_bridge.cpp ~6680: ROGUESQ_G1E_PCACHE default 0 -> g_rs64_g1e_pcache,
# latched into g_rs64_pc_arm by rs64PcLatch; ROGUESQ_G1E_HGATHER -> g_rs64_g1e_hgather, default 1, read only as hg >= 3 / == 3)
EXTERN_ENV = {"g_rs64_g1e_pcache", "g_rs64_pc_arm", "g_rs64_g1e_hgather"}
BIGLIT = re.compile(r"\b0[xX]([0-9A-Fa-f]+)\b|(?<![\w.])(\d{4,})\b")

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
    """(name, body_start, body_end) for every outermost function / method body (lambdas stay inside their parent)."""
    out, i = [], 0
    pat = re.compile(r"\)\s*(?:const\s*)?(?:override\s*)?(?:noexcept\s*)?(?:->\s*[\w:<>*&\s]+?)?\s*(?::[^;{}]*?)?\{")
    while True:
        m = pat.search(t, i)
        if not m: break
        j, d = m.start(), 0
        while j >= 0:
            if t[j] == ")": d += 1
            elif t[j] == "(":
                d -= 1
                if d == 0: break
            j -= 1
        w = re.search(r"(\w+)\s*$", t[:j])
        if not w or w.group(1) in CTRL or re.search(r"\]\s*$", t[:j]):
            i = m.end(); continue
        b = m.end() - 1
        e = match_brace(t, b)
        out.append((w.group(1), b, e))
        i = e + 1
    return out

def env_tokens(texts):
    """names whose value derives from getenv: statics/globals initialised from it, short functions containing it."""
    toks = set(EXTERN_ENV)
    for t in texts:
        for m in re.finditer(r"\bstatic\s+[^;{}=]*?\b(\w+)\s*=\s*(?:\[[^\]]*\]\s*(?:\([^)]*\))?\s*\{[^{}]*?getenv|[^;{}]*?getenv)", t):
            toks.add(m.group(1))
        for name, b, e in functions(t):
            body = t[b:e]
            if "getenv" in body and body.count("\n") <= 14: toks.add(name)
    for _ in range(3):  # statics initialised from an env function / token
        for t in texts:
            for m in re.finditer(r"\bstatic\s+[^;{}=]*?\b(\w+)\s*=\s*([^;]*);", t):
                if any(re.search(r"\b%s\b" % re.escape(k), m.group(2)) for k in toks): toks.add(m.group(1))
    # default-ON toggles (`return !(e && *e == '0')` / `!e || ...`): the env var only turns the work OFF, so reading the
    # static does not gate anything (s7632: ROGUESQ_S7632_SNAP, ROGUESQ_DIAG_GATE, ROGUESQ_SHADE_ORD_RESET)
    don, pos = set(), set()
    for t in texts:
        for m in re.finditer(r"\bstatic\s+[^;{}=]*?\b(\w+)\s*=\s*\[[^\]]*\]\s*(?:\([^)]*\))?\s*\{([^{}]*?getenv[^{}]*?)\}", t):
            (don if re.search(r"return\s*(?:!\s*\(|!\s*e\s*\|\|)", m.group(2)) else pos).add(m.group(1))
    toks -= (don - pos)  # names are not scoped here: a name also used for an opt-in toggle elsewhere stays a token
    toks -= CTRL
    return toks

def cond_gate(conds, envt):
    g = []
    for c in conds:
        if c == "@ONCE": g.append("ONCE"); continue
        if c.startswith("@NOT:"):  # early-return guard: the code after it runs when the condition is FALSE
            c = c[5:]
            if any(re.search(r"!\s*\(?\s*%s\b|\b%s\s*==\s*0\b" % (re.escape(k), re.escape(k)), c) for k in envt):
                g.append("ENV")
            elif re.search(r"\w\s*\+\+|\+\+\s*\w", c) and re.search(r"[<>]", c): g.append("BUDGET")
            continue
        # polarity: a token read only as !tok (or tok == 0 / !tok-style) selects the DEFAULT path, so it does not gate
        pos_env = "getenv" in c or any(re.search(r"(?<![!\w])(?<!!\s)\b%s\b(?!\s*==\s*0\b)" % re.escape(k), c) for k in envt)
        if pos_env: g.append("ENV")
        elif re.search(r"\w\s*\+\+|\+\+\s*\w", c) and re.search(r"[<>]", c): g.append("BUDGET")
        else:
            for m in BIGLIT.finditer(" ".join(re.findall(r"(?<==)=\s*(\w+)", c) + re.findall(r"(\w+)\s*==", c))):
                v = int(m.group(1), 16) if m.group(1) else int(m.group(2))
                if (m.group(1) and v >= 0x10000) or (m.group(2) and v >= 1000): g.append("SIG"); break
    for k in ("ONCE", "ENV", "BUDGET", "SIG"):
        if k in g: return k
    return "ALWAYS"

def peel(s):
    """strip leading if(...)/else if(...)/for(...)/while(...)/else prefixes of a braceless statement -> (conds, rest)."""
    conds = []
    while True:
        s = s.lstrip()
        m = re.match(r"(?:else\s+)?(if|while|for|switch)\s*\(", s)
        if m:
            k, d = m.end() - 1, 0
            for j in range(k, len(s)):
                if s[j] == "(": d += 1
                elif s[j] == ")":
                    d -= 1
                    if d == 0: break
            if m.group(1) == "if": conds.append(s[k + 1:j])
            s = s[j + 1:]; continue
        m = re.match(r"else\b|do\b|(?:case\s+[^:]+|default)\s*:(?!:)", s)
        if m: s = s[m.end():]; continue
        return conds, s

def scan_file(path, label, rows, envt, hotfns):
    t = clean(open(path, errors="replace").read())
    nl = [k for k, ch in enumerate(t) if ch == "\n"]
    line = lambda pos: bisect.bisect_left(nl, pos) + 1
    for fn, b, e in functions(t):
        # walk the body: stack of block-header conditions, statement split on ; { } at paren depth 0
        stack, guards, s0, d = [[]], [[]], b + 1, 0
        locals_ = set(re.findall(r"(\w+)\s*(?=[,)=])", t[max(0, b - 400):b].rsplit("(", 1)[-1] if "(" in t[max(0, b - 400):b] else ""))
        lenv = set()
        k = b + 1
        while k < e:
            ch = t[k]
            if ch == "(": d += 1
            elif ch == ")": d = max(0, d - 1)
            elif ch in "{};" and d == 0:
                s = t[s0:k]
                conds, rest = peel(s)
                pos = s0 + (len(s) - len(s.lstrip()))
                ctx = [c for lvl in stack for c in lvl] + [c for lvl in guards for c in lvl] + conds
                handle(rest, s, ctx, pos, line, label, fn, rows, envt | lenv, hotfns, locals_, lenv, guards, conds, ch)
                if ch == "{":
                    hdr_conds = conds
                    if re.search(r"\bstatic\b[^;{}]*=\s*\[[^\]]*\]\s*(?:\([^)]*\))?\s*(?:->\s*[\w:<>*&\s]+)?$", s):
                        hdr_conds = conds + ["@ONCE"]  # static initialiser lambda: runs once per process
                    # a lambda / initialiser brace keeps the current context
                    stack.append(hdr_conds); guards.append([])
                elif ch == "}":
                    if len(stack) > 1: stack.pop(); guards.pop()
                s0 = k + 1
            k += 1

def handle(rest, s, ctx, pos, line, label, fn, rows, envt, hotfns, locals_, lenv, guards, conds, term):
    r = rest.strip()
    if not r and not conds: return
    ln = line(pos)
    gate = cond_gate(ctx, envt)
    # early-return guard: `if (C) return;` -> later statements in this block carry C
    if conds and re.match(r"^return\b[^;]*$", r) and term == ";":
        guards[-1].extend("@NOT:" + c for c in conds); return
    dm = re.match(r"^(static\s+|thread_local\s+)?(?:(?:const|constexpr|volatile|struct|unsigned|signed|long|short)\s+)*"
                  r"(?:auto|[\w:]+(?:<[^;{}]*?>)?)(?:\s+|\s*[*&]+\s*)(?:const\s+)?(\w+)\s*(?:\[[^\]]*\])?\s*(=|\{|$)(.*)$", r, re.S)
    is_decl = bool(dm) and dm.group(2) not in CTRL and not re.match(r"^(return|delete|new|else|goto)\b", r)
    if is_decl:
        locals_.add(dm.group(2))
        rm = re.match(r"^[\w:]+\s*&\s*\w+\s*=\s*([\w:]+)\s*\[", r)  # T &e = g_ring[i]: a store through e
        if rm and DIAGNAME.search(rm.group(1).split("::")[-1]):
            rows.append(dict(file=label, line=ln, fn=fn, kind="store", name=rm.group(1).split("::")[-1], gate=gate))
        if dm.group(1) is None and re.search("getenv|" + "|".join(r"\b%s\b" % re.escape(x) for x in envt) if envt else "getenv", dm.group(4) or ""):
            lenv.add(dm.group(2))
    for m in PRINT.finditer(r):
        rows.append(dict(file=label, line=ln, fn=fn, kind="print", name=m.group(1), gate=gate))
    if conds and any(re.search(r"\bgetenv\s*\(", c) for c in conds) and not re.search(r"\bgetenv\s*\(", r):
        # getenv inside this statement's own condition: evaluated before that condition gates anything
        own = cond_gate([c for c in ctx if c not in conds], envt)
        rows.append(dict(file=label, line=ln, fn=fn, kind="getenv", name="getenv", gate=own))
    if re.search(r"\bgetenv\s*\(", r):
        st = is_decl and dm.group(1)
        rows.append(dict(file=label, line=ln, fn=fn, kind="getenv-static" if st else "getenv", name="getenv", gate=gate))
    seen_st = set(x["name"] for x in rows if x["line"] == ln and x["kind"] == "store")
    for m in re.finditer(r"(?<![\w.>])(\w+)\s*(?:\+\+|--)|(?:\+\+|--)\s*(\w+)\b(?!\s*[.(\[])", r):
        base = m.group(1) or m.group(2)
        if base not in locals_ and base not in seen_st and DIAGNAME.search(base):
            rows.append(dict(file=label, line=ln, fn=fn, kind="store", name=base, gate=gate)); seen_st.add(base)
    if is_decl: return
    # stores to DIAG-named non-locals
    am = re.match(r"^(?:\+\+|--)?\s*([\w:]+(?:\s*\[[^\]]*\])?(?:\s*(?:\.|->)\s*\w+)*)\s*(?:\+\+|--|[-+*/%&|^]?=(?!=)|<<=|>>=)", r)
    if not am: am = re.match(r"^(?:\+\+|--)\s*([\w:]+(?:\s*\[[^\]]*\])?)", r)
    if am:
        lhs = am.group(1)
        base = re.match(r"([\w:]+)", lhs).group(1).split("::")[-1]
        if base not in locals_ and DIAGNAME.search(base):
            rows.append(dict(file=label, line=ln, fn=fn, kind="store", name=base, gate=gate))
    for m in re.finditer(r"\b([\w:]+)\s*(?:\[[^\]]*\])?\s*\.\s*(assign|swap|push_back|emplace_back|insert|resize)\s*\(", r):
        base = m.group(1).split("::")[-1]
        if base not in locals_ and DIAGNAME.search(base):
            rows.append(dict(file=label, line=ln, fn=fn, kind="copy", name=base, gate=gate))
    for m in re.finditer(r"\bmem(?:cpy|move)\s*\(\s*&?\s*([\w:]+)", r):
        base = m.group(1).split("::")[-1]
        if base not in locals_ and DIAGNAME.search(base):
            rows.append(dict(file=label, line=ln, fn=fn, kind="copy", name=base, gate=gate))
    for m in re.finditer(r"(?<![\w.>:])(\w+)\s*(?:<[^;(){}<>]*>)?\s*\(", r):
        if m.group(1) in hotfns and m.group(1) != fn:
            rows.append(dict(file=label, line=ln, fn=fn, kind="call", name=m.group(1), gate=gate))

def main():
    a = sys.argv[1:]
    hot = [os.path.join(RT, f) for f in HOT]
    if "--hot" in a:  # comma-separated repo-relative paths replace the rt64 hot set (e.g. src/rsp/dpc_bridge.cpp)
        hot = [os.path.join(ROOT, f) for f in a[a.index("--hot") + 1].split(",")]
    files = [(f, os.path.relpath(f, ROOT)) for f in hot]
    if "--plant" in a:
        pf = a[a.index("--plant") + 1]; files.append((pf, "PLANT/" + os.path.basename(pf)))
    texts = [clean(open(p, errors="replace").read()) for p, _ in files]
    envt = env_tokens(texts)
    hotfns = set(n for t in texts for n, _, _ in functions(t)) - CTRL
    rows = []
    for p, lab in files: scan_file(p, lab, rows, envt, hotfns)
    ded = {(r["file"], r["line"], r["kind"], r["name"]): r for r in rows}
    rows = sorted(ded.values(), key=lambda r: (r["file"], r["line"], r["kind"]))
    sys.stderr.write("files=%d envtok=%d rows=%d\n" % (len(files), len(envt), len(rows)))
    o = a[a.index("--out") + 1] if "--out" in a else None
    s = json.dumps(dict(envtok=sorted(envt), rows=rows), indent=0)
    (open(o, "w").write(s) if o else sys.stdout.write(s))

if __name__ == "__main__":
    main()
