#!/usr/bin/env python3
"""s7352 class AC census: signed 32-bit add / subtract / negate overflow on guest-derived ints in host code.
`int32_t a + b`, `a - b`, `a += b`, `-a`, `abs(a)` overflow is UB in C++ (clang folds `x + 1 > x`, range checks and trip counts on
it); MIPS ADDU/SUBU wrap, so the retail meaning of guest arithmetic is an unsigned 32-bit wrap.
Generated code is out of this scope and clean by construction (checked s7352): N64Recomp ADD32/SUB32 add two `gpr` (uint64_t)
then truncate, RecompiledFuncs has no S32()/SIGNED() +/- and the F5 ucode C files neither (only S32() << k, class Z territory).
Scope = s7343 files_in_scope(). A site = a binary + / - / += / -= or unary - / abs() whose arithmetic is performed in signed 32
bits: at least one operand is declared int / int32_t / s32 / int_fast32_t (or cast to one), and no operand is unsigned 32,
64-bit or floating (those promote the whole expression away from signed int).
Classes: C/P/G/D from tools/s7338_mask_census.py sites() (rt64 G/D re-checked with s7343 body_gated(); CORE demotion as s7344)
  NAR every operand has a known width (narrow type, & mask, >> k, RDP bitfield, constant, bounded loop index) and the widths
      fit: max width + 1 <= 31 bits, so the sum cannot leave int range
  HOST no operand (or its one-level assignment) is guest-derived: host loop counters, container sizes, env / config values,
      host window dims, clocks (UB is impossible without a host value near INT_MAX; not a guest-input defect)
  H   hand-verified (reason in HAND)   FIX fixed this session   B default-on full-range guest int32 sum (defect)   ?  unclassified
  (W64 / U / FLT expressions are not signed-32 arithmetic and are counted, not listed.)
'?' or B => exit 1. --controls plants `int32_t s = (int32_t)task->a + (int32_t)task->b;` ('?'), the uint32 twin (not a site:
counted U), the int16 twin ('NAR'), the int64 twin (counted W64), and a gated twin ('G')."""
import re, sys, pathlib, importlib.util
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
def _load(name, f):
    s = importlib.util.spec_from_file_location(name, ROOT / f); mod = importlib.util.module_from_spec(s); s.loader.exec_module(mod); return mod
s48 = _load("s7348", "tools/s7348_div_census.py")
s46, s44, s43, s42, m = s48.s46, s48.s44, s48.s43, s48.s42, s48.m

SIG32 = re.compile(r"^(?:const\s+|static\s+|volatile\s+)*(?:signed\s+)?(?:int|int32_t|s32|int_fast32_t|signed)$")
NARROWT = {"int16_t": 15, "s16": 15, "short": 15, "int8_t": 7, "s8": 7, "char": 8, "signed char": 7, "uint8_t": 8, "u8": 8,
           "uint16_t": 16, "u16": 16, "unsigned short": 16, "unsigned char": 8, "bool": 1}
UNS32 = re.compile(r"^(?:const\s+|static\s+|volatile\s+)*(?:unsigned(?:\s+int)?|uint32_t|u32|uint)$")
W64T = re.compile(r"(?:^|\s)(?:u?int64_t|size_t|ssize_t|ptrdiff_t|uintptr_t|intptr_t|long|u64|s64|gpr|uint64|time_t|off_t)$")
FLTT = re.compile(r"(?:^|\s)(?:float|double|hlslpp::\w+|float\d|interop::\w+|glm::\w+)$")
GUEST = re.compile(r"\bMEM_[WHB]U?\b|\bctx->r\d+|\brdram\b|\bRDRAM\b|\btask->|\bosTask|->w[01]\b|\bw[01]\b|\bcmd\b|\bTMEM\b|\bdmem\b|"
                   r"\bDMEM\b|\bread_u32|\brd32\b|\brs64_rd\w*|\bbswap|__builtin_bswap|\bdl\[|\bword\b|\bguest\w*|\bvaddr\b|\bp[01]\s*\(|"
                   r"\bimm\b|\boffset\b|\bseg\w*|\bRAM\b|\bram\b|\bvi_\w+|\bVI_\w+|\bdram\b|\baddr\w*\b|\bsp_\w+|\bdp_\w+")
