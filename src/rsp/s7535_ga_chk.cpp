// s7535 class GA: does the guest change a gfx task's RSP inputs inside the early-sp_complete window?
//
// ultramodern's Gfx thread sends sp_complete BEFORE send_dl runs the Factor 5 LLE (events.cpp: "Games usually preserve the RSP
// inputs until the RDP is finished"), so every RSP DMA fetch of the gfx task (display list, vertices, matrices, segment tables)
// happens while the guest CPU already runs.  On hardware the guest is told "SP done" only after the RSP fetched everything.
// A guest store that lands in a gfx input after the early sp_complete and before the LLE fetches it is a decision the port
// makes on bytes hardware would never have seen (H-latent-fix); if the game keeps its gfx inputs until dp_complete the
// window is quiescent (H-canon).
//
// ROGUESQ_S7535_GA_CHK=1:
//   snap  (Gfx thread, right before the early sp_complete): copy guest RAM [0, osmem) and the spill arena [16 MB, 24 MB).
//   dma   (every non-audio dma_rdram_to_dmem while the window is open): compare the fetched bytes with the snapshot ->
//         diff_bytes / diff_dmas = bytes the guest (or another host thread) changed between sp_complete and the fetch.
//   wr    (every non-audio dma_dmem_to_rdram while open): mirror the LLE's own RDRAM writes into the snapshot, so a later
//         fetch of bytes the task itself wrote is not counted.
//   close (after send_dl returns, before dp_complete): every 32nd task counts ALL bytes changed in the window (activity
//         witness: proves the guest/host really write memory during the window, so a zero diff is not an idle window).
// Control: on every 64th task the first fetch is compared twice, once with one snapshot byte flipped; ctl_caught must equal
// ctl_planted (the same compare loop sees a one-byte change inside a fetched range).
// Per phase (rs64_phase_ord). Dump rs64_s7535.log in cwd (build/) every 5 s (SIGKILL-safe); first 60 diff rows on stderr.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <vector>
#include <pthread.h>
extern "C" uint32_t rs64_phase_ord(void);
extern "C" uint32_t rs64_ram_top;
extern "C" int rs64_s7535_on = [] {
    const char* e = getenv("ROGUESQ_S7535_GA_CHK");
    const int v = (e && *e && *e != '0') ? 1 : 0;
    if (v) fprintf(stderr, "[s7535] gfx RSP-input window check armed (snapshot at early sp_complete, compare per DMA fetch)\n");
    return v;
}();
namespace {
constexpr uint32_t kSpLo = 0x1000000u, kSpHi = 0x1800000u;
struct St {
    unsigned long long tasks = 0, dmas = 0, bytes = 0, diff_bytes = 0, diff_dmas = 0, oob = 0, wr_mirror = 0;
    unsigned long long ctl_planted = 0, ctl_caught = 0, sampled = 0, win_chg = 0, win_chg_tasks = 0, diff_tasks = 0;
    unsigned long long prod = 0, clear = 0, other = 0, refetch = 0, refetch_diff = 0;  // first-diff word 0->x / x->0 / x->y; same (dram,len) as the previous fetch
};
St g_st[16][2];  // [phase][late]: late = this task got sp_complete AFTER send_dl (ROGUESQ_S7535_LATE)
std::vector<uint8_t> g_sh;
uint32_t g_top = 0;
bool g_open = false, g_plant = false, g_task_diff = false;
uint32_t g_prev_a = ~0u, g_prev_n = 0;
unsigned long long g_task = 0;
pthread_t g_gfx;  // the Gfx thread (set at snap); audio tasks may share dmem, so the filter is the thread, not the DMEM base
int g_rows = 0;
time_t g_last = 0;
struct Row { unsigned long long task; uint32_t ph, dram, len, first, live, snap, n; int late; };
Row g_row[60];
unsigned long long g_hist[2][384];  // flight (phase>=5) diff bytes per 64 KB bucket of 0..24 MB, [late]
int g_frows = 0;
int g_late = 0;
St& ph() { const uint32_t p = rs64_phase_ord(); return g_st[p < 16 ? p : 15][g_late]; }
// ROGUESQ_S7535_LATE=alt: per task, bit = splitmix64(task index) & 1 picks early (0, upstream) or late (1) sp_complete, so
// both states see the same scenes in one run (iron rule 2). =1: every task late. Unset: upstream early sp_complete.
const int s_late_mode = [] { const char* e = getenv("ROGUESQ_S7535_LATE"); return !e || !*e || *e == '0' ? 0 : (*e == 'a' ? 2 : 1); }();
uint64_t mix(uint64_t x) { x += 0x9E3779B97F4A7C15ull; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ull; x = (x ^ (x >> 27)) * 0x94D049BB133111EBull; return x ^ (x >> 31); }
bool in_range(uint32_t lo, uint32_t hi) { return (hi <= g_top) || (lo >= kSpLo && hi <= kSpHi); }
uint32_t count(const uint8_t* rdram, uint32_t lo, uint32_t hi, uint32_t* first) {
    uint32_t d = 0;
    for (uint32_t i = lo; i < hi; ++i)
        if (rdram[i] != g_sh[i]) { if (!d && first) *first = i; ++d; }
    return d;
}
uint32_t w(const uint8_t* p, uint32_t a) { a &= ~3u; uint32_t v; memcpy(&v, p + a, 4); return v; }
void dump() {
    FILE* f = fopen("rs64_s7535.log", "w");
    if (!f) return;
    for (int p = 0; p < 16; ++p) for (int l = 0; l < 2; ++l) {
        const St& s = g_st[p][l];
        if (!s.tasks) continue;
        fprintf(f, "[s7535-sum] phase=%d late=%d tasks=%llu dmas=%llu bytes=%llu diff_bytes=%llu diff_dmas=%llu diff_tasks=%llu oob=%llu "
                   "wr_mirror=%llu ctl_planted=%llu ctl_caught=%llu sampled=%llu win_chg_bytes=%llu win_chg_tasks=%llu prod=%llu clear=%llu other=%llu refetch=%llu refetch_diff=%llu\n",
                p, l, s.tasks, s.dmas, s.bytes, s.diff_bytes, s.diff_dmas, s.diff_tasks, s.oob, s.wr_mirror, s.ctl_planted,
                s.ctl_caught, s.sampled, s.win_chg, s.win_chg_tasks, s.prod, s.clear, s.other, s.refetch, s.refetch_diff);
    }
    for (int i = 0; i < g_rows && i < 60; ++i) {
        const Row& r = g_row[i];
        fprintf(f, "[s7535-diff] task=%llu phase=%u late=%d dram=%06X len=%X first=%06X n=%u live=%08X snap=%08X\n", r.task, r.ph, r.late,
                r.dram, r.len, r.first, r.n, r.live, r.snap);
    }
    for (int l = 0; l < 2; ++l) for (int b = 0; b < 384; ++b)
        if (g_hist[l][b]) fprintf(f, "[s7535-hist] late=%d bucket=%06X bytes=%llu\n", l, b << 16, g_hist[l][b]);
    fclose(f);
}
}  // namespace

