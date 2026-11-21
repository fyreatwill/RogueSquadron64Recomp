#!/usr/bin/env python3
"""s7344 class U census: wrap-prone uint32 bound checks on guest-derived values.
A clamp of the form `if (a + n > LIMIT)` / `if (a + n <= end)` with 32-bit a and n both from guest data (DMA length,
OSTask size, DL word, DPC start/end) passes when a huge n wraps `a + n` below LIMIT, and the copy/loop then runs with the
raw n. Scope = s7343 files_in_scope() (183 host files). Every comparison with a sum on one side is a site.
Classes: C/P/G/D/R/X/S from tools/s7338_mask_census.py sites() (rt64 G/D re-checked with s7343 body_gated()), then
  K   every sum operand is a constant, or the sum is `<var> + <small constant>` whose var is a loop index of the same
      statement / a value the function already bounded (`v < N`, `v >= N) return`, min) -- no 32-bit wrap reachable
  W64 the sum is computed in >32 bits: a (uint64_t)/(size_t)/(int64_t)/ull cast, or an operand declared 64-bit / size_t /
      float / double / .size() in the function or file
  MSK an operand is masked to <= 24 bits in the function before the check, or declared uint8_t/uint16_t/bool
  SUB subtractive guard already present for the same operand (`n > LIMIT - a`) on an earlier line of the function
  LOOP loop index comparisons `i + k < n` inside a for-header that increments i (i < n holds, k small)
  H   hand-verified (reason in HAND)   B default-on, both operands guest-derived 32-bit, no guard (defect)   ? unclassified
'?' or B => exit 1. --controls plants `if (a + task->data_size > 0x1000) return; memcpy(..)` ('?'), the uint64 twin ('W64'),
the masked twin ('MSK'), and a gated twin ('G'). --regate re-runs the s7338-s7342 censuses' rt64 G/D rows through body_gated()."""
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
s43 = _load("s7343", "tools/s7343_buffer_copy_census.py")
s42, m = s43.s42, s43.m

OP = r"(?:\(\s*(?:u?int\d+_t|size_t|unsigned|int|uint64_t)\s*\)\s*)?[A-Za-z_0-9][\w\.]*(?:->\w+|\.\w+|\[[^\]\[]*\]|\(\s*\))*"
SUM = r"\(?\s*(%s)\s*\+\s*(%s)(?:\s*[-+]\s*(%s))?\s*\)?" % (OP, OP, OP)
CMP = r"(<=|>=|<(?![<=])|>(?![>=]))"
RXA = re.compile(r"(?<![\w\)\]\.>])%s\s*%s\s*(%s)" % (SUM, CMP, OP))          # a + n  cmp  Z
RXB = re.compile(r"(%s)\s*%s\s*%s(?![\w\(\[])" % (OP, CMP, SUM))                 # Z  cmp  a + n
ANY = re.compile(r"(?:%s\s*%s\s*%s|%s\s*%s\s*%s(?![\w\(\[]))" % (SUM, CMP, OP, OP, CMP, SUM))
CONST = re.compile(r"^(?:\d+[uUlL]*|0x[0-9A-Fa-f]+[uUlL]*|sizeof\b.*|[A-Z][A-Z0-9_]{2,}|k[A-Z]\w*)$")
W64T = r"(?:u?int64_t|size_t|ptrdiff_t|uintptr_t|intptr_t|double|float|long\s+long|unsigned\s+long\s+long|uint64_t)"
NARROW = r"(?:uint8_t|int8_t|uint16_t|int16_t|bool|u8|u16|s8|s16)"

