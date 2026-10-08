"""s4218: port-side twin of oracle [audio-objects-frame]: per frame active voices (u16@+0x2C != 0 until first zero or first nonzero +0x44) + voice0 words. Gate ROGUESQ_LOG_S4213=1."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
t = rsp.read_text()
if "[s4218-act]" not in t:
    anchor = "    if (n <= 6 || (n & (n - 1)) == 0) {\n        std::fprintf(stderr, \"[s4214-scan]"
    assert t.count(anchor) == 1
    add = r'''    if (n <= 8 || n % 64 == 0) {
        uint32_t cnt = (uint32_t)task->t.data_size; if (cnt > 4) cnt = 4;
        auto rd32 = [&](uint32_t a) { uint32_t v = 0; for (int k = 0; k < 4; k++) v = (v << 8) | rdram[((a + k) & 0x1FFFFFFFu) ^ 3]; return v; };
        auto rd16 = [&](uint32_t a) { return (uint32_t)((rdram[(a & 0x1FFFFFFFu) ^ 3] << 8) | rdram[((a + 1) & 0x1FFFFFFFu) ^ 3]); };
        for (uint32_t f = 0; f < cnt; f++) {
            uint32_t base = off + f * 0xA10u; unsigned active = 0; uint32_t output = 0;
            for (uint32_t v = 0; v < 32; v++) {
                uint32_t va = base + 0x10 + v * 0x50;
                output = rd32(va + 0x44);
                if (rd16(va + 0x2C) == 0) break;
                active++;
                if (output) break;
            }
            std::fprintf(stderr, "[s4218-act] phase=%u n=%u frame=%u base=%08X h0=%08X state=%08X active=%u output=%08X first=", phase, n, f, base, rd32(base), rd32(base + 8), active, output);
            for (uint32_t i = 0; i < 0x50; i += 4) std::fprintf(stderr, "%08X,", rd32(base + 0x10 + i));
            std::fprintf(stderr, "\n");
        }
    }
'''
    t = t.replace(anchor, add + anchor)
    rsp.write_text(t); print("patched")
