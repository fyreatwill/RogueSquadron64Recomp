#!/usr/bin/env python3
"""s4694b: census of EVERY generated guest store that covers a voice-slot status byte.

The slot status byte is RDRAM 0x80154620 + n*0x1228. s4694 showed the 03->00
transition that releases shutdownMusyXVoices call 3 fires NO [m5-status-store]
row (that hook only sits at PCs 0x8009B30C/B7CC/BBF0). This hooks the same
per-file rs64_m5_writer_parity helper as s4299/s4601 so a store from ANY
generated PC is attributed. Env ROGUESQ_LOG_S4694B=1 (or ROGUESQ_LOG_ALL).
Rows are gated to phase>=4 and capped; each (pc,width) logs its first 8 hits
then every 1000th. A store that never appears here but still flips the byte
is a host-side writer (memset/bzero override, DMA, native helper).

ORIGIN: no mitigation; read-only logging. Idempotent.
"""
from pathlib import Path

R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s4694b status census"
OLD = "static void rs64_m5_writer_parity(char width, uint32_t pc,\n                                   uint32_t addr, uint32_t value) {\n"
CODE = r'''
extern "C" void rs64_s4694b_status_store(char width, uint32_t pc, uint32_t addr, uint32_t value) {
    static const bool on = [] {
        const char* a = std::getenv("ROGUESQ_LOG_ALL"); const char* e = std::getenv("ROGUESQ_LOG_S4694B");
        return (a && a[0] && a[0] != '0') || (e && e[0] && e[0] != '0'); }();
    if (!on) return;
    if (rs64_phase_ord() < 4u) return;
    static int rows = 0;
    static uint32_t keys[256]; static uint32_t cnt[256]; static int nk = 0;
    const uint32_t key = (pc & ~3u) ^ ((uint32_t)width << 28) ^ (uint32_t)width;
    int k = 0; while (k < nk && keys[k] != key) k++;
    if (k == nk) { if (nk >= 256) return; keys[nk] = key; cnt[nk] = 0; nk++; }
    cnt[k]++;
    if (cnt[k] > 8 && (cnt[k] % 1000) != 0) return;
    if (rows >= 800) return;
    rows++;
    std::fprintf(stderr, "[s4694b-status] phase=%u pc=%08X %c addr=%08X val=%08X n=%u\n", rs64_phase_ord(), pc, width, addr, value, cnt[k]);
    std::fflush(stderr);
}
'''
CALL = (
    "    { uint32_t sc_p = addr & 0x1FFFFFFFu; "
    "uint32_t sc_l = width == 'B' ? 1u : (width == 'H' ? 2u : (width == 'D' ? 8u : 4u)); "
    "if (sc_p + sc_l > 0x154620u && sc_p < 0x168DB0u) { "
    "uint32_t sc_k = (sc_p + sc_l - 1u - 0x154620u) / 0x1228u; uint32_t sc_b = 0x154620u + sc_k * 0x1228u; "
    "if (sc_p <= sc_b && sc_b < sc_p + sc_l) rs64_s4694b_status_store(width, pc, addr, value); } } /* " + MARK + " */\n"
)


def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4694b_status_store" in t:
        return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))


def patch_c():
    n = 0
    for p in sorted(RF.glob("funcs_*.c")):
        s = p.read_text()
        if MARK in s or OLD not in s:
            continue
        s = s.replace(OLD, OLD + CALL, 1)
        anchor = '#include "funcs.h"\n'
        s = s.replace(anchor, anchor + "extern void rs64_s4694b_status_store(char, uint32_t, uint32_t, uint32_t);\n", 1)
        p.write_text(s)
        n += 1
    print("patched files:", n)


if __name__ == "__main__":
    patch_cpp()
    patch_c()
