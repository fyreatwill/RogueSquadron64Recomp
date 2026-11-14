#!/usr/bin/env python3
"""s7345 class V census: 32-bit multiply/shift overflow in guest-derived sizes.
A size computed as a uint32 product of guest values (`w * h * bpp`, `page * size`, `count * 8`, `n << k`) wraps before the
bound check / allocation sees it, so the check passes a small wrapped product while the copy or loop uses the factors.
Scope = s7343 files_in_scope(). A site is an integer `X * Y` or `X << Y` (Y variable or >= 8) on a line that is a sink
(comparison in if/while/for, memcpy/memset/memmove, resize/reserve/new/malloc/alloc, an index `[..]`) or that assigns the
product to a local which a later line of the same function uses in such a sink.
Classes: C/P/G/D from tools/s7338_mask_census.py sites() (rt64 G/D re-checked with s7343 body_gated(); CORE demotion as s7344)
  FLT a factor is float/double (declared, cast, literal, or a float maths call) -- not an integer size
  PTR the '*' is a pointer declaration / dereference / cast, not a multiply (regex false positive, kept for the count)
  W64 the product is computed in >32 bits: a factor is uint64_t/size_t/(u)int64 cast/.size()/sizeof (size_t), or ull literal
  BITS every factor has a known width (constant value, uint8/16 type, & mask, >> shift, bounded `v > N return`, loop index of a
      for with a known bound) and the widths sum to <= 31 bits, so the product cannot wrap
  H   hand-verified (reason in HAND)   B default-on guest factors whose product can exceed 2^32 before use (defect)
  ?   unclassified
'?' or B => exit 1. --controls plants `uint32_t n = task->w * task->h * 4; if (n > cap) return; memcpy(..)` ('?'), the uint64
twin ('W64'), the masked twin (w &= 0x3FF; h &= 0x3FF -> 'BITS'), and a gated twin ('G')."""
import re, sys, pathlib, importlib.util
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
def _load(name, f):
    s = importlib.util.spec_from_file_location(name, ROOT / f); mod = importlib.util.module_from_spec(s); s.loader.exec_module(mod); return mod
s44 = _load("s7344", "tools/s7344_wrap_census.py")
s43, s42, m = s44.s43, s44.s42, s44.m