KW = {"return", "case", "else", "if", "while", "operator", "sizeof", "throw", "co_return", "delete", "new"}
HAND = [  # (file suffix, needle in line, class, reason) -- s7352 review
    ("dpc_bridge.cpp", "g_rdram_for_submit + r.", "PTR", "uint8_t* + uint32 (g_deferred_ranges pairs are uint32): pointer arithmetic, r.first < r.second"),
    ("dpc_bridge.cpp", "rdram[s_last_timg + i]", "U", "s_last_timg is static uint32_t (:6944): unsigned index maths; LOADBLOCK dump n2 <= 6 gated"),
    ("overlays.cpp", "rom_addr - rom + ram_addr", "U", "uint32 rom_addr - uint32 rom + int32 ram_addr: usual conversions make it unsigned (wraps like MIPS)"),
    ("rt64_gbi_f3dex2.cpp", "index - 2", "NAR", "index = uint8_t offset / 24 <= 10; F3DEX2 HLE never dispatched under LLE gfx"),
    ("rt64_gbi_rdp.cpp", "triOut = n - 2", "NAR", "n = clipped polygon vertex count (fixed local arrays, <= 9)"),
    ("rt64_interpreter.cpp", "s_cimg_prev_n - i", "HOST", "host SetColorImage event counter minus loop i <= 8, & 7 ring index (no guest operand)"),
    ("rt64_interpreter.cpp", "dl + i * 8", "PTR", "s4282 diag dump: const uint8_t* + int"),
    ("rt64_interpreter.cpp", "(long long)(dl - rdram) + i", "W64", "long long arithmetic (s4282 diag)"),
    ("rt64_interpreter.cpp", "regions[r] + i", "PTR", "s4271 diag dump: const uint32_t* + int"),
    ("rt64_rdp.cpp", "n += (sA[wd * 8 + b] == sB[wd * 8 + b])", "NAR", "n counts 8 byte compares (b < 8): n <= 8"),
    ("rt64_rdp.cpp", "std::abs(width - height)", "NAR", "width = wpl * texelsPerWord (TMEM words <= 512 x <= 16), height = rows <= 512 (checked :1699)"),
    ("rt64_state.cpp", "T[addr + 1]", "NAR", "addr = 0xF80 + (pidx << 3), pidx an 8-bit palette index: TMEM offset < 4 KB"),
    # guest-derived but narrow (the auto rule would have said HOST: the census traces one assignment level only)
    ("rt64_state.cpp", "int32_t(tile.l", "NAR", "tile uls/ult/lrs/lrt are uint16_t 12-bit RDP fields (rt64_rdp.h:158): |diff| + 4 < 2^13"),
    ("rt64_state.cpp", "Scroll", "H", "x/yScroll = uls >> 2 <= 16383; int(texcoord * ShiftScaleMap) from 16-bit s10.5 texcoords x <= 32 is << 2^31 (out-of-range float -> int is class X)"),
    ("rt64_state.cpp", "rowStart", "H", "s_dumpci diag (idx <= 8): TMEM byte offsets, line/tmem 9-bit << 3 < 8 KB"),
    ("rt64_state.cpp", "tmemBase + rel", "H", "s_dumpci diag (idx <= 8): TMEM byte offsets < 8 KB"),
    ("rt64_state.cpp", "stride + (x >> 1)", "H", "s_dumpci diag: TMEM stride (9-bit << 3) + x < tile width"),
    ("rt64_rdp.cpp", "extAlignment.", "NAR", "ulx..lry are 12-bit RDP rect/scissor coords in int32 (<= 4095 << 2) + RT64 extended-GBI int16 offsets (0: this game sends no G_EX commands)"),
    ("rt64_rdp.cpp", "scissorRect.lr", "NAR", "12-bit RDP coords in int32: difference < 2^14"),
    ("rt64_rdp.cpp", "G_EX_ORIGIN_RIGHT", "H", "movedFromOrigin: only for ori < G_EX_ORIGIN_NONE, set by RT64 extended-GBI commands this game never sends"),
    ("rsp_vu_impl.hpp", "(s32)vs.u16(n) - (s32)vte.u16(n)", "NAR", "VCL: u16 - u16 in s32"),
    ("rsp_vu_impl.hpp", "product += 32", "H", "VMACQ: only when product < 0, cannot overflow"),
    ("rsp_vu_impl.hpp", "product -= 32", "H", "VMACQ: only when product >= 32, cannot overflow"),
    ("rsp_vu_impl.hpp", "product += 31", "H", "VMULQ: only when product < 0 (s16 x s16 >= -2^30)"),
    ("rsp_vu_impl.hpp", "data -= mask", "H", "VRCP/VRSQ: data = input ^ (input >> 31); the -= runs only for input > -32768, so INT_MIN (DIVIN 0x8000:0000) never reaches it"),
    ("dpc_bridge.cpp", "x - y * (int)std::floor", "H", "rs64_imod: only from rs64_i4_fetch (rs64_floor_texel returns at once without ROGUESQ_LOG_FLOOR, s6934) and its fixed self-test"),
    ("dpc_bridge.cpp", "masks - 1", "H", "rs64_i4_wrap: masks <= 15 (4-bit RDP field); floor-texel diag only"),
    ("dpc_bridge.cpp", "x0 + 1", "H", "rs64_i4_fetch: floor-texel diag only (ROGUESQ_LOG_FLOOR)"),
    ("dpc_bridge.cpp", "y0 + 1", "H", "rs64_i4_fetch: floor-texel diag only (ROGUESQ_LOG_FLOOR)"),
    ("dpc_bridge.cpp", "r.second - r.first", "U", "g_deferred_ranges are uint32 pairs, r.first < r.second (submit_hi <= submit_lo dropped, s7346)"),
    ("dpc_bridge.cpp", "rows - 1", "H", "floor-texel report table rows (host count, ROGUESQ_LOG_FLOOR)"),
    ("dpc_bridge.cpp", "covered - nok", "H", "floor-texel report host counts (nok <= covered)"),
    ("upstream_compat.cpp", "s7031_w + x", "H", "terrain height-map z/x < map dims (<= 64-wide bitmap, s6035), as class V s7345"),
    ("upstream_compat.cpp", "s7031_w", "H", "terrain cell x/z vs map dims (<= 64-wide bitmap): |x - w| < 2^8"),
    ("upstream_compat.cpp", "s7031_hgt", "H", "terrain cell z vs map height (bitmap dims)"),
    ("upstream_compat.cpp", "s.rplus - (int32_t)s.rminus", "H", "recv_trace_dump diag counters (host)"),
]

