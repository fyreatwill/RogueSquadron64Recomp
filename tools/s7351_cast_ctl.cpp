// s7351 control: RT64 Framebuffer copyRAMToNativeAndChanges / copyNativeToRAM word swap, old (uint32_t* deref of
// RDRAM + colour image address + row * rowBytes) vs new (memcpy rs64LoadWord / rs64StoreWord).
// Build: clang++ -std=c++17 -O2 -fsanitize=alignment -fno-sanitize-recover=all tools/s7351_cast_ctl.cpp -o /tmp/c
// `/tmp/c` must print PASS (new == old byte-for-byte at every 4-aligned base, new clean at 2-aligned bases);
// `/tmp/c old` runs the old form at base offset 2 (odd 16b row): UBSan must abort (misaligned load).
#include <cstdint>
#include <cstdio>
#include <cstring>
static inline uint32_t bswap(uint32_t v) { return __builtin_bswap32(v); }
static inline uint32_t ld(const uint8_t* p) { uint32_t v; memcpy(&v, p, 4); return v; }
static inline void st(uint8_t* p, uint32_t v) { memcpy(p, &v, 4); }
__attribute__((noinline)) static void old_in(const uint8_t* src, uint32_t* dst, uint32_t n) {
    const uint32_t* s = reinterpret_cast<const uint32_t*>(src); while (n--) *dst++ = bswap(*s++); }
__attribute__((noinline)) static void new_in(const uint8_t* src, uint32_t* dst, uint32_t n) {
    while (n--) { *dst++ = bswap(ld(src)); src += 4; } }
__attribute__((noinline)) static void old_out(uint8_t* b, uint32_t n) {
    uint32_t* w = reinterpret_cast<uint32_t*>(b); while (n--) { *w = bswap(*w); w++; } }
__attribute__((noinline)) static void new_out(uint8_t* b, uint32_t n) {
    while (n--) { st(b, bswap(ld(b))); b += 4; } }
int main(int argc, char** argv) {
    alignas(16) static uint8_t ram[4096 + 64]; for (int i = 0; i < (int)sizeof ram; i++) ram[i] = (uint8_t)(i * 37 + 11);
    if (argc > 1 && !strcmp(argv[1], "old")) { uint32_t d[16]; old_in(ram + 2, d, 16); printf("old ran: %08X\n", d[0]); return 0; }
    int n = 0, bad = 0;
    for (uint32_t base = 0; base < 64; base += 4) for (uint32_t words = 1; words < 200; words += 7) {
        uint32_t a[256], b[256]; old_in(ram + base, a, words); new_in(ram + base, b, words); ++n; if (memcmp(a, b, words * 4)) ++bad;
        alignas(16) uint8_t x[1024 + 64], y[1024 + 64]; memcpy(x, ram, sizeof x); memcpy(y, ram, sizeof y);
        old_out(x + base, words); new_out(y + base, words); ++n; if (memcmp(x, y, sizeof x)) ++bad;
    }
    for (uint32_t base = 2; base < 64; base += 4) {   // the misaligned case the guest can choose: new form defined, swaps bytes
        uint32_t d[32]; new_in(ram + base, d, 32); ++n;
        for (int k = 0; k < 32; k++) { const uint8_t* p = ram + base + 4 * k; if (d[k] != ((uint32_t)p[0] << 24 | p[1] << 16 | p[2] << 8 | p[3])) { ++bad; break; } }
    }
    printf("[s7351] %d cases, %d mismatch (new vs old aligned, new vs byte model misaligned): %s\n", n, bad, bad ? "FAIL" : "PASS");
    return bad != 0;
}
