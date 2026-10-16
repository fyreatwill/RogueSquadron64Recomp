#!/usr/bin/env python3
"""s5042: read-after-free probe. At rs_free entry, ROGUESQ_FREE_POISON=1 overwrites the first 16 payload bytes of the
freed block with 0xDEADBEEF (only when the heap header at ptr-0x10 holds a sane size at +4 with payload >= 16 bytes).
A crash / new guard fire in the poison arm only = a reader of freed memory. Counters: poisoned, skipped (bad header),
and a read-back verification (the control: poison must visibly land in guest RDRAM). Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
CODE = r'''
static inline uint32_t s5042_rd(const uint8_t* rd, uint32_t off) { return ((uint32_t)rd[off ^ 3u] << 24) | ((uint32_t)rd[(off + 1) ^ 3u] << 16) | ((uint32_t)rd[(off + 2) ^ 3u] << 8) | rd[(off + 3) ^ 3u]; }
extern "C" void rs64_s5042_poison(uint8_t* rdram, uint32_t ptr, uint32_t ra) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_FREE_POISON"); return e && e[0] && e[0] != '0'; }();
    if (!on || ptr < 0x80000010u || ptr >= 0x80800000u || (ptr & 3u)) return;
    static unsigned long npoison = 0, nskip = 0, nverify_bad = 0; static int shown = 0;
    uint32_t off = ptr - 0x80000000u;
    uint32_t sz = s5042_rd(rdram, off - 0x10 + 4);
    if (sz < 0x20 || sz > 0x700000u || off + 16 > 0x800000u) { ++nskip; if (shown < 8) { ++shown; std::fprintf(stderr, "[s5042-poison] SKIP ptr=%08X sz=%08X ra=%08X\n", ptr, sz, ra); } return; }
    for (uint32_t i = 0; i < 16; i += 4) { uint32_t v = 0xDEADBEEFu; for (int k = 0; k < 4; k++) rdram[(off + i + k) ^ 3u] = (uint8_t)(v >> (24 - 8 * k)); }
    bool ok = s5042_rd(rdram, off) == 0xDEADBEEFu && s5042_rd(rdram, off + 12) == 0xDEADBEEFu;
    if (!ok) ++nverify_bad;
    ++npoison;
    if ((npoison & (npoison - 1)) == 0) std::fprintf(stderr, "[s5042-poison] total poisoned=%lu skipped=%lu verify_bad=%lu last ptr=%08X sz=%08X ra=%08X\n", npoison, nskip, nverify_bad, ptr, sz, ra);
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s5042_poison" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    p = RF / "funcs_0.c"
    s = p.read_text()
    if "PATCH: s5042" in s: return
    hook = '    rs64_s5041_free(U32(ctx->r4), U32(ctx->r31)); /* PATCH: s5041 free census */\n'
    assert s.count(hook) == 1
    s = s.replace(hook, hook + '    rs64_s5042_poison(rdram, U32(ctx->r4), U32(ctx->r31)); /* PATCH: s5042 free poison */\n', 1)
    a = "extern void rs64_s5041_malloc(uint32_t);\n"
    assert a in s
    s = s.replace(a, a + "extern void rs64_s5042_poison(uint8_t*, uint32_t, uint32_t);\n", 1)
    p.write_text(s)
if __name__ == "__main__":
    patch_cpp(); patch_c(); print("ok")
