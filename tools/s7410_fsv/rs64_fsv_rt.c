/* s7410 runtime half of rs64_fsv.h. Entry snapshot of the FR=0 caller-visible callee-saved state: f20,f22,..,f30 .u64
 * (recomp model: the whole caller double + its odd single live in the even slot), s0-s7, s8, sp; plus the odd own slots
 * f21..f31 .u32l (FR=1-only storage, invisible to an FR=0 caller: informational). At every return: diff -> per-site
 * counters for even-pair diffs (fbad), GPR diffs (gbad), FR mode at return != FR at entry (mbad), odd own-slot changes (odd).
 * Positive control ROGUESQ_S7410_PLANT=1: every 64th return per site flips a bit of f24.u64 and of s1 AFTER the routine's own
 * restores, runs the same diff (must land in plant_bad), then undoes the flip. Diagnostic only. */
#include "rs64_fsv.h"
#include "recomp.h"
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define MAXS 64
static struct rs64_fsvsite* g_site[MAXS];
static _Atomic unsigned long long g_ret[MAXS], g_fbad[MAXS], g_gbad[MAXS], g_mbad[MAXS], g_odd[MAXS], g_pl[MAXS], g_plbad[MAXS], g_m1[MAXS];
static _Atomic unsigned g_fmask[MAXS], g_gmask[MAXS];
static _Atomic int g_nsite;
static pthread_mutex_t g_mu = PTHREAD_MUTEX_INITIALIZER;
static _Atomic long long g_last_ms;
static int g_plant = -1;
static long long now_ms(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec * 1000LL + ts.tv_nsec / 1000000; }
static void dump(const char* why) {
    int n = atomic_load(&g_nsite);
    fprintf(stderr, "[s7410-dump] %s t_ms=%lld sites=%d plant=%d\n", why, now_ms(), n, g_plant);
    for (int i = 0; i < n; i++) {
        struct rs64_fsvsite* s = g_site[i]; if (!s) continue;
        fprintf(stderr, "[s7410-site] fn=%s rets=%llu m1_entry=%llu fbad=%llu fmask=0x%x gbad=%llu gmask=0x%x mbad=%llu odd_changed=%llu plant=%llu plant_bad=%llu\n",
            s->fn, atomic_load(&g_ret[i]), atomic_load(&g_m1[i]), atomic_load(&g_fbad[i]), atomic_load(&g_fmask[i]),
            atomic_load(&g_gbad[i]), atomic_load(&g_gmask[i]), atomic_load(&g_mbad[i]), atomic_load(&g_odd[i]),
            atomic_load(&g_pl[i]), atomic_load(&g_plbad[i]));
    }
    fflush(stderr);
}
static void snap(struct rs64_fsvsnap* s, recomp_context* c) {
    fpr* fr[12] = { &c->f20, &c->f21, &c->f22, &c->f23, &c->f24, &c->f25, &c->f26, &c->f27, &c->f28, &c->f29, &c->f30, &c->f31 };
    for (int k = 0; k < 6; k++) { s->f[k] = fr[2 * k]->u64; s->odd[k] = fr[2 * k + 1]->u32l; }
    gpr* g[11] = { &c->r16, &c->r17, &c->r18, &c->r19, &c->r20, &c->r21, &c->r22, &c->r23, &c->r30, &c->r29, &c->r29 };
    for (int k = 0; k < 10; k++) s->r[k] = *g[k];
    s->mode = c->mips3_float_mode ? 1 : 0;
}
void rs64_fsv_enter(struct rs64_fsvsnap* s, void* vctx) { snap(s, (recomp_context*)vctx); }
static void diff(const struct rs64_fsvsnap* a, const struct rs64_fsvsnap* b, unsigned* fm, unsigned* gm, int* odd) {
    *fm = 0; *gm = 0; *odd = 0;
    for (int k = 0; k < 6; k++) { if (a->f[k] != b->f[k]) *fm |= 1u << k; if (a->odd[k] != b->odd[k]) *odd = 1; }
    for (int k = 0; k < 10; k++) if ((uint32_t)a->r[k] != (uint32_t)b->r[k]) *gm |= 1u << k;
}
void rs64_fsv_ret(struct rs64_fsvsite* site, struct rs64_fsvsnap* e, void* vctx) {
    recomp_context* c = (recomp_context*)vctx;
    int i = site->idx;
    if (__builtin_expect(i < 0, 0)) {
        pthread_mutex_lock(&g_mu);
        if (site->idx < 0) { int k = atomic_load(&g_nsite); if (k < MAXS) { g_site[k] = site; site->idx = k; atomic_store(&g_nsite, k + 1); } }
        if (g_plant < 0) { const char* ev = getenv("ROGUESQ_S7410_PLANT"); g_plant = ev && ev[0] == '1'; }
        pthread_mutex_unlock(&g_mu);
        i = site->idx; if (i < 0) return;
    }
    unsigned long long n = atomic_fetch_add(&g_ret[i], 1);
    if (e->mode) atomic_fetch_add(&g_m1[i], 1);
    struct rs64_fsvsnap r; snap(&r, c);
    unsigned fm, gm; int odd;
    diff(e, &r, &fm, &gm, &odd);
    if (fm) { atomic_fetch_add(&g_fbad[i], 1); atomic_fetch_or(&g_fmask[i], fm); }
    if (gm) { atomic_fetch_add(&g_gbad[i], 1); atomic_fetch_or(&g_gmask[i], gm); }
    if (r.mode != e->mode) atomic_fetch_add(&g_mbad[i], 1);
    if (odd) atomic_fetch_add(&g_odd[i], 1);
    if (g_plant == 1 && (n & 63) == 0) {
        c->f24.u64 ^= 0x0000000100000000ull; c->r17 ^= 0x10;
        struct rs64_fsvsnap p; snap(&p, c); unsigned pf, pg; int po;
        diff(e, &p, &pf, &pg, &po);
        c->f24.u64 ^= 0x0000000100000000ull; c->r17 ^= 0x10;
        atomic_fetch_add(&g_pl[i], 1);
        if ((pf & (1u << 2)) && (pg & 2u)) atomic_fetch_add(&g_plbad[i], 1);
    }
    long long t = now_ms(), l = atomic_load(&g_last_ms);
    if (t - l >= 10000 && atomic_compare_exchange_strong(&g_last_ms, &l, t)) dump(l ? "periodic" : "first");
}