OP = r"(?:\(\s*(?:u?int\d+_t|size_t|unsigned|int|uint64_t|float|double|s32|u32)\s*\)\s*)?(?:[A-Za-z_][\w\.:]*(?:->\w+|\.\w+|\[[^\]\[]*\]|\([^()]*\))*|0x[0-9A-Fa-f]+[uUlL]*|\d+[uUlL]*|\([^()]*\))"
MUL = re.compile(r"(?<![\w\)\]\*/&|\-<>=,(!~^\s])\s*" if False else r"(%s)\s*(\*|<<)\s*(%s)(?![\w\(\[])" % (OP, OP))
SINK = re.compile(r"\bmemcpy|\bmemset|\bmemmove|\.resize\(|\.reserve\(|\bnew\b|\bmalloc|\bcalloc|\brealloc|[Aa]lloc\w*\(|\b(?:if|while|for)\s*\(|\[")
TYPEW = r"(?:const\s+)?(?:unsigned\s+)?(?:u?int(?:8|16|32|64)_t|size_t|int|unsigned|long|short|char|bool|float|double|s8|u8|s16|u16|s32|u32|s64|u64|auto|uintptr_t)"
FLOATT = re.compile(r"^(?:const\s+)?(?:float|double|hlslpp::\w+|float\d|interop::\w+|glm::\w+|vec\d|Vec\d\w*)$")
WIDTH = {"MEM_B": 8, "MEM_BU": 8, "MEM_H": 16, "MEM_HU": 16, "uint8_t": 8, "int8_t": 7, "u8": 8, "s8": 7, "bool": 1, "char": 8, "uint16_t": 16, "int16_t": 15, "u16": 16, "s16": 15, "short": 15}
FLOATCALL = re.compile(r"\b(?:sqrt|sin|cos|tan|atan2?|floor|ceil|round|fabs|powf?|exp|log2?)f?\s*\(|\bstd::(?:floor|ceil|round|sqrt|abs)\b")
HAND = [  # (file suffix, needle in line, class, reason) -- s7345 review; widths are RDP/VI hardware field widths
    # RDP-command-derived row maths: colour/depth/texture image width field is 10 bits (+1 <= 1024 px, << siz >> 1 <= 4096 B/row),
    # tile/scissor/rect coords are 12-bit 10.2 (rows <= 1024), load line 9 bits (x8 <= 4096 B), siz 2 bits, tmem stride <= 4 KB.
    ("rt64_framebuffer.cpp", "Row", "H", "RDP fb rows (<=1024) x row bytes (<=4096): <=2^22"),
    ("rt64_framebuffer.cpp", "* rb", "H", "RDP fb rows (<=1024) x row bytes (<=4096): <=2^22"),
    ("rt64_framebuffer_manager.cpp", "resolutionScale", "FLT", "float resolution scale under lround/clamp"),
    ("rt64_framebuffer_manager.cpp", "rows * fbStride", "H", "RDP rows (<=1024) x fb stride (<=4096 B): <=2^22"),
    ("rt64_framebuffer_manager.cpp", "1 << fb->siz", "H", "siz is the 2-bit RDP size field"),
    ("rt64_framebuffer_manager.cpp", "sizMultiplier", "H", "RDP line width (<=4096) x siz multiplier (<=4), equality test only"),
    ("rt64_framebuffer_manager.cpp", "fb->width * fb->height", "G", "inside `if (s_fbup ...)` ROGUESQ_LOG_FBUPLOAD block, min()-clamped"),
    ("rt64_framebuffer_manager.cpp", "DifferenceFractionNum", "H", "fb->RAMBytes (<= 4 MB fb) x small constant numerator"),
    ("rt64_framebuffer_storage.cpp", "rdramUsed * 3", "H", "rdramUsed <= 8 MB RDRAM bytes (x3 < 2^25)"),
    ("rt64_present_queue.cpp", "drawnW * bpp", "H", "VI fb width (12-bit) x bpp (<=4) x16: <=2^18"),
    ("rt64_present_queue.cpp", "rsy * want", "FLT", "float shape scale"),
    ("rt64_rdp.cpp", "RowStart) * ", "H", "RDP fb rows (<=1024) x bytes/row (<=4096)"),
    ("rt64_rdp.cpp", "RowStart * ", "H", "RDP fb rows (<=1024) x bytes/row (<=4096)"),
    ("rt64_rdp.cpp", "n * dxt", "H", "LoadBlock texel count (12-bit) x dxt (12-bit): RDP counter maths, <=2^24"),
    ("rt64_rdp.cpp", "w * 8u", "H", "TMEM row words (9-bit line) x8"),
    ("rt64_rdp.cpp", "tmemStride", "H", "load rows (<=1024) x TMEM stride (<=4 KB) + words<<shift (<=4 KB)"),
    ("rt64_rdp.cpp", "wordCount << wordShift", "H", "TMEM word count (<=512) << 3"),
    ("rt64_rdp.cpp", "bytesPerRow", "H", "texture rows (<=1024) x bytes/row (10-bit width << siz, <=4096)"),
    ("rt64_rdp.cpp", "uint32_t(rc) * wpr", "G", "inside `if (s_big ...)` log-gated, compare only"),
    ("rt64_rdp.cpp", "G_MDSFT_CYCLETYPE", "K", "constant mask"),
    ("rt64_rdp.cpp", "triCount * 3", "H", "host triangle count from the drawCall buffer (vector-backed, << 2^30)"),
    ("rt64_rdp_tmem.cpp", "BytesPerRow", "H", "TMEM load: rows/ult (12-bit 10.2 >> 2 <=1024) x bytes/row (<=4096)"),
    ("rt64_rsp.cpp", "globalIndex", "H", "host vertex index into vector-backed float arrays (HLE RSP path; LLE port never runs it)"),
    ("rt64_state.cpp", "s.height", "D", "BandSource audit helper read() (rs64 band census, env-gated callers)"),
    ("rt64_state.cpp", "s.width", "D", "BandSource audit helper (rs64 band census)"),
    ("rt64_state.cpp", "Start * width) << siz", "H", "RDP rows (<=1024) x width (<=1024) << siz (<=3): <=2^23"),
    ("rt64_state.cpp", "End * width) << siz", "H", "RDP rows (<=1024) x width (<=1024) << siz (<=3): <=2^23"),
    ("rt64_state.cpp", "rowWidth << siz", "H", "width (<=1024) << siz (<=3)"),
    ("rt64_state.cpp", "* rowBytes", "H", "RDP rows (<=1024) x row bytes (<=4096)"),
    ("rt64_state.cpp", "swapWord * 4", "H", "TMEM word index (<=512) x4"),
    ("rt64_state.cpp", "tw * th", "H", "tile sample width x height (each <=1024 from 12-bit tile coords)"),
    ("rt64_state.cpp", "readRowBytes", "H", "fb read row bytes (<=4096) x rows/readHeight (<=1024)"),
    ("rt64_state.cpp", "colorWriteWidth + c) * 2", "H", "fb rows x write width (<=1024 each) x2"),
    ("rt64_state.cpp", "screenFbSize", "H", "VI fb size (12-bit width, <=1024 rows) << siz-1"),
    ("rt64_state.cpp", "screenFbSiz - 1u", "H", "siz is the 2-bit VI/RDP size field"),
    ("rt64_state.cpp", "x * bpp", "H", "x (<= VI width) x bpp (<=4)"),
    ("rt64_vi.cpp", "rowBytes * rowCount", "H", "VI row bytes (12-bit width x<=4) x rows (<=1024)"),
    ("rt64_workload_queue.cpp", "viFbSize[1] * 3", "H", "VI fb height (<=1024) x3"),
    ("rt64_workload_queue.cpp", "maxTimePerFrameMicro", "W64", "int64_t result: host clock maths, not a guest size"),
    ("rt64_buffer_uploader.cpp", "srcDataIndexRange", "W64", "std::pair<size_t,size_t> x size_t stride (rt64_buffer_uploader.h:39-40)"),
    ("rt64_framebuffer_renderer.cpp", "* rowBytes", "H", "fb rows (<=1024) x row bytes (<=4096)"),
    ("rt64_framebuffer_renderer.cpp", "kDepthStride", "K", "constant probe coordinate tables"),
    ("rt64_framebuffer_renderer.cpp", "kRdramXs", "K", "constant probe coordinate tables"),
    ("rt64_framebuffer_renderer.cpp", "rowStart) * width", "H", "fb rows (<=1024) x width (<=1024)"),
    ("rt64_framebuffer_renderer.cpp", "index * 2u", "H", "index < rows x width (<=2^20) x2"),
    ("rt64_framebuffer_renderer.cpp", "floorFaces * 142", "H", "floorFaces <= FloorPrimitiveCap checked at :1562 before use"),
    ("rt64_framebuffer_renderer.cpp", "transformsIndex * 4", "H", "host transform index into vector-backed viewportClipRatios"),
    ("rt64_projection_processor.cpp", "transformsIndex * 4", "H", "host transform index into vector-backed viewportClipRatios"),
    ("rt64_native_target.cpp", "floorBpp", "H", "checker probe: x/c < 256-wide probe tile, floorBpp <= 16"),
    ("rt64_texture_cache.cpp", "RowPitch * rowCount", "H", "host texture row pitch x rows: GPU texture dims <=16384 x <=16 B -> <2^32"),
    ("rt64_upscaler.cpp", "displayWidth * displayHeight", "H", "host display dims (<=16384 each): <=2^28"),
    ("rt64_gbi_s2dex.cpp", "", "H", "S2DEX HLE module: the port runs the F5 gfx ucode LLE, RT64 gets RDP commands only (never dispatched)"),
    ("rt64_gbi_f3dfactor5.cpp", "", "H", "F5 HLE gbi module: unreached under LLE gfx (RT64 fed RDP commands only); idx is a 16-bit DL index"),
    ("rt64_gbi_rdp.cpp", "b[k] *", "FLT", "barycentric float weights"),
    # librecomp / ultramodern
    ("rsp_vu_impl.hpp", ".get(n) <<", "PACK", "1-bit VCO/VCC flags packed into rt"),
    ("rsp_vu_impl.hpp", "vs.s16(n) * vte.s16(n)", "BITS", "s16 x s16 fits s32 (RSP VMADH semantics)"),
    ("rsp.cpp", "a * (b + 1)", "W64", "u64 constants_init loop vs u64(1) << 44"),
    ("dp.cpp", "bit * 2", "H", "bit is a small DP status-flag enum (< 16)"),
    ("dp.cpp", "1U << ", "H", "flag bit position < 32 from the enum above"),
    ("euc-jp.cpp", "* 94", "H", "EUC-JP byte arithmetic (<= 0xFE) x94 into fixed tables"),
    ("audio.cpp", "get_frames_remaining() * 2", "H", "host audio queue frames (SDL queue, < 2^20) x4"),
    ("events.cpp", "c * CPU_STATE_MAX", "H", "c < ncpu && c < 255 (loop bound) x 4"),
    # src/
    ("upstream_compat.cpp", "s7031_w + x", "H", "terrain height-map z/x < map dims (<= 64-wide bitmap, s6035) x2, result & 0x1FFF"),
    ("upstream_compat.cpp", "rs64_s7012_cap() * 10", "H", "env-config cap (owner setting, not guest data) for a loop counter"),
    ("upstream_compat.cpp", "1000000 * rs64_s7025_both()", "H", "rs64_s7025_both() returns 0/1"),
    ("upstream_compat.cpp", "yb - a.yb) * 16", "H", "RDP triangle y deltas (12-bit coords) x16 into int32"),
    ("upstream_compat.cpp", "tb.numer", "W64", "mach_absolute_time maths, uint64_t"),
    ("upstream_compat.cpp", "* 0xB8u", "H", "s6963_hu() returns a 16-bit guest halfword: 16+8 bits"),
    ("upstream_compat.cpp", "s.tb", "FLT", "host time base (double)"),
    ("rt64_render_context.cpp", "2 * s_sd_vi", "H", "VI counter equality probe, compare only"),
    ("rt64_render_context.cpp", "s_cw * 4", "H", "colour image width (10-bit RDP field) x4"),
    ("dpc_bridge.cpp", "1 << logmask", "H", "logmask checked 0 < logmask < 16 on the same line"),
    ("dpc_bridge.cpp", "masks * 2", "H", "masks < 2^16 (previous line) x2"),
    ("dpc_bridge.cpp", "g_bfsh_pk", "G", "inside `if (g_rs64_bfsh_arm == 1)` reserve of host peak counters"),
    ("s7324_rcp_spill.cpp", "tri_len[op - 8] * 8u", "K", "constant triangle-length table x8"),
    ("s7331_reset_writer.cpp", "1u << (ph * 3 + w)", "H", "ph/w are small enum indices; result cast to uint8_t"),
]
CORE = s44.CORE

