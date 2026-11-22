// s7812: host semantic test of recomp.h's guest-memory layer (MEM_B/BU/H/HU/W loads+stores, LD, SD,
// do_lwl/lwr/swl/swr and the 64-bit do_ldl/ldr/sdl/sdr) and the FCSR rounding round trip
// (get_cop1_cs/set_cop1_cs), compiled with the live RecompiledFuncs flags (-O2) and the live recomp.h.
// Reference: an independent big-endian byte array gb[] (guest byte at guest address A = gb[A]) with the
// R4300 load/store rules written per byte. The system under test runs on rdram[] (host word-native
// layout). After every op the loaded value is compared, and after every store the whole guest view of
// rdram (read back through MEM_BU) is compared with gb[]. Layout cross-check: rdram[a ^ 3] == gb[a] (the
// convention RT64 / PI DMA use) is tested separately so a self-consistent but wrong swizzle still fails.
// Build mutants with -DMUT_H (MEM_H/HU swizzle ^0), -DMUT_SD (SD word order swapped), -DMUT_LDR (ldr
// shift off by one byte); each must report mismatches > 0.
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <fenv.h>
#include <stdlib.h>
#include "recomp.h"

void do_break(uint32_t vram) { (void)vram; }
void rs64_g1d_blk_unaligned(char k, uint32_t a, uint32_t b, uint32_t c) { (void)k; (void)a; (void)b; (void)c; }
void rs64_floor_writer_unaligned(char k, uint32_t a, uint32_t b, uint32_t c) { (void)k; (void)a; (void)b; (void)c; }

#ifdef MUT_H
#undef MEM_H
#undef MEM_HU
#define MEM_H(offset, reg) (*(int16_t*)(rdram + ((((reg) + (offset)) ^ 0) - 0xFFFFFFFF80000000)))
#define MEM_HU(offset, reg) (*(uint16_t*)(rdram + ((((reg) + (offset)) ^ 0) - 0xFFFFFFFF80000000)))
#endif
#ifdef MUT_SD
#undef SD
#define SD(val, offset, reg) { \
    *(uint32_t*)(rdram + ((((reg) + (offset) + 0)) - 0xFFFFFFFF80000000)) = (uint32_t)((gpr)(val) >> 0); \
    *(uint32_t*)(rdram + ((((reg) + (offset) + 4)) - 0xFFFFFFFF80000000)) = (uint32_t)((gpr)(val) >> 32); }
#endif

#define NB 512
static uint8_t rdram[NB + 64] __attribute__((aligned(16)));
static uint8_t gb[NB];
static const gpr BASE = 0xFFFFFFFF80000000ull;  // guest 0x80000000, sign-extended as every generated base is

static uint64_t rs = 0x9E3779B97F4A7C15ull;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }

static uint64_t sext32(uint64_t v) { return (uint64_t)(int64_t)(int32_t)(uint32_t)v; }
static uint64_t ref_load(unsigned a, unsigned n) { uint64_t v = 0; for (unsigned i = 0; i < n; i++) v = (v << 8) | gb[a + i]; return v; }
static void ref_store(unsigned a, unsigned n, uint64_t v) { for (unsigned i = 0; i < n; i++) gb[a + i] = (uint8_t)(v >> (8 * (n - 1 - i))); }
// R4300 big-endian unaligned rules, byte by byte (W = 4 or 8).
static uint64_t ref_lxl(unsigned a, unsigned W, uint64_t reg) {  // bytes a..end-of-unit -> register MSB downwards
    unsigned k = a & (W - 1); uint64_t r = reg;
    for (unsigned i = 0; i < W - k; i++) { unsigned sh = 8 * (W - 1 - i); r = (r & ~(0xFFull << sh)) | ((uint64_t)gb[a + i] << sh); }
    return W == 4 ? sext32(r) : r;
}
static uint64_t ref_lxr(unsigned a, unsigned W, uint64_t reg) {  // bytes start-of-unit..a -> register LSB upwards
    unsigned k = a & (W - 1); uint64_t r = reg;
    for (unsigned i = 0; i <= k; i++) { unsigned sh = 8 * i; r = (r & ~(0xFFull << sh)) | ((uint64_t)gb[a - i] << sh); }
    return W == 4 ? sext32(r) : r;
}
static void ref_sxl(unsigned a, unsigned W, uint64_t v) { unsigned k = a & (W - 1); for (unsigned i = 0; i < W - k; i++) gb[a + i] = (uint8_t)(v >> (8 * (W - 1 - i))); }
static void ref_sxr(unsigned a, unsigned W, uint64_t v) { unsigned k = a & (W - 1); for (unsigned i = 0; i <= k; i++) gb[a - i] = (uint8_t)(v >> (8 * i)); }

static long n_ops[32], n_bad[32], n_membad, n_layoutbad;
static const char* opname[32] = {"lb","lbu","lh","lhu","lw","ld","sb","sh","sw","sd","lwl","lwr","swl","swr","ldl","ldr","sdl","sdr","negoff","cop1cs"};

static void check_mem(void) {
    for (unsigned a = 0; a < NB; a++) {
        uint8_t v = MEM_BU((int64_t)a, BASE);
        if (v != gb[a]) { n_membad++; return; }
        if (rdram[a ^ 3] != gb[a]) { n_layoutbad++; return; }
    }
}

