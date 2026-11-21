#!/usr/bin/env python3
"""s7346 class W census: signed lengths reaching size_t sinks.
A length held in a signed type (int / int32_t / s32 / long / ptrdiff_t / short, or an `a - b` difference) checked only from
above (`if (n > cap) return;`) lets a negative n through; at memcpy/memmove/memset (3rd arg), fread/fwrite (size*count),
.resize/.reserve/.assign, new T[n], malloc/calloc/realloc, std::vector<T>(n), or a `for (unsigned/size_t i = 0; i < n; ...)`
bound it converts to ~2^32/2^64.
Scope = s7343 files_in_scope(). A site is a sink whose length expression mentions a signed-typed variable or a subtraction.
Classes: C/P/G/D from tools/s7338_mask_census.py sites() (rt64 G/D re-checked with s7343 body_gated(); CORE demotion as s7344)
  K   length is constant / sizeof-only            U   every variable in the length is unsigned / size_t / .size() (no '-')
  LB  every signed variable is lower-bounded before the sink (`n < 0`, `n <= 0`, `n >= 0 &&`, `n > 0 &&`, max(0, ..), abs)
      or a subtraction is preceded by an ordering check of its operands (`a < b` / `a > b` / `a >= b` / `a <= b`)
  MSK the signed variable is assigned from an unsigned / masked / narrow-unsigned source (`& 0x..`, MEM_BU/HU, uint8/16)
  SL  signed loop: for-bound with a signed loop index (negative n -> zero iterations; not a sink)
  H   hand-verified (reason in HAND)   B default-on, guest-derived, no lower bound (defect)   ?  unclassified
'?' or B => exit 1. --controls plants `int n = (int)task->size; if (n > 0x1000) return; memcpy(b, rdram, n);` ('?'), the
lower-bounded twin ('LB'), the unsigned twin ('U') and a gated twin ('G')."""
import re, sys, pathlib, importlib.util
import importlib.util as _ilu_cr, sys as _sys_cr
if "census_rules" not in _sys_cr.modules:  # s7654 shared text-anchored rules (one instance per process)
    _crs = _ilu_cr.spec_from_file_location("census_rules", __import__("pathlib").Path(__file__).resolve().parent / "census_rules.py")
    _sys_cr.modules["census_rules"] = _ilu_cr.module_from_spec(_crs); _crs.loader.exec_module(_sys_cr.modules["census_rules"])
census_rules = _sys_cr.modules["census_rules"]
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
def _load(name, f):
    s = importlib.util.spec_from_file_location(name, ROOT / f); mod = importlib.util.module_from_spec(s); s.loader.exec_module(mod); return mod
s44 = _load("s7344", "tools/s7344_wrap_census.py")
s43, s42, m = s44.s43, s44.s42, s44.m
CORE = s44.CORE

SINK = re.compile(r"\b(?:std::)?(memcpy|memmove|memset|fread|fwrite|malloc|calloc|realloc)\s*\(|\.(resize|reserve|assign)\s*\(|\bnew\s+[\w:<>]+\s*\[|"
                  r"\bfor\s*\(\s*(?:size_t|unsigned(?:\s+int)?|uint32_t|uint64_t|u32|uintptr_t)\s+\w+\s*=")
SIGNED = re.compile(r"^(?:const\s+)?(?:signed\s+)?(?:int|int8_t|int16_t|int32_t|int64_t|s8|s16|s32|s64|long|long\s+long|short|ptrdiff_t|ssize_t|intptr_t|gpr|int_fast32_t)$")
UNS = re.compile(r"^(?:const\s+)?(?:unsigned(?:\s+\w+)?|u?int(?:8|16|32|64)_t|size_t|uintptr_t|u8|u16|u32|u64|uint|bool|auto)$")
NARROWU = re.compile(r"^(?:const\s+)?(?:uint8_t|uint16_t|u8|u16|unsigned\s+char|unsigned\s+short|bool)$")
KW = {"sizeof", "static_cast", "reinterpret_cast", "const", "uint8_t", "uint16_t", "uint32_t", "uint64_t", "int", "size_t", "int32_t",
      "int64_t", "unsigned", "char", "float", "double", "std", "min", "max", "u32", "s32", "void", "true", "false", "nullptr", "auto"}
