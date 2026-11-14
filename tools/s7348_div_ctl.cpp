// s7348 control: the two class Y fixes against the old forms and against the recompiler's MIPS DDIV/DDIVU (recomp.h).
// Build: clang++ -std=c++17 -O2 -fsanitize=integer-divide-by-zero,signed-integer-overflow -fno-sanitize-recover=all
//        -I lib/N64ModernRuntime/N64Recomp/include tools/s7348_div_ctl.cpp  (argv[1]=old runs the old forms: UBSan must abort)
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <algorithm>
#include "recomp.h"
static inline uint64_t rs64_udiv64(uint64_t a, uint64_t b) { return b ? a / b : ~0ull; }
static inline uint64_t rs64_urem64(uint64_t a, uint64_t b) { return b ? a % b : a; }
static inline int64_t rs64_sdiv64(int64_t a, int64_t b) {
    if (b == 0) return a < 0 ? 1 : -1;
    if ((uint64_t)a == 0x8000000000000000ull && b == -1) return a;
    return a / b;
}
static uint32_t px_old(uint32_t siz) { return 1 << siz >> 1; }
static uint32_t px_new(uint32_t siz) { return std::max(1u, (1u << siz) >> 1); }
int main(int argc, char** argv) {
    volatile int64_t z = 0, m1 = -1, mn = INT64_MIN;
    if (argc > 1 && !strcmp(argv[1], "old")) {   // positive control: the pre-fix forms must trip UBSan
        volatile uint32_t off = 6; printf("old pixelSize(4b)=%u\n", px_old(0));
        if (argc > 2) { volatile int64_t r = mn / m1; printf("%lld\n", (long long)r); }
        volatile uint32_t r = off % px_old(0); printf("unreached %u\n", r); return 0;
    }
    int bad = 0;
    for (uint32_t s = 1; s <= 3; s++) if (px_old(s) != px_new(s)) { bad++; printf("siz %u mismatch\n", s); }
    printf("pixelSize siz0 old=%u new=%u, siz1..3 = %u %u %u\n", px_old(0), px_new(0), px_new(1), px_new(2), px_new(3));
    if (px_new(0) != 1) bad++;
    const int64_t as[] = {0, 1, -1, 7, -7, 1000000007, -1000000007, INT64_MIN, INT64_MAX};
    const int64_t bs[] = {0, 1, -1, 3, -3, 1 << 20, INT64_MIN, INT64_MAX};
    int n = 0;
    for (int64_t a : as) for (int64_t b : bs) {
        int64_t q, r; DDIV(a, b, &q, &r);
        uint64_t uq, ur; DDIVU((uint64_t)a, (uint64_t)b, &uq, &ur);
        if (rs64_sdiv64(a, b) != q) { bad++; printf("sdiv %lld/%lld %lld vs %lld\n", (long long)a, (long long)b, (long long)rs64_sdiv64(a, b), (long long)q); }
        if (rs64_udiv64(a, b) != uq || rs64_urem64(a, b) != ur) { bad++; printf("udiv mismatch %llx %llx\n", (unsigned long long)a, (unsigned long long)b); }
        n++;
    }
    printf("pairs=%d (incl. b=0 and INT64_MIN/-1) vs recomp.h DDIV/DDIVU, sdiv(MIN,-1)=%lld udiv(5,0)=%llx urem(5,0)=%llu z=%lld\n", n,
           (long long)rs64_sdiv64(mn, m1), (unsigned long long)rs64_udiv64(5, z), (unsigned long long)rs64_urem64(5, z), (long long)z);
    printf("bad=%d\n", bad); return bad;
}
