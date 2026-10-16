#!/usr/bin/env python3
"""s5037: host guard on the game's byte-copy primitives memcpy_recomp / bcopy_recomp (M3 idiom class: copy with
wild length or non-RDRAM src/dst). A copy whose len > 8 MiB or whose src/dst span leaves RDRAM
(KSEG0/KSEG1/physical 0..0x7FFFFF) is skipped (returns dst in v0) and logged (first 16).
Env ROGUESQ_COPY_GUARD_FORCE=1 = log-only positive control: every non-empty copy is reported as a violation (first
16 logged) and nothing is skipped. ROGUESQ_COPY_GUARD=0 disables. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
CODE = r'''
extern "C" int rs64_s5037_copy_guard(uint8_t* rdram, uint32_t dst, uint32_t src, uint32_t len, uint32_t ra, int which) {
    static const bool off = [] { const char* e = std::getenv("ROGUESQ_COPY_GUARD"); return e && e[0] == '0'; }();
    static const bool force = [] { const char* e = std::getenv("ROGUESQ_COPY_GUARD_FORCE"); return e && e[0] && e[0] != '0'; }();
    if (off || !rdram || len == 0) return 0;
    auto span_ok = [len](uint32_t a) {
        uint32_t p = a & 0x1FFFFFFFu;
        bool seg = (a < 0x00800000u) || (a >= 0x80000000u && a < 0x80800000u) || (a >= 0xA0000000u && a < 0xA0800000u);
        return seg && (uint64_t)p + len <= 0x800000u;
    };
    bool bad = len > 0x800000u || !span_ok(dst) || !span_ok(src);
    static int shown = 0; static unsigned long viol = 0;
    if (force) bad = true;
    if (!bad) return 0;
    ++viol;
    if (shown < 16) { ++shown;
        std::fprintf(stderr, "[s5037-copy-guard] %s ra=%08X dst=%08X src=%08X len=%u viol=%lu%s\n",
                     which ? "bcopy" : "memcpy", ra, dst, src, len, viol, force ? " (FORCE control, not skipped)" : " SKIPPED");
    }
    return force ? 0 : 1;
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s5037_copy_guard" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    p = RF / "funcs_8.c"
    s = p.read_text()
    if "PATCH: s5037 copy guard" in s: return
    for name, which in (("memcpy_recomp", 0), ("bcopy_recomp", 1)):
        sig = "RECOMP_FUNC void %s(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n" % name
        assert s.count(sig) == 1, name
        s = s.replace(sig, sig + "    if (rs64_s5037_copy_guard(rdram, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r31), %d)) { ctx->r2 = ctx->r4; return; } /* PATCH: s5037 copy guard */\n" % which)
    a = '#include "funcs.h"\n'
    s = s.replace(a, a + "extern int rs64_s5037_copy_guard(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t, int);\n", 1)
    p.write_text(s)
if __name__ == "__main__":
    patch_cpp(); patch_c(); print("ok")
