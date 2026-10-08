#!/usr/bin/env python3
"""s4221: log inputs/result of computeVoiceVolumePanCoefficients (0x800940D4) at its first store 0x80094198. Env ROGUESQ_LOG_S4221=1.
Retail oracle (s4221): the per-voice bus volumes (voice object +0x44..+0x4A) are written only by 0x80094198/942BC/942C0/94338 in this function.
Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_25.c")
MARK = "PATCH: s4221 coef"

CODE = r'''extern "C" void rs64_s4221_coef(uint8_t* rdram, uint32_t sp, uint32_t res, uint32_t a2, uint32_t outp) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4221"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    static uint32_t ph_key = 0xFFFFFFFFu; static unsigned long calls, nzcalls;
    uint32_t phase = rs64_phase_ord();
    if (phase != ph_key) { ph_key = phase; calls = 0; nzcalls = 0; }
    auto w = [&](uint32_t a) { uint32_t v = 0; for (int k = 0; k < 4; k++) v = (v << 8) | rdram[((a + k) & 0x1FFFFFFFu) ^ 3]; return v; };
    calls++; if (res & 0xFFFF) nzcalls++;
    if (calls <= 6 || calls % 256 == 0) {
        std::fprintf(stderr, "[s4221-coef] phase=%u n=%lu nzres=%lu res=%08X vol(sp0)=%08X a2now=%08X pan(sp14)=%08X out=%08X tabV=%08X,%08X,%08X tabS=%08X,%08X,%08X,%08X tabP=%08X,%08X\n", phase, calls, nzcalls, res, w(sp), a2, w(sp + 0x14), outp, w(0x800A4BD8), w(0x800A4BDC), w(0x800A4BE0), w(0x800A4DD8), w(0x800A4DDC), w(0x800A4DE0), w(0x800A4DE4), w(0x800A4DE8), w(0x800A4DEC));
    }
}
'''

def patch_rsp():
    rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
    t = rsp.read_text()
    if "rs64_s4221_coef" in t:
        return
    anchor = 'extern "C" void rs64_s4220_snap(uint32_t pc) {'
    assert t.count(anchor) == 1
    rsp.write_text(t.replace(anchor, CODE + anchor))

def patch_c():
    s = TARGET.read_text()
    if MARK in s:
        return
    old = "    // 0x80094198: sh          $t0, 0x0($t1)\n"
    assert s.count(old) == 1
    s = s.replace(old, f"    rs64_s4221_coef(rdram, U32(ctx->r29), U32(ctx->r8), U32(ctx->r6), U32(ctx->r9)); /* {MARK} */\n" + old, 1)
    anchor = '#include "funcs.h"\n'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + "extern void rs64_s4221_coef(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t);\n", 1)
    TARGET.write_text(s)

if __name__ == "__main__":
    patch_rsp(); patch_c(); print("ok")
