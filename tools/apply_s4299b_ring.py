#!/usr/bin/env python3
"""s4299b: turn the s4299 node store watch into a store-HISTORY ring (phys 0x17C000..0x180000, 1M entries of pc/addr/width/seq)
and dump it when the s4298c scan finds a text-valued devAddr word inside that range, so the last guest stores to the
corrupted stream-node ROM pair are named (or their absence shows the writer is host-side: DMA / copyToRAM).
Run after apply_s4299_nodewatch.py. Positive control: the dump prints the ring size/total stores seen. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
RING = r'''
struct S4299Ent { uint32_t pc, addr; uint32_t seq; char w; };
static S4299Ent g_s4299_ring[1 << 20];
static unsigned long g_s4299_total = 0;
extern "C" void rs64_s4299_store_watch(char width, uint32_t pc, uint32_t addr, uint32_t value) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4299"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    (void)value;
    S4299Ent& e = g_s4299_ring[g_s4299_total & ((1u << 20) - 1)];
    e.pc = pc; e.addr = addr; e.seq = (uint32_t)g_s4299_total; e.w = width;
    g_s4299_total++;
}
extern "C" void rs64_s4299_dump(uint32_t lo, uint32_t hi) {
    unsigned long n = g_s4299_total < (1u << 20) ? g_s4299_total : (1u << 20);
    std::fprintf(stderr, "[s4299-D] dump [%08X,%08X) ring total=%lu held=%lu\n", lo, hi, g_s4299_total, n);
    int shown = 0;
    for (unsigned long i = 0; i < n && shown < 24; i++) {
        const S4299Ent& e = g_s4299_ring[(g_s4299_total - 1 - i) & ((1u << 20) - 1)];
        if (e.addr < hi && e.addr + (e.w == 'D' ? 8u : e.w == 'W' ? 4u : e.w == 'H' ? 2u : 1u) > lo) {
            std::fprintf(stderr, "[s4299-D]  back=%lu seq=%u pc=%08X %c addr=%08X\n", i, e.seq, e.pc, e.w, e.addr);
            shown++;
        }
    }
    std::fprintf(stderr, "[s4299-D] matches shown=%d\n", shown);
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4299_dump" in t: return
    a = t.index('extern "C" void rs64_s4299_store_watch')
    b = t.index('extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,')
    f.write_text(t[:a] + RING.lstrip("\n") + t[b:])
def patch_c():
    n = 0
    for p in sorted(RF.glob("funcs_*.c")):
        s = p.read_text()
        if "nw_p >= 0x17D000u && nw_p < 0x17E200u" not in s: continue
        p.write_text(s.replace("nw_p >= 0x17D000u && nw_p < 0x17E200u", "nw_p >= 0x17C000u && nw_p < 0x180000u")); n += 1
    print("widened files:", n)
    p = RF / "funcs_1.c"
    s = p.read_text()
    if "rs64_s4299_dump" not in s:
        old = '                            fprintf(stderr, "\\n");\n                        }\n                    }\n                    fprintf(stderr, "[s4298c] devAddr=0x%08X hits=%d\\n", dv, hits);'
        assert s.count(old) == 1
        new = old.replace('                            fprintf(stderr, "\\n");\n', '                            fprintf(stderr, "\\n");\n                            if (ra_ >= 0x17C000u && ra_ < 0x180000u) rs64_s4299_dump(ra_, ra_ + 8u);\n', 1)
        s = s.replace(old, new, 1)
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\nextern void rs64_s4299_dump(uint32_t, uint32_t);\n', 1)
        p.write_text(s)
if __name__ == "__main__":
    patch_cpp(); patch_c()
