#!/usr/bin/env python3
"""s7349 class Z census: shift by a guest-derived count with no range check.
`x << n` / `x >> n` with n >= the promoted operand width or n < 0 is UB in C++ (arm64/x86 mask the count, but clang may fold
assuming n < width); `1 << 31` on a signed int was UB before C++20 (implementation-defined since; not counted).
Scope = s7343 files_in_scope(). A site = a binary `<<` / `>>` (not a comment, string, stream insertion/extraction, template
close, `<<=`/`>>=` handled as sites too) whose count is not a literal / constexpr (s7342 ev()).
Classes: C/P/G/D from tools/s7338_mask_census.py sites() (rt64 G/D re-checked with s7343 body_gated(); CORE demotion as s7344)
  K   constant count            S   stream / template / not a shift   -- counted, not sites
  MSK count masked (`& 0x1F` .. `& 1`, `% 32`) or a narrow bitfield-extracted variable whose max < operand width
  RC  count range-checked before the op (`n < 32`, `n >= 32` return, min(n, ..), clamp)
  LP  loop induction variable bounded by a constant < width
  H   hand-verified (reason in HAND)   FIX fixed this session   B default-on guest count unchecked (defect)   ?  unclassified
'?' or B => exit 1. --controls plants `uint32_t n = tile->shifts; return x << n;` ('?'), the masked twin ('MSK'), the checked
twin ('RC'), a gated twin ('G') and a stream twin (`std::cout << n`, not a site)."""
import re, sys, pathlib, importlib.util
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
def _load(name, f):
    s = importlib.util.spec_from_file_location(name, ROOT / f); mod = importlib.util.module_from_spec(s); s.loader.exec_module(mod); return mod
s48 = _load("s7348", "tools/s7348_div_census.py")
s47, s46, s44, s43, s42, m = s48.s47, s48.s46, s48.s44, s48.s43, s48.s42, s48.m

SH = re.compile(r"(?<=[\w)\]\s])\s*(<<|>>)=?(?![<>])\s*")
KCONST = s48.KCONST
STREAMV = re.compile(r"(?:^|::|\b)(?:std::)?(?:cout|cerr|clog|cin|os|ss|oss|iss|out|stream|s|str|o|f|file|log|buf|msg|sstr|"
                     r"\w*[Ss]tream\w*|fmt|w|writer|\w+_ss|\w+_os|sout|dbg|line|ostr|key|text|desc|txt|name|report|result)$")