HAND = [   # (file suffix, needle in line, class, reason) -- s7346 review
    ("upstream_compat.cpp", "wa < a + (uint32_t)w; wa += 4u", "H", "s7777_access: w = guest access width 1..8 from the recompiled load/store hook (rs64_s7484_load/rs64_s7475_store), never negative; ROGUESQ_S7777_DANGLE-gated"),
    ("dpc_bridge.cpp", "u.hi - u.lo", "H", "unsigned WmUndo{lo,hi}: pushed from g_deferred_ranges r.first<r.second (submit_hi <= submit_lo dropped at :6793), hi only grows"),
    ("dpc_bridge.cpp", "r.second - r.first", "H", "unsigned pair; submit_hi <= submit_lo dropped at :6793 before the push; shadow entry needs hi-lo <= cap"),
    ("dpc_bridge.cpp", "x < r.second", "H", "unsigned pair, r.first < r.second (:6793); rstat-gated stats loop"),
    ("s7331_reset_writer.cpp", "memcpy(c, g, n)", "U", "n = min(kLine, req - off) uint32 (multi-declarator); off < req since mark.size() = ceil(req/kLine)"),
    ("rt64_state.cpp", "(b1 - b0) * s.height", "D", "BandSource audit helper read() (rs64 band census, env-gated callers); uint32 fields, b1 >= b0"),
    ("rt64_state.cpp", "y < s.height", "D", "BandSource audit helper (uint32 height)"),
    ("rt64_framebuffer_renderer.cpp", "r.end - r.begin", "H", "RenderRange r(0, pitch*height): end >= begin by construction (uint64)"),
    ("rsp_vu_impl.hpp", "n < cnt", "U", "u32 multi-declarator, cnt = (16 - (address & 15)) / 4 in 0..4"),
    ("rt64_command_warning.cpp", "resize(size_t(reqSize))", "FIX", "[s7346] reqSize < 0 clamped before resize; +1 buffer for vsnprintf"),
]

def length_of(l, mm):
    """the length expression of the sink match, or None."""
    k = mm.end()
    g = mm.group(1) or mm.group(2)
    if g in ("memcpy", "memmove", "memset"):
        a = s43.args_of(l, k); return a[2] if len(a) > 2 else None
    if g in ("fread", "fwrite"):
        a = s43.args_of(l, k); return (a[1] + " * " + a[2]) if len(a) > 2 else None
    if g in ("malloc",):
        a = s43.args_of(l, k); return a[0] if a else None
    if g in ("calloc",):
        a = s43.args_of(l, k); return (a[0] + " * " + a[1]) if len(a) > 1 else None
    if g in ("realloc",):
        a = s43.args_of(l, k); return a[1] if len(a) > 1 else None
    if g in ("resize", "reserve"):
        a = s43.args_of(l, k); return a[0] if a else None
    if g == "assign":
        a = s43.args_of(l, k); return a[0] if len(a) == 2 else None   # assign(count, value) only
    if mm.group(0).startswith("new"):
        a = s43.args_of(l.replace("[", "(", 1)[0:], k) if False else None
        depth, out = 0, ""
        for ch in l[k:]:
            if ch == "[": depth += 1
            elif ch == "]":
                if depth == 0: return out.strip()
                depth -= 1
            out += ch
        return None
    # for (unsigned i = ..; cond; ..): every `<`/`<=` bound in cond whose left side mentions the index
    fm = re.match(r"\bfor\s*\(\s*[\w\s]+?\s+(\w+)\s*=\s*[^;]*;([^;]*);", l[mm.start():])
    if not fm: return None
    v, cond = fm.group(1), fm.group(2)
    bs = []
    for part in re.split(r"&&|\|\|", cond):
        cm = re.match(r"\s*\(?\s*([^<>]*\b%s\b[^<>]*?)\s*(<=?)\s*(.+?)\s*\)?\s*$" % re.escape(v), part)
        if cm: bs.append(cm.group(3).strip())
    return " | ".join(bs) if bs else None

def idents(expr):
    e = re.sub(r"\bsizeof\s*\([^()]*\)", "", expr)
    e = re.sub(r"\b\w+(?:\[[^\]]*\])?\s*(?:->|\.)\s*\w+(?:\s*\([^()]*\)?)?", " ", e)   # object.member: typed by member_types()
    e = re.sub(r"(->|\.)\s*\w+(?:\s*\([^()]*\)?)?", " ", e)
    return [t for t in re.findall(r"(?<![\w.>])([A-Za-z_]\w*)", e) if t not in KW and not t.isupper()]