def opbits(o, body, ftext, names):
    """(kind, bits) for an operand: kind S32 / NAR / U32 / W64 / FLT / K / None (unknown type)."""
    so = o.strip()
    if not so: return None, None
    if re.search(r"\d\.\d*f?\b|\d+\.?\d*f\b|\bstd::(?:sin|cos|sqrt|floor|ceil|round)\b|\b(?:sqrtf?|floorf?|ceilf?|roundf?)\s*\(", so): return "FLT", None
    c = re.match(r"^\(\s*((?:const\s+)?(?:unsigned\s+|signed\s+)?[\w:]+)\s*\)\s*(.*)$", so) or \
        re.match(r"^(?:static_cast\s*<\s*([\w:\s]+)\s*>|(u?int\d+_t|int|float|double|size_t))\s*\((.*)\)$", so)
    if c:
        t = (c.group(1) or (c.group(2) if c.lastindex and c.lastindex >= 2 else "") or "").strip()
        rest = c.group(c.lastindex)
        if t and rest and not re.fullmatch(r"\w+\s*\(.*", so.split(")", 1)[0] if so.startswith("(") else ""):
            if SIG32.match(t): return "S32", inner_bits(rest, body, ftext, names)
            if t in NARROWT: return "NAR", NARROWT[t]
            if UNS32.match(t): return "U32", None
            if W64T.search(t): return "W64", None
            if FLTT.search(t): return "FLT", None
    o2 = s48.strip_div(so)
    try:
        v = s42.ev(o2, names)
        if v is not None: return "K", max(1, abs(int(v)).bit_length())
    except Exception: pass
    if s48.KCONST.match(o2): return "K", None
    if re.match(r"^ctx->r\d+$", o2): return "W64", None
    mb = re.match(r"^MEM_(BU?|HU?|W)\s*\(", o2)
    if mb: return ("NAR", {"B": 7, "BU": 8, "H": 15, "HU": 16}[mb.group(1)]) if mb.group(1) != "W" else ("S32", None)
    if re.search(r"\.size\(\)|\.length\(\)|\bsizeof\b", o2): return "W64", None
    t = typ(o2, body, ftext)
    if t is None: return None, None
    t = t.strip()
    if SIG32.match(t): return "S32", var_bits(o2, body)
    for k, b in NARROWT.items():
        if re.fullmatch(r"(?:const\s+)?%s" % k, t): return "NAR", b
    if UNS32.match(t): return "U32", None
    if W64T.search(t): return "W64", None
    if FLTT.search(t): return "FLT", None
    return None, None

