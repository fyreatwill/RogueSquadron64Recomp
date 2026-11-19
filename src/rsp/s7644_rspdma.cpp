// s7644 class TS-3: RSP audio task vs guest PI DMA on the same RDRAM bytes (default off, ROGUESQ_S7644_RSPDMA=1).
// s7643 TSan: recomp::do_rom_read (guest PI DMA thread, submitDmaSlot) wrote RDRAM bytes recomp::rsp::run_task had read in its
// inlined ucode_data -> DMEM byte copy (rsp.cpp dma_rdram_to_dmem(rdram, 0, t.ucode_data, ...), atos run_task+7108 on tsan3).
// This instrument answers, per PI DMA overlapping the LAST audio task's ucode_data image or command list [data_ptr, +data_size):
//   state  = copy (the task is copying ucode_data into DMEM right now: a torn image is possible), run (ucode executing), idle
//   chg    = bytes the DMA actually changed in the overlapping span (0 = the game rewrote identical bytes)
// Second witness, independent of the PI hook: FNV of the ucode_data image at every audio task vs the previous task with the same
// address (img_chg). Positive control ROGUESQ_S7644_RSPDMA_CTL=1: the first PI DMA after the first audio task is also classified
// against a synthetic range equal to its own destination (must show one ctl line with chg counted through the same code path).
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <vector>
#include <map>
#include <pthread.h>

extern "C" uint32_t rs64_phase_ord();
extern "C" volatile uint32_t g_rs64_last_guest_pc;

namespace {
bool env_on(const char* n) { const char* e = std::getenv(n); return e && *e && *e != '0'; }
// s7645: the value is a bit mask: 1 = audio (TS-3), 2 = gfx (TS-4), 3 = both.
const int g_mode = [] { const char* e = std::getenv("ROGUESQ_S7644_RSPDMA"); return (e && *e) ? std::atoi(e) : 0; }();
const bool g_on = (g_mode & 1) != 0;
const bool g_ctl = env_on("ROGUESQ_S7644_RSPDMA_CTL");
std::atomic<uint32_t> g_ud{0}, g_uds{0}, g_dp{0}, g_ds{0}, g_state{0};  // state 0 idle, 1 copy, 2 run
std::atomic<uint64_t> g_tasks{0}, g_dmas{0};
std::atomic<bool> g_ctl_done{false};
// counters [region 0 ud / 1 dp / 2 ctl][state at pre 0..2][changed 0/1]
std::atomic<uint64_t> g_cnt[3][3][2];
std::atomic<uint64_t> g_torn{0};      // state changed between pre and post (copy window crossed the DMA)
std::atomic<uint64_t> g_lines{0};
std::atomic<uint64_t> g_img_same{0}, g_img_chg{0};
inline uint8_t rb(const uint8_t* rdram, uint32_t a) { return rdram[(a & 0x007FFFFFu) ^ 3]; }
struct Snap { bool any; uint32_t lo[3], hi[3]; uint32_t st; uint8_t buf[3][0x1000]; };
thread_local Snap t_snap;
const char* kReg[3] = {"ud", "dp", "ctl"};
const char* kSt[3] = {"idle", "copy", "run"};

void summary(const char* why) {
    std::fprintf(stderr, "[s7644-sum] why=%s phase=%u tasks=%llu dmas=%llu img_same=%llu img_chg=%llu torn=%llu", why, rs64_phase_ord(),
                 (unsigned long long)g_tasks.load(), (unsigned long long)g_dmas.load(), (unsigned long long)g_img_same.load(),
                 (unsigned long long)g_img_chg.load(), (unsigned long long)g_torn.load());
    for (int r = 0; r < 3; r++) for (int s = 0; s < 3; s++) for (int c = 0; c < 2; c++) {
        const uint64_t v = g_cnt[r][s][c].load();
        if (v) std::fprintf(stderr, " %s.%s.%s=%llu", kReg[r], kSt[s], c ? "chg" : "same", (unsigned long long)v);
    }
    std::fputc('\n', stderr); std::fflush(stderr);
}
}  // namespace

