#!/usr/bin/env python3
"""s7613 class HP scanner: HOST pointers (into guest RAM or anywhere) held in static / thread_local / file-scope storage.

Two candidate sources over tools/s7611_sn_scan.py's scope (src/*, librecomp/src, ultramodern/src, generated .c):
 (A) declaration census: every static/thread_local/file-scope variable whose declared type is a pointer (T*, T* const,
     T* arr[N], std::atomic<T*>, a container whose element type holds a '*', uintptr_t / intptr_t) - multi-declarator
     lines and mid-line `{ static T* p = ...;` patch one-liners included. char* / const char* / FILE* strings excluded.
     Function pointers (`(*name)`) are reported with auto='fnptr' (host code address, not a guest view).
 (B) store cross-check: tools/s7611_sn_scan.scan_file with the HP taint set (TO_PTR, PTR(, &rdram[, rdram +,
     reinterpret_cast<T*>(rdram..., (T*)(rdram + ...), g_rdram_for_submit +). A (B) store whose target's declaration is
     pointer-shaped but which (A) did not list is emitted with kind='missed' (a census hole).
Usage: s7613_hp_scan.py [--extra FILE...] -> JSON {decl:[...], store:[...]} on stdout.
"""
import importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sp = importlib.util.spec_from_file_location("sn_scan", os.path.join(ROOT, "tools/s7611_sn_scan.py"))
sn = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(sn)

HP = re.compile(r"\bTO_PTR\s*\(|\bPTR\s*\(|&\s*rdram\s*\[|\brdram\s*\+|reinterpret_cast<[^>]*\*>\s*\(\s*rdram|"
                r"\(\s*[\w:]+\s*\*\s*\)\s*\(?\s*rdram\b|\bg_rdram_for_submit\s*\+")
STMT_STATIC = re.compile(r"(?:^|(?<=[;{}]))\s*((?:static|thread_local)\b[^;]*;)")
REC_BODY = re.compile(r"\b(struct|union|class)(\s+\w+)?\s*(?::[^{;]*)?\{[^{}]*\}")
PTR_TYPEDEF = re.compile(r"\b(pthread_t|\w+_fn|\w+_hook_t)\b")  # pointer typedefs (opaque on macOS) the regex cannot see through
STRING_T = re.compile(r"^(?:(?:static|thread_local|const|volatile|constexpr|inline)\s+)*(?:char|wchar_t|FILE)\s*\*")
FUNC_DEF = re.compile(r"^(?:(?:static|thread_local|inline|const|constexpr|extern)\s+)*[\w:<>,\s\*&]+?\b\w+\s*\([^()]*\)\s*(?:const\s*)?(?:\{|$|;)")

def untemplate(s):
    while re.search(r"<[^<>]*>", s):
        s = re.sub(r"<[^<>]*>", lambda m: "T" + ("PTR" if "*" in m.group(0) or PTR_TYPEDEF.search(m.group(0)) or re.search(r"\bu?intptr_t\b", m.group(0)) else ""), s)
    return s

def ptr_decls(stmt):
    """[(name, typeinfo, auto)] for one `static ...;` statement."""
    s = stmt.rstrip(";").strip()
    if FUNC_DEF.match(s) and "=" not in s.split("(")[0]:
        return []
    s = re.sub(r"\{[^{}]*\}", "", s)  # brace initialisers
    s = re.sub(r"\[\s*[^\]]*\]\s*\{.*$", "[]", s)
    s = re.sub(r"=\s*\[[^\]]*\][^,]*", "", s)  # lambda initialisers
    out = []
    m = re.match(r"^((?:(?:static|thread_local|const|volatile|constexpr|inline|mutable)\s+)+)(.*)$", s)
    if not m:
        return []
    body = m.group(2)
    base = untemplate(body)
    if "::iterator" in body:
        base = re.sub(r"^T", "T::iterator", base)
    # split declarators at top-level commas, drop initialisers
    parts, depth, cur = [], 0, ""
    for ch in base:
        if ch in "([": depth += 1
        elif ch in ")]": depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""
        else:
            cur += ch
    parts.append(cur)
    parts = [p.split("=")[0] for p in parts]
    first = parts[0].strip()
    fm = re.match(r"^(.*?)([\*&\s]*)\b(\w+)\s*(\[[^\]]*\]\s*)*$", first)
    fp = re.match(r"^(.*?)\(\s*\*\s*(?:const\s+)?(\w+)\s*\)", first)
    if fp:
        return [(fp.group(2), first[:80], "fnptr")]
    if not fm:
        return []
    tbase = fm.group(1).strip()
    if STRING_T.match(m.group(1) + tbase + fm.group(2)):
        return []
    # the type text: base + star of the first declarator
    def classify(stars, tb):
        if re.search(r"\bPTR\s*\(", tb):
            return False  # PTR(T) is a 32-bit GUEST address, not a host pointer (outside class HP)
        if "TPTR" in tb or "::iterator" in body:  # template argument holds a pointer (atomic<T*>, vector<T*>, map<K, V*>)
            return True
        if "*" in stars or "*" in tb:  # T* volatile name: the star sits before a cv-qualifier
            return True
        return bool(re.search(r"\b(u?intptr_t)\b|::iterator\b", tb) or PTR_TYPEDEF.search(tb))
    if classify(fm.group(2), tbase) and not STRING_T.match(tbase + "*"):
        out.append((fm.group(3), (tbase + fm.group(2)).strip(), ""))
    for p in parts[1:]:
        pm = re.match(r"^\s*([\*&\s]*)(\w+)\s*(\[[^\]]*\]\s*)*$", p)
        if pm and classify(pm.group(1), tbase) and not re.match(r"^(?:const\s+)?(?:char|wchar_t|FILE)$", tbase):
            out.append((pm.group(2), (tbase + pm.group(1)).strip(), ""))
    return out

