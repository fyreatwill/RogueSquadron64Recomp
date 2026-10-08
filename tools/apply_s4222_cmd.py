#!/usr/bin/env python3
"""s4222c: log entry args of dispatchAudioCommand (0x8008DD60: a0=value, a1=time, a2=cmd, a3, sp+0x10) with $ra, phase-gated, capped.
Env ROGUESQ_LOG_S4222=1. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
MARK = "PATCH: s4222 cmd"
CODE = r'''
extern "C" void rs64_s4222_cmd(uint8_t* rdram, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3, uint32_t sp, uint32_t ra) {
    if (!rdram || !rs64_s4222_on()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static unsigned long n[2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (++n[slot] > 400) return;
    uint32_t s10 = 0; for (int k = 0; k < 4; k++) s10 = (s10 << 8) | rdram[((sp + 0x10 + k) & 0x1FFFFFFFu) ^ 3];
    std::fprintf(stderr, "[s4222-C] w=%u n=%lu a0=%08X a1=%08X a2=%08X a3=%08X sp10=%08X ra=%08X\n", width, n[slot], a0, a1, a2, a3, s10, ra);
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4222_cmd" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    s = TARGET.read_text()
    if MARK in s: return
    old = "    // 0x8008DD60: addiu       $sp, $sp, -0x8\n"
    assert s.count(old) == 1
    s = s.replace(old, f"    rs64_s4222_cmd(rdram, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r29), U32(ctx->r31)); /* {MARK} */\n" + old, 1)
    anchor = '#include "funcs.h"\n'
    s = s.replace(anchor, anchor + "extern void rs64_s4222_cmd(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n", 1)
    TARGET.write_text(s)
if __name__ == "__main__":
    patch_cpp(); patch_c(); print("ok")