#ifdef MUT_LDR
static inline gpr sut_ldr(uint8_t* rd, gpr init, gpr off, gpr reg) {
    gpr address = off + reg, dw = address & ~0x7, m = address & 0x7;
    uint64_t lv = load_doubleword(rd, 0, dw);
    gpr mv = init & ~(0xFFFFFFFFFFFFFFFFu >> (56 - m * 8));
    lv >>= (m == 7 ? 0 : 48 - m * 8);
    return mv | lv;
}
#else
#define sut_ldr do_ldr
#endif

int main(int argc, char** argv) {
    long trials = argc > 1 ? atol(argv[1]) : 200000;
    for (unsigned a = 0; a < NB; a++) gb[a] = (uint8_t)rnd();
    for (unsigned a = 0; a < NB; a++) rdram[a ^ 3] = gb[a];  // seed through the documented layout
    check_mem();
    for (long t = 0; t < trials; t++) {
        unsigned op = (unsigned)(rnd() % 19);
        uint64_t v = rnd(), reg = rnd(); if (rnd() & 1) reg = sext32(reg);
        unsigned a = (unsigned)(rnd() % (NB - 16)) + 8;
        uint64_t got = 0, exp = 0; int cmp = 1, low32 = 0;
        gpr off = (gpr)(int64_t)a;
        switch (op) {
        case 0: got = (gpr)MEM_B(off, BASE); exp = (uint64_t)(int64_t)(int8_t)gb[a]; break;
        case 1: got = (gpr)MEM_BU(off, BASE); exp = gb[a]; break;
        case 2: a &= ~1u; off = a; got = (gpr)MEM_H(off, BASE); exp = (uint64_t)(int64_t)(int16_t)ref_load(a, 2); break;
        case 3: a &= ~1u; off = a; got = (gpr)MEM_HU(off, BASE); exp = ref_load(a, 2); break;
        case 4: a &= ~3u; off = a; got = (gpr)MEM_W(off, BASE); exp = sext32(ref_load(a, 4)); break;
        case 5: a &= ~7u; off = a; got = LD(off, BASE); exp = ref_load(a, 8); break;
        case 6: MEM_B(off, BASE) = (int8_t)v; ref_store(a, 1, v); cmp = 0; break;
        case 7: a &= ~1u; off = a; MEM_H(off, BASE) = (int16_t)v; ref_store(a, 2, v); cmp = 0; break;
        case 8: a &= ~3u; off = a; MEM_W(off, BASE) = (int32_t)v; ref_store(a, 4, v); cmp = 0; break;
        case 9: a &= ~7u; off = a; SD(v, off, BASE); ref_store(a, 8, v); cmp = 0; break;
        case 10: got = do_lwl(rdram, reg, off, BASE); exp = ref_lxl(a, 4, reg); break;
        case 11: got = do_lwr(rdram, reg, off, BASE); exp = ref_lxr(a, 4, reg); low32 = (a & 3) != 3; break;
        case 12: do_swl(rdram, off, BASE, v); ref_sxl(a, 4, v); cmp = 0; break;
        case 13: do_swr(rdram, off, BASE, v); ref_sxr(a, 4, v); cmp = 0; break;
        case 14: got = do_ldl(rdram, reg, off, BASE); exp = ref_lxl(a, 8, reg); break;
        case 15: got = sut_ldr(rdram, reg, off, BASE); exp = ref_lxr(a, 8, reg); break;
        case 16: do_sdl(rdram, off, BASE, v); ref_sxl(a, 8, v); cmp = 0; break;
        case 17: do_sdr(rdram, off, BASE, v); ref_sxr(a, 8, v); cmp = 0; break;
        case 18: {  // negative immediate offset from a raised base (the generated `lw rt, -0x10(base)` shape)
            unsigned d = 1 + (unsigned)(rnd() % 8); a &= ~3u; gpr base = BASE + a + 4 * d; gpr noff = (gpr)(int64_t)(-(int64_t)(4 * d));
            got = (gpr)MEM_W(noff, base); exp = sext32(ref_load(a, 4)); break; }
        }
        n_ops[op]++;
        if (cmp) { uint64_t g = low32 ? (got & 0xFFFFFFFFull) : got, e = low32 ? (exp & 0xFFFFFFFFull) : exp; if (g != e) n_bad[op]++; }
        else check_mem();
    }
    // FCSR rounding round trip + effect: set mode m, read it back, convert +-2.5 / +-1.5 through do_cvt_w_d.
    static const int32_t want[4][4] = {{2, -2, 2, -2}, {2, -2, 1, -1}, {3, -2, 2, -1}, {2, -3, 1, -2}};
    static volatile double in[4] = {2.5, -2.5, 1.5, -1.5};
    for (unsigned m = 0; m < 4; m++) {
        set_cop1_cs(m | 0x01000000u);  // FS bit set too: only RM may come back
        n_ops[19]++; if (get_cop1_cs() != m) n_bad[19]++;
        for (unsigned i = 0; i < 4; i++) { n_ops[19]++; if (do_cvt_w_d(in[i]) != want[m][i] || do_cvt_w_s((float)in[i]) != want[m][i]) n_bad[19]++; }
    }
    set_cop1_cs(0);
    long tot = 0;
    for (unsigned i = 0; i < 20; i++) { printf("op %-6s n=%ld bad=%ld\n", opname[i], n_ops[i], n_bad[i]); tot += n_bad[i]; }
    printf("memview_bad %ld layout_bad %ld\n", n_membad, n_layoutbad);
    printf("TOTAL_BAD %ld\n", tot + n_membad + n_layoutbad);
    return 0;
}
