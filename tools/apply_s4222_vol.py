#!/usr/bin/env python3
"""s4222d: ungated first-N hit log at the writers/readers of the volume-settings struct 0x80130B40 (+0x20..0x22 = master/music/sfx bytes,
+0x10 flag word). Each row prints the three bytes and the flag word so a writer that never runs or writes 0 is visible.
Env ROGUESQ_LOG_S4222=1. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s4222 vol"
SITES = {  # file -> [pc]
    "funcs_17.c": ["8006E5F8", "8006E0C8", "8006E468"],
    "funcs_27.c": ["800A5E10", "800A5E28"],
}
CODE = r'''
extern "C" void rs64_s4222_vol(uint8_t* rdram, uint32_t pc, uint32_t a0) {
    if (!rdram || !rs64_s4222_on()) return;
    static unsigned long cnt[16] = {}; static uint32_t pcs[16] = {}; static int npc = 0;
    int k = -1; for (int i = 0; i < npc; i++) if (pcs[i] == pc) { k = i; break; }
    if (k < 0) { if (npc >= 16) return; k = npc; pcs[npc++] = pc; }
    const unsigned long n = ++cnt[k];
    if (n > 16 && (n & (n - 1)) != 0) return;
    const auto B = [rdram](uint32_t a) { return (uint32_t)rdram[(a & 0x1FFFFFFFu) ^ 3]; };
    uint32_t fl = 0; for (int j = 0; j < 4; j++) fl = (fl << 8) | B(0x80130B50u + j);
    std::fprintf(stderr, "[s4222-V] w=%u pc=%08X n=%lu a0=%08X vol=%02X,%02X,%02X b23=%02X flags=%08X\n", rs64_vi_committed_width(), pc, n, a0, B(0x80130B60u), B(0x80130B61u), B(0x80130B62u), B(0x80130B63u), fl);
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4222_vol" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    for name, pcs in SITES.items():
        p = RF / name
        s = p.read_text()
        if MARK in s: continue
        for pc in pcs:
            old = f"    // 0x{pc}:"
            assert s.count(old) >= 1, pc
            s = s.replace(old, f"    rs64_s4222_vol(rdram, 0x{pc}u, U32(ctx->r4)); /* {MARK} */\n" + old, 1)
        anchor = '#include "funcs.h"\n'
        s = s.replace(anchor, anchor + "extern void rs64_s4222_vol(uint8_t*, uint32_t, uint32_t);\n", 1)
        p.write_text(s)
if __name__ == "__main__":
    patch_cpp(); patch_c(); print("ok")
