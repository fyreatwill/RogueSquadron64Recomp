#!/usr/bin/env python3
"""s7611 class SN scanner: host-side SNAPSHOTS of guest DATA held in static / thread_local / file-scope state.

A candidate is a line that stores into a static-storage variable (assignment, compound assignment, .store/.push_back/
.insert/.emplace/.assign, or passing it as an argument to a call that also receives rdram = out-param fill) where the
stored value is guest-derived: the line contains a guest-read token (MEM_*, rdram/RDRAM views, rs64_rdram_u*, rd8/16/32,
peek_be32, read_u*), or a local of the same function that is (transitively) assigned from one. Strings and comments are
stripped first. A name counts as static at a line only if the nearest declaration of that name above it, inside the
enclosing function, is a static/thread_local declaration, or there is none in the function and a file-scope one exists.

Auto classes (no row needed):
  base   the stored value is the host base pointer itself (`= rdram;`, `(uintptr_t)rdram + K`): a host address, not bytes.
Everything else must be classified by a row in tools/s7611_sn_census.py.
Usage: s7611_sn_scan.py [--root DIR] [--extra FILE...] -> JSON list of {file, line, name, text, auto} on stdout.
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.normpath(os.path.join(ROOT, "../N64Recomp/RecompiledFuncs"))

def scope_files(root=ROOT, gen=GEN):
    fs = []
    for pat in ("src/*/*.cpp", "src/*/*.h", "src/*/*.mm", "lib/N64ModernRuntime/librecomp/src/*.cpp",
                "lib/N64ModernRuntime/ultramodern/src/*.cpp"):
        fs += sorted(glob.glob(os.path.join(root, pat)))
    fs += sorted(glob.glob(os.path.join(gen, "*.c")))
    return fs

G = re.compile(r"\b(MEM_[A-Z]+|rdram\w*|RDRAM\w*|g_rdram_for_submit|rs64_rdram_u(8|16|32)|rd(8|16|32)|peek_be32|"
               r"read_u(8|16|32)|g_recomp_rdram\w*)\b")
STR = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
DECL = re.compile(r"^\s*(?:(?:static|thread_local|extern \"C\")\s+)+(?!const\b|constexpr\b|inline\b)")
SDECL = re.compile(r"^\s*(?:static|thread_local)\b")
LOCAL = re.compile(r"(?:^|[;{(]\s*)(?:const\s+)?(?:volatile\s+)?(?:u?int(?:8|16|32|64)_t|unsigned(?:\s+(?:int|long|char|short))*|"
                   r"int|long|gpr|float|double|auto|bool|size_t|uintptr_t|char)\s*\*?\s*(\w+)\s*(?:\[[^\]]*\])?\s*=\s*([^;]*)")
ASSIGN_LOCAL = re.compile(r"(?<![\w.>])(\w+)\s*(?:\[[^\]]*\]\s*)*(?:[-+|&^]?=(?!=))\s*([^;]*)")
FUNC_START = re.compile(r"^(?![#/ \t*}])[^;=]*\([^;]*\)\s*(const\s*)?\{?\s*$|^RECOMP_FUNC|^extern \"C\" [^;=]*\(")

def strip(l):
    l = STR.sub('""', l)
    l = re.sub(r"/\*.*?\*/", "", l)
    return l.split("//")[0]

def decl_names(line):
    """names declared static on this line (multi-decl aware)."""
    if not SDECL.match(line):
        return set()
    body = line
    if "(" in body.split("=")[0] and not re.search(r"\w+\s*\[", body.split("(")[0]):
        # function definition / prototype with static linkage: no variable unless brace-initialised later
        head = body.split("(")[0]
        if not re.search(r"=\s*$", head):
            return set()
    out = set()
    for stmt in body.split(";"):
        s = stmt.strip()
        if not SDECL.match(s + " "):
            continue
        s = re.sub(r"^\s*(?:static|thread_local|\s)+", "", s)
        while re.search(r"<[^<>]*>", s):
            s = re.sub(r"<[^<>]*>", "", s)  # template args carry commas (std::unordered_map<K, V>)
        s = re.sub(r"\{[^{}]*\}", "", s)
        s = re.sub(r"=\s*[^,]*", "", s)
        parts = s.split(",")
        m = re.match(r"([\w:<>\s\*&,]*?)\b(\w+)\s*(\[[^\]]*\])*\s*$", parts[0].strip())
        if not m:
            continue
        if m.group(1).strip() in ("const", "constexpr", "inline", "") and m.group(1).strip() != "":
            continue
        if re.match(r"\s*(const|constexpr|inline)\b", parts[0]):
            continue
        out.add(m.group(2))
        for p in parts[1:]:
            mm = re.match(r"\s*\*?\s*(\w+)", p)
            if mm:
                out.add(mm.group(1))
    return out

def scan_file(path, rel, taint_re=None, hot=None):
    """taint_re replaces the guest-read token set G (s7612 class RG passes the register set); hot = names of functions
    whose parameters are tainted on entry (called somewhere with a tainted argument). Defaults = the s7611 SN behaviour."""
    G = taint_re or globals()["G"]
    try:
        raw = open(path, errors="replace").read().split("\n")
    except OSError:
        return []
    L = [strip(l) for l in raw]
    file_statics = {}
    for i, l in enumerate(L):
        for n in decl_names(l):
            file_statics.setdefault(n, []).append(i)
    if not file_statics:
        return []
    starts = [i for i, l in enumerate(L) if FUNC_START.match(l)]
    import bisect
    names_re = re.compile(r"(?<![\w.>])(" + "|".join(sorted(map(re.escape, file_statics), key=len, reverse=True)) +
                          r")\b\s*((?:\[[^\]]*\]\s*|(?:\.|->)(?!store\(|push_back\(|insert\(|emplace|assign\()\w+\s*)*)([-+|&^]?=(?!=)|\.store\(|\.push_back\(|\.insert\(|\.emplace\w*\(|\.assign\()")
    out = []
    taint_cache = {}

    def fstart(i):
        k = bisect.bisect_right(starts, i) - 1
        return starts[k] if k >= 0 else 0

    def tainted_locals(f0, i):
        key = (f0, i)
        t = set()
        if hot:
            hdr = " ".join(L[f0:f0 + 4]).split("{")[0]
            mm = re.search(r"(\w+)\s*\(([^)]*)\)", hdr)
            if mm and mm.group(1) in hot:
                for prm in mm.group(2).split(","):
                    pm = re.search(r"(\w+)\s*(?:\[[^\]]*\])?\s*$", prm.strip())
                    if pm and pm.group(1) not in ("void", "rdram", "ctx"):
                        t.add(pm.group(1))
        for j in range(f0, i):
            l = L[j]
            for m in LOCAL.finditer(l):
                if G.search(m.group(2)) or any(re.search(r"\b" + re.escape(x) + r"\b", m.group(2)) for x in t):
                    t.add(m.group(1))
            for m in ASSIGN_LOCAL.finditer(l):
                if m.group(1) in t:
                    continue
                if G.search(m.group(2)) or any(re.search(r"\b" + re.escape(x) + r"\b", m.group(2)) for x in t):
                    # only plain locals already declared in this function are taintable. s7929: a file static of the same
                    # name elsewhere in the file (e.g. a function-local `static std::atomic<unsigned> n` in another
                    # function) no longer hides this function's own non-static local `n` (it dropped s7324 s_carry).
                    # (the old `\b\w+\s*\*?\s*NAME` form missed comma lists `float raw[3], o[3]` and only saw `o` by
                    # matching inside `lo[3]`; this form needs a real word break or a comma before NAME)
                    if any(re.search(r"(?:\b\w+(?:\s+|\s*\*\s*)|,\s*\*?\s*)" + re.escape(m.group(1)) + r"\b\s*[=;,\[]", L[k])
                           and not re.match(r"\s*(?:inline\s+)?(?:static|thread_local)\b", L[k]) for k in range(f0, j + 1)):
                        t.add(m.group(1))
        return t

    def is_static_at(name, i, f0):
        dre = re.compile(r"(?:\b[\w:<>]+[\s\*&]+|,\s*\*?\s*)" + re.escape(name) + r"\b\s*(\[[^\]]*\]\s*)*(=(?!=)|;|,|\)|\{)")
        if re.search(r"(?:^\s*|[;{(,]\s*)(?:const\s+)?(?:volatile\s+)?(?:u?int(?:8|16|32|64)_t|unsigned(?:\s+(?:int|long|char|short))*|"
                     r"int|long|gpr|float|double|auto|bool|size_t|uintptr_t|char|s32|u32|[A-Z]\w*)\s*[\*&]?\s*(?:\w+\s*(?:=[^,;]*)?,\s*\*?\s*)*"
                     + re.escape(name) + r"\b\s*(\[[^\]]*\]\s*)*=(?!=)", L[i]) and not SDECL.match(L[i]):
            return False  # local declared on this very line
        for j in range(i, f0 - 1, -1):
            l = L[j]
            if name in decl_names(l):
                return True
            if j != i and dre.search(l) and not SDECL.match(l):
                pre = l.split(name)[0]
                if re.search(r"\b(return|if|while|for|sizeof)\b", pre):
                    continue
                return False
            if j == i and j != f0 and re.search(r"[(,]\s*[\w:<>]+[\s\*&]+" + re.escape(name) + r"\b", l) and FUNC_START.match(l):
                return False
        if f0 < len(L) and re.search(r"[(,]\s*[\w:<>]+[\s\*&]+" + re.escape(name) + r"\b", L[f0]):
            return False  # parameter of the enclosing function
        return any(d < f0 or d == i for d in file_statics.get(name, []))

    for i, l in enumerate(L):
        cands = []
        for m in names_re.finditer(l):
            cands.append((m.group(1), l[m.end():]))
        # out-param fill: static passed to a call that also receives rdram
        for m in re.finditer(r"\b\w+\(([^()]*\brdram\b[^()]*)\)", l):
            for a in m.group(1).split(","):
                a = a.strip().lstrip("&").split("[")[0].strip()
                if a in file_statics:
                    cands.append((a, "rdram /*outparam*/"))
        if not cands:
            continue
        f0 = fstart(i)
        for name, rhs in cands:
            rhs = rhs.split(";")[0]
            g = bool(G.search(rhs))
            if not g:
                if f0 not in taint_cache or taint_cache[f0][0] != i:
                    taint_cache[f0] = (i, tainted_locals(f0, i))
                t = taint_cache[f0][1]
                g = any(re.search(r"\b" + re.escape(x) + r"\b", rhs) for x in t)
            if not g:
                continue
            if not is_static_at(name, i, f0):
                continue
            auto = ""
            if re.fullmatch(r"\s*\(?\s*(?:\(\s*\w+\s*\*?\s*\)\s*)?(rdram\w*|g_rdram_for_submit|g_recomp_rdram\w*)\s*\)?\s*", rhs):
                auto = "base"
            elif re.match(r"\s*(rdram\w*|g_rdram_for_submit)\s*,\s*std::memory_order_\w+\s*\)\s*$", rhs):
                auto = "base"  # atomic .store(rdram, order): the host base pointer
            elif re.match(r"\s*\(\(uintptr_t\)rdram\s*\+", rhs) or re.match(r"\s*\(\s*\(uintptr_t\)\s*rdram", rhs):
                auto = "base"
            out.append({"file": rel, "line": i + 1, "name": name, "text": raw[i].strip()[:240], "auto": auto})
    # dedupe (file, line, name)
    seen, ded = set(), []
    for o in out:
        k = (o["file"], o["line"], o["name"])
        if k not in seen:
            seen.add(k); ded.append(o)
    return ded

def scan(root=ROOT, gen=GEN, extra=(), taint_re=None, hot=None):
    res = []
    for p in list(scope_files(root, gen)) + list(extra):
        rel = os.path.relpath(p, root) if p.startswith(root) else "RF/" + os.path.basename(p) if p.startswith(gen) else p
        res += scan_file(p, rel, taint_re, hot)
    return res

if __name__ == "__main__":
    a = sys.argv[1:]
    root = ROOT
    if "--root" in a:
        root = a[a.index("--root") + 1]
    extra = a[a.index("--extra") + 1:] if "--extra" in a else []
    json.dump(scan(root, GEN if root == ROOT else os.path.join(root, "RF"), extra), sys.stdout, indent=0)