def typ(o, body, ftext):
    if re.fullmatch(r"[A-Za-z_]\w*", o):
        return s44.decl(o, body) or s44.decl(o, ftext)
    mem = re.match(r"^[\w\.\->\[\]]*(?:->|\.)(\w+)$", o)
    if mem:
        return s44.decl(mem.group(1), ftext) or s46.hdr_text().get(mem.group(1))
    arr = re.match(r"^([A-Za-z_]\w*)\s*\[", o)
    if arr:
        return s44.decl(arr.group(1), body) or s44.decl(arr.group(1), ftext)
    return None

def inner_bits(e, body, ftext, names):
    e = s48.strip_div(e.strip())
    mk = re.search(r"&\s*(0x[0-9A-Fa-f]+|\d+)[uUlL]*\s*\)*$", e)
    if mk: return max(1, int(mk.group(1), 0).bit_length())
    sh = re.search(r">>\s*(\d+)\s*\)*$", e)
    if sh and int(sh.group(1)) > 0: return 32 - int(sh.group(1))
    mb = re.match(r"^MEM_(BU?|HU?)\s*\(", e)
    if mb: return {"B": 7, "BU": 8, "H": 15, "HU": 16}[mb.group(1)]
    t = typ(e, body, ftext) if re.fullmatch(r"[\w\.\->\[\]]+", e) else None
    if t:
        for k, b in NARROWT.items():
            if re.fullmatch(r"(?:const\s+)?%s" % k, t.strip()): return b
    return var_bits(e, body)