HAND = [  # (file suffix, function or '?', needle in line, class, reason)
    ("src/main/main.cpp", "rs64_m5_audio_input_dma", "dram_addr + len", "H", "log-only m5 probe; overlap clamped to const 0x178C80..0x178F18 by min/max"),
    ("src/main/main.cpp", "rs64_m5_host_write_census", "s_ + len", "H", "census overlap test, log-only (no write uses it)"),
    ("src/main/main.cpp", "audio_route_apply_cycle", "pos + 1", "H", "host int menu cursor"),
    ("src/main/main.cpp", "rs64_g1f_target_display", "b.x + b.w", "H", "SDL display rect ints (host)"),
    ("src/main/upstream_compat.cpp", "rs64_s6569_isspill", "spill_cap", "H", "host spill base 0x80800000 + cap <= 0x1000000: no wrap"),
    ("src/main/upstream_compat.cpp", "rs64_fill_add_run", "hi + 4u", "H", "run bounds are KSEG0 guest addresses < 0xA0000000 (+4 cannot wrap)"),
    ("src/main/upstream_compat.cpp", "?", "k.h + 0x10u", "H", "g5a_walk caps h < 0x81000000 and sz <= 0x1000000: sum < 0x82000010"),
    ("src/main/upstream_compat.cpp", "?", "k->h + 0x10u", "H", "g5a_walk caps h < 0x81000000 and sz <= 0x1000000: sum < 0x82000010"),
    ("src/main/upstream_compat.cpp", "s7776_load", "a + (uint32_t)w", "H", "s7776 load-watch overlap test, log-only; a is a marked KSEG0 address < 0x81800000 (bitmap range), w <= 8: no wrap"),
    ("src/main/upstream_compat.cpp", "s7777_sweep", "b + 0x10u", "H", "s7777 chain walk, log-only; b < rs64_ram_top (KSEG0 < 0x81800000) and sz & 0xF checked, and the b + 0x10u + sz <= b clause itself rejects a wrap"),
    ("src/main/upstream_compat.cpp", "s7777_access", "a + (uint32_t)w", "H", "s7777 watch overlap test, log-only; a is a marked KSEG0 address < 0x81800000 (bitmap range), w <= 8: no wrap"),
    ("src/main/upstream_compat.cpp", "s7777_access", "x.bs + x.bsz", "H", "s7777 deref-watch range, log-only; bs >= 0x80154690 is a chain block start < rs64_ram_top and bsz <= 0x40000 is checked first: sum < 0x81840000"),
    ("src/main/upstream_compat.cpp", "floorWriterHit", "+ 4u", "H", "ROGUESQ_FLOOR_DEPTH_DIR probe; t constant target, other side uint64_t(p) + len"),
    ("overlays.cpp", "?", "entry.size + entry.rom_addr", "H", "generated section table (host constants)"),
    ("overlays.cpp", "?", "rom + size", "H", "PI DMA size/rom offset bounded by the s5061 64-bit guard (pi.cpp) before load_overlays_by_start"),
    ("overlays.cpp", "?", "loaded_ram_addr", "H", "ram_addr < rs64_ram_top and size bounded by the s5061 PI DMA guard; section sizes host constants"),
    ("pi.cpp", "save_write_ptr", "assert", "H", "s7344: 64-bit guard added above the assert (osFlash* unreferenced by RS64, latent)"),
    ("pi.cpp", "save_clear", "assert", "H", "s7344: 64-bit guard added above the assert (latent)"),
    ("pi.cpp", "?", "assert(offset + count", "H", "s5235 (uint64_t)offset + count guard returns first"),
    ("rsp.cpp", "rs64_audio_join_m5_event", "stage_event + 64u", "W64", "stage_event uint64_t"),
    ("rsp.cpp", "rs64_s4211_task", "e.dram", "H", "s4211 PI-ring probe, log-only; e.size bounded by s5061"),
    ("src/rsp/s7095_dpc_model.cpp", "?", "m.start", "D", "ROGUESQ_S7095_DPC probe file (getenv gate)"),
    ("src/rsp/s7097_edit_census.cpp", "?", "", "D", "ROGUESQ_S7097_EDIT probe file (getenv gate)"),
    ("src/rsp/s7106_rsptri.cpp", "?", "a + len", "D", "ROGUESQ_S7107_TAG/S7112_TRI probe file; mis++ log"),
    ("src/rsp/s7324_rcp_spill.cpp", "?", "", "D", "ROGUESQ_S7324_RCPREF probe file (getenv gate)"),
    ("src/rsp/s7331_reset_writer.cpp", "?", "", "D", "ROGUESQ_S7331_RESETW probe file (getenv gate)"),
    ("rt64_gbi_f3dfactor5.cpp", "?", "phys + off", "MSK", "phys = addr & 0x00FFFFFF, off < 64"),
    ("rt64_gbi_f3dfactor5.cpp", "?", "length + 1", "MSK", "length is a DL bitfield"),
    ("rt64_gbi_rdp.cpp", "?", "sy1 + gy", "W64", "float coordinates"),
    ("rt64_framebuffer.cpp", "rs64_log_m5_host_boundary", "", "D", "rs64_log_m5 boundary logger; off/step host loop over a host snapshot, explicit off + step < off wrap test"),
    ("rt64_framebuffer_manager.cpp", "?", "tmemStart + tmemWords", "H", "tmemStart & tmemMask; a wrapped tmemWords only shrinks the region-erase bookkeeping (no memory access)"),
    ("rt64_framebuffer_storage.cpp", "?", "rdramIndex + handle.size", "H", "assert on host storage handles"),
    ("rt64_interpreter.cpp", "?", "dl + cmdLength", "W64", "DisplayList* pointer arithmetic (64-bit)"),
    ("rt64_interpreter.cpp", "?", "commandAddress + static_cast", "H", "fprintf argument, not a check"),
    ("rt64_interpreter.cpp", "?", "e.post", "W64", "host pointer compare in a log line"),
    ("rt64_present_queue.cpp", "rs64PresentTestStall", "rows16", "D", "test-stall probe"),
    ("rt64_rsp.cpp", "?", "dstIndex + vtxCount", "MSK", "dstIndex < RSP_MAX_VERTICES checked first; every caller's vtxCount is a <= 8-bit DL bitfield"),
    ("rt64_rsp.cpp", "?", "lightCount + 1", "H", "host int light count"),
    ("rt64_workload_queue.cpp", "?", "frame + 1", "H", "host frame cursor"),
    ("rt64_framebuffer_renderer.cpp", "?", "textureCacheSize + 1", "H", "host cache size"),
    ("rt64_framebuffer_renderer.cpp", "?", "phys0 + 2u", "W64", "uint64_t(abs) - phys0 + 2u"),
    ("rt64_framebuffer_renderer.cpp", "?", "rowStart + rowCount", "H", "host readback rows"),
    ("rt64_framebuffer_renderer.cpp", "?", "g_depthSamples + 1u", "H", "host sample counter vs kDepthCap"),
    ("rsp.hpp", "dma_rdram_to_dmem", "rd_len < rd_len", "H", "s7344 wrap detector (logs the clamp)"),
    ("rsp.hpp", "dma_dmem_to_rdram", "wr_len < wr_len", "H", "s7344 wrap detector (logs the clamp)"),
    ("rsp.hpp", "dma_rdram_to_dmem", "s_dump", "D", "IMEM dump arm (ROGUESQ env s_dump), returns before any copy"),
    ("rsp.hpp", "dma_rdram_to_dmem", "g_rsp_dma_shadow2", "H", "shadow2 serving is ROGUESQ_SHADOW2-gated; rd_len already s7344-clamped <= 0x1000, dram < limit"),
    ("main.cpp", "factor5_gfx_runner", "sh2_phys + sh2_size", "MSK", "sh2_phys = ucode_addr & 0x00FFFFF8, size constant 0x82000 (ROGUESQ_SHADOW2)"),
    ("main.cpp", "factor5_gfx_runner", "+ 8u", "MSK", "DL walk address masked to 24 bits; loop also iteration-capped"),
    ("main.cpp", "rs64_run_lle_gfx", "a + bytes", "MSK", "a = addr & 0x7FFFFF, bytes small int (ROGUESQ_LOG_SEQ)"),
    ("main.cpp", "rs64_run_lle_gfx", "dl + 24", "MSK", "dl masked phys (ROGUESQ_LOG_SEQ)"),
    ("upstream_compat.cpp", "rs64_g1d_blk_dma", "", "H", "DMA end computed in 64 bits (end64) / s7344-clamped len <= 0x1000"),
    ("upstream_compat.cpp", "osSpTaskStartGo_recomp", "dp + 0x4000u", "H", "RS64_GFX_DL_DUMP_DIR arm; dp >= 0x80000000 && dp + 0x4000 cannot wrap below rs64_ram_top unless dp >= 0xFFFFC000 (KSEG2, then >= ram_top fails first only by wrap: dump-only)"),
    ("upstream_compat.cpp", "osSpTaskStartGo_recomp", "q + 8u", "K", "q DMEM offset loop to constant 0x1000"),
    ("rt64_render_context.cpp", "map_result", "", "MSK", "lo/hi_phys = DPC start/end & 0x3FFFFFF (dpc_bridge.cpp:6506) or KSEG0 words < rs64_ram_top; +4..+4096 cannot wrap"),
    ("dpc_bridge.cpp", "rs64_spike_scan", "", "MSK", "DPC lo/hi = start/end & 0x3FFFFFF at rsp_dpc_submit_impl entry; RDP op len <= 176; off < 0x1000000; DMA ring len <= 0x1000 (s7344)"),
    ("dpc_bridge.cpp", "rs64_dpc_defer_end_impl", "", "MSK", "DPC lo/hi = start/end & 0x3FFFFFF at rsp_dpc_submit_impl entry; RDP op len <= 176; off < 0x1000000; DMA ring len <= 0x1000 (s7344)"),
    ("dpc_bridge.cpp", "rs64_dpc_record_submit_impl", "", "MSK", "DPC lo/hi = start/end & 0x3FFFFFF at rsp_dpc_submit_impl entry; RDP op len <= 176; off < 0x1000000; DMA ring len <= 0x1000 (s7344)"),
    ("dpc_bridge.cpp", "rsp_dpc_submit_impl", "", "MSK", "DPC lo/hi = start/end & 0x3FFFFFF at rsp_dpc_submit_impl entry; RDP op len <= 176; off < 0x1000000; DMA ring len <= 0x1000 (s7344)"),
    ("dpc_bridge.cpp", "rs64_i4_fetch", "fx + fy", "W64", "float texel weights"),
    ("librecomp/src/rsp.cpp", "run_task", "", "D", "ROGUESQ_LOG_HUDBIT arm (s_vc_en); tg/d masked 24 bits"),
    ("rsp_vu_impl.hpp", "VRND", "sclip<48>", "W64", "regex false positive: template argument; acc int64"),
]

