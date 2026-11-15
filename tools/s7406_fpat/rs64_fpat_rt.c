/* s7406 runtime half of rs64_fpat.h (copied into the transformed RecompiledFuncs dir by the transform). Diagnostic. */
#include "rs64_fpat.h"
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define MAXS 8192
static struct rs64_fpsite* g_site[MAXS];
static _Atomic unsigned long long g_cnt[MAXS][6]; /* hits, ioc, dzc, ofc, ufc, idc */
static _Atomic unsigned g_tidmask[MAXS];
static _Atomic int g_nsite;
static _Atomic unsigned long long g_tot, g_plants;
static pthread_mutex_t g_mu = PTHREAD_MUTEX_INITIALIZER;
static __thread int t_tid = -2;
static double g_last;
static int tid_now(void) {
    if (t_tid != -2) return t_tid;
    char n[64] = {0}; pthread_getname_np(pthread_self(), n, sizeof n);
    int v = -1; size_t L = strlen(n); size_t i = L; while (i > 0 && n[i-1] >= '0' && n[i-1] <= '9') i--;
    if (i < L) v = atoi(n + i);
    t_tid = v; return v;
}
static double now_s(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + ts.tv_nsec * 1e-9; }
static void dump(const char* why) {
    int n = atomic_load(&g_nsite);
    fprintf(stderr, "[s7406-dump] %s sites=%d tot=%llu plants=%llu\n", why, n, atomic_load(&g_tot), atomic_load(&g_plants));
    for (int i = 0; i < n; i++) {
        struct rs64_fpsite* s = g_site[i]; if (!s) continue;
        fprintf(stderr, "[s7406-site] pc=%08x fn=%s kind=%s hits=%llu ioc=%llu dzc=%llu ofc=%llu ufc=%llu idc=%llu tids=%x\n",
            s->pc, s->fn, s->what, atomic_load(&g_cnt[i][0]), atomic_load(&g_cnt[i][1]), atomic_load(&g_cnt[i][2]),
            atomic_load(&g_cnt[i][3]), atomic_load(&g_cnt[i][4]), atomic_load(&g_cnt[i][5]), atomic_load(&g_tidmask[i]));
    }
    fflush(stderr);
}
void rs64_fpat_hit(struct rs64_fpsite* s, uint64_t f, uint64_t a, uint64_t b) {
    __asm__ volatile("msr fpsr, %0" :: "r"((uint64_t)0));
    int i = s->idx;
    if (i < 0) {
        pthread_mutex_lock(&g_mu);
        if (s->idx < 0) { int k = atomic_load(&g_nsite); if (k < MAXS) { g_site[k] = s; s->idx = k; atomic_store(&g_nsite, k + 1); } }
        pthread_mutex_unlock(&g_mu);
        i = s->idx; if (i < 0) return;
    }
    unsigned long long h = atomic_fetch_add(&g_cnt[i][0], 1) + 1;
    static const int bit[5] = {0, 1, 2, 3, 7};
    for (int k = 0; k < 5; k++) if (f & (1ull << bit[k])) atomic_fetch_add(&g_cnt[i][1 + k], 1);
    int t = tid_now(); atomic_fetch_or(&g_tidmask[i], 1u << ((t < 0 ? 31 : t) & 31));
    if (h <= 4) {
        char n[32] = {0}; pthread_getname_np(pthread_self(), n, sizeof n);
        fprintf(stderr, "[s7406-hit] pc=%08x fn=%s kind=%s n=%llu fpsr=%llx tid=%d thr=%s a=%016llx b=%016llx\n", s->pc, s->fn, s->what,
            h, (unsigned long long)f, t, n, (unsigned long long)a, (unsigned long long)b);
    }
    unsigned long long tot = atomic_fetch_add(&g_tot, 1) + 1;
    double tn = now_s();
    if ((tot & 4095) == 0 || tn - g_last > 10.0) { g_last = tn; dump("periodic"); }
}
/* Positive control: planted denormal-result multiply (UFC both arms) and denormal-input multiply (IDC when FZ=1),
 * inline in a guest function (the transform puts the call + its own RS64_FPCHK before that function's first FP stmt). */
void rs64_fpat_plant(void) {
    static int on = -1; if (on < 0) { const char* e = getenv("ROGUESQ_S7406_PLANT"); on = e && e[0] == '1'; }
    if (!on) return;
    static _Atomic unsigned long long calls; unsigned long long c = atomic_fetch_add(&calls, 1) + 1;
    if (c % 2000 != 0 || atomic_load(&g_plants) >= 8) return;
    atomic_fetch_add(&g_plants, 1);
    volatile float x = 1e-30f, y = 1e-10f; volatile float z = x * y; (void)z;
    union { uint32_t u; float f; } d = { 0x00400000u }; volatile float dv = d.f; volatile float w = dv * 3.0f; (void)w;
}