HAND = [  # (file suffix, needle in line, class, reason) -- s7349 review
    ("math_routines.cpp", "(b & 63)", "FIX", "[s7349] __ull_rshift/__ll_lshift: guest 64-bit count masked & 63 (MIPS dsrlv/dsllv); was C UB for >= 64"),
    ("main.cpp", "val >> (24 - 8*i)", "LP", "for i < 4 byte loop (ROGUESQ dlwalk dump)"),
    ("main.cpp", "val >> (24 - j * 8)", "LP", "for j < 4 byte loop (ROGUESQ_LOG_SEQ)"),
    ("main.cpp", "1ull << (width * 8u)", "RC", "inside width < 8 (width 1/2/4 from the insn switch)"),
    ("upstream_compat.cpp", "s7046_mask >> p", "H", "p = s7030_ph phase index (< array dim of s7046_k2), env-tuned mask"),
    ("threads.cpp", "m[2]", "S", "template close std::map<..>> m[2], not a shift"),
    ("dp.cpp", "1U <<", "H", "update_bit(): bit is an RDPStatusBit enum constant <= 10 at every call site, so 2*bit+1 <= 21"),
    ("mod_manifest.cpp", "input_file >>", "S", "ifstream >> json"),
    ("mods.cpp", "input_file >>", "S", "ifstream >> json"),
    ("rt64_user_configuration.cpp", "stream >> jroot", "S", "ifstream >> json"),
    ("librecomp/src/rsp.cpp", "(index + 512) >>", "H", "count is 0 or 1 (index % 2 ?:)"),
    ("s7331_reset_writer.cpp", "1u << (ph * 3 + w)", "H", "ph in {0,1}, w < W_N = 3 -> count <= 5"),
    ("rt64_gbi.cpp", "", "H", "_SHIFTL/_SHIFTR macro bodies: every use passes literal pos/bits"),
    ("rt64_gbi_s2dex.cpp", "", "H", "S2DEX HLE module: the port runs the F5 gfx ucode LLE, RT64 gets RDP commands only (never dispatched)"),
    ("rt64_rsp.cpp", "(((uint64_t)(1) << size) - 1) << off", "H", "HLE RSP setOtherMode (LLE port never runs it)"),
    ("rt64_gbi_f3dfactor5.cpp", "1u << (length + 1)", "RC", "inside length + 1 >= 32 ? 0xFFFFFFFF :"),
    ("rt64_color_converter.cpp", "exponent", "MSK", "exponent = (src & 0xE000) >> 13 <= 7; mantissa shift 6 - min(6, e)"),
    ("rt64_framebuffer_manager.cpp", "sizDifference", "RC", "sizDifference computed inside dstSiz > srcSiz (or the converse) of 2-bit siz fields: 1..3"),
    ("rt64_state.cpp", "1 << sizDifference", "RC", "sizDifference inside reinterpretSiz > loadTile.siz (2-bit fields): 1..3"),
    ("rt64_state.cpp", "1 << mask", "MSK", "clampAlignedToMask(tile.masks/maskt): RDP 4-bit mask field (p1(4,4)/p1(14,4)) <= 15"),
    ("rt64_framebuffer_manager.cpp", "<< pixelShift", "MSK", "pixelShift = (siz == 0) ? 1 : 0 style from the 2-bit siz (s7348 tile copy)"),
    ("rt64_rdp.cpp", "imageWidth << G_IM_SIZ_16b", "K", "G_IM_SIZ_16b constant"),
    ("rt64_rdp.cpp", "<< wordShift", "MSK", "wordShift = RGBA32 ? 2 : 3 (or 0 : 1)"),
    ("rt64_rdp.cpp", "(4 - tiles[tile].siz)", "MSK", "RDP 2-bit siz field -> count 1..4"),
    ("rsp_vu.hpp", "1ull << (bits - 1)", "H", "sclamp/sclip<bits> template constant (16/32/48)"),
    ("rsp_vu_impl.hpp", "+ n)", "LP", "CFC2/CTC2 for n < 8 lane loop"),
    ("rsp_vu_impl.hpp", "u64(data) << shift", "MSK", "shift = clz(data) of a nonzero u32 <= 31, u64 operand"),
    ("rsp_vu_impl.hpp", "31 - shift >> 1", "MSK", "shift = clz(nonzero) <= 31 -> (31 - shift) >> 1 in 0..15"),
]
# RDP siz is a 2-bit DL field (rt64_gbi_rdp.cpp p0(19, 2)); masks/maskt 4-bit (p1(4, 4) / p1(14, 4)); every rt64 struct siz is
# copied from those, from fbSiz() (VI type -> G_IM_SIZ_*), or a G_IM_SIZ_* constant (s7349 grep of every `siz =`).
SIZF = re.compile(r"^\(?\s*(?:\(\s*(?:\d+|RGBA32\s*\?[^)]*)\s*\+?\s*\w*\s*\)\s*-\s*)?(?:\d+\s*[-+]\s*)?(?:(?:[\w.]+(?:->|\.))?(?:siz|Siz|masks|maskt|screenFbSiz)|RGBA32\s*\?\s*G_IM_SIZ_\w+\s*:\s*[\w.]+siz|[\w.]*siz\s*==\s*3\s*\?\s*2\s*:\s*[\w.]*siz)\s*\)?$")
MASKMAX = re.compile(r"&\s*(0x[0-9A-Fa-f]+|\d+)[uUlL]*\s*\)*$")
def mask_max(d):
    mo = MASKMAX.search(d)
    if mo: return int(mo.group(1), 0)
    mo = re.search(r"%\s*(\d+)\s*\)*$", d)
    if mo: return int(mo.group(1)) - 1
    return None

def var_max(v, body):
    """max value of local v from its assignment(s) in body: `v = .. & 0xF`, `v = (x >> k) & m`, narrow bitfield `: N`."""
    e = re.escape(v); mx = None
    for a in re.finditer(r"\b%s\s*(?:=|\{)\s*([^;]+);" % e, body):
        rhs = a.group(1).strip().rstrip("}").strip()
        k = mask_max(rhs)
        if k is None:
            if KCONST.match(rhs) or s42.ev(rhs) is not None:
                try: k = int(s42.ev(rhs) or 0)
                except Exception: k = None
            if k is None: return None
        mx = k if mx is None else max(mx, k)
    for a in re.finditer(r"\b%s\s*&=\s*(0x[0-9A-Fa-f]+|\d+)" % e, body):
        k = int(a.group(1), 0); mx = k if mx is None else min(mx, k)
    return mx

