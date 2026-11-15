/* s7391 guest stack low-water watch (build_spwm only: cmake -DROGUESQ_SP_WATCH=ON puts this dir BEFORE the upstream
 * include path for RecompiledFuncs). Every generated `ctx->r29 = ADD32(ctx->r29, ...)` (the MIPS frame push/pop; one
 * generated line = one instruction) is routed through rs64_spwm_add, which keeps a per-host-thread (= per guest thread,
 * ultramodern gives each OSThread its own host thread) minimum $sp and reports each new low-water mark with the
 * generated __FILE__/__LINE__ that made it. The r29 test is a compile-time fold on the stringized first argument, so
 * every other ADD32 compiles exactly as upstream. s7391 line B: every 2^18 adjusts the thread rescans its own stack
 * (service workers only, exact bounds from the registerServiceWorker descriptor in a0 at entry) for the lowest word
 * that changed since the snapshot taken at entry, an independent check of the $sp minimum. Host half: src/main/s7391_spwm.cpp. Diagnostic. */
#include_next "recomp.h"
#ifdef RS64_SP_WATCH
#ifndef RS64_SPWM_OVERRIDE
#define RS64_SPWM_OVERRIDE
#ifdef __cplusplus
extern "C" {
#endif
extern __thread uint32_t rs64_spwm_min, rs64_spwm_cnt;
void rs64_spwm_new(uint32_t sp, uint8_t *rdram, uint32_t a0, const char *file, int line);
void rs64_spwm_tick(uint8_t *rdram);
#ifdef __cplusplus
}
#endif
static inline gpr rs64_spwm_add(gpr r, uint8_t *rd, uint32_t a0, const char *f, int l) {
    uint32_t s = (uint32_t)r;
    if (s < rs64_spwm_min && s >= 0x80000000u) rs64_spwm_new(s, rd, a0, f, l);
    if (((++rs64_spwm_cnt) & 0x3FFFFu) == 0) rs64_spwm_tick(rd);
    return r;
}
#define RS64_SPWM_IS_R29(s) (sizeof(s) == 9 && (s)[0] == 'c' && (s)[5] == 'r' && (s)[6] == '2' && (s)[7] == '9')
#undef ADD32
#define ADD32(a, b) \
    (RS64_SPWM_IS_R29(#a) ? rs64_spwm_add((gpr)(int32_t)((a) + (b)), rdram, (uint32_t)ctx->r4, __FILE__, __LINE__) \
                          : ((gpr)(int32_t)((a) + (b))))
#endif
#endif
