/* s7607 class UW second source, C half. Built by tools/s7607_uw_census.py --witness with the REAL RecompiledFuncs
   C_FLAGS/C_INCLUDES parsed from build/CMakeFiles/RecompiledFuncs.dir/flags.make (control arm adds
   -fno-asynchronous-unwind-tables -fno-unwind-tables). Shape copies a generated frame chain: thread entry -> mid frame
   with a stack-adjusting prologue and work after the call -> unregisterServiceWorker-style leaf -> the host
   osDestroyThread_recomp stub, which the C++ half makes throw ultramodern::thread_terminated. */
#include "recomp.h"
void s7607_destroy_recomp(uint8_t* rdram, recomp_context* ctx);           /* host stub (C++ half), throws */
volatile int s7607_after;                                                   /* code after the call: must NOT run */
__attribute__((noinline)) void s7607_leaf(uint8_t* rdram, recomp_context* ctx) {
    ctx->r29 = ADD32(ctx->r29, -0X20);
    MEM_W(0X18, ctx->r29) = ctx->r31;
    ctx->r4 = 0;                                                            /* osDestroyThread(NULL) = self */
    s7607_destroy_recomp(rdram, ctx);
    s7607_after += 1;
    ctx->r31 = MEM_W(0X18, ctx->r29);
    ctx->r29 = ADD32(ctx->r29, 0X20);
}
__attribute__((noinline)) void s7607_mid(uint8_t* rdram, recomp_context* ctx) {
    int32_t local[8]; for (int i = 0; i < 8; ++i) local[i] = (int32_t)ctx->r4 + i;
    ctx->r29 = ADD32(ctx->r29, -0X30);
    s7607_leaf(rdram, ctx);
    s7607_after += local[3];
    ctx->r29 = ADD32(ctx->r29, 0X30);
}
void s7607_entry(uint8_t* rdram, recomp_context* ctx) { s7607_mid(rdram, ctx); s7607_after += 100; }
