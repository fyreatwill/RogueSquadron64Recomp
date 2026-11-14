#!/usr/bin/env python3
"""s7348 class Y census: integer division / modulo by a guest-derived divisor with no zero check.
x86 raises SIGFPE on an integer `/ 0` or `% 0`; arm64 udiv/sdiv return 0 silently (wrong value, no crash). INT_MIN / -1 is UB.
Scope = s7343 files_in_scope(). A site = a binary `/` or `%` (not a comment, string, `//`, `/=`-in-comment) whose right operand is
not a literal / sizeof / constexpr (s7342 ev()) and whose operands are not float (s7347 is_float(); `%` is never float).
Classes: C/P/G/D from tools/s7338_mask_census.py sites() (rt64 G/D re-checked with s7343 body_gated(); CORE demotion as s7344)
  K   constant divisor (UPPER_CASE / kName / constexpr / literal expression)
  F   float division (either operand float)        -- counted, not a site
  NZ  divisor checked before the op in the function (`!b`, `b == 0`, `b != 0`, `b > 0`, `b >= 1`, `b < 1`, `b <= 0`,
      max(1, ..) / max(.., 1), `?:` guard, `b ? a / b : ..`, `if (b)`)
  BC  nonzero by construction (`1 << n`, `x | 1`, `(x + 1)` of an unsigned, std::max(.., 1), size of a non-empty container
      guarded with empty())
  H   hand-verified (reason in HAND)   B default-on guest divisor unchecked (defect)   ?  unclassified
'?' or B => exit 1. --controls plants `uint32_t w = task->width; return off / w;` ('?'), the checked twin ('NZ'), the shift
twin ('BC') and a gated twin ('G')."""
import re, sys, pathlib, importlib.util
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
def _load(name, f):
    s = importlib.util.spec_from_file_location(name, ROOT / f); mod = importlib.util.module_from_spec(s); s.loader.exec_module(mod); return mod
s47 = _load("s7347", "tools/s7347_f2i_census.py")
s46, s45, s44, s43, s42, m = s47.s46, s47.s45, s47.s44, s47.s43, s47.s42, s47.m