# Default-on hot paths where the inherited s7337 DIAG rule ('getenv' anywhere earlier in the function) is not a gate: their
# 'D' rows are demoted to '?' and each needs its own reason (HAND).
CORE = {"run_task", "dma_rdram_to_dmem", "dma_dmem_to_rdram", "rsp_dpc_submit_impl", "rs64_spike_scan", "rs64_dpc_record_submit_impl",
        "rs64_dpc_defer_end_impl", "osSpTaskStartGo_recomp", "map_result", "factor5_gfx_runner", "rs64_run_lle_gfx", "rs64_g1d_blk_dma"}

def base(o):
    o = re.sub(r"^\(\s*[\w\s]+\)\s*", "", o.strip()).strip("() ")
    return re.split(r"->|\.|\[", o)[0]

def is_const(o, names):
    o = re.sub(r"^\(\s*[\w\s]+\)\s*", "", o.strip()).strip()
    return bool(CONST.match(o)) or s42.ev(o, names) is not None

def decl(var, text):
    """type keyword(s) of the nearest declaration of var in text (function body or file)."""
    v = re.escape(var)
    mm = None
    for mm in re.finditer(r"\b((?:const\s+)?(?:unsigned\s+)?[\w:]+(?:\s*<[^>]*>)?)\s*[&\*]?\s+%s\s*(?:[=;,\)\[{]|$)" % v, text, re.M): pass
    return mm.group(1) if mm else None