def range_checked(v, body, pre):
    e = re.escape(v)
    pat = (r"\b%s\s*<\s*(?:\d+|\w+)|\b%s\s*>=?\s*(?:\d+|\w+)\s*\)\s*(?:return|continue|break|\{|%s\s*=)|\b%s\s*=\s*(?:std::)?(?:min|clamp)\b|"
           r"\bstd::(?:min|clamp)(?:<\w+>)?\s*\(\s*%s\b|\b%s\s*<=\s*\d+|\b%s\s*>\s*\d+\s*\?|\bassert\s*\([^;]*\b%s\b" % ((e,) * 8))
    return re.search(pat, body) or re.search(pat, pre)

def loop_var(v, body):
    e = re.escape(v)
    mo = re.search(r"for\s*\([^;]*\b%s\s*=\s*[^;]*;\s*%s\s*(<=?)\s*([^;]+);" % (e, e), body)
    if not mo: return None
    b = mo.group(2).strip()
    k = s42.ev(b)
    if k is None and re.fullmatch(r"\d+[uU]?", b): k = int(b.rstrip("uU"))
    if k is None: return None
    return int(k) - (1 if mo.group(1) == "<" else 0)

def width(lhs, body, ftext):
    if re.search(r"\b(?:u?int64_t|uint64|u64|s64|size_t|uintptr_t|long long|ULL|ull|LL)\b|\d+ull\b|\d+ULL\b|\d+ll\b", lhs): return 64
    b = s44.base(lhs) if lhs else ""
    t = (s44.decl(b, body) or s44.decl(b, ftext)) if b and re.fullmatch(r"\w+", b) else None
    if t and re.search(r"64|size_t|uintptr|long long|u64|s64", t): return 64
    return 32

st = {"raw": 0, "K": 0, "S": 0}
def census(files, pgf):
    rows = []
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = s43.ln_fn(p); ftext = "\n".join(lines)
        names = s42.names_of(lines)
        m.MASK = SH
        done = set()
        for (ln, fn, mk, c, text) in m.sites(p, pgf):
            raw = lines[ln - 1]
            l = re.sub(r'"(?:\\.|[^"\\])*"', lambda q: '"' + "_" * (len(q.group(0)) - 2) + '"', raw)
            l = re.sub(r"'(?:\\.|[^'\\])'", "'_'", l)
            ci = l.find("//")
            if ci >= 0: l = l[:ci] + " " * (len(l) - ci)
            ci = l.find("/*")
            if ci >= 0: l = l[:ci] + " " * (len(l) - ci)
            if l.lstrip().startswith(("#", "*")): continue
            for mm in SH.finditer(l):
                if (ln, mm.start(1)) in done: continue
                done.add((ln, mm.start(1)))
                if mm.start(1) >= len(l.rstrip()): continue
                d0 = s48.rhs_of(l, mm.end())
                lhs = s48.lhs_of(l, mm.start(1))
                after = l[mm.end():].lstrip()
                if not d0 or not lhs or after.startswith('"'):
                    st["S"] += 1; continue
                if re.match(r"^(?:return|case|else|if|while|operator)$", lhs) or "operator" in l[max(0, mm.start(1) - 10):mm.start(1)]:
                    st["S"] += 1; continue
                if mm.group(1) == "<<" and (STREAMV.search(lhs) or re.search(r"std::(?:cout|cerr|endl|hex|dec|setw)|<<\s*\"|\"\s*<<|<<\s*std::", l)):
                    st["S"] += 1; continue
                if mm.group(1) == ">>" and re.search(r"<[^<>;()]*>?>>\s*[\w:]*\s*(?:[;=,\{&*]|\w+\s*[;=({,)])", l[:mm.end() + 40]) and re.search(r"\w<", l[:mm.start(1)]):
                    st["S"] += 1; continue
                st["raw"] += 1
                d = s48.strip_div(d0)
                start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
                if KCONST.match(d) or (names is not None and s42.ev(d, names) is not None) or s42.ev(d) is not None:
                    st["K"] += 1; continue
                w = width(lhs, body, ftext)
                cc, why = c, ""
                if cc in "GD" and rel.startswith("lib/rt64/") and not s43.body_gated(lines, ln): cc = "?"
                if cc == "D" and fn in s44.CORE: cc = "?"
                if cc == "?":
                    hh = s43.hand(rel, fn, raw.strip(), HAND)
                    mx = mask_max(d)
                    v = d if re.fullmatch(r"\w+", d) else None
                    if hh and hh[0] in ("S", "K"): st[hh[0]] += 1; continue
                    if hh: cc, why = hh
                    elif SIZF.match(d) and not re.search(r"siz\w*\s*-\s*1", d): cc, why = "MSK", "RDP siz 2-bit / mask 4-bit field"
                    elif re.search(r"[sS]iz\w*\s*-\s*1", d) and re.search(r"[sS]iz\s*==\s*0\s*\?|[sS]iz\s*>=\s*G_IM_SIZ_16b|[sS]iz\s*>=\s*[12]\b", body + "\n" + l[:mm.start(1)]):
                        cc, why = "RC", "siz - 1 behind siz == 0 ? / siz >= G_IM_SIZ_16b"
                    elif mx is not None and mx < w: cc, why = "MSK", f"count <= {mx} < {w}"
                    elif v and (vm := var_max(v, body)) is not None and vm < w: cc, why = "MSK", f"{v} <= {vm} < {w}"
                    elif v and (lv := loop_var(v, body)) is not None and lv < w: cc, why = "LP", f"{v} <= {lv}"
                    elif v and range_checked(v, body, l[:mm.start(1)]): cc, why = "RC", f"{v} checked"
                rows.append((rel, ln, fn, cc, why, f"{lhs[-30:]} {mm.group(1)} {d0}"[:80], raw.strip(), w))
    return rows

