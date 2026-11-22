/* s7814: pass-through differential for the diagnostic recomp.h shadows (include/fbld = s7389, include/spwm = s7391).
 * Built three ways with the shipped force-include (rsp_dpc_macros.h) by tools/s7814_include_census.py:
 *   up   = upstream recomp.h only;  fbld = -Iinclude/fbld -DRS64_FB_LDWATCH;  spwm = -Iinclude/spwm -DRS64_SP_WATCH
 * Prints one hash over every wrapped macro's address/value on the same random inputs; the arms must print the same
 * hash, i.e. the diagnostic builds compute exactly what the shipped build computes (their findings transfer). */
#include "recomp.h"
#include <stdio.h>
#include <string.h>
#ifdef RS64_FB_LDWATCH
uint32_t rs64_fbpg[4096]; long g_hits;
void rs64_fbld_hit(uint32_t a, const char *f, int l, int w) { (void)a; (void)f; (void)l; (void)w; g_hits++; }
#endif
#ifdef RS64_SP_WATCH
__thread uint32_t rs64_spwm_min = 0xFFFFFFFFu, rs64_spwm_cnt;
void rs64_spwm_new(uint32_t sp, uint8_t *rd, uint32_t a0, const char *f, int l) { (void)sp; (void)rd; (void)a0; (void)f; (void)l; }
void rs64_spwm_tick(uint8_t *rd) { (void)rd; }
#endif
static uint64_t s = 0x243F6A8885A308D3ull;
static uint64_t rnd(void) { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
static uint64_t h = 1469598103934665603ull;
static void mix(uint64_t v) { h = (h ^ v) * 1099511628211ull; }
#define RDSZ (16u << 20)
int main(void) {
    static uint8_t buf[RDSZ + 64]; uint8_t *rdram = buf;
    recomp_context c; recomp_context *ctx = &c; memset(&c, 0, sizeof c);
    for (uint32_t i = 0; i < RDSZ; i++) buf[i] = (uint8_t)rnd();
#ifdef RS64_FB_LDWATCH
    for (int i = 0; i < 4096; i++) rs64_fbpg[i] = (uint32_t)((i * 2654435761u) >> 31);   /* half the pages marked, own
                                                         * sequence: the arms must draw identical rnd() streams */
#endif
    for (long n = 0; n < 2000000; n++) {
        gpr reg = (gpr)(int64_t)(int32_t)(0x80000000u + (uint32_t)(rnd() % (RDSZ - 0x100)) + 0x40);
        gpr off = (gpr)(int64_t)(int16_t)(rnd() & 0x3F);          /* in-buffer, mixed sign via the +0x40 base */
        off = (rnd() & 1) ? off : (gpr)(-(int64_t)off);
        mix((uint64_t)((uint8_t*)&MEM_W(off, reg) - rdram)); mix((uint64_t)MEM_W(off, reg));
        mix((uint64_t)((uint8_t*)&MEM_WU(off, reg) - rdram)); mix((uint64_t)MEM_WU(off, reg));
        mix((uint64_t)((uint8_t*)&MEM_H(off, reg) - rdram)); mix((uint64_t)(int64_t)MEM_H(off, reg));
        mix((uint64_t)((uint8_t*)&MEM_HU(off, reg) - rdram)); mix((uint64_t)MEM_HU(off, reg));
        mix((uint64_t)((uint8_t*)&MEM_B(off, reg) - rdram)); mix((uint64_t)(int64_t)MEM_B(off, reg));
        mix((uint64_t)((uint8_t*)&MEM_BU(off, reg) - rdram)); mix((uint64_t)MEM_BU(off, reg));
        mix((uint64_t)LD(off, reg));
        gpr iv = (gpr)rnd();
        mix((uint64_t)do_lwl(rdram, iv, off, reg)); mix((uint64_t)do_lwr(rdram, iv, off, reg));
        ctx->r29 = (gpr)rnd(); ctx->r4 = (gpr)rnd(); gpr k = (gpr)rnd();
        mix((uint64_t)ADD32(ctx->r29, k)); mix((uint64_t)ADD32(ctx->r4, k)); mix((uint64_t)ADD32(k, ctx->r29));
    }
    printf("hash=%016llx\n", (unsigned long long)h);
    return 0;
}