_HDR = None
def hdr_text():
    global _HDR
    if _HDR is None:
        pats = ["src/**/*.h", "src/**/*.hpp", "lib/rt64/src/**/*.h", "lib/N64ModernRuntime/**/*.h", "lib/N64ModernRuntime/**/*.hpp", "include/**/*.h"]
        seen, txt = set(), []
        for pat in pats:
            for f in ROOT.glob(pat):
                if f not in seen: seen.add(f); txt.append(f.read_text(errors="replace"))
        _HDR = {}
        for t in txt:
            for mm in re.finditer(r"^\s*((?:const\s+)?(?:unsigned\s+|signed\s+)?[\w:]+)\s+(\w+)\s*(?:=[^;]*)?;", t, re.M):
                if mm.group(1) not in ("return", "using", "typedef", "delete", "goto", "case"): _HDR.setdefault(mm.group(2), mm.group(1))
    return _HDR

def member_types(expr, ftext):
    """declared types of struct members used in expr (search the file for `T member;`)."""
    out = []
    for mem in re.findall(r"(?:->|\.)\s*(\w+)\b(?!\s*\()", expr):
        t = s44.decl(mem, ftext) or hdr_text().get(mem)
        out.append((mem, t))
    return out

def lower_bounded(v, body):
    e = re.escape(v)
    return bool(re.search(r"\b%s\s*<\s*0\b|\b%s\s*<=\s*0\b|\b%s\s*>=\s*0\b|\b%s\s*>\s*0\b|0\s*>\s*%s\b|0\s*<\s*%s\b|0\s*>=\s*%s\b|"
                          r"\b%s\s*=\s*(?:std::)?max\s*\(|\b%s\s*=\s*(?:std::)?(?:clamp|abs)\s*\(|\b%s\s*>=?\s*1\b" % ((e,) * 10), body))

def msk_source(v, body):
    e = re.escape(v)
    mm = None
    for mm in re.finditer(r"\b%s\s*=\s*([^;]+);" % e, body): pass
    if not mm: return False
    rhs = mm.group(1)
    return bool(re.search(r"&\s*(?:0x[0-9A-Fa-f]+|\d+)[uU]?\s*\)?\s*$|^\(?\s*MEM_(?:BU|HU)\b|^\(?\s*(?:uint8_t|uint16_t)\b|>>\s*(?:[89]|[12]\d)\b", rhs.strip()))

def diff_ordered(expr, body):
    """every `a - b` in expr has a preceding ordering check between a and b (or a max/min wrap)."""
    ds = re.findall(r"([\w\.\->\[\]]+)\s*-\s*([\w\.\->\[\]]+)", expr)
    if not ds: return True
    for a, b in ds:
        if re.fullmatch(r"\d+|0x[0-9A-Fa-f]+", b) and re.fullmatch(r"\d+", a or "x") is None:
            if not re.search(r"\b%s\s*(?:>=?|<=?|==|!=)\s*" % re.escape(a), body) and not lower_bounded(a, body): return False
            continue
        ea, eb = re.escape(a), re.escape(b)
        if not re.search(r"%s\s*(?:<=?|>=?)\s*%s|%s\s*(?:<=?|>=?)\s*%s" % (ea, eb, eb, ea), body): return False
    return True

st = {"sinks": 0, "nolen": 0, "nolen_rows": [], "untyped": []}
def census(files, pgf):
    rows = []; seen = set()
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = s43.ln_fn(p); ftext = "\n".join(lines); names = s42.names_of(lines)
        m.MASK = SINK
        for (ln, fn, mk, c, text) in m.sites(p, pgf):
            l = lines[ln - 1].split("//")[0]
            if l.lstrip().startswith("#"): continue
            for mm in SINK.finditer(l):
                if l[:mm.start()].count('"') % 2: continue
                st["sinks"] += 1
                lj = l + " " + " ".join(x.split("//")[0].strip() for x in lines[ln:ln + 4])   # multi-line call args
                n = length_of(lj, mm)
                if not n: st["nolen"] += 1; st["nolen_rows"].append(f"{rel}:{ln}"); continue
                if (rel, ln, n) in seen: continue
                seen.add((rel, ln, n))
                one(rel, ln, fn, c, text, l, mm, n, lines, fns, ftext, names, rows)
    return rows

