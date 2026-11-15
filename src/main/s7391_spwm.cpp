// s7391 guest stack low-water watch, host half (guest half: include/spwm/recomp.h, compiled in ONLY in build_spwm,
// cmake -DROGUESQ_SP_WATCH=ON; in every other build nothing calls rs64_spwm_new and this file is inert).
// Question (idiom class BA, guest thread stack headroom): does any guest thread ever push its $sp below the bottom of
// the stack its osCreateThread gave it? Two of the game's 12 creators hand out only 1 KB (rs_malloc base + 0x400 at
// 0x800073F0 / 0x80091BF8), so an overflow would write the heap block header below the allocation.
// Per host thread (ultramodern runs each OSThread on its own host thread) the first $sp seen is the "first" anchor
// and every new minimum >= 16 bytes below the last reported one prints
//   [s7391-sp] tid=<n> first=0x.. min=0x.. depth=<first-min> file:line nz_below=<k>/64 nz_above=<k>/16
// nz_below/nz_above = nonzero words in the 256 B under / 64 B over the new minimum, read from guest memory at report
// time (second evidence line: frames really sit at and above min; below min is whatever the memory was).
// Line B (independent of the $sp hook): when the thread's entry a0 is a registerServiceWorker descriptor (+8 top,
// +12 bottom, two 0xCDCDCDCD canary words at bottom), the stack [bottom, top) is snapshotted at the entry prologue and
// every 2^18 $sp adjusts the thread rescans it for the lowest word that differs from the snapshot:
//   [s7391-scan] tid=<n> bottom=0x.. top=0x.. lowdirty=0x.. spmin=0x.. gap=<lowdirty-spmin> canary=<0/1>
// gap < 0 = memory written below the lowest $sp the hook saw (hook missed a push, or a foreign writer).
// ROGUESQ_S7391_CTL=1 = positive control for line B: flips one SNAPSHOT word (host copy, never guest memory) at
// bottom+0x40, so every scan must report ctlseen=1 (the planted word is excluded from lowdirty).
// Env: ROGUESQ_S7391_SPWM=1 enables reporting (counting is always on in this build). Diagnostic only.
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

extern "C" {
__thread uint32_t rs64_spwm_min = 0xFFFFFFFFu, rs64_spwm_cnt = 0;
}
static thread_local uint32_t t_first, t_last_rep;
static thread_local int t_id = -1;
static std::atomic<int> s_next_id{0};
static int s_on = -1, s_ctl = -1;
static thread_local uint32_t t_bot, t_top, t_last_low;
static thread_local std::vector<uint32_t> t_snap;
static uint32_t rdw(const uint8_t *rdram, uint32_t a) { uint32_t v; memcpy(&v, rdram + (a & 0x7FFFFCu), 4); return v; }

static bool spwm_on() {
    if (s_on < 0) { const char *e = getenv("ROGUESQ_S7391_SPWM"); s_on = (e && *e == '1') ? 1 : 0; }
    return s_on == 1;
}

static int nz_words(const uint8_t *rdram, uint32_t lo, uint32_t n) {
    int k = 0;
    for (uint32_t i = 0; i < n; i++) {
        uint32_t a = (lo + 4 * i) & 0x1FFFFFFCu;
        if (a >= 0x800000u) break;
        uint32_t v; memcpy(&v, rdram + a, 4);
        k += v != 0;
    }
    return k;
}

extern "C" void rs64_spwm_tick(uint8_t *rdram) {
    if (!rdram || t_snap.empty() || !spwm_on()) return;
    uint32_t low = 0;
    int ctlseen = s_ctl == 1 && t_snap.size() > 16 && rdw(rdram, t_bot + 64) != t_snap[16];
    for (size_t i = 0; i < t_snap.size(); i++) {
        if (s_ctl == 1 && i == 16) continue;  // planted word: reported as ctlseen, excluded from lowdirty
        if (rdw(rdram, t_bot + 4 * (uint32_t)i) != t_snap[i]) { low = t_bot + 4 * (uint32_t)i; break; }
    }
    if (low == t_last_low && t_last_low) return;
    t_last_low = low;
    int canary = rdw(rdram, t_bot) == 0xCDCDCDCDu && rdw(rdram, t_bot + 4) == 0xCDCDCDCDu;
    fprintf(stderr, "[s7391-scan] tid=%d bottom=0x%08X top=0x%08X lowdirty=0x%08X spmin=0x%08X gap=%d canary=%d ctlseen=%d\n",
            t_id, t_bot, t_top, low, rs64_spwm_min, low ? (int)(low - rs64_spwm_min) : 0, canary, ctlseen);
}

extern "C" void rs64_spwm_new(uint32_t sp, uint8_t *rdram, uint32_t a0, const char *file, int line) {
    if (t_id < 0) {
        t_id = s_next_id.fetch_add(1); t_first = sp; t_last_rep = 0xFFFFFFFFu;
        if (rdram && a0 >= 0x80000000u && a0 < 0x807FFFF0u) {
            uint32_t top = rdw(rdram, a0 + 8), bot = rdw(rdram, a0 + 12);
            if (top > sp && top - sp < 0x200u && bot < top && top - bot <= 0x4000u && bot >= 0x80000000u &&
                rdw(rdram, bot) == 0xCDCDCDCDu && rdw(rdram, bot + 4) == 0xCDCDCDCDu) {
                t_bot = bot; t_top = top; t_last_low = 0;
                t_snap.resize((top - bot) / 4);
                for (size_t i = 0; i < t_snap.size(); i++) t_snap[i] = rdw(rdram, bot + 4 * (uint32_t)i);
                if (s_ctl < 0) { const char *e = getenv("ROGUESQ_S7391_CTL"); s_ctl = (e && *e == '1') ? 1 : 0; }
                if (s_ctl == 1 && t_snap.size() > 16) t_snap[16] ^= 0x5A5A5A5Au;
                if (spwm_on())
                    fprintf(stderr, "[s7391-svc] tid=%d a0=0x%08X bottom=0x%08X top=0x%08X size=%u first=0x%08X\n",
                            t_id, a0, bot, top, top - bot, sp);
            }
        }
    }
    rs64_spwm_min = sp;
    if (!spwm_on()) return;
    if (t_last_rep != 0xFFFFFFFFu && t_last_rep - sp < 16u) return;
    t_last_rep = sp;
    const char *b = strrchr(file, '/');
    int nb = rdram ? nz_words(rdram, sp - 256u, 64) : -1, na = rdram ? nz_words(rdram, sp, 16) : -1;
    fprintf(stderr, "[s7391-sp] tid=%d first=0x%08X min=0x%08X depth=%u %s:%d nz_below=%d/64 nz_above=%d/16\n",
            t_id, t_first, sp, t_first - sp, b ? b + 1 : file, line, nb, na);
}
