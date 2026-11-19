#!/usr/bin/env python3
"""s7614 class HM regex side (first source; the clang AST join tools/s7614_hm_join.py is the second).

 (R) record census: every struct / class / union body in the in-scope files plus the repo / N64ModernRuntime headers
     (named, and `static struct { ... } name;` unnamed bodies), with its top-level fields; a field is pointer-like when its
     declarator has '*' / an iterator / uintptr_t (char* strings, FILE*, function pointers and callback typedefs are
     auto-host and do not make a record a candidate). Nested record-typed fields recurse (depth 4).
 (V) static-aggregate census: every static / thread_local / file-scope declaration in an in-scope file whose type text names
     a candidate record (bare or inside a template / array), plus the unnamed-body statics.
 (S) member-store scan: `x.f = <HP token>` / `x[i].f = ...` / `p->f = ...` where the RHS carries a host-view-of-guest token
     (TO_PTR, &rdram[, rdram +, (T*)(rdram ...), g_rdram_for_submit +); every hit's field must be a classified row.
Output: dict(records={name: [ptr fields]}, vars=[{file,line,var,records}], stores=[{file,line,field,rhs}])."""
import glob, importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sp = importlib.util.spec_from_file_location("sn_scan", os.path.join(ROOT, "tools/s7611_sn_scan.py"))
sn = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(sn)

HEADERS = ("include/*.h", "src/*/*.h", "lib/N64ModernRuntime/*/include/*.h*", "lib/N64ModernRuntime/*/include/*/*.h*")
HP = re.compile(r"\bTO_PTR\s*\(|&\s*rdram\s*\[|\brdram\s*\+|reinterpret_cast<[^>]*\*>\s*\(\s*rdram|"
                r"\(\s*[\w:]+\s*\*\s*\)\s*\(?\s*rdram\b|\bg_rdram_for_submit\s*\+")
KW = set("struct class union enum const volatile static mutable unsigned signed long short int char bool float double void "
         "auto std uint8_t uint16_t uint32_t uint64_t int8_t int16_t int32_t int64_t size_t atomic vector map array deque".split())

def rel(p):
    p = os.path.normpath(p)
    return "RF/" + os.path.basename(p) if p.startswith(sn.GEN + "/") else os.path.relpath(p, ROOT)

def clean(t):
    t = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), t, flags=re.S)
    t = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', t)
    t = re.sub(r"'(?:\\.|[^'\\\n])'", "''", t)
    t = re.sub(r"//[^\n]*", "", t)
    t = re.sub(r"^[ \t]*#[^\n]*(?:\\\n[^\n]*)*", lambda m: "\n" * m.group(0).count("\n"), t, flags=re.M)
    return t

def fn_typedefs(texts):
    s = set()
    for t in texts:
        s |= set(re.findall(r"\busing\s+(\w+)\s*=\s*[^;]*\(", t))
        s |= set(re.findall(r"\btypedef\b[^;]*\(\s*\*?\s*(\w+)\s*\)\s*\(", t))
    return s

def match_brace(t, i):
    d = 0
    for j in range(i, len(t)):
        if t[j] == "{": d += 1
        elif t[j] == "}":
            d -= 1
            if d == 0: return j
    return len(t) - 1

def top_stmts(body):
    """top-level statements of a record body; a nested `struct {...} name;` stays one statement, method bodies end at '}'."""
    out, d, cur = [], 0, ""
    for i, ch in enumerate(body):
        if ch == "{": d += 1
        if ch == "}": d -= 1
        cur += ch
        if d == 0 and ch == ";":
            out.append(cur.strip()); cur = ""
        elif d == 0 and ch == "}" and not REC.match(cur.strip()) and re.search(r"\)[^;{=]*\{", cur):
            out.append(cur.strip()); cur = ""
    if cur.strip(): out.append(cur.strip())
    return out

REC = re.compile(r"\b(struct|class|union)\s+(?:alignas\([^)]*\)\s*)?(\w+)?\s*(?:final\s*)?(?::[^{;()]*)?\{")