def one(rel, ln, fn, c, text, l, mm, n, lines, fns, ftext, names, rows):
            pass
            start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
            ids = idents(n); mems = member_types(n, ftext)
            types = {v: (s44.decl(v, body) or s44.decl(v, ftext) or hdr_text().get(v)) for v in ids}
            signed = [v for v, t in types.items() if t and SIGNED.match(re.sub(r"\s+", " ", t.strip()))]
            signed += [mem for mem, t in mems if t and SIGNED.match(t.strip())]
            sub = bool(re.search(r"[\w\)\]]\s*-\s*[\w\(]", re.sub(r"->", "@", n)))
            unk = [v for v, t in types.items() if not t and not re.search(r"\b%s\b[\w\.\->\[\]]*\.size\(\)" % re.escape(v), n)] + \
                  [mem for mem, t in mems if not t]
            if unk and not signed and not sub: st["untyped"].append(f"{rel}:{ln} {','.join(unk)} :: {n.strip()[:50]}")
            if not signed and not sub: return
            if c in "GD" and rel.startswith("lib/rt64/") and not s43.body_gated(lines, ln): c = "?"
            if c == "D" and fn in CORE: c = "?"
            why = ""
            if c == "?":
                hh = s43.hand(rel, fn, text, HAND)
                if hh: c, why = hh
                elif s42.ev(n, names) is not None or s43.SIZEOF.match(n): c, why = "K", "constant length"
                elif mm.group(0).startswith("for"):
                    c, why = "?", "unsigned loop index vs signed bound"
                else:
                    plain = [v for v in signed if v in types]
                    ok = all(lower_bounded(v, body) or msk_source(v, body) for v in plain)
                    okm = all(lower_bounded(mem, body) for mem in signed if mem not in types)
                    if ok and okm and (not sub or diff_ordered(n, body)):
                        c, why = ("MSK" if any(msk_source(v, body) for v in plain) else "LB"), "lower bound / unsigned source before sink"
                    elif not signed and sub and diff_ordered(n, body):
                        c, why = "LB", "difference operands ordered before sink"
            rows.append((rel, ln, fn, c, why, n.strip()[:60], ",".join(signed) + ("|sub" if sub else ""), text))

PLANT = ("static void planted(uint8_t* rdram, uint8_t* b, OSTask* task) {\n    int n = (int)task->size;\n"
         "    if (n > 0x1000) return;\n    memcpy(b, rdram, n);\n}\n"
         "static void lb_twin(uint8_t* rdram, uint8_t* b, OSTask* task) {\n    int n = (int)task->size;\n"
         "    if (n < 0 || n > 0x1000) return;\n    memcpy(b, rdram, n);\n}\n"
         "static void uns_twin(uint8_t* rdram, uint8_t* b, OSTask* task) {\n    uint32_t n = task->size;\n"
         "    if (n > 0x1000) return;\n    memcpy(b, rdram, n - 0);\n}\n"
         "static void gated_twin(uint8_t* rdram, uint8_t* b, OSTask* task) {\n    if (!rs64_dlwalk_on()) return;\n"
         "    int n = (int)task->size;\n    if (n > 0x1000) return;\n    memcpy(b, rdram, n);\n}\n")

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text(PLANT)
        got = {(r[2], r[3]) for r in census([t], pgf)}
        want = {("planted", "?"), ("lb_twin", "LB"), ("uns_twin", "LB"), ("gated_twin", "G")}
        assert got == want, f"control failed: {got ^ want}"
        print("[s7346] controls: planted int n '?', lower-bounded twin 'LB', unsigned twin (n - 0) 'LB', gated twin 'G'")
    files = s43.files_in_scope()
    rows = census(files, pgf)
    cc = Counter(r[3] for r in rows)
    print(f"[s7346] sinks={st['sinks']} no-length-parsed={st['nolen']}")
    print(f"[s7346] sinks with an untyped length variable (no signed decl found): {len(st['untyped'])}")
    if "--untyped" in sys.argv: print("\n".join("  " + x for x in st["untyped"]))
    if "--nolen" in sys.argv: print("  " + " ".join(st["nolen_rows"]))
    print(f"[s7346] class W sites={len(rows)} files={len(files)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[3] in "?B" or "-v" in sys.argv or ("-h" in sys.argv and r[3] == "H"):
            print(f"  {r[3]} {r[0]}:{r[1]} {r[2]} [{r[6]}] {r[4]} :: {r[5]} :: {r[7][:100]}")
    w = (ROOT / "lib/rt64/src/hle/rt64_command_warning.cpp").read_text()
    fix = "if (reqSize < 0) reqSize = 0;" in w and "size_t(reqSize) + 1" in w
    print(f"[s7346] CommandWarning::format fix present: {fix}")
    bad = [r for r in rows if r[3] in ("?", "B")] + ([] if fix else [("fix-missing",)])
    print(f"[s7346] unclassified/defect: {len(bad)}")
    bad = list(bad) + census_rules.report("s7346")  # s7654: a stale shared rule fails the gate (after the row printers)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
