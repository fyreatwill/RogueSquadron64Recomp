// s7644 class TS-3: RSP audio task vs guest PI DMA on the same RDRAM bytes (default off, ROGUESQ_S7644_RSPDMA=1).
// s7643 TSan: recomp::do_rom_read (guest PI DMA thread, submitDmaSlot) wrote RDRAM bytes recomp::rsp::run_task had read in its
// inlined ucode_data -> DMEM byte copy (rsp.cpp dma_rdram_to_dmem(rdram, 0, t.ucode_data, ...), atos run_task+7108 on tsan3).
// This instrument answers, per PI DMA overlapping the LAST audio task's ucode_data image or command list [data_ptr, +data_size):
//   state  = copy (the task is copying ucode_data into DMEM right now: a torn image is possible), run (ucode executing), idle
//   chg    = bytes the DMA actually changed in the overlapping span (0 = the game rewrote identical bytes)
// Second witness, independent of the PI hook: FNV of the ucode_data image at every audio task vs the previous task with the same
// address (img_chg). Positive control ROGUESQ_S7644_RSPDMA_CTL=1: the first PI DMA after the first audio task is also classified
// against a synthetic range equal to its own destination (must show one ctl line with chg counted through the same code path).
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>

extern "C" uint32_t rs64_phase_ord();
extern "C" volatile uint32_t g_rs64_last_guest_pc;

namespace {
bool env_on(const char* n) { const char* e = std::getenv(n); return e && *e && *e != '0'; }
const bool g_on = env_on("ROGUESQ_S7644_RSPDMA");
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

extern "C" void rs64_s7644_pi_pre(const uint8_t* rdram, uint32_t dram, uint32_t size) {
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

extern "C" void rs64_s7644_pi_post(const uint8_t* rdram, uint32_t dram, uint32_t size, uint32_t rom_off) {
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
