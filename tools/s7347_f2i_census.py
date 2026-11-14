#!/usr/bin/env python3
"""s7347 class X census: float-to-integer conversions whose result reaches an index / size / loop-bound sink.
NaN, +-inf or |f| >= 2^31 converted with (int)f / static_cast<int> / int32_t(f) / lround / lrint is UB in C++; arm64
fcvtzs saturates (NaN -> 0, huge -> INT_MAX / INT_MIN), lrint returns a long that a later (int32_t) wraps. A guest-derived
NaN camera / vertex / scale value would then become INT_MIN as an array index or ~2^32 as a size.
Scope = s7343 files_in_scope(). A site = a conversion (C cast, functional cast, static_cast, l/ll round/rint) whose operand is
float-typed (float literal, float math call, (float)/(double) inner, ctx->f*, or an identifier / member declared float/double/
vec) AND whose result reaches a sink: it sits inside `[...]` or in the length argument of memcpy/memmove/memset/resize/reserve/
new[]/malloc/calloc/realloc on the same line, or is assigned to a variable that reaches such a sink or a `for` bound within 40
lines. Conversions that only feed arithmetic, comparisons, struct fields or calls are counted (NS) but not sites.
Classes: C/P/G/D from tools/s7338_mask_census.py sites() (rt64 G/D re-checked with s7343 body_gated())
  CL  clamped: std::clamp/min/max around the operand or the result, or the result variable is range-checked (lower AND upper,
      upper only for unsigned targets) between the conversion and the sink
  FIN isfinite/isnan check on the operand before the conversion
  H   hand-verified (reason in HAND)    B default-on, guest-derived float, unclamped (defect)    ?  unclassified
'?' or B => exit 1. --controls plants `float f = guest_f(); int i = (int)f; tab[i] = 1;` ('?'), the clamped twin ('CL'),
the isfinite twin ('FIN') and a gated twin ('G')."""
import re, sys, pathlib, importlib.util
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
def _load(name, f):
    s = importlib.util.spec_from_file_location(name, ROOT / f); mod = importlib.util.module_from_spec(s); s.loader.exec_module(mod); return mod
s46 = _load("s7346", "tools/s7346_signed_len_census.py")
s45 = _load("s7345", "tools/s7345_mul_census.py")
s44, s43, s42, m = s46.s44, s46.s43, s46.s42, s46.m

IT = r"(?:int|int8_t|int16_t|int32_t|int64_t|uint8_t|uint16_t|uint32_t|uint64_t|s8|s16|s32|s64|u8|u16|u32|u64|size_t|long|unsigned(?:\s+int)?|short|ssize_t|ptrdiff_t|intptr_t|uintptr_t)"
CONV = re.compile(r"\(\s*%s\s*\)\s*|static_cast\s*<\s*%s\s*>\s*\(|(?<=[=\[(,+\-*/ ])%s\s*\(|\bl?l?(?:round|rint)f?\s*\(" % (IT, IT, IT))
SINKCALL = re.compile(r"\b(?:std::)?(?:memcpy|memmove|memset|malloc|calloc|realloc)\s*\(|\.(?:resize|reserve|assign)\s*\(|\bnew\s+[\w:<>]+\s*\[")
FLOATLIT = re.compile(r"(?<![\w.])\d+\.\d*(?:[eE][-+]?\d+)?f?\b|(?<![\w.])\d+f\b|(?<![\w.])\.\d+f?\b")
HAND = [  # (file suffix, needle in line, class, reason) -- s7347 review
    ("rt64_state.cpp", "uint32_t(screenFbSize.x) * bpp", "H", "screenFbSize is hlslpp::uint2 (VI::fbSize): unsigned->unsigned, not a float conversion"),
    ("upstream_compat.cpp", "dd < 128.0f ? (int)(dd / 8.0f) : 16", "FIX", "[s7347] dd = sqrtf(..) of guest eye floats: NaN / huge now -> bin 16, (int) only on 0 <= dd < 128"),
]

def operand(l, mm):
    """operand text of the conversion match."""
    g = mm.group(0)
    k = mm.end()
    if g.rstrip().endswith("(") and not re.match(r"\(\s*%s\s*\)" % IT, g):
        a = s43.args_of(l, k); return a[0] if a else ""
    # C cast: following primary expression (unary minus, identifier chain, balanced groups)
    i, out = k, ""
    while i < len(l) and l[i] in " -!~*&": out += l[i]; i += 1
    while i < len(l):
        ch = l[i]
        if ch in "([":
            close = {"(": ")", "[": "]"}[ch]; depth = 0; j = i
            while j < len(l):
                if l[j] in "([": depth += 1
                elif l[j] in ")]":
                    depth -= 1
                    if depth == 0: break
                j += 1
            out += l[i:j + 1]; i = j + 1; continue
        mo = re.match(r"[\w.]+|->|::", l[i:])
        if mo: out += mo.group(0); i += len(mo.group(0)); continue
        break
    return out.strip()

