// s7081: runtime side of tools/fixup_selfbranch.py (N64Recomp backward out-of-function
// branch miscompile, s6871). A resampler helper that would branch into its caller's
// "sample finished" tail stores the target here and returns; the caller dispatches.
// ROGUESQ_SELFBRANCH_FIX=0 keeps the old miscompiled path (helper restarts itself).
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <atomic>

extern "C" {
__thread uint32_t g_rs64_sbx_target;
int g_rs64_sbx_on = 1;
void rs64_sbx_hit(uint32_t fn, uint32_t target);
}

namespace {
std::atomic<unsigned long> g_hits{0};
struct Init {
    Init() {
        const char* e = std::getenv("ROGUESQ_SELFBRANCH_FIX");
        if (e && e[0] == '0') g_rs64_sbx_on = 0;
        std::fprintf(stderr, "[s7081 selfbranch] fix %s\n", g_rs64_sbx_on ? "on" : "OFF (old path)");
    }
} g_init;
}

extern "C" void rs64_sbx_hit(uint32_t fn, uint32_t target) {
    unsigned long n = ++g_hits;
    // Never seen live (s6878: 0 hits in 420 s of mission speech); log loudly when it is.
    if (n <= 16 || (n & (n - 1)) == 0)
        std::fprintf(stderr, "[s7081 selfbranch] helper 0x%08X exits to caller tail 0x%08X (hit %lu)\n", fn, target, n);
}