DIV = re.compile(r"(?<=[\w)\]\s])\s*([/%])(?![/*=])\s*")
KCONST = re.compile(r"^\(?\s*(?:\d[\w.]*|0x[0-9A-Fa-f]+[uUlL]*|sizeof\b.*|[A-Z][A-Z0-9_]{1,}|k[A-Z]\w*|\w+::[A-Z]\w*|std::numeric_limits.*)\s*\)?$")
HAND = [   # (file suffix, needle in line, class, reason) -- s7348 review
    ("rt64_gbi_s2dex.cpp", "", "H", "S2DEX HLE module: the port runs the F5 gfx ucode LLE, RT64 gets RDP commands only (never dispatched)"),
    ("rt64_rsp.cpp", "/ vertexSize", "H", "HLE RSP vertex path (LLE port never runs it)"),
    ("main.cpp", "acc.slow_ucode / sn", "F", "sn is double (multi-declarator, `slow_n ? .. : 1.0`)"),
    ("main.cpp", "h = w / r", "F", "double window aspect"),
    ("upstream_compat.cpp", "int32_t q = a / b", "H", "s7239_fdiv: every caller passes a positive cell size (s7239 cell grid, literal / env >0)"),
    ("dpc_bridge.cpp", "sw % fg_every", "NZ", "fg_every = atoi(env) > 0 ? .. : 120"),
    ("events.cpp", "tb.denom", "H", "mach_timebase_info numer/denom: nonzero by the Mach API (1/1 on arm64)"),
    ("events.cpp", "tb.numer", "H", "mach_timebase_info numer/denom: nonzero by the Mach API (1/1 on arm64)"),
    ("mesgqueue.cpp", "% mq->msgCount", "H", "guest msgCount: osSendMesg/osRecvMesg reach the ring op only past the full check (validCount >= msgCount) / empty check (validCount == 0), so msgCount <= 0 never reaches it unless validCount is corrupted; arm64 x % 0 = x (no trap), and retail IDO code would trap (break 7)"),
    ("timer.cpp", "/ counter_per_ms", "K", "constexpr 46875 * speed_multiplier"),
    ("flash.cpp", "flash_size / sector_size", "K", "constexpr"),
    ("math_routines.cpp", "rs64_", "FIX", "[s7348] guest 64-bit divide helpers use MIPS ddiv/ddivu results for b == 0 and INT64_MIN / -1 (was C UB)"),
    ("math_routines.cpp", "return a / b;", "FIX", "[s7348] rs64_sdiv64: reached only after b == 0 and INT64_MIN / -1 returns"),
    ("mods.cpp", "/ page_size", "H", "getpagesize(): host page size, never 0"),
    ("rsp.cpp", "(u64(1) << 34) / a", "BC", "a = index + 512, index 1..511"),
    ("rt64_gbi_rdp.cpp", "sumWrap / i", "F", "static double sums"),
    ("rt64_framebuffer_manager.cpp", "% pixelSize", "FIX", "[s7348] pixelSize = max(1, (1 << siz) >> 1): G_IM_SIZ_4b gave 0"),
    ("rt64_framebuffer_manager.cpp", "/ pixelSize", "FIX", "[s7348] pixelSize = max(1, (1 << siz) >> 1): G_IM_SIZ_4b gave 0"),
    ("rt64_framebuffer_manager.cpp", "/ s4268Calls", "BC", "s4268Calls++ on the line before; s4268 log only"),
    ("rt64_framebuffer_pair.cpp", "nth", "H", "rs64_stage_count/add: every caller passes a literal nth"),
    ("rt64_rdp.cpp", "nth", "H", "rs64_stage_count/add: every caller passes a literal nth"),
    ("rt64_state.cpp", "nth", "H", "rs64_stage_count/add: every caller passes a literal nth"),
    ("rt64_workload_queue.cpp", "nth", "H", "rs64_stage_count/add: every caller passes a literal nth"),
    ("rt64_light_manager.cpp", "ambientColSum", "F", "hlslpp float3 / count -> float division"),
    ("rt64_present_queue.cpp", "/ colorTarget->downsampleMultiplier", "NZ", "inside if (downsampleMultiplier > 1)"),
    ("rt64_render_target.cpp", "/ downsampleMultiplier", "H", "user-config downsample multiplier (UI clamps 1..), not guest data"),
    ("rt64_rdp.cpp", "/ wordsPerLine", "BC", "wordsPerLine = found ? bestWpl : 4, bestWpl from a wpl >= 1 search loop (FIX_DXT opt-in)"),
    ("rt64_rdp.cpp", "tH / pxH", "F", "float extents, inside pxH > 1.0f"),
    ("rt64_rdp_tmem.cpp", "% size", "K", "rs64ProvSpanKey callers pass sizeW (256/512) or literal 256"),
    ("rt64_state.cpp", "% rectMultiplier", "NZ", "inside if (rectMultiplier > 1 && powerOfTwo)"),
    ("rt64_vi.cpp", "xScaleFloat()", "F", "float VI scale"),
    ("rt64_workload_queue.cpp", "/ referenceHeight", "BC", "referenceHeight = viFbSize > 0 ? max(.., MinimumReferenceHeight) : 240"),
    ("rt64_workload_queue.cpp", "/ framesRendered", "H", "inside frame > 0: framesRendered++ ran once per earlier frame of the same loop"),
    ("rt64_framebuffer_renderer.cpp", "std::lround(resScale[1])", "H", "only for origin < G_EX_ORIGIN_NONE: extended-GBI origins, never set under LLE (drawCall/scissor origins stay NONE); resScale >= 1"),
    ("rt64_native_target.cpp", "/ BlockSize", "K", "const BlockSize = FB_COMMON_WORKGROUP_SIZE"),
    ("rt64_native_target.cpp", "/ writeBuffer.floorBpp", "H", "floorBpp = RenderFormatSize(format) of a colour target (>= 1), set before the copy"),
    ("rt64_raster_shader.cpp", "% threadCount", "H", "ubershader thread count from the host config, not guest data"),
    ("rt64_texture_cache.cpp", "% alignment", "H", "nextSizeAlignedTo: callers pass constant pitch/placement alignments"),
    ("rt64_texture_cache.cpp", "RenderFormatSize(", "H", "format size of a host texture format (>= 1)"),
    ("rt64_texture_cache.cpp", "/ blockWidth", "H", "replacement-pack DDS block width (1 or 4), host file data, no pack in the port"),
    ("rt64_texture_cache.cpp", "/ formatSize", "H", "replacement-pack DDS format size, host file data, no pack in the port"),
    ("rt64_texture_cache.cpp", "/ streamLoadCount", "NZ", "inside streamLoadTimeTotal > 0 (both bumped together)"),
    ("rt64_math.cpp", "m[", "F", "hlslpp float4x4 elements"),
    ("rt64_profiling_timer.cpp", "% history.size()", "H", "history.resize(historyCount) from host-constant ProfilingTimer sizes"),
]
FS = re.compile(r"(?i)(?:path|dir(?:ectory)?|folder|file(?:name)?)\w*\s*(?:\(\))?$|^(?:mods_directory|mod_config_directory|save_folder|appDirName)$")
def rhs_of(l, k):
    """right operand starting at index k: unary prefix, primary with postfix chain (calls, [], ->, .)."""
    i, out = k, ""
    while i < len(l) and l[i] in " -!~*&+": out += l[i]; i += 1
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
        mo = re.match(r"[\w.]+|->|::|<[\w\s:,*]*>(?=\s*\()", l[i:])
        if mo: out += mo.group(0); i += len(mo.group(0)); continue
        break
    return out.strip()

