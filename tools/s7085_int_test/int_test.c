// s7085: host semantic test of N64Recomp's integer lowering (the exact statements cgenerator.cpp
// emits, and the recomp.h macros), compiled with the live RecompiledFuncs flags (-O2). One line per
// case: "op a b [c] -> lo hi" (hex u64); run_test.py compares against an exact R4300 reference.
// guard_*: the GCC div guard shape (div; bne rt,$zero; break 7; li at,-1; bne; lui; bne; break 6)
// with a VARIABLE divisor, so -O2 cannot fold it; the stub records whether do_break was reached
// (clang may treat the earlier C division by zero as UB and delete the guard).
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "recomp.h"

static int g_break; static uint32_t g_break_at;
void do_break(uint32_t vram) { g_break++; g_break_at = vram; }
// diagnostic hooks recomp.h calls from do_swl/do_swr (live versions only log specific words)
void rs64_g1d_blk_unaligned(char k, uint32_t a, uint32_t b, uint32_t c) { (void)k; (void)a; (void)b; (void)c; }
void rs64_floor_writer_unaligned(char k, uint32_t a, uint32_t b, uint32_t c) { (void)k; (void)a; (void)b; (void)c; }

static volatile uint64_t V[] = {0, 1, 2, 3, 7, 45, 0x300, 0x7FFFFFFFull, 0xFFFFFFFF80000000ull,
    0xFFFFFFFFFFFFFFFFull, 0xFFFFFFFFFFFFFFFEull, 0x12345678ull, 0xFFFFFFFF87654321ull,
    0x0000000100000005ull, 0x8000000000000000ull, 0x7FFFFFFFFFFFFFFFull, 0x00000000DEADBEEFull};
#define NV (sizeof(V) / sizeof(V[0]))

__attribute__((noinline)) static void mul32(recomp_context* ctx) {
    uint64_t hi = 0, lo = 0, result = 0;
    for (unsigned i = 0; i < NV; i++) for (unsigned j = 0; j < NV; j++) {
        ctx->r4 = V[i]; ctx->r5 = V[j];
        result = S64(S32(ctx->r4)) * S64(S32(ctx->r5)); lo = S32(result >> 0); hi = S32(result >> 32);
        printf("mult %llx %llx %llx %llx\n", (unsigned long long)ctx->r4, (unsigned long long)ctx->r5, (unsigned long long)lo, (unsigned long long)hi);
        result = U64(U32(ctx->r4)) * U64(U32(ctx->r5)); lo = S32(result >> 0); hi = S32(result >> 32);
        printf("multu %llx %llx %llx %llx\n", (unsigned long long)ctx->r4, (unsigned long long)ctx->r5, (unsigned long long)lo, (unsigned long long)hi);
        if (ctx->r5 != 0 && !(S32(ctx->r5) == -1 && S32(ctx->r4) == INT32_MIN && 0)) {
            lo = S32(S64(S32(ctx->r4)) / S64(S32(ctx->r5))); hi = S32(S64(S32(ctx->r4)) % S64(S32(ctx->r5)));
            if (S32(ctx->r5) != 0)
                printf("div %llx %llx %llx %llx\n", (unsigned long long)ctx->r4, (unsigned long long)ctx->r5, (unsigned long long)lo, (unsigned long long)hi);
            if (U32(ctx->r5) != 0) {
                lo = S32(U32(ctx->r4) / U32(ctx->r5)); hi = S32(U32(ctx->r4) % U32(ctx->r5));
                printf("divu %llx %llx %llx %llx\n", (unsigned long long)ctx->r4, (unsigned long long)ctx->r5, (unsigned long long)lo, (unsigned long long)hi);
            }
        }
        { int64_t l, h; DMULT(S64(ctx->r4), S64(ctx->r5), &l, &h);
          printf("dmult %llx %llx %llx %llx\n", (unsigned long long)ctx->r4, (unsigned long long)ctx->r5, (unsigned long long)l, (unsigned long long)h); }
        { uint64_t l, h; DMULTU(U64(ctx->r4), U64(ctx->r5), &l, &h);
          printf("dmultu %llx %llx %llx %llx\n", (unsigned long long)ctx->r4, (unsigned long long)ctx->r5, (unsigned long long)l, (unsigned long long)h); }
        // ddivu / ddiv including divisor 0 (the two unguarded live ddivu sites, u64DivU64 and
        // divideByMixerBaseFrequency, have no break 7): the macro result is what the game sees.
        DDIVU(U64(ctx->r4), U64(ctx->r5), &lo, &hi);
        printf("ddivu %llx %llx %llx %llx\n", (unsigned long long)ctx->r4, (unsigned long long)ctx->r5, (unsigned long long)lo, (unsigned long long)hi);
        { int64_t q, r; DDIV(S64(ctx->r4), S64(ctx->r5), &q, &r);
          printf("ddiv %llx %llx %llx %llx\n", (unsigned long long)ctx->r4, (unsigned long long)ctx->r5, (unsigned long long)q, (unsigned long long)r); }
    }
}