def decl_census(path, rel):
    try:
        raw = open(path, errors="replace").read().split("\n")
    except OSError:
        return []
    out = []
    stack = []  # brace kinds: 'ns' (namespace / extern "C" {), 'rec' (struct/class/union/enum), 'fn' (anything else)
    for i, r in enumerate(raw):
        l = REC_BODY.sub(lambda m: m.group(1) + (m.group(2) or "") + " _REC", sn.strip(r))  # one-line struct bodies
        filescope = all(k == "ns" for k in stack)
        full = l
        ro = re.search(r"\b(struct|union|class)(\s+\w+)?\s*(?::[^{;]*)?\{", l)
        if ro:
            l = l[:ro.end()]  # a record body opens here: its members are not variables (braces still counted on `full`)
        if re.match(r'^\s*extern\s+""\s+[^{=]*;\s*$', l):
            l = ""  # declaration-only `extern "C" T* x;`: the definition is censused where it lives
        stmts = [m.group(1) for m in STMT_STATIC.finditer(l)]
        g = re.sub(r'^\s*extern "(?:C)?"\s*\{?\s*', "", l)  # sn.strip blanks "C" to "" if filescope else l
        if filescope and not re.match(r"^\s*(static|thread_local)\b", g):
            for st in re.split(r"(?<=;)", g):
                s = st.strip()
                if not s.endswith(";") or re.match(r"(extern|typedef|using|return|template|namespace|struct|class|enum|union|#)\b", s):
                    continue
                if re.match(r"^(?:const\s+|volatile\s+)*[\w:]+(?:<[^;]*>)?[\s\*&]*(?:const\s+|volatile\s+)*[\w\s\*,]*?\b\w+\s*(\[[^\]]*\])?\s*(=[^;]*|\{[^;]*\})?;$", s) \
                   and not re.search(r"\w\s*\([^)]*\)\s*;$", s.split("=")[0].split("{")[0] + ";"):
                    stmts.append("static " + s)
        for st in stmts:
            for name, ty, auto in ptr_decls(st):
                out.append(dict(file=rel, line=i + 1, name=name, type=ty, auto=auto, text=r.strip()[:200], kind="decl"))
        # brace stack update, character by character
        for m in re.finditer(r"[{}]", full):
            if m.group(0) == "{":
                pre = full[:m.start()]
                if re.search(r'(\bnamespace\b[^{;]*|\bextern "(?:C)?"\s*)$', pre):
                    stack.append("ns")
                elif re.search(r"\b(struct|class|union|enum)\b[^;{()]*$", pre) and not re.search(r"\)\s*$", pre):
                    stack.append("rec")
                else:
                    stack.append("fn")
            elif stack:
                stack.pop()
    return out

def relname(p):
    return os.path.relpath(p, ROOT) if p.startswith(ROOT) else "RF/" + os.path.basename(p) if p.startswith(sn.GEN) else p

def scan(extra=()):
    files = list(sn.scope_files()) + list(extra)
    decl, store = [], []
    for p in files:
        rel = relname(p)
        d = decl_census(p, rel)
        decl += d
        names = {x["name"] for x in d}
        for c in sn.scan_file(p, rel, HP, None):
            ptrish = c["name"] in names
            if not ptrish:
                # declaration of the target pointer-shaped but missed by (A)?
                try:
                    txt = open(p, errors="replace").read()
                except OSError:
                    txt = ""
                if re.search(r"(?:static|thread_local)[^;\n]*(?:\*\s*|\b(?:u?intptr_t)\s+(?:\w+\s*,\s*)*)" + re.escape(c["name"]) + r"\b", txt):
                    c["kind"] = "missed"; store.append(c)
                continue
            c["kind"] = "store"; store.append(c)
    return dict(decl=decl, store=store)

if __name__ == "__main__":
    a = sys.argv[1:]
    extra = a[a.index("--extra") + 1:] if "--extra" in a else []
    json.dump(scan(extra), sys.stdout, indent=0)
