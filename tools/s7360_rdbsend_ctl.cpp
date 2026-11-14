// s7360 class AK control: links the REAL librecomp print.cpp and drives __osRdbSend_recomp on a fake 8 MB rdram under ASan.
// in-range send -> prints and returns size; past-top / non-KSEG0 / sign-broken buf -> returns 0, no read outside the buffer.
// build: see tools/s7360_rdbsend_ctl.sh
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "recomp.h"
extern "C" void __osRdbSend_recomp(uint8_t* rdram, recomp_context* ctx);
static int call(uint8_t* rd, int64_t buf, uint64_t size) {
    recomp_context c{}; c.r4 = buf; c.r5 = size; c.r6 = 0; c.r2 = 0xDEAD;
    __osRdbSend_recomp(rd, &c); return (int)c.r2;
}
int main() {
    // rdram is addressed as rdram + (addr - 0xFFFFFFFF80000000); allocate exactly 8 MB so any over-read trips ASan.
    uint8_t* rd = (uint8_t*)malloc(0x800000);
    const char* msg = "RDBOK\n"; for (int i = 0; i < 6; i++) rd[(0x1000 + i) ^ 3] = (uint8_t)msg[i];
    int bad = 0;
    struct { const char* n; int64_t b; uint64_t s; int want; } t[] = {
        {"in-range", (int64_t)(int32_t)0x80001000u, 6, 6},
        {"cross-top", (int64_t)(int32_t)0x807FFFF0u, 0x20, 0},
        {"kuseg-null", 0, 4, 0},
        {"unsext", (int64_t)0x80001000ll, 4, 0},
        {"top-exact", (int64_t)(int32_t)0x807FFFFCu, 4, 4},
    };
    for (auto& x : t) { int r = call(rd, x.b, x.s); bool ok = r == x.want; bad += !ok; std::fprintf(stderr, "CTL %-10s r2=%d want %d %s\n", x.n, r, x.want, ok ? "PASS" : "FAIL"); }
    free(rd); return bad ? 1 : 0;
}