// edge 0: before the ucode_data copy, 1: after it, 2: after the ucode returned. Audio tasks only.
extern "C" void rs64_s7644_task(const uint8_t* rdram, int edge, uint32_t ud, uint32_t uds, uint32_t dp, uint32_t ds) {
    if (!g_on) return;
    if (edge == 0) {
        static uint32_t last_ud = 0xFFFFFFFFu, last_h = 0;
        const uint32_t u = ud & 0xFFFFFFu, n = uds > 0x1000u ? 0x1000u : uds;
        uint32_t h = 2166136261u;
        for (uint32_t i = 0; i < n; i++) { h ^= rb(rdram, u + i); h *= 16777619u; }
        if (u == last_ud) { if (h == last_h) g_img_same++; else { const uint64_t k = ++g_img_chg; if (k <= 8) std::fprintf(stderr, "[s7644-img] task=%llu ud=0x%06X size=0x%X hash %08X -> %08X\n", (unsigned long long)g_tasks.load(), u, uds, last_h, h); } }
        last_ud = u; last_h = h;
        g_ud.store(u); g_uds.store(uds); g_dp.store(dp & 0xFFFFFFu); g_ds.store(ds);
        const uint64_t t = ++g_tasks;
        if (t <= 2) std::fprintf(stderr, "[s7644-task] n=%llu ud=0x%06X uds=0x%X dp=0x%06X ds=0x%X\n", (unsigned long long)t, u, uds, dp & 0xFFFFFFu, ds);
        g_state.store(1, std::memory_order_seq_cst);
    } else {
        g_state.store(edge == 1 ? 2u : 0u, std::memory_order_seq_cst);
    }
}

static void aud_pi_pre(const uint8_t* rdram, uint32_t dram, uint32_t size) {
    t_snap.any = false;
    if (!g_on || g_tasks.load() == 0) return;
    const uint64_t nd = ++g_dmas;
    const uint32_t d = dram & 0xFFFFFFu, e = d + size;
    uint32_t base[3] = {g_ud.load(), g_dp.load(), 0}, len[3] = {g_uds.load(), g_ds.load(), 0};
    if (g_ctl && !g_ctl_done.exchange(true)) { base[2] = d; len[2] = size; }
    t_snap.st = g_state.load(std::memory_order_seq_cst);
    for (int r = 0; r < 3; r++) {
        t_snap.lo[r] = t_snap.hi[r] = 0;
        if (!len[r]) continue;
        const uint32_t lo = d > base[r] ? d : base[r], hi0 = e < base[r] + len[r] ? e : base[r] + len[r];
        if (lo >= hi0) continue;
        const uint32_t hi = hi0 - lo > 0x1000u ? lo + 0x1000u : hi0;
        t_snap.lo[r] = lo; t_snap.hi[r] = hi; t_snap.any = true;
        for (uint32_t a = lo; a < hi; a++) t_snap.buf[r][a - lo] = rb(rdram, a);
    }
    if ((nd % 4096u) == 0) summary("dmas");
}

static void aud_pi_post(const uint8_t* rdram, uint32_t dram, uint32_t size, uint32_t rom_off) {
    if (!g_on || !t_snap.any) return;
    const uint32_t st_post = g_state.load(std::memory_order_seq_cst);
    const bool torn = st_post != t_snap.st;
    if (torn) g_torn++;
    for (int r = 0; r < 3; r++) {
        if (t_snap.hi[r] <= t_snap.lo[r]) continue;
        uint32_t chg = 0;
        for (uint32_t a = t_snap.lo[r]; a < t_snap.hi[r]; a++) chg += rb(rdram, a) != t_snap.buf[r][a - t_snap.lo[r]];
        const uint32_t s = t_snap.st > 2 ? 0 : t_snap.st;
        const uint64_t tot = ++g_cnt[r][s][chg ? 1 : 0];
        if (r == 2 || (tot <= 6 && g_lines.fetch_add(1) < 64))
            std::fprintf(stderr, "[s7644-hit] reg=%s state=%s post=%s chg=%u span=0x%06X+0x%X dma=0x%06X+0x%X rom_off=0x%08X pc=0x%08X phase=%u task=%llu\n",
                         kReg[r], kSt[s], kSt[st_post > 2 ? 0 : st_post], chg, t_snap.lo[r], t_snap.hi[r] - t_snap.lo[r], dram & 0xFFFFFFu, size,
                         rom_off, (unsigned)g_rs64_last_guest_pc, rs64_phase_ord(), (unsigned long long)g_tasks.load());
        if (tot == 1 || (tot % 64u) == 0) summary(kReg[r]);
    }
    t_snap.any = false;
}

