#include "../main/rs64_apf.h"  // s7359 class AJ
#include <algorithm>
#include <pthread.h>
#include <mach/mach_time.h>
#include <chrono>
extern "C" int rs64_s7536_cnt_on; extern "C" int rs64_s7536_tri(int, int, int);  // s7536 s7535_ga_chk.cpp
extern "C" int rs64_tog_odd(uint64_t mt); extern "C" void rs64_tog_anchor(uint64_t mt);  // s7017 upstream_compat.cpp
#include <map>
#include <set>
#include <array>
// DPC bridge for RSP graphics ucodes that emit RDP commands directly via
// mtc0 to DPC_START/DPC_END (Factor5 ucode does this). On DPC_END writes
// we forward [start..end) RDRAM bytes to RT64's RDP interpreter (LLE path,
// processDisplayLists with isHLE=false), matching what RT64 would consume
// from raw RDP command bytes.
//
// Reads of DPC_CURRENT/DPC_END return g_rsp_dpc_end so busy-wait loops in
// the ucode see "RDP completed instantly" and exit.

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <atomic>
#include <mutex>
#include <unordered_map>
#include <vector>
#include <utility>

namespace RT64 { struct S4280Ev { int64_t off; uint32_t addr; uint16_t width; uint8_t odd; }; extern S4280Ev g_s4280_ev[256]; extern volatile int g_s4280_n; }
// Per-task RDP range deferral (see rs64_dpc_defer_begin/_end below).
static bool g_defer_active = false;
static std::vector<std::pair<uint32_t, uint32_t>> g_deferred_ranges;
// s4272: bump-time shadow of every deferred range (compared to RDRAM at commit time).
static std::vector<uint8_t> g_s4272_shadow;
struct S4272Sh { uint32_t lo, hi; size_t off; };
extern "C" { int g_rs64_trim = 1; }  // s6934: ROGUESQ_G1E_TRIM state, set per wrap flush
extern "C" { int g_rs64_tmem_fast = 1; }  // s6935: ROGUESQ_G1E_TMEM state, TLUT scan table and word copy in RT64, set per wrap flush
static std::vector<S4272Sh> g_s4272_sh;

// s6955 G1e: ROGUESQ_G1E_BATCH (default on after the s6955 check run, =0 old per-bump entries, =tog 10 s blocks, latched per task at defer_begin).
// The ucode bumps DPC_END once per RDP command (~50k bumps per dd4 task), and each bump became its own deferred range + shadow
// entry, which the wrap flush (per-range key lookup, undo, restore) and the commit then walk one by one. With the batch on, a
// bump contiguous with the last deferred range EXTENDS it (and its shadow entry, in lockstep, bytes appended at bump time as
// before, capped at ROGUESQ_S4272_CAP) instead of pushing. Every consumer merges contiguous ranges anyway (commit, wrap merge,
// coal) and the shadow bytes are identical, so RT64 gets the same bytes. Per-bump inspection in submit_impl is untouched.
// ROGUESQ_G1E_BATCH_CHECK=1 keeps the unmerged per-bump lists beside the batched ones and, at every flush/commit, compares
// merged run lists, concatenated shadow coverage and bytes, and counts duplicate shadow keys (where first-match lookup could
// diverge); check #1 compares against a corrupted copy as the positive control (control must be 1, bad 0).
extern "C" { int g_rs64_g1e_batch = 0; uint64_t g_rs64_g1e_ranges = 0; }
// s6956 G1e: ROGUESQ_G1E_CDIAG (default 0 = skip the commit-side s4272 latewrite compare and the s4280/s4284 attribution block,
// stderr-only diagnostics; =1 old; =tog 10 s blocks, latched per task at defer_begin).
extern "C" { int g_rs64_g1e_cdiag = 0; }
// s6957 G1e: ROGUESQ_G1E_LBFAST (default 1 = run-copy LoadBlock in RT64 loadToTMEMCommon, =0 old per-word loop, =tog 10 s blocks,
// =check runs both and compares TMEM on every block load, check #1 vs a corrupted copy = positive control). Set per wrap flush.
extern "C" { int g_rs64_g1e_lbfast = 1; }
// s6961 G1e: ROGUESQ_G1E_HGATHER (default 1 gather-buffer TMEM hash in RT64 TMEMHasher, =0 streaming, =tog 10 s blocks, =c check, =s stat).
extern "C" { int g_rs64_g1e_hgather = 1; }
// s6960 G1e: ROGUESQ_G1E_PROVCACHE (default 0; =1 provenance-keyed upload hash cache in RT64, =tog 10 s blocks, =v verify: always hashes,
// counts wrong cache hits, params-only mutant table must be wrong). Set per wrap flush; RT64 latches it at the next TMEM load.
extern "C" { int g_rs64_g1e_pcache = 0; }
static bool g_bc_on = false;
static std::vector<std::pair<uint32_t, uint32_t>> g_bc_ranges;
static std::vector<S4272Sh> g_bc_sh;
static std::vector<uint8_t> g_bc_shadow;
static void rs64_g1e_bc_check(const char *where) {
    if (!g_bc_on) return;
    static unsigned long n = 0, bad = 0, ctl = 0, dup = 0, refr = 0, batr = 0;
    ++n;
    auto merged = [](const std::vector<std::pair<uint32_t, uint32_t>> &v) {
        std::vector<std::pair<uint32_t, uint32_t>> o;
        for (const auto &r : v) { if (!o.empty() && o.back().second == r.first) o.back().second = r.second; else o.push_back(r); }
        return o;
    };
    auto cover = [](const std::vector<S4272Sh> &v) {
        std::vector<std::pair<uint32_t, uint32_t>> o;
        for (const S4272Sh &e : v) { if (!o.empty() && o.back().second == e.lo) o.back().second = e.hi; else o.push_back({e.lo, e.hi}); }
        return o;
    };
    refr += g_bc_ranges.size(); batr += g_deferred_ranges.size();
    std::vector<uint8_t> ref_sh = g_bc_shadow;
    const bool control = n == 1 && !ref_sh.empty();
    if (control) ref_sh[0] ^= 0xFF;
    const bool d = merged(g_bc_ranges) != merged(g_deferred_ranges) || cover(g_bc_sh) != cover(g_s4272_sh) || ref_sh != g_s4272_shadow;
    if (d) { if (control) ++ctl; else ++bad; }
    else if (n == 1 && !control) { /* nothing to corrupt yet: retry the control next check */ n = 0; }
    {   // duplicate (lo,hi) shadow keys in the per-bump list: the wrap restore's first-match lookup is the one place grouping could matter
        std::vector<uint64_t> k; k.reserve(g_bc_sh.size());
        for (const S4272Sh &e : g_bc_sh) k.push_back(((uint64_t)e.lo << 32) | e.hi);
        std::sort(k.begin(), k.end());
        for (size_t i = 1; i < k.size(); ++i) if (k[i] == k[i - 1]) ++dup;
    }
    if (n <= 4 || (n & 0x3FF) == 0)
        fprintf(stderr, "[s6955-bc] n=%lu where=%s bad=%lu control(must be 1)=%lu dupkeys=%lu ref_ranges=%lu batch_ranges=%lu\n",
                n, where, bad, ctl, dup, refr, batr);
}
static void rs64_g1e_bc_clear() { g_bc_ranges.clear(); g_bc_sh.clear(); g_bc_shadow.clear(); }

#include "librecomp/rsp.hpp"
#include "ultramodern/events.hpp"
extern "C" int rs64_s6932_quiet(void);

// Direct RT64 entry — the upstream librecomp doesn't expose
// `ultramodern::submit_rdp_range` (that was a fork addition). Bypass the
// runtime layer entirely: shim through rs64_get_rt64_app() and call
// processDisplayLists(isHLE=false). Defined in src/main/rt64_render_context.cpp.
namespace RT64 { class Application; }
extern "C" RT64::Application* rs64_get_rt64_app();
extern "C" int rs64_rdpq_task_async(); // s6705 rt64_render_context.cpp
extern "C" uint32_t rs64_rdpq_task_stream(); // s6707: bytes per streamed flush for this task, 0 = commit at task end
namespace ultramodern {
    void submit_rdp_range(uint32_t lo_phys, uint32_t hi_phys);
}

uint32_t g_rsp_dpc_start = 0;
uint32_t g_rsp_dpc_end   = 0;
uint32_t g_rsp_dpc_current = 0;

// DPC_CURRENT read with a bounded-poll escape. Our RDP consumes instantly,
// so any ucode wait of the form "spin until CURRENT != X" must terminate.
// When the attribution ring wraps exactly onto the previous END, CURRENT ==
// new head forever and the ucode's L_115C overwrite-safety wait deadlocks
// (task #4 hang). After 64 identical polls with no intervening DPC write,
// report one 8-byte step of "consumption progress" for that poll only.
static uint32_t s_dpc_poll_last = 0xFFFFFFFFu;
static int s_dpc_poll_repeats = 0;

// Ring high-water mark used by rsp_dpc_submit to avoid re-forwarding bytes the
// RDP has already seen as the ucode bumps DPC_END command by command. This is a
// WITHIN-TASK guard only: every task restarts its ring writes from its own
// DPC_START, so the mark must be cleared per task (rs64_dpc_reset). Leaving it
// set across tasks silently swallowed every task whose output was no larger
// than the largest previous task's — 64 of 66 tasks emitted "0 bytes" that way.
static uint32_t s_submit_dl_base = 0;
static uint32_t s_submit_last_end = 0;
// s4284: per-commit ring-lap census (END < seen). Reset at each deferred commit.
static uint32_t s_c4284_laps = 0, s_c4284_first_lo = 0, s_c4284_first_hi = 0, s_c4284_start = 0, s_c4284_maxseen = 0;

// Task-local committed output bounds. These are reset before each deferred
// task and populated only when a range is accepted for RT64 submission.
static uint32_t s_task_first_lo = 0;
static uint32_t s_task_first_hi = 0;
static uint32_t s_task_last_lo = 0;
static uint32_t s_task_last_hi = 0;
static uint32_t s_task_min_lo = 0xFFFFFFFFu;
static uint32_t s_task_max_hi = 0;

// Reset all cross-task DPC emulation state. The ucode's boot/entry takes
// resume-vs-fresh branches based on DPC registers; state leaking from the
// previous task steers ~1/5 tasks into a resume path that loads the trig
// segment over the DL staging area (2026-07-13 canary bisect).
extern "C" int rs64_s7095_on; extern "C" void rs64_s7095_task(); extern "C" void rs64_s7095_cur_read(uint32_t ours, int escaped);
// s7096: forwarding coverage (src/rsp/s7096_fwd_cover.cpp). Sites: 0 live 1 merged 2 wrap 3 commit 4 synth 5 forcefs;
// drops: 0 pipe 1 synthrep 2 cimg 3 oob 4 wrapdrop 5 noflush 6 eqlast 7 uj.
extern "C" int rs64_s7096_on; extern "C" void rs64_s7096_task(); extern "C" void rs64_s7096_fwd(uint32_t lo, uint32_t hi, int site);
extern "C" void rs64_s7096_drop(uint32_t lo, uint32_t hi, int why);
#define RS64_S7096_DROP(lo, hi, why) do { if (rs64_s7096_on) rs64_s7096_drop((lo), (hi), (why)); } while (0)
extern "C" int rs64_s7523_on; extern "C" void rs64_s7523_task(); extern "C" uint32_t rs64_s7523_cur_read();  // s7523 class FT
extern "C" void rs64_dpc_reset() {
    if (rs64_s7523_on) rs64_s7523_task();
    if (rs64_s7095_on) rs64_s7095_task();
    if (rs64_s7096_on) rs64_s7096_task();
    g_rsp_dpc_start = 0;
    g_rsp_dpc_end = 0;
    g_rsp_dpc_current = 0;
    s_dpc_poll_last = 0xFFFFFFFFu;
    s_dpc_poll_repeats = 0;
    s_submit_dl_base = 0;
    s_submit_last_end = 0;
}

extern "C" int rs64_s7521_force_cur(); extern "C" void rs64_s7521_l1db0(int ev);  // s7521 class FR (src/rsp/s7521_ucode_watch.cpp)
uint32_t rs64_dpc_current_read() {
    uint32_t& s_last = s_dpc_poll_last;
    int& s_repeats = s_dpc_poll_repeats;
    if (__builtin_expect(rs64_s7523_on, 0)) return rs64_s7523_cur_read();  // s7523: finite-rate RDP model
    uint32_t v = g_rsp_dpc_current;
    if (rs64_s7521_force_cur()) return v + 8;  // s7521 ctl: one forced busy read inside L_1DB0
    if (v == s_last) {
        if (++s_repeats >= 64) {
            s_repeats = 0;
            if (rs64_s7095_on) rs64_s7095_cur_read(v, 1);
            return v + 8;
        }
    } else {
        s_last = v;
        s_repeats = 0;
    }
    if (rs64_s7095_on) rs64_s7095_cur_read(v, 0);
    return v;
}

// Set when an RDP FULL_SYNC (op 0x29) is observed in a submission. The
// factor5_ucode dispatch loop polls this and force-returns Broke so
// task_thread_func can fire sp_complete() and the CPU's GFX_SCHED can
// advance to the next task. Without this, the LLE ucode runs forever
// (the original game halts the RSP externally between frames; we don't
// model that).
std::atomic<bool> g_rsp_full_sync_seen{false};

// RDRAM-relative address of the most recent real FULL_SYNC byte (op 0x29)
// the bridge forwarded. rsp_force_fullsync() re-submits those 8 bytes via
// ultramodern::submit_rdp_range so RT64 sees a fullSync at task-end. Paired
// with the LoadOperation validity check in rt64_state.cpp:fullSyncFramebufferPairTiles
// — without that check, mid-frame fullSync crashes in loadTileOperation.
static std::atomic<uint32_t> g_last_fullsync_addr{0xFFFFFFFFu};

// Per-task RDP byte / command counters. The ucode resets these via
// rsp_task_log_and_reset() at the synthetic-halt site so we get a per-task
// chunk-size distribution.
static std::atomic<uint32_t> g_task_rdp_bytes{0};
extern "C" std::atomic<uint64_t> rs64_g1e_rdp_bytes; // s6982, defined in ultramodern events.cpp
static std::atomic<uint32_t> g_task_rdp_cmds{0};
static std::atomic<uint32_t> g_task_rdp_fullsyncs{0};
// Per-task RDP opcode histogram (low 6 bits of first byte = op). Bridge and
// task_log_and_reset both run on the RSP task thread, so plain array is fine.
static uint32_t g_task_op_count[64] = {0};

struct Rs64E9Provenance {
    struct M4NormRow {
        uint32_t phase;
        uint32_t image;
        uint32_t pc;
        uint32_t steps;
        uint32_t total;
        uint32_t lanes[24];
    };
    uint32_t root_dl = 0;
    struct Condition {
        uint32_t address;
        uint64_t serial;
        uint32_t lo;
        uint32_t hi;
        uint32_t kind;
    };
    struct FrameEvent {
        uint32_t kind;
        uint32_t id;
        uint32_t slot;
        uint32_t target;
        uint32_t pc;
        uint32_t caller;
        uint32_t w0;
        uint32_t w1;
        uint32_t source;
    };
    struct FrameDepth {
        uint32_t push = 0;
        uint32_t pop = 0;
        uint32_t resume = 0;
        uint32_t reuse_push = 0;
        uint32_t pop_without_push = 0;
        uint32_t resume_without_pop = 0;
        bool active = false;
        bool pending_resume = false;
    };
    struct ResetReusePair {
        uint32_t reset_seq;
        uint32_t reset_old;
        uint32_t reset_r17;
        uint32_t reuse_seq;
        uint32_t reuse_r17;
    };
    struct ResetRoute {
        uint32_t seq;
        uint32_t old;
        uint32_t r17;
        uint32_t ra;
        uint32_t resident;
        uint32_t pending_source;
        uint32_t pending_r17;
        uint32_t pending_w0;
        uint32_t pending_w1;
        uint32_t inline_active;
        uint32_t inline_opcode;
        uint32_t inline_entry;
        uint32_t inline_table_kind;
        uint32_t inline_table_word;
        uint32_t predecessor_target;
        uint32_t predecessor_line;
        uint32_t predecessor_ra;
        uint32_t predecessor_resident;
        uint32_t predecessor_r17;
        uint32_t predecessor_from_l1298;
    };
    uint32_t task = 0;
    uint32_t m4_image = 0;
    uint32_t m4_y8000_step = 0;
    uint32_t m4_norm_phase = 0xFFFFFFFFu;
    uint32_t m4_norm_phase_rows = 0;
    uint32_t m4_norm_phase_dropped = 0;
    std::vector<M4NormRow> m4_norm_rows;
    uint32_t guest = 0;
    uint32_t emitted = 0;
    uint32_t submitted = 0;
    uint32_t authoritative = 0;
    uint32_t handler = 0;
    uint32_t dispatched = 0;
    uint32_t matched = 0;
    uint32_t aligned = 0;
    uint32_t aligned_dl = 0xFFFFFFFFu;
    uint32_t source_fetch = 0;
    uint32_t source_e9 = 0;
    uint32_t source_end = 0;
    uint32_t source_end_addr = 0xFFFFFFFFu;
    uint32_t source_end_kind = 0;
    uint32_t unwind = 0;
    uint32_t unwind_natural = 0;
    uint32_t unwind_last = 0;
    uint32_t frame_push = 0;
    uint32_t frame_pop = 0;
    uint32_t frame_resume = 0;
    uint32_t frame_zero_resume = 0;
    uint32_t frame_min_slot = 0xFFFFFFFFu;
    uint32_t frame_max_slot = 0;
    uint32_t frame_resume_mismatch = 0;
    uint32_t frame_next_id = 0;
    uint32_t frame_06_push = 0;
    uint32_t frame_06_complete = 0;
    uint32_t l12a0_direct = 0;
    uint32_t l12a0_overlay = 0;
    uint32_t lifecycle_seq = 0;
    uint32_t l1db0_reset = 0;
    uint32_t l1db0_reset_active = 0;
    uint32_t l1db0_reset_last_active_seq = 0;
    uint32_t l1db0_reset_last_active_old = 0;
    uint32_t l1db0_reset_last_active_r17 = 0;
    uint32_t depth0_reuse_unpaired = 0;
    uint32_t l1db0_predecessor = 0;
    uint32_t l1db0_predecessor_target = 0;
    uint32_t l1db0_predecessor_line = 0;
    uint32_t l1db0_predecessor_ra = 0;
    uint32_t l1db0_predecessor_resident = 0;
    uint32_t l1db0_predecessor_r17 = 0;
    uint32_t l1db0_predecessor_from_l1298 = 0;
    uint32_t clip_route = 0;
    uint32_t ovl12_route = 0;
    uint32_t ovl12_ret = 0;
    uint32_t ovl24_route = 0;
    uint32_t ovl24_ret = 0;
    uint32_t ovl28_route = 0;
    uint32_t ovl14_route = 0;
    uint32_t ovl14_ret = 0;
    uint32_t ovl18_route = 0;
    uint32_t ovl10_route = 0;
    uint32_t ovl1c_route = 0;
    uint32_t ovl2c_route = 0;
    uint32_t l1298_12a0_res24 = 0;
    uint32_t l1298_12a0_other = 0;
    uint32_t last_ovl_res = 0;
    uint32_t last_ovl_tgt = 0;
    uint32_t j1364 = 0;
    uint32_t j1364_res04 = 0;
    uint32_t j1364_res24 = 0;
    uint32_t j1364_other = 0;
    uint32_t ovl24_jal17f0 = 0;
    uint32_t clip_1e48 = 0;
    uint32_t clip_1e48_1364 = 0;
    uint32_t j1364_line = 0;
    uint32_t j1364_r31 = 0;
    uint32_t j1364_r30 = 0;
    uint32_t j1364_res = 0;
    uint32_t j1364_ovl_res = 0;
    uint32_t j1364_ovl_tgt = 0;
    std::vector<ResetReusePair> reset_reuse_first;
    std::vector<ResetReusePair> reset_reuse_last;
    std::vector<ResetRoute> reset_route_first;
    std::vector<ResetRoute> reset_route_last;
    std::unordered_map<uint32_t, uint32_t> frame_id_by_slot;
    std::unordered_map<uint32_t, uint32_t> frame_opcode_by_slot;
    std::vector<FrameDepth> frame_depths;
    uint32_t source_first = 0xFFFFFFFFu;
    uint32_t source_last = 0xFFFFFFFFu;
    uint32_t trigen_sample = 0xFFFFFFFFu;
    bool trigen_pair_open = false;
    bool target = false;
    bool control = false;
    std::vector<uint32_t> emitted_addrs;
    uint32_t first_guest = 0xFFFFFFFFu;
    uint32_t first_emit = 0xFFFFFFFFu;
    uint32_t first_authoritative = 0xFFFFFFFFu;
    uint32_t first_match = 0xFFFFFFFFu;
    std::vector<uint32_t> fetched_addrs;
    std::vector<uint32_t> spanned_addrs;
    std::vector<Condition> conditions;
    uint32_t condition_direct = 0;
    uint32_t condition_span = 0;
    uint32_t condition_pending = 0;
    uint32_t condition_extended = 0;
    uint32_t condition_unassociated = 0;
    uint32_t non_e9_spans = 0;
    uint32_t uncovered = 0;
    std::vector<FrameEvent> frame_first;
    std::vector<FrameEvent> frame_last;
    std::vector<FrameEvent> frame_slot_first;
    FrameEvent frame_slot8_first{};
    FrameEvent frame_slot8_last{};
    bool frame_slot8_seen = false;
    FrameEvent frame_reentry_slot0_first{};
    FrameEvent frame_reentry_slot0_last{};
    bool frame_reentry_slot0_seen = false;
    uint32_t pending_pop_slot = 0xFFFFFFFFu;
    uint32_t pending_pop_pc = 0xFFFFFFFFu;
    uint32_t pending_l12a0_source = 0;
    uint32_t pending_l12a0_r17 = 0;
    uint32_t pending_l12a0_w0 = 0;
    uint32_t pending_l12a0_w1 = 0;
};
static Rs64E9Provenance g_e9prov;
static std::atomic<uint32_t> g_e9prov_latch_remaining{0};
static std::atomic<uint32_t> g_e9prov_join_lines{0};
static std::atomic<uint32_t> g_e9prov_nonzero_callback_lines{0};
static std::atomic<uint32_t> g_task_bridge_e9{0};
static std::atomic<uint32_t> g_task_synthetic_fullsyncs{0};
static std::atomic<bool> g_synthetic_consumer_pending{false};
static std::atomic<uint64_t> g_synthetic_submit_serial{0};
static uint32_t g_e9_boundary_lines = 0;
static uint8_t *g_rdram_for_submit = nullptr;
// s6690: submit-range scanners that WRITE rdram must use the full guest RAM size, not 8 MB.
// ROGUESQ_OSMEM_MB (21:9 sets 12) and RT64 allow up to 16 MB; the old 0x7FFFFC mask folded
// RDP commands at 0x892800+ onto 0x092800+ and the spike cull zeroed hangar overlay data.
static constexpr uint32_t kSubmitRamMask = 0xFFFFFCu;
static constexpr uint32_t kSubmitRamEnd = 0x1000000u;

static bool log_e9_unified();
static bool log_e9_boundary();
static bool log_tri_writer();
extern "C" uint32_t rs64_rdp_advance_task_e9();
extern "C" uint32_t rs64_rdp_advance_epoch();
extern "C" uint64_t rs64_rdp_advance_join_order();
extern "C" uint64_t rs64_rdp_advance_reset_order();
extern "C" uint64_t rs64_rdp_advance_first_consumer_order();
extern "C" uint32_t rs64_rdp_advance_first_consumer_address();
extern "C" uint32_t rs64_e9prov_current_root_dl();

static void rs64_count_submitted_e9(uint32_t lo, uint32_t hi) {
    if (!log_e9_unified() || g_rdram_for_submit == nullptr) return;
    uint32_t count = 0;
    for (uint32_t p = lo; p + 8 <= hi; p += 8) {
        if (g_rdram_for_submit[p ^ 3] == 0xE9) ++count;
    }
    if (count != 0) g_task_bridge_e9.fetch_add(count, std::memory_order_relaxed);
}

struct Rs64InlineProbe {
    bool active = false;
    uint32_t opcode = 0;
    uint32_t entry = 0;
    uint32_t table_kind = 0;
    uint32_t table_word = 0;
    uint32_t expected_extra = 0;
    uint32_t samples[7] = {};
    uint32_t mismatch[7] = {};
    uint32_t incomplete = 0;
};
static Rs64InlineProbe g_inline_probe;
static std::atomic<uint32_t> g_inline_probe_lines{0};
static std::atomic<uint32_t> g_inline_probe_route_lines{0};
static std::atomic<uint32_t> g_inline_probe_trigen_entry_lines{0};
static std::atomic<uint32_t> g_inline_probe_trigen_reload_lines{0};
static std::atomic<uint32_t> g_inline_probe_trigen_exit_lines[5];
static std::atomic<uint32_t> g_inline_probe_trigen_source_lines{0};
static std::atomic<uint32_t> g_inline_probe_trigen_chunk_lines{0};
static std::atomic<uint32_t> g_inline_probe_trigen_pairs{0};
static std::atomic<uint32_t> g_inline_probe_trigen_boot_lines{0};
static std::atomic<uint32_t> g_inline_probe_summaries{0};
static std::atomic<uint32_t> g_inline_probe_phase{0xFFFFFFFFu};
extern "C" uint32_t rs64_phase_ord(void);
extern "C" { extern thread_local uint32_t rs64_spk_dma_ring[256][3]; extern thread_local uint32_t rs64_spk_dma_n, rs64_spk_cov43a, rs64_spk_cov462, rs64_spk_ctl; } // s7366: per RSP thread (rsp.cpp)

static bool log_inline_advance() {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_INLINE_ADVANCE");
        return e && *e && *e != '0';
    }();
    return enabled;
}

static uint32_t inline_probe_slot(uint32_t opcode) {
    switch (opcode) {
    case 0x03: return 1;
    case 0x05: return 2;
    case 0xB4: case 0xBF: return 3;
    case 0xBD: return 4;
    case 0xBE: return 5;
    case 0xB3: return 6;
    default: return 0;
    }
}


// s4735 DL-walk jump trace (ROGUESQ_DLWALK=1): record every non-sequential fetch
// and every DL call/return so a runaway task's backward jump can be attributed.
struct DlWalkTrace {
    struct Ev { uint32_t kind, a, b, c, n; };  // 1 nonseq-fetch(prev,addr,prevop) 2 push 3 pop
    uint32_t task = 0, fetches = 0, nonseq = 0, back = 0, prev = 0xFFFFFFFFu, prev_op = 0;
    uint32_t n2c = 0, njmp = 0, nbd = 0;  // s4747: 0x1DB0 arrivals with d153==0x2C / all jump arrivals
    std::vector<Ev> ev;
    // s4738: ring of the last 8 do_indirect_jump arrivals; snapshots at 0x30(r18) site-3 stores.
    struct Jmp { uint32_t target, r31, line, d153, prev_op, n; };
    Jmp ring[8] = {}; uint32_t ring_n = 0;
    Jmp snap_first[8] = {}, snap_last[8] = {}; uint32_t nsnap = 0;
};
static DlWalkTrace g_dlw;
static bool dlwalk_on() {
    static const bool on = [] { const char *e = std::getenv("ROGUESQ_DLWALK"); return e && *e && *e != '0'; }();
    return on;
}
static void dlw_event(uint32_t kind, uint32_t a, uint32_t b, uint32_t c) {
    if (g_dlw.ev.size() < 6000) g_dlw.ev.push_back({kind, a, b, c, g_dlw.fetches});
}

static bool log_e9_provenance() {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_E9_PROVENANCE");
        return e && *e && *e != '0';
    }();
    return enabled;
}

static bool log_e9_unified() {
    static const bool enabled = [] {
        const char *all = std::getenv("ROGUESQ_LOG_ALL");
        const char *e = std::getenv("ROGUESQ_LOG_RDP_ADVANCE");
        const char *u = std::getenv("ROGUESQ_LOG_E9_UNIFIED");
        return (all && *all && *all != '0') ||
               (e && *e && *e != '0') || (u && *u && *u != '0');
    }();
    return enabled;
}

static bool log_e9_boundary() {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_E9_BOUNDARY");
        return e && *e && *e != '0';
    }();
    return enabled;
}

static bool log_tri_writer() {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_TRI_WRITER");
        return e && *e && *e != '0';
    }();
    return enabled;
}

extern "C" void rs64_m4_accum_probe(void *opaque, uint32_t stage,
                                     uint32_t guest_pc, uint32_t r9,
                                     const uint8_t *rdram) {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_M4_ACCUM");
        return e && *e && *e != '0';
    }();
    if (!enabled) return;
    static const uint32_t control_cap = [] {
        const char *e = std::getenv("ROGUESQ_M4_CONTROL_CAP");
        return e && *e ? static_cast<uint32_t>(std::strtoul(e, nullptr, 10)) : 64u;
    }();
    static const uint32_t target_cap = [] {
        const char *e = std::getenv("ROGUESQ_M4_TARGET_CAP");
        return e && *e ? static_cast<uint32_t>(std::strtoul(e, nullptr, 10)) : 2048u;
    }();
    static const uint32_t phase_from = [] {
        const char *e = std::getenv("ROGUESQ_M4_PHASE_FROM");
        return e && *e ? static_cast<uint32_t>(std::strtoul(e, nullptr, 10)) : 0u;
    }();
    if (stage != 1 && rs64_phase_ord() < phase_from) return;
    static uint32_t control_lines = 0;
    static uint32_t target_lines = 0;
    uint32_t *lines = stage == 1 ? &control_lines : &target_lines;
    const uint32_t cap = stage == 1 ? control_cap : target_cap;
    if ((*lines)++ >= cap) return;
    auto *rsp = static_cast<RSP *>(opaque);
    static uint16_t pre_v6[8];
    static uint16_t post_vge[8];
    if (stage == 10) {
        for (unsigned lane = 0; lane < 8; ++lane) pre_v6[lane] = rsp->vpu.r[6].u16(lane);
    } else if (stage == 12) {
        for (unsigned lane = 0; lane < 8; ++lane) post_vge[lane] = rsp->vpu.r[6].u16(lane);
    }
    fprintf(stderr, "[m4-accum] task=%u phase=%u stage=%u pc=0x%04X r9=0x%08X", g_e9prov.task,
            rs64_phase_ord(), stage, guest_pc, r9);
    for (unsigned lane = 0; lane < 8; ++lane) {
        fprintf(stderr, " l%u:v4=%04X v0=%04X v6=%04X pre=%04X vge=%04X v29=%04X acch=%04X accm=%04X accl=%04X",
                lane, rsp->vpu.r[4].u16(lane), rsp->vpu.r[0].u16(lane),
                rsp->vpu.r[6].u16(lane), pre_v6[lane], post_vge[lane], rsp->vpu.r[29].u16(lane),
                rsp->vpu.acch.u16(lane), rsp->vpu.accm.u16(lane),
                rsp->vpu.accl.u16(lane));
    }
    if (stage == 13) {
        const uint32_t base = r9 & 0xFFFu;
        fprintf(stderr, " record=");
        for (uint32_t i = 0; i < 0x38; ++i) {
            const uint32_t address = (base + 0x18u + i) & 0xFFFu;
            fprintf(stderr, "%02X", (unsigned)g_dmem_cur[address ^ 3u]);
        }
    }
    fputc('\n', stderr);
    fflush(stderr);
}

// s5005: one line per main-ucode gfx task exit with the 24 accumulator lanes'
// summary, comparable with the cxd4 RSD1 end-of-task VACC dump (s5003/s5004).
// kind: 1 = natural EndDL exit, 2 = 16384-iteration cap exit.
static bool rs64_m4_norm_enabled() {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_M4_NORM");
        return e && *e && *e != '0';
    }();
    return enabled;
}

static bool rs64_m4_y8000_in_gate();
extern "C" uint32_t rs64_vi_committed_width();
extern "C" uint32_t rs64_vi_committed_origin();

extern "C" void rs64_m4_norm_sample(void *opaque, uint32_t guest_pc, uint32_t steps,
                                     const uint8_t *rdram) {
    if (!rs64_m4_norm_enabled()) return;
    static const bool port_control = [] {
        const char *e = std::getenv("ROGUESQ_LOG_M4_PORT_RDRAM");
        return e && *e && *e != '0';
    }();
    static bool control_done = false;
    if (port_control && !control_done) {
        control_done = true;
        uint32_t nonzero = 0;
        if (rdram != nullptr) {
            for (uint32_t i = 0; i < 0x800000u; ++i) nonzero += rdram[i] != 0;
            fprintf(stderr, "[m4-port-rdram-control] bytes=0x800000 nonzero=%u\n", nonzero);
        } else {
            fprintf(stderr, "[m4-port-rdram-control] bytes=0x800000 unavailable=1\n");
        }
        fflush(stderr);
    }
    auto *rsp = static_cast<RSP *>(opaque);
    Rs64E9Provenance::M4NormRow row{};
    row.phase = rs64_phase_ord();
    if (row.phase != g_e9prov.m4_norm_phase) {
        g_e9prov.m4_norm_phase = row.phase;
        g_e9prov.m4_norm_phase_rows = 0;
        g_e9prov.m4_norm_phase_dropped = 0;
    }
    if (g_e9prov.m4_norm_phase_rows >= 4096) {
        ++g_e9prov.m4_norm_phase_dropped;
        return;
    }
    ++g_e9prov.m4_norm_phase_rows;
    row.image = g_e9prov.m4_image;
    row.pc = guest_pc;
    row.steps = steps;
    row.total = 0;
    for (unsigned lane = 0; lane < 8; ++lane) {
        row.lanes[lane] = rsp->vpu.acch.u16(lane);
        row.lanes[8 + lane] = rsp->vpu.accm.u16(lane);
        row.lanes[16 + lane] = rsp->vpu.accl.u16(lane);
    }
    g_e9prov.m4_norm_rows.push_back(row);
}

extern "C" void rs64_m4_end_probe(void *opaque, uint32_t kind, uint32_t total) {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_M4_END");
        return e && *e && *e != '0';
    }();
    if (!enabled && !rs64_m4_norm_enabled()) return;
    auto *rsp = static_cast<RSP *>(opaque);
    unsigned sat = 0, nz = 0;
    for (unsigned lane = 0; lane < 8; ++lane) {
        const uint16_t v[3] = {rsp->vpu.acch.u16(lane), rsp->vpu.accm.u16(lane), rsp->vpu.accl.u16(lane)};
        for (unsigned i = 0; i < 3; ++i) { sat += v[i] == 0x8000u; nz += v[i] != 0; }
    }
    if (rs64_m4_norm_enabled()) {
        for (const auto &row : g_e9prov.m4_norm_rows) {
            const uint32_t row_total = total;
            fprintf(stderr, "[m4-norm] phase=%u viw=%u origin=0x%06X image=0x%08X pc=0x%04X steps=%u total=%u progress=%u end=%u lanes=",
                    row.phase, rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu,
                    row.image, row.pc,
                    row.steps, row_total,
                    row_total ? (row.steps * 1000u) / row_total : 0u,
                    sat ? 1u : 0u);
            bool first = true;
            for (unsigned i = 0; i < 24; ++i) {
                if ((row.lanes[i] & 0xFFFFu) != 0x8000u) continue;
                if (!first) fputc(',', stderr);
                fprintf(stderr, "%u", i);
                first = false;
            }
            if (first) fputc('-', stderr);
            fprintf(stderr, " task=%u\n", g_e9prov.task);
        }
        if (g_e9prov.m4_norm_phase_dropped) {
            fprintf(stderr, "[m4-norm-cap] phase=%u dropped=%u cap=4096\n",
                    g_e9prov.m4_norm_phase, g_e9prov.m4_norm_phase_dropped);
        }
        g_e9prov.m4_norm_rows.clear();
    }
    if (!enabled) return;
    fprintf(stderr, "[m4-end] task=%u phase=%u kind=%u sat8000=%u nz=%u", g_e9prov.task,
            rs64_phase_ord(), kind, sat, nz);
    if (sat) {
        for (unsigned lane = 0; lane < 8; ++lane)
            fprintf(stderr, " l%u:%04X.%04X.%04X", lane, rsp->vpu.acch.u16(lane),
                    rsp->vpu.accm.u16(lane), rsp->vpu.accl.u16(lane));
    }
    fputc('\n', stderr);
    fflush(stderr);
}

static bool m4_src_enabled(uint32_t *cap_out) {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_M4_ACCUM");
        return e && *e && *e != '0';
    }();
    static const uint32_t cap = [] {
        const char *e = std::getenv("ROGUESQ_M4_SRC_CAP");
        return e && *e ? static_cast<uint32_t>(std::strtoul(e, nullptr, 10)) : 4096u;
    }();
    static const uint32_t phase_from = [] {
        const char *e = std::getenv("ROGUESQ_M4_PHASE_FROM");
        return e && *e ? static_cast<uint32_t>(std::strtoul(e, nullptr, 10)) : 0u;
    }();
    *cap_out = cap;
    return enabled && rs64_phase_ord() >= phase_from;
}

// s4630: every ucode SP DMA read in the M4 phase (dmem/dram/len), so the
// RDRAM source of the vertex/matrix blocks can be compared with retail.
extern "C" uint32_t rs64_ram_top;
extern "C" void rs64_m4_dma_probe(uint32_t mem, uint32_t dram, uint32_t len) {
    {   // s6328 G3c: ROGUESQ_G3C_DMALOG=period,count : log ucode DMA reads with (i %% period) < count with first 16 source bytes
        static uint32_t skip = 0, cnt = 0; static int init = 0; static uint32_t idx = 0;
        if (!init) { init = 1; const char *e = std::getenv("ROGUESQ_G3C_DMALOG"); if (e && *e) { unsigned a = 0, b = 0; if (sscanf(e, "%u,%u", &a, &b) == 2 && a) { skip = a; cnt = b; } } }
        if (cnt && g_rdram_for_submit != nullptr) {
            uint32_t i = idx++;
            if ((i % skip) < cnt) {
                uint32_t ph = dram & 0x00FFFFFFu; uint8_t b[16];
                for (uint32_t q = 0; q < 16; ++q) b[q] = g_rdram_for_submit[(ph + q) ^ 3u];
                fprintf(stderr, "[g3cdma] i=%u mem=%04X dram=%08X len=%u :", i, mem, dram, len);
                for (uint32_t q = 0; q < 16; ++q) fprintf(stderr, " %02X", b[q]);
                fputc('\n', stderr);
            }
        }
    }
    static const bool g1d_reads = [] {
        const char *e = std::getenv("ROGUESQ_LOG_G1D_READS");
        return e && *e && *e != '0';
    }();
    if (g1d_reads && rs64_phase_ord() >= 4u && g_rdram_for_submit != nullptr) {
        static uint32_t phase_key = 0xFFFFFFFFu;
        static uint32_t rows = 0;
        static uint32_t hits = 0;
        static uint32_t prefix_hits = 0;
        static uint32_t slot_hits = 0;
        static uint32_t scans = 0;
        static uint32_t win_at[2] = {};
        static int win_n = 0;
        static uint32_t ch_dram[4] = {};
        static int ch_idx[4] = {};
        static int ch_n = 0;
        const uint32_t phase = rs64_phase_ord();
        if (phase != phase_key) {
            phase_key = phase;
            rows = 0;
            hits = 0;
            prefix_hits = 0;
            slot_hits = 0;
            scans = 0;
            ch_n = 0;
        }
        const uint32_t phys = dram & 0x00FFFFFFu;
        // s6208: the per-DMA hash line is not emitted. s6195 showed it is
        // thousands of rows and it buries the texture-address slot.
        {
            const uint32_t ram_bytes = rs64_ram_top > 0x80000000u
                ? (rs64_ram_top - 0x80000000u) : 0u;
            // s6211: one line when a phase-4 DMA overlaps control chunk 72
            // (positive control) or wide chunks 151..156. Not a hash stream.
            if (phase == 4u && ch_n < 4 && len > 0u) {
                uint32_t pool = 0;
                if (0x1163ECu <= ram_bytes) {
                    for (uint32_t b = 0; b < 4u; ++b)
                        pool = (pool << 8) | g_rdram_for_submit[(0x1163E8u + b) ^ 3u];
                }
                const bool ctl_pool = pool == 0x80B25000u;
                const bool wide_pool = pool == 0x80AE6E00u;
                if (ctl_pool || wide_pool) {
                    const uint32_t watch0 = ctl_pool ? 72u : 151u;
                    const uint32_t watch_n = ctl_pool ? 1u : 6u;
                    const uint32_t pool_phys = pool & 0x00FFFFFFu;
                    const uint32_t watch_lo = pool_phys + watch0 * 0x108u;
                    const uint32_t watch_hi = watch_lo + watch_n * 0x108u;
                    const uint32_t dma_hi = phys + len;
                    if (phys < watch_hi && dma_hi > watch_lo && dma_hi >= phys) {
                        uint32_t cursor = phys > watch_lo ? phys : watch_lo;
                        const uint32_t ov_end = dma_hi < watch_hi ? dma_hi : watch_hi;
                        while (cursor < ov_end && ch_n < 4) {
                            const uint32_t rel = cursor - pool_phys;
                            const int idx = static_cast<int>(rel / 0x108u);
                            const uint32_t chunk_phys = pool_phys + static_cast<uint32_t>(idx) * 0x108u;
                            const uint32_t next_phys = chunk_phys + 0x108u;
                            bool seen = false;
                            for (int i = 0; i < ch_n; ++i)
                                seen = seen || (ch_idx[i] == idx && ch_dram[i] == dram);
                            if (!seen && idx >= static_cast<int>(watch0) &&
                                idx < static_cast<int>(watch0 + watch_n)) {
                                const uint32_t piece_lo = cursor > chunk_phys ? cursor : chunk_phys;
                                const uint32_t piece_hi = ov_end < next_phys ? ov_end : next_phys;
                                ch_idx[ch_n] = idx;
                                ch_dram[ch_n] = dram;
                                ++ch_n;
                                char words[12 * 8];
                                words[0] = 0;
                                if (chunk_phys + 0x20u <= ram_bytes) {
                                    size_t n = 0;
                                    for (uint32_t i = 0; i < 8u; ++i) {
                                        uint32_t w = 0;
                                        for (uint32_t b = 0; b < 4u; ++b)
                                            w = (w << 8) |
                                                g_rdram_for_submit[(chunk_phys + i * 4u + b) ^ 3u];
                                        n += static_cast<size_t>(std::snprintf(
                                            words + n, sizeof(words) - n, "%s%08X",
                                            i ? "," : "", w));
                                    }
                                }
                                std::fprintf(stderr,
                                    "[g1d-ch] arm=%s pool=0x%08X idx=%d dram=0x%08X len=0x%X "
                                    "ov=0x%X guest_pc=0x%08X words=%s\n",
                                    ctl_pool ? "ctl" : "wide", pool, idx, dram, len,
                                    piece_hi - piece_lo, (unsigned)g_rs64_last_guest_pc, words);
                                std::fflush(stderr);
                            }
                            cursor = next_phys;
                        }
                    }
                }
            }
            uint32_t scan_n = len > 0x1000u ? 0x1000u : len;
            if (phys >= ram_bytes) scan_n = 0;
            else if (scan_n > ram_bytes - phys) scan_n = ram_bytes - phys;
            const uint32_t root = rs64_e9prov_current_root_dl() & 0x007FFFFFu;
            const bool dram_in_node = root != 0u && phys >= root && phys < root + 0x200u;
            const bool dram_in_glob = phys >= 0x00116000u && phys < 0x00117000u;
            auto emit_hit = [&](uint32_t off, uint32_t word, const char *why) {
                const uint32_t word_phys = phys + off;
                const bool word_in_node = root != 0u && word_phys >= root &&
                    word_phys + 4u <= root + 0x200u;
                const int node_off = word_in_node ? static_cast<int>(word_phys - root) : -1;
                std::fprintf(stderr,
                    "[g1d-ptr] phase=%u why=%s dram=0x%08X off=0x%X word=0x%08X "
                    "guest_pc=0x%08X in_node=%u node_off=%d root=0x%06X mem=0x%04X len=0x%X\n",
                    phase, why, dram, off, word, (unsigned)g_rs64_last_guest_pc,
                    dram_in_node ? 1u : 0u, node_off, root, mem, len);
                std::fflush(stderr);
            };
            if (scan_n >= 4u) {
                ++scans;
                if ((scans % 512u) == 1u && scans <= 4097u) {
                    std::fprintf(stderr,
                        "[g1d-ptr-sum] phase=%u scans=%u hits=%u prefix=%u slot=%u\n",
                        phase, scans, hits, prefix_hits, slot_hits);
                    std::fflush(stderr);
                }
                bool logged_span = false;
                for (uint32_t off = 0; off + 4u <= scan_n; off += 4u) {
                    uint32_t word = 0;
                    for (uint32_t b = 0; b < 4u; ++b)
                        word = (word << 8) | g_rdram_for_submit[(phys + off + b) ^ 3u];
                    const uint32_t low = word & 0x00FFFFFFu;
                    if (low < 0x00A6A000u || low >= 0x00B00000u) continue;
                    const uint32_t top = word >> 24;
                    if (top != 0x00u && top != 0x80u) continue;
                    const bool exact = low == 0x00A6AA10u || low == 0x00AE6120u ||
                        low == 0x00AE5520u || low == 0x00AE5320u || low == 0x00AE5120u;
                    const bool stride = !exact && low >= 0x00A6AA10u &&
                        ((low - 0x00A6AA10u) & 0xFFFu) == 0u;
                    if (exact || stride) {
                        const uint32_t at = phys + off;
                        const uint32_t at_k = 0x80000000u | at;
                        bool win_seen = false;
                        for (int wi = 0; wi < win_n; ++wi)
                            win_seen = win_seen || win_at[wi] == at_k;
                        // Two windows per process: the first prefix, then the
                        // next prefix at a different address. A later DMA can
                        // start 8 bytes earlier and repeat the same word.
                        if (phase == 4u && win_n < 2 && !win_seen) {
                            win_at[win_n++] = at_k;
                            uint32_t pool = 0;
                            if (0x1163ECu <= ram_bytes) {
                                for (uint32_t b = 0; b < 4u; ++b)
                                    pool = (pool << 8) | g_rdram_for_submit[(0x1163E8u + b) ^ 3u];
                            }
                            int idx = -1;
                            int coff = -1;
                            if ((pool & 0xFu) == 0u && pool >= 0x80800000u && pool < 0x81000000u &&
                                at_k >= pool) {
                                const uint32_t rel = at_k - pool;
                                if (rel < 0x50000u) {
                                    idx = static_cast<int>(rel / 0x108u);
                                    coff = static_cast<int>(rel % 0x108u);
                                }
                            }
                            char pre[12 * 8], post[12 * 8];
                            pre[0] = 0;
                            post[0] = 0;
                            if (at >= 0x20u && at + 0x24u <= ram_bytes) {
                                size_t pn = 0, qn = 0;
                                for (uint32_t i = 0; i < 8u; ++i) {
                                    auto be_at = [&](uint32_t p) -> uint32_t {
                                        uint32_t w = 0;
                                        for (uint32_t b = 0; b < 4u; ++b)
                                            w = (w << 8) | g_rdram_for_submit[(p + b) ^ 3u];
                                        return w;
                                    };
                                    const uint32_t bw = be_at(at - 0x20u + i * 4u);
                                    const uint32_t aw = be_at(at + 4u + i * 4u);
                                    pn += static_cast<size_t>(std::snprintf(
                                        pre + pn, sizeof(pre) - pn, "%s%08X", i ? "," : "", bw));
                                    qn += static_cast<size_t>(std::snprintf(
                                        post + qn, sizeof(post) - qn, "%s%08X", i ? "," : "", aw));
                                }
                            }
                            std::fprintf(stderr,
                                "[g1d-win] phase=%u word_at=0x%08X word=0x%08X pool=0x%08X "
                                "idx=%d chunk_off=%d before=%s after=%s\n",
                                phase, at_k, word, pool, idx, coff, pre, post);
                            std::fflush(stderr);
                        }
                        if (prefix_hits < 64u) {
                            ++prefix_hits;
                            emit_hit(off, word, exact ? "prefix" : "stride");
                        }
                    } else if ((dram_in_node || dram_in_glob) && slot_hits < 64u) {
                        ++slot_hits;
                        emit_hit(off, word, dram_in_node ? "node" : "glob");
                    } else if (!logged_span && hits < 64u) {
                        ++hits;
                        logged_span = true;
                        emit_hit(off, word, "span");
                    }
                }
                if (prefix_hits < 64u && scan_n >= 3u) {
                    for (uint32_t off = 0; off + 3u <= scan_n && prefix_hits < 64u; ++off) {
                        const uint8_t b0 = g_rdram_for_submit[(phys + off) ^ 3u];
                        const uint8_t b1 = g_rdram_for_submit[(phys + off + 1) ^ 3u];
                        const uint8_t b2 = g_rdram_for_submit[(phys + off + 2) ^ 3u];
                        const bool ctl = b0 == 0xA6 && b1 == 0xAA && b2 == 0x10;
                        const bool wide_b = b0 == 0xAE && b1 == 0x61 && b2 == 0x20;
                        if (!ctl && !wide_b) continue;
                        if ((off & 3u) == 1u && off >= 1u) {
                            const uint8_t topb = g_rdram_for_submit[(phys + off - 1u) ^ 3u];
                            if (topb == 0x00u || topb == 0x80u) continue;
                        }
                        const uint32_t word = (off >= 1u
                                ? ((uint32_t)g_rdram_for_submit[(phys + off - 1u) ^ 3u] << 24)
                                : 0u) |
                            ((uint32_t)b0 << 16) | ((uint32_t)b1 << 8) | (uint32_t)b2;
                        const uint32_t log_off = ((off & 3u) == 1u && off >= 1u) ? off - 1u : off;
                        ++prefix_hits;
                        emit_hit(log_off, word, ctl ? "bytes-ctl" : "bytes-wide");
                    }
                }
            }
        }
        if (rows < 4096u) {
            ++rows;
            // s6196: the 0x10F command-source DMA is the first width-differing
            // RSP read. Dump its 0x100..0x10E tail as big-endian words, plus a
            // bounded look at pointer-shaped words, so one pair of arms can
            // separate relocation from a width-bearing command.
            // s6197: the RSP only reads 0x10F. Dump 0x200 of the first two
            // distinct root nodes so a shifted 05200002 block is visible.
            if (mem == 0x170u && len == 0x10Fu && phys + 0x200u < 0x01000000u) {
                static uint32_t seen = 0;
                static uint32_t dumped = 0;
                static uint32_t node_phys[2] = {};
                static uint32_t node_n = 0;
                const uint32_t root = rs64_e9prov_current_root_dl() & 0x007FFFFFu;
                const uint32_t rel = (phys - root) & 0x007FFFFFu;
                const bool at_root = rel == 0u;
                seen++;
                auto be_word = [&](uint32_t off) -> uint32_t {
                    uint32_t word = 0;
                    for (uint32_t b = 0; b < 4u; ++b)
                        word = (word << 8) | g_rdram_for_submit[(phys + off + b) ^ 3u];
                    return word;
                };
                if (at_root && node_n < 2u) {
                    bool known = false;
                    for (uint32_t i = 0; i < node_n; ++i) known = known || node_phys[i] == phys;
                    if (!known) {
                        int sig_off = -1;
                        uint32_t sig_n = 0;
                        uint32_t fill_n = 0;
                        int fill_off = -1;
                        char sig_offs[96] = {};
                        size_t sig_len = 0;
                        for (uint32_t off = 0; off + 4u <= 0x200u; ++off) {
                            const uint32_t word = be_word(off);
                            if (word == 0x05200002u) {
                                if (sig_off < 0) sig_off = static_cast<int>(off);
                                if (sig_n < 8u && sig_len + 8u < sizeof(sig_offs)) {
                                    sig_len += static_cast<size_t>(std::snprintf(
                                        sig_offs + sig_len, sizeof(sig_offs) - sig_len,
                                        "%s0x%X", sig_n ? "," : "", off));
                                }
                                sig_n++;
                            }
                            if ((off & 3u) == 0u && word == 0x00010001u) {
                                if (fill_off < 0) fill_off = static_cast<int>(off);
                                fill_n++;
                            }
                        }
                        std::fprintf(stderr,
                            "[g1d-node] phase=%u n=%u dram=0x%08X phys=0x%06X root=0x%06X "
                            "sig=05200002 sig_n=%u sig_off=%d sig_offs=%s fill10001=%u "
                            "fill_off=%d bytes=",
                            phase, node_n, dram, phys, root, sig_n, sig_off,
                            sig_n ? sig_offs : "-", fill_n, fill_off);
                        for (uint32_t i = 0; i < 0x200u; ++i)
                            std::fprintf(stderr, "%02X", g_rdram_for_submit[(phys + i) ^ 3u]);
                        std::fprintf(stderr, "\n");
                        node_phys[node_n++] = phys;
                    }
                }
                if (dumped < 8u && (at_root || dumped == 0u)) {
                    uint32_t head_nz = 0;
                    uint32_t head_hash = 2166136261u;
                    for (uint32_t i = 0; i < 0x100u; ++i) {
                        const uint8_t b = g_rdram_for_submit[(phys + i) ^ 3u];
                        head_nz += b != 0u;
                        head_hash = (head_hash * 16777619u) ^ b;
                    }
                    const uint32_t words[4] = {
                        be_word(0x100u), be_word(0x104u), be_word(0x108u), be_word(0x10Cu)};
                    std::fprintf(stderr,
                        "[g1d-tail] phase=%u n=%u seen=%u dram=0x%08X phys=0x%06X root=0x%06X rel=0x%X "
                        "head_nz=%u head_hash=0x%08X words=%08X,%08X,%08X,%08X bytes=",
                        phase, dumped, seen, dram, phys, root, rel, head_nz, head_hash,
                        words[0], words[1], words[2], words[3]);
                    for (uint32_t i = 0x100u; i < 0x10Fu; ++i)
                        std::fprintf(stderr, "%02X%s", g_rdram_for_submit[(phys + i) ^ 3u],
                            i == 0x10Eu ? "" : ":");
                    std::fprintf(stderr, "\n");
                    if (head_nz != 0u && dumped < 2u) {
                        std::fprintf(stderr, "[g1d-head] n=%u phys=0x%06X bytes=", dumped, phys);
                        for (uint32_t i = 0; i < 0x100u; ++i)
                            std::fprintf(stderr, "%02X", g_rdram_for_submit[(phys + i) ^ 3u]);
                        std::fprintf(stderr, "\n");
                    }
                    if (at_root) {
                        for (uint32_t wi = 0; wi < 4u; ++wi) {
                            const uint32_t word = words[wi];
                            const uint32_t tp = word & 0x00FFFFFFu;
                            const uint32_t hi = word >> 24;
                            if (!((hi == 0x00u || hi == 0x80u) && tp >= 0x1000u &&
                                  tp + 64u < 0x01000000u))
                                continue;
                            uint32_t th = 2166136261u;
                            std::fprintf(stderr,
                                "[g1d-tail-tgt] n=%u wi=%u word=0x%08X phys=0x%06X bytes=",
                                dumped, wi, word, tp);
                            for (uint32_t i = 0; i < 64u; ++i) {
                                const uint8_t b = g_rdram_for_submit[(tp + i) ^ 3u];
                                th = (th * 16777619u) ^ b;
                                std::fprintf(stderr, "%02X", b);
                            }
                            std::fprintf(stderr, " hash=0x%08X\n", th);
                        }
                    }
                    dumped++;
                }
            }
            std::fflush(stderr);
        }
    }
    uint32_t cap;
    if (!m4_src_enabled(&cap)) return;
    static uint32_t lines = 0;
    if (lines++ >= cap) return;
    fprintf(stderr, "[m4-dma] task=%u phase=%u mem=0x%04X dram=0x%08X len=0x%X\n",
            g_e9prov.task, rs64_phase_ord(), mem, dram, len);
    fflush(stderr);
    // s4631: matrix-span RDRAM words at DMA time (port side of the retail peek).
    const uint32_t phys = dram & 0x1FFFFFFFu;
    static uint32_t mlines = 0;
    if (g_rdram_for_submit != nullptr && phys >= 0x700000u && phys < 0x700400u && mlines++ < 400u) {
        fprintf(stderr, "[m4-mat] task=%u phase=%u mem=0x%04X dram=0x%08X w=", g_e9prov.task,
                rs64_phase_ord(), mem, phys);
        for (uint32_t i = 0; i < 16; ++i) {
            const uint32_t a = phys + 4 * i;
            fprintf(stderr, "%02x%02x%02x%02x%s", g_rdram_for_submit[a ^ 3], g_rdram_for_submit[(a + 1) ^ 3],
                    g_rdram_for_submit[(a + 2) ^ 3], g_rdram_for_submit[(a + 3) ^ 3], i == 15 ? "" : ",");
        }
        fputc('\n', stderr);
        fflush(stderr);
    }
}

// s4630: operands feeding the vertex transform at the loop head: vertex v2,
// matrix v8..v15, and the DMEM vertex window at r13.
extern "C" void rs64_m4_src_probe(void *opaque, uint32_t r13) {
    uint32_t cap;
    if (!m4_src_enabled(&cap)) return;
    static uint32_t lines = 0;
    if (lines++ >= cap) return;
    auto *rsp = static_cast<RSP *>(opaque);
    fprintf(stderr, "[m4-src] task=%u phase=%u r13=0x%04X", g_e9prov.task, rs64_phase_ord(), r13);
    static const unsigned regs[] = {2, 8, 9, 10, 11, 12, 13, 14, 15, 30};
    for (unsigned reg : regs) {
        fprintf(stderr, " v%u=", reg);
        for (unsigned lane = 0; lane < 8; ++lane) fprintf(stderr, "%04X", rsp->vpu.r[reg].u16(lane));
    }
    fprintf(stderr, " vtx=");
    for (uint32_t i = 0; i < 0x20; ++i)
        fprintf(stderr, "%02X", (unsigned)g_dmem_cur[(((r13 & 0xFFFu) + i) & 0xFFFu) ^ 3u]);
    fputc('\n', stderr);
    fflush(stderr);
}

extern "C" uint32_t rs64_vi_committed_width();
extern "C" uint32_t rs64_vi_committed_origin();
extern "C" int rs64_is_hangar_vi(void);

static bool rs64_m4_y8000_enabled() {
    static const int v = [] {
        const char *all = std::getenv("ROGUESQ_LOG_ALL");
        if (all && *all && *all != '0') return 1;
        const char *e = std::getenv("ROGUESQ_LOG_M4_Y8000");
        // s6712 G1e: was default-ON (env unset -> 1): a ~500-byte [m4-y8000] summary + fflush every 64 flushes, ~600 lines/s
        // in lvl5 dd4 flight (148k lines / 90 MB per 4-min run), 15.5% of the gfx ucode's samples in owner play. Opt-in now.
        if (!e) return 0;
        return (*e && *e != '0') ? 1 : 0;
    }();
    return v == 1;
}

static uint32_t rs64_m4_y8000_gate_width() {
    static const uint32_t w = [] {
        const char *e = std::getenv("ROGUESQ_M4_Y8000_WIDTH");
        return e && *e ? static_cast<uint32_t>(std::strtoul(e, nullptr, 10)) : 640u;
    }();
    return w;
}

// s1967 hangar hologram-beam artifact discriminator: unconditional (not
// Y=0x8000-gated) dump of every 0xC8-class Fill Triangle command's full
// geometry, restricted to the same hangar/512 gate as the y8000 probe.
// The mode census below uses standard RDP 0xB9/0xBA commands; Factor 5's
// upstream 0xB3/0xBE commands are not bytes emitted by this restage buffer.
static bool rs64_m4_tri_dump_enabled() {
    static const bool v = [] {
        const char *all = std::getenv("ROGUESQ_LOG_ALL");
        if (all && *all && *all != '0') return true;
        const char *e = std::getenv("ROGUESQ_LOG_M4_TRI_DUMP");
        return e && *e && *e != '0';
    }();
    return v;
}

static uint32_t rs64_m4_tri_dump_cap() {
    static const uint32_t cap = [] {
        const char *e = std::getenv("ROGUESQ_M4_TRI_DUMP_CAP");
        return e && *e ? static_cast<uint32_t>(std::strtoul(e, nullptr, 10)) : 500u;
    }();
    return cap;
}

struct Rs64M4Y8000 {
    uint32_t n_entry_all = 0;
    uint32_t n_flush_site_all = 0;
    uint32_t n_entry = 0;
    uint32_t n_y8000_entry = 0;
    uint32_t n_entry_allout = 0;
    uint32_t n_entry_partial = 0;
    uint32_t n_entry_fall = 0;
    uint32_t n_flush = 0;
    uint32_t n_empty = 0;
    uint32_t n_hdr = 0;
    uint32_t n_y8000_any = 0;
    uint32_t n_y8000_equal = 0;
    uint32_t n_y8000_mixed = 0;
    uint32_t n_dump = 0;
    uint32_t n_entry_dump = 0;
    uint32_t n_tri_total = 0;
    uint32_t n_tri_order_bad = 0;
    uint32_t n_tri_degenerate = 0;
    uint32_t n_tri_dump = 0;
    uint32_t n_tri_order_bad_confirmed = 0;
    uint32_t n_tri_order_bad_stale = 0;
    uint32_t n_othermode = 0;
    uint32_t n_othermode_h = 0;
    uint32_t n_othermode_l = 0;
    uint32_t n_othermode_invalid = 0;
    uint32_t n_othermode_dump = 0;
    uint32_t othermode_h = 0;
    uint32_t othermode_l = 0;
    bool othermode_valid = false;
    uint32_t last_width = 0xFFFFFFFFu;
    uint32_t last_origin = 0xFFFFFFFFu;
    bool last_in_gate = false;
    bool marked_entry = false;
    bool marked_flush = false;
    bool marked_hangar = false;
    bool atexit_armed = false;
    // Writer-attestation bitmap (s1968): set by rs64_m4_y8000_store when
    // L_1930 genuinely stores a header byte at that DMEM offset this
    // accumulation cycle. Cleared for the drained range after each flush
    // consumes it, so a true bit always means "written since the last
    // flush", never a carry-over from an older cycle.
    bool stored[0x1000] = {};
};

static Rs64M4Y8000 g_m4_y8000;

static void rs64_m4_y8000_reset_gated() {
    g_m4_y8000.n_entry = 0;
    g_m4_y8000.n_y8000_entry = 0;
    g_m4_y8000.n_entry_allout = 0;
    g_m4_y8000.n_entry_partial = 0;
    g_m4_y8000.n_entry_fall = 0;
    g_m4_y8000.n_flush = 0;
    g_m4_y8000.n_empty = 0;
    g_m4_y8000.n_hdr = 0;
    g_m4_y8000.n_y8000_any = 0;
    g_m4_y8000.n_y8000_equal = 0;
    g_m4_y8000.n_y8000_mixed = 0;
    g_m4_y8000.n_dump = 0;
    g_m4_y8000.n_entry_dump = 0;
    g_m4_y8000.n_tri_total = 0;
    g_m4_y8000.n_tri_order_bad = 0;
    g_m4_y8000.n_tri_degenerate = 0;
    g_m4_y8000.n_tri_dump = 0;
    g_m4_y8000.n_tri_order_bad_confirmed = 0;
    g_m4_y8000.n_tri_order_bad_stale = 0;
    g_m4_y8000.n_othermode = 0;
    g_m4_y8000.n_othermode_h = 0;
    g_m4_y8000.n_othermode_l = 0;
    g_m4_y8000.n_othermode_invalid = 0;
    g_m4_y8000.n_othermode_dump = 0;
    g_m4_y8000.othermode_h = 0;
    g_m4_y8000.othermode_l = 0;
    g_m4_y8000.othermode_valid = false;
    std::memset(g_m4_y8000.stored, 0, sizeof(g_m4_y8000.stored));
}

static void rs64_m4_y8000_summary(const char *why) {
    fprintf(stderr,
        "[m4-y8000] summary why=%s phase=%u viw=%u origin=0x%08X hangar=%d "
        "entry_all=%u flush_site_all=%u "
        "entry=%u y8000_entry=%u allout=%u partial=%u fall=%u "
        "flush=%u empty=%u hdr=%u y8000_any=%u y8000_equal=%u y8000_mixed=%u dump=%u "
        "tri_total=%u tri_order_bad=%u tri_degenerate=%u "
        "tri_order_bad_confirmed=%u tri_order_bad_stale=%u "
        "othermode=%u h=%u l=%u invalid=%u valid=%d\n",
        why, rs64_phase_ord(), rs64_vi_committed_width(),
        rs64_vi_committed_origin(), rs64_is_hangar_vi(),
        g_m4_y8000.n_entry_all, g_m4_y8000.n_flush_site_all,
        g_m4_y8000.n_entry, g_m4_y8000.n_y8000_entry,
        g_m4_y8000.n_entry_allout, g_m4_y8000.n_entry_partial, g_m4_y8000.n_entry_fall,
        g_m4_y8000.n_flush, g_m4_y8000.n_empty, g_m4_y8000.n_hdr,
        g_m4_y8000.n_y8000_any, g_m4_y8000.n_y8000_equal, g_m4_y8000.n_y8000_mixed,
        g_m4_y8000.n_dump,
        g_m4_y8000.n_tri_total, g_m4_y8000.n_tri_order_bad, g_m4_y8000.n_tri_degenerate,
        g_m4_y8000.n_tri_order_bad_confirmed, g_m4_y8000.n_tri_order_bad_stale,
        g_m4_y8000.n_othermode, g_m4_y8000.n_othermode_h, g_m4_y8000.n_othermode_l,
        g_m4_y8000.n_othermode_invalid,
        g_m4_y8000.othermode_valid ? 1 : 0);
    fflush(stderr);
}

static void rs64_m4_y8000_atexit() {
    rs64_m4_y8000_summary("atexit");
}

static bool rs64_m4_y8000_in_gate() {
    if (!g_m4_y8000.atexit_armed) {
        g_m4_y8000.atexit_armed = true;
        std::atexit(rs64_m4_y8000_atexit);
    }
    const uint32_t w = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    const uint32_t gate_w = rs64_m4_y8000_gate_width();
    const bool now_in = (w == gate_w) && (gate_w != 512u || rs64_is_hangar_vi());
    if (w != g_m4_y8000.last_width || origin != g_m4_y8000.last_origin) {
        if (g_m4_y8000.last_width != 0xFFFFFFFFu &&
            (g_m4_y8000.n_entry_all || g_m4_y8000.n_flush_site_all)) {
            rs64_m4_y8000_summary(w != g_m4_y8000.last_width ? "width-change" : "origin-change");
        }
        if (g_m4_y8000.last_in_gate && !now_in) {
            rs64_m4_y8000_reset_gated();
        }
        g_m4_y8000.last_width = w;
        g_m4_y8000.last_origin = origin;
    }
    if (now_in && !g_m4_y8000.marked_hangar && rs64_is_hangar_vi()) {
        g_m4_y8000.marked_hangar = true;
        fprintf(stderr,
            "[m4-y8000] mark hangar-origin phase=%u viw=%u origin=0x%08X\n",
            rs64_phase_ord(), w, origin);
        fflush(stderr);
    }
    g_m4_y8000.last_in_gate = now_in;
    return now_in;
}

// s1968 writer-attestation hook: called from the actual L_1930 store site
// (`sb $10, 0x0($16)`, see tools/fixup_factor5_ucode.py Fixup 21) so the
// flush walker below can tell a genuinely-written header byte from one
// that only appears written because the buffer wasn't cleared.
extern "C" void rs64_m4_y8000_store(uint32_t r16) {
    if (!rs64_m4_y8000_enabled()) return;
    if (!rs64_m4_y8000_in_gate()) return;
    g_m4_y8000.stored[r16 & 0xFFFu] = true;
}

extern "C" uint32_t rs64_m4_y8000_step(uint32_t guest_pc) {
    (void)guest_pc;
    return ++g_e9prov.m4_y8000_step;
}

extern "C" void rs64_m4_y8000_entry(uint32_t y11, uint32_t y12, uint32_t y13,
                                     uint32_t c13, uint32_t c12, uint32_t c11,
                                     uint32_t guest_pc, uint32_t step) {
    if (!rs64_m4_y8000_enabled()) return;
    g_m4_y8000.n_entry_all++;
    if (!g_m4_y8000.marked_entry) {
        g_m4_y8000.marked_entry = true;
        fprintf(stderr,
            "[m4-y8000] mark entry phase=%u viw=%u origin=0x%08X hangar=%d y=%04X/%04X/%04X clip=%04X/%04X/%04X\n",
            rs64_phase_ord(), rs64_vi_committed_width(),
            rs64_vi_committed_origin(), rs64_is_hangar_vi(),
            y11 & 0xFFFF, y12 & 0xFFFF, y13 & 0xFFFF,
            c11 & 0xFFFF, c12 & 0xFFFF, c13 & 0xFFFF);
        fflush(stderr);
    }
    if (!rs64_m4_y8000_in_gate()) return;
    static uint32_t key_lines = 0;
    if (key_lines++ < 2048) {
        fprintf(stderr, "[m4-key] edge=entry task=%u phase=%u viw=%u origin=0x%08X pc=0x%04X step=%u\n",
                g_e9prov.task, rs64_phase_ord(), rs64_vi_committed_width(),
                rs64_vi_committed_origin(), guest_pc, step);
        fflush(stderr);
    }
    g_m4_y8000.n_entry++;
    const uint32_t ya = y11 & 0xFFFF;
    const uint32_t yb = y12 & 0xFFFF;
    const uint32_t yc = y13 & 0xFFFF;
    if (ya != 0x8000 && yb != 0x8000 && yc != 0x8000) {
        if ((g_m4_y8000.n_entry & 255u) == 0) rs64_m4_y8000_summary("entry-hb");
        return;
    }
    g_m4_y8000.n_y8000_entry++;
    const uint32_t clip_and = (c11 & c12 & c13) & 0xFFFF;
    const uint32_t clip_or = (c11 | c12 | c13) & 0xFFFF;
    const char *cls;
    if (clip_and & 0x7070) {
        g_m4_y8000.n_entry_allout++;
        cls = "allout";
    } else if (clip_or & 0x4343) {
        g_m4_y8000.n_entry_partial++;
        cls = "partial";
    } else {
        g_m4_y8000.n_entry_fall++;
        cls = "fall";
    }
    if (g_m4_y8000.n_entry_dump < 8) {
        g_m4_y8000.n_entry_dump++;
        fprintf(stderr,
            "[m4-y8000] entry n=%u cls=%s y=%04X/%04X/%04X clip=%04X/%04X/%04X and=%04X or=%04X\n",
            g_m4_y8000.n_y8000_entry, cls, ya, yb, yc,
            c11 & 0xFFFF, c12 & 0xFFFF, c13 & 0xFFFF, clip_and, clip_or);
        fflush(stderr);
    }
}

extern "C" void rs64_m4_y8000_flush(uint32_t r16, uint32_t guest_pc, uint32_t step) {
    if (!rs64_m4_y8000_enabled()) return;
    g_m4_y8000.n_flush_site_all++;
    if (!g_m4_y8000.marked_flush) {
        g_m4_y8000.marked_flush = true;
        fprintf(stderr,
            "[m4-y8000] mark flush-site phase=%u viw=%u origin=0x%08X hangar=%d r16=0x%X\n",
            rs64_phase_ord(), rs64_vi_committed_width(),
            rs64_vi_committed_origin(), rs64_is_hangar_vi(), r16);
        fflush(stderr);
    }
    if (!rs64_m4_y8000_in_gate()) return;
    static uint32_t key_lines = 0;
    if (key_lines++ < 2048) {
        fprintf(stderr, "[m4-key] edge=flush task=%u phase=%u viw=%u origin=0x%08X pc=0x%04X step=%u\n",
                g_e9prov.task, rs64_phase_ord(), rs64_vi_committed_width(),
                rs64_vi_committed_origin(), guest_pc, step);
        fflush(stderr);
    }
    const uint32_t end = r16 & 0xFFFu;
    if (end <= 0xD60) {
        g_m4_y8000.n_empty++;
        return;
    }
    g_m4_y8000.n_flush++;
    if (g_m4_y8000.n_flush == 1) rs64_m4_y8000_summary("first-gated-flush");
    uint32_t off = 0xD60;
    while (off + 8 <= end) {
        const uint8_t hdr = RSP_MEM_BU(off, 0);

        // Standard RDP SETOTHERMODE_L/H are 0xB9/0xBA. The published Factor
        // 5 reference identifies 0xB3/0xBE as upstream _EX handlers with an
        // extra inline word; the L_1930 restage buffer is the plain RDP
        // command stream and must be decoded at the hardware opcode layer.
        if (hdr == 0xB9 || hdr == 0xBA) {
            const uint32_t w0 = RSP_MEM_W_LOAD(off, 0);
            const uint32_t w1 = RSP_MEM_W_LOAD(off + 4, 0);
            const uint32_t shift = (w0 >> 8) & 0xFFu;
            const uint32_t size = (w0 & 0xFFu) + 1u;
            const bool valid = shift < 32u && size <= 32u && shift + size <= 32u;
            if (!valid) {
                g_m4_y8000.n_othermode_invalid++;
                if (rs64_m4_tri_dump_enabled() &&
                    g_m4_y8000.n_othermode_dump < rs64_m4_tri_dump_cap()) {
                    g_m4_y8000.n_othermode_dump++;
                    fprintf(stderr,
                        "[m4-om-invalid] n=%u off=0x%03X kind=%c w0=%08X w1=%08X "
                        "shift=%u size=%u\n",
                        g_m4_y8000.n_othermode_dump, off, hdr == 0xBA ? 'H' : 'L',
                        w0, w1, shift, size);
                    fflush(stderr);
                }
                off += 8;
                continue;
            }
            const uint32_t mask = size >= 32u
                ? 0xFFFFFFFFu
                : (shift >= 32u ? 0u : ((1u << size) - 1u) << shift);
            if (hdr == 0xBA) {
                g_m4_y8000.n_othermode_h++;
                g_m4_y8000.othermode_h = (g_m4_y8000.othermode_h & ~mask) | (w1 & mask);
            } else {
                g_m4_y8000.n_othermode_l++;
                g_m4_y8000.othermode_l = (g_m4_y8000.othermode_l & ~mask) | (w1 & mask);
            }
            g_m4_y8000.n_othermode++;
            g_m4_y8000.othermode_valid = true;
            if (rs64_m4_tri_dump_enabled() &&
                g_m4_y8000.n_othermode_dump < rs64_m4_tri_dump_cap()) {
                g_m4_y8000.n_othermode_dump++;
                fprintf(stderr,
                    "[m4-om] n=%u off=0x%03X kind=%c w0=%08X w1=%08X "
                    "shift=%u size=%u H=%08X L=%08X zcmp=%d zupd=%d "
                    "cvgx=%d alphacvg=%d zmode=%u blend=%04X\n",
                    g_m4_y8000.n_othermode_dump, off, hdr == 0xBA ? 'H' : 'L',
                    w0, w1, shift, size, g_m4_y8000.othermode_h,
                    g_m4_y8000.othermode_l,
                    (g_m4_y8000.othermode_l & 0x10u) != 0,
                    (g_m4_y8000.othermode_l & 0x20u) != 0,
                    (g_m4_y8000.othermode_l & 0x1000u) != 0,
                    (g_m4_y8000.othermode_l & 0x2000u) != 0,
                    (g_m4_y8000.othermode_l >> 10) & 3u,
                    (g_m4_y8000.othermode_l >> 16) & 0xFFFFu);
                fflush(stderr);
            }
            off += 8;
            continue;
        }
        if ((hdr & 0xF8) != 0xC8) {
            off += 8;
            continue;
        }
        g_m4_y8000.n_hdr++;
        const uint16_t yl = static_cast<uint16_t>(RSP_MEM_HU_LOAD(off + 2, 0));
        const uint16_t ym = static_cast<uint16_t>(RSP_MEM_HU_LOAD(off + 4, 0));
        const uint16_t yh = static_cast<uint16_t>(RSP_MEM_HU_LOAD(off + 6, 0));

        // Unconditional geometry dump/check (not gated on Y=0x8000): hardware
        // requires YH <= YM <= YL (screen-space top-to-bottom scanline order,
        // s11.2 signed fixed-point). A violation or an all-equal (zero-height)
        // triangle here is a malformed-command signal independent of the
        // parked M4 accumulator question.
        g_m4_y8000.n_tri_total++;
        const int16_t syl = static_cast<int16_t>(yl);
        const int16_t sym = static_cast<int16_t>(ym);
        const int16_t syh = static_cast<int16_t>(yh);
        const bool order_bad = !(syh <= sym && sym <= syl);
        const bool degenerate = (yl == ym && ym == yh);
        if (order_bad) g_m4_y8000.n_tri_order_bad++;
        if (degenerate) g_m4_y8000.n_tri_degenerate++;
        // Writer attestation (s1968): a genuine L_1930 store this cycle set
        // stored[off]. If it's false, the 0xC8-class byte we're reading was
        // never written since the last drain -- a stale-buffer misread, not
        // a malformed command from the game. Only meaningful for order_bad
        // (the ambiguous case from s1967); a well-formed triangle at a
        // stale offset would be indistinguishable from a real one anyway.
        bool order_bad_confirmed = false;
        if (order_bad) {
            if (g_m4_y8000.stored[off & 0xFFFu]) {
                g_m4_y8000.n_tri_order_bad_confirmed++;
                order_bad_confirmed = true;
            } else {
                g_m4_y8000.n_tri_order_bad_stale++;
            }
        }
        if (rs64_m4_tri_dump_enabled() && g_m4_y8000.n_tri_dump < rs64_m4_tri_dump_cap()) {
            g_m4_y8000.n_tri_dump++;
            const uint32_t xl = RSP_MEM_W_LOAD(off + 8, 0);
            const uint32_t dxldy = RSP_MEM_W_LOAD(off + 12, 0);
            const uint32_t xh = RSP_MEM_W_LOAD(off + 16, 0);
            const uint32_t dxhdy = RSP_MEM_W_LOAD(off + 20, 0);
            const uint32_t xm = RSP_MEM_W_LOAD(off + 24, 0);
            const uint32_t dxmdy = RSP_MEM_W_LOAD(off + 28, 0);
            fprintf(stderr,
                "[m4-tri] n=%u off=0x%03X hdr=%02X YL=%04X YM=%04X YH=%04X "
                "XL=%08X DxLDy=%08X XH=%08X DxHDy=%08X XM=%08X DxMDy=%08X "
                "order_bad=%d degenerate=%d stored=%d om_valid=%d "
                "omH=%08X omL=%08X zcmp=%d zupd=%d cvgx=%d alphacvg=%d\n",
                g_m4_y8000.n_tri_dump, off, hdr, yl, ym, yh,
                xl, dxldy, xh, dxhdy, xm, dxmdy,
                order_bad ? 1 : 0, degenerate ? 1 : 0,
                order_bad ? (order_bad_confirmed ? 1 : 0) : (g_m4_y8000.stored[off & 0xFFFu] ? 1 : 0),
                g_m4_y8000.othermode_valid ? 1 : 0,
                g_m4_y8000.othermode_h, g_m4_y8000.othermode_l,
                (g_m4_y8000.othermode_l & 0x10u) != 0,
                (g_m4_y8000.othermode_l & 0x20u) != 0,
                (g_m4_y8000.othermode_l & 0x1000u) != 0,
                (g_m4_y8000.othermode_l & 0x2000u) != 0);
            fflush(stderr);
        }

        const int any = (yl == 0x8000) || (ym == 0x8000) || (yh == 0x8000);
        if (any) {
            g_m4_y8000.n_y8000_any++;
            if (yl == ym && ym == yh) g_m4_y8000.n_y8000_equal++;
            else g_m4_y8000.n_y8000_mixed++;
            if (g_m4_y8000.n_dump < 8) {
                g_m4_y8000.n_dump++;
                fprintf(stderr,
                    "[m4-y8000] cmd n=%u off=0x%03X hdr=%02X %02X YL=%04X YM=%04X YH=%04X",
                    g_m4_y8000.n_y8000_any, off, hdr, (unsigned)RSP_MEM_BU(off + 1, 0),
                    yl, ym, yh);
                for (uint32_t i = 0; i < 8; ++i) {
                    fprintf(stderr, "%s%02X", i == 0 ? " bytes=" : "",
                            (unsigned)RSP_MEM_BU(off + i, 0));
                }
                fputc('\n', stderr);
                fflush(stderr);
            }
        }
        uint32_t size = 32;
        if (hdr & 0x4) size += 64;
        if (hdr & 0x2) size += 64;
        if (hdr & 0x1) size += 64;
        off += size;
    }
    // Drained: clear the writer-attestation bits for [0xD60, end) so the
    // next accumulation cycle starts from a clean "not written" state and
    // a leftover true bit can never be misread as this cycle's write.
    std::memset(g_m4_y8000.stored + 0xD60, 0, end - 0xD60);
    if ((g_m4_y8000.n_flush & 63u) == 0) rs64_m4_y8000_summary("flush-hb");
}

struct Rs64F5VtxColorState {
    uint32_t task = 0xFFFFFFFFu;
    uint32_t ordinal = 0;
    uint32_t pc = 0;
    uint32_t source = 0;
    bool valid = false;
};

static Rs64F5VtxColorState g_f5_vtxcolor_state;
static std::mutex g_f5_vtxcolor_mutex;
static bool rs64_m4_y8000_in_gate();

struct Rs64F5VtxStoreRange {
    uint32_t phase;
    uint32_t source;
    uint32_t end;
    uint32_t task;
    uint32_t pc;
    uint32_t dma_events = 0;
    uint32_t last_dma_source = 0;
    uint32_t last_dma_len = 0;
    uint32_t last_dma_dmem = 0;
    uint32_t last_dma_fnv = 0;
    uint32_t last_dma_red_words = 0;
    uint8_t registration[32] = {};
};

struct Rs64F5LastWriter {
    uint32_t pc = 0;
    uint32_t value = 0;
    uint32_t pre_value = 0;
    uint32_t post_value = 0;
    uint32_t phase = 0;
    uint8_t width = 0;
    bool post_valid = false;
};

extern "C" volatile uint8_t* volatile g_recomp_rdram_for_wp_raw;

static Rs64F5VtxStoreRange g_f5_vtx_store_ranges[128] = {};
static uint32_t g_f5_vtx_store_range_next = 0;
static std::mutex g_f5_vtx_store_mutex;
static std::vector<Rs64F5LastWriter> g_f5_last_writer;
static uint32_t g_f5_last_writer_updates = 0;
// s7366: first-touch sizing ran unlocked on both the guest store hook and the Gfx-thread dump (TSan-class AQ review): two threads
// could resize the same empty vector at once. Size it exactly once.
static std::once_flag g_f5_last_writer_once;
static inline void rs64_f5_last_writer_ensure() { std::call_once(g_f5_last_writer_once, [] { g_f5_last_writer.resize(0x200000u); }); }
static uint32_t g_f5_bulk_control = 0;
static uint32_t g_f5_bulk_rows = 0;
static uint32_t g_f5_d114_exact_rows = 0;

static uint32_t rs64_f5_read_word(const volatile uint8_t* rd, uint32_t phys) {
    const uint32_t a = phys & ~3u;
    return (uint32_t(rd[a + 3u]) << 24) |
           (uint32_t(rd[a + 2u]) << 16) |
           (uint32_t(rd[a + 1u]) << 8) | uint32_t(rd[a]);
}

struct Rs64F5PhaseDma {
    uint32_t phase = 0;
    uint32_t start = 0;
    uint32_t end = 0;
    uint32_t dmem = 0;
    uint32_t fnv = 0;
    uint32_t red_words = 0;
};

static Rs64F5PhaseDma g_f5_phase_dma[512] = {};
static uint32_t g_f5_phase_dma_count = 0;

struct Rs64F5PhaseStore {
    uint64_t seq = 0;
    uint32_t phase = 0;
    uint32_t addr = 0;
    uint32_t span = 0;
    uint32_t pc = 0;
    uint32_t value = 0;
    uint8_t width = 0;
};

static constexpr uint32_t kF5PhaseStoreCapacity = 65536u;
static Rs64F5PhaseStore g_f5_phase_store[kF5PhaseStoreCapacity] = {};
static uint32_t g_f5_phase_store_count = 0;
static uint32_t g_f5_phase_store_next = 0;
static uint64_t g_f5_phase_store_seq = 0;
static uint32_t g_f5_phase_store_prints = 0;
static uint32_t g_f5_target_store_prints = 0;
static uint32_t g_f5_target_post_prints = 0;

struct Rs64F5HostOrderPending {
    uint64_t seq = 0;
    uint32_t phys = 0;
    uint32_t len = 0;
    uint32_t overlap = 0;
    uint32_t sample_len = 0;
    char api[32] = {};
    uint8_t before[32] = {};
    bool valid = false;
};

static Rs64F5HostOrderPending g_f5_host_order_pending;
// s6349: fixed-range host-write census for the red VTX boundary.
static constexpr uint32_t kF5HostTgtBegin = 0x735560u;
static constexpr uint32_t kF5HostTgtEnd = 0x7355D0u;
struct Rs64F5HostTgt {
    bool valid;
    unsigned long long seq;
    uint32_t phase, start, end;
    char api[32];
    uint8_t before[kF5HostTgtEnd - kF5HostTgtBegin];
};
static Rs64F5HostTgt g_f5_hosttgt_pending;
static unsigned long long g_f5_hosttgt_seq;
static uint32_t g_f5_hosttgt_rows;
static uint64_t g_f5_host_order_seq = 0;
static uint32_t g_f5_host_order_rows = 0;

static bool rs64_f5_shadow_on() {
    static const bool on = [] {
        const char* e = std::getenv("ROGUESQ_LOG_F5_STORE_SHADOW");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (e && *e && *e != '0') || (all && *all && *all != '0');
    }();
    return on;
}

static void rs64_f5_last_writer_update(char width, uint32_t pc,
                                       uint32_t addr, uint32_t value,
                                       uint32_t phase) {
    if (!rs64_f5_shadow_on() || addr < 0x80000000u || addr >= 0x80800000u)
        return;
    rs64_f5_last_writer_ensure();
    const uint32_t span = width == 'D' ? 8u : (width == 'B' ? 1u :
                           (width == 'H' ? 2u : 4u));
    const uint32_t phys = addr & 0x7FFFFFu;
    const uint32_t pre = g_recomp_rdram_for_wp_raw
        ? rs64_f5_read_word(g_recomp_rdram_for_wp_raw, phys) : 0u;
    std::lock_guard<std::mutex> lock(g_f5_vtx_store_mutex);
    if (phase == 5u) {
        Rs64F5PhaseStore& event =
            g_f5_phase_store[g_f5_phase_store_next++ % kF5PhaseStoreCapacity];
        event = {++g_f5_phase_store_seq, phase, phys, span, pc, value,
                 static_cast<uint8_t>(width)};
        if (g_f5_phase_store_count < kF5PhaseStoreCapacity)
            ++g_f5_phase_store_count;
        if (phys < 0x7355D0u && phys + span > 0x735560u &&
            g_f5_target_store_prints < 256u) {
            std::fprintf(stderr,
                "[f5-phase5-target-store] seq=%llu pc=0x%08X addr=0x%08X "
                "phys=0x%06X span=%u width=%c value=0x%08X pre=0x%08X "
                "overlap=0x%06X..0x%06X\n",
                static_cast<unsigned long long>(event.seq), pc, addr, phys,
                span, width, value, pre, std::max(phys, 0x735560u),
                std::min(phys + span, 0x7355D0u));
            ++g_f5_target_store_prints;
            std::fflush(stderr);
        }
    }
    const uint32_t first = phys >> 2u;
    const uint32_t last = (phys + span - 1u) >> 2u;
    for (uint32_t i = first; i <= last && i < 0x200000u; ++i) {
        Rs64F5LastWriter& row = g_f5_last_writer[i];
        row.pc = pc;
        row.value = value;
        row.pre_value = g_recomp_rdram_for_wp_raw
            ? rs64_f5_read_word(g_recomp_rdram_for_wp_raw, phys) : 0u;
        row.post_value = 0;
        row.phase = phase;
        row.width = static_cast<uint8_t>(width);
        row.post_valid = false;
        ++g_f5_last_writer_updates;
    }
}

extern "C" void rs64_floor_writer_post(char, uint32_t, uint32_t);
extern "C" void rs64_f5_store_shadow_post(char width, uint32_t pc,
                                             uint32_t addr) {
    rs64_floor_writer_post(width, pc, addr);
    if (!rs64_f5_shadow_on() || addr < 0x80000000u ||
        addr >= 0x80800000u || !g_recomp_rdram_for_wp_raw) return;
    const uint32_t span = width == 'D' ? 8u : (width == 'B' ? 1u :
                           (width == 'H' ? 2u : 4u));
    const uint32_t phys = addr & 0x7FFFFFu;
    const uint32_t aligned = phys & ~3u;
    const volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
    uint32_t now = rs64_f5_read_word(rd, aligned);
    std::lock_guard<std::mutex> lock(g_f5_vtx_store_mutex);
    rs64_f5_last_writer_ensure();
    const uint32_t first = phys >> 2u;
    const uint32_t last = (phys + span - 1u) >> 2u;
    if (rs64_phase_ord() == 5u && phys < 0x7355D0u &&
        phys + span > 0x735560u && g_f5_target_post_prints < 256u) {
        for (uint32_t i = 0; i < g_f5_phase_store_count; ++i) {
            const uint32_t index = (g_f5_phase_store_next +
                kF5PhaseStoreCapacity - 1u - i) % kF5PhaseStoreCapacity;
            const Rs64F5PhaseStore& event = g_f5_phase_store[index];
            if (event.phase != 5u || event.pc != pc || event.addr != phys ||
                event.span != span) continue;
            std::fprintf(stderr,
                "[f5-phase5-target-post] seq=%llu pc=0x%08X addr=0x%08X "
                "phys=0x%06X span=%u width=%c value=0x%08X pre=0x%08X "
                "post=0x%08X\n",
                static_cast<unsigned long long>(event.seq), pc, addr, phys,
                span, width, event.value, rs64_f5_read_word(rd, phys), now);
            ++g_f5_target_post_prints;
            std::fflush(stderr);
            break;
        }
    }
    for (uint32_t i = first; i <= last && i < 0x200000u; ++i) {
        Rs64F5LastWriter& row = g_f5_last_writer[i];
        if (row.pc == pc && row.phase == rs64_phase_ord()) {
            row.post_value = now;
            row.post_valid = true;
            if (pc == 0x8000D114u && row.phase == 5u &&
                phys >= 0x735560u && phys < 0x7355D0u &&
                g_f5_d114_exact_rows < 64u) {
                std::fprintf(stderr,
                    "[f5-d114-exact] phase=%u pc=0x%08X addr=0x%08X phys=0x%06X "
                    "base=%p width=%c source=0x%08X pre=0x%08X post=0x%08X "
                    "aligned=0x%06X endian=be-word\n",
                    row.phase, pc, addr, phys, (const void*)rd,
                    width, row.value, row.pre_value, now, aligned);
                ++g_f5_d114_exact_rows;
                std::fflush(stderr);
            }
        }
    }
}

static void rs64_f5_dump_join(uint32_t phase, uint32_t source, uint32_t bytes,
                              uint32_t task, uint32_t vtx_pc,
                              const uint8_t* rdram) {
    if (!rs64_f5_shadow_on() || phase < 6u || !rdram ||
        source >= 0x800000u || bytes == 0 || bytes > 0x800000u - source)
        return;
    rs64_f5_last_writer_ensure();
    std::lock_guard<std::mutex> lock(g_f5_vtx_store_mutex);
    uint32_t rows = 0, written = 0, red = 0;
    const uint32_t snapshot = std::min(bytes, 32u);
    uint8_t registration[32] = {};
    uint32_t dma_events = 0, dma_source = 0, dma_len = 0, dma_dmem = 0;
    uint32_t dma_fnv = 0, dma_red_words = 0;
    uint32_t phase5_dma_events = 0;
    uint32_t phase5_store_events = 0;
    uint32_t phase5_red_store_events = 0;
    uint32_t phase5_first_store_pc = 0;
    uint32_t phase5_first_store_value = 0;
    for (Rs64F5VtxStoreRange& row : g_f5_vtx_store_ranges) {
        if (row.phase == phase && row.source == source && row.end == source + bytes) {
            std::memcpy(registration, row.registration, sizeof registration);
            dma_events = row.dma_events;
            dma_source = row.last_dma_source;
            dma_len = row.last_dma_len;
            dma_dmem = row.last_dma_dmem;
            dma_fnv = row.last_dma_fnv;
            dma_red_words = row.last_dma_red_words;
            break;
        }
    }
    for (uint32_t i = 0; i < g_f5_phase_dma_count; ++i) {
        const Rs64F5PhaseDma& dma = g_f5_phase_dma[i];
        if (dma.phase == 5u && dma.start < source + bytes && dma.end > source)
            ++phase5_dma_events;
    }
    for (uint32_t i = 0; i < g_f5_phase_store_count; ++i) {
        const uint32_t oldest =
            (g_f5_phase_store_next + kF5PhaseStoreCapacity -
             g_f5_phase_store_count) % kF5PhaseStoreCapacity;
        const Rs64F5PhaseStore& store =
            g_f5_phase_store[(oldest + i) % kF5PhaseStoreCapacity];
        if (store.phase != 5u || store.addr >= source + bytes ||
            store.addr + store.span <= source) continue;
        ++phase5_store_events;
        if (!phase5_first_store_pc) {
            phase5_first_store_pc = store.pc;
            phase5_first_store_value = store.value;
        }
        const uint32_t v = store.value;
        if (((v >> 24) & 0xFFu) == 0xFFu || ((v >> 16) & 0xFFu) == 0xFFu ||
            ((v >> 8) & 0xFFu) == 0xFFu) ++phase5_red_store_events;
        if (g_f5_phase_store_prints++ < 128u) {
            std::fprintf(stderr,
                "[f5-phase5-store] addr=0x%06X span=%u width=%c "
                "pc=0x%08X value=0x%08X overlap=0x%06X..0x%06X\n",
                store.addr, store.span, store.width ? char(store.width) : '-',
                store.pc, store.value, std::max(store.addr, source),
                std::min(store.addr + store.span, source + bytes));
        }
    }
    // The ring records event order, but a busy phase can wrap it before the
    // VTX command arrives. The per-word last-writer table is the phase-boundary
    // snapshot for lanes that have not been overwritten in a later phase.
    if (phase5_store_events == 0u) {
        for (uint32_t p = source; p < source + bytes; p += 4u) {
            const Rs64F5LastWriter& store = g_f5_last_writer[p >> 2u];
            if (store.phase != 5u || !store.pc) continue;
            const uint32_t boundary =
                (uint32_t(rdram[p ^ 3u]) << 24) |
                (uint32_t(rdram[(p + 1u) ^ 3u]) << 16) |
                (uint32_t(rdram[(p + 2u) ^ 3u]) << 8) |
                uint32_t(rdram[(p + 3u) ^ 3u]);
            ++phase5_store_events;
            if (!phase5_first_store_pc) {
                phase5_first_store_pc = store.pc;
                phase5_first_store_value = store.value;
            }
            if (((boundary >> 24) & 0xFFu) == 0xFFu ||
                ((boundary >> 16) & 0xFFu) == 0xFFu ||
                ((boundary >> 8) & 0xFFu) == 0xFFu)
                ++phase5_red_store_events;
            if (g_f5_phase_store_prints++ < 128u) {
                std::fprintf(stderr,
                    "[f5-phase5-snapshot] addr=0x%06X span=4 width=%c "
                    "pc=0x%08X value=0x%08X boundary=0x%08X\n",
                    p, store.width ? char(store.width) : '-', store.pc,
                    store.value, boundary);
            }
        }
    }
    std::fprintf(stderr,
        "[f5-source-transition] phase=%u task=%u vtx=0x%06X..0x%06X registered=",
        phase, task, source, source + bytes);
    for (uint32_t i = 0; i < snapshot; ++i) std::fprintf(stderr, "%02X", registration[i]);
    std::fprintf(stderr, " read=");
    for (uint32_t i = 0; i < snapshot; ++i) std::fprintf(stderr, "%02X", rdram[(source + i) ^ 3u]);
    std::fprintf(stderr, " dma_events=%u phase5_dma_events=%u phase5_store_events=%u phase5_red_store_events=%u first_store_pc=0x%08X first_store_value=0x%08X last_dma=0x%06X..0x%06X dmem=0x%03X fnv=%08X red_words=%u\n",
                 dma_events, phase5_dma_events, phase5_store_events,
                 phase5_red_store_events, phase5_first_store_pc,
                 phase5_first_store_value,
                 dma_source, dma_source + dma_len, dma_dmem,
                 dma_fnv, dma_red_words);
    for (uint32_t p = source; p < source + bytes; p += 4u) {
        const Rs64F5LastWriter& w = g_f5_last_writer[p >> 2u];
        const uint32_t now = (uint32_t(rdram[p ^ 3u]) << 24) |
                             (uint32_t(rdram[(p + 1u) ^ 3u]) << 16) |
                             (uint32_t(rdram[(p + 2u) ^ 3u]) << 8) |
                             uint32_t(rdram[(p + 3u) ^ 3u]);
        if (w.pc) ++written;
        if (((now >> 24) & 0xFFu) == 0xFFu || ((now >> 16) & 0xFFu) == 0xFFu ||
            ((now >> 8) & 0xFFu) == 0xFFu) ++red;
        if (rows++ < 24u) {
            std::fprintf(stderr,
                "[f5-vtx-join] phase=%u task=%u vtx_pc=0x%06X phys=0x%06X "
                "bytes=0x%08X last_pc=0x%08X last_w=%c last_phase=%u "
                "last_val=0x%08X post=%s0x%08X now=0x%08X\n",
                phase, task, vtx_pc & 0x7FFFFFu, p, bytes, w.pc,
                w.width ? char(w.width) : '-', w.phase, w.value,
                w.post_valid ? "" : "?", w.post_value, now);
        }
    }
    std::fprintf(stderr,
        "[f5-vtx-join-summary] phase=%u task=%u source=0x%06X bytes=0x%X "
        "words=%u written=%u red_words=%u shadow_updates=%u\n",
        phase, task, source, bytes, rows, written, red, g_f5_last_writer_updates);
    std::fflush(stderr);
}

extern "C" void rs64_f5_host_bulk_shadow(uint32_t phys, uint32_t len,
                                           const char* api) {
    if (!rs64_f5_shadow_on() || len == 0u) return;
    if (!g_f5_bulk_control) {
        std::fprintf(stderr, "[f5-bulk-control] api=%s phys=0x%06X len=0x%X\n",
                     api ? api : "?", phys & 0x7FFFFFu, len);
        std::fflush(stderr);
        g_f5_bulk_control = 1;
    }
    const uint32_t start = phys & 0x7FFFFFu;
    const uint32_t end = std::min(start + len, 0x800000u);
    std::lock_guard<std::mutex> lock(g_f5_vtx_store_mutex);
    for (Rs64F5VtxStoreRange& row : g_f5_vtx_store_ranges) {
        if (!row.end || start >= row.end || end <= row.source) continue;
        if (g_f5_bulk_rows++ >= 64u) return;
        std::fprintf(stderr,
            "[f5-bulk-overlap] n=%u api=%s phase=%u task=%u bulk=0x%06X..0x%06X "
            "vtx=0x%06X..0x%06X\n", g_f5_bulk_rows, api ? api : "?",
            row.phase, row.task, start, end, row.source, row.end);
        std::fflush(stderr);
    }
}

extern "C" void rs64_floor_writer_begin(const uint8_t*, uint32_t, uint32_t, const char*);
extern "C" void rs64_floor_writer_after(const uint8_t*, uint32_t, uint32_t, const char*);
extern "C" void rs64_f5_host_write_begin(const uint8_t* rdram, uint32_t phys,
                                           uint32_t len, const char* api) {
    rs64_floor_writer_begin(rdram, phys, len, api);
    if (!rs64_f5_shadow_on() || !rdram || len == 0u) return;
    const uint32_t start = phys & 0x7FFFFFu;
    const uint32_t end = std::min(start + len, 0x800000u);
    std::lock_guard<std::mutex> lock(g_f5_vtx_store_mutex);
    // s6349: fixed target-range host-write census, independent of the VTX
    // range registry (which only fills at phase 6, after the red is present).
    {
        static uint32_t calls = 0;
        if (!calls++)
            std::fprintf(stderr, "[f5-hosttgt-control] first host write api=%s phys=0x%06X len=0x%X phase=%u\n",
                         api ? api : "?", start, end - start, rs64_phase_ord());
        if (start < kF5HostTgtEnd && end > kF5HostTgtBegin) {
            g_f5_hosttgt_pending = {};
            g_f5_hosttgt_pending.valid = true;
            g_f5_hosttgt_pending.seq = ++g_f5_hosttgt_seq;
            g_f5_hosttgt_pending.phase = rs64_phase_ord();
            g_f5_hosttgt_pending.start = start;
            g_f5_hosttgt_pending.end = end;
            std::snprintf(g_f5_hosttgt_pending.api, sizeof g_f5_hosttgt_pending.api,
                          "%s", api ? api : "?");
            for (uint32_t i = 0; i < kF5HostTgtEnd - kF5HostTgtBegin; ++i)
                g_f5_hosttgt_pending.before[i] = rdram[(kF5HostTgtBegin + i) ^ 3u];
        }
    }
    for (const Rs64F5VtxStoreRange& row : g_f5_vtx_store_ranges) {
        if (!row.end || start >= row.end || end <= row.source) continue;
        const uint32_t first = std::max(start, row.source);
        const uint32_t last = std::min(end, row.end);
        const uint32_t sample = std::min(last - first, 32u);
        g_f5_host_order_pending = {};
        g_f5_host_order_pending.seq = ++g_f5_host_order_seq;
        g_f5_host_order_pending.phys = start;
        g_f5_host_order_pending.len = end - start;
        g_f5_host_order_pending.overlap = first;
        g_f5_host_order_pending.sample_len = sample;
        std::snprintf(g_f5_host_order_pending.api,
                      sizeof g_f5_host_order_pending.api, "%s", api ? api : "?");
        for (uint32_t i = 0; i < sample; ++i)
            g_f5_host_order_pending.before[i] = rdram[(first + i) ^ 3u];
        g_f5_host_order_pending.valid = true;
        return;
    }
}

extern "C" void rs64_f5_host_write_after(const uint8_t* rdram, uint32_t phys,
                                           uint32_t len, const char* api) {
    rs64_floor_writer_after(rdram, phys, len, api);
    if (!rs64_f5_shadow_on() || !rdram || len == 0u) return;
    std::lock_guard<std::mutex> lock(g_f5_vtx_store_mutex);
    if (g_f5_hosttgt_pending.valid) {
        Rs64F5HostTgt& t = g_f5_hosttgt_pending;
        t.valid = false;
        if (t.start == (phys & 0x7FFFFFu) && g_f5_hosttgt_rows++ < 96u) {
            const uint32_t n = kF5HostTgtEnd - kF5HostTgtBegin;
            uint32_t changed = 0, red_before = 0, red_after = 0;
            uint8_t after[kF5HostTgtEnd - kF5HostTgtBegin];
            for (uint32_t i = 0; i < n; ++i) {
                after[i] = rdram[(kF5HostTgtBegin + i) ^ 3u];
                changed += after[i] != t.before[i];
                red_before += t.before[i] == 0xFFu;
                red_after += after[i] == 0xFFu;
            }
            std::fprintf(stderr,
                "[f5-hosttgt] seq=%llu api=%s phase=%u write=0x%06X..0x%06X "
                "changed=%u ff_before=%u ff_after=%u before=",
                (unsigned long long)t.seq, t.api, t.phase, t.start, t.end,
                changed, red_before, red_after);
            for (uint32_t i = 0; i < n; ++i) std::fprintf(stderr, "%02X", t.before[i]);
            std::fprintf(stderr, " after=");
            for (uint32_t i = 0; i < n; ++i) std::fprintf(stderr, "%02X", after[i]);
            std::fprintf(stderr, "\n");
            std::fflush(stderr);
        }
    }
    Rs64F5HostOrderPending& p = g_f5_host_order_pending;
    if (!p.valid || p.phys != (phys & 0x7FFFFFu) || p.len != len) return;
    bool red = false;
    for (uint32_t i = 0; i < p.sample_len; ++i) {
        const uint8_t v = rdram[(p.overlap + i) ^ 3u];
        red |= v == 0xFFu;
    }
    if (!red || g_f5_host_order_rows++ >= 128u) {
        p.valid = false;
        return;
    }
    std::fprintf(stderr, "[f5-host-order] seq=%llu api=%s phys=0x%06X len=0x%X "
                 "overlap=0x%06X sample=%u phase=%u before=",
                 (unsigned long long)p.seq, api ? api : p.api, p.phys, p.len,
                 p.overlap, p.sample_len, rs64_phase_ord());
    for (uint32_t i = 0; i < p.sample_len; ++i)
        std::fprintf(stderr, "%02X", p.before[i]);
    std::fprintf(stderr, " after=");
    for (uint32_t i = 0; i < p.sample_len; ++i)
        std::fprintf(stderr, "%02X", rdram[(p.overlap + i) ^ 3u]);
    std::fprintf(stderr, "\n");
    std::fflush(stderr);
    p.valid = false;
}

extern "C" void rs64_f5_host_bulk_payload(uint32_t phys, uint32_t len,
                                             uint32_t dmem_addr) {
    if (!rs64_f5_shadow_on() || len == 0u) return;
    const uint32_t start = phys & 0x7FFFFFu;
    const uint32_t end = std::min(start + len, 0x800000u);
    const uint32_t phase = rs64_phase_ord();
    // s7363 (class AN): the slot check-and-increment runs under the store mutex (before s7363 it was taken only after this block), so two RSP
    // DMA callers cannot both pass `count < 512` at 511 and write g_f5_phase_dma[512].
    std::lock_guard<std::mutex> lock(g_f5_vtx_store_mutex);
    if (phase == 5u && g_f5_phase_dma_count < 512u) {
        Rs64F5PhaseDma& dma = g_f5_phase_dma[g_f5_phase_dma_count++];
        dma.phase = phase;
        dma.start = start;
        dma.end = end;
        dma.dmem = dmem_addr;
        dma.fnv = 2166136261u;
        dma.red_words = 0u;
        const uint32_t sample = std::min(len, 0x1000u);
        for (uint32_t i = 0; i < sample; ++i)
            dma.fnv = (dma.fnv * 16777619u) ^
                g_dmem_cur[((dmem_addr + i) & 0xFFFu) ^ 3u];
        for (uint32_t i = 0; i + 2u < sample; i += 4u) {
            const uint8_t r = g_dmem_cur[((dmem_addr + i) & 0xFFFu) ^ 3u];
            const uint8_t g = g_dmem_cur[((dmem_addr + i + 1u) & 0xFFFu) ^ 3u];
            const uint8_t b = g_dmem_cur[((dmem_addr + i + 2u) & 0xFFFu) ^ 3u];
            dma.red_words += r == 0xFFu && (g == 0u || b == 0u);
        }
    }
    static uint32_t rows = 0;
    for (Rs64F5VtxStoreRange& row : g_f5_vtx_store_ranges) {
        if (!row.end || start >= row.end || end <= row.source) continue;
        if (rows++ >= 64u) return;
        const uint32_t first = std::max(start, row.source);
        const uint32_t last = std::min(end, row.end);
        uint32_t fnv = 2166136261u, nonzero = 0u, red = 0u;
        for (uint32_t p = first; p < last; ++p) {
            const uint32_t off = p - start;
            const uint8_t b = g_dmem_cur[((dmem_addr + off) & 0xFFFu) ^ 3u];
            fnv = (fnv * 16777619u) ^ b;
            nonzero += b != 0u;
        }
        for (uint32_t p = first; p + 2u < last; p += 4u) {
            const uint32_t off = p - start;
            const uint8_t r = g_dmem_cur[((dmem_addr + off) & 0xFFFu) ^ 3u];
            const uint8_t g = g_dmem_cur[((dmem_addr + off + 1u) & 0xFFFu) ^ 3u];
            const uint8_t b = g_dmem_cur[((dmem_addr + off + 2u) & 0xFFFu) ^ 3u];
            red += r == 0xFFu && (g == 0u || b == 0u);
        }
        row.dma_events++;
        row.last_dma_source = start;
        row.last_dma_len = end - start;
        row.last_dma_dmem = dmem_addr;
        row.last_dma_fnv = fnv;
        row.last_dma_red_words = red;
        std::fprintf(stderr,
            "[f5-bulk-payload] n=%u phase=%u task=%u bulk=0x%06X..0x%06X "
            "dmem=0x%03X vtx=0x%06X..0x%06X lanes=0x%06X..0x%06X "
            "fnv=%08X nonzero=%u red_words=%u bytes=",
            rows, row.phase, row.task, start, end, dmem_addr, row.source,
            row.end, first, last, fnv, nonzero, red);
        const uint32_t dump = std::min(last - first, 64u);
        for (uint32_t i = 0; i < dump; ++i) {
            const uint32_t off = first - start + i;
            std::fprintf(stderr, "%02X", (unsigned)g_dmem_cur[((dmem_addr + off) & 0xFFFu) ^ 3u]);
        }
        if (dump < last - first) std::fprintf(stderr, "...");
        std::fprintf(stderr, "\n");
    }
    std::fflush(stderr);
}

extern "C" void rs64_f5_vtx_store_range(uint32_t phase, uint32_t source,
                                           uint32_t bytes, uint32_t task,
                                           uint32_t pc) {
    const char* e = std::getenv("ROGUESQ_LOG_F5_STORE_SHADOW");
    const char* all = std::getenv("ROGUESQ_LOG_ALL");
    if (!((e && *e && *e != '0') || (all && *all && *all != '0')) ||
        phase < 6u) return;
    if (bytes == 0 || source >= 0x800000u || bytes > 0x800000u - source)
        return;
    std::lock_guard<std::mutex> lock(g_f5_vtx_store_mutex);
    Rs64F5VtxStoreRange& row =
        g_f5_vtx_store_ranges[g_f5_vtx_store_range_next++ % 128u];
    row = {phase, source, source + bytes, task, pc & 0x7FFFFFu};
    if (g_recomp_rdram_for_wp_raw) {
        const uint32_t snapshot = std::min(bytes, 32u);
        for (uint32_t i = 0; i < snapshot; ++i)
            row.registration[i] = g_recomp_rdram_for_wp_raw[(source + i) ^ 3u];
    }
}

extern "C" void rs64_f5_store_shadow(char width, uint32_t pc,
                                       uint32_t addr, uint32_t value) {
    static int enabled = -1;
    static uint32_t control = 0;
    static uint32_t rows = 0;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_F5_STORE_SHADOW");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && *e && *e != '0') ||
                   (all && *all && *all != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t phase = rs64_phase_ord();
    rs64_f5_last_writer_update(width, pc, addr, value, phase);
    const uint32_t phys = addr & 0x7FFFFFu;
    const uint32_t span = width == 'D' ? 8u : (width == 'B' ? 1u :
                           (width == 'H' ? 2u : 4u));
    if (addr == 0x801E8710u && !control) {
        std::fprintf(stderr,
            "[f5-store-shadow-control] phase=%u pc=0x%08X addr=0x%08X value=0x%08X\n",
            phase, pc, addr, value);
        std::fflush(stderr);
        control = 1;
    }
    if (phase < 6u) return;
    std::lock_guard<std::mutex> lock(g_f5_vtx_store_mutex);
    for (const Rs64F5VtxStoreRange& row : g_f5_vtx_store_ranges) {
        if (row.end == 0 || row.phase != phase || phys >= row.end ||
            phys + span <= row.source) continue;
        if (rows++ >= 512u) return;
        std::fprintf(stderr,
            "[f5-store-shadow] n=%u phase=%u vtx=0x%06X..0x%06X task=%u "
            "vtx_pc=0x%06X store_pc=0x%08X addr=0x%08X phys=0x%06X "
            "width=%c value=0x%08X overlap=0x%06X..0x%06X\n",
            rows, phase, row.source, row.end, row.task, row.pc, pc, addr,
            phys, width, value, std::max(phys, row.source),
            std::min(phys + span, row.end));
        std::fflush(stderr);
    }
}

static void rs64_f5_vtxcolor_state(uint32_t pc, uint32_t source, uint32_t ordinal) {
    std::lock_guard<std::mutex> lock(g_f5_vtxcolor_mutex);
    g_f5_vtxcolor_state.task = g_e9prov.task;
    g_f5_vtxcolor_state.ordinal = ordinal;
    g_f5_vtxcolor_state.pc = pc & 0x7FFFFFu;
    g_f5_vtxcolor_state.source = source & 0x7FFFFFu;
    g_f5_vtxcolor_state.valid = true;
}

extern "C" void rs64_e9prov_aligned(uint32_t task, uint32_t guestDl,
                                      uint32_t guestE9) {
    const uint32_t current = g_e9prov.task;
    if (log_e9_unified() && guestE9 != 0) {
        const uint32_t line = g_e9prov_nonzero_callback_lines.fetch_add(1, std::memory_order_relaxed);
        if (line < 128) {
            fprintf(stderr, "[e9-callback-nonzero] passed=%u current=%u guest_dl=0x%08X aligned=%u\n",
                    task, current, guestDl, guestE9);
            fflush(stderr);
        }
    }
    if (log_e9_unified() && (task <= 4 || g_e9prov.target)) {
        const uint32_t line = g_e9prov_join_lines.fetch_add(1, std::memory_order_relaxed);
        if (line < 96) {
            fprintf(stderr, "[e9-join-callback] passed=%u current=%u guest_dl=0x%08X aligned=%u\n",
                    task, current, guestDl, guestE9);
            fflush(stderr);
        }
    }
    if (current != task) return;
    g_e9prov.aligned = guestE9;
    g_e9prov.aligned_dl = guestDl;
}

extern "C" void rs64_e9prov_task_begin(uint32_t task, uint32_t root_dl,
                                        const uint8_t *rdram, uint32_t ucode_addr) {
    g_e9prov = {};
    if (dlwalk_on()) { g_dlw = {}; g_dlw.task = task; }
    {
        std::lock_guard<std::mutex> lock(g_f5_vtxcolor_mutex);
        g_f5_vtxcolor_state = {};
        g_f5_vtxcolor_state.task = 0xFFFFFFFFu;
    }
    g_e9prov.task = task;
    g_e9prov.root_dl = root_dl & 0x007FFFFFu;
    uint32_t image = 2166136261u;
    const uint32_t image_base = ucode_addr & 0x007FFFF8u;
    // s7068: the 4 KB ucode-image FNV is read only by the M4 norm rows (ROGUESQ_LOG_M4_NORM) and e9prov logs;
    // skip it per gfx task when neither is on. ROGUESQ_DIAG_GATE=0 restores the always-hash path.
    static const bool s7068_gate = [] { const char *e = std::getenv("ROGUESQ_DIAG_GATE"); return !(e && *e == '0'); }();
    if (rdram && image_base < 0x007FF000u && (!s7068_gate || rs64_m4_norm_enabled() || log_e9_provenance())) {
        for (uint32_t i = 0; i < 0x1000u; ++i) {
            image ^= rdram[(image_base + i) ^ 3u];
            image *= 16777619u;
        }
    }
    g_e9prov.m4_image = image;
    g_task_bridge_e9.store(0, std::memory_order_release);
    g_task_synthetic_fullsyncs.store(0, std::memory_order_release);
    g_e9_boundary_lines = 0;
    uint32_t remaining = g_e9prov_latch_remaining.load(std::memory_order_acquire);
    while (remaining != 0 && !g_e9prov_latch_remaining.compare_exchange_weak(
        remaining, remaining - 1, std::memory_order_acq_rel, std::memory_order_acquire)) {}
    g_e9prov.target = remaining != 0;
    g_e9prov.control = task <= 4;
    g_e9prov.first_guest = 0xFFFFFFFFu;
    g_e9prov.first_emit = 0xFFFFFFFFu;
    g_inline_probe = {};
    const uint32_t phase = rs64_phase_ord();
    uint32_t previous = g_inline_probe_phase.load(std::memory_order_acquire);
    if (previous != phase && g_inline_probe_phase.compare_exchange_strong(
            previous, phase, std::memory_order_acq_rel, std::memory_order_acquire)) {
        g_inline_probe_lines.store(0, std::memory_order_release);
        g_inline_probe_route_lines.store(0, std::memory_order_release);
        g_inline_probe_trigen_entry_lines.store(0, std::memory_order_release);
        g_inline_probe_trigen_reload_lines.store(0, std::memory_order_release);
        for (auto &lines : g_inline_probe_trigen_exit_lines) lines.store(0, std::memory_order_release);
        g_inline_probe_trigen_source_lines.store(0, std::memory_order_release);
        g_inline_probe_trigen_chunk_lines.store(0, std::memory_order_release);
        g_inline_probe_trigen_pairs.store(0, std::memory_order_release);
        g_inline_probe_trigen_boot_lines.store(0, std::memory_order_release);
        g_inline_probe_summaries.store(0, std::memory_order_release);
        g_e9prov_join_lines.store(0, std::memory_order_release);
    }
}

extern "C" void rs64_inline_probe_resume(uint32_t r17) {
    if (!log_inline_advance() || !g_inline_probe.active) return;
    const uint32_t slot = inline_probe_slot(g_inline_probe.opcode);
    const uint32_t actual = (r17 - g_inline_probe.entry) & 0x7FFFFFu;
    ++g_inline_probe.samples[slot];
    if (actual != g_inline_probe.expected_extra) ++g_inline_probe.mismatch[slot];
    const uint32_t line = g_inline_probe_lines.fetch_add(1, std::memory_order_relaxed);
    if (line < 96) {
        fprintf(stderr, "[inline-advance] task=%u phase=%u op=%02X table=%u:0x%04X entry=0x%06X exit=0x%06X extra=%u expected=%u verdict=%s\n",
                g_e9prov.task, rs64_phase_ord(), g_inline_probe.opcode, g_inline_probe.table_kind,
                g_inline_probe.table_word, g_inline_probe.entry & 0x7FFFFFu,
                r17 & 0x7FFFFFu, actual, g_inline_probe.expected_extra,
                actual == g_inline_probe.expected_extra ? "equal" : "MISMATCH");
        fflush(stderr);
    }
    g_inline_probe.active = false;
}

extern "C" void rs64_inline_probe_dispatch(uint32_t r17, uint32_t w0, uint32_t table_kind, uint32_t table_word) {
    if (!log_inline_advance()) return;
    const uint32_t opcode = w0 >> 24;
    const uint32_t slot = inline_probe_slot(opcode);
    if (slot == 0) return;
    g_inline_probe.active = true;
    g_inline_probe.opcode = opcode;
    g_inline_probe.entry = r17;
    g_inline_probe.table_kind = table_kind;
    g_inline_probe.table_word = table_word;
    g_inline_probe.expected_extra = opcode == 0x03 ? 16 : opcode == 0x05 ? 32 :
        (opcode == 0xB4 || opcode == 0xBF) ? ((w0 & 2) ? 16 : 0) :
        opcode == 0xBD ? 16 : 8;
}

extern "C" void rs64_m4_index_probe(uint32_t kind, uint32_t slot,
                                      uint32_t p0, uint32_t p1, uint32_t p2,
                                      uint32_t index, uint32_t masked,
                                      uint32_t c0, uint32_t c1, uint32_t c2);

extern "C" void rs64_f5_state_probe(uint32_t r17, uint32_t w0, uint32_t w1) {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_F5_STATE");
        return e && *e && *e != '0';
    }();
    if (!enabled) return;
    const uint32_t opcode = w0 >> 24;

    rs64_m4_index_probe(0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t fetch_n = 0;
    static uint32_t n02 = 0;
    static uint32_t n03 = 0;
    static uint32_t payload_ordinal = 0;
    static uint32_t task_seen = 0xFFFFFFFFu;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        if (phase_seen != 0xFFFFFFFFu) {
            fprintf(stderr, "[f5-state-summary] phase=%u op02=%u op03=%u\n",
                    phase_seen, n02, n03);
        }
        phase_seen = phase;
        fetch_n = 0;
        n02 = 0;
        n03 = 0;
        payload_ordinal = 0;
    }
    if (g_e9prov.task != task_seen) {
        task_seen = g_e9prov.task;
        payload_ordinal = 0;
    }
    ++fetch_n;
    if (fetch_n <= 4) {
        fprintf(stderr, "[f5-fetch-control] phase=%u n=%u op=0x%02X w0=0x%08X w1=0x%08X\n",
                phase, fetch_n, opcode, w0, w1);
        fflush(stderr);
    }
    if (opcode != 0x02 && opcode != 0x03) return;
    uint32_t &count = opcode == 0x02 ? n02 : n03;
    ++count;
    const uint32_t ordinal = opcode == 0x02 ? ++payload_ordinal : 0;
    if (opcode == 0x02)
        rs64_f5_vtxcolor_state(r17, w1 & 0x7FFFFFu, ordinal);
    if (count <= 24) {
        fprintf(stderr,
                "[f5-state-control] phase=%u op=0x%02X n=%u r17=0x%06X "
                "w0=0x%08X w1=0x%08X idx=0x%02X\n",
                phase, opcode, count, r17 & 0x7FFFFFu, w0, w1,
                (w0 >> 16) & 0xFFu);
        const uint32_t source = opcode == 0x02 ? (w1 & 0x7FFFFFu) :
            ((r17 + 8u) & 0x7FFFFFu);
        fprintf(stderr, "[f5-state-payload] phase=%u task=%u root_dl=0x%06X ord=%u pc=0x%06X op=0x%02X source=0x%06X bytes=",
                phase, g_e9prov.task, g_e9prov.root_dl, ordinal, r17 & 0x7FFFFFu, opcode, source);
        if (g_rdram_for_submit != nullptr && source + 16u <= 0x800000u) {
            for (uint32_t i = 0; i < 16; ++i)
                fprintf(stderr, "%02X", (unsigned)g_rdram_for_submit[(source + i) ^ 3]);
        } else {
            fprintf(stderr, "OUT_OF_RANGE");
        }
        fputc('\n', stderr);
        fflush(stderr);
    }
}

extern "C" void rs64_f5_vtx_probe(uint32_t pc, uint32_t w0, uint32_t w1,
                                    const uint8_t *rdram) {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_F5_VTX");
        return e && *e && *e != '0';
    }();
    if (!enabled || !rdram) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t lines = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        lines = 0;
        std::fprintf(stderr, "[f5-vtx-control] phase=%u task=%u\n", phase, g_e9prov.task);
    }
    if (lines++ >= 64) return;
    const uint32_t count = (w0 >> 12) & 0xFFu;
    const uint32_t first = (w0 >> 1) & 0x7Fu;
    const uint32_t source = w1 & 0x7FFFFFu;
    const uint32_t bytes = count * 16u;
    rs64_f5_vtx_store_range(phase, source, bytes, g_e9prov.task, pc);
    rs64_f5_dump_join(phase, source, bytes, g_e9prov.task, pc, rdram);
    std::fprintf(stderr,
                 "[f5-vtx] phase=%u task=%u pc=0x%06X w0=0x%08X w1=0x%08X "
                 "first=%u count=%u source=0x%06X end=0x%06X bytes=",
                 phase, g_e9prov.task, pc & 0x7FFFFFu, w0, w1, first, count,
                 source, source + bytes);
    const uint32_t dump = std::min(count, 4u) * 16u;
    if (source + dump <= 0x800000u) {
        for (uint32_t i = 0; i < dump; ++i)
            std::fprintf(stderr, "%02X", (unsigned)rdram[(source + i) ^ 3]);
    } else {
        std::fprintf(stderr, "OUT_OF_RANGE");
    }
    std::fprintf(stderr, "\n");
    std::fflush(stderr);
}

extern "C" void rs64_m4_index_probe(uint32_t kind, uint32_t slot,
                                      uint32_t p0, uint32_t p1, uint32_t p2,
                                      uint32_t index, uint32_t masked,
                                      uint32_t c0, uint32_t c1, uint32_t c2) {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_M4_INDEX");
        return e && *e && *e != '0';
    }();
    if (!enabled) return;
    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t lines = 0;
    if (phase != phase_seen) {
        phase_seen = phase;
        lines = 0;
        fprintf(stderr, "[m4-index-control] phase=%u width=%u origin=0x%06X task=%u\n",
                phase, width, origin, g_e9prov.task);
    }
    if (lines++ >= 256) return;
    if (kind == 0) {
        fprintf(stderr, "[m4-index-control] phase=%u width=%u origin=0x%06X task=%u\n",
                phase, width, origin, g_e9prov.task);
    } else if (kind == 1) {
        fprintf(stderr, "[m4-index] phase=%u task=%u kind=producer slot=0x%X p=0x%X/0x%X/0x%X\n",
                phase, g_e9prov.task, slot, p0, p1, p2);
    } else {
        fprintf(stderr, "[m4-index] phase=%u task=%u kind=consumer index=0x%02X masked=0x%02X c=0x%X/0x%X/0x%X source=0x%X/0x%X/0x%X\n",
                phase, g_e9prov.task, index, masked, c0, c1, c2, p0, p1, p2);
    }
    fflush(stderr);
}

extern "C" void rs64_m4_branch_probe(uint32_t r3, uint32_t r4,
                                      uint32_t expected, uint32_t resident,
                                      uint32_t target) {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_M4_INDEX");
        return e && *e && *e != '0';
    }();
    if (!enabled) return;
    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    const bool title = width == 1024 && origin == 0x00790400u;
    const bool hangar = width == 512 && (origin == 0x006AB400u || origin == 0x006AB800u);
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t lines = 0;
    if (phase != phase_seen) {
        phase_seen = phase;
        lines = 0;
        fprintf(stderr, "[m4-route-control] phase=%u width=%u origin=0x%06X task=%u resident=0x%02X target=0x%04X\n",
                phase, width, origin, g_e9prov.task, resident, target);
    }
    if (lines++ >= 256) return;
    fprintf(stderr, "[m4-route] phase=%u task=%u r3=0x%02X r4=0x%X expected=0x%X taken=%u\n",
            phase, g_e9prov.task, r3 & 0xFFu, r4, expected,
            r4 == expected ? 1u : 0u);
    fflush(stderr);
}

extern "C" void rs64_inline_probe_route(uint32_t r17, uint32_t target, uint32_t line) {
    if (!log_inline_advance() || !g_inline_probe.active || g_inline_probe.opcode != 0x05) return;
    const uint32_t line_no = g_inline_probe_route_lines.fetch_add(1, std::memory_order_relaxed);
    if (line_no < 96) {
        fprintf(stderr, "[inline-route] task=%u phase=%u op=05 table=%u:0x%04X entry=0x%06X target=0x%04X line=%u\n",
                g_e9prov.task, rs64_phase_ord(), g_inline_probe.table_kind, g_inline_probe.table_word,
                r17 & 0x7FFFFFu, target, line);
        fflush(stderr);
    }
}

extern "C" void rs64_inline_probe_step(uint32_t r17, uint32_t delta, uint32_t site) {
    if (!log_inline_advance() || !g_inline_probe.active) return;
    if (g_inline_probe.opcode != 0xB4 && g_inline_probe.opcode != 0xBF) return;
    const uint32_t line = g_inline_probe_lines.fetch_add(1, std::memory_order_relaxed);
    if (line < 96) {
        fprintf(stderr, "[inline-step] task=%u phase=%u op=%02X table=%u:0x%04X site=%04X r17=0x%06X delta=%u\n",
                g_e9prov.task, rs64_phase_ord(), g_inline_probe.opcode, g_inline_probe.table_kind,
                g_inline_probe.table_word, site, r17 & 0x7FFFFFu, delta);
        fflush(stderr);
    }
}

extern "C" void rs64_inline_probe_overlay(uint32_t r17, uint32_t selector) {
    if (!log_inline_advance() || !g_inline_probe.active || g_inline_probe.opcode != 0x05) return;
    const uint32_t line = g_inline_probe_route_lines.fetch_add(1, std::memory_order_relaxed);
    if (line < 96) {
        fprintf(stderr, "[inline-overlay] task=%u phase=%u op=05 table=%u:0x%04X entry=0x%06X selector=0x%X path=L_15AC\n",
                g_e9prov.task, rs64_phase_ord(), g_inline_probe.table_kind, g_inline_probe.table_word,
                r17 & 0x7FFFFFu, selector);
        fflush(stderr);
    }
}

extern "C" void rs64_inline_probe_trigen_entry(uint32_t r17) {
    if (!log_inline_advance() || !g_inline_probe.active || g_inline_probe.opcode != 0x05) return;
    const uint32_t line = g_inline_probe_trigen_entry_lines.fetch_add(1, std::memory_order_relaxed);
    if (line < 16) {
        fprintf(stderr, "[inline-trigen-entry] task=%u phase=%u entry=0x%06X l1db0=0x%06X\n",
                g_e9prov.task, rs64_phase_ord(), g_inline_probe.entry & 0x7FFFFFu, r17 & 0x7FFFFFu);
        fflush(stderr);
    }
}

static std::atomic<uint32_t> g_inline_probe_trigen_staged_dram{0};
static std::atomic<uint32_t> g_inline_probe_trigen_boot_130{0};
static std::atomic<uint32_t> g_inline_probe_trigen_post_130{0};
static std::atomic<uint32_t> g_inline_probe_trigen_skip_130{0};

extern "C" void rs64_inline_probe_trigen_stage(uint32_t dl_ptr, uint32_t boot_130,
                                                  uint32_t staged_130, uint32_t skipped_host_130,
                                                  uint32_t boot_ff0, uint32_t staged_ff0,
                                                  uint32_t skipped_host_ff0) {
    g_inline_probe_trigen_staged_dram.store(dl_ptr & 0x7FFFFFu, std::memory_order_relaxed);
    g_inline_probe_trigen_boot_130.store(boot_130 & 0x7FFFFFu, std::memory_order_relaxed);
    g_inline_probe_trigen_post_130.store(staged_130 & 0x7FFFFFu, std::memory_order_relaxed);
    g_inline_probe_trigen_skip_130.store(skipped_host_130, std::memory_order_relaxed);
    if (!log_inline_advance()) return;
    const uint32_t line = g_inline_probe_trigen_boot_lines.fetch_add(1, std::memory_order_relaxed);
    if (line < 16) {
        const uint32_t task = g_e9prov.task;
        const uint32_t boot = boot_ff0 & 0x7FFFFFu;
        const uint32_t staged = staged_ff0 & 0x7FFFFFu;
        const uint32_t expected = dl_ptr & 0x7FFFFFu;
        const uint32_t boot130 = boot_130 & 0x7FFFFFu;
        const uint32_t post130 = staged_130 & 0x7FFFFFu;
        fprintf(stderr, "[inline-trigen-boot] task=%u phase=%u 130_boot=0x%06X 130_post=0x%06X task_data=0x%06X host130=%s 130_boot_task=%s 130_post_task=%s ff0_boot=0x%06X ff0_post=0x%06X host_ff0=%s ff0_boot_task=%s ff0_post_task=%s\n",
                task, rs64_phase_ord(), boot130, post130, expected,
                skipped_host_130 ? "skipped" : "written",
                boot130 == expected ? "equal" : "MISMATCH",
                post130 == expected ? "equal" : "MISMATCH", boot, staged,
                skipped_host_ff0 ? "skipped" : "written",
                boot == expected ? "equal" : "MISMATCH",
                staged == expected ? "equal" : "MISMATCH");
        fflush(stderr);
    }
}

extern "C" void rs64_inline_probe_trigen_chunk(uint32_t r17, uint32_t chunk_dram) {
    if (!log_inline_advance() || !g_inline_probe.active || g_inline_probe.opcode != 0x05) return;
    const uint32_t line = g_inline_probe_trigen_chunk_lines.fetch_add(1, std::memory_order_relaxed);
    if (line < 16) {
        const uint32_t staged = g_inline_probe_trigen_staged_dram.load(std::memory_order_relaxed);
        const uint32_t boot130 = g_inline_probe_trigen_boot_130.load(std::memory_order_relaxed);
        const uint32_t post130 = g_inline_probe_trigen_post_130.load(std::memory_order_relaxed);
        const uint32_t skip130 = g_inline_probe_trigen_skip_130.load(std::memory_order_relaxed);
        const uint32_t chunk = chunk_dram & 0x7FFFFFu;
        fprintf(stderr, "[inline-trigen-chunk] task=%u phase=%u r17=0x%06X chunk130=0x%06X staged_dram=0x%06X host130=%s boot130=0x%06X post130=0x%06X stage=%s\n",
                g_e9prov.task, rs64_phase_ord(), r17 & 0x7FFFFFu, chunk, staged,
                skip130 ? "skipped" : "written", boot130, post130,
                chunk == staged ? "equal" : "MISMATCH");
        fflush(stderr);
    }
}

extern "C" void rs64_inline_probe_trigen_sources(uint32_t r17, uint32_t entry_dram, uint32_t refill_dram) {
    if (!log_inline_advance() || !g_inline_probe.active || g_inline_probe.opcode != 0x05) return;
    const uint32_t line = g_inline_probe_trigen_source_lines.fetch_add(1, std::memory_order_relaxed);
    if (line < 16) {
        const uint32_t entry_offset = (r17 - 0x170) & 0xFFF;
        const uint32_t expected = (entry_dram + entry_offset + 40) & 0x7FFFFFu;
        const uint32_t actual = refill_dram & 0x7FFFFFu;
        const uint32_t staged = g_inline_probe_trigen_staged_dram.load(std::memory_order_relaxed);
        const uint32_t boot130 = g_inline_probe_trigen_boot_130.load(std::memory_order_relaxed);
        const uint32_t post130 = g_inline_probe_trigen_post_130.load(std::memory_order_relaxed);
        const uint32_t skip130 = g_inline_probe_trigen_skip_130.load(std::memory_order_relaxed);
        fprintf(stderr, "[inline-trigen-source] task=%u phase=%u entry_dram=0x%06X entry_offset=0x%03X refill_dram=0x%06X staged_dram=0x%06X expected=0x%06X host130=%s boot130=0x%06X post130=0x%06X stage=%s verdict=%s\n",
                g_e9prov.task, rs64_phase_ord(), entry_dram & 0x7FFFFFu, entry_offset,
                actual, staged, expected, skip130 ? "skipped" : "written", boot130, post130,
                actual == staged ? "equal" : "MISMATCH",
                actual == expected ? "equal" : "MISMATCH");
        fflush(stderr);
    }
}

extern "C" void rs64_inline_probe_trigen_branch(uint32_t r17, uint32_t source_dram,
                                                   uint32_t dpc_end, uint32_t dpc_current,
                                                   uint32_t branch) {
    rs64_s7521_l1db0((int)branch);
    if (!log_inline_advance() || !g_inline_probe.active || g_inline_probe.opcode != 0x05) return;
    if (!g_e9prov.target) return;
    if (g_e9prov.trigen_sample == 0xFFFFFFFFu) {
        const uint32_t sample = g_inline_probe_trigen_pairs.fetch_add(1, std::memory_order_relaxed);
        if (sample >= 16) return;
        g_e9prov.trigen_sample = sample;
        g_e9prov.trigen_pair_open = true;
        fprintf(stderr, "[inline-trigen-branch] sample=%u task=%u phase=%u entry=0x%06X r17=0x%06X source=0x%06X end=0x%06X current=0x%06X branch=%u next=%s\n",
                sample,
                g_e9prov.task, rs64_phase_ord(), g_inline_probe.entry & 0x7FFFFFu,
                r17 & 0x7FFFFFu, source_dram & 0x7FFFFFu, dpc_end & 0x7FFFFFu,
                dpc_current & 0x7FFFFFu, branch,
                branch == 5 ? "L_1E5C/L_11B0" : branch == 0 ? "L_1E70" : "L_1E48/L_1E5C/L_11B0");
        fflush(stderr);
    }
}

extern "C" void rs64_inline_probe_trigen_return(uint32_t r17, uint32_t source_dram,
                                                   uint32_t target) {
    if (!log_inline_advance() || !g_inline_probe.active || g_inline_probe.opcode != 0x05) return;
    if (!g_e9prov.target) return;
    if (g_e9prov.trigen_pair_open) {
        fprintf(stderr, "[inline-trigen-return] sample=%u task=%u phase=%u entry=0x%06X r17=0x%06X source=0x%06X target=0x%04X\n",
                g_e9prov.trigen_sample,
                g_e9prov.task, rs64_phase_ord(), g_inline_probe.entry & 0x7FFFFFu,
                r17 & 0x7FFFFFu, source_dram & 0x7FFFFFu, target);
        fflush(stderr);
        g_e9prov.trigen_pair_open = false;
    }
}

extern "C" void rs64_inline_probe_trigen_reload(uint32_t r17) {
    if (!log_inline_advance() || !g_inline_probe.active || g_inline_probe.opcode != 0x05) return;
    const uint32_t line = g_inline_probe_trigen_reload_lines.fetch_add(1, std::memory_order_relaxed);
    if (line < 96) {
        const uint32_t extra = (r17 - g_inline_probe.entry) & 0x7FFFFFu;
        fprintf(stderr, "[inline-trigen-reload] task=%u phase=%u entry=0x%06X l1e80=0x%06X extra=%u expected=32 verdict=%s\n",
                g_e9prov.task, rs64_phase_ord(), g_inline_probe.entry & 0x7FFFFFu, r17 & 0x7FFFFFu,
                extra, extra == 32 ? "equal" : "MISMATCH");
        fflush(stderr);
    }
}

extern "C" void rs64_inline_probe_trigen_exit(uint32_t r17, uint32_t site) {
    if (!log_inline_advance() || !g_inline_probe.active || g_inline_probe.opcode != 0x05) return;
    uint32_t index;
    switch (site) {
    case 0x1E48: index = 0; break;
    case 0x1E5C: index = 1; break;
    case 0x1E70: index = 2; break;
    case 0x1E80: index = 3; break;
    case 0x11B0: index = 4; break;
    default: return;
    }
    const uint32_t line = g_inline_probe_trigen_exit_lines[index].fetch_add(1, std::memory_order_relaxed);
    if (line < 16) {
        fprintf(stderr, "[inline-trigen-exit] task=%u phase=%u entry=0x%06X site=%04X r17=0x%06X\n",
                g_e9prov.task, rs64_phase_ord(), g_inline_probe.entry & 0x7FFFFFu, site,
                r17 & 0x7FFFFFu);
        fflush(stderr);
    }
}

extern "C" void rs64_e9prov_section2_latch() {
    if (!log_e9_provenance()) return;
    g_e9prov_latch_remaining.store(512, std::memory_order_release);
    fprintf(stderr, "[e9-prov-latch] section=2 next_tasks=512\n");
    fflush(stderr);
}

extern "C" void rs64_e9prov_guest(uint32_t guest_addr, uint32_t) {
    if (!log_e9_provenance()) return;
    ++g_e9prov.guest;
    if (g_e9prov.first_guest == 0xFFFFFFFFu) g_e9prov.first_guest = guest_addr & 0x7FFFFFu;
}

static uint32_t g_dlw_zero_src[4], g_dlw_zero_task = 0, g_dlw_nzero = 0;
static void dlw_dump_words(const char *tag, uint32_t task, uint32_t src) {
    if (g_rdram_for_submit == nullptr) return;
    fprintf(stderr, "[dlwalk-zero] %s task=%u src=0x%06X:", tag, task, src);
    for (uint32_t i = 0; i < 24; ++i) {
        const uint32_t p = (src + i * 4) & 0x7FFFFFu;
        fprintf(stderr, " %02x%02x%02x%02x", g_rdram_for_submit[p ^ 3], g_rdram_for_submit[(p + 1) ^ 3],
                g_rdram_for_submit[(p + 2) ^ 3], g_rdram_for_submit[(p + 3) ^ 3]);
    }
    fprintf(stderr, "\n");
}
extern "C" void rs64_dlw_jump(uint32_t target, uint32_t r31, uint32_t line, uint32_t d153) {
    if (!dlwalk_on() || g_dlw.task == 0) return;
    // s4740: overlay-table dump. Control = first arrival with resident 0x28 (known content);
    // probe = first arrival at 0x1DB0 with resident 0x2C. DMEM table at 0x76 (idx) / 0x7A+id (idx<<12|len, rom off).
    {
        static bool done28 = false, done2c = false;
        const bool c28 = !done28 && d153 == 0x28;
        const bool c2c = !done2c && d153 == 0x2C && (target & 0xFFFFu) == 0x1DB0;
        if ((c28 || c2c) && g_dmem_cur != nullptr) {
            (c28 ? done28 : done2c) = true;
            fprintf(stderr, "[ovl-tbl] %s task=%u tgt=%04X r31=%04X line=%u\n", c28 ? "ctl28" : "probe2C", g_dlw.task, target & 0xFFFFu, r31 & 0xFFFFu, line);
            auto h = [](uint32_t a) { return (unsigned)(g_dmem_cur[a ^ 3u] << 8 | g_dmem_cur[(a + 1) ^ 3u]); };
            fprintf(stderr, "[ovl-tbl] 0x76:");
            for (uint32_t i = 0; i < 4; ++i) fprintf(stderr, " %04X", h(0x76 + 2 * i));
            fprintf(stderr, "\n[ovl-tbl] 0x7A+id (id: a,b):");
            for (uint32_t id = 0; id <= 0x34; id += 4) fprintf(stderr, " %02X:%04X,%04X", id, h(0x7A + id), h(0x7C + id));
            fprintf(stderr, "\n[ovl-tbl] DMEM 0x00-0x40:");
            for (uint32_t i = 0; i < 0x40; ++i) fprintf(stderr, " %02X", (unsigned)g_dmem_cur[i ^ 3u]);
            fprintf(stderr, "\n");
        }
    }
    ++g_dlw.njmp;
    if (d153 == 0x2C && (target & 0xFFFFu) == 0x1DB0) ++g_dlw.n2c;
    g_dlw.ring[g_dlw.ring_n++ & 7] = {target & 0xFFFFu, r31 & 0xFFFFu, line, d153, g_dlw.prev_op, g_dlw.fetches};
}

extern "C" void rs64_dlw_root(uint32_t kind, uint32_t a, uint32_t b) {
    if (!dlwalk_on() || g_dlw.task == 0) return;
    if (kind == 6 && a == 3) {
        auto *dst = g_dlw.nsnap == 0 ? g_dlw.snap_first : g_dlw.snap_last;
        for (uint32_t i = 0; i < 8; ++i) dst[i] = g_dlw.ring[(g_dlw.ring_n + i) & 7];
        if (g_dlw.nsnap == 0) memcpy(g_dlw.snap_last, g_dlw.snap_first, sizeof g_dlw.snap_last);
        ++g_dlw.nsnap;
    }
    uint32_t w0 = 0;
    if (kind == 4 && g_rdram_for_submit != nullptr) {
        const uint32_t p = b & 0x7FFFF8u;
        w0 = (uint32_t(g_rdram_for_submit[p ^ 3]) << 24) | (uint32_t(g_rdram_for_submit[(p + 1) ^ 3]) << 16) |
             (uint32_t(g_rdram_for_submit[(p + 2) ^ 3]) << 8) | uint32_t(g_rdram_for_submit[(p + 3) ^ 3]);
        b &= 0x7FFFFFu;
    }
    if (kind == 6) b &= 0x7FFFFFu;
    dlw_event(kind, a & 0xFFFFu, b, w0);
    if (kind == 4 && w0 == 0 && g_rdram_for_submit != nullptr) {
        if (g_dlw_zero_task != g_dlw.task) { g_dlw_zero_task = g_dlw.task; g_dlw_nzero = 0; memset(g_dlw_zero_src, 0, sizeof g_dlw_zero_src); }
        bool known = false;
        for (uint32_t i = 0; i < g_dlw_nzero; ++i) if (g_dlw_zero_src[i] == b) known = true;
        if (!known && g_dlw_nzero < 4) {
            g_dlw_zero_src[g_dlw_nzero++] = b;
            if (g_dlw.fetches > 3000) dlw_dump_words("dma", g_dlw.task, b);
        }
    }
}

// s6845d: guest DL fetch ring for ROGUESQ_WIPE_SCAN (dumped by rs64_wipe_scan at each submit inside the window).
static uint32_t g_wfr_addr[64], g_wfr_w[64][4]; static uint32_t g_wfr_n = 0; static bool g_wfr_on = false;
extern "C" void rs64_e9prov_source_fetch(uint32_t guest_addr, uint32_t w0) {
    if (g_wfr_on && g_dmem_cur) {  // guest_addr is r17 = the DMEM offset of the fetched command: copy 16 bytes from DMEM
        const uint32_t ga = guest_addr & 0xFFFu, i = g_wfr_n++ & 63u; g_wfr_addr[i] = ga;
        for (int k = 0; k < 4; ++k) { uint32_t v = 0; for (int q = 0; q < 4; ++q) v = (v << 8) | g_dmem_cur[((ga + 4 * k + q) & 0xFFFu) ^ 3u]; g_wfr_w[i][k] = v; }
        g_wfr_w[i][0] = w0;
    }
    if (dlwalk_on()) {
        const uint32_t a = guest_addr & 0x7FFFFFu;
        ++g_dlw.fetches;
        if (g_dlw.prev != 0xFFFFFFFFu && a != g_dlw.prev + 8) {
            ++g_dlw.nonseq;
            if (a < g_dlw.prev) ++g_dlw.back;
            dlw_event(1, g_dlw.prev, a, g_dlw.prev_op);
        }
        g_dlw.prev = a; g_dlw.prev_op = w0 >> 24; if (g_dlw.prev_op == 0xBD) ++g_dlw.nbd;
    }
    if (!log_e9_provenance()) return;
    const uint32_t address = guest_addr & 0x7FFFFFu;
    ++g_e9prov.source_fetch;
    if ((w0 >> 24) == 0xE9) ++g_e9prov.source_e9;
    if (g_e9prov.source_first == 0xFFFFFFFFu) g_e9prov.source_first = address;
    g_e9prov.source_last = address;
}

extern "C" void rs64_e9prov_source_end(uint32_t guest_addr, uint32_t kind) {
    if (!log_e9_provenance()) return;
    ++g_e9prov.source_end;
    g_e9prov.source_end_addr = guest_addr & 0x7FFFFFu;
    g_e9prov.source_end_kind = kind;
}

extern "C" void rs64_e9prov_unwind(uint32_t stack_byte, uint32_t natural) {
    if (!log_e9_provenance()) return;
    ++g_e9prov.unwind;
    g_e9prov.unwind_last = stack_byte;
    if (natural) ++g_e9prov.unwind_natural;
}

extern "C" void rs64_e9prov_l12a0_source(uint32_t source, uint32_t r17, uint32_t w0,
                                             uint32_t w1, uint32_t target) {
    if (!log_e9_provenance() || target != 0x12A0) return;
    if (source == 1) ++g_e9prov.l12a0_direct;
    else if (source == 2) ++g_e9prov.l12a0_overlay;
    g_e9prov.pending_l12a0_source = source;
    g_e9prov.pending_l12a0_r17 = r17;
    g_e9prov.pending_l12a0_w0 = w0;
    g_e9prov.pending_l12a0_w1 = w1;
}

extern "C" void rs64_e9prov_l1db0_reset(uint32_t old, uint32_t r17, uint32_t ra, uint32_t resident) {
    rs64_s7521_l1db0(6);
    if (!log_e9_provenance()) return;
    ++g_e9prov.lifecycle_seq;
    ++g_e9prov.l1db0_reset;
    if (g_e9prov.frame_depths.empty() || !g_e9prov.frame_depths[0].active) return;
    ++g_e9prov.l1db0_reset_active;
    g_e9prov.l1db0_reset_last_active_seq = g_e9prov.lifecycle_seq;
    g_e9prov.l1db0_reset_last_active_old = old;
    g_e9prov.l1db0_reset_last_active_r17 = r17;
    const Rs64E9Provenance::ResetRoute route{
        g_e9prov.lifecycle_seq, old, r17, ra, resident,
        g_e9prov.pending_l12a0_source, g_e9prov.pending_l12a0_r17,
        g_e9prov.pending_l12a0_w0, g_e9prov.pending_l12a0_w1,
        g_inline_probe.active ? 1u : 0u, g_inline_probe.opcode,
        g_inline_probe.entry, g_inline_probe.table_kind, g_inline_probe.table_word,
        g_e9prov.l1db0_predecessor_target, g_e9prov.l1db0_predecessor_line,
        g_e9prov.l1db0_predecessor_ra, g_e9prov.l1db0_predecessor_resident,
        g_e9prov.l1db0_predecessor_r17, g_e9prov.l1db0_predecessor_from_l1298};
    if (g_e9prov.reset_route_first.size() < 8) g_e9prov.reset_route_first.push_back(route);
    if (g_e9prov.reset_route_last.size() == 8) g_e9prov.reset_route_last.erase(g_e9prov.reset_route_last.begin());
    g_e9prov.reset_route_last.push_back(route);
}

extern "C" void rs64_e9prov_ovl_route(uint32_t resident, uint32_t target) {
    g_e9prov.last_ovl_res = resident;
    g_e9prov.last_ovl_tgt = target;
    if (resident == 4) ++g_e9prov.clip_route;
    else if (resident == 0xC) {
        ++g_e9prov.ovl12_route;
        if (target != 0x1DB0) ++g_e9prov.ovl12_ret;
    } else if (resident == 0x24) {
        ++g_e9prov.ovl24_route;
        if (target != 0x12A0) ++g_e9prov.ovl24_ret;
    } else if (resident == 0x28) {
        ++g_e9prov.ovl28_route;
    } else if (resident == 0x14) {
        ++g_e9prov.ovl14_route;
        if (target != 0x1DB0) ++g_e9prov.ovl14_ret;
    } else if (resident == 0x18) {
        ++g_e9prov.ovl18_route;
    } else if (resident == 0x10) {
        ++g_e9prov.ovl10_route;
    } else if (resident == 0x1C) {
        ++g_e9prov.ovl1c_route;
    } else if (resident == 0x2C) {
        ++g_e9prov.ovl2c_route;
    }
    if (!log_e9_provenance()) return;
    static uint32_t n4 = 0, nC = 0, n24 = 0, n28 = 0, n14 = 0, n18 = 0, n10 = 0, n1c = 0, n2c = 0;
    uint32_t *n = resident == 4 ? &n4 : resident == 0xC ? &nC
                 : resident == 0x24 ? &n24 : resident == 0x28 ? &n28
                 : resident == 0x14 ? &n14 : resident == 0x18 ? &n18
                 : resident == 0x10 ? &n10 : resident == 0x1C ? &n1c
                 : resident == 0x2C ? &n2c : nullptr;
    if (!n) return;
    ++*n;
    if (*n <= 16 || (*n % 64) == 0) {
        fprintf(stderr, "[ovl-route] n=%u res=0x%02X tgt=0x%04X task=%u scope=%s\n",
                *n, resident, target & 0xFFFFu, g_e9prov.task,
                g_e9prov.control ? "control" : (g_e9prov.target ? "sec2" : "other"));
        fflush(stderr);
    }
}

extern "C" void rs64_e9prov_l1298_12a0_res(uint32_t resident) {
    if (resident == 0x24) ++g_e9prov.l1298_12a0_res24;
    else ++g_e9prov.l1298_12a0_other;
    if (!log_e9_provenance()) return;
    static uint32_t n = 0;
    ++n;
    if (resident != 0x24 && (n <= 16 || (n % 64) == 0)) {
        fprintf(stderr, "[ovl-route] n=%u res=0x%02X tgt=0x12A0 task=%u scope=%s via=l1298-other\n",
                n, resident, g_e9prov.task,
                g_e9prov.control ? "control" : (g_e9prov.target ? "sec2" : "other"));
        fflush(stderr);
    }
}

static std::atomic<uint32_t> g_1364_life_n{0};
static std::atomic<uint32_t> g_1364_life_res04{0};
static std::atomic<uint32_t> g_1364_life_res24{0};
static std::atomic<uint32_t> g_1364_life_other{0};
static std::atomic<uint32_t> g_1364_life_jal17f0{0};
static std::atomic<uint32_t> g_1364_life_clip1e48{0};
static std::atomic<uint32_t> g_1364_life_clip1e48_1364{0};

extern "C" void rs64_e9prov_ovl24_jal17f0(void) {
    ++g_e9prov.ovl24_jal17f0;
    ++g_1364_life_jal17f0;
}

extern "C" void rs64_e9prov_clip_1e48_ra(uint32_t ra) {
    ++g_e9prov.clip_1e48;
    ++g_1364_life_clip1e48;
    if (((ra | 0x1000) & 0x1FFF) == 0x1364) {
        ++g_e9prov.clip_1e48_1364;
        ++g_1364_life_clip1e48_1364;
    }
}

extern "C" void rs64_e9prov_1364_jump(uint32_t line, uint32_t r31, uint32_t r30,
                                      uint32_t resident) {
    ++g_e9prov.j1364;
    const uint32_t n = ++g_1364_life_n;
    if (resident == 4) {
        ++g_e9prov.j1364_res04;
        ++g_1364_life_res04;
    } else if (resident == 0x24) {
        ++g_e9prov.j1364_res24;
        ++g_1364_life_res24;
    } else {
        ++g_e9prov.j1364_other;
        ++g_1364_life_other;
    }
    g_e9prov.j1364_line = line;
    g_e9prov.j1364_r31 = r31;
    g_e9prov.j1364_r30 = r30;
    g_e9prov.j1364_res = resident;
    g_e9prov.j1364_ovl_res = g_e9prov.last_ovl_res;
    g_e9prov.j1364_ovl_tgt = g_e9prov.last_ovl_tgt;
    if (!log_e9_provenance()) return;
    if (n <= 32 || (n % 64) == 0) {
        fprintf(stderr,
                "[1364-pred] n=%u line=%u r31=0x%04X r30=0x%04X res=0x%02X "
                "last_ovl=0x%02X/0x%04X task=%u scope=%s jal17f0=%u "
                "clip1e48=%u/%u\n",
                n, line, r31 & 0xFFFFu, r30 & 0xFFFFu, resident & 0xFFu,
                g_e9prov.last_ovl_res & 0xFFu, g_e9prov.last_ovl_tgt & 0xFFFFu,
                g_e9prov.task,
                g_e9prov.control ? "control" : (g_e9prov.target ? "sec2" : "other"),
                g_1364_life_jal17f0.load(std::memory_order_relaxed),
                g_1364_life_clip1e48_1364.load(std::memory_order_relaxed),
                g_1364_life_clip1e48.load(std::memory_order_relaxed));
        fflush(stderr);
    }
    if ((n % 64) == 0) {
        fprintf(stderr,
                "[1364-pred-sum] n=%u res04=%u res24=%u oth=%u jal17f0=%u "
                "clip1e48_1364=%u clip1e48=%u\n",
                n,
                g_1364_life_res04.load(std::memory_order_relaxed),
                g_1364_life_res24.load(std::memory_order_relaxed),
                g_1364_life_other.load(std::memory_order_relaxed),
                g_1364_life_jal17f0.load(std::memory_order_relaxed),
                g_1364_life_clip1e48_1364.load(std::memory_order_relaxed),
                g_1364_life_clip1e48.load(std::memory_order_relaxed));
        fflush(stderr);
    }
}

extern "C" void rs64_e9prov_l1db0_predecessor(uint32_t target, uint32_t line, uint32_t ra,
                                                   uint32_t resident, uint32_t r17, uint32_t from_l1298) {
    if (!log_e9_provenance()) return;
    ++g_e9prov.l1db0_predecessor;
    g_e9prov.l1db0_predecessor_target = target;
    g_e9prov.l1db0_predecessor_line = line;
    g_e9prov.l1db0_predecessor_ra = ra;
    g_e9prov.l1db0_predecessor_resident = resident;
    g_e9prov.l1db0_predecessor_r17 = r17;
    g_e9prov.l1db0_predecessor_from_l1298 = from_l1298;
}

static void rs64_e9prov_frame_event(uint32_t kind, uint32_t slot, uint32_t target, uint32_t pc,
                                     uint32_t caller = 0, uint32_t w0 = 0, uint32_t w1 = 0) {
    if (!log_e9_provenance()) return;
    ++(kind == 1 ? g_e9prov.frame_push : kind == 2 ? g_e9prov.frame_pop : g_e9prov.frame_resume);
    const uint32_t depth = slot / 8u;
    if (g_e9prov.frame_depths.size() <= depth) g_e9prov.frame_depths.resize(depth + 1);
    auto& ledger = g_e9prov.frame_depths[depth];
    if (kind == 1) {
        ++g_e9prov.lifecycle_seq;
        ++ledger.push;
        if (ledger.active) {
            ++ledger.reuse_push;
            if (depth == 0) {
                if (g_e9prov.l1db0_reset_last_active_seq != 0) {
                    const Rs64E9Provenance::ResetReusePair pair{
                        g_e9prov.l1db0_reset_last_active_seq,
                        g_e9prov.l1db0_reset_last_active_old,
                        g_e9prov.l1db0_reset_last_active_r17,
                        g_e9prov.lifecycle_seq, pc};
                    if (g_e9prov.reset_reuse_first.size() < 8)
                        g_e9prov.reset_reuse_first.push_back(pair);
                    if (g_e9prov.reset_reuse_last.size() == 8)
                        g_e9prov.reset_reuse_last.erase(g_e9prov.reset_reuse_last.begin());
                    g_e9prov.reset_reuse_last.push_back(pair);
                    g_e9prov.l1db0_reset_last_active_seq = 0;
                } else {
                    ++g_e9prov.depth0_reuse_unpaired;
                }
            }
        }
        ledger.active = true;
        ledger.pending_resume = false;
    } else if (kind == 2) {
        if (!ledger.active) ++ledger.pop_without_push;
        else ++ledger.pop;
        ledger.pending_resume = ledger.active;
    } else if (!ledger.active || !ledger.pending_resume) {
        ++ledger.resume_without_pop;
    } else {
        ++ledger.resume;
        ledger.active = false;
        ledger.pending_resume = false;
    }
    uint32_t id = 0;
    if (kind == 1) {
        id = ++g_e9prov.frame_next_id;
        g_e9prov.frame_id_by_slot[slot] = id;
        g_e9prov.frame_opcode_by_slot[slot] = w0 >> 24;
        if ((w0 >> 24) == 0x06) ++g_e9prov.frame_06_push;
    } else {
        const auto found = g_e9prov.frame_id_by_slot.find(slot);
        if (found != g_e9prov.frame_id_by_slot.end()) id = found->second;
    }
    if (slot < g_e9prov.frame_min_slot) g_e9prov.frame_min_slot = slot;
    if (slot > g_e9prov.frame_max_slot) g_e9prov.frame_max_slot = slot;
    const uint32_t source = kind == 1 ? g_e9prov.pending_l12a0_source : 0;
    Rs64E9Provenance::FrameEvent event{kind, id, slot, target, pc, caller, w0, w1, source};
    if (kind == 1 && source != 0) {
        g_e9prov.pending_l12a0_source = 0;
    }
    if (g_e9prov.frame_first.size() < 8) g_e9prov.frame_first.push_back(event);
    if (g_e9prov.frame_last.size() == 8) g_e9prov.frame_last.erase(g_e9prov.frame_last.begin());
    g_e9prov.frame_last.push_back(event);
    if (kind == 1) {
        bool seen = false;
        for (const auto& prior : g_e9prov.frame_slot_first) {
            if (prior.slot == slot) { seen = true; break; }
        }
        if (!seen) g_e9prov.frame_slot_first.push_back(event);
        if (slot == 8) {
            if (!g_e9prov.frame_slot8_seen) g_e9prov.frame_slot8_first = event;
            g_e9prov.frame_slot8_last = event;
            g_e9prov.frame_slot8_seen = true;
        }
        if (slot == 0 && caller == 0x1088) {
            if (!g_e9prov.frame_reentry_slot0_seen) g_e9prov.frame_reentry_slot0_first = event;
            g_e9prov.frame_reentry_slot0_last = event;
            g_e9prov.frame_reentry_slot0_seen = true;
        }
    }
}

extern "C" void rs64_e9prov_frame_push(uint32_t slot, uint32_t saved_target, uint32_t saved_pc,
                                          uint32_t caller, uint32_t w0, uint32_t w1) {
    if (dlwalk_on()) dlw_event(2, slot, saved_target & 0x7FFFFFu, saved_pc & 0x7FFFFFu);
    rs64_e9prov_frame_event(1, slot, saved_target, saved_pc, caller, w0, w1);
}

extern "C" void rs64_e9prov_frame_pop(uint32_t slot, uint32_t saved_target, uint32_t saved_pc) {
    if (dlwalk_on()) dlw_event(3, slot, saved_target & 0x7FFFFFu, saved_pc & 0x7FFFFFu);
    if (!log_e9_provenance()) return;  // s7441: bookkeeping below feeds only the provenance report
    rs64_e9prov_frame_event(2, slot, saved_target, saved_pc);
    g_e9prov.pending_pop_slot = slot;
    g_e9prov.pending_pop_pc = saved_pc;
}

extern "C" void rs64_e9prov_frame_resume(uint32_t slot, uint32_t resumed_pc) {
    if (!log_e9_provenance()) return;  // s7441: map find + 2 erases per DL return fed only the provenance report
    rs64_e9prov_frame_event(3, slot, 0, resumed_pc);
    if (slot == 0) ++g_e9prov.frame_zero_resume;
    if (g_e9prov.pending_pop_slot != slot || g_e9prov.pending_pop_pc != resumed_pc) ++g_e9prov.frame_resume_mismatch;
    g_e9prov.pending_pop_slot = 0xFFFFFFFFu;
    g_e9prov.pending_pop_pc = 0xFFFFFFFFu;
    const auto opcode = g_e9prov.frame_opcode_by_slot.find(slot);
    if (opcode != g_e9prov.frame_opcode_by_slot.end() && opcode->second == 0x06) ++g_e9prov.frame_06_complete;
    g_e9prov.frame_id_by_slot.erase(slot);
    g_e9prov.frame_opcode_by_slot.erase(slot);
}

extern "C" void rs64_e9prov_task_end(uint32_t task) {
    if (dlwalk_on() && g_dlw.task == task) {
        static int sums_ph[16] = {0}, dets = 0, dets2 = 0;
        const uint32_t ph_ord = rs64_phase_ord() & 15u;
        static uint32_t tot_ph[16] = {0}, run_ph[16] = {0};
        ++tot_ph[ph_ord];
        if (g_dlw.fetches >= 16000) ++run_ph[ph_ord];
        if (sums_ph[ph_ord] < 150 && (g_dlw.fetches > 3000 || sums_ph[ph_ord] < 10)) {
            ++sums_ph[ph_ord];
            if ((tot_ph[ph_ord] & 63u) == 1u)
                fprintf(stderr, "[dlwalk-ph] phase=%u tasks=%u runaway=%u\n", ph_ord, tot_ph[ph_ord], run_ph[ph_ord]);
            fprintf(stderr, "[dlwalk-sum] task=%u phase=%u fetches=%u nonseq=%u back=%u events=%zu\n",
                    task, rs64_phase_ord(), g_dlw.fetches, g_dlw.nonseq, g_dlw.back, g_dlw.ev.size());
        }
        {
            static int c2c_ph[16] = {0};
            if (c2c_ph[ph_ord] < 150 && (g_dlw.fetches > 3000 || c2c_ph[ph_ord] < 10)) {
                ++c2c_ph[ph_ord];
                fprintf(stderr, "[dlwalk-2c] task=%u phase=%u fetches=%u arrivals2c=%u jmps=%u nbd=%u\n", task, ph_ord, g_dlw.fetches, g_dlw.n2c, g_dlw.njmp, g_dlw.nbd);
            }
        }
        const bool runaway = g_dlw.fetches >= 16000, normal = g_dlw.fetches > 3000 && g_dlw.fetches < 4000;
        if (runaway && g_dlw_zero_task == task) { static int tz = 0; for (uint32_t i = 0; i < g_dlw_nzero && tz < 24; ++i, ++tz) dlw_dump_words("end", task, g_dlw_zero_src[i]); }
        if ((runaway && dets < 3) || (normal && dets2 < 2)) {
            if (runaway) ++dets; else ++dets2;
            auto dump = [&](const char *tag, const DlWalkTrace::Jmp *r, bool ordered) {
                for (uint32_t i = 0; i < 8; ++i) { const auto& j = ordered ? r[i] : r[(g_dlw.ring_n + i) & 7];
                    fprintf(stderr, "[dlwalk-jmp] task=%u %s i=%u n=%u tgt=0x%04X r31=0x%04X line=%u d153=0x%02X prevop=0x%02X\n",
                            task, tag, i, j.n, j.target, j.r31, j.line, j.d153, j.prev_op); }
            };
            fprintf(stderr, "[dlwalk-jmp] task=%u runaway=%d nsnap=%u ring_n=%u\n", task, runaway ? 1 : 0, g_dlw.nsnap, g_dlw.ring_n);
            dump("end", g_dlw.ring, false);
            if (g_dlw.nsnap) { dump("site3first", g_dlw.snap_first, true); dump("site3last", g_dlw.snap_last, true); }
            for (const auto& e : g_dlw.ev)
                fprintf(stderr, "[dlwalk-ev] task=%u n=%u k=%u a=0x%06X b=0x%06X c=0x%06X\n", task, e.n, e.kind, e.a, e.b, e.c);
        }
        fflush(stderr);
    }
    if (log_inline_advance() && g_e9prov.task == task && g_inline_probe.active) {
        ++g_inline_probe.incomplete;
        g_inline_probe.active = false;
    }
    if (log_inline_advance() && g_e9prov.task == task &&
        (g_inline_probe.samples[1] || g_inline_probe.samples[2] || g_inline_probe.samples[3] ||
         g_inline_probe.samples[4] || g_inline_probe.samples[5] || g_inline_probe.samples[6])) {
        if (g_inline_probe_summaries.fetch_add(1, std::memory_order_relaxed) < 32) {
            fprintf(stderr, "[inline-advance-summary] task=%u phase=%u samples=mm:%u/%u tg:%u/%u tri:%u/%u tx:%u/%u oh:%u/%u ol:%u/%u incomplete=%u\n",
                    task, rs64_phase_ord(), g_inline_probe.mismatch[1], g_inline_probe.samples[1],
                    g_inline_probe.mismatch[2], g_inline_probe.samples[2],
                    g_inline_probe.mismatch[3], g_inline_probe.samples[3],
                    g_inline_probe.mismatch[4], g_inline_probe.samples[4],
                    g_inline_probe.mismatch[5], g_inline_probe.samples[5],
                    g_inline_probe.mismatch[6], g_inline_probe.samples[6],
                    g_inline_probe.incomplete);
            fflush(stderr);
        }
    }
    if (g_e9prov.task != task) return;
    if (log_e9_unified() && (g_e9prov.control || g_e9prov.target)) {
        fprintf(stderr,
                "[e9-unified] task=%u scope=%s guest_dl=0x%08X aligned=%u "
                "fetched=%u handler=%u state_fullsync=%u emitted=%u matched=%u\n",
                task, g_e9prov.control ? "control" : "sec2",
                g_e9prov.aligned_dl, g_e9prov.aligned, g_e9prov.authoritative,
                g_e9prov.handler, g_e9prov.dispatched, g_e9prov.emitted,
                g_e9prov.matched);
        fflush(stderr);
    }
    if (!log_e9_provenance()) return;
    if (g_e9prov.control || g_e9prov.target) {
        for (uint32_t emitted : g_e9prov.emitted_addrs) {
            bool covered = false;
            for (uint32_t fetched : g_e9prov.fetched_addrs) {
                if (fetched == emitted) {
                    covered = true;
                    break;
                }
            }
            for (uint32_t spanned : g_e9prov.spanned_addrs) {
                if (spanned == emitted) {
                    covered = true;
                    break;
                }
            }
            if (!covered) {
                ++g_e9prov.uncovered;
                fprintf(stderr, "[e9-prov-gap] task=%u scope=%s addr=0x%06X\\n",
                        task, g_e9prov.control ? "control" : "sec2", emitted);
            }
            bool conditioned = false;
            for (const auto& condition : g_e9prov.conditions) {
                if (condition.address == emitted && condition.serial != 0) {
                    conditioned = true;
                    break;
                }
            }
            if (!conditioned) {
                ++g_e9prov.condition_unassociated;
                static uint32_t condition_gap_lines = 0;
                if (condition_gap_lines++ < 256) {
                    fprintf(stderr, "[rdp-condition] task=%u scope=%s kind=unassociated addr=0x%06X\\n",
                            task, g_e9prov.control ? "control" : "sec2", emitted);
                    fflush(stderr);
                }
            }
        }
        fprintf(stderr,
                "[rdp-condition-summary] task=%u scope=%s direct=%u span=%u pending=%u extended=%u unassociated=%u records=%zu\\n",
                task, g_e9prov.control ? "control" : "sec2", g_e9prov.condition_direct,
                g_e9prov.condition_span, g_e9prov.condition_pending,
                g_e9prov.condition_extended,
                g_e9prov.condition_unassociated, g_e9prov.conditions.size());
        fflush(stderr);
    }
    static uint32_t controls = 0;
    if ((g_e9prov.control && ++controls <= 4) || g_e9prov.target) {
        uint32_t frame_06_open = 0;
        for (const auto& pair : g_e9prov.frame_opcode_by_slot) {
            if (pair.second == 0x06) ++frame_06_open;
        }
        fprintf(stderr, "[e9-prov] task=%u scope=%s guest=%u emit=%u submit=%u raw=%u dispatch=%u match=%u "
                "src_fetch=%u src_e9=%u src_end=%u src_kind=%u src0=0x%06X src_last=0x%06X src_end0=0x%06X "
                "unwind=%u unwind_natural=%u unwind_last=0x%08X frame=push:%u,pop:%u,resume:%u,zresume:%u,slot:%u..%u,mis:%u dl06=push:%u,complete:%u,open:%u l12a0=direct:%u,overlay:%u span=%u gap=%u guest0=0x%06X emit0=0x%06X raw0=0x%06X match0=0x%06X\n",
                task, g_e9prov.control ? "control" : "sec2", g_e9prov.guest,
                g_e9prov.emitted, g_e9prov.submitted, g_e9prov.authoritative,
                g_e9prov.dispatched, g_e9prov.matched,
                g_e9prov.source_fetch, g_e9prov.source_e9, g_e9prov.source_end,
                g_e9prov.source_end_kind, g_e9prov.source_first, g_e9prov.source_last,
                g_e9prov.source_end_addr, g_e9prov.unwind, g_e9prov.unwind_natural,
                g_e9prov.unwind_last, g_e9prov.frame_push, g_e9prov.frame_pop,
                g_e9prov.frame_resume, g_e9prov.frame_zero_resume,
                g_e9prov.frame_min_slot == 0xFFFFFFFFu ? 0u : g_e9prov.frame_min_slot,
                g_e9prov.frame_max_slot, g_e9prov.frame_resume_mismatch,
                g_e9prov.frame_06_push, g_e9prov.frame_06_complete, frame_06_open,
                g_e9prov.l12a0_direct, g_e9prov.l12a0_overlay,
                g_e9prov.non_e9_spans, g_e9prov.uncovered,
                g_e9prov.first_guest, g_e9prov.first_emit, g_e9prov.first_authoritative,
                g_e9prov.first_match);
        fprintf(stderr, "[e9-prov-reset] task=%u scope=%s reset=%u active=%u predecessor=%u paired=%zu unpaired_reuse=%u pending_seq=%u clip=%u ovl12=%u ovl12_ret=%u ovl24=%u ovl24_ret=%u ovl28=%u ovl14=%u ovl14_ret=%u ovl18=%u ovl10=%u ovl1c=%u l1298_12a0=24:%u,other:%u j1364=%u,04:%u,24:%u,oth:%u jal17f0=%u clip1e48=%u/%u last_ovl=0x%02X/0x%04X pred=line:%u,r31:0x%04X,r30:0x%04X,res:0x%02X,ovl:0x%02X/0x%04X\n",
                task, g_e9prov.control ? "control" : "sec2", g_e9prov.l1db0_reset,
                g_e9prov.l1db0_reset_active, g_e9prov.l1db0_predecessor, g_e9prov.reset_reuse_last.size(),
                g_e9prov.depth0_reuse_unpaired, g_e9prov.l1db0_reset_last_active_seq,
                g_e9prov.clip_route, g_e9prov.ovl12_route, g_e9prov.ovl12_ret,
                g_e9prov.ovl24_route, g_e9prov.ovl24_ret, g_e9prov.ovl28_route,
                g_e9prov.ovl14_route, g_e9prov.ovl14_ret, g_e9prov.ovl18_route,
                g_e9prov.ovl10_route, g_e9prov.ovl1c_route,
                g_e9prov.l1298_12a0_res24, g_e9prov.l1298_12a0_other,
                g_e9prov.j1364, g_e9prov.j1364_res04, g_e9prov.j1364_res24,
                g_e9prov.j1364_other, g_e9prov.ovl24_jal17f0,
                g_e9prov.clip_1e48_1364, g_e9prov.clip_1e48,
                g_e9prov.last_ovl_res & 0xFFu, g_e9prov.last_ovl_tgt & 0xFFFFu,
                g_e9prov.j1364_line, g_e9prov.j1364_r31 & 0xFFFFu,
                g_e9prov.j1364_r30 & 0xFFFFu, g_e9prov.j1364_res & 0xFFu,
                g_e9prov.j1364_ovl_res & 0xFFu, g_e9prov.j1364_ovl_tgt & 0xFFFFu);
        const auto dump_reset_pair = [task](const char* edge,
                                             const std::vector<Rs64E9Provenance::ResetReusePair>& pairs) {
            for (const auto& pair : pairs) {
                fprintf(stderr, "[e9-prov-reset-pair] task=%u edge=%s reset_seq=%u old=0x%02X reset_r17=0x%06X reuse_seq=%u reuse_r17=0x%06X\n",
                        task, edge, pair.reset_seq, pair.reset_old, pair.reset_r17 & 0x7FFFFFu,
                        pair.reuse_seq, pair.reuse_r17 & 0x7FFFFFu);
            }
        };
        dump_reset_pair("first", g_e9prov.reset_reuse_first);
        dump_reset_pair("last", g_e9prov.reset_reuse_last);
        const auto dump_reset_route = [task](const char* edge,
                                              const std::vector<Rs64E9Provenance::ResetRoute>& routes) {
            for (const auto& route : routes) {
                fprintf(stderr, "[e9-prov-reset-predecessor] task=%u edge=%s seq=%u old=0x%02X r17=0x%06X ra=0x%04X resident=0x%02X pending=src:%u,r17:0x%06X,w0:0x%08X,w1:0x%08X inline=active:%u,op:0x%02X,entry:0x%06X,table:%u,word:0x%04X pred=target:0x%04X,line:%u,ra:0x%04X,resident:0x%02X,r17:0x%06X,l1298:%u\\n",
                        task, edge, route.seq, route.old, route.r17 & 0x7FFFFFu, route.ra & 0xFFFFu,
                        route.resident, route.pending_source, route.pending_r17 & 0x7FFFFFu,
                        route.pending_w0, route.pending_w1, route.inline_active, route.inline_opcode,
                        route.inline_entry & 0x7FFFFFu, route.inline_table_kind, route.inline_table_word,
                        route.predecessor_target & 0xFFFFu, route.predecessor_line,
                        route.predecessor_ra & 0xFFFFu, route.predecessor_resident,
                        route.predecessor_r17 & 0x7FFFFFu, route.predecessor_from_l1298);
            }
        };
        dump_reset_route("first", g_e9prov.reset_route_first);
        dump_reset_route("last", g_e9prov.reset_route_last);
        const auto dump_frame = [task](const char* edge, const std::vector<Rs64E9Provenance::FrameEvent>& events) {
            for (const auto& event : events) {
                fprintf(stderr, "[e9-prov-frame] task=%u edge=%s kind=%c id=%u src=%u slot=0x%X target=0x%06X pc=0x%06X caller=0x%04X w0=0x%08X w1=0x%08X\n",
                        task, edge, event.kind == 1 ? 'P' : event.kind == 2 ? 'O' : 'R',
                        event.id, event.source, event.slot, event.target & 0x7FFFFFu, event.pc & 0x7FFFFFu, event.caller & 0xFFFFu,
                        event.w0, event.w1);
            }
        };
        dump_frame("first", g_e9prov.frame_first);
        dump_frame("last", g_e9prov.frame_last);
        dump_frame("slot-first", g_e9prov.frame_slot_first);
        if (g_e9prov.frame_slot8_seen) {
            const std::vector<Rs64E9Provenance::FrameEvent> first{g_e9prov.frame_slot8_first};
            const std::vector<Rs64E9Provenance::FrameEvent> last{g_e9prov.frame_slot8_last};
            dump_frame("slot8-first", first);
            dump_frame("slot8-last", last);
        }
        if (g_e9prov.frame_reentry_slot0_seen) {
            const std::vector<Rs64E9Provenance::FrameEvent> first{g_e9prov.frame_reentry_slot0_first};
            const std::vector<Rs64E9Provenance::FrameEvent> last{g_e9prov.frame_reentry_slot0_last};
            dump_frame("reentry-slot0-first", first);
            dump_frame("reentry-slot0-last", last);
        }
        if (g_e9prov.target && g_e9prov.source_end_kind == 2) {
            uint32_t active = 0;
            uint32_t rows = 0;
            for (const auto& depth : g_e9prov.frame_depths) {
                if (depth.active) ++active;
            }
            fprintf(stderr, "[e9-prov-depth-summary] task=%u phase=%u cap=1 current_active=%u depths=%zu\n",
                    task, rs64_phase_ord(), active, g_e9prov.frame_depths.size());
            for (uint32_t depth = 0; depth < g_e9prov.frame_depths.size() && rows < 32; ++depth) {
                const auto& entry = g_e9prov.frame_depths[depth];
                if (entry.push == 0 && entry.pop == 0 && entry.resume == 0 &&
                    entry.reuse_push == 0 && entry.pop_without_push == 0 &&
                    entry.resume_without_pop == 0) continue;
                ++rows;
                fprintf(stderr, "[e9-prov-depth] task=%u depth=%u push=%u pop=%u resume=%u active=%u pending=%u reuse=%u pop_without_push=%u resume_without_pop=%u\n",
                        task, depth, entry.push, entry.pop, entry.resume,
                        entry.active ? 1u : 0u, entry.pending_resume ? 1u : 0u,
                        entry.reuse_push, entry.pop_without_push, entry.resume_without_pop);
            }
            if (rows < g_e9prov.frame_depths.size()) {
                fprintf(stderr, "[e9-prov-depth-truncated] task=%u rows=%u cap=32\n", task, rows);
            }
        }
        fflush(stderr);
    }
}

extern "C" void rs64_e9prov_task_join_report(uint32_t task) {
    if (!log_e9_unified() || g_e9prov.task != task) return;
    if (!(g_e9prov.control || g_e9prov.target || g_e9prov.aligned != 0)) return;
    const uint32_t bridge_e9 = g_task_bridge_e9.load(std::memory_order_acquire);
    const uint32_t parser_e9 = rs64_rdp_advance_task_e9();
    const uint32_t parser_epoch = rs64_rdp_advance_epoch();
    const uint64_t join_order = rs64_rdp_advance_join_order();
    fprintf(stderr,
            "[e9-task-join] task=%u begin=%u end=%u bridge_start=0 bridge_end=%u "
            "bridge_delta=%u parser_start=0 parser_end=%u parser_delta=%u "
            "parser_epoch=%u reset_order=%llu first_consumer_order=%llu "
            "first_consumer_addr=0x%06X join_order=%llu aligned=%u dl=0x%08X scope=%s\n",
            task, task, task, bridge_e9, bridge_e9, parser_e9, parser_e9,
            parser_epoch, (unsigned long long)rs64_rdp_advance_reset_order(),
            (unsigned long long)rs64_rdp_advance_first_consumer_order(),
            rs64_rdp_advance_first_consumer_address(),
            (unsigned long long)join_order, g_e9prov.aligned, g_e9prov.aligned_dl,
            g_e9prov.control ? "control" : g_e9prov.target ? "sec2" : "aligned");
    fprintf(stderr, "[e9-task-provenance] task=%u ordinary_bridge_e9=%u synthetic_fullsyncs=%u\n",
            task, bridge_e9, g_task_synthetic_fullsyncs.load(std::memory_order_acquire));
    fflush(stderr);
    const uint32_t line = g_e9prov_join_lines.fetch_add(1, std::memory_order_relaxed);
    if (line < 96) {
        fprintf(stderr, "[e9-join-end] passed=%u current=%u guest_dl=0x%08X aligned=%u\n",
                task, g_e9prov.task, g_e9prov.aligned_dl, g_e9prov.aligned);
        fflush(stderr);
    }
}

extern "C" void rs64_e9prov_authoritative_span(uint32_t start, uint32_t end,
                                                   uint32_t raw_opcode, uint32_t pending) {
    if (!log_e9_provenance() || raw_opcode == 0xE9 || end <= start) return;
    start &= 0x7FFFFFu;
    end &= 0x7FFFFFu;
    if (end <= start) return;
    for (uint32_t emitted : g_e9prov.emitted_addrs) {
        if (start < emitted && emitted < end) {
            g_e9prov.spanned_addrs.push_back(emitted);
            ++g_e9prov.non_e9_spans;
            if (log_e9_boundary() && (g_e9prov.control || g_e9prov.target)) {
                static uint32_t lines = 0;
                if (lines++ < 1024) {
                    fprintf(stderr,
                            "[e9-boundary-span] task=%u scope=%s addr=0x%06X span=0x%06X..0x%06X raw=0x%02X len=%u pending=%u\n",
                            g_e9prov.task, g_e9prov.control ? "control" : "sec2",
                            emitted, start, end, raw_opcode, (end - start) / 8u,
                            pending);
                    fflush(stderr);
                }
            }
            if (g_e9prov.control || g_e9prov.target) {
                fprintf(stderr,
                        "[e9-prov-span] task=%u scope=%s addr=0x%06X span=0x%06X..0x%06X raw=0x%02X len=%u pending=%u\n",
                        g_e9prov.task, g_e9prov.control ? "control" : "sec2", emitted,
                        start, end, raw_opcode, (end - start) / 8u, pending);
            }
        }
    }
}

extern "C" void rs64_e9prov_condition(const char *kind, uint32_t address,
                                       uint32_t length, uint32_t raw_opcode,
                                       uint32_t pending, uint64_t submit_serial,
                                       uint32_t submit_lo, uint32_t submit_hi) {
    if (!log_e9_provenance() || !kind || length == 0 || submit_hi <= submit_lo) return;
    address &= 0x7FFFFFu;
    const uint32_t end = address + length;
    uint32_t kind_id = 0;
    if (std::strcmp(kind, "direct") == 0) kind_id = 1;
    else if (std::strcmp(kind, "span") == 0) kind_id = 2;
    else if (std::strcmp(kind, "pending") == 0) kind_id = 3;
    else if (std::strcmp(kind, "extended") == 0) kind_id = 4;
    else return;
    for (uint32_t emitted : g_e9prov.emitted_addrs) {
        const bool match = (kind_id == 1 || kind_id == 4) ? emitted == address :
            (address <= emitted && emitted < end);
        if (!match || emitted < submit_lo || emitted >= submit_hi) continue;
        g_e9prov.conditions.push_back({emitted, submit_serial, submit_lo, submit_hi, kind_id});
        if (kind_id == 1) ++g_e9prov.condition_direct;
        else if (kind_id == 2) ++g_e9prov.condition_span;
        else if (kind_id == 3) ++g_e9prov.condition_pending;
        else ++g_e9prov.condition_extended;
        static uint32_t lines = 0;
        if (lines++ < 2048) {
            fprintf(stderr,
                    "[rdp-condition] task=%u scope=%s kind=%s addr=0x%06X len=%u raw=0x%02X pending=%u serial=%llu range=0x%06X..0x%06X\n",
                    g_e9prov.task, g_e9prov.control ? "control" : "sec2", kind,
                    emitted, length, raw_opcode, pending,
                    (unsigned long long)submit_serial, submit_lo, submit_hi);
            fflush(stderr);
        }
    }
}

static void rs64_e9prov_mark_submitted(uint32_t lo, uint32_t hi) {
    if (!log_e9_provenance()) return;
    for (uint32_t addr : g_e9prov.emitted_addrs) {
        if (lo <= addr && addr < hi) ++g_e9prov.submitted;
    }
}

// Called at RT64's raw-opcode fetch. This is deliberately a bridge-owned
// address set: a match proves this exact emitted output byte reached RT64's
// authoritative parser, not merely that some E9 was counted elsewhere.
extern "C" void rs64_e9prov_authoritative_fetch(uint32_t address) {
    if (!log_e9_provenance()) return;
    address &= 0x7FFFFFu;
    ++g_e9prov.authoritative;
    if (g_e9prov.first_authoritative == 0xFFFFFFFFu)
        g_e9prov.first_authoritative = address;
    bool match = false;
    for (uint32_t emitted : g_e9prov.emitted_addrs) {
        if (emitted == address) {
            match = true;
            g_e9prov.fetched_addrs.push_back(address);
            ++g_e9prov.matched;
            if (g_e9prov.first_match == 0xFFFFFFFFu)
                g_e9prov.first_match = address;
            break;
        }
    }
    if (g_e9prov.control || g_e9prov.target) {
        fprintf(stderr, "[e9-prov-fetch] task=%u scope=%s addr=0x%06X match=%u\n",
                g_e9prov.task, g_e9prov.control ? "control" : "sec2", address,
                match ? 1u : 0u);
        fflush(stderr);
    }
}

extern "C" void rs64_e9prov_handler() {
    if (log_e9_provenance() || log_e9_unified()) ++g_e9prov.handler;
}

extern "C" void rs64_e9prov_fullsync_dispatch() {
    if (log_e9_provenance()) ++g_e9prov.dispatched;
}

// Drain accessor for diagnostic — see rt64_render_context.cpp / main.cpp.
extern "C" void rs64_dpc_drain_histogram(uint32_t out[64]) {
    for (int i = 0; i < 64; ++i) {
        out[i] = g_task_op_count[i];
        g_task_op_count[i] = 0;
    }
}

// Cumulative opcode histogram across the whole session (NOT reset per task).
// Used by the SEH handler in rt64_render_context.cpp to dump what kinds of
// commands were submitted before the crash.
static std::atomic<uint32_t> g_cumulative_op_count[64] = {};
extern "C" void rs64_dpc_get_cumulative_histogram(uint32_t out[64]) {
    for (int i = 0; i < 64; ++i) {
        out[i] = g_cumulative_op_count[i].load(std::memory_order_relaxed);
    }
}

// Cumulative FULL_SYNC count across the whole session (NOT reset per task).
static std::atomic<uint32_t> g_cumulative_fullsyncs{0};
extern "C" uint32_t rs64_dpc_get_cumulative_fullsyncs() {
    return g_cumulative_fullsyncs.load(std::memory_order_relaxed);
}

// Phys RDRAM address of the most recent FULL_SYNC (0x29) byte the bridge
// forwarded this process. 0xFFFFFFFF if none yet. Used by ROGUESQ_LOG_DL_SYNC
// to correlate LLE emission with guest F3D walk (item -350 / s581).
extern "C" uint32_t rs64_dpc_get_last_fullsync_addr() {
    return g_last_fullsync_addr.load(std::memory_order_acquire);
}

// Sticky last dpc-wrap + last successful submit range (s662 cimg-origin-desync).
// processRDPLists reads these via weak symbols so a WILD SETCIMG dump can say
// whether its task address sits inside a recently-wrapped ring.
static std::atomic<uint32_t> g_last_wrap_end{0};
static std::atomic<uint32_t> g_last_wrap_seen{0};
static std::atomic<uint32_t> g_last_wrap_start{0};
static std::atomic<uint32_t> g_last_wrap_n{0};
static std::atomic<uint32_t> g_last_submit_lo{0};
static std::atomic<uint32_t> g_last_submit_hi{0};
static std::atomic<uint64_t> g_submit_serial{0};
extern "C" void rs64_dpc_get_last_wrap(uint32_t *end, uint32_t *seen,
                                      uint32_t *start, uint32_t *n) {
    if (end)   *end   = g_last_wrap_end.load(std::memory_order_acquire);
    if (seen)  *seen  = g_last_wrap_seen.load(std::memory_order_acquire);
    if (start) *start = g_last_wrap_start.load(std::memory_order_acquire);
    if (n)     *n     = g_last_wrap_n.load(std::memory_order_acquire);
}
extern "C" void rs64_dpc_get_last_submit(uint32_t *lo, uint32_t *hi) {
    if (lo) *lo = g_last_submit_lo.load(std::memory_order_acquire);
    if (hi) *hi = g_last_submit_hi.load(std::memory_order_acquire);
}
extern "C" uint64_t rs64_dpc_get_last_submit_serial() {
    return g_submit_serial.load(std::memory_order_acquire);
}
extern "C" void rs64_dpc_get_task_range(uint32_t *first_lo, uint32_t *first_hi,
                                          uint32_t *last_lo, uint32_t *last_hi,
                                          uint32_t *min_lo, uint32_t *max_hi) {
    if (first_lo) *first_lo = s_task_first_lo;
    if (first_hi) *first_hi = s_task_first_hi;
    if (last_lo) *last_lo = s_task_last_lo;
    if (last_hi) *last_hi = s_task_last_hi;
    if (min_lo) *min_lo = s_task_min_lo;
    if (max_hi) *max_hi = s_task_max_hi;
}
extern "C" uint32_t rs64_e9prov_current_task() {
    return g_e9prov.task;
}

extern "C" uint32_t rs64_e9prov_current_root_dl() {
    return g_e9prov.root_dl;
}

extern "C" void rs64_f5_vtxcolor_get(uint32_t *task, uint32_t *valid,
                                       uint32_t *ordinal, uint32_t *pc,
                                       uint32_t *source) {
    std::lock_guard<std::mutex> lock(g_f5_vtxcolor_mutex);
    if (task) *task = g_f5_vtxcolor_state.task;
    if (valid) *valid = g_f5_vtxcolor_state.valid ? 1u : 0u;
    if (ordinal) *ordinal = g_f5_vtxcolor_state.ordinal;
    if (pc) *pc = g_f5_vtxcolor_state.pc;
    if (source) *source = g_f5_vtxcolor_state.source;
}
extern "C" uint32_t rs64_e9prov_current_scope() {
    return g_e9prov.control ? 1u : g_e9prov.target ? 2u : 0u;
}

extern "C" bool rs64_dpc_take_synthetic_consumer(uint64_t *serial) {
    if (!g_synthetic_consumer_pending.exchange(false, std::memory_order_acq_rel))
        return false;
    if (serial) *serial = g_synthetic_submit_serial.load(std::memory_order_acquire);
    return true;
}

// s6083 G3b: scan every submitted RDP range for triangles whose edge-walk
// coordinates fall far outside the 320x240 viewport (spike-line signature).
// ROGUESQ_LOG_SPIKE=1 logs; ROGUESQ_SPIKE_CTL=<px> shrinks the guard band to
// <px> beyond the viewport as a positive control (ordinary tris must fire).
std::atomic<int> g_rs64_swap_n{0};
extern "C" int rs64_swap_n(void) { return g_rs64_swap_n.load(std::memory_order_relaxed); } // s6528 C accessor
// s6896 G5b: ROGUESQ_G5B_TG=<file>. Per swap: TriGen count, s16 lane bases, how many commands run past s16 (wa/wb) and past
// half range (ha/hb, same-run positive control for the wrap arithmetic), then the terrain window, DEB4 and the camera block.
// W lines: raw words of the first wrapping commands of a swap. Called on the gfx thread from the ucode fetch boundary.
static FILE *g5b_tg_open() { const char *e = std::getenv("ROGUESQ_G5B_TG"); return (e && *e) ? fopen(e, "w") : (FILE *)nullptr; }
static FILE *g_g5b_tg = g5b_tg_open();
extern "C" { int rs64_g5b_tg_on = g_g5b_tg != nullptr; }
// s6896 G5b: ROGUESQ_G5B_TG_FIX: default on at dd>1, off at dd1 (retail path untouched); =0 off, =1 on, =tog on in odd seconds of
// the mach clock so sheets can be binned by parity in one run. Mode 2 quads only, the only commands seen to wrap.
static int g5b_tg_fix_init() {
    const char *e = std::getenv("ROGUESQ_G5B_TG_FIX");
    if (e && *e) return *e == 't' ? 2 : *e != '0';
    const char *d = std::getenv("ROGUESQ_DRAW_DISTANCE");
    return (d && *d && atof(d) > 1.0) ? 1 : 0;
}
extern "C" { int rs64_g5b_tg_fix = g5b_tg_fix_init(); }
// s7427 class CJ: the latch above runs at static init, before main()'s env policy, so it saw the RAW ROGUESQ_DRAW_DISTANCE.
// The s7358 sanitiser unsets a non-number ("4x" -> atof 4, "inf") so the game runs retail dd1, but this latch had already armed
// the dd>1 TriGen fix. main() calls this after the policy; ROGUESQ_S7427_REINIT=0 keeps the pre-policy value (old).
extern "C" int rs64_s7427_tg_fix_reinit() {
    const int pre = rs64_g5b_tg_fix;
    const char *o = std::getenv("ROGUESQ_S7427_REINIT");
    if (!(o && *o == '0')) rs64_g5b_tg_fix = g5b_tg_fix_init();
    return pre;
}
extern "C" int rs64_g5b_tg_edge(uint32_t w0, uint32_t *p8, uint32_t *p9) {
    if (((w0 >> 8) & 0xFF) != 2) return 0;
    // s6898 G5b lever: ROGUESQ_G5B_TG_REACH=<r> zeroes the step of mode 2 quads with a base past r, =<r>t in odd mach seconds only. Test lever, off by default.
    static const int reach = [] { const char *e = std::getenv("ROGUESQ_G5B_TG_REACH"); return e && *e ? atoi(e) : 0; }();
    static const bool reach_tog = [] { const char *e = std::getenv("ROGUESQ_G5B_TG_REACH"); return e && *e && e[strlen(e) - 1] == 't'; }();
    if (reach) {
        const int ra = abs((int)(int16_t)(*p8 >> 16)), rb = abs((int)(int16_t)(*p9 >> 16));
        static const double rtick = [] { mach_timebase_info_data_t b; mach_timebase_info(&b); return (double)b.numer / b.denom / 1e9; }();
        if ((ra > reach || rb > reach) && (!reach_tog || ((uint64_t)(mach_absolute_time() * rtick) & 1))) { *p9 &= 0xFFFF0000u; return 1; }
    }
    if (rs64_g5b_tg_fix == 2) {
        static const double tick = [] { mach_timebase_info_data_t b; mach_timebase_info(&b); return (double)b.numer / b.denom / 1e9; }();
        if (!((uint64_t)(mach_absolute_time() * tick) & 1)) return 0;
    }
    const int v0 = (int)(*p9 & 0xFFFF), a = (int16_t)(*p8 >> 16), b = (int16_t)(*p9 >> 16);
    int hit = 0;
    if (a + v0 > 32767) { *p8 = (*p8 & 0xFFFFu) | ((uint32_t)(uint16_t)(32767 - v0) << 16); hit = 1; }
    if (b + v0 > 32767) { *p9 = (*p9 & 0xFFFFu) | ((uint32_t)(uint16_t)(32767 - v0) << 16); hit = 1; }
    return hit;
}
extern "C" void rs64_g5b_trigen(uint32_t pc, uint32_t w0, uint32_t w1, uint32_t p8, uint32_t p9) {
    static int s_sw = -1, s_wl = 0;
    static struct { uint32_t n, m2, wa, wb, ha, hb; int mina, maxa, minb, maxb, v0min, v0max; uint32_t hq[8]; } s = {};
    const int sw = g_rs64_swap_n.load(std::memory_order_relaxed);
    if (sw != s_sw) {
        if (s_sw >= 0 && s.n && g_rdram_for_submit) {
            auto rd = [](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & 0xFFFFFCu), 4); return v; };
            auto fl = [&](uint32_t a) { uint32_t v = rd(a); float f; memcpy(&f, &v, 4); return f; };
            fprintf(g_g5b_tg, "S %d %llu n=%u m2=%u wa=%u wb=%u ha=%u hb=%u a=%d,%d b=%d,%d v0=%d,%d win=%d,%d,%d,%d deb4=%g tt=", s_sw, (unsigned long long)mach_absolute_time(), s.n, s.m2, s.wa, s.wb, s.ha, s.hb,
                    s.mina, s.maxa, s.minb, s.maxb, s.v0min, s.v0max, (int)rd(0x132DB0), (int)rd(0x132DB4), (int)rd(0x132DB8), (int)rd(0x132DBC), fl(0x09DEB4));
            for (uint32_t q = 0x10; q < 0x50; q += 4) fprintf(g_g5b_tg, "%g,", fl(0x136DC0 + q));
            const uint32_t cp = rd(0x138D1C);
            fprintf(g_g5b_tg, " cam=");
            if (cp >= 0x80000000u && cp < 0x80800000u) for (uint32_t q = 0; q < 22; q++) fprintf(g_g5b_tg, "%g,", fl(cp + 0x28 + q * 4));
            fprintf(g_g5b_tg, " hq="); for (int q = 0; q < 8; q++) fprintf(g_g5b_tg, "%u,", s.hq[q]); // s6898: mode 2 quads by max(|a|,|b|) / 4096
            fputc('\n', g_g5b_tg); fflush(g_g5b_tg);
        }
        s_sw = sw; s_wl = 0; s = {}; s.mina = s.minb = s.v0min = 1 << 30; s.maxa = s.maxb = s.v0max = -(1 << 30);
    }
    s.n++;
    // s6911 G5h: ROGUESQ_G5B_TGCMD=<file>, every TriGen command as fetched: u32 swap, then the 10 words at the DMEM cursor. params[1..2] are the
    // quad's corner heights, [8..9] the bases and step (F5Rogue.cpp TriGen02_BuildVtxData). Joins the ROGUESQ_G5B_TRIS stream to world quads.
    static FILE *s_tc = [] { const char *e = std::getenv("ROGUESQ_G5B_TGCMD"); FILE *f = (e && *e) ? fopen(e, "wb") : (FILE *)nullptr; if (f) setvbuf(f, nullptr, _IOFBF, 1 << 22); return f; }();
    if (s_tc && g_dmem_cur) {
        uint32_t r[11]; r[0] = (uint32_t)sw;
        for (int q = 0; q < 10; q++) memcpy(&r[q + 1], g_dmem_cur + ((pc + q * 4) & 0xFFCu), 4);
        fwrite(r, sizeof r, 1, s_tc);
    }
    const uint32_t mode = (w0 >> 8) & 0xFF, sub = w0 & 0xFF;
    s.m2 += mode == 2;
    if (mode != 0 && mode != 2) return;
    // Mode 2 is one quad, base to base + step (TriGen02_BuildVtxData); mode 0 is a 5x5 or 3x3 grid of the same step.
    const int a = (int16_t)(p8 >> 16), b = (int16_t)(p9 >> 16), v0 = (int)(p9 & 0xFFFF), span = (mode == 2 ? 1 : sub == 0 ? 4 : 2) * v0;
    if (a < s.mina) s.mina = a; if (a > s.maxa) s.maxa = a; if (b < s.minb) s.minb = b; if (b > s.maxb) s.maxb = b;
    if (v0 < s.v0min) s.v0min = v0; if (v0 > s.v0max) s.v0max = v0;
    if (mode == 2) { const int r = std::max(abs(a), abs(b)) >> 12; s.hq[r > 7 ? 7 : r]++; }
    const bool wa = a + span > 32767, wb = b + span > 32767;
    s.wa += wa; s.wb += wb; s.ha += a + span > 16383; s.hb += b + span > 16383;
    if ((wa || wb) && s_wl < 6) { s_wl++; fprintf(g_g5b_tg, "W %d pc=%X w0=%08X w1=%08X p8=%08X p9=%08X a=%d b=%d v0=%d\n", sw, pc, w0, w1, p8, p9, a, b, v0); }
}
// s6895 G5b: ROGUESQ_G5B_FRAME=<file> records what the RDP was given, for offline replay through angrylion
// (tools/angrylion_replay/frame_replay.c). Records, u32 tag first: 'SWAP' mach(u64) swap; 'RAM ' 16 MB RDRAM, at the first range
// of every ROGUESQ_G5B_FRAME_EVERY-th swap (default 10); 'RNG ' lo len bytes (after the spike cull, so what RT64 gets).
// ROGUESQ_G5B_FRAME_FROM=<swap> starts it; ROGUESQ_G5B_FRAME_MAX_MB caps it (default 24000).
// s7128: RT64 (rt64_gbi_rdp.cpp W_SHEET_POS) calls this on every corner-hairline detection, dropped or not (=t off arm).
static std::atomic<int> g_rs64_wsheetpos_trig{-1};
extern "C" void rs64_wsheetpos_note(int arm) { (void)arm; g_rs64_wsheetpos_trig.store(g_rs64_swap_n.load(std::memory_order_relaxed), std::memory_order_relaxed); }
// s7166 g3-219-cutscene-hole: ROGUESQ_G5B_FRAME_TRIG_LB=<k> makes the TRIG ring fire on the k-th letterbox span (default 1) instead of on
// W_SHEET_POS detections. A span = setupMissionTransitionScreenOverlay calls (tools/apply_s6898_letterbox.py site, every letterboxed
// cutscene frame) with gaps < 30 swaps, counted only from ROGUESQ_G5B_FRAME_FROM. One-shot: later spans are logged, not dumped.
// Every span start/end goes to stderr as [lbspan], so a run names its cutscene swaps even without the recorder.
static std::atomic<int> g_rs64_lb_trig{-1};
extern "C" void rs64_frame_trig_lb(void) {
    static const int k = [] { const char *e = std::getenv("ROGUESQ_G5B_FRAME_TRIG_LB"); return e && *e ? std::max(1, atoi(e)) : 0; }();
    static const int from = [] { const char *e = std::getenv("ROGUESQ_G5B_FRAME_FROM"); return e && *e ? atoi(e) : 0; }();
    static int a = -1, b = -1, n = 0; static uint64_t calls = 0;
    const int sw = g_rs64_swap_n.load(std::memory_order_relaxed);
    calls++;
    if (b >= 0 && sw - b < 30) { b = sw; return; }
    if (a >= 0) fprintf(stderr, "[lbspan] end start=%d last=%d\n", a, b);
    a = b = sw;
    if (sw >= from) n++;
    fprintf(stderr, "[lbspan] start sw=%d n=%d k=%d calls=%llu\n", sw, n, k, (unsigned long long)calls);
    if (k > 0 && sw >= from && n == k) { g_rs64_lb_trig.store(sw, std::memory_order_relaxed); fprintf(stderr, "[lbspan] TRIGGER sw=%d\n", sw); }
}
static void rs64_g5b_frame(uint32_t lo, uint32_t hi) {
    static FILE *f = [] { const char *e = std::getenv("ROGUESQ_G5B_FRAME"); FILE *o = (e && *e) ? fopen(e, "wb") : (FILE *)nullptr; if (o) setvbuf(o, nullptr, _IOFBF, 1 << 24); return o; }();
    if (!f || g_rdram_for_submit == nullptr || hi <= lo || hi > kSubmitRamEnd) return;
    static const int from = [] { const char *e = std::getenv("ROGUESQ_G5B_FRAME_FROM"); return e && *e ? atoi(e) : 0; }();
    static const int every = [] { const char *e = std::getenv("ROGUESQ_G5B_FRAME_EVERY"); return e && *e ? atoi(e) : 10; }();
    static const uint64_t cap = [] { const char *e = std::getenv("ROGUESQ_G5B_FRAME_MAX_MB"); return (uint64_t)(e && *e ? atoll(e) : 24000) << 20; }();
    static uint64_t total = 0; static int last = -1, lastram = -1000000;
    const int sw = g_rs64_swap_n.load(std::memory_order_relaxed);
    if (sw < from || total >= cap) return;
    auto put = [&](const void *p, size_t n) { fwrite(p, 1, n, f); total += n; };
    // s7128 wsheet-escape: ROGUESQ_G5B_FRAME_TRIG=<pre>,<post> keeps the last <pre>+1 swaps (16 MB RAM + ranges each) in memory and
    // writes them, in the normal format with a RAM record per swap, only when RT64 reports a W_SHEET_POS detection
    // (rs64_wsheetpos_note, either arm) plus the <post> swaps after it. RT64 handles a swap's tris 2-10 ms after the bridge moves on,
    // so the ring must cover the lag. A whole 300 s flight then costs ~17 MB per kept swap instead of 12 GB per 15 s.
    static const int trigPre = [] { const char *e = std::getenv("ROGUESQ_G5B_FRAME_TRIG"); return e && *e ? std::max(1, atoi(e)) : 0; }();
    if (trigPre > 0) {
        static const int trigPost = [] { const char *e = std::getenv("ROGUESQ_G5B_FRAME_TRIG"); const char *c = e ? std::strchr(e, ',') : nullptr; return c ? atoi(c + 1) : 4; }();
        struct Slot { int sw = -1; uint64_t t = 0; std::vector<uint8_t> ram, rng; };
        static std::vector<Slot> ring(trigPre + 1);
        static int cur = -1, lastDumped = -1, dumpUntil = -1;
        auto dump = [&](Slot &q) {
            if (q.sw < 0 || q.sw <= lastDumped || q.ram.empty()) return;
            const uint32_t m = 0x50415753u, qs = (uint32_t)q.sw, mr = 0x204D4152u; put(&m, 4); put(&q.t, 8); put(&qs, 4);
            put(&mr, 4); put(q.ram.data(), kSubmitRamEnd); put(q.rng.data(), q.rng.size()); fflush(f); lastDumped = q.sw;
        };
        if (sw != last) {
            if (cur >= 0) {  // the previous slot is complete
                static const bool lbmode = [] { const char *e = std::getenv("ROGUESQ_G5B_FRAME_TRIG_LB"); return e && *e; }();
                const int trig = lbmode ? g_rs64_lb_trig.exchange(-1) : g_rs64_wsheetpos_trig.exchange(-1);
                if (trig >= 0) {
                    dumpUntil = std::max(dumpUntil, ring[cur].sw + trigPost);
                    std::vector<Slot *> ord; for (auto &q : ring) if (q.sw >= 0) ord.push_back(&q);
                    std::sort(ord.begin(), ord.end(), [](Slot *a, Slot *b) { return a->sw < b->sw; });
                    for (Slot *q : ord) dump(*q);
                    fprintf(stderr, "[g5btrig] trig_sw=%d at_sw=%d dumped_to=%d until=%d MB=%llu\n", trig, ring[cur].sw, lastDumped, dumpUntil, (unsigned long long)(total >> 20));
                } else if (ring[cur].sw <= dumpUntil) dump(ring[cur]);
            }
            last = sw; cur = (cur + 1) % (int)ring.size(); Slot &q = ring[cur];
            q.sw = sw; q.t = mach_absolute_time(); q.rng.clear();
            if (q.ram.size() != kSubmitRamEnd) q.ram.resize(kSubmitRamEnd);
            std::memcpy(q.ram.data(), g_rdram_for_submit, kSubmitRamEnd);
        }
        Slot &q = ring[cur]; const uint32_t m = 0x20474E52u, n = hi - lo; const size_t o = q.rng.size(); q.rng.resize(o + 12 + n);
        std::memcpy(&q.rng[o], &m, 4); std::memcpy(&q.rng[o + 4], &lo, 4); std::memcpy(&q.rng[o + 8], &n, 4); std::memcpy(&q.rng[o + 12], g_rdram_for_submit + lo, n);
        return;
    }
    if (sw != last) { last = sw; const uint32_t m = 0x50415753u, q = (uint32_t)sw; const uint64_t t = mach_absolute_time(); put(&m, 4); put(&t, 8); put(&q, 4); fflush(f); }
    if (sw - lastram >= every) { lastram = sw; const uint32_t m = 0x204D4152u; put(&m, 4); put(g_rdram_for_submit, kSubmitRamEnd); }
    const uint32_t m = 0x20474E52u, n = hi - lo; put(&m, 4); put(&lo, 4); put(&n, 4); put(g_rdram_for_submit + lo, n);
}
extern "C" int rs64_s7106_on; extern "C" void rs64_s7106_btri(void);  // s7106 rsptri control
extern "C" uint8_t rs64_s7107_pop(void);  // s7107 painter: per-triangle source-cell tag (0xFF = untagged)
static int g_rs64_skyz_why = 7; static uint32_t g_rs64_skyz_m = 0; static bool g_rs64_skyz_sel2 = false;  // s6948: SKYZ decision for the audit
static bool g_s7636_odd = false;  // s7636: GLUE_TOG parity of the current submit (set in rs64_dpc_record_submit_impl), for FASTSPIKE=tog
// s7635: rb/rc = the region walker's per-command body when fused (rs64_region_scan(lo, hi, fused)); it runs right after this
// walker's body on each command, in submit order, so it sees the same bytes as the old second pass (see the s7635 note there).
typedef uint32_t (*rs64_rbody_fn)(void *, uint32_t);
static void rs64_spike_scan(uint32_t lo, uint32_t hi, rs64_rbody_fn rb = nullptr, void *rc = nullptr) {
    static const bool on = [] { const char *e = std::getenv("ROGUESQ_LOG_SPIKE"); return e && *e && *e != '0'; }();
    // 2026-10-31 owner: cull is DEFAULT ON (ROGUESQ_CULL_SPIKE=0 restores retail wedges). It used to run only
    // under ROGUESQ_LOG_SPIKE=1, so the documented CULL_SPIKE=1 opt-in alone was a no-op.
    // s6906 G5f: =tog culls in odd seconds of the mach clock only (24 MHz, as W_CLAMP=tog), the same-run control for the escape census.
    static const bool cull = [] { const char *e = std::getenv("ROGUESQ_CULL_SPIKE"); return !(e && *e == '0'); }();
    static const bool cull_tog = [] { const char *e = std::getenv("ROGUESQ_CULL_SPIKE"); return e && *e == 't'; }();
    // s6894 G5b: ROGUESQ_G5B_BIGTRI=<file>, one line per swap: mach time (same clock as g5b_capture displayTime), the
    // largest triangle by hull area, its raw edge vertices and image width. Joins presented frames to the RDP stream.
    static FILE *s_big = [] { const char *e = std::getenv("ROGUESQ_G5B_BIGTRI"); return (e && *e) ? fopen(e, "w") : (FILE *)nullptr; }();
    // s6894: ROGUESQ_G5B_TRIS=<file>, every triangle: u32 0xF5F5F5F5, u64 mach, u32 swap at each swap; then per tri
    // u8 op, u8 pad, u16 cw, u32 timg, u32 z, 10 x s16 (x,y of the 5 edge vertices, 1/4 px, saturated).
    static FILE *s_tf = [] { const char *e = std::getenv("ROGUESQ_G5B_TRIS"); FILE *f = (e && *e) ? fopen(e, "wb") : (FILE *)nullptr; if (f) setvbuf(f, nullptr, _IOFBF, 1 << 22); return f; }();
    static uint32_t s_timg = 0;
    // s6894: ROGUESQ_G5B_SHEET=<file>, one line per triangle over 40000 px area: swap, mach, last w0/w1 of each RDP state
    // command, FNV of 2 KB at the texture image, then the raw triangle words. Splits visible from invisible sheets.
    static FILE *s_sh = [] { const char *e = std::getenv("ROGUESQ_G5B_SHEET"); return (e && *e) ? fopen(e, "w") : (FILE *)nullptr; }();
    static uint32_t s_st[64][2] = {};
    // s6904 G5e: ROGUESQ_G5E_FOG=<file>. On every 120th swap, one line per shaded Z triangle: swap, blender word, fog colour,
    // top vertex z (s15.16), shade alpha int (s16, unclamped) and dA/dy, dz/dy. Pairs z and fog at the same point.
    static FILE *s_fg = [] { const char *e = std::getenv("ROGUESQ_G5E_FOG"); return (e && *e) ? fopen(e, "w") : (FILE *)nullptr; }();
    // s6894: ROGUESQ_G5B_KILLSHEET=1 zeroes near-plane terrain sheets (op 0F, terrain blender, hull > 100000 px); =tog does
    // so on odd seconds of the mach clock only, so presented events can be binned by parity within one run.
    static const int killsheet = [] { const char *e = std::getenv("ROGUESQ_G5B_KILLSHEET"); return !(e && *e) ? 0 : (*e == 't' ? 2 : 1); }();
    // s6916 G5h: ROGUESQ_DD_MELT=1 turns the terrain fog blender (C811: fog colour x shade alpha + pixel x (1 - alpha)) into memory x shade
    // alpha + pixel x (1 - alpha), in cycle 2 with FORCE_BL + IM_RD (1200: in cycle 1 RT64's last-cycle passthrough resets the alpha to 1), so far terrain fades into the sky already drawn rather than to a flat colour that ends in a
    // straight edge. =tog on odd seconds of the mach clock (24 MHz), the same-run control. Default off, retail unaffected.
    static const int melt = [] { const char *e = std::getenv("ROGUESQ_DD_MELT"); return !(e && *e && *e != '0') ? 0 : (*e == 't' ? 2 : 1); }();
    static uint64_t s_melt_n = 0;
    // s6917 G5h: ROGUESQ_DD_SKYZ=1 puts the sky back at the far limit at dd>1. The sky draws with blender 00552224 (z from SET_PRIM_DEPTH, update, no compare). Its depth is
    // 32703 at dd1 and 32620-32627 at dd4, because the far scale moves it in, while far ships and beam tops sit at 32500-32767. They then fail the compare over bare sky
    // and survive only over terrain, which rewrites z without compare: beams end flat at the sea edge and their ships go. The sky must keep writing z: the game's z clear
    // fill usually starts part way down the screen, and above that the sky's z write is the clear. So the depth is rewritten, not the update bit. =tog on odd seconds of the
    // mach clock (24 MHz). Default off, dd1 never touched. Needs the scan live, like MELT.
    static const int skyz = [] { const char *e = std::getenv("ROGUESQ_DD_SKYZ"), *d = std::getenv("ROGUESQ_DRAW_DISTANCE"); if (!(e && *e && *e != '0') || !(d && atof(d) > 1.0)) return 0; return *e == 't' ? 2 : 1; }();
    // The RSP kicks tiny submits, so SET_PRIM_DEPTH has often gone to the RDP before the sky's mode word shows what it was for: looking back from the mode reached 8% of sky
    // groups. So a depth is rewritten when it arrives, if it matches one of the last 8 depths that were followed by the sky mode; those are stable from frame to frame.
    static uint64_t s_skyz_n = 0, s_skyz_miss = 0;
    static uint32_t s_skyz_ring[8] = {}, s_skyz_w = 0, s_skyz_pd = 0;  // sky depths learned; last depth seen, as the game wrote it
    static bool s_skyz_done = true;  // the last SET_PRIM_DEPTH seen is already handled, so later sky modes under it need nothing
    uint32_t skyz_pd = 0xFFFFFFFFu;  // its address when it is in this range and so still patchable
    static struct { double area, v[5][2]; uint32_t off, op, cw, n, big, w0, w1; int swap; } s_bt = {};
    if (g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    if (!(on || cull)) {  // s7635: spike off but fused with the region walk: the region body alone, same stride
        if (rb) for (uint32_t a = lo & ~3u; a + 8 <= hi;) { const uint32_t m = rb(rc, a); if (!m) break; a += m; }
        return;
    }
    static const double guard = [] { const char *e = std::getenv("ROGUESQ_SPIKE_CTL"); return e && *e ? atof(e) : 640.0; }();
    static uint64_t s_tris = 0, s_bad = 0, s_logged = 0, s_culled = 0;
    static uint32_t s_cw = 320;  // s6695: width of the last SET_COLOR_IMAGE seen in a submitted range
    static int s_swap = -1; static uint32_t s_swap_tris = 0, s_swap_bad = 0;
    const int sw = g_rs64_swap_n.load(std::memory_order_relaxed);
    // s6918 G5h: ROGUESQ_G5H_BAND=<file>, one row per swap: swap, mach, tris under the near terrain combiner (127E24, 1 cycle) and the far one (127FFF, 2 cycle fog),
    // then the far cutoff inputs as guest words: 0x8009DEAC radius, DEB0, DEB4 cutoff^2, 0x80136FBC scene scalar, 0x80130C54..60, and 32 words of the camera at *0x80138D1C.
    // Same words as the retail oracle spec in scratch/s6918/oracle.zsh. Diagnostic, off unless set.
    static FILE *s_bd = [] { const char *e = std::getenv("ROGUESQ_G5H_BAND"); return (e && *e) ? fopen(e, "w") : (FILE *)nullptr; }();
    static uint32_t s_bc0 = 0, s_bc1 = 0, s_bA = 0, s_bB = 0;
    if (s_bd && sw != s_swap) {
        const auto gw = [](uint32_t ph) { return *reinterpret_cast<const uint32_t *>(g_rdram_for_submit + ph); };
        fprintf(s_bd, "%d %llu %u %u", s_swap, (unsigned long long)mach_absolute_time(), s_bA, s_bB);
        for (uint32_t ph : {0x9DEACu, 0x9DEB0u, 0x9DEB4u, 0x136FBCu, 0x130C54u, 0x130C58u, 0x130C5Cu, 0x130C60u}) fprintf(s_bd, " %08X", gw(ph));
        const uint32_t cam = gw(0x138D1Cu); fprintf(s_bd, " %08X", cam);
        if ((cam & 0xFF800003u) == 0x80000000u) for (uint32_t i = 0; i < 32; i++) fprintf(s_bd, " %08X", gw((cam & 0x7FFFFFu) + 4 * i));
        { extern uint32_t g_rs64_s6919[12]; for (int i = 0; i < 12; i++) fprintf(s_bd, " %08X", g_rs64_s6919[i]); }  // s6919: what the chain read at 0x800434F4, tools/apply_s6919_cutlive.py
        fputc('\n', s_bd); fflush(s_bd); s_bA = s_bB = 0;
    }
    if (sw != s_swap) {
        if (on && s_swap_bad) { fprintf(stderr, "[spike-swap] swap=%d tris=%u bad=%u total_tris=%llu total_bad=%llu culled=%llu\n", s_swap, s_swap_tris, s_swap_bad, (unsigned long long)s_tris, (unsigned long long)s_bad, (unsigned long long)s_culled); fflush(stderr); }
        s_swap = sw; s_swap_tris = 0; s_swap_bad = 0;
        if (s_big && s_bt.n) {
            fprintf(s_big, "%llu %d n=%u big=%u cw=%u op=%02X off=%06X area=%.0f w0=%08X w1=%08X", (unsigned long long)mach_absolute_time(), s_bt.swap, s_bt.n, s_bt.big, s_bt.cw, s_bt.op, s_bt.off, s_bt.area, s_bt.w0, s_bt.w1);
            for (auto &q : s_bt.v) fprintf(s_big, " %.1f,%.1f", q[0], q[1]);
            fputc('\n', s_big); fflush(s_big);
        }
        s_bt = {}; s_bt.swap = sw;
        if (s_tf) { const uint32_t m = 0xF5F5F5F5u; const uint64_t t = mach_absolute_time(); const uint32_t q = (uint32_t)sw; fwrite(&m, 4, 1, s_tf); fwrite(&t, 8, 1, s_tf); fwrite(&q, 4, 1, s_tf); }
    }
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & kSubmitRamMask), 4); return v; };
    auto sx14 = [](uint32_t v) { return (double)(((int32_t)(v << 18)) >> 18) / 4.0; };
    auto body = [&](uint32_t a) -> uint32_t {  // s7635: one command; returns its length, 0 = stop
        const uint32_t w0 = rd(a), w1 = rd(a + 4);
        const uint32_t op = (w0 >> 24) & 0x3F;
        if ((s_sh || killsheet || s_fg) && op >= 0x20) { s_st[op][0] = w0; s_st[op][1] = w1; }
        if (melt && op == 0x2F && (w1 >> 16) == 0xC811u && (melt == 1 || ((mach_absolute_time() / 24000000ull) & 1))) {
            const uint32_t n1 = 0x12000000u | (w1 & 0xFFFFu) | 0x4040u; memcpy(g_rdram_for_submit + ((a + 4) & kSubmitRamMask), &n1, 4);
            if ((++s_melt_n & (s_melt_n - 1)) == 0) fprintf(stderr, "[dd-melt] n=%llu swap=%d %08X -> %08X\n", (unsigned long long)s_melt_n, sw, w1, n1);
        }
        // s6947: ROGUESQ_DD_SKYZ_SEL=tog alternates the rule on a 2 s period, so with DD_SKYZ=tog the 4 s cycle is off, value rule, off, SEL rule (one-run A/B).
        // s6947: SEL is now the default rule inside DD_SKYZ (=0 restores the s6917 value rule): two runs, live seconds, value rule rewrote 2421/2490 and 1675/1675
        // non-sky prim-z draws, SEL 0/1726 and 0/1155, sky rewrites 324k/338k and 68.8k/71.9k; shot 78 beams and far ships stay on SEL seconds (owner_sheet_s6947).
        static const int skyz_sel = [] { const char *e = std::getenv("ROGUESQ_DD_SKYZ_SEL"); return !(e && *e) ? 1 : *e == '0' ? 0 : *e == 't' ? 2 : 1; }();
        const bool sel_now = skyz_sel == 1 || (skyz_sel == 2 && ((mach_absolute_time() / 48000000ull) & 1));
        if (skyz) {
            const bool live = skyz == 1 || ((mach_absolute_time() / 24000000ull) & 1);
            auto put = [&](uint32_t at) {
                const uint32_t o1 = rd(at + 4), n1 = 0x7FFF0000u | (o1 & 0xFFFFu); memcpy(g_rdram_for_submit + ((at + 4) & kSubmitRamMask), &n1, 4);
                if ((++s_skyz_n & (s_skyz_n - 1)) == 0) fprintf(stderr, "[dd-skyz] n=%llu miss=%llu swap=%d %08X -> %08X\n", (unsigned long long)s_skyz_n, (unsigned long long)s_skyz_miss, sw, o1, n1);
            };
            // s6946: a sky depth value is shared by other prim-z modes (C8104A54, C4104A54: 3.2k draws per movie run on live seconds, ROGUESQ_DD_SKYZ_AUD), so a
            // ring match alone also pushed those to the far limit. Now the consumer decides: look ahead in this range for the first mode word or draw after the depth;
            // rewrite only if the sky mode comes first, or a draw comes under the sky mode. If the range ends first, rewrite unless the mode now set takes prim z and is
            // not the sky. s6946 opt-in; validated and made default s6947 (the s6946 b4 null was an audit fault).
            static uint32_t s_skyz_om0 = 0, s_skyz_om1 = 0;
            // s6948: why the last SET_PRIM_DEPTH was or was not rewritten, for ROGUESQ_DD_SKYZ_AUD: 0 put on arrival, 1 put late (sky mode first seen after it),
            // 2 SEL: non-sky mode word first, 3 SEL: draw first under a mode that does not read prim z, 4 SEL: draw first under a non-sky prim-z mode,
            // 5 SEL: range end under a non-sky prim-z mode, 6 off-live second, 7 not in the ring and no sky mode yet, 8 late but the depth sat in an earlier call (miss).
            static int s_skyz_why = 7; int why = 0;
            const auto pz = [](uint32_t m0, uint32_t m1) { return (m1 & 4u) && (m1 & 0x30u) && ((m0 >> 20) & 3u) < 2u; };  // the audit's consumer test
            auto skyish = [&](uint32_t at) {
                for (uint32_t b = at + 8; b + 8 <= hi;) {
                    const uint32_t o2 = (rd(b) >> 24) & 0x3F;
                    if (o2 == 0x2F) { why = 2; g_rs64_skyz_m = rd(b + 4); return g_rs64_skyz_m == 0x00552224u; }
                    if ((o2 >= 0x08 && o2 <= 0x0F) || o2 == 0x24 || o2 == 0x25 || o2 == 0x36) { why = pz(s_skyz_om0, s_skyz_om1) ? 4 : 3; g_rs64_skyz_m = s_skyz_om1; return s_skyz_om1 == 0x00552224u; }
                    if (o2 == 0x2E) return true;  // replaced before any use
                    b += (o2 >= 0x08 && o2 <= 0x0F) ? 32 + ((o2 & 4) ? 64 : 0) + ((o2 & 2) ? 64 : 0) + ((o2 & 1) ? 16 : 0) : (o2 == 0x24 || o2 == 0x25) ? 16 : 8;
                }
                why = 5; g_rs64_skyz_m = s_skyz_om1; return !(s_skyz_om1 & 4u) || s_skyz_om1 == 0x00552224u;
            };
            // s6948 SEL2 (default on inside SEL; ROGUESQ_DD_SKYZ_SEL2=0 is the s6947 SEL, =tog 4 s period on SEL seconds; run b1: SEL misses 585 sky draws whose depth
            // is followed by mode 0F0A4004 (no z read) before the sky mode, SEL2 0, unrewritten 1.78% vs value 1.84% vs SEL 3.60%, leak 0/230): the consumer is the first DRAW that reads prim z, so mode words and draws
            // under modes that do not read prim z are walked past, with the mode tracked through the look-ahead. Range end: the mode then set decides, as in SEL.
            auto skyish2 = [&](uint32_t at) {
                uint32_t m0 = s_skyz_om0, m1 = s_skyz_om1;
                for (uint32_t b = at + 8; b + 8 <= hi;) {
                    const uint32_t o2 = (rd(b) >> 24) & 0x3F;
                    if (o2 == 0x2F) { m0 = rd(b); m1 = rd(b + 4); }
                    else if ((o2 >= 0x08 && o2 <= 0x0F) || o2 == 0x24 || o2 == 0x25 || o2 == 0x36) { if (pz(m0, m1)) { why = 4; g_rs64_skyz_m = m1; return m1 == 0x00552224u; } }
                    else if (o2 == 0x2E) return true;
                    b += (o2 >= 0x08 && o2 <= 0x0F) ? 32 + ((o2 & 4) ? 64 : 0) + ((o2 & 2) ? 64 : 0) + ((o2 & 1) ? 16 : 0) : (o2 == 0x24 || o2 == 0x25) ? 16 : 8;
                }
                why = 5; g_rs64_skyz_m = m1; return !(m1 & 4u) || m1 == 0x00552224u;
            };
            static const int skyz_sel2 = [] { const char *e = std::getenv("ROGUESQ_DD_SKYZ_SEL2"); return !(e && *e) ? 1 : *e == '0' ? 0 : *e == 't' ? 2 : 1; }();  // s6948: default 1 (=0 SEL)
            const bool sel2_now = sel_now && (skyz_sel2 == 1 || (skyz_sel2 == 2 && ((mach_absolute_time() / 96000000ull) & 1)));
            if (op == 0x2F) { s_skyz_om0 = w0; s_skyz_om1 = w1; }
            if (op == 0x2E) {
                skyz_pd = a; s_skyz_pd = w1 >> 16; s_skyz_done = false; s_skyz_why = live ? 7 : 6;
                if (live) for (uint32_t v : s_skyz_ring) if (v && v == s_skyz_pd) {
                    why = 0; if (!sel_now || (sel2_now ? skyish2(a) : skyish(a))) { put(a); why = 0; }
                    s_skyz_why = why; s_skyz_done = true; break;
                }
            } else if (op == 0x2F && w1 == 0x00552224u && !s_skyz_done) {
                s_skyz_done = true;
                bool known = false; for (uint32_t v : s_skyz_ring) known |= v == s_skyz_pd;
                if (!known) s_skyz_ring[s_skyz_w++ & 7] = s_skyz_pd;
                if (live) { if (skyz_pd != 0xFFFFFFFFu) { put(skyz_pd); s_skyz_why = 1; } else { s_skyz_miss++; s_skyz_why = 8; } }
            }
            g_rs64_skyz_why = s_skyz_why; g_rs64_skyz_sel2 = sel2_now;
        }
        // s6946 G5h: ROGUESQ_DD_SKYZ_AUD=<file> (needs DD_SKYZ live) asks whether a sky depth SKYZ rewrites is ever consumed by a mode other than the sky (H-leak).
        // At every draw (tri, texrect, fill rect) whose other modes take z from prim depth and compare or update z, it bins the depth then current: ring = one SKYZ
        // matches (rewritten on live seconds), other = any other depth. Per swap: sky_ring, oth_ring (the leak), sky_other, oth_other (control: 0xC8104A54 and kin draw
        // with prim z, so the instrument must see non-sky prim z draws), on the odd-second parity. Leaking blender words are kept. Diagnostic, off unless set.
        static FILE *s_za = [] { const char *e = std::getenv("ROGUESQ_DD_SKYZ_AUD"); return (e && *e) ? fopen(e, "w") : (FILE *)nullptr; }();
        if (s_za && skyz) {
            static uint32_t z_om0 = 0, z_om1 = 0, z_pdk = 0, z_sw = 0xFFFFFFFFu, z_c[6] = {}, z_leak[16] = {}, z_nl = 0; static bool z_rw = false;
            // s6948: z_y[k] = sky draws under a ring depth that were NOT rewritten, by g_rs64_skyz_why k (0..8); z_o = non-sky draws under a ring depth that were.
            // First 16 (bin, mode then, swap) of bins 2-5 logged as "# why". Columns 11-12: SEL2 state, then z_y[0..8], then z_o.
            static uint32_t z_y[9] = {}, z_o = 0, z_nw = 0;
            if (z_sw != (uint32_t)sw) {
                if (z_c[0] | z_c[1] | z_c[2] | z_c[3]) {
                    fprintf(s_za, "%u %llu %u %u %u %u %u %u %u %u %u", z_sw, (unsigned long long)mach_absolute_time(), (unsigned)((mach_absolute_time() / 24000000ull) & 1), z_c[0], z_c[1], z_c[2], z_c[3], z_c[4], z_c[5], (unsigned)sel_now, (unsigned)g_rs64_skyz_sel2);
                    for (uint32_t y : z_y) fprintf(s_za, " %u", y);
                    fprintf(s_za, " %u\n", z_o);
                }
                fflush(s_za); z_sw = (uint32_t)sw; for (auto &c : z_c) c = 0; for (auto &y : z_y) y = 0; z_o = 0;
            }
            if (op == 0x2E) { z_pdk = 2; for (uint32_t v : s_skyz_ring) if (v && v == (w1 >> 16)) { z_pdk = 1; break; } }
            // s6947 fix: the s6946 b4 build put the mode update in an else branch, so a mode word after a depth in the same range was never recorded (sky_ring 0).
            if (op == 0x2F) { z_om0 = w0; z_om1 = w1; }
            if ((op == 0x2E || op == 0x2F) && skyz_pd != 0xFFFFFFFFu) z_rw = (rd(skyz_pd + 4) >> 16) == 0x7FFFu && z_pdk == 1;
            else if (((op >= 0x08 && op <= 0x0F) || op == 0x24 || op == 0x25 || op == 0x36) && z_pdk && (z_om1 & 4u) && (z_om1 & 0x30u) && ((z_om0 >> 20) & 3u) < 2u) {
                const bool sky = z_om1 == 0x00552224u; z_c[(sky ? 0 : 1) + (z_pdk == 1 ? 0 : 2)]++; if (z_rw) z_c[sky ? 4 : 5]++;
                if (sky && z_pdk == 1 && !z_rw) {
                    const int k = g_rs64_skyz_why < 0 || g_rs64_skyz_why > 8 ? 8 : g_rs64_skyz_why; z_y[k]++;
                    if (k >= 2 && k <= 5 && z_nw < 16) { z_nw++; fprintf(s_za, "# why %d decided_by %08X at_draw %08X %08X sel2=%d swap=%d\n", k, g_rs64_skyz_m, z_om0, z_om1, (int)g_rs64_skyz_sel2, sw); }
                }
                if (!sky && z_pdk == 1 && z_rw) z_o++;
                if (!sky && z_pdk == 1) { bool k = false; for (uint32_t i = 0; i < z_nl; i++) k |= z_leak[i] == z_om1; if (!k && z_nl < 16) { z_leak[z_nl++] = z_om1; fprintf(s_za, "# leak om %08X %08X swap=%d\n", z_om0, z_om1, sw); } }
            }
        }
        if (op == 0x24 || op == 0x25) return 16;
        if (op == 0x3F) { s_cw = (w0 & 0x3FFu) + 1u; return 8; }
        if (op == 0x3D) s_timg = w1;
        if (op == 0x3C) { s_bc0 = w0; s_bc1 = w1; }
        if (op < 0x08 || op > 0x0F) return 8;
        if (s_bd) { s_bA += s_bc0 == 0xFC127E24u && s_bc1 == 0xFFFFFFFFu; s_bB += s_bc0 == 0xFC127FFFu && s_bc1 == 0xFFFFFE3Fu; }
        const uint32_t len = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
        if (a + 32 > hi) return 0;
        uint8_t s7107_tg = 0xFF;  // s7107: source-cell tag popped in forwarding order, stored in the G5B_TRIS pad byte
        if (__builtin_expect(rs64_s7106_on, 0)) { rs64_s7106_btri(); s7107_tg = rs64_s7107_pop(); }  // s7106: independent per-swap tri count (control for the ucode DMEM parse)
        // s7636 item 25: ROGUESQ_S7636_FASTSPIKE integer guard test, exact equivalent of the double test below (x words are s15.16,
        // y words s11.2, so every double vertex coordinate is X / 2^18 with X an int64 below 2^48: both paths compare the same reals).
        // Used only when no spike diagnostic is armed. A good tri returns here; a bad one falls through to the double path (cull, logs).
        // Default 0 (s7636: saves only ~0.2-0.75 ms/s, A/A noise level; H-mem). =1 on, =0 off, =tog on even GLUE_TOG seconds (needs ROGUESQ_GLUE_TOG=3), =chk both paths and count disagreements of bad, with
        // the integer verdict flipped on every 4096th tri as the comparator's positive control (inj must equal inj_seen, live must be 0).
        static const int fast = [] { const char *e = std::getenv("ROGUESQ_S7636_FASTSPIKE"); return !(e && *e) ? 0 : *e == '0' ? 0 : *e == 't' ? 2 : *e == 'c' ? 3 : 1; }();
        static const int64_t G4 = (int64_t)llround(guard * 4.0);  // guard in quarter px
        static const bool gint = (double)G4 == guard * 4.0;      // fast path needs a quarter-px guard (default 640)
        static uint64_t s_fchk = 0, s_finj = 0, s_finj_seen = 0, s_flive = 0;
        int fbad = -1;
        if (fast && gint && !(on || s_tf || s_sh || s_big || s_fg || killsheet || rs64_s7536_cnt_on) && (fast != 2 || !g_s7636_odd)) {
            const int32_t yl4 = ((int32_t)(w0 << 18)) >> 18, ym4 = ((int32_t)(w1 << 2)) >> 18, yh4 = ((int32_t)(w1 << 18)) >> 18;
            const int64_t xl = (int32_t)rd(a + 8), dl = (int32_t)rd(a + 12), xh = (int32_t)rd(a + 16), dh = (int32_t)rd(a + 20),
                          xm = (int32_t)rd(a + 24), dm = (int32_t)rd(a + 28);
            const int64_t X0 = xh * 4, X1 = xm * 4 + dm * (ym4 - yh4), X2 = xl * 4, X3 = xl * 4 + dl * (yl4 - ym4), X4 = xh * 4 + dh * (yl4 - yh4);
            const int64_t XL = -G4 * 65536, XR = ((320 + (s_cw > 640u ? (int64_t)s_cw - 320 : 0)) * 4 + G4) * 65536;
            const int64_t mn = std::min(std::min(std::min(X0, X1), std::min(X2, X3)), X4), mx = std::max(std::max(std::max(X0, X1), std::max(X2, X3)), X4);
            fbad = !(yh4 <= ym4 && ym4 <= yl4) || mn < XL || mx > XR || yh4 < -G4 || yl4 < -G4 || ym4 < -G4 || yh4 > 960 + G4 || ym4 > 960 + G4 || yl4 > 960 + G4;
            if (fast == 3) { if ((++s_fchk & 4095u) == 0) { s_finj++; fbad ^= 1; } }
            else if (!fbad) { s_tris++; s_swap_tris++; return len; }
        }
        const double yl = sx14(w0 & 0x3FFF), ym = sx14((w1 >> 16) & 0x3FFF), yh = sx14(w1 & 0x3FFF);
        auto fx = [&](uint32_t o) { return (double)(int32_t)rd(a + o) / 65536.0; };
        const double xl = fx(8), dl = fx(12), xh = fx(16), dh = fx(20), xm = fx(24), dm = fx(28);
        const double v[5][2] = {{xh, yh}, {xm + dm * (ym - yh), ym}, {xl, ym}, {xl + dl * (yl - ym), yl}, {xh + dh * (yl - yh), yl}};
        bool bad = !(yh <= ym && ym <= yl);
        if (s_tf) {
            struct { uint8_t op, pad; uint16_t cw; uint32_t timg, z; int16_t c[10]; } r = {(uint8_t)op, s7107_tg, (uint16_t)s_cw, s_timg, (op & 1) && a + len <= hi ? rd(a + len - 16) : 0u, {}};
            for (int i = 0; i < 5; i++) for (int k = 0; k < 2; k++) r.c[i * 2 + k] = (int16_t)std::max(-32768.0, std::min(32767.0, v[i][k] * 4.0));
            fwrite(&r, sizeof r, 1, s_tf);
        }
        // s6920: ROGUESQ_G5E_FOG_EVERY=<n> sample period (default 120). Extra columns: odd second of the mach clock (the 1 s =tog arms), cutoff the chain read (g_rs64_s6919[1], needs ROGUESQ_G5H_BAND).
        static const int fg_every = [] { const char *e = std::getenv("ROGUESQ_G5E_FOG_EVERY"); return e && atoi(e) > 0 ? atoi(e) : 120; }();
        if (s_fg && (op & 5) == 5 && (sw % fg_every) == 0 && a + len <= hi) {
            extern uint32_t g_rs64_s6919[12]; const uint64_t mt = mach_absolute_time();
            fprintf(s_fg, "%d %08X %08X %08X %d %d %08X %d %d %08X\n", sw, s_st[0x2F][1], s_st[0x38][1], rd(a + len - 16), (int)(int16_t)rd(a + 36), (int)(int16_t)rd(a + 32 + 40 + 4), rd(a + len - 4), (int)((mt / 96000000ull) & 1), (int)((mt / 24000000ull) & 1), g_rs64_s6919[1]);
        }
        if (s_sh) {
            double ar = 0; for (int i = 0; i < 5; i++) { const int j = (i + 1) % 5; ar += v[i][0] * v[j][1] - v[j][0] * v[i][1]; }
            if (fabs(ar) / 2 > 40000.0 && a + len <= hi) {
                uint32_t h = 2166136261u; for (uint32_t o = 0; o < 2048; o += 4) { h = (h ^ rd((s_timg + o) & 0x00FFFFFCu)) * 16777619u; }
                fprintf(s_sh, "%d %llu op=%02X area=%.0f h=%08X", sw, (unsigned long long)mach_absolute_time(), op, fabs(ar) / 2, h);
                static const uint8_t ids[] = {0x2D, 0x2F, 0x32, 0x33, 0x34, 0x35, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F};
                for (uint8_t q : ids) fprintf(s_sh, " %02X:%08X,%08X", q, s_st[q][0], s_st[q][1]);
                fputs(" T", s_sh); for (uint32_t o = 0; o < len; o += 4) fprintf(s_sh, " %08X", rd(a + o));
                fputc('\n', s_sh); fflush(s_sh);
            }
        }
        if (killsheet && op == 0x0F && s_st[0x2F][1] == 0xC8112220u && a + len <= hi && rd(a + len - 16) < 0x00200000u
            && (killsheet == 1 || ((mach_absolute_time() / 24000000ull) & 1))) {
            double ar = 0; for (int i = 0; i < 5; i++) { const int j = (i + 1) % 5; ar += v[i][0] * v[j][1] - v[j][0] * v[i][1]; }
            if (fabs(ar) / 2 > 100000.0) { uint32_t n0 = w0 & ~0x3FFFu, n1 = 0; memcpy(g_rdram_for_submit + (a & kSubmitRamMask), &n0, 4); memcpy(g_rdram_for_submit + ((a + 4) & kSubmitRamMask), &n1, 4); }
        }
        if (s_big) {
            double ar = 0; for (int i = 0; i < 5; i++) { const int j = (i + 1) % 5; ar += v[i][0] * v[j][1] - v[j][0] * v[i][1]; }
            ar = fabs(ar) / 2; s_bt.n++; if (ar > 5000.0) s_bt.big++;
            if (ar > s_bt.area) { s_bt.area = ar; memcpy(s_bt.v, v, sizeof v); s_bt.off = a; s_bt.op = op; s_bt.cw = s_cw; s_bt.w0 = w0; s_bt.w1 = w1; }
        }
        // s6695: the right bound assumed a 320-wide viewport, so at 21:9 (colour image 1024 wide) every
        // ordinary triangle reaching x>960 was zeroed (level-select right-edge wall hole). Images wider
        // than 640 (widescreen only) get the guard measured from their own right edge; <=640 is unchanged.
        const double xr = 320.0 + guard + (s_cw > 640u ? (double)s_cw - 320.0 : 0.0);
        for (auto &p : v) if (p[0] < -guard || p[0] > xr || p[1] < -guard || p[1] > 240.0 + guard) bad = true;
        if (fast == 3 && fbad >= 0) {  // s7636 chk: integer vs double verdict
            const bool inj = (s_fchk & 4095u) == 0;
            if ((bool)fbad != bad) { if (inj) s_finj_seen++; else if (s_flive++ < 16) fprintf(stderr, "[s7636-live] w0=%08X w1=%08X cw=%u int=%d dbl=%d\n", w0, w1, s_cw, fbad, (int)bad); }
            if ((s_fchk & 0xFFFFFu) == 0) fprintf(stderr, "[s7636-chk] tris=%llu inj=%llu inj_seen=%llu live=%llu\n", (unsigned long long)s_fchk,
                (unsigned long long)s_finj, (unsigned long long)s_finj_seen, (unsigned long long)s_flive);
        }
        s_tris++; s_swap_tris++;
        bool s7536_cul = false;
        // s6792: 4:3 hi-res images (321..640 wide: cinematics, AT THE MOVIES) are never culled. Their legit cloud/sky
        // tris overrun even a width-scaled bound (retail dump: 26869 tris past the 320 bound, 4424 past a 640x480 one),
        // and zeroing them left a black notch at the right edge. The wedges (s6083) were 320-wide flight frames.
        if (bad && cull && (s_cw <= 320u || s_cw > 640u) && (!cull_tog || rs64_tog_odd(mach_absolute_time()))) {
            // s6084: zero the triangle height (yl=ym=yh=0) so the rasteriser emits no scanlines; length is unchanged.
            uint32_t n0 = w0 & ~0x3FFFu, n1 = 0; memcpy(g_rdram_for_submit + (a & kSubmitRamMask), &n0, 4); memcpy(g_rdram_for_submit + ((a + 4) & kSubmitRamMask), &n1, 4);
            s_culled++; s7536_cul = true;
        }
        {  // s7536: per sp_complete-state spike/big-hull counts (s7535_ga_chk.cpp)
          if (rs64_s7536_cnt_on) { double ar = 0; for (int i = 0; i < 5; i++) { const int j = (i + 1) % 5; ar += v[i][0] * v[j][1] - v[j][0] * v[i][1]; }
            (void)rs64_s7536_tri(bad ? 1 : 0, s7536_cul ? 1 : 0, fabs(ar) / 2 > 100000.0 ? 1 : 0); } }
        if (bad && on) {
            s_bad++; s_swap_bad++;
            if (s_logged++ < 600) {
                fprintf(stderr, "[spike] swap=%d off=%06X op=%02X Y(h,m,l)=%.2f,%.2f,%.2f V=(%.1f,%.1f)(%.1f,%.1f)(%.1f,%.1f)(%.1f,%.1f)(%.1f,%.1f) range=%06X..%06X\n",
                        sw, a, op, yh, ym, yl, v[0][0], v[0][1], v[1][0], v[1][1], v[2][0], v[2][1], v[3][0], v[3][1], v[4][0], v[4][1], lo, hi);
                fflush(stderr);
            }
            // s6367: DMEM search for the pinned (stale?) vertex. Encodings: s15.2 16-bit (y*4) and s15.16 32-bit (y*65536), BE.
            static const bool dsr = [] { const char *e = std::getenv("ROGUESQ_SPIKE_DMEM"); return e && *e && *e != '0'; }();
            static uint32_t s_dlog = 0;
            if (dsr && g_dmem_cur != nullptr && s_dlog < 120) {
                s_dlog++;
                auto b = [&](uint32_t o) { return (uint32_t)g_dmem_cur[(o & 0xFFFu) ^ 3u]; };
                auto find16 = [&](int16_t val, char *out, size_t n) {
                    size_t k = 0; int cnt = 0;
                    for (uint32_t o = 0; o < 0x1000; o += 2) if ((int16_t)((b(o) << 8) | b(o + 1)) == val) { cnt++; if (k + 6 < n) k += snprintf(out + k, n - k, "%03X ", o); }
                    return cnt; };
                auto find32 = [&](int32_t val, char *out, size_t n) {
                    size_t k = 0; int cnt = 0;
                    for (uint32_t o = 0; o < 0x1000; o += 4) if ((int32_t)((b(o) << 24) | (b(o + 1) << 16) | (b(o + 2) << 8) | b(o + 3)) == val) { cnt++; if (k + 6 < n) k += snprintf(out + k, n - k, "%03X ", o); }
                    return cnt; };
                const double ys[3] = {ym, v[0][1], v[0][0]};  // pinned y, apex y, apex x
                const char *nm[3] = {"pinY", "apexY", "apexX"};
                fprintf(stderr, "[spike-dmem] swap=%d off=%06X task=%u", sw, a, g_e9prov.task);
                for (int i = 0; i < 3; ++i) {
                    char h16[96] = "", h32[96] = "";
                    int c16 = find16((int16_t)lrint(ys[i] * 4.0), h16, sizeof h16);
                    int c32 = find32((int32_t)lrint(ys[i] * 65536.0), h32, sizeof h32);
                    fprintf(stderr, " %s=%.2f s15.2:%d[%s] s15.16:%d[%s]", nm[i], ys[i], c16, h16, c32, h32);
                }
                fputc('\n', stderr);
                // s6369: DMA-read windows (RDRAM->DMEM) since the previous spike row that cover DMEM 0x43A/0x462.
                static uint32_t s_ring_prev = 0;
                const uint32_t rn = rs64_spk_dma_n;
                uint32_t from = (rn - s_ring_prev > 256u) ? rn - 256u : s_ring_prev, ncov = 0, nall = rn - from;
                fprintf(stderr, "[spike-dma] task=%u events_since_prev=%u:", g_e9prov.task, rn - s_ring_prev);
                for (uint32_t i = from; i != rn; ++i) {
                    const uint32_t *r = rs64_spk_dma_ring[i & 255u];
                    const bool c43a = (0x43Au >= r[2] && 0x43Au < r[2] + r[1]);
                    const bool c462 = (0x462u >= r[2] && 0x462u < r[2] + r[1]);
                    if (c43a || c462) { ncov++; fprintf(stderr, " [dram=%06X dmem=%03X len=%X%s%s]", r[0], r[2], r[1], c43a ? " c43A" : "", c462 ? " c462" : ""); }
                }
                fprintf(stderr, " covering=%u/%u cum_cov43A=%u cum_cov462=%u cum_ctl500=%u cum_events=%u\n", ncov, nall, rs64_spk_cov43a, rs64_spk_cov462, rs64_spk_ctl, rn);
                s_ring_prev = rn;
                fflush(stderr);
            }
        }
        return len;
    };
    for (uint32_t a = lo & ~3u; a + 8 <= hi;) {
        const uint32_t n = body(a), m = rb ? rb(rc, a) : n;
        if (!n || !m) break;
        a += n;
    }
}

// s6612: phase is not a level-select key (21:9 is phase 4, 16:9 is phase 5).
// Gate on the VI framebuffer that the torn dumps actually are: 796x336 or
// 1024x336. Notes come from RT64's decoded triangles and texrects. A byte
// walker of the DPC range never locked onto a command (0 sane of thousands).
extern "C" void rs64_vi_fb_wh(uint32_t *out_w, uint32_t *out_h);

// The bbox rs64_floor_note stores is not coverage: a triangle does not
// fill its box. These spans use the same edge walk as the x=0 test
// (XH at floor(YH), XL at YM). Only op 0x0F tile 0 line 4, scanlines
// 180..250, outer thirds. A second accumulator is never cleared on a
// VI-origin change, so a per-frame split cannot hide a hole.
struct Rs64CovAcc {
    uint32_t bits[71][32];
    uint32_t tris = 0, x0 = 0, reject = 0;
};
static Rs64CovAcc s_cov_frame, s_cov_union;
static uint32_t s_cov_w = 0, s_cov_origin = 0xFFFFFFFFu, s_cov_frames = 0;
static int s_cov_origin_set = 0;
static float s_scx0 = 0, s_scy0 = 0, s_scx1 = 0, s_scy1 = 0;

static int rs64_cov_bit(const Rs64CovAcc &a, int row, int x) {
    return (a.bits[row][x >> 5] >> (x & 31)) & 1;
}

static void rs64_floor_cover_emit(const char *why, const Rs64CovAcc &a) {
    if (!s_cov_w || !a.tris) return;
    const int w = (int)s_cov_w;
    const int L = w / 3;
    const int R = (2 * w) / 3;
    const int segs[2][2] = {{0, L}, {R, w}};
    int covered = 0, total = 0, hole_rows = 0, rect_gap_rows = 0;
    int hull_px = 0, hull_cov = 0, rows_hull = 0;
    int max_hole = 0, max_gap = 0, left_holes = 0, right_holes = 0;
    for (int row = 0; row < 71; row++) {
        int row_hole = 0, row_gap = 0;
        for (int s = 0; s < 2; s++) {
            const int a0 = segs[s][0], b0 = segs[s][1];
            if (b0 <= a0) continue;
            total += b0 - a0;
            int first = -1, last = -1, cov = 0, run = 0, gap = 0;
            for (int x = a0; x < b0; x++) {
                if (rs64_cov_bit(a, row, x)) {
                    if (first < 0) first = x;
                    last = x;
                    cov++;
                    if (run > max_gap) max_gap = run;
                    if (run > 2) gap = 1;
                    run = 0;
                } else {
                    run++;
                }
            }
            if (run > max_gap) max_gap = run;
            if (run > 2) gap = 1;
            covered += cov;
            if (gap) row_gap = 1;
            if (first >= 0 && last >= first) {
                rows_hull++;
                hull_px += last - first + 1;
                int hrun = 0, hole = 0, hcov = 0;
                for (int x = first; x <= last; x++) {
                    if (rs64_cov_bit(a, row, x)) {
                        hcov++;
                        if (hrun > max_hole) max_hole = hrun;
                        if (hrun > 2) hole = 1;
                        hrun = 0;
                    } else {
                        hrun++;
                    }
                }
                hull_cov += hcov;
                if (hole) {
                    row_hole = 1;
                    if (s == 0) left_holes++; else right_holes++;
                }
            }
        }
        if (row_hole) hole_rows++;
        if (row_gap) rect_gap_rows++;
    }
    const double rect_frac = total ? (double)covered / (double)total : 0;
    const double hull_frac = hull_px ? (double)hull_cov / (double)hull_px : 0;
    const double mean_hull = rows_hull ? (double)hull_px / (double)rows_hull : 0;
    fprintf(stderr,
            "[floor-cov] why=%s w=%u tris=%u frames_closed=%u x0spans=%u reject=%u "
            "rect_frac=%.4f rect_gap_rows=%d max_gap=%d "
            "hull_frac=%.4f hole_rows=%d left_holes=%d right_holes=%d max_hole=%d "
            "hull_rows=%d mean_hull=%.1f scissor=%.1f,%.1f,%.1f,%.1f\n",
            why, s_cov_w, a.tris, s_cov_frames, a.x0, a.reject,
            rect_frac, rect_gap_rows, max_gap,
            hull_frac, hole_rows, left_holes, right_holes, max_hole,
            rows_hull, mean_hull, s_scx0, s_scy0, s_scx1, s_scy1);
    fflush(stderr);
}

static void rs64_cov_clear(Rs64CovAcc &a) {
    memset(a.bits, 0, sizeof(a.bits));
    a.tris = a.x0 = a.reject = 0;
}

extern "C" void rs64_floor_cover(
    uint32_t op, uint32_t tile, uint32_t line,
    float y_floor, float ym,
    float xh, float dxhdy, float xm, float dxmdy, float xl, float dxldy,
    float yh, float yl,
    float scx0, float scy0, float scx1, float scy1) {
    static const bool on = [] {
        const char *e = std::getenv("ROGUESQ_LOG_FLOOR");
        return e && *e && *e != '0';
    }();
    if (!on || op != 0x0Fu || tile != 0u || line != 4u) return;
    uint32_t vw = 0, vh = 0;
    rs64_vi_fb_wh(&vw, &vh);
    const bool gate = (vh >= 320 && vh <= 352) && (vw == 796 || vw == 1024);
    if (!gate) return;
    if (s_cov_w && s_cov_w != vw) {
        rs64_floor_cover_emit("width-frame", s_cov_frame);
        rs64_floor_cover_emit("width-union", s_cov_union);
        rs64_cov_clear(s_cov_frame);
        rs64_cov_clear(s_cov_union);
        s_cov_frames = 0;
        s_cov_origin_set = 0;
    }
    s_cov_w = vw;
    const uint32_t origin = rs64_vi_committed_origin();
    if (!s_cov_origin_set) {
        s_cov_origin = origin;
        s_cov_origin_set = 1;
    } else if (origin != s_cov_origin) {
        if (s_cov_frame.tris) {
            rs64_floor_cover_emit("frame", s_cov_frame);
            s_cov_frames++;
            if (s_cov_frames == 1 || s_cov_frames == 2 || (s_cov_frames % 30u) == 0u)
                rs64_floor_cover_emit("union", s_cov_union);
        }
        rs64_cov_clear(s_cov_frame);
        s_cov_origin = origin;
    }
    if (!std::isfinite(y_floor) || !std::isfinite(ym) || !std::isfinite(xh) || !std::isfinite(dxhdy) ||
        !std::isfinite(xm) || !std::isfinite(dxmdy) || !std::isfinite(xl) || !std::isfinite(dxldy) ||
        !std::isfinite(yh) || !std::isfinite(yl)) {
        s_cov_frame.reject++;
        s_cov_union.reject++;
        return;
    }
    s_scx0 = scx0; s_scy0 = scy0; s_scx1 = scx1; s_scy1 = scy1;
    float y_lo = yh < yl ? yh : yl;
    float y_hi = yh > yl ? yh : yl;
    if (scy1 > scy0) {
        if (scy0 > y_lo) y_lo = scy0;
        if (scy1 < y_hi) y_hi = scy1;
    }
    const float x_lo_sc = (scx1 > scx0) ? scx0 : -1.0e9f;
    const float x_hi_sc = (scx1 > scx0) ? scx1 : 1.0e9f;
    const int w = (int)vw;
    const int L = w / 3;
    const int R = (2 * w) / 3;
    int painted = 0, hit_x0 = 0, insane = 0;
    for (int s = 180; s <= 250; s++) {
        const float y = (float)s + 0.5f;
        if (y < y_lo || y > y_hi) continue;
        const float dy = y - y_floor;
        const float x_major = xh + dxhdy * dy;
        const float x_other = (y <= ym) ? (xm + dxmdy * dy) : (xl + dxldy * (y - ym));
        if (!std::isfinite(x_major) || !std::isfinite(x_other)) { insane = 1; continue; }
        float xa = x_major < x_other ? x_major : x_other;
        float xb = x_major > x_other ? x_major : x_other;
        if (xa < x_lo_sc) xa = x_lo_sc;
        if (xb > x_hi_sc) xb = x_hi_sc;
        if (!(xb > xa) || xb - xa > 8000.f) { if (xb - xa > 8000.f) insane = 1; continue; }
        if (xa <= 0.f && xb >= 0.f) hit_x0 = 1;
        int xa_i = (int)std::floor(xa);
        int xb_i = (int)std::ceil(xb);
        if (xa_i < 0) xa_i = 0;
        if (xb_i > w) xb_i = w;
        auto paint = [&](Rs64CovAcc &acc, int lo, int hi) {
            const int row = s - 180;
            for (int x = lo; x < hi; x++) acc.bits[row][x >> 5] |= 1u << (x & 31);
        };
        int nlo = 0, nhi = 0;
        if (xa_i < L && xb_i > 0) {
            nlo = xa_i > 0 ? xa_i : 0;
            nhi = xb_i < L ? xb_i : L;
            if (nhi > nlo) { paint(s_cov_frame, nlo, nhi); paint(s_cov_union, nlo, nhi); painted += nhi - nlo; }
        }
        if (xa_i < w && xb_i > R) {
            nlo = xa_i > R ? xa_i : R;
            nhi = xb_i < w ? xb_i : w;
            if (nhi > nlo) { paint(s_cov_frame, nlo, nhi); paint(s_cov_union, nlo, nhi); painted += nhi - nlo; }
        }
    }
    if (insane) { s_cov_frame.reject++; s_cov_union.reject++; }
    if (!painted) return;
    s_cov_frame.tris++;
    s_cov_union.tris++;
    if (hit_x0) { s_cov_frame.x0++; s_cov_union.x0++; }
    const uint32_t n = s_cov_frame.tris;
    if (s_cov_frames == 0 && (n == 40u || n == 120u || n == 240u)) {
        rs64_floor_cover_emit("open", s_cov_frame);
        rs64_floor_cover_emit("union", s_cov_union);
    }
}

// Perspective-correct T and S at the outer-third sample, plus shade luma,
// the I4 texel the RDP would fetch, and whether an untextured triangle or
// a rectangle covers the same point. Each plane is base + De*(y-yFloor) +
// Dx*(x - XH). Texels are (T/W)*1024 and (S/W)*1024. Luma is
// 0.2126 R + 0.7152 G + 0.0722 B. Texel, shade and I4 stay on the last
// floor triangle. `last` is the class of whichever primitive covered the
// sample latest in command order: 1 floor tri, 2 any other tri, 3 rect
// or fill. rect_n / utri_n count touches even after a later primitive wins.
//
// The I4 address matches TextureDecoder.hlsli implLoadTMEM: odd rows swap
// 32-bit words inside the 8-byte group. Factor 5's I4 is pre-interleaved
// for that unswap, so skipping it reads the neighbouring word and a flat
// intensity would refute the row step for a decoder bug.
namespace {
int rs64_imod(int x, int y) {
    if (y == 0) return x;
    return x - y * (int)std::floor((float)x / (float)y);
}

const float kRs64Shift[16] = {
    1.0f, 0.5f, 0.25f, 0.125f, 1.0f / 16.0f, 1.0f / 32.0f, 1.0f / 64.0f, 1.0f / 128.0f,
    1.0f / 256.0f, 1.0f / 512.0f, 1.0f / 1024.0f, 32.0f, 16.0f, 8.0f, 4.0f, 2.0f
};

int rs64_i4_wrap(int v, uint32_t logmask, uint32_t cm, uint32_t ul, uint32_t lr) {
    uint32_t mode = cm;
    if (logmask == 0) mode |= 2u;
    if (mode & 2u) {
        const double hi_d = std::round((double)lr) / 4.0 - std::round((double)ul) / 4.0;
        int hi = (int)hi_d;
        if (v < 0) return 0;
        if (v > hi) return hi;
        return v;
    }
    const int masks = (logmask > 0 && logmask < 16) ? (1 << logmask) : 0;
    if ((mode & 1u) && masks > 0 && rs64_imod(v, masks * 2) >= masks)
        return (masks - 1) - rs64_imod(v, masks);
    return rs64_imod(v, masks);
}

float rs64_i4_texel(const uint8_t *T, int tx, int ty, int stride, int base, int mask, unsigned tlut, unsigned palette) {
    if (!T || stride <= 0) return 0.f;
    const int oddRow = ty & 1;
    const int oddCol = tx & 1;
    const int rel = ty * stride + (tx >> 1);
    const int rowStart = (rel / stride) * stride;
    const int wordIndex = (rel - rowStart) / 4;
    int finalAddr = oddRow
        ? base + rowStart + ((wordIndex ^ 1) * 4) + (rel & 3)
        : base + rel;
    if (finalAddr < 0) finalAddr = 0;
    const uint8_t byte = T[finalAddr & mask];
    const unsigned nibble = oddCol ? (byte & 0xFu) : (byte >> 4);
    if (tlut == 0u) return (float)((nibble << 4) | nibble);
    const int addr = 0x800 + (int)(palette << 7) + (int)(nibble << 3);
    const unsigned pix = (unsigned)T[(addr + 1) & 0xFFF] | ((unsigned)T[addr & 0xFFF] << 8);
    if (tlut == 2u) {
        const unsigned r = (pix >> 11) & 0x1Fu;
        const unsigned g = (pix >> 6) & 0x1Fu;
        const unsigned b = (pix >> 1) & 0x1Fu;
        const float rf = ((r << 3) | (r >> 2)) / 255.0f;
        const float gf = ((g << 3) | (g >> 2)) / 255.0f;
        const float bf = ((b << 3) | (b >> 2)) / 255.0f;
        return (0.2126f * rf + 0.7152f * gf + 0.0722f * bf) * 255.0f;
    }
    if (tlut == 3u) return (float)((pix >> 8) & 0xFFu);
    return 0.f;
}

float rs64_i4_fetch(const uint8_t *T, float texel_s, float texel_t,
    uint32_t line, uint32_t tmem, uint32_t masks, uint32_t maskt,
    uint32_t cms, uint32_t cmt, uint32_t shifts, uint32_t shiftt,
    uint32_t uls, uint32_t ult, uint32_t lrs, uint32_t lrt,
    uint32_t palette, uint32_t om_h) {
    const float u = texel_s * kRs64Shift[shifts & 15] - (float)uls / 4.0f;
    const float v = texel_t * kRs64Shift[shiftt & 15] - (float)ult / 4.0f;
    const int stride = (int)line << 3;
    const int base = (int)tmem << 3;
    const unsigned tlut = (om_h >> 14) & 3u;
    const unsigned filt = (om_h >> 12) & 3u;
    const unsigned cyc = (om_h >> 20) & 3u;
    const int mask = tlut != 0u ? 0x7FF : 0xFFF;
    auto at = [&](int x, int y) {
        return rs64_i4_texel(T, rs64_i4_wrap(x, masks, cms, uls, lrs), rs64_i4_wrap(y, maskt, cmt, ult, lrt),
            stride, base, mask, tlut, palette);
    };
    const int x0 = (int)std::floor(u);
    const int y0 = (int)std::floor(v);
    const float s00 = at(x0, y0);
    if (filt == 0u || cyc == 2u) return s00;
    const float fx = u - (float)x0;
    const float fy = v - (float)y0;
    const float s10 = at(x0 + 1, y0);
    const float s01 = at(x0, y0 + 1);
    const float s11 = at(x0 + 1, y0 + 1);
    if (filt == 3u && std::fabs(fx - 0.5f) <= (1.0f / 128.0f) && std::fabs(fy - 0.5f) <= (1.0f / 128.0f))
        return (s00 + s01 + s10 + s11) * 0.25f;
    const float tri0 = s00 + (s10 - s00) * fx + (s01 - s00) * fy;
    const float tri1 = s11 + (s01 - s11) * (1.0f - fx) + (s10 - s11) * (1.0f - fy);
    return (fx + fy >= 1.0f) ? tri1 : tri0;
}

void rs64_bl_eq(uint32_t om_l, uint32_t om_h, char *out, size_t n) {
    static const char *pm[] = { "CC", "MEM", "BL", "FOG" };
    static const char *a[] = { "CCA", "FOGA", "SHA", "0" };
    static const char *b[] = { "1mA", "MEMA", "1", "0" };
    const uint32_t blend = (om_l >> 16) & 0xFFFFu;
    const unsigned cyc = (om_h >> 20) & 3u;
    const int force = (om_l & 0x4000u) ? 1 : 0;
    char c0[48], c1[48];
    auto one = [&](int second, char *dst) {
        const unsigned P = second ? (blend >> 12) & 3u : (blend >> 14) & 3u;
        const unsigned M = second ? (blend >> 4) & 3u : (blend >> 6) & 3u;
        const unsigned A = second ? (blend >> 8) & 3u : (blend >> 10) & 3u;
        const unsigned B = second ? (blend & 3u) : (blend >> 2) & 3u;
        std::snprintf(dst, 48, "(%s*%s+%s*%s)", pm[P], a[A], pm[M], b[B]);
    };
    one(0, c0);
    one(1, c1);
    std::snprintf(out, n, "cyc%uf%d%s|%s", cyc, force, c0, c1);
}

void rs64_i4_selftest() {
    uint8_t T[4096] = {};
    T[0] = 0xA0;
    T[36] = 0x50;
    const float a = rs64_i4_fetch(T, 0.2f, 0.2f, 4, 0, 6, 6, 0, 0, 0, 0, 0, 0, 252, 252, 0, 0);
    const float b = rs64_i4_fetch(T, 1.2f, 0.2f, 4, 0, 6, 6, 0, 0, 0, 0, 0, 0, 252, 252, 0, 0);
    const float c = rs64_i4_fetch(T, 0.2f, 1.2f, 4, 0, 6, 6, 0, 0, 0, 0, 0, 0, 252, 252, 0, 0);
    const float d = rs64_i4_fetch(T, 64.2f, 0.2f, 4, 0, 6, 6, 0, 0, 0, 0, 0, 0, 252, 252, 0, 0);
    if (a == 170.f && b == 0.f && c == 85.f && d == 170.f)
        std::fprintf(stderr, "[floor-i4] selftest ok a=170 b=0 c=85 d=170\n");
    else
        std::fprintf(stderr, "[floor-i4] selftest FAIL a=%.1f b=%.1f c=%.1f d=%.1f\n", a, b, c, d);
    std::fflush(stderr);
}

bool rs64_ft_span(float y, float y_floor, float ym,
    float xh, float dxhdy, float xm, float dxmdy, float xl, float dxldy,
    float x_lo, float x_hi, float &xa, float &xb) {
    const float dy = y - y_floor;
    const float x_major = xh + dxhdy * dy;
    const float x_other = (y <= ym) ? (xm + dxmdy * dy) : (xl + dxldy * (y - ym));
    if (!std::isfinite(x_major) || !std::isfinite(x_other)) return false;
    xa = x_major < x_other ? x_major : x_other;
    xb = x_major > x_other ? x_major : x_other;
    if (xa < x_lo) xa = x_lo;
    if (xb > x_hi) xb = x_hi;
    if (!(xb > xa) || xb - xa > 8000.f) return false;
    return true;
}

// The torn rows sit in the outer 1/12 (x=16 and x=w-17). x=w/6 is quiet.
static void rs64_ft_xs(uint32_t w, float xs[2]) {
    xs[0] = 16.f;
    xs[1] = (float)w - 17.f;
}

// 16-bit color-image fill: the low half is one RGBA5551 pixel. A word
// change whose luma does not move (alpha bit, or the high half) still
// counts as a step of 1 so a flat color stays at 0.
static float rs64_fill_luma(uint32_t word) {
    const unsigned c = word & 0xFFFFu;
    const unsigned r = (c >> 11) & 31u;
    const unsigned g = (c >> 6) & 31u;
    const unsigned b = (c >> 1) & 31u;
    const float rf = (float)((r << 3) | (r >> 2));
    const float gf = (float)((g << 3) | (g >> 2));
    const float bf = (float)((b << 3) | (b >> 2));
    return 0.2126f * rf + 0.7152f * gf + 0.0722f * bf;
}

static float rs64_fill_delta(uint32_t a, uint32_t b) {
    if (a == b) return 0.f;
    float d = std::fabs(rs64_fill_luma(a) - rs64_fill_luma(b));
    if (d < 1.f) d = 1.f;
    return d;
}

struct Rs64FtPt {
    float texel, texel_s, luma, inten, alpha;
    uint32_t fill;
    uint16_t floor_n, other_n, untex_n;
    uint8_t ok, ok_s, ok_l, ok_i, ok_a, ok_f, cc_i, cca_i, bl_i, last, rect_n, utri_n;
};

struct Rs64Ft {
    Rs64FtPt pts[71][2];
    struct Key { uint32_t op, tile, line, hits; } keys[24];
    char cc_str[4][64];
    uint32_t cc_omv[4];
    char cca_str[4][64];
    char bl_str[4][80];
    char untex_bl[80];
    int nkeys, ncc, ncca, nbl, untex_bl_set;
    uint32_t spill;
    uint32_t cur_w, origin;
    int origin_set, was, raws, cc_print_set, selftest, tile_logged;
    char cc_printed[64];
    uint32_t om_printed;

    void clear() {
        std::memset(pts, 0, sizeof(pts));
        std::memset(keys, 0, sizeof(keys));
        nkeys = 0;
        ncc = 0;
        ncca = 0;
        nbl = 0;
        spill = 0;
        untex_bl_set = 0;
        untex_bl[0] = 0;
    }

    void add_key(uint32_t kop, uint32_t ktile, uint32_t kline) {
        for (int i = 0; i < nkeys; i++) {
            if (keys[i].op == kop && keys[i].tile == ktile && keys[i].line == kline) {
                keys[i].hits++;
                return;
            }
        }
        if (nkeys < 24) {
            keys[nkeys].op = kop;
            keys[nkeys].tile = ktile;
            keys[nkeys].line = kline;
            keys[nkeys].hits = 1;
            nkeys++;
            return;
        }
        int small = 0;
        for (int i = 1; i < nkeys; i++) if (keys[i].hits < keys[small].hits) small = i;
        if (keys[small].hits <= 1) {
            keys[small].op = kop;
            keys[small].tile = ktile;
            keys[small].line = kline;
            keys[small].hits = 1;
        } else {
            spill++;
        }
    }

    void emit(const char *why) {
        const int rows = 71, cols = 2;
        int covered = 0, other = 0, multi = 0, nok = 0, npair = 0, npl = 0, npr = 0, jump4 = 0, jump8 = 0;
        int have = 0, nS = 0, nL = 0, nI = 0, nUntex = 0, anyI = 0, iLo = 0, iHi = 0;
        int nF = 0, nO = 0, nR = 0, nZ = 0, nBoth = 0, nTouchR = 0, nTouchU = 0, nOver = 0;
        int colF[2] = {}, colO[2] = {}, colR[2] = {};
        int cc_count[4] = {}, cca_count[4] = {}, bl_count[4] = {};
        int nFs = 0, nFw = 0, nFp = 0, nAa = 0;
        uint32_t fill_words[16];
        double sum = 0, suml = 0, sumr = 0, maxd = 0, sumS = 0, sumL = 0, sumI = 0, sumF = 0, sumA = 0;
        double texlo = 1e300, texhi = -1e300;
        for (int c = 0; c < cols; c++) {
            for (int r = 0; r < rows; r++) {
                const Rs64FtPt &p = pts[r][c];
                if (p.last == 1) { nF++; colF[c]++; }
                else if (p.last == 2) { nO++; colO[c]++; }
                else if (p.last == 3) { nR++; colR[c]++; }
                else nZ++;
                if (p.rect_n) nTouchR++;
                if (p.utri_n) nTouchU++;
                if (p.rect_n && p.last != 3) nOver++;
                if (p.floor_n && (p.untex_n || p.other_n)) nBoth++;
                if (p.untex_n) { nUntex++; have = 1; }
                if (p.ok_f) {
                    nFs++;
                    int seen = 0;
                    for (int i = 0; i < nFw; i++) if (fill_words[i] == p.fill) { seen = 1; break; }
                    if (!seen && nFw < 16) fill_words[nFw++] = p.fill;
                }
                if (p.floor_n) {
                    covered++;
                    have = 1;
                    if (p.floor_n > 1) multi++;
                    if (p.cc_i) cc_count[p.cc_i - 1]++;
                    if (p.cca_i) cca_count[p.cca_i - 1]++;
                    if (p.bl_i) bl_count[p.bl_i - 1]++;
                    if (p.ok) {
                        nok++;
                        if (p.texel < texlo) texlo = p.texel;
                        if (p.texel > texhi) texhi = p.texel;
                    }
                    if (p.ok_i) {
                        int iv = (int)std::lround(p.inten);
                        if (iv < 0) iv = 0;
                        if (iv > 255) iv = 255;
                        if (!anyI) { iLo = iHi = iv; anyI = 1; }
                        else { if (iv < iLo) iLo = iv; if (iv > iHi) iHi = iv; }
                    }
                }
                if (p.other_n) { other++; have = 1; }
            }
            int *np = c == 0 ? &npl : &npr;
            double *sm = c == 0 ? &suml : &sumr;
            for (int r = 0; r < rows - 1; r++) {
                const Rs64FtPt &a = pts[r][c];
                const Rs64FtPt &b = pts[r + 1][c];
                if (a.ok_s && b.ok_s) {
                    sumS += std::fabs((double)b.texel_s - (double)a.texel_s);
                    nS++;
                }
                if (a.ok_l && b.ok_l) {
                    sumL += std::fabs((double)b.luma - (double)a.luma);
                    nL++;
                }
                if (a.ok_i && b.ok_i) {
                    sumI += std::fabs((double)b.inten - (double)a.inten);
                    nI++;
                }
                if (a.ok_f && b.ok_f) {
                    sumF += rs64_fill_delta(a.fill, b.fill);
                    nFp++;
                }
                if (a.ok_a && b.ok_a) {
                    sumA += std::fabs((double)b.alpha - (double)a.alpha);
                    nAa++;
                }
                if (!a.ok || !b.ok) continue;
                const double d = std::fabs((double)b.texel - (double)a.texel);
                sum += d;
                *sm += d;
                (*np)++;
                npair++;
                if (d > maxd) maxd = d;
                if (d > 4.0) jump4++;
                if (d > 8.0) jump8++;
            }
        }
        int mode = -1, mode_n = 0, second = -1, second_n = 0, distinct = 0;
        int amode = -1, amode_n = 0, adistinct = 0;
        int bmode = -1, bmode_n = 0;
        for (int i = 0; i < ncc; i++) {
            if (!cc_count[i]) continue;
            distinct++;
            if (cc_count[i] > mode_n) {
                second = mode; second_n = mode_n;
                mode_n = cc_count[i]; mode = i;
            } else if (cc_count[i] > second_n) {
                second_n = cc_count[i]; second = i;
            }
        }
        for (int i = 0; i < ncca; i++) {
            if (!cca_count[i]) continue;
            adistinct++;
            if (cca_count[i] > amode_n) { amode_n = cca_count[i]; amode = i; }
        }
        for (int i = 0; i < nbl; i++) {
            if (bl_count[i] > bmode_n) { bmode_n = bl_count[i]; bmode = i; }
        }
        const char *cc_mode = mode >= 0 ? cc_str[mode] : "-";
        const char *cca_mode = amode >= 0 ? cca_str[amode] : "-";
        const uint32_t fw = (nFw == 1) ? fill_words[0] : 0u;
        const uint32_t om_mode = mode >= 0 ? cc_omv[mode] : 0u;
        const char *cc_second = second >= 0 ? cc_str[second] : "-";
        const uint32_t om_second = second >= 0 ? cc_omv[second] : 0u;
        const char *bl_mode = bmode >= 0 ? bl_str[bmode] : "-";
        const char *blu = untex_bl_set ? untex_bl : "-";
        if (!have) return;
        if (!nok) { texlo = 0; texhi = 0; }
        const double denom = (double)(rows * cols);
        float xsamp[2];
        rs64_ft_xs(cur_w, xsamp);
        std::fprintf(stderr,
            "[floor-tex] why=%s w=%u floor_frac=%.4f other_frac=%.4f multi_frac=%.4f "
            "dT=%.4f dTl=%.4f dTr=%.4f npair=%d maxdT=%.3f jump4=%d jump8=%d "
            "tex=%.3f..%.3f badw=%d spill=%u dS=%.4f dL=%.4f nS=%d nL=%d "
            "cc=%s omL=%08X ccn=%d n0=%d n1=%d cc2=%s om2=%08X "
            "dI=%.4f nI=%d iLo=%d iHi=%d untex=%.4f bl=%s blu=%s x0=%.2f x1=%.2f "
            "lastF=%.4f lastO=%.4f lastR=%.4f lastN=%.4f nF=%d nO=%d nR=%d nZ=%d "
            "both=%.4f touchR=%.4f touchU=%.4f over=%.4f "
            "nFL=%d nOL=%d nRL=%d nFR=%d nOR=%d nRR=%d "
            "nFs=%d nFw=%d fw=%08X dF=%.4f nFp=%d dA=%.4f nAa=%d cca=%s ccaN=%d\n",
            why, cur_w, covered / denom, other / denom, multi / denom,
            npair ? sum / npair : 0.0, npl ? suml / npl : 0.0, npr ? sumr / npr : 0.0,
            npair, maxd, jump4, jump8, texlo, texhi, covered - nok, spill,
            nS ? sumS / nS : 0.0, nL ? sumL / nL : 0.0, nS, nL,
            cc_mode, om_mode, distinct, mode_n, second_n, cc_second, om_second,
            nI ? sumI / nI : 0.0, nI, iLo, iHi, nUntex / denom, bl_mode, blu,
            xsamp[0], xsamp[1],
            nF / denom, nO / denom, nR / denom, nZ / denom, nF, nO, nR, nZ,
            nBoth / denom, nTouchR / denom, nTouchU / denom, nOver / denom,
            colF[0], colO[0], colR[0], colF[1], colO[1], colR[1],
            nFs, nFw, fw, nFp ? sumF / nFp : 0.0, nFp,
            nAa ? sumA / nAa : 0.0, nAa, cca_mode, adistinct);
        if (mode >= 0 && (!cc_print_set || std::strcmp(cc_printed, cc_mode) != 0 || om_printed != om_mode)) {
            std::fprintf(stderr, "[floor-cc] w=%u cc=%s omL=%08X\n", cur_w, cc_mode, om_mode);
            std::snprintf(cc_printed, sizeof(cc_printed), "%s", cc_mode);
            om_printed = om_mode;
            cc_print_set = 1;
        }
        int order[24];
        const int nk = nkeys < 24 ? nkeys : 24;
        for (int i = 0; i < nk; i++) order[i] = i;
        for (int i = 1; i < nk; i++) {
            int v = order[i], j = i;
            while (j > 0 && keys[order[j - 1]].hits < keys[v].hits) { order[j] = order[j - 1]; j--; }
            order[j] = v;
        }
        const int nprint = nk < 4 ? nk : 4;
        for (int i = 0; i < nprint; i++) {
            const Key &k = keys[order[i]];
            if (!k.hits) continue;
            std::fprintf(stderr, "[floor-tex] other why=%s w=%u op=%02X tile=%u line=%u hits=%u\n",
                why, cur_w, k.op, k.tile, k.line, k.hits);
        }
        std::fflush(stderr);
    }

    bool sync() {
        uint32_t vw = 0, vh = 0;
        rs64_vi_fb_wh(&vw, &vh);
        const bool gate = (vh >= 320 && vh <= 352) && (vw == 796 || vw == 1024);
        if (was && !gate) {
            emit("leave");
            clear();
            origin_set = 0;
            cur_w = 0;
            was = 0;
            return false;
        }
        was = gate ? 1 : 0;
        if (!gate) return false;
        if (cur_w && cur_w != vw) {
            emit("width");
            clear();
            origin_set = 0;
        }
        cur_w = vw;
        const uint32_t now = rs64_vi_committed_origin();
        if (!origin_set) {
            origin = now;
            origin_set = 1;
        } else if (now != origin) {
            emit("frame");
            clear();
            origin = now;
        }
        return true;
    }
};

Rs64Ft g_ft;
} // namespace

extern "C" void rs64_floor_mesh(uint32_t op, uint32_t width, const float *edge,
    const float *plane, const float *vertices, const uint32_t *flags,
    const char *cc, const char *cca) {
    if (!g_ft.sync() || width != g_ft.cur_w) return;
    if (edge[9] < 180.f || edge[8] > 251.f) return;
    const float lo = std::fmin(vertices[0], std::fmin(vertices[10], vertices[20]));
    const float hi = std::fmax(vertices[0], std::fmax(vertices[10], vertices[20]));
    if (!((lo <= 16.f && hi >= 16.f) || (lo <= width - 17.f && hi >= width - 17.f))) return;
    static uint32_t prevOrigin = ~0u, prevWidth = 0, frame = 0, ordinal = 0;
    if (prevOrigin != g_ft.origin || prevWidth != width) {
        frame++; ordinal = 0; prevOrigin = g_ft.origin; prevWidth = width;
    }
    char buf[8192];
    int n = std::snprintf(buf, sizeof(buf), "[floor-mesh] {\"w\":%u,\"origin\":%u,\"frame\":%u,\"ordinal\":%u,\"op\":%u,\"cc\":\"%s\",\"cca\":\"%s\"",
        width, g_ft.origin, frame, ++ordinal, op, cc, cca);
    auto floats = [&](const char *key, const float *v, int count) {
        n = rs64_apf(buf, sizeof buf, n, ",\"%s\":[", key);
        for (int i = 0; i < count; i++)
            n = rs64_apf(buf, sizeof buf, n, "%s%.9g", i ? "," : "", v[i]);
        n = rs64_apf(buf, sizeof buf, n, "]");
    };
    floats("edge", edge, 14); floats("plane", plane, 21); floats("v", vertices, 30);
    n = rs64_apf(buf, sizeof buf, n, ",\"flags\":[");
    for (int i = 0; i < 21; i++)
        n = rs64_apf(buf, sizeof buf, n, "%s%u", i ? "," : "", flags[i]);
    std::snprintf(buf + n, sizeof(buf) - n, "]}\n");
    std::fputs(buf, stderr);
}

extern "C" void rs64_floor_texel(
    uint32_t op, uint32_t tile, uint32_t line, int persp,
    float y_floor, float ym,
    float xh, float dxhdy, float xm, float dxmdy, float xl, float dxldy,
    float yh, float yl,
    float scx0, float scy0, float scx1, float scy1,
    float base_t, float dtde, float dtdx,
    float base_w, float dwde, float dwdx,
    float base_s, float dsde, float dsdx,
    float base_r, float base_g, float base_b,
    float de_r, float de_g, float de_b,
    float dx_r, float dx_g, float dx_b,
    uint32_t om_l, const char *cc_eq,
    uint32_t om_h,
    uint32_t fmt, uint32_t siz, uint32_t tmem,
    uint32_t masks, uint32_t maskt, uint32_t cms, uint32_t cmt,
    uint32_t shifts, uint32_t shiftt,
    uint32_t uls, uint32_t ult, uint32_t lrs, uint32_t lrt,
    uint32_t palette, const uint8_t *tmem_bytes,
    float base_a, float de_a, float dx_a, const char *cca_eq) {
    static const bool on = [] {
        const char *e = std::getenv("ROGUESQ_LOG_FLOOR");
        return e && *e && *e != '0';
    }();
    if (!on) return;
    if (!g_ft.selftest) {
        g_ft.selftest = 1;
        rs64_i4_selftest();
        Rs64Ft control{};
        control.cur_w = 796;
        for (int r = 0; r < 71; r++) {
            for (int c = 0; c < 2; c++) {
                auto &p = control.pts[r][c];
                p.floor_n = p.last = p.ok_a = p.ok_f = 1;
                p.alpha = (r & 1) ? 64.f : 0.f;
                p.fill = (r & 1) ? 0xFFFFFFFFu : 0x00010001u;
            }
        }
        control.emit("selftest-alpha-fill");
    }
    if (!g_ft.sync()) return;
    if (!std::isfinite(y_floor) || !std::isfinite(ym) || !std::isfinite(xh) || !std::isfinite(dxhdy) ||
        !std::isfinite(xm) || !std::isfinite(dxmdy) || !std::isfinite(xl) || !std::isfinite(dxldy) ||
        !std::isfinite(yh) || !std::isfinite(yl)) {
        return;
    }
    float y_lo = yh < yl ? yh : yl;
    float y_hi = yh > yl ? yh : yl;
    if (scy1 > scy0) {
        if (scy0 > y_lo) y_lo = scy0;
        if (scy1 < y_hi) y_hi = scy1;
    }
    if (y_hi < 180.5f || y_lo > 250.5f) return;
    const float x_lo_sc = (scx1 > scx0) ? scx0 : -1.0e9f;
    const float x_hi_sc = (scx1 > scx0) ? scx1 : 1.0e9f;
    float xs[2];
    rs64_ft_xs(g_ft.cur_w, xs);
    const bool is_floor = op == 0x0Fu && tile == 0u && line == 4u;
    const bool tex_ok = std::isfinite(base_t) && std::isfinite(dtde) && std::isfinite(dtdx) &&
        std::isfinite(base_w) && std::isfinite(dwde) && std::isfinite(dwdx);
    char tri_bl[80];
    rs64_bl_eq(om_l, om_h, tri_bl, sizeof(tri_bl));
    if (is_floor && !g_ft.tile_logged) {
        g_ft.tile_logged = 1;
        std::fprintf(stderr,
            "[floor-i4] tile w=%u fmt=%u siz=%u line=%u tmem=%u masks=%u maskt=%u "
            "cms=%u cmt=%u shifts=%u shiftt=%u uls=%u ult=%u lrs=%u lrt=%u pal=%u "
            "tlut=%u filt=%u cyc=%u\n",
            g_ft.cur_w, fmt, siz, line, tmem, masks, maskt, cms, cmt, shifts, shiftt,
            uls, ult, lrs, lrt, palette,
            (om_h >> 14) & 3u, (om_h >> 12) & 3u, (om_h >> 20) & 3u);
        std::fflush(stderr);
    }
    for (int s = 180; s <= 250; s++) {
        const float y = (float)s + 0.5f;
        if (y < y_lo || y > y_hi) continue;
        const float dy = y - y_floor;
        const float x_major = xh + dxhdy * dy;
        const float x_other = (y <= ym) ? (xm + dxmdy * dy) : (xl + dxldy * (y - ym));
        if (!std::isfinite(x_major) || !std::isfinite(x_other)) continue;
        float xa = x_major < x_other ? x_major : x_other;
        float xb = x_major > x_other ? x_major : x_other;
        if (xa < x_lo_sc) xa = x_lo_sc;
        if (xb > x_hi_sc) xb = x_hi_sc;
        if (!(xb > xa) || xb - xa > 8000.f) continue;
        for (int c = 0; c < 2; c++) {
            const float x = xs[c];
            if (x < xa || x > xb) continue;
            Rs64FtPt &p = g_ft.pts[s - 180][c];
            if (is_floor) {
                p.floor_n++;
                p.last = 1;
                const char *eqs = (cc_eq && cc_eq[0]) ? cc_eq : "-";
                int idx = -1;
                for (int i = 0; i < g_ft.ncc; i++) {
                    if (g_ft.cc_omv[i] == om_l && std::strcmp(g_ft.cc_str[i], eqs) == 0) { idx = i; break; }
                }
                if (idx < 0 && g_ft.ncc < 4) {
                    idx = g_ft.ncc++;
                    std::snprintf(g_ft.cc_str[idx], sizeof(g_ft.cc_str[idx]), "%s", eqs);
                    g_ft.cc_omv[idx] = om_l;
                }
                if (idx >= 0) p.cc_i = (uint8_t)(idx + 1);
                const char *aeq = (cca_eq && cca_eq[0]) ? cca_eq : "-";
                int aidx = -1;
                for (int i = 0; i < g_ft.ncca; i++) {
                    if (std::strcmp(g_ft.cca_str[i], aeq) == 0) { aidx = i; break; }
                }
                if (aidx < 0 && g_ft.ncca < 4) {
                    aidx = g_ft.ncca++;
                    std::snprintf(g_ft.cca_str[aidx], sizeof(g_ft.cca_str[aidx]), "%s", aeq);
                }
                if (aidx >= 0) p.cca_i = (uint8_t)(aidx + 1);
                int bidx = -1;
                for (int i = 0; i < g_ft.nbl; i++) {
                    if (std::strcmp(g_ft.bl_str[i], tri_bl) == 0) { bidx = i; break; }
                }
                if (bidx < 0 && g_ft.nbl < 4) {
                    bidx = g_ft.nbl++;
                    std::snprintf(g_ft.bl_str[bidx], sizeof(g_ft.bl_str[bidx]), "%s", tri_bl);
                }
                if (bidx >= 0) p.bl_i = (uint8_t)(bidx + 1);
                if (persp && tex_ok) {
                    const float T = base_t + dtde * dy + dtdx * (x - x_major);
                    const float W = base_w + dwde * dy + dwdx * (x - x_major);
                    if (std::fabs(W) > 1.0e-8f && std::isfinite(T) && std::isfinite(W)) {
                        p.texel = (T / W) * 1024.0f;
                        p.ok = 1;
                        float texel_s = 0.f;
                        if (std::isfinite(base_s) && std::isfinite(dsde) && std::isfinite(dsdx)) {
                            const float S = base_s + dsde * dy + dsdx * (x - x_major);
                            if (std::isfinite(S)) {
                                texel_s = (S / W) * 1024.0f;
                                p.texel_s = texel_s;
                                p.ok_s = 1;
                            }
                        }
                        p.ok_i = 0;
                        if (tmem_bytes && fmt == 4u && siz == 0u && p.ok_s) {
                            p.inten = rs64_i4_fetch(tmem_bytes, p.texel_s, p.texel, line, tmem,
                                masks, maskt, cms, cmt, shifts, shiftt, uls, ult, lrs, lrt, palette, om_h);
                            p.ok_i = 1;
                        }
                        if (g_ft.raws < 4 && (s == 200 || s == 230)) {
                            g_ft.raws++;
                            const float R = base_r + de_r * dy + dx_r * (x - x_major);
                            const float G = base_g + de_g * dy + dx_g * (x - x_major);
                            const float B = base_b + de_b * dy + dx_b * (x - x_major);
                            const float luma = 0.2126f * R + 0.7152f * G + 0.0722f * B;
                            std::fprintf(stderr,
                                "[floor-tex] raw w=%u y=%d x=%.2f T=%.5f W=%.5f texel=%.3f texelS=%.3f luma=%.3f "
                                "dtdx=%.5f dsdx=%.5f dwdx=%.5f dtde=%.5f cc=%s omL=%08X i4=%.1f\n",
                                g_ft.cur_w, s, x, T, W, p.texel, texel_s, luma, dtdx, dsdx, dwdx, dtde,
                                eqs, om_l, p.ok_i ? p.inten : -1.0f);
                            std::fflush(stderr);
                        }
                    } else {
                        p.ok = 0;
                        p.ok_s = 0;
                        p.ok_i = 0;
                    }
                } else {
                    p.ok = 0;
                    p.ok_s = 0;
                    p.ok_i = 0;
                }
                const float R = base_r + de_r * dy + dx_r * (x - x_major);
                const float G = base_g + de_g * dy + dx_g * (x - x_major);
                const float B = base_b + de_b * dy + dx_b * (x - x_major);
                if (std::isfinite(R) && std::isfinite(G) && std::isfinite(B)) {
                    p.luma = 0.2126f * R + 0.7152f * G + 0.0722f * B;
                    p.ok_l = 1;
                } else {
                    p.ok_l = 0;
                }
                const float A = base_a + de_a * dy + dx_a * (x - x_major);
                if (std::isfinite(A)) {
                    p.alpha = A;
                    p.ok_a = 1;
                } else {
                    p.ok_a = 0;
                }
            } else {
                p.other_n++;
                p.last = 2;
                g_ft.add_key(op, tile, line);
            }
        }
    }
}

extern "C" void rs64_floor_untex(
    float y_floor, float ym,
    float xh, float dxhdy, float xm, float dxmdy, float xl, float dxldy,
    float yh, float yl,
    float scx0, float scy0, float scx1, float scy1,
    uint32_t om_l, uint32_t om_h) {
    static const bool on = [] {
        const char *e = std::getenv("ROGUESQ_LOG_FLOOR");
        return e && *e && *e != '0';
    }();
    if (!on) return;
    if (!g_ft.sync()) return;
    if (!std::isfinite(y_floor) || !std::isfinite(ym) || !std::isfinite(xh) || !std::isfinite(dxhdy) ||
        !std::isfinite(xm) || !std::isfinite(dxmdy) || !std::isfinite(xl) || !std::isfinite(dxldy) ||
        !std::isfinite(yh) || !std::isfinite(yl)) {
        return;
    }
    float y_lo = yh < yl ? yh : yl;
    float y_hi = yh > yl ? yh : yl;
    if (scy1 > scy0) {
        if (scy0 > y_lo) y_lo = scy0;
        if (scy1 < y_hi) y_hi = scy1;
    }
    if (y_hi < 180.5f || y_lo > 250.5f) return;
    const float x_lo_sc = (scx1 > scx0) ? scx0 : -1.0e9f;
    const float x_hi_sc = (scx1 > scx0) ? scx1 : 1.0e9f;
    float xs[2];
    rs64_ft_xs(g_ft.cur_w, xs);
    int hit = 0;
    for (int s = 180; s <= 250; s++) {
        const float y = (float)s + 0.5f;
        if (y < y_lo || y > y_hi) continue;
        float xa, xb;
        if (!rs64_ft_span(y, y_floor, ym, xh, dxhdy, xm, dxmdy, xl, dxldy, x_lo_sc, x_hi_sc, xa, xb)) continue;
        for (int c = 0; c < 2; c++) {
            if (xs[c] < xa || xs[c] > xb) continue;
            Rs64FtPt &p = g_ft.pts[s - 180][c];
            if (p.untex_n < 65535) p.untex_n++;
            if (p.utri_n < 255) p.utri_n++;
            p.last = 2;
            hit = 1;
        }
    }
    if (hit) {
        rs64_bl_eq(om_l, om_h, g_ft.untex_bl, sizeof(g_ft.untex_bl));
        g_ft.untex_bl_set = 1;
    }
}

extern "C" void rs64_floor_rect(
    float x0, float y0, float x1, float y1,
    float scx0, float scy0, float scx1, float scy1,
    uint32_t om_l, uint32_t om_h, uint32_t fill_word, int is_fill) {
    static const bool on = [] {
        const char *e = std::getenv("ROGUESQ_LOG_FLOOR");
        return e && *e && *e != '0';
    }();
    if (!on) return;
    if (!g_ft.sync()) return;
    if (x0 > x1) { float t = x0; x0 = x1; x1 = t; }
    if (y0 > y1) { float t = y0; y0 = y1; y1 = t; }
    if (scx1 > scx0) {
        if (x0 < scx0) x0 = scx0;
        if (x1 > scx1) x1 = scx1;
    }
    if (scy1 > scy0) {
        if (y0 < scy0) y0 = scy0;
        if (y1 > scy1) y1 = scy1;
    }
    if (!(x1 > x0) || !(y1 > y0)) return;
    float xs[2];
    rs64_ft_xs(g_ft.cur_w, xs);
    int hit = 0;
    for (int s = 180; s <= 250; s++) {
        const float y = (float)s + 0.5f;
        if (y < y0 || y > y1) continue;
        for (int c = 0; c < 2; c++) {
            if (xs[c] < x0 || xs[c] > x1) continue;
            Rs64FtPt &p = g_ft.pts[s - 180][c];
            if (p.untex_n < 65535) p.untex_n++;
            if (p.rect_n < 255) p.rect_n++;
            p.last = 3;
            if (is_fill) {
                p.fill = fill_word;
                p.ok_f = 1;
            } else {
                p.fill = 0;
                p.ok_f = 0;
            }
            hit = 1;
        }
    }
    if (hit) {
        rs64_bl_eq(om_l, om_h, g_ft.untex_bl, sizeof(g_ft.untex_bl));
        g_ft.untex_bl_set = 1;
    }
}


// s6613: base S/T are the s15.16 coefficients decodeTriangles already
// computed. S at screen x=0 is that base walked to the band scanline
// (y in 180..250) and then across by dsdx. The texel is the same
// quantity the vertex buffer stores: (S/W)*1024 when perspective is on,
// S/16 when it is off. The sampler then multiplies by the tile shift and
// subtracts uls/4. "Inside the mask" is that sampled S in [0, 2^masks).
extern "C" void rs64_floor_note(
    int kind, int textured, uint32_t op, uint32_t tile,
    float x0, float y0, float x1, float y1,
    float dsdx, float dtdx, float dsde, float dtde,
    uint32_t line, uint32_t timg_w, uint32_t fmt, uint32_t siz,
    uint32_t masks, uint32_t maskt, uint32_t cms, uint32_t cmt,
    uint32_t cimg_w,
    float base_s, float base_t, float base_w,
    float s0, float t0, float w0,
    float sample_y, float x_major,
    int persp, int cover0,
    uint32_t uls, uint32_t ult, uint32_t shifts, uint32_t shiftt) {
    static const bool on = [] {
        const char *e = std::getenv("ROGUESQ_LOG_FLOOR");
        return e && *e && *e != '0';
    }();
    if (!on) return;
    struct Row {
        uint8_t kind = 0, op = 0, tile = 0, fmt = 0, siz = 0, masks = 0, maskt = 0, cms = 0, cmt = 0;
        uint8_t persp = 0, shifts = 0, shiftt = 0;
        uint16_t line = 0, timg_w = 0, cimg_w = 0, uls = 0, ult = 0;
        int32_t qs = 0, qt = 0;
        uint32_t hits = 0, pc = 0, n_in = 0, n_cover = 0;
        double area = 0, dsdx = 0, dtdx = 0, dsde = 0, dtde = 0;
        double minx = 1e9, maxx = -1e9, miny = 1e9, maxy = -1e9;
        double base_s = 0, base_t = 0, base_w = 0, s0 = 0, t0 = 0, w0 = 0;
        double sample_y = 0, x_major = 0, tex_s = 0, tex_t = 0;
        double tex_s_min = 1e300, tex_s_max = -1e300;
    };
    static Row rows[48];
    static int nrows = 0;
    static uint32_t hits = 0, draws = 0, n_tri = 0, n_rect = 0, n_sane = 0, raws = 0;
    static uint32_t n_in = 0, n_out = 0, n_cover_in = 0, n_cover_out = 0;
    static int dumped = 0;
    static bool was = false;
    static uint32_t gate_w = 0, gate_h = 0;
    uint32_t vw = 0, vh = 0;
    rs64_vi_fb_wh(&vw, &vh);
    const bool gate = (vh >= 320 && vh <= 352) && (vw == 796 || vw == 1024);
    auto dump_rows = [&](const char *why) {
        fprintf(stderr, "[floor] table why=%s w=%u h=%u submits=%u seen_tex=%u hits=%u keys=%d "
                "tri=%u sane=%u rect=%u sane_rect=%u cimg=%u settile=%u other=%u "
                "st_in=%u st_out=%u cover_in=%u cover_out=%u\n",
                why, gate_w, gate_h, draws, hits, hits, nrows,
                n_tri, n_sane, n_rect, n_sane, cimg_w, 0u, 0u,
                n_in, n_out, n_cover_in, n_cover_out);
        if (!nrows) { fflush(stderr); return; }
        int order[48];
        for (int i = 0; i < nrows; i++) order[i] = i;
        for (int i = 1; i < nrows; i++) {
            int v = order[i], j = i;
            while (j > 0 && rows[order[j - 1]].area < rows[v].area) { order[j] = order[j - 1]; j--; }
            order[j] = v;
        }
        const int nprint = nrows < 16 ? nrows : 16;
        for (int i = 0; i < nprint; i++) {
            const Row &r = rows[order[i]];
            fprintf(stderr,
                    "[floor] row why=%s kind=%s op=%02X tile=%u line=%u timgw=%u fmt=%u siz=%u "
                    "masks=%u maskt=%u cms=%u cmt=%u dsdx=%.4f dtdx=%.4f dsde=%.4f dtde=%.4f "
                    "hits=%u area=%.0f x=%.0f..%.0f y=%.0f..%.0f timg=%06X root=%06X pc=%08X f5=%06X cimg=%u "
                    "base=%.3f,%.3f,%.5f s0=%.3f t0=%.3f w0=%.5f tex=%.3f,%.3f texS=%.3f..%.3f "
                    "ys=%.1f xmaj=%.1f persp=%u cover=%u/%u uls=%u ult=%u sh=%u/%u in=%u/%u\n",
                    why, r.kind ? "rect" : "tri", r.op, r.tile, r.line, r.timg_w, r.fmt, r.siz,
                    r.masks, r.maskt, r.cms, r.cmt, r.dsdx, r.dtdx, r.dsde, r.dtde,
                    r.hits, r.area, r.minx, r.maxx, r.miny, r.maxy,
                    0u, g_e9prov.root_dl & 0xFFFFFFu, r.pc, 0u, r.cimg_w,
                    r.base_s, r.base_t, r.base_w, r.s0, r.t0, r.w0, r.tex_s, r.tex_t,
                    r.tex_s_min, r.tex_s_max, r.sample_y, r.x_major, r.persp,
                    r.n_cover, r.hits, r.uls, r.ult, r.shifts, r.shiftt, r.n_in, r.hits);
        }
        fflush(stderr);
    };
    if (was && !gate) {
        dump_rows("leave");
        rs64_floor_cover_emit("leave-frame", s_cov_frame);
        rs64_floor_cover_emit("leave-union", s_cov_union);
        rs64_cov_clear(s_cov_frame);
        rs64_cov_clear(s_cov_union);
        s_cov_frames = 0;
        s_cov_origin_set = 0;
        s_cov_w = 0;
        nrows = 0; hits = 0; draws = 0; n_tri = n_rect = n_sane = 0; dumped = 0; raws = 0;
        n_in = n_out = n_cover_in = n_cover_out = 0;
    }
    was = gate;
    if (!gate) return;
    gate_w = vw; gate_h = vh;
    if (kind) n_rect++; else n_tri++;
    const bool on_fb = x1 > -8.0f && x0 < vw + 8.0f && y1 > -8.0f && y0 < vh + 8.0f &&
        (x1 - x0) > 0.25f && (y1 - y0) > 0.25f &&
        (cimg_w == 0 || cimg_w + 1 >= vw) && cimg_w < vw + 8;
    if (textured && on_fb) n_sane++;
    const bool band = textured && on_fb && x0 < vw / 3.0f && x1 > 0.0f && y0 < 260.0f && y1 > 170.0f;
    if (draws++ == 0) {
        fprintf(stderr, "[floor] enter w=%u h=%u phase=%u\n", vw, vh, rs64_phase_ord());
        fflush(stderr);
    }
    if (band) {
        const float area = (x1 - x0) * (y1 - y0);
        static const float kShift[16] = {
            1.f, 0.5f, 0.25f, 0.125f, 1.f / 16.f, 1.f / 32.f, 1.f / 64.f, 1.f / 128.f,
            1.f / 256.f, 1.f / 512.f, 1.f / 1024.f, 32.f, 16.f, 8.f, 4.f, 2.f
        };
        float tex_s = 0.f, tex_t = 0.f;
        int tex_ok = 0;
        if (persp) {
            if (std::fabs(w0) > 1.0e-8f) {
                tex_s = (s0 / w0) * 1024.0f;
                tex_t = (t0 / w0) * 1024.0f;
                tex_ok = 1;
            }
        } else {
            tex_s = s0 / 16.0f;
            tex_t = t0 / 16.0f;
            tex_ok = 1;
        }
        const float persp_mod = (kind == 0 && !persp) ? 0.5f : 1.0f;
        const float shift_s = kShift[shifts & 15u];
        const float shift_t = kShift[shiftt & 15u];
        if (tex_ok) {
            tex_s = tex_s * persp_mod * shift_s - float(uls) / 4.0f;
            tex_t = tex_t * persp_mod * shift_t - float(ult) / 4.0f;
        }
        const float span = masks ? float(1u << (masks & 15u)) : 0.0f;
        const int inside = tex_ok && span > 0.0f && tex_s >= 0.0f && tex_s < span;
        if (inside) n_in++; else n_out++;
        if (cover0) { if (inside) n_cover_in++; else n_cover_out++; }
        Row key{};
        key.kind = (uint8_t)kind; key.op = (uint8_t)op; key.tile = (uint8_t)tile;
        key.line = (uint16_t)line; key.timg_w = (uint16_t)timg_w;
        key.fmt = (uint8_t)fmt; key.siz = (uint8_t)siz;
        key.masks = (uint8_t)masks; key.maskt = (uint8_t)maskt;
        key.cms = (uint8_t)cms; key.cmt = (uint8_t)cmt;
        key.cimg_w = (uint16_t)cimg_w;
        key.qs = (int32_t)std::lround(dsdx * 64.0); key.qt = (int32_t)std::lround(dtde * 64.0);
        key.dsdx = dsdx; key.dtdx = dtdx; key.dsde = dsde; key.dtde = dtde;
        key.pc = g_rs64_last_guest_pc;
        key.persp = (uint8_t)(persp ? 1 : 0);
        key.shifts = (uint8_t)shifts; key.shiftt = (uint8_t)shiftt;
        key.uls = (uint16_t)uls; key.ult = (uint16_t)ult;
        key.base_s = base_s; key.base_t = base_t; key.base_w = base_w;
        key.s0 = s0; key.t0 = t0; key.w0 = w0;
        key.sample_y = sample_y; key.x_major = x_major;
        key.tex_s = tex_s; key.tex_t = tex_t;
        int slot = -1;
        for (int i = 0; i < nrows; i++) {
            if (rows[i].kind == key.kind && rows[i].op == key.op && rows[i].tile == key.tile &&
                rows[i].line == key.line && rows[i].timg_w == key.timg_w &&
                rows[i].fmt == key.fmt && rows[i].siz == key.siz &&
                rows[i].qs == key.qs && rows[i].qt == key.qt) { slot = i; break; }
        }
        if (slot < 0 && nrows < 48) { slot = nrows++; rows[slot] = key; }
        else if (slot < 0) {
            int small = 0;
            for (int i = 1; i < nrows; i++) if (rows[i].area < rows[small].area) small = i;
            if (area > rows[small].area) { rows[small] = key; slot = small; }
        }
        if (slot >= 0) {
            Row &r = rows[slot];
            r.hits++; r.area += area;
            if (inside) r.n_in++;
            if (cover0) r.n_cover++;
            if (tex_s < r.tex_s_min) r.tex_s_min = tex_s;
            if (tex_s > r.tex_s_max) r.tex_s_max = tex_s;
            if (x0 < r.minx) r.minx = x0; if (x1 > r.maxx) r.maxx = x1;
            if (y0 < r.miny) r.miny = y0; if (y1 > r.maxy) r.maxy = y1;
            hits++;
            if (raws < 8) {
                raws++;
                fprintf(stderr, "[floor-raw] %s op=%02X tile=%u line=%u timgw=%u dsdx=%.4f dtde=%.4f x=%.0f..%.0f y=%.0f..%.0f cimg=%u\n",
                        kind ? "rect" : "tri", op, tile, line, timg_w, dsdx, dtde, x0, x1, y0, y1, cimg_w);
                fflush(stderr);
            }
        }
    }
    if (dumped == 0 && hits >= 40) { dump_rows("early"); dumped = 1; }
    else if (dumped == 1 && hits >= 400) { dump_rows("mid"); dumped = 2; }
    if (draws == 1 || draws == 40 || (draws % 2000u) == 0u) {
        fprintf(stderr, "[floor] census w=%u h=%u submits=%u tri=%u sane=%u rect=%u sane_rect=%u "
                "cimg=%u settile=%u other=%u hits=%u keys=%d\n",
                vw, vh, draws, n_tri, n_sane, n_rect, n_sane, cimg_w, 0u, 0u, hits, nrows);
        fflush(stderr);
    }
}

// s6692 G1d: floor texture-source census (ROGUESQ_LOG_FLOOR). For every textured
// triangle whose bbox centre falls in the g1d_row_noise side band (rows 180..330,
// outer 22% each side) while the VI fb is the level-select shape, record the tile
// it samples (SetTile), the last load into that tile's TMEM address (LoadBlock /
// LoadTile, the SetTImg it read from, source byte range), how many submits ago
// that load ran (never = stale TMEM), and whether the source range overlaps the
// current colour image, the depth image, or another colour image seen recently.
// Positive control: the 16:9 run must print its floor's load with bytes > 0.
static void rs64_floor_scan(uint32_t lo, uint32_t hi) {
    static const bool on = [] {
        const char *e = std::getenv("ROGUESQ_LOG_FLOOR");
        return e && *e && *e != '0';
    }();
    if (!on || g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    struct Tile { uint8_t fmt = 0, siz = 0, cmt = 0, cms = 0, maskt = 0, masks = 0; uint16_t line = 0, tmem = 0; };
    struct Load { uint8_t kind = 0, tile = 0, fmt = 0, siz = 0; uint16_t tmem = 0xFFFF, timg_w = 0;
                  uint32_t timg = 0, src_lo = 0, src_hi = 0, p0 = 0, p1 = 0; uint32_t sub = 0; };
    static Tile tiles[8];
    static Load loads[16]; static int nload = 0;           // ring of loads keyed by tmem
    static uint32_t timg = 0, timg_w = 0, timg_fmt = 0, timg_siz = 0;
    static uint32_t cimg = 0, cimg_w = 0, zimg = 0;
    static uint32_t recent_ci[8] = {}, recent_ciw[8] = {}; static int nci = 0;
    static uint32_t sub = 0, gated = 0, lines = 0;
    struct Key { uint8_t side, op, tile, fmt, siz, kind, lfmt, lsiz, own, age; uint16_t line, tmem, timg_w;
                 uint32_t timg, src_lo, src_hi, p0, p1, cimg, cimg_w, zimg; uint32_t hits; int sw0, sw1;
                 double x0, x1, y0, y1; };
    static Key keys[96]; static int nkeys = 0;
    // Per-swap frame census: tris low (bbox centre y>170) / textured / z-compare on,
    // fill rects into the depth image (z clear), colour images used.
    struct Fr { int sw = -1; uint32_t tri = 0, low = 0, low_tex = 0, low_zc = 0, low_zc_noz = 0, zclear = 0, fill = 0;
                double low_area = 0; uint32_t ci[4] = {}, nci = 0;
                double zmin = 1e30, zmax = -1e30; uint32_t zneg = 0, zover = 0, zn = 0;
                uint32_t zc_rect = 0, zc_fill = 0; };
    static uint32_t fill_color = 0;
    static Fr fr; static uint32_t fr_lines = 0; static uint32_t othermode_hi = 0, othermode_lo = 0;
    sub++;
    uint32_t vw = 0, vh = 0;
    rs64_vi_fb_wh(&vw, &vh);
    const bool gate = (vh >= 320 && vh <= 352) && (vw == 796 || vw == 1024);
    const int sw = g_rs64_swap_n.load(std::memory_order_relaxed);
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & kSubmitRamMask), 4); return v; };
    auto sx14 = [](uint32_t v) { return (double)(((int32_t)(v << 18)) >> 18) / 4.0; };
    auto ovl = [](uint32_t a0, uint32_t a1, uint32_t b0, uint32_t b1) { return a0 < b1 && b0 < a1; };
    const uint32_t fbh = vh ? vh : 336;
    if (gate && sw != fr.sw) {
        if (fr.sw >= 0 && fr_lines++ < 600)
            fprintf(stderr, "[floor-frame] w=%u sw=%d tri=%u low=%u low_tex=%u low_zc=%u low_zc_noz=%u low_area=%.0f "
                    "fill=%u zclear=%u ci=%06X,%06X,%06X nci=%u zimg=%06X z=%.1f..%.1f zn=%u zneg=%u zover=%u zc_rect=%08X zc_fill=%08X\n",
                    vw, fr.sw, fr.tri, fr.low, fr.low_tex,
                    fr.low_zc, fr.low_zc_noz, fr.low_area, fr.fill, fr.zclear, fr.ci[0], fr.ci[1], fr.ci[2], fr.nci, zimg,
                    fr.zmin, fr.zmax, fr.zn, fr.zneg, fr.zover, fr.zc_rect, fr.zc_fill);
        fr = Fr{}; fr.sw = sw;
    }
    auto print_key = [&](const char *why, const Key &k) {
        fprintf(stderr,
                "[floor-src] why=%s cimg_w=%u side=%c op=%02X tile=%u tfmt=%u tsiz=%u line=%u tmem=%03X "
                "load=%s ltile_fmt=%u lsiz=%u timg=%06X timg_w=%u src=%06X..%06X bytes=%u p0=%08X p1=%08X "
                "age=%s own=%s%s%s%s cimg=%06X zimg=%06X heap=%08X hits=%u sw=%d..%d bbox=(%.0f..%.0f,%.0f..%.0f)\n",
                why, k.cimg_w, k.side, k.op, k.tile, k.fmt, k.siz, k.line, k.tmem,
                k.kind == 0 ? "none" : k.kind == 1 ? "block" : "tile", k.lfmt, k.lsiz, k.timg, k.timg_w,
                k.src_lo, k.src_hi, k.src_hi - k.src_lo, k.p0, k.p1,
                k.age == 0 ? "same" : k.age == 1 ? "older" : "never",
                k.own ? "" : "free", (k.own & 1) ? "CI," : "", (k.own & 2) ? "ZI," : "", (k.own & 4) ? "otherCI," : "",
                k.cimg, k.zimg, rd(0x1163E4u), k.hits, k.sw0, k.sw1, k.x0, k.x1, k.y0, k.y1);
    };
    for (uint32_t a = lo & ~3u; a + 8 <= hi;) {
        const uint32_t w0 = rd(a), w1 = rd(a + 4);
        const uint32_t op = (w0 >> 24) & 0x3F;
        if (op == 0x24 || op == 0x25) { a += 16; continue; }
        if (op >= 0x08 && op <= 0x0F) {
            const uint32_t len = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
            if (a + 32 > hi) break;
            if (gate) {
                const double yl_ = sx14(w0 & 0x3FFF), yh_ = sx14(w1 & 0x3FFF);
                fr.tri++;
                if ((yl_ + yh_) / 2 > 170.0) {
                    const bool zc = (othermode_lo >> 4) & 1;
                    fr.low++; if (op & 2) fr.low_tex++; if (zc) { fr.low_zc++; if (!(op & 1)) fr.low_zc_noz++; }
                    const double xa = (double)(int32_t)rd(a + 8) / 65536.0, xb = (double)(int32_t)rd(a + 16) / 65536.0;
                    fr.low_area += std::fabs(xa - xb) * (yl_ - yh_);
                    if (op & 1) {
                        const double z = (double)(int32_t)rd(a + len - 16) / 65536.0;
                        fr.zn++; if (z < 0) fr.zneg++; if (z > 32767.0) fr.zover++;
                        fr.zmin = z < fr.zmin ? z : fr.zmin; fr.zmax = z > fr.zmax ? z : fr.zmax;
                    }
                }
            }
            if (gate && (op & 2)) {
                const double yl = sx14(w0 & 0x3FFF), ym = sx14((w1 >> 16) & 0x3FFF), yh = sx14(w1 & 0x3FFF);
                auto fx = [&](uint32_t o) { return (double)(int32_t)rd(a + o) / 65536.0; };
                const double xl = fx(8), dl = fx(12), xh = fx(16), dh = fx(20), xm = fx(24), dm = fx(28);
                const double xs[5] = {xh, xm + dm * (ym - yh), xl, xl + dl * (yl - ym), xh + dh * (yl - yh)};
                double mn = 1e9, mx = -1e9; for (double x : xs) { mn = x < mn ? x : mn; mx = x > mx ? x : mx; }
                const double cx = (mn + mx) / 2, cy = (yh + yl) / 2;
                const char side = cx < 0.22 * vw ? 'L' : cx > 0.78 * vw ? 'R' : 0;
                if (side && cy >= 180.0 && cy <= 330.0) {
                    const uint32_t t = (w0 >> 16) & 7;
                    const Tile &T = tiles[t];
                    const Load *L = nullptr;
                    for (int i = 0; i < nload && i < 16; i++) {
                        const Load &c = loads[(nload - 1 - i) & 15];
                        if (c.tmem == T.tmem) { L = &c; break; }
                    }
                    Key k{}; k.side = side; k.op = op; k.tile = t; k.fmt = T.fmt; k.siz = T.siz; k.line = T.line;
                    k.tmem = T.tmem; k.cimg = cimg; k.cimg_w = cimg_w; k.zimg = zimg;
                    if (L) { k.kind = L->kind; k.lfmt = L->fmt; k.lsiz = L->siz; k.timg = L->timg; k.timg_w = L->timg_w;
                             k.src_lo = L->src_lo; k.src_hi = L->src_hi; k.p0 = L->p0; k.p1 = L->p1;
                             k.age = L->sub == sub ? 0 : 1; }
                    else k.age = 2;
                    const uint32_t ci_bytes = cimg_w * fbh * 2;
                    if (L && ovl(k.src_lo, k.src_hi, cimg, cimg + ci_bytes)) k.own |= 1;
                    if (L && zimg && ovl(k.src_lo, k.src_hi, zimg, zimg + cimg_w * fbh * 2)) k.own |= 2;
                    for (int i = 0; L && i < nci && i < 8; i++)
                        if (recent_ci[i] != cimg && ovl(k.src_lo, k.src_hi, recent_ci[i], recent_ci[i] + recent_ciw[i] * fbh * 2)) k.own |= 4;
                    int hit = -1;
                    for (int i = 0; i < nkeys; i++) {
                        const Key &q = keys[i];
                        if (q.side == k.side && q.op == k.op && q.tile == k.tile && q.tmem == k.tmem && q.line == k.line &&
                            q.timg == k.timg && q.src_lo == k.src_lo && q.src_hi == k.src_hi && q.kind == k.kind &&
                            q.age == k.age && q.own == k.own && q.cimg_w == k.cimg_w && q.fmt == k.fmt && q.siz == k.siz) { hit = i; break; }
                    }
                    if (hit < 0 && nkeys < 96) {
                        k.sw0 = k.sw1 = sw; k.x0 = mn; k.x1 = mx; k.y0 = yh; k.y1 = yl; k.hits = 1;
                        keys[nkeys] = k; hit = nkeys++;
                        if (lines++ < 400) print_key("new", k);
                    } else if (hit >= 0) {
                        Key &q = keys[hit]; q.hits++; q.sw1 = sw;
                        q.x0 = mn < q.x0 ? mn : q.x0; q.x1 = mx > q.x1 ? mx : q.x1;
                        q.y0 = yh < q.y0 ? yh : q.y0; q.y1 = yl > q.y1 ? yl : q.y1;
                    }
                }
            }
            a += len; continue;
        }
        switch (op) {
        case 0x3D: timg = w1 & 0xFFFFFF; timg_w = (w0 & 0xFFF) + 1; timg_fmt = (w0 >> 21) & 7; timg_siz = (w0 >> 19) & 3; break;
        case 0x3F: {
            cimg = w1 & 0xFFFFFF; cimg_w = (w0 & 0xFFF) + 1;
            bool seen = false;
            if (gate) { bool f = false; for (uint32_t i = 0; i < fr.nci && i < 4; i++) f |= fr.ci[i] == cimg;
                        if (!f) { if (fr.nci < 4) fr.ci[fr.nci] = cimg; fr.nci++; } }
            for (int i = 0; i < nci && i < 8; i++) if (recent_ci[i] == cimg) { seen = true; recent_ciw[i] = cimg_w; }
            if (!seen) { recent_ci[nci & 7] = cimg; recent_ciw[nci & 7] = cimg_w; nci++; }
            break; }
        case 0x3E: zimg = w1 & 0xFFFFFF; break;
        case 0x2F: othermode_hi = w0; othermode_lo = w1; break;
        case 0x37: fill_color = w1; break;
        case 0x36: if (gate) { fr.fill++; if (zimg && cimg == zimg) { fr.zclear++; fr.zc_rect = w0 & 0xFFFFFF; fr.zc_fill = fill_color;
                       if (fr_lines < 600) fprintf(stderr, "[floor-zclear] w=%u sw=%d lr=(%u,%u) ul=(%u,%u) fill=%08X cimg_w=%u\n", vw, sw,
                           ((w0 >> 12) & 0xFFF) >> 2, (w0 & 0xFFF) >> 2, ((w1 >> 12) & 0xFFF) >> 2, (w1 & 0xFFF) >> 2, fill_color, cimg_w); } } break;
        case 0x35: {
            const uint32_t t = (w1 >> 24) & 7; Tile &T = tiles[t];
            T.fmt = (w0 >> 21) & 7; T.siz = (w0 >> 19) & 3; T.line = (w0 >> 9) & 0x1FF; T.tmem = w0 & 0x1FF;
            T.cmt = (w1 >> 18) & 3; T.maskt = (w1 >> 14) & 0xF; T.cms = (w1 >> 8) & 3; T.masks = (w1 >> 4) & 0xF;
            break; }
        case 0x33: case 0x34: {
            const uint32_t t = (w1 >> 24) & 7;
            Load &L = loads[nload & 15]; nload++;
            L.kind = op == 0x33 ? 1 : 2; L.tile = t; L.fmt = timg_fmt; L.siz = timg_siz; L.tmem = tiles[t].tmem;
            L.timg = timg; L.timg_w = timg_w; L.p0 = w0; L.p1 = w1; L.sub = sub;
            const uint32_t uls = (w0 >> 12) & 0xFFF, ult = w0 & 0xFFF, lrs = (w1 >> 12) & 0xFFF, lrt = w1 & 0xFFF;
            if (op == 0x33) {
                const uint32_t texels = lrs >= uls ? lrs - uls + 1 : 0;
                L.src_lo = timg + (((ult * timg_w + uls) << timg_siz) >> 1);
                L.src_hi = L.src_lo + ((texels << timg_siz) >> 1);
            } else {
                const uint32_t r0 = ult >> 2, r1 = lrt >> 2, c0 = uls >> 2, c1 = lrs >> 2;
                L.src_lo = timg + (((r0 * timg_w + c0) << timg_siz) >> 1);
                L.src_hi = timg + (((r1 * timg_w + c1 + 1) << timg_siz) >> 1);
            }
            break; }
        default: break;
        }
        a += 8;
    }
    if (gate && ++gated % 300 == 0) {
        fprintf(stderr, "[floor-src] table gated=%u keys=%d w=%u sw=%d\n", gated, nkeys, vw, sw);
        for (int i = 0; i < nkeys; i++) print_key("table", keys[i]);
        fflush(stderr);
    }
}


// s6695: swap number of the last renderRadarMinimap call (fixup tools/apply_s6695_radarmark.py).
static std::atomic<int> g_rs64_radar_swap{-1000};
// s6730: the 8-swap window outlived flight: the first ~7 swaps of the 21:9 game-over screen still counted as "radar
// drawn", so the s6158 disc-region shift moved the backdrop tiles whose lower-right corner fell in the region (tiles
// 6,7,14,15,22,23,30,31: x 640..768) by +256 -- 896..960 and a wrapped 960..0 -- and the top-right block stayed undrawn.
// The stamp now also records the G1d VI epoch; a mode change (flight -> game over / debrief) ends the window at once.
// ROGUESQ_RADAR_GATE_EPOCH=0 restores the swap-only window.
extern "C" int rs64_g1d_vi_epoch;
static std::atomic<int> g_rs64_radar_epoch{-1};
static std::atomic<uint32_t> g_rs64_census_radar{0}; // s6762 census
extern "C" void rs64_radar_mark(void) {
    g_rs64_census_radar.fetch_add(1, std::memory_order_relaxed);
    g_rs64_radar_swap.store(g_rs64_swap_n.load(std::memory_order_relaxed), std::memory_order_relaxed);
    g_rs64_radar_epoch.store(__atomic_load_n(&rs64_g1d_vi_epoch, __ATOMIC_RELAXED), std::memory_order_relaxed);
}
static bool rs64_radar_recent(int sw) {
    static const bool swapOnly = [] { const char *e = std::getenv("ROGUESQ_RADAR_GATE_EPOCH"); return e && *e == '0'; }();
    if ((sw - g_rs64_radar_swap.load(std::memory_order_relaxed)) > 8) return false;
    return swapOnly || g_rs64_radar_epoch.load(std::memory_order_relaxed) == __atomic_load_n(&rs64_g1d_vi_epoch, __ATOMIC_RELAXED);
}
// s6721: initHudStruct's pause-menu byte (HUD+0x258, 0x800C1998), stamped every frame (tools/apply_s6721_pausegate.py).
// The s6156 HUD anchor skips while it is set, so pause-menu text stays centred like retail.
// s6861: the byte is a state, not a flag (initOrUpdatePauseScreenDim: 1 opening, 3 open, 2 closing, timer HUD+0x25C). The menu text is
// linked into the draw list only at 3 (0x800C3A88) while the flight HUD keeps drawing through 1 and 2, so gating on !=0
// dropped the HUD to its centred position for the open and close animations. ROGUESQ_G1D_PAUSE_GATE_MASK = bit per state
// that holds the anchor off (default 8 = state 3; 14 = s6721 any non-zero). The dim overlay still follows any non-zero.
static std::atomic<int> g_rs64_g1d_paused{0};
extern "C" void rs64_g1d_pause_mark(int v) {
    static const bool lg = [] { const char *e = std::getenv("ROGUESQ_G1D_PAUSE_LOG"); return e && *e && *e != '0'; }();
    if (lg && v != g_rs64_g1d_paused.load(std::memory_order_relaxed)) { fprintf(stderr, "[pause-state] swap=%d v=%d\n", g_rs64_swap_n.load(std::memory_order_relaxed), v); fflush(stderr); }
    g_rs64_g1d_paused.store(v, std::memory_order_relaxed);
}
static int rs64_g1d_pause_any(void) {
    static const bool old = [] { const char *e = std::getenv("ROGUESQ_G1D_PAUSE_ANCHOR"); return e && *e == '1'; }();
    return !old && g_rs64_g1d_paused.load(std::memory_order_relaxed) != 0;
}
extern "C" int rs64_g1d_pause_live(void) {
    static const int mask = [] { const char *e = std::getenv("ROGUESQ_G1D_PAUSE_GATE_MASK"); return e && *e ? atoi(e) : 8; }();
    return rs64_g1d_pause_any() && ((mask >> (g_rs64_g1d_paused.load(std::memory_order_relaxed) & 7)) & 1);
}
// s6725: the s6156 HUD anchor is calibrated for the flight HUD, but the hangar level select draws its title, preview and
// level name through the same emitter list (vp 0x800CDC80), so at 21:9 they moved -256 px and the name clipped at x=0.
// Anchor only while renderRadarMinimap ran within the last 8 swaps (flight); ROGUESQ_G1D_HUD_ANYWHERE=1 = old.
extern "C" int rs64_g1d_hud_flight(void) {
    static const bool old = [] { const char *e = std::getenv("ROGUESQ_G1D_HUD_ANYWHERE"); return e && *e == '1'; }();
    return old || rs64_radar_recent(g_rs64_swap_n.load(std::memory_order_relaxed));
}

// s6158 G1d: region scan. ROGUESQ_LOG_REGION="x0,x1,y0,y1" (raw RDP px) logs every
// triangle (bbox centre in region) and texrect (ul in region) with its range and
// offset; ROGUESQ_SHIFT_REGION=<dx px> additionally shifts matching tris/rects in x
// (positive control: the matched element must visibly move in the fbdump).
static void rs64_region_scan(uint32_t lo, uint32_t hi, int fused = 0) {
    static double R[4]; static double dxs = 0; static int shiftOn = 0;
    static const bool on = [] {
        const char *e = std::getenv("ROGUESQ_LOG_REGION");
        if (!e || !*e || sscanf(e, "%lf,%lf,%lf,%lf", &R[0], &R[1], &R[2], &R[3]) != 4) return false;
        const char *d = std::getenv("ROGUESQ_SHIFT_REGION");
        if (d && *d) { dxs = atof(d); shiftOn = 1; }
        return true; }();
    if (g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    if (!on) { if (fused) rs64_spike_scan(lo, hi); return; }  // s7635: fused caller still owes the spike walk
    static uint32_t s_logged = 0, s_hits = 0;
    static const uint32_t s_cap = [] { const char *e = std::getenv("ROGUESQ_REGION_LOG_CAP"); return e && *e ? (uint32_t)atoi(e) : 400u; }();  // s6695
    const int sw = g_rs64_swap_n.load(std::memory_order_relaxed);
    // s6695: the box is a fixed screen region, so the shift also moved level-select scenery (the room seen
    // through the doorway, leaving a hole) and title texrects. Shift only while the flight radar is drawn;
    // =0 on ROGUESQ_SHIFT_REGION_ANYWHERE restores the ungated s6158 behaviour. Logging is unchanged.
    static const bool anywhere = [] { const char *e = std::getenv("ROGUESQ_SHIFT_REGION_ANYWHERE"); return e && *e && *e != '0'; }();
    // s6731: the radar is still stamped under the pause menu, so at 16:9/21:9 the pause Rebel logo's upper-right arm
    // tip (tris centred in the region) was torn off and drawn +dx px away. Skip the shift while the pause byte is set,
    // like the s6721 HUD anchor; ROGUESQ_G1D_PAUSE_ANCHOR=1 restores both old behaviours.
    // s6733: the byte clears one swap before the pause UI stops drawing: the first unpaused swap of the abort fly-out
    // still carries the pause texrects (x 633..745), which moved +256 for that frame. Hold the shift off for
    // ROGUESQ_G1D_PAUSE_HOLDOFF swaps (default 1) after the last paused swap; =0 restores s6731.
    static const int holdoff = [] { const char *e = std::getenv("ROGUESQ_G1D_PAUSE_HOLDOFF"); return e && *e ? atoi(e) : 1; }();
    static int s_paused_sw = -1000;
    bool paused = rs64_g1d_pause_live() != 0;
    if (paused) s_paused_sw = sw;
    else if (sw - s_paused_sw <= holdoff) paused = true;
    // s6861: the swap the pause byte goes to 1 fails the VI-epoch half of rs64_radar_recent for one swap, though the anchor built
    // that frame's ring at the edge and the disc is drawn: a one-frame disc left at the centre. Swap distance alone suffices here.
    static int s_any_sw = -1000;
    if (rs64_g1d_pause_any()) s_any_sw = sw;
    const bool trans = sw - s_any_sw <= holdoff;
    const bool radar = anywhere || ((rs64_radar_recent(sw) || (trans && sw - g_rs64_radar_swap.load(std::memory_order_relaxed) <= 8)) && !paused);
    static int s_radar_prev = -1;
    if (shiftOn && (int)radar != s_radar_prev) { fprintf(stderr, "[region-gate] swap=%d radar=%d paused=%d shift=%s\n", sw, (int)radar, (int)paused, radar ? "on" : "off"); fflush(stderr); s_radar_prev = (int)radar; }
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & kSubmitRamMask), 4); return v; };
    auto wr = [&](uint32_t a, uint32_t v) { memcpy(g_rdram_for_submit + (a & kSubmitRamMask), &v, 4); };
    auto sx14 = [](uint32_t v) { return (double)(((int32_t)(v << 18)) >> 18) / 4.0; };
    // s6852: the box is a fixed screen rectangle, so in flight it also caught world geometry: lvl17 21:9 bin (SHIFT 0,
    // tools/g1d_regiontex.py --ring 792DA0, 1268 flight VIs) had 8876 disc tris (texture 7965C0, 39..85 commands before
    // the ring) and ~49k world tris + 26 particle sprites (737640, also drawn at x 110..998) in the box, all moved +256.
    // A flight frame is Z clear (SETCIMG = z image) -> sky (z_cmp off) -> world (z_cmp on) -> HUD (z_cmp off: disc, ring).
    // Shift only z_cmp-off prims once the frame has drawn a z_cmp-on prim; the Z clear resets it. State persists across
    // submit ranges (submission order). Offline replay of this rule on that bin: disc 9680 shifted / 464 kept (the 464 =
    // the 58 VIs whose ring is also drawn un-anchored, so ring and disc stay aligned), 737640 and world tris 0 shifted.
    // (A first cut keyed on a mid-frame Z clear: only frame 1 of flight has one, disc 0 shifted at runtime.)
    // ROGUESQ_G1D_REGION_ZGATE=0 = old box-only selection.
    static const bool zgate = [] { const char *e = std::getenv("ROGUESQ_G1D_REGION_ZGATE"); return !(e && *e == '0'); }();
    static const bool zdiag = [] { const char *e = std::getenv("ROGUESQ_G1D_SPRITE_DIAG"); return e && *e && *e != '0'; }();
    static uint32_t s_zimg = 0xFFFFFFFFu, s_timg = 0; static bool s_zcmp = false, s_world = false;
    static std::map<std::pair<uint32_t, int>, std::array<uint32_t, 2>> s_zstat;  // (timg, tri=1/rect=0) -> {shifted, kept}
    static int s_zstat_sw = -1;
    // s6855: every texrect the gate selected in flight is a world-anchored marker crossing the box, not a radar element:
    // lvl17 R78E080 (s6854), lvl9 R79B270 drawn outside the box in 3933/3950 VIs at x 412..612, R79B070 3948/3950 (s6855
    // offline replay, tools/g1d_zoffobj.py); lvl1 16:9 none. Shifting one makes it jump 256 px. The radar disc and its
    // blips (T7A3FB0) are triangles. ROGUESQ_G1D_REGION_TEXRECT=1 = shift in-box texrects again (s6854 behaviour).
    static const bool rtex = [] { const char *e = std::getenv("ROGUESQ_G1D_REGION_TEXRECT"); return e && *e == '1'; }();
    // s6861: while the pause menu opens and closes the frame is a frozen backdrop of small z_cmp-off tiles, then the HUD, then the
    // logo (z_cmp on, with z_cmp-off tris of its own), so the latch misses the disc and it stayed centred under the anchored ring,
    // and dropping the latch moved backdrop tiles and tore the logo arm (first cut, scratch/s6861/fix_sheet.png). There, shift only
    // z_cmp-off tris whose texture the gate selected in flight: the disc and blips.
    static uint32_t s_disc_tex[16]; static int s_disc_n = 0;
    auto disc_tex = [&]() { for (uint32_t t : s_disc_tex) if (t == s_timg) return true; return false; };
    auto zok = [&](bool tri) { const bool sel = !s_zcmp && (trans ? disc_tex() : s_world);
        if (tri && sel && !trans && !disc_tex()) s_disc_tex[s_disc_n++ & 15] = s_timg;
        const bool ok = (!zgate || sel) && (tri || rtex || !zgate);
        if (zdiag && radar && shiftOn) s_zstat[{s_timg, tri ? 1 : 0}][ok ? 0 : 1]++; return ok; };
    if (zdiag && shiftOn && sw - s_zstat_sw >= 600 && !s_zstat.empty()) {
        s_zstat_sw = sw; std::string o;
        for (auto &kv : s_zstat) { char b[64]; snprintf(b, sizeof b, " %s%06X=%u/%u", kv.first.second ? "T" : "R", kv.first.first, kv.second[0], kv.second[1]); o += b; }
        fprintf(stderr, "[region-zgate] swap=%d zgate=%d shifted/kept:%s\n", sw, (int)zgate, o.c_str()); fflush(stderr); s_zstat.clear();
    }
    auto body = [&](uint32_t a) -> uint32_t {  // s7635: one command; returns its length, 0 = stop
        const uint32_t w0 = rd(a), w1 = rd(a + 4);
        const uint32_t op = (w0 >> 24) & 0x3F;
        if (op == 0x2F) s_zcmp = (w1 >> 4) & 1;
        else if (op == 0x3D) s_timg = w1 & 0xFFFFFFu;
        else if (op == 0x3E) s_zimg = w1 & 0xFFFFFFu;
        else if (op == 0x3F) {
            // s6854: many lvl17 frames have no Z clear (SETZIMG, SETCIMG colour, sky...), so the latch carried over from the
            // previous frame and that frame's sky (7AC2E0/7A81E0/7ABAC0, z_cmp off) in the box was shifted: the s6852 residual.
            // A SETCIMG naming a different colour image than the last one (buffer flip) also starts a frame.
            // Offline replay (tools/g1d_zoffobj.py --rule cflip): lvl17 disc 10032 unchanged, sky 503 -> 0; lvl1 16:9 disc
            // unchanged. ROGUESQ_G1D_REGION_CFLIP=0 = s6852 Z-clear-only reset.
            static const bool cflip = [] { const char *e = std::getenv("ROGUESQ_G1D_REGION_CFLIP"); return !(e && *e == '0'); }();
            static uint32_t s_clast = 0xFFFFFFFFu;
            const uint32_t ci = w1 & 0xFFFFFFu;
            if (ci == s_zimg) s_world = false;  // Z clear = frame start
            else { if (cflip && ci != s_clast) s_world = false; s_clast = ci; }
        }
        if (s_zcmp && ((op >= 0x08 && op <= 0x0F) || op == 0x24 || op == 0x25)) s_world = true;
        if (op == 0x24 || op == 0x25) {
            if (a + 16 > hi) return 0;
            const double xh = ((w1 >> 12) & 0xFFF) / 4.0, yh = (w1 & 0xFFF) / 4.0;
            const double xl = ((w0 >> 12) & 0xFFF) / 4.0, yl = (w0 & 0xFFF) / 4.0;
            if (xl >= R[0] && xl <= R[1] && yl >= R[2] && yl <= R[3]) {
                s_hits++;
                if (s_logged++ < s_cap) { fprintf(stderr, "[region] swap=%d TEXRECT off=%06X ul=(%.1f,%.1f) lr=(%.1f,%.1f) range=%06X..%06X\n", sw, a, xh, yh, xl, yl, lo, hi); fflush(stderr); }
                // s6851: the shift ran after rs64_g1d_rect_wrap and masked the 12-bit x fields, so a rect it pushed past 1024 px
                // (lvl17 radar-region texrect ul.x 760 -> 1016, lr.x 776 -> 1032 = 8.5) wrapped lr < ul and RT64 dropped it.
                // Saturate at 0xFFF instead: a straddling rect is clipped at the edge (same texture origin, ul unchanged),
                // one pushed wholly past the field draws nothing. ROGUESQ_G1D_SHIFT_SAT=0 = old masking.
                static const bool sat = [] { const char *e = std::getenv("ROGUESQ_G1D_SHIFT_SAT"); return !(e && *e == '0'); }();
                auto sx = [&](uint32_t w) { const int32_t v = (int32_t)((w >> 12) & 0xFFF) + (int32_t)(dxs * 4);
                    const uint32_t n = sat ? (uint32_t)std::clamp(v, 0, 0xFFF) : ((uint32_t)v & 0xFFF); return (w & ~0xFFF000u) | (n << 12); };
                if (shiftOn && radar && zok(false)) { wr(a, sx(w0)); wr(a + 4, sx(w1)); }
            }
            return 16;
        }
        if (op < 0x08 || op > 0x0F) return 8;
        const uint32_t len = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
        if (a + 32 > hi) return 0;
        const double yl = sx14(w0 & 0x3FFF), ym = sx14((w1 >> 16) & 0x3FFF), yh = sx14(w1 & 0x3FFF);
        auto fx = [&](uint32_t o) { return (double)(int32_t)rd(a + o) / 65536.0; };
        const double xl = fx(8), dl = fx(12), xh = fx(16), dh = fx(20), xm = fx(24), dm = fx(28);
        const double xs[5] = {xh, xm + dm * (ym - yh), xl, xl + dl * (yl - ym), xh + dh * (yl - yh)};
        double mn = 1e9, mx = -1e9; for (double x : xs) { mn = x < mn ? x : mn; mx = x > mx ? x : mx; }
        const double cx = (mn + mx) / 2, cy = (yh + yl) / 2;
        // s6852: one disc tri per flight frame (lvl17: 1210/1268 VIs) has its bbox centre 20..30 px left of the box edge and was
        // left behind 256 px from the radar (the grey wedge at x~687 at 21:9, both s6852 arms). With the Z gate keeping world
        // geometry out, the tri test reaches ROGUESQ_G1D_REGION_TRI_PAD px further left (default 32 at a 141 px box, scaled);
        // in the same bin only ~5 other HUD-segment tris fall in the added strip.
        static const double tpad = [] { const char *e = std::getenv("ROGUESQ_G1D_REGION_TRI_PAD"); return e && *e ? atof(e) : 32.0; }() * (R[1] - R[0]) / 141.0;
        const double tx0 = zgate ? R[0] - tpad : R[0];
        if (cx >= tx0 && cx <= R[1] && cy >= R[2] && cy <= R[3] && (mx - mn) <= 130.0 && (yl - yh) <= 130.0) {  // size cap: skip sky/terrain tris
            s_hits++;
            if (s_logged++ < s_cap) { fprintf(stderr, "[region] swap=%d TRI off=%06X op=%02X x=%.1f..%.1f y=%.1f..%.1f range=%06X..%06X\n", sw, a, op, mn, mx, yh, yl, lo, hi); fflush(stderr); }
            if (shiftOn && radar && zok(true)) { const int32_t d = (int32_t)(dxs * 65536.0); wr(a + 8, rd(a + 8) + d); wr(a + 16, rd(a + 16) + d); wr(a + 24, rd(a + 24) + d); }
        }
        return len;
    };
    if (!fused) { for (uint32_t a = lo & ~3u; a + 8 <= hi;) { const uint32_t m = body(a); if (!m) break; a += m; } return; }
    // s7635 bridge-walker-fusion: one walk runs the spike body then this body on each command (ROGUESQ_S7634_FUSE, default 1).
    // Same bytes as the old two passes because the two bodies only meet on the current command: this body reads and writes
    // only command a's own words (texrect x fields, tri x words at +8/+16/+24, never a 0x2E or 0x2F), and the spike body reads
    // command a, looks ahead only at op bytes and 0x2F words (skyish), and writes command a or, late, the w1 of an earlier
    // 0x2E (DD_SKYZ put), which this body ignores. fused=2 (=chk) checks the late-write half at runtime: it shadows each
    // command's words right after this body ran and compares them with the range once the walk ends; any differing word is a
    // spike write that landed after this body passed it, binned by the command's op (inert: ops this body does not read).
    // fused=3 (=inj) also flips one shadow word every 4096th check: the comparator's positive control.
    if (fused == 1) { rs64_spike_scan(lo, hi, [](void *c, uint32_t a) { return (*static_cast<decltype(body) *>(c))(a); }, &body); return; }
    static std::vector<uint32_t> s_shw; static std::vector<uint8_t> s_sop;
    static uint64_t s_runs = 0, s_cmds = 0, s_late_live = 0, s_late_inert = 0, s_inj = 0;
    const uint32_t base = lo & ~3u, nw = (hi - base + 3u) / 4u;
    s_shw.resize(nw); s_sop.assign(nw, 0xFF);
    for (uint32_t i = 0; i < nw; i++) s_shw[i] = rd(base + 4 * i);
    struct Ck { decltype(body) *b; decltype(rd) *r; uint32_t base, hi; uint64_t *cmds; } ck = {&body, &rd, base, hi, &s_cmds};
    rs64_spike_scan(lo, hi, [](void *c, uint32_t a) {
        Ck &k = *static_cast<Ck *>(c); const uint32_t r = (*k.b)(a), op = ((*k.r)(a) >> 24) & 0x3F; (*k.cmds)++;
        const uint32_t span = (r && a + r <= k.hi) ? r : k.hi - a;
        for (uint32_t o = 0; o < span; o += 4) { const uint32_t i = (a + o - k.base) / 4u; if (i < s_shw.size()) { s_shw[i] = (*k.r)(a + o); s_sop[i] = (uint8_t)op; } }
        return r; }, &ck);
    s_runs++;
    static uint64_t s_inj_seen = 0; static uint32_t s_nlog = 0;
    const bool inj = fused == 3 && (s_runs & 4095u) == 0 && nw > 1;
    if (inj) { s_shw[1] ^= 1u; s_inj++; }
    for (uint32_t i = 0; i < nw; i++) if (s_shw[i] != rd(base + 4 * i)) {
        if (inj && i == 1 && (s_shw[1] ^ 1u) == rd(base + 4)) { s_inj_seen++; continue; }  // the injected flip, nothing else on that word
        const uint32_t op = s_sop[i];
        const bool live = op == 0x24 || op == 0x25 || op == 0x2F || op == 0x3D || op == 0x3E || op == 0x3F || (op >= 0x08 && op <= 0x0F);
        (live ? s_late_live : s_late_inert)++;
        if (s_nlog++ < 32) { fprintf(stderr, "[s7635-late] run=%llu word=%u op=%02X live=%d shadow=%08X now=%08X\n", (unsigned long long)s_runs, i, op, (int)live, s_shw[i], rd(base + 4 * i)); fflush(stderr); }
    }
    if ((s_runs & 4095u) == 0) { fprintf(stderr, "[s7635-chk] runs=%llu cmds=%llu late_live=%llu late_inert=%llu injected=%llu inj_seen=%llu\n", (unsigned long long)s_runs,
        (unsigned long long)s_cmds, (unsigned long long)s_late_live, (unsigned long long)s_late_inert, (unsigned long long)s_inj, (unsigned long long)s_inj_seen); fflush(stderr); }
}

// s6720 G1d: ROGUESQ_LOG_G1D_RECT=1 logs, per swap, the colour-image width, scissor and the x extents of texrects
// (with first rect + dsdx) and triangles in submitted RDP ranges. Read-only. Cap ROGUESQ_G1D_RECT_CAP lines (400).
extern "C" int rs64_g1d_vi_epoch;
static void rs64_g1d_rect_scan(uint32_t lo, uint32_t hi) {
    static const bool on = [] { const char *e = std::getenv("ROGUESQ_LOG_G1D_RECT"); return e && *e && *e != '0'; }();
    if (!on || g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    static const int cap = [] { const char *e = std::getenv("ROGUESQ_G1D_RECT_CAP"); return e && *e ? atoi(e) : 400; }();
    static int s_lines = 0, s_swap = -1;
    static uint32_t s_cw, s_cimg, s_nr, s_nt, s_sc0, s_sc1, s_first[4];
    static double s_rx0, s_rx1, s_tx0, s_tx1;
    static uint32_t s_om0, s_om1, s_cc0, s_cc1, s_prim, s_env, s_blend, s_fillc;
    static int s_plines = 0;
    static const int pcap = [] { const char *e = std::getenv("ROGUESQ_G1D_PAUSE_CAP"); return e && *e ? atoi(e) : 600; }();
    const int sw = g_rs64_swap_n.load(std::memory_order_relaxed);
    const bool paused = g_rs64_g1d_paused.load(std::memory_order_relaxed) != 0;
    struct Grp { uint32_t n = 0; double x0, x1, y0, y1; };
    static std::map<std::array<uint32_t, 7>, Grp> s_grp;
    static std::set<std::array<uint32_t, 7>> s_flight;
    static bool s_swap_paused = false;
    if (sw != s_swap) {
        for (auto &kv : s_grp) {
            if (!s_swap_paused) { s_flight.insert(kv.first); continue; }
            if (s_flight.count(kv.first) || s_plines >= pcap) continue;
            const auto &k = kv.first; const auto &g = kv.second; s_plines++;
            fprintf(stderr, "[g1d-pause] swap=%d GRP op=%02X n=%u x=%.1f..%.1f y=%.1f..%.1f om=%08X,%08X cc=%08X,%08X prim=%08X env=%08X cw=%u\n",
                    s_swap, k[6], g.n, g.x0, g.x1, g.y0, g.y1, k[0], k[1], k[2], k[3], k[4], k[5], s_cw);
        }
        s_grp.clear(); s_swap_paused = paused;
    }
    if (sw != s_swap) {
        if (s_swap >= 0 && (s_nr || s_nt) && s_lines < cap) {
            s_lines++;
            fprintf(stderr, "[g1d-rect] swap=%d cimg=%06X cw=%u sc=%08X,%08X rects=%u x=%.1f..%.1f first=%08X %08X %08X %08X tris=%u x=%.1f..%.1f\n",
                    s_swap, s_cimg, s_cw, s_sc0, s_sc1, s_nr, s_rx0, s_rx1, s_first[0], s_first[1], s_first[2], s_first[3], s_nt, s_tx0, s_tx1);
        }
        s_swap = sw; s_nr = s_nt = 0; s_rx0 = s_tx0 = 1e9; s_rx1 = s_tx1 = -1e9;
    }
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & kSubmitRamMask), 4); return v; };
    // s6728: ROGUESQ_LOG_G1D_RECT=2 + ROGUESQ_G1D_RECT_EPOCH=<e>: for the first ROGUESQ_G1D_RECT_SWAPS (12) swaps of VI
    // epoch e, log EVERY texrect with its y extent and the SETTIMG / LOADBLOCK|LOADTILE / SETTILE / other-mode / combine
    // it draws under, so one rect can be followed across aspects. Own cap ROGUESQ_G1D_RECT2_CAP (4000).
    static const int r2_ep = [] { const char *e = std::getenv("ROGUESQ_LOG_G1D_RECT"); const char *p = std::getenv("ROGUESQ_G1D_RECT_EPOCH");
                                  return (e && *e == '2' && p && *p) ? atoi(p) : -1; }();
    static const int r2_swaps = [] { const char *e = std::getenv("ROGUESQ_G1D_RECT_SWAPS"); return e && *e ? atoi(e) : 12; }();
    static const int r2_cap = [] { const char *e = std::getenv("ROGUESQ_G1D_RECT2_CAP"); return e && *e ? atoi(e) : 4000; }();
    static int r2_first = -1, r2_lines = 0, r2_idx = 0, r2_sw = -1;
    static uint32_t r2_timg, r2_load0, r2_load1, r2_tile0, r2_tile1, r2_tsz0, r2_tsz1;
    const bool r2 = r2_ep >= 0 && __atomic_load_n(&rs64_g1d_vi_epoch, __ATOMIC_RELAXED) == r2_ep;
    if (r2 && r2_first < 0) r2_first = sw;
    if (r2 && sw != r2_sw) { r2_sw = sw; r2_idx = 0; }
    const bool r2_log = r2 && sw - r2_first < r2_swaps;
    for (uint32_t a = lo & ~3u; a + 8 <= hi;) {
        const uint32_t w0 = rd(a), w1 = rd(a + 4), op = (w0 >> 24) & 0x3F;
        if (op == 0x3D) r2_timg = (w1 & 0xFFFFFFu) | (((w0 >> 19) & 0x1Fu) << 24);
        if (op == 0x33 || op == 0x34) { r2_load0 = w0; r2_load1 = w1; }
        if (op == 0x35 && ((w1 >> 24) & 7u) == 0u) { r2_tile0 = w0; r2_tile1 = w1; }
        if (op == 0x32 && ((w1 >> 24) & 7u) == 0u) { r2_tsz0 = w0; r2_tsz1 = w1; }
        if (r2_log && (op == 0x24 || op == 0x25) && r2_lines < r2_cap) {
            r2_lines++;
            // texel census of the 4 KB LOADBLOCK source as guest RDRAM holds it at submit: nonzero halfwords, alpha-bit set,
            // and an additive sum, so "rect issued but texture not there yet" splits from "texture there, renderer drops it"
            uint32_t tnz = 0, tal = 0, tsum = 0;
            for (uint32_t o = 0; o < 0x1000u; o += 2) {
                const uint32_t ta = (r2_timg & 0xFFFFFFu) + o; const uint16_t h = (uint16_t)((rd(ta & ~3u) >> ((ta & 2) ? 0 : 16)) & 0xFFFFu);
                tnz += h != 0; tal += h & 1u; tsum += h;
            }
            fprintf(stderr, "[g1d-rect2] tex nz=%u alpha=%u sum=%08X\n", tnz, tal, tsum);
            fprintf(stderr, "[g1d-rect2] ep=%d swap=%d+%d i=%d x=%.2f..%.2f y=%.2f..%.2f st=%08X dd=%08X timg=%02X:%06X load=%08X,%08X tile=%08X,%08X tsz=%08X,%08X om=%08X,%08X cc=%08X,%08X cw=%u sc=%08X,%08X\n",
                    r2_ep, sw, sw - r2_first, r2_idx, ((w1 >> 12) & 0xFFF) / 4.0, ((w0 >> 12) & 0xFFF) / 4.0, (w1 & 0xFFF) / 4.0, (w0 & 0xFFF) / 4.0,
                    a + 16 <= hi ? rd(a + 8) : 0, a + 16 <= hi ? rd(a + 12) : 0, r2_timg >> 24, r2_timg & 0xFFFFFF, r2_load0, r2_load1,
                    r2_tile0, r2_tile1, r2_tsz0, r2_tsz1, s_om0, s_om1, s_cc0, s_cc1, s_cw, s_sc0, s_sc1);
        }
        if (r2_log && (op == 0x24 || op == 0x25)) r2_idx++;
        // s6728: every other draw / target change of the same window (fill rects, triangle bboxes, SETCIMG, SETSCISSOR)
        if (r2_log && r2_lines < r2_cap && (op == 0x36 || op == 0x3F || op == 0x2D || (op >= 0x08 && op <= 0x0F && a + 32 <= hi))) {
            r2_lines++;
            if (op >= 0x08 && op <= 0x0F) {
                auto sx14 = [](uint32_t v) { return (double)(((int32_t)(v << 18)) >> 18) / 4.0; };
                double t0 = 1e9, t1 = -1e9;
                for (uint32_t o : {8u, 16u, 24u}) { const double x = (double)(int32_t)rd(a + o) / 65536.0; t0 = std::min(t0, x); t1 = std::max(t1, x); }
                fprintf(stderr, "[g1d-rect2] ep=%d swap=%d+%d TRI op=%02X x~%.1f..%.1f y=%.1f..%.1f om=%08X,%08X cc=%08X,%08X timg=%02X:%06X cw=%u\n", r2_ep, sw, sw - r2_first, op,
                        t0, t1, sx14(rd(a + 4) & 0x3FFF), sx14(w0 & 0x3FFF), s_om0, s_om1, s_cc0, s_cc1, r2_timg >> 24, r2_timg & 0xFFFFFF, s_cw);
            } else {
                fprintf(stderr, "[g1d-rect2] ep=%d swap=%d+%d CMD op=%02X w0=%08X w1=%08X om=%08X,%08X\n", r2_ep, sw, sw - r2_first, op, w0, w1, s_om0, s_om1);
            }
        }
        if (op == 0x24 || op == 0x25) {
            const double xl = ((w0 >> 12) & 0xFFF) / 4.0, xh = ((w1 >> 12) & 0xFFF) / 4.0;
            if (s_nr == 0) { s_first[0] = w0; s_first[1] = w1; s_first[2] = a + 16 <= hi ? rd(a + 8) : 0; s_first[3] = a + 16 <= hi ? rd(a + 12) : 0; }
            s_nr++; s_rx0 = std::min(s_rx0, xh); s_rx1 = std::max(s_rx1, xl);
            a += 16; continue;
        }
        if (op == 0x3F) { s_cw = (w0 & 0x3FFu) + 1u; s_cimg = w1 & 0xFFFFFF; a += 8; continue; }
        if (op == 0x2D) { s_sc0 = w0; s_sc1 = w1; a += 8; continue; }
        // s6722: while the pause byte is live, log fill rects and every big (>=150 px wide or tall) tri with the RDP
        // state it was drawn under (other mode, combine, prim/env/blend colour, scissor), so the dim overlay is named.
        if (op == 0x2F) { s_om0 = w0; s_om1 = w1; }
        if (op == 0x3C) { s_cc0 = w0; s_cc1 = w1; }
        if (op == 0x3A) s_prim = w1;
        if (op == 0x3B) s_env = w1;
        if (op == 0x39) s_blend = w1;
        if (op == 0x37) s_fillc = w1;
        if (op == 0x36 && paused && s_plines < pcap) {
            s_plines++;
            fprintf(stderr, "[g1d-pause] swap=%d FILL x=%.1f..%.1f y=%.1f..%.1f fill=%08X om=%08X,%08X sc=%08X,%08X cw=%u\n", sw,
                    ((w1 >> 12) & 0xFFF) / 4.0, ((w0 >> 12) & 0xFFF) / 4.0, (w1 & 0xFFF) / 4.0, (w0 & 0xFFF) / 4.0, s_fillc, s_om0, s_om1, s_sc0, s_sc1, s_cw);
        }
        if (op < 0x08 || op > 0x0F) { a += 8; continue; }
        const uint32_t len = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
        if (a + 32 > hi) break;
        double t0 = 1e9, t1 = -1e9;
        for (uint32_t o : {8u, 16u, 24u}) { const double x = (double)(int32_t)rd(a + o) / 65536.0; s_tx0 = std::min(s_tx0, x); s_tx1 = std::max(s_tx1, x); t0 = std::min(t0, x); t1 = std::max(t1, x); }
        {
            auto sx14 = [](uint32_t v) { return (double)(((int32_t)(v << 18)) >> 18) / 4.0; };
            const double yh = sx14(rd(a + 4) & 0x3FFF), yl = sx14(w0 & 0x3FFF);
            auto &g = s_grp[std::array<uint32_t, 7>{s_om0, s_om1, s_cc0, s_cc1, s_prim, s_env, op}];
            if (g.n++ == 0) { g.x0 = t0; g.x1 = t1; g.y0 = yh; g.y1 = yl; }
            g.x0 = std::min(g.x0, t0); g.x1 = std::max(g.x1, t1); g.y0 = std::min(g.y0, yh); g.y1 = std::max(g.y1, yl);
        }
        s_nt++;
        a += len;
    }
}

// s6720 G1d: while the widened title mode is live (rs64_g1d_title_vi, set by the osViSetMode hook), the title still
// covers only the centre 512 columns of its fbw-wide colour image; the pillar columns are never drawn and showed stale
// heap bytes (white / noise / smeared strips). Zero each new >512-wide colour image once, before RT64 sees the task.
extern "C" int rs64_g1d_title_vi;
extern "C" int rs64_g1d_pfm_h; extern "C" int rs64_s6926_on(void);
// s6723 G1d debrief (title_vi == 2, ROGUESQ_LOG_G1D_RECT=1): log per colour image the scissor/cimg/fill commands and
// texrect x extent. s6723 showed no fill rects at all: ~510 backdrop texrects x 256..768 + ~212 tris, scissor full width.
static void rs64_g1d_debrief(uint32_t lo, uint32_t hi) {
    static const bool on = [] { const char *e = std::getenv("ROGUESQ_LOG_G1D_RECT"); return e && *e == '1'; }();
    if (!on || g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    static int s_lines = 0;
    if (s_lines > 400) return;
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & kSubmitRamMask), 4); return v; };
    double tx0 = 1e9, tx1 = -1e9; uint32_t ntr = 0, ntx = 0;
    for (uint32_t a = lo & ~3u, step = 8; a + 8 <= hi; a += step) {
        const uint32_t w0 = rd(a), w1 = rd(a + 4), op = (w0 >> 24) & 0x3F;
        step = (op == 0x24 || op == 0x25) ? 16u : (op >= 0x08 && op <= 0x0F) ? 32u + ((op & 4) ? 64u : 0u) + ((op & 2) ? 64u : 0u) + ((op & 1) ? 16u : 0u) : 8u;
        if (op == 0x24 || op == 0x25) { ntx++; tx0 = std::min(tx0, ((w1 >> 12) & 0xFFF) / 4.0); tx1 = std::max(tx1, ((w0 >> 12) & 0xFFF) / 4.0); continue; }
        if (op >= 0x08 && op <= 0x0F) { ntr++; continue; }
        if (op == 0x3F || op == 0x36 || op == 0x37 || op == 0x2D) {
            if (s_lines++ < 3000) fprintf(stderr, "[g1d-debrief] sw=%d off=%06X op=%02X w=%08X %08X\n", g_rs64_swap_n.load(std::memory_order_relaxed), a, op, w0, w1);
        }
    }
    if (s_lines < 400) { s_lines++; fprintf(stderr, "[g1d-debrief] sw=%d range=%06X..%06X tris=%u texrects=%u tx=%.1f..%.1f\n", g_rs64_swap_n.load(std::memory_order_relaxed), lo, hi, ntr, ntx, tx0, tx1); }
}
static void rs64_g1d_title_clear(uint32_t lo, uint32_t hi) {
    static uint32_t s_done[4]; static int s_n = 0, s_lines = 0;
    if (!rs64_g1d_title_vi) { s_n = 0; return; }
    if (rs64_g1d_title_vi == 2) { rs64_g1d_debrief(lo, hi); return; }
    if (g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & kSubmitRamMask), 4); return v; };
    // The menu bar slides in from x<256 (rects x 172->256): in this single-buffered, never-cleared image its trail
    // stayed in the left pillar. A full-width scissor is clamped to the centre 512 columns (the retail visible area).
    static uint32_t s_cw = 0;
    for (uint32_t a = lo & ~3u, step = 8; a + 8 <= hi; a += step) {
        const uint32_t w0 = rd(a), op = (w0 >> 24) & 0x3F;
        // Walk command boundaries (texrect 16 B, triangles 32..176 B) so payload words are never parsed as commands.
        step = (op == 0x24 || op == 0x25) ? 16u : (op >= 0x08 && op <= 0x0F) ? 32u + ((op & 4) ? 64u : 0u) + ((op & 2) ? 64u : 0u) + ((op & 1) ? 16u : 0u) : 8u;
        if (op == 0x2D && s_cw > 512u) {
            const uint32_t w1 = rd(a + 4), ulx = (w0 >> 12) & 0xFFFu, lrx = (w1 >> 12) & 0xFFFu;
            // s6929: 2 px tolerance missed the game's full scissor at fbw 652 (lrx 649), leaving the menu slide trail in the pillars. ROGUESQ_G1D_SCISSOR_TOL=8 = old.
            static const uint32_t tol = [] { const char* e = std::getenv("ROGUESQ_G1D_SCISSOR_TOL"); return e ? (uint32_t)std::atoi(e) : 32u; }();
            if (ulx == 0 && lrx + tol >= s_cw * 4u) {
                const uint32_t x0 = (s_cw - 512u) / 2u * 4u, x1 = (s_cw + 512u) / 2u * 4u;
                const uint32_t n0 = (w0 & ~(0xFFFu << 12)) | (x0 << 12), n1 = (w1 & ~(0xFFFu << 12)) | (x1 << 12);
                memcpy(g_rdram_for_submit + (a & kSubmitRamMask), &n0, 4); memcpy(g_rdram_for_submit + ((a + 4) & kSubmitRamMask), &n1, 4);
            }
            continue;
        }
        if (op != 0x3F) continue;
        const uint32_t cw = (w0 & 0x3FFu) + 1u, ci = rd(a + 4) & 0xFFFFFFu, bytes = cw * (rs64_g1d_pfm_h == 300 && rs64_s6926_on() ? 300u : 448u) * 2u;  // s6926: 512x300 buffers sit closer together
        s_cw = ((w0 >> 19) & 3u) == 2u ? cw : 0u;
        if (cw <= 512u || ((w0 >> 19) & 3u) != 2u || (ci & 0x3Fu) || ci + bytes > kSubmitRamEnd) continue;  // 16-bit, aligned, wide only
        bool seen = false; for (int i = 0; i < s_n; i++) seen |= (s_done[i] == ci);
        if (seen || s_n >= 4) continue;
        s_done[s_n++] = ci;
        memset(g_rdram_for_submit + ci, 0, bytes);
        if (s_lines++ < 16) fprintf(stderr, "[g1d-title-clear] cimg=%06X cw=%u bytes=%u\n", ci, cw, bytes);
    }
}

// s6844 G1d: RDP texrect / fill-rect x coordinates are 12-bit 10.2 fields (max 1023.75). The abort-level wipe (a black
// texrect, prim 000000FF, ul.x sweeping right-to-left, lr.x = the colour-image width) carries lr.x = 1024 at 21:9 and
// 1024*4 = 0x1000 wraps to 0, so lr < ul and the rect draws nothing (4:3: lr.x 512 fits). Retail never exceeds 640 px,
// so on a >1023-wide image a rect with lr.x == 0 and ul.x > 0 is always a wrapped full-width right edge: clamp it to
// 0xFFF (1023.75 covers column 1023). ROGUESQ_G1D_RECT_WRAP=0 = old behaviour.
// s6851: ROGUESQ_G1D_SPRITE_DIAG=2 records every command address the walker steps on in the current submit range (and
// the words it read there, pre-rewrite), so the RT64-side bin writer (rt64_render_context.cpp, same thread, right after
// record_submit) can tell for each wrapped rect it is about to hand RT64 whether the walker skipped the range, stepped on
// the command with other words, or never landed on it (stepping desync). Diagnostic only.
extern "C" { int rs64_g1d_walk_diag = -1; uint32_t rs64_g1d_walk_lo = 0, rs64_g1d_walk_hi = 0; }
std::vector<uint32_t> g_rs64_g1d_walk;   // triples: addr, w0, w1 (+ cw packed in the high bits of nothing: see walk_cw)
std::vector<uint32_t> g_rs64_g1d_walk_cw;
// s7016 gfx-host-glue: the rect-wrap fix as a per-command step so rs64_g1d_pillar_scan can run it inside its own walk
// (one pass over the ~2 MB/frame dd4 stream instead of two). Order per command is unchanged: pillar reads the command,
// then this may rewrite that command's own w0; no command reads another's fields, so fused == two passes.
// ROGUESQ_GLUE_FUSE=0 = two passes; =chk fused then the old pass again, which must find nothing left to patch.
static uint32_t s_rw_cw = 0; static bool g_rw_fused = false, g_rw_walked = false; static int s_rw_lines = 0, s_rw_diag = 0; static uint64_t g_rw_patches = 0;
static inline void rs64_rw_cmd(uint32_t lo, uint32_t a, uint32_t w0, uint32_t op, bool diag) {
    auto rd = [&](uint32_t x) { uint32_t v; memcpy(&v, g_rdram_for_submit + (x & kSubmitRamMask), 4); return v; };
    uint32_t &s_cw = s_rw_cw; int &s_lines = s_rw_lines; int &s_diag = s_rw_diag;
    if (op == 0x3F) { s_cw = (w0 & 0x3FFu) + 1u; return; }
    if (diag && (op == 0x24 || op == 0x25) && s_cw <= 640u) {
        const uint32_t w1 = rd(a + 4);
        if (((w0 >> 12) & 0xFFFu) < ((w1 >> 12) & 0xFFFu) && (w0 & 0xFFFu) > (w1 & 0xFFFu) && s_diag++ < 40)
            fprintf(stderr, "[g1d-sprite-diag] wrap-at-cw sw=%d cw=%u w0=%08X w1=%08X lo=%06X a=%06X\n",
                g_rs64_swap_n.load(std::memory_order_relaxed), s_cw, w0, w1, lo, a);
    }
    if ((op != 0x24 && op != 0x25 && op != 0x36) || s_cw <= 640u) return;
    const uint32_t w1 = rd(a + 4), lrx = (w0 >> 12) & 0xFFFu, ulx = (w1 >> 12) & 0xFFFu;
    if ((w0 & 0xFFFu) <= (w1 & 0xFFFu)) return;
    if (s_cw > 1023u && lrx == 0) {
        // s6845: a texrect at ul.x 0 wraps too (the abort-wipe hold rect: x0 0, x1 = 4096 after the s6845 hudwipe fix);
        // ul == lr == 0 draws nothing either way, so only a fill rect still needs ul.x > 0.
        if (ulx == 0 && op == 0x36) return;
        const uint32_t n0 = w0 | (0xFFFu << 12);
        memcpy(g_rdram_for_submit + (a & kSubmitRamMask), &n0, 4); g_rw_patches++;
        if (s_lines++ < 24) fprintf(stderr, "[g1d-rect-wrap] sw=%d op=%02X cw=%u ul.x=%.2f lr.x 0 -> 1023.75 off=%06X\n",
            g_rs64_swap_n.load(std::memory_order_relaxed), op, s_cw, ulx / 4.0, a);
        return;
    }
    // s6850: the F5 TexrectGen billboard path (ucode overlay 0x2C, op 0xBD; docs/F5-OVL2C-TEXRECTGEN.md) clamps ul at
    // 0 but packs lr unclamped, so lr.x >= 1024 px wraps (lr < ul) and the sprite is dropped. Retail (640-wide image)
    // does the same, but only for sprites hanging >= 384 px past the right edge; on a wide image every sprite that
    // straddles the edge vanished (s6850 21:9 sweep: lvl2/3/4/5 smoke/explosion billboards). Keep retail's tolerance
    // relative to the image edge: a once-wrapped rect that starts on the image and overhangs it by < 384 px is
    // clipped at the edge instead; a larger overhang still drops, as in retail. ROGUESQ_G1D_SPRITE_WRAP=0 = old.
    static const bool spr = [] { const char *e = std::getenv("ROGUESQ_G1D_SPRITE_WRAP"); return !(e && *e == '0'); }();
    if (!spr || lrx >= ulx || ulx >= s_cw * 4u || lrx + 4096u >= (s_cw + 384u) * 4u) {
        if (diag && lrx < ulx && ulx < s_cw * 4u && s_diag++ < 40)
            fprintf(stderr, "[g1d-sprite-diag] skip sw=%d cw=%u w0=%08X w1=%08X a=%06X\n",
                g_rs64_swap_n.load(std::memory_order_relaxed), s_cw, w0, w1, a);
        return;
    }
    const uint32_t elr = std::min(s_cw * 4u, 0xFFFu);
    const uint32_t n0 = (w0 & ~(0xFFFu << 12)) | (elr << 12);
    memcpy(g_rdram_for_submit + (a & kSubmitRamMask), &n0, 4); g_rw_patches++;
    static int s_spr = 0;
    if (s_spr++ < 24) fprintf(stderr, "[g1d-sprite-wrap] sw=%d op=%02X cw=%u ul=(%.2f,%.2f) lr.x %.2f(+1024) -> %.2f lr.y=%.2f off=%06X\n",
        g_rs64_swap_n.load(std::memory_order_relaxed), op, s_cw, ulx / 4.0, (w1 & 0xFFFu) / 4.0, lrx / 4.0, elr / 4.0,
        (w0 & 0xFFFu) / 4.0, a);
}
static void rs64_g1d_rect_wrap(uint32_t lo, uint32_t hi) {
    static const bool on = [] { const char *e = std::getenv("ROGUESQ_G1D_RECT_WRAP"); return !(e && *e == '0'); }();
    static const bool diag = [] { const char *e = std::getenv("ROGUESQ_G1D_SPRITE_DIAG"); return e && (*e == '1' || *e == '2'); }();
    static const bool diag2 = [] { const char *e = std::getenv("ROGUESQ_G1D_SPRITE_DIAG"); rs64_g1d_walk_diag = (e && *e == '2'); return rs64_g1d_walk_diag == 1; }();
    if (diag2) { g_rs64_g1d_walk.clear(); g_rs64_g1d_walk_cw.clear(); rs64_g1d_walk_lo = rs64_g1d_walk_hi = 0; }
    if (diag && on && (hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) && s_rw_diag++ < 40)
        fprintf(stderr, "[g1d-sprite-diag] early-return lo=%06X hi=%06X\n", lo, hi);
    if (!on || g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & kSubmitRamMask), 4); return v; };
    if (diag2) { rs64_g1d_walk_lo = lo; rs64_g1d_walk_hi = hi; }
    for (uint32_t a = lo & ~3u, step = 8; a + 8 <= hi; a += step) {
        const uint32_t w0 = rd(a), op = (w0 >> 24) & 0x3F;
        if (diag2) { g_rs64_g1d_walk.push_back(a); g_rs64_g1d_walk.push_back(w0); g_rs64_g1d_walk.push_back(rd(a + 4)); g_rs64_g1d_walk_cw.push_back(s_rw_cw); }
        step = (op == 0x24 || op == 0x25) ? 16u : (op >= 0x08 && op <= 0x0F) ? 32u + ((op & 4) ? 64u : 0u) + ((op & 2) ? 64u : 0u) + ((op & 1) ? 16u : 0u) : 8u;
        rs64_rw_cmd(lo, a, w0, op, diag);
    }
}
// s7016: 1 = pillar_scan runs the rect-wrap step in its walk (needs no sprite diag); 0 = separate pass; 2 = chk
static int rs64_glue_fuse() {
    static const int v = [] { const char *e = std::getenv("ROGUESQ_GLUE_FUSE"); const char *d = std::getenv("ROGUESQ_G1D_SPRITE_DIAG");
        const char *r = std::getenv("ROGUESQ_G1D_RECT_WRAP");
        int f = (e && *e == '0') ? 0 : (e && *e == 'c') ? 2 : 1; if (d && *d && *d != '0') f = 0; if (r && *r == '0') f = 0;
        fprintf(stderr, "[s7016] glue_fuse=%d\n", f); return f; }();
    return v;
}

// s6845: ROGUESQ_WIPE_SCAN=<vi_lo>:<vi_hi> (decimal VI). On each RDP submit inside the window, scan guest RDRAM
// 0..8 MB for 8-aligned G_TEXRECT/FLIP words (top byte E4/E5) that sit OUTSIDE the submitted RDP range: the game-side
// display-list copy of the abort-wipe rect (ul.y 0, lr.y 448). Logs `[wipescan]` per hit (addr, 4 words) plus the total
// E4/E5 count per scan (positive control: HUD/text glyph rects). The first wipe-shaped hit arms the s6843 store watch
// on its 16 bytes (rs64_s6843_lo/len; start the run with ROGUESQ_STORE_WATCH=0:1 so store diag is on), so later swaps
// print the writing PC (`[swatch]`). Diagnostic only.
extern "C" volatile uint32_t rs64_s6843_lo, rs64_s6843_len;
extern "C" volatile uint32_t rs64_vi_n_g;
static void rs64_wipe_scan(uint32_t lo, uint32_t hi) {
    static uint32_t vlo = 0, vhi = 0;
    static const bool on = [] { const char *e = std::getenv("ROGUESQ_WIPE_SCAN"); if (!e || !*e) return false;
        char *c = nullptr; vlo = (uint32_t)strtoul(e, &c, 10); vhi = (c && *c == ':') ? (uint32_t)strtoul(c + 1, nullptr, 10) : 0u; return vhi > vlo; }();
    if (!on || g_rdram_for_submit == nullptr) return;
    const uint32_t vi = rs64_vi_n_g;
    g_wfr_on = vi + 2 >= vlo && vi <= vhi;
    if (vi < vlo || vi > vhi) return;
    static int s_lines = 0; static bool s_armed = false;
    uint32_t n_all = 0, n_in = 0, n_wipe = 0;
    if (s_lines < 3000) {
        const uint32_t n = g_wfr_n < 40u ? g_wfr_n : 40u;
        for (uint32_t j = g_wfr_n - n; j < g_wfr_n; ++j) { const uint32_t i = j & 63u; s_lines++;
            fprintf(stderr, "[wfr] vi=%u k=%d addr=%06X w=%08X %08X %08X %08X\n", vi, (int)(j - g_wfr_n), g_wfr_addr[i], g_wfr_w[i][0], g_wfr_w[i][1], g_wfr_w[i][2], g_wfr_w[i][3]); }
    }
    g_wfr_n = 0;
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + a, 4); return v; };
    // s6845b: match on the dsdx/dtdy word instead of the opcode (the game-side source may not be an RDP-encoded E4):
    // ROGUESQ_WIPE_SCAN_W3=<hex> (default 000D000B, the 21:9 wipe; 4:3 = 001B000B). Any 4-aligned hit outside the
    // submitted range logs the 3 words before it and the word after.
    static const uint32_t w3k = [] { const char *e = std::getenv("ROGUESQ_WIPE_SCAN_W3"); return e && *e ? (uint32_t)strtoul(e, nullptr, 16) : 0x000D000Bu; }();
    for (uint32_t a = 0; a + 16 <= 0x800000u; a += 4) {
        const uint32_t w0 = rd(a);
        if ((w0 >> 24) == 0xE4 || (w0 >> 24) == 0xE5) { n_all++; n_in += a >= lo && a < hi; }
        // s6845c: key = the SetCombine pair that precedes the wipe rect (FC119623 FF2FFFFF / FC11FE23 FFFFF7FB), a guest
        // passthrough command, so its guest-DL copy (outside the RDP FIFO region 0x6E0000-0x760000) shows what follows it.
        if (w0 != 0xFC119623u && w0 != 0xFC11FE23u) continue;
        const uint32_t b = a;
        if (b >= 0x6E0000u && b < 0x760000u) continue;
        n_wipe++;
        if (s_lines++ < 3000) {
            fprintf(stderr, "[wipescan] vi=%u sw=%d addr=%06X", vi, g_rs64_swap_n.load(std::memory_order_relaxed), b);
            for (uint32_t o = 0; o < 0x60 && b + o + 4 <= 0x800000u; o += 4) fprintf(stderr, " %08X", rd(b + o));
            fputc('\n', stderr);
        }
        (void)w3k;
        if (!s_armed && !(b >= 0x6E0000u && b < 0x760000u)) { s_armed = true; rs64_s6843_lo = b; rs64_s6843_len = 0x40; fprintf(stderr, "[wipescan] watch armed %06X+0x40\n", b); }
    }
    if (s_lines++ < 3000) fprintf(stderr, "[wipescan] vi=%u sw=%d range=%06X-%06X e4_all=%u e4_in=%u wipe_out=%u\n", vi,
                                 g_rs64_swap_n.load(std::memory_order_relaxed), lo, hi, n_all, n_in, n_wipe);
}

// s6722 G1d: the pause dim panel is a camera-facing 3D quad sized for the retail 4:3 frustum (runPauseMenuStateMachine
// object fp+0xC78), so the s6104-widened projection shows past its sides (dark band x 222..802 of 1024 at 21:9). While
// the pause byte is live, widen the triangles drawn with its RDP state (shade-only combine, blend C8104240, other-mode
// hi 2F18xCF0 (dither bits vary per run); logged by rs64_g1d_rect_scan, never seen in flight) about the image centre by ROGUESQ_ASPECT_SCALE:
// edge x and slopes * k, shade/z x-gradients / k. Scissor clips the overshoot. ROGUESQ_G1D_PAUSE_DIM=0 = old.
static void rs64_g1d_pause_dim(uint32_t lo, uint32_t hi) {
    static const double k = [] { const char *a = std::getenv("ROGUESQ_ASPECT_SCALE"), *m = std::getenv("ROGUESQ_G1D_PAUSE_DIM");
        const char *kk = std::getenv("ROGUESQ_G1D_PAUSE_DIM_K");  // test override of the widening factor
        const double v = (kk && *kk) ? atof(kk) : (a && *a) ? atof(a) : 1.0; return (m && *m == '0') ? 1.0 : v; }();
    if (k == 1.0 || k <= 0.0 || !rs64_g1d_pause_any() || g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    static uint32_t s_om0, s_om1, s_cc0, s_cc1, s_cw = 640; static int s_lines = 0;
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & kSubmitRamMask), 4); return v; };
    auto wr = [&](uint32_t a, uint32_t v) { memcpy(g_rdram_for_submit + (a & kSubmitRamMask), &v, 4); };
    auto cl = [](double v) { return (uint32_t)(int32_t)std::clamp(v, -2147483648.0, 2147483647.0); };
    for (uint32_t a = lo & ~3u, step = 8; a + 8 <= hi; a += step) {
        const uint32_t w0 = rd(a), w1 = rd(a + 4), op = (w0 >> 24) & 0x3F;
        step = (op == 0x24 || op == 0x25) ? 16u : (op >= 0x08 && op <= 0x0F) ? 32u + ((op & 4) ? 64u : 0u) + ((op & 2) ? 64u : 0u) + ((op & 1) ? 16u : 0u) : 8u;
        if (op == 0x2F) { s_om0 = w0; s_om1 = w1; continue; }
        if (op == 0x3C) { s_cc0 = w0; s_cc1 = w1; continue; }
        if (op == 0x3F) { s_cw = (w0 & 0x3FFu) + 1u; continue; }
        if ((op != 0x0C && op != 0x0D) || a + step > hi) continue;
        if ((s_om0 & ~0xC000u) != 0x2F182CF0u || s_om1 != 0xC8104240u || s_cc0 != 0xFCFFFFFFu || s_cc1 != 0xFFFE7638u) continue;
        static const bool zap = [] { const char *m = std::getenv("ROGUESQ_G1D_PAUSE_DIM"); return m && *m == 'z'; }();  // positive control: delete them
        if (zap) { wr(a, w0 & ~0x3FFFu); wr(a + 4, 0); if (s_lines++ < 8) fprintf(stderr, "[g1d-dim] zapped tri off=%06X\n", a); continue; }
        const double c = s_cw * 0.5 * 65536.0;
        for (uint32_t o : {8u, 16u, 24u}) { wr(a + o, cl(c + k * ((double)(int32_t)rd(a + o) - c))); wr(a + o + 4, cl(k * (double)(int32_t)rd(a + o + 4))); }
        // shade: DxDx int halves at +32+8/+12, frac halves at +32+24/+28 (r,g | b,a)
        for (uint32_t h = 0; h < 2; h++) {
            const uint32_t ia = a + 40 + 4 * h, fa = a + 56 + 4 * h, iv = rd(ia), fv = rd(fa);
            uint32_t ni = 0, nf = 0;
            for (int sh : {16, 0}) {
                const int32_t v = (int32_t)((((iv >> sh) & 0xFFFFu) << 16) | ((fv >> sh) & 0xFFFFu));
                const uint32_t n = cl(v / k); ni |= (n >> 16) << sh; nf |= (n & 0xFFFFu) << sh;
            }
            wr(ia, ni); wr(fa, nf);
        }
        if (op & 1) { const uint32_t za = a + 32 + 64 + 4; wr(za, cl((double)(int32_t)rd(za) / k)); }
        if (s_lines++ < 12) { fprintf(stderr, "[g1d-dim] widened tri off=%06X op=%02X k=%g cw=%u range=%06X..%06X sw=%d w=", a, op, k, s_cw, lo, hi, g_rs64_swap_n.load(std::memory_order_relaxed));
            for (uint32_t o = 0; o < 32; o += 4) fprintf(stderr, " %08X", rd(a + o)); fprintf(stderr, "\n"); }
    }
}

// s6724 G1d: some 4:3 screens (the debrief pages, MISSION FAILED + stats) draw only the centre 512 columns of their
// widened colour image, and the pillars show whatever the buffer held (s6723: the game's own live debrief heap, so it
// must not be cleared in RDRAM). Per VI-mode epoch (rs64_g1d_vi_epoch, bumped on a mode_ptr change), note whether any
// draw (texrect, fill rect, triangle; clipped to the scissor) reaches outside the centre 512 of a >512-wide image.
// rs64_g1d_pillar_crop = >= 64 draws seen and none outside: RT64's VI renderer then crops the present to the centre (black
// bars, display only). Content-gated, so flight / hangar (full-width draws) are never cropped. ROGUESQ_G1D_DEBRIEF=0 = off.
extern "C" int rs64_g1d_vi_epoch;
extern "C" { int rs64_g1d_pillar_crop = 0; }
// s6726 G1d: right-edge source columns no draw of the current VI epoch can reach (the game's scissor stops at width-1:
// G_SETSCISSOR xh 0x7FC on a 512 image), and the colour-image width they apply to. RT64's VI renderer trims them from the
// present: on the 4:3 debrief that column shows stale heap bytes (a CRT hides it in overscan). ROGUESQ_G1D_EDGE=0 = off.
extern "C" { int rs64_g1d_edge_cols = 0; int rs64_g1d_edge_cw = 0; }
static void rs64_g1d_pillar_scan(uint32_t lo, uint32_t hi) {
    static const bool on = [] { const char *v = std::getenv("ROGUESQ_G1D_DEBRIEF"); return !(v && *v == '0'); }();
    static int s_epoch = -1, s_lines = 0; static uint32_t s_draws = 0, s_out = 0, s_cw = 0, s_sx0 = 0, s_sx1 = 0xFFF, s_sy0 = 0, s_sy1 = 0xFFF;
    static uint32_t s_edraws = 0, s_ecw = 0, s_esx = 0;  // s6726 edge: draws, colour width, max scissor xh (10.2) this epoch
    struct Reach { uint32_t cw, draws, sx; double rx1, tx1; double cx0 = 1e9, cy0 = 1e9, cy1 = 0, sy0 = 1e9, sy1 = 0; };  // s6737: content min x0 / y0, max y1 (exclusive), scissor y range
    static Reach s_reach[4] = {}; static int s_rlines = 0;
    static const bool edge_on = [] { const char *v = std::getenv("ROGUESQ_G1D_EDGE"); return !(v && *v == '0'); }();
    // s6736 G3: the rule above keys on the scissor, but on the briefing fly-over (cw 640) and in flight (cw 512) the scissor
    // is the full width while no triangle / texrect / 1-2-cycle rect ever covers the last column (max x1 = cw-1.00,
    // exclusive): only the fill-mode clear reaches it, so a sky-coloured 1 px column shows at the right edge (and on the
    // faded briefing target during the mission load). Key on the reach of content draws instead, and keep the last decision
    // across a VI-mode epoch change until the new epoch has its own (the load epoch draws nothing).
    // ROGUESQ_G1D_EDGE_CONTENT=0 = s6726 scissor rule.
    static const bool edge_content = [] { const char *v = std::getenv("ROGUESQ_G1D_EDGE_CONTENT"); return !(v && *v == '0'); }();
    static uint32_t s_cyc = 0; static double s_erx = 0.0;  // current cycle type; max content reach (exclusive px) this epoch
    // s7571 19d diag: ROGUESQ_S7571_EDGE=1 evaluates BOTH trim rules at every decision and logs per epoch how often each
    // would trim (scissor rule = s6726, content rule = s6736), how often they disagree, and whether the scissor clip of the
    // content reach ever bound (unclipped reach > scissor xh). Decision output (rs64_g1d_edge_cols) unchanged.
    static const bool s7571 = [] { const char *v = std::getenv("ROGUESQ_S7571_EDGE"); return v && *v == '1'; }();
    static double s_erx_raw = 0.0; static uint32_t s71_dec = 0, s71_sc = 0, s71_ct = 0, s71_both = 0, s71_sconly = 0, s71_ctonly = 0, s71_diffn = 0, s71_clip = 0, s71_held = 0;
    static int s71_lines = 0; static uint64_t s71_tot[8] = {};
    if (!on || g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    const int ep = __atomic_load_n(&rs64_g1d_vi_epoch, __ATOMIC_RELAXED);
    if (ep != s_epoch) {
        if (s_lines < 200 && s_epoch >= 0) { s_lines++; fprintf(stderr, "[g1d-pillar] epoch=%d end draws=%u outside=%u crop=%d sw=%d\n", s_epoch, s_draws, s_out, rs64_g1d_pillar_crop, g_rs64_swap_n.load(std::memory_order_relaxed)); }
        // s6736: per-epoch, per-colour-width reach table (which columns any draw touches), for the right-edge column audit
        for (auto &e : s_reach) { if (e.cw && e.draws && s_rlines < 400) { s_rlines++; fprintf(stderr, "[g1d-reach] epoch=%d cw=%u draws=%u max_sc_xh=%.2f max_rect_x1=%.2f max_tri_x1=%.2f min_x0=%.2f sc_y=%.2f..%.2f content_y=%.2f..%.2f sw=%d\n", s_epoch, e.cw, e.draws, e.sx / 4.0, e.rx1, e.tx1, e.cx0, e.sy0, e.sy1, e.cy0, e.cy1, g_rs64_swap_n.load(std::memory_order_relaxed)); } e = {}; }
        if (s7571 && s_epoch >= 0) {
            const uint32_t v[8] = {s71_dec, s71_sc, s71_ct, s71_both, s71_sconly, s71_ctonly, s71_diffn, s71_clip};
            for (int i = 0; i < 8; i++) s71_tot[i] += v[i];
            if (s71_lines < 400 && s71_dec) { s71_lines++; fprintf(stderr, "[s7571-edge] epoch=%d dec=%u sc_trim=%u ct_trim=%u both=%u sc_only=%u ct_only=%u cols_differ=%u clip_bound=%u held_in=%u cur_cols=%d tot dec=%llu sc=%llu ct=%llu sc_only=%llu ct_only=%llu differ=%llu clip=%llu content=%d sw=%d\n", s_epoch, s71_dec, s71_sc, s71_ct, s71_both, s71_sconly, s71_ctonly, s71_diffn, s71_clip, s71_held, rs64_g1d_edge_cols, (unsigned long long)s71_tot[0], (unsigned long long)s71_tot[1], (unsigned long long)s71_tot[2], (unsigned long long)s71_tot[4], (unsigned long long)s71_tot[5], (unsigned long long)s71_tot[6], (unsigned long long)s71_tot[7], (int)edge_content, g_rs64_swap_n.load(std::memory_order_relaxed)); }
            s71_dec = s71_sc = s71_ct = s71_both = s71_sconly = s71_ctonly = s71_diffn = s71_clip = 0;
            s71_held = (edge_content && rs64_g1d_edge_cols) ? 1u : 0u;  // trim carried into the new epoch (s6736 hold)
        }
        s_epoch = ep; s_draws = 0; s_out = 0; s_edraws = 0; s_ecw = 0; s_esx = 0; s_erx = 0.0; s_erx_raw = 0.0;
        if (!edge_content) __atomic_store_n(&rs64_g1d_edge_cols, 0, __ATOMIC_RELAXED);
    }
    g_rw_walked = g_rw_fused;
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & kSubmitRamMask), 4); return v; };
    for (uint32_t a = lo & ~3u, step = 8; a + 8 <= hi; a += step) {
        const uint32_t w0 = rd(a), w1 = rd(a + 4), op = (w0 >> 24) & 0x3F;
        step = (op == 0x24 || op == 0x25) ? 16u : (op >= 0x08 && op <= 0x0F) ? 32u + ((op & 4) ? 64u : 0u) + ((op & 2) ? 64u : 0u) + ((op & 1) ? 16u : 0u) : 8u;
        if (g_rw_fused) rs64_rw_cmd(lo, a, w0, op, false);  // s7016 fused rect-wrap step
        if (op == 0x3F) { s_cw = ((w0 >> 19) & 3u) == 2u ? (w0 & 0x3FFu) + 1u : 0u; continue; }
        if (op == 0x2D) { s_sx0 = (w0 >> 12) & 0xFFFu; s_sx1 = (w1 >> 12) & 0xFFFu; s_sy0 = w0 & 0xFFFu; s_sy1 = w1 & 0xFFFu; continue; }
        if (op == 0x2F) { s_cyc = (w0 >> 20) & 3u; continue; }
        double x0, x1, y0 = 0, y1 = 0;
        if (op == 0x24 || op == 0x25 || op == 0x36) { x0 = ((w1 >> 12) & 0xFFFu) / 4.0; x1 = ((w0 >> 12) & 0xFFFu) / 4.0; y0 = (w1 & 0xFFFu) / 4.0; y1 = (w0 & 0xFFFu) / 4.0; }
        else if (op >= 0x08 && op <= 0x0F) {
            if (a + 32 > hi) continue;
            const double yl = ((int32_t)(w0 << 18) >> 18) / 4.0, ym = ((int32_t)(w1 << 2) >> 18) / 4.0, yh = ((int32_t)(w1 << 18) >> 18) / 4.0;
            auto fx = [&](uint32_t o) { return (int32_t)rd(a + o) / 65536.0; };
            const double xl = fx(8), dl = fx(12), xh = fx(16), dh = fx(20), xm = fx(24), dm = fx(28);
            const double v[6] = {xh, xh + dh * (yl - yh), xm, xm + dm * (ym - yh), xl, xl + dl * (yl - ym)};
            x0 = *std::min_element(v, v + 6); x1 = *std::max_element(v, v + 6); y0 = yh; y1 = yl;
            if (yl <= yh) continue;  // degenerate (zapped / empty)
        } else continue;
        if (s_cw != 0) {
            Reach *r = nullptr;
            for (auto &e : s_reach) if (e.cw == s_cw || e.cw == 0) { r = &e; break; }
            if (r) {
                if (!r->cw) r->cw = s_cw;
                const double cx1 = std::min(x1, s_sx1 / 4.0);
                r->draws++; r->sx = std::max(r->sx, s_sx1);
                if (op >= 0x08 && op <= 0x0F) r->tx1 = std::max(r->tx1, cx1); else r->rx1 = std::max(r->rx1, cx1);
                r->sy0 = std::min(r->sy0, s_sy0 / 4.0); r->sy1 = std::max(r->sy1, s_sy1 / 4.0);
                if (!(op == 0x36 && s_cyc == 3u)) {  // s6737: content reach on the other borders (fill-mode fill rect = the clear)
                    const bool incl = !(op >= 0x08 && op <= 0x0F) && s_cyc >= 2u;  // copy/fill-mode rects are inclusive
                    r->cx0 = std::min(r->cx0, std::max(x0, s_sx0 / 4.0)); r->cy0 = std::min(r->cy0, std::max(y0, s_sy0 / 4.0));
                    r->cy1 = std::max(r->cy1, std::min(incl ? y1 + 1.0 : y1, s_sy1 / 4.0));
                }
            }
            if (s_cw != s_ecw) { s_ecw = s_cw; s_esx = 0; s_edraws = 0; s_erx = 0.0; s_erx_raw = 0.0; }
            s_edraws++; s_esx = std::max(s_esx, s_sx1);
            const bool tri = op >= 0x08 && op <= 0x0F;
            if (!(op == 0x36 && s_cyc == 3u)) {  // fill-mode fill rects are the clear, not content
                const double reach = (!tri && s_cyc >= 2u) ? x1 + 1.0 : x1;  // copy/fill-mode rects are inclusive
                s_erx = std::max(s_erx, std::min(reach, s_sx1 / 4.0));
                s_erx_raw = std::max(s_erx_raw, reach);
            }
        }
        if (s_cw <= 512u) continue;
        x0 = std::max(x0, s_sx0 / 4.0); x1 = std::min(x1, s_sx1 / 4.0);
        if (x1 <= x0) continue;
        const double c0 = (s_cw - 512u) / 2.0, c1 = c0 + 512.0;
        s_draws++;
        if (x0 < c0 - 1.0 || x1 > c1 + 1.0) {
            // s6726: name the first outside draws of each epoch (G1d game-over page lost its crop to 1 stray draw)
            static int s_olines = 0; if (s_out < 4 && s_olines < 400) { s_olines++; fprintf(stderr, "[g1d-pillar] epoch=%d outside#%u op=0x%02X x=%.1f..%.1f sc=%.1f..%.1f cw=%u draws=%u w0=%08X w1=%08X sw=%d\n", ep, s_out + 1, op, x0, x1, s_sx0 / 4.0, s_sx1 / 4.0, s_cw, s_draws, w0, w1, g_rs64_swap_n.load(std::memory_order_relaxed)); }
            s_out++;
        }
    }
    // s6726: once an epoch has latched the crop, a few stray outside draws (game-over page: 1 draw in 15058; stats-page
    // slide-out texrects overhanging the centre by 6 px) no longer drop it; only > 2% outside does (flight/hangar/level
    // select epochs run 15-30% outside and never latch). ROGUESQ_G1D_CROP_STRICT=1 = s6724 rule (any outside draw drops).
    static const bool strict = [] { const char *v = std::getenv("ROGUESQ_G1D_CROP_STRICT"); return v && *v == '1'; }();
    static int s_latch_ep = -1;
    const bool latched = !strict && s_latch_ep == ep && rs64_g1d_pillar_crop;
    const int crop = latched ? ((uint64_t)s_out * 50u <= s_draws ? 1 : 0)
                             : (s_draws >= 64 && s_out == 0) ? 1 : 0;  // >= 64: no 1-submit flash at an epoch start (s6724: draws=1..3)
    s_latch_ep = crop ? ep : -1;
    if (edge_on && s_edraws >= 64 && s_ecw != 0) {
        const int n = edge_content ? (int)s_ecw - (int)std::ceil(s_erx - 1e-6)  // columns >= ceil(reach) only ever see the clear
                                   : (int)s_ecw - (int)((s_esx + 3u) / 4u);  // xh is exclusive: columns >= ceil(xh) are never drawn
        const int cols = (n >= 1 && n <= 4) ? n : 0;
        if (s7571) {
            const int nsc = (int)s_ecw - (int)((s_esx + 3u) / 4u), nct = (int)s_ecw - (int)std::ceil(s_erx - 1e-6);
            const int csc = (nsc >= 1 && nsc <= 4) ? nsc : 0, cct = (nct >= 1 && nct <= 4) ? nct : 0;
            s71_dec++; s71_sc += csc > 0; s71_ct += cct > 0; s71_both += (csc > 0 && cct > 0);
            s71_sconly += (csc > 0 && cct == 0); s71_ctonly += (cct > 0 && csc == 0); s71_diffn += csc != cct;
            s71_clip += s_erx_raw > s_esx / 4.0 + 1e-6;
        }
        if (cols != rs64_g1d_edge_cols && s_lines < 200) { s_lines++; fprintf(stderr, "[g1d-edge] epoch=%d cols %d->%d cw=%u scissor_xh=%.2f reach=%.2f draws=%u sw=%d\n", ep, rs64_g1d_edge_cols, cols, s_ecw, s_esx / 4.0, s_erx, s_edraws, g_rs64_swap_n.load(std::memory_order_relaxed)); }
        __atomic_store_n(&rs64_g1d_edge_cw, (int)s_ecw, __ATOMIC_RELAXED);
        __atomic_store_n(&rs64_g1d_edge_cols, cols, __ATOMIC_RELAXED);
    }
    if (crop != rs64_g1d_pillar_crop && s_lines < 200) { s_lines++; fprintf(stderr, "[g1d-pillar] epoch=%d crop %d->%d draws=%u cw=%u sw=%d\n", ep, rs64_g1d_pillar_crop, crop, s_draws, s_cw, g_rs64_swap_n.load(std::memory_order_relaxed)); }
    __atomic_store_n(&rs64_g1d_pillar_crop, crop, __ATOMIC_RELAXED);
}

// s6762 G3 lvl9 HUD drop: ROGUESQ_G3_CENSUS=<file> writes one line per update_screen (VI) with the sums over its DPC
// submits: triangles, texrects, texrects with ulx >= 360 (radar/ship-icon side), renderRadarMinimap entries, submits,
// last colour image. A capture window with no HUD then reads as HUD draws in the RDP stream (H-gfx) or none (H-gate).
extern "C" volatile uint32_t rs64_vi_n_g;
// s6788 G3e: two cumulative columns appended per line: LLE ucode iteration-cap fires (fixup_factor5_ucode.py) and
// RT64-accepted triangles, so a terrain-dropout VI reads as ucode truncation, a stream without the draws, or RT64 loss.
extern "C" volatile uint32_t rs64_ucode_cap_fires_g;
extern "C" { volatile uint32_t rs64_ucode_cap_fires_g = 0; }
extern std::atomic<uint64_t> g_rs64_rt64_tri_accepted;
static FILE *rs64_census_file() {
    static FILE *f = [] { const char *e = std::getenv("ROGUESQ_G3_CENSUS"); return (e && *e) ? fopen(e, "w") : (FILE *)nullptr; }();
    return f;
}
// s6788 G3e: ROGUESQ_G3E_TRACE=<file>: terrain draw-distance trace from funcs_9.c (tools/apply_s6788_ddtrace.py), one line
// "vi swap site a b c d" per event; joined offline with the census VI lines.
static FILE *rs64_g3e_file() {
    static FILE *f = [] { const char *e = std::getenv("ROGUESQ_G3E_TRACE"); return (e && *e) ? fopen(e, "w") : (FILE *)nullptr; }();
    return f;
}
extern "C" int rs64_g3e_on(void) { return rs64_g3e_file() != nullptr; }
extern "C" void rs64_g3e_trace(unsigned site, unsigned a, unsigned b, unsigned c, unsigned d) {
    if (FILE *f = rs64_g3e_file()) fprintf(f, "%u %d %u %u %u %u %u\n", rs64_vi_n_g, g_rs64_swap_n.load(std::memory_order_relaxed), site, a, b, c, d);
}
static void rs64_g3_census(uint32_t lo, uint32_t hi) {
    FILE *f = rs64_census_file();
    if (!f || g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    static uint32_t cvi = 0, ntr = 0, ntx = 0, nright = 0, nsub = 0, ci = 0;
    const uint32_t vi = rs64_vi_n_g;
    if (vi != cvi) {
        if (nsub) { fprintf(f, "%u %u %u %u %u %u %06X %u %llu\n", cvi, ntr, ntx, nright, g_rs64_census_radar.exchange(0), nsub, ci, rs64_ucode_cap_fires_g, (unsigned long long)g_rs64_rt64_tri_accepted.load(std::memory_order_relaxed)); fflush(f); }
        cvi = vi; ntr = ntx = nright = nsub = 0;
    }
    nsub++;
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, g_rdram_for_submit + (a & kSubmitRamMask), 4); return v; };
    for (uint32_t a = lo & ~3u, step = 8; a + 8 <= hi; a += step) {
        const uint32_t w0 = rd(a), w1 = rd(a + 4), op = (w0 >> 24) & 0x3F;
        step = (op == 0x24 || op == 0x25) ? 16u : (op >= 0x08 && op <= 0x0F) ? 32u + ((op & 4) ? 64u : 0u) + ((op & 2) ? 64u : 0u) + ((op & 1) ? 16u : 0u) : 8u;
        if (op == 0x24 || op == 0x25) { ntx++; nright += ((w1 >> 12) & 0xFFFu) >= 360u * 4u; }
        else if (op >= 0x08 && op <= 0x0F) ntr++;
        else if (op == 0x3F) ci = w1 & 0xFFFFFFu;
    }
}

// s7016 gfx-host-glue: ROGUESQ_GLUE_TIME=1 times each stream walk below (mach ticks, summary to stderr every 10 s as
// [s7016-glue]); ROGUESQ_GLUE_TOG=1 skips every walk except the default-on spike cull on odd mach 24e6-tick seconds
// (same parity + [s7010-clk] anchor as WIDEWIN=tog) for a same-run rsp split (measurement only: rect_wrap/pillar fixes off then).
#include <time.h>
// s7026 G1c (g1c-gfx-percell): ROGUESQ_S7026_SUB=1 times every RT64 handoff (ultramodern::submit_rdp_range) and every
// rs64_dpc_record_submit call (CLOCK_UPTIME_RAW pair each), counts both and their bytes, and samples 1/16 RT64 calls with a
// thread-CPU pair (wall vs on-CPU inside RT64 = lock/queue wait, H-sync). main.cpp adds the totals to the ROGUESQ_G1E_TRING row.
// ROGUESQ_S7026_SPIN_NS=<ns>: positive control, spins that long after every RT64 handoff in (uptime/10 s) odd windows (flag column).
extern "C" { int g_rs64_s7026 = [] { const char *e = std::getenv("ROGUESQ_S7026_SUB"); return (e && *e && *e != '0') ? 1 : 0; }();
uint64_t g_rs64_s7026_rt_n = 0, g_rs64_s7026_rt_ns = 0, g_rs64_s7026_rt_by = 0, g_rs64_s7026_rec_n = 0, g_rs64_s7026_rec_ns = 0,
         g_rs64_s7026_smp_n = 0, g_rs64_s7026_smp_w = 0, g_rs64_s7026_smp_c = 0; int g_rs64_s7026_spin_win = 0; }
static void rs64_dpc_record_submit_impl(uint32_t lo, uint32_t hi);
extern "C" void rs64_s7096_pre(uint32_t lo, uint32_t hi);
extern "C" int rs64_s7324_on; extern "C" void rs64_s7324_rdp(uint32_t lo, uint32_t hi, uint8_t (*rd8)(uint32_t));
static uint8_t rs64_s7324_rd8(uint32_t a) { return g_rdram_for_submit ? g_rdram_for_submit[(a & 0xFFFFFFu) ^ 3u] : 0; }
extern "C" int rs64_s7702_on; extern "C" void rs64_s7702_rdp(uint32_t lo, uint32_t hi, uint8_t (*rd8)(uint32_t));
static inline void rs64_dpc_record_submit(uint32_t lo, uint32_t hi) {
    if (rs64_s7096_on) rs64_s7096_pre(lo, hi);
    if (rs64_s7702_on) rs64_s7702_rdp(lo, hi, rs64_s7324_rd8);  // s7702 colour-buffer read census
    if (rs64_s7324_on) rs64_s7324_rdp(lo, hi, rs64_s7324_rd8);   // s7324 class G: RDP image addresses vs live spill blocks   // s7096: bytes before the bridge's record/edit walkers
    if (!g_rs64_s7026) { rs64_dpc_record_submit_impl(lo, hi); return; }
    const uint64_t t0 = clock_gettime_nsec_np(CLOCK_UPTIME_RAW);
    rs64_dpc_record_submit_impl(lo, hi);
    g_rs64_s7026_rec_ns += clock_gettime_nsec_np(CLOCK_UPTIME_RAW) - t0; ++g_rs64_s7026_rec_n;
}
extern "C" int rs64_s7526_alt; extern "C" void rs64_s7526_fwd(uint32_t lo, uint32_t hi, const uint8_t* rdram);  // s7526 V2P twin
static inline void rs64_rt_submit(uint32_t lo, uint32_t hi, int site) {
    if (rs64_s7096_on) rs64_s7096_fwd(lo, hi, site);
    if (rs64_s7526_alt) rs64_s7526_fwd(lo, hi, g_rdram_for_submit);
    if (!g_rs64_s7026) { ultramodern::submit_rdp_range(lo, hi); return; }
    static const uint64_t spin = [] { const char *e = std::getenv("ROGUESQ_S7026_SPIN_NS"); return e ? (uint64_t)std::strtoull(e, nullptr, 0) : 0ull; }();
    const bool smp = (g_rs64_s7026_rt_n & 15u) == 0;
    const uint64_t c0 = smp ? clock_gettime_nsec_np(CLOCK_THREAD_CPUTIME_ID) : 0;
    const uint64_t t0 = clock_gettime_nsec_np(CLOCK_UPTIME_RAW);
    ultramodern::submit_rdp_range(lo, hi);
    uint64_t t1 = clock_gettime_nsec_np(CLOCK_UPTIME_RAW);
    if (smp) { const uint64_t c1 = clock_gettime_nsec_np(CLOCK_THREAD_CPUTIME_ID); g_rs64_s7026_smp_w += t1 - t0; g_rs64_s7026_smp_c += c1 - c0; ++g_rs64_s7026_smp_n; }
    if (spin) { g_rs64_s7026_spin_win = (int)((t0 / 10000000000ull) & 1u);
        if (g_rs64_s7026_spin_win) { const uint64_t until = t1 + spin; while ((t1 = clock_gettime_nsec_np(CLOCK_UPTIME_RAW)) < until) {} } }
    g_rs64_s7026_rt_ns += t1 - t0; ++g_rs64_s7026_rt_n; if (hi > lo) g_rs64_s7026_rt_by += hi - lo;
}
// s7097 (src/rsp/s7097_edit_census.cpp): per-walker byte-diff census, ROGUESQ_S7097_EDIT=1|ctl.
extern "C" int rs64_s7097_on; extern "C" void rs64_s7097_begin(uint32_t, uint32_t, uint8_t *);
extern "C" void rs64_s7097_pre(int); extern "C" void rs64_s7097_post(int); extern "C" void rs64_s7097_end();
#define RS64_W7(id, call) do { if (rs64_s7097_on) rs64_s7097_pre(id); call; if (rs64_s7097_on) rs64_s7097_post(id); } while (0)
extern "C" void rs64_s7389_scan(uint32_t, uint32_t, const uint8_t *);  // s7389 fb-load watch marks
// s7634 bridge-walker-fusion discriminator: ROGUESQ_S7634_NULLWALK=1 walks every submit with the same op-size rules as
// rs64_spike_scan / rs64_region_scan (16 B texrects, tri lengths from op bits, 8 B otherwise) and does nothing else, timed in
// its own [s7016-glue] bucket (null=) right after the spike walk (warm cache, as the region walk sees it). Measurement only.
// =t with ROGUESQ_GLUE_TOG=3 runs it twice on odd seconds: the null bucket must double there (dose-response positive control).
static volatile uint32_t g_s7634_sink = 0;
static void rs64_s7634_nullwalk(uint32_t lo, uint32_t hi) {
    if (g_rdram_for_submit == nullptr || hi <= lo || (hi - lo) > 0x100000u || hi > kSubmitRamEnd) return;
    uint32_t acc = 0;
    for (uint32_t a = lo & ~3u; a + 8 <= hi;) {
        uint32_t w0, w1; memcpy(&w0, g_rdram_for_submit + (a & kSubmitRamMask), 4); memcpy(&w1, g_rdram_for_submit + ((a + 4) & kSubmitRamMask), 4);
        const uint32_t op = (w0 >> 24) & 0x3F; acc += op ^ w1;
        if (op == 0x24 || op == 0x25) { a += 16; continue; }
        if (op < 0x08 || op > 0x0F) { a += 8; continue; }
        if (a + 32 > hi) break;
        a += 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
    }
    g_s7634_sink += acc;
}
static void rs64_dpc_record_submit_impl(uint32_t lo, uint32_t hi) {
    rs64_s7389_scan(lo, hi, g_rdram_for_submit);
    if (rs64_s7097_on) rs64_s7097_begin(lo, hi, g_rdram_for_submit);
    static const bool gtime = [] { const char *e = std::getenv("ROGUESQ_GLUE_TIME"); return e && *e && *e != '0'; }();
    static const int gtog = [] { const char *e = std::getenv("ROGUESQ_GLUE_TOG"); return (e && *e == '2') ? 2 : (e && *e == '3') ? 3 : (e && *e && *e != '0') ? 1 : 0; }();  // 3 = A/A null: anchor + parity only
    bool skip = false, odd = false;
    if (gtog) {
        const uint64_t mt = mach_absolute_time(); static bool anc = false;
        if (!anc) { anc = true; rs64_tog_anchor(mt); }
        odd = rs64_tog_odd(mt) != 0; skip = gtog == 1 && odd;  // GLUE_TOG=2: odd seconds = unfused two-pass walk
    }
    g_s7636_odd = odd;  // s7636: FASTSPIKE=tog parity
    static uint64_t s_acc[2][7] = {}, s_n[2] = {}, s_bytes = 0, s_last = 0;  // walks: census..wipe, pillar, rect_wrap, pause+rscan, spike, g5b..floor
    uint64_t t[8]; const bool tm = gtime;
    static const int s7634null = [] { const char *e = std::getenv("ROGUESQ_S7634_NULLWALK"); return !(e && *e && *e != '0') ? 0 : (*e == 't' ? 2 : 1); }();  // =t: 2 passes on odd GLUE_TOG seconds (dose control)
    if (tm) t[0] = mach_absolute_time();
    if (!skip) { RS64_W7(0, rs64_g3_census(lo, hi)); RS64_W7(1, rs64_g1d_title_clear(lo, hi)); RS64_W7(2, rs64_wipe_scan(lo, hi)); }
    if (tm) t[1] = mach_absolute_time();
    const int fuse = (gtog == 2 && odd) ? 0 : rs64_glue_fuse();
    g_rw_fused = fuse != 0; g_rw_walked = false;
    if (!skip) RS64_W7(3, rs64_g1d_pillar_scan(lo, hi));
    g_rw_fused = false;
    if (tm) t[2] = mach_absolute_time();
    if (!skip && (!g_rw_walked || fuse == 2)) {
        static uint64_t s_chk_left = 0, s_chk_runs = 0;
        const uint64_t before = g_rw_patches;
        RS64_W7(4, rs64_g1d_rect_wrap(lo, hi));
        if (fuse == 2 && g_rw_walked) { s_chk_runs++; s_chk_left += g_rw_patches - before; g_rw_patches = before;
            if ((s_chk_runs & 4095u) == 0) fprintf(stderr, "[s7016-chk] runs=%llu fused_patches=%llu left_after_fused=%llu\n",
                (unsigned long long)s_chk_runs, (unsigned long long)g_rw_patches, (unsigned long long)s_chk_left); }
    }
    if (tm) t[3] = mach_absolute_time();
    if (!skip) { RS64_W7(5, rs64_g1d_pause_dim(lo, hi)); RS64_W7(6, rs64_g1d_rect_scan(lo, hi)); }
    if (tm) t[4] = mach_absolute_time();
    // s7635 item 24: ROGUESQ_S7634_FUSE=1 (default) runs the spike and region walks as one walk here (rs64_region_scan fused=1);
    // =0 the old two walks; =tog the old two on odd GLUE_TOG seconds (same-run A/B, needs ROGUESQ_GLUE_TOG=3); =chk / =inj the
    // fused walk with the late-write check / plus its injected control. G5B_FRAME_EARLY=1 (recorder between the two) keeps two walks.
    static const bool s_g5bEarly = [] { const char *e = std::getenv("ROGUESQ_G5B_FRAME_EARLY"); return e && *e == '1'; }();
    static const int s7635fuse = [] { const char *e = std::getenv("ROGUESQ_S7634_FUSE"); if (!(e && *e)) return 1;
        return *e == '0' ? 0 : *e == 't' ? 4 : *e == 'c' ? 2 : *e == 'i' ? 3 : 1; }();
    const int fz = (skip || s_g5bEarly) ? 0 : s7635fuse == 4 ? (odd ? 0 : 1) : s7635fuse;
    if (fz) RS64_W7(7, rs64_region_scan(lo, hi, fz)); else RS64_W7(7, rs64_spike_scan(lo, hi));
    if (tm) t[5] = mach_absolute_time();
    if (s7634null) { rs64_s7634_nullwalk(lo, hi); if (s7634null == 2 && odd) rs64_s7634_nullwalk(lo, hi); }
    uint64_t t_null = 0; if (tm) { const uint64_t tn = mach_absolute_time(); t_null = tn - t[5]; t[5] = tn; }
    // s7125 G3: the G5B_FRAME recorder now runs AFTER the region shift (radar disc, s6158) and floor walkers, so the replay stream is
    // the bytes RT64 is given; before, every 16:9/21:9 capture showed the disc unshifted (~1000 px HUD diff per frame vs RT64).
    // ROGUESQ_G5B_FRAME_EARLY=1 restores the old pre-walker record point.
    if (!skip) { if (s_g5bEarly) RS64_W7(8, rs64_g5b_frame(lo, hi)); if (!fz) RS64_W7(9, rs64_region_scan(lo, hi)); RS64_W7(10, rs64_floor_scan(lo, hi));
                 if (!s_g5bEarly) RS64_W7(8, rs64_g5b_frame(lo, hi)); }
    if (tm) {
        t[6] = mach_absolute_time();
        for (int i = 0; i < 6; i++) s_acc[odd][i] += t[i + 1] - t[i];
        s_acc[odd][6] += t_null;
        s_n[odd ? 1 : 0]++; if (hi > lo) s_bytes += hi - lo;
        if (s_last == 0) s_last = t[6];
        if (t[6] - s_last >= 240000000u) {  // 10 s at 24 MHz
            const double us = 1.0 / 24.0, sec = (t[6] - s_last) / 24e6;
            for (int q = 0; q < 2; q++)
            fprintf(stderr, "[s7016-glue] par=%d sec=%.1f submits=%llu odd=%llu kB=%.0f us_per_s: misc=%.0f pillar=%.0f rect_wrap=%.0f pause_rscan=%.0f spike=%.0f tail=%.0f null=%.0f\n",
                    q, sec, (unsigned long long)(s_n[0] + s_n[1]), (unsigned long long)s_n[1], s_bytes / 1024.0,
                    s_acc[q][0] * us / sec, s_acc[q][1] * us / sec, s_acc[q][2] * us / sec, s_acc[q][3] * us / sec, s_acc[q][4] * us / sec, s_acc[q][5] * us / sec, s_acc[q][6] * us / sec);
            for (auto &r : s_acc) for (auto &x : r) x = 0; s_n[0] = s_n[1] = 0; s_bytes = 0; s_last = t[6];
        }
    }
    g_last_submit_lo.store(lo, std::memory_order_release);
    g_last_submit_hi.store(hi, std::memory_order_release);
    const uint32_t before = g_task_bridge_e9.load(std::memory_order_acquire);
    rs64_count_submitted_e9(lo, hi);
    const uint32_t after = g_task_bridge_e9.load(std::memory_order_acquire);
    const uint64_t serial = g_submit_serial.fetch_add(1, std::memory_order_acq_rel) + 1;
    if (s_task_first_hi == 0) {
        s_task_first_lo = lo;
        s_task_first_hi = hi;
    }
    s_task_last_lo = lo;
    s_task_last_hi = hi;
    if (lo < s_task_min_lo) s_task_min_lo = lo;
    if (hi > s_task_max_hi) s_task_max_hi = hi;
    if (log_tri_writer() && (g_e9prov.control || g_e9prov.target) &&
        g_rdram_for_submit != nullptr) {
        static std::atomic<uint32_t> writer_lines{0};
        static uint32_t writer_task = 0xFFFFFFFFu;
        static uint32_t writer_task_lines = 0;
        if (writer_task != g_e9prov.task) {
            writer_task = g_e9prov.task;
            writer_task_lines = 0;
        }
        for (uint32_t p = lo; p + 8 <= hi; p += 8) {
            const uint8_t raw = g_rdram_for_submit[p ^ 3];
            if (raw < 0x08 || raw > 0x0F) continue;
            if (writer_task_lines++ >= 64) break;
            const uint32_t line = writer_lines.fetch_add(1, std::memory_order_relaxed);
            const uint32_t w0 = ((uint32_t)g_rdram_for_submit[(p + 0) ^ 3] << 24) |
                                ((uint32_t)g_rdram_for_submit[(p + 1) ^ 3] << 16) |
                                ((uint32_t)g_rdram_for_submit[(p + 2) ^ 3] << 8) |
                                (uint32_t)g_rdram_for_submit[(p + 3) ^ 3];
            const uint32_t w1 = ((uint32_t)g_rdram_for_submit[(p + 4) ^ 3] << 24) |
                                ((uint32_t)g_rdram_for_submit[(p + 5) ^ 3] << 16) |
                                ((uint32_t)g_rdram_for_submit[(p + 6) ^ 3] << 8) |
                                (uint32_t)g_rdram_for_submit[(p + 7) ^ 3];
            fprintf(stderr,
                    "[tri-writer] line=%u task=%u scope=%s serial=%llu addr=0x%06X "
                    "raw=0x%02X w0=0x%08X w1=0x%08X range=0x%06X..0x%06X "
                    "f5_task=%u f5_valid=%u f5_ord=%u f5_pc=0x%06X f5_source=0x%06X\n",
                    line + 1, g_e9prov.task,
                    g_e9prov.control ? "control" : "sec2",
                    (unsigned long long)serial, p, raw, w0, w1, lo, hi,
                    g_f5_vtxcolor_state.task, g_f5_vtxcolor_state.valid ? 1u : 0u,
                    g_f5_vtxcolor_state.ordinal, g_f5_vtxcolor_state.pc,
                    g_f5_vtxcolor_state.source);
        }
        fflush(stderr);
    }
    if (log_e9_boundary() && (g_e9prov.control || g_e9prov.target) &&
        g_rdram_for_submit != nullptr) {
        for (uint32_t p = lo; p + 8 <= hi; p += 8) {
            if (g_rdram_for_submit[p ^ 3] != 0xE9) continue;
            if (g_e9_boundary_lines++ >= 1024) break;
            fprintf(stderr,
                    "[e9-boundary-bridge] serial=%llu task=%u scope=%s addr=0x%06X range=0x%06X..0x%06X\n",
                    (unsigned long long)serial, g_e9prov.task,
                    g_e9prov.control ? "control" : "sec2", p, lo, hi);
        }
        fflush(stderr);
    }
    if (log_e9_unified() && after > before && (g_e9prov.control || g_e9prov.target)) {
        fprintf(stderr,
                "[e9-ordinary-submit] serial=%llu task=%u e9=%u lo=0x%06X hi=0x%06X\n",
                (unsigned long long)serial, g_e9prov.task, after - before, lo, hi);
        fprintf(stderr, "[e9-submit-range] serial=%llu task=%u lo=0x%06X hi=0x%06X e9=%u\n",
                (unsigned long long)serial, g_e9prov.task, lo, hi, after - before);
        fflush(stderr);
    }
    if (rs64_s7097_on) rs64_s7097_end();
}

// ROGUESQ_DROP_WRAP_RDP (s664, default OFF): drop RDP submits whose
// submit_lo sits inside the last dpc-wrap sticky [start, seen). Candidate
// root fix for in-wrap garbage SETCIMG (exact freelist killer + hangar
// wilds; ORIGIN s663). Wrap sticky still updates on every wrap event even
// when this filter is dropping submits.
static bool drop_wrap_rdp_enabled() {
    static const bool v = []{
        const char *e = std::getenv("ROGUESQ_DROP_WRAP_RDP");
        const bool on = e && *e && *e != '0';
        if (on) {
            fprintf(stderr,
                "[dpc] DROP_WRAP_RDP=1 (skip submits with lo in last wrap "
                "sticky [start,seen))\n");
            fflush(stderr);
        }
        return on;
    }();
    return v;
}

static bool should_drop_wrap_rdp(uint32_t submit_lo, uint32_t submit_hi) {
    if (!drop_wrap_rdp_enabled()) {
        return false;
    }
    const uint32_t start = g_last_wrap_start.load(std::memory_order_acquire);
    const uint32_t seen = g_last_wrap_seen.load(std::memory_order_acquire);
    if (start == 0 || seen <= start) {
        return false;
    }
    if (submit_lo < start || submit_lo >= seen) {
        return false;
    }
    static std::atomic<uint64_t> s_n{0};
    const uint64_t n = ++s_n;
    if (n <= 16 || (n % 1024) == 0) {
        fprintf(stderr,
            "[dpc-wrap-drop] #%llu lo=0x%06X hi=0x%06X "
            "wrap=[start=0x%06X,seen=0x%06X)\n",
            (unsigned long long)n, submit_lo, submit_hi, start, seen);
        fflush(stderr);
    }
    return true;
}

// Per-task GFX opcode histogram (high byte of DL command word). Counted
// directly from the factor5_ucode dispatch loop — a single increment per
// command, no function call. Same single-thread-only constraint as above.
extern "C" uint32_t g_task_gfx_op_count[256] = {0};

// Per-task G_MOVEMEM index histogram. F3D indices: 0x80 viewport,
// 0x82 lookat_y, 0x84 lookat_x, 0x86..0x94 lights L0..L7, 0x96 txtatt,
// 0x98/9A/9C/9E matrix1-4. Tells us if Factor5 is loading lights every
// frame (animated lighting) or just static state.
extern "C" uint32_t g_task_movemem_idx_count[256] = {0};

// Per-task distinct G_SETCOMBINE mux tracker. Multi-pass rendering would
// produce DIFFERENT (w0, w1) pairs per task — single-pass would repeat the
// same mux. Tells us empirically whether the Pak (5 tris, 161 setCombine
// per task) is one combiner repeated or a multi-pass setup. Capped at 16
// distinct muxes per task; overflow counted separately.
struct TaskCombineEntry { uint32_t w0; uint32_t w1; uint32_t count; };
static TaskCombineEntry g_task_combine[16] = {};
static uint32_t g_task_combine_uniq = 0;
static uint32_t g_task_combine_total = 0;
static uint32_t g_task_combine_overflow = 0;

// True while the most recently-set combiner mux equals the Pak's
// (TEXEL × SHADE = 0xFC127E24/0xFFFFFFFF). Texture-command logging
// gates on this so we only see the Pak's loads, not the 159 text loads.
bool g_in_pak_combiner = false;

// Track the most recent SETTIMG address while in Pak combiner block —
// LOADTLUT consumes whatever SETTIMG address is current (RGBA16 source).
uint32_t g_pak_last_tlut_addr = 0;

// Cinematic / particle combiner instrumentation. Mux 0xFC11FE23 /
// 0xFFFFFFFF dominates task #290+ (count 522 in the captured run) and
// covers the cinematic's TEXRECT-rendered particles (shockwaves,
// fireballs, smoke). Asset lookup func_80057338 was confirmed feeding
// "shock_sml"/"shock_sph" into this combiner block, so this gate
// brackets the active particle-render path.
bool g_in_cine_combiner = false;
uint32_t g_cine_last_settimg_fmt = 0;
uint32_t g_cine_last_settimg_siz = 0;
uint32_t g_cine_last_settimg_addr = 0;
uint32_t g_cine_last_cimg_addr = 0;     // current SET_COLOR_IMAGE target fb

// PHASE 21 correlation: which cinematic effect slot (0-5) is currently
// executing its handler. Set by the recompiled slot dispatcher around the
// handler `jalr` call (funcs_8.c:func_8003E8DC); reset to -1 between calls.
// Lets us annotate dpc_bridge SET_COLOR_IMAGE / TEXRECT logs with the
// originating effect slot, so we can see the slot → fb mapping.
//
// Plain global (not thread_local) — the cinematic dispatcher runs on the
// MAIN game thread; SET_COLOR_IMAGE detection runs on the GFX thread; both
// see the same value with eventual-consistency, which is fine for logging.
// Declared `extern int` from C (recompiled funcs_8.c) — needs `extern "C"`
// linkage here so the C-side reference resolves at link time. Read
// non-atomically; minor races produce wrong slot annotations on a few
// events, not crashes.
extern "C" int g_cine_current_slot = -1;

// PHASE 21 engine-aware filter: per-fb slot ownership.
// Records, for each fb address (key), the slot index that was active when
// the most recent SET_COLOR_IMAGE targeting that fb was emitted. If >= 0,
// the fb is "owned by a cinematic effect" and full-screen fills on it
// are the cinematic erasure pattern (suppress). If -1, the fb belongs
// to non-cinematic phases (attribution / N64 logo / etc) and its fills
// are legitimate clear-then-redraw (don't suppress).
//
// RT64's framebuffer_renderer queries this map via a free function
// (rt64_cine_fb_is_slot_owned, defined below).
static std::mutex g_cine_fb_owner_mutex;
static std::unordered_map<uint32_t, int> g_cine_fb_owner_slot;

// Query function called from RT64's framebuffer_renderer FillRect handler.
// Returns true iff the fb at `addr` was last targeted by a SET_COLOR_IMAGE
// emitted from inside an active slot dispatch (slot >= 0), meaning the fb
// is the cinematic's render target and a full-screen fill on it would be
// erasing visible content. Returns false for fbs that have never been
// touched by the cinematic, or that were last touched by non-cinematic
// SET_COLOR_IMAGE (slot=-1).
extern "C" bool rt64_cine_fb_is_slot_owned(uint32_t addr) {
    std::lock_guard<std::mutex> lk(g_cine_fb_owner_mutex);
    auto it = g_cine_fb_owner_slot.find(addr & 0x00FFFFFFu);
    return (it != g_cine_fb_owner_slot.end()) && (it->second >= 0);
}

// Shadow of the most recent RDP state-set commands. Used so the
// 64-tri particle mux entry can dump the full draw context (otherMode,
// texture, framebuffer, tile) at the moment the particle combiner is
// activated — that's the state the particle triangles will actually use.
uint32_t g_last_othermode_l = 0;
uint32_t g_last_othermode_h = 0;
uint32_t g_last_settimg_w0 = 0;
uint32_t g_last_settimg_w1 = 0;
uint32_t g_last_setcimg_w0 = 0;
uint32_t g_last_setcimg_w1 = 0;
uint32_t g_last_settile_w0 = 0;
uint32_t g_last_settile_w1 = 0;
uint32_t g_last_fogcolor = 0;     // G_SETFOGCOLOR (0xF8) RGBA
uint32_t g_last_primcolor = 0;    // G_SETPRIMCOLOR (0xFA) RGBA
uint32_t g_last_envcolor = 0;     // G_SETENVCOLOR (0xFB) RGBA
uint32_t g_last_blendcolor = 0;   // G_SETBLENDCOLOR (0xF9) RGBA

namespace {
    // Cached env-var read for dpc_bridge logging. The bridge emits ~1000+
    // lines per second of `[task-brief]`, `[task#N gfx]`, `[dpc-pak]`,
    // `[dpc-cine]`, `[dpc-64tri]`, `[trace] cinematic_drv` etc. during
    // cinematic playback — extremely noisy. Default off; enable when
    // tracing what GFX commands the Factor5 LLE ucode is emitting.
    // ROGUESQ_LOG_DPC=1 (or ROGUESQ_LOG_ALL=1).
    bool log_dpc() {
        static const bool v = []{
            const char *a = std::getenv("ROGUESQ_LOG_ALL");
            if (a && *a && *a != '0') return true;
            const char *e = std::getenv("ROGUESQ_LOG_DPC");
            return e && *e && *e != '0';
        }();
        return v;
    }
    // ROGUESQ_LOG_RDP_FULLSYNC: every real op-0x29 (FULL_SYNC) submit site.
    // Discriminates H-sync4: guest-E9 outside e9_b walk vs synthetic/misdecode.
    // Not folded into LOG_ALL — can be ~1 line/task for thousands of tasks.
    bool log_rdp_fullsync() {
        static const bool v = []{
            const char *e = std::getenv("ROGUESQ_LOG_RDP_FULLSYNC");
            return e && *e && *e != '0';
        }();
        return v;
    }
    // ROGUESQ_LOG_FS_SLOT: any DPC submit that touches the fixed FULL_SYNC
    // side-slot (default phys 0x76DF60, override ROGUESQ_FS_SLOT_ADDR).
    // Discriminates H-sync4 stop edge: path stops submitting vs content mutates.
    bool log_fs_slot() {
        static const bool v = []{
            const char *e = std::getenv("ROGUESQ_LOG_FS_SLOT");
            return e && *e && *e != '0';
        }();
        return v;
    }
    uint32_t fs_slot_addr() {
        static const uint32_t v = []{
            uint32_t a = 0x76DF60u;
            if (const char *e = std::getenv("ROGUESQ_FS_SLOT_ADDR")) {
                unsigned long x = std::strtoul(e, nullptr, 0);
                if (x > 0 && x < 0x800000u) a = (uint32_t)x;
            }
            return a & 0x7FFFFFu;
        }();
        return v;
    }
}

// s6936 G1e: ROGUESQ_G1E_WALK_STAT=1 counts, on the wrap flush, the deferred ranges that begin inside an RDP command (the walkers in
// record_submit decode a range from its first word, so a range that starts mid-command is read as body words). A command cursor
// follows contiguous ranges; a gap resets it. Self-test at first use: one 32-byte triangle bumped as 4 x 8 bytes must give mid=3.
static uint32_t rs64_cmd_len(const uint8_t *ram, uint32_t a) {
    uint32_t w0; memcpy(&w0, ram + (a & kSubmitRamMask), 4); const uint32_t op = (w0 >> 24) & 0x3F;
    if (op == 0x24 || op == 0x25) return 16u;
    if (op >= 0x08 && op <= 0x0F) return 32u + ((op & 4) ? 64u : 0u) + ((op & 2) ? 64u : 0u) + ((op & 1) ? 16u : 0u);
    return 8u;
}
struct Rs64WalkStat { uint32_t cur = 0, end = 0; uint64_t ranges = 0, mid = 0, bytes = 0, tri_heads = 0; };
static void rs64_walk_stat_range(Rs64WalkStat &st, const uint8_t *ram, uint32_t lo, uint32_t hi) {
    if (lo != st.end) st.cur = lo;
    st.ranges++; st.bytes += hi - lo;
    if (st.cur > lo) st.mid++;
    while (st.cur < hi) { uint32_t w0; memcpy(&w0, ram + (st.cur & kSubmitRamMask), 4); const uint32_t op = (w0 >> 24) & 0x3F; if (op >= 0x08 && op <= 0x0F) st.tri_heads++; st.cur += rs64_cmd_len(ram, st.cur); }
    st.end = hi;
}
static uint64_t rs64_walk_stat_selftest() {
    uint8_t buf[64] = {}; const uint32_t tri = 0x08000000u, nop = 0x27000000u;
    memcpy(buf, &tri, 4); memcpy(buf + 32, &nop, 4);
    Rs64WalkStat t; for (uint32_t a = 0; a < 40; a += 8) rs64_walk_stat_range(t, buf, a, a + 8);
    return t.mid;  // must be 3
}

// The ucode bumps DPC_END one 8-byte command at a time, so a task's deferred list is mostly runs of contiguous ranges;
// submit each run as one range (byte-for-byte identical content and order, far fewer RT64 entries). Used by the
// task-end commit and by the s6707 streamed flush.
static uint32_t g_defer_stream_pending = 0, g_defer_stream_task_flushes = 0;
static uint64_t g_defer_stream_flushes = 0, g_defer_stream_bytes = 0;
static void submit_deferred_merged(uint32_t &bytes, size_t &calls) {
    if (g_deferred_ranges.empty()) return;
    uint32_t lo = g_deferred_ranges[0].first;
    uint32_t hi = g_deferred_ranges[0].second;
    for (size_t i = 1; i <= g_deferred_ranges.size(); i++) {
        if (i < g_deferred_ranges.size() && g_deferred_ranges[i].first == hi) {
            hi = g_deferred_ranges[i].second;
            continue;
        }
        if (!should_drop_wrap_rdp(lo, hi)) {
            rs64_e9prov_mark_submitted(lo, hi);
            bytes += hi - lo;
            calls++;
            rs64_dpc_record_submit(lo, hi);
            rs64_rt_submit(lo, hi, 1);
        } else RS64_S7096_DROP(lo, hi, 4);
        if (i < g_deferred_ranges.size()) {
            lo = g_deferred_ranges[i].first;
            hi = g_deferred_ranges[i].second;
        }
    }
}

// s7027 bump fast path state (see rsp_dpc_submit_impl).
extern "C" { int g_rs64_bf_task_on = 0; uint64_t g_rs64_bf_fast = 0, g_rs64_bf_slow = 0, g_rs64_bf_tasks_on = 0, g_rs64_bf_tasks_off = 0;
             uint64_t g_rs64_bf_chk_n = 0, g_rs64_bf_chk_bad = 0, g_rs64_bf_chk_ctl = 0; }
static uint32_t g_bf_seen = 0, g_bf_ctl_armed = 0; static uint64_t g_bf_slow_op[64] = {};
// s7028: modes 0 off, 1 fast, 2 tog (xor8 off/fast), 3 = env "2" fast + plain per-task counters, 4 = env "tog3" (mach second % 3 -> off/fast/fast+plain).
static const int g_bf_mode = [] { const char *e = std::getenv("ROGUESQ_G1E_BUMPFAST"); if (!e || !*e || *e == '0') return 0;
    if (!strcmp(e, "tog3")) return 4; if (*e == 't') return 2; if (*e == '2') return 3; return 1; }();
// s7028 G1c (g1c-bump-push-split): arm 2 (task_on == 2) keeps the per-bump counters (s_fwd pair, g_task_rdp_bytes, rs64_g1e_rdp_bytes,
// g_task_rdp_cmds, fast-path g_cumulative_op_count) in plain gfx-thread accumulators, flushed into the atomics at rsp_task_log_and_reset,
// rs64_task_rdp_bytes_total and rs64_dpc_defer_end (every gfx-thread reader). CHECK=1 also does the atomic adds into reference atomics
// and compares them with the pending sums at each flush (bad2 must be 0); the first 4 flushes compare a planted +1 (ctl2 must be 4).
extern "C" { uint64_t g_rs64_bf_tasks_on2 = 0, g_rs64_bf_chk2_n = 0, g_rs64_bf_chk2_bad = 0, g_rs64_bf_chk2_ctl = 0; }
// s7029: H-thread control (CHECK=1 only): bf2 bumps from a thread other than the one that ran rs64_dpc_defer_begin.
extern "C" { uint64_t g_rs64_bf2_thr_mm = 0; } static pthread_t g_bf2_thr;
// s7029 G1c (g1c-bump-push-split): ROGUESQ_G1E_BUMPFAST_SH=tog3 latches a shadow arm per task (mach second % 3, as BUMPFAST tog3):
// 0 as is, 1 reserve the deferred-range/shadow vectors from the previous task's peak sizes at defer_begin, 2 no S4272 shadow for this
// task (DIAGNOSTIC ONLY: the commit-time restore then finds no shadow and skips; use with BUMPFAST=2, never in owner play).
extern "C" { int g_rs64_bfsh_arm = 0; uint64_t g_rs64_bfsh_tasks[3] = {0, 0, 0}; }
static const bool g_bfsh_mode = [] { const char *e = std::getenv("ROGUESQ_G1E_BUMPFAST_SH"); return e && *e && *e != '0'; }();
static size_t g_bfsh_pk_sh = 0, g_bfsh_pk_shadow = 0, g_bfsh_pk_ranges = 0;
static uint64_t g_bf2_fwd_bytes = 0, g_bf2_fwd_subs = 0, g_bf2_g1e_bytes = 0; static uint32_t g_bf2_task_bytes = 0, g_bf2_task_cmds = 0;
static uint32_t g_bf2_ops[64] = {}; static bool g_bf2_dirty = false;
static std::atomic<uint64_t> g_bf2_ref_bytes{0}, g_bf2_ref_cmds{0}, g_bf2_ref_ops{0};
extern "C" int rs64_diag_fprintf(FILE* f, const char* fmt, ...);  // s7432
static std::atomic<uint64_t> s_fwd_bytes{0};    // s7028: hoisted from rsp_dpc_submit_impl (the [dpc-fwd] pair)
static std::atomic<uint64_t> s_fwd_submits{0};
static bool g_bf_check_flag();
static void rs64_bf2_flush() {
    if (!g_bf2_dirty) return;
    g_bf2_dirty = false;
    if (g_bf_check_flag()) {
        static uint64_t n = 0; const uint64_t plant = (n++ < 4) ? 1 : 0; uint64_t ops = 0; for (int i = 0; i < 64; ++i) ops += g_bf2_ops[i];
        // s7029: read every reference unconditionally. The s7028 `a.exchange(0) == x && b.exchange(0) == y` short-circuited on the
        // planted flushes 1-4, so ref_cmds/ref_ops were never reset there and flush 5 always miscompared (the s7028 bad2=1).
        const uint64_t rb = g_bf2_ref_bytes.exchange(0), rc = g_bf2_ref_cmds.exchange(0), ro = g_bf2_ref_ops.exchange(0);
        const bool same = rb == g_bf2_task_bytes + plant && rc == g_bf2_task_cmds && ro == ops && g_bf2_fwd_bytes == g_bf2_task_bytes &&
                          g_bf2_fwd_subs == g_bf2_task_cmds && g_bf2_g1e_bytes == g_bf2_task_bytes;
        if (!same && !plant && g_rs64_bf_chk2_bad < 8)
            fprintf(stderr, "[s7029-bad2] ref b/c/o=%llu/%llu/%llu task b/c=%u/%u ops=%llu fwd b/s=%llu/%llu g1e=%llu thrMismatch=%llu\n",
                    (unsigned long long)rb, (unsigned long long)rc, (unsigned long long)ro, g_bf2_task_bytes, g_bf2_task_cmds,
                    (unsigned long long)ops, (unsigned long long)g_bf2_fwd_bytes, (unsigned long long)g_bf2_fwd_subs,
                    (unsigned long long)g_bf2_g1e_bytes, (unsigned long long)g_rs64_bf2_thr_mm);
        if (plant) { if (!same) ++g_rs64_bf_chk2_ctl; } else { ++g_rs64_bf_chk2_n; if (!same) ++g_rs64_bf_chk2_bad; }
    }
    s_fwd_bytes.fetch_add(g_bf2_fwd_bytes, std::memory_order_relaxed); s_fwd_submits.fetch_add(g_bf2_fwd_subs, std::memory_order_relaxed);
    g_task_rdp_bytes.fetch_add(g_bf2_task_bytes, std::memory_order_relaxed); rs64_g1e_rdp_bytes.fetch_add(g_bf2_g1e_bytes, std::memory_order_relaxed);
    g_task_rdp_cmds.fetch_add(g_bf2_task_cmds, std::memory_order_relaxed);
    for (int i = 0; i < 64; ++i) if (g_bf2_ops[i]) { g_cumulative_op_count[i].fetch_add(g_bf2_ops[i], std::memory_order_relaxed); g_bf2_ops[i] = 0; }
    g_bf2_fwd_bytes = g_bf2_fwd_subs = g_bf2_g1e_bytes = 0; g_bf2_task_bytes = g_bf2_task_cmds = 0;
}
static const bool g_bf_check = [] { const char *e = std::getenv("ROGUESQ_G1E_BUMPFAST_CHECK"); return e && *e && *e != '0'; }();
static bool g_bf_check_flag() { return g_bf_check; }
static bool rs64_bf_env(const char *n) { const char *e = std::getenv(n); return e && *e && *e != '0'; }
// Every env that arms a per-bump diagnostic or rdram-mutating block between the counters and the defer push.
static const bool g_bf_diag = [] {
    static const char *const k[] = {"ROGUESQ_LOG_ALL", "ROGUESQ_LOG_DPC", "ROGUESQ_LOG_RDP_FULLSYNC", "ROGUESQ_LOG_FS_SLOT",
        "ROGUESQ_LOG_E9_PROVENANCE", "ROGUESQ_LOG_SEQ", "ROGUESQ_FS_PIPE_INJECT", "ROGUESQ_SUPPRESS_OOB_CIMG", "ROGUESQ_PRIM_ALPHA_FF",
        "ROGUESQ_PRIM_FF"};
    for (const char *n : k) if (rs64_bf_env(n)) return true;
    return false; }();
static const bool g_bf_keep_pipe = [] { const char *e = std::getenv("ROGUESQ_DPC_KEEP_PIPE"); return !(e && *e == '0'); }();
static inline bool rs64_bf_op_ok(uint8_t op, uint32_t sz) {
    if (op == 0x3F || op == 0x29) return false;                       // CIMG checks / FULL_SYNC state (any size)
    if (sz == 16 && g_in_cine_combiner) return false;                 // 16-byte texrect log
    if (sz != 8) return true;
    switch (op) {
    case 0x22: case 0x23: case 0x24: case 0x25: case 0x2F: case 0x35: case 0x38: case 0x39: case 0x3A: case 0x3B:
    case 0x3C: case 0x3D: case 0x3E: return false;                    // shadows, combiner, texrect, image tracking
    case 0x27: return g_bf_keep_pipe;                                 // KEEP_PIPE=0 drops PIPE_SYNC
    default: return true;
    }
}
struct Rs64BfGuard {
    bool on = false, ctl = false, hit = false; uint32_t lo = 0; uint8_t *rd = nullptr; uint32_t v[24] = {}; uint8_t b[8] = {};
    void snap(uint32_t *o) const {
        int i = 0;
        o[i++] = g_last_othermode_l; o[i++] = g_last_othermode_h; o[i++] = g_last_settimg_w0; o[i++] = g_last_settimg_w1;
        o[i++] = g_last_setcimg_w0; o[i++] = g_last_setcimg_w1; o[i++] = g_last_settile_w0; o[i++] = g_last_settile_w1;
        o[i++] = g_last_fogcolor; o[i++] = g_last_primcolor; o[i++] = g_last_envcolor; o[i++] = g_last_blendcolor;
        o[i++] = g_in_pak_combiner; o[i++] = g_in_cine_combiner; o[i++] = g_task_rdp_fullsyncs.load(std::memory_order_relaxed);
        o[i++] = g_cumulative_fullsyncs.load(std::memory_order_relaxed); o[i++] = g_last_fullsync_addr.load(std::memory_order_relaxed);
        o[i++] = g_rsp_full_sync_seen.load(std::memory_order_relaxed); o[i++] = g_task_combine_total;
        o[i++] = g_cine_last_settimg_addr; o[i++] = g_cine_last_cimg_addr; o[i++] = (uint32_t)g_deferred_ranges.size();
        o[i++] = (uint32_t)g_s4272_shadow.size(); o[i++] = 0;
    }
    void arm(uint8_t *r, uint32_t l, bool c) { on = true; ctl = c; hit = false; rd = r; lo = l; snap(v); for (int i = 0; i < 8; ++i) b[i] = r[(l + i) ^ 3]; }
    void reached() {
        if (!on) return;
        on = false; uint32_t now[24]; snap(now); bool same = true;
        for (int i = 0; i < 24; ++i) if (now[i] != v[i]) same = false;
        for (int i = 0; i < 8; ++i) if (rd[(lo + i) ^ 3] != b[i]) same = false;
        if (ctl) { if (!same) ++g_rs64_bf_chk_ctl; } else { ++g_rs64_bf_chk_n; if (!same) ++g_rs64_bf_chk_bad; }
    }
    void returned_early() { if (!on) return; on = false; if (ctl) ++g_rs64_bf_chk_ctl; else { ++g_rs64_bf_chk_n; ++g_rs64_bf_chk_bad; } }
};
static Rs64BfGuard g_bf_guard;
struct Rs64BfScope { ~Rs64BfScope() { g_bf_guard.returned_early(); } };
// s7486 class EK: host-read UAF watch on the RDP side (upstream_compat.cpp rs64_s7486_hostread; no-op unless ROGUESQ_S7486_HOSTUAF
// armed it). Per newly forwarded command range: the range itself (kind 2 rdp_cmd) and, from a parse of its commands, the RDRAM source
// span of every LoadBlock / LoadTile (kind 3 rdp_tex) and LoadTLUT (kind 4) against the last SetTextureImage (state kept across calls).
extern "C" int g_rs64_s7486_on;
extern "C" void rs64_s7486_hostread(int kind, uint32_t addr, uint32_t len);
static void rs64_s7486_rdp(const uint8_t* rdram, uint32_t from, uint32_t to) {
    if (!g_rs64_s7486_on || to <= from || to - from > 0x100000u) return;
    rs64_s7486_hostread(2, from, to - from);
    static uint32_t timg = 0, tw = 1, tsiz = 2;
    for (uint32_t p = from & ~7u; p + 8u <= to;) {
        const uint32_t w0 = *(const uint32_t*)(rdram + p), w1 = *(const uint32_t*)(rdram + p + 4u), op = (w0 >> 24) & 0x3Fu;
        uint32_t n = 8u;
        if (op >= 0x08u && op <= 0x0Fu) n = 32u + ((op & 4u) ? 64u : 0u) + ((op & 2u) ? 64u : 0u) + ((op & 1u) ? 16u : 0u);
        else if (op == 0x24u || op == 0x25u) n = 16u;
        else if (op == 0x3Du) { timg = w1 & 0xFFFFFFu; tw = (w0 & 0x3FFu) + 1u; tsiz = (w0 >> 19) & 3u; }
        else if (op == 0x33u) {  // LoadBlock: sl, tl integer texels; sh = last texel
            const uint32_t sl = (w0 >> 12) & 0xFFFu, tl = w0 & 0xFFFu, sh = (w1 >> 12) & 0xFFFu;
            if (sh >= sl) rs64_s7486_hostread(3, timg + (((tl * tw + sl) << tsiz) >> 1), ((sh - sl + 1u) << tsiz) >> 1);
        } else if (op == 0x34u || op == 0x30u) {  // LoadTile / LoadTLUT: 10.2 coords
            const uint32_t uls = (w0 >> 14) & 0x3FFu, ult = (w0 >> 2) & 0x3FFu, lrs = (w1 >> 14) & 0x3FFu, lrt = (w1 >> 2) & 0x3FFu;
            const uint32_t b = timg + (((ult * tw + uls) << tsiz) >> 1), e = timg + (((lrt * tw + lrs + 1u) << tsiz) >> 1);
            if (lrt >= ult && lrs >= uls && e > b) rs64_s7486_hostread(op == 0x30u ? 4 : 3, b, e - b);
        }
        p += n;
    }
}

static void rsp_dpc_submit_impl(uint8_t* rdram, uint32_t start, uint32_t end) {
    Rs64BfScope bf_scope_;
    if (end <= start) {
        return;
    }
    g_rdram_for_submit = rdram;

    // RT64 expects RDRAM-relative addresses. Factor5 writes KSEG0 (0x80xxxxxx)
    // to DPC_START/END — mask to 24 bits.
    uint32_t start_phys = start & 0x3FFFFFF;
    uint32_t end_phys   = end   & 0x3FFFFFF;

    // The ucode emits one RDP command at a time and bumps DPC_END after each.
    // On real hardware, RDP processes [DPC_CURRENT..DPC_END) once and advances
    // CURRENT. We mirror that: only forward bytes the RT64 RDP hasn't seen yet.
    // Reset on a new DPC_START (KSEG0 base address change).
    uint32_t &s_dl_base = s_submit_dl_base;
    uint32_t &s_last_end = s_submit_last_end;

    {   // s6138: DPC window log (RDP list start/end + first bytes), 8 vs 12 MB discriminator
        static const bool s_win = []{ const char *e = std::getenv("ROGUESQ_LOG_DPCWIN"); return e && *e && *e != '0'; }();
        static int s_winn = 0, s_winhi = 0;
        if (s_win && end_phys > start_phys) {
            if (start_phys >= 0x800000u) ++s_winhi;
            if (s_winn < 40 || (s_winn % 20000) == 0) {
                uint32_t from = (start_phys != s_submit_dl_base) ? start_phys : s_submit_last_end;
                fprintf(stderr, "[dpcwin #%d] start=0x%08X end=0x%08X new=0x%06X..0x%06X hi=%d bytes=", s_winn, start, end, from, end_phys, s_winhi);
                for (uint32_t i = 0; i < 16 && from + i < 0x4000000u; ++i)
                    fprintf(stderr, "%02X", (unsigned)rdram[(from + i) ^ 3]);
                fputc('\n', stderr); fflush(stderr);
            }
            ++s_winn;
        }
    }
    if (g_rs64_s7486_on && end_phys > start_phys) {  // s7486 EK: the same "new bytes" window the forwarder uses
        const uint32_t from = (start_phys != s_dl_base) ? start_phys : s_last_end;
        if (end_phys > from) rs64_s7486_rdp(rdram, from, end_phys);
    }
    if (start_phys != s_dl_base) {
        s_dl_base = start_phys;
        s_last_end = start_phys;
    }

    if (end_phys <= s_last_end) {
        if (end_phys == s_last_end) {
            // Exactly where we left off: nothing new to forward.
            RS64_S7096_DROP(start_phys, end_phys, 6);
            return;
        }
        // END moved BACKWARDS: the ucode wrapping its RDP ring back to the
        // base. These bytes are genuine dropped content, but forwarding them
        // is NOT the answer: the forwarding path (ROGUESQ_DPC_WRAP, retired
        // 2026-07-26) re-sent already-consumed ring bytes — 53247 of 53248
        // wrap events in an 80 s run carried byte-identical content — and the
        // black screen it appeared to fix was really the missing FULL_SYNC,
        // solved by VI_FULLSYNC (session 11). Count and drop.
        static std::atomic<int> s_wrapped{0};
        int n = ++s_wrapped;
        g_last_wrap_end.store(end_phys, std::memory_order_release);
        g_last_wrap_seen.store(s_last_end, std::memory_order_release);
        g_last_wrap_start.store(start_phys, std::memory_order_release);
        g_last_wrap_n.store((uint32_t)n, std::memory_order_release);
        if (s_c4284_laps++ == 0) { s_c4284_first_lo = end_phys; s_c4284_first_hi = s_last_end; s_c4284_start = start_phys; }
        if (s_last_end > s_c4284_maxseen) s_c4284_maxseen = s_last_end;
        if (n <= 4 || (n % 4096) == 0) {
            fprintf(stderr, "[dpc-wrap #%d] end=0x%06X < seen=0x%06X start=0x%06X (dropped)\n",
                    n, end_phys, s_last_end, start_phys);
            fflush(stderr);
        }
        // s4273 ORIGIN: with the defer layer the RDP reads RDRAM at COMMIT time, so a task whose
        // ring laps (END < seen) has its lap-1 head overwritten by lap-2 before RT64 reads it, and
        // the lap-2 bumps were dropped here => lap-1 head commands are lost / replaced. Flush the
        // pending ranges to RT64 now (submit is synchronous), then restart the ring mark.
        static const bool s_wrap_flush = []{ const char *e = std::getenv("ROGUESQ_DPC_WRAP_FLUSH"); return !(e && *e == '0'); }(); /* s4549: default on (=0 disables) */
        static std::atomic<uint64_t> s_wf_n{0}, s_wf_bytes{0}, s_wf_dropped{0};
        // s7566 19d: g_defer_active is always true here (see the KEEP_PIPE note); only WRAP_FLUSH=0 reaches the drop.
        if (!(s_wrap_flush && g_defer_active)) {
            ++s_wf_dropped;
            RS64_S7096_DROP(start_phys, end_phys, 5);
            if ((n & 1023) == 1)
                fprintf(stderr, "[s4273-wrap] flush=0 wrapBumps=%llu\n", (unsigned long long)s_wf_dropped.load());
            return;
        }
        {   // s4285: at flush, is the lap-1 content RT64 is about to read already overwritten (bump-time shadow vs live)?
            static unsigned long fl = 0, flDiff = 0, flWords = 0, flDiffWords = 0, flCtl = 0;
            unsigned long d = 0, w = 0;
            static const bool s_s4285 = []{ const char *e = std::getenv("ROGUESQ_S4285"); return e && *e == '1'; }(); /* s6016: diag-only O(shadow bytes) loop per flush; default off */
            if (s_s4285 && g_rdram_for_submit) for (const S4272Sh &e : g_s4272_sh)
                for (uint32_t x = e.lo; x + 4 <= e.hi; x += 4) { uint32_t was, now; memcpy(&was, &g_s4272_shadow[e.off + (x - e.lo)], 4); /* s7364: word loop stayed inside an unaligned range */ memcpy(&now, g_rdram_for_submit + x, 4); w++; if (was != now) d++; }
            if (s_s4285) fl++; flWords += w; flDiffWords += d; if (d) flDiff++;
            { uint32_t x = 0, y = 1; flCtl += (x != y); }
            if (s_s4285 && (fl <= 8 || (fl & 63) == 0))
                fprintf(stderr, "[s4285-flush] n=%lu shRanges=%zu words=%lu diffWords=%lu | tot flushes=%lu withDiff=%lu words=%lu diff=%lu control=%lu\n", fl, g_s4272_sh.size(), w, d, fl, flDiff, flWords, flDiffWords, flCtl);
        }
        {
            uint32_t b = 0;
            /* s6016: was a linear scan of g_s4272_sh per deferred range (O(n^2), ~80% of Gfx-thread samples in s6015); first-match semantics kept via emplace */
            // s6934 G1e: ROGUESQ_G1E_TRIM default on, =0 old, =tog 10 s blocks. The map cost a node allocation per range on every flush (481 of 15203 Gfx
            // samples at dd4); a reused open-addressed table keeps the same first-match result. The trim also drops the per-triangle combiner strings in RT64.
            static const int s_trim_env = [] { const char *e = std::getenv("ROGUESQ_G1E_TRIM"); return !e ? 1 : (*e == 't' ? 2 : (*e != '0')); }();
            g_rs64_trim = s_trim_env == 2 ? (int)((time(nullptr) / 10) & 1) : s_trim_env;
            static const int s_tmem_env = [] { const char *e = std::getenv("ROGUESQ_G1E_TMEM"); return !e ? 1 : (*e == 't' ? 2 : (*e != '0')); }();
            g_rs64_tmem_fast = s_tmem_env == 2 ? (int)((time(nullptr) / 10) & 1) : s_tmem_env;
            static const int s_lbf_env = [] { const char *e = std::getenv("ROGUESQ_G1E_LBFAST"); return !e ? 1 : (*e == 't' ? 2 : (*e == 'c' ? 3 : (*e != '0'))); }();
            g_rs64_g1e_lbfast = s_lbf_env == 2 ? (int)((time(nullptr) / 10) & 1) : s_lbf_env;
            static const int s_pc_env = [] { const char *e = std::getenv("ROGUESQ_G1E_PROVCACHE"); return !e ? 0 : (*e == 't' ? 2 : (*e == 'v' ? 3 : (*e != '0'))); }();
            g_rs64_g1e_pcache = s_pc_env == 2 ? (int)((time(nullptr) / 10) & 1) : s_pc_env;
            static const int s_hg_env = [] { const char *e = std::getenv("ROGUESQ_G1E_HGATHER"); return !e ? 1 : (*e == 't' ? 2 : (*e == 'c' ? 3 : (*e == 's' ? 4 : (*e != '0')))); }();
            g_rs64_g1e_hgather = s_hg_env == 2 ? (int)((time(nullptr) / 10) & 1) : s_hg_env;
            std::unordered_map<uint64_t, const S4272Sh *> shIdx;
            static std::vector<uint64_t> shK; static std::vector<const S4272Sh *> shV; size_t shMask = 0;
            auto shSlot = [&](uint64_t k) { size_t i = (size_t)((k * 0x9E3779B97F4A7C15ull) >> 20) & shMask; while (shV[i] && shK[i] != k) i = (i + 1) & shMask; return i; };
            if (g_rs64_trim) {
                size_t cap = 16; while (cap < g_s4272_sh.size() * 2) cap <<= 1;
                shMask = cap - 1; shK.resize(cap); shV.assign(cap, nullptr);
                for (const S4272Sh &e : g_s4272_sh) { const uint64_t k = ((uint64_t)e.lo << 32) | e.hi; const size_t i = shSlot(k); if (!shV[i]) { shK[i] = k; shV[i] = &e; } }
            }
            static const bool s_tbl_chk = [] { const char *e = std::getenv("ROGUESQ_WRAP_MERGE_CHECK"); return e && *e && *e != '0'; }();
            if (!g_rs64_trim || s_tbl_chk) {
                shIdx.reserve(g_s4272_sh.size());
                for (const S4272Sh &e : g_s4272_sh) shIdx.emplace(((uint64_t)e.lo << 32) | e.hi, &e);
            }
            // s6933 G1e: a big task laps the ring ~6 times, and this flush fed RT64 one bump at a time (47k calls per task at
            // lvl1 16:9 dd4, 6 merged; 19.3 -> 17.3 ms per task sync, same run) where the commit path merges. Every per-range step below keeps its
            // order and inputs; only submit_rdp_range is held to the end of a contiguous run, with the live bytes put back after
            // it. ROGUESQ_WRAP_MERGE default on, =0 old, =tog 10 s blocks. ROGUESQ_WRAP_MERGE_CHECK=1 compares the bytes each
            // range left after its record step with what the run hands RT64; run 1 corrupts its copy as the positive control.
            static const int s_wm_env = [] { const char *e = std::getenv("ROGUESQ_WRAP_MERGE"); return !e ? 1 : (*e == 't' ? 2 : (*e != '0')); }();
            static const bool s_wm_chk = [] { const char *e = std::getenv("ROGUESQ_WRAP_MERGE_CHECK"); return e && *e && *e != '0'; }();
            const bool wm_on = s_wm_env == 2 ? ((time(nullptr) / 10) & 1) != 0 : s_wm_env != 0;
            struct WmUndo { uint32_t lo, hi; size_t off; };
            static thread_local std::vector<WmUndo> wm_undo;
            static thread_local std::vector<uint8_t> wm_live, wm_chk;
            static unsigned long wm_runs = 0, wm_ranges = 0, wm_bad = 0, wm_ctl = 0;
            uint32_t wm_lo = 0, wm_hi = 0;
            // s6936 G1e: ROGUESQ_G1E_WALK default on, =0 old, =tog 10 s blocks. With the merge on, record_submit runs once per contiguous
            // run at its flush instead of once per bump (~47k calls per task at dd4 16:9): its walkers then read whole commands, as on
            // the task-end commit path (submit_deferred_merged), where a per-bump call read triangle body words as commands. Each range
            // is restored from its shadow before the run's record, and the undo snapshot was taken before that, so RT64 gets the same
            // restored-then-edited bytes. ROGUESQ_G1D_PREWRAP_RECORD=1 keeps the old per-range order.
            static const int s_walk_env = [] { const char *e = std::getenv("ROGUESQ_G1E_WALK"); return !e ? 1 : (*e == 't' ? 2 : (*e != '0')); }();
            static const bool s_wstat = [] { const char *e = std::getenv("ROGUESQ_G1E_WALK_STAT"); return e && *e && *e != '0'; }();
            static Rs64WalkStat s_ws; static const uint64_t s_ws_ctl = rs64_walk_stat_selftest();
            static const bool s_prewrap0 = [] { const char *e = std::getenv("ROGUESQ_G1D_PREWRAP_RECORD"); return e && *e == '1'; }();
            const bool walk_on = !s_prewrap0 && (s_walk_env == 2 ? ((time(nullptr) / 10) & 1) != 0 : s_walk_env != 0);
            // s6945 G1e: ROGUESQ_G1E_COAL default on, =0 old, =tog 10 s blocks. Adjacent ranges of one merged run whose shadows are also
            // adjacent get ONE shadow->rdram memcpy + ONE "wrap" blk_dma, and adjacent undo entries merge (one live memcpy + one "unwrap"
            // at the flush), instead of one each per bump (~1M ranges/s at dd4 16:9). The pending restore is committed before anything
            // reads the run's bytes (record_submit at the flush) and before a non-adjacent range is snapshotted, so RT64 and the undo see
            // the same bytes as before. Only active on the default path (walk+merge on, no prewrap/rstat/walk-stat, which read per range).
            // ROGUESQ_G1E_COAL_CHECK=1: per run, compares the bytes record_submit is handed with the per-range expectation (shadow bytes
            // for restored ranges, live for the rest) and, after the undo, the restored ranges with their pre-restore bytes; run 1
            // corrupts its expectation as the positive control (control must be 1, bad 0).
            static const int s_coal_env = [] { const char *e = std::getenv("ROGUESQ_G1E_COAL"); return !e ? 1 : (*e == 't' ? 2 : (*e != '0')); }();
            static const bool s_coal_chk = [] { const char *e = std::getenv("ROGUESQ_G1E_COAL_CHECK"); return e && *e && *e != '0'; }();
            static const bool s_prewrap = s_prewrap0;
            static const bool s_restore = []{ const char *e = std::getenv("ROGUESQ_WRAP_RESTORE"); return !(e && *e == '0'); }(); /* s4287: default on */
            static const int s_rstat_env = [] { const char *e = std::getenv("ROGUESQ_G1E_RSTAT"); return !e ? 0 : (*e == 't' ? 2 : (*e != '0')); }();
            const bool rstat = s_rstat_env == 2 ? (bool)((time(nullptr) / 10) & 1) : (bool)s_rstat_env;
            const bool coal = (s_coal_env == 2 ? ((time(nullptr) / 10) & 1) != 0 : s_coal_env != 0) && walk_on && wm_on && !s_prewrap && !rstat && !s_wstat;
            uint32_t pr_lo = 0, pr_hi = 0; size_t pr_off = 0;
            static thread_local std::vector<uint8_t> cc_exp, cc_pre; struct CcSp { uint32_t lo, hi; size_t off; };
            static thread_local std::vector<CcSp> cc_sp; static unsigned long cc_runs = 0, cc_bad = 0, cc_ubad = 0, cc_ctl = 0, cc_merged = 0, cc_ranges = 0;
            auto commit_pr = [&] {
                if (pr_hi > pr_lo) {
                    memcpy(g_rdram_for_submit + pr_lo, &g_s4272_shadow[pr_off], pr_hi - pr_lo);
                    rs64_g1d_blk_dma("wrap", 0, pr_lo, pr_hi - pr_lo, 0);
                }
                pr_lo = pr_hi = 0;
            };
            auto wm_flush = [&] {
                commit_pr();
                const bool cc_on = s_coal_chk && coal && wm_hi > wm_lo && g_rdram_for_submit;
                if (cc_on) {
                    if (++cc_runs == 1 && !cc_exp.empty()) cc_exp[0] ^= 0xFF;
                    const bool d = cc_exp.size() != wm_hi - wm_lo || memcmp(cc_exp.data(), g_rdram_for_submit + wm_lo, cc_exp.size()) != 0;
                    if (d) { if (cc_runs == 1) ++cc_ctl; else ++cc_bad; }
                }
                if (wm_hi > wm_lo && walk_on && wm_on) {
                    rs64_dpc_record_submit(wm_lo, wm_hi);
                    if (s_wm_chk && g_rdram_for_submit) wm_chk.assign(g_rdram_for_submit + wm_lo, g_rdram_for_submit + wm_hi);
                }
                if (wm_hi > wm_lo) {
                    if (s_wm_chk && g_rdram_for_submit) {
                        if (++wm_runs == 1 && !wm_chk.empty()) wm_chk[0] ^= 0xFF;
                        const bool diff = wm_chk.size() != wm_hi - wm_lo || memcmp(wm_chk.data(), g_rdram_for_submit + wm_lo, wm_chk.size()) != 0;
                        if (diff) { if (wm_runs == 1) ++wm_ctl; else ++wm_bad; }
                        if (wm_runs <= 4 || (wm_runs & 0x3FF) == 0)
                            fprintf(stderr, "[s6933-wm] runs=%lu ranges=%lu bad=%lu control=%lu\n", wm_runs, wm_ranges, wm_bad, wm_ctl);
                    }
                    // s7532 FY: ROGUESQ_S7532_UNDO_CHK=1 (default off). gfx tasks signal sp_complete before send_dl, so the guest CPU runs
                    // while this thread holds bump-time shadow bytes in RDRAM and then writes the wm_live snapshot back (undo). A guest store
                    // into an undo range inside that window would be lost. Snapshot the bytes RT64 is handed, compare them right before the
                    // undo: a difference inside an undo range = a foreign writer in the window. Run 2 plants a flip (positive control, the
                    // undo then rewrites it with live bytes, so the plant is harmless).
                    static const bool s_uchk = [] { const char *e = std::getenv("ROGUESQ_S7532_UNDO_CHK"); return e && *e == '1'; }();
                    static thread_local std::vector<uint8_t> uc_post;
                    static unsigned long uc_runs = 0, uc_undo_runs = 0, uc_foreign = 0, uc_fbytes = 0, uc_ctl = 0, uc_any = 0;
                    static uint64_t uc_ns = 0, uc_max_ns = 0, uc_ubytes = 0;
                    const bool uc_on = s_uchk && g_rdram_for_submit;
                    std::chrono::steady_clock::time_point uc_t0;
                    if (uc_on) { uc_post.assign(g_rdram_for_submit + wm_lo, g_rdram_for_submit + wm_hi); uc_t0 = std::chrono::steady_clock::now(); }
                    rs64_rt_submit(wm_lo, wm_hi, 2);
                    if (uc_on) {
                        ++uc_runs;
                        if (!wm_undo.empty()) {
                            ++uc_undo_runs;
                            const bool plant = uc_undo_runs == 2;
                            if (plant) g_rdram_for_submit[wm_undo[0].lo] ^= 0x5A;
                            unsigned long fb = 0; bool anyd = false;
                            for (const WmUndo &u : wm_undo) {
                                uc_ubytes += u.hi - u.lo;
                                if (u.lo < wm_lo || u.hi > wm_hi) continue;
                                const uint8_t *a = g_rdram_for_submit + u.lo, *b = uc_post.data() + (u.lo - wm_lo);
                                for (uint32_t i = 0; i < u.hi - u.lo; ++i) fb += a[i] != b[i];
                            }
                            if (memcmp(g_rdram_for_submit + wm_lo, uc_post.data(), wm_hi - wm_lo) != 0) anyd = true;
                            if (plant) { if (fb) ++uc_ctl; } else if (fb) { ++uc_foreign; uc_fbytes += fb; }
                            if (!plant && anyd) ++uc_any;
                        }
                        const uint64_t ns = (uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - uc_t0).count();
                        uc_ns += ns; if (ns > uc_max_ns) uc_max_ns = ns;
                        static auto uc_last = std::chrono::steady_clock::now(); const auto uc_now = std::chrono::steady_clock::now();
                        const bool uc_tick = uc_now - uc_last >= std::chrono::seconds(5);   // time cadence: a 120 s hold has < 16k runs
                        if (uc_tick) uc_last = uc_now;
                        if (uc_runs <= 4 || uc_tick)
                            fprintf(stderr, "[s7532-undo] runs=%lu undo_runs=%lu undo_bytes=%llu foreign_runs=%lu foreign_bytes=%lu any_diff_runs=%lu control(must be 1)=%lu window_ms_total=%.1f window_us_max=%.1f\n",
                                    uc_runs, uc_undo_runs, (unsigned long long)uc_ubytes, uc_foreign, uc_fbytes, uc_any, uc_ctl, uc_ns / 1e6, uc_max_ns / 1e3);
                    }
                }
                for (const WmUndo &u : wm_undo) {
                    memcpy(g_rdram_for_submit + u.lo, wm_live.data() + u.off, u.hi - u.lo);
                    if (u.hi > u.lo) rs64_g1d_blk_dma("unwrap", 0, u.lo, u.hi - u.lo, 0);
                }
                if (cc_on) {
                    for (const CcSp &c : cc_sp) if (memcmp(g_rdram_for_submit + c.lo, cc_pre.data() + c.off, c.hi - c.lo) != 0) ++cc_ubad;
                    if (cc_runs <= 4 || (cc_runs & 0x3FFF) == 0)
                        fprintf(stderr, "[s6945-coal] runs=%lu ranges=%lu merged=%lu bad=%lu undo_bad=%lu control(must be 1)=%lu\n", cc_runs, cc_ranges, cc_merged, cc_bad, cc_ubad, cc_ctl);
                }
                cc_exp.clear(); cc_pre.clear(); cc_sp.clear();
                wm_undo.clear(); wm_live.clear(); wm_chk.clear(); wm_lo = wm_hi = 0;
            };
            rs64_g1e_bc_check("wrap");
            for (const auto &r : g_deferred_ranges) {
                if (should_drop_wrap_rdp(r.first, r.second)) { RS64_S7096_DROP(r.first, r.second, 4); continue; }
                if (wm_hi > wm_lo && wm_hi != r.first) wm_flush();
                b += r.second - r.first;
                rs64_e9prov_mark_submitted(r.first, r.second);
                // s6723: record_submit (which also rewrites RDP words: s6720 title clear, s6722 pause dim) now runs after the
                // s4286 shadow restore below, so its edits land in the bytes RT64 is fed; before, the restore overwrote them on
                // any wrap-flushed range (pause dim band back in s6723 b219 / s6722 fixb219). ROGUESQ_G1D_PREWRAP_RECORD=1 = old.
                if (s_prewrap) rs64_dpc_record_submit(r.first, r.second);
                const S4272Sh *shp = nullptr;
                if (s_restore && g_rdram_for_submit) {
                    const uint64_t k = ((uint64_t)r.first << 32) | r.second;
                    if (g_rs64_trim) shp = shV[shSlot(k)];
                    else { auto it = shIdx.find(k); if (it != shIdx.end()) shp = it->second; }
                    if (s_tbl_chk && g_rs64_trim) {  // table vs map on every lookup. Control: the first hit is also compared against a wrong key, which must differ.
                        static uint64_t tn = 0, tbad = 0, thit = 0; static int tctl = 0;
                        auto it = shIdx.find(k); const S4272Sh *ref = it != shIdx.end() ? it->second : nullptr;
                        tn++; if (ref != shp) tbad++; if (ref) thit++;
                        if (ref && !tctl && shV[shSlot(k ^ 0xFFFFFFFFull)] != ref) tctl = 1;
                        if ((tn & 0xFFFFFu) == 1) fprintf(stderr, "[s6934-tbl] n=%llu hit=%llu bad=%llu control=%d\n", (unsigned long long)tn, (unsigned long long)thit, (unsigned long long)tbad, tctl);
                    }
                }
                static unsigned long rn = 0, rMiss = 0, rWordsRestored = 0, rPostDiff = 0, rCtl = 0;
                // s6943 G1e: the two per-word compare loops below only feed the [s4286-restore] counters (~2% of Gfx-thread samples at dd4 16:9, s6943 xctrace).
                // ROGUESQ_G1E_RSTAT=1 keeps them (old behaviour), =tog 10 s blocks, default off: wordsRestored/postDiff then read 0. The restore itself is unchanged.
                if (shp && coal) {
                    const bool ext = pr_hi > pr_lo && pr_hi == r.first && pr_off + (pr_hi - pr_lo) == shp->off;
                    if (!ext) commit_pr();   // an earlier pending range may overlap r: restore it before r's live snapshot
                    const uint32_t len = r.second - r.first;
                    if (s_coal_chk) {
                        cc_sp.push_back({r.first, r.second, cc_pre.size()});
                        cc_pre.insert(cc_pre.end(), g_rdram_for_submit + r.first, g_rdram_for_submit + r.second);
                        cc_exp.insert(cc_exp.end(), g_s4272_shadow.begin() + shp->off, g_s4272_shadow.begin() + shp->off + len);
                        ++cc_ranges; cc_merged += ext;
                    }
                    if (!wm_undo.empty() && wm_undo.back().hi == r.first && wm_undo.back().off + (wm_undo.back().hi - wm_undo.back().lo) == wm_live.size())
                        wm_undo.back().hi = r.second;
                    else wm_undo.push_back({r.first, r.second, wm_live.size()});
                    wm_live.insert(wm_live.end(), g_rdram_for_submit + r.first, g_rdram_for_submit + r.second);
                    if (ext) pr_hi = r.second; else { pr_lo = r.first; pr_hi = r.second; pr_off = shp->off; }
                    rCtl += 1;
                } else if (shp) {   // s4286: feed RT64 the bump-time bytes, then put live back
                    wm_undo.push_back({r.first, r.second, wm_live.size()});
                    wm_live.insert(wm_live.end(), g_rdram_for_submit + r.first, g_rdram_for_submit + r.second);
                    if (rstat) for (uint32_t x = r.first; x + 4 <= r.second; x += 4) { uint32_t was, now; memcpy(&was, &g_s4272_shadow[shp->off + (x - r.first)], 4); /* s7364 */ memcpy(&now, g_rdram_for_submit + x, 4); if (was != now) rWordsRestored++; }
                    memcpy(g_rdram_for_submit + r.first, &g_s4272_shadow[shp->off], r.second - r.first);
                    if (r.second > r.first)
                        rs64_g1d_blk_dma("wrap", 0, r.first, r.second - r.first, 0);
                    if (rstat) for (uint32_t x = r.first; x + 4 <= r.second; x += 4) { uint32_t was, now; memcpy(&was, &g_s4272_shadow[shp->off + (x - r.first)], 4); /* s7364 */ memcpy(&now, g_rdram_for_submit + x, 4); if (was != now) rPostDiff++; }
                    rCtl += 1;
                } else if (s_restore) rMiss++;
                if (!shp && coal && s_coal_chk && g_rdram_for_submit) { commit_pr(); cc_exp.insert(cc_exp.end(), g_rdram_for_submit + r.first, g_rdram_for_submit + r.second); ++cc_ranges; }
                if (s_wstat && g_rdram_for_submit) {
                    rs64_walk_stat_range(s_ws, g_rdram_for_submit, r.first, r.second);
                    if ((s_ws.ranges & 0xFFFFFu) == 1) fprintf(stderr, "[s6936-walk] ranges=%llu mid=%llu tri_heads=%llu bytes=%llu walk=%d selftest_mid(must be 3)=%llu\n", (unsigned long long)s_ws.ranges, (unsigned long long)s_ws.mid, (unsigned long long)s_ws.tri_heads, (unsigned long long)s_ws.bytes, (int)walk_on, (unsigned long long)s_ws_ctl);
                }
                if (!s_prewrap && !(walk_on && wm_on)) rs64_dpc_record_submit(r.first, r.second);
                if (wm_hi <= wm_lo) wm_lo = r.first;
                wm_hi = r.second; ++wm_ranges;
                if (s_wm_chk && g_rdram_for_submit && !(walk_on && wm_on)) wm_chk.insert(wm_chk.end(), g_rdram_for_submit + r.first, g_rdram_for_submit + r.second);
                if (!wm_on) wm_flush();
                if (s_restore && (++rn <= 8 || (rn & (rs64_s6932_quiet() ? 0xFFFFFul : 1023ul)) == 0)) /* s6932: ~1M ranges/s at dd4 16:9 */
                    fprintf(stderr, "[s4286-restore] n=%lu restoredRanges=%lu noShadow=%lu wordsRestored=%lu postDiff(must be 0)=%lu\n", rn, rCtl, rMiss, rWordsRestored, rPostDiff);
            }
            wm_flush();
            g_deferred_ranges.clear(); g_s4272_sh.clear(); g_s4272_shadow.clear(); rs64_g1e_bc_clear();
            uint64_t k = ++s_wf_n; s_wf_bytes += b;
            if (k <= 8 || (k & 63) == 0)
                fprintf(stderr, "[s4273-wrap] flush=1 n=%llu bytes=%u totbytes=%llu\n", (unsigned long long)k, b, (unsigned long long)s_wf_bytes.load());
            s_last_end = start_phys;
        }
    }

    uint32_t submit_lo = s_last_end;
    uint32_t submit_hi = end_phys;
    s_last_end = end_phys;
    // Note: sticky last-submit is updated at the actual ultramodern::
    // submit_rdp_range call sites below (live + deferred commit), not here.
    // Updating here records the last 8-byte DPC_END bump, which is NOT the
    // range processRDPLists sees after merge/defer (s662 false correlation).

    const bool bf2 = g_rs64_bf_task_on == 2 && g_defer_active;  // s7028 arm 2: plain per-task counters
    {
        uint64_t bytes, submits;
        if (bf2) { g_bf2_dirty = true; g_bf2_fwd_bytes += submit_hi - submit_lo; ++g_bf2_fwd_subs;
                   bytes = s_fwd_bytes.load(std::memory_order_relaxed) + g_bf2_fwd_bytes; submits = s_fwd_submits.load(std::memory_order_relaxed) + g_bf2_fwd_subs; }
        else { bytes = s_fwd_bytes.fetch_add(submit_hi - submit_lo) + (submit_hi - submit_lo); submits = s_fwd_submits.fetch_add(1) + 1; }
        if ((submits % 16384) == 0) {
            rs64_diag_fprintf(stderr, "[dpc-fwd] submits=%llu bytes=%llu (%.1f MB)\n",
                    (unsigned long long)submits, (unsigned long long)bytes, bytes / 1048576.0);
            fflush(stderr);
        }
    }

    // Garbage tasks (trig data executed as DL) write junk DPC pointers; any
    // range outside 8MB RDRAM would make the diagnostics below (and RT64)
    // read OOB host memory. Drop it before the first dereference.
    if (submit_lo >= 0x1000000 || submit_hi > 0x1000000 || submit_hi <= submit_lo) { // s6135: 16 MB (was 8 MB: dropped every RDP submit above 8 MB at OSMEM>8)
        static int s_n = 0;
        if (++s_n <= 16 || (s_n & 255) == 0) {
            fprintf(stderr, "[dpc-oob-range #%d] dropping submit range 0x%08X..0x%08X\n",
                    s_n, submit_lo, submit_hi);
        }
        RS64_S7096_DROP(submit_lo, submit_hi, 3);
        if (bf2) { g_bf2_fwd_bytes -= submit_hi - submit_lo; --g_bf2_fwd_subs;   // s7028: keep the s_fwd sums equal to the atomic path's
                   s_fwd_bytes.fetch_add(submit_hi - submit_lo); s_fwd_submits.fetch_add(1); }
        return;
    }

    if (bf2) {
        g_bf2_task_bytes += submit_hi - submit_lo; g_bf2_g1e_bytes += submit_hi - submit_lo; ++g_bf2_task_cmds;
        if (g_bf_check) { g_bf2_ref_bytes.fetch_add(submit_hi - submit_lo); g_bf2_ref_cmds.fetch_add(1); if (!pthread_equal(pthread_self(), g_bf2_thr)) ++g_rs64_bf2_thr_mm; }
    } else {
    g_task_rdp_bytes.fetch_add(submit_hi - submit_lo, std::memory_order_relaxed);
    rs64_g1e_rdp_bytes.fetch_add(submit_hi - submit_lo, std::memory_order_relaxed); // s6982 G1e R-row rb= (ultramodern events.cpp)
    g_task_rdp_cmds.fetch_add(1, std::memory_order_relaxed);
    }
    // s7027 G1c (g1c-bump-fastpath): ROGUESQ_G1E_BUMPFAST=1|tog (tog = odd xor8 seconds, latched per task in rs64_dpc_defer_begin).
    // A deferred bump whose first op touches none of the state-tracking blocks below (shadows, 0x29 fullsync, 0x3C combiner,
    // 0x3D-0x3F image, 0x24/0x25 texrect, 0x27 drop when KEEP_PIPE=0) with every diagnostic env off goes straight to the defer push.
    // ROGUESQ_G1E_BUMPFAST_CHECK=1: eligible bumps take the slow path instead and a guard verifies it changed no tracked state and
    // reached the push (bad must be 0); the first 4 0x29 bumps are deliberately classed eligible (positive control: ctl must be 4).
    ++g_bf_seen;
    if (g_defer_active && g_rs64_bf_task_on && g_bf_seen > 40000u) {
        const uint32_t sz = submit_hi - submit_lo;
        const uint8_t fb0 = (uint8_t)MEM_B(0, (int64_t)(int32_t)(submit_lo + 0x80000000));
        const uint8_t fop = fb0 & 0x3F;
        bool elig = rs64_bf_op_ok(fop, sz);
        bool ctl = false;
        if (g_bf_check && !elig && fop == 0x29 && sz == 8 && g_bf_ctl_armed < 4) { elig = true; ctl = true; ++g_bf_ctl_armed; }
        if (bf2 && elig && !g_bf_check) {   // s7028 arm 2: fast path with a plain op count
            g_task_op_count[fop]++; ++g_bf2_ops[fop]; ++g_rs64_bf_fast; goto rs64_bf_push;
        }
        if (elig) {
            g_task_op_count[fop]++;
            g_cumulative_op_count[fop].fetch_add(1, std::memory_order_relaxed);
            if (!g_bf_check) { ++g_rs64_bf_fast; goto rs64_bf_push; }
            // check mode: undo the counts (the slow path below repeats them) and arm the guard
            g_task_op_count[fop]--;
            g_cumulative_op_count[fop].fetch_sub(1, std::memory_order_relaxed);
            g_bf_guard.arm(rdram, submit_lo, ctl);
        } else { ++g_rs64_bf_slow; ++g_bf_slow_op[fop]; }
    }
    {
        int64_t mips_first = (int64_t)(int32_t)(submit_lo + 0x80000000);
        uint8_t b0_first = (uint8_t)MEM_B(0, mips_first);
        uint8_t op = b0_first & 0x3F;
        if (log_e9_provenance()) {
            for (uint32_t p = submit_lo; p + 8 <= submit_hi; p += 8) {
                int64_t e9_mips = (int64_t)(int32_t)(p + 0x80000000);
                if ((uint8_t)MEM_B(0, e9_mips) == 0xE9) {
                    ++g_e9prov.emitted;
                    g_e9prov.emitted_addrs.push_back(p);
                    if (g_e9prov.first_emit == 0xFFFFFFFFu) g_e9prov.first_emit = p;
                }
            }
        }
        g_task_op_count[op]++;
        g_cumulative_op_count[op].fetch_add(1, std::memory_order_relaxed);
        // H-sync4 stop edge (item -353): any submit that covers the fixed slot.
        if (log_fs_slot()) {
            const uint32_t slot = fs_slot_addr();
            if (submit_lo <= slot && submit_hi > slot) {
                static std::atomic<uint64_t> s_slot_sub{0};
                uint64_t n = ++s_slot_sub;
                const uint32_t size = submit_hi - submit_lo;
                uint32_t w0 = ((uint32_t)(uint8_t)MEM_B(0, mips_first) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(1, mips_first) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(2, mips_first) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(3, mips_first));
                uint32_t w1 = 0;
                if (size >= 8) {
                    w1 = ((uint32_t)(uint8_t)MEM_B(4, mips_first) << 24) |
                         ((uint32_t)(uint8_t)MEM_B(5, mips_first) << 16) |
                         ((uint32_t)(uint8_t)MEM_B(6, mips_first) <<  8) |
                         ((uint32_t)(uint8_t)MEM_B(7, mips_first));
                }
                // Always log first 20 + every hit once cum_fs high (cutscene edge).
                const uint32_t cum = g_cumulative_fullsyncs.load(std::memory_order_relaxed);
                // H7: log every size-8 head_b0 change at the slot (E9↔E7 etc).
                // Submit is always on the RSP LLE path; pairs with task_delta.
                static uint8_t s_prev_slot_b0 = 0xFF;
                static int s_have_prev_b0 = 0;
                const bool b0_changed = s_have_prev_b0 && (b0_first != s_prev_slot_b0);
                const bool e9e7 = (b0_first == 0xE9 || b0_first == 0xE7 ||
                                   s_prev_slot_b0 == 0xE9 || s_prev_slot_b0 == 0xE7);
                if (b0_changed && e9e7 && size == 8) {
                    fprintf(stderr,
                        "[fs-slot] n=%llu event=slot_op_change lo=0x%08X hi=0x%08X size=%u "
                        "slot=0x%08X head_b0=%02X->%02X op=%02X w0=%08X w1=%08X "
                        "cum_fs=%u src=rsp_submit\n",
                        (unsigned long long)n, submit_lo, submit_hi, size,
                        slot, s_prev_slot_b0, b0_first, op, w0, w1, cum);
                    fflush(stderr);
                }
                if (size == 8 || submit_lo == slot) {
                    s_prev_slot_b0 = b0_first;
                    s_have_prev_b0 = 1;
                }
                if (n <= 20 || cum >= 4000 || (n % 50) == 0 || (b0_changed && e9e7)) {
                    fprintf(stderr,
                        "[fs-slot] n=%llu event=submit lo=0x%08X hi=0x%08X size=%u "
                        "slot=0x%08X head_b0=%02X op=%02X w0=%08X w1=%08X cum_fs=%u\n",
                        (unsigned long long)n, submit_lo, submit_hi, size,
                        slot, b0_first, op, w0, w1, cum);
                    fflush(stderr);
                }
            }
        }
        // H-sync4: log every range whose FIRST byte is RDP FULL_SYNC family
        // (b0&0x3F==0x29). This is exactly what runner hist[0x29]/syncs counts.
        // size==8 path below also updates g_last_fullsync_addr; multi-cmd heads
        // inflate hist without refreshing last_addr (sticky-fs risk).
        if (log_rdp_fullsync() && op == 0x29) {
            static std::atomic<uint64_t> s_fs_head{0};
            uint64_t n = ++s_fs_head;
            const uint32_t size = submit_hi - submit_lo;
            // Always log: first 40 (boot/hangar control), every head during the
            // late dual-DL window (n large), and the edge into starvation.
            // Cap mid-run noise: after 40, log every 25th until cumulative
            // fullsyncs >= 4000, then every submit (cutscene/plateau).
            const uint32_t cum = g_cumulative_fullsyncs.load(std::memory_order_relaxed);
            const bool log_this = (n <= 40) || (cum >= 4000) || ((n % 25) == 0);
            if (log_this) {
                uint32_t w0 = ((uint32_t)(uint8_t)MEM_B(0, mips_first) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(1, mips_first) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(2, mips_first) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(3, mips_first));
                uint32_t w1 = 0;
                if (size >= 8) {
                    w1 = ((uint32_t)(uint8_t)MEM_B(4, mips_first) << 24) |
                         ((uint32_t)(uint8_t)MEM_B(5, mips_first) << 16) |
                         ((uint32_t)(uint8_t)MEM_B(6, mips_first) <<  8) |
                         ((uint32_t)(uint8_t)MEM_B(7, mips_first));
                }
                fprintf(stderr,
                    "[rdp-fullsync] n=%llu kind=head addr=0x%08X b0=%02X size=%u "
                    "w0=%08X w1=%08X cum_fs=%u\n",
                    (unsigned long long)n, submit_lo, b0_first, size, w0, w1, cum);
                fflush(stderr);
            }
        }
        // Full-range walk (ROGUESQ_LOG_DPC=1): the first-command histogram
        // above misses commands bundled after the head of a multi-command
        // submit. TEXRECT/TEXRECTFLIP are 16 bytes, everything else 8.
        if (log_dpc()) {
            static std::atomic<uint32_t> s_full_hist[64];
            static std::atomic<uint64_t> s_walk_dumps{0};
            static uint32_t s_last_timg = 0;
            static std::atomic<int> s_tex_dumps{0};
            for (uint32_t p = submit_lo; p + 8 <= submit_hi; ) {
                int64_t mp = (int64_t)(int32_t)(p + 0x80000000);
                uint8_t wop = (uint8_t)MEM_B(0, mp) & 0x3F;
                s_full_hist[wop].fetch_add(1, std::memory_order_relaxed);
                if (wop == 0x3D) { // SETTIMG: remember source addr
                    s_last_timg = (((uint32_t)(uint8_t)MEM_B(4, mp) << 24) |
                                   ((uint32_t)(uint8_t)MEM_B(5, mp) << 16) |
                                   ((uint32_t)(uint8_t)MEM_B(6, mp) <<  8) |
                                   ((uint32_t)(uint8_t)MEM_B(7, mp))) & 0x7FFFFF;
                } else if (wop == 0x33 && s_last_timg) { // LOADBLOCK: dump source pixels
                    int n2 = ++s_tex_dumps;
                    if (n2 <= 6 || n2 == 100 || n2 == 400) {
                        fprintf(stderr, "[tex-src #%d] timg=0x%06X:", n2, s_last_timg);
                        for (int i = 0; i < 32; ++i)
                            fprintf(stderr, " %02X", (unsigned)rdram[s_last_timg + i]);
                        fprintf(stderr, "\n");
                        fflush(stderr);
                    }
                }
                p += (wop == 0x24 || wop == 0x25) ? 16 : 8;
            }
            uint64_t n = ++s_walk_dumps;
            if ((n & 1023) == 0) {
                fprintf(stderr, "[full-hist @%llu]", (unsigned long long)n);
                for (int i = 0; i < 64; ++i) {
                    uint32_t c = s_full_hist[i].load(std::memory_order_relaxed);
                    if (c) fprintf(stderr, " op%02X=%u", i, c);
                }
                fprintf(stderr, "\n");
                fflush(stderr);
            }
        }
        // ORDERED command-sequence trace (ROGUESQ_LOG_SEQ=1). The [full-hist]
        // walker above counts opcodes but loses their ORDER, and order is what
        // decides whether the texrects we know reach the GPU are subsequently
        // painted over. Prints every command in submit order with the geometry
        // of the ops that can cover the screen (FILLRECT, TEXRECT) and the
        // render target they land in (SETCIMG). Capped so a soak stays usable.
        if ([]{
                static const bool v = []{
                    const char *e = std::getenv("ROGUESQ_LOG_SEQ");
                    return e && *e && *e != '0';
                }();
                return v;
            }()) {
            static std::atomic<int> s_seq_lines{0};
            static const int s_seq_max = []{
                const char *e = std::getenv("ROGUESQ_LOG_SEQ_MAX");
                int v = e ? atoi(e) : 0;
                return v > 0 ? v : 6000;
            }();
            static uint32_t s_seq_fillcolor = 0;
            for (uint32_t p = submit_lo; p + 8 <= submit_hi; ) {
                int64_t mp = (int64_t)(int32_t)(p + 0x80000000);
                uint32_t w0 = ((uint32_t)(uint8_t)MEM_B(0, mp) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(1, mp) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(2, mp) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(3, mp));
                uint32_t w1 = ((uint32_t)(uint8_t)MEM_B(4, mp) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(5, mp) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(6, mp) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(7, mp));
                uint8_t wop = (uint8_t)(w0 >> 24) & 0x3F;
                if (wop == 0x37) s_seq_fillcolor = w1;
                int line = ++s_seq_lines;
                if (line <= s_seq_max) {
                    // 10.2 fixed-point rect corners, shared by FILLRECT/TEXRECT.
                    const unsigned xl = (w0 >> 12) & 0xFFF, yl = w0 & 0xFFF;
                    const unsigned xh = (w1 >> 12) & 0xFFF, yh = w1 & 0xFFF;
                    switch (wop) {
                    case 0x3F:
                        fprintf(stderr, "[seq %d] SETCIMG addr=0x%06X fmt=%u siz=%u w=%u\n",
                                line, w1 & 0x7FFFFF, (w0 >> 21) & 7, (w0 >> 19) & 3,
                                (w0 & 0xFFF) + 1);
                        break;
                    case 0x36:
                        fprintf(stderr, "[seq %d] FILLRECT (%u,%u)-(%u,%u) fill=0x%08X\n",
                                line, xh >> 2, yh >> 2, xl >> 2, yl >> 2, s_seq_fillcolor);
                        break;
                    case 0x24: case 0x25:
                        fprintf(stderr, "[seq %d] TEXRECT%s (%u,%u)-(%u,%u) tile=%u\n",
                                line, wop == 0x25 ? "FLIP" : "",
                                xh >> 2, yh >> 2, xl >> 2, yl >> 2, (w1 >> 24) & 7);
                        break;
                    case 0x37:
                        fprintf(stderr, "[seq %d] SETFILLCOLOR 0x%08X\n", line, w1);
                        break;
                    case 0x2D:
                        fprintf(stderr, "[seq %d] SETSCISSOR (%u,%u)-(%u,%u)\n",
                                line, xl >> 2, yl >> 2, xh >> 2, yh >> 2);
                        break;
                    case 0x2F:
                        fprintf(stderr, "[seq %d] SETOTHERMODE 0x%08X 0x%08X\n", line, w0, w1);
                        break;
                    case 0x3C:
                        fprintf(stderr, "[seq %d] SETCOMBINE 0x%08X 0x%08X\n", line, w0, w1);
                        break;
                    case 0x29:
                        fprintf(stderr, "[seq %d] FULLSYNC\n", line);
                        break;
                    default:
                        fprintf(stderr, "[seq %d] op%02X 0x%08X 0x%08X\n", line, wop, w0, w1);
                        break;
                    }
                    if (line == s_seq_max) {
                        fprintf(stderr, "[seq] cap %d reached, further commands suppressed\n",
                                s_seq_max);
                    }
                    fflush(stderr);
                }
                p += (wop == 0x24 || wop == 0x25) ? 16 : 8;
            }
        }

        // Track all SET_COLOR_IMAGE addresses (op 0x3F = G_SETCIMG mask) so
        // we can compare them against VI_ORIGIN to diagnose visual gaps.
        if (op == 0x3F) {
            uint32_t w1 = ((uint32_t)(uint8_t)MEM_B(4, mips_first) << 24) |
                          ((uint32_t)(uint8_t)MEM_B(5, mips_first) << 16) |
                          ((uint32_t)(uint8_t)MEM_B(6, mips_first) <<  8) |
                          ((uint32_t)(uint8_t)MEM_B(7, mips_first));
            static std::atomic<int> s_set_count{0};
            int n = ++s_set_count;
            if (n <= 16 || (n & 63) == 0) {
                fprintf(stderr, "[set-cimg #%d] addr=0x%08X (phys=0x%06X)\n",
                        n, w1, w1 & 0x00FFFFFF);
                fflush(stderr);
            }
        }
    }

    // EARLY DUMP: capture RDRAM at MIPS 0x4B7800 + DMEM at the first few
    // submit_rdp_range calls. Lets us compare to PJ64's first-explosion screenshot
    // (which captures cinematic data well before the freeze). Tags numbered so we
    // know which submission produced each dump.
    {
        static std::atomic<uint32_t> s_early_dump{0};
        uint32_t n = ++s_early_dump;
        // Dump at submission counts spanning boot → late cinematic. The 9A C2 C2 C2
        // pattern doesn't appear in early dumps (#1, #50, #200, #1000 all-zero),
        // so we sample farther out to find when it first emerges.
        if (n == 1 || n == 1000 || n == 3000 || n == 6000 || n == 10000 ||
            n == 15000 || n == 20000 || n == 25000 || n == 30000) {
            fprintf(stderr, "[early-dump #%u] RDRAM 0x4B7800-0x4B7900 host order:\n", n);
            for (uint32_t row = 0; row < 16; ++row) {
                uint32_t base = 0x4B7800u + row * 16;
                fprintf(stderr, "  %08X:", base);
                for (uint32_t col = 0; col < 16; ++col) {
                    fprintf(stderr, " %02X", (unsigned)rdram[base + col]);
                }
                fprintf(stderr, "\n");
            }
            fprintf(stderr, "[early-dump #%u] DMEM 0x170-0x1C0 host order:\n", n);
            for (uint32_t row = 0; row < 5; ++row) {
                uint32_t base = 0x170u + row * 16;
                fprintf(stderr, "  %03X:", base);
                for (uint32_t col = 0; col < 16; ++col) {
                    fprintf(stderr, " %02X", (unsigned)g_dmem_cur[base + col]);
                }
                fprintf(stderr, "\n");
            }
            fflush(stderr);
        }
    }

    // OOB-CIMG: catch G_SETCIMG (byte 0 == 0xFF EXACTLY) with bogus addr OR width.
    // Originally only fired for size==8 submissions; extended 2026-05-08 to
    // scan first 8 bytes of any submission (catches CIMGs at the head of
    // multi-command batches too). Width-bogus branch added for the iter-810
    // 600 MB allocation spike investigation — see CIMG-width-filter plan.
    //
    // Three categories of bogus CIMG:
    //   addr >= 0x800000  : past 8MB RDRAM (typical: 0x00FFFFFF garbage)
    //   addr <  0x100000  : in asset/code region, not framebuffer space
    //                       (typical: 0x00008FFD, 0x00001FFE, 0x00003B83)
    //   width >  640      : impossible (lo-res 320, hi-res 640).
    //                       Observed: 3846, 7888, 7934 — clearly garbage
    //                       interpretation, NOT real fb dimensions.
    //
    // The "segHigh" field is the high byte of the unmasked w1 — if non-zero,
    // it's a segment index (real RDP would resolve via segments[]). Tells us
    // whether we're misinterpreting raw bytes vs. failing to do segment
    // resolution on a real game-emitted CIMG.
    if ((submit_hi - submit_lo) >= 8) {
        int64_t mips = (int64_t)(int32_t)(submit_lo + 0x80000000);
        uint8_t b0w = (uint8_t)MEM_B(0, mips);
        if (b0w == 0xFF) {  // strict G_SETCIMG opcode match
            uint32_t w0w = ((uint32_t)(uint8_t)MEM_B(0, mips) << 24) |
                           ((uint32_t)(uint8_t)MEM_B(1, mips) << 16) |
                           ((uint32_t)(uint8_t)MEM_B(2, mips) <<  8) |
                           ((uint32_t)(uint8_t)MEM_B(3, mips));
            uint32_t w1w = ((uint32_t)(uint8_t)MEM_B(4, mips) << 24) |
                           ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                           ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                           ((uint32_t)(uint8_t)MEM_B(7, mips));
            uint32_t addr24 = w1w & 0x00FFFFFF;
            uint8_t  segHigh = (uint8_t)((w1w >> 24) & 0xFF);
            // Width is encoded in bits 0-11 of w0 as (width-1).
            uint16_t cimg_width = (uint16_t)((w0w & 0xFFFu) + 1);
            const bool oob_high  = (addr24 >= 0x01000000u);
            const bool oob_low   = (addr24 < 0x00100000u && addr24 != 0);
            const bool oob_width = (cimg_width > 640u);
            (void)segHigh;
            if (oob_high || oob_low || oob_width) {
                static std::atomic<uint64_t> s_oob{0};
                static std::atomic<uint32_t> s_oob_low{0};
                static std::atomic<uint32_t> s_oob_width{0};
                uint64_t n = ++s_oob;
                bool log_low   = oob_low && (++s_oob_low <= 30);
                bool log_high  = oob_high && (n == 1 || (n & (n - 1)) == 0);
                bool log_width = oob_width && (++s_oob_width <= 40);
                if (log_low || log_high || log_width) {
                    const char *region = oob_width ? "WIDTH"
                                       : oob_high  ? "HIGH"
                                       : "LOW";
                    uint32_t submit_size = submit_hi - submit_lo;
                    fprintf(stderr,
                        "[cimg-oob-1] #%llu region=%s slot=%d dl=0x%08X size=%u w0=0x%08X w1=0x%08X addr24=0x%06X w=%u segHigh=0x%02X\n",
                        (unsigned long long)n, region, g_cine_current_slot,
                        (unsigned)submit_lo | 0x80000000u, submit_size, w0w, w1w, addr24, (unsigned)cimg_width, (unsigned)segHigh);
                    // Dump 72 bytes context (32 before + cmd + 32 after) around the
                    // submission's source byte. Tells us whether the bogus CIMG is:
                    //   (a) A real game-emitted command (addr next to legit DL ops)
                    //   (b) Garbage past a short DL (preceded by FULL_SYNC + zeros)
                    //   (c) Trailing pixel data (preceded by triangle/texrect bytes)
                    // 32-byte pre-window picks up the typical 4-cmd lead-in patterns
                    // that a single emit-helper would produce; helps grep against
                    // RecompiledFuncs/funcs_*.c for the owning function.
                    if (log_low || log_width) {
                        int64_t pre  = (int64_t)(int32_t)((submit_lo - 32) + 0x80000000);
                        int64_t post = (int64_t)(int32_t)((submit_lo +  8) + 0x80000000);
                        fprintf(stderr,
                            "  [ctx] pre32:");
                        for (int i = 0; i < 32; ++i) fprintf(stderr, " %02X", (unsigned)(uint8_t)MEM_B(i, pre));
                        fprintf(stderr, "  cmd:");
                        for (int i = 0; i < 8;  ++i) fprintf(stderr, " %02X", (unsigned)(uint8_t)MEM_B(i, mips));
                        fprintf(stderr, "  post32:");
                        for (int i = 0; i < 32; ++i) fprintf(stderr, " %02X", (unsigned)(uint8_t)MEM_B(i, post));
                        fprintf(stderr, "\n");
                    }
                    fflush(stderr);
                }
                // ONE-SHOT MEMORY DUMP at first OOB. RDRAM at MIPS 0x4B7800 + DMEM
                // (the RSP's local memory). Lets us compare to PJ64 screenshots:
                //  - If our DMEM matches PJ64's at a similar frame → RSP recompile is
                //    fine, the dpc_bridge interpretation differs.
                //  - If our DMEM diverges structurally (uniform vs varied) → RSP bug.
                {
                    static std::atomic<bool> s_dumped{false};
                    bool expected = false;
                    if (s_dumped.compare_exchange_strong(expected, true)) {
                        fprintf(stderr, "[mem-dump-4B7800] 256 bytes (host order, MIPS 0x4B7800-0x4B7900):\n");
                        for (uint32_t row = 0; row < 16; ++row) {
                            uint32_t base = 0x4B7800u + row * 16;
                            fprintf(stderr, "  %08X:", base);
                            for (uint32_t col = 0; col < 16; ++col) {
                                fprintf(stderr, " %02X", (unsigned)rdram[base + col]);
                            }
                            fprintf(stderr, "\n");
                        }
                        // Dump DMEM contents at the same moment.
                        fprintf(stderr, "[mem-dump-DMEM] 1KB (host order, DMEM 0x000-0x400):\n");
                        for (uint32_t row = 0; row < 64; ++row) {
                            uint32_t base = row * 16;
                            fprintf(stderr, "  %03X:", base);
                            for (uint32_t col = 0; col < 16; ++col) {
                                fprintf(stderr, " %02X", (unsigned)g_dmem_cur[base + col]);
                            }
                            fprintf(stderr, "\n");
                        }
                        fflush(stderr);
                    }
                }
            }
        }
    }

    // PIPESYNC FILTER: Factor5 emits PIPESYNC (op_int 0x27) very heavily.
    // RT64 implicitly maintains pipeline coherence; per-cmd PIPESYNC floods
    // the action_queue. Keep LOADSYNC (0x26), TILESYNC (0x28), FULLSYNC (0x29).
    //
    // ROGUESQ_FS_PIPE_INJECT (default OFF): when a size-8 submit hits the dual
    // sticky FULL_SYNC staging cell (phys default 0x76DF60 = ROGUESQ_FS_SLOT_ADDR)
    // *and* that cell is still g_last_fullsync_addr, queue a synthetic FULL_SYNC
    // from host-owned scratch phys 0x7FFF80 whenever the cell is no longer a
    // real FULL_SYNC (E9). Post-exit the RSP overwrites the cell E9→E7→F3/FD/F5
    // while dual DLs keep re-submitting it; without inject, runner hist[0x29]/
    // syncs and RT64 fullSync starve while GFX continues (H-sync4 / -355..-357).
    //
    // s587 r1: last_fullsync_addr alone flooded mid-boot staging (H8c).
    // Gate mode 1 = fs_slot ∩ last_fs; mode 2 = last_fs-only (A/B only).
    // s587 r2: mutating the sticky cell to E9 in place correlated with UJ 2080.
    // Non-mutating path: permanent E9 at 0x7FFF80; leave guest cell alone.
    // s588 H9d: extend beyond PIPE — F3/FD/F5 size-8 at the same gate also
    // inject + drop (forward residual correlated with UJ; drop-return GREEN).
    if ((submit_hi - submit_lo) == 8) {
        int64_t mips = (int64_t)(int32_t)(submit_lo + 0x80000000);
        uint8_t b0 = (uint8_t)MEM_B(0, mips);
        const uint8_t op6_head = (uint8_t)(b0 & 0x3F);

        static const int s_pipe_inject = []{
            const char *e = std::getenv("ROGUESQ_FS_PIPE_INJECT");
            if (!e || !*e || *e == '0') return 0;
            if (*e == '2') return 2;
            return 1;
        }();
        const uint32_t last_fs =
            g_last_fullsync_addr.load(std::memory_order_acquire);
        const uint32_t slot = fs_slot_addr();
        const bool at_last = (last_fs != 0xFFFFFFFFu && submit_lo == last_fs);
        const bool at_slot = (submit_lo == slot);
        const bool gate_inject =
            (s_pipe_inject == 2 && at_last) ||
            (s_pipe_inject == 1 && at_last && at_slot);

        // Shared synth FULL_SYNC from host scratch. Returns true if queued.
        // replace_pipe_hist: when dropping a PIPE, fix 0x27→0x29 hist counts.
        auto inject_synth_fullsync = [&](bool replace_pipe_hist) -> bool {
            if (!gate_inject || s_pipe_inject == 0) return false;
            constexpr uint32_t kSynthFsPhys = 0x7FFF80u;
            static bool s_synth_inited = false;
            if (!s_synth_inited) {
                int64_t sm = (int64_t)(int32_t)(kSynthFsPhys + 0x80000000);
                MEM_B(0, sm) = (int8_t)0xE9;
                MEM_B(1, sm) = 0;
                MEM_B(2, sm) = 0;
                MEM_B(3, sm) = 0;
                MEM_B(4, sm) = 0;
                MEM_B(5, sm) = 0;
                MEM_B(6, sm) = 0;
                MEM_B(7, sm) = 0;
                s_synth_inited = true;
            }
            if (replace_pipe_hist) {
                if (g_task_op_count[0x27] > 0) {
                    g_task_op_count[0x27]--;
                }
                uint32_t prev =
                    g_cumulative_op_count[0x27].load(std::memory_order_relaxed);
                if (prev > 0) {
                    g_cumulative_op_count[0x27].store(
                        prev - 1, std::memory_order_relaxed);
                }
            }
            g_task_op_count[0x29]++;
            g_cumulative_op_count[0x29].fetch_add(1, std::memory_order_relaxed);
            g_rsp_full_sync_seen.store(true, std::memory_order_release);
            g_task_rdp_fullsyncs.fetch_add(1, std::memory_order_relaxed);
            g_cumulative_fullsyncs.fetch_add(1, std::memory_order_relaxed);
            // Keep last_fullsync_addr on the sticky slot so subsequent
            // filters still match; do not point it at the scratch.
            if (g_defer_active) {
                g_deferred_ranges.emplace_back(kSynthFsPhys, kSynthFsPhys + 8); ++g_rs64_g1e_ranges;
                if (g_bc_on) g_bc_ranges.emplace_back(kSynthFsPhys, kSynthFsPhys + 8);
            } else {
                rs64_rt_submit(kSynthFsPhys, kSynthFsPhys + 8, 4);
            }
            static std::atomic<uint64_t> s_inject_n{0};
            uint64_t in = ++s_inject_n;
            if (in <= 20 || (in % 50) == 0) {
                fprintf(stderr,
                    "[fs-pipe-inject] n=%llu addr=0x%08X last_fs=0x%08X "
                    "slot=0x%08X synth=0x%08X mode=%d b0=%02X defer=%d "
                    "task_cmds=%u\n",
                    (unsigned long long)in, submit_lo, last_fs, slot,
                    kSynthFsPhys, s_pipe_inject, b0,
                    g_defer_active ? 1 : 0,
                    g_task_rdp_cmds.load(std::memory_order_relaxed));
                fflush(stderr);
            }
            return true;
        };

        // s4272 ORIGIN: bump-time content of an 8-byte submit is a PLACEHOLDER (the ucode bumps
        // DPC_END before its output DMA lands; the slot is later overwritten with triangle data).
        // A bump-time E7 can therefore be the future middle of a triangle; dropping it deletes 8
        // bytes of coefficients and desyncs the RDP walker. RT64 treats E7 as a no-op anyway.
        static const bool s_keep_pipe = []{ const char *e = std::getenv("ROGUESQ_DPC_KEEP_PIPE"); return !(e && *e == '0'); }();  // default ON; =0 restores the old drop
        // s7566 19d: every DPC_END site is gfx ucode run inside rs64_dpc_defer_begin/_end (main.cpp factor5_gfx_runner), so
        // g_defer_active is true at every bump and this drop runs only under KEEP_PIPE=0 (L1 dd1: 0 pipe drops by default).
        if (op6_head == 0x27 && !(s_keep_pipe && g_defer_active)) {
            if (inject_synth_fullsync(/*replace_pipe_hist=*/true)) {
                RS64_S7096_DROP(submit_lo, submit_hi, 0);
                return; // drop the PIPE; synth FULL_SYNC already queued
            }
            (void)rdram;
            RS64_S7096_DROP(submit_lo, submit_hi, 0);
            return; // drop PIPE always
        }
        // Residual non-FULL_SYNC size-8 at sticky slot (F3/FD/F5…): same
        // control flow as PIPE — inject synth FS and DROP the size-8. The
        // cell is RSP scratch reused after E9; main dual DLs carry real
        // SETTIMG/SETTILE. s588 r2 forward-then-continue correlated with
        // UJ 0xA8A9 at task ~5880 (same family as s587 r2 in-place rewrite);
        // E7 drop-return path did not.
        if (op6_head != 0x29 && gate_inject) {
            if (inject_synth_fullsync(/*replace_pipe_hist=*/false)) {
                RS64_S7096_DROP(submit_lo, submit_hi, 1);
                return;
            }
        }
        if (op6_head == 0x29) {
            // FULL_SYNC marks the end of a frame's RDP work — on real hw
            // it raises DP interrupt and the CPU halts the RSP. We don't
            // halt externally, so signal the ucode dispatcher to break out.
            g_rsp_full_sync_seen.store(true, std::memory_order_release);
            g_task_rdp_fullsyncs.fetch_add(1, std::memory_order_relaxed);
            g_cumulative_fullsyncs.fetch_add(1, std::memory_order_relaxed);
            g_last_fullsync_addr.store(submit_lo, std::memory_order_release);
            // Count FULL_SYNC bytes submitted. Compare to State::fullSync
            // count to see if RT64 is observing every one we send.
            static std::atomic<uint64_t> s_fs{0};
            uint64_t n = ++s_fs;
            if (log_dpc() && (n <= 8 || (n & 31) == 0)) {
                fprintf(stderr, "[dpc] FULL_SYNC byte sent #%llu\n",
                    (unsigned long long)n);
                fflush(stderr);
            }
            // size==8 path is the only site that refreshes g_last_fullsync_addr.
            // kind=single distinguishes from kind=head (hist) above.
            if (log_rdp_fullsync()) {
                const uint32_t cum = g_cumulative_fullsyncs.load(std::memory_order_relaxed);
                const bool log_this = (n <= 40) || (cum >= 4000) || ((n % 25) == 0);
                if (log_this) {
                    uint32_t w0 = ((uint32_t)(uint8_t)MEM_B(0, mips) << 24) |
                                  ((uint32_t)(uint8_t)MEM_B(1, mips) << 16) |
                                  ((uint32_t)(uint8_t)MEM_B(2, mips) <<  8) |
                                  ((uint32_t)(uint8_t)MEM_B(3, mips));
                    uint32_t w1 = ((uint32_t)(uint8_t)MEM_B(4, mips) << 24) |
                                  ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                                  ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                                  ((uint32_t)(uint8_t)MEM_B(7, mips));
                    fprintf(stderr,
                        "[rdp-fullsync] n=%llu kind=single addr=0x%08X b0=%02X size=8 "
                        "w0=%08X w1=%08X cum_fs=%u\n",
                        (unsigned long long)n, submit_lo, b0, w0, w1, cum);
                    fflush(stderr);
                }
            }
        }
        // SET_COLOR/DEPTH/TEXTURE_IMAGE tracer. Confirmed Factor5 LLE cycles a
        // small (A,B,C) tuple set forever; addFramebufferPair now dedupes
        // search-all by tuple, so per-call printing is no longer useful. Keep
        // the first few prints as a smoke test that the byte stream still has
        // the expected shape.
        uint8_t op6 = b0 & 0x3F;
        // Shadow the most recent state-set commands so the 64-tri particle
        // mux entry log can dump the full draw context. Cheap (always-on).
        if (op6 == 0x22 || op6 == 0x23 || op6 == 0x2F ||
            op6 == 0x3D || op6 == 0x3F || op6 == 0x35 ||
            op6 == 0x38 || op6 == 0x39 || op6 == 0x3A || op6 == 0x3B) {
            uint32_t w0_now = ((uint32_t)(uint8_t)MEM_B(0, mips) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(1, mips) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(2, mips) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(3, mips));
            uint32_t w1_now = ((uint32_t)(uint8_t)MEM_B(4, mips) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(7, mips));
            switch (op6) {
                case 0x22: g_last_othermode_l = w1_now; break;
                case 0x23: g_last_othermode_h = w1_now; break;
                case 0x2F: g_last_othermode_h = w0_now; g_last_othermode_l = w1_now; break;
                case 0x3D: g_last_settimg_w0 = w0_now; g_last_settimg_w1 = w1_now; break;
                case 0x3F: g_last_setcimg_w0 = w0_now; g_last_setcimg_w1 = w1_now; break;
                case 0x35: g_last_settile_w0 = w0_now; g_last_settile_w1 = w1_now; break;
                case 0x38: g_last_fogcolor = w1_now; break;
                case 0x39: g_last_blendcolor = w1_now; break;
                case 0x3A: g_last_primcolor = w1_now; break;
                case 0x3B: g_last_envcolor = w1_now; break;
            }
        }
        // G_SETPRIMCOLOR (0xFA, masked to 0x3A) and G_SETENVCOLOR (0xFB,
        // masked to 0x3B): log the RGBA values being loaded. PRIM modulates
        // TEXEL in many Factor5 combiner modes; if PRIM RGBA is dimmer than
        // expected (e.g. 0xC0 instead of 0xFF) this could explain residual
        // saturation gap from ideal.
        if (op6 == 0x3A || op6 == 0x3B) {
            static std::atomic<uint64_t> s_prim{0}, s_env{0};
            uint32_t w1 = ((uint32_t)(uint8_t)MEM_B(4, mips) << 24) |
                          ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                          ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                          ((uint32_t)(uint8_t)MEM_B(7, mips));
            uint64_t n = (op6 == 0x3A) ? ++s_prim : ++s_env;
            if (log_dpc() && (n <= 12 || n == 100 || n == 1000)) {
                const char *name = (op6 == 0x3A) ? "PRIM" : "ENV";
                fprintf(stderr, "[dpc] G_SET%s_COLOR #%llu RGBA=%02X %02X %02X %02X (w1=0x%08X)\n",
                    name, (unsigned long long)n,
                    (w1 >> 24) & 0xFF,
                    (w1 >> 16) & 0xFF,
                    (w1 >>  8) & 0xFF,
                    (w1 >>  0) & 0xFF,
                    w1);
                fflush(stderr);
            }
            // ROGUESQ_PRIM_ALPHA_FF=1 — diagnostic: force PRIM alpha to 0xFF.
            // The attribution text's combiner is TEXEL0*PRIM with alpha taken
            // straight from PRIM, and PRIM alpha is observed at only two values
            // (0x08 and 0xFE) — so for most frames the text is drawn at ~3%
            // opacity over a black clear and is effectively invisible. This
            // tells apart "the fade value is wrong/stuck" from "the text is
            // not being drawn".
            if (op6 == 0x3A) {
                static const bool alpha_full = []() {
                    const char *e = std::getenv("ROGUESQ_PRIM_ALPHA_FF");
                    return e && *e && *e != '0';
                }();
                if (alpha_full) {
                    // `mips` is this command's KSEG0 address; the alpha byte is
                    // w1's low byte, i.e. offset 7. (Note the pre-existing
                    // ROGUESQ_PRIM_FF block below pokes `submit_lo + n`, the
                    // base of the whole submit range rather than this command —
                    // that looks wrong, but it is off by default and untouched.)
                    const uint32_t off = (uint32_t)mips & 0xFFFFFF;
                    if (off + 8 <= 0x1000000) {
                        rdram[(off + 7) ^ 3] = 0xFF;
                    }
                }
            }

            // ROGUESQ_PRIM_FF: experimental override — force PRIM_COLOR to
            // (FF,FF,FF, original_alpha). Tests whether the (EB,E1,D7) warm
            // off-white tint we observed accounts for the residual "less
            // saturated reds" gap from ideal-initial.PNG.
            if (op6 == 0x3A) {
                static const bool prim_full = []() {
                    const char *e = std::getenv("ROGUESQ_PRIM_FF");
                    return e && *e && *e != '0';
                }();
                if (prim_full) {
                    uint8_t a = (w1 >> 0) & 0xFF;
                    // Skip the engine-glow outlier so we don't make orange flames white
                    bool is_glow = ((w1 >> 24) & 0xFF) < 0xC0 ||
                                   ((w1 >> 8) & 0xFF) < 0x40;
                    if (!is_glow) {
                        // Rewrite PRIM RGB to FF FF FF, keep alpha + alpha-only path
                        // (rdram bytes 4-7) — write back via direct rdram poke
                        int64_t mips_w1_lo = mips + 4;
                        // High byte of w1 is at offset 4
                        // Order: w1 bytes are at offsets 4..7 in big-endian.
                        // But MEM_B is endian-aware; let's set w1 directly as ulong
                        // and convert. Use the SAME MEM_B-style writes.
                        // For Big-endian w1: byte4=R(MSB), byte5=G, byte6=B, byte7=A.
                        // Replace bytes 4,5,6 with 0xFF.
                        // (We can't easily write through MEM_B without macro, so use rdram.)
                        // submit_lo is RDRAM-relative byte offset.
                        uint8_t *p = rdram + (submit_lo ^ 0);  // RDRAM is byte-swapped: index ^ 3
                        // RDRAM is stored little-endian internally? Use MIPS XOR-3 idiom.
                        rdram[(submit_lo + 4) ^ 3] = 0xFF;
                        rdram[(submit_lo + 5) ^ 3] = 0xFF;
                        rdram[(submit_lo + 6) ^ 3] = 0xFF;
                        // alpha (offset 7) preserved
                        static std::atomic<uint64_t> s_overridden{0};
                        uint64_t v = ++s_overridden;
                        if (v <= 3) {
                            fprintf(stderr, "[dpc] PRIM override -> FF FF FF %02X (#%llu)\n",
                                a, (unsigned long long)v);
                            fflush(stderr);
                        }
                    }
                }
            }
        }
        // G_SETCOMBINE (0xFC, masked to 0x3C): log first few combiner modes
        // task #256 (memory module) sets the combiner 161 times per task.
        // Combiner modes determine pixel-level color compositing — relevant
        // to env-map blending. Check distinct (w0, w1) pairs.
        if (op6 == 0x3C) {
            uint32_t w0 = ((uint32_t)MEM_B(0, mips) << 24) |
                          ((uint32_t)(uint8_t)MEM_B(1, mips) << 16) |
                          ((uint32_t)(uint8_t)MEM_B(2, mips) <<  8) |
                          ((uint32_t)(uint8_t)MEM_B(3, mips));
            uint32_t w1 = ((uint32_t)(uint8_t)MEM_B(4, mips) << 24) |
                          ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                          ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                          ((uint32_t)(uint8_t)MEM_B(7, mips));
            // Linear scan (max 16 entries — fast). Multi-pass rendering with
            // multiple combiner formulas will populate multiple slots.
            g_task_combine_total++;
            bool found = false;
            for (uint32_t i = 0; i < g_task_combine_uniq; i++) {
                if (g_task_combine[i].w0 == w0 && g_task_combine[i].w1 == w1) {
                    g_task_combine[i].count++;
                    found = true;
                    break;
                }
            }
            if (!found) {
                if (g_task_combine_uniq < 16) {
                    g_task_combine[g_task_combine_uniq].w0 = w0;
                    g_task_combine[g_task_combine_uniq].w1 = w1;
                    g_task_combine[g_task_combine_uniq].count = 1;
                    g_task_combine_uniq++;
                } else {
                    g_task_combine_overflow++;
                }
            }
            // Pak combiner = TEXEL × SHADE (mux 0xFC127E24/0xFFFFFFFF).
            // Track entry/exit so we can log only the Pak's texture commands
            // and skip the 159 setCombines for text rendering.
            extern bool g_in_pak_combiner;
            g_in_pak_combiner = (w0 == 0xFC127E24u && w1 == 0xFFFFFFFFu);
            if (g_in_pak_combiner && log_dpc()) {
                fprintf(stderr, "[dpc-pak] >>> ENTER Pak combiner block\n");
                fflush(stderr);
            }
            // Cinematic-particle combiner (mux 0xFC11FE23/0xFFFFFFFF).
            // 522 calls/cinematic-frame in task #290; covers the
            // particle/shockwave/fireball texrects.
            extern bool g_in_cine_combiner;
            bool was_cine = g_in_cine_combiner;
            g_in_cine_combiner = (w0 == 0xFC11FE23u && w1 == 0xFFFFFFFFu);
            if (g_in_cine_combiner && !was_cine && log_dpc()) {
                static std::atomic<uint64_t> s_first{0};
                uint64_t v = ++s_first;
                if (v <= 4) {
                    fprintf(stderr, "[dpc-cine] >>> ENTER cinematic particle combiner block #%llu\n",
                        (unsigned long long)v);
                    fflush(stderr);
                }
            }
            // 64-triangle particle mux: TEXEL×SHADE used by the actual 3D
            // particle billboards (32 quads = 64 triangles per cinematic
            // frame in task #290+). User confirmed these triangles do NOT
            // turn magenta with the alphaCvgSel diagnostic, so they use a
            // different render-mode preset. Capture full draw context to
            // see why they're not visible.
            static bool s_in_64tri = false;
            const bool now_64tri = (w0 == 0xFC127FFFu && w1 == 0xFFFFFE3Fu);
            if (now_64tri && !s_in_64tri && log_dpc()) {
                static std::atomic<uint64_t> s_first{0};
                uint64_t v = ++s_first;
                // Log first 8, then every 64th — boot uses this mux too,
                // so the first few entries are N64-logo state, not cinematic.
                // Cinematic phase repeats the mux many times per second.
                if (v <= 8 || (v & 63) == 0) {
                    extern uint32_t g_last_othermode_l, g_last_othermode_h;
                    extern uint32_t g_last_settimg_w0, g_last_settimg_w1;
                    extern uint32_t g_last_setcimg_w0, g_last_setcimg_w1;
                    extern uint32_t g_last_settile_w0, g_last_settile_w1;
                    extern uint32_t g_last_fogcolor, g_last_primcolor;
                    extern uint32_t g_last_envcolor, g_last_blendcolor;
                    fprintf(stderr,
                        "[dpc-64tri] ENTER #%llu  L=0x%08X H=0x%08X  TIMG=[%08X %08X]  CIMG=[%08X %08X]  TILE=[%08X %08X]  FOG=%08X PRIM=%08X ENV=%08X BLEND=%08X\n",
                        (unsigned long long)v,
                        g_last_othermode_l, g_last_othermode_h,
                        g_last_settimg_w0, g_last_settimg_w1,
                        g_last_setcimg_w0, g_last_setcimg_w1,
                        g_last_settile_w0, g_last_settile_w1,
                        g_last_fogcolor, g_last_primcolor,
                        g_last_envcolor, g_last_blendcolor);
                    fflush(stderr);
                }
            }
            s_in_64tri = now_64tri;
        }
        // Inside the Pak combiner block, log every texture-loading
        // command so we can see the format / palette / address chain
        // for the Pak's draws. Outside the block, fall back to the
        // original "first 8" capture for SET_TEXTURE/DEPTH/COLOR_IMAGE.
        // Per-command volume is high (200+ lines per cinematic frame);
        // gated on ROGUESQ_LOG_DPC.
        if (g_in_pak_combiner && log_dpc()) {
            const char *name = nullptr;
            switch (op6) {
                case 0x30: name = "G_LOADTLUT";      break;
                case 0x32: name = "G_SETTILESIZE";   break;
                case 0x33: name = "G_LOADBLOCK";     break;
                case 0x34: name = "G_LOADTILE";      break;
                case 0x35: name = "G_SETTILE";       break;
                case 0x3D: name = "G_SETTIMG";       break;
                case 0x3F: name = "G_SETCIMG";       break;
                case 0x05: case 0x07: case 0x08: case 0x09:
                case 0x0A: case 0x0B: case 0x0C: case 0x0D:
                case 0x0E: case 0x0F: name = "G_TRI"; break;
                default: break;
            }
            if (name) {
                uint32_t w0 = ((uint32_t)MEM_B(0, mips) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(1, mips) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(2, mips) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(3, mips));
                uint32_t w1 = ((uint32_t)(uint8_t)MEM_B(4, mips) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(7, mips));
                if (op6 == 0x3D) {
                    // SET_TEXTURE_IMAGE: w0 has fmt(31-29)/siz(20-19)/width(11-0)
                    uint32_t fmt = (w0 >> 21) & 0x7;
                    uint32_t siz = (w0 >> 19) & 0x3;
                    uint32_t width = (w0 & 0xFFF) + 1;
                    uint32_t addr = w1 & 0x00FFFFFF;
                    const char *fmt_name = "?";
                    switch (fmt) {
                        case 0: fmt_name = "RGBA"; break;
                        case 1: fmt_name = "YUV";  break;
                        case 2: fmt_name = "CI";   break;
                        case 3: fmt_name = "IA";   break;
                        case 4: fmt_name = "I";    break;
                    }
                    const char *siz_name =
                        (siz == 0) ? "4b" : (siz == 1) ? "8b" :
                        (siz == 2) ? "16b" : "32b";
                    fprintf(stderr,
                        "[dpc-pak] %s fmt=%s siz=%s width=%u addr=0x%08X\n",
                        name, fmt_name, siz_name, width, addr);
                    // Cache for upcoming LOADTLUT — TLUT data lives at the
                    // RGBA16 SETTIMG that immediately precedes a LOADTLUT.
                    if (fmt == 0 /* RGBA */) {
                        g_pak_last_tlut_addr = addr;
                    }
                } else if (op6 == 0x35) {
                    // SET_TILE: w0 = fmt/siz/line/tmem/tile, w1 = palette/clamp/mask/shift
                    uint32_t fmt = (w0 >> 21) & 0x7;
                    uint32_t siz = (w0 >> 19) & 0x3;
                    uint32_t line = (w0 >> 9) & 0x1FF;
                    uint32_t tmem = w0 & 0x1FF;
                    uint32_t tile = (w1 >> 24) & 0x7;
                    uint32_t palette = (w1 >> 20) & 0xF;
                    fprintf(stderr,
                        "[dpc-pak] %s tile=%u fmt=%u siz=%u line=%u tmem=0x%X palette=%u\n",
                        name, tile, fmt, siz, line, tmem, palette);
                } else if (op6 == 0x33) {
                    // LOAD_BLOCK
                    uint32_t uls = (w0 >> 12) & 0xFFF;
                    uint32_t ult = w0 & 0xFFF;
                    uint32_t tile = (w1 >> 24) & 0x7;
                    uint32_t lrs = (w1 >> 12) & 0xFFF;
                    uint32_t dxt = w1 & 0xFFF;
                    fprintf(stderr,
                        "[dpc-pak] %s tile=%u uls=%u ult=%u texels=%u dxt=%u\n",
                        name, tile, uls, ult, lrs + 1, dxt);
                } else if (op6 == 0x30) {
                    uint32_t tile = (w1 >> 24) & 0x7;
                    fprintf(stderr,
                        "[dpc-pak] %s tile=%u w0=0x%08X w1=0x%08X\n",
                        name, tile, w0, w1);
                    // Dump the 16 TLUT entries we just loaded. They live
                    // at the most-recent SETTIMG address (RGBA16 format).
                    extern uint32_t g_pak_last_tlut_addr;
                    if (g_pak_last_tlut_addr != 0) {
                        fprintf(stderr, "[dpc-pak] TLUT @ 0x%08X (RGBA16):\n",
                            g_pak_last_tlut_addr);
                        // 16 entries × 2 bytes each = 32 bytes
                        uint8_t* base = rdram + (g_pak_last_tlut_addr ^ 3);
                        // RDRAM is BE; ^3 flips to RSP-side aligned reads.
                        for (int i = 0; i < 16; i++) {
                            uint32_t off = g_pak_last_tlut_addr + i * 2;
                            uint8_t hi = rdram[(off + 0) ^ 3];
                            uint8_t lo = rdram[(off + 1) ^ 3];
                            uint16_t rgba16 = ((uint16_t)hi << 8) | lo;
                            int r = (rgba16 >> 11) & 0x1F;
                            int g = (rgba16 >> 6) & 0x1F;
                            int b = (rgba16 >> 1) & 0x1F;
                            int a = rgba16 & 0x1;
                            fprintf(stderr,
                                "  [%2d] rgba16=0x%04X  R=%2d G=%2d B=%2d A=%d  "
                                "(R8=%3d G8=%3d B8=%3d)\n",
                                i, rgba16, r, g, b, a,
                                (r << 3) | (r >> 2),
                                (g << 3) | (g >> 2),
                                (b << 3) | (b >> 2));
                        }
                        (void)base;
                    }
                } else {
                    fprintf(stderr,
                        "[dpc-pak] %s w0=0x%08X w1=0x%08X\n", name, w0, w1);
                }
                fflush(stderr);
            }
        }
        // Track latest SETTIMG / SETCIMG GLOBALLY (regardless of which
        // combiner is active) so we have correlation context when the
        // next texrect fires inside any block.
        if (op6 == 0x3D) {
            uint32_t w0 = ((uint32_t)MEM_B(0, mips) << 24) |
                          ((uint32_t)(uint8_t)MEM_B(1, mips) << 16) |
                          ((uint32_t)(uint8_t)MEM_B(2, mips) <<  8) |
                          ((uint32_t)(uint8_t)MEM_B(3, mips));
            uint32_t w1 = ((uint32_t)(uint8_t)MEM_B(4, mips) << 24) |
                          ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                          ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                          ((uint32_t)(uint8_t)MEM_B(7, mips));
            g_cine_last_settimg_fmt = (w0 >> 21) & 0x7;
            g_cine_last_settimg_siz = (w0 >> 19) & 0x3;
            g_cine_last_settimg_addr = w1 & 0x00FFFFFF;
        }
        if (op6 == 0x3F) {
            uint32_t w1 = ((uint32_t)MEM_B(4, mips) << 24) |
                          ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                          ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                          ((uint32_t)(uint8_t)MEM_B(7, mips));
            g_cine_last_cimg_addr = w1 & 0x00FFFFFF;
            // ALWAYS log when CIMG address is OOB (>= 8MB). Captures the slot
            // that emitted the bad command + the source DL location, so we can
            // backtrack to whichever code wrote garbage into this DL slot.
            // Throttled exponentially to avoid log floods.
            if (g_cine_last_cimg_addr >= 0x01000000u) {
                static std::atomic<uint64_t> s_oob{0};
                uint64_t n = ++s_oob;
                if (n == 1 || (n & (n - 1)) == 0) {
                    uint32_t w0 = ((uint32_t)MEM_B(0, mips) << 24) |
                                  ((uint32_t)(uint8_t)MEM_B(1, mips) << 16) |
                                  ((uint32_t)(uint8_t)MEM_B(2, mips) <<  8) |
                                  ((uint32_t)(uint8_t)MEM_B(3, mips));
                    fprintf(stderr,
                        "[cimg-oob] #%llu slot=%d dl=0x%08X w0=0x%08X w1=0x%08X addr24=0x%08X\n",
                        (unsigned long long)n, g_cine_current_slot,
                        (unsigned)mips, w0, w1, g_cine_last_cimg_addr);
                    fflush(stderr);
                }
            }
            // PHASE 21 engine-aware filter: record slot ownership for this fb.
            // Once an effect-dispatched SET_COLOR_IMAGE selects this fb, the fb
            // is owned by that slot until a non-cinematic SET_COLOR_IMAGE
            // (slot=-1) selects the same address again.
            {
                std::lock_guard<std::mutex> lk(g_cine_fb_owner_mutex);
                g_cine_fb_owner_slot[g_cine_last_cimg_addr] = g_cine_current_slot;
            }
            // PHASE 21 correlation log. Tag every SET_COLOR_IMAGE with the
            // currently-executing effect slot index (or -1 if not inside an
            // effect dispatch). Run with ROGUESQ_LOG_DPC=1 to enable.
            if (log_dpc()) {
                static std::atomic<uint64_t> s_seq{0};
                uint64_t v = ++s_seq;
                if (v <= 200 || (v % 100) == 0) {
                    fprintf(stderr,
                        "[cimg-corr] seq=%llu slot=%d addr=0x%08X\n",
                        (unsigned long long)v, g_cine_current_slot,
                        g_cine_last_cimg_addr);
                    fflush(stderr);
                }
            }
        }
        // Cinematic particle combiner — log first ~32 texrects + their
        // tile/texture/CIMG context so we can see whether particles are
        // on-screen, what fb they target, what texture they sample.
        if (g_in_cine_combiner) {
            // TEXRECT (0xE4 -> low6 = 0x24): log geometry + context.
            if (op6 == 0x24) {
                static std::atomic<uint64_t> s_rect{0};
                uint64_t v = ++s_rect;
                if (v <= 32) {
                    uint32_t w0 = ((uint32_t)MEM_B(0, mips) << 24) |
                                  ((uint32_t)(uint8_t)MEM_B(1, mips) << 16) |
                                  ((uint32_t)(uint8_t)MEM_B(2, mips) <<  8) |
                                  ((uint32_t)(uint8_t)MEM_B(3, mips));
                    uint32_t w1 = ((uint32_t)MEM_B(4, mips) << 24) |
                                  ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                                  ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                                  ((uint32_t)(uint8_t)MEM_B(7, mips));
                    // Standard RDP TEXRECT: lrx/lry/tile/ulx/uly in 10.2 fixed
                    uint32_t lrx = (w0 >> 12) & 0xFFF;
                    uint32_t lry = w0 & 0xFFF;
                    uint32_t tile = (w1 >> 24) & 0x7;
                    uint32_t ulx = (w1 >> 12) & 0xFFF;
                    uint32_t uly = w1 & 0xFFF;
                    fprintf(stderr,
                        "[dpc-cine] TEXRECT #%llu ul=(%u,%u) lr=(%u,%u) "
                        "size=(%u,%u) tile=%u  fb=0x%08X texSrc=0x%08X fmt=%u siz=%u\n",
                        (unsigned long long)v,
                        ulx >> 2, uly >> 2, lrx >> 2, lry >> 2,
                        (lrx - ulx) >> 2, (lry - uly) >> 2,
                        tile, g_cine_last_cimg_addr, g_cine_last_settimg_addr,
                        g_cine_last_settimg_fmt, g_cine_last_settimg_siz);
                    fflush(stderr);
                }
            }
        }
        if (!g_in_pak_combiner && (op6 == 0x3D || op6 == 0x3E || op6 == 0x3F)) {
            static std::atomic<uint64_t> s_seen{0};
            uint64_t n = ++s_seen;
            if (log_dpc() && n <= 8) {
                uint32_t w0 = ((uint32_t)MEM_B(0, mips) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(1, mips) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(2, mips) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(3, mips));
                uint32_t w1 = ((uint32_t)(uint8_t)MEM_B(4, mips) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(7, mips));
                const char *name = (op6 == 0x3F) ? "SET_COLOR_IMAGE" :
                                   (op6 == 0x3E) ? "SET_DEPTH_IMAGE" : "SET_TEXTURE_IMAGE";
                fprintf(stderr, "[dpc] %s #%llu w0=0x%08X w1=0x%08X (addr=0x%08X)\n",
                    name, (unsigned long long)n, w0, w1, w1 & 0x00FFFFFF);
                fflush(stderr);
            }
        }
    }

    // 16-byte LLE TEXRECT chunk: Factor5 emits these for particle billboards
    // (~522/cinematic-frame). The 8-byte block above misses them because they
    // arrive as a single 16-byte submission. Log geometry + texture context
    // when the cinematic combiner is active so we can see whether particles
    // are on-screen, hitting the right framebuffer, etc.
    if ((submit_hi - submit_lo) == 16 && g_in_cine_combiner) {
        int64_t mips = (int64_t)(int32_t)(submit_lo + 0x80000000);
        uint8_t b0 = MEM_B(0, mips);
        uint8_t op6 = b0 & 0x3F;
        if (op6 == 0x24 || op6 == 0x25) { // TEXRECT or TEXRECTFLIP
            static std::atomic<uint64_t> s_rect{0};
            uint64_t v = ++s_rect;
            if (v <= 32) {
                uint32_t w0 = ((uint32_t)MEM_B(0, mips) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(1, mips) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(2, mips) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(3, mips));
                uint32_t w1 = ((uint32_t)MEM_B(4, mips) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(5, mips) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(6, mips) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(7, mips));
                uint32_t w2 = ((uint32_t)MEM_B(8, mips) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(9, mips) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(10, mips) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(11, mips));
                uint32_t w3 = ((uint32_t)MEM_B(12, mips) << 24) |
                              ((uint32_t)(uint8_t)MEM_B(13, mips) << 16) |
                              ((uint32_t)(uint8_t)MEM_B(14, mips) <<  8) |
                              ((uint32_t)(uint8_t)MEM_B(15, mips));
                uint32_t lrx = (w0 >> 12) & 0xFFF;
                uint32_t lry = w0 & 0xFFF;
                uint32_t tile = (w1 >> 24) & 0x7;
                uint32_t ulx = (w1 >> 12) & 0xFFF;
                uint32_t uly = w1 & 0xFFF;
                fprintf(stderr,
                    "[dpc-cine] TEXRECT%s #%llu ul=(%u,%u) lr=(%u,%u) "
                    "size=(%u,%u) tile=%u  fb=0x%08X tex=0x%08X fmt=%u siz=%u "
                    "stuv=0x%08X dxdy=0x%08X\n",
                    (op6 == 0x25) ? "_FLIP" : "",
                    (unsigned long long)v,
                    ulx >> 2, uly >> 2, lrx >> 2, lry >> 2,
                    (lrx > ulx) ? ((lrx - ulx) >> 2) : 0,
                    (lry > uly) ? ((lry - uly) >> 2) : 0,
                    tile, g_cine_last_cimg_addr, g_cine_last_settimg_addr,
                    g_cine_last_settimg_fmt, g_cine_last_settimg_siz,
                    w2, w3);
                fflush(stderr);
            }
        }
    }

    (void)rdram;

    // SUPPRESS_OOB_CIMG: drop isolated 8-byte SET_COLOR_IMAGE commands whose
    // address field is outside legitimate framebuffer space.
    //   HIGH (>= 0x800000)  : past 8MB RDRAM (typical: 0x00FFFFFF garbage)
    //   LOW  (<  0x100000)  : asset/code region — but Factor 5 LLE legitimately
    //                         emits some lowmem CIMGs for the 3D logo render
    //                         path; dropping them causes a visual regression.
    //                         Existing writeback guard at rt64_state.cpp gates
    //                         the resulting RDRAM writeback on addressStart
    //                         >= 0x100000, which is the right place to filter
    //                         these — let them through to RT64.
    // Default OFF; set ROGUESQ_SUPPRESS_OOB_CIMG=1 to enable for leak-mitigation
    // experiments. Tradeoff: HIGH+LOW drop reduces the iter-810 memory spike,
    // but kills the Factor 5 3D logo visual.
    {
        static const bool s_suppress = []{
            const char* v = std::getenv("ROGUESQ_SUPPRESS_OOB_CIMG");
            return v && *v && *v != '0';
        }();
        if (s_suppress && (submit_hi - submit_lo) == 8) {
            int64_t mp = (int64_t)(int32_t)(submit_lo + 0x80000000);
            uint8_t b0 = (uint8_t)MEM_B(0, mp);
            if (b0 == 0xFF) {
                uint32_t w1v = ((uint32_t)(uint8_t)MEM_B(4, mp) << 24) |
                               ((uint32_t)(uint8_t)MEM_B(5, mp) << 16) |
                               ((uint32_t)(uint8_t)MEM_B(6, mp) <<  8) |
                               ((uint32_t)(uint8_t)MEM_B(7, mp));
                uint32_t addr24 = w1v & 0x00FFFFFF;
                const bool drop_high = (addr24 >= 0x01000000u); // s6135: 16 MB
                const bool drop_low  = (addr24 != 0 && addr24 < 0x00100000u);
                if (drop_high || drop_low) {
                    static std::atomic<uint64_t> s_drop_h{0};
                    static std::atomic<uint64_t> s_drop_l{0};
                    uint64_t n = drop_high ? ++s_drop_h : ++s_drop_l;
                    if (n == 1 || (n & (n - 1)) == 0) {
                        fprintf(stderr, "[cimg-drop] %s #%llu submit_lo=0x%08X addr=0x%06X\n",
                            drop_high ? "HIGH" : "LOW",
                            (unsigned long long)n, submit_lo, addr24);
                        fflush(stderr);
                    }
                    RS64_S7096_DROP(submit_lo, submit_hi, 2);
                    return;
                }
            }
        }
    }

rs64_bf_push:
    g_bf_guard.reached();
    // Defer layer: while a task is running, hold ranges instead of feeding
    // RT64 live. The runner commits them on clean ucode exit and drops them
    // on UnhandledJumpTarget, so garbage streams (trig data executed as DL)
    // never reach RT64's deferred state. Gfx-thread only, no locking needed.
    if (g_defer_active) {
        {
            static const bool sh_env = []{ const char *e = std::getenv("ROGUESQ_S4272"); return !(e && *e == '0'); }(); /* s4549: default on (=0 disables) */
            const bool sh = sh_env && g_rs64_bfsh_arm != 2;   // s7029 shadow arm 2 (diagnostic)
            static const uint32_t cap = []{ const char *e = std::getenv("ROGUESQ_S4272_CAP"); return e ? (uint32_t)strtoul(e, nullptr, 0) : 0x2000u; }(); /* s4286, s4287: default 0x2000 */
            bool ext = false;   // s6955: ROGUESQ_G1E_BATCH, extend the contiguous last range (+ its shadow entry in lockstep)
            if (g_rs64_g1e_batch && !g_deferred_ranges.empty() && g_deferred_ranges.back().second == submit_lo) {
                auto &bk = g_deferred_ranges.back();
                if (!sh) { bk.second = submit_hi; ext = true; }
                else if (!g_s4272_sh.empty()) {
                    S4272Sh &se = g_s4272_sh.back();
                    if (se.lo == bk.first && se.hi == bk.second && se.off + (se.hi - se.lo) == g_s4272_shadow.size() && submit_hi - se.lo <= cap) {
                        se.hi = submit_hi; bk.second = submit_hi;
                        g_s4272_shadow.insert(g_s4272_shadow.end(), rdram + submit_lo, rdram + submit_hi);
                        ext = true;
                    }
                }
            }
            if (!ext) {
                g_deferred_ranges.emplace_back(submit_lo, submit_hi); ++g_rs64_g1e_ranges;
                if (sh && submit_hi - submit_lo <= cap) {
                    g_s4272_sh.push_back({submit_lo, submit_hi, g_s4272_shadow.size()});
                    g_s4272_shadow.insert(g_s4272_shadow.end(), rdram + submit_lo, rdram + submit_hi);
                }
            }
            if (g_bc_on) {   // per-bump reference lists (old behaviour)
                g_bc_ranges.emplace_back(submit_lo, submit_hi);
                if (sh && submit_hi - submit_lo <= cap) {
                    g_bc_sh.push_back({submit_lo, submit_hi, g_bc_shadow.size()});
                    g_bc_shadow.insert(g_bc_shadow.end(), rdram + submit_lo, rdram + submit_hi);
                }
            }
        }
        // s6707 G1e: in a streaming async task, hand the pending ranges to the RT64 worker every stream_bytes so it runs
        // while the RSP does, instead of one ~120 kB commit after the ucode exits (s6706 H-endload). Same risk class as the
        // s4273 wrap flush: bytes already flushed cannot be dropped if the task later ends on UnhandledJumpTarget.
        if (const uint32_t sb = rs64_rdpq_task_stream()) {
            g_defer_stream_pending += submit_hi - submit_lo;
            if (g_defer_stream_pending >= sb) {
                uint32_t bytes = 0; size_t calls = 0;
                rs64_g1e_bc_check("stream");
                submit_deferred_merged(bytes, calls);
                g_deferred_ranges.clear(); g_s4272_sh.clear(); g_s4272_shadow.clear(); rs64_g1e_bc_clear();
                g_defer_stream_pending = 0; ++g_defer_stream_flushes;
                g_defer_stream_task_flushes++;
                g_defer_stream_bytes += bytes;
            }
        }
        return;
    }

    if (should_drop_wrap_rdp(submit_lo, submit_hi)) {
        RS64_S7096_DROP(submit_lo, submit_hi, 4);
        return;
    }

    rs64_e9prov_mark_submitted(submit_lo, submit_hi);
    rs64_dpc_record_submit(submit_lo, submit_hi);
    rs64_rt_submit(submit_lo, submit_hi, 0);
}

extern "C" void rs64_dpc_defer_begin() {
    g_defer_active = true;
    if (g_bf_mode && !g_bf_diag) {   // s7027: latch the bump fast-path arm per task; [s7027-bf] summary every 10 s
        const uint64_t mt = mach_absolute_time(); static bool anc = false; static uint64_t last = 0;
        if ((g_bf_mode == 2 || g_bf_mode == 4) && !anc) { anc = true; rs64_tog_anchor(mt); }
        // s7028: tog3 = mach second % 3 (period 3 is coprime with the harness's 8 s press cycle, so each arm samples it evenly)
        g_rs64_bf_task_on = g_bf_mode == 1 ? 1 : g_bf_mode == 3 ? 2 : g_bf_mode == 4 ? (int)((mt / 24000000u) % 3u) : rs64_tog_odd(mt);
        (g_rs64_bf_task_on == 2 ? g_rs64_bf_tasks_on2 : g_rs64_bf_task_on ? g_rs64_bf_tasks_on : g_rs64_bf_tasks_off)++;
        if (mt - last > 240000000ull) { last = mt;
            int top[6] = {0}; for (int k = 0; k < 6; ++k) { int bi = -1; for (int o = 0; o < 64; ++o) { bool used = false; for (int j = 0; j < k; ++j) used |= top[j] == o;
                if (!used && (bi < 0 || g_bf_slow_op[o] > g_bf_slow_op[bi])) bi = o; } top[k] = bi; }
            fprintf(stderr, "[s7027-bf] mode=%d check=%d tasksOn=%llu tasksOff=%llu fast=%llu slowElig=%llu chk=%llu bad=%llu ctl=%llu ",
                    g_bf_mode, (int)g_bf_check, (unsigned long long)g_rs64_bf_tasks_on, (unsigned long long)g_rs64_bf_tasks_off,
                    (unsigned long long)g_rs64_bf_fast, (unsigned long long)g_rs64_bf_slow, (unsigned long long)g_rs64_bf_chk_n,
                    (unsigned long long)g_rs64_bf_chk_bad, (unsigned long long)g_rs64_bf_chk_ctl);
            fprintf(stderr, "tasksOn2=%llu chk2=%llu bad2=%llu ctl2=%llu slowTop=", (unsigned long long)g_rs64_bf_tasks_on2,
                    (unsigned long long)g_rs64_bf_chk2_n, (unsigned long long)g_rs64_bf_chk2_bad, (unsigned long long)g_rs64_bf_chk2_ctl);
            for (int k = 0; k < 6; ++k) fprintf(stderr, "%02X:%llu,", top[k], (unsigned long long)g_bf_slow_op[top[k]]);
            fputc('\n', stderr); }
    } else g_rs64_bf_task_on = 0;
    if (g_bf_check) g_bf2_thr = pthread_self();   // s7029
    if (g_bfsh_mode) {   // s7029 shadow arm, latched per task; arm 1 reserves from the previous task's peaks
        g_bfsh_pk_sh = std::max(g_bfsh_pk_sh, g_s4272_sh.size()); g_bfsh_pk_shadow = std::max(g_bfsh_pk_shadow, g_s4272_shadow.size());
        g_bfsh_pk_ranges = std::max(g_bfsh_pk_ranges, g_deferred_ranges.size());
        g_rs64_bfsh_arm = (int)((mach_absolute_time() / 24000000u) % 3u); ++g_rs64_bfsh_tasks[g_rs64_bfsh_arm];
        if (g_rs64_bfsh_arm == 1) { g_s4272_sh.reserve(g_bfsh_pk_sh * 2); g_s4272_shadow.reserve(g_bfsh_pk_shadow * 2); g_deferred_ranges.reserve(g_bfsh_pk_ranges * 2); }
    } else g_rs64_bfsh_arm = 0;
    {   // s6955: ROGUESQ_G1E_BATCH arm, latched per task
        static const int s_batch_env = [] { const char *e = std::getenv("ROGUESQ_G1E_BATCH"); return !e ? 1 : (*e == 't' ? 2 : (*e != '0')); }();
        static const bool s_bc = [] { const char *e = std::getenv("ROGUESQ_G1E_BATCH_CHECK"); return e && *e && *e != '0'; }();
        g_rs64_g1e_batch = s_batch_env == 2 ? (int)((time(nullptr) / 10) & 1) : s_batch_env;
        g_bc_on = s_bc; rs64_g1e_bc_clear();
        static const int s_cdiag_env = [] { const char *e = std::getenv("ROGUESQ_G1E_CDIAG"); return !e ? 0 : (*e == 't' ? 2 : (*e != '0')); }();
        g_rs64_g1e_cdiag = s_cdiag_env == 2 ? (int)((time(nullptr) / 10) & 1) : s_cdiag_env;
    }
    g_defer_stream_pending = 0; g_defer_stream_task_flushes = 0;
    g_deferred_ranges.clear();
    g_s4272_sh.clear(); g_s4272_shadow.clear();
    s_task_first_lo = 0;
    s_task_first_hi = 0;
    s_task_last_lo = 0;
    s_task_last_hi = 0;
    s_task_min_lo = 0xFFFFFFFFu;
    s_task_max_hi = 0;
}

static void rs64_dpc_defer_end_impl(int commit) {
    g_defer_active = false;
    if (!commit && rs64_s7096_on) for (const auto &r : g_deferred_ranges) rs64_s7096_drop(r.first, r.second, 7);
    if (commit) rs64_g1e_bc_check("commit");
    /* s7444 class DA: this tally printed [s6956-cdiag] every 1024 commits with no env (8 lines per 150 s owner run). Its only
       consumer is the ROGUESQ_G1E_CDIAG experiment; latch it on that env. ROGUESQ_G1E_TRIM=0 restores the old always-on tally. */
    static const bool s_cdiag_tally = [] { const char *c = std::getenv("ROGUESQ_G1E_CDIAG"), *t = std::getenv("ROGUESQ_G1E_TRIM");
        return (c && *c) || (t && *t == '0'); }();
    if (commit && s_cdiag_tally) {   // s6956: per-arm task tally (positive control: cmpWords must advance only with on-tasks)
        static unsigned long onT = 0, offT = 0; (g_rs64_g1e_cdiag ? onT : offT)++;
        if (((onT + offT) & 0x3FF) == 0) fprintf(stderr, "[s6956-cdiag] onTasks=%lu offTasks=%lu\n", onT, offT);
    }
    if (commit && g_rs64_g1e_cdiag && !g_s4272_sh.empty() && g_rdram_for_submit) {
        static unsigned long cmpWords = 0, diffWords = 0, tasks = 0, tasksDiff = 0; static int shown = 0;
        unsigned long d = 0;
        for (const S4272Sh &e : g_s4272_sh) {
            for (uint32_t a = e.lo; a + 4 <= e.hi; a += 4) {   /* s7364: was a < e.hi, read 1-3 bytes past an unaligned range */
                uint32_t was, now;
                memcpy(&was, &g_s4272_shadow[e.off + (a - e.lo)], 4);
                memcpy(&now, g_rdram_for_submit + a, 4);
                cmpWords++;
                if (was != now) {
                    d++; diffWords++;
                    if (shown++ < 24)
                        fprintf(stderr, "[s4272-latewrite] addr=%06X bump-time=%08X commit-time=%08X (range %06X..%06X)\n", a, was, now, e.lo, e.hi);
                }
            }
        }
        tasks++; if (d) tasksDiff++;
        // positive control: a forced mismatch must be detected by the same compare
        uint32_t ctl = 0; { uint32_t x = 0, y = 1; ctl = (x != y); }
        if ((tasks & 0x3FF) == 1 || (tasks % 2000) == 0)
            fprintf(stderr, "[s4272-latetot] tasks=%lu tasksWithDiff=%lu cmpWords=%lu diffWords=%lu control=%u\n", tasks, tasksDiff, cmpWords, diffWords, ctl);
    }
    if (commit) {
        // The ucode bumps DPC_END one 8-byte command at a time, so a task's
        // deferred list is mostly runs of contiguous ranges. Submitting each
        // one separately costs a full RT64 processDisplayLists entry per
        // command — millions per run in the tiled hi-res phase. Merging runs
        // is byte-for-byte identical in content and order, just far fewer
        // calls. ROGUESQ_NO_DPC_MERGE=1 restores the old one-call-per-range
        // behavior for comparison.
        static const bool merge_enabled = []{
            const char *e = std::getenv("ROGUESQ_NO_DPC_MERGE");
            return !(e && *e && *e != '0');
        }();

        uint32_t bytes = 0;
        size_t calls = 0;
        if (merge_enabled && !g_deferred_ranges.empty()) {
            submit_deferred_merged(bytes, calls);
        }
        else {
            for (const auto& r : g_deferred_ranges) {
                if (should_drop_wrap_rdp(r.first, r.second)) {
                    RS64_S7096_DROP(r.first, r.second, 4);
                    continue;
                }
                bytes += r.second - r.first;
                calls++;
                rs64_e9prov_mark_submitted(r.first, r.second);
                rs64_dpc_record_submit(r.first, r.second);
                rs64_rt_submit(r.first, r.second, 3);
            }
        }

        if (!g_rs64_g1e_cdiag) RT64::g_s4280_n = 0;
        else if (!rs64_rdpq_task_async()) {   // s4280: attribute each SetColorImage RT64 saw during this commit to its bump-time shadow range (s6705: not for async-consumed tasks).
            int n = RT64::g_s4280_n; static unsigned long nOdd = 0, nSane = 0, oddNoShadow = 0, oddDiff = 0, sane_diff = 0; static int shownO = 0, shownS = 0;
            for (int i = 0; i < n && i < 256; i++) {
                const RT64::S4280Ev &ev = RT64::g_s4280_ev[i];
                const uint32_t off = (uint32_t)ev.off;
                const S4272Sh *hit = nullptr;
                for (const S4272Sh &e : g_s4272_sh) if (off >= e.lo && off + 8 <= e.hi) { hit = &e; break; }
                uint32_t bw0 = 0, bw1 = 0, nw0 = 0, nw1 = 0;
                if (g_rdram_for_submit) { memcpy(&nw0, g_rdram_for_submit + off, 4); memcpy(&nw1, g_rdram_for_submit + off + 4, 4); }
                if (hit) { memcpy(&bw0, &g_s4272_shadow[hit->off + (off - hit->lo)], 4); memcpy(&bw1, &g_s4272_shadow[hit->off + (off - hit->lo) + 4], 4); }
                const bool diff = hit && (bw0 != nw0 || bw1 != nw1);
                if (ev.odd) { nOdd++; if (!hit) oddNoShadow++; if (diff) oddDiff++; } else { nSane++; if (diff) sane_diff++; }
                int &shown = ev.odd ? shownO : shownS;
                if (shown < 12 || ev.addr == 0x130393u) {
                    shown++;
                    fprintf(stderr, "[s4280-cimg] %s off=%06X addr=%08X w=%u shadow=%s bump=%08X %08X commit=%08X %08X range=%06X..%06X\n",
                            ev.odd ? "ODD" : "SANE", off, ev.addr, ev.width, hit ? "yes" : "NO", bw0, bw1, nw0, nw1, hit ? hit->lo : 0, hit ? hit->hi : 0);
                }
            }
            for (int i = 0; i < n && i < 256; i++) {   // s4280b: full bump-vs-commit walk of the range holding the 0x130393 / w1033 event
                const RT64::S4280Ev &ev = RT64::g_s4280_ev[i];
                static int s4283Shown = 0;
                const bool s4283 = ev.odd && ev.addr != 0x130393u && s4283Shown < 4;
                if (ev.addr != 0x130393u && !s4283) continue;
                if (s4283) s4283Shown++;
                const uint32_t off = (uint32_t)ev.off;
                if (s4283) {   // s4283b: ALL deferred ranges (incl. >0x400, unshadowed) that overlap the event, in push order: >1 hit = ring lap inside this commit
                    for (size_t j = 0; j < g_deferred_ranges.size(); j++) { const auto &r = g_deferred_ranges[j];
                        if ((uint32_t)r.second + 0x80 >= off && (uint32_t)r.first <= off + 0x80) fprintf(stderr, "[s4283-def] j=%zu/%zu %06X..%06X len=%X\n", j, g_deferred_ranges.size(), (uint32_t)r.first, (uint32_t)r.second, (uint32_t)(r.second - r.first)); } }
                if (s4283) {   // s4283: range tiling around the ODD event (push order) to test H-F (range starts mid-block) vs H-D/H-E
                    for (size_t k = 0; k < g_s4272_sh.size(); k++) { const S4272Sh &r = g_s4272_sh[k];
                        if (r.hi + 0x200 >= off && r.lo <= off + 0x100) fprintf(stderr, "[s4283-rng] k=%zu/%zu %06X..%06X len=%X%s\n", k, g_s4272_sh.size(), r.lo, r.hi, r.hi - r.lo, (off >= r.lo && off + 8 <= r.hi) ? " <== holds cimg" : ""); } }
                for (const S4272Sh &e : g_s4272_sh) if (off >= e.lo && off + 8 <= e.hi) {
                    for (uint32_t a = e.lo; a + 8 <= e.hi; a += 8) { uint32_t b0, b1, n0 = 0, n1 = 0; /* s7364 */ memcpy(&b0, &g_s4272_shadow[e.off + (a - e.lo)], 4); memcpy(&b1, &g_s4272_shadow[e.off + (a - e.lo) + 4], 4);
                        if (g_rdram_for_submit) { memcpy(&n0, g_rdram_for_submit + a, 4); memcpy(&n1, g_rdram_for_submit + a + 4, 4); }
                        fprintf(stderr, "[s4280-walk] %06X bump=%08X %08X commit=%08X %08X%s%s\n", a, b0, b1, n0, n1, (b0 != n0 || b1 != n1) ? " DIFF" : "", a == off ? " <== cimg" : ""); }
                    break; }
            }
            { static unsigned long cm = 0, cmLap = 0, oddCm = 0, oddCmLap = 0, shown4284 = 0; cm++; if (s_c4284_laps) cmLap++;
              bool anyOdd = false; for (int i = 0; i < n && i < 256; i++) if (RT64::g_s4280_ev[i].odd) { anyOdd = true;
                  const uint32_t off = (uint32_t)RT64::g_s4280_ev[i].off;
                  if (shown4284++ < 60) fprintf(stderr, "[s4284-odd] off=%06X laps=%u firstLap end=%06X seen=%06X start=%06X maxseen=%06X inDropped=%d\n", off, s_c4284_laps, s_c4284_first_lo, s_c4284_first_hi, s_c4284_start, s_c4284_maxseen, (s_c4284_laps && off >= s_c4284_start && off < s_c4284_maxseen) ? 1 : 0); }
              if (anyOdd) { oddCm++; if (s_c4284_laps) oddCmLap++; }
              if ((cm & 0xFF) == 0) fprintf(stderr, "[s4284-tot] commits=%lu withLap=%lu oddCommits=%lu oddWithLap=%lu\n", cm, cmLap, oddCm, oddCmLap); }
            RT64::g_s4280_n = 0;
            static unsigned long cnt = 0;
            if ((++cnt & 0xFFF) == 0)
                fprintf(stderr, "[s4280-tot] odd=%lu (noShadow=%lu bumpNeCommit=%lu) sane=%lu (bumpNeCommit=%lu)\n", nOdd, oddNoShadow, oddDiff, nSane, sane_diff);
        }
        static std::atomic<uint64_t> s_ranges_in{0};
        static std::atomic<uint64_t> s_calls_out{0};
        const uint64_t in = s_ranges_in.fetch_add(g_deferred_ranges.size()) + g_deferred_ranges.size();
        const uint64_t out = s_calls_out.fetch_add(calls) + calls;
        static std::atomic<uint64_t> s_tasks{0};
        if ((++s_tasks % 64) == 0) {
            fprintf(stderr, "[dpc-merge] ranges=%llu submits=%llu (%.1fx fewer)\n",
                    (unsigned long long)in, (unsigned long long)out,
                    out ? double(in) / double(out) : 0.0);
            fflush(stderr);
        }
        // Diag: per-task committed RDP volume (correlate with [ucode-b] lines
        // to confirm B tasks emit real work). Same gating as defer-drop.
        static int s_c = 0;
        static const bool s_trace_dispatch = getenv("ROGUESQ_TRACE_DISPATCH") != nullptr;  // s7633 class HB: was a per-commit getenv
        if (s_trace_dispatch && (++s_c <= 64 || (s_c & 63) == 0)) {
            fprintf(stderr, "[defer-commit #%d] %zu ranges, %u bytes\n",
                    s_c, g_deferred_ranges.size(), bytes);
        }
    } else if (!g_deferred_ranges.empty() || g_defer_stream_task_flushes) {
        if (g_defer_stream_task_flushes) {   // s6707: the task failed after streamed flushes already reached RT64
            static unsigned long n = 0;
            if (++n <= 16 || (n & 63) == 0)
                fprintf(stderr, "[g1e-stream] drop-after-stream #%lu flushes=%u pending_ranges=%zu\n", n, g_defer_stream_task_flushes, g_deferred_ranges.size());
        }
        uint32_t bytes = 0;
        for (const auto& r : g_deferred_ranges) bytes += r.second - r.first;
        static int s_n = 0;
        if (++s_n <= 32 || (s_n & 63) == 0) {
            fprintf(stderr, "[defer-drop #%d] discarded %zu RDP ranges (%u bytes) from failed task\n",
                    s_n, g_deferred_ranges.size(), bytes);
            fflush(stderr);
        }
    }
    if (g_defer_stream_task_flushes) {   // s6707 positive control: streamed flushes must fire in as=2 tasks
        static unsigned long st = 0;
        if (++st <= 4 || (st % 2000) == 0)
            fprintf(stderr, "[g1e-stream] tasks=%lu flushes=%llu bytes=%llu last_task_flushes=%u\n", st,
                    (unsigned long long)g_defer_stream_flushes, (unsigned long long)g_defer_stream_bytes, g_defer_stream_task_flushes);
    }
    s_c4284_laps = 0; s_c4284_maxseen = 0;
    g_deferred_ranges.clear(); rs64_g1e_bc_clear();
}

// s68: external noinline host stub for ImemOverrun site attribution. Called
// from factor5_ucode_recompiled.c at the remaining hard-exit sites (L_1650 /
// bare epilogue) plus a once-per-process "control" call at ucode entry.
// Lives in a different TU so default -O2 cannot DCE the call sites the way
// it did for s67's ucode-local volatile/fprintf on the L_0000 block.
extern "C" __attribute__((noinline)) void rs64_note_imem_overrun(const char* site) {
    static std::atomic<int> n{0};
    int k = ++n;
    if (k <= 40 || (k % 100) == 0) {
        fprintf(stderr, "[ucode-imem] #%d site=%s\n", k, site ? site : "?");
        fflush(stderr);
    }
}

// Called from the factor5_ucode synthetic-halt site. Logs per-task RDP byte
// volume / command count / FULL_SYNC count, then resets the counters for the
// next task. Throttled to first 16 tasks + every 256 thereafter so we get the
// distribution without flooding the SDL message pump.
extern "C" void rsp_task_log_and_reset(uint32_t iters, uint32_t data_size, uint32_t r17,
                                        uint32_t cmd_w0, uint32_t cmd_w1) {
    rs64_bf2_flush();  // s7028
    uint32_t bytes = g_task_rdp_bytes.exchange(0, std::memory_order_acq_rel);
    uint32_t cmds  = g_task_rdp_cmds.exchange(0, std::memory_order_acq_rel);
    uint32_t fs    = g_task_rdp_fullsyncs.exchange(0, std::memory_order_acq_rel);
    static std::atomic<uint64_t> s_n{0};
    uint64_t n = ++s_n;
    bool capped_no_fs = (iters > 16000 && fs == 0);
    // Throttle CAPPED-NO-FS spam — at 13/s with histogram dump it's ~117
    // lines/sec, enough to starve the SDL pump and stall GFX scheduling.
    static std::atomic<uint64_t> s_capped_count{0};
    bool log_capped = false;
    if (capped_no_fs) {
        uint64_t cn = ++s_capped_count;
        log_capped = (cn <= 8 || (cn & 4095) == 0);
    }
    // Targeted task numbers for particle-explosion phase (per user
    // observation). Mirror the dump_full list below so the outer gate
    // doesn't suppress these full dumps.
    const bool target_task_outer = (n == 256 || n == 384 || n == 512 ||
                                    n == 640 || n == 768 || n == 896 ||
                                    n == 290 || n == 320 || n == 350);
    // Brief per-task summary on EVERY task — lets us spot stages where
    // triangle/texrect submission goes to zero (e.g. blank cinematic stages
    // where particles SHOULD be rendering but the foreground is missing).
    if (log_dpc()) {
        // Brief per-task summary. Useful for spotting cinematic stages
        // where triangle/texrect submission goes to zero or spikes (e.g.
        // tasks #948-949 with tri=8000+ are the explosion sphere bursts).
        const uint32_t tri_count = g_task_gfx_op_count[0x05] + g_task_gfx_op_count[0x07];
        const uint32_t texrect_count = g_task_gfx_op_count[0xE4] + g_task_gfx_op_count[0xE5];
        fprintf(stderr,
            "[task-brief] #%llu tri=%u texrect=%u fs=%u iters=%u\n",
            (unsigned long long)n, tri_count, texrect_count, fs, iters);
    }
    if (log_dpc() && (n <= 16 || (n & 255) == 0 || target_task_outer || log_capped)) {
        // Detailed per-task dump (cmd words + rdp bytes + opcode histogram).
        // Triggered for first 16 tasks, every 256th, target tasks, and
        // any iteration-capped task. Heavy output; gated on ROGUESQ_LOG_DPC.
        fprintf(stderr,
            "[task] #%llu iters=%u data_size=%u r17=0x%X cmd=[%08X %08X] rdp_bytes=%u cmds=%u fullsyncs=%u%s\n",
            (unsigned long long)n, iters, data_size, r17, cmd_w0, cmd_w1,
            bytes, cmds, fs,
            capped_no_fs ? " CAPPED-NO-FS" : "");
        // Top-8 gfx opcode dump (full byte 0xB0..0xFF range plus low ops).
        // Identifies what Factor5 actually dispatches per task — including
        // lighting-related ops (G_MOVEMEM 0x03/0xDB, G_SETLIGHTS macros).
        // First capped task ALSO dumps every non-zero op for full coverage.
        {
            uint32_t copy[256];
            for (int i = 0; i < 256; i++) copy[i] = g_task_gfx_op_count[i];
            for (int slot = 0; slot < 8; slot++) {
                int max_idx = 0;
                for (int i = 0; i < 256; i++) {
                    if (copy[i] > copy[max_idx]) max_idx = i;
                }
                if (copy[max_idx] == 0) break;
                fprintf(stderr, "  [task#%llu gfx] op 0x%02X = %u\n",
                    (unsigned long long)n, (unsigned)max_idx, copy[max_idx]);
                copy[max_idx] = 0;
            }
            // Full non-zero dump for first 4 tasks (attribution screen) +
            // first task with substantial work (memory module phase) +
            // first capped-no-fs task (cinematic). Three phases captured.
            static bool s_first_capped_dumped = false;
            static bool s_first_substantial_dumped = false;
            const bool substantial = (iters > 1000 && !s_first_substantial_dumped);
            if (substantial) s_first_substantial_dumped = true;
            // Targeted task numbers — user observation that #512 / #768 are
            // when particle explosions are expected. Force a full op +
            // setcombine dump for those frames so we can identify what
            // muxes/triangles the explosion phase emits beyond the
            // already-known fb-blit (mux 0xFC11FE23) and 64-tri (mux
            // 0xFC127FFF) pair seen in task #290.
            const bool target_task = (n == 512 || n == 768 || n == 256 ||
                                      n == 384 || n == 640 || n == 896 ||
                                      n == 290 || n == 320 || n == 350);
            const bool dump_full = (n <= 4) || substantial || target_task ||
                                   (capped_no_fs && !s_first_capped_dumped);
            if (dump_full) {
                if (capped_no_fs) s_first_capped_dumped = true;
                fprintf(stderr, "  [task#%llu gfx-FULL] all non-zero ops:\n",
                    (unsigned long long)n);
                for (int i = 0; i < 256; i++) {
                    if (g_task_gfx_op_count[i] > 0) {
                        fprintf(stderr, "    op 0x%02X = %u\n",
                            (unsigned)i, g_task_gfx_op_count[i]);
                    }
                }
                // Distinct G_SETCOMBINE muxes for this task. Multi-pass
                // rendering shows up here as 2+ entries with different muxes.
                fprintf(stderr,
                    "  [task#%llu setcombine] total=%u uniq=%u overflow=%u\n",
                    (unsigned long long)n, g_task_combine_total,
                    g_task_combine_uniq, g_task_combine_overflow);
                for (uint32_t i = 0; i < g_task_combine_uniq; i++) {
                    fprintf(stderr, "    mux #%u w0=0x%08X w1=0x%08X count=%u\n",
                        i, g_task_combine[i].w0, g_task_combine[i].w1,
                        g_task_combine[i].count);
                }
                // G_MOVEMEM index breakdown: which kinds of state are being
                // loaded (lights, matrices, viewport, etc.).
                fprintf(stderr, "  [task#%llu movemem-idx]\n",
                    (unsigned long long)n);
                for (int i = 0; i < 256; i++) {
                    if (g_task_movemem_idx_count[i] > 0) {
                        const char *name = "?";
                        switch (i) {
                            case 0x80: name = "VIEWPORT"; break;
                            case 0x82: name = "LOOKAT_Y"; break;
                            case 0x84: name = "LOOKAT_X"; break;
                            case 0x86: name = "L0"; break;
                            case 0x88: name = "L1"; break;
                            case 0x8A: name = "L2"; break;
                            case 0x8C: name = "L3"; break;
                            case 0x8E: name = "L4"; break;
                            case 0x90: name = "L5"; break;
                            case 0x92: name = "L6"; break;
                            case 0x94: name = "L7"; break;
                            case 0x96: name = "TXTATT"; break;
                            case 0x98: name = "MTX_2"; break;
                            case 0x9A: name = "MTX_3"; break;
                            case 0x9C: name = "MTX_4"; break;
                            case 0x9E: name = "MTX_1"; break;
                        }
                        fprintf(stderr, "    idx 0x%02X (%s) = %u\n",
                            (unsigned)i, name, g_task_movemem_idx_count[i]);
                    }
                }
            }
            fflush(stderr);
        }
        fflush(stderr);
        // For cap-without-fullSync tasks, dump the opcode histogram (top 8).
        // Helps identify the loop: if one opcode dominates, that's the stuck
        // command. Reset is unconditional below.
        if (log_capped) {
            uint32_t copy[64];
            for (int i = 0; i < 64; i++) copy[i] = g_task_op_count[i];
            // Find top 8 by count.
            for (int slot = 0; slot < 8; slot++) {
                int max_idx = 0;
                for (int i = 0; i < 64; i++) {
                    if (copy[i] > copy[max_idx]) max_idx = i;
                }
                if (copy[max_idx] == 0) break;
                fprintf(stderr, "  [task#%llu hist] op 0x%02X = %u\n",
                    (unsigned long long)n, (unsigned)max_idx, copy[max_idx]);
                copy[max_idx] = 0;
            }
            fflush(stderr);
        }
    }
    for (int i = 0; i < 64; i++) g_task_op_count[i] = 0;
    for (int i = 0; i < 256; i++) g_task_gfx_op_count[i] = 0;
    for (int i = 0; i < 256; i++) g_task_movemem_idx_count[i] = 0;
    for (int i = 0; i < 16; i++) { g_task_combine[i].w0 = 0; g_task_combine[i].w1 = 0; g_task_combine[i].count = 0; }
    g_task_combine_uniq = 0;
    g_task_combine_total = 0;
    g_task_combine_overflow = 0;
}

// Submit a synthetic FULL_SYNC by re-using the RDRAM bytes of the most recent
// real FULL_SYNC. Called from factor5_ucode at synthetic-halt for tasks that
// don't naturally emit op 0x29 (cinematic phase). The action_queue is FIFO,
// so all prior submit_rdp_range calls process first; this fullSync runs after
// state has all the task's geometry. Paired with the LoadOperation validity
// check in rt64_state.cpp so partial tile state is skipped, not crashed.
//
// Env var ROGUESQ_NO_SYNTH_FULLSYNC=1 disables this and reverts to the slow
// "wait for real FULL_SYNC bytes" path (~5 fps cinematic) — useful for A/B
// comparison against the higher-rate-but-stalls-at-60s default behavior.
extern "C" void rsp_force_fullsync() {
    static const bool disabled = []() {
        const char *e = std::getenv("ROGUESQ_NO_SYNTH_FULLSYNC");
        bool d = (e != nullptr && *e != '\0' && *e != '0');
        if (d) {
            fprintf(stderr, "[dpc] synthetic FULL_SYNC injection DISABLED via env\n");
            fflush(stderr);
        }
        return d;
    }();
    if (disabled) return;
    uint32_t addr = g_last_fullsync_addr.load(std::memory_order_acquire);
    if (addr == 0xFFFFFFFFu) {
        return;
    }
    const uint64_t synthetic = g_synthetic_submit_serial.fetch_add(1, std::memory_order_acq_rel) + 1;
    g_task_synthetic_fullsyncs.fetch_add(1, std::memory_order_relaxed);
    g_synthetic_consumer_pending.store(true, std::memory_order_release);
    if (log_e9_unified() && (g_e9prov.control || g_e9prov.target)) {
        fprintf(stderr,
                "[e9-synthetic-submit] synthetic=%llu task=%u previous_serial=%llu "
                "previous_lo=0x%06X previous_hi=0x%06X range=0x%06X..0x%06X\n",
                (unsigned long long)synthetic, g_e9prov.task,
                (unsigned long long)g_submit_serial.load(std::memory_order_acquire),
                g_last_submit_lo.load(std::memory_order_acquire),
                g_last_submit_hi.load(std::memory_order_acquire), addr, addr + 8);
        fflush(stderr);
    }
    rs64_rt_submit(addr, addr + 8, 5);
}

// s6712 G1e: split the gfx task's RSP segment into bridge (per-DPC_END submit, task-end commit) vs the rest
// (LLE interpreter + in-ucode probes). ROGUESQ_G1E_AQ=1 arms it (main.cpp reports [g1e-split]); off = one load per call.
// ROGUESQ_G1E_AQ=2 (s6715): per-task ucode wall + call count only; submit_ms/commit_ms read 0.
// g_rs64_aq_spin_ns > 0 busy-waits that long inside the timed submit: the same-run positive control.
#include <chrono>
extern "C" {
uint64_t g_rs64_aq_submit_ns = 0, g_rs64_aq_commit_ns = 0, g_rs64_aq_submit_calls = 0;
uint32_t g_rs64_aq_spin_ns = 0;
int g_rs64_aq_on = -1;
}
#include <time.h>
// CLOCK_UPTIME_RAW is a commpage read; steady_clock (CLOCK_MONOTONIC_RAW) cost ~10% of the ucode at ~50k submits/task (s6712 sample).
static inline uint64_t rs64_aq_now() { return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
extern "C" __attribute__((noinline)) void rs64_g1e_aq_spin(uint64_t until) {
    while (rs64_aq_now() < until) {}
}
// s6954 G1e: ROGUESQ_G1E_AQ=3 times every 16th submit call (x16 estimate) so the per-task ring (ROGUESQ_G1E_TRING) gets a
// submit term without AQ=1's two clock reads per call; the spin control applies to every call.
extern "C" uint32_t rs64_task_rdp_bytes_total() { rs64_bf2_flush(); return g_task_rdp_bytes.load(std::memory_order_relaxed); }
// s7028 G1c: ROGUESQ_G1E_AQ_NULL=1 times an empty noinline call with the same clock pair on every AQ=3 sampled call (x16, like the
// submit term) so the ring can subtract the per-timed-call offset from submit_ms.
extern "C" { uint64_t g_rs64_aq_null_ns = 0; }
static const bool g_aq_null = [] { const char *e = std::getenv("ROGUESQ_G1E_AQ_NULL"); return e && *e && *e != '0'; }();
extern "C" __attribute__((noinline)) void rs64_g1e_aq_null_fn(uint8_t *, uint32_t, uint32_t) { __asm__ volatile("" ::: "memory"); }
extern "C" void rs64_s7751_rdp(const uint8_t* rdram, uint32_t start, uint32_t end); extern "C" int rs64_s7751_on(void);
void rsp_dpc_submit(uint8_t* rdram, uint32_t start, uint32_t end) {
    { static const int s7751 = rs64_s7751_on(); if (s7751) rs64_s7751_rdp(rdram, start, end); }  // s7751 snapshot (raw ucode output)
    if (g_rs64_aq_on == 3) {
        const uint64_t c = ++g_rs64_aq_submit_calls;
        if ((c & 15u) == 0 || g_rs64_aq_spin_ns) {
            const uint64_t t0 = rs64_aq_now();
            rsp_dpc_submit_impl(rdram, start, end);
            if (g_rs64_aq_spin_ns) rs64_g1e_aq_spin(t0 + g_rs64_aq_spin_ns);
            if ((c & 15u) == 0) g_rs64_aq_submit_ns += (rs64_aq_now() - t0) * 16u;
            if ((c & 15u) == 0 && g_aq_null) { const uint64_t t1 = rs64_aq_now(); rs64_g1e_aq_null_fn(rdram, start, end);
                                               g_rs64_aq_null_ns += (rs64_aq_now() - t1) * 16u; }
        } else rsp_dpc_submit_impl(rdram, start, end);
        return;
    }
    if (g_rs64_aq_on != 1) {  // s6715: AQ=2 counts calls without the per-call clock pair (which cost more than the bridge)
        if (g_rs64_aq_on == 2) ++g_rs64_aq_submit_calls;
        rsp_dpc_submit_impl(rdram, start, end); return;
    }
    const uint64_t t0 = rs64_aq_now();
    rsp_dpc_submit_impl(rdram, start, end);
    if (g_rs64_aq_spin_ns) rs64_g1e_aq_spin(t0 + g_rs64_aq_spin_ns);
    g_rs64_aq_submit_ns += rs64_aq_now() - t0;
    ++g_rs64_aq_submit_calls;
}
extern "C" void rs64_dpc_defer_end(int commit) {
    rs64_bf2_flush();  // s7028
    if (g_rs64_aq_on != 1 && g_rs64_aq_on != 3) { rs64_dpc_defer_end_impl(commit); return; }
    const uint64_t t0 = rs64_aq_now();
    rs64_dpc_defer_end_impl(commit);
    g_rs64_aq_commit_ns += rs64_aq_now() - t0;
}
