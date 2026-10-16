#!/usr/bin/env python3
"""s5041: log-only double-free census (M3 use-after-free class). rs_malloc is wrapped so every returned pointer is
erased from a host shadow set of freed pointers; rs_free entry inserts the pointer and reports a pointer already in
the set (freed twice with no allocation between). ROGUESQ_FREE_CENSUS=1 arms; ROGUESQ_FREE_CENSUS_FORCE=1 reports every
free as a double free (positive control). Prints totals at power-of-two free counts. Skips nothing. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
CODE = r'''
#include <unordered_set>
static std::unordered_set<uint32_t> s_s5041_freed;
static bool s5041_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_FREE_CENSUS"); return e && e[0] && e[0] != '0'; }(); return on; }
extern "C" void rs64_s5041_free(uint32_t ptr, uint32_t ra) {
    static const bool force = [] { const char* e = std::getenv("ROGUESQ_FREE_CENSUS_FORCE"); return e && e[0] && e[0] != '0'; }();
    if (!s5041_on() || ptr == 0) return;
    static unsigned long nfree = 0, ndouble = 0; static int shown = 0;
    ++nfree;
    bool dbl = !s_s5041_freed.insert(ptr).second;
    if (force) dbl = true;
    if (dbl) { ++ndouble; if (shown < 16) { ++shown;
        std::fprintf(stderr, "[s5041-free-census] DOUBLE ptr=%08X ra=%08X nfree=%lu ndouble=%lu%s\n", ptr, ra, nfree, ndouble, force ? " (FORCE control)" : ""); } }
    if ((nfree & (nfree - 1)) == 0) std::fprintf(stderr, "[s5041-free-census] total nfree=%lu ndouble=%lu live_freed=%zu\n", nfree, ndouble, s_s5041_freed.size());
}
extern "C" void rs64_s5041_malloc(uint32_t ptr) {
    if (!s5041_on() || ptr == 0) return;
    s_s5041_freed.erase(ptr);
}
'''
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s5041_free" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    p = RF / "funcs_0.c"
    s = p.read_text()
    if "PATCH: s5041" in s: return
    hook = '    { // PATCH: rs_free log (s140)'
    assert s.count(hook) == 1
    s = s.replace(hook, '    rs64_s5041_free(U32(ctx->r4), U32(ctx->r31)); /* PATCH: s5041 free census */\n' + hook, 1)
    sig = "RECOMP_FUNC void rs_malloc(uint8_t* rdram, recomp_context* ctx) {\n"
    assert s.count(sig) == 1
    s = s.replace(sig, "RECOMP_FUNC void rs_malloc_s5041_inner(uint8_t* rdram, recomp_context* ctx);\n"
        "RECOMP_FUNC void rs_malloc(uint8_t* rdram, recomp_context* ctx) { rs_malloc_s5041_inner(rdram, ctx); rs64_s5041_malloc(U32(ctx->r2)); } /* PATCH: s5041 malloc wrap */\n"
        "RECOMP_FUNC void rs_malloc_s5041_inner(uint8_t* rdram, recomp_context* ctx) {\n", 1)
    a = '#include "funcs.h"\n'
    assert a in s
    s = s.replace(a, a + "extern void rs64_s5041_free(uint32_t, uint32_t);\nextern void rs64_s5041_malloc(uint32_t);\n", 1)
    p.write_text(s)
if __name__ == "__main__":
    patch_cpp(); patch_c(); print("ok")