// ---------------------------------------------------------------------------------------------------------------------------
// s7645 class TS-4 (ROGUESQ_S7644_RSPDMA=2): LLE gfx task (factor5_gfx_runner, F5 ucode) vs guest PI DMA on the RDRAM the task
// reads through RSP DMA (display list chunks, vertices, matrices, ucode_data; NOT RDP texture reads, which RT64 does itself).
// Tables:
//   pi.run.cur   PI DMA landing while a gfx task runs, on bytes this task already DMA-read (chg = bytes it altered)
//   pi.run.prev  PI DMA landing while a gfx task runs, on bytes the previous task read (likely to be read again by this one)
//   pi.idle.prev PI DMA between gfx tasks on bytes the last task read (buffer reuse; ordinary if chg and the game owns it)
//   rd.after.pi  a gfx task DMA-reads bytes a PI DMA wrote DURING this task (the task consumed data that arrived mid-run)
// Positive controls (ROGUESQ_S7644_RSPDMA_CTL=1): the first PI DMA during a running gfx task is also classified against its own
// destination (ctl.pi, must count chg through the same path) and the first gfx read after that gets a synthetic PI record equal
// to its own range (ctl.rd, must count through the rd.after.pi path).
namespace {
const bool g_gon = (g_mode & 2) != 0;
struct Rg { uint32_t lo, hi; };
struct Pr { uint32_t lo, hi, rom, ctl, src; };
// s7646: issuer (osPiStartDma/osEPiStartDma ra + guest OSThread id) and the stale-order refetch test.
thread_local uint32_t t_src_ra = 0, t_src_tid = 0xFFFFFFFFu; thread_local bool t_src_set = false;
struct St { uint32_t lo, hi, src; bool refetch; };
std::vector<St> g_gstale;  // spans the task read, then a PI DMA during the task changed (this task)
std::vector<std::pair<uint32_t, uint32_t>> g_srcs;  // src index -> (ra, tid)
struct SrcC { uint64_t pi_run, rd_after_b, stale, stale_b, refetch, refetch_b; };
std::vector<SrcC> g_srcc;
uint64_t g_stale_n = 0, g_stale_b = 0, g_refetch_n = 0, g_refetch_b = 0, g_stale_tasks = 0, g_refetch_ctl = 0;
bool g_refetch_ctl_armed = false;
uint32_t src_idx(uint32_t ra, uint32_t tid) {
    for (uint32_t i = 0; i < g_srcs.size(); i++) if (g_srcs[i].first == ra && g_srcs[i].second == tid) return i;
    if (g_srcs.size() >= 256) return 255;
    g_srcs.push_back({ra, tid}); g_srcc.push_back({}); return (uint32_t)g_srcs.size() - 1;
}
void stale_tally() {  // g_gmu held, at task end
    bool any = false;
    for (const St& t : g_gstale) {
        if (t.src == 0xFFFFFFFEu) continue;
        const uint32_t b = t.hi - t.lo; any = true;
        g_stale_n++; g_stale_b += b; if (t.src < g_srcc.size()) { g_srcc[t.src].stale++; g_srcc[t.src].stale_b += b; }
        if (t.refetch) { g_refetch_n++; g_refetch_b += b; if (t.src < g_srcc.size()) { g_srcc[t.src].refetch++; g_srcc[t.src].refetch_b += b; } }
    }
    if (any) g_stale_tasks++;
    g_gstale.clear();
}
std::mutex g_gmu;
std::vector<Rg> g_gcur, g_gprev;
std::vector<Pr> g_gpi;  // PI DMAs that landed during the current task
bool g_grun = false;
uint64_t g_gtasks = 0, g_gpi_n = 0, g_gpi_run_n = 0, g_grd_n = 0, g_grd_bytes = 0, g_gcap = 0;
bool g_gctl_pi = false, g_gctl_rd_armed = false, g_gctl_rd_done = false;
enum { K_RUN_CUR, K_RUN_PREV, K_IDLE_PREV, K_CTL_PI, K_N };
const char* kK[K_N] = {"pi.run.cur", "pi.run.prev", "pi.idle.prev", "ctl.pi"};
uint64_t g_gk[K_N][2], g_gk_bytes[K_N][2];
uint64_t g_grd_after = 0, g_grd_after_bytes = 0, g_gctl_rd = 0;
uint32_t g_glines = 0;
pthread_t g_gtid; uint32_t g_gdl = 0; uint64_t g_gother = 0, g_gother_ovl = 0;
std::map<uint64_t, uint64_t> g_ghist;  // key (pi dram >> 12) << 32 | (rom_off >> 16) | mem<<24 -> rd_after_pi bytes
struct GSnap { bool any, run; uint32_t d, n; uint32_t span[K_N][16][2]; uint32_t nspan[K_N]; std::vector<uint8_t> buf; };
thread_local GSnap t_g;
void gadd(std::vector<Rg>& v, uint32_t lo, uint32_t hi) {
    if (!v.empty() && v.back().hi >= lo && v.back().lo <= hi) { if (lo < v.back().lo) v.back().lo = lo; if (hi > v.back().hi) v.back().hi = hi; return; }
    if (v.size() >= 8192) { g_gcap++; return; }
    v.push_back({lo, hi});
}
void gsum(const char* why) {  // g_gmu held
    std::fprintf(stderr, "[s7645-sum] why=%s phase=%u gtasks=%llu reads=%llu rbytes=%llu pi=%llu pi_during_run=%llu cap=%llu rd_after_pi=%llu/%lluB ctl_rd=%llu",
                 why, rs64_phase_ord(), (unsigned long long)g_gtasks, (unsigned long long)g_grd_n, (unsigned long long)g_grd_bytes,
                 (unsigned long long)g_gpi_n, (unsigned long long)g_gpi_run_n, (unsigned long long)g_gcap, (unsigned long long)g_grd_after,
                 (unsigned long long)g_grd_after_bytes, (unsigned long long)g_gctl_rd);
    for (int k = 0; k < K_N; k++) for (int c = 0; c < 2; c++)
        if (g_gk[k][c]) std::fprintf(stderr, " %s.%s=%llu/%lluB", kK[k], c ? "chg" : "same", (unsigned long long)g_gk[k][c], (unsigned long long)g_gk_bytes[k][c]);
    std::fprintf(stderr, " ranges_prev=%zu other_thread_reads=%llu other_ovl=%llu stale=%llu/%lluB stale_tasks=%llu stale_refetch=%llu/%lluB ctl_refetch=%llu\n", g_gprev.size(), (unsigned long long)g_gother, (unsigned long long)g_gother_ovl,
                 (unsigned long long)g_stale_n, (unsigned long long)g_stale_b, (unsigned long long)g_stale_tasks, (unsigned long long)g_refetch_n, (unsigned long long)g_refetch_b, (unsigned long long)g_refetch_ctl);
    for (uint32_t i = 0; i < g_srcs.size() && i < 24; i++)
        std::fprintf(stderr, "[s7646-src] ra=0x%08X tid=%d pi_run=%llu rd_after=%lluB stale=%llu/%lluB refetch=%llu/%lluB\n", g_srcs[i].first, (int)g_srcs[i].second,
                     (unsigned long long)g_srcc[i].pi_run, (unsigned long long)g_srcc[i].rd_after_b, (unsigned long long)g_srcc[i].stale, (unsigned long long)g_srcc[i].stale_b,
                     (unsigned long long)g_srcc[i].refetch, (unsigned long long)g_srcc[i].refetch_b);
    std::vector<std::pair<uint64_t, uint64_t>> h(g_ghist.begin(), g_ghist.end());
    std::sort(h.begin(), h.end(), [](auto& a, auto& b) { return a.second > b.second; });
    for (size_t i = 0; i < h.size() && i < 10; i++)
        std::fprintf(stderr, "[s7645-hist] page=0x%05X000 rom64k=0x%04X0000 mem=0x%03X bytes=%llu\n", (unsigned)(h[i].first >> 40),
                     (unsigned)(h[i].first & 0xFFFF), (unsigned)((h[i].first >> 16) & 0xFFFFFF), (unsigned long long)h[i].second);
    std::fflush(stderr);
}
void gspans(const std::vector<Rg>& v, uint32_t d, uint32_t e, int k) {
    for (const Rg& r : v) {
        const uint32_t lo = d > r.lo ? d : r.lo, hi = e < r.hi ? e : r.hi;
        if (lo >= hi) continue;
        if (t_g.nspan[k] < 16) { t_g.span[k][t_g.nspan[k]][0] = lo; t_g.span[k][t_g.nspan[k]][1] = hi; t_g.nspan[k]++; }
        t_g.any = true;
    }
}
}  // namespace