def records_in(t, fnt):
    recs = []
    for m in REC.finditer(t):
        if re.search(r"\benum\s*$", t[max(0, m.start() - 6):m.start()]):
            continue
        b0 = m.end() - 1; b1 = match_brace(t, b0)
        body = t[b0 + 1:b1]
        fields = []
        for s in top_stmts(body):
            s0 = re.sub(r"^(?:public|private|protected)\s*:", "", s).strip()
            if not s0 or s0.startswith(("using ", "typedef ", "friend ", "static ", "enum ", "template")):
                continue
            nested = REC.match(s0)
            if nested:
                inner = s0[s0.find("{"):].rsplit("}", 1)
                nm = (inner[1] if len(inner) > 1 else "").strip(" ;")
                if nm and re.fullmatch(r"\w+(\s*\[[^\]]*\])*", nm):
                    fields.append(("rec:", re.match(r"\w+", nm).group(0), b0 + 1 + body.find(s0) + nested.start()))
                continue
            if s0.endswith("}") or not s0.endswith(";"):
                continue  # method body / ctor
            s1 = re.sub(r"\{[^{}]*\}", "", s0.rstrip(";"))
            s1 = re.sub(r"=[^,]*", "", s1)
            if re.search(r"\w\s*\([^*]", s1) and "(*" not in s1:
                continue  # method declaration
            # split declarators
            parts, dd, cur = [], 0, ""
            for ch in s1:
                if ch in "<([": dd += 1
                elif ch in ">)]": dd -= 1
                if ch == "," and dd == 0: parts.append(cur); cur = ""
                else: cur += ch
            parts.append(cur)
            mt = re.match(r"^\s*((?:(?:const|volatile|mutable|alignas\([^)]*\))\s+)*(?:[\w:]+(?:<.*>)?)(?:\s*::\s*\w+)*)(.*)$", parts[0])
            if not mt:
                continue
            base, d0 = mt.group(1), mt.group(2)
            decls = [d0] + parts[1:]
            for dcl in decls:
                nm = re.findall(r"(\w+)\s*(?:\[[^\]]*\]\s*)*(?::\s*\d+)?\s*$", dcl)
                if not nm:
                    continue
                n = nm[0]
                full = base + " " + dcl
                if "(*" in dcl or re.search(r"\(\s*\*", full) or re.search(r"std::function|GenericFunction", base):
                    kind = "fnptr"
                elif re.search(r"\b(%s)\s*\*" % "|".join(fnt), full) if fnt else False:
                    kind = "fnptr"
                elif re.fullmatch(r"\s*(?:std::atomic<)?(?:const\s+)?(?:volatile\s+)?char\s*\*.*", full):
                    kind = "str"
                elif re.match(r"\s*FILE\s*\*", full):
                    kind = "file"
                elif "*" in full or "iterator" in full or re.search(r"\bu?intptr_t\b", full):
                    kind = "ptr"
                else:
                    kind = None
                fields.append(("f", n, kind, base) if kind is None else ("f", n, kind))
        nm = m.group(2)
        tail = t[b1 + 1:b1 + 200]
        vm = re.match(r"\s*(\w+)\s*(?:\[[^\]]*\]\s*)*(?:\{\s*\}\s*)?[;=]", tail)
        pre = t[max(0, m.start() - 40):m.start()]
        static_var = None
        if vm and vm.group(1) not in ("const",):
            static_var = vm.group(1)
        recs.append(dict(name=nm, pos=m.start(), fields=fields, var=static_var, typedef=bool(re.search(r"\btypedef\s*$", pre)),
                         static=bool(re.search(r"\b(static|thread_local)\s*$", pre))))
    return recs