def var_bits(o, body):
    """width of a local from its assignments (mask / shift / narrow source) or a constant-bounded for loop."""
    if not re.fullmatch(r"[A-Za-z_]\w*", o): return None
    e = re.escape(o); mx = None
    lp = re.search(r"for\s*\([^;]*\b%s\s*=\s*([^;]*);\s*%s\s*(<=?)\s*([^;]+);" % (e, e), body)
    if lp:
        b = lp.group(3).strip(); k = s42.ev(b)
        if k is None and re.fullmatch(r"\d+[uU]?", b): k = int(b.rstrip("uU"))
        if k is not None: return max(1, int(k).bit_length())
    for a in re.finditer(r"\b%s\s*(?:=|\{)\s*([^;{]+);" % e, body):
        rhs = a.group(1).strip().rstrip("}").strip()
        mk = re.search(r"&\s*(0x[0-9A-Fa-f]+|\d+)[uUlL]*\s*\)*$", rhs)
        sh = re.search(r">>\s*(\d+)\s*\)*$", rhs)
        mb = re.match(r"^\(?\s*(?:\(\s*(?:int|int32_t)\s*\)\s*)?\(?\s*MEM_(BU?|HU?)\s*\(", rhs)
        pf = re.match(r"^\(?\s*(?:\(\s*(?:int|int32_t)\s*\)\s*)?p[01]\s*\(\s*\d+\s*,\s*(\d+)\s*\)", rhs)
        if mk: k = max(1, int(mk.group(1), 0).bit_length())
        elif pf: k = int(pf.group(1))
        elif sh and int(sh.group(1)) > 0 and re.fullmatch(r"[\w\.\->\[\]()\s]+>>\s*\d+\s*\)*", rhs): k = 32 - int(sh.group(1))
        elif mb: k = {"B": 7, "BU": 8, "H": 15, "HU": 16}[mb.group(1)]
        else:
            try: v = s42.ev(rhs)
            except Exception: v = None
            if v is None: return None
            k = max(1, abs(int(v)).bit_length())
        mx = k if mx is None else max(mx, k)
    return mx

def guest(o, body):
    if GUEST.search(o): return True
    for v in re.findall(r"(?<![\w.>])([A-Za-z_]\w*)", o):
        for a in re.finditer(r"\b%s\s*(?:=|\{)\s*([^;]+);" % re.escape(v), body):
            if GUEST.search(a.group(1)): return True
    return False

# Blind-spot review (s7352): every default-on +/- whose guest-derived operand type the census cannot resolve is classed here.
BLIND_HAND = [  # (file suffix, needle in expression, class, reason)
    ("rsp_vu_impl.hpp", "", "U", "LWC2/SWC2 address maths: rs is RSP::r32 = uint32_t (rsp_vu.hpp:66), address/base are auto from it or & 15"),
    ("rsp_vu_impl.hpp", "", "U", ""),
    ("rt64_rdp_tmem.cpp", "+= (", "HOST", "audit counter += bool comparison (rs64PCS / rs64HGS hash census)"),
    ("helpers.hpp", "ret +=", "HOST", "std::string append of a guest byte, not arithmetic"),
    ("upstream_compat.cpp", "rec(rdram", "HOST", "s4580::rec() returns a host ring index (+1), not a guest value"),
    ("rsp.cpp", "n - 1", "HOST", "rs64_s4214_scan host loop count (n >= 1 checked)"),
    ("rt64_gbi_f3dex2.cpp", "p0(1, 7) - vtxCount", "H", "F3DEX2 HLE (never dispatched under LLE gfx); 7-bit field minus a <= 127 vertex count"),
    ("rt64_gbi_f3dex2.cpp", "32 - (*dl)->p0(8, 8)", "H", "F3DEX2 HLE (never dispatched under LLE gfx); 8-bit field"),
    ("dpc_bridge.cpp", "a + 4", "U", "rs64_rw_cmd(uint32_t lo, uint32_t a, ...) (:5672): unsigned"),
    ("librecomp/src/rsp.cpp", "e.dram + e.size", "U", "Rs64S4211Pi { uint32_t dram; uint32_t size; } (rsp.cpp:319): unsigned"),
    ("librecomp/src/rsp.cpp", "base + ", "U", "uint32_t base = off + f * 0xA10u (rsp.cpp:1592): unsigned"),
    ("s7106_rsptri.cpp", "? 64 : 0", "NAR", "sum of constants <= 32 + 64 + 64 + 16 = 176"),
    ("rt64_gbi_f3d.cpp", "w1 - 0x80000000", "U", "w1 is uint32_t: unsigned; F3D HLE never dispatched under LLE gfx"),
]
UNSLIT = re.compile(r"\b(?:0x[0-9A-Fa-f]+|\d+)[uU][lL]*\b")
PTRV = re.compile(r"^\(?\s*(?:rdram|ram|rd|g_rdram_for_submit|RS64_DMEM_BASE|TMEM|segments\s*\[|\(?\s*recomp::alloc|\(?\s*task\s*\))|-\s*(?:events_context\.)?rdram\s*$")
BITF = re.compile(r"->p[01]\s*\(\s*\d+\s*,\s*\d+\s*\)")
def blind_class(rel, a, b, op):
    e = f"{a} {b}"
    for f, needle, c, why in BLIND_HAND:
        if rel.endswith(f) and needle in f"{a} {op} {b}": return c, why or "see above"
    if UNSLIT.search(e): return "U", "an operand carries a u-suffixed literal: unsigned arithmetic"
    if PTRV.search(a.strip()) or PTRV.search(b.strip()): return "PTR", "pointer +/- integer or pointer difference (class AB / T territory), not int arithmetic"
    if BITF.search(e): return "U", "RT64 GBI p0/p1 bitfield accessor returns uint32_t (field <= 24 bits)"
    if re.search(r"&\s*0x[0-9A-Fa-f]{1,6}\b\s*\)", e): return "NAR", "masked to <= 24 bits"
    return "?", ""

