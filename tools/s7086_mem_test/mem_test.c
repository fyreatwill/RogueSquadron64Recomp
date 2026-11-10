// s7086: host test of N64Recomp's memory-access macros (recomp.h MEM_B/BU/H/HU/W, LD/SD, and our
// include/rsp_dpc_macros.h MEM_WU) against a big-endian byte model of RDRAM, at -O2 with the live flags.
// rdram is stored word-swapped (each aligned 32-bit word native little-endian), as librecomp loads it.
// Every naturally aligned address in a 64-byte window, every width, loads and stores, each base/offset
// split (positive, negative, odd base + odd offset). lwu must zero-extend, lw/lh/lb sign-extend into 64 bits.
// -DNEG swaps the byte swizzle to ^2 (a wrong lowering): the test must then report mismatches.
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "recomp.h"
#include "rsp_dpc_macros.h"
#ifdef NEG
#undef MEM_BU
#define MEM_BU(offset, reg) (*(uint8_t*)(rdram + ((((reg) + (offset)) ^ 2) - 0xFFFFFFFF80000000)))
#endif
#define N 64
static uint8_t be[N];            // big-endian reference
static uint8_t store[N] __attribute__((aligned(8)));
static uint8_t* rdram;            // rdram[phys] = word-swapped
static void sync_from_be(void) { for (int i = 0; i < N; i++) store[i ^ 3] = be[i]; }
static int cmp_be(void) { int m = 0; for (int i = 0; i < N; i++) m += store[i ^ 3] != be[i]; return m; }
static uint64_t rbe(int a, int w) { uint64_t v = 0; for (int i = 0; i < w; i++) v = (v << 8) | be[a + i]; return v; }
static void wbe(int a, int w, uint64_t v) { for (int i = w - 1; i >= 0; i--) { be[a + i] = v & 0xFF; v >>= 8; } }
static int64_t sx(uint64_t v, int w) { int s = 64 - 8 * w; return w == 8 ? (int64_t)v : (int64_t)(v << s) >> s; }
static volatile int32_t OFFS[] = {0, 3, -1, 0x7, -0x17, 5};

int main(void) {
    recomp_context c, *ctx = &c; memset(&c, 0, sizeof c);
    rdram = store - 0x100;           // window at physical 0x100 so base-offset never wraps below KSEG0
    unsigned rows = 0, bad = 0;
    uint32_t seed = 12345;
    for (int pass = 0; pass < 8; pass++) {
        for (int i = 0; i < N; i++) { seed = seed * 1103515245u + 12345u; be[i] = seed >> 16; }
        sync_from_be();
        for (int w = 1; w <= 8; w *= 2) for (int a = 0; a + w <= N; a += w) for (unsigned o = 0; o < 6; o++) {
            int32_t off = OFFS[o];
            ctx->r4 = (gpr)(int32_t)(0x80000100u + a - off);   // sign-extended KSEG0 base
            uint64_t ref = rbe(a, w), got = 0, got2 = 0; int64_t want = sx(ref, w), want2 = 0;
            switch (w) {
            case 1: got = MEM_B(ctx->r4, off); got2 = MEM_BU(ctx->r4, off); want2 = ref; break;
            case 2: got = MEM_H(ctx->r4, off); got2 = MEM_HU(ctx->r4, off); want2 = ref; break;
            case 4: got = MEM_W(ctx->r4, off); got2 = MEM_WU(ctx->r4, off); want2 = ref; break;
            case 8: got = LD(ctx->r4, off); got2 = got; want2 = want; break;
            }
            rows++; if ((int64_t)(gpr)(int64_t)got != want || got2 != (uint64_t)want2) {
                if (bad < 8) printf("LOAD w%d a%d off%d got %llx/%llx want %llx/%llx\n", w, a, off,
                    (unsigned long long)got, (unsigned long long)got2, (unsigned long long)want, (unsigned long long)want2);
                bad++;
            }
            // store a fresh value and compare the whole window against the big-endian model
            seed = seed * 1103515245u + 12345u;
            ctx->r5 = ((uint64_t)seed << 32) | (seed * 2654435761u);
            switch (w) {
            case 1: MEM_B(off, ctx->r4) = ctx->r5; break;
            case 2: MEM_H(off, ctx->r4) = ctx->r5; break;
            case 4: MEM_W(off, ctx->r4) = ctx->r5; break;
            case 8: SD(ctx->r5, off, ctx->r4); break;
            }
            wbe(a, w, ctx->r5);
            rows++; int m = cmp_be(); if (m) { if (bad < 8) printf("STORE w%d a%d off%d %d bytes differ\n", w, a, off, m); bad++; sync_from_be(); }
        }
    }
    // register-file view: lw of a word 0x80000000 must be 0xFFFFFFFF80000000 in the 64-bit register, lwu 0x80000000
    memset(be, 0, N); be[0] = 0x80; sync_from_be();
    ctx->r4 = (gpr)(int32_t)0x80000100u;
    ctx->r2 = MEM_W(ctx->r4, 0); ctx->r3 = MEM_WU(ctx->r4, 0);
    rows += 2; bad += ctx->r2 != 0xFFFFFFFF80000000ull; bad += ctx->r3 != 0x80000000ull;
    printf("rows %u bad %u\n", rows, bad);
    return bad ? 1 : 0;
}
