#!/usr/bin/env python3
"""s4221: log the inputs/outputs of the voice-record gain-word writer (musyxKeyOnVoice 0x80090CA4..CC8). Env ROGUESQ_LOG_S4221=1.
Retail oracle (s4221) shows this PC range writes record +0x00..+0x0C from voice-state halfwords +0x6E..+0x74 (<<16).
Idempotent; chained from fixup_game_funcs-style regen via this script."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARK = "PATCH: s4221 gain writer"

def patch_rsp():
    rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
    t = rsp.read_text()
    if "rs64_s4221_gain" in t:
        return
    anchor = 'extern "C" void rs64_s4220_snap(uint32_t pc) {'
    assert t.count(anchor) == 1
    code = r'''extern "C" void rs64_s4221_gain(uint8_t* rdram, uint32_t s0, uint32_t s1, uint32_t ra) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4221"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    static uint32_t ph_key = 0xFFFFFFFFu; static unsigned long calls, nzcalls;
    uint32_t phase = rs64_phase_ord();
    if (phase != ph_key) {
        if (ph_key != 0xFFFFFFFFu) std::fprintf(stderr, "[s4221-sum] phase=%u calls=%lu nonzero_gain_calls=%lu\n", ph_key, calls, nzcalls);
        ph_key = phase; calls = 0; nzcalls = 0;
    }
    auto h = [&](uint32_t a) { return (uint32_t)((rdram[(a & 0x1FFFFFFFu) ^ 2] << 8) | rdram[((a & 0x1FFFFFFFu) + 1) ^ 2]); };
    uint32_t g[4]; bool nz = false;
    for (int i = 0; i < 4; i++) { g[i] = h(s0 + 0x6E + 2 * i); nz |= g[i] != 0; }
    calls++; if (nz) nzcalls++;
    if (calls <= 6 || calls % 256 == 0) {
        std::fprintf(stderr, "[s4221] phase=%u n=%lu s0=%08X s1=%08X ra=%08X gain_src(+6E..74)=%04X,%04X,%04X,%04X vol60..6C=", phase, calls, s0, s1, ra, g[0], g[1], g[2], g[3]);
        for (uint32_t o = 0x5C; o <= 0x6C; o += 2) std::fprintf(stderr, "%04X,", h(s0 + o));
        std::fputc('\n', stderr);
    }
}
'''
    rsp.write_text(t.replace(anchor, code + anchor))

def patch_c():
    s = TARGET.read_text()
    if MARK in s:
        return
    old = "    rs64_probe_submit_gate_store('W', 0x80090CC8u, U32(ADD32(ctx->r17, 0XC)), U32(ctx->r2));\n"
    assert s.count(old) == 1
    s = s.replace(old, old + f"    rs64_s4221_gain(rdram, U32(ctx->r16), U32(ctx->r17), U32(ctx->r31)); /* {MARK} */\n", 1)
    anchor = '#include "funcs.h"\n'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + "extern void rs64_s4221_gain(uint8_t*, uint32_t, uint32_t, uint32_t);\n", 1)
    TARGET.write_text(s)

if __name__ == "__main__":
    patch_rsp(); patch_c(); print("ok")