st = Counter()
UNTYPED = []   # operand type unresolved, guest-derived, default-on: the blind spot, listed with --untyped
def census(files, pgf):
    rows = []
    OPS = re.compile(r"(?<![+\-])([-+])(=?)(?![-+=>])")
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = s43.ln_fn(p); ftext = "\n".join(lines)
        names = s42.names_of(lines)
        m.MASK = re.compile(r"[-+]")
        done = set()
        for (ln, fn, mk, c, text) in m.sites(p, pgf):
            if ln in done: continue
            done.add(ln)
            raw = lines[ln - 1]
            l = re.sub(r'"(?:\\.|[^"\\])*"', lambda q: '"' + "_" * (len(q.group(0)) - 2) + '"', raw)
            l = re.sub(r"'(?:\\.|[^'\\])'", "'_'", l)
            for tok in ("//", "/*"):
                ci = l.find(tok)
                if ci >= 0: l = l[:ci] + " " * (len(l) - ci)
            if l.lstrip().startswith(("#", "*")): continue
            start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
            ops = []
            for mm in OPS.finditer(l):
                k = mm.start(1)
                if l[k:k + 2] == "->" or re.search(r"\d[eE]$", l[:k]): continue
                prev = l[:k].rstrip()
                unary = (not prev) or prev[-1] in "=(,?:[{!<>&|*/%^~+-" or re.search(r"\b(?:return|case)$", prev)
                if unary:
                    if mm.group(2): continue
                    if mm.group(1) == "+": continue
                    a = s48.rhs_of(l, mm.end())
                    if not a or re.fullmatch(r"\d[\w.]*|0x\w+", a.strip()): continue
                    ops.append(("neg", "", a))
                else:
                    a = s48.lhs_of(l, k); b = s48.rhs_of(l, mm.end())
                    if not a or not b or a in KW or b.startswith('"'): st["S"] += 1; continue
                    ops.append((mm.group(1) + mm.group(2), a, b))
            for mm in re.finditer(r"\b(?:std::)?(?:abs|labs)\s*\(", l):
                ops.append(("abs", "", s43.args_of(l, mm.end())[0]))
            for (op, a, b) in ops:
                ka, ba = opbits(a, body, ftext, names) if a else ("K", 1)
                kb, bb = opbits(b, body, ftext, names)
                kinds = {ka, kb}
                if "FLT" in kinds: st["FLT"] += 1; continue
                if "W64" in kinds: st["W64"] += 1; continue
                if "U32" in kinds: st["U"] += 1; continue
                if "S32" not in kinds:
                    st["other"] += 1
                    if (ka is None or kb is None) and c == "?" and (guest(a, body) or guest(b, body)) and op not in ("neg", "abs") or \
                       (op in ("neg", "abs") and kb is None and c == "?" and guest(b, body)):
                        UNTYPED.append((rel, ln, fn, f"{a} {op} {b}"[:90], blind_class(rel, a, b, op)))
                    continue
                if op in ("+=", "-=") and ka != "S32": st["other"] += 1; continue
                st["raw"] += 1
                cc, why = c, ""
                if cc in "GD" and rel.startswith("lib/rt64/") and not s43.body_gated(lines, ln): cc = "?"
                if cc == "D" and fn in s44.CORE: cc = "?"
                if cc == "?":
                    hh = s43.hand(rel, fn, raw.strip(), HAND)
                    bits = [x for x in (ba, bb)]
                    if hh: cc, why = hh
                    elif None not in bits and (max(bits) + 1 <= 31):
                        cc, why = "NAR", f"widths {ba}/{bb}"
                    elif not guest(a, body) and not guest(b, body):
                        cc, why = "HOST", "no guest-derived operand"
                rows.append((rel, ln, fn, cc, why, f"{a} {op} {b}"[:90], raw.strip()))
    return rows