def classify(o, body, ftext, names):
    if is_const(o, names): return "K"
    if re.match(r"^\(\s*(?:u?int64_t|size_t|uintptr_t|unsigned\s+long\s+long)\s*\)", o.strip()) or re.search(r"\d+ull\b|\d+ULL\b", o): return "W64"
    if re.search(r"\.size\(\)|\.length\(\)|sizeof", o): return "W64"
    b = base(o)
    if "->" not in o and "." not in o and "[" not in o:
        t = decl(b, body) or decl(b, ftext)
        if t and re.fullmatch(r"(?:const\s+)?%s" % W64T, t.strip()): return "W64"
        if t and re.fullmatch(r"(?:const\s+)?%s" % NARROW, t.strip()): return "MSK"
        if t and re.fullmatch(r"(?:const\s+)?auto", t.strip()):
            am = re.search(r"\bauto\s+%s\s*=\s*([^;]+);" % re.escape(b), body)
            if am and re.search(r"\.size\(\)|size_t|uint64_t|double|float", am.group(1)): return "W64"
        v = re.escape(b)
        if re.search(r"\b%s\s*&=\s*0x[0-9A-Fa-f]{1,6}\b|\b%s\s*=\s*[^;]*&\s*0x[0-9A-Fa-f]{1,6}u?\s*\)?\s*;|\b%s\s*=\s*[^;]*>>\s*(?:[89]|[12]\d)\b[^;]*;" % (v, v, v), body):
            return "MSK"
        if re.search(r"(?:if\s*\(\s*%s\s*>=?\s*[^)]+\)\s*(?:return|continue|break|%s\s*=)|\b%s\s*=\s*(?:std::)?min\b|\bstd::min(?:<\w+>)?\s*\(\s*%s\b|%s\s*<\s*\w+\s*&&)" % (v, v, v, v, v), body):
            return "BND"
    if re.search(r"&\s*0x[0-9A-Fa-f]{1,6}u?\s*\)?$", o.strip()): return "MSK"
    return None

