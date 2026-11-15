/* s7409 runtime half of rs64_frp.h. Per probe site: calls, entries with mips3_float_mode 0/1, mode != expected, and a
 * real write-through test of the odd view: write a sentinel via ctx->f_odd[(21-1)*2] and see which physical slot moved
 * (f21.u32l = FR=1 own view, f20.u32h = FR=0 pair view), then restore both. view_bad = slot inconsistent with mode.
 * Positive control ROGUESQ_S7409_PLANT=1: every 64th call per site repeats the test with f_odd swapped to the other
 * mode's base pointer (restored after); each such plant must land in view_bad_plant. Diagnostic only.
 * Bisect gates (s7409): ROGUESQ_S7409_OFF=1 returns before any work; ROGUESQ_S7409_VIEW=0 skips view test + plant. */
#include "rs64_frp.h"
#include "recomp.h"
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define MAXS 256
static struct rs64_frsite* g_site[MAXS];
static _Atomic unsigned long long g_calls[MAXS], g_m0[MAXS], g_m1[MAXS], g_bad[MAXS], g_vbad[MAXS], g_pl[MAXS], g_plbad[MAXS];
static _Atomic int g_nsite;
static pthread_mutex_t g_mu = PTHREAD_MUTEX_INITIALIZER;
static _Atomic long long g_last_ms;
static int g_plant = -1, g_off = -1, g_view = -1;
static long long now_ms(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec * 1000LL + ts.tv_nsec / 1000000; }
static void dump(const char* why) {
    int n = atomic_load(&g_nsite);
    fprintf(stderr, "[s7409-dump] %s t_ms=%lld sites=%d plant=%d\n", why, now_ms(), n, g_plant);
    for (int i = 0; i < n; i++) {
        struct rs64_frsite* s = g_site[i]; if (!s) continue;
        fprintf(stderr, "[s7409-site] fn=%s where=%s expect=%d calls=%llu m0=%llu m1=%llu bad=%llu view_bad=%llu plant=%llu plant_bad=%llu\n",
            s->fn, s->where, s->expect, atomic_load(&g_calls[i]), atomic_load(&g_m0[i]), atomic_load(&g_m1[i]),
            atomic_load(&g_bad[i]), atomic_load(&g_vbad[i]), atomic_load(&g_pl[i]), atomic_load(&g_plbad[i]));
    }
    fflush(stderr);
}
/* returns 1 if the slot the odd view wrote is inconsistent with mode m */
static int view_test(recomp_context* c, int m) {
    uint32_t own = c->f21.u32l, pair = c->f20.u32h, s = 0xA5C3E1F7u;
    if (own == s || pair == s) s ^= 0x0F0F0F0Fu;
    c->f_odd[(21 - 1) * 2] = s;
    int hit_own = c->f21.u32l == s, hit_pair = c->f20.u32h == s;
    c->f21.u32l = own; c->f20.u32h = pair;
    return m ? !(hit_own && !hit_pair) : !(hit_pair && !hit_own);
}
void rs64_frp_note(struct rs64_frsite* s, void* vctx) {
    recomp_context* c = (recomp_context*)vctx;
    if (__builtin_expect(g_off < 0, 0)) { const char* e = getenv("ROGUESQ_S7409_OFF"); g_off = e && e[0] == '1';
        e = getenv("ROGUESQ_S7409_VIEW"); g_view = !(e && e[0] == '0'); }
    if (g_off) return;
    int i = s->idx;
    if (__builtin_expect(i < 0, 0)) {
        pthread_mutex_lock(&g_mu);
        if (s->idx < 0) { int k = atomic_load(&g_nsite); if (k < MAXS) { g_site[k] = s; s->idx = k; atomic_store(&g_nsite, k + 1); } }
        if (g_plant < 0) { const char* e = getenv("ROGUESQ_S7409_PLANT"); g_plant = e && e[0] == '1'; }
        pthread_mutex_unlock(&g_mu);
        i = s->idx; if (i < 0) return;
    }
    unsigned long long n = atomic_fetch_add(&g_calls[i], 1);
    int m = c->mips3_float_mode ? 1 : 0;
    atomic_fetch_add(m ? &g_m1[i] : &g_m0[i], 1);
    if (s->expect >= 0 && m != s->expect) atomic_fetch_add(&g_bad[i], 1);
    if (g_view && view_test(c, m)) atomic_fetch_add(&g_vbad[i], 1);
    if (g_view && g_plant == 1 && (n & 63) == 0) {
        uint32_t* keep = c->f_odd;
        c->f_odd = m ? &c->f0.u32h : &c->f1.u32l;
        atomic_fetch_add(&g_pl[i], 1);
        if (view_test(c, m)) atomic_fetch_add(&g_plbad[i], 1);
        c->f_odd = keep;
    }
    long long t = now_ms(), l = atomic_load(&g_last_ms);
    if (t - l >= 10000 && atomic_compare_exchange_strong(&g_last_ms, &l, t)) dump(l ? "periodic" : "first");
}