def bits_of_value(v):
    return max(1, int(v).bit_length())

def strip_cast(o):
    return re.sub(r"^\(\s*[\w\s]+\)\s*", "", o.strip()).strip()

def width(o, body, ftext, names, loops):
    """(kind, bits): kind in K/FLT/W64/W/None; bits = known max width of the factor, None if unknown."""
    so = o.strip()
    if re.match(r"^\(\s*(?:float|double)\s*\)", so) or re.search(r"\d\.\d|\d\.f\b|\d+\.?\d*f\b", so) or FLOATCALL.search(so): return "FLT", None
    if re.match(r"^\(\s*(?:u?int64_t|size_t|uintptr_t|unsigned\s+long\s+long|s64|u64)\s*\)", so) or re.search(r"\d+ull\b|\d+ULL\b", so): return "W64", None
    if re.search(r"\.size\(\)|\.length\(\)|\bsizeof\b", so): return "W64", None
    if re.match(r"^(?:u?int64_t|size_t|uintptr_t|u64|s64|uint64)\s*\(", so): return "W64", None   # functional 64-bit cast
    o2 = strip_cast(so)
    if re.match(r"^ctx->r\d+$|^ctx->(?:hi|lo)$", o2): return "W64", None          # MIPS GPRs are 64-bit
    mb = re.match(r"^(MEM_BU?|MEM_HU?)\s*\(", o2)
    if mb: return "W", WIDTH[mb.group(1)]
    if o2.startswith("(") and o2.endswith(")"):
        inner = o2[1:-1]
        mm = re.search(r"&\s*(0x[0-9A-Fa-f]+|\d+)[uU]?\s*$", inner)
        if mm: return "W", bits_of_value(int(mm.group(1), 0))
        mm = re.search(r">>\s*(\d+)\s*$", inner)
        if mm and re.fullmatch(r"[\w\.\->\[\]]+\s*>>\s*\d+", inner.strip()): return "W", max(1, 32 - int(mm.group(1)))
        try:
            v = s42.ev(inner, names)
            if v is not None: return "K", bits_of_value(abs(v))
        except Exception: pass
        return None, None
    try:
        v = s42.ev(o2, names)
        if v is not None: return "K", bits_of_value(abs(v))
    except Exception: pass
    if s44.CONST.match(o2): return "K", 16 if not re.match(r"^\d|^0x", o2) else bits_of_value(int(re.sub(r"[uUlL]+$", "", o2), 0))
    b = s44.base(o2)
    simple = "->" not in o2 and "." not in o2 and "[" not in o2 and "(" not in o2
    if simple and b in loops and loops[b] is not None: return "W", loops[b]
    t = (s44.decl(b, body) or s44.decl(b, ftext)) if simple else None
    if t:
        tt = re.sub(r"^const\s+", "", t.strip())
        if FLOATT.match(tt): return "FLT", None
        if re.fullmatch(s44.W64T, tt) and tt not in ("float", "double"): return "W64", None
        if tt in WIDTH: return "W", WIDTH[tt]
        if tt == "auto":
            am = re.search(r"\bauto\s+%s\s*=\s*([^;]+);" % re.escape(b), body)
            if am and re.search(r"\.size\(\)|size_t|uint64_t", am.group(1)): return "W64", None
            if am and re.search(r"float|double|\d\.\d", am.group(1)): return "FLT", None
    if simple:
        v = re.escape(b)
        mm = None
        for mm in re.finditer(r"\b%s\s*&=\s*(0x[0-9A-Fa-f]+|\d+)\b|\b%s\s*=\s*[^;]*&\s*(0x[0-9A-Fa-f]+|\d+)u?\s*\)?\s*;" % (v, v), body): pass
        if mm: return "W", bits_of_value(int(mm.group(1) or mm.group(2), 0))
        mm = re.search(r"if\s*\(\s*%s\s*(>=?)\s*(0x[0-9A-Fa-f]+|\d+)[uU]?\s*\)\s*(?:\{?\s*)?(?:return|continue|break|%s\s*=)" % (v, v), body)
        if mm: return "W", bits_of_value(int(mm.group(2), 0))
        mm = re.search(r"\b%s\s*=\s*(?:std::)?min(?:<\w+>)?\s*\([^;]*?(0x[0-9A-Fa-f]+|\d+)[uU]?\s*\)\s*;" % v, body)
        if mm: return "W", bits_of_value(int(mm.group(1), 0))
    mm = re.search(r"&\s*(0x[0-9A-Fa-f]+|\d+)[uU]?\s*\)?$", so)
    if mm: return "W", bits_of_value(int(mm.group(1), 0))
    return None, None

