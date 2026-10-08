#!/usr/bin/env python3
"""s4299c: the s4299b store-history ring only sees stores that pass rs64_m5_writer_parity; the 414 do_swl/do_swr sites (unaligned
word stores, what memcpy/struct-copy idioms emit) bypass it. Wrap them with a macro that records (fn, line, addr) into the same
ring, so the ring dump can say 'last swl/swr to the node ROM pair came from <function>:<line>'. Run after apply_s4299b_ring.py.
Control: dump prints how many swl/swr entries the ring holds in total. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s4299 swlr"
MACRO = (
    "extern void rs64_s4299_swlr(char, const char*, uint32_t, uint32_t); /* " + MARK + " */\n"
    "#define do_swl(rd_, off_, reg_, val_) (rs64_s4299_swlr('L', __func__, __LINE__, (uint32_t)((reg_) + (off_))), do_swl((rd_), (off_), (reg_), (val_)))\n"
    "#define do_swr(rd_, off_, reg_, val_) (rs64_s4299_swlr('R', __func__, __LINE__, (uint32_t)((reg_) + (off_))), do_swr((rd_), (off_), (reg_), (val_)))\n"
)
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4299_swlr" in t: return
    t = t.replace("struct S4299Ent { uint32_t pc, addr; uint32_t seq; char w; };",
                  "struct S4299Ent { uint32_t pc, addr; uint32_t seq; char w; const char* fn; };", 1)
    t = t.replace("e.pc = pc; e.addr = addr; e.seq = (uint32_t)g_s4299_total; e.w = width;",
                  "e.pc = pc; e.addr = addr; e.seq = (uint32_t)g_s4299_total; e.w = width; e.fn = nullptr;", 1)
    add = r'''extern "C" void rs64_s4299_swlr(char w, const char* fn, uint32_t line, uint32_t addr) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4299"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    g_s4299_swlr_total++;
    uint32_t p = addr & 0x1FFFFFFFu;
    if (p < 0x17C000u || p >= 0x180000u) return;
    S4299Ent& e = g_s4299_ring[g_s4299_total & ((1u << 20) - 1)];
    e.pc = line; e.addr = addr; e.seq = (uint32_t)g_s4299_total; e.w = w; e.fn = fn;
    g_s4299_total++;
}
'''
    t = t.replace("static unsigned long g_s4299_total = 0;\n", "static unsigned long g_s4299_total = 0;\nstatic unsigned long g_s4299_swlr_total = 0;\n", 1)
    anchor = 'extern "C" void rs64_s4299_dump(uint32_t lo, uint32_t hi) {'
    assert t.count(anchor) == 1
    t = t.replace(anchor, add + anchor, 1)
    t = t.replace('std::fprintf(stderr, "[s4299-D] dump [%08X,%08X) ring total=%lu held=%lu\\n", lo, hi, g_s4299_total, n);',
                  'std::fprintf(stderr, "[s4299-D] dump [%08X,%08X) ring total=%lu held=%lu swlr_calls=%lu\\n", lo, hi, g_s4299_total, n, g_s4299_swlr_total);', 1)
    t = t.replace('std::fprintf(stderr, "[s4299-D]  back=%lu seq=%u pc=%08X %c addr=%08X\\n", i, e.seq, e.pc, e.w, e.addr);',
                  'std::fprintf(stderr, "[s4299-D]  back=%lu seq=%u pc=%08X %c addr=%08X fn=%s\\n", i, e.seq, e.pc, e.w, e.addr, e.fn ? e.fn : "-");', 1)
    t = t.replace("e.w == 'D' ? 8u : e.w == 'W' ? 4u : e.w == 'H' ? 2u : 1u", "e.w == 'D' ? 8u : (e.w == 'W' || e.w == 'L' || e.w == 'R') ? 4u : e.w == 'H' ? 2u : 1u", 1)
    f.write_text(t)
def patch_c():
    n = 0
    for p in sorted(RF.glob("funcs_*.c")):
        s = p.read_text()
        if MARK in s or "do_sw" not in s: continue
        a = '#include "funcs.h"\n'
        assert a in s
        p.write_text(s.replace(a, a + MACRO, 1)); n += 1
    print("swlr-wrapped files:", n)
if __name__ == "__main__":
    patch_cpp(); patch_c()