def lhs_of(l, k):
    """left operand ending before index k (primary with postfix chain)."""
    i = k - 1
    while i >= 0 and l[i] == " ": i -= 1
    j = i
    while j >= 0:
        ch = l[j]
        if ch in ")]":
            open_ = {")": "(", "]": "["}[ch]; depth = 0
            while j >= 0:
                if l[j] in ")]": depth += 1
                elif l[j] in "([":
                    depth -= 1
                    if depth == 0: break
                j -= 1
            j -= 1; continue
        if re.match(r"[\w.>:\-]", ch):
            if ch == ">" and not (j > 0 and l[j - 1] == "-"): break
            if ch == "-" and not (j + 1 < len(l) and l[j + 1] == ">"): break
            j -= 1; continue
        break
    return l[j + 1:i + 1].strip()

def strip_div(d):
    d = d.strip()
    while d.startswith("(") and d.endswith(")") and s43.args_of(d, 1)[0] == d[1:-1].strip() and d.count("(") == d.count(")"):
        inner = d[1:-1].strip()
        if inner.count("(") != inner.count(")"): break
        d = inner
    d = re.sub(r"^\(\s*(?:const\s+)?[\w:]+\s*\)\s*", "", d)
    d = re.sub(r"^(?:static_cast|reinterpret_cast)\s*<[^>]*>\s*\((.*)\)$", r"\1", d)
    d = re.sub(r"^(?:u?int\d+_t|size_t|float|double|int|unsigned)\s*\((.*)\)$", r"\1", d)
    return d.strip()