PLANT = ("static uint32_t planted(Tile* tile, uint32_t x) {\n    uint32_t n = tile->shifts;\n    return x << n;\n}\n"
         "static uint32_t msk_twin(Tile* tile, uint32_t x) {\n    uint32_t n = tile->shifts & 0xF;\n    return x << n;\n}\n"
         "static uint32_t rc_twin(Tile* tile, uint32_t x) {\n    uint32_t n = tile->shifts;\n    if (n >= 32) return 0;\n    return x >> n;\n}\n"
         "static uint32_t gated_twin(Tile* tile, uint32_t x) {\n    if (!rs64_dlwalk_on()) return 0;\n    uint32_t n = tile->shifts;\n    return x << n;\n}\n"
         "static void stream_twin(Tile* tile) {\n    uint32_t n = tile->shifts;\n    std::cout << n;\n}\n")

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text(PLANT)
        got = {(r[2], r[3]) for r in census([t], pgf)}
        want = {("planted", "?"), ("msk_twin", "MSK"), ("rc_twin", "RC"), ("gated_twin", "G")}
        assert got == want, f"control failed: {got ^ want}"
        print("[s7349] controls: planted x << tile->shifts '?', masked twin 'MSK', checked twin 'RC', gated twin 'G', stream twin excluded")
        for k in st: st[k] = 0
    files = s43.files_in_scope()
    rows = census(files, pgf)
    cc = Counter(r[3] for r in rows)
    print(f"[s7349] raw shifts={st['raw']} constant-count={st['K']} stream/template={st['S']}")
    print(f"[s7349] class Z sites={len(rows)} files={len(files)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[3] in "?B" or "-v" in sys.argv or ("-h" in sys.argv and r[3] in ("H", "FIX")):
            print(f"  {r[3]} {r[0]}:{r[1]} {r[2]} w{r[7]} {r[4]} :: {r[5]}")
    mr = (ROOT / "lib/N64ModernRuntime/librecomp/src/math_routines.cpp").read_text()
    fix = "uint64_t ret = a >> (b & 63);" in mr and "uint64_t ret = a << (b & 63);" in mr
    print(f"[s7349] fix present: guest 64-bit shift helpers count & 63 {fix}")
    bad = [r for r in rows if r[3] in ("?", "B")] + ([] if fix else [("fix-missing",)])
    print(f"[s7349] unclassified/defect: {len(bad)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