extern "C" void rs64_s7535_snap(const uint8_t* rdram) {
    if (g_sh.empty()) {
        g_top = rs64_ram_top - 0x80000000u;
        if (g_top > kSpLo) g_top = kSpLo;
        g_sh.resize(kSpHi);
    }
    memcpy(g_sh.data(), rdram, g_top);
    memcpy(g_sh.data() + kSpLo, rdram + kSpLo, kSpHi - kSpLo);
    ++g_task;
    g_late = s_late_mode == 2 ? (int)(mix(g_task) & 1u) : s_late_mode;
    ++ph().tasks;
    g_plant = (g_task % 64u) == 5u;
    g_task_diff = false;
    g_prev_a = ~0u;
    g_gfx = pthread_self();
    g_open = true;
}

extern "C" void rs64_s7535_dma(const uint8_t* rdram, uint32_t dram, uint32_t len, int aud) {
    (void)aud;
    if (!g_open || !len || !pthread_equal(pthread_self(), g_gfx)) return;
    St& s = ph();
    ++s.dmas;
    const uint32_t lo = dram, hi = dram + len;
    if (hi < lo || !in_range(lo, hi)) { ++s.oob; return; }
    s.bytes += len;
    const bool re = (dram == g_prev_a && len == g_prev_n); g_prev_a = dram; g_prev_n = len;
    if (re) ++s.refetch;
    uint32_t first = lo;
    const uint32_t d = count(rdram, lo, hi, &first);
    if (g_plant) {
        g_plant = false;
        ++s.ctl_planted;
        g_sh[lo] ^= 0x5Au;
        const uint32_t dp = count(rdram, lo, hi, nullptr);
        g_sh[lo] ^= 0x5Au;
        if (dp != d) ++s.ctl_caught;
    }
    if (!d) return;
    if (re) ++s.refetch_diff;
    { const uint32_t wl = w(rdram, first), ws = w(g_sh.data(), first); if (!ws && wl) ++s.prod; else if (ws && !wl) ++s.clear; else ++s.other; }
    ++s.diff_dmas;
    s.diff_bytes += d;
    if (!g_task_diff) { g_task_diff = true; ++s.diff_tasks; }
    const bool flight = rs64_phase_ord() >= 5u;
    if (flight) for (uint32_t i = lo; i < hi; ++i) if (rdram[i] != g_sh[i]) g_hist[g_late][(i >> 16) % 384u] += 1;
    if (flight && g_frows < 120 && (g_task % 7u) == 0u) {
        ++g_frows;
        fprintf(stderr, "[s7535-fdiff] task=%llu late=%d dram=%06X len=%X first=%06X n=%u live=%08X snap=%08X live4=%08X snap4=%08X\n", g_task, g_late, dram, len,
                first, d, w(rdram, first), w(g_sh.data(), first), w(rdram, first + 4), w(g_sh.data(), first + 4));
    }
    if (g_rows < 60) {
        g_row[g_rows] = {g_task, rs64_phase_ord(), dram, len, first, w(rdram, first), w(g_sh.data(), first), d, g_late};
        fprintf(stderr, "[s7535-diff] task=%llu phase=%u late=%d dram=%06X len=%X first=%06X n=%u live=%08X snap=%08X\n", g_task,
                rs64_phase_ord(), g_late, dram, len, first, d, w(rdram, first), w(g_sh.data(), first));
        ++g_rows;
    }
}

extern "C" void rs64_s7535_wr(const uint8_t* rdram, uint32_t dram, uint32_t len, int aud) {
    (void)aud;
    if (!g_open || !len || !pthread_equal(pthread_self(), g_gfx)) return;
    const uint32_t lo = dram, hi = dram + len;
    if (hi < lo || !in_range(lo, hi)) return;
    memcpy(g_sh.data() + lo, rdram + lo, len);
    ++ph().wr_mirror;
}

extern "C" void rs64_s7535_close(const uint8_t* rdram) {
    if (!g_open) return;
    g_open = false;
    St& s = ph();
    if ((g_task % 32u) == 7u) {
        const uint32_t n = count(rdram, 0, g_top, nullptr) + count(rdram, kSpLo, kSpHi, nullptr);
        ++s.sampled;
        s.win_chg += n;
        if (n) ++s.win_chg_tasks;
    }
    const time_t now = time(nullptr);
    if (now - g_last >= 5) { g_last = now; dump(); }
}

// events.cpp asks once per gfx task (after snap): 1 = deliver sp_complete after send_dl instead of before it.
extern "C" int rs64_s7535_late(void) { return g_open ? g_late : 0; }