__attribute__((noinline)) static void shifts(recomp_context* ctx) {
    for (unsigned i = 0; i < NV; i++) for (unsigned s = 0; s < 64; s++) {
        ctx->r4 = V[i]; ctx->r5 = s | 0xFFFFFFC0u;   // variable shifts must mask the amount
        uint64_t sll = s < 32 ? S32(ctx->r4 << s) : 0, srl = s < 32 ? S32(U32(ctx->r4) >> s) : 0,
                 sra = s < 32 ? S32(SIGNED(ctx->r4) >> s) : 0;
        uint64_t sllv = S32(ctx->r4 << (ctx->r5 & 31)), srlv = S32(U32(ctx->r4) >> (ctx->r5 & 31)),
                 srav = S32(SIGNED(ctx->r4) >> (ctx->r5 & 31));
        uint64_t dsll = ctx->r4 << s, dsrl = ctx->r4 >> s, dsra = SIGNED(ctx->r4) >> s;
        printf("shift %llx %u %llx %llx %llx %llx %llx %llx %llx %llx %llx\n", (unsigned long long)ctx->r4, s,
               (unsigned long long)sll, (unsigned long long)srl, (unsigned long long)sra, (unsigned long long)sllv,
               (unsigned long long)srlv, (unsigned long long)srav, (unsigned long long)dsll, (unsigned long long)dsrl,
               (unsigned long long)dsra);
    }
    static const int16_t imm[] = {0, 1, 0x7FFF, -1, -0x8000, 0x300};
    for (unsigned i = 0; i < NV; i++) for (unsigned k = 0; k < 6; k++) {
        ctx->r4 = V[i];
        // generator emits the sign-extended 64-bit immediate for sltiu/slti
        uint64_t u = ctx->r4 < (uint64_t)(int64_t)imm[k] ? 1 : 0, sg = SIGNED(ctx->r4) < (int64_t)imm[k] ? 1 : 0;
        uint64_t a = ADD32(ctx->r4, (int64_t)imm[k]), sb = SUB32(ctx->r4, V[(i + k) % NV]);
        printf("imm %llx %d %llu %llu %llx %llx %llx\n", (unsigned long long)ctx->r4, imm[k], (unsigned long long)u,
               (unsigned long long)sg, (unsigned long long)a, (unsigned long long)V[(i + k) % NV], (unsigned long long)sb);
    }
}