// edge 0 = task start, 1 = task end (factor5_gfx_runner RAII, all return paths).
extern "C" void rs64_s7645_gfx_task(int edge, uint32_t dl) {
    if (!g_gon) return;
    std::lock_guard<std::mutex> lk(g_gmu);
    if (edge == 0) {
        g_gtid = pthread_self(); g_gdl = dl & 0x7FFFFFu;
        g_gtasks++; g_grun = true; g_gcur.clear(); g_gpi.clear(); g_gstale.clear();
        if (g_gtasks == 1 || (g_gtasks % 1800u) == 0) gsum("tasks");
    } else {
        stale_tally();
        g_grun = false; g_gprev.swap(g_gcur); g_gcur.clear(); g_gpi.clear();
    }
}

// Every RSP DMA RDRAM->DMEM in the gfx bank (rides rs64_s7094_dma_shape, armed by ROGUESQ_S7644_RSPDMA&2).
extern "C" void rs64_s7645_gfx_read(uint32_t mem, uint32_t dram, uint32_t raw_len) {
    if (!g_gon) return;
    const uint32_t lo = dram & 0x7FFFFFu, n = raw_len >= 0xFFFu ? 0x1000u : raw_len + 1u, hi = lo + n;
    std::lock_guard<std::mutex> lk(g_gmu);
    if (!g_grun) return;
    if (!pthread_equal(pthread_self(), g_gtid)) {  // not the gfx runner thread: count, do not attribute to the task
        g_gother++;
        for (const Pr& p : g_gpi) if (!p.ctl && (lo < p.hi && p.lo < hi)) { g_gother_ovl++; break; }
        return;
    }
    g_grd_n++; g_grd_bytes += n;
    if (g_ctl && g_gctl_rd_armed && !g_gctl_rd_done) { g_gctl_rd_done = true; g_gpi.push_back({lo, hi, 0xFFFFFFFFu, 1, 0}); }
    // s7646 refetch control: the first read after the first stale record is also recorded as a synthetic stale span over its
    // own range, then this same read is tested against it below (must count ctl_refetch=1 through the refetch path).
    if (g_ctl && g_refetch_ctl_armed) { g_refetch_ctl_armed = false; g_gstale.push_back({lo, hi, 0xFFFFFFFEu, false}); }
    for (St& t : g_gstale) if (lo < t.hi && t.lo < hi && !t.refetch) { t.refetch = true; if (t.src == 0xFFFFFFFEu) g_refetch_ctl++; }
    for (const Pr& p : g_gpi) {
        const uint32_t a = lo > p.lo ? lo : p.lo, b = hi < p.hi ? hi : p.hi;
        if (a >= b) continue;
        if (p.ctl) g_gctl_rd++; else { g_grd_after++; g_grd_after_bytes += b - a; if (p.src < g_srcc.size()) g_srcc[p.src].rd_after_b += b - a; g_ghist[((uint64_t)(p.lo >> 12) << 40) | ((uint64_t)(mem & 0xFFF) << 16) | (p.rom >> 16)] += b - a; }
        if (p.ctl || g_glines++ < 48)
            std::fprintf(stderr, "[s7645-rd] %s task=%llu dl=0x%06X mem=0x%03X read=0x%06X+0x%X span=0x%06X+0x%X pi=0x%06X+0x%X rom_off=0x%08X phase=%u\n",
                         p.ctl ? "ctl" : "live", (unsigned long long)g_gtasks, g_gdl, mem & 0x1FFF, lo, n, a, b - a, p.lo, p.hi - p.lo, p.rom, rs64_phase_ord());
    }
    gadd(g_gcur, lo, hi);
}

