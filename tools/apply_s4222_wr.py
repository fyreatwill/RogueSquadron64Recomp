#!/usr/bin/env python3
"""s4222b: per-PC execution counters (phase-gated, printed at powers of two) at the group-volume-table writers in funcs_23.c.
Env ROGUESQ_LOG_S4222=1. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
MARK = "PATCH: s4222 wr"
PCS = ["8008E77C", "8008E788", "8008DF94", "8008DFEC", "8008E028", "8008E07C", "8008E0A0", "8008D77C", "8008D7B4", "8008D7E0", "8008D7EC"]
CODE = r'''
extern "C" void rs64_s4222_pc(uint8_t* rdram, uint32_t pc, uint32_t addr, uint32_t val, uint32_t t1, uint32_t s0) {
    if (!rdram || !rs64_s4222_on()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static unsigned long cnt[2][16] = {}; static uint32_t pcs[16] = {}; static int npc = 0;
    int k = -1; for (int i = 0; i < npc; i++) if (pcs[i] == pc) { k = i; break; }
    if (k < 0) { if (npc >= 16) return; k = npc; pcs[npc++] = pc; }
    const uint32_t slot = width == 1024u ? 0u : 1u;
    const unsigned long n = ++cnt[slot][k];
    if (n <= 12 || (n & (n - 1)) == 0) std::fprintf(stderr, "[s4222-W] w=%u pc=%08X n=%lu at=%08X v0=%08X t1=%08X s0=%08X\n", width, pc, n, addr, val, t1, s0);
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4222_pc" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    s = TARGET.read_text()
    if MARK in s: return
    for pc in PCS:
        old = f"    // 0x{pc}:"
        assert s.count(old) >= 1, pc
        s = s.replace(old, f"    rs64_s4222_pc(rdram, 0x{pc}u, U32(ctx->r1), U32(ctx->r2), U32(ctx->r9), U32(ctx->r16)); /* {MARK} */\n" + old, 1)
    anchor = '#include "funcs.h"\n'
    s = s.replace(anchor, anchor + "extern void rs64_s4222_pc(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n", 1)
    TARGET.write_text(s)
if __name__ == "__main__":
    patch_cpp(); patch_c(); print("ok")