// unaligned pairs: lwl at addr, lwr at addr+3 (big-endian guest), at every misalignment
__attribute__((noinline)) static void unaligned(uint8_t* rdram, recomp_context* ctx) {
    for (unsigned off = 0; off < 4; off++) for (unsigned init = 0; init < 2; init++) {
        for (unsigned b = 0; b < 16; b++) rdram[b ^ 3] = (uint8_t)(0x80 + b * 0x11);   // guest bytes 80 91 a2 ...
        ctx->r6 = 0xFFFFFFFF80000000ull + off;  // base
        ctx->r2 = init ? 0x0123456789ABCDEFull : 0;
        ctx->r2 = do_lwl(rdram, ctx->r2, ctx->r6, 0X0);
        uint64_t mid = ctx->r2;
        ctx->r2 = do_lwr(rdram, ctx->r2, ctx->r6, 0X3);
        // single lwl / lwr alone (partial merge) from a known register value
        ctx->r3 = 0x0123456789ABCDEFull; ctx->r3 = do_lwl(rdram, ctx->r3, ctx->r6, 0X0);
        ctx->r7 = 0x0123456789ABCDEFull; ctx->r7 = do_lwr(rdram, ctx->r7, ctx->r6, 0X0);
        printf("lw %u %u %llx %llx %llx %llx\n", off, init, (unsigned long long)mid, (unsigned long long)ctx->r2,
               (unsigned long long)ctx->r3, (unsigned long long)ctx->r7);
        // swl/swr pair storing 0xCAFEBABE at addr, then single swl and single swr
        for (unsigned b = 0; b < 16; b++) rdram[b ^ 3] = 0;
        ctx->r8 = 0xFFFFFFFFCAFEBABEull;
        do_swl(rdram, 0X0, ctx->r6, ctx->r8); do_swr(rdram, 0X3, ctx->r6, ctx->r8);
        printf("sw %u pair", off); for (unsigned b = 0; b < 8; b++) printf(" %02x", rdram[b ^ 3]); printf("\n");
        for (unsigned b = 0; b < 16; b++) rdram[b ^ 3] = 0x55;
        do_swl(rdram, 0X0, ctx->r6, ctx->r8);
        printf("sw %u swl", off); for (unsigned b = 0; b < 8; b++) printf(" %02x", rdram[b ^ 3]); printf("\n");
        for (unsigned b = 0; b < 16; b++) rdram[b ^ 3] = 0x55;
        do_swr(rdram, 0X0, ctx->r6, ctx->r8);
        printf("sw %u swr", off); for (unsigned b = 0; b < 8; b++) printf(" %02x", rdram[b ^ 3]); printf("\n");
    }
}

// the exact generated guard shape (0x800464F4), divisor loaded through ctx so it stays variable
__attribute__((noinline)) static void guard_div(uint8_t* rdram, recomp_context* ctx) {
    uint64_t hi = 0, lo = 0;
    lo = S32(S64(S32(ctx->r2)) / S64(S32(ctx->r3))); hi = S32(S64(S32(ctx->r2)) % S64(S32(ctx->r3)));
    if (ctx->r3 != 0) { goto L_1; }
    do_break(0x80046500);
L_1:
    ctx->r1 = ADD32(0, -0X1);
    if (ctx->r3 != ctx->r1) { ctx->r1 = S32(0X8000 << 16); goto L_2; }
    ctx->r1 = S32(0X8000 << 16);
    if (ctx->r2 != ctx->r1) { goto L_2; }
    do_break(0x80046518);
L_2:
    ctx->r3 = hi; ctx->r4 = lo;
}
__attribute__((noinline)) static void guard_divu(uint8_t* rdram, recomp_context* ctx) {
    uint64_t hi = 0, lo = 0;
    lo = S32(U32(ctx->r2) / U32(ctx->r3)); hi = S32(U32(ctx->r2) % U32(ctx->r3));
    if (ctx->r3 != 0) { goto L_1; }
    do_break(0x80046600);
L_1:
    ctx->r3 = hi; ctx->r4 = lo;
}

int main(int argc, char** argv) {
    static uint8_t mem[64];
    recomp_context ctx; memset(&ctx, 0, sizeof ctx);
    mul32(&ctx); shifts(&ctx);
    uint8_t* rdram = mem;   // MEM_W subtracts 0xFFFFFFFF80000000, so guest 0x80000000 = mem[0]
    unaligned(rdram, &ctx);
    static volatile uint64_t gd[][2] = {{100, 7}, {(uint64_t)-100, 7}, {5, 0}, {(uint64_t)-5, 0},
        {0xFFFFFFFF80000000ull, 0xFFFFFFFFFFFFFFFFull}};
    for (unsigned i = 0; i < 5; i++) {
        g_break = 0; g_break_at = 0; ctx.r2 = gd[i][0]; ctx.r3 = gd[i][1]; guard_div(rdram, &ctx);
        printf("guard_div %llx %llx breaks=%d at=%x\n", (unsigned long long)gd[i][0], (unsigned long long)gd[i][1], g_break, g_break_at);
        g_break = 0; g_break_at = 0; ctx.r2 = gd[i][0]; ctx.r3 = gd[i][1]; guard_divu(rdram, &ctx);
        printf("guard_divu %llx %llx breaks=%d at=%x\n", (unsigned long long)gd[i][0], (unsigned long long)gd[i][1], g_break, g_break_at);
    }
    return 0;
}