def scan(extra=()):
    files = sn.scope_files() + list(extra)
    hdrs = sorted({h for p in HEADERS for h in glob.glob(os.path.join(ROOT, p))})
    texts = {f: clean(open(f, errors="replace").read()) for f in set(files) | set(hdrs)}
    fnt = fn_typedefs(texts.values())
    R = {}  # name -> list of record dicts
    per_file = {}
    for f, t in texts.items():
        rs = records_in(t, fnt)
        per_file[f] = rs
        for r in rs:
            r["file"] = rel(f)
            if r["name"]:
                R.setdefault(r["name"], []).append(r)
            if r["typedef"] and r["var"]:
                R.setdefault(r["var"], []).append(r)
    memo = {}
    def ptrs(r, depth=0):
        k = id(r)
        if k in memo: return memo[k]
        memo[k] = []
        out = []
        for fld in r["fields"]:
            if fld[0] == "rec:":
                sub = [x for x in per_file_of(r) if x["pos"] == fld[2]]
                for s in sub[:1]:
                    out += [fld[1] + "." + p for p in ptrs(s, depth + 1)]
                continue
            if fld[2] == "ptr":
                out.append(fld[1])
            elif fld[2] is None and depth < 4:
                for w in re.findall(r"[A-Za-z_]\w*", fld[3]):
                    if w in R and w not in KW:
                        c = [x for x in R[w] if x["file"] == r["file"]] or [x for x in R[w] if re.search(r"\.(h|hpp)$", x["file"])]
                        for s in c[:1]:
                            if s is not r:
                                out += [fld[1] + "." + p for p in ptrs(s, depth + 1)]
        memo[k] = out
        return out
    def per_file_of(r):
        for f, rs in per_file.items():
            if r in rs: return rs
        return []
    cand = {n: rs for n, rs in R.items()}
    vars_, stores = [], []
    for f in files:
        t = texts[f]; rf = rel(f)
        for r in per_file[f]:
            if r["var"] and not r["typedef"] and r["static"]:
                p = ptrs(r)
                if p:
                    vars_.append(dict(file=rf, line=t[:r["pos"]].count("\n") + 1, var=r["var"], records=[r["name"] or "(unnamed)"], fields=p))
        lines = t.split("\n")
        bstack = []  # brace kinds: 'ns' (namespace / extern "C" - transparent) or 'b' (any other block)
        pend = ""
        for i, l in enumerate(lines):
            segs = []  # (block depth at segment start, text) for segments split at ; { }
            cur = ""
            for ch in l:
                if ch in ";{}":
                    d0 = sum(1 for k in bstack if k == "b")
                    segs.append((d0, cur))
                    if ch == "{":
                        head = (pend + " " + cur).strip()
                        bstack.append("ns" if re.search(r'(?:^|\s)(?:namespace(?:\s+[\w:]+)?|extern\s+""\s*)$', head) else "b")
                    elif ch == "}" and bstack:
                        bstack.pop()
                    cur = ""; pend = ""
                else:
                    cur += ch
            segs.append((sum(1 for k in bstack if k == "b"), cur))
            pend = cur
            words = set(re.findall(r"\b[A-Za-z_]\w*\b", l)) & set(cand)
            for w in words:
                if w in KW: continue
                c = [x for x in cand[w] if x["file"] == rf] or [x for x in cand[w] if re.search(r"\.(h|hpp)$", x["file"])]
                if not c: continue
                p = ptrs(c[0])
                if not p: continue
                for d_at_start, st in segs:
                    m = re.match(r"^\s*((?:(?:static|thread_local|inline|const|constexpr)\s+)*)(?:struct\s+)?((?:[\w:]+)(?:<.*>)?(?:::\w+)*)\s+(.*)$", st)
                    if not m or not re.search(r"\b%s\b" % re.escape(w), m.group(2)):
                        continue
                    qual, ty, rest = m.groups()
                    if re.match(r"(?:return|new|sizeof|case|typedef|using|extern|delete|throw|else|goto)\b", ty):
                        continue
                    if not ("static" in qual or "thread_local" in qual or d_at_start == 0):
                        continue  # automatic local
                    if re.search(r"<[^<>]*\b%s\b\s*\*" % re.escape(w), ty) is None and re.search(r"\b%s\b\s*\*?$" % re.escape(w), ty) is None and "<" not in ty:
                        continue
                    rest = re.sub(r"=.*$", "", rest)
                    parts, dd, cur = [], 0, ""
                    for ch in rest:
                        if ch in "<([": dd += 1
                        elif ch in ">)]": dd -= 1
                        if ch == "," and dd == 0: parts.append(cur); cur = ""
                        else: cur += ch
                    parts.append(cur)
                    for dcl in parts:
                        dm = re.match(r"^\s*([\*&]*)\s*(\w+)\s*(\[[^\]]*\]\s*)*(\(.*)?$", dcl)
                        if not dm or dm.group(2) in KW:
                            continue
                        if dm.group(4) is not None:
                            continue  # function declaration / ctor-call init (handled: `T x(args)` is rare at file scope)
                        if dm.group(1):
                            continue  # pointer / reference to the record: class HP's var
                        vars_.append(dict(file=rf, line=i + 1, var=dm.group(2), records=[w], fields=p))
            if HP.search(l):
                for m in re.finditer(r"(?:\.|->)\s*(\w+)\s*(?:\[[^\]]*\]\s*)*=(?!=)\s*([^;]*)", l):
                    if HP.search(m.group(2)):
                        stores.append(dict(file=rf, line=i + 1, field=m.group(1), rhs=m.group(2)[:80]))
    ded = {}
    for v in vars_:
        k = (v["file"], v["var"])
        if k in ded: ded[k]["records"] = sorted(set(ded[k]["records"] + v["records"])); continue
        ded[k] = v
    return dict(vars=sorted(ded.values(), key=lambda v: (v["file"], v["line"])), stores=stores,
                records={n: sorted({p for r in rs for p in ptrs(r)}) for n, rs in R.items() if any(ptrs(r) for r in rs)})

if __name__ == "__main__":
    s = scan(sys.argv[2:] if sys.argv[1:2] == ["--extra"] else ())
    print(json.dumps(s, indent=0) if "--json" in sys.argv else "\n".join(
        ["vars %d stores %d records %d" % (len(s["vars"]), len(s["stores"]), len(s["records"]))] +
        ["%s:%d %s %s %s" % (v["file"], v["line"], v["var"], v["records"], v["fields"][:3]) for v in s["vars"]] +
        ["STORE %s:%d .%s = %s" % (x["file"], x["line"], x["field"], x["rhs"]) for x in s["stores"]]))
