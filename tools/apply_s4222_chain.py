#!/usr/bin/env python3
"""s4222: log every factor of the tickAllAudioChannels volume product (a1 of the 0x8008D710 call).
Hook A at 0x8008D5F0 (after the table scalings), hook B at 0x8008D6F4 (final s2/s3/s0). Env ROGUESQ_LOG_S4222=1. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
MARK = "PATCH: s4222 chain"
CODE = r'''
static bool rs64_s4222_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4222"); return e && e[0] && e[0] != '0'; }(); return on; }
extern "C" void rs64_s4222_chain(uint8_t* rdram, uint32_t which, uint32_t s1, uint32_t s2, uint32_t s3, uint32_t s4, uint32_t fp) {
    if (!rdram || !rs64_s4222_on()) return;
    uint32_t width = 0, origin = 0;
    if (!rs64_m5_voice_modulation_phase(&width, &origin)) return;
    static uint32_t rows[2][2] = {}; static unsigned long calls[2][2] = {}, nz[2][2] = {};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    calls[slot][which]++; if (s2) nz[slot][which]++;
    if (rows[slot][which] >= 48u) return;
    rows[slot][which]++;
    const auto w = [rdram](uint32_t g) -> uint32_t { if (g < 0x80000000u || g > 0x807FFFFCu) return 0xFFFFFFFFu; const uint8_t* p = rdram + (g - 0x80000000u); return ((uint32_t)p[3] << 24) | ((uint32_t)p[2] << 16) | ((uint32_t)p[1] << 8) | p[0]; };
    // rdram is stored host-word-swapped (byte ^ 3): reuse the idiom from s4221
    const auto W = [rdram](uint32_t a) { uint32_t v = 0; for (int k = 0; k < 4; k++) v = (v << 8) | rdram[((a + k) & 0x1FFFFFFFu) ^ 3]; return v; };
    const auto H = [rdram](uint32_t a) { uint32_t v = 0; for (int k = 0; k < 2; k++) v = (v << 8) | rdram[((a + k) & 0x1FFFFFFFu) ^ 3]; return v; };
    const auto B = [rdram](uint32_t a) { return (uint32_t)rdram[(a & 0x1FFFFFFFu) ^ 3]; };
    (void)w;
    const uint32_t base = 0x80140000u + s1;
    if (which == 0) {
        const uint32_t idx = B(base - 0x26C6), grp = B(base - 0x2751);
        std::fprintf(stderr, "[s4222-A] w=%u n=%lu nzs2=%lu s1=%08X s2=%08X raw(-2750)=%08X rec(-275C)=%08X idx=%u t1B30=%04X t1B18=%04X m370=%04X flag(-2730)=%02X grp=%02X t1AD8=%02X s3=%08X s4=%02X\n",
            width, calls[slot][0], nz[slot][0], s1, s2, W(base - 0x2750), W(base - 0x275C), idx, H(0x80141B30u + idx * 40u), H(0x80141B18u + idx * 40u), H(0x80141B18u + 0x370u), B(base - 0x2730), grp, grp == 0xFF ? 0xFFu : B(0x80141AD8u + grp), s3, s4 & 0xFF);
    } else {
        const uint32_t s0 = s1 + fp;
        std::fprintf(stderr, "[s4222-B] w=%u n=%lu nzs2=%lu s1=%08X s2(final)=%08X s3=%08X s0rec=%08X lerp@C0=%04X D2=%04X E4=%04X 150=%04X byteMasterOn(80148...)=%02X\n",
            width, calls[slot][1], nz[slot][1], s1, s2, s3, s0, H(s0 + 0xC0), H(s0 + 0xD2), H(s0 + 0xE4), H(s0 + 0x150), B(0x80150000u - 0x7C38u));
    }
    std::fflush(stderr);
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4222_chain" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    s = TARGET.read_text()
    if MARK in s: return
    for old, which in (("    // 0x8008D5F0: beq         $s4, $a1, L_8008D690\n", 0), ("    // 0x8008D6F4: addu        $a1, $s2, $zero\n", 1)):
        assert s.count(old) == 1, old
        s = s.replace(old, f"    rs64_s4222_chain(rdram, {which}u, U32(ctx->r17), U32(ctx->r18), U32(ctx->r19), U32(ctx->r20), U32(ctx->r30)); /* {MARK} */\n" + old, 1)
    anchor = '#include "funcs.h"\n'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + "extern void rs64_s4222_chain(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n", 1)
    TARGET.write_text(s)
if __name__ == "__main__":
    patch_cpp(); patch_c(); print("ok")