def is_float(op, body, ftext):
    if not op: return False
    if FLOATLIT.search(op) or s45.FLOATCALL.search(op) or re.search(r"\(\s*(?:float|double)\s*\)|\bfloat\s*\(|\bdouble\s*\(|static_cast\s*<\s*(?:float|double)|ctx->f\d|\.fl\b|\.fh\b|\.d\b", op):
        return True
    ids = s46.idents(op)
    for v in ids:
        t = s44.decl(v, body) or s44.decl(v, ftext) or s46.hdr_text().get(v)
        if t and s45.FLOATT.match(re.sub(r"\s+", " ", t.strip())): return True
    for mem, t in s46.member_types(op, ftext):
        if t and s45.FLOATT.match(t.strip()): return True
    # hlslpp / vec components: a.x / v.y / m[i][j] of a float vector
    for v in re.findall(r"(\w+)(?:\[[^\]]*\])*\s*\.\s*[xyzw]\b", op):
        t = s44.decl(v, body) or s44.decl(v, ftext)
        if t and re.search(r"float|hlslpp|vec|Vec|interop", t): return True
    return False

def in_index(l, pos):
    d = 0
    for ch in l[:pos]:
        if ch == "[": d += 1
        elif ch == "]": d -= 1
    return d > 0

def in_sinkcall(l, pos):
    for sm in SINKCALL.finditer(l):
        if sm.start() < pos:
            a = s43.args_of(l, sm.end()); end = sm.end() + sum(len(x) + 1 for x in a)
            if pos < end: return True
    return False

def wrapped_clamp(l, pos):
    pre = l[:pos]
    return bool(re.search(r"(?:std::)?(?:clamp|min|max)\s*(?:<[^>]*>)?\s*\([^;]*$", pre))

def target_var(l, pos):
    mo = re.match(r"^\s*(?:(?:const\s+|static\s+)*([\w:]+)\s+)?(\w+)\s*(?:\[[^\]]*\])?\s*[+\-]?=(?!=)", l)
    if mo and mo.end() <= pos: return mo.group(2), mo.group(1)
    return None, None

def var_sink(v, lines, ln, end, pos=0):
    e = re.escape(v)
    for j in range(ln - 1, min(end, ln + 40)):
        l = lines[j].split("//")[0]
        if j == ln - 1:   # same line: only the statements after the assignment's ';'
            k = l.find(";", pos)
            if k < 0: continue
            l = " " * (k + 1) + l[k + 1:]
        if not re.search(r"\b%s\b" % e, l): continue
        if re.search(r"^\s*(?:[\w:]+\s+)?%s\s*=(?!=)" % e, l) and not re.search(r"\b%s\b" % e, l.split("=", 1)[1]): return None  # reassigned
        for mo in re.finditer(r"\b%s\b" % e, l):
            if in_index(l, mo.start()) or in_sinkcall(l, mo.start()): return j + 1
        if re.search(r"\bfor\s*\(", l) and re.search(r"[<>]=?\s*%s\b" % e, l): return j + 1
    return None

def ranged(v, ty, between):
    e = re.escape(v)
    if re.search(r"\b%s\s*=\s*(?:std::)?(?:clamp|min|max)\s*(?:<[^>]*>)?\s*\(" % e, between): return True
    hi = re.search(r"\b%s\s*(?:>=?|<=?)\s*[\w(]|[\w)]\s*(?:>=?|<=?)\s*%s\b" % (e, e), between)
    lo = s46.lower_bounded(v, between) or (ty and re.match(r"(?:const\s+)?u", ty.strip()))
    return bool(hi and lo)

