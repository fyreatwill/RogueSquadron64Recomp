#!/usr/bin/env python3
"""s4223: log memcpy_recomp calls whose destination is the settings struct 0x8013A5C0 (retail: ra=0x80006a40, len 0xAF,
src 0x80194FC8, src+0x10 = 7f7f7f00). Env ROGUESQ_LOG_S4223=1. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
CODE = r'''
extern "C" void rs64_s4223_memcpy(uint8_t* rdram, uint32_t dst, uint32_t src, uint32_t len, uint32_t ra) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4223"); return e && e[0] && e[0] != '0'; }();
    if (!rdram || !on || dst != 0x8013A5C0u) return;
    static int n = 0; if (++n > 16) return;
    std::fprintf(stderr, "[s4223-memcpy] ra=%08X dst=%08X src=%08X len=%u src+0x10=", ra, dst, src, len);
    for (uint32_t o = 0x10; o < 0x20; o++) std::fprintf(stderr, "%02x", rdram[((src + o) & 0x1FFFFFFFu) ^ 3]);
    std::fprintf(stderr, "\n");
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4223_memcpy" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    p = RF / "funcs_8.c"
    s = p.read_text()
    if "PATCH: s4223 memcpy" in s: return
    sig = "RECOMP_FUNC void memcpy_recomp(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
    assert s.count(sig) == 1
    s = s.replace(sig, sig + "    rs64_s4223_memcpy(rdram, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r31)); /* PATCH: s4223 memcpy */\n")
    a = '#include "funcs.h"\n'
    s = s.replace(a, a + "extern void rs64_s4223_memcpy(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t);\n", 1)
    p.write_text(s)
if __name__ == "__main__":
    patch_cpp(); patch_c(); print("ok")
