/* s7408 runtime half of rs64_cvt.h. Diagnostic only. kind: 0 TRUNC_W_S 1 TRUNC_W_D 2 CVT_W_S 3 CVT_W_D.
 * Model (VR4300): TRUNC -> trunc(x); CVT -> nearbyint(x) under the current host rounding (= guest FCSR.RM via
 * set_cop1_cs). NaN/inf/rounded outside int32 -> UNIMPL (retail faults). Positive control ROGUESQ_S7408_PLANT=1:
 * every 4096th call per site also classifies x*1e10+3e9 (always UNIMPL) into plant counters. */
#include "rs64_cvt.h"
#include <fenv.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define MAXS 2048
static struct rs64_cvsite* g_site[MAXS];
static _Atomic unsigned long long g_calls[MAXS], g_oor[MAXS], g_mism[MAXS], g_rmz[MAXS], g_pl[MAXS], g_ploor[MAXS];
static _Atomic unsigned long long g_maxbits[MAXS];
static _Atomic int g_nsite;
static _Atomic unsigned long long g_tot;
static pthread_mutex_t g_mu = PTHREAD_MUTEX_INITIALIZER;
static double g_last;
static int g_plant = -1;
static const char* KN[4] = {"TRUNC_W_S", "TRUNC_W_D", "CVT_W_S", "CVT_W_D"};
static double now_s(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + ts.tv_nsec * 1e-9; }
static void dump(const char* why) {
    int n = atomic_load(&g_nsite);
    unsigned long long po = 0, pl = 0, oor = 0, mm = 0;
    for (int i = 0; i < n; i++) { po += g_ploor[i]; pl += g_pl[i]; oor += g_oor[i]; mm += g_mism[i]; }
    fprintf(stderr, "[s7408-dump] %s t=%.1f sites=%d tot=%llu oor=%llu mism=%llu plant=%llu plant_oor=%llu\n", why, now_s(), n,
        atomic_load(&g_tot), oor, mm, pl, po);
    for (int i = 0; i < n; i++) {
        struct rs64_cvsite* s = g_site[i]; if (!s) continue;
        union { unsigned long long u; double d; } m = { atomic_load(&g_maxbits[i]) };
        fprintf(stderr, "[s7408-site] pc=%08x fn=%s kind=%s calls=%llu max=%.6g oor=%llu mism=%llu rmz=%llu plant=%llu/%llu\n",
            s->pc, s->fn, KN[s->kind & 3], atomic_load(&g_calls[i]), m.d, atomic_load(&g_oor[i]), atomic_load(&g_mism[i]),
            atomic_load(&g_rmz[i]), atomic_load(&g_ploor[i]), atomic_load(&g_pl[i]));
    }
    fflush(stderr);
}
static int unimpl(double x, int cvt, double* rv) {
    *rv = cvt ? nearbyint(x) : trunc(x);
    return (x != x) || isinf(x) || *rv < -2147483648.0 || *rv > 2147483647.0;
}
void rs64_cvt_note(struct rs64_cvsite* s, double x, int32_t host) {
    int i = s->idx;
    if (__builtin_expect(i < 0, 0)) {
        pthread_mutex_lock(&g_mu);
        if (s->idx < 0) { int k = atomic_load(&g_nsite); if (k < MAXS) { g_site[k] = s; s->idx = k; atomic_store(&g_nsite, k + 1); } }
        if (g_plant < 0) { const char* e = getenv("ROGUESQ_S7408_PLANT"); g_plant = e && e[0] == '1'; }
        pthread_mutex_unlock(&g_mu);
        i = s->idx; if (i < 0) return;
    }
    int cvt = s->kind >= 2;
    unsigned long long c = atomic_fetch_add(&g_calls[i], 1) + 1;
    if (cvt && fegetround() == FE_TOWARDZERO) atomic_fetch_add(&g_rmz[i], 1);
    double ax = fabs(x); union { double d; unsigned long long u; } a = { ax };
    if (x == x) { unsigned long long cur = atomic_load(&g_maxbits[i]); while (a.u > cur && !atomic_compare_exchange_weak(&g_maxbits[i], &cur, a.u)) {} }
    double rv;
    if (unimpl(x, cvt, &rv)) {
        unsigned long long o = atomic_fetch_add(&g_oor[i], 1) + 1;
        if (o <= 6) fprintf(stderr, "[s7408-oor] pc=%08x fn=%s kind=%s n=%llu x=%.9g host=%d\n", s->pc, s->fn, KN[s->kind & 3], o, x, host);
    } else if ((int32_t)rv != host) {
        unsigned long long o = atomic_fetch_add(&g_mism[i], 1) + 1;
        if (o <= 6) fprintf(stderr, "[s7408-mism] pc=%08x fn=%s kind=%s x=%.9g host=%d model=%d\n", s->pc, s->fn, KN[s->kind & 3], x, host, (int32_t)rv);
    }
    if (g_plant > 0 && (c & 4095) == 1) {
        atomic_fetch_add(&g_pl[i], 1);
        if (unimpl(x * 1e10 + (x < 0 ? -3e9 : 3e9), cvt, &rv)) atomic_fetch_add(&g_ploor[i], 1);
    }
    unsigned long long tot = atomic_fetch_add(&g_tot, 1) + 1;
    if ((tot & 65535) == 0) { double tn = now_s(); if (tn - g_last > 10.0) { g_last = tn; dump("periodic"); } }
}