def nonzero_construct(d, body):
    if re.search(r"<<", d) and re.match(r"^\(?\s*\(?\s*1[uUlL]*\s*<<", d): return "1 << n"
    if re.search(r"\|\s*1[uU]?\s*\)?$", d): return "x | 1"
    if re.search(r"(?:std::)?max\s*(?:<[^>]*>)?\s*\(\s*(?:1[uU]?\b[^,]*,|[^,]*,\s*\(?\w*\)?\s*1[uU]?\s*\))", d): return "max(.., 1)"
    if re.match(r"^\(?\s*[\w.\->]+\s*\+\s*1[uU]?\s*\)?$", d):
        v = re.match(r"^\(?\s*([\w]+)", d).group(1); t = s44.decl(v, body)
        if t and re.search(r"unsigned|uint|u8|u16|u32|size_t", t) and not re.search(r"uint32_t|u32|unsigned\s*$|size_t|uint64_t", t or ""): return "+1 of narrow unsigned"
        if t and re.search(r"uint8_t|uint16_t|u8|u16", t): return "+1 of narrow unsigned"
    return None

def checked(d, body, l, pos):
    """divisor d is zero-checked in the function body before the op, or guarded on the same line."""
    keys = {d}
    if re.match(r"^[\w.\->\[\]]+$", d): keys.add(d)
    ids = [x for x in s46.idents(d)] + re.findall(r"(?:->|\.)\s*(\w+)\b(?!\s*\()", d)
    pre = l[:pos]
    for k in keys | set(ids):
        e = re.escape(k)
        pat = (r"!\s*\(?\s*(?:[\w.\->]*?)?%s\b(?!\s*[(\[])|\b%s\s*==\s*0|\b%s\s*!=\s*0|\b%s\s*>\s*0|\b%s\s*>=\s*1\b|\b%s\s*<\s*1\b|"
               r"\b%s\s*<=\s*0|\b%s\s*>\s*\d|0\s*[<!=]=?\s*%s\b|\bif\s*\(\s*[\w.\->]*%s\s*\)|\b%s\s*\?|\b%s\s*&&|&&\s*[\w.\->]*%s\s*\)|"
               r"\b%s\s*=\s*(?:std::)?max\s*\(|\bassert\s*\([^;]*\b%s\b" % ((e,) * 15))
        if re.search(pat, body) or re.search(pat, pre): return k
    return None

def operands_float(lhs, d, body, ftext):
    return s47.is_float(lhs, body, ftext) or s47.is_float(d, body, ftext)

st = {"raw": 0, "K": 0, "F": 0, "FS": 0, "ARR": 0}
def hdr_for(p):
    out = []
    for h in (p.with_suffix(".h"), p.with_suffix(".hpp")):
        if h.exists(): out.append(h.read_text(errors="replace"))
    return out
def census(files, pgf):
    rows = []
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = s43.ln_fn(p); ftext = "\n".join(lines)
        names = s42.names_of(lines)
        m.MASK = DIV
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
            for mm in DIV.finditer(l):
                if (ln, mm.start(1)) in done: continue
                done.add((ln, mm.start(1)))
                if mm.start(1) >= len(l.rstrip()): continue
                if re.match(r"^\s*(?:#|\*)", l): continue
                if l[mm.start(1) - 1:mm.start(1)] in "/*" or l[mm.end(1):mm.end(1) + 1] in "/*": continue
                d0 = rhs_of(l, mm.end())
                lhs = lhs_of(l, mm.start(1))
                if not d0 or not lhs: continue
                if re.match(r"^(?:return|case|else|if|while)$", lhs): continue
                st["raw"] += 1
                d = strip_div(d0)
                start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
                if KCONST.match(d) or (names is not None and s42.ev(d, names) is not None) or s42.ev(d) is not None:
                    st["K"] += 1; continue
                if mm.group(1) == "/" and operands_float(lhs, d0, body, ftext): st["F"] += 1; continue
                if mm.group(1) == "/" and (FS.search(lhs) or FS.search(re.sub(r"\(.*", "", d)) or re.search(r'\+\s*(?:u8)?"', d0)): st["FS"] += 1; continue
                am = re.match(r"^(\w+)\.size\(\)$", d)
                if am and re.search(r"std::array\s*<[^;]*>\s*%s\s*;" % am.group(1), ftext + "\n" + "\n".join(hdr_for(p))): st["ARR"] += 1; continue
                cc, why = c, ""
                if cc in "GD" and rel.startswith("lib/rt64/") and not s43.body_gated(lines, ln): cc = "?"
                if cc == "D" and fn in s44.CORE: cc = "?"
                hh = s43.hand(rel, fn, raw.strip(), HAND) if cc in "?D" else None
                if hh and hh[0] in ("F", "K"): st[hh[0]] += 1; continue
                if cc == "?":
                    if hh: cc, why = hh
                    else:
                        bc = nonzero_construct(d, body)
                        if bc: cc, why = "BC", bc
                        else:
                            k = checked(d, body, l, mm.start(1))
                            if k: cc, why = "NZ", f"{k} checked"
                rows.append((rel, ln, fn, cc, why, f"{lhs[-30:]} {mm.group(1)} {d0}"[:80], raw.strip()))
    return rows

