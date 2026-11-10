// s7084: host semantic test of N64Recomp's FPU lowering macros (recomp.h), compiled with the
// live RecompiledFuncs flags (-O2, no -frounding-math). Prints one line per case:
//   op mode input -> result ; the Python driver compares against an exact MIPS reference.
// The value is produced BEFORE set_cop1_cs and converted AFTER it, the guPerspectiveF shape
// (s7084), so a compiler that hoisted the conversion above fesetround would fail the RZ/RP/RM rows.
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "recomp.h"

static volatile double g_in_d[] = {2.5, -2.5, 3.5, 0.5, -0.5, 1.7, -1.7, 43690.666666666664, 65535.5, -0.0, 1e-300};
static volatile float  g_in_s[] = {2.5f, -2.5f, 3.5f, 0.5f, -0.5f, 1.7f, -1.7f, 16777215.5f, 8388608.5f, -7.5f};
static volatile double g_narrow[] = {1.0 + 0x1p-30, -(1.0 + 0x1p-30), 1.0 + 0x1p-24 + 0x1p-40, 3.0e38 * 1.5};

__attribute__((noinline)) static void run(recomp_context* ctx, uint32_t mode) {
    unsigned n = sizeof(g_in_d) / sizeof(g_in_d[0]);
    for (unsigned i = 0; i < n; i++) {
        ctx->f4.d = g_in_d[i] * 1.0;           // computed before the mode switch
        uint32_t saved = get_cop1_cs();
        set_cop1_cs(mode);
        ctx->f6.u32l = CVT_W_D(ctx->f4.d);
        uint32_t seen = get_cop1_cs();
        set_cop1_cs(saved);
        printf("cvt.w.d %u %a %d cs=%u\n", mode, g_in_d[i], (int32_t)ctx->f6.u32l, seen);
    }
    n = sizeof(g_in_s) / sizeof(g_in_s[0]);
    for (unsigned i = 0; i < n; i++) {
        ctx->f8.fl = g_in_s[i] * 1.0f;
        uint32_t saved = get_cop1_cs();
        set_cop1_cs(mode);
        ctx->f10.u32l = CVT_W_S(ctx->f8.fl);
        ctx->f12.u32l = TRUNC_W_S(ctx->f8.fl);
        set_cop1_cs(saved);
        printf("cvt.w.s %u %a %d\n", mode, (double)g_in_s[i], (int32_t)ctx->f10.u32l);
        printf("trunc.w.s %u %a %d\n", mode, (double)g_in_s[i], (int32_t)ctx->f12.u32l);
    }
    n = sizeof(g_narrow) / sizeof(g_narrow[0]);
    for (unsigned i = 0; i < n; i++) {
        ctx->f14.d = g_narrow[i] * 1.0;
        uint32_t saved = get_cop1_cs();
        set_cop1_cs(mode);
        ctx->f16.fl = CVT_S_D(ctx->f14.d);
        set_cop1_cs(saved);
        printf("cvt.s.d %u %a %a\n", mode, g_narrow[i], (double)ctx->f16.fl);
    }
}

int main(void) {
    recomp_context ctx; memset(&ctx, 0, sizeof(ctx));
    for (uint32_t m = 0; m < 4; m++) run(&ctx, m);
    // ceil.w.d lowering (ceilDouble): S32(ceil(d)), mode-independent.
    double cd[] = {2.1, -2.1, 2.0, -0.5};
    for (unsigned i = 0; i < 4; i++) printf("ceil.w.d 0 %a %d\n", cd[i], (int32_t)S32(ceil(cd[i])));
    printf("final_cs %u\n", get_cop1_cs());
    return 0;
}