st = {"conv": 0, "float": 0, "ns": 0}
def census(files, pgf):
    rows = []
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = s43.ln_fn(p); ftext = "\n".join(lines)
        m.MASK = CONV
        done = set()
        for (ln, fn, mk, c, text) in m.sites(p, pgf):
            l = lines[ln - 1].split("//")[0]
            if l.lstrip().startswith("#"): continue
            for mm in CONV.finditer(l):
                if (ln, mm.start()) in done: continue
                done.add((ln, mm.start()))
                if l[:mm.start()].count('"') % 2: continue
                st["conv"] += 1
                start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
                op = operand(l, mm)
                if not ("round" in mm.group(0) or "rint" in mm.group(0)) and not is_float(op, body, ftext): continue
                st["float"] += 1
                sink, v, ty = None, None, None
                if in_index(l, mm.start()) or in_sinkcall(l, mm.start()): sink = ln
                else:
                    v, ty = target_var(l, mm.start())
                    if v:
                        end = next((j for j in range(ln, len(fns)) if fns[j][1] != start), len(lines))
                        sink = var_sink(v, lines, ln, end, mm.start())
                if not sink: st["ns"] += 1; continue
                cc, why = c, ""
                if cc in "GD" and rel.startswith("lib/rt64/") and not s43.body_gated(lines, ln): cc = "?"
                if cc == "D" and fn in s44.CORE: cc = "?"
                if cc == "?":
                    hh = s43.hand(rel, fn, text, HAND)
                    ids = s46.idents(op)
                    between = "\n".join(lines[ln - 1:sink])
                    if hh: cc, why = hh
                    elif re.search(r"(?:std::)?(?:clamp|min|max)\s*\(", op) or wrapped_clamp(l, mm.start()): cc, why = "CL", "clamp/min/max around operand or result"
                    elif v and ranged(v, ty, between): cc, why = "CL", f"{v} range-checked before sink"
                    elif v and re.search(r"(?:std::)?(?:clamp|min|max)\s*(?:<[^>]*>)?\s*\(\s*%s\b" % re.escape(v), lines[sink - 1]): cc, why = "CL", f"{v} clamped at the sink"
                    elif any(re.search(r"\bis(?:finite|nan|inf)\s*\(\s*%s\b" % re.escape(x), body) for x in ids): cc, why = "FIN", "isfinite/isnan on operand"
                rows.append((rel, ln, fn, cc, why, op[:60], f"{v or '-'}@{sink}", text))
    return rows

PLANT = ("static void planted(uint8_t* tab) {\n    float f = guest_f();\n    int i = (int)f;\n    tab[i] = 1;\n}\n"
         "static void cl_twin(uint8_t* tab) {\n    float f = guest_f();\n    int i = std::clamp((int)f, 0, 15);\n    tab[i] = 1;\n}\n"
         "static void fin_twin(uint8_t* tab) {\n    float f = guest_f();\n    if (std::isfinite(f) == false) return;\n    int i = (int)f;\n    tab[i] = 1;\n}\n"
         "static void gated_twin(uint8_t* tab) {\n    if (!rs64_dlwalk_on()) return;\n    float f = guest_f();\n    int i = (int)f;\n    tab[i] = 1;\n}\n"
         "static void ns_twin(uint8_t* tab) {\n    float f = guest_f();\n    int i = (int)f;\n    put(i);\n}\n")

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text(PLANT)
        got = {(r[2], r[3]) for r in census([t], pgf)}
        want = {("planted", "?"), ("cl_twin", "CL"), ("fin_twin", "FIN"), ("gated_twin", "G")}
        assert got == want, f"control failed: {got ^ want}"
        print("[s7347] controls: planted (int)f index '?', clamped twin 'CL', isfinite twin 'FIN', gated twin 'G', no-sink twin not a site")
        for k in st: st[k] = 0
    files = s43.files_in_scope()
    rows = census(files, pgf)
    cc = Counter(r[3] for r in rows)
    print(f"[s7347] conversions={st['conv']} float-operand={st['float']} no-sink={st['ns']}")
    print(f"[s7347] class X sites={len(rows)} files={len(files)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[3] in "?B" or "-v" in sys.argv or ("-h" in sys.argv and r[3] == "H"):
            print(f"  {r[3]} {r[0]}:{r[1]} {r[2]} [{r[6]}] {r[4]} :: {r[5]} :: {r[7][:100]}")
    u = (ROOT / "src/main/upstream_compat.cpp").read_text()
    fix = "dd < 128.0f ? (int)(dd / 8.0f) : 16" in u and "int b = (int)(dd / 8.0f); if (b > 16)" not in u
    print(f"[s7347] rs64_s7233_cell NaN-safe bin fix present: {fix}")
    bad = [r for r in rows if r[3] in ("?", "B")] + ([] if fix else [("fix-missing",)])
    print(f"[s7347] unclassified/defect: {len(bad)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