def loop_bounds(body, names):
    """loop index -> bits of its constant bound (None if the bound is not a constant)."""
    out = {}
    for mm in re.finditer(r"\bfor\s*\(\s*(?:[\w:]+\s+)?(\w+)\s*=\s*[^;]*;\s*\1\s*(<=?)\s*([^;]+);", body):
        v, op, lim = mm.group(1), mm.group(2), mm.group(3).strip()
        try: val = s42.ev(lim, names)
        except Exception: val = None
        if val is None and re.fullmatch(r"0x[0-9A-Fa-f]+|\d+", lim): val = int(lim, 0)
        out[v] = bits_of_value(val) if val is not None else out.get(v)
    return out

DECLPTR = re.compile(r"(?:^|[(,;{]\s*|\breturn\s+|=\s*)(?:const\s+)?(?:struct\s+)?[A-Za-z_][\w:]*(?:<[^<>]*>)?\s*\*+\s*(?:const\s+)?[A-Za-z_]\w*\s*(?:[=;,)\[]|$)")
def is_ptr(l, mm):
    """the '*' of this match is a declaration/cast/deref rather than a multiply."""
    if mm.group(2) != "*": return False
    a = mm.group(1).strip(); pre = l[:mm.start()]
    seg = l[max(0, mm.start() - 2):mm.end() + 2]
    if re.fullmatch(r"(?:const\s+)?(?:struct\s+)?[A-Za-z_][\w:]*", a) and re.search(r"(?:^|[(,;{]|\bconst|\bstatic|\breturn|=)\s*$", pre) and \
            re.match(r"\s*\*+\s*(?:const\s+)?[A-Za-z_]\w*\s*(?:[=;,)\[]|$)", l[mm.start() + len(mm.group(1)) + (len(l[mm.start():]) - len(l[mm.start():].lstrip())):]):
        return True
    if re.search(r"\(\s*(?:const\s+)?[A-Za-z_][\w:]*\s*$", pre) and re.match(r"\s*\*\s*\)", l[mm.start(2):]): return True  # (T*) cast
    if re.match(r"^(?:u?int\d+_t|char|void|float|double|int|unsigned|bool|auto|const|[A-Z]\w*)$", a) and re.search(r"[(,=]\s*$|^\s*$|\bconst\s*$|\bstatic\s*$", pre):
        return True
    if re.search(r"<\s*$", pre): return True                                # template<T*>
    return False

