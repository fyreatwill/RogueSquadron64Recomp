// DPC bridge for RSP graphics ucodes that emit RDP commands directly via
// mtc0 to DPC_START/DPC_END (Factor5 ucode does this). On DPC_END writes
// we forward [start..end) RDRAM bytes to RT64's RDP interpreter (LLE path,
// processDisplayLists with isHLE=false), matching what RT64 would consume
// from raw RDP command bytes.
//
// Reads of DPC_CURRENT/DPC_END return g_rsp_dpc_end so busy-wait loops in
// the ucode see "RDP completed instantly" and exit.

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <atomic>
#include <mutex>
#include <unordered_map>
#include <vector>
#include <utility>

// Per-task RDP range deferral (see rs64_dpc_defer_begin/_end below).
static bool g_defer_active = false;
static std::vector<std::pair<uint32_t, uint32_t>> g_deferred_ranges;
#include "librecomp/rsp.hpp"
#include "ultramodern/events.hpp"

// Direct RT64 entry — the upstream librecomp doesn't expose
// `ultramodern::submit_rdp_range` (that was a fork addition). Bypass the
// runtime layer entirely: shim through rs64_get_rt64_app() and call
// processDisplayLists(isHLE=false). Defined in src/main/rt64_render_context.cpp.
namespace RT64 { class Application; }
extern "C" RT64::Application* rs64_get_rt64_app();
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

// Reset all cross-task DPC emulation state. The ucode's boot/entry takes
// resume-vs-fresh branches based on DPC registers; state leaking from the
// previous task steers ~1/5 tasks into a resume path that loads the trig
// segment over the DL staging area (2026-07-13 canary bisect).
extern "C" void rs64_dpc_reset() {
    g_rsp_dpc_start = 0;
    g_rsp_dpc_end = 0;
    g_rsp_dpc_current = 0;
    s_dpc_poll_last = 0xFFFFFFFFu;
    s_dpc_poll_repeats = 0;
    s_submit_dl_base = 0;
    s_submit_last_end = 0;
}