PLANT = ("static int32_t planted(OSTask* task) {\n    int32_t s = (int32_t)task->a + (int32_t)task->b;\n    return s;\n}\n"
         "static uint32_t u_twin(OSTask* task) {\n    uint32_t s = (uint32_t)task->a + (uint32_t)task->b;\n    return s;\n}\n"
         "static int32_t nar_twin(OSTask* task) {\n    int32_t s = (int16_t)task->a + (int32_t)(task->b & 0xFFFF);\n    return s;\n}\n"
         "static int64_t w64_twin(OSTask* task) {\n    int64_t s = (int64_t)task->a + (int32_t)task->b;\n    return s;\n}\n"
         "static int32_t gated_twin(OSTask* task) {\n    if (!rs64_dlwalk_on()) return 0;\n    int32_t s = (int32_t)task->a + (int32_t)task->b;\n    return s;\n}\n")

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text(PLANT)
        got = {(r[2], r[3]) for r in census([t], pgf)}
        want = {("planted", "?"), ("nar_twin", "NAR"), ("gated_twin", "G")}
        assert got == want, f"control failed: got {got} want {want}"
        assert st["U"] >= 1 and st["W64"] >= 1, f"control failed: U/W64 twins not counted {dict(st)}"
        print("[s7352] controls: planted (int32_t)task->a + (int32_t)task->b '?', int16 twin 'NAR', gated twin 'G', uint32 twin U, int64 twin W64")
        st.clear()
    files = s43.files_in_scope()
    rows = census(files, pgf)
    cc = Counter(r[3] for r in rows)
    print(f"[s7352] signed-32 +/-/neg/abs sites={st['raw']} (not signed-32: W64={st['W64']} U={st['U']} FLT={st['FLT']} untyped={st['other']} skipped={st['S']})")
    print(f"[s7352] class AC sites={len(rows)} files={len(files)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[3] in "?B" or "-v" in sys.argv or ("-h" in sys.argv and r[3] in ("H", "FIX")):
            print(f"  {r[3]} {r[0]}:{r[1]} {r[2]} {r[4]} :: {r[5]}")
    bc = Counter(u[4][0] for u in UNTYPED)
    print(f"[s7352] blind spot (guest-derived operand of unresolved type, default-on): {len(UNTYPED)} " + " ".join(f"{k}={v}" for k, v in sorted(bc.items())))
    for u in UNTYPED:
        if u[4][0] == "?" or "--untyped" in sys.argv: print(f"  {u[4][0]} {u[0]}:{u[1]} {u[2]} {u[4][1]} :: {u[3]}")
    vu = (ROOT / "lib/N64ModernRuntime/librecomp/include/librecomp/rsp_vu_impl.hpp").read_text()
    guard = vu.count("    s32 data = input ^ mask;\n    if (input > -32768) data -= mask;") == 2
    print(f"[s7352] VRCP/VRSQ INT_MIN guard present (tools/s7352_signed_ctl.cpp copies it): {guard}")
    bad = [r for r in rows if r[3] in ("?", "B")] + [u for u in UNTYPED if u[4][0] == "?"] + ([] if guard else [("guard-missing",)])
    print(f"[s7352] unclassified/defect: {len(bad)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