PLANT = ("static uint32_t planted(OSTask* task, uint32_t off) {\n    uint32_t w = task->width;\n    return off / w;\n}\n"
         "static uint32_t nz_twin(OSTask* task, uint32_t off) {\n    uint32_t w = task->width;\n    if (w == 0) return 0;\n    return off % w;\n}\n"
         "static uint32_t bc_twin(OSTask* task, uint32_t off) {\n    uint32_t n = task->shift;\n    return off / (1u << n);\n}\n"
         "static uint32_t gated_twin(OSTask* task, uint32_t off) {\n    if (!rs64_dlwalk_on()) return 0;\n    uint32_t w = task->width;\n    return off / w;\n}\n"
         "static float f_twin(float a, float b) {\n    return a / b;\n}\n")

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text(PLANT)
        got = {(r[2], r[3]) for r in census([t], pgf)}
        want = {("planted", "?"), ("nz_twin", "NZ"), ("bc_twin", "BC"), ("gated_twin", "G")}
        assert got == want, f"control failed: {got ^ want}"
        print("[s7348] controls: planted off / w '?', checked twin 'NZ', shift twin 'BC', gated twin 'G', float twin excluded")
        for k in st: st[k] = 0
    files = s43.files_in_scope()
    rows = census(files, pgf)
    cc = Counter(r[3] for r in rows)
    print(f"[s7348] raw / % ops={st['raw']} constant-divisor={st['K']} float={st['F']} fs-path={st['FS']} std::array-ring={st['ARR']}")
    print(f"[s7348] class Y sites={len(rows)} files={len(files)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[3] in "?B" or "-v" in sys.argv or ("-h" in sys.argv and r[3] in ("H", "FIX")):
            print(f"  {r[3]} {r[0]}:{r[1]} {r[2]} {r[4]} :: {r[5]}")
    fm = (ROOT / "lib/rt64/src/hle/rt64_framebuffer_manager.cpp").read_text()
    mr = (ROOT / "lib/N64ModernRuntime/librecomp/src/math_routines.cpp").read_text()
    fix1 = "std::max(1u, (1u << fb->siz) >> 1)" in fm and "= 1 << fb->siz >> 1;" not in fm
    fix2 = mr.count("rs64_udiv64(a, b)") == 2 and mr.count("rs64_sdiv64(a, b)") == 2 and mr.count("rs64_urem64(a, b)") == 2 and "ret = a / b" not in mr and "ret = a % b" not in mr
    print(f"[s7348] fixes present: framebuffer pixelSize {fix1}, guest 64-bit div helpers {fix2}")
    bad = [r for r in rows if r[3] in ("?", "B")] + ([] if fix1 and fix2 else [("fix-missing",)])
    print(f"[s7348] unclassified/defect: {len(bad)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
