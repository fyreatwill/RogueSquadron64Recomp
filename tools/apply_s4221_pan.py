#!/usr/bin/env python3
"""s4221: dump the per-bus volume inputs after 8008F4D8 returns in musyxRenderVoiceSamples (0x800908F0). Env ROGUESQ_LOG_S4221=1.
Gains = s1[0x44..0x4A] (u16) * float s1[0x5C]; the record gain words come from these. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARK = "PATCH: s4221 pan"

CODE = r'''extern "C" void rs64_s4221_pan(uint8_t* rdram, uint32_t s1, uint32_t sp, uint32_t s5) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4221"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    static uint32_t ph_key = 0xFFFFFFFFu; static unsigned long calls, nzcalls;
    uint32_t phase = rs64_phase_ord();
    if (phase != ph_key) { ph_key = phase; calls = 0; nzcalls = 0; }
    auto h = [&](uint32_t a) { return (uint32_t)((rdram[(a & 0x1FFFFFFFu) ^ 2] << 8) | rdram[((a & 0x1FFFFFFFu) + 1) ^ 2]); };
    auto w = [&](uint32_t a) { uint32_t v = 0; for (int k = 0; k < 4; k++) v = (v << 8) | rdram[((a + k) & 0x1FFFFFFFu) ^ 3]; return v; };
    bool nz = h(s1 + 0x44) | h(s1 + 0x46) | h(s1 + 0x48) | h(s1 + 0x4A);
    calls++; if (nz) nzcalls++;
    if (calls <= 6 || calls % 256 == 0) {
        std::fprintf(stderr, "[s4221-pan] phase=%u n=%lu nzcalls=%lu s1=%08X a1(s5)=%04X h44..4A=%04X,%04X,%04X,%04X f5C=%08X w38..40=%08X,%08X,%08X sp28=%08X,%08X,%08X,%08X\n", phase, calls, nzcalls, s1, s5 & 0xFFFF, h(s1 + 0x44), h(s1 + 0x46), h(s1 + 0x48), h(s1 + 0x4A), w(s1 + 0x5C), w(s1 + 0x38), w(s1 + 0x3C), w(s1 + 0x40), w(sp + 0x28), w(sp + 0x2C), w(sp + 0x30), w(sp + 0x34));
    }
}
'''

def patch_rsp():
    rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
    t = rsp.read_text()
    if "rs64_s4221_pan" in t:
        return
    anchor = 'extern "C" void rs64_s4220_snap(uint32_t pc) {'
    assert t.count(anchor) == 1
    rsp.write_text(t.replace(anchor, CODE + anchor))

def patch_c():
    s = TARGET.read_text()
    if MARK in s:
        return
    old = "    // 0x800908F0: lh          $v0, 0x44($s1)\n"
    assert s.count(old) == 1
    s = s.replace(old, f"    rs64_s4221_pan(rdram, U32(ctx->r17), U32(ctx->r29), U32(ctx->r21)); /* {MARK} */\n" + old, 1)
    anchor = "extern void rs64_s4221_gain(uint8_t*, uint32_t, uint32_t, uint32_t);\n"
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + "extern void rs64_s4221_pan(uint8_t*, uint32_t, uint32_t, uint32_t);\n", 1)
    TARGET.write_text(s)

if __name__ == "__main__":
    patch_rsp(); patch_c(); print("ok")