uint32_t rs64_dpc_current_read() {
    uint32_t& s_last = s_dpc_poll_last;
    int& s_repeats = s_dpc_poll_repeats;
    uint32_t v = g_rsp_dpc_current;
    if (v == s_last) {
        if (++s_repeats >= 64) {
            s_repeats = 0;
            return v + 8;
        }
    } else {
        s_last = v;
        s_repeats = 0;
    }
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
static std::atomic<uint32_t> g_task_rdp_cmds{0};
static std::atomic<uint32_t> g_task_rdp_fullsyncs{0};
// Per-task RDP opcode histogram (low 6 bits of first byte = op). Bridge and
// task_log_and_reset both run on the RSP task thread, so plain array is fine.
static uint32_t g_task_op_count[64] = {0};

struct Rs64E9Provenance {
    struct FrameEvent {
        uint32_t kind;
        uint32_t slot;
        uint32_t target;
        uint32_t pc;
    };
    uint32_t task = 0;
    uint32_t guest = 0;
    uint32_t emitted = 0;
    uint32_t submitted = 0;
    uint32_t authoritative = 0;
    uint32_t dispatched = 0;
    uint32_t matched = 0;
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
    uint32_t source_first = 0xFFFFFFFFu;
    uint32_t source_last = 0xFFFFFFFFu;
    bool target = false;
    bool control = false;
    std::vector<uint32_t> emitted_addrs;
    uint32_t first_guest = 0xFFFFFFFFu;
    uint32_t first_emit = 0xFFFFFFFFu;
    uint32_t first_authoritative = 0xFFFFFFFFu;
    uint32_t first_match = 0xFFFFFFFFu;
    std::vector<uint32_t> fetched_addrs;
    std::vector<uint32_t> spanned_addrs;
    uint32_t non_e9_spans = 0;
    uint32_t uncovered = 0;
    std::vector<FrameEvent> frame_first;
    std::vector<FrameEvent> frame_last;
    uint32_t pending_pop_slot = 0xFFFFFFFFu;
    uint32_t pending_pop_pc = 0xFFFFFFFFu;
};
static Rs64E9Provenance g_e9prov;
static std::atomic<uint32_t> g_e9prov_latch_remaining{0};

static bool log_e9_provenance() {
    static const bool enabled = [] {
        const char *e = std::getenv("ROGUESQ_LOG_E9_PROVENANCE");
        return e && *e && *e != '0';
    }();
    return enabled;
}

extern "C" void rs64_e9prov_task_begin(uint32_t task) {
    g_e9prov = {};
    g_e9prov.task = task;
    uint32_t remaining = g_e9prov_latch_remaining.load(std::memory_order_acquire);
    while (remaining != 0 && !g_e9prov_latch_remaining.compare_exchange_weak(
        remaining, remaining - 1, std::memory_order_acq_rel, std::memory_order_acquire)) {}
    g_e9prov.target = remaining != 0;
    g_e9prov.control = task <= 4;
    g_e9prov.first_guest = 0xFFFFFFFFu;
    g_e9prov.first_emit = 0xFFFFFFFFu;
}

extern "C" void rs64_e9prov_section2_latch() {
    if (!log_e9_provenance()) return;
    g_e9prov_latch_remaining.store(64, std::memory_order_release);
    fprintf(stderr, "[e9-prov-latch] section=2 next_tasks=64\n");
    fflush(stderr);
}

extern "C" void rs64_e9prov_guest(uint32_t guest_addr, uint32_t) {
    if (!log_e9_provenance()) return;
    ++g_e9prov.guest;
    if (g_e9prov.first_guest == 0xFFFFFFFFu) g_e9prov.first_guest = guest_addr & 0x7FFFFFu;
}

extern "C" void rs64_e9prov_source_fetch(uint32_t guest_addr, uint32_t w0) {
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

static void rs64_e9prov_frame_event(uint32_t kind, uint32_t slot, uint32_t target, uint32_t pc) {
    if (!log_e9_provenance()) return;
    ++(kind == 1 ? g_e9prov.frame_push : kind == 2 ? g_e9prov.frame_pop : g_e9prov.frame_resume);
    if (slot < g_e9prov.frame_min_slot) g_e9prov.frame_min_slot = slot;
    if (slot > g_e9prov.frame_max_slot) g_e9prov.frame_max_slot = slot;
    Rs64E9Provenance::FrameEvent event{kind, slot, target, pc};
    if (g_e9prov.frame_first.size() < 8) g_e9prov.frame_first.push_back(event);
    if (g_e9prov.frame_last.size() == 8) g_e9prov.frame_last.erase(g_e9prov.frame_last.begin());
    g_e9prov.frame_last.push_back(event);
}

extern "C" void rs64_e9prov_frame_push(uint32_t slot, uint32_t saved_target, uint32_t saved_pc) {
    rs64_e9prov_frame_event(1, slot, saved_target, saved_pc);
}

extern "C" void rs64_e9prov_frame_pop(uint32_t slot, uint32_t saved_target, uint32_t saved_pc) {
    rs64_e9prov_frame_event(2, slot, saved_target, saved_pc);
    g_e9prov.pending_pop_slot = slot;
    g_e9prov.pending_pop_pc = saved_pc;
}

extern "C" void rs64_e9prov_frame_resume(uint32_t slot, uint32_t resumed_pc) {
    rs64_e9prov_frame_event(3, slot, 0, resumed_pc);
    if (slot == 0) ++g_e9prov.frame_zero_resume;
    if (g_e9prov.pending_pop_slot != slot || g_e9prov.pending_pop_pc != resumed_pc) ++g_e9prov.frame_resume_mismatch;
    g_e9prov.pending_pop_slot = 0xFFFFFFFFu;
    g_e9prov.pending_pop_pc = 0xFFFFFFFFu;
}

extern "C" void rs64_e9prov_task_end(uint32_t task) {
    if (!log_e9_provenance() || g_e9prov.task != task) return;
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
        }
    }
    static uint32_t controls = 0;
    if ((g_e9prov.control && ++controls <= 4) || g_e9prov.target) {
        fprintf(stderr, "[e9-prov] task=%u scope=%s guest=%u emit=%u submit=%u raw=%u dispatch=%u match=%u "
                "src_fetch=%u src_e9=%u src_end=%u src_kind=%u src0=0x%06X src_last=0x%06X src_end0=0x%06X "
                "unwind=%u unwind_natural=%u unwind_last=0x%08X frame=push:%u,pop:%u,resume:%u,zresume:%u,slot:%u..%u,mis:%u span=%u gap=%u guest0=0x%06X emit0=0x%06X raw0=0x%06X match0=0x%06X\n",
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
                g_e9prov.non_e9_spans, g_e9prov.uncovered,
                g_e9prov.first_guest, g_e9prov.first_emit, g_e9prov.first_authoritative,
                g_e9prov.first_match);
        const auto dump_frame = [task](const char* edge, const std::vector<Rs64E9Provenance::FrameEvent>& events) {
            for (const auto& event : events) {
                fprintf(stderr, "[e9-prov-frame] task=%u edge=%s kind=%c slot=0x%X target=0x%06X pc=0x%06X\n",
                        task, edge, event.kind == 1 ? 'P' : event.kind == 2 ? 'O' : 'R',
                        event.slot, event.target & 0x7FFFFFu, event.pc & 0x7FFFFFu);
            }
        };
        dump_frame("first", g_e9prov.frame_first);
        dump_frame("last", g_e9prov.frame_last);
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
            if (g_e9prov.control || g_e9prov.target) {
                fprintf(stderr,
                        "[e9-prov-span] task=%u scope=%s addr=0x%06X span=0x%06X..0x%06X raw=0x%02X len=%u pending=%u\n",
                        g_e9prov.task, g_e9prov.control ? "control" : "sec2", emitted,
                        start, end, raw_opcode, (end - start) / 8u, pending);
            }
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

void rsp_dpc_submit(uint8_t* rdram, uint32_t start, uint32_t end) {
    if (end <= start) {
        return;
    }

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

    if (start_phys != s_dl_base) {
        s_dl_base = start_phys;
        s_last_end = start_phys;
    }

    if (end_phys <= s_last_end) {
        if (end_phys == s_last_end) {
            // Exactly where we left off: nothing new to forward.
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
        if (n <= 4 || (n % 4096) == 0) {
            fprintf(stderr, "[dpc-wrap #%d] end=0x%06X < seen=0x%06X start=0x%06X (dropped)\n",
                    n, end_phys, s_last_end, start_phys);
            fflush(stderr);
        }
        return;
    }

    uint32_t submit_lo = s_last_end;
    uint32_t submit_hi = end_phys;
    s_last_end = end_phys;
    // Note: sticky last-submit is updated at the actual ultramodern::
    // submit_rdp_range call sites below (live + deferred commit), not here.
    // Updating here records the last 8-byte DPC_END bump, which is NOT the
    // range processRDPLists sees after merge/defer (s662 false correlation).

    {
        static std::atomic<uint64_t> s_fwd_bytes{0};
        static std::atomic<uint64_t> s_fwd_submits{0};
        const uint64_t bytes = s_fwd_bytes.fetch_add(submit_hi - submit_lo) + (submit_hi - submit_lo);
        const uint64_t submits = s_fwd_submits.fetch_add(1) + 1;
        if ((submits % 16384) == 0) {
            fprintf(stderr, "[dpc-fwd] submits=%llu bytes=%llu (%.1f MB)\n",
                    (unsigned long long)submits, (unsigned long long)bytes, bytes / 1048576.0);
            fflush(stderr);
        }
    }

    // Garbage tasks (trig data executed as DL) write junk DPC pointers; any
    // range outside 8MB RDRAM would make the diagnostics below (and RT64)
    // read OOB host memory. Drop it before the first dereference.
    if (submit_lo >= 0x800000 || submit_hi > 0x800000 || submit_hi <= submit_lo) {
        static int s_n = 0;
        if (++s_n <= 16 || (s_n & 255) == 0) {
            fprintf(stderr, "[dpc-oob-range #%d] dropping submit range 0x%08X..0x%08X\n",
                    s_n, submit_lo, submit_hi);
        }
        return;
    }

    g_task_rdp_bytes.fetch_add(submit_hi - submit_lo, std::memory_order_relaxed);
    g_task_rdp_cmds.fetch_add(1, std::memory_order_relaxed);
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
            extern uint8_t dmem[];
            fprintf(stderr, "[early-dump #%u] DMEM 0x170-0x1C0 host order:\n", n);
            for (uint32_t row = 0; row < 5; ++row) {
                uint32_t base = 0x170u + row * 16;
                fprintf(stderr, "  %03X:", base);
                for (uint32_t col = 0; col < 16; ++col) {
                    fprintf(stderr, " %02X", (unsigned)dmem[base + col]);
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
            const bool oob_high  = (addr24 >= 0x00800000u);
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
                        extern uint8_t dmem[];  // defined in librecomp/rsp.cpp
                        fprintf(stderr, "[mem-dump-DMEM] 1KB (host order, DMEM 0x000-0x400):\n");
                        for (uint32_t row = 0; row < 64; ++row) {
                            uint32_t base = row * 16;
                            fprintf(stderr, "  %03X:", base);
                            for (uint32_t col = 0; col < 16; ++col) {
                                fprintf(stderr, " %02X", (unsigned)dmem[base + col]);
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
                g_deferred_ranges.emplace_back(kSynthFsPhys, kSynthFsPhys + 8);
            } else {
                ultramodern::submit_rdp_range(kSynthFsPhys, kSynthFsPhys + 8);
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

        if (op6_head == 0x27) {
            if (inject_synth_fullsync(/*replace_pipe_hist=*/true)) {
                return; // drop the PIPE; synth FULL_SYNC already queued
            }
            (void)rdram;
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
                    const uint32_t off = (uint32_t)mips & 0x7FFFFF;
                    if (off + 8 <= 0x800000) {
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
            if (g_cine_last_cimg_addr >= 0x00800000u) {
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
                const bool drop_high = (addr24 >= 0x00800000u);
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
                    return;
                }
            }
        }
    }

    // Defer layer: while a task is running, hold ranges instead of feeding
    // RT64 live. The runner commits them on clean ucode exit and drops them
    // on UnhandledJumpTarget, so garbage streams (trig data executed as DL)
    // never reach RT64's deferred state. Gfx-thread only, no locking needed.
    if (g_defer_active) {
        g_deferred_ranges.emplace_back(submit_lo, submit_hi);
        return;
    }

    if (should_drop_wrap_rdp(submit_lo, submit_hi)) {
        return;
    }

    rs64_e9prov_mark_submitted(submit_lo, submit_hi);
    g_last_submit_lo.store(submit_lo, std::memory_order_release);
    g_last_submit_hi.store(submit_hi, std::memory_order_release);
    ultramodern::submit_rdp_range(submit_lo, submit_hi);
}

extern "C" void rs64_dpc_defer_begin() {
    g_defer_active = true;
    g_deferred_ranges.clear();
}

extern "C" void rs64_dpc_defer_end(int commit) {
    g_defer_active = false;
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
            uint32_t lo = g_deferred_ranges[0].first;
            uint32_t hi = g_deferred_ranges[0].second;
            for (size_t i = 1; i < g_deferred_ranges.size(); i++) {
                const auto &r = g_deferred_ranges[i];
                if (r.first == hi) {
                    hi = r.second;
                    continue;
                }

                if (!should_drop_wrap_rdp(lo, hi)) {
                    rs64_e9prov_mark_submitted(lo, hi);
                    bytes += hi - lo;
                    calls++;
                    g_last_submit_lo.store(lo, std::memory_order_release);
                    g_last_submit_hi.store(hi, std::memory_order_release);
                    ultramodern::submit_rdp_range(lo, hi);
                }
                lo = r.first;
                hi = r.second;
            }

            if (!should_drop_wrap_rdp(lo, hi)) {
                rs64_e9prov_mark_submitted(lo, hi);
                bytes += hi - lo;
                calls++;
                g_last_submit_lo.store(lo, std::memory_order_release);
                g_last_submit_hi.store(hi, std::memory_order_release);
                ultramodern::submit_rdp_range(lo, hi);
            }
        }
        else {
            for (const auto& r : g_deferred_ranges) {
                if (should_drop_wrap_rdp(r.first, r.second)) {
                    continue;
                }
                bytes += r.second - r.first;
                calls++;
                rs64_e9prov_mark_submitted(r.first, r.second);
                g_last_submit_lo.store(r.first, std::memory_order_release);
                g_last_submit_hi.store(r.second, std::memory_order_release);
                ultramodern::submit_rdp_range(r.first, r.second);
            }
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
        if (getenv("ROGUESQ_TRACE_DISPATCH") && (++s_c <= 64 || (s_c & 63) == 0)) {
            fprintf(stderr, "[defer-commit #%d] %zu ranges, %u bytes\n",
                    s_c, g_deferred_ranges.size(), bytes);
        }
    } else if (!g_deferred_ranges.empty()) {
        uint32_t bytes = 0;
        for (const auto& r : g_deferred_ranges) bytes += r.second - r.first;
        static int s_n = 0;
        if (++s_n <= 32 || (s_n & 63) == 0) {
            fprintf(stderr, "[defer-drop #%d] discarded %zu RDP ranges (%u bytes) from failed task\n",
                    s_n, g_deferred_ranges.size(), bytes);
            fflush(stderr);
        }
    }
    g_deferred_ranges.clear();
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
    ultramodern::submit_rdp_range(addr, addr + 8);
}
