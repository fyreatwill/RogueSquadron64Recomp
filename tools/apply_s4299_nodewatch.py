#!/usr/bin/env python3
"""s4299: guest store watch on the musyx stream-node block (phys 0x17D000..0x17E200) to name the writer (PC + addr) of the
ASCII text that replaces node ROM-pair words. Hooks the same per-file rs64_m5_writer_parity helper as s4222 storewatch.
Env ROGUESQ_LOG_S4299=1. Note: several call sites pass value=0, so value is informational only. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s4299 nodewatch"
OLD = "static void rs64_m5_writer_parity(char width, uint32_t pc,\n                                   uint32_t addr, uint32_t value) {\n"
CODE = r'''
extern "C" void rs64_s4299_store_watch(char width, uint32_t pc, uint32_t addr, uint32_t value) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4299"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    static int rows = 0;
    static uint32_t pcs[512]; static uint32_t pcn[512]; static int npc = 0;
    int k = 0; while (k < npc && pcs[k] != pc) k++;
    if (k == npc) { if (npc >= 512) return; pcs[npc] = pc; pcn[npc] = 0; npc++; }
    pcn[k]++;
    if (pcn[k] > 24 && (pcn[k] % 1000) != 0) return;
    if (rows >= 6000) return;
    rows++;
    std::fprintf(stderr, "[s4299-S] w=%u pc=%08X %c addr=%08X val=%08X n=%u\n", rs64_vi_committed_width(), pc, width, addr, value, pcn[k]);
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4299_store_watch" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    n = 0
    for p in sorted(RF.glob("funcs_*.c")):
        s = p.read_text()
        if MARK in s or OLD not in s: continue
        s = s.replace(OLD, OLD + f"    {{ uint32_t nw_p = addr & 0x1FFFFFFFu; if (nw_p >= 0x17D000u && nw_p < 0x17E200u) rs64_s4299_store_watch(width, pc, addr, value); }} /* {MARK} */\n", 1)
        anchor = '#include "funcs.h"\n'
        s = s.replace(anchor, anchor + "extern void rs64_s4299_store_watch(char, uint32_t, uint32_t, uint32_t);\n", 1)
        p.write_text(s); n += 1
    print("patched files:", n)
if __name__ == "__main__":
    patch_cpp(); patch_c()