def census(files, pgf):
    rows = []
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = s43.ln_fn(p); ftext = "\n".join(lines); names = s42.names_of(lines)
        m.MASK = ANY
        for (ln, fn, mk, c, text) in m.sites(p, pgf):
            l = lines[ln - 1]; why = ""
            start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
            if c in "GD" and rel.startswith("lib/rt64/") and not s43.body_gated(lines, ln): c = "?"
            if c == "D" and fn in CORE: c = "?"
            mm = RXA.search(mk + " ") or RXA.search(l) ; a = n = None
            g = re.match(SUM, mk.strip())
            if RXA.fullmatch(mk.strip()) or g:
                mm = RXA.search(mk); a, n = mm.group(1), mm.group(2); z = mm.group(5)
            else:
                mm = RXB.search(mk); z, a, n = mm.group(1), mm.group(3), mm.group(4)
            if c == "?":
                hh = s43.hand(rel, fn, text, HAND)
                ca, cn = classify(a, body, ftext, names), classify(n, body, ftext, names)
                cs = {ca, cn}
                if hh: c, why = hh
                elif re.search(r"\(\s*(?:u?int64_t|size_t|uintptr_t)\s*\)\s*\(?\s*%s" % re.escape(a.strip()), l): c, why = "W64", "64-bit cast on the sum"
                elif "W64" in cs: c, why = "W64", f"{a if ca == 'W64' else n} is >32-bit"
                elif ca == "K" and cn == "K": c, why = "K", "constant operands"
                elif "MSK" in cs: c, why = "MSK", f"{a if ca == 'MSK' else n} <= 24 bits"
                elif re.search(r"\bfor\s*\(", l) and re.search(r";\s*%s\s*\+" % re.escape(a.strip()), l) and cn == "K":
                    c, why = "LOOP", f"loop index {a} + {n}"
                elif re.search(r"\b%s\s*>\s*[^;]*-\s*%s\b" % (re.escape(base(n)), re.escape(base(a))), body) or \
                        re.search(r"\b%s\s*>\s*[^;]*-\s*%s\b" % (re.escape(base(a)), re.escape(base(n))), body):
                    c, why = "SUB", "subtractive guard earlier"
                elif ("K" in cs and "BND" in cs) or cs == {"BND"}: c, why = "K", f"{a}/{n} bounded earlier, small addend"
            rows.append((rel, ln, fn, c, why, f"{a} + {n} ? {z}", text))
    return rows

REGATE = [("s7338", "tools/s7338_mask_census.py", lambda d: [d.MASK]),
          ("s7339", "tools/s7339_mask16_census.py", lambda d: [d.m.MASK]),
          ("s7340", "tools/s7340_kseg16_census.py", lambda d: [d.m.MASK]),
          ("s7341", "tools/s7341_topbyte_census.py", lambda d: [d.TEST]),
          ("s7342", "tools/s7342_addr_index_census.py", lambda d: [d.SUB, d.BITOP])]

def regate(pgf):
    """re-run each earlier census's primary site regex over lib/rt64 and list G/D rows whose enclosing member is not gated."""
    out = []
    rt = [p for p in s43.files_in_scope() if str(p.relative_to(ROOT)).startswith("lib/rt64/")]
    for tag, f, pats in REGATE:
        mod = _load(tag + "r", f); rxs = pats(mod)
        for rx in rxs:
            for p in rt:
                rel = str(p.relative_to(ROOT)); lines = p.read_text(errors="replace").splitlines(); m.MASK = rx
                for (ln, fn, mk, c, text) in m.sites(p, pgf):
                    if c in "GD" and not s43.body_gated(lines, ln): out.append((tag, rel, ln, fn, regate_bucket(tag, text), text))
    return out

