/* s7087 host test: the generated and/or/xor/nor/negu lowerings (statement text copied from the
 * front-end output, via recomp.h macros) vs an R4300 reference model, at -O2 with the live flags;
 * plus the FR-mode odd-FPR mapping on the real recomp_context layout (the two f_odd assignments are
 * copied from librecomp recomp.cpp cop0_status_write). -DNEG lowers nor as (S|T) and negu as
 * ADD32(0,T): must produce mismatches. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "recomp.h"
typedef uint64_t u64; typedef int64_t s64;
static u64 vals[] = {0, 1, 2, 0x7F, 0x80, 0x7FFF, 0x8000, 0xFFFF, 0x12345678, 0x7FFFFFFF,
    0xFFFFFFFF80000000ull, 0xFFFFFFFFFFFFFFFFull, 0xFFFFFFFF9ABCDEF0ull, 0xFFFFFFFFFFFF8000ull,
    0x00000000FFFFFFFFull /* not sign-extended */, 0x0123456789ABCDEFull, 0x8000000000000000ull};
#define NV (sizeof vals / sizeof vals[0])
static u64 se32(u64 x) { return (u64)(s64)(int32_t)(uint32_t)x; }
int main(void) {
    long rows = 0, bad = 0;
    recomp_context c; memset(&c, 0, sizeof c); recomp_context* ctx = &c;
    for (unsigned i = 0; i < NV; i++) for (unsigned j = 0; j < NV; j++) {
        u64 s = vals[i], t = vals[j];
        ctx->r8 = s; ctx->r9 = t;
        ctx->r10 = ctx->r8 & ctx->r9;           rows++; bad += ctx->r10 != (s & t);
        ctx->r10 = ctx->r8 | ctx->r9;           rows++; bad += ctx->r10 != (s | t);
        ctx->r10 = ctx->r8 ^ ctx->r9;           rows++; bad += ctx->r10 != (s ^ t);
#ifdef NEG
        ctx->r10 = (ctx->r8 | ctx->r9);
#else
        ctx->r10 = ~(ctx->r8 | ctx->r9);
#endif
        rows++; bad += ctx->r10 != ~(s | t);
        ctx->r10 = ~(0 | ctx->r9);              rows++; bad += ctx->r10 != ~t;
        ctx->r10 = ~(ctx->r8 | 0);              rows++; bad += ctx->r10 != ~s;
        /* sign-extended inputs keep sign-extended results */
        if (s == se32(s) && t == se32(t)) {
            rows++; bad += se32(~(s | t)) != (u64)~(s | t);
            rows++; bad += se32(s & t) != (s & t) || se32(s ^ t) != (s ^ t);
        }
    }
    for (unsigned j = 0; j < NV; j++) {          /* negu $rd, $rt: 32-bit subtract, sign-extended */
        u64 t = vals[j]; ctx->r9 = t;
#ifdef NEG
        ctx->r10 = ADD32(0, ctx->r9);
#else
        ctx->r10 = SUB32(0, ctx->r9);
#endif
        rows++; bad += ctx->r10 != se32((uint32_t)(0u - (uint32_t)t));
    }
    /* FR mapping: f_odd[(n-1)*2] must alias fpr[n-1].u32h when FR=0 and fpr[n].u32l when FR=1 */
    fpr* f = &ctx->f0;
    for (int fr = 0; fr < 2; fr++) {
        ctx->f_odd = fr ? &ctx->f1.u32l : &ctx->f0.u32h;
        for (int n = 1; n < 32; n += 2) {
            uint32_t* want = fr ? &f[n].u32l : &f[n - 1].u32h;
            rows++; bad += &ctx->f_odd[(n - 1) * 2] != want;
        }
    }
    /* osGetCount shim: Count >= 0x80000000 must reach $v0 sign-extended, as mfc0 does */
    { uint32_t cnt = 0x9ABCDEF0u; ctx->r2 = (int32_t)cnt; rows++; bad += ctx->r2 != 0xFFFFFFFF9ABCDEF0ull; }
    printf("rows %ld bad %ld\n", rows, bad);
    return 0;
}
