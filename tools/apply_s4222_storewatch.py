#!/usr/bin/env python3
"""s4222e: address watch on the volume-settings bytes 0x80130B60..62 inside the per-file static rs64_m5_writer_parity helper
(called from ~49k store sites), so the first writer to change them is named by PC + value. Env ROGUESQ_LOG_S4222=1. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s4222 storewatch"
OLD = "static void rs64_m5_writer_parity(char width, uint32_t pc,\n                                   uint32_t addr, uint32_t value) {\n"
CODE = r'''
extern "C" void rs64_s4222_store_watch(char width, uint32_t pc, uint32_t addr, uint32_t value) {
    if (!rs64_s4222_on()) return;
    static int rows = 0;
    if (rows >= 60) return;
    rows++;
    std::fprintf(stderr, "[s4222-S] w=%u pc=%08X %c addr=%08X val=%08X\n", rs64_vi_committed_width(), pc, width, addr, value);
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4222_store_watch" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    n = 0
    for p in sorted(RF.glob("funcs_*.c")):
        s = p.read_text()
        if MARK in s or OLD not in s: continue
        s = s.replace(OLD, OLD + f"    {{ uint32_t sw_p = addr & 0x1FFFFFFFu; if (sw_p >= 0x130B5Cu && sw_p < 0x130B64u) rs64_s4222_store_watch(width, pc, addr, value); }} /* {MARK} */\n", 1)
        anchor = '#include "funcs.h"\n'
        s = s.replace(anchor, anchor + "extern void rs64_s4222_store_watch(char, uint32_t, uint32_t, uint32_t);\n", 1)
        p.write_text(s); n += 1
    print("patched files:", n)
if __name__ == "__main__":
    patch_cpp(); patch_c()