static void gfx_pi_pre(const uint8_t* rdram, uint32_t dram, uint32_t size) {
    t_g.any = false;
    if (!g_gon) return;
    const uint32_t d = dram & 0x7FFFFFu, e = d + size;
    std::lock_guard<std::mutex> lk(g_gmu);
    if (g_gtasks == 0) return;
    g_gpi_n++;
    t_g.run = g_grun; t_g.d = d; t_g.n = size;
    for (int k = 0; k < K_N; k++) t_g.nspan[k] = 0;
    if (g_grun) {
        g_gpi_run_n++;
        gspans(g_gcur, d, e, K_RUN_CUR); gspans(g_gprev, d, e, K_RUN_PREV);
        if (g_ctl && !g_gctl_pi) { g_gctl_pi = true; g_gctl_rd_armed = true; t_g.span[K_CTL_PI][0][0] = d; t_g.span[K_CTL_PI][0][1] = e; t_g.nspan[K_CTL_PI] = 1; t_g.any = true; }
    } else {
        gspans(g_gprev, d, e, K_IDLE_PREV);
    }
    if (t_g.any) {
        const uint32_t m = size > 0x200000u ? 0x200000u : size;
        t_g.buf.resize(m);
        for (uint32_t i = 0; i < m; i++) t_g.buf[i] = rb(rdram, d + i);
    }
}