def sink_use(var, lines, ln, end):
    v = re.escape(var)
    for j in range(ln, min(end, ln + 40)):
        l = lines[j]
        if re.search(r"\b%s\b" % v, l) and (SINK.search(l) or re.search(r"[<>]=?\s*%s\b|\b%s\s*[<>]" % (v, v), l)): return j + 1
    return None

def census(files, pgf):
    rows = []
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = s43.ln_fn(p); ftext = "\n".join(lines); names = s42.names_of(lines)
        m.MASK = MUL
        fnend = {}
        for (ln, fn, mk, c, text) in m.sites(p, pgf):
            l = lines[ln - 1]
            mm = MUL.search(l[l.find(mk):]) if mk in l else MUL.search(l)
            if not mm: continue
            a, op, n = mm.group(1), mm.group(2), mm.group(3)
            if op == "<<":
                try: k = s42.ev(n.strip(), names)
                except Exception: k = None
                if k is not None and k < 8: continue
            stripped = l.split("//")[0]
            if l.lstrip().startswith("#") or re.search(r'"[^"]*\*[^"]*"', l) and mk not in re.sub(r'"[^"]*"', "", l): continue
            start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
            # sink: the line itself, or a local assigned the product and used in a sink later
            nob = re.sub(r"\[", "", stripped)
            pos = stripped.find(mk.strip())
            inbr = pos >= 0 and stripped[:pos].count("[") > stripped[:pos].count("]")
            sk = bool(SINK.search(nob)) or inbr
            loc = re.match(r"^\s*(?:%s\s+)?(\w+)\s*[+\-|]?=\s*" % TYPEW, stripped)
            if not sk and loc:
                sk = sink_use(loc.group(1), lines, ln, len(lines)) is not None
            if not sk: continue
            if c in "GD" and rel.startswith("lib/rt64/") and not s43.body_gated(lines, ln): c = "?"
            if c == "D" and fn in CORE: c = "?"
            why = ""
            if c == "?":
                hh = s43.hand(rel, fn, text, HAND)
                if hh: c, why = hh
                elif (re.match(r"^\(\s*\w+\s*\)$|^\(\s*[^()]*\)$", a.strip()) and re.search(r"\)\s*\*\s*%s\s*=" % re.escape(n.strip()), stripped)) or \
                        re.match(r"^\(\s*(?:u?int\d+_t|char|unsigned)\s*\)$", a.strip()):
                    c, why = "PTR", "conditional store through pointer / cast deref"
                elif re.search(r"16777619|0x9E3779B|\bh\s*\*\s*31\b|\bfnv\b", stripped): c, why = "HASH", "FNV/polynomial hash mixing (wrap intended)"
                elif is_ptr(stripped, mm) or re.match(r"^\s*\*", mk) or re.match(r"^(?:return|long|std::\w+|recomp_\w+|[a-z_]+_t)$", a.strip()) and op == "*" and not re.match(r"^\d", n.strip()) and re.search(r"\b%s\s*\*\s*\w+\s*(?:[=;,)]|$)|\breturn\s*\*" % re.escape(a.strip()), stripped):
                    c, why = "PTR", "pointer declaration/cast/deref"
                else:
                    loops = loop_bounds("\n".join(lines[start:ln]), names)
                    ka, ba = width(a, body, ftext, names, loops); kn, bn = width(n, body, ftext, names, loops)
                    if "FLT" in (ka, kn) or re.search(r"\b(?:float|double)\b|\d\.\d+f?\b", stripped): c, why = "FLT", "float maths"
                    elif "W64" in (ka, kn) or re.search(r"\((?:u?int64_t|size_t|uintptr_t)\)\s*\(?\s*%s" % re.escape(a.strip()), stripped): c, why = "W64", "64-bit product"
                    elif op == "<<" and ba is not None and kn == "K":
                        k = s42.ev(n.strip(), names) if kn == "K" else None
                        if k is not None and ba + k <= 31: c, why = "BITS", f"{ba}+{k} bits"
                    elif ba is not None and bn is not None and ba + bn <= 31: c, why = "BITS", f"{ba}+{bn} bits"
                    if c == "?" and op == "<<" and kn == "K" and (re.search(r"[|^]\s*\(?\s*%s|%s\s*\)?\s*[|^]" % (re.escape(mk[:12]), re.escape(mk[-8:])), stripped) or
                                                         re.search(r"<<\s*\d+\s*\)?\s*[|^+]|[|^]\s*\(?[^;]*<<", stripped)):
                        c, why = "PACK", "constant-shift bit composition (word/key assembly), not a size"
                    if c == "?":
                        li = {kk for kk in re.findall(r"\bfor\s*\(\s*(?:[\w:]+\s+)?(\w+)\s*=", "\n".join(lines[start:ln]))}
                        for x, kx, bx in ((a, ka, ba), (n, kn, bn)):
                            o = (n if x is a else a); ko, bo = (kn, bn) if x is a else (ka, ba)
                            if strip_cast(x) in li and ko == "K" and bo is not None and bo <= 12:
                                c, why = "LOOPK", f"loop index {strip_cast(x)} x constant <= 2^{bo}: wrap needs >= 2^{32-bo} iterations"; break
            rows.append((rel, ln, fn, c, why, f"{a.strip()} {op} {n.strip()}", text))
    return rows

