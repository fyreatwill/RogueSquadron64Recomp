// s7349 control: librecomp __ull_rshift / __ll_lshift old (C shift by the guest count, UB for >= 64) vs new (& 63, MIPS
// dsrlv/dsllv). Build: clang++ -std=c++17 -fsanitize=shift -fno-sanitize-recover=all tools/s7349_shift_ctl.cpp -o /tmp/c
// Run `/tmp/c` (new forms vs a MIPS model, must print PASS) and `/tmp/c old` (old form with count 64: UBSan must abort).
#include <cstdint>
#include <cstdio>
#include <cstring>
static uint64_t mips_dsrlv(uint64_t a, uint32_t rs) { uint32_t s = rs & 63; uint64_t r = a; for (uint32_t i = 0; i < s; ++i) r >>= 1; return r; }
static uint64_t mips_dsllv(uint64_t a, uint32_t rs) { uint32_t s = rs & 63; uint64_t r = a; for (uint32_t i = 0; i < s; ++i) r <<= 1; return r; }
static uint64_t new_r(uint64_t a, uint64_t b) { return a >> (b & 63); }
static uint64_t new_l(uint64_t a, uint64_t b) { return a << (b & 63); }
static uint64_t old_r(uint64_t a, volatile uint64_t b) { return a >> b; }
int main(int argc, char** argv) {
    if (argc > 1 && !strcmp(argv[1], "old")) { printf("old 64: %llx\n", (unsigned long long)old_r(0x8000000000000001ull, 64)); return 0; }
    const uint64_t as[] = {0, 1, 0x8000000000000001ull, 0xDEADBEEFCAFEF00Dull, ~0ull};
    int n = 0, bad = 0;
    for (uint64_t a : as) for (uint64_t b = 0; b < 200; ++b) {
        uint64_t bb = b | (b > 130 ? 0x100000000ull : 0);  // high count word set (guest r6) too
        ++n; if (new_r(a, bb) != mips_dsrlv(a, (uint32_t)bb) || new_l(a, bb) != mips_dsllv(a, (uint32_t)bb)) ++bad;
    }
    printf("[s7349] %d pairs, %d mismatch vs MIPS dsrlv/dsllv: %s\n", n, bad, bad ? "FAIL" : "PASS");
    return bad != 0;
}