static void gfx_pi_post(const uint8_t* rdram, uint32_t dram, uint32_t size, uint32_t rom_off) {
    if (!g_gon) return;
    const uint32_t d = dram & 0x7FFFFFu;
    std::lock_guard<std::mutex> lk(g_gmu);
    const uint32_t ra = t_src_set ? t_src_ra : 0u, thr = t_src_set ? t_src_tid : 0u; t_src_set = false;
    const uint32_t tid = (thr >= 0x80000000u && thr + 0x18u <= 0x80800000u) ? (uint32_t)*(const int32_t*)(rdram + ((thr + 0x14u) & 0x7FFFFCu)) : 0xFFFFFFFFu;
    if (g_gtasks == 0) return;
    const uint32_t si = (g_grun || t_g.run) ? src_idx(ra, tid) : 0u;
    if (g_grun || t_g.run) { g_srcc[si < g_srcc.size() ? si : 0].pi_run++; if (g_gpi.size() < 4096) g_gpi.push_back({d, d + size, rom_off, 0, si}); }
    if (!t_g.any) return;
    const uint32_t m = (uint32_t)t_g.buf.size();
    for (int k = 0; k < K_N; k++) {
        if (!t_g.nspan[k]) continue;
        uint32_t chg = 0, bytes = 0;
        for (uint32_t j = 0; j < t_g.nspan[k]; j++) {
            uint32_t cj = 0;
            for (uint32_t a = t_g.span[k][j][0]; a < t_g.span[k][j][1]; a++) { bytes++; if (a - d < m && rb(rdram, a) != t_g.buf[a - d]) { chg++; cj++; } }
            if (k == K_RUN_CUR && cj && g_grun && g_gstale.size() < 8192) { g_gstale.push_back({t_g.span[k][j][0], t_g.span[k][j][1], si, false}); if (g_ctl && g_stale_n == 0 && g_gstale.size() == 1) g_refetch_ctl_armed = true; }
        }
        const int c = chg ? 1 : 0;
        const uint64_t tot = ++g_gk[k][c]; g_gk_bytes[k][c] += bytes;
        if (k == K_CTL_PI || (tot <= 6 && g_glines++ < 48))
            std::fprintf(stderr, "[s7645-pi] reg=%s chg=%u bytes=%u first=0x%06X+0x%X dma=0x%06X+0x%X rom_off=0x%08X pc=0x%08X post_run=%d phase=%u task=%llu\n",
                         kK[k], chg, bytes, t_g.span[k][0][0], t_g.span[k][0][1] - t_g.span[k][0][0], d, size, rom_off,
                         (unsigned)g_rs64_last_guest_pc, (int)g_grun, rs64_phase_ord(), (unsigned long long)g_gtasks);
        if (tot == 1) gsum(kK[k]);
    }
    t_g.any = false;
}

extern "C" void rs64_s7644_pi_pre(const uint8_t* rdram, uint32_t dram, uint32_t size) { aud_pi_pre(rdram, dram, size); gfx_pi_pre(rdram, dram, size); }
extern "C" void rs64_s7644_pi_post(const uint8_t* rdram, uint32_t dram, uint32_t size, uint32_t rom_off) {
    aud_pi_post(rdram, dram, size, rom_off); gfx_pi_post(rdram, dram, size, rom_off);
}
extern "C" void rs64_s7646_pi_src(uint32_t ra, uint32_t thread) {
    if (!g_gon) return;
    t_src_ra = ra; t_src_set = true;
    t_src_tid = thread;  // OSThread VA; id (offset 0x14) read in gfx_pi_post, which has rdram
}
extern "C" int rs64_s7645_gfx_on() { return g_gon ? 1 : 0; }