PLANT = ("static void planted(uint8_t* rdram, uint8_t* dst, OSTask* task) {\n    uint32_t n = task->w * task->h;\n"
         "    if (n > 0x10000) return;\n    memcpy(dst, rdram, n);\n}\n"
         "static void wide_twin(uint8_t* rdram, uint8_t* dst, OSTask* task) {\n    uint64_t n = (uint64_t)task->w * task->h;\n"
         "    if (n > 0x10000) return;\n    memcpy(dst, rdram, n);\n}\n"
         "static void masked_twin(uint8_t* rdram, uint8_t* dst, OSTask* task) {\n    uint32_t w = task->w;\n    uint32_t h = task->h;\n"
         "    w &= 0x3FF;\n    h &= 0x3FF;\n    uint32_t n = w * h;\n    if (n > 0x10000) return;\n    memcpy(dst, rdram, n);\n}\n"
         "static void gated_twin(uint8_t* rdram, uint8_t* dst, OSTask* task) {\n    if (!rs64_dlwalk_on()) return;\n"
         "    uint32_t n = task->w * task->h;\n    if (n > 0x10000) return;\n    memcpy(dst, rdram, n);\n}\n")

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text(PLANT)
        got = {(r[2], r[3]) for r in census([t], pgf)}
        want = {("planted", "?"), ("wide_twin", "W64"), ("masked_twin", "BITS"), ("gated_twin", "G")}
        assert got == want, f"control failed: {got ^ want}"
        print("[s7345] controls: planted task->w * task->h '?', uint64 twin 'W64', masked twin 'BITS', gated twin 'G'")
    files = s43.files_in_scope()
    rows = census(files, pgf)
    cc = Counter(r[3] for r in rows)
    print(f"[s7345] class V sites={len(rows)} files={len(files)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[3] in "?B" or "-v" in sys.argv or ("-h" in sys.argv and r[3] == "H"):
            print(f"  {r[3]} {r[0]}:{r[1]} {r[2]} {r[4]} :: {r[5][:60]} :: {r[6][:110]}")
    bad = [r for r in rows if r[3] in ("?", "B")]
    print(f"[s7345] unclassified/defect: {len(bad)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