def regate_bucket(tag, t):
    """why an ungated earlier-census rt64 row is still harmless (or '?')."""
    if re.search(r"\bconstexpr\b", t): return "K"                          # named 16 MB constant
    if re.search(r">>\s*52\b", t) and "4096" not in t: return "HASH"       # 64-bit hash >> 52 = 12 bits into [4096] tables
    if re.search(r"\bwd\s*>>\s*6\b", t): return "HASH"                   # wd < RDP_TMEM_WORDS_RS64 (512) -> [8]
    if re.search(r"uint64_t|\bull\b|\d+ull\b", t): return "W64"
    if re.search(r'%|fprintf|snprintf|fopen|fwrite|setPrimColor|float\(', t) or (re.match(r"^[\w\s,&|()\.\->\[\]:?*+\-\d]*[,;]?\)?;?$", t) and "=" not in t and "if" not in t):
        return "LOG"                                                        # log / dump argument, debug colour, float maths
    if re.search(r"&\s*0x0*FFFFF[8F]u?\b|AddressMask\s*=|rdramMask\s*=", t): return "R24"  # RDP/DL address: 24-bit by hardware
    if re.search(r"\boff\s*[<+]|len\s*=\s*\(uint32_t\)\(0x01000000u", t): return "R24"
    return "?"

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text("static void planted(uint8_t* rdram, uint32_t a, OSTask* task) {\n    uint8_t b[0x1000];\n"
                     "    if (a + task->data_size > 0x1000) return;\n    memcpy(b + a, rdram, task->data_size);\n}\n"
                     "static void wide_twin(uint8_t* rdram, uint32_t a, OSTask* task) {\n    uint8_t b[0x1000];\n"
                     "    if ((uint64_t)a + task->data_size > 0x1000) return;\n    memcpy(b + a, rdram, task->data_size);\n}\n"
                     "static void masked_twin(uint8_t* rdram, uint32_t a, OSTask* task) {\n    uint8_t b[0x1000];\n"
                     "    uint32_t n = task->data_size;\n    n &= 0xFFF;\n    if (a + n > 0x1000) return;\n    memcpy(b + a, rdram, n);\n}\n"
                     "static void gated_twin(uint8_t* rdram, uint32_t a, OSTask* task) {\n    if (!rs64_dlwalk_on()) return;\n"
                     "    uint8_t b[0x1000];\n    if (a + task->data_size > 0x1000) return;\n    memcpy(b + a, rdram, task->data_size);\n}\n")
        got = {(r[2], r[3]) for r in census([t], pgf)}
        want = {("planted", "?"), ("wide_twin", "W64"), ("masked_twin", "MSK"), ("gated_twin", "G")}
        assert got == want, f"control failed: {got ^ want}"
        print("[s7344] controls: planted a + task->data_size > 0x1000 '?', uint64 twin 'W64', masked twin 'MSK', gated twin 'G'")
    files = s43.files_in_scope()
    rows = census(files, pgf)
    cc = Counter(r[3] for r in rows)
    print(f"[s7344] class U sites={len(rows)} files={len(files)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[3] in "?B" or "-v" in sys.argv or ("-h" in sys.argv and r[3] == "H"):
            print(f"  {r[3]} {r[0]}:{r[1]} {r[2]} {r[4]} :: {r[5][:70]} :: {r[6][:110]}")
    bad = [r for r in rows if r[3] in ("?", "B")]
    hp = (ROOT / "lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp").read_text(errors="replace")
    pi = (ROOT / "lib/N64ModernRuntime/librecomp/src/pi.cpp").read_text(errors="replace")
    for need, txt, what in (("rd_len = rs64_s7344_clamp(dmem_addr, rd_len, 0x1000)", hp, "dma_rdram_to_dmem DMEM clamp"),
                            ("wr_len = rs64_s7344_clamp(dmem_addr, wr_len, 0x1000)", hp, "dma_dmem_to_rdram DMEM clamp"),
                            ("s7344-save-guard] save_write_ptr", pi, "save_write_ptr 64-bit guard"),
                            ("s7344-save-guard] save_clear", pi, "save_clear 64-bit guard")):
        if need not in txt: print(f"  DEFECT s7344 fix missing: {what}"); bad.append(None)
    if "--regate" in sys.argv:
        rg = regate(pgf)
        bc = Counter(r[4] for r in rg)
        print(f"[s7344] regate: {len(rg)} earlier rt64 G/D rows whose enclosing member is not gated: " + " ".join(f"{k}={v}" for k, v in sorted(bc.items())))
        for r in rg:
            if r[4] == "?" or "-v" in sys.argv: print("  R", *r[:5], "::", r[5][:110])
        bad += [r for r in rg if r[4] == "?"]
    print(f"[s7344] unclassified/defect: {len(bad)}")
    bad = list(bad) + census_rules.report("s7344")  # s7654: a stale shared rule fails the gate (after the row printers)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
