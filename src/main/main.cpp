#include <mach/mach_time.h> // s7766 [inlat] (also included again later; header is guarded)
#include <algorithm>
#include <string>
#include <cmath>
#include "rs64_rdram_peek.h"
#include <dlfcn.h>
#include <cstdio>
#include <cstdarg>
#include <cstdlib>
#include <cstring>
#include <csignal>
#include <vector>
#include <map>
#include <array>
#include <set>
#include <mutex>
#include <cinttypes>
#include <filesystem>
#include <thread>
#include <chrono>
#include <atomic>
#include <tuple>
#include <functional>

#include "ultramodern/ultra64.h"
#include "ultramodern/ultramodern.hpp"

extern "C" void rs64_m5_route_prepare_handoff(uint32_t prepare_seq,
                                                uint32_t phase, uint32_t width,
                                                uint32_t origin, uint32_t accepted);
#include "ultramodern/events.hpp"
#include "ultramodern/error_handling.hpp"
#include "librecomp/game.hpp"
#include "librecomp/rsp.hpp"
#include "common/rt64_common.h"

#define SDL_MAIN_HANDLED
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <Windows.h>
#include <DbgHelp.h>
#include <TlHelp32.h>
#pragma comment(lib, "Dbghelp.lib")
#include <crtdbg.h>
#include "SDL.h"
#include "SDL_syswm.h"
#else
#include "SDL2/SDL.h"
#include "SDL2/SDL_syswm.h"
#include "win_compat.h"
#include <execinfo.h>
#include <unistd.h>
#include <sys/ucontext.h>
#include <sys/mman.h>
#include <dlfcn.h>
#if defined(__APPLE__) && defined(__aarch64__)
#include <mach-o/dyld.h>
#include <mach/mach.h>
#include <mach/mach_vm.h>
#include <mach/thread_act.h>
#include <mach/thread_status.h>
#include <pthread.h>
#include <algorithm>
#include <cerrno>
#include <string>
#include <cctype>
#endif
#endif

// N64 button bitmasks (from libultra PR/controller.h)
#define N64_A_BUTTON     0x8000
#define N64_B_BUTTON     0x4000
#define N64_Z_TRIG       0x2000
#define N64_START_BUTTON 0x1000
#define N64_U_JPAD       0x0800
#define N64_D_JPAD       0x0400
#define N64_L_JPAD       0x0200
#define N64_R_JPAD       0x0100
#define N64_L_TRIG       0x0020
#define N64_R_TRIG       0x0010
#define N64_U_CBUTTONS   0x0008
#define N64_D_CBUTTONS   0x0004
#define N64_L_CBUTTONS   0x0002
#define N64_R_CBUTTONS   0x0001

// ---------------------------------------------------------------------------
// Forward declarations
// ---------------------------------------------------------------------------
void rs64_register_overlays();
extern "C" void recomp_entrypoint(uint8_t* rdram, recomp_context* ctx);
extern "C" void do_break(uint32_t vram); // librecomp; s7575 control
extern "C" uint32_t rs64_vi_committed_width();
extern "C" uint32_t rs64_dpc_get_cumulative_fullsyncs();
extern "C" uint32_t rs64_vi_committed_origin();
extern "C" int rs64_g1d_pause_live(void);
extern "C" uint32_t rs64_phase_ord();
extern "C" double rs64_elapsed_seconds(void);
extern "C" volatile uint32_t rs64_vi_n_g; // s6808: ROGUESQ_AI_TRACE 6th column = update_screen # (ROGUESQ_VI_WALL key)
extern "C" void rs64_audio_route_set(const char* arm, uint32_t phase,
                                       uint32_t width, uint32_t origin,
                                       uint32_t ordinal, uint32_t row,
                                       int exit_reason);
static bool rs64_m5_audio_host_probe_enabled(uint32_t& phase, uint32_t& width,
                                               uint32_t& origin);
static uint32_t rs64_m5_audio_queue_snapshot();
static uint32_t rs64_m5_pcm_consumer_count();
static bool rs64_m5_callback_order_event(uint32_t width, uint32_t origin,
                                         uint32_t& sequence, uint64_t& time_us);
extern "C" void rs64_audio_join_image_stage(const char* arm,
                                               uint32_t ordinal, uint32_t row,
                                               uint32_t phase, uint32_t width,
                                               uint32_t origin, uint32_t stage,
                                               uint32_t dest, uint32_t len,
                                               uint32_t fnv, uint32_t nonzero,
                                               uint32_t dest_valid,
                                               uint32_t task_data_ptr,
                                               uint64_t task_generation,
                                               uint32_t handoff_thread,
                                               uint32_t event_thread,
                                               uint64_t latest_generation,
                                               uint32_t latest_route_seq,
                                               uint32_t latest_route_ordinal,
                                               uint32_t latest_route_row);
extern "C" void rs64_audio_join_image_source(
    const char* arm, uint32_t ordinal, uint32_t row, uint32_t phase,
    uint32_t width, uint32_t origin, uint64_t source_event,
    uint32_t task_data_ptr, uint32_t dram, uint32_t len, uint32_t fnv,
    uint32_t nonzero, uint64_t task_generation, uint32_t handoff_thread,
    uint32_t event_thread, uint32_t input_fnv, uint32_t input_nonzero,
    uint32_t input_dram, uint32_t input_len, uint32_t input_dmem,
    uint32_t input_task_data_ptr);
extern "C" void rs64_audio_join_image_complete(const char* arm,
                                                  uint32_t ordinal, uint32_t row,
                                                  uint32_t phase, uint32_t width,
                                                  uint32_t origin);
extern "C" bool rs64_audio_current_route_snapshot(
    uint32_t* phase, uint32_t* width, uint32_t* origin, uint32_t* ordinal,
    uint32_t* row, int* exit_reason, const char** arm);
extern "C" uint32_t rs64_audio_rate_snapshot();
extern "C" volatile uint8_t* volatile g_recomp_rdram_for_wp_raw;
extern "C" void rs64_m5_audio_join_snapshot(
    const char* arm, uint32_t ordinal, uint32_t row, uint32_t phase,
    uint32_t width, uint32_t origin, uint64_t* task_generation,
    uint64_t* source_match_event, uint64_t* consumer_match_event,
    uint64_t* stage_event);
extern "C" uint64_t rs64_audio_join_m5_event(
    const char* kind, uint32_t site, uint32_t active, const char* arm,
    uint32_t phase, uint32_t width, uint32_t origin, uint32_t ordinal,
    uint32_t row, uint32_t idx, uint32_t dest, uint32_t value0,
    uint32_t value1, uint32_t value2, uint32_t value3);
extern "C" uint64_t rs64_m5_route_handoff_event(
    const char* edge, uint32_t site, uint32_t active, const char* arm,
    uint32_t phase, uint32_t width, uint32_t origin, uint32_t ordinal,
    uint32_t row, uint32_t value0, uint32_t value1, uint32_t value2);
extern "C" uint64_t rs64_m5_latest_audio_generation();
extern "C" void rs64_m5_audio_transition_commit(uint32_t width,
                                                   uint32_t origin,
                                                   uint32_t phase);
extern "C" void rs64_m5_audio_transition_event(const char* kind,
                                                  uint32_t site,
                                                  uint32_t phase,
                                                  uint32_t width,
                                                  uint32_t origin);
static uint32_t rs64_m5_identity_thread_id();

namespace {
std::mutex g_rs64_m5_audio_transition_mutex;
bool g_rs64_m5_audio_transition_open = false;
extern "C" int g_rs64_s5508_in_mission = 0; /* s5508: set by initMission hook, gates [mfst] log */
uint32_t g_rs64_m5_audio_transition_window = 0;
uint32_t g_rs64_m5_audio_transition_rows = 0;
}

static thread_local uint32_t s_pending_task_data_ptr  = 0;
static thread_local uint32_t s_pending_task_data_size = 0;
static thread_local uint32_t s_pending_task_ucode_data = 0;
static thread_local uint32_t s_pending_task_ucode_data_size = 0;
static std::atomic<uint32_t> s_pending_task_guest_ptr{0};

extern "C" uint64_t rs64_m5_route_handoff_event(
    const char* edge, uint32_t site, uint32_t active, const char* arm,
    uint32_t phase, uint32_t width, uint32_t origin, uint32_t ordinal,
    uint32_t row, uint32_t value0, uint32_t value1, uint32_t value2) {
    return rs64_audio_join_m5_event(
        edge, site, active, arm, phase, width, origin, ordinal, row,
        0u, value0, value1, value2, 0u, 0u);
}

static thread_local const OSTask* s_pending_audio_task = nullptr;
static thread_local uint64_t s_pending_audio_generation = 0;
static thread_local uint32_t s_pending_audio_thread_id = 0;
static std::atomic<uint64_t> g_audio_task_generation{1};
static std::atomic<uint64_t> g_m5_latest_audio_generation{0};
static std::atomic<uint32_t> g_m5_latest_audio_route_seq{0};
static std::atomic<uint32_t> g_m5_latest_audio_route_ordinal{0xFFFFFFFFu};
static std::atomic<uint32_t> g_m5_latest_audio_route_row{0xFFFFFFFFu};

extern "C" uint64_t rs64_m5_latest_audio_generation() {
    return g_m5_latest_audio_generation.load(std::memory_order_acquire);
}

extern "C" volatile uint32_t g_rs64_last_guest_pc;

extern "C" void rs64_m5_dispatch_boundary(uint32_t target_pc) {
    static int enabled = -1;
    static uint32_t control = 0;
    static uint32_t rows = 0;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_SECOND_EXEC");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target_phase =
        (width == 1024u && origin == 0x00790400u) ||
        (width == 512u && origin == 0x006AB400u);
    const bool target = target_pc == 0x800078E0u;
    const bool positive_control = target_pc == 0x8009123Cu;
    if (!target_phase && !positive_control) return;
    if (!target && !positive_control) return;
    uint32_t phase = rs64_phase_ord();
    uint32_t ordinal = 0xFFFFFFFFu, row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &row, &exit_reason, &arm);
    if (!control) {
        std::fprintf(stderr,
            "[m5-dispatch-boundary-control] phase=%u width=%u origin=0x%06X"
            " target=0x%08X caller=0x%08X arm=%s active=%u\n",
            phase, width, origin, target_pc,
            static_cast<uint32_t>(g_rs64_last_guest_pc), arm ? arm : "n/a",
            active ? 1u : 0u);
        std::fflush(stderr);
        control = 1;
    }
    if (!target || rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-dispatch-boundary] n=%u target=0x%08X caller=0x%08X"
        " phase=%u width=%u origin=0x%06X arm=%s ordinal=%u row=%u"
        " active=%u exit=%d\n",
        rows, target_pc, static_cast<uint32_t>(g_rs64_last_guest_pc),
        phase, width, origin, arm ? arm : "n/a", ordinal, row,
        active ? 1u : 0u, exit_reason);
    std::fflush(stderr);
    ++rows;
}

extern "C" void rs64_m5_dynamic_callback(uint32_t context,
                                           uint32_t handler,
                                           uint32_t update,
                                           uint32_t ra) {
    static int enabled = -1;
    static uint32_t rows = 0;
    static uint32_t bucket = 0xFFFFFFFFu;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_DYNAMIC_CALLBACK");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    const uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) { bucket = next_bucket; rows = 0; }
    if (rows >= 512u) return;
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    std::fprintf(stderr,
        "[m5-dynamic-callback] n=%u phase=%u width=%u origin=0x%06X "
        "arm=%s ordinal=%u row=%u active=%u context=0x%08X "
        "handler=0x%08X stored=0x%08X pre=0x%08X ra=0x%08X exit=%d\n",
        rows, rs64_phase_ord(), width, origin, arm ? arm : "n/a",
        ordinal, route_row, active ? 1u : 0u, context, handler, update,
        update, ra, exit_reason);
    std::fflush(stderr);
    ++rows;
}

namespace {
struct M5CallbackWriterRow {
    uint32_t pc;
    uint32_t edge;
    uint32_t value;
    uint32_t count;
};

std::mutex g_m5_callback_writer_mutex;
M5CallbackWriterRow g_m5_callback_writer_rows[32] = {};
uint32_t g_m5_callback_writer_row_count = 0;
uint32_t g_m5_callback_writer_total = 0;
uint32_t g_m5_callback_writer_dumped = 0;
}

extern "C" void rs64_m5_callback_writer_event(uint32_t pc,
                                                uint32_t edge,
                                                uint32_t value) {
    static int enabled = -1;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_CALLBACK_WRITER");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target_phase =
        (width == 1024u && origin == 0x00790400u) ||
        (width == 512u && origin == 0x006AB400u);
    const bool registration_callsite =
        pc == 0x80002FDCu || pc == 0x8009BC50u;
    const bool callback_table_store = pc == 0x80007928u ||
                                      pc == 0x80007968u ||
                                      pc == 0x80017D08u;
    const bool callback_pointer_store = pc == 0x80091900u;
    if (!target_phase && !registration_callsite && !callback_table_store &&
        !callback_pointer_store) return;
    std::lock_guard<std::mutex> lock(g_m5_callback_writer_mutex);
    ++g_m5_callback_writer_total;
    for (uint32_t i = 0; i < g_m5_callback_writer_row_count; ++i) {
        auto& row = g_m5_callback_writer_rows[i];
        if (row.pc == pc && row.edge == edge && row.value == value) {
            ++row.count;
            return;
        }
    }
    if (g_m5_callback_writer_row_count < 32u) {
        auto& row = g_m5_callback_writer_rows[g_m5_callback_writer_row_count++];
        row = {pc, edge, value, 1};
    }
}

static void rs64_m5_callback_writer_snapshot() {
    static int enabled = -1;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_CALLBACK_WRITER");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    std::lock_guard<std::mutex> lock(g_m5_callback_writer_mutex);
    if (g_m5_callback_writer_total == g_m5_callback_writer_dumped) return;
    std::fprintf(stderr, "[m5-callback-writer-control] phase=%u width=%u "
                         "origin=0x%06X total=%u unique=%u\n",
                 rs64_phase_ord(), rs64_vi_committed_width(),
                 rs64_vi_committed_origin() & 0x00FFFFFFu,
                 g_m5_callback_writer_total, g_m5_callback_writer_row_count);
    for (uint32_t i = 0; i < g_m5_callback_writer_row_count; ++i) {
        const auto& row = g_m5_callback_writer_rows[i];
        std::fprintf(stderr, "[m5-callback-writer-row] n=%u edge=%u pc=0x%08X "
                             "value=0x%08X count=%u\n",
                     i, row.edge, row.pc, row.value, row.count);
    }
    std::fflush(stderr);
    g_m5_callback_writer_dumped = g_m5_callback_writer_total;
}

extern "C" void rs64_m5_callback_entry_event(uint32_t value, uint32_t ra,
                                               uint32_t unused) {
    (void)unused;
    static int enabled = -1;
    static uint32_t rows = 0;
    static uint32_t bucket = 0xFFFFFFFFu;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_CALLBACK_ENTRY");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) { bucket = next_bucket; rows = 0; }
    if (rows >= 64u) return;
    std::fprintf(stderr,
        "[m5-callback-entry] n=%u phase=%u width=%u origin=0x%06X "
        "a0=0x%08X ra=0x%08X\n",
        rows, rs64_phase_ord(), width, origin, value, ra);
    std::fflush(stderr);
    ++rows;
}

extern "C" void rs64_m5_callback_teardown_event(uint32_t kind, uint32_t ra,
                                                  uint32_t slot0, uint32_t slot1,
                                                  uint32_t slot2, uint32_t slot3,
                                                  uint32_t scanned, uint32_t unused) {
    (void)unused;
    static int enabled = -1;
    static uint32_t rows = 0;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_S4700_CB");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target_phase =
        (width == 1024u && origin == 0x00790400u) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase && rows >= 32u) return;
    std::fprintf(stderr,
        "[s4771-cb] n=%u kind=%u phase=%u width=%u origin=0x%06X ra=0x%08X "
        "scanned=%u tbl=%08X %08X %08X %08X\n",
        rows++, kind, rs64_phase_ord(), width, origin, ra, scanned,
        slot0, slot1, slot2, slot3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_callback_transfer_event(uint32_t pc,
                                                  uint32_t target,
                                                  uint32_t value) {
    static int enabled = -1;
    static uint32_t rows = 0;
    static uint32_t bucket = 0xFFFFFFFFu;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_CALLBACK_TRANSFER");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) { bucket = next_bucket; rows = 0; }
    if (rows >= 4096u) return;
    std::fprintf(stderr,
        "[m5-callback-transfer] n=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X target=0x%08X a0=0x%08X\n",
        rows, rs64_phase_ord(), width, origin, pc, target, value);
    std::fflush(stderr);
    ++rows;
}

// Wrapper: captures rdram into the watchdog global on first call so the
// hwbp/poll diagnostic threads can attach. Forwards to the real entrypoint.
extern "C" volatile uint8_t* volatile g_recomp_rdram_for_wp_raw;
extern "C" void rs64_entrypoint_with_rdram_capture(uint8_t* rdram, recomp_context* ctx) {
    g_recomp_rdram_for_wp_raw = rdram;
    if (const char* e = std::getenv("ROGUESQ_LOG_M5_PRETARGET");
        e && e[0] && e[0] != '0') {
        std::fprintf(stderr,
            "[m5-runtime-context] site=rs64_entrypoint_with_rdram_capture "
            "r31=0x%08X r4=0x%08X r5=0x%08X\n",
            (unsigned)ctx->r31, (unsigned)ctx->r4, (unsigned)ctx->r5);
        std::fflush(stderr);
    }
    recomp_entrypoint(rdram, ctx);
}
// The game's N64 "main" function — renamed to avoid clash with C main()
extern "C" void rs_main(uint8_t* rdram, recomp_context* ctx);
gpr get_entrypoint_address();

// ---------------------------------------------------------------------------
// RSP microcode dispatch
// ---------------------------------------------------------------------------
extern RspExitReason factor5_ucode(uint8_t* rdram, uint32_t ucode_addr);
extern RspExitReason factor5_ucode_tls(uint8_t* rdram, uint32_t ucode_addr);  // s6775: old TLS DMEM base arm
extern RspExitReason factor5_ucode_lean(uint8_t* rdram, uint32_t ucode_addr);  // s6940: hook/probe gates compiled out
extern RspExitReason factor5_ucode_nmac(uint8_t* rdram, uint32_t ucode_addr);  // s6941: lean + native NEON multiply ops
extern "C" uint32_t rs64_phase_ord(void);
extern RspExitReason factor5_ucode_b(uint8_t* rdram, uint32_t ucode_addr);
extern "C" void rs64_dpc_defer_begin();
extern "C" void rs64_dpc_reset();
extern "C" void rs64_dpc_defer_end(int commit);
extern "C" { extern uint64_t g_rs64_aq_submit_ns, g_rs64_aq_commit_ns, g_rs64_aq_submit_calls; extern uint32_t g_rs64_aq_spin_ns; extern int g_rs64_aq_on; } // s6712
extern "C" void rs64_dpc_get_task_range(uint32_t *first_lo, uint32_t *first_hi,
                                         uint32_t *last_lo, uint32_t *last_hi,
                                         uint32_t *min_lo, uint32_t *max_hi);
extern RspExitReason factor5_boot (uint8_t* rdram, uint32_t ucode_addr);
extern "C" void rs64_dpc_drain_histogram(uint32_t out[64]);
extern "C" uint32_t rs64_dpc_get_last_fullsync_addr();
extern "C" void rs64_rdp_advance_reset();
extern "C" void rs64_rdp_advance_report(uint32_t task, uint32_t guestDl,
                                          uint32_t guestE9);
extern "C" void rs64_e9prov_aligned(uint32_t task, uint32_t guestDl,
                                      uint32_t guestE9);
extern "C" void rs64_e9prov_task_join_report(uint32_t task);
extern "C" void rs64_e9prov_force_update(void);
extern "C" void rs64_e9prov_task_begin(uint32_t task, uint32_t root_dl,
                                          const uint8_t *rdram, uint32_t ucode_addr);
extern "C" void rs64_e9prov_task_end(uint32_t task);
extern "C" uint32_t rs64_e9prov_current_root_dl();
extern "C" void rs64_inline_probe_trigen_stage(uint32_t dl_ptr, uint32_t boot_130,
                                                  uint32_t staged_130, uint32_t skipped_host_130,
                                                  uint32_t boot_ff0, uint32_t staged_ff0,
                                                  uint32_t skipped_host_ff0);
extern "C" uint32_t rs64_audio_image_break_pc();
extern "C" uint32_t rs64_m5_pcm_task_data_ptr();
extern "C" void rs64_m5_pcm_task_data_set(uint32_t data_ptr);
// Defined in lib/rt64/src/hle/rt64_state.cpp — s171 crash-instant snapshot
// of [vi-fs-decision] state, read from the SIGSEGV/SIGBUS handler below.
extern "C" void rs64_get_vifs_crash_snapshot(uint64_t *decisionN, uint64_t *lastFireDecisionN,
                                              int *lastFireWasStalled, int *stalledNow);
// s265: last-executed-guest-PC breadcrumb. Stamped by submitSceneNodeRender's
// recompiled body (fixup_game_funcs.py-injected, one store per guest
// instruction) so the crash handler below can report exactly which guest
// MIPS instruction was executing, instead of requiring manual native-offset
// disassembly/branch-density correlation (s264's bottleneck). Declared
// `extern` in recomp.h so any RECOMP_FUNC translation unit can write it by
// name; defined once here.
extern "C" volatile uint32_t g_rs64_last_guest_pc = 0;
extern "C" uint32_t rs64_ram_top = 0x80800000u; // s6132: set by librecomp from ROGUESQ_OSMEM_MB
extern "C" int rogue_current_thread_id(uint8_t* rdram);
static thread_local uint32_t g_rs64_m5_field348_static_callsite = 0;
static thread_local uint32_t g_rs64_m5_pcm_callsite = 0;
static thread_local uint32_t g_rs64_m5_static_rs_memset_callsite = 0;
static thread_local uint32_t g_rs64_m5_static_rs_memset_ra = 0;
static std::atomic<uint32_t> g_rs64_m5_clear_object{0};
extern "C" uint64_t rs64_m5_clear_branch_dmem_sequence();
extern "C" uint64_t rs64_m5_clear_branch_source_sequence();

extern "C" void rs64_m5_writer_setup_state(uint8_t* rdram, uint32_t callsite, uint32_t ra,
                                              uint32_t a0, uint32_t a2,
                                              uint32_t s0, uint32_t s1,
                                              uint32_t t0, uint32_t t1) {
    static int enabled = -1;
    static uint32_t bucket = 0xFFFFFFFFu;
    static unsigned rows = 0;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_WRITER_SETUP");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* family = std::getenv("ROGUESQ_LOG_M5_FAMILY_STORE");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (family && family[0] && family[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    if (callsite == 0x8008F2CCu && a2 == 0x298u &&
        a0 >= 0x80000000u && a0 < 0x80800000u) {
        g_rs64_m5_clear_object.store(a0, std::memory_order_release);
    }
    uint32_t width = rs64_vi_committed_width();
    uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && (origin == 0x006AB800u || origin == 0x00790400u)) ||
          (width == 512u && origin == 0x006AB400u))) return;
    uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) { bucket = next_bucket; rows = 0; }
    if (rows >= 128u) return;
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (!rdram || guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        uint32_t p = guest - 0x80000000u;
        return rs64_rdram_u32(rdram, p);
    };
    if (rows == 0u) {
        std::fprintf(stderr, "[m5-writer-setup-input-control] phase=%u width=%u origin=0x%06X\n", rs64_phase_ord(), width, origin);
        std::fflush(stderr);
    }
    std::fprintf(stderr,
        "[m5-writer-setup] n=%u edge=0x%08X phase=%u width=%u origin=0x%06X "
        "ra=0x%08X a0=0x%08X a2=0x%08X s0=0x%08X s1=0x%08X "
        "t0=0x%08X t1=0x%08X target=%u clear_obj=0x%08X alloc_len=0x%X "
        "obj0=0x%08X obj4=0x%08X s0p60=0x%08X s1p60=0x%08X clear0=0x%08X clear4=0x%08X\n",
        rows, callsite, rs64_phase_ord(), width, origin, ra, a0, a2,
        s0, s1, t0, t1,
        (a0 == 0x801797B0u && a2 == 0x298u) ? 1u : 0u,
        g_rs64_m5_clear_object.load(std::memory_order_acquire),
        a2,
        word(a0), word(a0 + 4u), word(s0 + 0x60u), word(s1 + 0x60u), word(0x801797B0u), word(0x801797B4u));
    std::fflush(stderr);
    ++rows;
}

extern "C" void rs64_m5_family_entry(uint8_t* rdram, const char* family, uint32_t pc,
                                       uint32_t a0, uint32_t a1, uint32_t a2,
                                       uint32_t a3, uint32_t ra) {
    static int enabled = -1;
    static unsigned control[3] = {};
    static uint32_t bucket = 0xFFFFFFFFu;
    static unsigned rows[3] = {};
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_FAMILY_EDGE");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled || !family) return;
    unsigned which = family[0] == 'S' ? 0u : (family[0] == 'L' ? 2u : 1u);
    if (control[which] < 2u) {
        std::fprintf(stderr,
            "[m5-family-edge-control] family=%s pc=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X ra=0x%08X\n",
            family, pc, a0, a1, a2, a3, ra);
        std::fflush(stderr);
        ++control[which];
    }
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target_phase =
        (width == 1024u && origin == 0x00790400u) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    const uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) {
        bucket = next_bucket;
        rows[0] = rows[1] = rows[2] = 0;
    }
    if (rows[which] >= 64u) return;
    auto guest_byte = [rdram](uint32_t guest) -> uint32_t {
        if (!rdram || guest < 0x80000000u || guest >= 0x80800000u) return 0xFFFFFFFFu;
        return rdram[(guest - 0x80000000u) ^ 3u];
    };
    const uint32_t state_1ad0 = guest_byte(0x80141AD0u);
    const uint32_t state_3b038 = guest_byte(0x8013B038u);
    const uint32_t state_1ad1 = guest_byte(0x80141AD1u);
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    uint64_t task_generation = 0, source_match_event = 0;
    uint64_t consumer_match_event = 0, stage_event = 0;
    rs64_m5_audio_join_snapshot(
        arm, ordinal, route_row, rs64_phase_ord(), width, origin,
        &task_generation, &source_match_event, &consumer_match_event,
        &stage_event);
    const uint64_t family_event = rs64_audio_join_m5_event(
        "family-entry", pc, active ? 1u : 0u, arm, rs64_phase_ord(), width,
        origin, ordinal, route_row, 0u, a0, a1, a2, a3, ra);
    const uint32_t task_queue = rs64_m5_audio_queue_snapshot();
    const uint32_t pcm_consumers = rs64_m5_pcm_consumer_count();
    const bool target_arg =
        (a0 >= 0x80178C80u && a0 < 0x80178F80u) ||
        (a1 >= 0x80178C80u && a1 < 0x80178F80u) ||
        (a2 >= 0x80178C80u && a2 < 0x80178F80u) ||
        (a3 >= 0x80178C80u && a3 < 0x80178F80u) ||
        (a0 >= 0x801797B0u && a0 < 0x80179A48u) ||
        (a1 >= 0x801797B0u && a1 < 0x80179A48u) ||
        (a2 >= 0x801797B0u && a2 < 0x80179A48u) ||
        (a3 >= 0x801797B0u && a3 < 0x80179A48u);
    std::fprintf(stderr,
        "[m5-family-guest-route] family=%s n=%u pc=0x%08X phase=%u width=%u origin=0x%06X "
        "arm=%s active=%u ordinal=%u row=%u exit=%d task_generation=%llu "
        "event=%llu stage_event=%llu source_match_event=%llu consumer_match_event=%llu "
        "task_queue=%u pcm_consumers=%u target_arg=%u "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X ra=0x%08X "
        "state_1ad0=0x%02X state_3b038=0x%02X state_1ad1=0x%02X\n",
        family, rows[which], pc, rs64_phase_ord(), width, origin,
        arm ? arm : "n/a", active ? 1u : 0u, ordinal, route_row,
        exit_reason, static_cast<unsigned long long>(task_generation),
        static_cast<unsigned long long>(family_event),
        static_cast<unsigned long long>(stage_event),
        static_cast<unsigned long long>(source_match_event),
        static_cast<unsigned long long>(consumer_match_event), task_queue,
        pcm_consumers, target_arg ? 1u : 0u,
        a0, a1, a2, a3, ra,
        state_1ad0, state_3b038, state_1ad1);
    std::fflush(stderr);
    ++rows[which];
}

extern "C" void rs64_m5_family_store(const char* family, uint32_t pc,
                                       char width, uint32_t addr,
                                       uint32_t value) {
    static int enabled = -1;
    static unsigned control[3] = {};
    static uint32_t bucket = 0xFFFFFFFFu;
    static unsigned rows[3] = {};
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_FAMILY_STORE");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled || !family) return;
    unsigned which = family[0] == 'S' ? 0u : (family[0] == 'L' ? 2u : 1u);
    if (control[which] < 2u) {
        std::fprintf(stderr,
            "[m5-family-store-control] family=%s pc=0x%08X width=%c addr=0x%08X value=0x%08X\n",
            family, pc, width, addr, value);
        std::fflush(stderr);
        ++control[which];
    }
    const uint32_t vi_width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool title = vi_width == 1024u && origin == 0x00790400u;
    const bool hangar = vi_width == 512u && origin == 0x006AB400u;
    if (!title && !hangar) return;
    const uint32_t next_bucket = (vi_width << 24) ^ origin;
    if (next_bucket != bucket) {
        bucket = next_bucket;
        rows[0] = rows[1] = rows[2] = 0;
    }
    if (rows[which] >= 256u) return;
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    uint64_t task_generation = 0, source_match_event = 0;
    uint64_t consumer_match_event = 0, stage_event = 0;
    rs64_m5_audio_join_snapshot(
        arm, ordinal, route_row, rs64_phase_ord(), vi_width, origin,
        &task_generation, &source_match_event, &consumer_match_event,
        &stage_event);
    const uint64_t family_event = rs64_audio_join_m5_event(
        "family-store", pc, active ? 1u : 0u, arm, rs64_phase_ord(),
        vi_width, origin, ordinal, route_row, addr, value, 0u, 0u, 0u, 0u);
    const uint32_t task_queue = rs64_m5_audio_queue_snapshot();
    const uint32_t pcm_consumers = rs64_m5_pcm_consumer_count();
    const uint32_t lo = title ? 0x80178C80u : 0x801797B0u;
    const uint32_t hi = title ? 0x80178F80u : 0x80179A48u;
    const bool target = addr >= lo && addr < hi;
    const uint32_t clear_object =
        g_rs64_m5_clear_object.load(std::memory_order_acquire);
    const bool clear_object_exact = clear_object != 0u && addr == clear_object;
    const bool clear_object_span = clear_object != 0u &&
                                   addr >= clear_object &&
                                   addr < clear_object + 0x298u;
    std::fprintf(stderr,
        "[m5-family-store] family=%s n=%u pc=0x%08X width=%c phase=%u vi_width=%u origin=0x%06X "
        "arm=%s active=%u ordinal=%u row=%u exit=%d task_generation=%llu "
        "event=%llu stage_event=%llu source_match_event=%llu consumer_match_event=%llu "
        "task_queue=%u pcm_consumers=%u "
        "addr=0x%08X value=0x%08X target=%u "
        "clear_obj=0x%08X clear_exact=%u clear_span=%u\n",
        family, rows[which], pc, width, rs64_phase_ord(), vi_width, origin,
        arm ? arm : "n/a", active ? 1u : 0u, ordinal, route_row,
        exit_reason, static_cast<unsigned long long>(task_generation),
        static_cast<unsigned long long>(family_event),
        static_cast<unsigned long long>(stage_event),
        static_cast<unsigned long long>(source_match_event),
        static_cast<unsigned long long>(consumer_match_event), task_queue,
        pcm_consumers, addr, value, target ? 1u : 0u,
        clear_object,
        clear_object_exact ? 1u : 0u, clear_object_span ? 1u : 0u);
    std::fflush(stderr);
    ++rows[which];
}

extern "C" void rs64_m5_clear_branch(uint32_t pc, uint32_t branch_taken,
                                       uint32_t v0, uint32_t v1,
                                       uint32_t a0, uint32_t a1, uint32_t a2,
                                       uint32_t s0, uint32_t s1, uint32_t ra) {
    static int enabled = -1;
    static uint32_t bucket = 0xFFFFFFFFu;
    static unsigned rows = 0;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_CLEAR_BRANCH");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && (origin == 0x006AB800u || origin == 0x00790400u)) ||
          (width == 512u && origin == 0x006AB400u))) return;
    const uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) { bucket = next_bucket; rows = 0; }
    if (rows >= 128u) return;
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    std::fprintf(stderr,
        "[m5-clear-branch] n=%u pc=0x%08X taken=%u v0=0x%08X v1=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X s0=0x%08X s1=0x%08X ra=0x%08X "
        "phase=%u width=%u origin=0x%06X arm=%s active=%u route_ordinal=%u "
        "route_row=%u dmem_seq=%llu source_event=%llu exit=%d\n",
        rows, pc, branch_taken, v0, v1, a0, a1, a2, s0, s1, ra,
        rs64_phase_ord(), width, origin, arm ? arm : "n/a", active ? 1u : 0u,
        ordinal, route_row,
        static_cast<unsigned long long>(rs64_m5_clear_branch_dmem_sequence()),
        static_cast<unsigned long long>(rs64_m5_clear_branch_source_sequence()), exit_reason);
    std::fflush(stderr);
    ++rows;
}

extern "C" void rs64_m5_writer_setup_step(uint32_t pc, uint32_t ra,
                                             uint32_t s1, uint32_t t0,
                                             uint32_t t1) {
    static int enabled = -1;
    static uint32_t bucket = 0xFFFFFFFFu;
    static unsigned rows = 0;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_WRITER_SETUP");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    uint32_t width = rs64_vi_committed_width();
    uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x006AB800u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) { bucket = next_bucket; rows = 0; }
    if (rows >= 128u) return;
    std::fprintf(stderr,
        "[m5-writer-setup-step] n=%u pc=0x%08X phase=%u width=%u origin=0x%06X "
        "ra=0x%08X s1=0x%08X t0=0x%08X t1=0x%08X\n",
        rows, pc, rs64_phase_ord(), width, origin, ra, s1, t0, t1);
    std::fflush(stderr);
    ++rows;
}

extern "C" void rs64_m5_allocate_boundary(uint32_t edge, uint32_t ra,
                                             uint32_t a0, uint32_t a1,
                                             uint32_t a2, uint32_t s0,
                                             uint32_t s1, uint32_t v0) {
    static int enabled = -1;
    static uint32_t bucket = 0xFFFFFFFFu;
    static unsigned rows = 0;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_WRITER_SETUP");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    uint32_t width = rs64_vi_committed_width();
    uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width == 0u) return;
    uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) { bucket = next_bucket; rows = 0; }
    if (rows >= 64u) return;
    std::fprintf(stderr,
        "[m5-allocate-boundary] n=%u edge=0x%08X phase=%u width=%u origin=0x%06X "
        "ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X s0=0x%08X s1=0x%08X v0=0x%08X\n",
        rows, edge, rs64_phase_ord(), width, origin, ra, a0, a1, a2, s0, s1, v0);
    std::fflush(stderr);
    ++rows;
}

extern "C" void rs64_m5_static_rs_memset_callsite(uint32_t callsite,
                                                    uint32_t ra,
                                                    uint32_t dst,
                                                    uint32_t value,
                                                    uint32_t len) {
    g_rs64_m5_static_rs_memset_callsite = callsite;
    g_rs64_m5_static_rs_memset_ra = ra;
    static int enabled = -1;
    static uint32_t rows = 0;
    static uint32_t bucket = 0xFFFFFFFFu;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_STATIC_CALLS");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    uint32_t width = rs64_vi_committed_width();
    uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) { bucket = next_bucket; rows = 0; }
    if (rows >= 512u) return;
    uint32_t phase = rs64_phase_ord();
    uint32_t ordinal = 0xFFFFFFFFu, row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    unsigned active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &row, &exit_reason, &arm) ? 1u : 0u;
    std::fprintf(stderr,
        "[m5-static-rsmemset-call] n=%u callsite=0x%08X ra=0x%08X "
        "phase=%u width=%u origin=0x%06X arm=%s ordinal=%u row=%u active=%u "
        "dst=0x%08X val=0x%08X len=0x%X exit=%d\n",
        rows, callsite, ra, phase, width, origin, arm ? arm : "n/a",
        ordinal, row, active, dst, value, len, exit_reason);
    std::fflush(stderr);
    ++rows;
}

extern "C" uint32_t rs64_m5_static_rs_memset_last_callsite() {
    return g_rs64_m5_static_rs_memset_callsite;
}

extern "C" uint32_t rs64_m5_static_rs_memset_last_ra() {
    return g_rs64_m5_static_rs_memset_ra;
}

extern "C" void rs64_m5_preclear_snapshot(uint8_t* rdram, uint32_t dst,
                                             uint32_t fill, uint32_t len,
                                             uint32_t ra, uint32_t guest_pc,
                                             uint32_t edge) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_PRECLEAR");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled || len == 0u) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    const uint32_t phys = dst & 0x007FFFFFu;
    const uint64_t end = static_cast<uint64_t>(phys) + len;
    const uint32_t spans[][2] = {{0x178C80u, 0x178E00u},
                                 {0x1797B0u, 0x179A48u}};
    uint32_t span = 0;
    for (uint32_t i = 0; i < 2u; ++i) {
        if (phys < spans[i][1] && end > spans[i][0]) { span = i + 1u; break; }
    }
    if (span == 0u) return;
    const uint32_t first = spans[span - 1u][0];
    const uint32_t last = spans[span - 1u][1];
    uint32_t fnv = 2166136261u, nonzero = 0;
    for (uint32_t i = first; i < last; ++i) {
        const uint8_t b = rdram[i ^ 3u];
        fnv = (fnv * 16777619u) ^ b;
        nonzero += b != 0;
    }
    static std::mutex mutex;
    static uint64_t ordinal = 0;
    static uint32_t phase_rows[2] = {};
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t slot = width == 1024u ? 0u : 1u;
    const uint32_t row = phase_rows[slot]++;
    if (row >= 512u) return;
    std::fprintf(stderr,
        "[m5-preclear] ordinal=%llu edge=%u row=%u phase=%u width=%u "
        "origin=0x%06X span=%u dst=0x%08X phys=0x%06X fill=0x%02X len=0x%X "
        "pre_fnv=%08X pre_nz=%u ra=0x%08X guest_pc=0x%08X\n",
        static_cast<unsigned long long>(ordinal++), edge, row,
        rs64_phase_ord(), width, origin, span, dst, phys, fill & 0xFFu, len,
        fnv, nonzero, ra, guest_pc);
    std::fflush(stderr);
}

extern "C" void rs64_m5_preclear_nonscalar(uint8_t* rdram, char kind,
                                             uint32_t pc, uint32_t dst,
                                             uint32_t src_or_fill, uint32_t len,
                                             uint32_t ra) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_PRECLEAR_NONSCALAR");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled || !rdram || len == 0u) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t controls = 0;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) { phase_key = key; controls = 0; rows = 0; }
    if (controls++ == 0u) {
        std::fprintf(stderr,
            "[m5-nonscalar-control] phase=%u width=%u origin=0x%06X kind=%c\n",
            rs64_phase_ord(), width, origin, kind);
        std::fflush(stderr);
    }
    const uint32_t dst_phys = (dst - 0x80000000u) & 0x007FFFFFu;
    const uint64_t end = static_cast<uint64_t>(dst_phys) + len;
    const uint32_t first = 0x1797B0u, last = 0x179A48u;
    if (dst_phys >= last || end <= first || rows >= 512u) return;
    uint32_t payload_fnv = 2166136261u, payload_nz = 0u;
    if (kind == 'M') {
        const uint32_t src_phys = (src_or_fill - 0x80000000u) & 0x007FFFFFu;
        for (uint32_t i = 0; i < len && i < 0x4000u; ++i) {
            const uint8_t b = rdram[(src_phys + i) & 0x007FFFFFu];
            payload_fnv = (payload_fnv * 16777619u) ^ b;
            payload_nz += b != 0u;
        }
    } else {
        const uint8_t b = static_cast<uint8_t>(src_or_fill);
        payload_fnv = b ? 0xFFFFFFFFu : 2166136261u;
        payload_nz = b ? len : 0u;
    }
    std::fprintf(stderr,
        "[m5-nonscalar] row=%u phase=%u width=%u origin=0x%06X kind=%c "
        "pc=0x%08X ra=0x%08X dst=0x%08X phys=0x%06X src_or_fill=0x%08X "
        "len=0x%X payload_fnv=%08X payload_nz=%u\n",
        rows++, rs64_phase_ord(), width, origin, kind, pc, ra, dst, dst_phys,
        src_or_fill, len, payload_fnv, payload_nz);
    std::fflush(stderr);
}

extern "C" void rs64_m5_destination_contract(uint8_t*, uint32_t pc,
                                                char width, uint32_t base,
                                                uint32_t index, uint32_t addr,
                                                uint32_t value, uint32_t s0,
                                                uint32_t s1, uint32_t s3,
                                                uint32_t s4, uint32_t s5,
                                                uint32_t s6, uint32_t fp,
                                                uint32_t ra) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_DESTINATION");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width_n = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width_n == 1024u && origin == 0x00790400u) ||
          (width_n == 512u && origin == 0x006AB400u))) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width_n << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) { phase_key = key; rows = 0; }
    if (rows >= 2048u) return;
    if (rows == 0u) {
        std::fprintf(stderr, "[m5-destination-control] phase=%u width=%u origin=0x%06X\n",
                     rs64_phase_ord(), width_n, origin);
    }
    std::fprintf(stderr,
        "[m5-destination] row=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "width=%c base=0x%08X index=0x%08X addr=0x%08X phys=0x%06X "
        "value=0x%08X s0=0x%08X s1=0x%08X s3=0x%08X s4=0x%08X s5=0x%08X "
        "s6=0x%08X fp=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width_n, origin, pc, width, base, index,
        addr, (addr - 0x80000000u) & 0x007FFFFFu, value, s0, s1, s3, s4,
        s5, s6, fp, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_base_index_producer(
    uint8_t*, uint32_t pc, char stage, uint32_t a0, uint32_t a1,
    uint32_t a2, uint32_t a3, uint32_t base, uint32_t index, uint32_t ptr,
    uint32_t s0, uint32_t s1, uint32_t s2, uint32_t s3, uint32_t s4,
    uint32_t fp, uint32_t ra) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_BASE_INDEX");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) { phase_key = key; rows = 0; }
    if (rows >= 512u) return;
    if (rows == 0u) {
        std::fprintf(stderr,
                     "[m5-base-index-control] phase=%u width=%u origin=0x%06X\n",
                     rs64_phase_ord(), width, origin);
    }
    std::fprintf(stderr,
        "[m5-base-index] row=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "stage=%c a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
        "base=0x%08X index=0x%08X ptr=0x%08X s0=0x%08X s1=0x%08X "
        "s2=0x%08X s3=0x%08X s4=0x%08X fp=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, stage, a0, a1, a2, a3,
        base, index, ptr, s0, s1, s2, s3, s4, fp, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_caller_input_producer(
    uint8_t*, uint32_t pc, char stage, uint32_t a0, uint32_t a1,
    uint32_t a2, uint32_t a3, uint32_t field20, uint32_t field24,
    uint32_t v0, uint32_t ra) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_CALLER_INPUT");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) { phase_key = key; rows = 0; }
    if (rows >= 256u) return;
    if (rows == 0u) {
        std::fprintf(stderr,
            "[m5-caller-input-control] phase=%u width=%u origin=0x%06X\n",
            rs64_phase_ord(), width, origin);
    }
    std::fprintf(stderr,
        "[m5-caller-input] row=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X stage=%c a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
        "field20=0x%08X field24=0x%08X v0=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, stage, a0, a1, a2,
        a3, field20, field24, v0, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_hmt_input(
    uint8_t* rdram, uint32_t pc, const char* label, uint32_t a0, uint32_t a1,
    uint32_t a2, uint32_t a3, uint32_t sp, uint32_t w10, uint32_t w14,
    uint32_t w18, uint32_t w1c, uint32_t w20, uint32_t w24, uint32_t w28,
    uint32_t w2c, uint32_t w30, uint32_t ra) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_HMT_INPUT");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled) return;
    static std::mutex mutex;
    static uint32_t rows = 0;
    std::lock_guard<std::mutex> lock(mutex);
    if (rows >= 4096u) return;
    auto guest_ptr = [](uint32_t value) {
        return value >= 0x80000000u && value < 0x80800000u;
    };
    const bool parse = pc == 0x80022A00u;
    const bool a1_ptr_ok = !parse || guest_ptr(a1);
    const bool a2_ptr_ok = !parse || a2 == 0u || guest_ptr(a2);
    const uint32_t bad = parse && (!a1_ptr_ok || !a2_ptr_ok);
    uint32_t entry_28 = 0, entry_2a = 0, entry_2c = 0, entry_2d = 0, entry_2e = 0;
    if (parse && a2_ptr_ok) {
        const uint32_t phys = a2 & 0x007FFFFFu;
        auto rd16 = [rdram, phys](uint32_t offset) {
            return (static_cast<uint32_t>(rdram[(phys + offset) ^ 3u]) << 8) |
                   static_cast<uint32_t>(rdram[(phys + offset + 1u) ^ 3u]);
        };
        entry_28 = rd16(0x28);
        entry_2a = rd16(0x2A);
        entry_2c = rdram[(phys + 0x2Cu) ^ 3u];
        entry_2d = rdram[(phys + 0x2Du) ^ 3u];
        entry_2e = rd16(0x2E);
    }
    if (rows == 0u) {
        std::fprintf(stderr, "[m5-hmt-input-control] enabled=1 roles=pointer-only\n");
    }
    std::fprintf(stderr,
        "[m5-hmt-input] row=%u pc=0x%08X label=%s bad=%u "
        "a0_role=%s a1_role=%s a2_role=%s a3_role=%s "
        "a1_ptr_ok=%u a2_ptr_ok=%u entry28=0x%04X entry2a=0x%04X "
        "entry2c=0x%02X entry2d=0x%02X entry2e=0x%04X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X sp=0x%08X "
        "w10=0x%08X w14=0x%08X w18=0x%08X w1c=0x%08X "
        "w20=0x%08X w24=0x%08X w28=0x%08X w2c=0x%08X w30=0x%08X ra=0x%08X\n",
        rows++, pc, label, bad,
        parse ? "material_index" : "entry_or_table_ptr",
        parse ? "output_record_ptr" : "material_or_index",
        parse ? "nullable_material_entry_ptr" : "scalar_or_mode",
        parse ? "mode_u8" : "mode_u8",
        a1_ptr_ok, a2_ptr_ok, entry_28, entry_2a, entry_2c, entry_2d, entry_2e,
        a0, a1, a2, a3, sp, w10, w14, w18, w1c,
        w20, w24, w28, w2c, w30, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_052c4_join(uint8_t* rdram, uint32_t dst,
                                     uint32_t value, uint32_t len,
                                     uint32_t edge) {
    static int enabled = -1;
    static uint32_t rows = 0;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_M5_052C4_JOIN");
        enabled = e && e[0] && e[0] != '0' ? 1 : 0;
    }
    if (!enabled ||
        (g_rs64_m5_static_rs_memset_callsite != 0x800052C4u &&
         g_rs64_m5_static_rs_memset_callsite != 0x8008F2CCu)) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    const uint64_t end = static_cast<uint64_t>(dst) + len;
    if (dst >= 0x80179A48u || end <= 0x801797B0u) return;
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    uint32_t phys = dst & 0x007FFFFFu;
    uint32_t nz = 0;
    uint32_t fnv = 2166136261u;
    bool valid = len != 0 && len <= 0x4000 && phys < 0x00800000u &&
                 len <= 0x00800000u - phys;
    if (valid) {
        for (uint32_t i = 0; i < len; ++i) {
            const uint8_t b = rdram[(phys + i) ^ 3u];
            fnv ^= b;
            fnv *= 16777619u;
            nz += b != 0;
        }
    }
    if (rows < 64u) {
        std::fprintf(stderr,
            "[m5-052c4-join] n=%u edge=%u phase=%u width=%u origin=0x%06X "
            "arm=%s ordinal=%u row=%u active=%u exit=%d caller=0x%08X "
            "dst=0x%08X phys=0x%06X val=0x%08X len=0x%X valid=%u "
            "post_fnv=%08X post_nz=%u\n",
            rows, edge, rs64_phase_ord(), width, origin, arm ? arm : "n/a",
            ordinal, route_row, active ? 1u : 0u, exit_reason,
            g_rs64_m5_static_rs_memset_callsite, dst, phys, value, len,
            valid ? 1u : 0u, fnv, nz);
        std::fflush(stderr);
    }
    ++rows;
}

namespace {
struct Rs64PcmWriterState {
    uint32_t last_pc = 0;
    uint32_t last_kind = 0;
    uint32_t last_phys = 0;
    uint32_t last_value = 0;
    uint32_t writes = 0;
    uint64_t sequence = 0;
};

constexpr uint32_t rs64_pcm_ring_first = 0x166450u;
constexpr uint32_t rs64_pcm_ring_last = 0x169450u;
constexpr uint32_t rs64_pcm_ring_slot = 0x300u;
constexpr uint32_t rs64_m5_candidate_ranges[][2] = {
    {0x167000u, 0x169B00u},
    {0x179800u, 0x179B00u},
    {0x18FC00u, 0x18FD00u},
};
Rs64PcmWriterState g_rs64_pcm_writer[16];
std::mutex g_rs64_pcm_writer_mutex;
uint32_t g_rs64_pcm_writer_phase_key = 0xFFFFFFFFu;
uint64_t g_rs64_pcm_writer_sequence = 0;
uint32_t g_rs64_pcm_writer_printed[16] = {};
bool g_rs64_pcm_writer_control = false;
uint32_t g_rs64_pcm_last_dma_phys = 0;
uint32_t g_rs64_pcm_last_dma_len = 0;
uint32_t g_rs64_pcm_guest_rows = 0;
uint32_t g_rs64_m5_second_range_rows = 0;
std::atomic<uint32_t> g_rs64_pcm_task_data_ptr{0};
uint64_t g_rs64_m5_source_event = 0;
uint32_t g_rs64_m5_source_window_rows = 0;
static thread_local uint64_t g_rs64_m5_last_source_event = 0;
static thread_local uint64_t g_rs64_m5_last_input_event = 0;
static thread_local uint32_t g_rs64_m5_last_input_fnv = 0;
static thread_local uint32_t g_rs64_m5_last_input_nonzero = 0;
static thread_local uint32_t g_rs64_m5_last_input_dram = 0;
static thread_local uint32_t g_rs64_m5_last_input_len = 0;
static thread_local uint32_t g_rs64_m5_last_input_dmem = 0;
static thread_local uint32_t g_rs64_m5_last_input_task_data_ptr = 0;
static thread_local uint64_t g_rs64_m5_last_source_dma_seq = 0;
static thread_local uint32_t g_rs64_m5_last_source_dma_dram = 0;
static thread_local uint32_t g_rs64_m5_last_source_dma_len = 0;
static thread_local uint32_t g_rs64_m5_last_source_dma_dmem = 0;
static thread_local uint32_t g_rs64_m5_last_source_dma_fnv = 0;
static thread_local uint32_t g_rs64_m5_last_source_dma_nonzero = 0;
static thread_local uint64_t g_rs64_m5_last_source_dma3_seq = 0;
static thread_local uint32_t g_rs64_m5_last_source_dma3_dram = 0;
static thread_local uint32_t g_rs64_m5_last_source_dma3_len = 0;
static thread_local uint32_t g_rs64_m5_last_source_dma3_dmem = 0;
static thread_local uint32_t g_rs64_m5_last_source_dma3_fnv = 0;
static thread_local uint32_t g_rs64_m5_last_source_dma3_nonzero = 0;
static std::atomic<uint64_t> g_rs64_m5_pre_dma_writer_seq{0};
static std::atomic<uint32_t> g_rs64_m5_pre_dma_writer_pc{0};
static std::atomic<uint32_t> g_rs64_m5_pre_dma_writer_phys{0};
static std::atomic<uint32_t> g_rs64_m5_pre_dma_writer_len{0};
static std::atomic<uint32_t> g_rs64_m5_pre_dma_writer_value{0};
static std::atomic<uint64_t> g_rs64_m5_dmem_writer_seq{0};
static thread_local uint64_t g_rs64_m5_last_dmem_writer_seq = 0;
static thread_local uint32_t g_rs64_m5_last_dmem_writer_addr = 0;
static thread_local uint32_t g_rs64_m5_last_dmem_writer_len = 0;
static thread_local uint32_t g_rs64_m5_last_dmem_writer_value = 0;
static thread_local uint32_t g_rs64_m5_last_dmem_writer_fnv = 0;
static thread_local uint32_t g_rs64_m5_last_dmem_writer_nonzero = 0;
static thread_local uint32_t g_rs64_m5_last_dmem_writer_kind = 0;
static thread_local uint32_t g_rs64_m5_last_dmem_writer_vector_op = 0;
static thread_local uint32_t g_rs64_m5_last_dmem_writer_route_ordinal = 0xFFFFFFFFu;
static thread_local uint64_t g_rs64_m5_last_input_dmem_writer_seq = 0;

extern "C" uint64_t rs64_m5_clear_branch_dmem_sequence() {
    return g_rs64_m5_last_dmem_writer_seq;
}

extern "C" uint64_t rs64_m5_clear_branch_source_sequence() {
    return g_rs64_m5_source_event;
}

struct Rs64M5DmemCoverage {
    uint64_t sequence = 0;
    uint32_t addr = 0;
    uint32_t len = 0;
    uint32_t kind = 0;
    uint32_t value = 0;
    uint32_t fnv = 0;
    uint32_t nonzero = 0;
    uint32_t vector_op = 0;
    uint32_t route_ordinal = 0xFFFFFFFFu;
};
static Rs64M5DmemCoverage g_rs64_m5_dmem_coverage[0x1000];
static std::mutex g_rs64_m5_dmem_coverage_mutex;

extern "C" void rs64_m5_pre_dma_writer_store(char width, uint32_t pc,
                                                uint32_t addr, uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_INPUT_WRITER");
        const char* producer = std::getenv("ROGUESQ_LOG_M5_SOURCE_PRODUCER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0') ||
               (producer && producer[0] && producer[0] != '0');
    }();
    static const bool producer_enabled = [] {
        const char* e = std::getenv("ROGUESQ_LOG_M5_SOURCE_PRODUCER");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (e && e[0] && e[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    static std::atomic<bool> control{false};
    if (!control.exchange(true, std::memory_order_relaxed)) {
        std::fprintf(stderr, "[m5-input-writer-control] any_store=1 pc=0x%08X\n", pc);
        std::fflush(stderr);
    }
    if (!enabled) return;
    if ((addr & 0xFFF00000u) != 0x80100000u) return;

    const uint32_t adjust = width == 'B' ? 3u : (width == 'H' ? 2u : 0u);
    const uint32_t len = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
    const uint32_t phys = ((addr ^ adjust) - 0x80000000u) & 0x007FFFFFu;
    if (phys >= 0x178F18u || phys + len <= 0x178C80u) return;

    uint32_t phase = 0, width_n = 0, origin = 0;
    uint32_t ordinal = 0xFFFFFFFFu, row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool route_active = rs64_audio_current_route_snapshot(
        &phase, &width_n, &origin, &ordinal, &row, &exit_reason, &arm);
    const bool target_phase = (width_n == 1024u && origin == 0x00790400u) ||
                              (width_n == 512u && origin == 0x006AB400u);
    if (!producer_enabled && (!route_active || !target_phase)) return;

    const uint64_t seq = g_rs64_m5_pre_dma_writer_seq.fetch_add(
        1u, std::memory_order_relaxed) + 1u;
    g_rs64_m5_pre_dma_writer_pc.store(pc, std::memory_order_relaxed);
    g_rs64_m5_pre_dma_writer_phys.store(phys, std::memory_order_relaxed);
    g_rs64_m5_pre_dma_writer_len.store(len, std::memory_order_relaxed);
    g_rs64_m5_pre_dma_writer_value.store(value, std::memory_order_relaxed);
    static std::mutex producer_log_mutex;
    static uint32_t producer_phase_key = 0xFFFFFFFFu;
    static uint32_t producer_phase_rows = 0;
    std::lock_guard<std::mutex> producer_log_lock(producer_log_mutex);
    const uint32_t phase_key = (width_n << 24) ^ origin;
    if (phase_key != producer_phase_key) {
        producer_phase_key = phase_key;
        producer_phase_rows = 0;
        std::fprintf(stderr,
            "[m5-source-producer-phase-control] width=%u origin=0x%06X\n",
            width_n, origin);
        std::fflush(stderr);
    }
    if (producer_enabled && producer_phase_rows++ < 4096u) {
        std::fprintf(stderr,
            "[m5-source-producer] seq=%llu route_active=%u phase=%u width=%u "
            "origin=0x%06X arm=%s route_ordinal=%u route_row=%u pc=0x%08X "
            "phys=0x%06X len=%u value=0x%08X exit=%d\n",
            static_cast<unsigned long long>(seq), route_active ? 1u : 0u,
            phase, width_n, origin, arm ? arm : "n/a", ordinal, row, pc,
            phys, len, value, exit_reason);
        std::fflush(stderr);
    } else if (seq <= 4096u) {
        std::fprintf(stderr,
            "[m5-input-writer] seq=%llu phase=%u width=%u origin=0x%06X arm=%s "
            "route_ordinal=%u route_row=%u pc=0x%08X phys=0x%06X len=%u value=0x%08X\n",
            static_cast<unsigned long long>(seq), phase, width_n, origin,
            arm ? arm : "n/a", ordinal, row, pc, phys, len, value);
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_audio_input_dma(uint8_t* rdram, uint32_t dram_addr,
                                           uint32_t len, uint32_t dmem_addr) {
    (void)rdram;
    uint32_t phase = 0, width = 0, origin = 0;
    uint32_t route_ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &phase, &width, &origin, &route_ordinal, &route_row, &exit_reason,
        &arm);
    const uint32_t source_first = 0x178C80u, source_last = 0x178F18u;
    if (!active || !((width == 1024u && origin == 0x00790400u) ||
                     (width == 512u && origin == 0x006AB400u)) ||
        dram_addr >= source_last || dram_addr + len <= source_first) return;
    const uint32_t overlap_first = dram_addr > source_first ?
        dram_addr : source_first;
    const uint32_t overlap_last = dram_addr + len < source_last ?
        dram_addr + len : source_last;
    uint32_t input_fnv = 2166136261u, input_nonzero = 0u;
    for (uint32_t addr = overlap_first; addr < overlap_last; ++addr) {
        const uint8_t byte = rdram[(addr & 0x007FFFFFu) ^ 3u];
        input_fnv = (input_fnv * 16777619u) ^ byte;
        input_nonzero += byte != 0u;
    }
    const uint64_t event = g_rs64_m5_source_event++;
    g_rs64_m5_last_input_event = event;
    g_rs64_m5_last_input_fnv = input_fnv;
    g_rs64_m5_last_input_nonzero = input_nonzero;
    g_rs64_m5_last_input_dram = dram_addr;
    g_rs64_m5_last_input_len = len;
    g_rs64_m5_last_input_dmem = dmem_addr;
    g_rs64_m5_last_input_task_data_ptr = s_pending_audio_task == nullptr ?
        0u : static_cast<uint32_t>(s_pending_audio_task->t.data_ptr);
    std::fprintf(stderr,
        "[m5-input-dma] event=%llu phase=%u width=%u origin=0x%06X arm=%s "
        "route_ordinal=%u route_row=%u dram=0x%06X len=0x%X dmem=0x%03X "
        "overlap=0x%06X..0x%06X input_fnv=%08X input_nz=%u "
        "input_task_data_ptr=0x%08X "
        "prev_writer_seq=%llu prev_writer_pc=0x%08X prev_writer_phys=0x%06X "
        "prev_writer_len=%u prev_writer_value=0x%08X "
        "task_generation=%llu latest_generation=%llu latest_route_seq=%u "
        "latest_route_ordinal=%u latest_route_row=%u exit=%d\n",
        static_cast<unsigned long long>(event), phase, width, origin,
        arm ? arm : "n/a", route_ordinal, route_row, dram_addr, len,
        dmem_addr, overlap_first, overlap_last, input_fnv, input_nonzero,
        g_rs64_m5_last_input_task_data_ptr,
        static_cast<unsigned long long>(g_rs64_m5_pre_dma_writer_seq.load(
            std::memory_order_relaxed)),
        g_rs64_m5_pre_dma_writer_pc.load(std::memory_order_relaxed),
        g_rs64_m5_pre_dma_writer_phys.load(std::memory_order_relaxed),
        g_rs64_m5_pre_dma_writer_len.load(std::memory_order_relaxed),
        g_rs64_m5_pre_dma_writer_value.load(std::memory_order_relaxed),
        static_cast<unsigned long long>(s_pending_audio_generation),
        static_cast<unsigned long long>(g_m5_latest_audio_generation.load(
            std::memory_order_acquire)),
        g_m5_latest_audio_route_seq.load(std::memory_order_acquire),
        g_m5_latest_audio_route_ordinal.load(std::memory_order_acquire),
        g_m5_latest_audio_route_row.load(std::memory_order_acquire), exit_reason);
    std::fflush(stderr);
}

extern "C" void rs64_m5_audio_dma_identity(
    uint64_t* source_event, uint64_t* task_generation,
    uint32_t* latest_route_seq, uint32_t* latest_route_ordinal,
    uint32_t* latest_route_row) {
    if (source_event) *source_event = g_rs64_m5_last_source_event;
    if (task_generation) *task_generation = s_pending_audio_generation;
    if (latest_route_seq) {
        *latest_route_seq = g_m5_latest_audio_route_seq.load(
            std::memory_order_acquire);
    }
    if (latest_route_ordinal) {
        *latest_route_ordinal = g_m5_latest_audio_route_ordinal.load(
            std::memory_order_acquire);
    }
    if (latest_route_row) {
        *latest_route_row = g_m5_latest_audio_route_row.load(
            std::memory_order_acquire);
    }
}

bool rs64_pcm_writer_enabled() {
    static int enabled = -1;
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_PCM_WRITER");
        enabled = ((all && all[0] && all[0] != '0') ||
                   (own && own[0] && own[0] != '0')) ? 1 : 0;
    }
    return enabled != 0;
}

bool rs64_pcm_writer_phase(uint32_t& phase, uint32_t& width,
                           uint32_t& origin, uint32_t& key) {
    phase = rs64_phase_ord();
    width = rs64_vi_committed_width();
    origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return false;
    key = (width << 24) ^ origin;
    return true;
}

static uint64_t rs64_m5_callback_host_thread() {
    return static_cast<uint64_t>(
        std::hash<std::thread::id>{}(std::this_thread::get_id()));
}

void rs64_pcm_writer_phase_reset(uint32_t key) {
    if (key == g_rs64_pcm_writer_phase_key) return;
    g_rs64_pcm_writer_phase_key = key;
    std::memset(g_rs64_pcm_writer, 0, sizeof(g_rs64_pcm_writer));
    std::memset(g_rs64_pcm_writer_printed, 0,
                sizeof(g_rs64_pcm_writer_printed));
    g_rs64_pcm_writer_control = false;
    g_rs64_pcm_guest_rows = 0;
    g_rs64_m5_second_range_rows = 0;
}

void rs64_pcm_writer_note(uint32_t phys, uint32_t len, uint32_t pc,
                          uint32_t kind, uint32_t value) {
    if (!rs64_pcm_writer_enabled() || len == 0) return;
    uint32_t phase = 0, width = 0, origin = 0, key = 0;
    if (!rs64_pcm_writer_phase(phase, width, origin, key)) return;
    const uint32_t end = phys + len;
    bool candidate = false;
    for (const auto& range : rs64_m5_candidate_ranges) {
        if (phys < range[1] && end > range[0]) {
            candidate = true;
            break;
        }
    }
    const bool ring = phys < rs64_pcm_ring_last && end > rs64_pcm_ring_first;
    if (!candidate && !ring) return;

    std::lock_guard<std::mutex> lock(g_rs64_pcm_writer_mutex);
    rs64_pcm_writer_phase_reset(key);
    if (candidate && !g_rs64_pcm_writer_control) {
        std::fprintf(stderr,
                     "[pcm-writer-control] phase=%u width=%u origin=0x%06X"
                     " kind=%u phys=0x%06X len=0x%X\n",
                     phase, width, origin, kind, phys, len);
        std::fflush(stderr);
        g_rs64_pcm_writer_control = true;
    }

    if (candidate && kind == 1u && g_rs64_pcm_guest_rows < 256u) {
        uint32_t route_phase = phase, route_width = width, route_origin = origin;
        uint32_t ordinal = 0xFFFFFFFFu, row = 0xFFFFFFFFu;
        int exit_reason = 0;
        const char* arm = "n/a";
        const bool active = rs64_audio_current_route_snapshot(
            &route_phase, &route_width, &route_origin, &ordinal, &row,
            &exit_reason, &arm);
        std::fprintf(stderr,
                     "[m5-guest-writer] n=%u phase=%u width=%u origin=0x%06X"
                     " pc=0x%08X phys=0x%06X len=0x%X value=0x%08X"
                     " arm=%s ordinal=%u row=%u task_data=0x%08X"
                     " dma_dest=0x%06X dma_len=0x%X sp_return=0x%04X"
                     " active=%u exit=%d\n",
                     g_rs64_pcm_guest_rows, active ? route_phase : phase,
                     active ? route_width : width,
                     active ? route_origin : origin, pc, phys, len, value,
                     active && arm ? arm : "n/a", ordinal, row,
                     g_rs64_pcm_task_data_ptr.load(std::memory_order_relaxed),
                     g_rs64_pcm_last_dma_phys,
                     g_rs64_pcm_last_dma_len, rs64_audio_image_break_pc(),
                     active ? 1u : 0u, exit_reason);
        std::fflush(stderr);
        ++g_rs64_pcm_guest_rows;
    }
    const bool second_range = phys < 0x179A48u && end > 0x1798B0u;
    if (second_range && kind == 1u && g_rs64_m5_second_range_rows < 256u) {
        uint32_t route_phase = phase, route_width = width, route_origin = origin;
        uint32_t ordinal = 0xFFFFFFFFu, row = 0xFFFFFFFFu;
        int exit_reason = 0;
        const char* arm = "n/a";
        const bool active = rs64_audio_current_route_snapshot(
            &route_phase, &route_width, &route_origin, &ordinal, &row,
            &exit_reason, &arm);
        std::fprintf(stderr,
            "[m5-second-range] n=%u phase=%u width=%u origin=0x%06X"
            " pc=0x%08X phys=0x%06X len=0x%X value=0x%08X"
            " arm=%s ordinal=%u row=%u task_data=0x%08X"
            " dma_dest=0x%06X dma_len=0x%X active=%u exit=%d\n",
            g_rs64_m5_second_range_rows,
            active ? route_phase : phase, active ? route_width : width,
            active ? route_origin : origin, pc, phys, len, value,
            active && arm ? arm : "n/a", ordinal, row,
            g_rs64_pcm_task_data_ptr.load(std::memory_order_relaxed),
            g_rs64_pcm_last_dma_phys, g_rs64_pcm_last_dma_len,
            active ? 1u : 0u, exit_reason);
        std::fflush(stderr);
        ++g_rs64_m5_second_range_rows;
    }
    if (!ring) return;

    const uint32_t first = phys < rs64_pcm_ring_first ? rs64_pcm_ring_first : phys;
    const uint32_t last = end > rs64_pcm_ring_last ? rs64_pcm_ring_last : end;
    const uint32_t first_slot = (first - rs64_pcm_ring_first) / rs64_pcm_ring_slot;
    const uint32_t last_slot = (last - 1u - rs64_pcm_ring_first) /
                               rs64_pcm_ring_slot;
    for (uint32_t slot = first_slot; slot <= last_slot && slot < 16u; ++slot) {
        Rs64PcmWriterState& state = g_rs64_pcm_writer[slot];
        state.last_pc = pc;
        state.last_kind = kind;
        state.last_phys = phys;
        state.last_value = value;
        state.writes++;
        state.sequence = ++g_rs64_pcm_writer_sequence;
        if (g_rs64_pcm_writer_printed[slot] < 32u) {
            std::fprintf(stderr,
                         "[pcm-writer] phase=%u width=%u origin=0x%06X"
                         " slot=%u phys=0x%06X len=0x%X kind=%u pc=0x%08X"
                         " value=0x%08X sequence=%llu writes=%u\n",
                         phase, width, origin, slot,
                         rs64_pcm_ring_first + slot * rs64_pcm_ring_slot,
                         len, kind, pc, value,
                         static_cast<unsigned long long>(state.sequence),
                         state.writes);
            std::fflush(stderr);
            g_rs64_pcm_writer_printed[slot]++;
        }
    }
}

extern "C" void rs64_floor_writer_context(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern "C" void rs64_m5_source_context(uint8_t*, uint32_t pc, uint32_t ra,
                            uint32_t a0, uint32_t a1, uint32_t a2,
                            uint32_t a3, uint32_t source_ptr,
                            uint32_t destination, uint32_t value) {
    rs64_floor_writer_context(pc, ra, a0, a1, a2, g_rs64_m5_field348_static_callsite);
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_SOURCE_CONTEXT");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        if (target) {
            std::fprintf(stderr,
                         "[m5-source-context-control] phase=%u width=%u origin=0x%06X\n",
                         rs64_phase_ord(), width, origin);
            std::fflush(stderr);
        }
    }
    if (!target || rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-source-context] row=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
        "callsite=0x%08X source=0x%08X destination=0x%08X value=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, ra, a0, a1, a2, a3,
        g_rs64_m5_field348_static_callsite, source_ptr, destination, value);
    std::fflush(stderr);
}

struct Rs64M5ObjectEntrySnapshot {
    bool valid = false;
    uint32_t ra = 0;
    uint32_t a0 = 0;
    uint32_t a1 = 0;
    uint32_t a2 = 0;
    uint32_t a3 = 0;
    uint32_t s0 = 0;
    uint32_t s1 = 0;
    uint32_t source_word = 0xFFFFFFFFu;
    uint32_t source_half = 0xFFFFFFFFu;
    uint32_t s1_half = 0xFFFFFFFFu;
};
static std::mutex g_rs64_m5_object_entry_mutex;
static Rs64M5ObjectEntrySnapshot g_rs64_m5_object_entry;

extern "C" void rs64_m5_object_field_witness(uint8_t* rdram, uint32_t pc,
                                                recomp_context* ctx,
                                                uint32_t store_addr,
                                                uint32_t store_value) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_OBJECT_FIELD");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled || !rdram || !ctx) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        std::fprintf(stderr,
                     "[m5-object-field-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
                     rs64_phase_ord(), width, origin, pc);
        std::fflush(stderr);
        std::lock_guard<std::mutex> entry_lock(g_rs64_m5_object_entry_mutex);
        if (g_rs64_m5_object_entry.valid) {
            const auto& e = g_rs64_m5_object_entry;
            std::fprintf(stderr,
                "[m5-object-entry-join] phase=%u width=%u origin=0x%06X "
                "pc=0x8008F900 ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
                "s0=0x%08X s1=0x%08X source_word=0x%08X source_half=0x%04X "
                "s1_half=0x%04X\n",
                rs64_phase_ord(), width, origin, e.ra, e.a0, e.a1, e.a2,
                e.a3, e.s0, e.s1, e.source_word, e.source_half, e.s1_half);
            std::fflush(stderr);
        }
    }
    if (rows >= 512u) return;
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        return static_cast<uint32_t>(MEM_W(0x00, (int32_t)guest));
    };
    auto byte = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= 0x80800000u) return 0xFFFFFFFFu;
        return static_cast<uint32_t>(MEM_BU(0x00, (int32_t)guest));
    };
    const uint32_t s0 = U32(ctx->r16);
    const uint32_t s1 = U32(ctx->r17);
    std::fprintf(stderr,
        "[m5-object-field] row=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X ra=0x%08X store_addr=0x%08X store_value=0x%08X "
        "s0=0x%08X s1=0x%08X source_word=0x%08X source_byte=0x%02X "
        "branch_selector=0x%08X branch_state=0x%04X\n",
        rows++, rs64_phase_ord(), width, origin, pc, U32(ctx->r31),
        store_addr, store_value, s0, s1, word(s0 + 0x60u),
        byte(s0 + 0x22u), U32(ctx->r2), word(s1 + 0x22u) & 0xFFFFu);
    std::fflush(stderr);
}

extern "C" void rs64_m5_object_entry_witness(uint8_t* rdram,
                                                recomp_context* ctx) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_OBJECT_ENTRY");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled || !rdram || !ctx) return;
    auto raw_word = [rdram](uint32_t address) -> uint32_t {
        const uint32_t p = address & 0x007FFFFCu;
        return rs64_rdram_u32(rdram, p);
    };
    auto raw_half = [rdram](uint32_t address) -> uint32_t {
        const uint32_t p = address & 0x007FFFFCu;
        const uint32_t word = rs64_rdram_u32(rdram, p);
        return (word >> ((address & 2u) ? 0u : 16u)) & 0xFFFFu;
    };
    const uint32_t s0 = U32(ctx->r16);
    const uint32_t s1 = U32(ctx->r17);
    std::lock_guard<std::mutex> lock(g_rs64_m5_object_entry_mutex);
    g_rs64_m5_object_entry = {true, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5),
                              U32(ctx->r6), U32(ctx->r7), s0, s1,
                              raw_word(s0 + 0x60u), raw_half(s0 + 0x22u),
                              raw_half(s1 + 0x22u)};
}

extern "C" void rs64_m5_object_body_witness(uint8_t* rdram,
                                               recomp_context* ctx) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_OBJECT_BODY");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled || !rdram || !ctx) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        std::fprintf(stderr,
                     "[m5-object-body-control] phase=%u width=%u origin=0x%06X\n",
                     rs64_phase_ord(), width, origin);
        std::fflush(stderr);
    }
    if (rows >= 512u) return;
    const uint32_t a3 = U32(ctx->r7);
    const uint32_t t0 = U32(ctx->r8);
    const uint32_t a1 = U32(ctx->r5);
    const uint32_t v1 = t0 + 0x18u;
    const uint32_t v0 = t0 + a1;
    std::fprintf(stderr,
        "[m5-object-body] row=%u phase=%u width=%u origin=0x%06X "
        "pc=0x8008F900 ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
        "s0=0x%08X s1=0x%08X t0=0x%08X next_a3=0x%08X "
        "store1_addr=0x%08X store1_value=0x%08X store2_addr=0x%08X store2_value=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, U32(ctx->r31), U32(ctx->r4),
        a1, U32(ctx->r6), a3, U32(ctx->r16), U32(ctx->r17), t0,
        a3 + 0x600u, v1 - 0x18u, v1, v1 + 0x4u, v0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_object_loop_witness(uint8_t* rdram,
                                               recomp_context* ctx,
                                               uint32_t pc) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_OBJECT_LOOP");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled || !rdram || !ctx) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        std::fprintf(stderr,
                     "[m5-object-loop-control] phase=%u width=%u origin=0x%06X\n",
                     rs64_phase_ord(), width, origin);
    }
    if (rows >= 512u) return;
    const uint32_t a2 = U32(ctx->r6);
    const uint32_t s0 = U32(ctx->r16);
    std::fprintf(stderr,
        "[m5-object-loop] row=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "a2=0x%08X s0=0x%08X compare=%u ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, a2, s0,
        static_cast<unsigned>(static_cast<int32_t>(a2) < static_cast<int32_t>(s0)),
        U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_object_branch_witness(uint8_t* rdram,
                                                 recomp_context* ctx,
                                                 uint32_t pc) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_OBJECT_BRANCH");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled || !rdram || !ctx) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        std::fprintf(stderr,
                     "[m5-object-branch-control] phase=%u width=%u origin=0x%06X\n",
                     rs64_phase_ord(), width, origin);
        std::fflush(stderr);
    }
    if (rows >= 512u) return;
    const uint32_t v0 = U32(ctx->r2);
    const uint32_t a2 = U32(ctx->r6);
    const uint32_t s0 = U32(ctx->r16);
    std::fprintf(stderr,
        "[m5-object-branch] row=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X v0=0x%08X a2=0x%08X s0=0x%08X taken=%u v1=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, v0, a2, s0,
        v0 != 0u, U32(ctx->r3), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_object_successor_witness(uint8_t* rdram,
                                                     recomp_context* ctx,
                                                     uint32_t pc) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_OBJECT_SUCCESSOR");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled || !rdram || !ctx) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        std::fprintf(stderr,
                     "[m5-object-successor-control] phase=%u width=%u origin=0x%06X\n",
                     rs64_phase_ord(), width, origin);
        std::fflush(stderr);
    }
    if (rows >= 512u) return;
    const uint32_t a2 = U32(ctx->r6);
    const uint32_t s0 = U32(ctx->r16);
    const uint32_t v0 = U32(ctx->r2);
    const uint32_t v1 = U32(ctx->r3);
    const uint32_t load_addr = 0x801499C8u;
    const uint32_t load_phys = load_addr - 0x80000000u;
    const uint32_t load_value =
        rs64_rdram_u32(rdram, load_phys);
    std::fprintf(stderr,
        "[m5-object-successor] row=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X v0=0x%08X v1=0x%08X a2=0x%08X s0=0x%08X "
        "load_addr=0x%08X load_value=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, v0, v1, a2, s0,
        load_addr, load_value, U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_object_load_witness(uint8_t* rdram,
                                                recomp_context* ctx,
                                                uint32_t pc) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_OBJECT_LOAD");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled || !rdram || !ctx) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        std::fprintf(stderr,
                     "[m5-object-load-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
                     rs64_phase_ord(), width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 512u) return;
    const uint32_t load_addr = 0x801499C8u;
    const uint32_t load_phys = load_addr - 0x80000000u;
    const uint32_t load_value =
        rs64_rdram_u32(rdram, load_phys);
    const uint32_t v0 = U32(ctx->r2);
    const uint32_t v1 = U32(ctx->r3);
    std::fprintf(stderr,
        "[m5-object-load] row=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "v0=0x%08X v1=0x%08X a2=0x%08X load_addr=0x%08X "
        "load_value=0x%08X derived_addr=0x%08X store_value=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, v0, v1, U32(ctx->r6),
        load_addr, load_value, v0 - 0x18u, 0u, U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_object_return_witness(uint8_t* rdram,
                                                  recomp_context* ctx,
                                                  uint32_t pc) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_OBJECT_RETURN");
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        return (own && own[0] && own[0] != '0') ||
               (all && all[0] && all[0] != '0');
    }();
    if (!enabled || !rdram || !ctx) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        std::fprintf(stderr,
                     "[m5-object-return-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
                     rs64_phase_ord(), width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-object-return] row=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "a0=0x%08X a2=0x%08X v0=0x%08X v1=0x%08X s0=0x%08X s1=0x%08X "
        "s2=0x%08X ra=0x%08X sp=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, U32(ctx->r4), U32(ctx->r6),
        U32(ctx->r2), U32(ctx->r3), U32(ctx->r16), U32(ctx->r17),
        U32(ctx->r18), U32(ctx->r31), U32(ctx->r29));
    std::fflush(stderr);
}
}

extern "C" void rs64_m5_pcm_set_callsite(uint32_t callsite) {
    g_rs64_m5_pcm_callsite = callsite;
}

extern "C" uint32_t rs64_m5_pcm_get_callsite() {
    return g_rs64_m5_pcm_callsite;
}

extern "C" void rs64_m5_pcm_writer_store(char width, uint32_t pc,
                                             uint32_t addr, uint32_t value) {
    const uint32_t adjust = width == 'B' ? 3u : (width == 'H' ? 2u : 0u);
    const uint32_t span = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
    rs64_pcm_writer_note((addr ^ adjust) - 0x80000000u, span, pc, 1u, value);
}

extern "C" void rs64_m5_pcm_writer_dma(uint32_t addr, uint32_t len,
                                           uint32_t fnv, uint32_t nonzero) {
    (void)fnv;
    (void)nonzero;
    g_rs64_pcm_last_dma_phys = addr & 0x007FFFFFu;
    g_rs64_pcm_last_dma_len = len;
    rs64_pcm_writer_note(g_rs64_pcm_last_dma_phys, len, 0u, 2u, 0u);
}

extern "C" void rs64_m5_exact_route_dma_write(uint8_t* rdram,
                                                 uint32_t dram_addr,
                                                 uint32_t len,
                                                 uint32_t dmem_addr) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_EXACT_ROUTE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    static std::atomic<bool> control{false};
    if (!control.exchange(true, std::memory_order_relaxed)) {
        std::fprintf(stderr, "[m5-exact-route-dma-control] DMA witness is live\n");
        std::fflush(stderr);
    }
    if (!enabled || len == 0u) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target) return;
    const uint32_t end = dram_addr + len;
    const uint32_t fields[][2] = {{0x128C92u, 1u}, {0x128CD0u, 4u}};
    static uint32_t rows = 0;
    for (const auto& field : fields) {
        if (dram_addr >= field[0] + field[1] || end <= field[0]) continue;
        if (rows++ >= 512u) return;
        uint32_t post = 0u;
        for (uint32_t i = 0; i < field[1]; ++i) {
            post = (post << 8) | rdram[((field[0] + i) ^ 3u) & 0x007FFFFFu];  // s7601 BS: was no ^3 (wrong byte / reversed word)
        }
        std::fprintf(stderr,
            "[m5-exact-route-dma] n=%u phase=%u width=%u origin=0x%06X "
            "dram=0x%06X len=0x%X dmem=0x%03X field=0x%06X field_len=%u post=0x%08X\n",
            rows - 1u, rs64_phase_ord(), width, origin, dram_addr, len,
            dmem_addr, field[0], field[1], post);
        std::fflush(stderr);
    }
}

// s4578: host-thread poll of the MusyX voice-count halfword (phys 0x149700) plus a ring of host writes.
extern "C" void rs64_s4577_dump();
namespace {
struct S4578Hw { uint32_t seq, phys, len, vi_w; char api[24]; };
S4578Hw g_s4578_ring[16]; uint32_t g_s4578_n = 0; std::mutex g_s4578_mu;
std::atomic<uint32_t> g_s4578_total{0}, g_s4578_page{0};
std::atomic<bool> g_s4578_started{false};
bool s4578_on() {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4578"); return e && e[0] && e[0] != '0'; }();
    return on;
}
void s4578_poll(uint8_t* rdram) {
    auto hw = [&] { return (uint32_t)*(volatile uint16_t*)(rdram + (0x149700u ^ 2u)); };
    uint32_t last = hw(); uint32_t changes = 0;
    std::fprintf(stderr, "[s4578-start] initial=%u\n", last);
    for (;;) {
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        const uint32_t cur = hw();
        if (cur == last) continue;
        std::fprintf(stderr, "[s4578-change] n=%u old=%u new=%u vi_w=%u host_total=%u host_page=%u words:", changes++, last, cur,
                     rs64_vi_committed_width(), g_s4578_total.load(), g_s4578_page.load());
        for (uint32_t p = 0x1496F8u; p < 0x149720u; p += 4) std::fprintf(stderr, " %08X", *(volatile uint32_t*)(rdram + p));
        std::fprintf(stderr, "\n");
        {
            std::lock_guard<std::mutex> g(g_s4578_mu);
            const uint32_t n = g_s4578_n < 16 ? g_s4578_n : 16;
            for (uint32_t i = g_s4578_n - n; i < g_s4578_n; i++) {
                const auto& e = g_s4578_ring[i % 16];
                std::fprintf(stderr, "[s4578-hostring] seq=%u phys=%06X len=%X api=%s vi_w=%u\n", e.seq, e.phys, e.len, e.api, e.vi_w);
            }
        }
        if (cur > 18) rs64_s4577_dump();
        std::fflush(stderr);
        last = cur;
    }
}
}  // namespace
extern "C" void rs64_s4578_start(uint8_t* rdram) {
    if (!s4578_on() || !rdram) return;
    bool exp = false;
    if (!g_s4578_started.compare_exchange_strong(exp, true)) return;
    std::thread(s4578_poll, rdram).detach();
}

// s5653: voice-read source range (set by rsp.cpp on speech-hit audio tasks); census tracks host writers into it.
extern "C" {
volatile uint32_t rs64_vsrc_lo = 0, rs64_vsrc_hi = 0;
uint32_t rs64_vsrc_nw = 0, rs64_vsrc_lastphys = 0, rs64_vsrc_lastlen = 0; char rs64_vsrc_lastapi[24] = {0};
}
// s5654: per-PC census of instrumented game stores into the voice-read source range.
// narrow [1B2C60,1B3600) = where s5653 saw rail data with zero host writers; wide = positive control.
extern "C" void rs64_s5654_vstore(uint32_t pc, uint32_t addr, uint32_t value, char width) {
    static std::mutex mu; static std::map<uint32_t, uint64_t> by_pc; static uint64_t nw = 0, nn = 0;
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_VSRC_STORES"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    // s5655: hook runs BEFORE the store (value arg is a literal 0), so resolve the previous store of this
    // thread now by reading its datum back from RDRAM.  Rail = a halfword of 0x8000/0x7FF8 in the word.
    struct Pend { uint32_t pc, addr; char w; bool v; };
    static thread_local Pend pend = {0, 0, 0, false};
    static std::map<uint32_t, uint64_t> rail_by_pc; static uint64_t chk = 0, nzv = 0, rails = 0;
    volatile uint8_t* rd_ = g_recomp_rdram_for_wp_raw;
    if (pend.v && rd_) {
        std::lock_guard<std::mutex> lk2(mu);
        const uint32_t wv = rs64_rdram_u32(rd_, pend.addr); ++chk; if (wv) ++nzv;
        const uint32_t h0 = wv >> 16, h1 = wv & 0xFFFFu;
        const bool rail = (h0 == 0x8000u || h0 == 0x7FF8u || h1 == 0x8000u || h1 == 0x7FF8u);
        if (rail && pend.addr < 0x1B3600u) { ++rails; uint64_t rc = ++rail_by_pc[pend.pc];
            if (rc == 1 && rail_by_pc.size() <= 40) std::fprintf(stderr, "[vstore-rail] pc=%08X addr=%06X w=%c word=%08X rails=%llu\n", pend.pc, pend.addr, pend.w, wv, (unsigned long long)rails); }
        if ((chk & 0xFFFFu) == 0) std::fprintf(stderr, "[vstore-val] chk=%llu nonzero=%llu rails=%llu railpcs=%zu\n", (unsigned long long)chk, (unsigned long long)nzv, (unsigned long long)rails, rail_by_pc.size());
    }
    pend = {pc, addr & ~0u, width, addr < 0x1B3600u};
    std::lock_guard<std::mutex> lk(mu);
    ++nw;
    if (addr >= 0x1B3600u) { if ((nw & 0xFFFFFu) == 1) std::fprintf(stderr, "[vstore-wide] total=%llu narrow=%llu\n", (unsigned long long)nw, (unsigned long long)nn); return; }
    ++nn;
    uint64_t c = ++by_pc[pc];
    if (c == 1 && by_pc.size() <= 60) std::fprintf(stderr, "[vstore] new pc=%08X addr=%06X w=%c val=%08X nn=%llu\n", pc, addr, width, value, (unsigned long long)nn);
    if ((nn & 0x3FFFu) == 0) { std::fprintf(stderr, "[vstore-sum] nn=%llu pcs=%zu:", (unsigned long long)nn, by_pc.size()); int k = 0; for (auto& kv : by_pc) { if (k++ >= 12) break; std::fprintf(stderr, " %08X=%llu", kv.first, (unsigned long long)kv.second); } std::fprintf(stderr, "\n"); }
}
// s5660: unaligned stores (swl/swr/sdl/sdr) were never hooked by the s5654 census; route them through it.
// Positive control: [ustore-all] counts every call (all addresses) so a zero narrow count is interpretable.
extern "C" void rs64_g1d_blk_set_ustore_pc(uint32_t pc);
extern "C" volatile uint32_t rs64_s6843_lo, rs64_s6843_len;
static void rs64_s6843_note(uint32_t key, uint32_t phys, uint32_t len, const char* api);
extern "C" void rs64_s5660_ustore(uint32_t pc, uint32_t addr, uint32_t value, char width) {
    rs64_g1d_blk_set_ustore_pc(pc);
    if (((addr & 0x1FFFFFFFu) - rs64_s6843_lo) < rs64_s6843_len) rs64_s6843_note(pc, addr & 0x1FFFFFFFu, 4u, nullptr); // s6843
    /* s7443 class CZ: the census below (atomic counters, [ustore-all] every 2^18 calls, s5654 forward) ran on every guest
       swl/swr/sdl/sdr with no env (42 lines per 4-min owner run). Its only consumers are ROGUESQ_VSRC_STORES (s5654, which
       returns at entry without it) and the [ustore-all] control line itself: latch both on VSRC_STORES / LOG_USTORE.
       ROGUESQ_G1E_TRIM=0 restores the old always-on census. g1d_blk pc and the s6843 store watch above stay unconditional. */
    static const bool cen = [] { auto on = [](const char* n) { const char* e = std::getenv(n); return e && e[0] && e[0] != '0'; };
        const char* t = std::getenv("ROGUESQ_G1E_TRIM"); return on("ROGUESQ_VSRC_STORES") || on("ROGUESQ_LOG_USTORE") || (t && *t == '0'); }();
    if (!cen) return;
    static std::atomic<uint64_t> all{0}, wide{0}, narrow{0};
    uint64_t a = ++all; const uint32_t p = addr & 0x1FFFFFFFu;
    if (p >= 0x1B2C60u && p < 0x29DFB8u) { ++wide; if (p < 0x1B3600u) ++narrow; rs64_s5654_vstore(pc, p, value, width); }
    if ((a & 0x3FFFFu) == 1) std::fprintf(stderr, "[ustore-all] all=%llu wide=%llu narrow=%llu\n", (unsigned long long)a, (unsigned long long)wide.load(), (unsigned long long)narrow.load());
}
// s6843: generic RDRAM store watch (tools/apply_s6843_store_watch.py). ROGUESQ_STORE_WATCH=<lo>:<hi> (hex phys) makes every
// instrumented game store, unaligned store and host write census call in [lo,hi) count per (swap, pc|api); the table of
// the previous swap prints when the swap number changes ([swatch] lines, first ROGUESQ_STORE_WATCH_LINES=4000, from swap
// ROGUESQ_STORE_WATCH_FROM_SWAP=<n>).
extern std::atomic<int> g_rs64_swap_n;
extern "C" volatile uint32_t rs64_s6843_lo = 0, rs64_s6843_len = 0;
static const bool s_s6843_init = [] {
    const char* e = std::getenv("ROGUESQ_STORE_WATCH");
    if (e && *e) { char* c = nullptr; const uint32_t lo = (uint32_t)strtoul(e, &c, 16);
        const uint32_t hi = (c && *c == ':') ? (uint32_t)strtoul(c + 1, nullptr, 16) : 0u;
        if (hi > lo) { rs64_s6843_lo = lo; rs64_s6843_len = hi - lo; std::fprintf(stderr, "[swatch] armed %06X-%06X\n", lo, hi); } }
    return true; }();
// s7334: ROGUESQ_STORE_WATCH_PTS=<p>,<p>,... (hex phys, up to 16) watches only the 16-byte windows [p, p+16): the pre-check range
// becomes [min, max+16) and every hit prints one [swatch-pt] line (swap, pc|api, phys, width, the 4 words BEFORE the store);
// non-point stores in the range are ignored (no table). First ROGUESQ_STORE_WATCH_LINES lines. Diagnostic only.
static uint32_t s_s7334_pt[16]; static int s_s7334_n = 0;
static const bool s_s7334_init = [] {
    const char* e = std::getenv("ROGUESQ_STORE_WATCH_PTS");
    if (!e || !*e) return true;
    uint32_t lo = 0xFFFFFFFFu, hi = 0; const char* c = e;
    while (*c && s_s7334_n < 16) { char* q = nullptr; const uint32_t v = (uint32_t)strtoul(c, &q, 16) & 0x1FFFFFF0u;
        if (q == c) break; s_s7334_pt[s_s7334_n++] = v; if (v < lo) lo = v; if (v + 16 > hi) hi = v + 16; c = (*q == ',') ? q + 1 : q; if (!*q) break; }
    if (s_s7334_n) { rs64_s6843_lo = lo; rs64_s6843_len = hi - lo; std::fprintf(stderr, "[swatch-pt] armed %d points %06X-%06X\n", s_s7334_n, lo, hi); }
    return true; }();
// s7779: FB-arena host-stomp census. Retail rs_malloc(flag 4) -> ensureHeapInitialized builds a scratch arena (head 0x8010FEFC)
// over a FREE framebuffer slot from acquireFreeBufferSlot (which does not mark it busy); beginSceneRenderFrame -> clearFrameReadyFlag
// drops it each frame. ROGUESQ_S7779_ARENA=1 arms the s6843 range over phys [0x400000,0x800000) and classifies every host write
// (rs64_m5_host_write_census: rt64_writeback, rsp_dmem_to_rdram, pi DMA) against the live arena [h, h + w*h*2) (w,h = 0x8011A838/3C):
// hit = host write into a live arena (H-stomp); ctl = host write into the same 0x60000 span while no arena is live. Guest stores into a
// live arena are counted lock-free (arena in use). Slot state bytes 0x80128EAA+i (count 0x80128EAD), slot words 0x80128E98+4i.
// ROGUESQ_S7779_PLANT=<n>: on the n-th guest store into a live arena a fake 4-byte host write "s7779_plant" is sent through
// rs64_m5_host_write_census (no memory is written) and MUST be counted as a hit. Summary every 10 s ([s7779] sum). Measurement only.
extern "C" void rs64_m5_host_write_census(uint8_t* rdram, uint32_t phys, uint32_t len, const char* api);
static const bool s_s7779_on = [] { const char* e = std::getenv("ROGUESQ_S7779_ARENA"); if (!(e && *e == '1')) return false;
    rs64_s6843_lo = 0x400000u; rs64_s6843_len = 0x400000u; std::fprintf(stderr, "[s7779] armed host-write vs FB-arena census 400000-800000\n"); return true; }();
static std::atomic<uint64_t> s_s7779_gst{0}, s_s7779_gst_live{0};
static uint32_t s7779_w(const volatile uint8_t* rd, uint32_t a) { return *(const volatile uint32_t*)(rd + (a & 0x7FFFFCu)); }
static uint32_t s7779_b(const volatile uint8_t* rd, uint32_t a) { return rd[(a & 0x7FFFFFu) ^ 3u]; }  /* diag-only: sole caller rs64_s7779_note */
static void rs64_s7779_note(uint32_t key, uint32_t phys, uint32_t len, const char* api) {
    if (!s_s7779_on) return;  /* ROGUESQ_S7779_ARENA diag only (s7780: census gate) */
    const volatile uint8_t* rd = g_recomp_rdram_for_wp_raw; if (!rd) return;
    const uint32_t h = s7779_w(rd, 0x10FEFCu) & 0x1FFFFFFFu;
    const uint32_t ext = (s7779_w(rd, 0x11A838u) * s7779_w(rd, 0x11A83Cu) * 2u) & 0x7FFFFFu;
    const bool live = h >= 0x400000u && h < 0x800000u;
    if (!api) {
        const uint64_t n = s_s7779_gst.fetch_add(1, std::memory_order_relaxed);
        (void)n;
        if (live && phys >= h && phys < h + ext) {
            const uint64_t k = s_s7779_gst_live.fetch_add(1, std::memory_order_relaxed) + 1;
            static const uint64_t plant = [] { const char* e = std::getenv("ROGUESQ_S7779_PLANT"); return (e && *e) ? (uint64_t)std::atoll(e) : 0ull; }();
            if (plant && k == plant) { std::fprintf(stderr, "[s7779] plant fire h=%06X pc=%08X\n", h, key);
                rs64_m5_host_write_census((uint8_t*)rd, h + 0x100u, 4u, "s7779_plant"); }
        }
        return;
    }
    struct A { uint64_t hit = 0, hitb = 0, ctl = 0, ctlb = 0, other = 0; };
    static std::mutex mu; static std::map<std::string, A> by; static int lines = 0; static double t0 = 0, tl = 0;
    static uint32_t last_h = 0; static int ntrans = 0; static uint64_t epochs = 0, busy_slot_live = 0;
    const double t = std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
    std::lock_guard<std::mutex> lk(mu);
    if (t0 == 0) t0 = tl = t;
    if (h != last_h) { if (live) ++epochs; if (ntrans++ < 60) std::fprintf(stderr, "[s7779] arena %06X -> %06X ext=%X t=%.2f\n", last_h, h, ext, t - t0); last_h = h; }
    const uint32_t nsl = s7779_b(rd, 0x128EADu); int si = -1; uint32_t st = 0xFF;
    if (live) for (uint32_t i = 0; i < nsl && i < 4; ++i) if ((s7779_w(rd, 0x128E98u + 4u * i) & 0x1FFFFFFFu) == h) { si = (int)i; st = s7779_b(rd, 0x128EAAu + i); }
    if (live && si >= 0 && st != 0) ++busy_slot_live;
    A& a = by[api];
    const bool in_live = live && phys < h + ext && phys + len > h;
    const uint32_t span_lo = live ? h : 0x656000u;  /* ctl span: hangar FB A when no arena is live */
    if (in_live) { ++a.hit; a.hitb += len;
        if (lines++ < 80) std::fprintf(stderr, "[s7779] HIT api=%s phys=%06X len=%X arena=%06X ext=%X slot=%d st=%u nsl=%u t=%.2f\n", api, phys, len, h, ext, si, st, nsl, t - t0); }
    else if (!live && phys < span_lo + 0x60000u && phys + len > span_lo) { ++a.ctl; a.ctlb += len; }
    else ++a.other;
    if (t - tl >= 10.0) { tl = t;
        std::fprintf(stderr, "[s7779] sum t=%.1f epochs=%llu busy_slot_live=%llu gst=%llu gst_live=%llu", t - t0, (unsigned long long)epochs, (unsigned long long)busy_slot_live,
                     (unsigned long long)s_s7779_gst.load(), (unsigned long long)s_s7779_gst_live.load());
        for (auto& kv : by) std::fprintf(stderr, " %s:hit=%llu/%lluB,ctl=%llu/%lluB,oth=%llu", kv.first.c_str(), (unsigned long long)kv.second.hit, (unsigned long long)kv.second.hitb,
                                         (unsigned long long)kv.second.ctl, (unsigned long long)kv.second.ctlb, (unsigned long long)kv.second.other);
        std::fprintf(stderr, "\n"); }
}
static void rs64_s6843_note(uint32_t key, uint32_t phys, uint32_t len, const char* api) {
    if (s_s7779_on) { rs64_s7779_note(key, phys, len, api); return; }
    struct Agg { uint64_t n = 0, bytes = 0; uint32_t lo = 0xFFFFFFFFu, hi = 0; const char* api = nullptr; };
    static std::mutex mu; static std::map<uint32_t, Agg> by; static int cur = -1; static int lines = 0;
    static const int cap = [] { const char* e = std::getenv("ROGUESQ_STORE_WATCH_LINES"); return (e && *e) ? std::atoi(e) : 4000; }();
    static const int from = [] { const char* e = std::getenv("ROGUESQ_STORE_WATCH_FROM_SWAP"); return (e && *e) ? std::atoi(e) : 0; }();
    const int sw = g_rs64_swap_n.load(std::memory_order_relaxed);
    if (sw < from) return;
    if (s_s7334_n) {   // s7334 point mode
        int k = -1; for (int i = 0; i < s_s7334_n; ++i) if (phys + len > s_s7334_pt[i] && phys < s_s7334_pt[i] + 16) { k = i; break; }
        if (k < 0) return;
        std::lock_guard<std::mutex> lk(mu);
        if (lines++ >= cap) return;
        uint32_t w[4] = {}; const volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (rd) for (int i = 0; i < 4; ++i) { const uint32_t a = s_s7334_pt[k] + 4u * i; w[i] = *(const volatile uint32_t*)(rd + a); }
        std::fprintf(stderr, "[swatch-pt] swap=%d %s=%08X%s%s phys=%06X len=%u pt=%06X pre=%08X %08X %08X %08X\n", sw, api ? "api" : "pc", key,
                     api ? ":" : "", api ? api : "", phys, len, s_s7334_pt[k], w[0], w[1], w[2], w[3]);
        return;
    }
    std::lock_guard<std::mutex> lk(mu);
    if (sw != cur) {
        for (auto& kv : by) if (lines++ < cap)
            std::fprintf(stderr, "[swatch] swap=%d %s=%08X%s%s n=%llu bytes=%llu lo=%06X hi=%06X\n", cur, kv.second.api ? "api" : "pc", kv.first, kv.second.api ? ":" : "", kv.second.api ? kv.second.api : "",
                         (unsigned long long)kv.second.n, (unsigned long long)kv.second.bytes, kv.second.lo, kv.second.hi);
        if (!by.empty() && lines < cap) std::fprintf(stderr, "[swatch] swap=%d keys=%zu\n", cur, by.size());
        by.clear(); cur = sw;
    }
    Agg& a = by[key]; ++a.n; a.bytes += len; if (phys < a.lo) a.lo = phys; if (phys + len > a.hi) a.hi = phys + len; if (api) a.api = api;
}
// s6876: mat3x4Multiply entry (tools/apply_s6876_camcaller.py). ROGUESQ_CAM_CALLER=1 prints, for calls whose output is the camera rotation
// 0x80138458+0x28, the host return address and row 1 of both inputs: every new caller, then every 512th call.
// s6877: each call that moves row 1 of the camera also prints a [camcall2] row (first ROGUESQ_CAM_CALLER_LINES=30000): swap, row 1 before and
// the product's row 1 after (the mat3x4Multiply formula, in float), both 3x3 inputs, camera position and the +0xD0/+0xE0 angle words.
extern std::atomic<int> g_rs64_swap_n;
extern "C" void rs64_s6876_mm(uint8_t* rdram, uint32_t ra, uint32_t a0, uint32_t a1, uint32_t a2) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_CAM_CALLER"); return e && *e && *e != '0'; }();
    if (!on || (a2 & 0x1FFFFFFFu) != 0x138480u) return;
    // ctx->r31 reads 0 here (recompiled jal does not set it), so key on the host return into the caller; resolve offline: atos -o <exe> -l 0x100000000 <hra>.
    const uintptr_t hra = (uintptr_t)__builtin_return_address(1) - (uintptr_t)_dyld_get_image_vmaddr_slide(0);
    static std::mutex mu; static std::map<uintptr_t, uint64_t> by;
    std::lock_guard<std::mutex> lk(mu);
    const uint64_t n = ++by[hra];
    auto rf = [&](uint32_t va, uint32_t o) { float f; memcpy(&f, rdram + ((va + o) & 0x7FFFFCu), 4); return f; };
    static const int cap = [] { const char* e = std::getenv("ROGUESQ_CAM_CALLER_LINES"); return (e && *e) ? std::atoi(e) : 30000; }();
    static int lines = 0;
    float A[9], B[9], o[3], w[3];
    for (int i = 0; i < 9; i++) { A[i] = rf(a0, 4 * i); B[i] = rf(a1, 4 * i); }
    for (int i = 0; i < 3; i++) { o[i] = A[3] * B[i] + A[4] * B[3 + i] + A[5] * B[6 + i]; w[i] = rf(a2, 12 + 4 * i); }
    if (lines < cap && (o[0] != w[0] || o[1] != w[1] || o[2] != w[2])) {
        lines++;
        std::fprintf(stderr, "[camcall2] sw=%d hra=%llX n=%llu a0=%08X a1=%08X was=%.7f,%.7f,%.7f now=%.7f,%.7f,%.7f A=%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f "
                     "B=%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f pos=%.4f,%.4f,%.4f d0=%.7f e0=%.7f\n", g_rs64_swap_n.load(), (unsigned long long)hra, (unsigned long long)n, a0, a1,
                     w[0], w[1], w[2], o[0], o[1], o[2], A[0], A[1], A[2], A[3], A[4], A[5], A[6], A[7], A[8], B[0], B[1], B[2], B[3], B[4], B[5], B[6], B[7], B[8],
                     rf(0x80138458u, 0x10), rf(0x80138458u, 0x14), rf(0x80138458u, 0x18), rf(0x80138458u, 0xD0), rf(0x80138458u, 0xE0));
    }
    if (n != 1 && (n & 511u)) return;
    std::fprintf(stderr, "[camcaller] hra=%llX n=%llu a0=%08X a1=%08X a0row1=%.5f,%.5f,%.5f a1row1=%.5f,%.5f,%.5f\n", (unsigned long long)hra, (unsigned long long)n, a0, a1,
                 (double)A[3], (double)A[4], (double)A[5], (double)B[3], (double)B[4], (double)B[5]);
}
// s6845: drawSubtitleText -> drawTextGlyphRect argument probe (tools/apply_s6845_glyph_probe.py), VI window = ROGUESQ_WIPE_SCAN.
extern "C" volatile uint32_t rs64_vi_n_g;
static uint32_t s_s6845_lo = 0, s_s6845_hi = 0;
extern "C" int rs64_s6845_on = [] { const char* e = std::getenv("ROGUESQ_WIPE_SCAN"); if (!e || !*e) return 0; char* c = nullptr;
    s_s6845_lo = (uint32_t)strtoul(e, &c, 10); s_s6845_hi = (c && *c == ':') ? (uint32_t)strtoul(c + 1, nullptr, 10) : 0u; return s_s6845_hi > s_s6845_lo ? 1 : 0; }();
extern "C" void rs64_s6845_glyph(uint8_t* rdram, uint32_t site, uint32_t a1, uint32_t a2, uint32_t a3, uint32_t lry, uint32_t s3, uint32_t s1,
                                 uint32_t fp, uint32_t bx, uint32_t by) {
    const uint32_t vi = rs64_vi_n_g;
    if (vi < s_s6845_lo || vi > s_s6845_hi) return;
    static int lines = 0; if (lines++ >= 4000) return;
    auto rw = [&](uint32_t va) { uint32_t v; memcpy(&v, rdram + (va & 0x7FFFFCu), 4); return v; };
    auto rf = [&](uint32_t va) { uint32_t v = rw(va); float f; memcpy(&f, &v, 4); return (double)f; };
    // s6846: + text length (+0x8 hu), string ptr (+0xC), flags (+0x14) and the first string halfwords, to name the glyph selector.
    const uint32_t sp = rw(s3 + 0xC); const uint32_t s0w = rw(sp), s1w = rw(sp + 4);
    std::fprintf(stderr, "[glyph] vi=%u site=%08X ulx=%d uly=%d lrx=%d lry=%d fp=%d base=%d,%d obj=%08X ox=%.3f oy=%.3f sx=%.4f sy=%.4f arg=%08X ax=%d ay=%d W=%u len=%u str=%08X:%08X%08X fl=%08X\n",
                 vi, site, (int)(int16_t)a1, (int)(int16_t)a2, (int)(int16_t)a3, (int)(int32_t)lry, (int)(int32_t)fp, (int)(int16_t)bx, (int)(int16_t)by,
                 s3, rf(s3 + 0x18), rf(s3 + 0x1C), rf(s3 + 0x24), rf(s3 + 0x28), s1, (int)rw(s1 + 0x18), (int)rw(s1 + 0x1C), rw(0x8011A838u),
                 rw(s3 + 0x8) >> 16, sp, s0w, s1w, rw(s3 + 0x14));
}
// s6845b: drawSubtitleText entry: log (text obj, screen struct, struct+0x18 x centre) when the centre changes inside the
// window, and arm the s6843 store watch on the first struct's +0x18 word so `[swatch]` names its writer.
extern "C" void rs64_s6845_entry(uint8_t* rdram, uint32_t a0, uint32_t a1) {
    const uint32_t vi = rs64_vi_n_g;
    if (vi + 40 < s_s6845_lo || vi > s_s6845_hi) return;
    static uint32_t last_a1 = 0, last_c = 0xFFFFFFFFu; static int lines = 0; static bool armed = false;
    uint32_t c; memcpy(&c, rdram + ((a1 + 0x18) & 0x7FFFFCu), 4);
    if ((a1 != last_a1 || c != last_c) && lines++ < 400) std::fprintf(stderr, "[glyph-entry] vi=%u obj=%08X scr=%08X cx=%d\n", vi, a0, a1, (int)c);
    last_a1 = a1; last_c = c;
    // s6846: ROGUESQ_WIPE_WATCH_OBJ=1 arms the watch on the full-screen (|x scale| > 8) text object itself (+0x00..+0x40) instead,
    // so `[swatch]` names the wipe updater that writes its x (+0x18) and glyph/string fields.
    static const bool watch_obj = [] { const char* e = std::getenv("ROGUESQ_WIPE_WATCH_OBJ"); return e && *e == '1'; }();
    if (watch_obj) {
        float sc; uint32_t w; memcpy(&w, rdram + ((a0 + 0x24) & 0x7FFFFCu), 4); memcpy(&sc, &w, 4);
        if (!armed && (sc > 8.0f || sc < -8.0f)) { armed = true; rs64_s6843_lo = a0 & 0x1FFFFFFFu; rs64_s6843_len = 0x40;
            std::fprintf(stderr, "[glyph-entry] obj watch armed %08X+0x40 vi=%u\n", rs64_s6843_lo, vi); }
    } else if (!armed) { armed = true; rs64_s6843_lo = (a1 + 0x18) & 0x1FFFFFFFu; rs64_s6843_len = 4; std::fprintf(stderr, "[glyph-entry] watch armed %08X\n", rs64_s6843_lo); }
}
extern "C" void rs64_s6845_base(uint8_t* rdram, uint32_t s3, uint32_t s1, uint32_t t2, uint32_t f4, uint32_t f6) {
    const uint32_t vi = rs64_vi_n_g;
    if (vi < s_s6845_lo || vi > s_s6845_hi) return;
    static int lines = 0; if (lines++ >= 2000) return;
    auto rw = [&](uint32_t va) { uint32_t v; memcpy(&v, rdram + (va & 0x7FFFFCu), 4); return v; };
    auto fl = [](uint32_t v) { float f; memcpy(&f, &v, 4); return (double)f; };
    std::fprintf(stderr, "[glyph-base] vi=%u obj=%08X scr=%08X ox=%.3f cx=%d f4=%.3f f6=%.4f t2=%d\n", vi, s3, s1, fl(rw(s3 + 0x18)), (int)rw(s1 + 0x18), fl(f4), fl(f6), (int)t2);
}
// s6845 G1d (tools/apply_s6845_hudwipe.py): the s6156 HUD anchor applies only to HUD-sized elements. A text element
// whose x scale (obj+0x24) exceeds 8 is a full-screen sprite (the abort-level wipe, glyph 0x180, sx 36.6 at 4:3 / 73.1
// at 21:9; HUD items 1.0-3.2) and keeps the game's centred position. ROGUESQ_G1D_HUD_BIGSCALE=1 = old (anchor everything).
// s6846 G1d (tools/apply_s6846_wipeeps.py): the abort-wipe updater in initHudStruct picks the flat end glyph when
// ox <= -W/2 + 1; the end residual is W*0.001, so the 1 px epsilon scales with W above 640 (ceil(W/512)).
// Argument = the generated v0 = (-W)/2. ROGUESQ_G1D_WIPE_EPS=0 = old (always 1).
// s6848 G1d: emitColorFillRect packs the screen width as (W & 0x3FF) << 14 into G_FILLRECT lr.x; W 1024 wraps to 0 and
// the mission-end transition overlay bands vanish at 21:9. Clamp to 1023 (fill-mode lr is inclusive); identity for W <= 1023.
// ROGUESQ_G1D_OVL_WRAP=0 = old. tools/apply_s6848_ovlwrap.py.
extern "C" uint64_t rs64_s6848_ovl_w(uint64_t w) {
    static const bool old = [] { const char* e = std::getenv("ROGUESQ_G1D_OVL_WRAP"); return e && *e == '0'; }();
    if (old || (uint32_t)w <= 1023u) return w;
    static int lines = 0;
    if (lines++ < 4) std::fprintf(stderr, "[g1d-ovlwrap] W=%u -> 1023 vi=%u\n", (unsigned)(uint32_t)w, rs64_vi_n_g);
    return 1023u;
}
// s6848 diagnostic: ROGUESQ_S6848_FORCE_OVL=<vi_lo>:<vi_hi> arms setScreenColorOverlay's state (window x0 128 y0 64 x1 896
// y1 384, red, mode 0 = every frame) inside the VI window, so emitColorFillRect runs on a route that never ends a mission.
extern "C" void rs64_s6848_force_ovl(uint8_t* rdram) {
    static uint32_t lo = 0, hi = 0;
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_S6848_FORCE_OVL"); if (!e || !*e) return false;
        char* c = nullptr; lo = (uint32_t)std::strtoul(e, &c, 10); hi = (c && *c == ':') ? (uint32_t)std::strtoul(c + 1, nullptr, 10) : 0u; return hi > lo; }();
    if (!on) return;
    const uint32_t vi = rs64_vi_n_g;
    static bool armed = false;
    auto h = [&](uint32_t a, uint16_t v) { std::memcpy(rdram + (((a - 0x80000000u)) ^ 2u), &v, 2); };
    auto b = [&](uint32_t a, uint8_t v) { rdram[(a - 0x80000000u) ^ 3u] = v; };
    if (vi >= lo && vi <= hi) {
        h(0x8011A880u, 128); h(0x8011A882u, 64); h(0x8011A884u, 896); h(0x8011A886u, 384);
        b(0x8011A888u, 255); b(0x8011A889u, 0); b(0x8011A88Au, 0); b(0x8011A88Cu, 1); b(0x8011A88Du, 0);
        if (!armed) { armed = true; std::fprintf(stderr, "[s6848-forceovl] armed vi=%u\n", vi); }
    } else if (armed) { armed = false; b(0x8011A88Cu, 0); std::fprintf(stderr, "[s6848-forceovl] disarmed vi=%u\n", vi); }
}

extern "C" int32_t rs64_s6846_wipe_eps(int32_t neg_half_w) {
    static const bool old = [] { const char* e = std::getenv("ROGUESQ_G1D_WIPE_EPS"); return e && *e == '0'; }();
    const int32_t w = -2 * neg_half_w;
    if (old || w <= 640) return 1;
    const int32_t eps = (w + 511) / 512;
    static int lines = 0;
    if (lines++ < 4) std::fprintf(stderr, "[g1d-wipeeps] W=%d eps=%d vi=%u\n", (int)w, (int)eps, rs64_vi_n_g);
    return eps;
}
extern "C" int rs64_s6845_hud_small(uint32_t sx_bits) {
    static const bool old = [] { const char* e = std::getenv("ROGUESQ_G1D_HUD_BIGSCALE"); return e && *e == '1'; }();
    float sx; memcpy(&sx, &sx_bits, 4);
    if (old || !(sx > 8.0f || sx < -8.0f)) return 1;
    static int lines = 0;
    if (lines++ < 8) std::fprintf(stderr, "[g1d-hudwipe] anchor skipped for full-screen element sx=%.3f vi=%u\n", (double)sx, rs64_vi_n_g);
    return 0;
}
// s6860: anchor exemption bound for vp 0x80138D20. The reticle is static data (0x8010CA58/88); the HUD table is heap and
// sits at 0x8028FDxx on lvl10, under the old 0x80300000 bound. ROGUESQ_G1D_HUD_ELEMTOP=1 = old.
extern "C" uint32_t rs64_s6860_hud_elem_top(void) {
    static const bool old = [] { const char* e = std::getenv("ROGUESQ_G1D_HUD_ELEMTOP"); return e && *e == '1'; }();
    return old ? 0x80300000u : 0x80110000u;
}
extern "C" void rs64_s6843_store(uint32_t pc, uint32_t phys, char width) {
    const char w = (char)(width | 0x20); rs64_s6843_note(pc, phys, w == 'b' ? 1u : w == 'h' ? 2u : w == 'd' ? 8u : 4u, nullptr);
}
extern "C" void rs64_f5_host_bulk_shadow(uint32_t phys, uint32_t len,
                                           const char* api);
extern "C" void rs64_f5_host_write_after(const uint8_t* rdram, uint32_t phys,
                                           uint32_t len, const char* api);
extern "C" void rs64_m5_host_write_census(uint8_t* rdram,
                                            uint32_t phys,
                                            uint32_t len,
                                            const char* api) {
    if (rs64_s6843_len && len && (phys & 0x00FFFFFFu) < rs64_s6843_lo + rs64_s6843_len && (phys & 0x00FFFFFFu) + len > rs64_s6843_lo)
        rs64_s6843_note((uint32_t)(uintptr_t)api ^ 0xA0000000u, phys & 0x00FFFFFFu, len, api ? api : "?"); // s6843 host writes
    rs64_f5_host_bulk_shadow(phys, len, api);
    rs64_f5_host_write_after(rdram, phys, len, api);
    if (rs64_vsrc_hi && len) {
        const uint32_t s_ = phys & 0x007FFFFFu;
        if (s_ < rs64_vsrc_hi && s_ + len > rs64_vsrc_lo) {
            rs64_vsrc_nw++; rs64_vsrc_lastphys = s_; rs64_vsrc_lastlen = len;
            // s6712: copy only when the api changes (the per-write snprintf was ~11% of the gfx ucode under LOG_HUDBIT).
            static const char* s_vsrc_api = nullptr;
            if (api != s_vsrc_api) { s_vsrc_api = api; std::snprintf(rs64_vsrc_lastapi, sizeof rs64_vsrc_lastapi, "%s", api ? api : "?"); }
            if (rs64_vsrc_nw <= 30) std::fprintf(stderr, "[vsrc-hostwrite] #%u api=%s phys=%06X len=%X range=%06X-%06X\n", rs64_vsrc_nw, api ? api : "?", s_, len, rs64_vsrc_lo, rs64_vsrc_hi);
        }
    }
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_HOST_WRITE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (s4578_on() && rdram && len) {
        rs64_s4578_start(rdram);
        const uint32_t s_ = phys & 0x007FFFFFu;
        g_s4578_total++;
        if (s_ < 0x14A000u && s_ + len > 0x149000u) g_s4578_page++;
        {
            std::lock_guard<std::mutex> g(g_s4578_mu);
            auto& e = g_s4578_ring[g_s4578_n % 16];
            e.seq = g_s4578_n++; e.phys = s_; e.len = len; e.vi_w = rs64_vi_committed_width();
            std::snprintf(e.api, sizeof e.api, "%s", api ? api : "?");
        }
        if (s_ < 0x149720u && s_ + len > 0x149700u)
            std::fprintf(stderr, "[s4578-HOSTWRITE-OVERLAP] phys=%06X len=%X api=%s vi_w=%u\n", s_, len, api ? api : "?", rs64_vi_committed_width());
    }
    {
        // s4639: host writes into the hangar colour buffers (0x656400 and
        // 0x6AB400, 512x16bpp, 260 rows). "col511" = write touches bytes
        // 1022..1023 of some row. Body hits are the same-run positive control.
        static const bool bw_on = [] {
            const char* v = std::getenv("ROGUESQ_BUF_WATCH");
            return v && v[0] && v[0] != '0';
        }();
        if (bw_on && rdram && len) {
            static const uint32_t bases[2] = {0x656400u, 0x6AB400u};
            static std::atomic<uint32_t> cnt[2][2];  // [buf][0=any,1=col511]
            static std::atomic<uint32_t> logged{0};
            const uint32_t s = phys & 0x007FFFFFu;
            for (int b = 0; b < 2; ++b) {
                const uint32_t lo = bases[b], hi = lo + 512u * 2u * 260u;
                if (s >= hi || s + len <= lo) continue;
                const uint32_t a = s > lo ? s : lo;
                const uint32_t e = (s + len) < hi ? (s + len) : hi;
                bool c511 = (e - a) >= 1024u;
                for (uint32_t o = a; !c511 && o < e; ++o)
                    if (((o - lo) & 1023u) >= 1022u) c511 = true;
                const uint32_t n_any = ++cnt[b][0];
                const uint32_t n_c = c511 ? ++cnt[b][1] : cnt[b][1].load();
                if (rs64_vi_committed_width() == 512u && logged++ < 200u)
                    std::fprintf(stderr,
                        "[s4639-bufwatch] buf=%06X api=%s phys=%06X len=%X c511=%d vi_w=%u n_any=%u n_c511=%u\n",
                        lo, api ? api : "?", s, len, (int)c511,
                        rs64_vi_committed_width(), n_any, n_c);
            }
        }
    }
    if (!enabled || !rdram || len == 0u) return;
    static std::atomic<uint32_t> api_mask{0};
    uint32_t bit = 8u;
    if (api && std::strcmp(api, "pi_rom_to_rdram") == 0) bit = 1u;
    else if (api && std::strcmp(api, "pi_sram_to_rdram") == 0) bit = 2u;
    else if (api && std::strcmp(api, "zmemcpy") == 0) bit = 4u;
    const uint32_t prior = api_mask.fetch_or(bit, std::memory_order_relaxed);
    if ((prior & bit) == 0u) {
        std::fprintf(stderr, "[m5-host-write-api-control] api=%s phys=0x%06X len=0x%X\n",
                     api ? api : "unknown", phys & 0x007FFFFFu, len);
        std::fflush(stderr);
    }
    const uint32_t start = phys & 0x007FFFFFu;
    const uint32_t end = start + len;
    const struct {
        uint32_t start;
        uint32_t len;
        const char* name;
    } fields[] = {
        {0x128C92u, 1u, "route_byte"},
        {0x128CD0u, 4u, "route_word"},
        {0x171E70u, 0x100u, "task_data"},
        {0x178C80u, 0x198u, "image_input"},
        {0x1797B0u, 0x298u, "preclear_target"},
    };
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target) return;
    static uint32_t rows = 0;
    for (const auto& field : fields) {
        if (start >= field.start + field.len || end <= field.start) continue;
        if (rows++ >= 512u) return;
        uint32_t post = 0u;
        for (uint32_t i = 0; i < field.len; ++i) {
            post = (post << 8) | rdram[((field.start + i) ^ 3u) & 0x007FFFFFu];  // s7601 BS: was no ^3
        }
        std::fprintf(stderr,
            "[m5-host-write] n=%u api=%s phase=%u width=%u origin=0x%06X "
            "phys=0x%06X len=0x%X field=%s@0x%06X field_len=%u post=0x%08X\n",
            rows - 1u, api ? api : "unknown", rs64_phase_ord(), width, origin,
            start, len, field.name, field.start, field.len, post);
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_audio_source_dma(uint8_t* rdram, uint32_t dram_addr,
                                           uint32_t len, uint32_t dmem_addr) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_RSP_SOURCE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || len == 0) return;

    static std::atomic<uint32_t> hook_control{0};
    if (hook_control.fetch_add(1, std::memory_order_relaxed) == 0) {
        std::fprintf(stderr,
            "[m5-rsp-source-hook-control] dram=0x%06X dmem=0x%03X len=0x%X\n",
            dram_addr, dmem_addr, len);
        std::fflush(stderr);
    }

    uint32_t phase = 0, width = 0, origin = 0, route_ordinal = 0xFFFFFFFFu,
             route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &phase, &width, &origin, &route_ordinal, &route_row, &exit_reason,
        &arm);
    const bool target_phase = (width == 1024u && origin == 0x00790400u) ||
                              (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;

    static std::mutex census_mutex;
    static uint32_t census_key = 0xFFFFFFFFu;
    static uint32_t census_rows = 0;
    const uint32_t census_phase_key = (width << 24) ^ origin;
    {
        std::lock_guard<std::mutex> lock(census_mutex);
        if (census_phase_key != census_key) {
            census_key = census_phase_key;
            census_rows = 0;
            std::fprintf(stderr,
                "[m5-rsp-dma-census-control] phase=%u width=%u origin=0x%06X arm=%s\n",
                phase, width, origin, arm ? arm : "n/a");
            std::fflush(stderr);
        }
        if (census_rows < 4096u) {
            const bool dram_source = dram_addr < 0x1798B0u &&
                                     dram_addr + len > 0x1797B0u;
            const bool dmem_window2 = dmem_addr < 0x9F0u &&
                                      dmem_addr + len > 0x6F0u;
            const bool dmem_window3 = dmem_addr < 0xE48u &&
                                      dmem_addr + len > 0xCB0u;
            std::fprintf(stderr,
                "[m5-rsp-dma-census] row=%u phase=%u width=%u origin=0x%06X arm=%s "
                "route_ordinal=%u route_row=%u dram=0x%06X len=0x%X dmem=0x%03X "
                "dram_source=%u dmem2=%u dmem3=%u exit=%d\n",
                census_rows++, phase, width, origin, arm ? arm : "n/a",
                route_ordinal, route_row, dram_addr, len, dmem_addr,
                dram_source ? 1u : 0u, dmem_window2 ? 1u : 0u,
                dmem_window3 ? 1u : 0u, exit_reason);
            std::fflush(stderr);
        }
    }

    const uint32_t source_first = 0x1797B0u, source_last = 0x179A48u;
    const uint32_t source_end = dram_addr + len;

    const bool source_window2 = dmem_addr < 0x9F0u &&
                                dmem_addr + len > 0x6F0u;
    const bool source_window3 = dmem_addr < 0xE48u &&
                                dmem_addr + len > 0xCB0u;
    if (source_window2 || source_window3) {
        uint32_t source_dma_fnv = 2166136261u;
        uint32_t source_dma_nonzero = 0u;
        for (uint32_t i = 0; i < len; ++i) {
            const uint8_t byte = rdram[(dram_addr + i) & 0x007FFFFFu];
            source_dma_fnv = (source_dma_fnv * 16777619u) ^ byte;
            source_dma_nonzero += byte != 0u;
        }
        g_rs64_m5_last_source_dma_seq = g_rs64_m5_source_event++;
        g_rs64_m5_last_source_dma_dram = dram_addr;
        g_rs64_m5_last_source_dma_len = len;
        g_rs64_m5_last_source_dma_dmem = dmem_addr;
        g_rs64_m5_last_source_dma_fnv = source_dma_fnv;
        g_rs64_m5_last_source_dma_nonzero = source_dma_nonzero;
        if (source_window3) {
            g_rs64_m5_last_source_dma3_seq = g_rs64_m5_last_source_dma_seq;
            g_rs64_m5_last_source_dma3_dram = dram_addr;
            g_rs64_m5_last_source_dma3_len = len;
            g_rs64_m5_last_source_dma3_dmem = dmem_addr;
            g_rs64_m5_last_source_dma3_fnv = source_dma_fnv;
            g_rs64_m5_last_source_dma3_nonzero = source_dma_nonzero;
        }
    }
    if (dram_addr < source_last && source_end > source_first) {
        const uint32_t overlap_first = dram_addr > source_first ?
            dram_addr : source_first;
        const uint32_t overlap_last = source_end < source_last ?
            source_end : source_last;
        uint32_t source_fnv = 2166136261u, source_nz = 0u;
        uint32_t dmem_fnv = 2166136261u, dmem_nz = 0u;
        for (uint32_t addr = overlap_first; addr < overlap_last; ++addr) {
            const uint32_t offset = addr - dram_addr;
            const uint8_t source = rdram[(addr & 0x007FFFFFu) ^ 3u];
            const uint8_t staged = RSP_MEM_BU(0, dmem_addr + offset);
            source_fnv = (source_fnv * 16777619u) ^ source;
            source_nz += source != 0u;
            dmem_fnv = (dmem_fnv * 16777619u) ^ staged;
            dmem_nz += staged != 0u;
        }
        static std::mutex source_mutex;
        static uint32_t source_rows[2] = {};
        std::lock_guard<std::mutex> lock(source_mutex);
        const uint32_t slot = width == 1024u ? 0u : 1u;
        if (source_rows[slot] < 512u) {
            const uint64_t event = g_rs64_m5_last_input_event;
            g_rs64_m5_last_source_event = event;
            const uint32_t task_data_ptr = s_pending_audio_task == nullptr ?
                0u : static_cast<uint32_t>(s_pending_audio_task->t.data_ptr);
            const uint32_t task_data_size = s_pending_audio_task == nullptr ?
                0u : static_cast<uint32_t>(s_pending_audio_task->t.data_size);
            const uint64_t latest_generation =
                g_m5_latest_audio_generation.load(std::memory_order_acquire);
            const uint32_t latest_route_seq =
                g_m5_latest_audio_route_seq.load(std::memory_order_acquire);
            const uint32_t latest_route_ordinal =
                g_m5_latest_audio_route_ordinal.load(std::memory_order_acquire);
            const uint32_t latest_route_row =
                g_m5_latest_audio_route_row.load(std::memory_order_acquire);
            const uint32_t input_fnv = g_rs64_m5_last_input_fnv;
            const uint32_t input_nonzero = g_rs64_m5_last_input_nonzero;
            const uint32_t input_dram = g_rs64_m5_last_input_dram;
            const uint32_t input_len = g_rs64_m5_last_input_len;
            const uint32_t input_dmem = g_rs64_m5_last_input_dmem;
            const uint32_t input_task_data_ptr =
                g_rs64_m5_last_input_task_data_ptr;
            std::fprintf(stderr,
                "[m5-source-range-reader] event=%llu row=%u op=dma_to_dmem "
                "phase=%u width=%u origin=0x%06X arm=%s route_ordinal=%u "
                "route_row=%u dram=0x%06X len=0x%X dmem=0x%03X "
                "overlap=0x%06X..0x%06X source_fnv=%08X source_nz=%u "
                "input_event=%llu input_dram=0x%06X input_len=0x%X "
                "input_dmem=0x%03X input_fnv=%08X input_nz=%u "
                "input_task_data_ptr=0x%08X "
                "dmem_fnv=%08X dmem_nz=%u task_data_ptr=0x%08X "
                "task_data_size=0x%X task_generation=%llu handoff_thread=%u "
                "event_thread=%u latest_generation=%llu latest_route_seq=%u "
                "latest_route_ordinal=%u latest_route_row=%u exit=%d\n",
                static_cast<unsigned long long>(event),
                source_rows[slot]++, phase, width, origin, arm ? arm : "n/a",
                route_ordinal, route_row, dram_addr, len, dmem_addr,
                overlap_first, overlap_last, source_fnv, source_nz,
                static_cast<unsigned long long>(event), input_dram, input_len,
                input_dmem, input_fnv, input_nonzero, input_task_data_ptr,
                dmem_fnv,
                dmem_nz, task_data_ptr, task_data_size,
                static_cast<unsigned long long>(s_pending_audio_generation),
                s_pending_audio_thread_id, rs64_m5_identity_thread_id(),
                static_cast<unsigned long long>(latest_generation),
                latest_route_seq, latest_route_ordinal, latest_route_row,
                exit_reason);
            std::fflush(stderr);
            rs64_audio_join_image_source(
                arm, route_ordinal, route_row, phase, width, origin, event,
                task_data_ptr, dram_addr, overlap_last - overlap_first,
                source_fnv, source_nz, s_pending_audio_generation,
                s_pending_audio_thread_id, rs64_m5_identity_thread_id(),
                input_fnv, input_nonzero, input_dram, input_len, input_dmem,
                input_task_data_ptr);
        }
    }

    const bool window2 = dmem_addr < 0x9F0u && dmem_addr + len > 0x6F0u;
    const bool window3 = dmem_addr < 0xE48u && dmem_addr + len > 0xCB0u;
    uint32_t fnv = 2166136261u, nonzero = 0;
    for (uint32_t i = 0; i < len; ++i) {
        const uint8_t b = rdram[(dram_addr + i) & 0x007FFFFFu];
        fnv = (fnv * 16777619u) ^ b;
        nonzero += b != 0;
    }
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        g_rs64_m5_source_window_rows = 0;
        std::fprintf(stderr,
            "[m5-rsp-source-control] phase=%u width=%u origin=0x%06X\n",
            phase, width, origin);
        std::fflush(stderr);
    }
    if (rows < 512u) {
        std::fprintf(stderr,
            "[m5-rsp-source] row=%u phase=%u width=%u origin=0x%06X arm=%s "
            "route_ordinal=%u route_row=%u dmem=0x%03X len=0x%X window2=%u "
            "window3=%u dram=0x%06X fnv=%08X nz=%u exit=%d\n",
            rows, phase, width, origin, arm ? arm : "n/a", route_ordinal,
            route_row, dmem_addr, len, window2 ? 1u : 0u, window3 ? 1u : 0u,
            dram_addr, fnv, nonzero, exit_reason);
        std::fflush(stderr);
        ++rows;
    }

    if ((window2 || window3) && g_rs64_m5_source_window_rows < 4096u) {
        const uint32_t windows[][2] = {{0x6F0u, 0x9F0u}, {0xCB0u, 0xE48u}};
        for (uint32_t window = 0; window < 2u; ++window) {
            const uint32_t first = windows[window][0];
            const uint32_t last = windows[window][1];
            if (dmem_addr >= last || dmem_addr + len <= first) continue;
            uint32_t exact_fnv = 2166136261u;
            uint32_t exact_nz = 0;
            for (uint32_t i = first; i < last; ++i) {
                const uint8_t b = g_dmem_cur[i ^ 3u];
                exact_fnv = (exact_fnv * 16777619u) ^ b;
                exact_nz += b != 0;
            }
            std::fprintf(stderr,
                "[m5-source-window] event=%llu op=dma phase=%u width=%u "
                "origin=0x%06X route_ordinal=%u route_row=%u window=%u "
                "dmem=0x%03X len=0x%X post_fnv=%08X post_nz=%u "
                "dram=0x%06X\n",
                static_cast<unsigned long long>(g_rs64_m5_source_event++),
                phase, width, origin, route_ordinal, route_row, window + 2u,
                dmem_addr, len, exact_fnv, exact_nz, dram_addr);
            ++g_rs64_m5_source_window_rows;
        }
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_source_range_dma_write(uint8_t* rdram,
                                                   uint32_t dram_addr,
                                                   uint32_t len,
                                                   uint32_t dmem_addr) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SOURCE_WRITER");
        const char* transition = std::getenv("ROGUESQ_LOG_M5_SOURCE_TRANSITION");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0') ||
               (transition && transition[0] && transition[0] != '0');
    }();
    if (!enabled || len == 0u) return;
    static const bool transition_enabled = [] {
        const char* rs64_la = std::getenv("ROGUESQ_LOG_ALL"); // s7728: LOG_ALL, as the line-2716 gate
        const char* value = std::getenv("ROGUESQ_LOG_M5_SOURCE_TRANSITION");
        return (rs64_la && *rs64_la && *rs64_la != '0') || (value && value[0] && value[0] != '0');
    }();
    uint32_t phase = 0, width = 0, origin = 0, route_ordinal = 0xFFFFFFFFu,
             route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool route_active = rs64_audio_current_route_snapshot(
            &phase, &width, &origin, &route_ordinal, &route_row,
            &exit_reason, &arm);
    const bool target_phase = (width == 1024u && origin == 0x00790400u) ||
                              (width == 512u && origin == 0x006AB400u);
    if (!route_active || !target_phase) return;

    const uint32_t first = 0x1797B0u, last = 0x179A48u;
    const uint32_t end = dram_addr + len;
    if (dram_addr >= last || end <= first) return;
    const uint32_t overlap_first = dram_addr > first ? dram_addr : first;
    const uint32_t overlap_last = end < last ? end : last;
    uint32_t payload_fnv = 2166136261u, payload_nz = 0u;
    uint32_t post_fnv = 2166136261u, post_nz = 0u;
    for (uint32_t addr = overlap_first; addr < overlap_last; ++addr) {
        const uint8_t source = g_dmem_cur[((dmem_addr + (addr - dram_addr)) & 0xFFFu) ^ 3u];
        payload_fnv = (payload_fnv * 16777619u) ^ source;
        payload_nz += source != 0u;
        const uint8_t stored = rdram[(addr & 0x007FFFFFu) ^ 3u];
        post_fnv = (post_fnv * 16777619u) ^ stored;
        post_nz += stored != 0u;
    }
    static std::mutex mutex;
    static uint32_t rows[2] = {};
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t slot = width == 1024u ? 0u : 1u;
    if (rows[slot] < 512u) {
        const uint32_t mapped_first = dmem_addr + (overlap_first - dram_addr);
        const uint32_t mapped_last = dmem_addr + (overlap_last - dram_addr);
        std::lock_guard<std::mutex> coverage_lock(g_rs64_m5_dmem_coverage_mutex);
        uint32_t segment_first = mapped_first;
        uint64_t segment_sequence = 0;
        while (segment_first < mapped_last && segment_first < 0x1000u) {
            const Rs64M5DmemCoverage& first_coverage =
                g_rs64_m5_dmem_coverage[segment_first];
            segment_sequence = first_coverage.sequence;
            uint32_t segment_last = segment_first + 1u;
            while (segment_last < mapped_last && segment_last < 0x1000u &&
                   g_rs64_m5_dmem_coverage[segment_last].sequence == segment_sequence) {
                ++segment_last;
            }
            std::fprintf(stderr,
                "[m5-dmem-coverage] row=%u phase=%u width=%u origin=0x%06X "
                "route_ordinal=%u source_dram=0x%06X source_len=0x%X "
                "source_fnv=%08X source_nz=%u post_fnv=%08X post_nz=%u "
                "dmem_subrange=0x%03X..0x%03X seq=%llu writer_addr=0x%03X "
                "writer_len=0x%X kind=%s vector_op=0x%08X value=0x%08X writer_fnv=%08X "
                "writer_nz=%u writer_route=%u input_dma_seq=%llu\n",
                rows[slot], phase, width, origin, route_ordinal, dram_addr, len,
                payload_fnv, payload_nz, post_fnv, post_nz, segment_first,
                segment_last, static_cast<unsigned long long>(segment_sequence),
                first_coverage.addr, first_coverage.len,
                first_coverage.kind == 2u ? "dma" :
                    (first_coverage.kind ? "vector" : "scalar"),
                first_coverage.vector_op, first_coverage.value,
                first_coverage.fnv, first_coverage.nonzero,
                first_coverage.route_ordinal,
                static_cast<unsigned long long>(g_rs64_m5_last_input_dmem_writer_seq));
            segment_first = segment_last;
        }
        std::fflush(stderr);
    }
    if (transition_enabled) {
        static uint32_t transition_rows = 0;
        if (transition_rows < 4096u) {
            std::fprintf(stderr,
                "[m5-source-transition] event=%llu op=dma_to_rdram "
                "phase=%u width=%u origin=0x%06X route_ordinal=%u "
                "route_row=%u dram=0x%06X len=0x%X dmem=0x%03X "
                "overlap=0x%06X..0x%06X payload_fnv=%08X payload_nz=%u "
                "post_fnv=%08X post_nz=%u\n",
                static_cast<unsigned long long>(g_rs64_m5_source_event++),
                phase, width, origin, route_ordinal, route_row, dram_addr,
                len, dmem_addr, overlap_first, overlap_last, payload_fnv,
                payload_nz, post_fnv, post_nz);
            std::fflush(stderr);
            ++transition_rows;
        }
    }
    if (rows[slot] >= 512u) return;
    const uint64_t event = g_rs64_m5_source_event++;
    const bool output_window3 = dmem_addr < 0xE48u &&
                                dmem_addr + len > 0xCB0u;
    const uint64_t source_dma_seq = output_window3 ?
        g_rs64_m5_last_source_dma3_seq : g_rs64_m5_last_source_dma_seq;
    const uint32_t source_dma_dram = output_window3 ?
        g_rs64_m5_last_source_dma3_dram : g_rs64_m5_last_source_dma_dram;
    const uint32_t source_dma_len = output_window3 ?
        g_rs64_m5_last_source_dma3_len : g_rs64_m5_last_source_dma_len;
    const uint32_t source_dma_dmem = output_window3 ?
        g_rs64_m5_last_source_dma3_dmem : g_rs64_m5_last_source_dma_dmem;
    const uint32_t source_dma_fnv = output_window3 ?
        g_rs64_m5_last_source_dma3_fnv : g_rs64_m5_last_source_dma_fnv;
    const uint32_t source_dma_nonzero = output_window3 ?
        g_rs64_m5_last_source_dma3_nonzero : g_rs64_m5_last_source_dma_nonzero;
    std::fprintf(stderr,
        "[m5-source-range-writer] event=%llu op=dma_to_rdram row=%u "
        "phase=%u width=%u origin=0x%06X arm=%s route_ordinal=%u "
        "route_row=%u dram=0x%06X len=0x%X dmem=0x%03X overlap=0x%06X..0x%06X "
        "payload_fnv=%08X payload_nz=%u post_fnv=%08X post_nz=%u "
        "prev_dmem_seq=%llu prev_dmem_addr=0x%03X prev_dmem_len=0x%X "
        "prev_dmem_kind=%s prev_dmem_value=0x%08X prev_dmem_fnv=%08X "
        "prev_dmem_nz=%u prev_dmem_vector_op=0x%08X prev_dmem_route_ordinal=%u prev_dmem_overlap=%u "
        "source_dma_seq=%llu source_dma_dram=0x%06X source_dma_len=0x%X "
        "source_dma_dmem=0x%03X source_dma_fnv=%08X source_dma_nz=%u "
        "source_dma_overlap=%u "
        "exit=%d\n",
        static_cast<unsigned long long>(event), rows[slot]++, phase, width,
        origin, arm ? arm : "n/a", route_ordinal, route_row, dram_addr, len,
        dmem_addr, overlap_first, overlap_last, payload_fnv, payload_nz,
        post_fnv, post_nz,
        static_cast<unsigned long long>(g_rs64_m5_last_dmem_writer_seq),
        g_rs64_m5_last_dmem_writer_addr, g_rs64_m5_last_dmem_writer_len,
        g_rs64_m5_last_dmem_writer_kind == 2u ? "dma" :
            (g_rs64_m5_last_dmem_writer_kind ? "vector" : "scalar"),
        g_rs64_m5_last_dmem_writer_value, g_rs64_m5_last_dmem_writer_fnv,
        g_rs64_m5_last_dmem_writer_nonzero,
        g_rs64_m5_last_dmem_writer_vector_op,
        g_rs64_m5_last_dmem_writer_route_ordinal,
        (g_rs64_m5_last_dmem_writer_addr < dmem_addr + len &&
         dmem_addr < g_rs64_m5_last_dmem_writer_addr +
             g_rs64_m5_last_dmem_writer_len) ? 1u : 0u,
        static_cast<unsigned long long>(source_dma_seq), source_dma_dram,
        source_dma_len, source_dma_dmem, source_dma_fnv, source_dma_nonzero,
        (source_dma_dmem < dmem_addr + len &&
         dmem_addr < source_dma_dmem + source_dma_len) ? 1u : 0u,
        exit_reason);
    std::fflush(stderr);
}

extern "C" void rs64_m5_ai_table_row(uint32_t index, uint32_t root,
                                       uint32_t entry, uint32_t is_root) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_AI_TABLE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        std::fprintf(stderr, "[m5-ai-table-control] phase=%u width=%u"
                     " origin=0x%06X\n", rs64_phase_ord(), width, origin);
    }
    if (rows++ >= 64u) return;
    std::fprintf(stderr,
        "[m5-ai-table-row] phase=%u width=%u origin=0x%06X index=%u"
        " root=0x%08X entry=0x%08X is_root=%u expected=0x%08X\n",
        rs64_phase_ord(), width, origin, index, root, entry, is_root,
        root + index * 0x300u);
    std::fflush(stderr);
}

extern "C" void rs64_m5_pcm_writer_snapshot(uint32_t addr,
                                                uint32_t* kind,
                                                uint32_t* pc,
                                                uint32_t* phys,
                                                uint32_t* writes,
                                                uint64_t* sequence,
                                                uint32_t* value) {
    if (kind) *kind = 0;
    if (pc) *pc = 0;
    if (phys) *phys = 0;
    if (writes) *writes = 0;
    if (sequence) *sequence = 0;
    if (value) *value = 0;
    if (!rs64_pcm_writer_enabled()) return;
    const uint32_t target = addr & 0x007FFFFFu;
    if (target < rs64_pcm_ring_first || target >= rs64_pcm_ring_last ||
        ((target - rs64_pcm_ring_first) % rs64_pcm_ring_slot) != 0) return;
    uint32_t phase = 0, width = 0, origin = 0, key = 0;
    if (!rs64_pcm_writer_phase(phase, width, origin, key)) return;
    std::lock_guard<std::mutex> lock(g_rs64_pcm_writer_mutex);
    rs64_pcm_writer_phase_reset(key);
    const uint32_t slot = (target - rs64_pcm_ring_first) / rs64_pcm_ring_slot;
    const Rs64PcmWriterState& state = g_rs64_pcm_writer[slot];
    if (kind) *kind = state.last_kind;
    if (pc) *pc = state.last_pc;
    if (phys) *phys = state.last_phys;
    if (writes) *writes = state.writes;
    if (sequence) *sequence = state.sequence;
    if (value) *value = state.last_value;
}

extern "C" void rs64_m5_field348_set_callsite(uint32_t callsite) {
    g_rs64_m5_field348_static_callsite = callsite;
}

extern "C" void rs64_m5_field348_input(uint32_t slot_addr, uint32_t value,
                                         uint32_t guest_pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_FIELD348_INPUT");
        const char* own = std::getenv("ROGUESQ_LOG_ALL");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static std::mutex mutex;
    static uint32_t rows[2] = {};
    static bool control[2] = {};
    const uint32_t bucket = width == 1024u ? 0u : 1u;
    std::lock_guard<std::mutex> lock(mutex);
    uint32_t route_phase = rs64_phase_ord();
    uint32_t route_width = width;
    uint32_t route_origin = origin;
    uint32_t route_ordinal = 0xFFFFFFFFu;
    uint32_t route_row = 0xFFFFFFFFu;
    int route_exit = 0;
    const char* route_arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &route_phase, &route_width, &route_origin, &route_ordinal,
        &route_row, &route_exit, &route_arm);
    if (!control[bucket]) {
        control[bucket] = true;
        std::fprintf(stderr,
            "[field348-input-control] phase=%u width=%u origin=0x%06X guest_pc=0x%08X "
            "arm=%s ordinal=%u row=%u active=%u exit=%d\n",
            route_phase, route_width, route_origin, guest_pc,
            route_arm ? route_arm : "n/a", route_ordinal, route_row,
            active ? 1u : 0u, route_exit);
        std::fflush(stderr);
    }
    if (rows[bucket] >= 512u) return;
    const uint32_t phys = value & 0x007FFFFFu;
    std::fprintf(stderr,
        "[field348-input] row=%u phase=%u width=%u origin=0x%06X slot=0x%08X "
        "value=0x%08X value_phys=0x%06X guest_pc=0x%08X arm=%s ordinal=%u "
        "route_row=%u active=%u exit=%d\n",
        rows[bucket]++, route_phase, route_width, route_origin, slot_addr, value,
        phys, guest_pc, route_arm ? route_arm : "n/a", route_ordinal,
        route_row, active ? 1u : 0u, route_exit);
    std::fflush(stderr);
}

static bool rs64_filter_voice_guest_span_ok(uint32_t base, uint32_t span) {
    const uint32_t segment = base & 0xE0000000u;
    const uint32_t phys = base & 0x1FFFFFFFu;
    const bool rdram_segment = segment == 0x80000000u || segment == 0xA0000000u;
    return rdram_segment && phys <= 0x800000u && span <= 0x800000u - phys;
}

static uint32_t rs64_filter_voice_guest_hash(uint32_t base, uint32_t span) {
    const uint32_t segment = base & 0xE0000000u;
    const uint32_t phys = base & 0x1FFFFFFFu;
    if (segment != 0x80000000u && segment != 0xA0000000u)
        return 0u;
    if (phys > 0x800000u || span > 0x800000u - phys)
        return 0u;
    const volatile uint8_t* rdram = g_recomp_rdram_for_wp_raw;
    if (!rdram)
        return 0u;
    uint32_t hash = 2166136261u;
    for (uint32_t i = 0; i < span; ++i)
        hash = (hash * 16777619u) ^ rdram[(phys + i) ^ 3u];
    return hash;
}

static uint32_t rs64_filter_voice_guest_word(uint32_t base) {
    const uint32_t segment = base & 0xE0000000u;
    const uint32_t phys = base & 0x1FFFFFFFu;
    if ((segment != 0x80000000u && segment != 0xA0000000u) ||
        phys > 0x7FFFFCu)
        return 0u;
    const volatile uint8_t* rdram = g_recomp_rdram_for_wp_raw;
    if (!rdram)
        return 0u;
    return rs64_rdram_u32(rdram, phys);
}

static const char* rs64_filter_voice_site_name(uint32_t site) {
    switch (site) {
    case 0x8009C540u: return "updateVoiceChannelParams";
    case 0x8009C88Cu: return "decodeAndFillVoiceBlock";
    case 0x8009D740u: return "updateVoiceChannelParamsLarge";
    default: return "unknown";
    }
}

static const char* rs64_filter_voice_range_class(bool source_ok, bool output_ok,
                                                   bool table_used, bool table_ok) {
    static char value[8];
    unsigned n = 0;
    if (!source_ok) value[n++] = 'S';
    if (!output_ok) value[n++] = 'O';
    if (table_used && !table_ok) value[n++] = 'T';
    if (n == 0) value[n++] = 'O';
    value[n] = '\0';
    return value;
}

struct Rs64FilterVoiceCallerObject {
    uint32_t site = 0;
    uint32_t object = 0;
    uint32_t descriptor = 0;
    uint32_t aux0 = 0;
    uint32_t aux1 = 0;
    unsigned long sequence = 0;
    bool valid = false;
};

static Rs64FilterVoiceCallerObject g_rs64_filter_voice_caller;
static unsigned long g_rs64_filter_voice_sequence = 0;

extern "C" void rs64_filter_voice_sequence_probe(const char* edge,
                                                   uint32_t site) {
    static int enabled = -1;
    static unsigned long entry_count = 0;
    static unsigned long caller_count = 0;
    static unsigned long direct_count = 0;
    static uint32_t direct_phase_key = 0;
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_FILTER_VOICE_AUDIT");
        enabled = ((all && *all && *all != '0') ||
                   (own && *own && *own != '0')) ? 1 : 0;
    }
    if (!enabled || site != 0x8009D740u) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (std::strcmp(edge, "entry") == 0) {
        ++g_rs64_filter_voice_sequence;
        ++entry_count;
    } else if (std::strcmp(edge, "caller") == 0) {
        ++caller_count;
    } else if (std::strcmp(edge, "direct") == 0) {
        if (width != 512u || (origin != 0x006AB400u && origin != 0x006AB800u)) return;
        if (origin != direct_phase_key) {
            direct_phase_key = origin;
            direct_count = 0;
        }
        ++direct_count;
    } else {
        return;
    }
    if (std::strcmp(edge, "entry") == 0 && entry_count > 256ul) return;
    if (std::strcmp(edge, "caller") == 0 && caller_count > 256ul) return;
    if (std::strcmp(edge, "direct") == 0 && direct_count > 256ul) return;
    std::fprintf(stderr,
                 "[m5-filter-seq] edge=%s site=0x%08X width=%u origin=0x%06X "
                 "seq=%lu entry_n=%lu caller_n=%lu direct_n=%lu\n",
                 edge, site, width, origin, g_rs64_filter_voice_sequence, entry_count, caller_count,
                 direct_count);
    std::fflush(stderr);
}

static void rs64_filter_voice_audit_row(const char* edge, uint32_t site,
                                        uint32_t sp, uint32_t ra,
                                        uint32_t a0, uint32_t a1,
                                        uint32_t source, uint32_t output) {
    static int enabled = -1;
    static bool control = false;
    static uint32_t phase_key = 0;
    static unsigned long phase_rows = 0;
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* e = std::getenv("ROGUESQ_LOG_FILTER_VOICE_AUDIT");
        enabled = ((all && *all && *all != '0') || (e && *e && *e != '0')) ? 1 : 0;
    }
    if (!enabled) return;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    if (!control) {
        const bool source_ok = rs64_filter_voice_guest_span_ok(0x80000000u, 26u);
        const bool output_ok = rs64_filter_voice_guest_span_ok(0x80000000u, 40u);
        fprintf(stderr,
                "[filter-voice-audit-control] source=0x80000000 source_span=26 source_ok=%u output=0x80000000 output_span=40 output_ok=%u range=OK\n",
                source_ok ? 1u : 0u, output_ok ? 1u : 0u);
        fflush(stderr);
        control = true;
    }
    if (width != 512u || (origin != 0x006AB400u && origin != 0x006AB800u)) return;

    const uint32_t key = origin;
    if (key != phase_key) {
        phase_key = key;
        phase_rows = 0;
    }
    if (phase_rows >= 256) return;

    const int32_t index = static_cast<int32_t>(a0);
    const int32_t selector = static_cast<int32_t>(static_cast<int16_t>(a1 & 0xFFFFu));
    const bool table_used = index <= 7;
    const uint32_t table = table_used ? sp + 0xD4u + a0 : 0u;
    const bool source_ok = rs64_filter_voice_guest_span_ok(source, 26u);
    const bool output_ok = rs64_filter_voice_guest_span_ok(output, 40u);
    const bool table_ok = !table_used || rs64_filter_voice_guest_span_ok(table, 1u);
    const uint32_t phase = rs64_phase_ord();
    uint32_t route_ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    const char* arm = "n/a";
    rs64_audio_current_route_snapshot(nullptr, nullptr, nullptr, &route_ordinal,
                                      &route_row, nullptr, &arm);
    const uint32_t source_hash = rs64_filter_voice_guest_hash(source, 26u);
    const uint32_t output_hash = rs64_filter_voice_guest_hash(output, 40u);
    const uint32_t table_value = table_used ? rs64_filter_voice_guest_word(table) : 0u;
    const uint32_t voice_object = site == 0x8009D740u ?
        rs64_filter_voice_guest_word(sp + 0x114u) : 0u;
    const uint32_t voice_w0 = rs64_filter_voice_guest_word(voice_object + 0x00u);
    const uint32_t voice_w1 = rs64_filter_voice_guest_word(voice_object + 0x04u);
    const uint32_t voice_w2 = rs64_filter_voice_guest_word(voice_object + 0x08u);
    const uint32_t voice_w3 = rs64_filter_voice_guest_word(voice_object + 0x0Cu);
    const uint32_t voice_w4 = rs64_filter_voice_guest_word(voice_object + 0x10u);
    const uint32_t voice_w5 = rs64_filter_voice_guest_word(voice_object + 0x14u);
    const uint32_t voice_w6 = rs64_filter_voice_guest_word(voice_object + 0x18u);
    const uint32_t voice_w7 = rs64_filter_voice_guest_word(voice_object + 0x1Cu);
    const bool caller_join = g_rs64_filter_voice_caller.valid &&
                             g_rs64_filter_voice_caller.site == 0x8009C88Cu;
    const uint32_t caller_object = caller_join ?
        g_rs64_filter_voice_caller.object : 0u;
    const uint32_t caller_descriptor = caller_join ?
        g_rs64_filter_voice_caller.descriptor : 0u;
    const uint32_t caller_aux0 = caller_join ? g_rs64_filter_voice_caller.aux0 : 0u;
    const uint32_t caller_aux1 = caller_join ? g_rs64_filter_voice_caller.aux1 : 0u;
    const uint32_t descriptor_w0 = rs64_filter_voice_guest_word(caller_descriptor);
    const uint32_t descriptor_w1 = rs64_filter_voice_guest_word(caller_descriptor + 4u);
    const uint32_t descriptor_w2 = rs64_filter_voice_guest_word(caller_descriptor + 8u);
    const uint32_t descriptor_type = (descriptor_w0 >> 28) & 0xFu;
    const uint32_t descriptor_class = (descriptor_w1 >> 24) & 0x3Fu;
    const uint32_t descriptor_source = caller_join ? caller_aux1 : 0u;
    fprintf(stderr,
            "[m5-filter-join] edge=%s site=0x%08X arm=%s phase=%u width=%u origin=0x%06X "
            "route_ordinal=%u route_row=%u rate=%u a0=%d a1=%d a2=0x%08X a3=0x%08X "
            "source=0x%08X source_hash=0x%08X output=0x%08X output_hash=0x%08X "
            "table=0x%08X table_value=0x%08X voice_object=0x%08X "
            "voice_w0=0x%08X voice_w1=0x%08X voice_w2=0x%08X voice_w3=0x%08X "
            "voice_w4=0x%08X voice_w5=0x%08X voice_w6=0x%08X voice_w7=0x%08X "
            "source_delta=%d caller_join=%u caller_object=0x%08X caller_descriptor=0x%08X "
            "caller_aux0=0x%08X caller_aux1=0x%08X descriptor_w0=0x%08X "
            "descriptor_w1=0x%08X descriptor_w2=0x%08X descriptor_type=%u "
            "descriptor_class=%u descriptor_source=0x%08X\n",
            edge, site, arm ? arm : "n/a", phase, width, origin, route_ordinal,
            route_row, rs64_audio_rate_snapshot(), index, selector, source, output,
            source, source_hash, output, output_hash, table, table_value,
            voice_object, voice_w0, voice_w1, voice_w2, voice_w3, voice_w4,
            voice_w5, voice_w6, voice_w7,
            static_cast<int32_t>(source - voice_object), caller_join ? 1u : 0u,
            caller_object, caller_descriptor, caller_aux0, caller_aux1,
            descriptor_w0, descriptor_w1, descriptor_w2, descriptor_type,
            descriptor_class, descriptor_source);
    fflush(stderr);
    fprintf(stderr,
            "[filter-voice-audit] edge=%s site=0x%08X caller=%s phase=%u width=%u origin=0x%06X row=%lu sp=0x%08X ra=0x%08X a0=%d a1=%d source=0x%08X source_span=26 output=0x%08X output_span=40 table_used=%u table=0x%08X table_span=1 source_ok=%u output_ok=%u table_ok=%u source_delta=%d output_delta=%d range=%s\n",
            edge, site, rs64_filter_voice_site_name(site), phase, width, origin,
            phase_rows, sp, ra, index, selector, source, output, table_used ? 1u : 0u,
            table, source_ok ? 1u : 0u, output_ok ? 1u : 0u, table_ok ? 1u : 0u,
            static_cast<int32_t>(source - sp), static_cast<int32_t>(output - sp),
            rs64_filter_voice_range_class(source_ok, output_ok, table_used, table_ok));
    fflush(stderr);
    ++phase_rows;
}

static void rs64_filter_voice_audit_positive_control() {
    static int enabled = -1;
    static bool emitted = false;
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* e = std::getenv("ROGUESQ_LOG_FILTER_VOICE_AUDIT");
        enabled = ((all && *all && *all != '0') || (e && *e && *e != '0')) ? 1 : 0;
    }
    if (!enabled || emitted) return;
    emitted = true;
    const bool source_ok = rs64_filter_voice_guest_span_ok(0x80000000u, 26u);
    const bool output_ok = rs64_filter_voice_guest_span_ok(0x80000000u, 40u);
    std::fprintf(stderr,
                 "[filter-voice-audit-control] kind=host-positive-control"
                 " source=0x80000000 source_span=26 source_ok=%u"
                 " output=0x80000000 output_span=40 output_ok=%u range=OK\n",
                 source_ok ? 1u : 0u, output_ok ? 1u : 0u);
    std::fflush(stderr);
}

extern "C" void rs64_filter_voice_caller_probe(const char* caller,
                                                 uint32_t site, uint32_t a0,
                                                 uint32_t a1, uint32_t a2,
                                                 uint32_t a3) {
    static int enabled = -1;
    static uint32_t rows[3] = {};
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_FILTER_VOICE_AUDIT");
        enabled = ((all && *all && *all != '0') ||
                   (own && *own && *own != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    if (site == 0x8009C88Cu) {
        g_rs64_filter_voice_caller.site = site;
        g_rs64_filter_voice_caller.object = a0;
        g_rs64_filter_voice_caller.descriptor = a1;
        g_rs64_filter_voice_caller.aux0 = a2;
        g_rs64_filter_voice_caller.aux1 = a3;
        g_rs64_filter_voice_caller.sequence = g_rs64_filter_voice_sequence;
        g_rs64_filter_voice_caller.valid = true;
    }
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 512u || (origin != 0x006AB400u && origin != 0x006AB800u)) return;
    unsigned bucket = site == 0x8009C540u ? 0u :
                      (site == 0x8009C88Cu ? 1u : 2u);
    if (rows[bucket] >= 128u) return;
    uint32_t phase = 0, route_width = 0, route_origin = 0, ordinal = 0xFFFFFFFFu,
             route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &phase, &route_width, &route_origin, &ordinal, &route_row,
        &exit_reason, &arm);
    std::fprintf(stderr,
        "[filter-voice-caller] caller=%s site=0x%08X row=%u phase=%u width=%u "
        "origin=0x%06X arm=%s active=%u ordinal=%u route_row=%u exit=%d "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X\n",
        caller, site, rows[bucket]++, phase, width, origin,
        arm ? arm : "n/a", active ? 1u : 0u, ordinal, route_row,
        exit_reason, a0, a1, a2, a3);
    std::fflush(stderr);
}

static bool rs64_filter_voice_guest_pointer(uint32_t value) {
    const uint32_t segment = value & 0xE0000000u;
    const uint32_t phys = value & 0x1FFFFFFFu;
    return (segment == 0x80000000u || segment == 0xA0000000u) && phys <= 0x7FFFF4u;
}

extern "C" void rs64_filter_voice_c88c_descriptor_probe(uint32_t a0,
                                                          uint32_t a1,
                                                          uint32_t a2,
                                                          uint32_t a3) {
    static int enabled = -1;
    static unsigned rows = 0;
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_FILTER_VOICE_AUDIT");
        enabled = ((all && *all && *all != '0') ||
                   (own && *own && *own != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 512u || (origin != 0x006AB400u && origin != 0x006AB800u) || rows >= 256u)
        return;
    const uint32_t args[4] = {a0, a1, a2, a3};
    std::fprintf(stderr, "[m5-c88c-desc] seq=%lu row=%u phase=%u origin=0x%06X",
                 g_rs64_filter_voice_sequence, rows++, rs64_phase_ord(), origin);
    for (unsigned i = 0; i < 4; ++i) {
        const uint32_t base = args[i];
        std::fprintf(stderr, " a%u=0x%08X valid=%u", i, base,
                     rs64_filter_voice_guest_pointer(base) ? 1u : 0u);
        if (rs64_filter_voice_guest_pointer(base)) {
            std::fprintf(stderr, " w0=0x%08X w1=0x%08X w2=0x%08X",
                         rs64_filter_voice_guest_word(base),
                         rs64_filter_voice_guest_word(base + 4u),
                         rs64_filter_voice_guest_word(base + 8u));
        }
    }
    std::fprintf(stderr, "\n");
    std::fflush(stderr);
}

extern "C" void rs64_filter_voice_c88c_field_probe(uint8_t* rdram,
                                                     uint32_t s0,
                                                     uint32_t s1,
                                                     uint32_t branch_selector) {
    static int enabled = -1;
    static unsigned rows = 0;
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_FILTER_VOICE_AUDIT");
        enabled = ((all && *all && *all != '0') ||
                   (own && *own && *own != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 512u || (origin != 0x006AB400u && origin != 0x006AB800u) ||
        rows >= 256u) return;
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (!rdram) return 0xFFFFFFFFu;
        const uint32_t segment = guest & 0xE0000000u;
        const uint32_t phys = (segment == 0x80000000u || segment == 0xA0000000u)
            ? (guest & 0x1FFFFFFFu) : guest;
        if (phys > 0x7FFFF8u) return 0xFFFFFFFFu;
        return rs64_rdram_u32(rdram, phys);
    };
    auto byte = [rdram](uint32_t guest) -> uint32_t {
        if (!rdram) return 0xFFFFFFFFu;
        const uint32_t segment = guest & 0xE0000000u;
        const uint32_t phys = (segment == 0x80000000u || segment == 0xA0000000u)
            ? (guest & 0x1FFFFFFFu) : guest;
        if (phys >= 0x800000u) return 0xFFFFFFFFu;
        return rdram[phys ^ 3u];
    };
    auto half = [rdram](uint32_t guest) -> uint32_t {
        if (!rdram) return 0xFFFFFFFFu;
        const uint32_t segment = guest & 0xE0000000u;
        const uint32_t phys = (segment == 0x80000000u || segment == 0xA0000000u)
            ? (guest & 0x1FFFFFFFu) : guest;
        const uint32_t aligned = phys & ~3u;
        if (aligned + 3u >= 0x800000u) return 0xFFFFFFFFu;
        const uint32_t value = rs64_rdram_u32(rdram, aligned);
        return (value >> ((phys & 2u) ? 0u : 16u)) & 0xFFFFu;
    };
    std::fprintf(stderr,
        "[m5-c88c-fields] seq=%lu row=%u phase=%u origin=0x%06X "
        "s0=0x%08X s1=0x%08X source_word=0x%08X source_byte=0x%02X "
        "branch_selector=0x%08X branch_state=0x%04X\n",
        g_rs64_filter_voice_sequence, rows++, rs64_phase_ord(), origin, s0, s1,
        word(s0 + 0x60u), byte(s0 + 0x22u), branch_selector,
        half(s1 + 0x22u));
    std::fflush(stderr);
}

extern "C" void rs64_filter_voice_c88c_branch_probe(uint8_t* rdram,
                                                       uint32_t object,
                                                       uint32_t cursor,
                                                       uint32_t table_addr,
                                                       uint32_t table_word,
                                                       uint32_t a0,
                                                       uint32_t a1,
                                                       uint32_t stack_ptr) {
    static int enabled = -1;
    static unsigned rows = 0;
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_FILTER_VOICE_AUDIT");
        enabled = ((all && *all && *all != '0') ||
                   (own && *own && *own != '0')) ? 1 : 0;
    }
    static bool entry_control = false;
    if (enabled && !entry_control) {
        entry_control = true;
        std::fprintf(stderr, "[m5-c88c-branch-control] helper entered\n");
        std::fflush(stderr);
    }
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 512u || (origin != 0x006AB400u && origin != 0x006AB800u) ||
        rows >= 256u) return;
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (!rdram) return 0xFFFFFFFFu;
        const uint32_t segment = guest & 0xE0000000u;
        const uint32_t phys = (segment == 0x80000000u || segment == 0xA0000000u)
            ? (guest & 0x1FFFFFFFu) : guest;
        if (phys > 0x7FFFFCu) return 0xFFFFFFFFu;
        return rs64_rdram_u32(rdram, phys);
    };
    std::fprintf(stderr,
        "[m5-c88c-branch] seq=%lu row=%u phase=%u origin=0x%06X "
        "object=0x%08X cursor=0x%08X table_addr=0x%08X table_word=0x%08X "
        "a0=0x%08X a1=0x%08X stack_ptr=0x%08X stack_w0=0x%08X stack_w1=0x%08X\n",
        g_rs64_filter_voice_sequence, rows++, rs64_phase_ord(), origin,
        object, cursor, table_addr, table_word, a0, a1, stack_ptr,
        word(stack_ptr), word(stack_ptr + 4u));
    std::fflush(stderr);
}

extern "C" void rs64_filter_voice_call_probe(uint32_t site, uint32_t sp,
                                               uint32_t ra, uint32_t a0,
                                               uint32_t a1, uint32_t a2,
                                               uint32_t a3) {
    rs64_filter_voice_audit_row("call", site, sp, ra, a0, a1, a2, a3);
}

extern "C" void rs64_filter_voice_direct_probe(uint32_t site, uint32_t sp,
                                                  uint32_t ra, uint32_t a0,
                                                  uint32_t a1, uint32_t a2,
                                                  uint32_t a3) {
    static int enabled = -1;
    static uint32_t phase_key = 0;
    static unsigned long d740_store_n = 0;
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_FILTER_VOICE_AUDIT");
        enabled = ((all && *all && *all != '0') ||
                   (own && *own && *own != '0')) ? 1 : 0;
    }
    if (!enabled || site != 0x8009D740u) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 512u || (origin != 0x006AB400u && origin != 0x006AB800u)) return;
    if (origin != phase_key) {
        phase_key = origin;
        d740_store_n = 0;
    }
    rs64_filter_voice_sequence_probe("direct", site);
    ++d740_store_n;
    if (d740_store_n > 256ul) return;
    const uint32_t object = g_rs64_filter_voice_caller.valid ?
        g_rs64_filter_voice_caller.object : 0u;
    const uint32_t cursor = rs64_filter_voice_guest_word(object + 0x11C8u);
    const uint32_t table_addr = object + 0x1A0u +
        ((static_cast<int32_t>(cursor) >> 3) & 0xFFCu);
    const uint32_t table_word = rs64_filter_voice_guest_word(table_addr);
    std::fprintf(stderr,
                 "[m5-filter-direct] site=0x%08X phase=%u origin=0x%06X "
                 "d740_store_n=%lu sp=0x%08X ra=0x%08X "
                 "actual_a0=0x%08X actual_a1=0x%08X actual_a2=0x%08X actual_a3=0x%08X "
                 "branch_object=0x%08X branch_cursor=0x%08X branch_table=0x%08X "
                 "branch_table_word=0x%08X branch_stack_ptr=0x%08X "
                 "caller_sequence=%lu "
                 "caller_join=%u caller_object=0x%08X caller_descriptor=0x%08X "
                 "caller_aux0=0x%08X caller_aux1=0x%08X\n",
                 site, rs64_phase_ord(), origin, d740_store_n, sp, ra,
                 a0, a1, a2, a3,
                 object, cursor, table_addr, table_word, sp,
                 g_rs64_filter_voice_caller.sequence,
                 (g_rs64_filter_voice_caller.valid &&
                  g_rs64_filter_voice_caller.site == 0x8009C88Cu) ? 1u : 0u,
                 g_rs64_filter_voice_caller.object,
                 g_rs64_filter_voice_caller.descriptor,
                 g_rs64_filter_voice_caller.aux0,
                 g_rs64_filter_voice_caller.aux1);
    std::fflush(stderr);
}

extern "C" void rs64_filter_voice_entry_probe(uint32_t sp, uint32_t ra,
                                                uint32_t a0, uint32_t a1,
                                                uint32_t a2, uint32_t a3) {
    rs64_filter_voice_audit_row("entry", 0u, sp, ra, a0, a1, a2, a3);
}

extern "C" void rs64_probe_dma_write_origin(uint32_t dram_addr, uint32_t len,
                                               uint32_t dmem_addr) {
    static std::atomic<uint64_t> all_dma{0};
    static std::atomic<uint64_t> target_dma{0};
    static std::atomic<uint32_t> last_phase{0xFFFFFFFFu};
    const uint32_t phase = rs64_phase_ord();
    const uint64_t all = all_dma.fetch_add(1, std::memory_order_relaxed) + 1;
    if (phase != 4 && phase != 6) return;
    static std::atomic<uint64_t> phase_dma{0};
    const uint64_t phase_n = phase_dma.fetch_add(1, std::memory_order_relaxed) + 1;
    const uint32_t old_phase = last_phase.exchange(phase, std::memory_order_relaxed);
    if (old_phase != phase || phase_n <= 8) {
        fprintf(stderr, "[shade-dma-control] phase=%u n=%llu all=%llu dram=0x%06X..0x%06X dmem=0x%03X\n",
                phase, (unsigned long long)phase_n, (unsigned long long)all,
                dram_addr, dram_addr + len, dmem_addr);
        fflush(stderr);
    }
    const uint32_t lo = (phase == 6) ? 0x732A10u : 0x726200u;
    const uint32_t hi = (phase == 6) ? 0x73E3B0u : 0x726C50u;
    const uint32_t end = dram_addr + len;
    if (end <= lo || dram_addr >= hi) return;
    const uint32_t hit_lo = dram_addr > lo ? dram_addr : lo;
    const uint32_t hit_hi = end < hi ? end : hi;
    const uint64_t hit = target_dma.fetch_add(1, std::memory_order_relaxed) + 1;
    if (hit <= 32) {
        fprintf(stderr, "[shade-dma] phase=%u all=%llu hit=%llu dram=0x%06X..0x%06X "
                       "overlap=0x%06X..0x%06X dmem=0x%03X\n",
                phase, (unsigned long long)all, (unsigned long long)hit,
                dram_addr, end, hit_lo, hit_hi, dmem_addr);
        fflush(stderr);
    }
}

// s586 H7 writer discrimination: LLE task depth + serial for the FS_SLOT
// poller / task-boundary snapshots. depth>0 ⇒ mutation during RSP LLE;
// depth==0 + intertask_delta ⇒ guest/DMA window between tasks.
static std::atomic<int> g_rs64_lle_depth{0};
static std::atomic<uint32_t> g_rs64_lle_task_n{0};
extern uint32_t g_rsp_dpc_start;
extern uint32_t g_rsp_dpc_end;

#if defined(__APPLE__) && defined(__aarch64__)
// s480 (item -310 tooling fix): local (non-exported) symbol table for
// crash-pc resolution. dladdr() (used in the pc-symbol crash-handler block
// below) only resolves EXPORTED (Mach-O "T") symbols; item -310 root-caused
// a recurring misattribution to this exact gap -- `nm -n` on our own binary
// confirms local ("t")-type function symbols ARE present with real names and
// unstripped (e.g. `do_lwl`/`do_lwr`/`do_swl`/`do_swr` sit in the 40KB
// unexported gap right after `heapFreeListDequeue` that item -310 found), so
// a self-built sorted table covering BOTH "T" and "t" symbols, searched by
// nearest-preceding-address, closes the blind spot dladdr can't see past.
// Built ONCE at startup (main(), well before any signal handler installs) by
// shelling out to nm -- safe there since none of this runs in a signal
// context. The crash handler only ever does a binary search over the
// already-built in-memory vector: no malloc, no subprocess, no I/O at signal
// time, which is actually SAFER than the dladdr() fallback it supplements.
struct RS64LocalSymbol { uint64_t addr; std::string name; };
static std::vector<RS64LocalSymbol> g_rs64_local_symtab;

static void rs64_build_local_symbol_table() {
    char exe_path[4096];
    uint32_t sz = sizeof(exe_path);
    if (_NSGetExecutablePath(exe_path, &sz) != 0) {
        fprintf(stderr, "[symtab] _NSGetExecutablePath failed (path too long)\n");
        return;
    }
    // nm reports link-time (unslid) addresses; add the ASLR slide once here
    // so the crash handler's lookup is a plain compare against the live pc,
    // no arithmetic needed at signal time.
    intptr_t slide = _dyld_get_image_vmaddr_slide(0);

    char cmd[4096];
    snprintf(cmd, sizeof(cmd), "nm -n '%s' 2>/dev/null", exe_path);
    FILE* p = popen(cmd, "r");
    if (!p) {
        fprintf(stderr, "[symtab] popen(nm) failed: %s\n", strerror(errno));
        return;
    }
    char line[1024];
    while (fgets(line, sizeof(line), p)) {
        unsigned long long addr;
        char type;
        char name[900];
        // Lines look like "0000000100486000 t _do_lwl". Undefined ("U")
        // symbols omit the address column, so sscanf's match count below
        // naturally skips them.
        if (sscanf(line, "%llx %c %899s", &addr, &type, name) != 3) continue;
        if (type != 't' && type != 'T') continue;  // code symbols only
        const char* n = name;
        if (n[0] == '_') n++;  // match dladdr()'s dli_sname convention
        g_rs64_local_symtab.push_back({(uint64_t)addr + (uint64_t)slide, n});
    }
    pclose(p);
    // Already sorted (nm -n), but sort defensively -- the binary-search
    // precondition below must never depend on nm's output order unchecked.
    std::sort(g_rs64_local_symtab.begin(), g_rs64_local_symtab.end(),
        [](const RS64LocalSymbol& a, const RS64LocalSymbol& b) { return a.addr < b.addr; });
    fprintf(stderr, "[symtab] loaded %zu code symbols (T+t) from nm -n\n",
        g_rs64_local_symtab.size());
}

// Nearest-preceding-symbol lookup. Safe to call from the signal handler --
// std::upper_bound over an already-built vector, no allocation.
static const RS64LocalSymbol* rs64_lookup_local_symbol(uint64_t pc) {
    if (g_rs64_local_symtab.empty()) return nullptr;
    auto it = std::upper_bound(g_rs64_local_symtab.begin(), g_rs64_local_symtab.end(), pc,
        [](uint64_t v, const RS64LocalSymbol& s) { return v < s.addr; });
    if (it == g_rs64_local_symtab.begin()) return nullptr;
    --it;
    return &*it;
}
#endif // __APPLE__ && __aarch64__

// Cached for the next ucode invocation. get_rsp_microcode is called with the
// OSTask immediately before the ucode runs on the same thread.
extern "C" uint32_t rs64_m5_pcm_task_data_ptr() {
    return g_rs64_pcm_task_data_ptr.load(std::memory_order_relaxed);
}

extern "C" void rs64_m5_pcm_task_data_set(uint32_t data_ptr) {
    g_rs64_pcm_task_data_ptr.store(data_ptr, std::memory_order_relaxed);
}

extern "C" void rs64_set_pending_task_guest_ptr(uint32_t guest_ptr) {
    s_pending_task_guest_ptr.store(guest_ptr, std::memory_order_release);
}

// Rogue Squadron uses Factor5's MusyX audio ucode, NOT stock aspMain. Running
// aspMain on MusyX-formatted task data produces garbage or hangs the audio
// thread (no shared format). The Factor 5 image is the default arm; the stub
// remains available through ROGUESQ_AUDIO_UCODE=0.
static RspExitReason musyx_stub(uint8_t* /*rdram*/, uint32_t /*ucode_addr*/) {
    return RspExitReason::Broke;
}

struct Rs64AudioRouteIdentity {
    bool valid = false;
    const char* arm = "n/a";
    uint32_t phase = 0;
    uint32_t width = 0;
    uint32_t origin = 0;
    uint32_t ordinal = 0;
    uint32_t row = 0;
    uint32_t prepare_seq = 0xFFFFFFFFu;
};

static thread_local Rs64AudioRouteIdentity g_rs64_audio_identity;
static std::atomic<uint32_t> g_rs64_audio_ordinal{0};
static uint32_t g_rs64_audio_phase_key = 0xFFFFFFFFu;
static uint32_t g_rs64_audio_phase_row = 0;
static std::atomic<uint32_t> g_rs64_audio_prepare_seq{0};
static thread_local uint32_t g_rs64_audio_last_prepare_seq = 0xFFFFFFFFu;
static thread_local uint32_t g_rs64_audio_last_prepare_accepted = 0;
static std::atomic<uint32_t> g_rs64_audio_identity_edge_seq{0};
static std::atomic<uint32_t> g_rs64_audio_identity_thread_seq{1};
static thread_local uint32_t g_rs64_audio_identity_thread_id = 0;
static thread_local uint32_t g_rs64_audio_break_pc = 0;
static thread_local uint32_t g_rs64_m5_init_voice_caller_pc = 0;
static thread_local uint64_t g_rs64_m5_init_voice_event = 0;
static std::atomic<uint64_t> g_rs64_m5_init_voice_next_event{1};

static bool rs64_m5_identity_edge_enabled() {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_M5_IDENTITY_EDGES");
        return own && own[0] && own[0] != '0';
    }();
    return enabled;
}

static uint32_t rs64_m5_identity_thread_id() {
    if (g_rs64_audio_identity_thread_id == 0) {
        g_rs64_audio_identity_thread_id =
            g_rs64_audio_identity_thread_seq.fetch_add(1, std::memory_order_relaxed);
    }
    return g_rs64_audio_identity_thread_id;
}

static void rs64_m5_identity_edge(const char* edge,
                                  const Rs64AudioRouteIdentity& route,
                                  uint32_t prepare_seq, uint32_t clear_seq,
                                  uint32_t phase, uint32_t width,
                                  uint32_t origin) {
    if (!rs64_m5_identity_edge_enabled()) return;
    static std::atomic<bool> control_emitted{false};
    bool expected = false;
    if (control_emitted.compare_exchange_strong(expected, true)) {
        std::fprintf(stderr,
            "[m5-identity-control] enabled=1 thread=%u phase=%u width=%u origin=0x%06X\n",
            rs64_m5_identity_thread_id(), phase, width, origin & 0x00FFFFFFu);
        std::fflush(stderr);
    }
    origin &= 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    if (!target && !route.valid) return;
    static std::atomic<uint32_t> emitted{0};
    const uint32_t n = emitted.fetch_add(1, std::memory_order_relaxed);
    if (n >= 4096u) return;
    std::fprintf(stderr,
        "[m5-identity-edge] n=%u edge=%s thread=%u clear_seq=%u "
        "prepare_seq=%u valid=%u route_prepare=%u route_ordinal=%u "
        "route_row=%u route_phase=%u route_width=%u route_origin=0x%06X "
        "phase=%u width=%u origin=0x%06X\n",
        n, edge ? edge : "?", rs64_m5_identity_thread_id(), clear_seq,
        prepare_seq, route.valid ? 1u : 0u, route.prepare_seq,
        route.ordinal, route.row, route.phase, route.width, route.origin,
        phase, width, origin);
    std::fflush(stderr);
}

extern "C" void rs64_audio_image_break(uint32_t pc) {
    g_rs64_audio_break_pc = pc;
}

extern "C" uint32_t rs64_audio_image_break_pc() {
    return g_rs64_audio_break_pc;
}

static bool rs64_m5_init_voice_probe_enabled() {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_INIT_VOICE_SAMPLE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    return enabled;
}

static bool rs64_m5_init_voice_target_phase(uint32_t width, uint32_t origin) {
    return (width == 1024u && origin == 0x00790400u) ||
           (width == 512u && origin == 0x006AB400u);
}

extern "C" void rs64_m5_init_voice_probe_control() {
    if (!rs64_m5_init_voice_probe_enabled()) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;
    static std::atomic<uint32_t> emitted_key{0xFFFFFFFFu};
    const uint32_t key = (width << 24) ^ origin;
    if (emitted_key.exchange(key, std::memory_order_relaxed) == key) return;
    std::fprintf(stderr,
                 "[init-voice-sample-control] kind=host-positive-control"
                 " phase=%u width=%u origin=0x%06X\n",
                 rs64_phase_ord(), width, origin);
    std::fflush(stderr);
}

extern "C" void rs64_m5_init_voice_callsite(uint32_t caller_pc) {
    g_rs64_m5_init_voice_caller_pc = caller_pc;
    g_rs64_m5_init_voice_event = 0;
    if (!rs64_m5_init_voice_probe_enabled()) return;

    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;

    uint32_t route_phase = phase;
    uint32_t route_width = width;
    uint32_t route_origin = origin;
    uint32_t ordinal = 0xFFFFFFFFu;
    uint32_t row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &route_phase, &route_width, &route_origin, &ordinal, &row,
        &exit_reason, &arm);
    const uint64_t event = g_rs64_m5_init_voice_next_event.fetch_add(
        1, std::memory_order_relaxed);
    g_rs64_m5_init_voice_event = event;
    std::fprintf(stderr,
                 "[init-voice-callsite] event=%llu caller_pc=0x%08X"
                 " prev_pc=0x%08X phase=%u width=%u origin=0x%06X"
                 " active=%u arm=%s ordinal=%u row=%u\n",
                 static_cast<unsigned long long>(event), caller_pc, caller_pc,
                 active ? route_phase : phase, active ? route_width : width,
                 active ? route_origin : origin, active ? 1u : 0u,
                 active && arm ? arm : "n/a", ordinal, row);
    std::fflush(stderr);
}

extern "C" void rs64_m5_init_voice_caller_event(uint32_t caller_pc,
                                                   uint32_t edge_kind) {
    if (!rs64_m5_init_voice_probe_enabled()) return;

    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;

    uint32_t route_phase = phase;
    uint32_t route_width = width;
    uint32_t route_origin = origin;
    uint32_t ordinal = 0xFFFFFFFFu;
    uint32_t row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &route_phase, &route_width, &route_origin, &ordinal, &row,
        &exit_reason, &arm);
    const uint64_t event = g_rs64_m5_init_voice_next_event.fetch_add(
        1, std::memory_order_relaxed);
    std::fprintf(stderr,
                 "[init-voice-caller] event=%llu edge=%s caller=0x%08X"
                 " phase=%u width=%u origin=0x%06X active=%u arm=%s"
                 " ordinal=%u row=%u\n",
                 static_cast<unsigned long long>(event),
                 edge_kind == 0u ? "entry" : "pre-call", caller_pc,
                 active ? route_phase : phase, active ? route_width : width,
                 active ? route_origin : origin, active ? 1u : 0u,
                 active && arm ? arm : "n/a", ordinal, row);
    std::fflush(stderr);
}

extern "C" void rs64_m5_init_mixer_args(uint32_t edge, uint32_t ra,
                                           uint32_t a0, uint32_t a1,
                                           uint32_t a2, uint32_t a3) {
    if (!rs64_m5_init_voice_probe_enabled()) return;

    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;

    static std::atomic<uint32_t> emitted{0};
    const uint32_t n = emitted.fetch_add(1, std::memory_order_relaxed);
    if (n >= 256u) return;
    std::fprintf(stderr,
                 "[m5-init-mixer-args] n=%u edge=%s phase=%u width=%u"
                 " origin=0x%06X ra=0x%08X a0=0x%08X a1=0x%08X"
                 " a2=0x%08X a3=0x%08X\n",
                 n, edge == 0u ? "entry" : "pre-allocate", phase, width,
                 origin, ra, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_init_mixer_callsite(uint32_t caller_pc,
                                                uint32_t a0, uint32_t a1,
                                                uint32_t a2, uint32_t a3) {
    if (!rs64_m5_init_voice_probe_enabled()) return;

    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;

    static std::atomic<uint32_t> emitted{0};
    const uint32_t n = emitted.fetch_add(1, std::memory_order_relaxed);
    if (n >= 256u) return;
    std::fprintf(stderr,
                 "[m5-init-mixer-callsite] n=%u caller=0x%08X phase=%u"
                 " width=%u origin=0x%06X a0=0x%08X a1=0x%08X"
                 " a2=0x%08X a3=0x%08X\n",
                 n, caller_pc, phase, width, origin, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_setup_state_args(const char* edge, uint32_t ra,
                                             uint32_t a0, uint32_t a1,
                                             uint32_t a2, uint32_t a3) {
    if (!rs64_m5_init_voice_probe_enabled()) return;

    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;

    static std::atomic<uint32_t> emitted{0};
    const uint32_t n = emitted.fetch_add(1, std::memory_order_relaxed);
    if (n >= 256u) return;
    std::fprintf(stderr,
                 "[m5-setup-state-args] n=%u edge=%s phase=%u width=%u"
                 " origin=0x%06X ra=0x%08X a0=0x%08X a1=0x%08X"
                 " a2=0x%08X a3=0x%08X\n",
                 n, edge, phase, width, origin, ra, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_reapply_boundary(const char* edge, uint32_t ra,
                                           uint32_t a0, uint32_t a1,
                                           uint32_t a2, uint32_t a3,
                                           uint32_t s1, uint32_t s2,
                                           uint32_t s3, uint32_t v0) {
    if (!rs64_m5_init_voice_probe_enabled()) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;
    static std::atomic<uint32_t> emitted{0};
    const uint32_t n = emitted.fetch_add(1, std::memory_order_relaxed);
    if (n >= 256u) return;
    std::fprintf(stderr,
                 "[m5-reapply-boundary] n=%u edge=%s phase=%u width=%u"
                 " origin=0x%06X ra=0x%08X a0=0x%08X a1=0x%08X"
                 " a2=0x%08X a3=0x%08X s1=0x%08X s2=0x%08X"
                 " s3=0x%08X v0=0x%08X\n",
                 n, edge, rs64_phase_ord(), width, origin, ra, a0, a1,
                 a2, a3, s1, s2, s3, v0);
    std::fflush(stderr);
}

static std::atomic<uint32_t> g_rs64_m5_b40_writer_seq{0};

extern "C" uint32_t rs64_m5_b40_writer_event(uint32_t pc,
                                                uint32_t old_value,
                                                uint32_t requested_value,
                                                uint32_t stored_value,
                                                uint32_t ra) {
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = rs64_m5_init_voice_target_phase(width, origin);
    if (!target) return g_rs64_m5_b40_writer_seq.load(std::memory_order_relaxed);

    const uint32_t seq = g_rs64_m5_b40_writer_seq.fetch_add(
        1u, std::memory_order_relaxed) + 1u;
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_B40_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return seq;

    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t row = 0;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (rs64_phase_ord() << 24) ^ (width << 16) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        row = 0;
    }
    if (row < 64u) {
        std::fprintf(stderr,
            "[m5-b40-writer] seq=%u row=%u phase=%u width=%u origin=0x%06X"
            " pc=0x%08X old=0x%02X requested=0x%02X stored=0x%02X ra=0x%08X\n",
            seq, row, rs64_phase_ord(), width, origin, pc,
            old_value & 0xFFu, requested_value & 0xFFu,
            stored_value & 0xFFu, ra);
        std::fflush(stderr);
        ++row;
    }
    return seq;
}

extern "C" uint32_t rs64_m5_b40_writer_sequence() {
    return g_rs64_m5_b40_writer_seq.load(std::memory_order_relaxed);
}

extern "C" void rs64_m5_audio_sequencer_event(uint32_t source,
                                                 uint32_t edge_kind,
                                                 uint32_t target,
                                                 uint32_t guest_ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_AUDIOTICK_TRACE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;

    uint32_t slot = 0xFFFFFFFFu;
    switch (source) {
    case 0x8008D960u: slot = 0; break;
    case 0x800914A4u: slot = 1; break;
    case 0x80091564u: slot = 2; break;
    case 0x80091618u: slot = 3; break;
    case 0x80019B74u: slot = 4; break;
    default: return;
    }

    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t event_count[5] = {};
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        for (uint32_t& count : event_count) count = 0;
    }
    const uint32_t event = event_count[slot]++;
    if (event >= 64u && (event % 256u) != 0u) return;

    uint32_t phase = rs64_phase_ord();
    uint32_t route_width = width;
    uint32_t route_origin = origin;
    uint32_t ordinal = 0xFFFFFFFFu;
    uint32_t row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &phase, &route_width, &route_origin, &ordinal, &row,
        &exit_reason, &arm);
    if (!active) {
        phase = rs64_phase_ord();
        route_width = width;
        route_origin = origin;
        arm = "n/a";
    }
    std::fprintf(stderr,
        "[m5-audio-seq] event=%u source=0x%08X edge=%s callsite=0x%08X"
        " target=0x%08X phase=%u width=%u origin=0x%06X active=%u arm=%s"
        " ordinal=%u row=%u ra=0x%08X\n",
        event, source, edge_kind == 0u ? "entry" :
            (edge_kind == 2u ? "control" : "callsite"), source,
        target, phase, route_width, route_origin, active ? 1u : 0u,
        active && arm ? arm : "n/a", ordinal, row, guest_ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_synth_parent_gate_event(uint32_t source,
                                                   uint32_t edge_kind,
                                                   uint32_t gate,
                                                   uint32_t callsite,
                                                   uint32_t branch_taken,
                                                   uint32_t countdown,
                                                   uint32_t period,
                                                   uint32_t guest_ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_AUDIOTICK_TRACE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;

    uint32_t slot = 0xFFFFFFFFu;
    switch (source) {
    case 0x8009123Cu: slot = 0; break;
    case 0x80091484u: slot = 1; break;
    case 0x80091544u: slot = 2; break;
    case 0x800915F8u: slot = 3; break;
    default: return;
    }

    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t event_count[4] = {};
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        for (uint32_t& count : event_count) count = 0;
    }
    const uint32_t event = event_count[slot]++;
    if (event >= 128u && (event % 256u) != 0u) return;

    uint32_t phase = rs64_phase_ord();
    uint32_t route_width = width;
    uint32_t route_origin = origin;
    uint32_t ordinal = 0xFFFFFFFFu;
    uint32_t row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &phase, &route_width, &route_origin, &ordinal, &row,
        &exit_reason, &arm);
    if (!active) {
        phase = rs64_phase_ord();
        route_width = width;
        route_origin = origin;
        arm = "n/a";
    }
    std::fprintf(stderr,
        "[m5-synth-parent] event=%u source=0x%08X edge=%s gate=%u"
        " callsite=0x%08X taken=%u countdown=%u period=%u"
        " phase=%u width=%u origin=0x%06X active=%u arm=%s"
        " ordinal=%u row=%u ra=0x%08X\n",
        event, source, edge_kind == 0u ? "entry" : "gate", gate,
        callsite, branch_taken, countdown, period, phase, route_width,
        route_origin, active ? 1u : 0u, active && arm ? arm : "n/a",
        ordinal, row, guest_ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_synth_pregate_event(uint32_t source,
                                               uint32_t branch_taken,
                                               uint32_t lhs,
                                               uint32_t rhs,
                                               uint32_t target,
                                               uint32_t guest_ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_AUDIOTICK_TRACE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;

    uint32_t phase = rs64_phase_ord();
    uint32_t route_width = width;
    uint32_t route_origin = origin;
    uint32_t ordinal = 0xFFFFFFFFu;
    uint32_t row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &phase, &route_width, &route_origin, &ordinal, &row,
        &exit_reason, &arm);
    if (!active) {
        phase = rs64_phase_ord();
        route_width = width;
        route_origin = origin;
        arm = "n/a";
    }

    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t event_count[3] = {};
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        for (uint32_t& count : event_count) count = 0;
    }

    uint32_t slot = 0xFFFFFFFFu;
    switch (source) {
    case 0x8009142Cu: slot = 0; break;
    case 0x80091454u: slot = 1; break;
    case 0x80091468u: slot = 2; break;
    default: return;
    }
    const uint32_t event = event_count[slot]++;
    if (event >= 64u && (event % 256u) != 0u) return;

    std::fprintf(stderr,
        "[m5-synth-pregate] event=%u source=0x%08X edge=branch"
        " taken=%u lhs=0x%08X rhs=0x%08X target=0x%08X"
        " phase=%u width=%u origin=0x%06X active=%u arm=%s"
        " ordinal=%u row=%u writer_seq=%u ra=0x%08X\n",
        event, source, branch_taken, lhs, rhs, target, phase, route_width,
        route_origin, active ? 1u : 0u, active && arm ? arm : "n/a",
        ordinal, row, rs64_m5_b40_writer_sequence(), guest_ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_init_voice_entry(uint32_t voice_idx, uint32_t desc,
                                           uint32_t f4, uint32_t f8,
                                           uint32_t fC, uint32_t f10,
                                           uint32_t f14, uint32_t guest_ra) {
    if (!rs64_m5_init_voice_probe_enabled()) return;

    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!rs64_m5_init_voice_target_phase(width, origin)) return;

    uint32_t route_phase = phase;
    uint32_t route_width = width;
    uint32_t route_origin = origin;
    uint32_t ordinal = 0xFFFFFFFFu;
    uint32_t row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &route_phase, &route_width, &route_origin, &ordinal, &row,
        &exit_reason, &arm);
    const uint64_t event = g_rs64_m5_init_voice_event != 0
        ? g_rs64_m5_init_voice_event
        : g_rs64_m5_init_voice_next_event.fetch_add(1, std::memory_order_relaxed);
    std::fprintf(stderr,
                 "[init-voice-sample] event=%llu caller_pc=0x%08X"
                 " prev_pc=0x%08X guest_ra=0x%08X phase=%u width=%u"
                 " origin=0x%06X active=%u arm=%s ordinal=%u row=%u"
                 " voiceIdx=0x%08X desc=0x%08X f4=0x%08X f8=0x%08X"
                 " fC=0x%08X f10=0x%08X f14=0x%08X\n",
                 static_cast<unsigned long long>(event),
                 g_rs64_m5_init_voice_caller_pc,
                 g_rs64_m5_init_voice_caller_pc, guest_ra,
                 active ? route_phase : phase, active ? route_width : width,
                 active ? route_origin : origin, active ? 1u : 0u,
                 active && arm ? arm : "n/a", ordinal, row, voice_idx, desc,
                 f4, f8, fC, f10, f14);
    std::fflush(stderr);
    g_rs64_m5_init_voice_event = 0;
}

static bool rs64_audio_probe_enabled() {
    static int enabled = -1;
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_AUDIO_RETURN");
        const char* contract = std::getenv("ROGUESQ_LOG_M5_TASK_CONTRACT");
        enabled = ((all && *all && *all != '0') ||
                   (own && *own && *own != '0') ||
                   (contract && *contract && *contract != '0')) ? 1 : 0;
    }
    return enabled != 0;
}

extern "C" void rs64_m5_audio_event(const char* kind, uint32_t site,
                                      uint32_t idx, uint32_t dest,
                                      uint32_t value0, uint32_t value1,
                                      uint32_t value2, uint32_t value3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* contract = std::getenv("ROGUESQ_LOG_M5_TASK_CONTRACT");
        return (all && all[0] && all[0] != '0') ||
               (contract && contract[0] && contract[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t vi_phase = rs64_phase_ord();
    const uint32_t vi_width = rs64_vi_committed_width();
    const uint32_t vi_origin = rs64_vi_committed_origin();
    if (!((vi_width == 1024u && vi_origin == 0x00790400u) ||
          (vi_width == 512u && (vi_origin == 0x006AB400u ||
                                vi_origin == 0x00690400u ||
                                vi_origin == 0x00620400u)))) return;

    uint32_t phase = vi_phase;
    uint32_t width = vi_width;
    uint32_t origin = vi_origin;
    uint32_t ordinal = 0xFFFFFFFFu;
    uint32_t row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        &phase, &width, &origin, &ordinal, &row, &exit_reason, &arm);
    if (!active) {
        phase = vi_phase;
        width = vi_width;
        origin = vi_origin;
        arm = "n/a";
    }

    static std::mutex mutex;
    static uint32_t event_count[2] = {};
    static uint32_t control_key[2] = {0xFFFFFFFFu, 0xFFFFFFFFu};
    const uint32_t slot = width == 1024u ? 0u : 1u;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (width << 24) ^ origin;
    if (control_key[slot] != key) {
        control_key[slot] = key;
        std::fprintf(stderr,
            "[m5-audio-join-control] phase=%u width=%u origin=0x%06X "
            "active=%u arm=%s ordinal=%u row=%u\n",
            phase, width, origin, active ? 1u : 0u, arm ? arm : "n/a",
            ordinal, row);
        std::fflush(stderr);
    }
    if (event_count[slot] >= 4096u) return;
    ++event_count[slot];
    rs64_audio_join_m5_event(
        kind, site, active ? 1u : 0u, arm, phase, width, origin, ordinal,
        row, idx, dest, value0, value1, value2, value3);
}

extern "C" void rs64_m5_audio_transition_commit(uint32_t width,
                                                   uint32_t origin,
                                                   uint32_t phase) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_TRANSITION");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || width != 512u) return;
    std::lock_guard<std::mutex> lock(g_rs64_m5_audio_transition_mutex);
    origin &= 0x00FFFFFFu;
    if (origin == 0x00690400u) {
        g_rs64_m5_audio_transition_open = true;
        ++g_rs64_m5_audio_transition_window;
        g_rs64_m5_audio_transition_rows = 0;
        std::fprintf(stderr,
                     "[m5-audio-transition-control] edge=start window=%u "
                     "phase=%u width=%u origin=0x%06X\n",
                     g_rs64_m5_audio_transition_window, phase, width, origin);
        std::fflush(stderr);
    } else if (origin == 0x00620400u && g_rs64_m5_audio_transition_open) {
        std::fprintf(stderr,
                     "[m5-audio-transition-control] edge=end window=%u "
                     "phase=%u width=%u origin=0x%06X\n",
                     g_rs64_m5_audio_transition_window, phase, width, origin);
        std::fflush(stderr);
        g_rs64_m5_audio_transition_open = false;
    }
}

extern "C" void rs64_m5_audio_transition_event(const char* kind,
                                                  uint32_t site,
                                                  uint32_t phase,
                                                  uint32_t width,
                                                  uint32_t origin) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_TRANSITION");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    if (width != 512u) return;
    std::lock_guard<std::mutex> lock(g_rs64_m5_audio_transition_mutex);
    origin &= 0x00FFFFFFu;
    if (origin == 0x00690400u && !g_rs64_m5_audio_transition_open) {
        g_rs64_m5_audio_transition_open = true;
        ++g_rs64_m5_audio_transition_window;
        g_rs64_m5_audio_transition_rows = 0;
        std::fprintf(stderr,
                     "[m5-audio-transition-control] edge=start window=%u "
                     "phase=%u width=%u origin=0x%06X source=event\n",
                     g_rs64_m5_audio_transition_window, phase, width, origin);
        std::fflush(stderr);
    }
    if (!g_rs64_m5_audio_transition_open ||
        g_rs64_m5_audio_transition_rows >= 512u) return;
    std::fprintf(stderr,
                 "[m5-audio-transition-event] window=%u row=%u phase=%u "
                 "width=%u origin=0x%06X kind=%s site=0x%08X\n",
                 g_rs64_m5_audio_transition_window,
                 g_rs64_m5_audio_transition_rows++, phase, width, origin,
                 kind ? kind : "?", site);
    std::fflush(stderr);
    if (origin == 0x00620400u) {
        std::fprintf(stderr,
                     "[m5-audio-transition-control] edge=end window=%u "
                     "phase=%u width=%u origin=0x%06X source=event\n",
                     g_rs64_m5_audio_transition_window, phase, width, origin);
        std::fflush(stderr);
        g_rs64_m5_audio_transition_open = false;
    }
}

static void rs64_audio_route_prepare(const char* arm) {
    static const bool order_probe_enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_ORDER");
        const char* transition = std::getenv("ROGUESQ_LOG_M5_ROUTE_TRANSITION");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0') ||
               (transition && transition[0] && transition[0] != '0');
    }();
    const uint32_t prepare_seq = order_probe_enabled ?
        g_rs64_audio_prepare_seq.fetch_add(1, std::memory_order_relaxed) :
        0xFFFFFFFFu;
    g_rs64_audio_last_prepare_seq = prepare_seq;
    const Rs64AudioRouteIdentity before_clear = g_rs64_audio_identity;
    const uint32_t clear_seq = g_rs64_audio_identity_edge_seq.fetch_add(
        1, std::memory_order_relaxed);
    g_rs64_audio_identity.valid = false;
    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    const bool target_phase =
        (width == 1024u && origin == 0x00790400u) ||
        (width == 512u && (origin == 0x006AB400u ||
                           origin == 0x00690400u ||
                           origin == 0x00620400u));
    rs64_m5_route_prepare_handoff(prepare_seq, phase, width, origin,
                                  target_phase ? 1u : 0u);
    rs64_m5_identity_edge("prepare-clear", before_clear, prepare_seq, clear_seq,
                          phase, width, origin);
    g_rs64_audio_last_prepare_accepted = target_phase ? 1u : 0u;
    if (!rs64_audio_probe_enabled()) {
        if (order_probe_enabled) {
            std::fprintf(stderr,
                "[m5-route-prepare] seq=%u accepted=%u phase=%u width=%u "
                "origin=0x%06X arm=%s probe=disabled\n",
                prepare_seq, target_phase ? 1u : 0u, phase, width, origin,
                arm ? arm : "n/a");
            std::fflush(stderr);
        }
        return;
    }
    if (!target_phase) {
        if (order_probe_enabled) {
            std::fprintf(stderr,
                "[m5-route-prepare] seq=%u accepted=0 phase=%u width=%u "
                "origin=0x%06X arm=%s\n",
                prepare_seq, phase, width, origin, arm ? arm : "n/a");
            std::fflush(stderr);
        }
        return;
    }
    const uint32_t key = (width << 24) ^ origin;
    if (key != g_rs64_audio_phase_key) {
        g_rs64_audio_phase_key = key;
        g_rs64_audio_phase_row = 0;
    }
    g_rs64_audio_identity = {
        true, arm, phase, width, origin,
        g_rs64_audio_ordinal.fetch_add(1, std::memory_order_relaxed),
        g_rs64_audio_phase_row++, prepare_seq
    };
    g_m5_latest_audio_route_seq.fetch_add(1, std::memory_order_acq_rel);
    g_m5_latest_audio_route_ordinal.store(g_rs64_audio_identity.ordinal,
                                          std::memory_order_release);
    g_m5_latest_audio_route_row.store(g_rs64_audio_identity.row,
                                      std::memory_order_release);
    if (order_probe_enabled) {
        std::fprintf(stderr,
            "[m5-route-prepare] seq=%u accepted=1 phase=%u width=%u "
            "origin=0x%06X arm=%s route_ordinal=%u route_row=%u\n",
            prepare_seq, phase, width, origin, arm ? arm : "n/a",
            g_rs64_audio_identity.ordinal, g_rs64_audio_identity.row);
        std::fflush(stderr);
    }
}

static std::atomic<uint32_t> g_rs64_m5_descriptor_event_payload{0};
static std::atomic<uint32_t> g_rs64_m5_descriptor_yield_ptr{0};

static bool rs64_m5_descriptor_phase(uint32_t* phase, uint32_t* width,
                                     uint32_t* origin, const char** arm);

extern "C" void rs64_m5_task_lifetime_edge(const char* edge,
                                             uint32_t task_ptr,
                                             const OSTask* task) {
    static const bool enabled = [] {
        const char* e = std::getenv("ROGUESQ_LOG_M5_TASK_LIFETIME");
        return e && e[0] && e[0] != '0';
    }();
    if (!enabled || !task || task->t.type != M_AUDTASK) return;
    uint32_t phase = 0, width = 0, origin = 0;
    const char* arm = nullptr;
    if (!rs64_m5_descriptor_phase(&phase, &width, &origin, &arm)) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    static uint32_t seq = 0;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
    }
    const uint32_t ordinal = seq++;
    if (rows++ >= 512u) return;
    const uint32_t words[16] = {
        (uint32_t)task->t.type, (uint32_t)task->t.flags,
        (uint32_t)task->t.ucode_boot, (uint32_t)task->t.ucode_boot_size,
        (uint32_t)task->t.ucode, (uint32_t)task->t.ucode_size,
        (uint32_t)task->t.ucode_data, (uint32_t)task->t.ucode_data_size,
        (uint32_t)task->t.dram_stack, (uint32_t)task->t.dram_stack_size,
        (uint32_t)task->t.output_buff, (uint32_t)task->t.output_buff_size,
        (uint32_t)task->t.data_ptr, (uint32_t)task->t.data_size,
        (uint32_t)task->t.yield_data_ptr, (uint32_t)task->t.yield_data_size,
    };
    std::fprintf(stderr,
        "[m5-task-lifetime] edge=%s phase=%u width=%u origin=0x%06X arm=%s "
        "seq=%u task_ptr=0x%08X words=",
        edge, phase, width, origin, arm ? arm : "n/a", ordinal, task_ptr);
    for (uint32_t i = 0; i < 16; ++i)
        std::fprintf(stderr, "%s%08X", i ? "," : "", words[i]);
    std::fprintf(stderr, "\n");
    std::fflush(stderr);
}

extern "C" void rs64_m5_host_task_boundary(const char* edge,
                                             uint32_t task_ptr,
                                             const OSTask* task) {
    static const bool enabled = [] {
        const char* rs64_la = std::getenv("ROGUESQ_LOG_ALL"); // s7728: LOG_ALL, as upstream_compat.cpp
        const char* e = std::getenv("ROGUESQ_LOG_M5_DOWNSTREAM");
        return (rs64_la && *rs64_la && *rs64_la != '0') || (e && e[0] && e[0] != '0');
    }();
    if (!enabled || !task || task->t.type != M_AUDTASK) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (1024u << 24) ^ origin;
    if (key != phase_key) { phase_key = key; rows = 0; }
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-host-task-boundary] ordinal=%u phase=%u origin=0x%06X edge=%s "
        "task_ptr=0x%08X type=0x%08X flags=0x%08X data_ptr=0x%08X data_size=0x%08X "
        "output=0x%08X output_size=0x%08X yield=0x%08X yield_size=0x%08X\n",
        rows++, rs64_phase_ord(), origin, edge ? edge : "?", task_ptr,
        (uint32_t)task->t.type, (uint32_t)task->t.flags, (uint32_t)task->t.data_ptr,
        (uint32_t)task->t.data_size, (uint32_t)task->t.output_buff,
        (uint32_t)task->t.output_buff_size, (uint32_t)task->t.yield_data_ptr,
        (uint32_t)task->t.yield_data_size);
    std::fflush(stderr);
}

extern "C" void rs64_m5_raw_task_boundary(const char* edge,
                                            uint8_t* rdram,
                                            uint32_t raw_task_ptr) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_HOST_BOUNDARY");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !rdram) return;

    static std::mutex mutex;
    static uint32_t rows = 0;
    static bool positive = false;
    static bool rejected = false;
    std::lock_guard<std::mutex> lock(mutex);
    const bool valid = raw_task_ptr >= 0x80000000u &&
                       raw_task_ptr <= 0x807FFFF0u;
    if (valid && !positive) {
        positive = true;
        std::fprintf(stderr,
            "[m5-host-boundary-positive] edge=%s raw_task=0x%08X\n",
            edge ? edge : "?", raw_task_ptr);
    }
    if (!valid && !rejected) {
        rejected = true;
        const int64_t signed_raw = static_cast<int64_t>(
            static_cast<int32_t>(raw_task_ptr));
        const uint64_t macro_index = static_cast<uint64_t>(signed_raw) -
                                     0xFFFFFFFF80000000ull;
        std::fprintf(stderr,
            "[m5-host-boundary-reject] edge=%s raw_task=0x%08X "
            "signed=0x%016llX macro_index=0x%016llX\n",
            edge ? edge : "?", raw_task_ptr,
            static_cast<unsigned long long>(signed_raw),
            static_cast<unsigned long long>(macro_index));
    }
    if (rows++ >= 128u) {
        std::fflush(stderr);
        return;
    }
    if (!valid) {
        std::fflush(stderr);
        return;
    }
    const OSTask* task = TO_PTR(OSTask, static_cast<int64_t>(
        static_cast<int32_t>(raw_task_ptr)));
    std::fprintf(stderr,
        "[m5-host-boundary] row=%u edge=%s phase=%u width=%u origin=0x%06X "
        "raw_task=0x%08X type=0x%08X flags=0x%08X "
        "ucode=0x%08X ucode_size=0x%08X data_ptr=0x%08X data_size=0x%08X "
        "output=0x%08X output_size=0x%08X yield=0x%08X yield_size=0x%08X\n",
        rows - 1u, edge ? edge : "?", rs64_phase_ord(),
        rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu,
        raw_task_ptr, (uint32_t)task->t.type, (uint32_t)task->t.flags,
        (uint32_t)task->t.ucode, (uint32_t)task->t.ucode_size,
        (uint32_t)task->t.data_ptr, (uint32_t)task->t.data_size,
        (uint32_t)task->t.output_buff, (uint32_t)task->t.output_buff_size,
        (uint32_t)task->t.yield_data_ptr, (uint32_t)task->t.yield_data_size);
    std::fflush(stderr);
}

static void rs64_m5_task_handoff(const OSTask* task) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_TASK_CONTRACT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !g_rs64_audio_identity.valid || !task) return;

    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t phase_rows = 0;
    static uint32_t control_key = 0xFFFFFFFFu;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (g_rs64_audio_identity.width << 24) ^
                         g_rs64_audio_identity.origin;
    if (key != phase_key) {
        phase_key = key;
        phase_rows = 0;
    }
    if (key != control_key) {
        control_key = key;
        std::fprintf(stderr,
            "[m5-task-handoff-control] phase=%u width=%u origin=0x%06X arm=%s\n",
            g_rs64_audio_identity.phase, g_rs64_audio_identity.width,
            g_rs64_audio_identity.origin, g_rs64_audio_identity.arm);
    }
    if (phase_rows++ >= 256u) return;
    const uint32_t data_ptr = static_cast<uint32_t>(task->t.data_ptr);
    std::fprintf(stderr,
        "[m5-task-handoff] phase=%u width=%u origin=0x%06X arm=%s "
        "ordinal=%u row=%u task_ptr=0x%08X data_ptr=0x%08X data_size=0x%08X "
        "data_ptr_plus_100=0x%08X task_generation=%llu\n",
        g_rs64_audio_identity.phase, g_rs64_audio_identity.width,
        g_rs64_audio_identity.origin, g_rs64_audio_identity.arm,
        g_rs64_audio_identity.ordinal, g_rs64_audio_identity.row,
        s_pending_task_guest_ptr.load(std::memory_order_acquire), data_ptr,
        static_cast<uint32_t>(task->t.data_size), data_ptr + 0x100u,
        static_cast<unsigned long long>(s_pending_audio_generation));
    std::fflush(stderr);
}

extern "C" void rs64_m5_scheduler_handoff(uint8_t* rdram,
                                            uint32_t event_ptr,
                                            uint32_t payload,
                                            uint32_t task_ptr) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_SCHEDULER_ID");
        return all && all[0] && all[0] != '0';
    }();
    if (!enabled) return;

    g_rs64_m5_descriptor_event_payload.store(payload, std::memory_order_release);

    uint32_t phase = 0;
    uint32_t width = 0;
    uint32_t origin = 0;
    uint32_t ordinal = 0;
    uint32_t row = 0;
    int exit_reason = 0;
    const char* arm = nullptr;
    if (!rs64_audio_current_route_snapshot(&phase, &width, &origin,
                                           &ordinal, &row, &exit_reason,
                                           &arm)) return;

    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t phase_rows = 0;
    static uint32_t control_key = 0xFFFFFFFFu;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        phase_rows = 0;
    }
    if (key != control_key) {
        control_key = key;
        std::fprintf(stderr,
            "[m5-scheduler-id-control] phase=%u width=%u origin=0x%06X arm=%s\n",
            phase, width, origin, arm ? arm : "n/a");
    }
    if (phase_rows++ >= 256u) return;

    const OSTask* task = nullptr;
    if (task_ptr >= 0x80000000u && task_ptr < 0x80800000u) {
        const uint32_t offset = (task_ptr - 0x80000000u) ^ 3u;
        task = reinterpret_cast<const OSTask*>(rdram + offset);
    }
    std::fprintf(stderr,
        "[m5-scheduler-id] phase=%u width=%u origin=0x%06X arm=%s "
        "ordinal=%u row=%u event_ptr=0x%08X event_payload=0x%08X "
        "task_ptr=0x%08X type=0x%08X data_ptr=0x%08X data_size=0x%08X "
        "output_buff=0x%08X yield_data_ptr=0x%08X\n",
        phase, width, origin, arm ? arm : "n/a", ordinal, row,
        event_ptr, payload, task_ptr, task ? (unsigned)task->t.type : 0u,
        task ? (unsigned)task->t.data_ptr : 0u,
        task ? (unsigned)task->t.data_size : 0u,
        task ? (unsigned)task->t.output_buff : 0u,
        task ? (unsigned)task->t.yield_data_ptr : 0u);
    std::fflush(stderr);
}

extern "C" void rs64_m5_scheduler_boundary(uint8_t* rdram, const char* edge,
                                             uint32_t pc, uint32_t a0,
                                             uint32_t a1, uint32_t a2,
                                             uint32_t successor) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SCHEDULER_BOUNDARY");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !rdram) return;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t phase_rows = 0;
    static uint32_t control_key = 0xFFFFFFFFu;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        phase_rows = 0;
    }
    if (key != control_key) {
        control_key = key;
        std::fprintf(stderr,
            "[m5-scheduler-boundary-control] phase=%u width=%u origin=0x%06X\n",
            rs64_phase_ord(), width, origin);
    }
    if (phase_rows >= 128u) return;
    const OSTask* task = nullptr;
    if (a0 >= 0x80000000u && a0 < 0x80800000u) {
        const uint32_t offset = (a0 - 0x80000000u) ^ 3u;
        task = reinterpret_cast<const OSTask*>(rdram + offset);
    }
    const uint32_t task_type = task ? static_cast<uint32_t>(task->t.type) : 0u;
    const uint32_t ucode = task ? static_cast<uint32_t>(task->t.ucode) : 0u;
    const uint32_t ucode_size = task ? static_cast<uint32_t>(task->t.ucode_size) : 0u;
    const uint32_t ucode_data = task ? static_cast<uint32_t>(task->t.ucode_data) : 0u;
    const uint32_t declared_size = task ? static_cast<uint32_t>(task->t.ucode_data_size) : 0u;
    const uint32_t data_ptr = task ? static_cast<uint32_t>(task->t.data_ptr) : 0u;
    const uint32_t data_size = task ? static_cast<uint32_t>(task->t.data_size) : 0u;
    const char* legacy = std::getenv("ROGUESQ_AUDIO_LEGACY_UCODE_DMA");
    const uint32_t staging = (legacy && legacy[0] && legacy[0] != '0') ? 0xF80u : declared_size;
    std::fprintf(stderr,
        "[m5-scheduler-boundary] row=%u edge=%s pc=0x%08X phase=%u width=%u "
        "origin=0x%06X a0=0x%08X a1=0x%08X a2=0x%08X successor=0x%08X "
        "type=0x%08X ucode=0x%08X ucode_size=0x%X ucode_data=0x%08X "
        "declared=0x%X staging=0x%X data=0x%08X data_size=0x%X arm=%s\n",
        phase_rows++, edge ? edge : "?", pc, rs64_phase_ord(), width, origin,
        a0, a1, a2, successor, task_type, ucode, ucode_size, ucode_data,
        declared_size, staging, data_ptr, data_size,
        (legacy && legacy[0] && legacy[0] != '0') ? "legacy" : "declared");
    std::fflush(stderr);
}

extern "C" void rs64_m5_audio_stage_boundary(const OSTask* task,
                                               uint32_t dma_size) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SCHEDULER_BOUNDARY");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !task) return;

    static std::mutex mutex;
    static uint32_t key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    static uint32_t controls = 0;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t phase_key = (width << 24) ^ origin;
    if (phase_key != key) {
        key = phase_key;
        rows = 0;
        if (controls++ < 16u) {
            std::fprintf(stderr,
                "[m5-audio-stage-control] phase=%u width=%u origin=0x%06X\n",
                rs64_phase_ord(), width, origin);
        }
    }
    if (rows >= 64u) return;
    const char* legacy = std::getenv("ROGUESQ_AUDIO_LEGACY_UCODE_DMA");
    const char* arm = (legacy && legacy[0] && legacy[0] != '0') ? "legacy" : "declared";
    static std::atomic<uint64_t> sequence{0};
    const uint64_t seq = sequence.fetch_add(1u, std::memory_order_relaxed) + 1u;
    std::fprintf(stderr,
        "[m5-audio-stage] row=%u seq=%llu phase=%u width=%u origin=0x%06X arm=%s "
        "writer=audio-ucode-data-dma dma_size=0x%X declared=0x%X "
        "ucode_data=0x%08X data_ptr=0x%08X data_size=0x%X\n",
        rows++, static_cast<unsigned long long>(seq), rs64_phase_ord(), width,
        origin, arm, dma_size, static_cast<uint32_t>(task->t.ucode_data_size),
        static_cast<uint32_t>(task->t.ucode_data),
        static_cast<uint32_t>(task->t.data_ptr),
        static_cast<uint32_t>(task->t.data_size));
    std::fflush(stderr);
}

static bool rs64_m5_descriptor_phase(uint32_t* phase, uint32_t* width,
                                     uint32_t* origin, const char** arm) {
    uint32_t ordinal = 0, row = 0;
    int exit_reason = 0;
    if (!rs64_audio_current_route_snapshot(phase, width, origin, &ordinal, &row,
                                           &exit_reason, arm)) return false;
    return (*width == 1024u && *origin == 0x00790400u) ||
           (*width == 512u && (*origin == 0x006AB400u ||
                               *origin == 0x00690400u ||
                               *origin == 0x00620400u));
}

extern "C" void rs64_m5_descriptor_yield(uint8_t* rdram, uint32_t task_ptr) {
    static const bool enabled = [] {
        const char* e = std::getenv("ROGUESQ_LOG_M5_DESCRIPTOR");
        return e && e[0] && e[0] != '0';
    }();
    if (!enabled || task_ptr != 0x800377C8u) return;

    uint32_t phase = 0, width = 0, origin = 0;
    const char* arm = nullptr;
    if (!rs64_m5_descriptor_phase(&phase, &width, &origin, &arm)) return;
    const uint64_t guest_task_ptr = static_cast<uint64_t>(
        static_cast<int64_t>(static_cast<int32_t>(task_ptr)));
    const uint32_t words[16] = {
        (uint32_t)MEM_W(0x00, guest_task_ptr), (uint32_t)MEM_W(0x04, guest_task_ptr),
        (uint32_t)MEM_W(0x08, guest_task_ptr), (uint32_t)MEM_W(0x0C, guest_task_ptr),
        (uint32_t)MEM_W(0x10, guest_task_ptr), (uint32_t)MEM_W(0x14, guest_task_ptr),
        (uint32_t)MEM_W(0x18, guest_task_ptr), (uint32_t)MEM_W(0x1C, guest_task_ptr),
        (uint32_t)MEM_W(0x20, guest_task_ptr), (uint32_t)MEM_W(0x24, guest_task_ptr),
        (uint32_t)MEM_W(0x28, guest_task_ptr), (uint32_t)MEM_W(0x2C, guest_task_ptr),
        (uint32_t)MEM_W(0x30, guest_task_ptr), (uint32_t)MEM_W(0x34, guest_task_ptr),
        (uint32_t)MEM_W(0x38, guest_task_ptr), (uint32_t)MEM_W(0x3C, guest_task_ptr),
    };
    static uint32_t layout_phase_key = 0xFFFFFFFFu;
    static uint32_t layout_rows = 0;
    const uint32_t layout_key = (width << 24) ^ origin;
    if (layout_key != layout_phase_key) {
        layout_phase_key = layout_key;
        layout_rows = 0;
    }
    if (layout_rows++ < 64u) {
        const uint32_t base = task_ptr - 0x80000000u;
        std::fprintf(stderr, "[m5-descriptor-layout] phase=%u width=%u origin=0x%06X task_ptr=0x%08X raw=",
                     phase, width, origin, task_ptr);
        for (uint32_t i = 0; i < 0x40u; ++i)
            std::fprintf(stderr, "%02X", (unsigned)rdram[(base + i) ^ 3u]);
        std::fprintf(stderr, " fields=");
        for (uint32_t i = 0; i < 16u; ++i) {
            uint32_t aligned = 0;
            uint32_t xor_lane = 0;
            std::memcpy(&aligned, rdram + base + i * 4u, sizeof(aligned));
            std::memcpy(&xor_lane, rdram + base + (i * 4u ^ 3u), sizeof(xor_lane));
            std::fprintf(stderr, "%s%u:g=0x%08X,a=0x%08X,x=0x%08X,s=0x%08X",
                         i ? ";" : "", i, task_ptr + i * 4u, aligned, xor_lane,
                         __builtin_bswap32(aligned));
        }
        std::fprintf(stderr, "\n");
        std::fflush(stderr);

        const OSTask* task = TO_PTR(OSTask, guest_task_ptr);
        const uint32_t to_ptr_words[16] = {
            (uint32_t)task->t.type, (uint32_t)task->t.flags,
            (uint32_t)task->t.ucode_boot, (uint32_t)task->t.ucode_boot_size,
            (uint32_t)task->t.ucode, (uint32_t)task->t.ucode_size,
            (uint32_t)task->t.ucode_data, (uint32_t)task->t.ucode_data_size,
            (uint32_t)task->t.dram_stack, (uint32_t)task->t.dram_stack_size,
            (uint32_t)task->t.output_buff, (uint32_t)task->t.output_buff_size,
            (uint32_t)task->t.data_ptr, (uint32_t)task->t.data_size,
            (uint32_t)task->t.yield_data_ptr, (uint32_t)task->t.yield_data_size,
        };
        static const uint32_t compare_fields[] = {0u, 2u, 4u, 6u, 10u, 11u, 12u, 14u};
        std::fprintf(stderr, "[m5-descriptor-compare] phase=%u width=%u origin=0x%06X task_ptr=0x%08X base=0x%06X",
                     phase, width, origin, task_ptr, base);
        for (uint32_t field : compare_fields) {
            uint32_t explicit_read = 0;
            std::memcpy(&explicit_read, rdram + base + field * 4u, sizeof(explicit_read));
            std::fprintf(stderr, " f%u:guest=0x%08X off=0x%06X memw=0x%08X explicit=0x%08X toptr=0x%08X",
                         field, task_ptr + field * 4u, base + field * 4u,
                         (uint32_t)MEM_W(field * 4u, guest_task_ptr), explicit_read,
                         to_ptr_words[field]);
        }
        std::fprintf(stderr, "\n");
        std::fflush(stderr);
    }
    g_rs64_m5_descriptor_yield_ptr.store(task_ptr, std::memory_order_release);
    std::fprintf(stderr,
        "[m5-descriptor-control] phase=%u width=%u origin=0x%06X arm=%s\n",
        phase, width, origin, arm ? arm : "n/a");
    std::fprintf(stderr,
        "[m5-descriptor-yield] phase=%u width=%u origin=0x%06X arm=%s "
        "task_ptr=0x%08X event_payload=0x%08X words=",
        phase, width, origin, arm ? arm : "n/a", task_ptr,
        g_rs64_m5_descriptor_event_payload.load(std::memory_order_acquire));
    for (uint32_t i = 0; i < 16; ++i)
        std::fprintf(stderr, "%s%08X", i ? "," : "", words[i]);
    std::fprintf(stderr, "\n");
    std::fflush(stderr);
}

extern "C" void rs64_m5_descriptor_start(uint8_t* rdram, uint32_t task_ptr) {
    static const bool enabled = [] {
        const char* e = std::getenv("ROGUESQ_LOG_M5_DESCRIPTOR");
        return e && e[0] && e[0] != '0';
    }();
    if (!enabled) return;
    uint32_t phase = 0, width = 0, origin = 0;
    const char* arm = nullptr;
    if (!rs64_m5_descriptor_phase(&phase, &width, &origin, &arm)) return;
    if (task_ptr != 0x800377C8u) return;
    const OSTask* task = TO_PTR(OSTask, task_ptr);
    static std::atomic<uint32_t> rows{0};
    const uint32_t row = rows.fetch_add(1, std::memory_order_relaxed);
    if (row >= 256u) return;
    const uint32_t yielded = g_rs64_m5_descriptor_yield_ptr.load(std::memory_order_acquire);
    const uint32_t payload = g_rs64_m5_descriptor_event_payload.load(std::memory_order_acquire);
    std::fprintf(stderr,
        "[m5-descriptor-start] phase=%u width=%u origin=0x%06X arm=%s row=%u "
        "task_ptr=0x%08X data_ptr=0x%08X data_size=0x%08X "
        "yield_ptr=0x%08X event_payload=0x%08X yield_match=%u payload_match=%u\n",
        phase, width, origin, arm ? arm : "n/a", row, task_ptr,
        (uint32_t)task->t.data_ptr, (uint32_t)task->t.data_size, yielded,
        payload, task_ptr == yielded ? 1u : 0u, task_ptr == payload ? 1u : 0u);
    std::fflush(stderr);
}

extern "C" void rs64_m5_port_task_load(uint8_t* rdram, uint32_t task_ptr) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_PORT_LOAD");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    uint32_t phase = 0, width = 0, origin = 0;
    const char* arm = nullptr;
    if (!rs64_m5_descriptor_phase(&phase, &width, &origin, &arm)) return;

    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t phase_rows = 0;
    static uint32_t control_key = 0xFFFFFFFFu;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        phase_rows = 0;
    }
    if (key != control_key) {
        control_key = key;
        std::fprintf(stderr,
            "[m5-port-load-control] phase=%u width=%u origin=0x%06X arm=%s\n",
            phase, width, origin, arm ? arm : "n/a");
        std::fflush(stderr);
    }
    if (phase_rows++ >= 256u) return;

    if (task_ptr < 0x80000000u || task_ptr > 0x80800000u - sizeof(OSTask)) {
        // s5250: count fires; ROGUESQ_NO_TASKPTR_GUARD=1 lets the old (unguarded) path run for the route-stall bisect.
        static int fired = 0;
        static const bool disabled = std::getenv("ROGUESQ_NO_TASKPTR_GUARD") != nullptr;
        if (fired++ < 8) std::fprintf(stderr, "[s5250-taskptr-guard] task_ptr=0x%08X %s\n", task_ptr, disabled ? "PASSTHROUGH" : "RETURN");
        if (!disabled) return;
    }
    const uint64_t guest_task_ptr = static_cast<uint64_t>(
        static_cast<int64_t>(static_cast<int32_t>(task_ptr)));
    const OSTask* task = TO_PTR(OSTask, guest_task_ptr);
    std::fprintf(stderr,
        "[m5-port-load] phase=%u width=%u origin=0x%06X arm=%s row=%u "
        "task_ptr=0x%08X type=0x%08X flags=0x%08X data_ptr=0x%08X "
        "data_size=0x%08X output_buff=0x%08X output_size=0x%08X "
        "yield_ptr=0x%08X yield_size=0x%08X\n",
        phase, width, origin, arm ? arm : "n/a", phase_rows - 1u, task_ptr,
        (uint32_t)task->t.type, (uint32_t)task->t.flags,
        (uint32_t)task->t.data_ptr, (uint32_t)task->t.data_size,
        (uint32_t)task->t.output_buff, (uint32_t)task->t.output_buff_size,
        (uint32_t)task->t.yield_data_ptr, (uint32_t)task->t.yield_data_size);
    std::fflush(stderr);
}

static void rs64_audio_hash_dmem(uint32_t addr, uint32_t len,
                                  uint32_t& fnv, uint32_t& nonzero) {
    fnv = 2166136261u;
    nonzero = 0;
    for (uint32_t i = 0; i < len; ++i) {
        const uint8_t b = g_dmem_cur[((addr + i) & 0xFFFu) ^ 3u];
        fnv = (fnv * 16777619u) ^ b;
        nonzero += b != 0;
    }
}

static void rs64_audio_hash_dmem_dma(uint32_t addr, uint32_t len,
                                     uint32_t& fnv, uint32_t& nonzero) {
    fnv = 2166136261u;
    nonzero = 0;
    for (uint32_t i = 0; i < len; ++i) {
        const uint8_t b = g_dmem_cur[((addr + (i ^ 3u)) & 0xFFFu) ^ 3u];
        fnv = (fnv * 16777619u) ^ b;
        nonzero += b != 0;
    }
}

static void rs64_audio_hash_rdram(const uint8_t* rdram, uint32_t addr,
                                   uint32_t len, uint32_t& fnv,
                                   uint32_t& nonzero, bool& valid) {
    fnv = 2166136261u;
    nonzero = 0;
    valid = addr <= 0x800000u - len;
    if (!valid) return;
    for (uint32_t i = 0; i < len; ++i) {
        const uint8_t b = rdram[(addr + i) & 0x7FFFFFu];
        fnv = (fnv * 16777619u) ^ b;
        nonzero += b != 0;
    }
}

static thread_local bool g_rs64_audio_vector_store = false;
static thread_local uint32_t g_spike_sdv_reg = 0, g_spike_sdv_e = 0, g_spike_sdv_lanes[8], g_spike_sdv_snap[88];
struct Rs64VuRingEnt { uint16_t op, vd, e, vtr, vl[8], all[48], post[8]; uint32_t src; const char* kind; };
static thread_local uint32_t g_vld_addr[32]; static thread_local const char* g_vld_kind[32];
static thread_local uint32_t g_vte_pend_reg; static thread_local uint16_t g_vte_pend_l[8];
// s6696 G3d: the s6372 version called getenv() on EVERY RSP vector load and the SDV hook copied 96 lanes on every SDV, armed or not;
// lvl1 gfx task cost went ~10 -> ~50-80 ms (30 -> 11-17 game fps, bursty presents = the owner's turning shake). Flag is cached now.
// ROGUESQ_G3D_LEGACY_TOGGLE=<sec>: same-run A/B, re-enables the old per-load getenv + SDV snapshot in alternate <sec> windows ([g3d] line per flip).
static const bool g_spike_dmem_on = [] { const char* e = getenv("ROGUESQ_SPIKE_DMEM"); return e && *e && *e != '0'; }();  // s7714: =0 off, as in dpc_bridge/rsp.cpp
// s6704 G1e: inline master gate for the per-RSP-load/store hooks (rs64_vld_note, rs64_m5_audio_dmem_store/_vector_store, the
// VU ring, the SDV snapshot). On iff one of the env vars those hooks read is set, or ROGUESQ_RSP_HOOKS=1, so default output
// is unchanged; off, the gfx LLE skips ~10% of its Gfx-thread time in out-of-line no-op calls (s6704 sample).
extern "C" int rs64_rsp_hooks_on;
int rs64_rsp_hooks_on = [] {
    auto on = [](const char* n) { const char* e = getenv(n); return e && *e && *e != '0'; };
    const int v = (g_spike_dmem_on || on("ROGUESQ_LOG_ALL") || on("ROGUESQ_LOG_M5_SOURCE_WRITER") || on("ROGUESQ_RSP_HOOKS") ||
                   on("ROGUESQ_G3D_LEGACY_TOGGLE")) ? 1 : 0;
    fprintf(stderr, "[s6704] rsp_hooks_on=%d rt64_profile=%d\n", v, on("ROGUESQ_RT64_PROFILE") ? 1 : 0);
    return v;
}();
// s6698 G1c: master gate for the per-guest-store diagnostic hooks (tools/apply_s6698_storediag.py gates ~143k call sites).
// They cost 52% of the game thread's busy time in lvl5 dd4 flight with nothing armed. Auto-on whenever a logging/watch env
// var is set, so every existing soak recipe keeps its instruments; ROGUESQ_STORE_DIAG=0/1 overrides.
// ROGUESQ_STORE_DIAG_TOGGLE=<sec>: same-run A/B, flips the gate every <sec> s at osViSwapBuffer ([storediag] line per flip).
extern "C" int g_rs64_store_diag = [] {
    if (const char* e = getenv("ROGUESQ_STORE_DIAG"); e && *e) {
        fprintf(stderr, "[storediag] on=%d reason=ROGUESQ_STORE_DIAG\n", *e != '0' ? 1 : 0);
        return *e != '0' ? 1 : 0;
    }
    extern char** environ;
    for (char** v = environ; v && *v; ++v) {
        const char* s = *v;
        if (strncmp(s, "ROGUESQ_", 8)) continue;
        const char* eq = strchr(s, '='); std::string name(s, eq ? eq - s : strlen(s));
        if (!name.compare(0, 12, "ROGUESQ_LOG_") || name.find("WATCH") != std::string::npos ||
            name == "ROGUESQ_FLOOR_DEPTH_DIR" || name == "ROGUESQ_VSRC_STORES" || name == "ROGUESQ_SPANW") {
            fprintf(stderr, "[storediag] on=1 reason=%s\n", name.c_str());
            return 1;
        }
    }
    fprintf(stderr, "[storediag] on=0 reason=no-logging-env\n");
    return 0;
}();
// s6713 G1e: fast RSP DMA (see librecomp rsp.hpp). Default on iff no diagnostic env is armed that the skipped per-DMA hooks
// could serve: any ROGUESQ_LOG_*, *WATCH*, session-numbered probe (ROGUESQ_S<digit>...), or the hooks' own non-LOG vars.
extern "C" int rs64_g1e_fast = [] {
    if (const char* e = getenv("ROGUESQ_G1E_FAST"); e && *e) {
        fprintf(stderr, "[g1e-fast] on=%d reason=ROGUESQ_G1E_FAST\n", *e != '0' ? 1 : 0);
        return *e != '0' ? 1 : 0;
    }
    if (rs64_rsp_hooks_on) { fprintf(stderr, "[g1e-fast] on=0 reason=rsp_hooks_on\n"); return 0; }
    static const char* const k_diag[] = {"ROGUESQ_FLOOR_DEPTH_DIR", "ROGUESQ_VSRC_STORES", "ROGUESQ_SPANW", "ROGUESQ_SPIKE_DMEM",
                                         "ROGUESQ_TRACE_DMA", "ROGUESQ_DUMP_IMEM_DMA", "ROGUESQ_RSP_HOOKS"};
    extern char** environ;
    for (char** v = environ; v && *v; ++v) {
        const char* s = *v;
        if (strncmp(s, "ROGUESQ_", 8)) continue;
        const char* eq = strchr(s, '='); std::string name(s, eq ? eq - s : strlen(s));
        bool diag = !name.compare(0, 12, "ROGUESQ_LOG_") || name.find("WATCH") != std::string::npos ||
                    (name.size() > 9 && name[8] == 'S' && name[9] >= '0' && name[9] <= '9');
        for (const char* d : k_diag) diag = diag || name == d;
        if (diag) { fprintf(stderr, "[g1e-fast] on=0 reason=%s\n", name.c_str()); return 0; }
    }
    fprintf(stderr, "[g1e-fast] on=1 reason=no-diag-env\n");
    return 1;
}();
// s6715 G1e: in-ucode diagnostic probes (rs64_dlw_*, rs64_inline_probe_*, rs64_m4_*, rs64_f5_*_probe, source_fetch) are
// gated at the call site (tools/fixup_factor5_ucode.py macro block). Default on iff an env that any of them reads is armed
// (any ROGUESQ_LOG_*, ROGUESQ_DLWALK, ROGUESQ_G3C_DMALOG); ROGUESQ_G1E_PROBES=0/1 overrides, ROGUESQ_G1E_PROBES_TOGGLE=<sec>
// flips it every <sec> s ([g1e-probes] line per flip). Off = the callees' early return was all they did.
extern "C" int rs64_g1e_probes = [] {
    if (const char* e = getenv("ROGUESQ_G1E_PROBES"); e && *e) {
        fprintf(stderr, "[g1e-probes] on=%d reason=ROGUESQ_G1E_PROBES\n", *e != '0' ? 1 : 0);
        return *e != '0' ? 1 : 0;
    }
    extern char** environ;
    for (char** v = environ; v && *v; ++v) {
        const char* s = *v;
        const char* eq = strchr(s, '=');
        if (!eq || !eq[1] || strncmp(s, "ROGUESQ_", 8)) continue;
        std::string name(s, eq - s);
        if (!name.compare(0, 12, "ROGUESQ_LOG_") || name == "ROGUESQ_DLWALK" || name == "ROGUESQ_G3C_DMALOG") {
            fprintf(stderr, "[g1e-probes] on=1 reason=%s\n", name.c_str());
            return 1;
        }
    }
    fprintf(stderr, "[g1e-probes] on=0 reason=no-probe-env\n");
    return 0;
}();
// s6932 G1e: probes that throttle on width < 640 ran unthrottled for the whole game at wide aspect (tools/apply_s6932_widequiet.py).
// Default: quiet unless probes are on. ROGUESQ_WIDE_LOGQUIET=0 old, =1 always quiet, =tog 10 s blocks on the present ring's clock, odd block quiet.
extern "C" int rs64_s6932_quiet(void) {
    static const int mode = [] { const char* e = getenv("ROGUESQ_WIDE_LOGQUIET"); if (!e || !*e) return 3; if (!strcmp(e, "tog")) return 2; return *e != '0' ? 1 : 0; }();
    if (mode == 3) return !rs64_g1e_probes;
    if (mode < 2) return mode;
    struct timespec ts; clock_gettime(CLOCK_UPTIME_RAW, &ts); return (int)((ts.tv_sec / 10) & 1);
}
static void rs64_g1e_probes_tick() {
    static const double sec = [] { const char* e = getenv("ROGUESQ_G1E_PROBES_TOGGLE"); return (e && *e) ? atof(e) : 0.0; }();
    if (sec <= 0.0) return;
    static const auto t0 = std::chrono::steady_clock::now(); static auto t_flip = t0;
    const auto now = std::chrono::steady_clock::now();
    if (std::chrono::duration<double>(now - t_flip).count() < sec) return;
    t_flip = now; rs64_g1e_probes = !rs64_g1e_probes;
    fprintf(stderr, "[g1e-probes] on=%d t=%.3f\n", rs64_g1e_probes, std::chrono::duration<double>(now - t0).count());
}
// ROGUESQ_G1E_FAST_TOGGLE=<sec>: flip rs64_g1e_fast every <sec> s at osViSwapBuffer ([g1e-fast] line per flip).
static void rs64_g1e_fast_tick() {
    static const double sec = [] { const char* e = getenv("ROGUESQ_G1E_FAST_TOGGLE"); return (e && *e) ? atof(e) : 0.0; }();
    if (sec <= 0.0) return;
    static const auto t0 = std::chrono::steady_clock::now(); static auto t_flip = t0;
    const auto now = std::chrono::steady_clock::now();
    if (std::chrono::duration<double>(now - t_flip).count() < sec) return;
    t_flip = now; rs64_g1e_fast = !rs64_g1e_fast;
    fprintf(stderr, "[g1e-fast] on=%d t=%.3f\n", rs64_g1e_fast, std::chrono::duration<double>(now - t0).count());
}
// s6774 G1e: aligned DMEM fast paths in the RSP scalar/vector loads and stores (librecomp rsp.hpp rs64_dmem_w, rsp_vu_impl.hpp
// LDV/SDV/LLV/SLV/LSV/SSV/LQV/SQV). Bit-identical to the byte loops (scratch/s6774 equivalence harness); the per-access hooks
// still run. Default on; ROGUESQ_G1E_DMEM=0 restores the byte loops, ROGUESQ_G1E_DMEM_TOGGLE=<sec> flips it ([g1e-dmem] line).
extern "C" int rs64_g1e_dmem = [] {
    const char* e = getenv("ROGUESQ_G1E_DMEM");
    const int on = (e && *e) ? (*e != '0') : 1;
    fprintf(stderr, "[g1e-dmem] on=%d\n", on);
    return on;
}();
static void rs64_g1e_dmem_tick() {
    static const double sec = [] { const char* e = getenv("ROGUESQ_G1E_DMEM_TOGGLE"); return (e && *e) ? atof(e) : 0.0; }();
    if (sec <= 0.0) return;
    static const auto t0 = std::chrono::steady_clock::now(); static auto t_flip = t0;
    const auto now = std::chrono::steady_clock::now();
    if (std::chrono::duration<double>(now - t_flip).count() < sec) return;
    t_flip = now; rs64_g1e_dmem = !rs64_g1e_dmem;
    fprintf(stderr, "[g1e-dmem] on=%d t=%.3f\n", rs64_g1e_dmem, std::chrono::duration<double>(now - t0).count());
}
// s6775 G1e: the gfx ucode TU addresses DMEM through the constant `dmem` array instead of the thread-local g_dmem_cur
// (rsp.hpp RS64_DMEM_BASE). Default on; ROGUESQ_G1E_DMEMBASE=0 runs factor5_ucode_tls (same ucode, old base),
// ROGUESQ_G1E_DMEMBASE_TOGGLE=<sec> flips it ([g1e-dmembase] lines). Either arm falls back to the TLS one if g_dmem_cur != dmem.
static int rs64_g1e_dmembase = [] {
    const char* e = getenv("ROGUESQ_G1E_DMEMBASE");
    const int on = (e && *e) ? (*e != '0') : 1;
    fprintf(stderr, "[g1e-dmembase] on=%d\n", on);
    return on;
}();
static void rs64_g1e_dmembase_tick() {
    static const double sec = [] { const char* e = getenv("ROGUESQ_G1E_DMEMBASE_TOGGLE"); return (e && *e) ? atof(e) : 0.0; }();
    if (sec <= 0.0) return;
    static const auto t0 = std::chrono::steady_clock::now(); static auto t_flip = t0;
    const auto now = std::chrono::steady_clock::now();
    if (std::chrono::duration<double>(now - t_flip).count() < sec) return;
    t_flip = now; rs64_g1e_dmembase = !rs64_g1e_dmembase;
    fprintf(stderr, "[g1e-dmembase] on=%d t=%.3f\n", rs64_g1e_dmembase, std::chrono::duration<double>(now - t0).count());
}
// s6940 G1e: lean gfx ucode arm (src/rsp/factor5_ucode_lean.cpp: hook and probe gates compiled to 0, so the RSP vector
// registers stay in host registers). Runs only while rs64_rsp_hooks_on == 0 and rs64_g1e_probes == 0, where it executes
// the same code as the main TU. Default on; ROGUESQ_G1E_LEAN=0 old, ROGUESQ_G1E_LEAN_TOGGLE=<sec> flips it
// ([g1e-lean] line per flip with the task count each arm ran since the last flip: the positive control).
static int rs64_g1e_lean = [] {
    const char* e = getenv("ROGUESQ_G1E_LEAN");
    const int on = (e && *e) ? (*e != '0') : 1;
    fprintf(stderr, "[g1e-lean] on=%d\n", on);
    return on;
}();
static std::atomic<uint64_t> rs64_g1e_lean_tasks[2];  // bumped on the gfx thread, read at the flip
static void rs64_g1e_lean_tick() {
    static const double sec = [] { const char* e = getenv("ROGUESQ_G1E_LEAN_TOGGLE"); return (e && *e) ? atof(e) : 0.0; }();
    if (sec <= 0.0) return;
    static const auto t0 = std::chrono::steady_clock::now(); static auto t_flip = t0;
    const auto now = std::chrono::steady_clock::now();
    if (std::chrono::duration<double>(now - t_flip).count() < sec) return;
    t_flip = now; rs64_g1e_lean = !rs64_g1e_lean;
    fprintf(stderr, "[g1e-lean] on=%d t=%.3f ran_main=%llu ran_lean=%llu\n", rs64_g1e_lean,
            std::chrono::duration<double>(now - t0).count(), (unsigned long long)rs64_g1e_lean_tasks[0].exchange(0),
            (unsigned long long)rs64_g1e_lean_tasks[1].exchange(0));
}
// s6941 G1e: NEON multiply-op arm (src/rsp/factor5_ucode_nmac.cpp), taken instead of the lean arm when the lean arm would
// run. Default on since s6941 (bit-exact, same-run -0.20 ms/task in flight); ROGUESQ_G1E_NMAC=0 runs the lean arm,
// ROGUESQ_G1E_NMAC_TOGGLE=<sec> flips it; [g1e-nmac] line per flip
// with the task count each arm ran since the last flip (positive control).
static int rs64_g1e_nmac = [] {
    const char* e = getenv("ROGUESQ_G1E_NMAC");
    const int on = (e && *e) ? (*e != '0') : 1;
    fprintf(stderr, "[g1e-nmac] on=%d\n", on);
    return on;
}();
static std::atomic<uint64_t> rs64_g1e_nmac_tasks[2];
static void rs64_g1e_nmac_tick() {
    static const double sec = [] { const char* e = getenv("ROGUESQ_G1E_NMAC_TOGGLE"); return (e && *e) ? atof(e) : 0.0; }();
    if (sec <= 0.0) return;
    static const auto t0 = std::chrono::steady_clock::now(); static auto t_flip = t0;
    const auto now = std::chrono::steady_clock::now();
    if (std::chrono::duration<double>(now - t_flip).count() < sec) return;
    t_flip = now; rs64_g1e_nmac = !rs64_g1e_nmac;
    fprintf(stderr, "[g1e-nmac] on=%d t=%.3f ran_lean=%llu ran_nmac=%llu\n", rs64_g1e_nmac,
            std::chrono::duration<double>(now - t0).count(), (unsigned long long)rs64_g1e_nmac_tasks[0].exchange(0),
            (unsigned long long)rs64_g1e_nmac_tasks[1].exchange(0));
}
// s7432 class CO: default-on diagnostic fprintf cost on the calling threads. include/rsp_dpc_macros.h routes every fprintf
// in the generated C (RecompiledFuncs: [s2020-svc], [s3290-stall], [s5855], [s5908], ...) through rs64_diag_fprintf, and the
// per-frame src sites ([dpc-fwd], [osViSetMode], [vi-mode-table], [lle task]) call it directly. ROGUESQ_DIAG_QUIET=1 drops
// their stderr lines at source (crash/abort/fatal/SIG/ERROR/assert formats always pass). Measurement (ROGUESQ_DIAG_STAT=1 or
// any toggle): per-window calls/ns/bytes split by in-gfx-task vs other threads. ROGUESQ_DIAG_QUIET_TOGGLE=<s> flips quiet,
// ROGUESQ_DIAG_BUSY_TOGGLE=<s> flips the positive control: ROGUESQ_DIAG_BUSY_US busy-wait per gfx task (inside the
// [g1e-split] ucode window) and ROGUESQ_DIAG_BUSY_GUEST_US per osViSwapBuffer on the guest thread. One [diag-quiet] line per flip.
static int rs64_env_int(const char* n, int d) { const char* e = getenv(n); return (e && *e) ? atoi(e) : d; }
extern "C" int rs64_diag_quiet = [] { const int q = rs64_env_int("ROGUESQ_DIAG_QUIET", 0) != 0;
    (fprintf)(stderr, "[diag-quiet] init quiet=%d\n", q); return q; }();
static const double s_dq_qtog = [] { const char* e = getenv("ROGUESQ_DIAG_QUIET_TOGGLE"); return (e && *e) ? atof(e) : 0.0; }();
static const double s_dq_btog = [] { const char* e = getenv("ROGUESQ_DIAG_BUSY_TOGGLE"); return (e && *e) ? atof(e) : 0.0; }();
static const int s_dq_stat = rs64_env_int("ROGUESQ_DIAG_STAT", 0) || s_dq_qtog > 0 || s_dq_btog > 0;
static const int s_dq_busy_us = rs64_env_int("ROGUESQ_DIAG_BUSY_US", 0), s_dq_busy_guest_us = rs64_env_int("ROGUESQ_DIAG_BUSY_GUEST_US", 0);
static std::atomic<int> rs64_diag_busy{0};
static std::atomic<uint64_t> s_dq_calls[2], s_dq_ns[2], s_dq_bytes[2], s_dq_drop[2];
static void rs64_diag_spin_us(int us) {
    if (us <= 0) return;
    const auto t = std::chrono::steady_clock::now() + std::chrono::microseconds(us);
    while (std::chrono::steady_clock::now() < t) {}
}
// s7448 class DE: harness markers survive QUIET (format-string prefix match). The live harnesses
// (scratch/agent/m6_god_common.sh via g1_level_coverage_common.zsh, tools/s7230_headroom.py / s7257_dip_runs.py /
// s7229_flat30_cost.py, tools/boot_freeze_hunt.sh) gate on these; all are low-rate (lvl4 211 s default: [vi] 194,
// [autopilot] 75, [godmode] 3, [initMission] 1 lines) or opt-in ([g1b], [stall-*]). ROGUESQ_DIAG_QUIET_HARNESS=0 drops them too.
static const int s_dq_keep_harness = rs64_env_int("ROGUESQ_DIAG_QUIET_HARNESS", 1);
// s7449 class DF: failure reports whose keyword lives in an ARGUMENT or in a word the s7432 list missed were dropped under
// QUIET: ultramodern message_box "%s\n" + our callback "[Error] %s\n" ("Failed to allocate memory!", "Error opening stored
// ROM!"), quick_exit "Exiting with exit status", librecomp "Failed to find function at", "RSP ucode %u exited unexpectedly",
// [s7357-io] "... failed", [s6892] "%s\n" walker-guard repairs. Now: extra keywords + when fmt has "%s" the FORMATTED text
// is checked too. ROGUESQ_DIAG_QUIET_ARGCHECK=0 restores the s7448 filter (A/B arm). ROGUESQ_PLANT_FAIL=<s>: positive
// control, emits one line of each class at t=s on the guest thread, then raises SIGSEGV (crash-handler path).
static const int s_dq_argcheck = rs64_env_int("ROGUESQ_DIAG_QUIET_ARGCHECK", 1);
static bool rs64_diag_keep_words(const char* f) {
    static const char* const k[] = {"CRASH", "crash", "abort", "FATAL", "fatal", "SIG", "ERROR", "assert"};
    for (const char* w : k) if (strstr(f, w)) return true;
    if (s_dq_argcheck) {
        static const char* const k2[] = {"Error", "error", "Fail", "fail", "unexpected", "Exiting", "[s6892]"};
        for (const char* w : k2) if (strstr(f, w)) return true;
    }
    return false;
}
static bool rs64_diag_keep(const char* f) {
    if (rs64_diag_keep_words(f)) return true;
    if (s_dq_keep_harness && f[0] == '[') {
        static const char* const h[] = {"[initMission]", "[autopilot]", "[vi] update_screen", "[f5-phase5-target-store]",
                                        "[godmode]", "[g1b]", "[stall-"};
        for (const char* w : h) if (strncmp(f, w, strlen(w)) == 0) return true;
    }
    return false;
}
extern "C" int rs64_diag_fprintf(FILE* f, const char* fmt, ...) {
    const int task = g_rs64_lle_depth.load(std::memory_order_relaxed) > 0;
    if (rs64_diag_quiet && f == stderr && !rs64_diag_keep(fmt)) {
        bool keep = false;
        if (s_dq_argcheck && strstr(fmt, "%s")) {  // s7449: keyword may be in a %s argument
            char b[2048]; va_list a2; va_start(a2, fmt); const int n = vsnprintf(b, sizeof b, fmt, a2); va_end(a2);
            keep = n > 0 && rs64_diag_keep(b);
        }
        if (!keep) {
            if (s_dq_stat) s_dq_drop[task].fetch_add(1, std::memory_order_relaxed);
            return 0;
        }
    }
    va_list ap; va_start(ap, fmt);
    if (!s_dq_stat || f != stderr) { const int r = vfprintf(f, fmt, ap); va_end(ap); return r; }
    const auto t0 = std::chrono::steady_clock::now();
    const int r = vfprintf(f, fmt, ap);
    const auto t1 = std::chrono::steady_clock::now();
    va_end(ap);
    s_dq_calls[task].fetch_add(1, std::memory_order_relaxed);
    s_dq_ns[task].fetch_add((uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count(), std::memory_order_relaxed);
    if (r > 0) s_dq_bytes[task].fetch_add((uint64_t)r, std::memory_order_relaxed);
    return r;
}
extern "C" void rs64_diag_busy_task(void) { if (rs64_diag_busy.load(std::memory_order_relaxed)) rs64_diag_spin_us(s_dq_busy_us); }
static void rs64_diag_plant_tick() {
    static const double sec = [] { const char* e = getenv("ROGUESQ_PLANT_FAIL"); return (e && *e) ? atof(e) : 0.0; }();
    if (sec <= 0) return;
    static const auto t0 = std::chrono::steady_clock::now();
    if (std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count() < sec) return;
    const char* mb = "Failed to allocate memory! (s7449 plant)";
    fprintf(stderr, "%s\n", mb);                       // ultramodern message_box line
    fprintf(stderr, "[Error] %s\n", mb);               // our message_box callback line
    fprintf(stderr, "Exiting with exit status '%i'. Function %s, at file %s:%i\n", 1, "s7449_plant", __FILE__, __LINE__);
    fprintf(stderr, "Failed to find function at 0x%08X\n", 0x80001234u);
    fprintf(stderr, "RSP ucode %u exited unexpectedly. exit_reason: %i\n", 1u, 3);
    char buf[128]; snprintf(buf, sizeof buf, "[s6892] pc=%08X s2=%08X bad=%08X plant", 0x80022160u, 0x80100000u, 0x26282B2Bu);
    fprintf(stderr, "%s\n", buf);                      // upstream_compat s6892 "%s\n" line
    fprintf(stderr, "[s7449-plant] raising SIGSEGV\n"); // contains SIG: kept by the s7432 list (in-run control)
    fflush(stderr);
    raise(SIGSEGV);
}
// s7450 class DG: ROGUESQ_PLANT_EXIT=<s> positive control for NON-signal fatal exits (harness scorers grepped only
// CRASH|SIGSEGV|abort). KIND (ROGUESQ_PLANT_EXIT_KIND): switch = librecomp switch_error's exact printf (stdout) + exit(1);
// quick = ultramodern quick_exit's exact stderr line + _Exit(1); silent = _Exit(1) with no text.
static void rs64_diag_plant_exit_tick() {
    static const double sec = [] { const char* e = getenv("ROGUESQ_PLANT_EXIT"); return (e && *e) ? atof(e) : 0.0; }();
    if (sec <= 0) return;
    static const auto t0 = std::chrono::steady_clock::now();
    if (std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count() < sec) return;
    const char* k = getenv("ROGUESQ_PLANT_EXIT_KIND"); const std::string kind = k ? k : "switch";
    if (kind == "quick") {
        (fprintf)(stderr, "Exiting with exit status '%i'. Function %s, at file %s:%i\n", 1, "s7450_plant", __FILE__, __LINE__);
        std::_Exit(1);
    }
    if (kind == "silent") std::_Exit(1);
    // s7593: uquick = a burst of ROGUESQ_S7593_FLOOD (default 5000) numbered lines, then the real ULTRAMODERN fatal exit, so the
    // log shows whether the lines queued in async stderr (s6979) survive the exit (scorer: count "[s7593-flood]" + the exit line).
    if (kind == "uquick") {
        const char* fe = getenv("ROGUESQ_S7593_FLOOD"); const int fn = (fe && *fe) ? atoi(fe) : 5000;
        for (int i = 0; i < fn; i++) (fprintf)(stderr, "[s7593-flood] %d padpadpadpadpadpadpadpadpadpadpadpadpadpadpadpadpadpad\n", i);
        ultramodern::error_handling::quick_exit(__FILE__, __LINE__, "s7593_plant", 1);
    }
    printf("Switch-case out of bounds in %s at 0x%08X for jump table at 0x%08X\n", "s7450_plant", 0x80001234u, 0x800A0000u);
    exit(EXIT_FAILURE);
}
// s7460 class DP: ROGUESQ_PLANT_HOLD=<s>[,<dur_s>] positive control for a HELD frame (no crash, no exit). Once, at
// t>=<s> after the first swap, the guest thread blocks <dur_s> (default 40) inside osViSwapBuffer_recomp, so no new
// frame/gfx task is produced while the host VI thread keeps ticking. Every stall scorer (m6 fs_holds, g1e ring
// vi_stalls30s) must flag it.
static void rs64_diag_plant_hold_tick() {
    static double sec = 0, dur = 40; static bool done = false;
    static const bool on = [] {
        const char* e = getenv("ROGUESQ_PLANT_HOLD"); if (!e || !*e) return false;
        sec = atof(e); if (const char* c = strchr(e, ',')) dur = atof(c + 1);
        return sec > 0 && dur > 0;
    }();
    if (!on || done) return;
    static const auto t0 = std::chrono::steady_clock::now();
    if (std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count() < sec) return;
    done = true;
    (fprintf)(stderr, "[s7460-plant-hold] begin dur=%.1f s\n", dur); fflush(stderr);
    std::this_thread::sleep_for(std::chrono::duration<double>(dur));
    (fprintf)(stderr, "[s7460-plant-hold] end\n"); fflush(stderr);
}
static void rs64_diag_quiet_tick() {
    rs64_diag_plant_tick();
    rs64_diag_plant_exit_tick();
    rs64_diag_plant_hold_tick();
    if (rs64_diag_busy.load(std::memory_order_relaxed)) rs64_diag_spin_us(s_dq_busy_guest_us);
    if (!s_dq_stat) return;
    static const auto t0 = std::chrono::steady_clock::now(); static auto tq = t0, tb = t0, tw = t0;
    const auto now = std::chrono::steady_clock::now();
    const bool fq = s_dq_qtog > 0 && std::chrono::duration<double>(now - tq).count() >= s_dq_qtog;
    const bool fb = s_dq_btog > 0 && std::chrono::duration<double>(now - tb).count() >= s_dq_btog;
    const bool fw = !s_dq_qtog && !s_dq_btog && std::chrono::duration<double>(now - tw).count() >= 10.0;
    if (!fq && !fb && !fw) return;
    const double win = std::chrono::duration<double>(now - tw).count(); tw = now;
    uint64_t c[2], ns[2], by[2], dr[2];
    for (int i = 0; i < 2; ++i) { c[i] = s_dq_calls[i].exchange(0); ns[i] = s_dq_ns[i].exchange(0); by[i] = s_dq_bytes[i].exchange(0); dr[i] = s_dq_drop[i].exchange(0); }
    // window stats belong to the state BEFORE this flip
    (fprintf)(stderr, "[diag-quiet] win quiet=%d busy=%d t=%.3f secs=%.3f task_calls=%llu task_ms=%.3f task_bytes=%llu task_drop=%llu "
            "oth_calls=%llu oth_ms=%.3f oth_bytes=%llu oth_drop=%llu\n", rs64_diag_quiet, rs64_diag_busy.load(),
            std::chrono::duration<double>(now - t0).count(), win, (unsigned long long)c[1], ns[1] / 1e6, (unsigned long long)by[1],
            (unsigned long long)dr[1], (unsigned long long)c[0], ns[0] / 1e6, (unsigned long long)by[0], (unsigned long long)dr[0]);
    if (fq) { tq = now; rs64_diag_quiet = !rs64_diag_quiet; }
    if (fb) { tb = now; rs64_diag_busy = !rs64_diag_busy.load(); }
    if (fq || fb) (fprintf)(stderr, "[diag-quiet] flip quiet=%d busy=%d t=%.3f\n", rs64_diag_quiet, rs64_diag_busy.load(),
                          std::chrono::duration<double>(now - t0).count());
}
extern "C" void rs64_store_diag_tick(void) {
    rs64_diag_quiet_tick();
    rs64_g1e_fast_tick();
    rs64_g1e_dmem_tick();
    rs64_g1e_dmembase_tick();
    rs64_g1e_lean_tick();
    rs64_g1e_nmac_tick();
    rs64_g1e_probes_tick();
    static const double sec = [] { const char* e = getenv("ROGUESQ_STORE_DIAG_TOGGLE"); return (e && *e) ? atof(e) : 0.0; }();
    if (sec <= 0.0) return;
    static const auto t0 = std::chrono::steady_clock::now(); static auto t_flip = t0;
    const auto now = std::chrono::steady_clock::now();
    if (std::chrono::duration<double>(now - t_flip).count() < sec) return;
    t_flip = now; g_rs64_store_diag = !g_rs64_store_diag;
    fprintf(stderr, "[storediag] on=%d t=%.3f\n", g_rs64_store_diag, std::chrono::duration<double>(now - t0).count());
}
static const double g_g3d_toggle_s = [] { const char* e = getenv("ROGUESQ_G3D_LEGACY_TOGGLE"); return (e && *e) ? atof(e) : 0.0; }();
static bool g_g3d_legacy = false;
extern "C" int rs64_sdv_snap_enabled(void) { return g_spike_dmem_on || g_g3d_legacy; }
extern "C" void rs64_vld_note(uint32_t reg, uint32_t addr, const char* kind) {
    if (g_g3d_toggle_s > 0.0) {
        static uint32_t n = 0; static auto t_flip = std::chrono::steady_clock::now(); static const auto t0 = t_flip;
        if ((++n & 0xFFFFu) == 0) {
            auto now = std::chrono::steady_clock::now();
            if (std::chrono::duration<double>(now - t_flip).count() >= g_g3d_toggle_s) {
                t_flip = now; g_g3d_legacy = !g_g3d_legacy;
                fprintf(stderr, "[g3d] legacy=%d t=%.3f loads=%u\n", g_g3d_legacy ? 1 : 0, std::chrono::duration<double>(now - t0).count(), n);
            }
        }
        if (g_g3d_legacy && [] { const char* e = getenv("ROGUESQ_SPIKE_DMEM"); return e && *e && *e != '0'; }()) { g_vld_addr[reg & 31] = addr; }  // legacy arm keeps its per-load getenv
    }
    if (reg < 32 && g_spike_dmem_on) { g_vld_addr[reg] = addr; g_vld_kind[reg] = kind; }
}
extern "C" void rs64_vu_ring_vte(uint32_t reg, const uint16_t* l) { g_vte_pend_reg = reg & 31; for (int i = 0; i < 8; i++) g_vte_pend_l[i] = l[i]; }
static thread_local Rs64VuRingEnt g_vu_ring[128];
static thread_local uint32_t g_vu_ring_n = 0;
extern "C" int rs64_vu_ring_enabled(void) { return g_spike_dmem_on; }
extern "C" uint32_t rs64_vu_ring_prev_vd(void) { return g_vu_ring_n ? g_vu_ring[(g_vu_ring_n - 1) % 128].vd : 0; }
extern "C" void rs64_vu_ring_capture_prev(const uint16_t* lanes) {
    if (!g_vu_ring_n) return;
    Rs64VuRingEnt& r = g_vu_ring[(g_vu_ring_n - 1) % 128];
    for (int i = 0; i < 8; i++) r.post[i] = lanes[i];
}
extern "C" void rs64_vu_ring_push(uint32_t op, uint32_t vd, uint32_t e, const uint16_t* all) {
    Rs64VuRingEnt& r = g_vu_ring[g_vu_ring_n++ % 128];
    r.op = (uint16_t)op; r.vd = (uint16_t)vd; r.e = (uint16_t)e; r.vtr = (uint16_t)g_vte_pend_reg;
    for (int i = 0; i < 8; i++) r.vl[i] = g_vte_pend_l[i];
    for (int i = 0; i < 48; i++) r.all[i] = all[i];
    for (int i = 0; i < 8; i++) r.post[i] = 0;
    r.src = g_vld_addr[g_vte_pend_reg]; r.kind = g_vld_kind[g_vte_pend_reg];
}
static void rs64_vu_ring_dump(FILE* f) {
    static const char* const names[10] = {"VMACF","VMADH","VMADL","VMADM","VMADN","VMUDH","VMUDL","VMUDM","VMUDN","VMULF"};
    uint32_t n = g_vu_ring_n, cnt = n < 128 ? n : 128;
    for (uint32_t k = 0; k < cnt; k++) {
        const Rs64VuRingEnt& r = g_vu_ring[(n - cnt + k) % 128];
        // legacy fields (lane 1) kept for old tooling; [spike-vu8] carries all lanes.
        fprintf(f, "[spike-vu] %s vd=v%u e=%u vs1=%04X vte1=%04X preACC=%04X.%04X.%04X vt=v%u[%04X %04X %04X %04X %04X %04X %04X %04X] lastld=%s@%03X\n", names[r.op], r.vd, r.e, r.all[1], r.all[9], r.all[17], r.all[25], r.all[33], r.vtr, r.vl[0], r.vl[1], r.vl[2], r.vl[3], r.vl[4], r.vl[5], r.vl[6], r.vl[7], r.kind ? r.kind : "none", r.src & 0xFFF);
        fprintf(f, "[spike-vu8] %s vd=v%u", names[r.op], r.vd);
        static const char* const tag[6] = {"vs","vte","H","M","L","pvd"};
        for (int g = 0; g < 6; g++) { fprintf(f, " %s=", tag[g]); for (int i = 0; i < 8; i++) fprintf(f, "%04X%s", r.all[g*8+i], i < 7 ? "," : ""); }
        fprintf(f, " post="); for (int i = 0; i < 8; i++) fprintf(f, "%04X%s", r.post[i], i < 7 ? "," : "");
        fprintf(f, "\n");
    }
}
extern "C" void rs64_spike_sdv_note(uint32_t reg, uint32_t e, const uint32_t* lanes) {
    g_spike_sdv_reg = reg; g_spike_sdv_e = e;
    for (int i = 0; i < 8; i++) g_spike_sdv_lanes[i] = lanes[i];
    for (int i = 0; i < 88; i++) g_spike_sdv_snap[i] = lanes[8 + i];
}

extern "C" void rs64_m5_audio_dmem_store(uint32_t dmem_addr,
                                           uint32_t len, uint32_t value,
                                           uint32_t vector_op) {
    // s6372: RSP store watch on the spike's pinned-Y DMEM slots (0x43A/0x462) + positive control (0xB00..0xB05), gfx DMEM only.
    {
        static const bool spw = [] { const char* e = std::getenv("ROGUESQ_SPIKE_DMEM"); return e && *e && *e != '0'; }();
        if (spw && len != 0u && g_dmem_cur == dmem) {
            const uint32_t a0 = dmem_addr & 0xFFFu;
            auto hit = [&](uint32_t t) { return t >= a0 && t < a0 + len; };
            static uint32_t n43a = 0, n462 = 0, nctl = 0, nlog = 0, nfd = 0;
            const bool h43a = hit(0x43Au), h462 = hit(0x462u), hctl = hit(0xB00u);
            if (hctl) nctl++;
            if (h43a || h462) {
                if (h43a) n43a++;
                if (h462) n462++;
                auto h16 = [&](uint32_t o) { return (uint32_t)(((uint32_t)g_dmem_cur[(o & 0xFFFu) ^ 3u] << 8) | g_dmem_cur[((o + 1) & 0xFFFu) ^ 3u]); };
                const uint32_t v43a = h16(0x43Au), v462 = h16(0x462u);
                const bool fd = v43a == 0xFD57u || v462 == 0xFD57u;
                if (fd) nfd++;
                if ((fd || (n43a + n462) <= 40u) && nlog < 400u) {
                    nlog++;
                    void* ra = __builtin_return_address(0);
                    Dl_info di{}; dladdr(ra, &di);
                    fprintf(stderr, "[spike-st] dmem=%03X len=%u op=%08X val=%08X v43A=%04X v462=%04X%s ra=%p %s+0x%lx n43A=%u n462=%u ctl=%u\n",
                            a0, len, vector_op, value, v43a, v462, fd ? " FD57" : "", ra, di.dli_sname ? di.dli_sname : "?",
                            di.dli_saddr ? (unsigned long)((char*)ra - (char*)di.dli_saddr) : 0ul, n43a, n462, nctl);
                    if (vector_op == 0x53445600u)
                        fprintf(stderr, "[spike-sdv] vreg=%u e=%u lanes=%04X %04X %04X %04X %04X %04X %04X %04X\n", g_spike_sdv_reg, g_spike_sdv_e,
                                g_spike_sdv_lanes[0], g_spike_sdv_lanes[1], g_spike_sdv_lanes[2], g_spike_sdv_lanes[3],
                                g_spike_sdv_lanes[4], g_spike_sdv_lanes[5], g_spike_sdv_lanes[6], g_spike_sdv_lanes[7]);
                    if (vector_op == 0x53445600u) {
                        static const int rn[11] = {0, 1, 2, 3, 4, 5, 6, 29, -1, -2, -3};
                        for (int r = 0; r < 11; r++) {
                            if (rn[r] >= 0) fprintf(stderr, "[spike-vr] v%d=", rn[r]); else fprintf(stderr, "[spike-vr] ACC%c=", "?HML"[-rn[r]]);
                            for (int i = 0; i < 8; i++) fprintf(stderr, "%04X ", g_spike_sdv_snap[r * 8 + i]);
                            fputc('\n', stderr);
                        }
                        rs64_vu_ring_dump(stderr);
                        fprintf(stderr, "[spike-dmem60]");
                        for (uint32_t o = 0x60; o < 0x70; o += 2)
                            fprintf(stderr, " %04X", (unsigned)(((uint32_t)g_dmem_cur[o ^ 3u] << 8) | g_dmem_cur[(o + 1) ^ 3u]));
                        fputc('\n', stderr);
                    }
                }
            }
        }
    }
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SOURCE_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || len == 0u) return;

    const Rs64AudioRouteIdentity& route = g_rs64_audio_identity;
    if (!route.valid ||
        !((route.width == 1024u && route.origin == 0x00790400u) ||
          (route.width == 512u && route.origin == 0x006AB400u))) return;

    g_rs64_m5_last_dmem_writer_seq =
        g_rs64_m5_dmem_writer_seq.fetch_add(1u, std::memory_order_relaxed) + 1u;
    g_rs64_m5_last_dmem_writer_addr = dmem_addr & 0xFFFu;
    g_rs64_m5_last_dmem_writer_len = len;
    g_rs64_m5_last_dmem_writer_value = value;
    g_rs64_m5_last_dmem_writer_kind = g_rs64_audio_vector_store ? 1u : 0u;
    g_rs64_m5_last_dmem_writer_vector_op = g_rs64_audio_vector_store ? vector_op : 0u;
    g_rs64_m5_last_dmem_writer_route_ordinal = route.ordinal;
    g_rs64_m5_last_dmem_writer_fnv = 2166136261u;
    g_rs64_m5_last_dmem_writer_nonzero = 0u;
    for (uint32_t i = 0; i < len && i < 16u; ++i) {
        const uint8_t byte = g_dmem_cur[((dmem_addr + i) & 0xFFFu) ^ 3u];
        g_rs64_m5_last_dmem_writer_fnv =
            (g_rs64_m5_last_dmem_writer_fnv * 16777619u) ^ byte;
        g_rs64_m5_last_dmem_writer_nonzero += byte != 0u;
    }

    {
        std::lock_guard<std::mutex> lock(g_rs64_m5_dmem_coverage_mutex);
        const uint32_t first = dmem_addr & 0xFFFu;
        const uint32_t count = len > 0x1000u ? 0x1000u : len;
        for (uint32_t i = 0; i < count; ++i) {
            Rs64M5DmemCoverage& coverage = g_rs64_m5_dmem_coverage[(first + i) & 0xFFFu];
            coverage.sequence = g_rs64_m5_last_dmem_writer_seq;
            coverage.addr = first;
            coverage.len = len;
            coverage.kind = g_rs64_audio_vector_store ? 1u : 0u;
            coverage.vector_op = g_rs64_audio_vector_store ? vector_op : 0u;
            coverage.value = value;
            coverage.fnv = g_rs64_m5_last_dmem_writer_fnv;
            coverage.nonzero = g_rs64_m5_last_dmem_writer_nonzero;
            coverage.route_ordinal = route.ordinal;
        }
    }

    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    static bool control_seen = false;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (route.width << 24) ^ route.origin;
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
        control_seen = false;
    }
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-dmem-source-control] phase=%u width=%u origin=0x%06X "
            "dmem=0x%03X len=0x%X value=0x%08X\n",
            rs64_phase_ord(), route.width, route.origin, dmem_addr, len, value);
        std::fflush(stderr);
    }

    const uint32_t end = dmem_addr + len;
    if (dmem_addr >= 0xE48u || end <= 0x3F0u || rows >= 1024u) return;

    uint32_t fnv = 2166136261u;
    uint32_t nonzero = 0;
    for (uint32_t i = 0; i < 0xAB8u; ++i) {
        const uint8_t b = g_dmem_cur[((0x3F0u + i) & 0xFFFu) ^ 3u];
        fnv = (fnv * 16777619u) ^ b;
        nonzero += b != 0;
    }
    const uint32_t value_bytes = len > 4u ? 4u : len;
    uint32_t value_nz = 0;
    if (!g_rs64_audio_vector_store) {
        for (uint32_t i = 0; i < value_bytes; ++i) {
            value_nz += ((value >> ((value_bytes - 1u - i) * 8u)) & 0xFFu) != 0;
        }
    }
    std::fprintf(stderr,
        "[m5-dmem-source-writer] row=%u phase=%u width=%u origin=0x%06X "
        "route_ordinal=%u route_row=%u dmem=0x%03X len=0x%X kind=%s "
        "vector_op=0x%08X value=0x%08X value_nz=%u span_fnv=%08X span_nz=%u "
        "prepare_seq=%u identity_edge_seq=%u\n",
        rows, rs64_phase_ord(), route.width, route.origin, route.ordinal,
        route.row, dmem_addr, len, g_rs64_audio_vector_store ? "vector" : "scalar",
        g_rs64_audio_vector_store ? vector_op : 0u, value, value_nz, fnv, nonzero,
        route.prepare_seq, g_rs64_audio_identity_edge_seq.load());
    std::fflush(stderr);

    if (g_rs64_m5_source_window_rows < 4096u) {
        const uint32_t windows[][2] = {{0x6F0u, 0x9F0u}, {0xCB0u, 0xE48u}};
        for (uint32_t window = 0; window < 2u; ++window) {
            const uint32_t first = windows[window][0];
            const uint32_t last = windows[window][1];
            if (dmem_addr >= last || end <= first) continue;
            uint32_t exact_fnv = 2166136261u;
            uint32_t exact_nz = 0;
            for (uint32_t i = first; i < last; ++i) {
                const uint8_t b = g_dmem_cur[i ^ 3u];
                exact_fnv = (exact_fnv * 16777619u) ^ b;
                exact_nz += b != 0;
            }
            std::fprintf(stderr,
                "[m5-source-window] event=%llu op=store phase=%u width=%u "
                "origin=0x%06X route_ordinal=%u route_row=%u window=%u "
                "dmem=0x%03X len=0x%X post_fnv=%08X post_nz=%u\n",
                static_cast<unsigned long long>(g_rs64_m5_source_event++),
                rs64_phase_ord(), route.width, route.origin, route.ordinal,
                route.row, window + 2u, dmem_addr, len, exact_fnv, exact_nz);
            ++g_rs64_m5_source_window_rows;
        }
        std::fflush(stderr);
    }
    ++rows;
}

extern "C" void rs64_m5_audio_dmem_vector_store(uint32_t dmem_addr,
                                                  uint32_t len,
                                                  uint32_t vector_op) {
    g_rs64_audio_vector_store = true;
    rs64_m5_audio_dmem_store(dmem_addr, len, 0u, vector_op);
    g_rs64_audio_vector_store = false;
}

extern "C" void rs64_m5_audio_dmem_dma_write(uint32_t dmem_addr,
                                                uint32_t len) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SOURCE_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || len == 0u) return;

    const Rs64AudioRouteIdentity& route = g_rs64_audio_identity;
    if (!route.valid ||
        !((route.width == 1024u && route.origin == 0x00790400u) ||
          (route.width == 512u && route.origin == 0x006AB400u))) return;

    const uint32_t first = dmem_addr & 0xFFFu;
    const uint32_t count = len > 0x1000u ? 0x1000u : len;
    const uint64_t sequence =
        g_rs64_m5_dmem_writer_seq.fetch_add(1u, std::memory_order_relaxed) + 1u;
    uint32_t fnv = 2166136261u;
    uint32_t nonzero = 0u;
    for (uint32_t i = 0; i < count; ++i) {
        const uint8_t byte = g_dmem_cur[((first + i) & 0xFFFu) ^ 3u];
        fnv = (fnv * 16777619u) ^ byte;
        nonzero += byte != 0u;
    }

    g_rs64_m5_last_dmem_writer_seq = sequence;
    g_rs64_m5_last_dmem_writer_addr = first;
    g_rs64_m5_last_dmem_writer_len = len;
    g_rs64_m5_last_dmem_writer_value = 0u;
    g_rs64_m5_last_dmem_writer_kind = 2u;
    g_rs64_m5_last_dmem_writer_fnv = fnv;
    g_rs64_m5_last_dmem_writer_nonzero = nonzero;
    g_rs64_m5_last_dmem_writer_route_ordinal = route.ordinal;
    const bool input_window = first < 0xE48u && first + count > 0xCB0u;
    if (input_window) {
        g_rs64_m5_last_input_dmem_writer_seq = sequence;
        std::fprintf(stderr,
            "[m5-vector-order] phase=%u width=%u origin=0x%06X "
            "input_dma_seq=%llu dmem=0x%03X len=0x%X\n",
            rs64_phase_ord(), route.width, route.origin,
            static_cast<unsigned long long>(sequence), first, len);
        std::fflush(stderr);
    }

    std::lock_guard<std::mutex> lock(g_rs64_m5_dmem_coverage_mutex);
    for (uint32_t i = 0; i < count; ++i) {
        Rs64M5DmemCoverage& coverage =
            g_rs64_m5_dmem_coverage[(first + i) & 0xFFFu];
        coverage.sequence = sequence;
        coverage.addr = first;
        coverage.len = len;
        coverage.kind = 2u;
        coverage.vector_op = 0u;
        coverage.value = 0u;
        coverage.fnv = fnv;
        coverage.nonzero = nonzero;
        coverage.route_ordinal = route.ordinal;
    }
}

extern "C" void rs64_m5_field348_store(char width, uint32_t pc,
                                          uint32_t addr, uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FIELD348_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t width_n = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;

    const uint32_t phys = addr & 0x007FFFFFu;
    const uint32_t len = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
    const uint32_t value_mask = len == 1u ? 0xFFu : (len == 2u ? 0xFFFFu : 0xFFFFFFFFu);
    const uint32_t logged_value = value & value_mask;
    uint32_t value_fnv = 2166136261u;
    uint32_t value_nz = 0;
    for (uint32_t i = 0; i < len; ++i) {
        const uint32_t shift = (len - 1u - i) * 8u;
        const uint8_t b = static_cast<uint8_t>((logged_value >> shift) & 0xFFu);
        value_fnv = (value_fnv * 16777619u) ^ b;
        value_nz += b != 0;
    }

    static std::mutex mutex;
    static uint64_t store_ordinal = 0;
    static uint32_t control_phase_key[2] = {0xFFFFFFFFu, 0xFFFFFFFFu};
    static uint32_t total[2] = {0, 0};
    static uint32_t printed[2] = {0, 0};
    static uint32_t unique_n[2] = {0, 0};
    static uint32_t unique_pc[2][64] = {};
    static const uint32_t spans[2] = {0x178C80u, 0x1797B0u};
    uint64_t source_event = 0;
    std::lock_guard<std::mutex> lock(mutex);

    const uint64_t ordinal = store_ordinal++;
    const uint32_t phase = rs64_phase_ord();
    const uint32_t phase_key = (width_n << 24) ^ origin;
    const uint32_t phase_slot = width_n == 1024u ? 0u : 1u;
    const bool overlaps_field348 =
        (phys < spans[0] + 0x180u && phys + len > spans[0]) ||
        (phys < spans[1] + 0x180u && phys + len > spans[1]);
    static const bool transition_enabled = [] {
        const char* rs64_la = std::getenv("ROGUESQ_LOG_ALL"); // s7728: LOG_ALL, as the line-2716 gate
        const char* value = std::getenv("ROGUESQ_LOG_M5_SOURCE_TRANSITION");
        return (rs64_la && *rs64_la && *rs64_la != '0') || (value && value[0] && value[0] != '0');
    }();
    if (transition_enabled && overlaps_field348) {
        static uint32_t transition_rows = 0;
        if (transition_rows < 4096u) {
            std::fprintf(stderr,
                "[m5-source-transition] event=%llu op=cpu_store "
                "phase=%u width=%u origin=0x%06X route_ordinal=%u "
                "route_row=%u pc=0x%08X phys=0x%06X len=%u value=0x%08X "
                "value_fnv=%08X value_nz=%u span=%u\n",
                static_cast<unsigned long long>(g_rs64_m5_source_event++),
                phase, width_n, origin,
                g_rs64_audio_identity.valid ? g_rs64_audio_identity.ordinal : 0xFFFFFFFFu,
                g_rs64_audio_identity.valid ? g_rs64_audio_identity.row : 0xFFFFFFFFu,
                pc, phys, len, logged_value, value_fnv, value_nz,
                phys >= spans[1] ? 2u : 1u);
            std::fflush(stderr);
            ++transition_rows;
        }
    }
    if (control_phase_key[phase_slot] != phase_key &&
        !overlaps_field348) {
        control_phase_key[phase_slot] = phase_key;
        std::fprintf(stderr,
            "[field348-writer-control] ordinal=%llu phase=%u width=%u "
            "origin=0x%06X phys=0x%06X len=%u pc=0x%08X value=0x%08X\n",
            static_cast<unsigned long long>(ordinal), phase, width_n, origin,
            phys, len, pc, logged_value);
        std::fflush(stderr);
    }

    for (uint32_t i = 0; i < 2u; ++i) {
        if (phys >= spans[i] + 0x180u || phys + len <= spans[i]) continue;
        ++total[i];
        bool new_pc = true;
        for (uint32_t j = 0; j < unique_n[i]; ++j) {
            if (unique_pc[i][j] == pc) {
                new_pc = false;
                break;
            }
        }
        if (new_pc && unique_n[i] < 64u) unique_pc[i][unique_n[i]++] = pc;
        if (i == 1u && source_event == 0u) {
            source_event = g_rs64_m5_source_event++;
        }
        if (printed[i] < 512u || (new_pc && unique_n[i] <= 64u)) {
            std::fprintf(stderr,
                "[field348-writer] ordinal=%llu phase=%u width=%u "
                "origin=0x%06X span=%u phys=0x%06X len=%u pc=0x%08X "
                "value=0x%08X value_fnv=%08X value_nz=%u total=%u unique=%u "
                "source_event=%llu\n",
                static_cast<unsigned long long>(ordinal), phase, width_n, origin,
                i + 1u, phys, len, pc, logged_value, value_fnv, value_nz,
                total[i], unique_n[i],
                static_cast<unsigned long long>(source_event));
            std::fflush(stderr);
            ++printed[i];
        }
    }
}

// s4429: port-side witness for the title heap bytes. Observes only; reads
// guest RDRAM through the capture pointer and never writes it.
extern "C" void rs64_s4429_heap_probe(const char* kind, uint32_t pc,
                                      uint32_t addr, uint32_t value) {
    static const bool enabled = [] {
        const char* own = std::getenv("ROGUESQ_LOG_S4429_HEAP");
        return own && own[0] && own[0] != '0';
    }();
    if (!enabled) return;
    volatile uint8_t* base = g_recomp_rdram_for_wp_raw;
    if (!base) return;
    auto rd8 = [&](uint32_t g) -> uint32_t {
        return (g >= 0x80000000u && g < 0x80800000u) ? base[(g - 0x80000000u) ^ 3u] : 0xFFFFFFFFu;
    };
    auto rd32 = [&](uint32_t g) -> uint32_t {
        return (rd8(g) << 24) | (rd8(g + 1) << 16) | (rd8(g + 2) << 8) | rd8(g + 3);
    };
    static uint32_t total_sb = 0, total_pub = 0, rows = 0;
    static uint32_t seen_window[2] = {0, 0};
    const uint32_t w = rs64_vi_committed_width();
    const uint32_t o = rs64_vi_committed_origin() & 0x00FFFFFFu;
    auto dump = [&](const char* tag, uint32_t hdr) {
        std::fprintf(stderr,
            "[s4429-heap] %s kind=%s pc=0x%08X addr=0x%08X value=0x%08X width=%u origin=0x%06X "
            "hdr=0x%08X[%08X %08X] user=0x%08X[%08X %08X %08X %08X]\n",
            tag, kind, pc, addr, value, w, o, hdr, rd32(hdr), rd32(hdr + 4),
            hdr + 16, rd32(hdr + 16), rd32(hdr + 20), rd32(hdr + 24), rd32(hdr + 28));
        std::fflush(stderr);
    };
    if (kind[0] == 'B') {  // byte store at 0x80007670
        ++total_sb;
        const uint32_t hdrs[2] = {0x80171CD0u, 0x80173B10u};
        for (uint32_t i = 0; i < 2; ++i) {
            if (addr >= hdrs[i] && addr < hdrs[i] + 32u) {
                if (!(seen_window[i] & 1u)) {  // pre-store state, first byte of the copy
                    seen_window[i] |= 1u;
                    dump(i ? "copy-pre-B" : "copy-pre-A", hdrs[i]);
                }
                if (rows < 400u) {
                    ++rows;
                    std::fprintf(stderr, "[s4429-heap] copy-sb idx=%u addr=0x%08X value=0x%02X origin=0x%06X\n",
                                 i, addr, value & 0xFFu, o);
                }
            }
        }
        return;
    }
    // word store of a published title-table pointer
    ++total_pub;
    if (total_pub <= 64u) {
        dump(addr == 0x80149758u ? "publish-A" : "publish-B", value - 16u);
        std::fprintf(stderr, "[s4429-heap] counts sb_calls=%u publish_calls=%u\n", total_sb, total_pub);
    }
}

// s4457: last-two-writers table per guest word (0x80000000..0x80400000), armed by
// ROGUESQ_LOG_S4457. Queried by rs64_s4457_list_check at the synth list walk.
struct S4457W { uint32_t pc, val, ppc, pval; uint16_t w; };
static S4457W* g_s4457_tab = nullptr;
static uint64_t g_s4457_stores = 0;
static bool rs64_s4457_on() {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4457"); return e && e[0] && e[0] != '0'; }();
    return on;
}
extern "C" void rs64_s4457_list_check(uint8_t* rdram, uint32_t value) {
    if (!rs64_s4457_on() || !g_s4457_tab) return;
    static uint32_t ring[16]; static uint32_t rn = 0;
    static bool control = false, dumped = false;
    if (!control) {  // positive control: the list head must have a recorded writer
        control = true;
        const S4457W& h = g_s4457_tab[(0x801499B0u & 0x3FFFFFu) >> 2];
        std::fprintf(stderr, "[s4457-control] stores=%llu head_writer pc=0x%08X val=0x%08X prev_pc=0x%08X\n",
                     (unsigned long long)g_s4457_stores, h.pc, h.val, h.ppc);
    }
    {   // s4779: shadow scan of the audio node arena. A word whose LAST HOOKED store was a W but whose memory now differs was
        // modified by an unhooked writer (DMA / host memcpy / unhooked store). Control: matched count must be >0 and a scan of
        // the table-vs-memory for the LUT-agnostic 'matched' words proves the comparison works.
        static uint64_t scans = 0, matched = 0, mism = 0; static uint32_t shown = 0;
        static bool seen[0x1800] = {};
        ++scans;
        for (uint32_t a = 0x80179400u; a < 0x8017B000u; a += 4) {
            const S4457W& e = g_s4457_tab[(a & 0x3FFFFFu) >> 2];
            if (e.w != 'W') continue;
            const uint32_t p = a & 0x7FFFFFu;
            const uint32_t now = (uint32_t(rdram[(p) ^ 3]) << 24) | (uint32_t(rdram[(p + 1) ^ 3]) << 16) | (uint32_t(rdram[(p + 2) ^ 3]) << 8) | uint32_t(rdram[(p + 3) ^ 3]);
            if (now == e.val) { ++matched; continue; }
            ++mism;
            const uint32_t idx = (a - 0x80179400u) >> 2;
            if (!seen[idx] && shown < 64u) {
                seen[idx] = true; ++shown;
                std::fprintf(stderr, "[s4779-unhooked] scan=%llu at=0x%08X now=0x%08X lastw pc=0x%08X val=0x%08X prev pc=0x%08X val=0x%08X vi_w=%u phase=%u\n",
                             (unsigned long long)scans, a, now, e.pc, e.val, e.ppc, e.pval, rs64_vi_committed_width(), rs64_phase_ord());
            }
        }
        if ((scans & 0x3FFFu) == 1u) std::fprintf(stderr, "[s4779-ctl] scans=%llu matched=%llu mism=%llu shown=%u\n", (unsigned long long)scans, (unsigned long long)matched, (unsigned long long)mism, shown);
    }
    ring[rn++ & 15u] = value;
    if (dumped || value == 0 || (value >> 24) == 0x80u) return;
    dumped = true;
    const uint32_t P = ring[(rn - 2) & 15u];
    auto rd32 = [&](uint32_t g) { const uint32_t p = g & 0x7FFFFFu;
        return (uint32_t(rdram[(p) ^ 3]) << 24) | (uint32_t(rdram[(p + 1) ^ 3]) << 16) | (uint32_t(rdram[(p + 2) ^ 3]) << 8) | uint32_t(rdram[(p + 3) ^ 3]); };
    std::fprintf(stderr, "[s4457-bad] bad_next=0x%08X prev_node=0x%08X stores=%llu chain:", value, P, (unsigned long long)g_s4457_stores);
    for (uint32_t i = 0; i < 8; ++i) std::fprintf(stderr, " 0x%08X", ring[(rn - 1 - i) & 15u]);
    std::fprintf(stderr, "\n");
    {   // writer of the pointer that led to the bad node (X+0, X = node before P; or the head itself)
        const uint32_t X = ring[(rn - 3) & 15u];
        for (uint32_t pa : {X, 0x801499B0u}) {
            if (pa < 0x80000000u || pa >= 0x80400000u) continue;
            const S4457W& e = g_s4457_tab[(pa & 0x3FFFFFu) >> 2];
            std::fprintf(stderr, "[s4457-ptr] at=0x%08X now=0x%08X lastw pc=0x%08X w=%c val=0x%08X prev pc=0x%08X val=0x%08X\n",
                         pa, rd32(pa), e.pc, e.w ? char(e.w) : '-', e.val, e.ppc, e.pval);
        }
    }
    for (uint32_t o = 0; o < 0x30u; o += 4) {
        const uint32_t a = P + o;
        const S4457W& e = (P >= 0x80000000u && P < 0x80400000u) ? g_s4457_tab[(a & 0x3FFFFFu) >> 2] : S4457W{};
        std::fprintf(stderr, "[s4457-node] +0x%02X now=0x%08X lastw pc=0x%08X w=%c val=0x%08X prev pc=0x%08X val=0x%08X\n",
                     o, (P >= 0x80000000u && P < 0x80400000u) ? rd32(a) : 0u, e.pc, e.w ? char(e.w) : '-', e.val, e.ppc, e.pval);
    }
    std::fflush(stderr);
}
// s5229: byte-granular last-writer shadow for the entry-byte question. Every
// patched guest store updates the covered bytes; the entry join then compares
// the live RDRAM byte at record+0x22 against the last recorded store. A
// mismatch means the byte was written by something that is not a patched guest
// store (host memcpy/memset, DMA, unpatched file).
static uint32_t* g_s5229_pc;
static uint8_t* g_s5229_val;
static uint8_t* g_s5229_w;
static uint64_t g_s5229_calls;
static bool rs64_s5229_on() {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S5223_ENTRY_JOIN"); return e && e[0] && e[0] != '0'; }();
    return on;
}
static void rs64_s5229_store(char width, uint32_t pc, uint32_t addr, uint32_t value) {
    if (!g_s5229_pc) {
        g_s5229_pc = (uint32_t*)std::calloc(0x800000, sizeof(uint32_t));
        g_s5229_val = (uint8_t*)std::calloc(0x800000, 1);
        g_s5229_w = (uint8_t*)std::calloc(0x800000, 1);
        if (!g_s5229_pc || !g_s5229_val || !g_s5229_w) { std::fprintf(stderr, "[s7356] FATAL s5229 tables: calloc failed (host out of memory)\n"); std::fflush(stderr); std::abort(); }
    }
    ++g_s5229_calls;
    const uint32_t n = width == 'B' ? 1u : width == 'H' ? 2u : width == 'W' ? 4u : width == 'D' ? 8u : 0u;
    if (!n || addr < 0x80000000u || addr >= 0x80800000u) return;
    const uint32_t base = addr & 0x7FFFFFu;
    for (uint32_t i = 0; i < n && base + i < 0x800000u; ++i) {
        g_s5229_pc[base + i] = pc;
        g_s5229_w[base + i] = (uint8_t)width;
        g_s5229_val[base + i] = (uint8_t)(n == 1u ? value : (n == 2u ? (value >> (8u * (1u - i))) : (n == 4u ? (value >> (8u * (3u - i))) : 0xEEu)));
    }
}
// Entry-time query: bucket[origin_idx][(writer pc, width, actual byte, matches recorded)] -> count.
struct S5229Row { uint32_t pc; uint8_t w, actual, recorded, match; uint64_t n; };
static S5229Row g_s5229_rows[2][96];
static int g_s5229_nrows[2];
static uint64_t g_s5229_over[2], g_s5229_entries[2];
extern "C" void rs64_s5229_entry(int bi, uint32_t guest_addr, uint32_t actual) {
    if (bi < 0 || bi > 1 || !g_s5229_pc) return;
    const uint32_t b = guest_addr & 0x7FFFFFu;
    ++g_s5229_entries[bi];
    S5229Row key{g_s5229_pc[b], g_s5229_w[b], (uint8_t)actual, g_s5229_val[b], 0, 0};
    key.match = g_s5229_pc[b] != 0 && g_s5229_val[b] == (uint8_t)actual;
    for (int i = 0; i < g_s5229_nrows[bi]; ++i) {
        S5229Row& r = g_s5229_rows[bi][i];
        if (r.pc == key.pc && r.w == key.w && r.actual == key.actual && r.recorded == key.recorded) { ++r.n; return; }
    }
    if (g_s5229_nrows[bi] < 96) { key.n = 1; g_s5229_rows[bi][g_s5229_nrows[bi]++] = key; }
    else ++g_s5229_over[bi];
}
extern "C" void rs64_s5229_flush(int bi, const char* why) {
    if (bi < 0 || bi > 1 || !g_s5229_entries[bi]) return;
    std::fprintf(stderr, "[s5229-writer] bi=%d why=%s entries=%llu hook_calls=%llu rows=%d overflow=%llu :",
                 bi, why, (unsigned long long)g_s5229_entries[bi], (unsigned long long)g_s5229_calls,
                 g_s5229_nrows[bi], (unsigned long long)g_s5229_over[bi]);
    for (int i = 0; i < g_s5229_nrows[bi]; ++i) {
        const S5229Row& r = g_s5229_rows[bi][i];
        std::fprintf(stderr, " [pc=%08X w=%c actual=%02X rec=%02X %s n=%llu]", r.pc, r.w ? (char)r.w : '-', r.actual, r.recorded, r.match ? "match" : "MISMATCH", (unsigned long long)r.n);
    }
    std::fputc('\n', stderr);
    std::fflush(stderr);
}
// s7069: inline call-site gate read by the generated code (tools/apply_s7069_callsite_gate.py). Starts at 1; the hook clears
// it on its first call when every gate is off. ROGUESQ_DIAG_CALLSITE=0 / ROGUESQ_DIAG_GATE=0 keep it 1 (old path).
extern "C" { int g_rs64_lowfield_hook = 1; }
static bool rs64_s7069_callsite_on() {
    const char* c = std::getenv("ROGUESQ_DIAG_CALLSITE");
    return !(c && c[0] == '0');
}
extern "C" void rs64_m5_lowfield_store(char width, uint32_t pc,
                                         uint32_t addr, uint32_t value) {
    // s7068: one early-out for the whole store hook (every gate below is env-armed, all default off).
    // ROGUESQ_DIAG_GATE=0 restores the per-gate checks.
    static const bool s7068_any = [] {
        auto on = [](const char* n) { const char* e = std::getenv(n); return e && e[0] && e[0] != '0'; };
        const char* g = std::getenv("ROGUESQ_DIAG_GATE");
        if (g && g[0] == '0') return true;
        return rs64_s5229_on() || rs64_s4457_on() || on("ROGUESQ_LOG_S4472") || on("ROGUESQ_LOG_ALLOC_CALLERS") ||
               on("ROGUESQ_LOG_S4429_HEAP") || on("ROGUESQ_LOG_S4443_WATCH") || on("ROGUESQ_LOG_ALL") ||
               on("ROGUESQ_LOG_M5_LOWFIELD_WRITER");
    }();
    if (!s7068_any) { if (rs64_s7069_callsite_on()) g_rs64_lowfield_hook = 0; return; }
    if (rs64_s5229_on()) rs64_s5229_store(width, pc, addr, value);
    {   // s4472: who stores into the slot-0 request byte 0x801545FD (word 0x801545FC)? Control: slot-0 status word 0x80154620.
        static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4472"); return e && e[0] && e[0] != '0'; }();
        if (on) {
            static uint32_t nreq = 0, nctl = 0;
            const bool req = addr == 0x801545FDu || (addr == 0x801545FCu && width != 'B');
            const bool ctl = addr >= 0x80154620u && addr < 0x80154624u;
            if ((req && nreq++ < 120u) || (ctl && nctl++ < 12u)) {
                std::fprintf(stderr, "[s4472-%s] w=%c addr=0x%08X pc=0x%08X val=0x%08X vi=%u\n", req ? "req" : "ctl", width, addr, pc, value, rs64_vi_committed_width());
                std::fflush(stderr);
            }
        }
    }
    {   // s4714: who stores into the runVideoFrameTick audio-config record 0x8003757C..8B? Control: total store hook calls + stores to 0x80037590..9F neighbours.
        static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_ALLOC_CALLERS"); return e && e[0] && e[0] != '0'; }();
        if (on) {
            static uint32_t tot = 0, nrec = 0, nnb = 0;
            if ((++tot % 5000000u) == 0) { std::fprintf(stderr, "[s4714-ctl] hook calls=%u rec=%u neighbour=%u\n", tot, nrec, nnb); std::fflush(stderr); }
            if (addr >= 0x8003757Cu && addr < 0x8003758Cu) {
                if (nrec++ < 200u) { std::fprintf(stderr, "[s4714-w] w=%c addr=0x%08X pc=0x%08X val=0x%08X vi=%u\n", width, addr, pc, value, rs64_vi_committed_width()); std::fflush(stderr); }
            } else if (addr >= 0x8003758Cu && addr < 0x8003759Cu) {
                if (nnb++ < 20u) { std::fprintf(stderr, "[s4714-nb] w=%c addr=0x%08X pc=0x%08X val=0x%08X\n", width, addr, pc, value); std::fflush(stderr); }
            }
        }
    }
    if (rs64_s4457_on()) {
        if (!g_s4457_tab) g_s4457_tab = (S4457W*)std::calloc(0x100000, sizeof(S4457W));
        if (!g_s4457_tab) { std::fprintf(stderr, "[s7356] FATAL s4457 table: calloc failed (host out of memory)\n"); std::fflush(stderr); std::abort(); }
        if (addr >= 0x80000000u && addr < 0x80400000u) {
            S4457W& e = g_s4457_tab[(addr & 0x3FFFFFu) >> 2];
            e.ppc = e.pc; e.pval = e.val; e.pc = pc; e.val = value; e.w = (uint16_t)width;
            ++g_s4457_stores;
        }
        if (addr >= 0x801767C0u && addr < 0x801767E0u) {  // s4465: heap header of the 0x1E000 block (never rs_free'd, yet rs_malloc hands out inside it)
            static uint32_t hn = 0;
            if (hn++ < 60u) {
                std::fprintf(stderr, "[s4465-hdr] w=%c addr=0x%08X pc=0x%08X val=0x%08X vi=%u\n", width, addr, pc, value, rs64_vi_committed_width());
                std::fflush(stderr);
            }
        }
        if (addr >= 0x80179360u && addr < 0x80179490u && pc >= 0x80001000u && pc < 0x80002800u) {  // allocator-code stores only  // s4558: headers/bodies around the 0x80179380(900) vs 0x80179480(73728) overlap
            static uint32_t hn2 = 0;
            if (hn2++ < 400u) {
                std::fprintf(stderr, "[s4558-hdr] w=%c addr=0x%08X pc=0x%08X val=0x%08X vi=%u\n", width, addr, pc, value, rs64_vi_committed_width());
                std::fflush(stderr);
            }
        }
        if ((addr == 0x80128F08u || addr == 0x80128EF0u || addr == 0x80128F04u || addr == 0x80128F00u || addr == 0x80128EFCu) ||
            (pc == 0x8001E2C0u && (addr == 0x80179480u || addr == 0x80179510u))) {  // s4558: LUT base/count globals + clear-loop writes into the audio range
            static uint32_t hn3 = 0, hn3b = 0;
            if (pc == 0x8001E2C0u ? hn3b++ < 12u : hn3++ < 80u) {
                std::fprintf(stderr, "[s4558-lut] w=%c addr=0x%08X pc=0x%08X val=0x%08X vi=%u\n", width, addr, pc, value, rs64_vi_committed_width());
                std::fflush(stderr);
            }
        }
        if (addr >= 0x801794F0u && addr < 0x80179530u) {  // s4559: every store (any pc) into the audio list node range, vi-stamped, interleaved with rs-malloc/rs-free lines
            static uint32_t hn4 = 0;
            if (hn4++ < 300u) {
                std::fprintf(stderr, "[s4559-node] w=%c addr=0x%08X pc=0x%08X val=0x%08X vi=%u\n", width, addr, pc, value, rs64_vi_committed_width());
                std::fflush(stderr);
            }
        }
        if (addr == 0x800375A4u || addr == 0x8010FCB0u) {  // s4560b: every store (any pc) to the mode pointer 0x8010FCB0 and the +0x44 flag word of mode struct 0x80037560 (bit 0x80 blocks the flags=4 scratch heap; 0x140 at VI 640 -> 0x2C0 at VI 1024)
            static uint32_t hn5 = 0;
            if (hn5++ < 400u) {
                std::fprintf(stderr, "[s4560-reg] w=%c addr=0x%08X pc=0x%08X val=0x%08X vi=%u\n", width, addr, pc, value, rs64_vi_committed_width());
                std::fflush(stderr);
            }
        }
        if (pc == 0x80085424u && width == 'W') {  // s4462: every store of the caller-supplied SND pointer in the sorted-table insert
            static uint32_t n = 0, inpool = 0;
            ++n;
            const bool ip = value >= 0x80193B00u && value < 0x80194C00u;
            if (ip) ++inpool;
            if (n <= 40u || (ip && inpool <= 40u)) {
                const S4457W& o = g_s4457_tab[(value & 0x3FFFFFu) >> 2];
                const S4457W& h = g_s4457_tab[(0x801499B0u & 0x3FFFFFu) >> 2];
                std::fprintf(stderr, "[s4462-ins] n=%u addr=0x%08X val=0x%08X in_pool_range=%d inpool_total=%u vi=%u val_target_lastwriter_pc=0x%08X head_val=0x%08X\n",
                             n, addr, value, ip ? 1 : 0, inpool, rs64_vi_committed_width(), (value >= 0x80000000u && value < 0x80400000u) ? o.pc : 0u, h.val);
                std::fflush(stderr);
            }
        }
        if (pc == 0x8008F690u || pc == 0x8008F6A4u) {  // s4463: buildSongDecodeBufferRing rs_malloc results (node block / 0x100 buffer block)
            std::fprintf(stderr, "[s4463-poolalloc] pc=0x%08X ptr=0x%08X vi=%u\n", pc, value, rs64_vi_committed_width());
            std::fflush(stderr);
        }
        if (pc == 0x8008F6F4u) {  // s4463: one store per node after the first; count + addresses = pool node-block extent
            static uint32_t nn = 0, firstA = 0;
            if (nn++ == 0) firstA = addr;
            if ((nn & 0x3Fu) == 0 || nn <= 2u) {
                std::fprintf(stderr, "[s4463-poolnodes] n=%u first_store_addr=0x%08X last_store_addr=0x%08X vi=%u\n", nn, firstA, addr, rs64_vi_committed_width());
                std::fflush(stderr);
            }
        }
        if (pc == 0x80085424u && width == 'W') {  // s4463: min/max of the inserted pointers
            static uint32_t mn = 0xFFFFFFFFu, mx = 0, cnt = 0;
            if (value < mn) mn = value;
            if (value > mx) mx = value;
            if ((++cnt & 0x3Fu) == 0 || cnt == 1u)
                std::fprintf(stderr, "[s4463-insrange] cnt=%u min=0x%08X max=0x%08X vi=%u\n", cnt, mn, mx, rs64_vi_committed_width());
        }
        if (addr == 0x801499B0u && value != 0 && width == 'W') {  // s4459: head set non-zero -> who last wrote the pool-node words
            static uint32_t hn = 0;
            if (hn++ < 6u) {
                std::fprintf(stderr, "[s4459-headset] n=%u pc=0x%08X val=0x%08X vi=%u words:", hn, pc, value, rs64_vi_committed_width());
                for (uint32_t a : {0x80193C18u, 0x80193C20u, 0x80193C34u, 0x80193C48u, 0x80193C5Cu, 0x80193C70u}) {
                    const S4457W& e = g_s4457_tab[(a & 0x3FFFFFu) >> 2];
                    std::fprintf(stderr, " [%X pc=%X w=%c]", a & 0xFFFFu, e.pc, e.w ? char(e.w) : '-');
                }
                std::fprintf(stderr, "\n"); std::fflush(stderr);
            }
        }
        if (width == 'W' && value >= 0x80193C10u && value <= 0x80193C20u) {  // s4460: writer of a node-8-ish link value; 0x...C20 = positive control (legit head value)
            static uint32_t nbad = 0, nctl = 0;
            const bool ctl = value == 0x80193C20u;
            if (ctl ? nctl++ < 8u : nbad++ < 20u) {
                std::fprintf(stderr, "[s4460-%s] n=%u pc=0x%08X addr=0x%08X val=0x%08X vi=%u\n", ctl ? "ctl" : "linkval",
                             ctl ? nctl : nbad, pc, addr, value, rs64_vi_committed_width());
                std::fflush(stderr);
            }
        }
        if (pc == 0x80061520u && width == 'B') {  // s4459: loadCharTextureSet 256-byte 0xFF-fill table loop
            static uint32_t last = 0, tables = 0, lines = 0, overlap = 0;
            if (addr != last + 1u) {
                ++tables;
                const bool ov = addr < 0x80194C00u && addr + 0x100u > 0x80193B00u;
                if (ov) ++overlap;
                if (lines < 80u && (ov || tables <= 12u)) {
                    ++lines;
                    const S4457W& h = g_s4457_tab[(0x801499B0u & 0x3FFFFFu) >> 2];
                    std::fprintf(stderr, "[s4459-tbl] n=%u base=0x%08X overlap_pool=%d overlaps_total=%u stores=%llu head_val=0x%08X head_pc=0x%08X vi=%u\n",
                                 tables, addr, ov ? 1 : 0, overlap, (unsigned long long)g_s4457_stores, h.val, h.pc, rs64_vi_committed_width());
                    if (ov) {
                        std::fprintf(stderr, "[s4459-tblpool] words:");
                        for (uint32_t a : {0x80193C18u, 0x80193C20u, 0x80193C34u, 0x80193C48u, 0x80193C5Cu, 0x80193C70u}) {
                            const S4457W& e = g_s4457_tab[(a & 0x3FFFFFu) >> 2];
                            std::fprintf(stderr, " [%X pc=%X w=%c]", a & 0xFFFFu, e.pc, e.w ? char(e.w) : '-');
                        }
                        std::fprintf(stderr, "\n");
                    }
                    std::fflush(stderr);
                }
            }
            last = addr;
        }
    }
    if (pc == 0x80007670u) rs64_s4429_heap_probe("B", pc, addr, value);
    {   // s4443: store watch on the pool-tail next word (and its +0x18 neighbour);
        // 0x801F9CE0 (init-written) is the positive control. Observes only.
        static const bool wen = [] {
            const char* e = std::getenv("ROGUESQ_LOG_S4443_WATCH");
            return e && e[0] && e[0] != '0';
        }();
        if (wen) {
            const uint32_t len = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
            static const uint32_t wa[3] = {0x801FB3F0u, 0x801FB408u, 0x801F9CE0u};
            static uint32_t wn[3] = {0, 0, 0};
            for (int i = 0; i < 3; ++i) {
                if (addr < wa[i] + 4u && addr + len > wa[i] && wn[i] < 200u) {
                    ++wn[i];
                    std::fprintf(stderr,
                        "[s4443-watch] %c%d n=%u w=%c pc=0x%08X addr=0x%08X value=0x%08X vi=%u\n",
                        i == 2 ? 'C' : 'W', i, wn[i], width, pc, addr, value,
                        rs64_vi_committed_width());
                    std::fflush(stderr);
                }
            }
        }
    }
    static int enabled = -1;
    static uint32_t control = 0;
    static uint32_t rows = 0;
    if (enabled < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_LOWFIELD_WRITER");
        enabled = ((all && all[0] && all[0] != '0') ||
                   (own && own[0] && own[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t width_n = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width_n == 1024u && origin == 0x00790400u) ||
          (width_n == 512u && origin == 0x006AB400u))) return;

    const uint32_t phys = addr & 0x007FFFFFu;
    const uint32_t len = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
    const uint32_t logged_value = value & (len == 1u ? 0xFFu :
                                           (len == 2u ? 0xFFFFu : 0xFFFFFFFFu));
    if (!control) {
        std::fprintf(stderr,
            "[m5-lowfield-writer-control] phase=%u width=%u origin=0x%06X "
            "pc=0x%08X phys=0x%06X len=%u value=0x%08X\n",
            rs64_phase_ord(), width_n, origin, pc, phys, len, logged_value);
        std::fflush(stderr);
        control = 1;
    }
    if (phys >= 0x20u && phys < 0x31u && rows < 4096u) {
        std::fprintf(stderr,
            "[m5-lowfield-writer] row=%u phase=%u width=%u origin=0x%06X "
            "pc=0x%08X addr=0x%08X phys=0x%06X len=%u value=0x%08X\n",
            rows++, rs64_phase_ord(), width_n, origin, pc, addr, phys, len,
            logged_value);
        std::fflush(stderr);
    }
}

extern "C" void rs64_s4938_aux_store(char width, uint32_t pc,
                                      uint32_t addr, uint32_t value,
                                      uint32_t s0, uint32_t s1) {
    static const bool enabled = [] {
        const char* e = std::getenv("ROGUESQ_LOG_S4938_AUX_JOIN");
        return e && e[0] && e[0] != '0';
    }();
    if (!enabled) return;
    const uint32_t width_vi = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width_vi != 512u && width_vi != 1024u) return;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (width_vi << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        rows = 0;
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
                 "[s4938-aux-store] row=%u phase=%u width=%u origin=0x%06X"
                 " pc=0x%08X type=%c addr=0x%08X value=0x%08X"
                 " s0=0x%08X s1=0x%08X\n",
                 rows++, rs64_phase_ord(), width_vi, origin, pc, width, addr,
                 value, s0, s1);
    std::fflush(stderr);
}

extern "C" void rs64_m5_status_table_store(uint8_t* rdram, uint32_t pc,
                                               uint32_t addr, uint32_t old_value,
                                               uint32_t new_value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATUS_TABLE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t phys = addr & 0x007FFFFFu;
    if (phys < 0x154620u || phys >= 0x168DB0u || ((phys - 0x154620u) % 0x1228u) != 0u)
        return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u && origin == 0x00790400u) ||
                        (width == 512u && origin == 0x006AB400u);
    static uint32_t control = 0;
    static uint32_t rows = 0;
    if (!control) {
        std::fprintf(stderr,
                     "[m5-status-store-control] phase=%u width=%u origin=0x%06X pc=0x%08X addr=0x%08X old=0x%02X new=0x%02X\n",
                     rs64_phase_ord(), width, origin, pc, addr, old_value & 0xFFu, new_value & 0xFFu);
        std::fflush(stderr);
        control = 1;
    }
    if (!target || rows >= 2048u) return;
    const uint32_t slot = (phys - 0x154620u) / 0x1228u;
    std::fprintf(stderr,
                 "[m5-status-store] row=%u phase=%u width=%u origin=0x%06X pc=0x%08X addr=0x%08X slot=%u old=0x%02X new=0x%02X thr=%d ra=0x%08X\n",
                 rows++, rs64_phase_ord(), width, origin, pc, addr, slot,
                 old_value & 0xFFu, new_value & 0xFFu,
                 rogue_current_thread_id(rdram), g_rs64_last_guest_pc ? g_rs64_last_guest_pc : 0u);
    std::fflush(stderr);
}

extern "C" void rs64_m5_spin2_gate_store(char width, uint32_t pc,
                                           uint32_t addr, uint32_t value) {
    static int enabled = -1;
    static uint32_t rows = 0;
    if (enabled < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_WAITMUSYX_SPIN2");
        enabled = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!enabled || width != 'B') return;
    if ((addr & 0x1FFFFFFCu) != 0x0014974Cu || rows >= 256u) return;
    const uint32_t vi = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (vi == 1024u && origin == 0x00790400u) ||
                        (vi == 512u && origin == 0x006AB400u);
    if (!target) return;
    std::fprintf(stderr,
        "[waitmusyx-spin2-writer] row=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X addr=0x%08X phys=0x%06X value=0x%02X host_thr=%llu\n",
        rows++, rs64_phase_ord(), vi, origin, pc, addr, addr & 0x1FFFFFFFu,
        value & 0xFFu,
        static_cast<unsigned long long>(std::hash<std::thread::id>{}(
            std::this_thread::get_id())));
    std::fflush(stderr);
}

extern "C" void rs64_m5_field348_candidate_store(uint32_t writer_pc,
                                                     char width,
                                                     uint32_t store_pc,
                                                     uint32_t addr,
                                                     uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FIELD348_CANDIDATES");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t width_n = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width_n == 1024u && origin == 0x00790400u) ||
          (width_n == 512u && origin == 0x006AB400u))) return;

    const uint32_t phys = addr & 0x007FFFFFu;
    const uint32_t len = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
    const uint32_t value_mask = len == 1u ? 0xFFu :
                                (len == 2u ? 0xFFFFu : 0xFFFFFFFFu);
    const uint32_t logged_value = value & value_mask;
    uint32_t value_nz = 0;
    for (uint32_t i = 0; i < len; ++i) {
        const uint32_t shift = (len - 1u - i) * 8u;
        value_nz += ((logged_value >> shift) & 0xFFu) != 0;
    }

    const uint32_t span =
        (phys < 0x178E00u && phys + len > 0x178C80u) ? 1u :
        ((phys < 0x179A48u && phys + len > 0x1797B0u) ? 2u : 0u);
    const uint32_t route_ordinal = g_rs64_audio_identity.valid ?
        g_rs64_audio_identity.ordinal : 0xFFFFFFFFu;
    const uint32_t route_row = g_rs64_audio_identity.valid ?
        g_rs64_audio_identity.row : 0xFFFFFFFFu;

    static std::mutex mutex;
    static uint64_t store_ordinal = 0;
    static uint32_t phase_row[2] = {};
    static bool cap_reported[2] = {};
    std::lock_guard<std::mutex> lock(mutex);

    const uint64_t ordinal = store_ordinal++;
    const uint32_t slot = width_n == 1024u ? 0u : 1u;
    const uint32_t row = phase_row[slot]++;
    if (row < 65536u) {
        std::fprintf(stderr,
            "[field348-candidate] ordinal=%llu row=%u phase=%u width=%u "
            "origin=0x%06X route_ordinal=%u route_row=%u "
            "writer_pc=0x%08X store_pc=0x%08X width_code=%c "
            "addr=0x%08X phys=0x%06X len=%u value=0x%08X value_nz=%u "
            "span=%u\n",
            static_cast<unsigned long long>(ordinal), row, rs64_phase_ord(),
            width_n, origin, route_ordinal, route_row, writer_pc, store_pc,
            width, addr, phys, len, logged_value, value_nz, span);
        std::fflush(stderr);
    } else if (!cap_reported[slot]) {
        cap_reported[slot] = true;
        std::fprintf(stderr,
            "[field348-candidate-cap] width=%u origin=0x%06X row=%u "
            "cap=65536\n", width_n, origin, row);
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_field348_memset(uint32_t dst, uint32_t fill,
                                           uint32_t len, uint32_t ra,
                                           uint32_t guest_pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FIELD348_MEMSET");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t static_callsite = g_rs64_m5_field348_static_callsite;
    g_rs64_m5_field348_static_callsite = 0;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;

    const uint32_t phys = dst & 0x007FFFFFu;
    const uint64_t end = static_cast<uint64_t>(phys) + len;
    const bool overlap_1 = len != 0u && phys < 0x178E00u && end > 0x178C80u;
    const bool overlap_2 = len != 0u && phys < 0x179A48u && end > 0x1797B0u;
    const uint32_t span = overlap_1 ? 1u : (overlap_2 ? 2u : 0u);
    const uint32_t slot = width == 1024u ? 0u : 1u;

    static std::mutex mutex;
    static uint64_t call_ordinal = 0;
    static uint32_t phase_rows[2] = {};
    static bool control_seen[2] = {};
    std::lock_guard<std::mutex> lock(mutex);

    const uint64_t ordinal = call_ordinal++;
    const uint32_t row = phase_rows[slot]++;
    const uint32_t callsite = ra >= 8u ? ra - 8u : 0u;
    static const bool transition_enabled = [] {
        const char* rs64_la = std::getenv("ROGUESQ_LOG_ALL"); // s7728: LOG_ALL, as the line-2716 gate
        const char* value = std::getenv("ROGUESQ_LOG_M5_SOURCE_TRANSITION");
        return (rs64_la && *rs64_la && *rs64_la != '0') || (value && value[0] && value[0] != '0');
    }();
    if (transition_enabled && span != 0u) {
        static uint32_t transition_rows = 0;
        if (transition_rows < 4096u) {
            std::fprintf(stderr,
                "[m5-source-transition] event=%llu op=memset "
                "phase=%u width=%u origin=0x%06X route_ordinal=%u "
                "route_row=%u dst=0x%08X phys=0x%06X fill=0x%02X len=0x%X "
                "span=%u ra=0x%08X callsite=0x%08X guest_pc=0x%08X\n",
                static_cast<unsigned long long>(g_rs64_m5_source_event++),
                rs64_phase_ord(), width, origin,
                g_rs64_audio_identity.valid ? g_rs64_audio_identity.ordinal : 0xFFFFFFFFu,
                g_rs64_audio_identity.valid ? g_rs64_audio_identity.row : 0xFFFFFFFFu,
                dst, phys, fill & 0xFFu, len, span, ra, callsite, guest_pc);
            std::fflush(stderr);
            ++transition_rows;
        }
    }
    if (span == 0u && !control_seen[slot]) {
        control_seen[slot] = true;
        std::fprintf(stderr,
            "[field348-memset-control] ordinal=%llu row=%u phase=%u "
            "width=%u origin=0x%06X dst=0x%08X phys=0x%06X fill=0x%02X "
            "len=0x%X span=0 ra=0x%08X callsite=0x%08X static_callsite=0x%08X "
            "guest_pc=0x%08X\n",
            static_cast<unsigned long long>(ordinal), row, rs64_phase_ord(),
            width, origin, dst, phys, fill & 0xFFu, len, ra, callsite,
            static_callsite, guest_pc);
        std::fflush(stderr);
    }
    if (row >= 512u) return;
    std::fprintf(stderr,
        "[field348-memset] ordinal=%llu row=%u phase=%u width=%u "
        "origin=0x%06X dst=0x%08X phys=0x%06X fill=0x%02X len=0x%X "
        "span=%u ra=0x%08X callsite=0x%08X static_callsite=0x%08X "
        "guest_pc=0x%08X\n",
        static_cast<unsigned long long>(ordinal), row, rs64_phase_ord(),
        width, origin, dst, phys, fill & 0xFFu, len, span, ra, callsite,
        static_callsite, guest_pc);
    std::fflush(stderr);
}

extern "C" void rs64_audio_image_stage(uint32_t stage, uint8_t* rdram,
                                         uint32_t r2, uint32_t field348,
                                         uint32_t field44, uint32_t dest) {
    const Rs64AudioRouteIdentity& route = g_rs64_audio_identity;
    rs64_m5_identity_edge("stage-observe", route,
                          route.valid ? route.prepare_seq : g_rs64_audio_last_prepare_seq,
                          g_rs64_audio_identity_edge_seq.load(std::memory_order_relaxed),
                          rs64_phase_ord(), rs64_vi_committed_width(),
                          rs64_vi_committed_origin());
    if (stage <= 3u) {
        static const bool capture_enabled = [] {
            const char* own = std::getenv("ROGUESQ_LOG_M5_STAGE_CALLS");
            return own && own[0] && own[0] != '0';
        }();
        static std::mutex capture_mutex;
        static uint32_t capture_phase = UINT32_MAX;
        static uint32_t capture_count[4] = {};
        if (capture_enabled) {
            std::lock_guard<std::mutex> lock(capture_mutex);
            const uint32_t phase = rs64_phase_ord();
            if (phase != capture_phase) {
                capture_phase = phase;
                std::fill(std::begin(capture_count), std::end(capture_count), 0u);
            }
            if (capture_count[stage] < 8u) {
                const uint32_t ordinal = capture_count[stage]++;
                std::fprintf(stderr,
                    "[m5-stage-call] ordinal=%u stage=%u route_valid=%u arm=%s "
                    "route_ordinal=%u route_row=%u prepare_seq=%u phase=%u "
                    "width=%u origin=0x%06X\n",
                    ordinal, stage, route.valid ? 1u : 0u, route.arm,
                    route.ordinal, route.row,
                    route.valid ? route.prepare_seq : g_rs64_audio_last_prepare_seq,
                    phase, route.valid ? route.width : rs64_vi_committed_width(),
                    route.valid ? route.origin : rs64_vi_committed_origin());
                std::fflush(stderr);
            }
        }
    }
    if (!route.valid ||
        !((route.width == 1024u && route.origin == 0x00790400u) ||
          (route.width == 512u && route.origin == 0x006AB400u))) return;

    uint32_t dmem_a = 0, dmem_b = 0, len_a = 0, len_b = 0;
    uint32_t dest_len = 0;
    switch (stage) {
    case 0: dmem_a = 0xCC0; len_a = 0x180; break;
    case 1: dmem_a = 0x3F0; len_a = 0x180; dmem_b = 0x570; len_b = 0x180; break;
    case 2: dmem_a = 0x6F0; len_a = 0x300; dest_len = 0x300; break;
    case 3: dmem_a = 0xCB0; len_a = 0x198; dest_len = 0x198; break;
    default: return;
    }

    uint32_t fnv_a = 0, nz_a = 0, fnv_b = 0, nz_b = 0;
    const uint32_t task_data_ptr = s_pending_audio_task == nullptr ?
        0u : static_cast<uint32_t>(s_pending_audio_task->t.data_ptr);
    const uint32_t task_data_size = s_pending_audio_task == nullptr ?
        0u : static_cast<uint32_t>(s_pending_audio_task->t.data_size);
    const uint64_t latest_generation =
        g_m5_latest_audio_generation.load(std::memory_order_acquire);
    const uint32_t latest_route_seq =
        g_m5_latest_audio_route_seq.load(std::memory_order_acquire);
    const uint32_t latest_route_ordinal =
        g_m5_latest_audio_route_ordinal.load(std::memory_order_acquire);
    const uint32_t latest_route_row =
        g_m5_latest_audio_route_row.load(std::memory_order_acquire);
    if (len_a) rs64_audio_hash_dmem(dmem_a, len_a, fnv_a, nz_a);
    if (len_b) rs64_audio_hash_dmem(dmem_b, len_b, fnv_b, nz_b);
    uint32_t field348_fnv = 2166136261u, field348_nz = 0;
    bool field348_valid = false;
    rs64_audio_hash_rdram(rdram, field348 & 0x007FFFFFu, 0x180,
                          field348_fnv, field348_nz, field348_valid);
    uint32_t dest_fnv = 2166136261u, dest_nz = 0;
    bool dest_valid = false;
    if (dest_len) {
        rs64_audio_hash_rdram(rdram, dest & 0xFFFFF8u, dest_len,
                               dest_fnv, dest_nz, dest_valid);
    }
    uint32_t dma_fnv_a = fnv_a, dma_nz_a = nz_a;
    if (stage >= 2 && dest_valid) {
        const uint32_t phys = (dest & 0xFFFFF8u) & 0x007FFFFFu;
        const char* window = nullptr;
        uint32_t slot = 0;
        if (phys == 0x167050u && dest_len == 0x300u) {
            window = "167050";
            slot = 0;
        } else if (phys == 0x1935E0u && dest_len == 0x198u) {
            window = "1935E0";
            slot = 1;
        } else if (phys == 0x166D50u && dest_len == 0x300u) {
            window = "166D50";
            slot = 2;
        }
        static const bool capture_enabled = [] {
            const char* all = std::getenv("ROGUESQ_LOG_ALL");
            const char* own = std::getenv("ROGUESQ_LOG_M5_STAGE_BYTES");
            return (all && all[0] && all[0] != '0') ||
                   (own && own[0] && own[0] != '0');
        }();
        static uint32_t capture_count[3] = {};
        if (capture_enabled && window != nullptr && capture_count[slot] < 8u) {
            char source_sample[49] = {};
            char sample[49] = {};
            const uint32_t sample_len = dest_len < 16u ? dest_len : 16u;
            const uint32_t source_len = len_a < 16u ? len_a : 16u;
            for (uint32_t i = 0; i < source_len; ++i) {
                const uint8_t b = g_dmem_cur[((dmem_a + (i ^ 3u)) & 0xFFFu) ^ 3u];
                std::snprintf(source_sample + i * 3u, 4u, "%02X%s", b,
                              i + 1u == source_len ? "" : " ");
            }
            for (uint32_t i = 0; i < sample_len; ++i) {
                std::snprintf(sample + i * 3u, 4u, "%02X%s", rdram[(phys + i) ^ 3u],
                              i + 1u == sample_len ? "" : " ");
            }
            ++capture_count[slot];
            std::fprintf(stderr,
                "[m5-stage-bytes] arm=%s ordinal=%u row=%u phase=%u width=%u "
                "origin=0x%06X stage=%u window=%s phys=0x%06X len=0x%X "
                "source=0x%03X source_len=0x%X source_nz=%u source_fnv=%08X "
                "capture_nz=%u capture_fnv=%08X retained_nz=%u "
                "retained_fnv=%08X exact=%u source_sample=%s sample=%s\n",
                route.arm, route.ordinal, route.row, route.phase, route.width,
                route.origin, stage, window, phys, dest_len, dmem_a, len_a,
                nz_a, fnv_a, dest_nz, dest_fnv, dest_nz, dest_fnv, 1u,
                source_sample, sample);
            std::fflush(stderr);
        }
    }
    if (stage >= 2) {
        rs64_audio_hash_dmem_dma(dmem_a, len_a, dma_fnv_a, dma_nz_a);
        rs64_audio_join_image_stage(
            route.arm, route.ordinal, route.row, route.phase, route.width,
            route.origin, stage, (dest & 0xFFFFF8u) & 0x007FFFFFu, dest_len,
            dma_fnv_a, dma_nz_a,
            dest_valid ? 1u : 0u, task_data_ptr,
            s_pending_audio_generation, s_pending_audio_thread_id,
            rs64_m5_identity_thread_id(), latest_generation, latest_route_seq,
            latest_route_ordinal, latest_route_row);
    }
    if (stage >= 2) {
        uint32_t queue_phase = 0, queue_width = 0, queue_origin = 0;
        if (rs64_m5_audio_host_probe_enabled(queue_phase, queue_width,
                                             queue_origin)) {
            uint32_t callback_seq = 0;
            uint64_t callback_time_us = 0;
            const bool callback_order = rs64_m5_callback_order_event(
                queue_width, queue_origin, callback_seq, callback_time_us);
            const uint64_t callback_thread = rs64_m5_callback_host_thread();
            std::fprintf(stderr,
                "[m5-image-queue] arm=%s stage=%u phase=%u width=%u "
                "origin=0x%06X route_ordinal=%u route_row=%u "
                "callback_source=image_stage callback_thread=%llu "
                "queued_bytes=%u pcm_consumers_seen=%u callback_seq=%u "
                "callback_t_us=%llu callback_order=%u\n",
                route.arm, stage, queue_phase, queue_width, queue_origin,
                route.ordinal, route.row,
                static_cast<unsigned long long>(callback_thread),
                rs64_m5_audio_queue_snapshot(),
                rs64_m5_pcm_consumer_count(), callback_seq,
                static_cast<unsigned long long>(callback_time_us),
                callback_order ? 1u : 0u);
            std::fflush(stderr);
        }
    }
    std::fprintf(stderr,
        "[audtask-image-stage] arm=%s ordinal=%u row=%u phase=%u width=%u"
        " origin=0x%06X stage=%u r2=0x%03X field348=0x%08X field44=0x%08X"
        " dest=0x%08X dmem_a=0x%03X len_a=0x%X fnv_a=%08X nz_a=%u"
        " dmem_b=0x%03X len_b=0x%X fnv_b=%08X nz_b=%u"
        " source_event=%llu"
        " task_data_ptr=0x%08X task_data_size=0x%X task_generation=%llu"
        " handoff_thread=%u event_thread=%u latest_generation=%llu"
        " latest_route_seq=%u latest_route_ordinal=%u latest_route_row=%u"
        " field348_fnv=%08X field348_nz=%u field348_valid=%u"
        " dma_fnv_a=%08X dma_nz_a=%u dest_valid=%u dest_fnv=%08X dest_nz=%u\n",
        route.arm, route.ordinal, route.row, route.phase, route.width,
        route.origin, stage, r2, field348, field44, dest, dmem_a, len_a,
        fnv_a, nz_a, dmem_b, len_b, fnv_b, nz_b,
        static_cast<unsigned long long>(g_rs64_m5_last_source_event),
        task_data_ptr,
        task_data_size,
        static_cast<unsigned long long>(s_pending_audio_generation),
        s_pending_audio_thread_id, rs64_m5_identity_thread_id(),
        static_cast<unsigned long long>(latest_generation), latest_route_seq,
        latest_route_ordinal, latest_route_row,
        field348_fnv, field348_nz,
        field348_valid ? 1u : 0u, dma_fnv_a, dma_nz_a,
        dest_valid ? 1u : 0u, dest_fnv, dest_nz);
    std::fflush(stderr);
}

static void rs64_log_audio_return(const char* arm, RspExitReason reason) {
    if (!rs64_audio_probe_enabled()) return;
    if (!g_rs64_audio_identity.valid) rs64_audio_route_prepare(arm);
    if (!g_rs64_audio_identity.valid) return;
    const Rs64AudioRouteIdentity route = g_rs64_audio_identity;
    if (route.row < 256 || (route.row % 128) == 0) {
        fprintf(stderr,
                "[audio-return] arm=%s phase=%u width=%u origin=0x%06X ordinal=%u row=%u exit=%d\n",
                arm, route.phase, route.width, route.origin, route.ordinal,
                route.row, (int)reason);
        fflush(stderr);
    }
    rs64_audio_join_image_complete(route.arm, route.ordinal, route.row,
                                   route.phase, route.width, route.origin);
    rs64_audio_route_set(arm, route.phase, route.width, route.origin,
                         route.ordinal, route.row,
                         static_cast<int>(reason));
    rs64_audio_join_m5_event(
        "route-context", 0x52544358u, 1u, arm, route.phase, route.width,
        route.origin, route.ordinal, route.row, 0u, 0u,
        static_cast<uint32_t>(s_pending_audio_generation),
        static_cast<uint32_t>(s_pending_audio_generation >> 32),
        static_cast<uint32_t>(reason), 0u);
    const uint32_t clear_seq = g_rs64_audio_identity_edge_seq.fetch_add(
        1, std::memory_order_relaxed);
    rs64_m5_identity_edge("return-clear", route, route.prepare_seq, clear_seq,
                          rs64_phase_ord(), rs64_vi_committed_width(),
                          rs64_vi_committed_origin());
    g_rs64_audio_identity.valid = false;
}

static void rs64_audio_source_objects(uint8_t* rdram, const OSTask* task);

static RspExitReason musyx_stub_probe(uint8_t* rdram, uint32_t ucode_addr) {
    rs64_audio_route_prepare("musyx_stub");
    rs64_m5_task_handoff(s_pending_audio_task);
    rs64_audio_source_objects(rdram, s_pending_audio_task);
    const RspExitReason reason = musyx_stub(rdram, ucode_addr);
    rs64_log_audio_return("musyx_stub", reason);
    return reason;
}

static void rs64_audio_source_objects(uint8_t* rdram, const OSTask* task) {
    static const bool enabled = [] {
        const char* value = std::getenv("ROGUESQ_LOG_AUDIO_OBJECTS");
        return value && value[0] && value[0] != '0';
    }();
    if (!enabled || rdram == nullptr || task == nullptr) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    if (!((width == 1024 && origin == 0x790400) ||
          (width == 512 && origin == 0x6AB400))) return;
    static uint32_t rows[2] = {};
    uint32_t row = rows[width == 512]++;
    if (row >= 8 && (row % 128 != 0 || row >= 4096)) return;
    auto word = [rdram](uint32_t addr) {
        uint32_t value;
        std::memcpy(&value, rdram + (addr & 0x7FFFFC), sizeof(value));
        return value;
    };
    const uint32_t data = static_cast<uint32_t>(task->t.data_ptr) & 0x1FFFFFFF;
    const uint32_t count = static_cast<uint32_t>(task->t.data_size);
    std::fprintf(stderr, "[audio-objects-task] width=%u origin=%08X row=%u ucode=%08X data=%08X count=%u\n",
                 width, origin, row, (uint32_t)task->t.ucode, data, count);
    if (count > 8 || data > 0x800000 || count * 0xA10 > 0x800000 - data) return;
    for (uint32_t frame = 0; frame < count; frame++) {
        const uint32_t base = data + frame * 0xA10;
        const uint32_t state = word(base + 8) & 0x1FFFFFFF;
        uint32_t nz = 0, active = 0, output = 0;
        const bool valid = state <= 0x800000 - 0x298;
        if (valid) for (uint32_t i = 0; i < 0x298; i++) nz += rdram[(state + i) ^ 3] != 0;
        for (uint32_t voice = 0; voice < 32; voice++) {
            uint32_t v = base + 0x10 + voice * 0x50;
            output = word(v + 0x44);
            if ((word(v + 0x2C) >> 16) == 0) break;
            active++;
            if (output) break;
        }
        std::fprintf(stderr, "[audio-objects-frame] width=%u row=%u frame=%u base=%08X h0=%08X h4=%08X state=%08X hc=%08X valid=%u state_nz=%u active=%u output=%08X first=",
                     width, row, frame, base, word(base), word(base + 4), state,
                     word(base + 12), valid, nz, active, output);
        for (uint32_t i = 0; i < 0x50; i += 4) std::fprintf(stderr, "%08X,", word(base + 0x10 + i));
        std::fprintf(stderr, "\n");
    }
}

static RspExitReason factor5_ucode_b_probe(uint8_t* rdram, uint32_t ucode_addr) {
    g_rs64_audio_break_pc = 0;
    rs64_audio_route_prepare("factor5_ucode_b");
    rs64_m5_task_handoff(s_pending_audio_task);
    rs64_audio_source_objects(rdram, s_pending_audio_task);
    const RspExitReason reason = factor5_ucode_b(rdram, ucode_addr);
    rs64_log_audio_return("factor5_ucode_b", reason);
    return reason;
}

// Catch-all stub for unrecognised task types. Returning Broke (instead of
// QUICK_EXIT'ing) avoids tearing down the process when a stale/uninitialised
// task struct gets dispatched — observed early in boot with type fields like
// 0x21E50ADF that don't match M_GFXTASK/M_AUDTASK.
static RspExitReason unknown_task_stub(uint8_t* /*rdram*/, uint32_t /*ucode_addr*/) {
    return RspExitReason::Broke;
}

// Optional diagnostic DMA shadow for the ucode CODE image (declared in
// librecomp/rsp.hpp). The former ucode-data snapshot/shadow was removed after
// the DMEM serialization fix: audio-task staging, not mutable ucode data, was
// the source of the apparent corruption.
const uint8_t* g_rsp_dma_shadow2_data = nullptr;
uint32_t g_rsp_dma_shadow2_addr = 0;
uint32_t g_rsp_dma_shadow2_size = 0;
uint32_t g_rsp_last_chunk_dram = 0;
uint32_t g_rsp_last_chunk_dmem = 0;
uint32_t g_rsp_last_chunk_len = 0;

// Factor 5 GFX ucode runner (LLE side of the hybrid pipeline).
//
// Runs the boot ucode to set up DMEM + DMA the data section, emulates
// L_112C's first DL fetch by hand (the original ucode normally calls L_112C
// from inside the dispatch loop, but on first invocation that hasn't happened
// yet so DMEM has no real DL bytes), then runs the main ucode. The main ucode
// processes DL commands and, for vertex-pipeline ops, emits raw RDP triangle
// bytes via mtc0 DPC_END writes that flow through src/rsp/dpc_bridge.cpp into
// RT64 (isHLE=false).

// One-shot dump of each distinct ucode image so the second F5 ucode (embedded
// base 0x80099FE0 — arrives via ucode_data DMA'd over DMEM[0xFD0], the outer
// OSTask always says 0x80024A10) can be recompiled offline. Written into the
// build dir (cwd).
// s7430 class CM: was default-on (512 KB per distinct ucode into the exe dir on every run, nothing reads it back);
// now opt-in, ROGUESQ_DUMP_UCODE_BIN=1.
static void rs64_dump_ucode(uint8_t* rdram, uint32_t phys) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_DUMP_UCODE_BIN"); return e && *e && *e != '0'; }();
    if (!on) return;
    static std::vector<uint32_t> s_dumped;
    const uint32_t up = phys & 0x00FFFFF8;
    if (up == 0 || up >= 0x800000) return;
    for (uint32_t d : s_dumped) if (d == up) return;
    s_dumped.push_back(up);
    char name[64];
    snprintf(name, sizeof(name), "ucode_%06X.bin", up);
    if (FILE* f = fopen(name, "wb")) {
        uint32_t n = 0x80000;
        if (up + n > 0x800000) n = 0x800000 - up;
        for (uint32_t k = 0; k < n; k++) {
            uint8_t b = (uint8_t)MEM_B(0, (int64_t)(int32_t)(up + k + 0x80000000));
            fwrite(&b, 1, 1, f);
        }
        fclose(f);
        fprintf(stderr, "[ucode-dump] wrote %s (0x%X bytes)\n", name, n);
    }
}

// Diag: canary snapshot of DMEM[0x130] word + dispatch-table hash (0x60..0xE0).
static void rs64_canary(const char* tag, int task_n) {
    uint32_t c130 = ((uint32_t)g_dmem_cur[0x130 ^ 3] << 24) | ((uint32_t)g_dmem_cur[0x131 ^ 3] << 16) |
                    ((uint32_t)g_dmem_cur[0x132 ^ 3] << 8) | (uint32_t)g_dmem_cur[0x133 ^ 3];
    uint32_t h = 0;
    for (uint32_t a = 0x60; a < 0xE0; ++a) h = h * 31 + g_dmem_cur[a ^ 3];
    fprintf(stderr, "[rcanary t%d %s] 0x130=0x%08X tblhash=0x%08X\n", task_n, tag, c130, h);
}

// Serializes every LLE gfx task (OSTask pokes + boot + main ucode) against
// the single shared global g_dmem_cur[]. The old "tasks are serialized (single
// virtual RSP)" assumption was FALSE: send_dl invokes the runner from more
// than one thread, and 2026-07-13 DMA traces caught runner-step #4's boot
// interleaved with task #3's pre-ucode — a concurrent B task's ucode_data DMA
// (0xA4E00, len 0xF80) trampling DMEM mid-run is the mechanism behind the
// "clean pre-ucode canary, trig at first dispatch" residual exit=3 class.
// Recursive: rs64_run_lle_gfx locks around its OSTask pokes + runner call,
// and the runner locks itself for the get_rsp_microcode-driven path.
static std::recursive_mutex g_lle_task_mutex;

// Hooks called by librecomp's run_task (SP task thread, audio tasks) so its
// DMEM staging serializes against the gfx LLE runner. See rsp.cpp.
// s4249: per-holder hold-time census of g_lle_task_mutex (outermost holds only).
// Tags: 0=audio run_task (DmemGuard), 1=rs64_run_lle_gfx, 2=factor5_gfx_runner (outermost,
// i.e. not nested in 1). Enabled by ROGUESQ_S4245. Prints each hold >=3 ms and a 3 s summary.
namespace s4249 {
static thread_local int t_depth = 0;
static thread_local int t_tag = 0;
static thread_local std::chrono::steady_clock::time_point t_t0;
static const bool on = [] { const char* e = std::getenv("ROGUESQ_S4245"); return e && e[0] && e[0] != '0'; }();
static const auto T0 = std::chrono::steady_clock::now();
static const char* const names[3] = {"audio", "run_lle_gfx", "gfx_runner"};
struct Agg { uint64_t n = 0, sum_us = 0, max_us = 0, over1ms = 0; };
static std::mutex agg_mu;
static Agg agg[3];
static double last_print = 0;
static void acquired(int tag) {
    if (!on) return;
    if (t_depth++ == 0) { t_tag = tag; t_t0 = std::chrono::steady_clock::now(); }
}
static void released() {
    if (!on) return;
    if (--t_depth != 0) return;
    auto now = std::chrono::steady_clock::now();
    uint64_t us = (uint64_t)std::chrono::duration_cast<std::chrono::microseconds>(now - t_t0).count();
    double t = std::chrono::duration<double>(now - T0).count();
    std::lock_guard<std::mutex> g(agg_mu);
    Agg& a = agg[t_tag]; a.n++; a.sum_us += us; if (us > a.max_us) a.max_us = us; if (us >= 1000) a.over1ms++;
    if (us >= 3000)
        std::fprintf(stderr, "[s4249-hold] t=%.3f tag=%s hold_us=%llu\n", t, names[t_tag], (unsigned long long)us);
    if (t - last_print >= 3.0) {
        for (int i = 0; i < 3; ++i) {
            std::fprintf(stderr, "[s4249-sum] t=%.1f tag=%s n=%llu sum_us=%llu max_us=%llu over1ms=%llu\n", t, names[i],
                (unsigned long long)agg[i].n, (unsigned long long)agg[i].sum_us, (unsigned long long)agg[i].max_us, (unsigned long long)agg[i].over1ms);
            agg[i] = Agg{};
        }
        last_print = t;
    }
}
struct Hold { explicit Hold(int tag) { acquired(tag); } ~Hold() { released(); } };
}

// s6954 G1e per-task ring (ROGUESQ_G1E_TRING=<file>, needs ROGUESQ_G1E_AQ=3 and ROGUESQ_G1B=1): one text row per send_dl:
// "t_ms sd_wall sd_cpu ucode_ms submit_ms commit_ms calls rdp_bytes n_ucode phase spin". Rows are line-buffered into the file.
extern "C" uint32_t rs64_task_rdp_bytes_total();
extern "C" uint32_t g_rs64_aq_spin_ns;
struct Rs64TrAcc { uint64_t nul = 0; uint64_t n = 0, uc = 0, sub = 0, com = 0, calls = 0, bytes = 0, ranges = 0;
    uint64_t rt_n = 0, rt_ns = 0, rt_by = 0, rec_n = 0, rec_ns = 0, smp_n = 0, smp_w = 0, smp_c = 0; int cap0 = -1, capx = 0; };
// s7026 G1c: per-task RT64 handoff / record_submit totals (dpc_bridge.cpp, ROGUESQ_S7026_SUB=1) and the s7012 cap at task start/end.
extern "C" uint64_t g_rs64_bf_tasks_on, g_rs64_bf_tasks_off, g_rs64_bf_fast, g_rs64_bf_slow;  // s7027
extern "C" uint64_t g_rs64_bf_tasks_on2, g_rs64_aq_null_ns;  // s7028
extern "C" uint64_t g_rs64_bfsh_tasks[3];  // s7029
extern "C" int g_rs64_s7026, g_rs64_s7026_spin_win; extern "C" int rs64_s7012_cap(void);
extern "C" uint64_t g_rs64_s7026_rt_n, g_rs64_s7026_rt_ns, g_rs64_s7026_rt_by, g_rs64_s7026_rec_n, g_rs64_s7026_rec_ns,
                    g_rs64_s7026_smp_n, g_rs64_s7026_smp_w, g_rs64_s7026_smp_c;
extern "C" int g_rs64_g1e_batch, g_rs64_g1e_cdiag, g_rs64_g1e_lbfast, g_rs64_g1e_pcache, g_rs64_g1e_hgather; extern "C" uint64_t g_rs64_g1e_ranges;  // s6955: batch arm + deferred range entries
static Rs64TrAcc g_rs64_tr;
static FILE *g_rs64_tr_f = nullptr;
extern "C" int rs64_g1e_tring_on = [] {
    const char *e = std::getenv("ROGUESQ_G1E_TRING");
    if (!e || !*e) return 0;
    g_rs64_tr_f = std::fopen(e, "w");
    if (!g_rs64_tr_f) return 0;
    std::setvbuf(g_rs64_tr_f, nullptr, _IOFBF, 1 << 16);
    std::fprintf(g_rs64_tr_f, "# t_ms sd_wall sd_cpu ucode_ms submit_ms commit_ms calls rdp_bytes n_ucode phase spin batch ranges cdiag lbfast pcache hgather | s7026: cap0 cap_end capmix rt_n rt_us rt_bytes rec_n rec_us smp_n smp_wall_us smp_cpu_us spin_win bf_on bf_off bf_fast bf_slow | s7028: bf_on2 aq_null_ms\n");
    return 1;
}();
extern "C" uint32_t rs64_phase_ord();
extern "C" void rs64_g1e_tring_push(double t_ms, double w, double c) {
    if (!g_rs64_tr_f) return;
    const Rs64TrAcc a = g_rs64_tr; g_rs64_tr = Rs64TrAcc{};
    std::fprintf(g_rs64_tr_f, "%.3f %.3f %.3f %.3f %.3f %.3f %llu %llu %llu %u %u %d %llu %d %d %d %d", t_ms, w, c, a.uc / 1e6, a.sub / 1e6, a.com / 1e6,
                 (unsigned long long)a.calls, (unsigned long long)a.bytes, (unsigned long long)a.n, rs64_phase_ord(), g_rs64_aq_spin_ns,
                 g_rs64_g1e_batch, (unsigned long long)a.ranges, g_rs64_g1e_cdiag, g_rs64_g1e_lbfast, g_rs64_g1e_pcache, g_rs64_g1e_hgather);
    if (!g_rs64_s7026) std::fputc('\n', g_rs64_tr_f);
    else {  // s7026: extend the row
        std::fprintf(g_rs64_tr_f, " %d %d %d %llu %.3f %llu %llu %.3f %llu %.3f %.3f %d", a.cap0, rs64_s7012_cap(), a.capx,
                     (unsigned long long)a.rt_n, a.rt_ns / 1e3, (unsigned long long)a.rt_by, (unsigned long long)a.rec_n, a.rec_ns / 1e3,
                     (unsigned long long)a.smp_n, a.smp_w / 1e3, a.smp_c / 1e3, g_rs64_s7026_spin_win);
        // s7027: bump fast-path deltas per row (tasks on / off, fast bumps, slow bumps)
        static uint64_t p[5] = {}; const uint64_t q[5] = {g_rs64_bf_tasks_on, g_rs64_bf_tasks_off, g_rs64_bf_fast, g_rs64_bf_slow, g_rs64_bf_tasks_on2};
        std::fprintf(g_rs64_tr_f, " %llu %llu %llu %llu %llu %.4f", (unsigned long long)(q[0] - p[0]), (unsigned long long)(q[1] - p[1]),
                     (unsigned long long)(q[2] - p[2]), (unsigned long long)(q[3] - p[3]), (unsigned long long)(q[4] - p[4]), a.nul / 1e6);
        static uint64_t ps[3] = {}; std::fprintf(g_rs64_tr_f, " %llu %llu %llu\n", (unsigned long long)(g_rs64_bfsh_tasks[0] - ps[0]),   // s7029 shadow arm
                     (unsigned long long)(g_rs64_bfsh_tasks[1] - ps[1]), (unsigned long long)(g_rs64_bfsh_tasks[2] - ps[2]));
        for (int i = 0; i < 3; ++i) ps[i] = g_rs64_bfsh_tasks[i];
        for (int i = 0; i < 5; ++i) p[i] = q[i]; }
    static double last_flush = 0; if (t_ms - last_flush > 1000.0) { std::fflush(g_rs64_tr_f); last_flush = t_ms; }
}

extern "C" void rs64_dmem_lock()   { g_lle_task_mutex.lock(); s4249::acquired(0); }
extern "C" void rs64_dmem_unlock() { s4249::released(); g_lle_task_mutex.unlock(); }

extern "C" void rs64_s7645_gfx_task(int edge, uint32_t dl);  // s7645 TS-4 (src/rsp/s7644_rspdma.cpp; no-op unless ROGUESQ_S7644_RSPDMA&2)
extern "C" void rs64_s7751_task_begin(const uint8_t* rdram, const uint8_t* dmem); extern "C" void rs64_s7751_task_end(void);
static RspExitReason factor5_gfx_runner(uint8_t* rdram, uint32_t ucode_addr) {
    std::lock_guard<std::recursive_mutex> lle_lock(g_lle_task_mutex);
    struct S7645Edge { S7645Edge() { rs64_s7645_gfx_task(0, s_pending_task_data_ptr); } ~S7645Edge() { rs64_s7645_gfx_task(1, 0); } } s7645_edge;
    s4249::Hold s4249_hold(2);
    uint32_t dl_ptr           = s_pending_task_data_ptr;
    uint32_t ucode_data_addr  = s_pending_task_ucode_data;
    uint32_t ucode_data_size  = s_pending_task_ucode_data_size;

    // Mimic SP_BOOT (silicon-level RSP boot ucode): zero DMEM[0..0xFC0] then
    // populate DMEM[0..ucode_data_size]. Leave DMEM[0xFC0..0x1000] alone —
    // that's the OSTask region the boot ucode reads.
    //
    std::memset(g_dmem_cur, 0, 0xFC0);
    // Always load each task's ucode data from live RDRAM. Before shared-DMEM
    // serialization, a concurrent audio task could overwrite this area while
    // GFX was running; a first-task snapshot only hid that race and could make
    // later phase changes stale. g_lle_task_mutex now models the single RSP.
    if (ucode_data_addr != 0 && ucode_data_size != 0 && ucode_data_size <= 0xFC0) {
        dma_rdram_to_dmem(rdram, 0, ucode_data_addr & 0x00FFFFFF, ucode_data_size - 1);
    }
    {
        static const bool enabled = [] {
            const char* e = std::getenv("ROGUESQ_LOG_G1D_INPUT");
            return e && *e && *e != '0';
        }();
        if (enabled && rs64_phase_ord() == 4 && dl_ptr != 0) {
            static uint32_t root_base = 0;
            static uint32_t roots[32] = {};
            static uint32_t root_count = 0;
            static uint32_t row = 0;
            const uint32_t root = dl_ptr & 0x007FFFFFu;
            if (root_base == 0) root_base = root;
            bool known = false;
            for (uint32_t i = 0; i < root_count; ++i) {
                if (roots[i] == root) { known = true; break; }
            }
            if (!known && root_count < 32) {
                roots[root_count++] = root;
                uint32_t root_hash = 2166136261u;
                uint32_t root_nonzero = 0;
                for (uint32_t i = 0; i < 0x100; ++i) {
                    const uint8_t b = rdram[(root + i) ^ 3u];
                    root_hash ^= b;
                    root_hash *= 16777619u;
                    root_nonzero += b != 0;
                }
                uint32_t data_hash = 2166136261u;
                uint32_t data_nonzero = 0;
                for (uint32_t i = 0; i < ucode_data_size && i < 0xFC0; ++i) {
                    const uint8_t b = g_dmem_cur[i ^ 3u];
                    data_hash ^= b;
                    data_hash *= 16777619u;
                    data_nonzero += b != 0;
                }
                std::fprintf(stderr,
                    "[g1d-udata] phase=4 row=%u task_root=0x%06X "
                    "root_hash=0x%08X root_nz=%u ucode_data=0x%08X data_size=0x%X "
                    "data_hash=0x%08X data_nz=%u\n",
                    ++row, root,
                    root_hash, root_nonzero, ucode_data_addr, ucode_data_size,
                    data_hash, data_nonzero);
                std::fflush(stderr);
            }
        }
    }
    // Second shadow: the ucode CODE image. The overlay loader (L_1278) and
    // bootstrap DMA segments from OSTask.ucode + table offsets (observed up to
    // +0x803F0, len 0xF80), and that RDRAM is also engine-corrupted mid-flight
    // — the source of trig-as-dispatch-table at first dispatch on failing
    // tasks. Capture once on first task, serve all reads in range from the
    // clean copy. Disable with ROGUESQ_NO_SHADOW2=1 for A/B soaks.
    {
        static int s_sh2 = -1;
        if (s_sh2 < 0) {
            // Default OFF: a 300s soak with the full-image shadow was WORSE
            // (109 unhandled, 35 send_dl vs 256 baseline) — the region holds
            // legit dynamic data (mailbox-like spots at +0x12DEA/+0x7CD5C)
            // and serving it stale breaks real work. Kept for the LIVE DIFF
            // diagnostic; enable serving with ROGUESQ_SHADOW2=1.
            const char* e = std::getenv("ROGUESQ_SHADOW2");
            s_sh2 = (e && *e && *e != '0') ? 1 : 0;
        }
        if (s_sh2 && ucode_addr != 0) {
            static std::vector<uint8_t> s_sh2_buf; // shared, tasks serialized
            const uint32_t sh2_phys = ucode_addr & 0x00FFFFF8;
            uint32_t sh2_size = 0x82000; // covers observed +0x803F0 + 0xF80
            if (sh2_phys >= 0x800000) sh2_size = 0;
            else if (sh2_phys + sh2_size > 0x800000) sh2_size = 0x800000 - sh2_phys;
            if (s_sh2_buf.empty()) {
                s_sh2_buf.resize(sh2_size);
                for (uint32_t k = 0; k < sh2_size; k++) {
                    s_sh2_buf[k] = MEM_B(0, (int64_t)(int32_t)(sh2_phys + k + 0x80000000));
                }
                fprintf(stderr, "[shadow2] captured ucode image 0x%06X..0x%06X\n",
                        sh2_phys, sh2_phys + sh2_size);
                g_rsp_dma_shadow2_addr = sh2_phys;
                g_rsp_dma_shadow2_size = sh2_size;
            }
            g_rsp_dma_shadow2_data = s_sh2_buf.data();
            // Two-source evidence: does the engine actually rewrite this RDRAM?
            // Compare live RDRAM vs the clean capture each task (cheap scan).
            static int s_diff_logs = 0;
            if (s_diff_logs < 24) {
                uint32_t ndiff = 0, first = 0;
                // s7364: s_sh2_buf is sized by the FIRST task; a later task's sh2_size/sh2_phys can exceed it.
                const uint32_t sh2_cap_phys = g_rsp_dma_shadow2_addr;
                const uint32_t sh2_cmp = (uint32_t)std::min<size_t>(sh2_size, s_sh2_buf.size());
                for (uint32_t k = 0; k < sh2_cmp; k++) {
                    if ((uint8_t)MEM_B(0, (int64_t)(int32_t)(sh2_cap_phys + k + 0x80000000)) != s_sh2_buf[k]) {
                        if (ndiff == 0) first = k;
                        ndiff++;
                    }
                }
                if (ndiff != 0) {
                    ++s_diff_logs;
                    fprintf(stderr, "[shadow2] LIVE DIFF: %u bytes, first at ucode+0x%X (dram 0x%06X)\n",
                            ndiff, first, sh2_phys + first);
                }
            }
        }
    }
    // Diagnostic: log re-DMA params + DMEM[0..0x10] after the copy.
    {
        static int s_log = -1;
        if (s_log < 0) {
            const char* rs64_la = std::getenv("ROGUESQ_LOG_ALL"); // s7728: LOG_ALL, as rsp.cpp
            const char* e = std::getenv("ROGUESQ_LOG_SPBOOT");
            s_log = ((rs64_la && *rs64_la && *rs64_la != '0') || (e && *e && *e != '0')) ? 1 : 0;
        }
        if (s_log) {
            static int s_n = 0;
            ++s_n;
            if (s_n <= 4) {
                fprintf(stderr,
                    "[spboot] task #%d ucode_data=0x%08X size=0x%X DMEM[0..0x10]:",
                    s_n, ucode_data_addr, ucode_data_size);
                for (int i = 0; i < 0x10; ++i) {
                    fprintf(stderr, " %02X", g_dmem_cur[i ^ 3]);
                }
                fprintf(stderr, "\n");
                fflush(stderr);
            }
        }
    }

    // Boot exits via UnhandledJumpTarget on its `jr $7=0x1080` (jumping into
    // the main ucode it just DMA'd to IMEM 0x80) — that's expected.
    static thread_local int s_runner_step_log = 0;
    const bool log_step = (++s_runner_step_log) <= 16;
    if (log_step) {
        fprintf(stderr, "[runner-step #%d] entering factor5_boot ucode_addr=0x%08X\n",
                s_runner_step_log, ucode_addr);
        fflush(stderr);
    }
    rs64_dpc_reset();
    if (log_step) rs64_canary("pre-boot", s_runner_step_log);
    RspExitReason boot_r = factor5_boot(rdram, ucode_addr);
    if (log_step) rs64_canary("post-boot", s_runner_step_log);
    rs64_dump_ucode(rdram, ucode_addr & 0x00FFFFFF);
    // Canary: DMEM[0xFD0] (OSTask.ucode slot) must still hold the poked gfx
    // ucode after boot. A mismatch previously meant librecomp's run_task
    // (audio tasks, SP task thread) had memcpy'd the MusyX OSTask
    // (ucode=0x80099FE0, ucode_data=0xA4E00 — its wavetables were the "trig"
    // trample) over our staging mid-run. That race is closed by
    // rs64_dmem_lock in run_task; if this ever fires again, a new unlocked
    // DMEM writer exists. (An earlier theory recompiled 0x99FE0 as a "second
    // gfx ucode" factor5_ucode_b — wrong: it's the audio ucode. The recompile
    // is kept in-tree but must never run for gfx tasks.)
    uint32_t embedded_ucode = ((uint32_t)g_dmem_cur[0xFD0 ^ 3] << 24) | ((uint32_t)g_dmem_cur[0xFD1 ^ 3] << 16) |
                              ((uint32_t)g_dmem_cur[0xFD2 ^ 3] << 8) | (uint32_t)g_dmem_cur[0xFD3 ^ 3];
    if ((embedded_ucode & 0x00FFFFF8) != (ucode_addr & 0x00FFFFF8) &&
        (embedded_ucode & 0x00FFFFF8) != 0) {
        static int s_bn = 0;
        if (++s_bn <= 16 || (s_bn & 63) == 0) {
            fprintf(stderr, "[dmem-race] DMEM[0xFD0]=0x%08X != task ucode 0x%08X (#%d) — "
                    "unlocked DMEM writer!\n", embedded_ucode, ucode_addr, s_bn);
        }
    }
    if (log_step) {
        fprintf(stderr, "[runner-step #%d] factor5_boot returned %d\n",
                s_runner_step_log, (int)boot_r);
        fflush(stderr);
    }
    if (boot_r != RspExitReason::UnhandledJumpTarget && boot_r != RspExitReason::Broke) {
        fprintf(stderr, "[RSP] factor5_boot returned unexpected %d, abandoning task\n", (int)boot_r);
        return RspExitReason::Broke;
    }

    // s5597 ORIGIN: the ASan arm (tools/build_asan.sh) caught poke_be32(0x101C)
    // writing 0x1C bytes past the end of the 4 KB gfx `dmem` (global-buffer-
    // overflow, 3/3 boots) - into the adjacent audio DMEM global. The offset is
    // the original author's; RSP DMEM addressing wraps at 0xFFF. Default drops
    // out-of-range bytes (gfx state unchanged, overflow gone);
    // ROGUESQ_POKE_WRAP=1 masks to the wrapped hardware address (DMEM[0x01C]).
    static const bool s_poke_wrap = [] {
        const char* e = std::getenv("ROGUESQ_POKE_WRAP");
        return e && *e && *e != '0';
    }();
    auto poke_be32 = [](uint32_t off, uint32_t val) {
        for (int i = 0; i < 4; ++i) {
            uint32_t a = off + i;
            if (a >= 0x1000u) {
                if (!s_poke_wrap) continue;
                a &= 0xFFFu;
            }
            g_dmem_cur[a ^ 3] = (uint8_t)(val >> (24 - 8*i));
        }
    };
    auto peek_be32 = [](uint32_t off) {
        return ((uint32_t)g_dmem_cur[(off + 0) ^ 3] << 24) |
               ((uint32_t)g_dmem_cur[(off + 1) ^ 3] << 16) |
               ((uint32_t)g_dmem_cur[(off + 2) ^ 3] << 8) |
               (uint32_t)g_dmem_cur[(off + 3) ^ 3];
    };
    if (dl_ptr) {
        // Stage the first 0x110 bytes of DL into DMEM at 0x170 (where the
        // main ucode's L_112C helper would normally DMA). Set DMEM[0x654] to
        // 0x178 so the dispatcher's first `lw $17, 0x654` lands past the
        // 8-byte header at the start of real commands.
        dma_rdram_to_dmem(rdram, /*dmem*/0x170, /*dram*/dl_ptr & 0x00FFFFFF, /*rd_len*/0x10F);
        // DMEM[$18+0x30] = the "current chunk RDRAM addr". With $18=0x100
        // (the value our fixup injects, matching L_1DB0's bootstrap), this
        // is DMEM[0x130]. L_11B0's chunk-fetch reads this slot for the next
        // re-DMA. L_1DB0 normally bootstraps it from DMEM[$1+0x30] = 0xFF0;
        // The generated L_1DB0 bootstrap normally seeds this slot from FF0.
        // Keep an opt-in host mirror only for the cleanup A/B.
        const uint32_t boot_130 = peek_be32(0x130);
        static int s_stage_host_130 = -1;
        if (s_stage_host_130 < 0) {
            const char* e = std::getenv("ROGUESQ_STAGE_HOST_130");
            s_stage_host_130 = (e && *e && *e != '0') ? 1 : 0;
        }
        if (s_stage_host_130) {
            poke_be32(0x130, dl_ptr);
        }
        const uint32_t boot_ff0 = peek_be32(0xFF0);
        static int s_stage_host_ff0 = -1;
        if (s_stage_host_ff0 < 0) {
            const char* e = std::getenv("ROGUESQ_STAGE_HOST_FF0");
            s_stage_host_ff0 = (e && *e && *e != '0') ? 1 : 0;
        }
        if (s_stage_host_ff0) {
            poke_be32(0xFF0, dl_ptr);
        }
        rs64_inline_probe_trigen_stage(dl_ptr, boot_130, peek_be32(0x130), !s_stage_host_130,
                                        boot_ff0, peek_be32(0xFF0), !s_stage_host_ff0);
        poke_be32(0x101C, dl_ptr);
        poke_be32(0x654,  0x178);
        // RDP flush ring state (L_112C): DMEM[0x100]=ring base, [0x104]=limit,
        // [0x108]=write pos. The snapshot restore rewrites these with task
        // #1's values while rs64_dpc_reset() zeroes the bridge side — the
        // stale write pos makes the ucode skip flushes until the staging
        // cursor (r16, base 0xD60) overflows to ~0x16E0 and the oversized
        // flush DMA tramples DMEM[0..0xF80] with ring bytes (the trig-as-
        // dispatch-table symptom). Re-sync write pos to ring base per task.
        // Tested 2026-07-13: no measurable change (41 vs 51 unhandled/120s,
        // inside the noise band) — gated off pending a better slot decode.
        static int s_ring = -1;
        if (s_ring < 0) {
            const char* e = std::getenv("ROGUESQ_RING_RESYNC");
            s_ring = (e && *e && *e != '0') ? 1 : 0;
        }
        if (s_ring) {
            uint32_t ring_base = ((uint32_t)g_dmem_cur[0x100 ^ 3] << 24) | ((uint32_t)g_dmem_cur[0x101 ^ 3] << 16) |
                                 ((uint32_t)g_dmem_cur[0x102 ^ 3] << 8) | (uint32_t)g_dmem_cur[0x103 ^ 3];
            poke_be32(0x108, ring_base);
        }
        // Reset the DL-stack-pointer byte. The ucode runs with $18 = 0x100
        // (set by L_1DB0's bootstrap), so $18+0x52 = DMEM[0x152]. Op_0F's
        // L_12C4 handler decrements this by 8 each call and exits the
        // dispatch loop when it goes negative. After task #1 underflows the
        // byte is left negative; subsequent tasks would exit immediately with
        // 0 RDP work emitted. Reset to 0x18 (3 stack entries) at task start.
        g_dmem_cur[0x152 ^ 3] = 0x18;
        // Resident-segment cache byte (L_1DB0 clears it). Forcing an invalid
        // id (0xFF) to make the loader always reload was tried 2026-07-12 and
        // INCREASED failures — the entry path apparently relies on 0 here.
        g_dmem_cur[0x153 ^ 3] = 0;

        // Diagnostic: dump first 16 DMEM bytes at the dispatch start so we
        // can see what opcode the first iter is dispatching on per task.
        static int s_dump = -1;
        if (s_dump < 0) {
            const char* e = std::getenv("ROGUESQ_LOG_DMEM_DL");
            s_dump = (e && *e && *e != '0') ? 1 : 0;
        }
        if (s_dump) {
            static int s_n = 0;
            ++s_n;
            if (s_n <= 8) {
                fprintf(stderr, "[dl] task #%d dl_ptr=0x%08X DMEM[0x178..0x190]:",
                        s_n, dl_ptr);
                for (int i = 0x178; i < 0x190; ++i) {
                    fprintf(stderr, " %02X", g_dmem_cur[i ^ 3]);
                }
                fprintf(stderr, "\n");
                fflush(stderr);
            }
        }
    } else {
        poke_be32(0x654, 0x270);
    }
    if (log_step) {
        fprintf(stderr, "[runner-step #%d] entering factor5_ucode\n", s_runner_step_log);
        fflush(stderr);
    }
    { static int tn2 = 0; if (++tn2 <= 16) rs64_canary("pre-ucode", tn2); }
    // s6845: ROGUESQ_WIPE_DLWALK=<vi_lo>:<vi_hi> walks the guest gfx DL (F5 command lengths per docs/F5-UCODE-REFERENCE.md,
    // following 0x06 calls 4 deep) at task start inside the VI window and logs every non-geometry command with its
    // guest address ([wdl] lines), so the guest command behind an RDP texrect can be named. Diagnostic only.
    {
        static uint32_t wlo = 0, whi = 0;
        static const bool won = [] { const char* e = std::getenv("ROGUESQ_WIPE_DLWALK"); if (!e || !*e) return false;
            char* c = nullptr; wlo = (uint32_t)strtoul(e, &c, 10); whi = (c && *c == ':') ? (uint32_t)strtoul(c + 1, nullptr, 10) : 0u; return whi > wlo; }();
        const uint32_t vi = rs64_vi_n_g;
        if (won && dl_ptr && vi >= wlo && vi <= whi) {
            static int lines = 0;
            auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, rdram + (a & 0x7FFFFCu), 4); return v; };
            uint32_t stk[8]; int sp = 0; uint32_t pc = dl_ptr & 0x7FFFFFu; int n = 0;
            while (n++ < 20000 && lines < 60000) {
                const uint32_t w0 = rd(pc), w1 = rd(pc + 4), op = w0 >> 24;
                uint32_t len = 8;
                if (op == 0x03 || op == 0xBD) len = 24; else if (op == 0x05) len = 40;
                else if (op == 0xBF || op == 0xB4) len = (w0 & 2) ? 32 : 16;
                else if (op == 0xBE || op == 0xB3) len = 16; else if (op == 0xE4 || op == 0xE5) len = 16;
                if (op != 0xBF && op != 0xB4 && op != 0x05) {
                    lines++;
                    fprintf(stderr, "[wdl] vi=%u d=%d pc=%06X op=%02X w=%08X %08X", vi, sp, pc, op, w0, w1);
                    for (uint32_t o = 8; o < len; o += 4) fprintf(stderr, " %08X", rd(pc + o));
                    fputc('\n', stderr);
                }
                if (op == 0x06 && sp < 4) { stk[sp++] = pc + len; pc = w1 & 0x7FFFFFu; continue; }
                if (op == 0x07) { pc = w1 & 0x7FFFFFu; continue; }
                if (op == 0xB8) { if (sp == 0) break; pc = stk[--sp]; continue; }
                pc += len;
            }
            fprintf(stderr, "[wdl] vi=%u end n=%d\n", vi, n);
        }
    }
    const uint32_t task_serial = g_rs64_lle_task_n.fetch_add(1, std::memory_order_relaxed) + 1;
    rs64_e9prov_force_update();  // s7021
    rs64_e9prov_task_begin(task_serial, dl_ptr, rdram, ucode_addr);
    rs64_s7751_task_begin(rdram, g_dmem_cur);  // s7751: ROGUESQ_S7751_SNAP gfx task snapshot (src/rsp/s7751_task_snap.cpp)
    rs64_dpc_defer_begin();
    // ROGUESQ_LOG_TASKMS=1 (session 37) — wall time of the ucode call per task,
    // phase-scoped. s36 put 82% of Gfx Thread samples inside factor5_ucode but
    // sampling cannot distinguish "computing" from "spinning in the DPC ring
    // wait", and it cannot give a per-task cost. This does both: mean/max ms per
    // phase, plus a count of tasks over 100ms.
    static const bool s_taskms = []{
        const char *e = std::getenv("ROGUESQ_LOG_TASKMS");
        return e && *e && *e != '0';
    }();
    // H7: pre/post LLE snapshot of the fixed FULL_SYNC side-slot. A b0
    // change with in_task=1 is RSP-side (H7a); a change only visible between
    // tasks is guest/DMA (H7b). Gated by the same env as the poller.
    static const bool s_fs_slot_task = []{
        const char *e = std::getenv("ROGUESQ_LOG_FS_SLOT");
        return e && *e && *e != '0';
    }();
    static const uint32_t s_fs_slot_phys = []{
        uint32_t a = 0x76DF60u;
        if (const char *e = std::getenv("ROGUESQ_FS_SLOT_ADDR")) {
            unsigned long v = strtoul(e, nullptr, 0);
            if (v > 0 && v < 0x800000u) a = (uint32_t)v;
        }
        return a & 0x7FFFFFu;
    }();
    auto fs_slot_b0 = [&]() -> uint8_t {
        return (uint8_t)MEM_B(0, (int64_t)(int32_t)(s_fs_slot_phys + 0x80000000u));
    };
    auto fs_slot_w0 = [&]() -> uint32_t {
        uint32_t w = 0;
        for (int i = 0; i < 4; ++i) {
            w = (w << 8) | (uint32_t)(uint8_t)MEM_B(0,
                (int64_t)(int32_t)(s_fs_slot_phys + (uint32_t)i + 0x80000000u));
        }
        return w;
    };
    // Shared across pre/post so intertask_delta sees the previous task's post.
    static int s_fs_have_post = 0;
    static uint8_t s_fs_last_post_b0 = 0;
    static uint32_t s_fs_last_post_w0 = 0;
    static uint32_t s_fs_last_post_task = 0;
    uint8_t slot_b0_pre = 0;
    uint32_t slot_w0_pre = 0;
    if (s_fs_slot_task) {
        slot_b0_pre = fs_slot_b0();
        slot_w0_pre = fs_slot_w0();
        // Inter-task window: slot changed since last task's post snapshot ⇒
        // writer was outside LLE (guest CPU or DMA).
        if (s_fs_have_post &&
            (slot_b0_pre != s_fs_last_post_b0 || slot_w0_pre != s_fs_last_post_w0)) {
            const bool e9e7 = (s_fs_last_post_b0 == 0xE9 || s_fs_last_post_b0 == 0xE7 ||
                               slot_b0_pre == 0xE9 || slot_b0_pre == 0xE7);
            if (e9e7 || (task_serial <= 40) || ((task_serial % 200) == 0)) {
                fprintf(stderr,
                    "[fs-slot] n=%u event=intertask_delta prev_task=#%u next_task=#%u "
                    "b0=%02X->%02X w0=%08X->%08X guest_pc=0x%08X src=outside_lle\n",
                    task_serial, s_fs_last_post_task, task_serial,
                    s_fs_last_post_b0, slot_b0_pre, s_fs_last_post_w0, slot_w0_pre,
                    (unsigned)g_rs64_last_guest_pc);
                fflush(stderr);
            }
        }
    }
    g_rs64_lle_depth.fetch_add(1, std::memory_order_release);
    const auto t_start = s_taskms ? std::chrono::steady_clock::now()
                                  : std::chrono::steady_clock::time_point{};
    // s6712 G1e: [g1e-split] per-second split of the task (ucode wall vs dpc_bridge submit/commit). ROGUESQ_G1E_AQ=1;
    // ROGUESQ_G1E_AQ_SPIN_NS=<ns> spins that long per submit call in alternate 10 s windows (positive control).
    static uint32_t s_aq_spin_cfg = 0;
    if (g_rs64_aq_on < 0) {
        const char *e = std::getenv("ROGUESQ_G1E_AQ");
        const char *sp = std::getenv("ROGUESQ_G1E_AQ_SPIN_NS");
        s_aq_spin_cfg = sp ? (uint32_t)std::strtoul(sp, nullptr, 0) : 0u;
        g_rs64_aq_on = (e && *e && *e != '0') ? (*e == '2' ? 2 : *e == '3' ? 3 : 1) : 0;  // s6954: 3 = sampled submit timing  // s6715: 2 = per-task ucode timing only (no per-submit clock)
    }
    const uint64_t aq_null0 = g_rs64_aq_null_ns;  // s7028
    const uint64_t aq_sub0 = g_rs64_aq_submit_ns, aq_calls0 = g_rs64_aq_submit_calls, aq_com0 = g_rs64_aq_commit_ns;
    const uint32_t tr_bytes0 = rs64_task_rdp_bytes_total(); const uint64_t tr_rng0 = g_rs64_g1e_ranges;
    const uint64_t s26[8] = {g_rs64_s7026_rt_n, g_rs64_s7026_rt_ns, g_rs64_s7026_rt_by, g_rs64_s7026_rec_n, g_rs64_s7026_rec_ns,
                             g_rs64_s7026_smp_n, g_rs64_s7026_smp_w, g_rs64_s7026_smp_c};  // s7026
    const int s26cap = g_rs64_s7026 ? rs64_s7012_cap() : 0;
    const auto aq_t0 = g_rs64_aq_on > 0 ? std::chrono::steady_clock::now() : std::chrono::steady_clock::time_point{};
    rs64_diag_busy_task();  // s7432 positive control (ROGUESQ_DIAG_BUSY_US)
    RspExitReason r;
    if (rs64_g1e_dmembase && g_dmem_cur == dmem) {
        const int lean = rs64_g1e_lean && !rs64_rsp_hooks_on && !rs64_g1e_probes;
        rs64_g1e_lean_tasks[lean].fetch_add(1, std::memory_order_relaxed);
        const int nmac = lean && rs64_g1e_nmac;
        if (lean) rs64_g1e_nmac_tasks[nmac].fetch_add(1, std::memory_order_relaxed);
        r = nmac ? factor5_ucode_nmac(rdram, ucode_addr) : lean ? factor5_ucode_lean(rdram, ucode_addr) : factor5_ucode(rdram, ucode_addr);
    }
    else {
        static bool warned = false;
        if (rs64_g1e_dmembase && !warned) { warned = true; fprintf(stderr, "[g1e-dmembase] g_dmem_cur != dmem on the gfx thread: TLS arm\n"); }
        r = factor5_ucode_tls(rdram, ucode_addr);
    }
    const auto aq_t1 = g_rs64_aq_on > 0 ? std::chrono::steady_clock::now() : std::chrono::steady_clock::time_point{};
    {
        static const bool enabled = [] {
            const char* e = std::getenv("ROGUESQ_LOG_G1D_INPUT");
            return e && *e && *e != '0';
        }();
        const uint32_t root = rs64_e9prov_current_root_dl() & 0x007FFFFFu;
        if (enabled && rs64_phase_ord() == 4 && root != 0 && root <= 0x007FFF00u) {
            static uint32_t root_base = 0;
            static uint32_t roots[32] = {};
            static uint32_t root_count = 0;
            static uint32_t row = 0;
            if (root_base == 0) root_base = root;
            bool known = false;
            for (uint32_t i = 0; i < root_count; ++i) {
                if (roots[i] == root) { known = true; break; }
            }
            if (!known && root_count < 32) {
                roots[root_count++] = root;
                uint32_t hash = 2166136261u;
                uint32_t nonzero = 0;
                for (uint32_t i = 0; i < 0x100; ++i) {
                    const uint8_t b = rdram[(root + i) ^ 3u];
                    hash ^= b;
                    hash *= 16777619u;
                    nonzero += b != 0;
                }
                std::fprintf(stderr,
                    "[g1d-root] phase=4 row=%u root_seq=%u root=0x%06X root_norm=0x%06X "
                    "hash=0x%08X nz=%u bytes=",
                    ++row, root_count - 1, root, (root - root_base) & 0x007FFFFFu,
                    hash, nonzero);
                for (uint32_t i = 0; i < 0x100; ++i)
                    std::fprintf(stderr, "%02X", rdram[(root + i) ^ 3u]);
                std::fprintf(stderr, "\n");
                std::fflush(stderr);
            }
        }
    }
    g_rs64_lle_depth.fetch_sub(1, std::memory_order_release);
    if (s_fs_slot_task) {
        const uint8_t slot_b0_post = fs_slot_b0();
        const uint32_t slot_w0_post = fs_slot_w0();
        if (slot_b0_pre != slot_b0_post || slot_w0_pre != slot_w0_post) {
            const bool e9e7 = (slot_b0_pre == 0xE9 || slot_b0_pre == 0xE7 ||
                               slot_b0_post == 0xE9 || slot_b0_post == 0xE7);
            // Always log E7/E9 transitions; sparse otherwise for noise.
            if (e9e7 || (task_serial <= 40) || ((task_serial % 200) == 0)) {
                fprintf(stderr,
                    "[fs-slot] n=%u event=task_delta task=#%u "
                    "b0=%02X->%02X w0=%08X->%08X dpc_start=0x%08X dpc_end=0x%08X "
                    "guest_pc=0x%08X src=rsp_lle\n",
                    task_serial, task_serial,
                    slot_b0_pre, slot_b0_post, slot_w0_pre, slot_w0_post,
                    g_rsp_dpc_start, g_rsp_dpc_end,
                    (unsigned)g_rs64_last_guest_pc);
                fflush(stderr);
            }
        }
        s_fs_last_post_b0 = slot_b0_post;
        s_fs_last_post_w0 = slot_w0_post;
        s_fs_last_post_task = task_serial;
        s_fs_have_post = 1;
    }
    if (s_taskms) {
        const double ms = std::chrono::duration<double, std::milli>(
            std::chrono::steady_clock::now() - t_start).count();
        static std::mutex mu_tm;
        static uint32_t ph_tm = 0xFFFFFFFFu;
        static int n_tm = 0, slow_tm = 0;
        static double sum_tm = 0.0, max_tm = 0.0;
        const uint32_t phase = rs64_phase_ord();
        bool report = false;
        int n = 0, slow = 0; double mean = 0, mx = 0;
        {
            std::lock_guard<std::mutex> lk(mu_tm);
            if (phase != ph_tm) { ph_tm = phase; n_tm = slow_tm = 0; sum_tm = max_tm = 0.0; }
            n_tm++; sum_tm += ms; if (ms > max_tm) max_tm = ms;
            if (ms > 100.0) slow_tm++;
            if ((n_tm % 10) == 0) {
                report = true; n = n_tm; slow = slow_tm; mean = sum_tm / n_tm; mx = max_tm;
            }
        }
        if (report) {
            fprintf(stderr, "[taskms ph%u] n=%d mean=%.1fms max=%.1fms over100ms=%d\n",
                    phase, n, mean, mx, slow);
            fflush(stderr);
        }
    }
    // Drop the task's RDP output if the ucode wandered into garbage (trig
    // data executed as DL) — RT64 must never see those streams.
    rs64_dpc_defer_end(r != RspExitReason::UnhandledJumpTarget);
    rs64_s7751_task_end();
    if (g_rs64_aq_on > 0) {
        struct AqAcc { uint64_t n = 0, ucode = 0, sub = 0, calls = 0, com = 0, slow_n = 0, slow_ucode = 0, slow_sub = 0, max = 0; };
        static AqAcc acc;
        static auto win0 = aq_t1, sec0 = aq_t1;
        const uint64_t ucode_ns = (uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(aq_t1 - aq_t0).count();
        const uint64_t sub_ns = g_rs64_aq_submit_ns - aq_sub0;
        acc.n++; acc.ucode += ucode_ns; acc.sub += sub_ns; acc.calls += g_rs64_aq_submit_calls - aq_calls0;
        acc.com += g_rs64_aq_commit_ns - aq_com0;
        if (rs64_g1e_tring_on) {  // s6954: per-task terms, joined to send_dl wall/cpu by rs64_g1e_tring_push (events.cpp)
            g_rs64_tr.nul += g_rs64_aq_null_ns - aq_null0;  // s7028
            g_rs64_tr.n++; g_rs64_tr.uc += ucode_ns; g_rs64_tr.sub += sub_ns; g_rs64_tr.com += g_rs64_aq_commit_ns - aq_com0;
            g_rs64_tr.calls += g_rs64_aq_submit_calls - aq_calls0; g_rs64_tr.bytes += rs64_task_rdp_bytes_total() - tr_bytes0; g_rs64_tr.ranges += g_rs64_g1e_ranges - tr_rng0;
            if (g_rs64_s7026) { Rs64TrAcc &q = g_rs64_tr;
                q.rt_n += g_rs64_s7026_rt_n - s26[0]; q.rt_ns += g_rs64_s7026_rt_ns - s26[1]; q.rt_by += g_rs64_s7026_rt_by - s26[2];
                q.rec_n += g_rs64_s7026_rec_n - s26[3]; q.rec_ns += g_rs64_s7026_rec_ns - s26[4]; q.smp_n += g_rs64_s7026_smp_n - s26[5];
                q.smp_w += g_rs64_s7026_smp_w - s26[6]; q.smp_c += g_rs64_s7026_smp_c - s26[7];
                if (q.cap0 < 0) q.cap0 = s26cap; else if (q.cap0 != s26cap) q.capx = 1;
                if (rs64_s7012_cap() != s26cap) q.capx = 1; }
        }
        if (ucode_ns > 10000000ull) { acc.slow_n++; acc.slow_ucode += ucode_ns; acc.slow_sub += sub_ns; }
        if (ucode_ns > acc.max) acc.max = ucode_ns;
        const auto now = std::chrono::steady_clock::now();
        if (now - sec0 >= std::chrono::seconds(1)) {
            const double n = (double)acc.n, sn = acc.slow_n ? (double)acc.slow_n : 1.0;
            fprintf(stderr, "[g1e-split] phase=%u spin=%u fast=%d tasks=%llu ucode_ms=%.3f submit_ms=%.3f rest_ms=%.3f commit_ms=%.3f "
                    "calls=%.0f max_ms=%.2f slow_n=%llu slow_ucode_ms=%.3f slow_submit_ms=%.3f probes=%d\n",
                    rs64_phase_ord(), g_rs64_aq_spin_ns, rs64_g1e_fast, (unsigned long long)acc.n, acc.ucode / n / 1e6, acc.sub / n / 1e6,
                    (acc.ucode - acc.sub) / n / 1e6, acc.com / n / 1e6, acc.calls / n, acc.max / 1e6,
                    (unsigned long long)acc.slow_n, acc.slow_ucode / sn / 1e6, acc.slow_sub / sn / 1e6, rs64_g1e_probes);
            acc = AqAcc{};
            sec0 = now;
        }
        if (s_aq_spin_cfg && now - win0 >= std::chrono::seconds(10)) {
            g_rs64_aq_spin_ns = g_rs64_aq_spin_ns ? 0u : s_aq_spin_cfg;
            win0 = now;
        }
    }
    static const bool s_log_f5_state = [] {
        const char *e = std::getenv("ROGUESQ_LOG_F5_STATE");
        return e && *e && *e != '0';
    }();
    if (s_log_f5_state && (task_serial <= 4 || rs64_phase_ord() >= 4)) {
        uint32_t first_lo = 0, first_hi = 0, last_lo = 0, last_hi = 0;
        uint32_t min_lo = 0xFFFFFFFFu, max_hi = 0;
        rs64_dpc_get_task_range(&first_lo, &first_hi, &last_lo, &last_hi, &min_lo, &max_hi);
        fprintf(stderr,
                "[f5-dpc-task-range] phase=%u task=%u root_dl=0x%06X "
                "first=[0x%06X,0x%06X) last=[0x%06X,0x%06X) "
                "bounds=[0x%06X,0x%06X) committed=%s\n",
                rs64_phase_ord(), task_serial, dl_ptr & 0x7FFFFFu,
                first_lo, first_hi, last_lo, last_hi,
                min_lo == 0xFFFFFFFFu ? 0u : min_lo, max_hi,
                first_hi != 0 ? "yes" : "no");
        fflush(stderr);
    }
    rs64_e9prov_task_end(task_serial);
    if (log_step) {
        fprintf(stderr, "[runner-step #%d] factor5_ucode returned %d\n",
                s_runner_step_log, (int)r);
        fflush(stderr);
    }
    {
        static int s_log = -1;
        if (s_log < 0) {
            const char* e = std::getenv("ROGUESQ_LOG_RUNNER");
            s_log = (e && *e && *e != '0') ? 1 : 0;
        }
        // ROGUESQ_LOG_RUNNER_ALL: rs64_dpc_drain_histogram() resets its
        // counters on every call, but the default 1-in-32 sampling below only
        // calls it on sampled tasks — so the other 31 tasks' histograms
        // silently accumulate into whichever task number is sampled next
        // (misattributed aggregate, not that task's real content). This mode
        // drains+prints every task so counts are exact.
        static int s_log_all = -1;
        if (s_log_all < 0) {
            const char* e = std::getenv("ROGUESQ_LOG_RUNNER_ALL");
            s_log_all = (e && *e && *e != '0') ? 1 : 0;
        }
        // ROGUESQ_LOG_DL_SYNC: walk guest F3D DL tree counting G_RDPFULLSYNC
        // (0xE9) vs post-LLE RDP hist[0x29] (= runner syncs). Discriminates
        // guest omit (raw_e9=0) vs LLE drop (raw_e9>=1, syncs=0) on the
        // post-mission-overlay FULL_SYNC starvation (item -349 / s579).
        static int s_dl_sync = -1;
        if (s_dl_sync < 0) {
            const char* e = std::getenv("ROGUESQ_LOG_DL_SYNC");
            s_dl_sync = (e && *e && *e != '0') ? 1 : 0;
        }
        // ROGUESQ_LOG_DL_SYNC2 (m3 cimg-origin-desync, s661): independent of
        // LOG_DL_SYNC — read here (not just at the walker call site) so it
        // can gate do_probe/the outer sampling condition on its own; a probe
        // wired only into LOG_DL_SYNC's do_probe silently never fires when
        // only LOG_DL_SYNC2 is set.
        static int s_dl_sync2 = -1;
        if (s_dl_sync2 < 0) {
            const char* e = std::getenv("ROGUESQ_LOG_DL_SYNC2");
            s_dl_sync2 = (e && *e && *e != '0') ? 1 : 0;
        }
        static int s_e9_unified = -1;
        if (s_e9_unified < 0) {
            const char* rs64_la = std::getenv("ROGUESQ_LOG_ALL"); // s7728: LOG_ALL, as the other E9 readers
            const char* e = std::getenv("ROGUESQ_LOG_E9_UNIFIED");
            s_e9_unified = ((rs64_la && *rs64_la && *rs64_la != '0') || (e && *e && *e != '0')) ? 1 : 0;
        }
        // ROGUESQ_LOG_FS_SLOT densifies late dual-task dumps (every task
        // after s_n>=5200) so the stop edge is not lost to rate limits.
        static int s_fs_slot = -1;
        if (s_fs_slot < 0) {
            const char* e = std::getenv("ROGUESQ_LOG_FS_SLOT");
            s_fs_slot = (e && *e && *e != '0') ? 1 : 0;
        }
        if (s_log || s_dl_sync || s_dl_sync2 || s_e9_unified || s_fs_slot) {
            static int s_n = 0;
            ++s_n;
            const bool sample_runner = s_log && (s_log_all || s_n <= 8 || (s_n & 31) == 0);
            // Probe rate: first 20 (boot positive control), first 40 early
            // syncs>0, first 30 late (s_n>=4000) syncs>0 (post-exit control),
            // first 120 consec zero-sync + every 50th after.
            static int consec_zero = 0;
            static int n_with_sync_probed = 0;
            static int late_sync_probed = 0;
            static int ever_sync = 0;
            // Pre-drain estimate: when not sampling runner and not log_all,
            // hist may be stale; force drain whenever we might probe.
            // Actual syncs come from drained hist below.
            const bool dense_slot = s_fs_slot && s_n >= 5200;
            bool force_for_probe = (s_dl_sync || s_dl_sync2 || dense_slot) && (
                s_n <= 20 || consec_zero < 120 ||
                (consec_zero > 0 && (consec_zero % 50) == 0) ||
                n_with_sync_probed < 40 ||
                (s_n >= 4000 && late_sync_probed < 30) ||
                s_n >= 4000 ||
                dense_slot);
            if (sample_runner || force_for_probe) {
                // Pull the dpc_bridge per-task RDP-opcode histogram (raw 6-bit
                // RDP opcodes, NOT the F3D DL byte). 0x08-0x0F = triangle
                // variants; 0x24/0x25 = TEXRECT/TEXRECT_FLIP; 0x29 = SYNC_FULL;
                // 0x36 = FILL_RECTANGLE; 0x3E/0x3F = SET_DEPTH/COLOR_IMAGE.
                uint32_t hist[64];
                rs64_dpc_drain_histogram(hist);
                uint32_t tris = 0;
                for (int i = 0x08; i <= 0x0F; ++i) tris += hist[i];
                const uint32_t syncs = hist[0x29];
                if (syncs > 0) {
                    consec_zero = 0;
                    ever_sync = 1;
                } else if (ever_sync) {
                    consec_zero++;
                }
                if (sample_runner) {
                    fprintf(stderr,
                            "[runner] task #%d exit=%d dl_ptr=0x%08X tris=%u texrects=%u fillrects=%u syncs=%u cimg=%u depth=%u\n",
                            s_n, (int)r, dl_ptr,
                            tris, hist[0x24] + hist[0x25], hist[0x36],
                            syncs, hist[0x3F], hist[0x3E]);
                }
                const bool do_probe = s_e9_unified ||
                    (s_dl_sync || s_dl_sync2 || dense_slot) && (
                    s_n <= 20 ||
                    (syncs > 0 && n_with_sync_probed < 40) ||
                    (syncs > 0 && s_n >= 4000 && late_sync_probed < 30) ||
                    (syncs == 0 && ever_sync && consec_zero <= 120) ||
                    (syncs == 0 && ever_sync && (consec_zero % 50) == 0) ||
                    (s_n >= 4000 && (s_n % 25) == 0) ||
                    dense_slot);
                if (do_probe) {
                    if (syncs > 0) {
                        if (s_n < 4000) n_with_sync_probed++;
                        else late_sync_probed++;
                    }
                    // Guest F3D walk (s581): two B5 semantics + linear scan.
                    // H-walk1: B5-as-ENDDL ends Factor5 chunk streams early
                    //   (HLE maps 0xB5 → no-op; real ENDDL is 0xB8).
                    // H-walk3: no guest 0xE9 in DL; LLE still emits RDP 0x29.
                    // Strict G_DL: only follow 0x06 when w0 payload bits are
                    // clean (Factor5 reuses opcode byte 0x06).
                    auto rbyte = [&](uint32_t a) -> uint8_t {
                        a &= 0x7FFFFF;
                        return rdram[a ^ 3];
                    };
                    auto walk_tree = [&](bool b5_is_enddl, uint32_t* out_e9,
                                         uint32_t* out_b5, uint32_t* out_b8,
                                         uint32_t* out_cmds, uint32_t* out_jumps,
                                         char* first_ops, size_t first_ops_sz,
                                         char* end_reason, size_t end_reason_sz) {
                        uint32_t stack[32];
                        int sp = 0;
                        int jumps_left = 64;
                        uint32_t addr = dl_ptr & 0x7FFFFF;
                        uint32_t e9 = 0, b5 = 0, b8 = 0, cmds = 0, jumps = 0;
                        int fop_n = 0;
                        first_ops[0] = '\0';
                        end_reason[0] = '\0';
                        for (int i = 0; i < 8192 && addr + 8u <= 0x800000u; ++i) {
                            uint8_t op = rbyte(addr);
                            uint32_t w0 = ((uint32_t)rbyte(addr) << 24) |
                                          ((uint32_t)rbyte(addr + 1) << 16) |
                                          ((uint32_t)rbyte(addr + 2) <<  8) |
                                          ((uint32_t)rbyte(addr + 3));
                            cmds++;
                            if (fop_n < 16) {
                                int used = (int)strlen(first_ops);
                                if (used < (int)first_ops_sz - 4) {
                                    snprintf(first_ops + used, first_ops_sz - used,
                                             "%s%02X", fop_n ? "," : "", op);
                                }
                                fop_n++;
                            }
                            if (op == 0xE9) e9++;
                            if (op == 0xB5) b5++;
                            if (op == 0xB8) b8++;
                            const bool is_end = (op == 0xB8 || op == 0xDF ||
                                                 (b5_is_enddl && op == 0xB5));
                            if (is_end) {
                                if (sp > 0) { addr = stack[--sp]; continue; }
                                snprintf(end_reason, end_reason_sz, "end%02X", op);
                                break;
                            }
                            // Strict G_DL (F3D 0x06): w0 payload excl. branch
                            // bit16 must be zero. 0xDE is F3DEX2 G_DL — rare
                            // here; keep loose for that opcode only.
                            bool is_dl = false;
                            uint8_t branch = 0;
                            if (op == 0x06) {
                                if ((w0 & 0x00FEFFFFu) == 0) {
                                    is_dl = true;
                                    branch = (uint8_t)((w0 >> 16) & 1);
                                }
                            } else if (op == 0xDE) {
                                is_dl = true;
                                branch = rbyte(addr + 1);
                            }
                            if (is_dl && jumps_left > 0) {
                                uint32_t w1 = ((uint32_t)rbyte(addr + 4) << 24) |
                                              ((uint32_t)rbyte(addr + 5) << 16) |
                                              ((uint32_t)rbyte(addr + 6) <<  8) |
                                              ((uint32_t)rbyte(addr + 7));
                                uint32_t target = w1 & 0x7FFFFF;
                                if (branch == 0 && sp < 32)
                                    stack[sp++] = (addr + 8) & 0x7FFFFF;
                                addr = target;
                                jumps_left--;
                                jumps++;
                                continue;
                            }
                            addr = (addr + 8) & 0x7FFFFF;
                        }
                        if (!end_reason[0]) {
                            snprintf(end_reason, end_reason_sz,
                                     addr + 8u > 0x800000u ? "oob" : "lim");
                        }
                        *out_e9 = e9; *out_b5 = b5; *out_b8 = b8;
                        *out_cmds = cmds; *out_jumps = jumps;
                    };
                    uint32_t e9_a = 0, b5_a = 0, b8_a = 0, cmds_a = 0, jumps_a = 0;
                    uint32_t e9_b = 0, b5_b = 0, b8_b = 0, cmds_b = 0, jumps_b = 0;
                    char first_ops[48];
                    char end_a[8], end_b[8];
                    walk_tree(true,  &e9_a, &b5_a, &b8_a, &cmds_a, &jumps_a,
                              first_ops, sizeof(first_ops), end_a, sizeof(end_a));
                    walk_tree(false, &e9_b, &b5_b, &b8_b, &cmds_b, &jumps_b,
                              first_ops, sizeof(first_ops), end_b, sizeof(end_b));
                    // Linear scan: every 8-byte slot from dl_ptr, no control
                    // flow. Catches 0xE9 sitting past a false early end.
                    uint32_t lin_e9 = 0, lin_b5 = 0, lin_b8 = 0, lin_cmds = 0;
                    {
                        uint32_t addr = dl_ptr & 0x7FFFFF;
                        for (int i = 0; i < 4096 && addr + 8u <= 0x800000u; ++i) {
                            uint8_t op = rbyte(addr);
                            lin_cmds++;
                            if (op == 0xE9) lin_e9++;
                            if (op == 0xB5) lin_b5++;
                            if (op == 0xB8) lin_b8++;
                            addr = (addr + 8) & 0x7FFFFF;
                        }
                    }
                    // ROGUESQ_LOG_DL_SYNC2=1 (m3 cimg-origin-desync, s661):
                    // six-command-aware walk of the SAME guest SW DL, honouring
                    // the inline-data advances from docs/F5-UCODE-REFERENCE.md
                    // (MoveMem 0x03 +16, TriGen 0x05 +32, Tri 0xB4/0xBF +16 iff
                    // w0&2, TexrectGen 0xBD +16, SetOtherMode_*_EX 0xB3/0xBE +8)
                    // instead of walk_tree's/the linear scan's fixed 8-byte
                    // step. Discriminates H-legit from H-desync-inline: if this
                    // walk reaches a SETCIMG-shaped (op 0xFF) command whose
                    // operands match the observed wild CIMG (addr=0x1F0D74
                    // w=1161), the SW DL genuinely contains it under a length
                    // model that respects every documented inline-data command
                    // — not merely as an artifact of a fixed-stride walk. If it
                    // never does, the fixed-stride walkers' apparent
                    // presence/absence of SETCIMG proves nothing either way.
                    // (s_dl_sync2 itself is read once, earlier in this
                    // function, so it can also gate do_probe/force_for_probe.)
                    if (s_dl_sync2 && do_probe) {
                        uint32_t addr2 = dl_ptr & 0x7FFFFF;
                        uint32_t stack2[32];
                        int sp2 = 0;
                        int jumps_left2 = 64;
                        uint32_t cmds2 = 0, jumps2 = 0, b8_2 = 0;
                        uint32_t setcimg_n = 0, setcimg_wild = 0;
                        uint32_t wild_addr = 0, wild_w = 0;
                        uint32_t e9_aligned = 0; // item -421: E9 hits at inline-data-respecting cmd boundaries
                        char end2[8] = {0};
                        for (int i = 0; i < 8192 && addr2 + 8u <= 0x800000u; ++i) {
                            uint8_t op = rbyte(addr2);
                            uint32_t w0 = ((uint32_t)rbyte(addr2) << 24) |
                                          ((uint32_t)rbyte(addr2 + 1) << 16) |
                                          ((uint32_t)rbyte(addr2 + 2) <<  8) |
                                          ((uint32_t)rbyte(addr2 + 3));
                            cmds2++;
                            if (op == 0xE9) e9_aligned++;
                            if (op == 0xFF) {
                                setcimg_n++;
                                const uint16_t w = (uint16_t)((w0 & 0xFFFu) + 1u);
                                if (!(w == 320 || w == 512 || w == 640 || w == 1024)) {
                                    setcimg_wild++;
                                    if (wild_w == 0) {
                                        wild_w = w;
                                        wild_addr = ((uint32_t)rbyte(addr2 + 4) << 24) |
                                                    ((uint32_t)rbyte(addr2 + 5) << 16) |
                                                    ((uint32_t)rbyte(addr2 + 6) <<  8) |
                                                    ((uint32_t)rbyte(addr2 + 7));
                                    }
                                }
                            }
                            if (op == 0xB8 || op == 0xDF) {
                                b8_2++;
                                if (sp2 > 0) { addr2 = stack2[--sp2]; continue; }
                                snprintf(end2, sizeof(end2), "%s", "endB8");
                                break;
                            }
                            bool is_dl2 = false;
                            uint8_t branch2 = 0;
                            if (op == 0x06) {
                                if ((w0 & 0x00FEFFFFu) == 0) {
                                    is_dl2 = true;
                                    branch2 = (uint8_t)((w0 >> 16) & 1);
                                }
                            } else if (op == 0xDE) {
                                is_dl2 = true;
                                branch2 = rbyte(addr2 + 1);
                            }
                            if (is_dl2 && jumps_left2 > 0) {
                                uint32_t w1 = ((uint32_t)rbyte(addr2 + 4) << 24) |
                                              ((uint32_t)rbyte(addr2 + 5) << 16) |
                                              ((uint32_t)rbyte(addr2 + 6) <<  8) |
                                              ((uint32_t)rbyte(addr2 + 7));
                                uint32_t target2 = w1 & 0x7FFFFF;
                                if (branch2 == 0 && sp2 < 32)
                                    stack2[sp2++] = (addr2 + 8) & 0x7FFFFF;
                                addr2 = target2;
                                jumps_left2--;
                                jumps2++;
                                continue;
                            }
                            uint32_t extra = 0;
                            switch (op) {
                                case 0x03: extra = 16; break; // MoveMem
                                case 0x05: extra = 32; break; // TriGen
                                case 0xB4: case 0xBF: extra = (w0 & 2) ? 16 : 0; break; // Tri
                                case 0xBD: extra = 16; break; // TexrectGen
                                case 0xB3: case 0xBE: extra = 8; break; // SetOtherMode_*_EX
                                default: break;
                            }
                            addr2 = (addr2 + 8 + extra) & 0x7FFFFF;
                        }
                        if (!end2[0]) {
                            snprintf(end2, sizeof(end2), "%s", addr2 + 8u > 0x800000u ? "oob" : "lim");
                        }
                        fprintf(stderr,
                                "[dl-sync-probe2] task=#%d cmds=%u jumps=%u b8=%u end=%s "
                                "setcimg_n=%u setcimg_wild=%u wild_addr=0x%X wild_w=%u e9_aligned=%u dl_ptr=0x%08X\n",
                                s_n, cmds2, jumps2, b8_2, end2,
                                setcimg_n, setcimg_wild, wild_addr, wild_w, e9_aligned, dl_ptr);
                        rs64_rdp_advance_report((uint32_t)s_n, dl_ptr, e9_aligned);
                        rs64_e9prov_aligned(task_serial, dl_ptr, e9_aligned);
                        rs64_e9prov_task_join_report(task_serial);
                        fflush(stderr);
                    }
                    const uint32_t fs_addr = rs64_dpc_get_last_fullsync_addr();
                    uint8_t fs_b0 = 0xFF;
                    if (fs_addr != 0xFFFFFFFFu && (fs_addr & 0x7FFFFF) + 1u <= 0x800000u)
                        fs_b0 = rbyte(fs_addr);
                    if (s_dl_sync) {
                        fprintf(stderr,
                                "[dl-sync-probe] task=#%d syncs=%u "
                                "e9_a=%u e9_b=%u lin_e9=%u "
                                "b5_a=%u b8_a=%u cmds_a=%u jumps_a=%u end_a=%s "
                                "b5_b=%u b8_b=%u cmds_b=%u jumps_b=%u end_b=%s "
                                "lin_b5=%u lin_b8=%u lin_cmds=%u "
                                "fs_addr=0x%08X fs_b0=%02X "
                                "dl_ptr=0x%08X tris=%u first_ops=%s\n",
                                s_n, syncs,
                                e9_a, e9_b, lin_e9,
                                b5_a, b8_a, cmds_a, jumps_a, end_a,
                                b5_b, b8_b, cmds_b, jumps_b, end_b,
                                lin_b5, lin_b8, lin_cmds,
                                fs_addr, fs_b0,
                                dl_ptr, tris, first_ops);
                    }
                    // Dense post-task dump of the fixed FULL_SYNC side-slot
                    // around the dual-buffer plateau edge (item -353).
                    if (s_fs_slot && (dense_slot || (s_n >= 4000 && (s_n % 25) == 0) ||
                                      s_n <= 20)) {
                        static uint32_t slot_off = 0;
                        static int slot_inited = 0;
                        if (!slot_inited) {
                            slot_off = 0x76DF60u;
                            if (const char* e = std::getenv("ROGUESQ_FS_SLOT_ADDR")) {
                                unsigned long v = strtoul(e, nullptr, 0);
                                if (v > 0 && v < 0x800000u) slot_off = (uint32_t)v;
                            }
                            slot_off &= 0x7FFFFFu;
                            slot_inited = 1;
                        }
                        uint8_t b[16];
                        for (int i = 0; i < 16; ++i) b[i] = rbyte(slot_off + (uint32_t)i);
                        // Also dump 8 bytes immediately before the slot for
                        // ring-adjacency / ownership context.
                        uint8_t pre[8];
                        for (int i = 0; i < 8; ++i) {
                            uint32_t a = (slot_off >= 8u) ? (slot_off - 8u + (uint32_t)i) : 0;
                            pre[i] = rbyte(a);
                        }
                        fprintf(stderr,
                            "[fs-slot] n=%d event=task_end task=#%d syncs=%u "
                            "dl_ptr=0x%08X tris=%u e9_b=%u end_b=%s "
                            "slot=0x%08X b0=%02X bytes=%02X%02X%02X%02X%02X%02X%02X%02X "
                            "pre=%02X%02X%02X%02X%02X%02X%02X%02X "
                            "fs_addr=0x%08X fs_b0=%02X\n",
                            s_n, s_n, syncs, dl_ptr, tris, e9_b, end_b,
                            slot_off, b[0],
                            b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7],
                            pre[0], pre[1], pre[2], pre[3],
                            pre[4], pre[5], pre[6], pre[7],
                            fs_addr, fs_b0);
                    }
                }
                fflush(stderr);
            }
        }
    }
    return r;
}

// Public entry point for the LLE GFX path — used by the renderer's send_dl
// callback when ROGUESQ_LLE_FORCE=1. Sets the pending-task statics that
// factor5_gfx_runner reads, writes the OSTask struct to DMEM[0xFC0..0x1000]
// (real SP_BOOT does this DMA-style; the runner mimics SP_BOOT but skips
// this step), then invokes the LLE runner.
extern "C" void rs64_s7521_task(uint8_t* rdram, const OSTask* task); extern "C" int rs64_s7521_on;  // s7521 class FR
extern "C" int rs64_s7526_alt; extern "C" int rs64_s7526_task_begin();  // s7526 V2P twin (src/rsp/s7526_v2p_twin.cpp)
extern "C" int rs64_run_lle_gfx(uint8_t* rdram, const OSTask* task) {
    if (rs64_s7521_on) rs64_s7521_task(rdram, task);
    // The host owns both buffers; a teardown can invalidate the callback
    // context before the scheduler drops its last task reference.
    if (rdram == nullptr || g_dmem_cur == nullptr || task == nullptr) {
        return -1;
    }
    std::lock_guard<std::recursive_mutex> lle_lock(g_lle_task_mutex);
    s4249::Hold s4249_hold(1);
    static int s_log_g1d_task = -1;
    if (s_log_g1d_task < 0) {
        const char* v = std::getenv("ROGUESQ_LOG_G1D_TASK");
        s_log_g1d_task = (v && *v && *v != '0') ? 1 : 0;
    }
    const uint32_t g1d_phase = rs64_phase_ord();
    if (s_log_g1d_task && g1d_phase == 4) {
        static uint32_t s_g1d_task_rows = 0;
        if (s_g1d_task_rows < 4096) {
            ++s_g1d_task_rows;
            uint32_t w28 = 0, w78 = 0;
            if (s_g1d_task_rows <= 16) {
                auto gword = [&](uint32_t guest) -> uint32_t {
                    if (!rdram || guest < 0x80000000u || guest >= rs64_ram_top) return 0xFFFFFFFFu;
                    if (rs64_ram_top - guest < 4u) return 0xFFFFFFFFu;
                    return rs64_rdram_u32(rdram, guest - 0x80000000u);
                };
                const uint32_t dp = (uint32_t)task->t.data_ptr;
                w28 = gword(dp + 0x28u);
                w78 = gword(dp + 0x78u);
            }
            if (s_g1d_task_rows <= 16) {
                std::fprintf(stderr,
                    "[g1d-task] phase=%u row=%u task_ptr=%p type=0x%08X "
                    "data_ptr=0x%08X data_size=0x%08X ucode=0x%08X "
                    "ucode_data=0x%08X ucode_data_size=0x%08X root_dl=0x%08X "
                    "w28=0x%08X w78=0x%08X\n",
                    g1d_phase, s_g1d_task_rows, (const void*)task,
                    (uint32_t)task->t.type, (uint32_t)task->t.data_ptr,
                    (uint32_t)task->t.data_size, (uint32_t)task->t.ucode,
                    (uint32_t)task->t.ucode_data,
                    (uint32_t)task->t.ucode_data_size,
                    (uint32_t)task->t.data_ptr, w28, w78);
            } else {
                std::fprintf(stderr,
                    "[g1d-task] phase=%u row=%u task_ptr=%p type=0x%08X "
                    "data_ptr=0x%08X data_size=0x%08X ucode=0x%08X "
                    "ucode_data=0x%08X ucode_data_size=0x%08X root_dl=0x%08X\n",
                    g1d_phase, s_g1d_task_rows, (const void*)task,
                    (uint32_t)task->t.type, (uint32_t)task->t.data_ptr,
                    (uint32_t)task->t.data_size, (uint32_t)task->t.ucode,
                    (uint32_t)task->t.ucode_data,
                    (uint32_t)task->t.ucode_data_size,
                    (uint32_t)task->t.data_ptr);
            }
            std::fflush(stderr);
        }
    }
    rs64_rdp_advance_reset();
    s_pending_task_data_ptr        = (uint32_t)task->t.data_ptr;
    s_pending_task_ucode_data      = (uint32_t)task->t.ucode_data;
    s_pending_task_ucode_data_size = (uint32_t)task->t.ucode_data_size;

    // Write OSTask to DMEM[0xFC0..0x1000] in big-endian byte order via the
    // i^3 swizzle (matching RSP_MEM_W_LOAD's encoding). The ucode reads
    // task fields from this region via DMEM[r18+offset] where r18 = 0xFC0.
    // OSTask is 0x40 bytes: type/flags/ucode_boot/ucode_boot_size/ucode/
    // ucode_size/ucode_data/ucode_data_size/dram_stack/dram_stack_size/
    // output_buff/output_buff_size/data_ptr/data_size/yield_data_ptr/yield_data_size.
    auto poke = [](uint32_t off, uint32_t val) {
        for (int j = 0; j < 4; ++j) {
            g_dmem_cur[(off + j) ^ 3] = (uint8_t)(val >> (24 - j * 8));
        }
    };
    // s7524 class FT: retail osSpTaskLoad (0x80033E3C) DMAs a copy converted by _VirtualToPhysicalTask (0x80033D20: ucode,
    // ucode_data, dram_stack, output_buff, output_buff_size, data_ptr, yield_data_ptr when non-null); the port's
    // osSpTaskLoad_recomp skips it, so the ucode sees KSEG0 pointers against 24-bit DPC_CURRENT. ROGUESQ_S7524_V2P=1 applies
    // the retail conversion to the DMEM copy only (opt-in; the guest's task in RDRAM is untouched, as on hardware).
    static const bool s7524_v2p = [] { const char* e = std::getenv("ROGUESQ_S7524_V2P"); bool on = e && *e && *e != '0';
        if (on) std::fprintf(stderr, "[s7524] DMEM OSTask virtual->physical conversion armed\n"); return on; }();
    // s7526: ROGUESQ_S7524_V2P=alt -> per-task pseudo-random on/off + forwarded-byte twin digest (src/rsp/s7526_v2p_twin.cpp).
    const bool v2p_on = rs64_s7526_alt ? rs64_s7526_task_begin() != 0 : s7524_v2p;
    auto v2p = [v2p_on](uint32_t v) -> uint32_t { return (v2p_on && v >= 0x80000000u && v < 0xC0000000u) ? (v & 0x1FFFFFFFu) : v; };
    poke(0xFC0 + 0x00, (uint32_t)task->t.type);
    poke(0xFC0 + 0x04, (uint32_t)task->t.flags);
    poke(0xFC0 + 0x08, (uint32_t)task->t.ucode_boot);
    poke(0xFC0 + 0x0C, (uint32_t)task->t.ucode_boot_size);
    poke(0xFC0 + 0x10, v2p((uint32_t)task->t.ucode));
    poke(0xFC0 + 0x14, (uint32_t)task->t.ucode_size);
    poke(0xFC0 + 0x18, v2p((uint32_t)task->t.ucode_data));
    poke(0xFC0 + 0x1C, (uint32_t)task->t.ucode_data_size);
    poke(0xFC0 + 0x20, v2p((uint32_t)task->t.dram_stack));
    poke(0xFC0 + 0x24, (uint32_t)task->t.dram_stack_size);
    poke(0xFC0 + 0x28, v2p((uint32_t)task->t.output_buff));
    poke(0xFC0 + 0x2C, v2p((uint32_t)task->t.output_buff_size));
    poke(0xFC0 + 0x30, v2p((uint32_t)task->t.data_ptr));
    poke(0xFC0 + 0x34, (uint32_t)task->t.data_size);
    poke(0xFC0 + 0x38, v2p((uint32_t)task->t.yield_data_ptr));
    poke(0xFC0 + 0x3C, (uint32_t)task->t.yield_data_size);
    { extern volatile uint32_t g_rs64_s7481_task_out; g_rs64_s7481_task_out = (uint32_t)task->t.output_buff | 0x80000000u; } // s7481 EH frame-span class
    { extern volatile uint32_t g_rs64_g1cf_tasks, g_rs64_g1cf_dsize; ++g_rs64_g1cf_tasks; g_rs64_g1cf_dsize += (uint32_t)task->t.data_size; } // s6070 g1cf
    rs64_diag_fprintf(stderr, "[lle task] flags=0x%X yield_ptr=0x%08X yield_size=0x%X data=0x%08X dsize=0x%X out=0x%08X\n",
            (uint32_t)task->t.flags, (uint32_t)task->t.yield_data_ptr,
            (uint32_t)task->t.yield_data_size, (uint32_t)task->t.data_ptr,
            (uint32_t)task->t.data_size, (uint32_t)task->t.output_buff);

    // ROGUESQ_LOG_SEQ: dump the head of the task's display list. Most gfx
    // tasks emit ZERO RDP bytes; this says whether the game handed us an
    // empty/short DL (game-side pacing) or a real one the ucode ignored.
    if ([]{
            static const bool v = []{
                const char *e = std::getenv("ROGUESQ_LOG_SEQ");
                return e && *e && *e != '0';
            }();
            return v;
        }()) {
        auto dump = [&](const char *tag, uint32_t addr, int bytes) {
            const uint32_t a = addr & 0x7FFFFF;
            if (!a || a + bytes > 0x800000) return;
            fprintf(stderr, "[%s] 0x%08X:", tag, addr);
            for (int i = 0; i < bytes; ++i) {
                fprintf(stderr, "%s%02X", (i % 8) == 0 ? " " : "",
                        (unsigned)rdram[(a + i) ^ 3]);
            }
            fprintf(stderr, "\n");
        };
        // The per-task DL is a fixed 5-command stub whose op-0x06 entries chase
        // sub-DLs; the frame's real content lives there. Dump both so an
        // empty-output task can be told apart from an empty sub-DL.
        dump("dl-head", (uint32_t)task->t.data_ptr, 64);
        const uint32_t dl = (uint32_t)task->t.data_ptr & 0x7FFFFF;
        if (dl && dl + 24 <= 0x800000) {
            auto word = [&](uint32_t off) {
                return ((uint32_t)rdram[(off + 0) ^ 3] << 24) |
                       ((uint32_t)rdram[(off + 1) ^ 3] << 16) |
                       ((uint32_t)rdram[(off + 2) ^ 3] <<  8) |
                       ((uint32_t)rdram[(off + 3) ^ 3]);
            };
            dump("dl-sub0", word(dl + 4), 96);
            dump("dl-sub1", word(dl + 12), 64);
            dump("dl-sub2", word(dl + 20), 96);
        }
        fflush(stderr);
    }

    return (int)factor5_gfx_runner(rdram, (uint32_t)task->t.ucode);
}

RspUcodeFunc* get_rsp_microcode(const OSTask* task) {
    if (task == nullptr) {
        return &unknown_task_stub;
    }
    switch (task->t.type) {
    case M_GFXTASK:
        // Cache OSTask fields for factor5_gfx_runner. The runner needs to:
        //   - DMA the ucode_data segment to DMEM (mimicking SP_BOOT) so each
        //     task starts with fresh per-task data, not state carried over
        //     from the previous task's exit.
        //   - DMA the first chunk of the DL into DMEM[0x170] so the first
        //     dispatch loop iter has real bytes.
        s_pending_task_data_ptr        = (uint32_t)task->t.data_ptr;
        s_pending_task_ucode_data      = (uint32_t)task->t.ucode_data;
        s_pending_task_ucode_data_size = (uint32_t)task->t.ucode_data_size;
        return &factor5_gfx_runner;
    case M_AUDTASK: {
        s_pending_audio_task = task;
        s_pending_audio_thread_id = rs64_m5_identity_thread_id();
        s_pending_audio_generation = g_audio_task_generation.fetch_add(
            1, std::memory_order_relaxed);
        g_m5_latest_audio_generation.store(s_pending_audio_generation,
                                           std::memory_order_release);
        s_pending_task_data_ptr = (uint32_t)task->t.data_ptr;
        s_pending_task_data_size = (uint32_t)task->t.data_size;
        rs64_m5_pcm_task_data_set(s_pending_task_data_ptr);
        g_rs64_audio_break_pc = 0;
        // The image arm is default; set ROGUESQ_AUDIO_UCODE=0 for the stub
        // control used by the incremental audio qualification steps.
        {
            // Read the arm for each task. Audio task submission can outlive
            // the probe that selected the previous task, so caching this
            // process-wide would make the explicit silent control stale.
            const char* audio_ucode = getenv("ROGUESQ_AUDIO_UCODE");
            const int use_real_audio_ucode =
                !(audio_ucode && audio_ucode[0] == '0');
            // s300: ground-truth counter for whether M_AUDTASK is ever
            // dispatched at all (step 1's source trace found the gate byte
            // doesn't directly block it, but the first soak logged 0
            // [musyx-dma-call] hits -- that instrument turned out to be the
            // PI-DMA sample-streaming path, not RSP task submission, so it
            // doesn't settle the question either way). Always-on, cheap.
            // s315: the original `n<20 || n%256==0` cap is the SAME unwidened
            // flat-cap bug s312/s313 found and fixed in the other M5 audio
            // diagnostics (reach-*/tick-audio-seq/musyx-gate1) -- it produces
            // exactly 20 print lines whether the counter truly stops at 20 or
            // keeps incrementing silently until n=256, which a ~40-call
            // freeze would never reach. The "[audtask-dispatch] stops at
            // 20/20" conclusion (s307-313, CURRENT-TRUTH item -173) was
            // resting on this same illusion, unverified. Widened to the
            // established n<40||(n%128)==0 resample convention so this is a
            // direct measurement, not an assumption.
            static uint32_t s_audtask_n = 0;
            rs64_filter_voice_audit_positive_control();
            rs64_m5_init_voice_probe_control();
            if (s_audtask_n < 40 || (s_audtask_n % 128) == 0) {
                fprintf(stderr, "[audtask-dispatch] n=%u real_ucode=%d\n",
                        s_audtask_n, use_real_audio_ucode);
            }
            s_audtask_n++;
            if (use_real_audio_ucode) return &factor5_ucode_b_probe;
        }
        return &musyx_stub_probe;
    }
    default:
        // Don't crash — log once per distinct type and stub it out.
        static thread_local uint32_t last_unknown = 0;
        if (task->t.type != last_unknown) {
            last_unknown = task->t.type;
            fprintf(stderr, "[RSP] Stubbing unknown task type: %" PRIu32 " (0x%08X)\n",
                task->t.type, task->t.type);
            fflush(stderr);
        }
        return &unknown_task_stub;
    }
}

// ---------------------------------------------------------------------------
// Audio (SDL2)
// ---------------------------------------------------------------------------
static SDL_AudioDeviceID audio_device = 0;
// s6739: osAiSetFrequency (game thread) closes and reopens the device while the events thread
// polls SDL_GetQueuedAudioSize (events.cpp get_remaining_audio_bytes): SIGSEGV in SDL on a freed
// device (plain launch, boot ~6 s). Every SDL call on audio_device holds this lock.
static std::recursive_mutex audio_device_mutex;
static uint32_t audio_sample_rate = 48000;

extern "C" uint32_t rs64_audio_rate_snapshot() {
    return audio_sample_rate;
}
static std::atomic<uint32_t> g_rs64_pcm_consumer_count{0};
static std::atomic<uint32_t> g_rs64_pcm_consumer_phase_key{0xFFFFFFFFu};

static bool rs64_m5_audio_host_probe_enabled(uint32_t& phase, uint32_t& width,
                                               uint32_t& origin) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_AUDIO_HOST");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return false;
    phase = rs64_phase_ord();
    width = rs64_vi_committed_width();
    origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    return (width == 1024u && origin == 0x00790400u) ||
           (width == 512u && origin == 0x006AB400u);
}

static void rs64_m5_audio_host_row(const char* edge, uint32_t queued_before,
                                    uint32_t queued_after, uint32_t pcm_bytes,
                                    uint32_t samples) {
    uint32_t phase = 0, width = 0, origin = 0;
    if (!rs64_m5_audio_host_probe_enabled(phase, width, origin)) return;
    static uint32_t row_phase_key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    static uint32_t previous_queue = 0;
    static uint64_t sequence = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != row_phase_key) {
        row_phase_key = key;
        rows = 0;
        previous_queue = queued_before;
    }
    if (rows >= 1024u) return;
    const auto now = std::chrono::steady_clock::now().time_since_epoch();
    const uint64_t now_us = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::microseconds>(now).count());
    const int64_t sample_delta = static_cast<int64_t>(queued_before) -
                                 static_cast<int64_t>(previous_queue);
    const int64_t call_delta = static_cast<int64_t>(queued_after) -
                               static_cast<int64_t>(queued_before);
    std::fprintf(stderr,
        "[m5-audio-host] seq=%llu n=%u edge=%s phase=%u width=%u "
        "origin=0x%06X t_us=%llu queued_before=%u queued_after=%u "
        "sample_delta=%lld call_delta=%lld pcm_bytes=%u samples=%u device=%u\n",
        static_cast<unsigned long long>(sequence++), rows++, edge, phase, width,
        origin, static_cast<unsigned long long>(now_us), queued_before,
        queued_after, static_cast<long long>(sample_delta),
        static_cast<long long>(call_delta), pcm_bytes, samples,
        static_cast<unsigned>(audio_device));
    std::fflush(stderr);
    previous_queue = queued_after;
}

static uint32_t rs64_m5_audio_queue_snapshot() {
    std::lock_guard<std::recursive_mutex> lock(audio_device_mutex);
    return audio_device ? SDL_GetQueuedAudioSize(audio_device) : 0;
}

static uint32_t rs64_m5_pcm_consumer_count() {
    return g_rs64_pcm_consumer_count.load(std::memory_order_relaxed);
}

static bool rs64_m5_callback_order_event(uint32_t width, uint32_t origin,
                                         uint32_t& sequence, uint64_t& time_us) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_CALLBACK_ORDER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !((width == 1024u && origin == 0x00790400u) ||
                      (width == 512u && origin == 0x006AB400u))) return false;
    static std::mutex mutex;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static uint32_t next_sequence = 0;
    std::lock_guard<std::mutex> lock(mutex);
    const uint32_t key = (width << 24) ^ origin;
    if (key != phase_key) {
        phase_key = key;
        next_sequence = 0;
    }
    sequence = next_sequence++;
    const auto now = std::chrono::steady_clock::now().time_since_epoch();
    time_us = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::microseconds>(now).count());
    return true;
}

// ---------------------------------------------------------------------------
// Output-device routing (owner request 2026-10-19). By default the game plays
// through the macOS default output and follows it when it changes. To pin the
// game to one device instead (e.g. muted laptop speakers while everything else
// plays elsewhere), name it by case-insensitive substring:
//   ROGUESQ_AUDIO_DEVICE="MacBook Pro Speakers"            (env var, wins), or
//   the same text on the first line of audio_device.txt beside the executable.
// With neither set, the built-in default is "MacBook Pro Speakers" (owner
// request 2026-10-19). "default" follows the system default. F9 cycles outputs live
// (default -> each device -> default) and saves the choice to audio_device.txt,
// so the loop's headless runs pick it up too. Available names are logged as
// "[audio-route] device[i]=..." at first open.
// ---------------------------------------------------------------------------
static std::atomic<int> g_audio_route_cycle{0};   // F9 presses; consumed on the audio thread
static std::string g_audio_route_pref;            // audio thread only after first open
static bool g_audio_route_loaded = false;

static std::string audio_route_file_path() {
    char* base = SDL_GetBasePath();
    std::string path = base ? std::string(base) + "audio_device.txt" : "audio_device.txt";
    if (base) SDL_free(base);
    return path;
}

static std::string audio_route_trim(std::string v) {
    while (!v.empty() && (v.back() == '\n' || v.back() == '\r' || v.back() == ' ' || v.back() == '\t')) v.pop_back();
    size_t i = 0;
    while (i < v.size() && (v[i] == ' ' || v[i] == '\t')) ++i;
    return v.substr(i);
}

static bool audio_route_is_default(const std::string& v) {
    if (v.empty()) return true;
    std::string l = v;
    for (auto& c : l) c = (char)std::tolower((unsigned char)c);
    return l == "default";
}

static void audio_route_load_pref() {
    if (g_audio_route_loaded) return;
    g_audio_route_loaded = true;
    if (const char* env = std::getenv("ROGUESQ_AUDIO_DEVICE")) {
        g_audio_route_pref = audio_route_trim(env);
        fprintf(stderr, "[audio-route] preference from ROGUESQ_AUDIO_DEVICE: '%s'\n", g_audio_route_pref.c_str());
    } else if (FILE* f = fopen(audio_route_file_path().c_str(), "r")) {
        char line[256] = {0};
        if (fgets(line, sizeof line, f)) g_audio_route_pref = audio_route_trim(line);
        fclose(f);
        fprintf(stderr, "[audio-route] preference from %s: '%s'\n", audio_route_file_path().c_str(), g_audio_route_pref.c_str());
    } else {
        // Owner default "for now" (2026-10-19): with no env var and no file, play on
        // the laptop speakers. If they are absent, audio_route_resolve() falls back
        // to the system default. Write "default" to audio_device.txt to undo.
        g_audio_route_pref = "MacBook Pro Speakers";
        fprintf(stderr, "[audio-route] preference from built-in default: '%s'\n", g_audio_route_pref.c_str());
    }
    const int n = SDL_GetNumAudioDevices(0);
    for (int i = 0; i < n; ++i) {
        const char* name = SDL_GetAudioDeviceName(i, 0);
        fprintf(stderr, "[audio-route] device[%d]=%s\n", i, name ? name : "?");
    }
    fflush(stderr);
}

// Exact SDL device name for the preference, or empty for the system default.
static std::string audio_route_resolve(bool quiet = false) {
    if (audio_route_is_default(g_audio_route_pref)) return {};
    std::string want = g_audio_route_pref;
    for (auto& c : want) c = (char)std::tolower((unsigned char)c);
    const int n = SDL_GetNumAudioDevices(0);
    for (int i = 0; i < n; ++i) {
        const char* name = SDL_GetAudioDeviceName(i, 0);
        if (!name) continue;
        std::string l = name;
        for (auto& c : l) c = (char)std::tolower((unsigned char)c);
        if (l.find(want) != std::string::npos) return name;
    }
    if (quiet) return {};
    fprintf(stderr, "[audio-route] no output device matches '%s'; using the system default\n", g_audio_route_pref.c_str());
    fflush(stderr);
    return {};
}

static std::string g_audio_open_name;  // s7199: resolved name of the open device, "" = system default (audio_device_mutex)
static void open_audio_output() {
    std::lock_guard<std::recursive_mutex> lock(audio_device_mutex);
    audio_route_load_pref();
    SDL_AudioSpec desired{};
    desired.freq     = (int)audio_sample_rate;
    desired.format   = AUDIO_S16SYS;
    desired.channels = 2;
    desired.samples  = 1024;

    const std::string name = audio_route_resolve();
    audio_device = SDL_OpenAudioDevice(name.empty() ? nullptr : name.c_str(), 0, &desired, nullptr, 0);
    if (!audio_device && !name.empty()) {
        fprintf(stderr, "[audio-route] opening '%s' failed (%s); falling back to the system default\n",
                name.c_str(), SDL_GetError());
        audio_device = SDL_OpenAudioDevice(nullptr, 0, &desired, nullptr, 0);
        g_audio_open_name.clear();
    } else {
        g_audio_open_name = name;
    }
    if (!audio_device) {
        fprintf(stderr, "[Audio] SDL_OpenAudioDevice failed: %s\n", SDL_GetError());
        return;
    }
    fprintf(stderr, "[audio-route] output=%s rate=%u\n", name.empty() ? "<system default>" : name.c_str(),
            audio_sample_rate);
    fflush(stderr);
    SDL_PauseAudioDevice(audio_device, 0);
}

// Applies pending F9 presses: advance default -> device 0 -> ... -> default,
// persist the choice, and reopen. Runs on the audio thread (queue_samples); set_frequency
// also reopens from the game thread, so both hold audio_device_mutex (s6739).
static void audio_route_apply_cycle() {
    int presses = g_audio_route_cycle.exchange(0, std::memory_order_acq_rel);
    if (presses <= 0) return;
    audio_route_load_pref();
    const int n = SDL_GetNumAudioDevices(0);
    // Current position: -1 = default, else the index of the device in use.
    int pos = -1;
    const std::string cur = audio_route_resolve();
    for (int i = 0; i < n && !cur.empty(); ++i) {
        const char* name = SDL_GetAudioDeviceName(i, 0);
        if (name && cur == name) { pos = i; break; }
    }
    while (presses-- > 0) pos = (pos + 1 >= n) ? -1 : pos + 1;
    const char* next = (pos >= 0) ? SDL_GetAudioDeviceName(pos, 0) : nullptr;
    g_audio_route_pref = next ? next : "default";
    // s7428 class CK: audio_device.txt is the only owner-facing state a run persists besides the save. Probe/test runs
    // (ROGUESQ_NO_SAVE_WRITE, exported by tools/agent/runner.sh) must not change the next run's default, same as the save.
    const bool persist = !std::getenv("ROGUESQ_NO_SAVE_WRITE");
    if (persist) {
        if (FILE* f = fopen(audio_route_file_path().c_str(), "w")) {
            fprintf(f, "%s\n", g_audio_route_pref.c_str());
            fclose(f);
        }
    }
    fprintf(stderr, "[audio-route] F9 -> '%s' (%s %s)\n", g_audio_route_pref.c_str(),
            persist ? "saved to" : "NOT saved (ROGUESQ_NO_SAVE_WRITE):", audio_route_file_path().c_str());
    std::lock_guard<std::recursive_mutex> lock(audio_device_mutex);
    if (audio_device) {
        SDL_CloseAudioDevice(audio_device);
        audio_device = 0;
    }
    open_audio_output();
}

// s7199: output hot-plug. When the open output disconnects (TV off, headset gone) SDL2 marks the device disabled and
// nobody reopened one, so audio stayed dead until F9 or a rate change. Two detectors, either reopens: the
// SDL_AUDIODEVICEREMOVED event for our device id (posted by the event pump), and SDL_GetAudioDeviceStatus ==
// SDL_AUDIO_STOPPED polled every 250 ms (SDL2 reports a disconnected device as STOPPED; covers an event eaten by a
// filter). An SDL_AUDIODEVICEADDED whose name matches the preference while we run on the fallback default moves back
// onto it. Runs on the audio thread like F9. ROGUESQ_AUDIO_HOTPLUG=0 = old behaviour.
// Forced arm: ROGUESQ_AUDIO_REMOVE_TEST=<sec> pushes a synthetic REMOVED for the open device at <sec>.
// Bitmask of removed playback ids (bit = id & 31): a real removal posts REMOVED for our id followed at once by one for
// id 0 (measured s7199), so a single stored id was overwritten before the audio thread read it.
static std::atomic<uint32_t> g_audio_hp_removed{0};
static std::atomic<int> g_audio_hp_added{0};
// Third detector (measured s7199: a real CoreAudio device removal under sdl2-compat/SDL3 posts NO REMOVED for our id and
// the status stays PLAYING, while the device silently stops pulling): drain watchdog. queue_samples reports the queue
// size before each post; any drop since the previous post's size is the device pulling. No pull for 400 ms on an
// unpaused device = stalled -> reopen (falls back to the system default if the named device is gone). Back-off 1,2,4,8 s
// between stall reopens so a present-but-stuck device does not reopen 115 times a second; reset after 2 s of pulling.
static bool g_audio_hp_stalled = false;  // audio thread only
static void audio_hotplug_note_queue(uint32_t raw_before, uint32_t after) {
    static uint32_t last_after = 0;
    static auto last_pull = std::chrono::steady_clock::now();
    static auto last_reopen = last_pull - std::chrono::hours(1);
    static double backoff_s = 1.0;
    const auto now = std::chrono::steady_clock::now();
    if (raw_before < last_after || after == 0) {
        last_pull = now;
        if (backoff_s > 1.0 && std::chrono::duration<double>(now - last_reopen).count() > backoff_s + 2.0) backoff_s = 1.0;
    } else if (audio_device && SDL_GetAudioDeviceStatus(audio_device) != SDL_AUDIO_PLAYING) {
        last_pull = now;  // paused on purpose (s7197 test): not a stall, and do not fire the moment it resumes
    } else if (audio_device && std::chrono::duration<double>(now - last_pull).count() > 0.4 &&
               std::chrono::duration<double>(now - last_reopen).count() > backoff_s &&
               SDL_GetAudioDeviceStatus(audio_device) == SDL_AUDIO_PLAYING) {
        g_audio_hp_stalled = true;
        last_reopen = now;
        last_pull = now;
        backoff_s = std::min(backoff_s * 2.0, 8.0);
    }
    last_after = after;
}
static void audio_hotplug_apply() {
    static const bool on = [] { const char* e = getenv("ROGUESQ_AUDIO_HOTPLUG"); return !(e && e[0] == '0'); }();
    static const double test_s = [] { const char* e = getenv("ROGUESQ_AUDIO_REMOVE_TEST"); return e ? atof(e) : 0.0; }();
    static const auto t0 = std::chrono::steady_clock::now();
    static auto last_poll = t0;
    static bool test_done = false;
    static uint32_t n_reopen = 0;
    const uint32_t rem = g_audio_hp_removed.exchange(0, std::memory_order_acq_rel);
    const int added = g_audio_hp_added.exchange(0, std::memory_order_acq_rel);
    std::lock_guard<std::recursive_mutex> lock(audio_device_mutex);
    const auto now = std::chrono::steady_clock::now();
    if (test_s > 0 && !test_done && audio_device &&
        std::chrono::duration<double>(now - t0).count() >= test_s) {
        test_done = true;
        SDL_Event ev{};
        ev.type = SDL_AUDIODEVICEREMOVED;
        ev.adevice.which = audio_device;
        ev.adevice.iscapture = 0;
        const int pushed = SDL_PushEvent(&ev);
        fprintf(stderr, "[s7199-hotplug] TEST pushed REMOVED device=%u at %.1f s pushed=%d status=%d\n",
                (unsigned)audio_device, test_s, pushed, (int)SDL_GetAudioDeviceStatus(audio_device));
        fflush(stderr);
    }
    if (rem || added)
        fprintf(stderr, "[s7199-hotplug] event removed_mask=0x%X added=%d open=%u on=%d\n", rem, added, (unsigned)audio_device,
                on ? 1 : 0);
    if (!on) return;
    bool stopped = false;
    if (now - last_poll >= std::chrono::milliseconds(250)) {
        last_poll = now;
        stopped = audio_device && SDL_GetAudioDeviceStatus(audio_device) == SDL_AUDIO_STOPPED;
    }
    const char* why = nullptr;
    const bool stall = g_audio_hp_stalled;
    g_audio_hp_stalled = false;
    if (audio_device && (rem & (1u << ((uint32_t)audio_device & 31u)))) why = "removed-event";
    else if (stopped) why = "status-stopped";
    else if (stall) why = "drain-stall";
    else if (added > 0 && !audio_device) why = "added-while-closed";
    else if (added > 0 && g_audio_open_name.empty() && !audio_route_is_default(g_audio_route_pref) &&
             !audio_route_resolve(true).empty()) why = "preferred-added";
    if (!why) return;
    const auto r0 = std::chrono::steady_clock::now();
    const uint32_t old = audio_device;
    if (audio_device) {
        SDL_CloseAudioDevice(audio_device);
        audio_device = 0;
    }
    open_audio_output();
    ++n_reopen;
    fprintf(stderr, "[s7199-hotplug] reopen n=%u why=%s old=%u new=%u name=%s status=%d took=%.1f ms\n", n_reopen, why, old,
            (unsigned)audio_device, g_audio_open_name.empty() ? "<system default>" : g_audio_open_name.c_str(),
            audio_device ? (int)SDL_GetAudioDeviceStatus(audio_device) : -1,
            std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - r0).count());
    fflush(stderr);
}

static void set_frequency(uint32_t freq) {
    static const bool probe_enabled = [] {
        const char* all = getenv("ROGUESQ_LOG_ALL");
        const char* own = getenv("ROGUESQ_LOG_M5_AI_STATE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (probe_enabled) {
        const uint32_t width = rs64_vi_committed_width();
        const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
        const bool target = (width == 1024u &&
                             (origin == 0x00790400u || origin == 0x00790800u)) ||
                            (width == 512u && origin == 0x006AB400u);
        static std::atomic<uint32_t> rows{0};
        if (target) {
            const uint32_t n = rows.fetch_add(1, std::memory_order_relaxed);
            if (n < 64u) {
                fprintf(stderr,
                        "[m5-ai-state] n=%u phase=%u width=%u origin=0x%06X "
                        "api=set-frequency previous=%u requested=%u device=%u\n",
                        n, rs64_phase_ord(), width, origin, audio_sample_rate,
                        freq, (unsigned)audio_device);
                fflush(stderr);
            }
        }
    }
    std::lock_guard<std::recursive_mutex> lock(audio_device_mutex);
    // s6807: on hardware osAiSetFrequency is a DACRATE register write. Closing and reopening the CoreAudio device
    // blocks the calling guest thread ~150 ms per call, and the game sets the (unchanged) rate twice at every audio
    // re-init, so the guest fed no AI buffer for 19 VI at each scene transition (retail oracle: max gap 2 VI). Same rate
    // with an open device is a no-op now; ROGUESQ_AI_REOPEN_ALWAYS=1 restores the old reopen for A/B.
    static const bool reopen_always = [] { const char* e = getenv("ROGUESQ_AI_REOPEN_ALWAYS"); return e && e[0] == '1'; }();
    if (audio_device && freq == audio_sample_rate && !reopen_always) {
        return;
    }
    const auto t0 = std::chrono::steady_clock::now();
    if (audio_device) {
        SDL_CloseAudioDevice(audio_device);
        audio_device = 0;
    }
    audio_sample_rate = freq;
    open_audio_output();
    fprintf(stderr, "[audio-reopen] rate=%u took %.1f ms\n", freq,
            std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count());
}

extern "C" void rs64_s4245_tick(int kind, uint32_t amount);
// s7198: per-second counters for the [s7198-q] stall-test log (get_frames_remaining).
static std::atomic<uint32_t> s7198_bufs_sec{0}, s7198_trims_sec{0};
static void queue_samples(int16_t* samples, size_t num_samples, uint32_t rdram_addr) {
    rs64_s4245_tick(4, 1);
    audio_route_apply_cycle();
    audio_hotplug_apply();
    // s371 (M5-AUDIO-PLAN.md Step 6): this parameter was named `num_bytes` but
    // is actually a SAMPLE count -- ultramodern::queue_audio_buffer
    // (lib/N64ModernRuntime/ultramodern/src/audio.cpp:25-36) computes
    // `sample_count = byte_count / sizeof(int16_t)` and passes THAT in.
    // SDL_QueueAudio's `len` is a byte count, not a sample count. The
    // previous code passed the raw sample count straight through as the byte
    // length, so every single call queued only HALF the correct number of
    // bytes to SDL -- the back half of every audio buffer's PCM data was
    // silently dropped, unconditionally, independent of whether the ucode
    // upstream produced correct content. M5-AUDIO-PLAN.md Step 6 described
    // this host bridge as "already fully implemented and functional,
    // confirmed by the runtime survey, not assumed" -- that claim is
    // overturned (docs/CURRENT-TRUTH.md superseded section, this session).
    // RDRAM stores N64 PCM in network byte order; SDL_AUDIO_S16SYS expects
    // native-endian samples. Convert at this host boundary so the guest's
    // sample count and address remain unchanged while the device gets values
    // in its configured format.
    std::vector<int16_t> native_samples(num_samples);
    const uint8_t* n64_bytes = reinterpret_cast<const uint8_t*>(samples);
    for (size_t i = 0; i < num_samples; ++i) {
        // RDRAM is word-swapped on the host (byte at guest offset k lives at k^3);
        // s4239 proved p[i^3] is the correct order (876/894 AI buffers FNV-match
        // ucode output), so s4242 applies it here, the audible path.
        const uint16_t value = (static_cast<uint16_t>(n64_bytes[(i * 2) ^ 3]) << 8) |
                               static_cast<uint16_t>(n64_bytes[(i * 2 + 1) ^ 3]);
        native_samples[i] = static_cast<int16_t>(value);
    }
    if (const char* c = getenv("ROGUESQ_S4242_CTRL"); c && c[0] && c[0] != '0') {
        static uint32_t cn = 0;
        cn++;
        {
            double a = 0, b = 0;
            for (size_t i = 0; i < num_samples; ++i) {
                const int16_t w = static_cast<int16_t>((n64_bytes[i * 2] << 8) | n64_bytes[i * 2 + 1]);
                a += (double)native_samples[i] * native_samples[i];
                b += (double)w * w;
            }
            const double n = num_samples ? (double)num_samples : 1.0;
            if (b > 0 && (cn % 16) == 0)
            std::fprintf(stderr, "[s4242-ctrl] n=%u fixed_rms=%.0f old_rms=%.0f samples=%zu\n",
                         cn, std::sqrt(a / n), std::sqrt(b / n), num_samples);
            // s4243: per-buffer FNV; a repeated hash on distinct DMA addrs = stall/re-feed.
            static uint64_t prev_h = 0; static uint32_t prev_addr = 0, reps = 0;
            uint64_t h = 1469598103934665603ull;
            for (size_t i = 0; i < num_samples; ++i) { h ^= (uint16_t)native_samples[i]; h *= 1099511628211ull; }
            if (b > 0 && h == prev_h && reps++ < 300)
                std::fprintf(stderr, "[s4243-rep] n=%u fnv=%016llx addr=0x%08X prev_addr=0x%08X rms=%.0f\n",
                             cn, (unsigned long long)h, rdram_addr, prev_addr, std::sqrt(a / n));
            if (b > 0 && cn >= 1500 && cn < 1660 && (cn % 4) == 0)
                std::fprintf(stderr, "[s4243-seq] n=%u fnv=%016llx addr=0x%08X\n", cn, (unsigned long long)h, rdram_addr);
            if (cn >= 1000 && cn < 1720) { // s4244: same FNV32 as rsp.cpp s4239-out (guest byte order) for write/read join
                uint32_t f32 = 2166136261u;
                for (size_t i = 0; i < num_samples * 2; ++i) f32 = (f32 * 16777619u) ^ n64_bytes[i ^ 3];
                std::fprintf(stderr, "[s4244-q] n=%u addr=0x%06X fnv=0x%08X\n", cn, rdram_addr & 0x7FFFFFu, f32);
            }
            prev_h = h; prev_addr = rdram_addr;
            static FILE* pcm = [] { const char* e = getenv("ROGUESQ_S4243_PCM"); return e ? fopen(e, "wb") : nullptr; }();  // s7466 DV: one getenv
            static size_t pcm_bytes = 0;
            if (pcm && cn >= 1200 && pcm_bytes < 2400000) { fwrite(native_samples.data(), 2, num_samples, pcm); pcm_bytes += num_samples * 2; fflush(pcm); }
        }
    }

    uint32_t queued_before = 0, queued_after = 0;
    int queue_result = -1;
    {
        std::lock_guard<std::recursive_mutex> lock(audio_device_mutex);
        queued_before = audio_device ? SDL_GetQueuedAudioSize(audio_device) : 0;
        const uint32_t raw_queued_before = queued_before;
        // s7198: a device that stops pulling (paused, output disconnected) keeps receiving the s7197 fallback-paced
        // buffers, so its queue grows ~768 B per post and replays as latency once it resumes. Hardware's DAC never holds
        // more than the AI's two buffers. When the queue already holds more than ROGUESQ_AI_BACKLOG_MS at the live rate,
        // drop it before queueing the new buffer. Default 150 (normal play peaks ~36 ms, s7198 ctl); 0 = old unbounded queue.
        static const long backlog_ms = [] { const char* e = getenv("ROGUESQ_AI_BACKLOG_MS"); return e ? strtol(e, nullptr, 0) : 150L; }();
        s7198_bufs_sec.fetch_add(1, std::memory_order_relaxed);
        if (audio_device && backlog_ms > 0 &&
            (uint64_t)queued_before * 1000u > (uint64_t)backlog_ms * audio_sample_rate * 4u) {
            static uint32_t ntrim = 0;
            if (++ntrim <= 8 || (ntrim & 255) == 0)
                fprintf(stderr, "[s7198-trim] n=%u dropped=%u rate=%u limit_ms=%ld\n", ntrim, queued_before,
                        (unsigned)audio_sample_rate, backlog_ms);
            SDL_ClearQueuedAudio(audio_device);
            s7198_trims_sec.fetch_add(1, std::memory_order_relaxed);
            queued_before = 0;
        }
        if (audio_device) {
            queue_result = SDL_QueueAudio(audio_device, native_samples.data(),
                                          (Uint32)(num_samples * sizeof(int16_t)));
            audio_hotplug_note_queue(raw_queued_before, SDL_GetQueuedAudioSize(audio_device));
        }
        queued_after = audio_device ? SDL_GetQueuedAudioSize(audio_device) : 0;
    }
    if (queue_result != 0) {
        static uint32_t failures = 0;
        const uint32_t n = failures++;
        if (n < 8u || (n % 256u) == 0u) {
            fprintf(stderr,
                    "[m5-audio-host-error] n=%u phase=%u width=%u origin=0x%06X"
                    " result=%d device=%u samples=%zu bytes=%zu error=%s\n",
                    n, rs64_phase_ord(), rs64_vi_committed_width(),
                    rs64_vi_committed_origin() & 0x00FFFFFFu, queue_result,
                    (unsigned)audio_device, num_samples,
                    num_samples * sizeof(int16_t), SDL_GetError());
            fflush(stderr);
        }
    }
    {
        // s5672 [ai-underrun]: host SDL queue depth at each AI buffer. queued_before==0
        // after the first fill means the device drained dry (crackle/underrun).
        static const bool uf = getenv("ROGUESQ_LOG_AI_UNDERRUN") != nullptr;
        static uint32_t calls = 0, zero = 0, maxq = 0, lastphase = 0xFFFFFFFFu;
        static uint64_t sumq = 0; static uint32_t minq = 0xFFFFFFFFu;
        if (uf && audio_device) {
            const uint32_t ph = rs64_phase_ord();
            if (ph != lastphase) {
                if (calls) fprintf(stderr, "[ai-underrun] phase=%u calls=%u zero=%u min=%u max=%u avg=%llu rate=%u\n",
                    lastphase, calls, zero, minq, maxq, (unsigned long long)(sumq / calls), audio_sample_rate);
                calls = zero = maxq = 0; sumq = 0; minq = 0xFFFFFFFFu; lastphase = ph;
            }
            calls++; sumq += queued_before; if (!queued_before) zero++;
            static uint64_t t0 = 0, fr = 0;
            const uint64_t now = SDL_GetTicks64(); if (!t0) t0 = now;
            fr += num_samples / 2;
            if (queued_before < minq) minq = queued_before;
            if (queued_before > maxq) maxq = queued_before;
            if ((calls % 512) == 0)
                fprintf(stderr, "[ai-underrun] phase=%u calls=%u zero=%u min=%u max=%u avg=%llu rate=%u wall_ms=%llu prod_fps=%llu\n",
                    ph, calls, zero, minq, maxq, (unsigned long long)(sumq / calls), audio_sample_rate,
                    (unsigned long long)(now - t0), (unsigned long long)(fr * 1000 / (now - t0 + 1)));
        }
    }
    {
        // s6790 G2b: ROGUESQ_AI_TRACE=<file> writes one row per AI buffer (wall s, SDL queue bytes before, samples, VI
        // width/origin) and the raw s16 stereo PCM to <file>.pcm, all phases, for an offline gap/underrun scan of the
        // Chapter II crawl (no per-buffer stderr).
        static FILE* tr = nullptr; static FILE* tp = nullptr; static int init = 0;
        if (!init) {
            init = 1;
            if (const char* e = getenv("ROGUESQ_AI_TRACE"); e && *e) {
                tr = fopen(e, "w");
                tp = fopen((std::string(e) + ".pcm").c_str(), "wb");
            }
        }
        if (tr) {
            fprintf(tr, "%.4f %u %zu %u %06X %u\n", rs64_elapsed_seconds(), queued_before, num_samples,
                    rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu, rs64_vi_n_g);
            if (tp) fwrite(native_samples.data(), sizeof(int16_t), num_samples, tp);
        }
    }
    rs64_m5_audio_host_row("queue", queued_before, queued_after,
                           static_cast<uint32_t>(num_samples * sizeof(int16_t)),
                           static_cast<uint32_t>(num_samples));

    static const bool ai_state_probe = [] {
        const char* all = getenv("ROGUESQ_LOG_ALL");
        const char* own = getenv("ROGUESQ_LOG_M5_AI_STATE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (ai_state_probe) {
        const uint32_t width = rs64_vi_committed_width();
        const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
        const bool target = (width == 1024u &&
                             (origin == 0x00790400u || origin == 0x00790800u)) ||
                            (width == 512u && origin == 0x006AB400u);
        static std::atomic<uint32_t> rows{0};
        if (target) {
            const uint32_t n = rows.fetch_add(1, std::memory_order_relaxed);
            if (n < 64u) {
                fprintf(stderr,
                        "[m5-ai-state] n=%u phase=%u width=%u origin=0x%06X "
                        "api=queue-samples rate=%u samples=%zu rdram=0x%08X device=%u\n",
                        n, rs64_phase_ord(), width, origin, audio_sample_rate,
                        num_samples, rdram_addr, (unsigned)audio_device);
                fflush(stderr);
            }
        }
    }

    static int s_log_pcm_boundary = -1;
    if (s_log_pcm_boundary < 0) {
        const char* all = getenv("ROGUESQ_LOG_ALL");
        const char* own = getenv("ROGUESQ_LOG_PCM_BOUNDARY");
        const bool all_enabled = all && all[0] && all[0] != '0';
        const bool own_enabled = own && own[0] && own[0] != '0';
        s_log_pcm_boundary = (all_enabled || own_enabled) ? 1 : 0;
    }
    if (s_log_pcm_boundary && queue_result == 0) {
        const uint32_t width = rs64_vi_committed_width();
        const uint32_t origin = rs64_vi_committed_origin();
        const bool phase_allowed =
            (width == 1024u && origin == 0x00790400u) ||
            (width == 512u && (origin == 0x006AB400u ||
                               origin == 0x00690400u ||
                               origin == 0x00620400u));
        static uint32_t s_phase_key = 0xFFFFFFFFu;
        static uint32_t s_phase_n = 0;
        if (phase_allowed) {
            const uint32_t phase_key = (width << 24) ^ origin;
            if (phase_key != s_phase_key) {
                s_phase_key = phase_key;
                s_phase_n = 0;
            }
            uint32_t observed_key = g_rs64_pcm_consumer_phase_key.load(
                std::memory_order_relaxed);
            if (observed_key != phase_key &&
                g_rs64_pcm_consumer_phase_key.compare_exchange_strong(
                    observed_key, phase_key, std::memory_order_relaxed)) {
                g_rs64_pcm_consumer_count.store(0, std::memory_order_relaxed);
            }
            const uint32_t n = s_phase_n++;
            g_rs64_pcm_consumer_count.fetch_add(1, std::memory_order_relaxed);
            const size_t full_byte_count = num_samples * sizeof(int16_t);
            const uint8_t* p = reinterpret_cast<const uint8_t*>(samples);
            uint32_t fnv = 2166136261u;
            uint32_t nonzero = 0;
            for (size_t i = 0; i < full_byte_count; i++) {
                fnv = (fnv * 16777619u) ^ p[i];
                nonzero += p[i] != 0;
            }
            int smin = 32767, smax = -32768;
            for (size_t i = 0; i < num_samples; i++) {
                if (samples[i] < smin) smin = samples[i];
                if (samples[i] > smax) smax = samples[i];
            }
            if (n < 256 || (n % 128) == 0) {
                fprintf(stderr, "[pcm-samples] width=%u n=%u min=%d max=%d first16:",
                        width, n, smin, smax);
                for (size_t i = 0; i < 16 && i < num_samples; i++)
                    fprintf(stderr, " %d", samples[i]);
                fputc('\n', stderr);
            }
            uint32_t ordinal = 0xFFFFFFFFu;
            uint32_t row = 0xFFFFFFFFu;
            rs64_audio_current_route_snapshot(nullptr, nullptr, nullptr,
                                              &ordinal, &row, nullptr, nullptr);
            const uint32_t queued_bytes = rs64_m5_audio_queue_snapshot();
            uint32_t callback_seq = 0;
            uint64_t callback_time_us = 0;
            const bool callback_order = rs64_m5_callback_order_event(
                width, origin, callback_seq, callback_time_us);
            const uint64_t callback_thread = rs64_m5_callback_host_thread();
            ultramodern::rs64_audio_join_pcm(
                "consumer", rs64_phase_ord(), width, origin, ordinal, row,
                n, rdram_addr,
                static_cast<uint32_t>(num_samples),
                static_cast<uint32_t>(full_byte_count), fnv, nonzero);
            if (n < 256 || (n % 128) == 0) {
                fprintf(stderr,
                    "[pcm-boundary-consumer] n=%u phase=%u width=%u origin=0x%06X"
                    " route_ordinal=%u route_row=%u"
                    " rdram=0x%08X samples=%zu bytes=%zu fnv=0x%08X nz=%u"
                    " callback_source=queue_samples callback_thread=%llu"
                    " queued_bytes=%u callback_seq=%u callback_t_us=%llu"
                    " callback_order=%u\n",
                    n, rs64_phase_ord(), width, origin, ordinal, row, rdram_addr,
                    num_samples,
                    full_byte_count, fnv, nonzero,
                    static_cast<unsigned long long>(callback_thread),
                    queued_bytes, callback_seq,
                    static_cast<unsigned long long>(callback_time_us),
                    callback_order ? 1u : 0u);
                fflush(stderr);
            }
        }
    }

    // ROGUESQ_LOG_PCM_SANITY (M5-AUDIO-PLAN.md Step 6): independent of the
    // byte-count fix above, does the real ucode (ROGUESQ_AUDIO_UCODE=1)
    // actually hand this callback non-silent PCM? First ~20 calls, then every
    // 256th (matches the [audtask-dispatch] resample convention fixed s315).
    static int s_log_pcm_sanity = -1;
    if (s_log_pcm_sanity < 0) {
        const char* e = getenv("ROGUESQ_LOG_PCM_SANITY");
        s_log_pcm_sanity = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (s_log_pcm_sanity) {
        static uint32_t s_pcm_n = 0;
        static uint32_t s_pcm_allzero_calls = 0;
        bool all_zero = true;
        for (size_t i = 0; i < num_samples; i++) {
            if (samples[i] != 0) { all_zero = false; break; }
        }
        if (all_zero) s_pcm_allzero_calls++;
        // s5669: rail fraction + high-frequency energy (mean|diff| / mean|x|)
        // so noise is measurable at the AI PCM, not just "non-silent".
        uint64_t rails = 0, sum_abs = 0, sum_diff = 0;
        for (size_t i = 0; i < num_samples; i++) {
            int v = samples[i];
            if (v >= 32767 || v <= -32768) rails++;
            sum_abs += (uint64_t)(v < 0 ? -v : v);
            if (i >= 2) {
                int d = v - (int)samples[i - 2];
                sum_diff += (uint64_t)(d < 0 ? -d : d);
            }
        }
        if (!all_zero && (s_pcm_n % 64) == 0) {
            fprintf(stderr, "[pcm-noise] n=%u phase=%u rail_pct=%.2f mean_abs=%.1f hf_ratio=%.3f\n",
                    s_pcm_n, rs64_phase_ord(), 100.0 * rails / (double)num_samples,
                    (double)sum_abs / (double)num_samples,
                    sum_abs ? (double)sum_diff / (double)sum_abs : 0.0);
        }
        // s5670: dense per-callback trace so mean_abs can be aligned with
        // [spath] enqueueSpeechClip lines in the same stderr stream.
        static int s_pcm_dense = -1;
        if (s_pcm_dense < 0) {
            const char* e = getenv("ROGUESQ_LOG_PCM_DENSE");
            s_pcm_dense = (e && e[0] && e[0] != '0') ? 1 : 0;
        }
        if (s_pcm_dense && rs64_phase_ord() >= 4) {
            fprintf(stderr, "[pcm-dense] n=%u ma=%.0f hf=%.3f\n", s_pcm_n,
                    (double)sum_abs / (double)num_samples,
                    sum_abs ? (double)sum_diff / (double)sum_abs : 0.0);
        }
        // s5674: raw s16 dump of every phase>=4 callback; the [pcm-dense] n= index
        // lines up with the n= printed here (file offset in samples).
        static FILE* s_pcm_raw = nullptr;
        static int s_pcm_raw_init = 0;
        static uint64_t s_pcm_raw_off = 0;
        if (!s_pcm_raw_init) {
            s_pcm_raw_init = 1;
            const char* e = getenv("ROGUESQ_PCM_RAW");
            if (e && e[0]) s_pcm_raw = fopen(e, "wb");
        }
        if (s_pcm_raw && rs64_phase_ord() >= 4) {
            fprintf(stderr, "[pcm-raw] n=%u off=%llu ns=%zu\n", s_pcm_n,
                    (unsigned long long)s_pcm_raw_off, num_samples);
            fwrite(samples, sizeof(int16_t), num_samples, s_pcm_raw);
            s_pcm_raw_off += num_samples;
        }
        if (s_pcm_n < 20 || (s_pcm_n % 256) == 0) {
            fprintf(stderr, "[pcm-sanity] n=%u phase=%u width=%u origin=0x%06X num_samples=%zu all_zero=%d allzero_calls=%u total_calls=%u\n",
                    s_pcm_n, rs64_phase_ord(), rs64_vi_committed_width(),
                    rs64_vi_committed_origin(), num_samples, all_zero ? 1 : 0,
                    s_pcm_allzero_calls, s_pcm_n + 1);
        }
        s_pcm_n++;
    }
}

static size_t get_frames_remaining() {
    Uint32 queued;
    {
        std::lock_guard<std::recursive_mutex> lock(audio_device_mutex);
        if (!audio_device) return 0;
        { // s7197 forced arm: ROGUESQ_AI_STALL_TEST=<sec> pauses the device from <sec> on (re-paused after any reopen). A paused
          // SDL2 device stops calling its queue callback exactly like a disconnected output, so the queue never drains.
          // s7198: ROGUESQ_AI_STALL_TEST=<pause_s>:<resume_s> unpauses at resume_s (a TV switched back on), and logs the queue
          // once per second ([s7198-q]: queued bytes, ms at the live rate, AI buffers queued and trims in that second).
            static const double t_s = [] { const char* e = getenv("ROGUESQ_AI_STALL_TEST"); return e ? atof(e) : 0.0; }();
            static const double r_s = [] { const char* e = getenv("ROGUESQ_AI_STALL_TEST"); const char* c = e ? strchr(e, ':') : nullptr; return c ? atof(c + 1) : 0.0; }();
            static const auto t0 = std::chrono::steady_clock::now();
            static SDL_AudioDeviceID paused = 0;
            static bool resumed = false;
            static int last_sec = -1;
            const double el = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            if (t_s > 0 && !resumed && paused != audio_device && el >= t_s) {
                SDL_PauseAudioDevice(audio_device, 1);
                paused = audio_device;
                fprintf(stderr, "[s7197-ai-stall] TEST paused device=%u at %.1f s\n", (unsigned)audio_device, t_s);
            }
            if (r_s > t_s && !resumed && paused && el >= r_s) {
                SDL_PauseAudioDevice(audio_device, 0);
                resumed = true;
                fprintf(stderr, "[s7198-ai-stall] TEST resumed device=%u at %.1f s queued=%u\n", (unsigned)audio_device, r_s,
                        (unsigned)SDL_GetQueuedAudioSize(audio_device));
            }
            if (t_s > 0 && (int)el != last_sec) {
                last_sec = (int)el;
                const uint32_t q = SDL_GetQueuedAudioSize(audio_device);
                const uint32_t rate = audio_sample_rate ? audio_sample_rate : 1;
                fprintf(stderr, "[s7198-q] t=%d queued=%u ms=%.1f rate=%u bufs=%u trims=%u state=%s dev=%u st=%d\n", last_sec, q,
                        q * 1000.0 / (rate * 4.0), rate, s7198_bufs_sec.exchange(0), s7198_trims_sec.exchange(0),
                        resumed ? "resumed" : (paused ? "paused" : "pre"), (unsigned)audio_device,
                        (int)SDL_GetAudioDeviceStatus(audio_device));
            }
        }
        queued = SDL_GetQueuedAudioSize(audio_device);
    }
    rs64_m5_audio_host_row("remaining", queued, queued, 0, 0);
    static const bool probe_enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_AUDIO_DRAIN");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (probe_enabled) {
        const uint32_t width = rs64_vi_committed_width();
        const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
        const bool target = (width == 1024u && origin == 0x00790400u) ||
                            (width == 512u && origin == 0x006AB400u);
        static uint32_t rows = 0;
        static uint32_t phase_key = 0xFFFFFFFFu;
        if (target) {
            const uint32_t current_key = (width << 24) ^ origin;
            if (current_key != phase_key) {
                phase_key = current_key;
                rows = 0;
            }
        }
        if (target && rows < 512u) {
            std::fprintf(stderr,
                         "[m5-audio-drain-raw] n=%u phase=%u width=%u origin=0x%06X"
                         " queued_bytes=%u frames=%u device=%u\n",
                         rows++, rs64_phase_ord(), width, origin,
                         (unsigned)queued, (unsigned)(queued / 4u),
                         (unsigned)audio_device);
            std::fflush(stderr);
        }
    }
    // queued is in bytes; 4 bytes per stereo frame (2 ch × 2 bytes)
    return queued / 4;
}

#ifdef _WIN32
// Forward declaration so the F12 hotkey in poll_input() can write a dump.
static void write_minidump_safe(EXCEPTION_POINTERS* ep);
// Forward declaration so the hwbp VEH (defined before print_stack_with_symbols)
// can render the offending thread's stack with symbols. Non-static so RT64's
// d3d12 allocator-failure tracer can extern-declare and call it.
void print_stack_with_symbols(void** frames, USHORT count);
#endif

// (Periodic mqdiag watchdog removed — mqdiag_dump lived in the librecomp
//  fork and isn't in upstream. Hangs are rare enough now that on-demand
//  dump-game.ps1 is sufficient.)

// Memory watchpoint: caught the corruption window via polling but missed the
// instigating store. Switch to a Win32 hardware data breakpoint (DR0, write,
// 4 bytes) on rdram + 0x3CBC4. When a write hits, the OS raises
// EXCEPTION_SINGLE_STEP on the offending thread; our vectored handler logs
// tid/RIP/stack so we can name the racing writer.
//
// DR0..DR3 are per-thread; we walk the process thread list and arm DR0 on each
// thread (skipping ourselves). New threads spawned later need re-arming, so we
// re-walk the list on a slow cadence — overhead is negligible vs. catching the
// race.
extern "C" volatile uint8_t* volatile g_recomp_rdram_for_wp_raw = nullptr;

#ifdef _WIN32
static volatile uintptr_t g_wp_addr = 0;     // address being watched (in our VA)
static volatile LONG      g_wp_hit_count = 0; // limit logging — race may fire fast

static LONG WINAPI memwp_veh(EXCEPTION_POINTERS* ep) {
    // Hardware data breakpoints raise EXCEPTION_SINGLE_STEP with B0..B3 set in DR6.
    if (ep->ExceptionRecord->ExceptionCode != EXCEPTION_SINGLE_STEP) {
        return EXCEPTION_CONTINUE_SEARCH;
    }
    CONTEXT* ctx = ep->ContextRecord;
    DWORD64 dr6_hits = ctx->Dr6 & 0xFu;
    if (!dr6_hits) {
        return EXCEPTION_CONTINUE_SEARCH;  // BS or other source — not us
    }

    // Throttle: catastrophic loop would flood stderr and slow everything to a halt.
    static volatile uint32_t s_last_val = 0;
    DWORD tid = GetCurrentThreadId();
    uint32_t cur_val = 0;
    if (g_wp_addr) cur_val = *(uint32_t*)g_wp_addr;
    // Only log on value TRANSITIONS — the watched word may be written many times
    // with the same value (a DMA hot path); we want the moments it CHANGES.
    bool changed = (cur_val != s_last_val);
    if (changed) s_last_val = cur_val;
    LONG n = changed ? InterlockedIncrement(&g_wp_hit_count) : g_wp_hit_count;
    if (changed && n <= 200) {
        fprintf(stderr,
            "[hwbp-hit #%ld] tid=%lu RIP=0x%llX  watch=0x%llX  "
            "current=0x%08X  DR6=0x%llX\n",
            n, tid,
            (unsigned long long)ctx->Rip,
            (unsigned long long)g_wp_addr,
            cur_val,
            (unsigned long long)ctx->Dr6);
        void* frames[24];
        USHORT count = RtlCaptureStackBackTrace(0, 24, frames, nullptr);
        print_stack_with_symbols(frames, count);
        fflush(stderr);
    }

    // Clear DR6 status bits so further hits can be observed.
    ctx->Dr6 &= ~0xFull;
    // Set RF in EFlags to avoid refire on the same instruction (data BP is a
    // trap that fires AFTER the write, but RF is harmless here and matches
    // canonical post-handler behavior).
    ctx->EFlags |= 0x10000;
    return EXCEPTION_CONTINUE_EXECUTION;
}

// Configure DR0 on the given (suspended) thread to trap on 4-byte WRITE at addr.
// Returns true if we actually wrote new debug regs.
static bool arm_hwbp_on_thread(HANDLE hThread, uintptr_t addr) {
    CONTEXT ctx{};
    ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;
    if (!GetThreadContext(hThread, &ctx)) return false;
    if (ctx.Dr0 == (DWORD64)addr && (ctx.Dr7 & 0x000D0001ull) == 0x000D0001ull) {
        // Already armed — no need to rewrite (avoids per-tick churn cost).
        return false;
    }
    ctx.Dr0 = (DWORD64)addr;
    // DR7: clear DR0 fields, then set L0=1, R/W0=01 (write), LEN0=11 (4 bytes).
    //   L0=bit0, R/W0=bits16-17, LEN0=bits18-19. Combined mask 0xF0001 in low20.
    DWORD64 dr7 = ctx.Dr7;
    dr7 &= ~((0x3ull << 16) | (0x3ull << 18) | 0x1ull);
    dr7 |= (0x1ull << 16);  // R/W0 = 01 (write)
    dr7 |= (0x3ull << 18);  // LEN0 = 11 (4 bytes)
    dr7 |= 0x1ull;          // L0 = 1
    ctx.Dr7 = dr7;
    ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;
    return SetThreadContext(hThread, &ctx) != 0;
}

static void arm_hwbp_all_threads(uintptr_t addr) {
    DWORD me  = GetCurrentThreadId();
    DWORD pid = GetCurrentProcessId();
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
    if (snap == INVALID_HANDLE_VALUE) return;
    THREADENTRY32 te{};
    te.dwSize = sizeof(te);
    if (Thread32First(snap, &te)) {
        do {
            if (te.th32OwnerProcessID != pid) continue;
            if (te.th32ThreadID == me) continue;
            HANDLE h = OpenThread(
                THREAD_GET_CONTEXT | THREAD_SET_CONTEXT | THREAD_SUSPEND_RESUME,
                FALSE, te.th32ThreadID);
            if (!h) continue;
            if (SuspendThread(h) != (DWORD)-1) {
                arm_hwbp_on_thread(h, addr);  // skips if already armed; silent
                ResumeThread(h);
            }
            CloseHandle(h);
        } while (Thread32Next(snap, &te));
    }
    CloseHandle(snap);
    // Intentionally no per-tick print — recurring stderr writes starve the
    // SDL message pump and produce a "Not Responding" window. Hits are still
    // reported by memwp_veh; that's the only signal we care about.
}
#endif // _WIN32

// Helper: read a 4-byte BE word from RDRAM at the given RDRAM-relative offset.
// (RDRAM is host-LE-stored; XOR-3 byte order for BE).
static inline uint32_t rdram_be32(const uint8_t* rdram, uint32_t off) {
    return (uint32_t(rdram[(off + 0) ^ 3]) << 24) |
           (uint32_t(rdram[(off + 1) ^ 3]) << 16) |
           (uint32_t(rdram[(off + 2) ^ 3]) <<  8) |
            uint32_t(rdram[(off + 3) ^ 3]);
}

// Periodic poll of the scene-state struct at D_80130B10 + the per-frame
// callback array at D_8011A8A4. Both regions are documented in
// `project_thread_topology_2026_05_09.md`. Gated by ROGUESQ_LOG_STATE=1.
//
// Reports the first dump immediately, then logs changes only. The state byte
// at +0x14 of D_80130B10 indexes the level/scene jump-table at jtbl_8003A3E8.
// The 4 callback slots at D_8011A8A4 are the per-frame draw callbacks the
// main game thread iterates each frame.
// gCurrentLevel @ 0x80130B70 (syms datasyms.toml:1072). ROGUESQ_LOG_LEVEL=1
// logs every change with the VI phase ordinal. ROGUESQ_FORCE_MISSION=<n>
// additionally rewrites the word to n (poll period 2 ms) once the phase
// ordinal reaches ROGUESQ_FORCE_MISSION_PHASE (default 0), to test whether
// the hangar/mission loader consumes the level word.
static void start_level_poller() {
    const char* lg = std::getenv("ROGUESQ_LOG_LEVEL");
    const char* fm = std::getenv("ROGUESQ_FORCE_MISSION");
    const char* fs = std::getenv("ROGUESQ_FORCE_SEL");  // byte @0x80130B40: menuOverlayInit table[sel] -> cinematicLoopBody arg
    if (!(lg && lg[0] && lg[0] != '0') && !(fm && fm[0]) && !(fs && fs[0])) return;
    const int force = fm && fm[0] ? std::atoi(fm) : -1;
    const int force_sel = fs && fs[0] ? std::atoi(fs) : -1;
    const char* fp = std::getenv("ROGUESQ_FORCE_MISSION_PHASE");
    const uint32_t force_phase = fp ? (uint32_t)std::strtoul(fp, nullptr, 0) : 0;
    static std::thread t{[=]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        const uint32_t off = 0x130B70;
        uint32_t prev = 0xDEADBEEFu;
        uint32_t pokes = 0;
        uint32_t prev_sel = 0xDEADBEEFu, sel_pokes = 0;
        for (;;) {
            uint32_t sel = rdram[0x130B40 ^ 3];
            if (sel != prev_sel) {
                std::fprintf(stderr, "[level] phase=%u sel@B40=0x%02X (prev=0x%02X) selpokes=%u\n",
                             rs64_phase_ord(), sel, prev_sel, sel_pokes);
                std::fflush(stderr);
                prev_sel = sel;
            }
            if (force_sel >= 0 && rs64_phase_ord() >= force_phase && sel != (uint32_t)force_sel) {
                rdram[0x130B40 ^ 3] = (uint8_t)force_sel;
                ++sel_pokes;
            }
            uint32_t cur = rdram_be32(rdram, off);
            if (cur != prev) {
                std::fprintf(stderr, "[level] phase=%u gCurrentLevel=0x%08X (prev=0x%08X) pokes=%u\n",
                             rs64_phase_ord(), cur, prev, pokes);
                std::fflush(stderr);
                prev = cur;
            }
            if (force >= 0 && rs64_phase_ord() >= force_phase && cur != (uint32_t)force) {
                for (int j = 0; j < 4; ++j)
                    rdram[(off + j) ^ 3] = (uint8_t)((uint32_t)force >> (24 - 8 * j));
                ++pokes;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
        }
    }};
}

static void start_state_poller() {
    if (!std::getenv("ROGUESQ_LOG_STATE")) return;
    static std::thread t{[]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        // KSEG0 → RDRAM-relative offset (mask 0x00FFFFFF).
        const uint32_t state_off  = 0x130B10;  // D_80130B10..B40 (scene state)
        const uint32_t cbarr_off  = 0x11A8A4;  // D_8011A8A4..B4  (4 callbacks)
        // 12 words covers B10..B3F. asm/main/3EBA0.s reads bytes at +0x20,
        // +0x21, +0x22 (D_80130B30..B32) to gate state transitions, so the
        // first poll missed exactly the bytes needed for forward-progress
        // analysis. Now we cover the whole B10..B3F region.
        uint32_t prev[16] = {0xFFFFFFFFu};
        bool first = true;
        for (int i = 0; i < 1200; ++i) {  // ~60s @ 50ms
            uint32_t state[12];
            for (int j = 0; j < 12; ++j) state[j] = rdram_be32(rdram, state_off + j * 4);
            uint32_t cbs[4];    // 4 callback fn ptrs
            for (int j = 0; j < 4; ++j) cbs[j]   = rdram_be32(rdram, cbarr_off + j * 4);

            // Drain-loop diagnostic — boot thread is stuck waiting for these.
            // D_800A0F50 byte: drain-enable gate (0 = bypass drain, return ready)
            // D_80141AD0 byte: drain-entry count
            // D_801496F8 word: array base ptr (each entry 0x88 bytes; byte[0] = active flag)
            uint8_t  a0f50 = rdram[0xA0F50 ^ 3];
            uint8_t  c1ad0 = rdram[0x141AD0 ^ 3];
            uint32_t array_base = rdram_be32(rdram, 0x1496F8);
            // Sound-asset data dumps — boot deadlocks in func_80097518 walking
            // pool_SND, possibly because the asset loader leaves buffers zeroed.
            // Dump all 3 sound assets once each when they become non-null.
            //   D_80139B4C = sound/proj_SND  (first asset)
            //   D_80139B54 = sound/pool_SND  (second asset, fed to func_80097518)
            //   D_80139B50 = sound/sdir_SND  (third asset)
            static bool snd_dumped[3] = {false, false, false};
            const uint32_t snd_addrs[3] = {0x139B4C, 0x139B54, 0x139B50};
            const char* snd_names[3] = {"proj_SND", "pool_SND", "sdir_SND"};
            for (int s = 0; s < 3; ++s) {
                if (snd_dumped[s]) continue;
                uint32_t ptr = rdram_be32(rdram, snd_addrs[s]);
                uint32_t off = ptr & 0x00FFFFFFu;
                if ((ptr & 0xF0000000u) == 0x80000000u && off + 0x40 < 0x800000u) {
                    fprintf(stderr, "[%s] t=%4d ms ptr=0x%08X first 0x40 bytes (BE):\n",
                            snd_names[s], i * 50, ptr);
                    for (int row = 0; row < 4; ++row) {
                        fprintf(stderr, "  %04X:", row * 16);
                        for (int b = 0; b < 16; ++b) {
                            fprintf(stderr, " %02X", rdram[(off + row * 16 + b) ^ 3]);
                        }
                        fprintf(stderr, "\n");
                    }
                    fflush(stderr);
                    snd_dumped[s] = true;
                    // EXPERIMENTAL: if the buffer is all zeros, write -1 sentinel
                    // into the first word. The user's hypothesis is that the
                    // attribution screen has no audio, so empty pool is correct
                    // and the game's pool walker should exit early on -1 sentinel.
                    // Our zero-init heap puts 0 instead. Test the hypothesis:
                    // ROGUESQ_FORCE_EMPTY_POOL_SENTINEL=1.
                    if (std::getenv("ROGUESQ_FORCE_EMPTY_POOL_SENTINEL")) {
                        bool all_zero = true;
                        for (int j = 0; j < 16; ++j) {
                            if (rdram[(off + j) ^ 3] != 0) { all_zero = false; break; }
                        }
                        if (all_zero) {
                            // Write 0xFFFFFFFF (BE) to first word.
                            for (int j = 0; j < 4; ++j) {
                                rdram[(off + j) ^ 3] = 0xFF;
                            }
                            fprintf(stderr,
                                "[%s-FIX] wrote sentinel -1 to first word at 0x%08X\n",
                                snd_names[s], ptr);
                            fflush(stderr);
                        }
                    }
                }
            }
            // Compute first-N active flags if array_base is a sane KSEG0 ptr
            uint8_t flags[8] = {0};
            uint32_t array_off = array_base & 0x00FFFFFFu;
            int n = c1ad0 < 8 ? c1ad0 : 8;
            if ((array_base & 0xF0000000u) == 0x80000000u && array_off + n * 0x88 < 0x800000u) {
                for (int j = 0; j < n; ++j) {
                    flags[j] = rdram[(array_off + j * 0x88) ^ 3];
                }
            }

            uint32_t cur[16];
            for (int j = 0; j < 12; ++j) cur[j] = state[j];
            for (int j = 0; j < 4; ++j) cur[12 + j] = cbs[j];
            bool changed = first;
            for (int j = 0; j < 16; ++j) if (cur[j] != prev[j]) { changed = true; break; }
            // Track drain state too — re-log when it changes.
            static uint8_t prev_a0f50 = 0xFF, prev_c1ad0 = 0xFF;
            static uint32_t prev_array_base = 0xFFFFFFFFu;
            static uint8_t prev_flags[8] = {0xFF};
            if (a0f50 != prev_a0f50 || c1ad0 != prev_c1ad0 || array_base != prev_array_base) changed = true;
            for (int j = 0; j < 8; ++j) if (flags[j] != prev_flags[j]) { changed = true; break; }
            if (changed) {
                first = false;
                fprintf(stderr,
                    "[state] t=%4d ms B10=%08X B14=%08X B18=%08X B1C=%08X B20=%08X B24=%08X B28=%08X B2C=%08X B30=%08X B34=%08X B38=%08X B3C=%08X | scene=%u | cb=[%08X,%08X,%08X,%08X] | drain.A0F50=%02X drain.cnt=%u arr=0x%08X flags=[%02X,%02X,%02X,%02X,%02X,%02X,%02X,%02X]\n",
                    i * 50,
                    state[0], state[1], state[2], state[3], state[4], state[5],
                    state[6], state[7], state[8], state[9], state[10], state[11],
                    (state[1] >> 24) & 0xFFu,
                    cbs[0], cbs[1], cbs[2], cbs[3],
                    a0f50, c1ad0, array_base,
                    flags[0], flags[1], flags[2], flags[3],
                    flags[4], flags[5], flags[6], flags[7]);
                fflush(stderr);
                for (int j = 0; j < 16; ++j) prev[j] = cur[j];
                prev_a0f50 = a0f50;
                prev_c1ad0 = c1ad0;
                prev_array_base = array_base;
                for (int j = 0; j < 8; ++j) prev_flags[j] = flags[j];
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    }};
    t.detach();
}

static void start_m5_exact_route_poller() {
    const char* all = std::getenv("ROGUESQ_LOG_ALL");
    const char* own = std::getenv("ROGUESQ_LOG_M5_EXACT_ROUTE");
    if (!((all && all[0] && all[0] != '0') ||
          (own && own[0] && own[0] != '0'))) return;
    static std::thread t{[]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        uint8_t prev_92 = 0xFF;
        uint32_t prev_d0 = 0xFFFFFFFFu;
        uint32_t prev_b50 = 0xFFFFFFFFu;
        uint32_t rows = 0;
        for (;;) {
            const uint32_t width = rs64_vi_committed_width();
            const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
            const bool target = (width == 1024u && origin == 0x00790400u) ||
                                (width == 512u && origin == 0x006AB400u);
            const uint8_t v92 = rdram[0x128C92u ^ 3u];
            const uint32_t vd0 = (uint32_t(rdram[0x128CD0u ^ 3u]) << 24) |
                                 (uint32_t(rdram[0x128CD1u ^ 3u]) << 16) |
                                 (uint32_t(rdram[0x128CD2u ^ 3u]) << 8) |
                                 uint32_t(rdram[0x128CD3u ^ 3u]);
            const uint32_t b50 = rdram_be32(rdram, 0x130B50u);
            if (b50 != prev_b50 && prev_b50 != 0xFFFFFFFFu) {
                std::fprintf(stderr,
                    "[m5-exact-route-poll-control] B50=0x%08X phase=%u\n",
                    b50, rs64_phase_ord());
                std::fflush(stderr);
            }
            if (target && (v92 != prev_92 || vd0 != prev_d0) && rows < 512u) {
                std::fprintf(stderr,
                    "[m5-exact-route-poll] n=%u phase=%u width=%u origin=0x%06X "
                    "field92=0x%02X fieldD0=0x%08X\n",
                    rows++, rs64_phase_ord(), width, origin, v92, vd0);
                std::fflush(stderr);
            }
            prev_92 = v92;
            prev_d0 = vd0;
            prev_b50 = b50;
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }};
    t.detach();
}

// Periodic poll of MEM[0x80130B50] (the inner-loop transition gate). Reports
// changes so we can see WHO writes it and what bits flip. Gated by
// ROGUESQ_LOG_B50=1.
static void start_b50_poller() {
    if (!std::getenv("ROGUESQ_LOG_B50")) return;
    static std::thread t{[]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        // RDRAM-relative offsets for KSEG0 0x80130B50 / 0x80130B58.
        const uint32_t b50_off = 0x130B50;
        const uint32_t b58_off = 0x130B58;
        uint32_t prev_b50 = 0xFFFFFFFFu;
        uint32_t prev_b58 = 0xFFFFFFFFu;
        for (int i = 0; i < 1200; ++i) {  // ~60s @ 50ms
            // Reads via byte XOR-3 to get BE word (RDRAM is host-LE-stored).
            uint32_t b50 = (uint32_t(rdram[(b50_off + 0) ^ 3]) << 24) |
                           (uint32_t(rdram[(b50_off + 1) ^ 3]) << 16) |
                           (uint32_t(rdram[(b50_off + 2) ^ 3]) <<  8) |
                            uint32_t(rdram[(b50_off + 3) ^ 3]);
            uint32_t b58 = (uint32_t(rdram[(b58_off + 0) ^ 3]) << 24) |
                           (uint32_t(rdram[(b58_off + 1) ^ 3]) << 16) |
                           (uint32_t(rdram[(b58_off + 2) ^ 3]) <<  8) |
                            uint32_t(rdram[(b58_off + 3) ^ 3]);
            if (b50 != prev_b50 || b58 != prev_b58) {
                fprintf(stderr, "[b50] t=%4d ms B50=0x%08X B58=0x%08X (b50.bit5=%d b50.b3=0x%02X b58.bit25=%d)\n",
                        i * 50, b50, b58,
                        (b50 >> 5) & 1, b50 & 0xFF,
                        (b58 >> 25) & 1);
                fflush(stderr);
                prev_b50 = b50;
                prev_b58 = b58;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    }};
    t.detach();
}

// Periodic poll of cinematic phase state so we can see stage transitions
// and timing. Gated by ROGUESQ_LOG_PHASE=1. Reports on change only.
//
// State variables (per memory notes project_cinematic_data_structures.md
// + project_b50_b58_polled_state.md):
//   cineState  : MEM_W[0x800B0934] — master cinematic state word
//   gateCtr    : MEM_W[0x800B0B28] — cinematic frame counter (compared
//                vs cutscene[0x44])
//   cutscene   : MEM_W[0x800B1904] — pointer to currently-loaded cutscene
//                struct
//   cuts_44    : MEM_W[cutscene+0x44] — total-count / duration field
//   B50        : MEM_W[0x80130B50] — state word, bit 5 is inner-loop
//                advance gate
//   B58        : MEM_W[0x80130B58] — state word, bit 25 is outer gate
//   slot_dispatcher_ptr : MEM_W[0x80130BB0] — pointer to 6-slot table
//                (each slot is 8B, jalr handler at slot+0x00)
//   active_slot_indices : 6 halfwords at 0x80139560
static void start_phase_poller() {
    if (!std::getenv("ROGUESQ_LOG_PHASE")) return;
    static std::thread t{[]{
        const bool callback_census = [] {
            const char* e = std::getenv("ROGUESQ_LOG_M5_CALLBACK_CENSUS");
            return e && e[0] && e[0] != '0';
        }();
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        uint32_t prev_cineState = 0xFFFFFFFFu;
        uint32_t prev_gateCtr   = 0xFFFFFFFFu;
        uint32_t prev_cutscene  = 0xFFFFFFFFu;
        uint32_t prev_cuts44    = 0xFFFFFFFFu;
        uint32_t prev_b50       = 0xFFFFFFFFu;
        uint32_t prev_b58       = 0xFFFFFFFFu;
        uint32_t prev_slot_tbl  = 0xFFFFFFFFu;
        uint32_t prev_cur_ovl   = 0xFFFFFFFFu;
        uint32_t prev_star_word = 0xFFFFFFFFu;
        uint32_t prev_cb0 = 0xDEADBEEFu, prev_cb1 = 0xDEADBEEFu;
        uint32_t prev_cb2 = 0xDEADBEEFu, prev_cb3 = 0xDEADBEEFu;
        uint16_t prev_active[6] = {0xFFFFu, 0xFFFFu, 0xFFFFu, 0xFFFFu, 0xFFFFu, 0xFFFFu};
        uint64_t start_ms = GetTickCount64();
        uint64_t last_change_ms = start_ms;
        bool first = true;

        auto rdram_be32_at = [&](uint32_t off) -> uint32_t {
            return rdram_be32(rdram, off);
        };
        auto rdram_be16_at = [&](uint32_t off) -> uint16_t {
            return (uint16_t)((uint16_t(rdram[(off + 0) ^ 3]) << 8) |
                              uint16_t(rdram[(off + 1) ^ 3]));
        };

        for (int i = 0; i < 1200; ++i) {  // ~60s @ 50ms
            uint32_t cur_ovl   = rdram_be32_at(0x375B0);  // gCurrentLoadedOverlay
            // Probe first 4 bytes of STAR WARS string at menu_overlay 0xA5E60
            // — if menu overlay is loaded, these should spell 'STAR' (0x53 54 41 52).
            uint32_t star_word = rdram_be32_at(0xA5E60);
            // Per-frame draw callbacks at 0x8011A8A4 (4 slots, fn ptrs)
            uint32_t cb0 = rdram_be32_at(0x11A8A4);
            uint32_t cb1 = rdram_be32_at(0x11A8A8);
            uint32_t cb2 = rdram_be32_at(0x11A8AC);
            uint32_t cb3 = rdram_be32_at(0x11A8B0);
            uint32_t cineState = rdram_be32_at(0xB0934);
            uint32_t gateCtr   = rdram_be32_at(0xB0B28);
            uint32_t cutscene  = rdram_be32_at(0xB1904);
            uint32_t cuts44 = 0;
            if ((cutscene & 0xF0000000u) == 0x80000000u &&
                (cutscene & 0x00FFFFFFu) + 0x44 < 0x800000u) {
                cuts44 = rdram_be32_at((cutscene & 0x00FFFFFFu) + 0x44);
            }
            uint32_t b50      = rdram_be32_at(0x130B50);
            uint32_t b58      = rdram_be32_at(0x130B58);
            uint32_t slot_tbl = rdram_be32_at(0x130BB0);
            uint16_t active[6];
            for (int j = 0; j < 6; ++j) active[j] = rdram_be16_at(0x139560 + j * 2);

            bool changed = first;
            if (cineState != prev_cineState) changed = true;
            if (gateCtr   != prev_gateCtr)   changed = true;
            if (cutscene  != prev_cutscene)  changed = true;
            if (cuts44    != prev_cuts44)    changed = true;
            if (b50       != prev_b50)       changed = true;
            if (b58       != prev_b58)       changed = true;
            if (slot_tbl  != prev_slot_tbl)  changed = true;
            if (cur_ovl   != prev_cur_ovl)   changed = true;
            if (star_word != prev_star_word) changed = true;
            if (cb0 != prev_cb0 || cb1 != prev_cb1 || cb2 != prev_cb2 || cb3 != prev_cb3) changed = true;
            if (callback_census &&
                (cb0 != prev_cb0 || cb1 != prev_cb1 ||
                 cb2 != prev_cb2 || cb3 != prev_cb3)) {
                static uint32_t callback_rows = 0;
                if (callback_rows < 256u) {
                    fprintf(stderr,
                        "[m5-callback-census] n=%u t=%llu phase=%u "
                        "last_pc=0x%08X cb=[%08X,%08X,%08X,%08X]\n",
                        callback_rows,
                        (unsigned long long)(GetTickCount64() - start_ms),
                        rs64_phase_ord(), (unsigned)g_rs64_last_guest_pc,
                        cb0, cb1, cb2, cb3);
                    fflush(stderr);
                    ++callback_rows;
                }
            }
            rs64_m5_callback_writer_snapshot();
            for (int j = 0; j < 6; ++j) {
                if (active[j] != prev_active[j]) { changed = true; break; }
            }

            if (changed) {
                uint64_t now = GetTickCount64();
                uint64_t since_start = now - start_ms;
                uint64_t stable = now - last_change_ms;
                // Decode star_word as 4-char ASCII for at-a-glance
                // "is the menu overlay's STAR WARS string here" check.
                char sw[5]; sw[0]=(char)(star_word>>24); sw[1]=(char)(star_word>>16);
                sw[2]=(char)(star_word>>8); sw[3]=(char)star_word; sw[4]=0;
                for (int k=0;k<4;k++) if (sw[k]<0x20||sw[k]>0x7E) sw[k]='.';
                fprintf(stderr,
                    "[phase] t=%5llums (stable %4llums)  cineState=%08X gateCtr=%5u "
                    "cuts=%08X cuts44=%5u B50=%08X B58=%08X slotTbl=%08X "
                    "active=[%04X %04X %04X %04X %04X %04X] curOvl=%u starWord=0x%08X(%s) "
                    "cb=[%08X %08X %08X %08X]\n",
                    (unsigned long long)since_start, (unsigned long long)stable,
                    cineState, gateCtr,
                    cutscene, cuts44,
                    b50, b58,
                    slot_tbl,
                    active[0], active[1], active[2], active[3], active[4], active[5],
                    cur_ovl, star_word, sw,
                    cb0, cb1, cb2, cb3);
                fflush(stderr);

                // When slotTbl becomes valid, dump non-empty slot entries
                // so we can see which NPCs are populated. Compare to real
                // N64 RAM dumps (e.g. lucasArtsScreen has handlers in
                // 0x80206000-0x80209000 range; N64-logo state is different).
                if ((slot_tbl & 0xF0000000u) == 0x80000000u && slot_tbl != prev_slot_tbl) {
                    uint32_t pool_off = slot_tbl & 0x00FFFFFFu;
                    int populated = 0;
                    fprintf(stderr, "[phase] slot pool @ 0x%08X populated entries:\n", slot_tbl);
                    for (int s = 0; s < 2048 && populated < 40; ++s) {
                        uint32_t entry_off = pool_off + (uint32_t)s * 8;
                        if (entry_off + 8 > 0x800000u) break;
                        uint32_t h = rdram_be32_at(entry_off);
                        uint32_t w = rdram_be32_at(entry_off + 4);
                        if (h != 0 && h != 0xFFFFFFFFu) {
                            fprintf(stderr, "  slot[%4d]: handler=0x%08X  word2=0x%08X\n", s, h, w);
                            ++populated;
                        }
                    }
                    fprintf(stderr, "[phase] (showing first %d populated of pool 2048)\n", populated);
                    fflush(stderr);
                }
                first = false;
                prev_cineState = cineState;
                prev_gateCtr   = gateCtr;
                prev_cutscene  = cutscene;
                prev_cuts44    = cuts44;
                prev_b50       = b50;
                prev_b58       = b58;
                prev_slot_tbl  = slot_tbl;
                prev_cur_ovl   = cur_ovl;
                prev_star_word = star_word;
                prev_cb0 = cb0; prev_cb1 = cb1; prev_cb2 = cb2; prev_cb3 = cb3;
                for (int j = 0; j < 6; ++j) prev_active[j] = active[j];
                last_change_ms = now;
            }
            // Periodic slot-pool snapshot every ~1 second so we can see if
            // NPCs spawn over time (real N64 attribution has 30+ populated;
            // if we stay at 4, something's stopping further spawns).
            if ((i % 20) == 0 && (slot_tbl & 0xF0000000u) == 0x80000000u) {
                uint32_t pool_off = slot_tbl & 0x00FFFFFFu;
                int total_pop = 0;
                for (int s = 0; s < 2048; ++s) {
                    uint32_t entry_off = pool_off + (uint32_t)s * 8;
                    if (entry_off + 8 > 0x800000u) break;
                    uint32_t h = rdram_be32_at(entry_off);
                    if (h != 0 && h != 0xFFFFFFFFu) ++total_pop;
                }
                fprintf(stderr, "[phase] t=%5llums slot-pool count = %d\n",
                        (unsigned long long)(GetTickCount64() - start_ms), total_pop);
                fflush(stderr);
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(
                callback_census ? 1 : 50));
        }
    }};
    t.detach();
}

static void start_m5_voice_slot_poller() {
    if (!std::getenv("ROGUESQ_LOG_M5_VOICE_SLOTS")) return;
    static std::thread t{[]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        uint8_t prev_max = 0xFF;
        uint32_t prev_mask = 0xFFFFFFFFu;
        uint64_t start_ms = GetTickCount64();
        for (int i = 0; i < 4800; ++i) {
            uint8_t max_slots = rdram[0xA5121 ^ 3];
            if (max_slots > 32) max_slots = 32;
            uint32_t active_mask = 0;
            unsigned active_count = 0;
            for (uint8_t slot = 0; slot < max_slots; ++slot) {
                uint32_t off = 0x154620u + (uint32_t)slot * 0x1228u + 0x4620u;
                uint8_t active = rdram[off ^ 3];
                if (active) {
                    active_mask |= 1u << slot;
                    ++active_count;
                }
            }
            if (max_slots != prev_max || active_mask != prev_mask) {
                const auto* vi = ultramodern::renderer::get_vi_regs();
                std::fprintf(stderr,
                    "[m5-voice-slots] t=%llums max=%u active=%u mask=0x%08X width=%u origin=0x%06X\n",
                    (unsigned long long)(GetTickCount64() - start_ms),
                    max_slots, active_count, active_mask,
                    vi->VI_WIDTH_REG, vi->VI_ORIGIN_REG & 0x00FFFFFFu);
                std::fflush(stderr);
                prev_max = max_slots;
                prev_mask = active_mask;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }};
    t.detach();
}

// ROGUESQ_LOG_FS_SLOT: macOS-friendly substitute for HWBP on the fixed
// FULL_SYNC side-slot (default phys 0x76DF60). Polls 16 bytes every 250us
// and logs any mutation + a 5s heartbeat (positive control). Discriminates
// H5a (content mutates → op no longer matches) vs H5b (submits stop while
// E9 still present). Pair with dpc_bridge [fs-slot] event=submit lines.
static void start_fs_slot_poller() {
    static std::thread t{[]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        uint32_t slot = 0x76DF60u;
        if (const char* e = std::getenv("ROGUESQ_FS_SLOT_ADDR")) {
            unsigned long v = strtoul(e, nullptr, 0);
            if (v > 0 && v < 0x800000u) slot = (uint32_t)v;
        }
        slot &= 0x7FFFFFu;
        auto rbyte = [&](uint32_t a) -> uint8_t {
            return rdram[(a & 0x7FFFFF) ^ 3];
        };
        auto snap16 = [&](uint8_t out[16]) {
            for (int i = 0; i < 16; ++i) out[i] = rbyte(slot + (uint32_t)i);
        };
        uint8_t prev[16];
        snap16(prev);
        fprintf(stderr,
            "[fs-slot] n=0 event=arm slot=0x%08X bytes="
            "%02X%02X%02X%02X %02X%02X%02X%02X %02X%02X%02X%02X %02X%02X%02X%02X\n",
            slot,
            prev[0], prev[1], prev[2], prev[3],
            prev[4], prev[5], prev[6], prev[7],
            prev[8], prev[9], prev[10], prev[11],
            prev[12], prev[13], prev[14], prev[15]);
        fflush(stderr);
        uint64_t n_change = 0;
        uint64_t n_poll = 0;
        auto t0 = std::chrono::steady_clock::now();
        auto last_hb = t0;
        for (;;) {
            uint8_t cur[16];
            snap16(cur);
            ++n_poll;
            if (memcmp(cur, prev, 16) != 0) {
                ++n_change;
                auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                    std::chrono::steady_clock::now() - t0).count();
                // H7: stamp LLE depth / task serial / guest PC / DPC regs so
                // E7/E9 transitions classify as rsp_lle vs outside_lle.
                // Positive control: dual-entry E7→E9 and stop E9→E7 both log.
                const int lle_d = g_rs64_lle_depth.load(std::memory_order_acquire);
                const uint32_t lle_tn = g_rs64_lle_task_n.load(std::memory_order_relaxed);
                const char* src = (lle_d > 0) ? "rsp_lle" : "outside_lle_or_race";
                fprintf(stderr,
                    "[fs-slot] n=%llu event=write t_ms=%lld slot=0x%08X "
                    "prev=%02X%02X%02X%02X%02X%02X%02X%02X "
                    "cur=%02X%02X%02X%02X%02X%02X%02X%02X "
                    "b0=%02X->%02X lle_depth=%d lle_task=#%u "
                    "guest_pc=0x%08X dpc_start=0x%08X dpc_end=0x%08X src=%s\n",
                    (unsigned long long)n_change, (long long)ms, slot,
                    prev[0], prev[1], prev[2], prev[3],
                    prev[4], prev[5], prev[6], prev[7],
                    cur[0], cur[1], cur[2], cur[3],
                    cur[4], cur[5], cur[6], cur[7],
                    prev[0], cur[0],
                    lle_d, lle_tn,
                    (unsigned)g_rs64_last_guest_pc,
                    g_rsp_dpc_start, g_rsp_dpc_end, src);
                fflush(stderr);
                memcpy(prev, cur, 16);
            }
            auto now = std::chrono::steady_clock::now();
            if (now - last_hb >= std::chrono::seconds(5)) {
                auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                    now - t0).count();
                fprintf(stderr,
                    "[fs-slot] n=%llu event=heartbeat t_ms=%lld slot=0x%08X "
                    "b0=%02X polls=%llu changes=%llu bytes="
                    "%02X%02X%02X%02X %02X%02X%02X%02X\n",
                    (unsigned long long)n_change, (long long)ms, slot, prev[0],
                    (unsigned long long)n_poll, (unsigned long long)n_change,
                    prev[0], prev[1], prev[2], prev[3],
                    prev[4], prev[5], prev[6], prev[7]);
                fflush(stderr);
                last_hb = now;
            }
            std::this_thread::sleep_for(std::chrono::microseconds(250));
        }
    }};
    t.detach();
}


#if defined(__APPLE__) && defined(__aarch64__)
// True if PC resolves into our main executable (not system/dylib).
static bool fl_zero_pc_in_our_bin(void* pc) {
    Dl_info dli{};
    if (!dladdr(pc, &dli) || !dli.dli_fname) return false;
    const char* base = std::strrchr(dli.dli_fname, '/');
    base = base ? base + 1 : dli.dli_fname;
    return std::strstr(base, "RogueSquadron64Recomp") != nullptr;
}

// Guest-side recomp / heap leaves (writer candidates). Deliberately does
// NOT match host `recomp::` / RT64 / ultramodern — those dominated s644's
// first sample and buried the OSThread host stacks.
static bool fl_zero_sym_is_guest(const char* s) {
    if (!s || !s[0]) return false;
    // Guest recomp bodies are mostly unmangled C (`rs_malloc`, human names).
    // Ultramodern OSThread host helpers are Itanium-mangled free functions
    // (`_Z16wait_for_resumed…`, `_ZL12_thread_func…`) — allow those by
    // substring. Reject `recomp::` / `ultramodern::` / `RT64::` class methods
    // (`_ZN…`) which are host runtime and drowned s644 v1 samples.
    if (std::strstr(s, "_ZN6recomp") || std::strstr(s, "_ZN11ultramodern") ||
        std::strstr(s, "_ZN4RT64") || std::strstr(s, "_ZN10moodycamel") ||
        std::strstr(s, "_ZNSt3")) {
        return false;
    }
    if (std::strstr(s, "rs_malloc") || std::strstr(s, "rs_free") ||
        std::strstr(s, "rs_memset") || std::strstr(s, "rs_zcalloc") ||
        std::strstr(s, "drainMesh") || std::strstr(s, "loadLevel") ||
        std::strstr(s, "heapFree") || std::strstr(s, "heapAlloc") ||
        std::strstr(s, "buildHeap") || std::strstr(s, "runModelViewer") ||
        std::strstr(s, "menuOverlay") || std::strstr(s, "mainEventQueue") ||
        std::strstr(s, "mainGameLoop") || std::strstr(s, "processAsset") ||
        std::strstr(s, "registerService") || std::strstr(s, "unregisterService") ||
        std::strstr(s, "saveService") || std::strstr(s, "hudDisplay") ||
        std::strstr(s, "buildMaterial") || std::strstr(s, "parseHmt") ||
        std::strstr(s, "loadTexture") || std::strstr(s, "initScene") ||
        std::strstr(s, "advanceVideo") || std::strstr(s, "cinematicLoop") ||
        std::strstr(s, "submitScene") || std::strstr(s, "beginFrame") ||
        std::strstr(s, "osSendMesg") || std::strstr(s, "osRecvMesg") ||
        std::strstr(s, "osPiStartDma") || std::strstr(s, "osStartThread") ||
        std::strstr(s, "osCreateThread") || std::strstr(s, "wait_for_resumed") ||
        std::strstr(s, "resume_thread") || std::strstr(s, "swap_to_thread") ||
        std::strstr(s, "thread_func") || std::strstr(s, "run_thread_function") ||
        // recompiled MIPS bodies (fixup renames + raw addresses)
        std::strstr(s, "func_") || std::strstr(s, "funcs_") ||
        std::strstr(s, "fake_func_")) {
        return true;
    }
    return false;
}

struct FlZeroThrSnap {
    unsigned thr;
    int nframes;
    int guest_n;
    int our_n;
    void* frames[32];
    char names[32][160];
    uintptr_t saddrs[32];
};

// s644: sample non-poller host threads at freelist to_zero. Poller
// backtrace (s643) is structural Outcome B — side thread has no guest
// writer frames. Collect every other thread's FP chain, rank by guest
// leaf count, dump top hits. Posctrl = menu to_zero #1 prints ≥1
// [fl-zero-poll-gbt] summary; guest_n>0 on a thr is the useful hit.
static void fl_zero_sample_game_threads(uint64_t n_change, uint64_t n_to_zero,
                                        long long ms, unsigned pf, unsigned psz) {
    thread_act_array_t threads = nullptr;
    mach_msg_type_number_t nthreads = 0;
    kern_return_t kr = task_threads(mach_task_self(), &threads, &nthreads);
    if (kr != KERN_SUCCESS || !threads) {
        fprintf(stderr,
            "[fl-zero-poll-gbt] n=%llu to_zero_n=%llu event=task_threads_fail "
            "kr=%d t_ms=%lld\n",
            (unsigned long long)n_change, (unsigned long long)n_to_zero,
            (int)kr, ms);
        return;
    }
    thread_t self = mach_thread_self();
    // Cap collection — process can have 60+ threads; we only care about
    // those with guest frames. Keep up to 24 snaps for ranking.
    static const int kMaxSnap = 24;
    FlZeroThrSnap snaps[kMaxSnap];
    int nsnap = 0;
    int thr_with_guest = 0;
    int thr_with_our = 0;

    for (mach_msg_type_number_t ti = 0; ti < nthreads; ++ti) {
        if (threads[ti] == self) continue;
        if (thread_suspend(threads[ti]) != KERN_SUCCESS) continue;

        arm_thread_state64_t st{};
        mach_msg_type_number_t scount = ARM_THREAD_STATE64_COUNT;
        kr = thread_get_state(threads[ti], ARM_THREAD_STATE64,
                              (thread_state_t)&st, &scount);
        void* frames[32];
        int nframes = 0;
        if (kr == KERN_SUCCESS) {
            uintptr_t pc = (uintptr_t)arm_thread_state64_get_pc(st);
            uintptr_t fp = (uintptr_t)arm_thread_state64_get_fp(st);
            if (pc) frames[nframes++] = (void*)pc;
            for (int depth = 0; depth < 31 && fp >= 0x1000 && (fp & 0xF) == 0; ++depth) {
                uintptr_t pair[2] = {0, 0};
                mach_vm_size_t out_sz = 0;
                kern_return_t rkr = mach_vm_read_overwrite(
                    mach_task_self(), (mach_vm_address_t)fp,
                    (mach_vm_size_t)sizeof(pair),
                    (mach_vm_address_t)pair, &out_sz);
                if (rkr != KERN_SUCCESS || out_sz != sizeof(pair)) break;
                uintptr_t next_fp = pair[0];
                uintptr_t lr = pair[1];
                if (!lr) break;
                frames[nframes++] = (void*)lr;
                if (next_fp <= fp || (next_fp & 0xF) != 0) break;
                fp = next_fp;
            }
        }
        thread_resume(threads[ti]);
        if (nframes <= 0) continue;

        int guest_n = 0;
        int our_n = 0;
        char names[32][160];
        uintptr_t saddrs[32];
        for (int bi = 0; bi < nframes; ++bi) {
            names[bi][0] = '\0';
            saddrs[bi] = (uintptr_t)frames[bi];
            Dl_info dli{};
            if (dladdr(frames[bi], &dli)) {
                if (dli.dli_sname) {
                    std::snprintf(names[bi], sizeof(names[bi]), "%s", dli.dli_sname);
                }
                if (dli.dli_saddr) saddrs[bi] = (uintptr_t)dli.dli_saddr;
            }
            const char* s = names[bi];
            if (std::strstr(s, "start_fl_zero_poller") ||
                std::strstr(s, "fl_zero_sample_game") ||
                std::strstr(s, "fl_zero_pc_in_our") ||
                std::strstr(s, "fl_zero_sym_is_guest")) {
                continue;
            }
            if (fl_zero_sym_is_guest(s)) {
                ++guest_n;
                ++our_n;
            } else if (fl_zero_pc_in_our_bin(frames[bi])) {
                ++our_n;
            }
        }
        if (guest_n > 0) ++thr_with_guest;
        if (our_n > 0) ++thr_with_our;
        // Prefer guest-bearing; keep a few our-bin-only for posctrl if no
        // guest yet. Host-only stacks (RT64/ultramodern) are dropped.
        if (guest_n == 0 && thr_with_guest > 0) continue;
        if (guest_n == 0 && nsnap >= 8) continue;
        if (our_n == 0) continue;

        int slot = -1;
        if (nsnap < kMaxSnap) {
            slot = nsnap++;
        } else {
            int worst = 0;
            for (int i = 1; i < kMaxSnap; ++i) {
                if (snaps[i].guest_n < snaps[worst].guest_n ||
                    (snaps[i].guest_n == snaps[worst].guest_n &&
                     snaps[i].our_n < snaps[worst].our_n)) {
                    worst = i;
                }
            }
            if (guest_n < snaps[worst].guest_n ||
                (guest_n == snaps[worst].guest_n && our_n <= snaps[worst].our_n)) {
                continue;
            }
            slot = worst;
        }
        FlZeroThrSnap& sn = snaps[slot];
        sn.thr = (unsigned)threads[ti];
        sn.nframes = nframes;
        sn.guest_n = guest_n;
        sn.our_n = our_n;
        for (int bi = 0; bi < nframes; ++bi) {
            sn.frames[bi] = frames[bi];
            std::memcpy(sn.names[bi], names[bi], sizeof(names[bi]));
            sn.saddrs[bi] = saddrs[bi];
        }
    }

    // Rank by guest_n desc, then our_n
    int order[kMaxSnap];
    for (int i = 0; i < nsnap; ++i) order[i] = i;
    for (int i = 0; i < nsnap; ++i) {
        for (int j = i + 1; j < nsnap; ++j) {
            FlZeroThrSnap& a = snaps[order[i]];
            FlZeroThrSnap& b = snaps[order[j]];
            if (b.guest_n > a.guest_n ||
                (b.guest_n == a.guest_n && b.our_n > a.our_n)) {
                int tmp = order[i]; order[i] = order[j]; order[j] = tmp;
            }
        }
    }

    int report_cap = 6;
    int reported = 0;
    for (int oi = 0; oi < nsnap && reported < report_cap; ++oi) {
        FlZeroThrSnap& sn = snaps[order[oi]];
        // Prefer guest-bearing; if none exist, still dump top our-bin for
        // posctrl visibility (proves sampler reaches game binary frames).
        if (sn.guest_n == 0 && thr_with_guest > 0) continue;
        ++reported;
        fprintf(stderr,
            "[fl-zero-poll-gbt] n=%llu to_zero_n=%llu thr=%u frames=%d "
            "guest_n=%d our_n=%d guest_pc=0x%08X t_ms=%lld "
            "prev_f=0x%X prev_sz=0x%X\n",
            (unsigned long long)n_change, (unsigned long long)n_to_zero,
            sn.thr, sn.nframes, sn.guest_n, sn.our_n,
            (unsigned)g_rs64_last_guest_pc, ms, pf, psz);
        for (int bi = 0; bi < sn.nframes; ++bi) {
            Dl_info dli{};
            const char* sname = sn.names[bi][0] ? sn.names[bi] : nullptr;
            const char* fname = nullptr;
            uintptr_t saddr = sn.saddrs[bi];
            if (dladdr(sn.frames[bi], &dli)) {
                if (!sname && dli.dli_sname) sname = dli.dli_sname;
                fname = dli.dli_fname;
                if (dli.dli_saddr) saddr = (uintptr_t)dli.dli_saddr;
            }
            const char* base = fname ? std::strrchr(fname, '/') : nullptr;
            fprintf(stderr,
                "[fl-zero-poll-gbt]   thr=%u [%2d] %s | %s+0x%llx\n",
                sn.thr, bi,
                sname ? sname : "?",
                base ? base + 1 : (fname ? fname : "?"),
                (unsigned long long)((uintptr_t)sn.frames[bi] - saddr));
        }
    }
    fprintf(stderr,
        "[fl-zero-poll-gbt] n=%llu to_zero_n=%llu event=summary "
        "nthreads=%u nsnap=%d reported=%d thr_with_guest=%d thr_with_our=%d "
        "guest_pc=0x%08X t_ms=%lld prev_f=0x%X prev_sz=0x%X\n",
        (unsigned long long)n_change, (unsigned long long)n_to_zero,
        (unsigned)nthreads, nsnap, reported, thr_with_guest, thr_with_our,
        (unsigned)g_rs64_last_guest_pc, ms, pf, psz);

    for (mach_msg_type_number_t ti = 0; ti < nthreads; ++ti) {
        mach_port_deallocate(mach_task_self(), threads[ti]);
    }
    vm_deallocate(mach_task_self(), (vm_address_t)threads,
                  sizeof(thread_t) * nthreads);
    mach_port_deallocate(mach_task_self(), self);
}
#endif

// s646/s647: mprotect page-fault watch on the fail136c freelist header page.
// Poller sticky guest_pc + gbt cannot name the freelist stomp writer
// (Outcome B s644/s645/s646: writer off-stack; freelist+memset class REFUTED).
// Arm PROT_READ on the host page of phys slot while the header is in a
// target shape; SIGSEGV on write logs [fl-zero-fault] with host PC (local
// symtab) + guest sticky, then re-enables RW so the store completes.
// s647 Outcome B (s646 freeroll): freelist arm LIVE + to_zero 0x2/0x60→0 but
// flz_fault_hdr=0 — neighbor thrash unprotects the 16KB Apple page, then the
// real header store races through the RW window before the 250µs poller re-arm.
// Fix: (1) want=1 boot / want=2 freelist; (2) dedicated busy re-arm spinner
// while want==2 (s647: ARM64 SS via thread_set_state from SEGV is toxic —
// nested SIGTRAP in mach_msg/thread_set_state, CRASH=36 posctrl); (3) full
// BT while want==2; (4) poller 10µs while freelist-armed; (5) to_zero_correlate.
// Filter in_hdr=1 = fa in [slot,slot+8). Gate: ROGUESQ_LOG_FL_ZERO_WATCH.
#ifndef _WIN32
static std::atomic<uint8_t*> g_flz_fault_rdram{nullptr};
static std::atomic<uint32_t> g_flz_fault_slot{0x1F3CC0u};
static std::atomic<int> g_flz_fault_want{0};   // 0=off 1=boot-zero 2=freelist
static std::atomic<int> g_flz_fault_armed{0};  // currently PROT_READ
static std::atomic<uint64_t> g_flz_fault_n{0};
static std::atomic<uint64_t> g_flz_fault_hdr_n{0};
static std::atomic<uint64_t> g_flz_fault_late_n{0}; // s649: recover with armed==0
static std::atomic<int> g_flz_fault_enabled{0};
static std::atomic<uint64_t> g_flz_busy_rearm_n{0};
// Steady-clock ns of last handled page fault — busy re-arm waits ≥20µs
// after this so the restarted store can complete (re-arm too early →
// infinite SEGV on the same insn).
static std::atomic<uint64_t> g_flz_last_fault_ns{0};
static std::atomic<uint64_t> g_flz_last_fa{0};
static std::atomic<uint64_t> g_flz_last_pc{0};
static std::atomic<uint64_t> g_flz_last_lr{0};
static std::atomic<uint64_t> g_flz_last_n{0};
static std::atomic<int> g_flz_last_in_hdr{0};
static std::atomic<int> g_flz_last_want{0};
// Last resolved symbol name (async-signal: fixed buffer, not a pointer into
// dyld string tables that may move).
static char g_flz_last_sym[96] = "none";

// s651: rate-limit drops want==2 lines after n=32 (every 256th only), so
// freelist-window faults n=33..to_zero were invisible except last_* atomics.
// Always record a compact ring; dump on freelist-shaped to_zero_correlate.
// No BT in the ring path — avoids s648 thrash cost.
struct FlzFaultRingRec {
    uint64_t n;
    uint64_t fa;
    uint64_t pc;
    uint64_t lr;
    uint64_t pc_off;
    uint32_t guest_pc;
    int in_hdr;
    int near_hdr;
    int late;
    int want;
    char sym[64];
};
static constexpr int kFlzFaultRing = 16;
static FlzFaultRingRec g_flz_fault_ring[kFlzFaultRing];
static std::atomic<uint64_t> g_flz_fault_ring_w{0};
static size_t fl_zero_page_size();

// Phase-scoped host write attribution for the remaining exact route fields.
// The page is read-protected so a native store exposes its host PC through
// the ARM64 signal context; the handler briefly restores write access so the
// faulting instruction can retry.
static std::atomic<uint8_t*> g_m5_host_fault_rdram{nullptr};
static std::atomic<int> g_m5_host_fault_enabled{0};
static std::atomic<int> g_m5_host_fault_armed{0};
static uintptr_t g_m5_host_fault_page = 0;
static size_t g_m5_host_fault_page_size = 0;
static std::atomic<uint64_t> g_m5_host_fault_n{0};
static std::atomic<uint64_t> g_m5_host_fault_control_n{0};
static std::atomic<uint64_t> g_m5_host_fault_exact_n{0};

static bool m5_host_fault_try_handle(siginfo_t* info, void* ucontext_raw) {
    if (!g_m5_host_fault_enabled.load(std::memory_order_acquire) ||
        !info || !info->si_addr) return false;
    const uintptr_t fa = (uintptr_t)info->si_addr;
    const uintptr_t page = g_m5_host_fault_page;
    const size_t page_size = g_m5_host_fault_page_size;
    if (!page || !page_size || fa < page || fa >= page + page_size) return false;

    mprotect((void*)page, page_size, PROT_READ | PROT_WRITE);
    g_m5_host_fault_armed.store(0, std::memory_order_release);
    const uint32_t phys = (uint32_t)(fa - (uintptr_t)g_m5_host_fault_rdram.load(
        std::memory_order_relaxed));
    const bool exact = (phys >= 0x128C92u && phys < 0x128C93u) ||
                       (phys >= 0x128CD0u && phys < 0x128CD4u);
    const uint64_t n = g_m5_host_fault_n.fetch_add(1, std::memory_order_relaxed) + 1;
    if (exact) g_m5_host_fault_exact_n.fetch_add(1, std::memory_order_relaxed);
    else g_m5_host_fault_control_n.fetch_add(1, std::memory_order_relaxed);

    uint64_t pc = 0, lr = 0;
#if defined(__APPLE__) && defined(__aarch64__)
    if (ucontext_raw) {
        ucontext_t* uc = static_cast<ucontext_t*>(ucontext_raw);
        if (uc->uc_mcontext) {
            pc = (uint64_t)uc->uc_mcontext->__ss.__pc;
            lr = (uint64_t)uc->uc_mcontext->__ss.__lr;
        }
    }
#else
    (void)ucontext_raw;
#endif
    uint32_t phase = 0, width = 0, origin = 0, ordinal = 0xFFFFFFFFu, row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool route_active = rs64_audio_current_route_snapshot(
        &phase, &width, &origin, &ordinal, &row, &exit_reason, &arm);
    const bool target_phase = (width == 1024u && origin == 0x00790400u) ||
                             (width == 512u && origin == 0x006AB400u);
    if (n == 1) {
        fprintf(stderr, "[m5-host-write-fault-control] first=1 phys=0x%06X pc=0x%llX\n",
            phys, (unsigned long long)pc);
    }
    if (exact && route_active && target_phase && n <= 256) {
        fprintf(stderr,
            "[m5-host-write-fault] n=%llu phys=0x%06X phase=%u width=%u "
            "origin=0x%06X arm=%s route_ordinal=%u route_row=%u pc=0x%llX lr=0x%llX\n",
            (unsigned long long)n, phys, phase, width, origin, arm ? arm : "n/a",
            ordinal, row, (unsigned long long)pc, (unsigned long long)lr);
    }
    fflush(stderr);
    return true;
}

static void start_m5_host_write_fault_watch() {
    static std::thread t{[]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        g_m5_host_fault_rdram.store(rdram, std::memory_order_release);
        g_m5_host_fault_page_size = fl_zero_page_size();
        g_m5_host_fault_page = ((uintptr_t)rdram + 0x128C92u) &
            ~(uintptr_t)(g_m5_host_fault_page_size - 1);
        if (mprotect((void*)g_m5_host_fault_page, g_m5_host_fault_page_size,
                     PROT_READ) != 0) {
            fprintf(stderr, "[m5-host-write-fault-control] arm_failed errno=%d\n", errno);
            fflush(stderr);
            return;
        }
        g_m5_host_fault_armed.store(1, std::memory_order_release);
        g_m5_host_fault_enabled.store(1, std::memory_order_release);
        fprintf(stderr,
            "[m5-host-write-fault-control] armed page=0x%llX page_size=%zu "
            "ranges=0x128C92..0x128C93,0x128CD0..0x128CD4\n",
            (unsigned long long)g_m5_host_fault_page, g_m5_host_fault_page_size);
        fflush(stderr);
        for (;;) {
            std::this_thread::sleep_for(std::chrono::microseconds(250));
            if (g_m5_host_fault_enabled.load(std::memory_order_relaxed) &&
                mprotect((void*)g_m5_host_fault_page, g_m5_host_fault_page_size,
                         PROT_READ) == 0) {
                g_m5_host_fault_armed.store(1, std::memory_order_release);
            }
        }
    }};
    t.detach();
}

// Phase-scoped native-write census for the task-data object. This is separate
// from the route-field watch because the two objects are on different pages.
static std::atomic<uint8_t*> g_m5_task_fault_rdram{nullptr};
static std::atomic<int> g_m5_task_fault_enabled{0};
static uintptr_t g_m5_task_fault_page = 0;
static size_t g_m5_task_fault_page_size = 0;
static std::atomic<uint64_t> g_m5_task_fault_n{0};
static std::atomic<uint64_t> g_m5_task_fault_control_n{0};
static std::atomic<uint64_t> g_m5_task_fault_exact_n{0};
static std::atomic<uint64_t> g_m5_task_fault_pending_n{0};
static std::atomic<uint32_t> g_m5_task_fault_pending_phys{0};
static std::atomic<uint32_t> g_m5_task_fault_pending_width{0};
static std::atomic<uint64_t> g_m5_task_fault_pending_value{0};
static std::atomic<uint64_t> g_m5_task_fault_pending_pc{0};

#if defined(__APPLE__) && defined(__aarch64__)
static bool m5_task_decode_str(uint32_t insn, const ucontext_t* uc,
                               uint32_t& width, uint64_t& value,
                               uint32_t& rt) {
    uint32_t base = insn & 0xFFC00000u;
    switch (base) {
    case 0x39000000u: width = 1; break;
    case 0x79000000u: width = 2; break;
    case 0xB9000000u: width = 4; break;
    case 0xF9000000u: width = 8; break;
    default: return false;
    }
    rt = insn & 31u;
    value = rt == 31u ? 0u : uc->uc_mcontext->__ss.__x[rt];
    if (width < 8) value &= (1ull << (width * 8u)) - 1ull;
    return true;
}
#endif

static bool m5_task_fault_try_handle(siginfo_t* info, void* ucontext_raw) {
    if (!g_m5_task_fault_enabled.load(std::memory_order_acquire) ||
        !info || !info->si_addr) return false;
    const uintptr_t fa = (uintptr_t)info->si_addr;
    const uintptr_t page = g_m5_task_fault_page;
    const size_t page_size = g_m5_task_fault_page_size;
    if (!page || !page_size || fa < page || fa >= page + page_size) return false;

    mprotect((void*)page, page_size, PROT_READ | PROT_WRITE);
    const uint32_t phys = (uint32_t)(fa - (uintptr_t)g_m5_task_fault_rdram.load(
        std::memory_order_relaxed));
    const bool exact = phys >= 0x171E70u && phys < 0x171F70u;
    const uint64_t n = g_m5_task_fault_n.fetch_add(1, std::memory_order_relaxed) + 1;
    if (exact) g_m5_task_fault_exact_n.fetch_add(1, std::memory_order_relaxed);
    else g_m5_task_fault_control_n.fetch_add(1, std::memory_order_relaxed);

    uint64_t pc = 0, lr = 0, store_value = 0;
    uint32_t store_width = 0, store_rt = 0, store_insn = 0;
    bool store_decoded = false;
    uint32_t phase = 0, width = 0, origin = 0, ordinal = 0xFFFFFFFFu,
             row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool route_active = rs64_audio_current_route_snapshot(
        &phase, &width, &origin, &ordinal, &row, &exit_reason, &arm);
    const bool target_phase = (width == 1024u && origin == 0x00790400u) ||
                             (width == 512u && origin == 0x006AB400u);
#if defined(__APPLE__) && defined(__aarch64__)
    if (exact && route_active && target_phase && ucontext_raw) {
        ucontext_t* uc = static_cast<ucontext_t*>(ucontext_raw);
        if (uc->uc_mcontext) {
            pc = (uint64_t)uc->uc_mcontext->__ss.__pc;
            lr = (uint64_t)uc->uc_mcontext->__ss.__lr;
            store_insn = *reinterpret_cast<const uint32_t*>(pc);
            store_decoded = m5_task_decode_str(store_insn, uc, store_width,
                                               store_value, store_rt);
        }
    }
#else
    (void)ucontext_raw;
#endif
    if (n == 1) {
        fprintf(stderr, "[m5-task-write-fault-control] first=1 phys=0x%06X pc=0x%llX "
                       "phase=%u width=%u origin=0x%06X\n",
            phys, (unsigned long long)pc, phase, width, origin);
    }
    if (exact && route_active && target_phase && n <= 512) {
        fprintf(stderr,
            "[m5-task-write-fault] n=%llu phys=0x%06X phase=%u width=%u "
            "origin=0x%06X arm=%s route_ordinal=%u route_row=%u pc=0x%llX lr=0x%llX "
            "insn=0x%08X decoded=%u store_width=%u rt=%u store_value=0x%llX\n",
            (unsigned long long)n, phys, phase, width, origin, arm ? arm : "n/a",
            ordinal, row, (unsigned long long)pc, (unsigned long long)lr,
            store_insn, store_decoded ? 1u : 0u, store_width, store_rt,
            (unsigned long long)store_value);
        if (store_decoded) {
            g_m5_task_fault_pending_phys.store(phys, std::memory_order_relaxed);
            g_m5_task_fault_pending_width.store(store_width, std::memory_order_relaxed);
            g_m5_task_fault_pending_value.store(store_value, std::memory_order_relaxed);
            g_m5_task_fault_pending_pc.store(pc, std::memory_order_relaxed);
            g_m5_task_fault_pending_n.store(n, std::memory_order_release);
        }
    }
    fflush(stderr);
    return true;
}

static void start_m5_task_write_fault_watch() {
    static std::thread t{[]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        g_m5_task_fault_rdram.store(rdram, std::memory_order_release);
        g_m5_task_fault_page_size = fl_zero_page_size();
        g_m5_task_fault_page = ((uintptr_t)rdram + 0x171E70u) &
            ~(uintptr_t)(g_m5_task_fault_page_size - 1);
        bool armed = false;
        uint64_t target_ticks = 0;
        uint64_t target_gaps = 0;
        uint64_t arm_count = 0;
        uint64_t rearm_count = 0;
        bool target_seen = false;
        for (;;) {
            std::this_thread::sleep_for(std::chrono::microseconds(250));
            const uint64_t pending = g_m5_task_fault_pending_n.exchange(
                0, std::memory_order_acq_rel);
            if (pending) {
                const uint32_t phys = g_m5_task_fault_pending_phys.load(
                    std::memory_order_relaxed);
                const uint32_t sw = g_m5_task_fault_pending_width.load(
                    std::memory_order_relaxed);
                const uint64_t sv = g_m5_task_fault_pending_value.load(
                    std::memory_order_relaxed);
                const uint64_t spc = g_m5_task_fault_pending_pc.load(
                    std::memory_order_relaxed);
                const uint8_t* post = rdram + phys;
                fprintf(stderr,
                    "[m5-task-write-post] n=%llu phys=0x%06X width=%u "
                    "source=0x%llX pc=0x%llX bytes="
                    "%02X%02X%02X%02X%02X%02X%02X%02X\n",
                    (unsigned long long)pending, phys, sw,
                    (unsigned long long)sv, (unsigned long long)spc,
                    post[0], post[1], post[2], post[3],
                    post[4], post[5], post[6], post[7]);
                fflush(stderr);
            }
            const uint32_t width = rs64_vi_committed_width();
            const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
            const bool target = (width == 1024u && origin == 0x00790400u) ||
                                (width == 512u && origin == 0x006AB400u);
            if (target && !armed) {
                if (mprotect((void*)g_m5_task_fault_page, g_m5_task_fault_page_size,
                             PROT_READ) != 0) {
                    fprintf(stderr, "[m5-task-write-fault-control] arm_failed errno=%d\n", errno);
                    fflush(stderr);
                    return;
                }
                armed = true;
                ++arm_count;
                ++target_gaps;
                if (!target_seen) {
                    target_seen = true;
                    fprintf(stderr,
                        "[m5-task-write-window] event=enter width=%u origin=0x%06X "
                        "target_ticks=%llu target_gaps=%llu arm_count=%llu rearm_count=%llu\n",
                        width, origin, (unsigned long long)target_ticks,
                        (unsigned long long)target_gaps,
                        (unsigned long long)arm_count,
                        (unsigned long long)rearm_count);
                }
                g_m5_task_fault_enabled.store(1, std::memory_order_release);
                fprintf(stderr,
                    "[m5-task-write-fault-control] armed page=0x%llX page_size=%zu "
                    "range=0x171E70..0x171F70 width=%u origin=0x%06X\n",
                    (unsigned long long)g_m5_task_fault_page, g_m5_task_fault_page_size,
                    width, origin);
                fflush(stderr);
            } else if (!target && armed) {
                mprotect((void*)g_m5_task_fault_page, g_m5_task_fault_page_size,
                         PROT_READ | PROT_WRITE);
                armed = false;
                g_m5_task_fault_enabled.store(0, std::memory_order_release);
                fprintf(stderr,
                    "[m5-task-write-window] event=exit width=%u origin=0x%06X "
                    "target_ticks=%llu target_gaps=%llu arm_count=%llu rearm_count=%llu\n",
                    width, origin, (unsigned long long)target_ticks,
                    (unsigned long long)target_gaps,
                    (unsigned long long)arm_count,
                    (unsigned long long)rearm_count);
            } else if (armed) {
                ++rearm_count;
                if (mprotect((void*)g_m5_task_fault_page, g_m5_task_fault_page_size,
                             PROT_READ) != 0) {
                    ++target_gaps;
                }
            }
            if (target) {
                ++target_ticks;
                if (!armed) ++target_gaps;
                if (target_ticks == 1 || (target_ticks % 2000u) == 0) {
                    fprintf(stderr,
                        "[m5-task-write-window] event=heartbeat width=%u origin=0x%06X "
                        "target_ticks=%llu target_gaps=%llu arm_count=%llu rearm_count=%llu\n",
                        width, origin, (unsigned long long)target_ticks,
                        (unsigned long long)target_gaps,
                        (unsigned long long)arm_count,
                        (unsigned long long)rearm_count);
                    fflush(stderr);
                }
            }
        }
    }};
    t.detach();
}

// Phase-gated write-fault census for the F5 VTXCOLOR payload pages. This is
// diagnostic only: the handler makes the faulting store retry after briefly
// restoring page write access, then the watcher re-arms the page.
static std::atomic<uint8_t*> g_vtx_fault_rdram{nullptr};
static std::atomic<int> g_vtx_fault_enabled{0};
static std::atomic<uint64_t> g_vtx_fault_n{0};
static std::atomic<uint64_t> g_vtx_fault_phase4_n{0};
static std::atomic<uint64_t> g_vtx_fault_phase6_n{0};
static std::atomic<int> g_vtx_fault_armed{0};
static uintptr_t g_vtx_fault_pages[2] = {};
static size_t g_vtx_fault_page = 0;

static bool vtx_fault_page_for(uintptr_t fa, int* page_index) {
    for (int i = 0; i < 2; ++i) {
        if (g_vtx_fault_pages[i] != 0 && fa >= g_vtx_fault_pages[i] &&
            fa < g_vtx_fault_pages[i] + g_vtx_fault_page) {
            if (page_index) *page_index = i;
            return true;
        }
    }
    return false;
}

static bool vtx_fault_try_handle_fault(siginfo_t* info, void* ucontext_raw) {
    if (!g_vtx_fault_enabled.load(std::memory_order_acquire) ||
        !info || !info->si_addr) return false;
    int page_index = -1;
    const uintptr_t fa = (uintptr_t)info->si_addr;
    if (!vtx_fault_page_for(fa, &page_index)) return false;

    mprotect((void*)g_vtx_fault_pages[page_index], g_vtx_fault_page,
             PROT_READ | PROT_WRITE);
    g_vtx_fault_armed.fetch_sub(1, std::memory_order_release);

    uint64_t n = g_vtx_fault_n.fetch_add(1, std::memory_order_relaxed) + 1;
    const uint32_t phys = (uint32_t)(fa - (uintptr_t)g_vtx_fault_rdram.load(
        std::memory_order_relaxed));
    const uint32_t phase = rs64_phase_ord();
    const uint32_t p4lo = 0x726200u, p4hi = 0x726C50u;
    const uint32_t p6lo = 0x732A10u, p6hi = 0x73E3B0u;
    const bool p4 = phys < p4hi && phys + 1 >= p4lo;
    const bool p6 = phys < p6hi && phys + 1 >= p6lo;
    if (p4) g_vtx_fault_phase4_n.fetch_add(1, std::memory_order_relaxed);
    if (p6) g_vtx_fault_phase6_n.fetch_add(1, std::memory_order_relaxed);

    uint64_t pc = 0, lr = 0;
#if defined(__APPLE__) && defined(__aarch64__)
    if (ucontext_raw) {
        ucontext_t* uc = static_cast<ucontext_t*>(ucontext_raw);
        if (uc->uc_mcontext) {
            pc = (uint64_t)uc->uc_mcontext->__ss.__pc;
            lr = (uint64_t)uc->uc_mcontext->__ss.__lr;
        }
    }
#else
    (void)ucontext_raw;
#endif
    static uint64_t phase_detail_n = 0;
    if (phase >= 6 && p6) {
        ++phase_detail_n;
    }
    if (n <= 128 || (phase >= 6 && p6 && phase_detail_n <= 256)) {
        fprintf(stderr,
            "[vtx-write-fault] n=%llu phase=%u phys=0x%06X page=%d "
            "overlap=p4:%d,p6:%d pc=0x%llX lr=0x%llX guest_pc=0x%08X\n",
            (unsigned long long)n, phase, phys, page_index, p4 ? 1 : 0,
            p6 ? 1 : 0, (unsigned long long)pc, (unsigned long long)lr,
            (unsigned)g_rs64_last_guest_pc);
        fflush(stderr);
    }
    return true;
}

static void start_vtx_write_fault_watch() {
    static std::thread t{[]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        g_vtx_fault_rdram.store(rdram, std::memory_order_release);
        g_vtx_fault_page = fl_zero_page_size();
        const uint32_t ranges[] = {0x726200u, 0x732A10u};
        for (int i = 0; i < 2; ++i) {
            uintptr_t host = (uintptr_t)rdram + ranges[i];
            g_vtx_fault_pages[i] = host & ~(uintptr_t)(g_vtx_fault_page - 1);
            mprotect((void*)g_vtx_fault_pages[i], g_vtx_fault_page, PROT_READ);
        }
        g_vtx_fault_armed.store(2, std::memory_order_release);
        g_vtx_fault_enabled.store(1, std::memory_order_release);
        fprintf(stderr,
            "[vtx-write-fault-control] armed pages=0x%llX,0x%llX page=%zu "
            "ranges=p4:0x726200..0x726C50,p6:0x732A10..0x73E3B0\n",
            (unsigned long long)g_vtx_fault_pages[0],
            (unsigned long long)g_vtx_fault_pages[1], g_vtx_fault_page);
        fflush(stderr);
        for (;;) {
            for (int i = 0; i < 2; ++i) {
                uintptr_t page = g_vtx_fault_pages[i];
                if (page && g_vtx_fault_enabled.load(std::memory_order_relaxed)) {
                    // Give the faulting store time to retire before re-arming.
                    std::this_thread::sleep_for(std::chrono::microseconds(250));
                    if (mprotect((void*)page, g_vtx_fault_page, PROT_READ) == 0)
                        g_vtx_fault_armed.fetch_add(1, std::memory_order_release);
                }
            }
        }
    }};
    t.detach();
}

static size_t fl_zero_page_size() {
    long p = sysconf(_SC_PAGESIZE);
    return (p > 0) ? (size_t)p : 16384u;
}

// MEM_W host address for KSEG0 0x80000000+phys (word-aligned).
static uintptr_t fl_zero_header_host(uint8_t* rdram, uint32_t slot) {
    return (uintptr_t)rdram + (uintptr_t)(slot & 0x1FFFFFFu);
}

static void fl_zero_resolve_sym(uint64_t pc, const char** out_name, uint64_t* out_off) {
    *out_name = "<unresolved>";
    *out_off = 0;
    if (!pc) return;
#if defined(__APPLE__) && defined(__aarch64__)
    const RS64LocalSymbol* localSym = rs64_lookup_local_symbol(pc);
    if (localSym) {
        *out_name = localSym->name.c_str();
        *out_off = pc - localSym->addr;
        return;
    }
#endif
    Dl_info dli{};
    if (dladdr((void*)(uintptr_t)pc, &dli) && dli.dli_sname) {
        *out_name = dli.dli_sname;
        *out_off = pc - (uint64_t)(uintptr_t)dli.dli_saddr;
    }
}

static void fl_zero_fault_disarm() {
    uint8_t* rdram = g_flz_fault_rdram.load(std::memory_order_acquire);
    if (!rdram) return;
    uint32_t slot = g_flz_fault_slot.load(std::memory_order_relaxed);
    size_t page = fl_zero_page_size();
    uintptr_t host = fl_zero_header_host(rdram, slot);
    uintptr_t page_base = host & ~(uintptr_t)(page - 1);
    if (mprotect((void*)page_base, page, PROT_READ | PROT_WRITE) == 0) {
        g_flz_fault_armed.store(0, std::memory_order_release);
    }
}

static void fl_zero_fault_arm() {
    uint8_t* rdram = g_flz_fault_rdram.load(std::memory_order_acquire);
    if (!rdram) return;
    uint32_t slot = g_flz_fault_slot.load(std::memory_order_relaxed);
    size_t page = fl_zero_page_size();
    uintptr_t host = fl_zero_header_host(rdram, slot);
    uintptr_t page_base = host & ~(uintptr_t)(page - 1);
    if (mprotect((void*)page_base, page, PROT_READ) == 0) {
        g_flz_fault_armed.store(1, std::memory_order_release);
    }
}

// Called from SIGSEGV/SIGBUS handler. Returns true if this was our watch fault
// (store should be retried after RW re-enable). Not async-signal-pure
// (fprintf/backtrace) — same diagnostic trade-off as the crash handler.
//
// s649: do NOT require armed==1. s648 att4: after arm_freelist, neighbor thrash
// (buildModelViewerTextPage on same 16KB page) delivered SIGBUS at fa in page
// with armed already 0 — concurrent/stale-TLB fault after a peer handler
// disarmed fell through to [CRASH] and killed the run before the freelist
// stomp window (~+19s). Policy: if fa is on the watch page and want!=0,
// always unprotect + recover (idempotent). armed is only a re-arm hint.
static bool fl_zero_try_handle_fault(siginfo_t* info, void* ucontext_raw) {
    if (!g_flz_fault_enabled.load(std::memory_order_relaxed)) return false;
    int want_gate = g_flz_fault_want.load(std::memory_order_acquire);
    int was_armed = g_flz_fault_armed.load(std::memory_order_acquire);
    // Boot-zero (want=1) or freelist (want=2) window must recover page faults
    // even when armed==0 (TLB race). Outside a watch window, leave to CRASH.
    if (want_gate == 0 && !was_armed) return false;
    uint8_t* rdram = g_flz_fault_rdram.load(std::memory_order_acquire);
    if (!rdram || !info || !info->si_addr) return false;

    uintptr_t fa = (uintptr_t)info->si_addr;
    uint32_t slot = g_flz_fault_slot.load(std::memory_order_relaxed);
    size_t page = fl_zero_page_size();
    uintptr_t host = fl_zero_header_host(rdram, slot);
    uintptr_t page_base = host & ~(uintptr_t)(page - 1);
    if (fa < page_base || fa >= page_base + page) return false;

    // Allow the faulting store to complete (idempotent if already RW).
    mprotect((void*)page_base, page, PROT_READ | PROT_WRITE);
    g_flz_fault_armed.store(0, std::memory_order_release);
    {
        auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count();
        g_flz_last_fault_ns.store((uint64_t)ns, std::memory_order_release);
    }

    uint64_t n = g_flz_fault_n.fetch_add(1, std::memory_order_relaxed) + 1;
    int in_hdr = (fa >= host && fa < host + 8) ? 1 : 0;
    // Free-block window (size 0x60): fa in [host, host+0x80). Catches payload
    // stores that open the RW race without counting as strict header hits.
    int near_hdr = (fa >= host && fa < host + 0x80) ? 1 : 0;
    if (in_hdr) {
        g_flz_fault_hdr_n.fetch_add(1, std::memory_order_relaxed);
    }
    int late = (!was_armed && want_gate != 0) ? 1 : 0;
    if (late) {
        g_flz_fault_late_n.fetch_add(1, std::memory_order_relaxed);
    }

    uint64_t pc = 0, lr = 0;
#if defined(__APPLE__) && defined(__aarch64__)
    if (ucontext_raw) {
        ucontext_t* uc = static_cast<ucontext_t*>(ucontext_raw);
        if (uc->uc_mcontext) {
            pc = (uint64_t)uc->uc_mcontext->__ss.__pc;
            lr = (uint64_t)uc->uc_mcontext->__ss.__lr;
        }
    }
#endif
    const char* pc_sym = "<unresolved>";
    uint64_t pc_off = 0;
    fl_zero_resolve_sym(pc, &pc_sym, &pc_off);
    // Prefer LR when PC resolves to an absurd offset (s646 freeroll n=21:
    // PC landed in dyld cold path with +0x88cb7198 garbage).
    const char* lr_sym = "<unresolved>";
    uint64_t lr_off = 0;
    if (pc_off > 0x100000ull && lr) {
        fl_zero_resolve_sym(lr, &lr_sym, &lr_off);
        if (lr_off <= 0x100000ull) {
            pc_sym = lr_sym;
            pc_off = lr_off;
            pc = lr;
        }
    }

    int want = g_flz_fault_want.load(std::memory_order_relaxed);
    g_flz_last_fa.store(fa, std::memory_order_relaxed);
    g_flz_last_pc.store(pc, std::memory_order_relaxed);
    g_flz_last_lr.store(lr, std::memory_order_relaxed);
    g_flz_last_n.store(n, std::memory_order_relaxed);
    g_flz_last_in_hdr.store(in_hdr, std::memory_order_relaxed);
    g_flz_last_want.store(want, std::memory_order_relaxed);
    {
        // Truncate into fixed buffer (signal-safe-ish; no alloc).
        size_t i = 0;
        for (; i + 1 < sizeof(g_flz_last_sym) && pc_sym[i]; ++i)
            g_flz_last_sym[i] = pc_sym[i];
        g_flz_last_sym[i] = '\0';
        if (i == 0) {
            g_flz_last_sym[0] = 'n'; g_flz_last_sym[1] = 'o';
            g_flz_last_sym[2] = 'n'; g_flz_last_sym[3] = 'e';
            g_flz_last_sym[4] = '\0';
        }
    }

    // Always push ring (even when line rate-limited). Poller dumps on
    // freelist-shaped to_zero so mid-window n=33..N are recoverable.
    {
        uint64_t wi = g_flz_fault_ring_w.fetch_add(1, std::memory_order_relaxed);
        FlzFaultRingRec& rec = g_flz_fault_ring[wi % (uint64_t)kFlzFaultRing];
        rec.n = n;
        rec.fa = fa;
        rec.pc = pc;
        rec.lr = lr;
        rec.pc_off = pc_off;
        rec.guest_pc = (uint32_t)g_rs64_last_guest_pc;
        rec.in_hdr = in_hdr;
        rec.near_hdr = near_hdr;
        rec.late = late;
        rec.want = want;
        size_t si = 0;
        for (; si + 1 < sizeof(rec.sym) && pc_sym[si]; ++si)
            rec.sym[si] = pc_sym[si];
        rec.sym[si] = '\0';
        if (si == 0) {
            rec.sym[0] = 'n'; rec.sym[1] = 'o';
            rec.sym[2] = 'n'; rec.sym[3] = 'e';
            rec.sym[4] = '\0';
        }
    }

    // s648: s647 freeroll under want==2 dumped BT on EVERY fault (~7.5k
    // faults × ~16 frames ≈ 120k lines / 24 MB after arm_freelist alone).
    // Neighbor thrash (buildModelViewerTextPage on same 16KB page) made
    // full-BT-every-fault toxic — likely elevates recovery silence and
    // prevents freelist to_zero from ever firing. Rate-limit:
    //   line: first 32 any; all in_hdr; all near_hdr (s651); every 256th want==2
    //   BT:   first 16 any; all in_hdr (cap 32); every 256th want==2
    //         (near_hdr does NOT get BT — still toxic if thrash near block)
    // s651 fault_ring retains last 16 even when line is dropped.
    uint64_t hdr_n = g_flz_fault_hdr_n.load(std::memory_order_relaxed);
    int log_line = (n <= 32) || in_hdr || near_hdr ||
                   (want == 2 && (n % 256ull) == 0);
    int log_bt = (n <= 16) || (in_hdr && hdr_n <= 32) ||
                 (want == 2 && (n % 256ull) == 0);
    // Always log late recovers (discriminate s648 att4 race) + rate-limit rest.
    if (log_line || late) {
        fprintf(stderr,
            "[fl-zero-fault] n=%llu in_hdr=%d near_hdr=%d late=%d fa=0x%llx "
            "hdr_host=0x%llx slot=0x%X pc=0x%llx sym=%s+0x%llx lr=0x%llx "
            "guest_pc=0x%08X want=%d\n",
            (unsigned long long)n, in_hdr, near_hdr, late,
            (unsigned long long)fa, (unsigned long long)host, slot,
            (unsigned long long)pc, pc_sym, (unsigned long long)pc_off,
            (unsigned long long)lr, (unsigned)g_rs64_last_guest_pc, want);
    }
    if (log_bt) {
        void* frames[24];
        int bn = backtrace(frames, 24);
        char** syms = backtrace_symbols(frames, bn);
        for (int i = 0; i < bn; ++i) {
            Dl_info dli{};
            const char* sn = nullptr;
            if (dladdr(frames[i], &dli) && dli.dli_sname) sn = dli.dli_sname;
            fprintf(stderr, "[fl-zero-fault]   [%2d] %s%s%s\n", i,
                sn ? sn : "", sn ? " | " : "",
                (syms && syms[i]) ? syms[i] : "?");
        }
        free(syms);
    }
    if (log_line || log_bt) fflush(stderr);
    // Re-arm is NOT done here: re-arming PROT_READ before the faulting store
    // restarts would infinite-loop. The busy re-arm spinner (want==2) and the
    // poller's fallback restore PROT_READ after the store completes. s647:
    // ARM64 hardware single-step via thread_set_state-from-SEGV is REFUTED
    // (nested SIGTRAP inside mach_msg/thread_set_state → CRASH path).
    return true;
}
#else
static bool fl_zero_try_handle_fault(void*, void*) { return false; }
#endif

// s7493 class ER: RT64 writeback liveness. ROGUESQ_S7493_WBLIVE=1. RDP::setColorImage / setDepthImage (lib/rt64 rt64_rdp.cpp)
// call rs64_s7493_img for EVERY image set the RDP stream carries; each writeback [phys, phys+bytes) is looked up against the last
// set of the image that contains phys (same kind: 0 colour, 1 depth; greatest base <= phys within base + 1024 rows of the image
// row bytes). Age in swaps (g_rs64_swap_n) since that set: age0 / age1 / age>=2 / never. First 20 age>=2|never rows are logged,
// plus the first 40 writebacks of the run (seed timing: set age in seconds vs the s7480 free age). Positive control:
// ROGUESQ_S7493_WBLIVE_CTL=<k>: at the k-th writeback the ring entry for that writeback's image is erased, so the same image's
// next writeback (unless the stream re-sets it first) must log `never ... CTL`; reported as ctl_armed / ctl_never.
extern std::atomic<int> g_rs64_swap_n;
namespace {
struct S7493Img { double t; int sw; uint32_t width, siz; uint64_t n; };
std::mutex g_s7493_mu; std::map<uint32_t, S7493Img> g_s7493_img[2];
uint64_t g_s7493_cnt[2][4] = {}, g_s7493_wb = 0, g_s7493_sets[2] = {}; int g_s7493_logged = 0; uint32_t g_s7493_ctl_base = 0xFFFFFFFFu; int g_s7493_ctl_kind = -1;
uint64_t g_s7493_ctl_armed = 0, g_s7493_ctl_never = 0; double g_s7493_t0 = 0, g_s7493_last_sum = 0;
int g_s7493_wlog = 0; std::atomic<uint32_t> g_s7493_next_base{0xFFFFFFFFu}; uint64_t g_s7493_nobase = 0;
uint32_t g_s7493_w[4]; uint32_t g_s7493_nw = 0xFFFFFFFFu;
uint32_t s7493_nwatch() { if (g_s7493_nw == 0xFFFFFFFFu) { g_s7493_nw = 0; if (const char* e = std::getenv("ROGUESQ_S7493_WBLIVE_WATCH")) { const char* q = e;
        while (*q && g_s7493_nw < 4) { char* x; const unsigned long v = std::strtoul(q, &x, 16); if (x == q) break; g_s7493_w[g_s7493_nw++] = (uint32_t)v & 0xFFFFFFu; q = (*x == ',') ? x + 1 : x; if (!*x) break; } } }
    return g_s7493_nw; }
uint32_t s7493_watch(uint32_t i) { return g_s7493_w[i]; }
bool s7493_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7493_WBLIVE"); return e && *e && *e != '0'; }(); return on; }
double s7493_now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
}
// s7495 class ET: the game's fixed DL-chunk pool (tools/apply_s7495_poolwatch.py) vs RDP depth images. ROGUESQ_S7495_POOL=1.
namespace { bool s7495_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7495_POOL"); return e && *e && *e != '0'; }(); return on; }
std::mutex g_s7495_mu; uint32_t g_s7495_lo = 0, g_s7495_hi = 0, g_s7495_cw = 0; int g_s7495_np = 0; uint64_t g_s7495_zsets = 0, g_s7495_live = 0, g_s7495_hist = 0;
std::map<uint32_t, double> g_s7495_z; double g_s7495_t0 = 0; }
// s7496 class EU: every guest-heap block under a new partition (pool rebuild, new colour/depth image extent), walked from the real
// arena chains (upstream_compat.cpp rs64_s7496_overlap). Rows: `[s7496] under kind= lo= hi= hdr= size= fl= ra= age= cls=` where
// cls = container (one used block holds the whole extent), live (used, partial), free. Counts in `[s7496] sum`. ROGUESQ_S7495_POOL=1.
extern "C" int rs64_s7496_overlap(uint32_t, uint32_t, void (*)(uint32_t, uint32_t, uint32_t, uint32_t, double, void*), void*);
extern "C" int rs64_s7496_ctl(uint32_t*);
namespace { uint64_t g_s7496_q = 0, g_s7496_qbad = 0, g_s7496_live = 0, g_s7496_cont = 0, g_s7496_free = 0, g_s7496_freehdr = 0, g_s7496_rows = 0, g_s7496_ctln = 0, g_s7496_ctlok = 0;
void s7496_query(const char* kind, uint32_t lo, uint32_t hi, double t) {
    struct Q { const char* kind; uint32_t lo, hi; double t; int nl, nc, nf; } q{kind, lo, hi, t, 0, 0, 0};
    const int n = rs64_s7496_overlap(lo, hi, [](uint32_t h, uint32_t sz, uint32_t fl, uint32_t ra, double age, void* u) {
        Q* p = (Q*)u; const uint32_t hp = h & 0xFFFFFFu, ep = hp + 0x10u + sz;
        const char* cls = fl == 1u ? "free" : (hp + 0x10u <= p->lo && ep >= p->hi) ? "container" : "live";
        if (fl == 1u) { ++p->nf; ++g_s7496_free; if (hp >= p->lo && hp < p->hi) ++g_s7496_freehdr; } else if (cls[0] == 'c') { ++p->nc; ++g_s7496_cont; } else { ++p->nl; ++g_s7496_live; }
        if (fl != 1u ? ++g_s7496_rows <= 60 : false)
            std::fprintf(stderr, "[s7496] under kind=%s ext=[%06X,%06X) hdr=%06X end=%06X size=%X fl=%X ra=%08X age=%.2f cls=%s t=%.3f\n", p->kind, p->lo, p->hi, hp, ep, sz, fl, ra, age, cls, p->t);
    }, &q);
    ++g_s7496_q; if (n < 0) ++g_s7496_qbad;
    std::fprintf(stderr, "[s7496] q kind=%s ext=[%06X,%06X) walked=%d live=%d container=%d free=%d t=%.3f\n", kind, lo, hi, n, q.nl, q.nc, q.nf, t);
    std::fprintf(stderr, "[s7496] sum q=%llu qbad=%llu live=%llu container=%llu free=%llu freehdr=%llu ctl=%llu/%llu\n", (unsigned long long)g_s7496_q, (unsigned long long)g_s7496_qbad,
                 (unsigned long long)g_s7496_live, (unsigned long long)g_s7496_cont, (unsigned long long)g_s7496_free, (unsigned long long)g_s7496_freehdr, (unsigned long long)g_s7496_ctlok, (unsigned long long)g_s7496_ctln);
} std::set<std::pair<uint32_t, uint32_t>> g_s7496_imgs; }
extern "C" void rs64_s7495_pool(uint32_t base, uint32_t size) {
    if (!s7495_on()) return;
    std::lock_guard<std::mutex> lk(g_s7495_mu); const double now = s7493_now(); if (g_s7495_t0 == 0) g_s7495_t0 = now;
    const uint32_t lo = base & 0xFFFFFFu, hi = lo + (size / 0x108u) * 0x108u; g_s7495_lo = lo; g_s7495_hi = hi; ++g_s7495_np;
    std::fprintf(stderr, "[s7495] pool #%d t=%.3f base=%06X end=%06X size=%X chunks=%u cimg_w=%u zsets=%llu\n", g_s7495_np, now - g_s7495_t0, lo, hi, size,
                 size / 0x108u, g_s7495_cw, (unsigned long long)g_s7495_zsets);
    for (auto& kv : g_s7495_z) if (kv.first >= lo && kv.first < hi) { ++g_s7495_hist;
        std::fprintf(stderr, "[s7495] hist-overlap pool#%d z=%06X (set %.3f s before this rebuild)\n", g_s7495_np, kv.first, now - kv.second); }
    std::fprintf(stderr, "[s7495] sum pools=%d zsets=%llu live=%llu hist=%llu\n", g_s7495_np, (unsigned long long)g_s7495_zsets, (unsigned long long)g_s7495_live, (unsigned long long)g_s7495_hist);
    s7496_query("pool", lo, hi, now - g_s7495_t0);
    { uint32_t cb = 0; const int c = rs64_s7496_ctl(&cb); ++g_s7496_ctln; if (c == 1) ++g_s7496_ctlok;
      std::fprintf(stderr, "[s7496] ctl pool#%d youngest_rec=%08X found_used=%d\n", g_s7495_np, cb, c); }
}
static void rs64_s7495_img(uint32_t kind, uint32_t addr, uint32_t width, uint32_t siz) {
    std::lock_guard<std::mutex> lk(g_s7495_mu); const uint32_t a = addr & 0xFFFFFFu;
    { const uint32_t w = kind == 0 ? width : g_s7495_cw, bpp = siz >= 3 ? 4u : siz == 2 ? 2u : 1u;  /* s7496: new (kind, addr, width) extents */
      if (w && g_s7496_imgs.insert({(kind << 24) | a, w}).second) { const double now = s7493_now(); if (g_s7495_t0 == 0) g_s7495_t0 = now;
          s7496_query(kind == 0 ? "cimg" : "zimg", a, a + w * 480u * bpp, now - g_s7495_t0); } }
    if (kind == 0) { g_s7495_cw = width; return; }
    ++g_s7495_zsets; const bool fresh = g_s7495_z.find(a) == g_s7495_z.end(); const double now = s7493_now(); if (g_s7495_t0 == 0) g_s7495_t0 = now; g_s7495_z[a] = now;
    if (fresh) std::fprintf(stderr, "[s7495] zimg new z=%06X t=%.3f cimg_w=%u pool=[%06X,%06X)%s\n", a, now - g_s7495_t0, g_s7495_cw, g_s7495_lo, g_s7495_hi,
                            (a >= g_s7495_lo && a < g_s7495_hi) ? " LIVE-OVERLAP" : "");
    if (g_s7495_np > 0 && a >= g_s7495_lo && a < g_s7495_hi && ++g_s7495_live <= 20)
        std::fprintf(stderr, "[s7495] live-overlap z=%06X pool#%d [%06X,%06X) t=%.3f\n", a, g_s7495_np, g_s7495_lo, g_s7495_hi, now - g_s7495_t0);
}
static void s7497_img(uint32_t, uint32_t);
static void s7500_set(uint32_t, uint32_t);
static void s7500_cover(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint64_t, int, int);
static void s7500_wb(uint32_t, uint32_t);
static void s7503_set(uint32_t, uint32_t); static void s7503_fill(uint32_t); static void s7503_wb(uint32_t, uint32_t);
extern "C" void rs64_s7503_arm(uint32_t, uint32_t, uint32_t, const char*, int);
extern "C" void rs64_s7493_img(uint32_t kind, uint32_t addr, uint32_t width, uint32_t siz) {
    s7497_img(kind, addr); s7500_set(kind, addr); s7503_set(kind, addr);
    if (s7495_on() && kind <= 1) rs64_s7495_img(kind, addr, width, siz);
    if (!s7493_on() || kind > 1) return;
    std::lock_guard<std::mutex> lk(g_s7493_mu); const double now = s7493_now(); if (g_s7493_t0 == 0) g_s7493_t0 = now;
    if (g_s7493_ctl_kind == (int)kind && (addr & 0xFFFFFFu) == g_s7493_ctl_base) return;  /* control: this image's sets are no longer recorded */
    S7493Img& m = g_s7493_img[kind][addr & 0xFFFFFFu]; m.t = now; m.sw = g_rs64_swap_n.load(std::memory_order_relaxed); m.width = width; m.siz = siz; m.n++;
    g_s7493_sets[kind]++;
}
// s7497 class EV: is depth ever WRITTEN through the game's Z=0 placeholder depth image (SETZIMG 0, s7496)? ROGUESQ_S7497_Z0=1.
// lib/rt64 rt64_rdp.cpp calls rs64_s7497_zdraw for every z-update tri (k=0) / rect (k=1) draw that survives the scissor (the exact
// branch that merges fbPair.drawDepthRect, i.e. what makes RT64 write depth back), and every fill rect (k=2, keyed by COLOUR address:
// the z-clear idiom points the colour image at the depth buffer). Depth writebacks are keyed by their exact base (rs64_s7493_base,
// kind 1) plus any depth/colour writeback whose range touches [0, 0x100000). Positive control, same run, same keyed code: the busiest
// NON-zero depth address must show zupd draws > 0, depth writebacks > 0 and z-clear fills > 0.
namespace { std::mutex g_s7497_mu; std::map<uint32_t, uint64_t> g_s7497_zd[3], g_s7497_wbd; uint64_t g_s7497_wblow = 0, g_s7497_tr = 0;
  uint32_t g_s7497_lastz = 0xFFFFFFFFu; double g_s7497_t0 = 0, g_s7497_last = 0; int g_s7497_log = 0; std::atomic<uint32_t> g_s7497_base{0xFFFFFFFFu};
  bool s7497_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7497_Z0"); return e && *e && *e != '0'; }(); return on; }
  double s7497_now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
  void s7497_sum_locked(double now) {
    uint32_t ca = 0; uint64_t cn = 0; for (auto& kv : g_s7497_zd[0]) if (kv.first != 0 && kv.second > cn) { cn = kv.second; ca = kv.first; }
    auto g = [](std::map<uint32_t, uint64_t>& m, uint32_t a) -> unsigned long long { auto it = m.find(a); return it == m.end() ? 0ull : (unsigned long long)it->second; };
    std::fprintf(stderr, "[s7497] sum t=%.1f z0 tri_zupd=%llu rect_zupd=%llu fill_c0=%llu wb_base0=%llu wb_low=%llu ztrans=%llu ctl z=%06X tri_zupd=%llu rect_zupd=%llu fill_cz=%llu wb=%llu zaddrs=%zu\n",
      now - g_s7497_t0, g(g_s7497_zd[0], 0), g(g_s7497_zd[1], 0), g(g_s7497_zd[2], 0), g(g_s7497_wbd, 0), (unsigned long long)g_s7497_wblow, (unsigned long long)g_s7497_tr,
      ca, (unsigned long long)cn, g(g_s7497_zd[1], ca), g(g_s7497_zd[2], ca), g(g_s7497_wbd, ca), g_s7497_zd[0].size()); }
}
static void s7500_fill(uint32_t);
extern "C" void rs64_s7497_zdraw(uint32_t k, uint32_t zaddr, uint32_t caddr, uint32_t cw, uint32_t cyc) {
  if (k == 2) { s7500_fill(caddr); s7503_fill(caddr); }
  if (!s7497_on() || k > 2) return;
  std::lock_guard<std::mutex> lk(g_s7497_mu); const double now = s7497_now(); if (g_s7497_t0 == 0) g_s7497_t0 = now;
  const uint32_t key = (k == 2 ? caddr : zaddr) & 0xFFFFFFu; g_s7497_zd[k][key]++;
  if (key == 0 && g_s7497_log < 30) { ++g_s7497_log;
    std::fprintf(stderr, "[s7497] z0 %s z=%06X c=%06X cw=%u cyc=%u t=%.3f\n", k == 0 ? "tri_zupd" : k == 1 ? "rect_zupd" : "fill_c0", zaddr, caddr, cw, cyc, now - g_s7497_t0); }
  if (now - g_s7497_last >= 10.0) { g_s7497_last = now; s7497_sum_locked(now); }
}
static void s7497_img(uint32_t kind, uint32_t addr) {
  if (!s7497_on() || kind != 1) return; std::lock_guard<std::mutex> lk(g_s7497_mu); const double now = s7497_now(); if (g_s7497_t0 == 0) g_s7497_t0 = now;
  addr &= 0xFFFFFFu; if (addr == g_s7497_lastz) return; ++g_s7497_tr;
  if (g_s7497_tr <= 40 || addr == 0 || g_s7497_lastz == 0) std::fprintf(stderr, "[s7497] zimg %06X -> %06X t=%.3f\n", g_s7497_lastz, addr, now - g_s7497_t0);
  g_s7497_lastz = addr; }
static void s7497_wb(uint32_t phys, uint32_t bytes, uint32_t kind) {
  const uint32_t b = g_s7497_base.exchange(0xFFFFFFFFu); if (!s7497_on() || !bytes) return;
  std::lock_guard<std::mutex> lk(g_s7497_mu); const double now = s7497_now(); if (g_s7497_t0 == 0) g_s7497_t0 = now;
  if (kind == 1 && b != 0xFFFFFFFFu) g_s7497_wbd[b & 0xFFFFFFu]++;
  if ((phys & 0xFFFFFFu) < 0x100000u) { ++g_s7497_wblow; if (g_s7497_log < 30) { ++g_s7497_log;
    std::fprintf(stderr, "[s7497] wb_low kind=%u phys=%06X bytes=%u base=%06X t=%.3f\n", kind, phys, bytes, b, now - g_s7497_t0); } } }
// s7498 class EW: does the byte range RT64 actually writes back, [phys, phys+bytes), stay inside ONE used guest-heap block (or a
// non-heap region)? ROGUESQ_S7498_EW=1. Per (kind, image base, width) the range [base, end) is re-queried whenever its end grows past
// the largest end already checked (rs64_s7496_overlap chain walk). cls: container (one used block holds the range), partial (a used
// block intersects but none contains it = spill into a neighbour), free (only free blocks), nonheap (no arena block intersects). A
// broken walk (racing guest malloc, n<0) counts qbad and is retried on the next writeback. Control ROGUESQ_S7498_CTL=<n>: the first
// container query at or after the n-th query is re-run with its end extended 0x100 past that container's end; it MUST classify
// non-container (proves the classifier sees a spill one block over).
static void s7499_ex(uint32_t lo, uint32_t hi, uint32_t kind, uint32_t base, uint32_t width);
namespace { std::mutex g_s7498_mu; std::atomic<uint32_t> g_s7498_base{0xFFFFFFFFu}; std::map<uint64_t, uint32_t> g_s7498_max;
  uint64_t g_s7498_q = 0, g_s7498_qbad = 0, g_s7498_n[4] = {0, 0, 0, 0}, g_s7498_wb = 0, g_s7498_nobase = 0; int g_s7498_rows = 0, g_s7498_ctl = -2;
  double g_s7498_t0 = 0, g_s7498_last = 0;
  bool s7498_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7498_EW"); return e && *e && *e != '0'; }(); return on; }
  long s7498_ctl_at() { static const long n = [] { const char* e = std::getenv("ROGUESQ_S7498_CTL"); return e && *e ? std::strtol(e, nullptr, 10) : 0L; }(); return n; }
  struct S7498Q { uint32_t lo, hi; int nc, nl, nf; uint32_t cend, lhdr, lend, lra; };
  int s7498_walk(S7498Q& q) {
    q.nc = q.nl = q.nf = 0; q.cend = q.lhdr = q.lend = q.lra = 0;
    return rs64_s7496_overlap(q.lo, q.hi, [](uint32_t h, uint32_t sz, uint32_t fl, uint32_t ra, double, void* u) {
      S7498Q* p = (S7498Q*)u; const uint32_t hp = h & 0xFFFFFFu, ep = hp + 0x10u + sz;
      if (fl == 1u) ++p->nf;
      else if (hp + 0x10u <= p->lo && ep >= p->hi) { ++p->nc; p->cend = ep; }
      else { if (!p->nl) { p->lhdr = hp; p->lend = ep; p->lra = ra; } ++p->nl; } }, &q); }
  int s7498_ci(const S7498Q& q) { return q.nc ? 0 : q.nl ? 1 : q.nf ? 2 : 3; }
  const char* s7498_cls(int ci) { static const char* k[4] = {"container", "partial", "free", "nonheap"}; return k[ci & 3]; }
  void s7498_sum_locked(double now) {
    std::fprintf(stderr, "[s7498] sum t=%.1f wb=%llu nobase=%llu keys=%zu q=%llu qbad=%llu container=%llu partial=%llu free=%llu nonheap=%llu ctl=%s\n", now - g_s7498_t0,
      (unsigned long long)g_s7498_wb, (unsigned long long)g_s7498_nobase, g_s7498_max.size(), (unsigned long long)g_s7498_q, (unsigned long long)g_s7498_qbad,
      (unsigned long long)g_s7498_n[0], (unsigned long long)g_s7498_n[1], (unsigned long long)g_s7498_n[2], (unsigned long long)g_s7498_n[3],
      g_s7498_ctl == 1 ? "ok" : g_s7498_ctl == 0 ? "FAIL" : g_s7498_ctl == -1 ? "pending" : "unarmed"); }
  void s7498_wb(uint32_t phys, uint32_t bytes, uint32_t kind, uint32_t width, uint32_t rows) {
    const uint32_t b = g_s7498_base.exchange(0xFFFFFFFFu); if (!s7498_on() || !bytes) return;
    std::lock_guard<std::mutex> lk(g_s7498_mu); const double now = s7493_now(); if (g_s7498_t0 == 0) g_s7498_t0 = now;
    if (g_s7498_ctl == -2 && s7498_ctl_at() > 0) g_s7498_ctl = -1;
    ++g_s7498_wb; if (b == 0xFFFFFFFFu) ++g_s7498_nobase;
    const uint32_t lo = phys & 0xFFFFFFu, hi = lo + bytes, base = (b == 0xFFFFFFFFu ? lo : b) & 0xFFFFFFu;
    s7499_ex(lo, hi, kind, base, width);
    const uint64_t key = ((uint64_t)(kind & 0xFu) << 48) | ((uint64_t)base << 16) | (width & 0xFFFFu);
    auto it = g_s7498_max.find(key);
    if (it == g_s7498_max.end() || hi > it->second) {
      S7498Q q{base < lo ? base : lo, hi}; const int n = s7498_walk(q); ++g_s7498_q;
      if (n < 0) ++g_s7498_qbad;
      else { g_s7498_max[key] = hi; const int ci = s7498_ci(q); ++g_s7498_n[ci];
        if ((ci != 0 && ci != 3) || ++g_s7498_rows <= 60)
          std::fprintf(stderr, "[s7498] wb ext=[%06X,%06X) kind=%u base=%06X w=%u rows=%u bytes=%u cls=%s nc=%d nl=%d nf=%d cend=%06X spill_hdr=%06X spill_end=%06X spill_ra=%08X t=%.3f\n",
            q.lo, q.hi, kind, base, width, rows, bytes, s7498_cls(ci), q.nc, q.nl, q.nf, q.cend, q.lhdr, q.lend, q.lra, now - g_s7498_t0);
        if (g_s7498_ctl == -1 && ci == 0 && (long)g_s7498_q >= s7498_ctl_at()) {
          S7498Q c{q.lo, q.cend + 0x100u}; const int m = s7498_walk(c);
          if (m >= 0) { const int cc = s7498_ci(c); g_s7498_ctl = cc != 0 ? 1 : 0;
            std::fprintf(stderr, "[s7498] ctl q#%llu ext=[%06X,%06X) container_end=%06X -> cls=%s (%s)\n", (unsigned long long)g_s7498_q, c.lo, c.hi, q.cend, s7498_cls(cc), g_s7498_ctl ? "ok" : "FAIL"); } } } }
    if (now - g_s7498_last >= 10.0) { g_s7498_last = now; s7498_sum_locked(now); } }
}
// s7499 class EX: cross-image overlap. Does the range one RT64 writeback really writes, [phys, phys+bytes) of image A (kind, base,
// width; base from rs64_s7493_base), cover bytes of a DIFFERENT image B the RDP stream has set (g_s7493_img, both kinds; needs
// ROGUESQ_S7493_WBLIVE=1)? ROGUESQ_S7499_EX=1. B's extent = the largest range B's own writebacks have covered (wb), else its first row
// estimate base + width*bpp*240 (est). Classes per (A, B) pair, counted once per pair and swap-age bucket: same (B.base == A.base: the
// colour==depth z-clear idiom), live (B set this swap or the previous one), stale (B last set >= 2 swaps ago), est (B never written
// back; estimated extent only). Rows `[s7499] x` (first 60 pairs), `[s7499] sum` every 10 s. Positive control ROGUESQ_S7499_CTL=<n>:
// at the n-th writeback a fake image (kind 2) is registered at that writeback's phys + bytes/2 (8-aligned) with A's width, set "now";
// A's next writebacks MUST count it as ctl (kept apart from live).
namespace { std::mutex g_s7499_mu; std::map<uint64_t, uint32_t> g_s7499_end; std::set<uint64_t> g_s7499_pairs;
  uint64_t g_s7499_wb = 0, g_s7499_n[5] = {0, 0, 0, 0, 0}, g_s7499_imgs = 0; int g_s7499_rows = 0; double g_s7499_t0 = 0, g_s7499_last = 0;
  uint32_t g_s7499_cb = 0xFFFFFFFFu, g_s7499_cw = 0; int g_s7499_csw = 0; uint64_t g_s7499_ctlhit = 0; int g_s7499_ctl = -2;
  bool s7499_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7499_EX"); return e && *e && *e != '0'; }(); return on; }
  long s7499_ctl_at() { static const long n = [] { const char* e = std::getenv("ROGUESQ_S7499_CTL"); return e && *e ? std::strtol(e, nullptr, 10) : 0L; }(); return n; }
  const char* s7499_cls(int c) { static const char* k[5] = {"same", "live", "stale", "est", "ctl"}; return k[c % 5]; }
  void s7499_sum(double now) {
    std::fprintf(stderr, "[s7499] sum t=%.1f wb=%llu imgs=%llu pairs=%zu same=%llu live=%llu stale=%llu est=%llu ctl=%llu ctlhit=%llu ctlst=%s\n", now - g_s7499_t0,
      (unsigned long long)g_s7499_wb, (unsigned long long)g_s7499_imgs, g_s7499_pairs.size(), (unsigned long long)g_s7499_n[0], (unsigned long long)g_s7499_n[1],
      (unsigned long long)g_s7499_n[2], (unsigned long long)g_s7499_n[3], (unsigned long long)g_s7499_n[4], (unsigned long long)g_s7499_ctlhit,
      g_s7499_ctl == 1 ? "ok" : g_s7499_ctl == -1 ? "pending" : g_s7499_ctl == 0 ? "FAIL" : "unarmed"); }
}
static void s7499_ex(uint32_t lo, uint32_t hi, uint32_t kind, uint32_t base, uint32_t width) {
  if (!s7499_on() || kind > 1 || hi <= lo) return;
  std::lock_guard<std::mutex> l1(g_s7493_mu); std::lock_guard<std::mutex> l2(g_s7499_mu);
  const double now = s7493_now(); if (g_s7499_t0 == 0) g_s7499_t0 = now; const int sw = g_rs64_swap_n.load(std::memory_order_relaxed);
  const uint64_t k = ++g_s7499_wb; if (g_s7499_ctl == -2 && s7499_ctl_at() > 0) g_s7499_ctl = -1;
  s7500_wb(kind, base);
  const uint64_t ak = ((uint64_t)kind << 32) | base; uint32_t& ae = g_s7499_end[ak]; if (hi > ae) ae = hi;
  auto test = [&](uint32_t bk, uint32_t bb, uint32_t bw, uint32_t siz, int bsw) {
    if (bk == kind && bb == base) return;
    const auto ei = g_s7499_end.find(((uint64_t)bk << 32) | bb); const bool haswb = ei != g_s7499_end.end();
    const uint32_t bpp = siz >= 3 ? 4u : siz == 2 ? 2u : 1u, be = haswb ? ei->second : bb + bw * bpp * 240u;
    if (!(bb < hi && be > lo)) return;
    const int age = sw - bsw; const int c = bk == 2 ? 4 : bb == base ? 0 : !haswb ? 3 : age <= 1 ? 1 : 2;
    if (c == 4) ++g_s7499_ctlhit;
    if (c == 2 || c == 3) s7500_cover(bk, bb, be, kind, base, width, k, sw, bsw);
    const uint64_t pk = ((uint64_t)kind << 62) | ((uint64_t)bk << 60) | ((uint64_t)(base & 0xFFFFFFu) << 32) | ((uint64_t)(bb & 0xFFFFFFu) << 8) | (uint64_t)(c << 1);
    if (!g_s7499_pairs.insert(pk).second) return;
    ++g_s7499_n[c]; if (c == 4 && g_s7499_ctl == -1) g_s7499_ctl = 1;
    if (++g_s7499_rows <= 60 || c == 1)
      std::fprintf(stderr, "[s7499] x cls=%s A kind=%u base=%06X w=%u wb=[%06X,%06X) B kind=%u base=%06X w=%u siz=%u ext=[%06X,%06X)%s age=%d wb#%llu t=%.3f\n", s7499_cls(c),
        kind, base, width, lo, hi, bk, bb, bw, siz, bb, be, haswb ? "" : " est", age, (unsigned long long)k, now - g_s7499_t0); };
  for (uint32_t bk = 0; bk < 2; ++bk) for (auto& kv : g_s7493_img[bk]) test(bk, kv.first, kv.second.width, kv.second.siz, kv.second.sw);
  if (g_s7499_cb != 0xFFFFFFFFu) test(2, g_s7499_cb, g_s7499_cw, 2, g_s7499_csw);
  g_s7499_imgs = g_s7493_img[0].size() + g_s7493_img[1].size();
  if (g_s7499_ctl == -1 && g_s7499_cb == 0xFFFFFFFFu && (long)k >= s7499_ctl_at() && hi - lo >= 16) {
    g_s7499_cb = (lo + (hi - lo) / 2) & ~7u; g_s7499_cw = width; g_s7499_csw = sw;
    std::fprintf(stderr, "[s7499] ctl armed wb#%llu A kind=%u base=%06X fake=%06X\n", (unsigned long long)k, kind, base, g_s7499_cb); }
  if (now - g_s7499_last >= 10.0) { g_s7499_last = now; s7499_sum(now); } }
// s7503 class FA: are the freed-fb-RAM uploads (EZ cls=cpu, writer = allocator metadata or packTlutEntriesRgba5551) into an image
// that is LIVE? ROGUESQ_S7503_FA=1 (needs S7501_EZ + S7500_EY for the draw/tex/up hooks). rs64_s7501_up arms a watch on the fb when
// the newest window writer is rs_malloc* / rs_free / coalesceFreeHeap* / buildHeapFreeList / packTlut*; then every later event on that
// fb is logged in order with its swap offset: set (SETCIMG/SETZIMG exact base), fill, draw / zread / zupd (exact base), tex (load range
// overlaps), up / upP (RT64 checkRAM upload, draw / present path), wb (RT64 writeback, exact base), vi (osViSwapBuffer target or
// committed VI origin inside the fb within 3 swaps). Verdict per watch (skipping draw-path re-uploads): fill = fill first, or set then
// fill; live = draw / zread / zupd / tex / upP / vi first, set then a non-fill, or the arming upload itself on the present path;
// rewrite = wb first; dead = nothing within 5 s and 3 swaps. Controls (same matcher, same run, t >= 30 s, one each): ctlC = arm on
// the colour image last set (must see an event), ctlV = arm on the fb holding the committed VI origin (must see vi).
namespace {
struct S7503W { uint32_t a, bytes, w; std::string fn; double t; int sw, ctl, done; bool present; std::string seq; int nev; char verdict[12]; };
std::mutex g_s7503_mu; std::vector<S7503W> g_s7503; std::atomic<int> g_s7503_act{0};
uint64_t g_s7503_v[5] = {}; double g_s7503_t0 = 0, g_s7503_last = 0; int g_s7503_ctlc = -2, g_s7503_ctlv = -2, g_s7503_rows = 0;
uint32_t g_s7503_lastc = 0xFFFFFFFFu; std::map<std::string, uint64_t> g_s7503_livefn;
bool s7503_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7503_FA"); return e && *e && *e != '0'; }(); return on; }
double s7503_now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
const char* s7503_vn(int i) { static const char* k[5] = {"fill", "live", "rewrite", "dead", "pend"}; return k[i]; }
void s7503_sum_locked(double now) {
  uint64_t pend = 0; for (auto& w : g_s7503) if (!w.done && !w.ctl) ++pend;
  std::string lf; for (auto& kv : g_s7503_livefn) { char t[96]; std::snprintf(t, sizeof t, "%s%s:%llu", lf.empty() ? "" : ",", kv.first.c_str(), (unsigned long long)kv.second); lf += t; }
  auto cs = [](int c) { return c == 1 ? "ok" : c == 0 ? "FAIL" : c == -1 ? "pending" : "unarmed"; };
  std::fprintf(stderr, "[s7503] sum t=%.1f armed=%llu fill=%llu live=%llu rewrite=%llu dead=%llu pend=%llu livefn=%s ctlC=%s ctlV=%s\n", now - g_s7503_t0,
    (unsigned long long)(g_s7503_v[0] + g_s7503_v[1] + g_s7503_v[2] + g_s7503_v[3] + pend), (unsigned long long)g_s7503_v[0], (unsigned long long)g_s7503_v[1],
    (unsigned long long)g_s7503_v[2], (unsigned long long)g_s7503_v[3], (unsigned long long)pend, lf.empty() ? "none" : lf.c_str(), cs(g_s7503_ctlc), cs(g_s7503_ctlv)); }
void s7503_finish_locked(S7503W& w, int v, double now) {
  if (w.done) return; w.done = 1; g_s7503_act.fetch_sub(1); std::snprintf(w.verdict, sizeof w.verdict, "%s", s7503_vn(v));
  if (w.ctl == 1) g_s7503_ctlc = (v != 3) ? 1 : 0;
  else if (w.ctl == 2) g_s7503_ctlv = (w.seq.find("vi@") != std::string::npos) ? 1 : 0;
  else { ++g_s7503_v[v]; if (v == 1) ++g_s7503_livefn[w.fn]; }
  if (++g_s7503_rows <= 300 || w.ctl)
    std::fprintf(stderr, "[s7503] verdict=%s%s fb=%06X w=%u bytes=%u fn=%s armpath=%s seq=%s t_arm=%.3f t=%.3f\n", w.verdict, w.ctl == 1 ? " CTL-C" : w.ctl == 2 ? " CTL-V" : "",
      w.a, w.w, w.bytes, w.fn.c_str(), w.present ? "present" : "draw", w.seq.empty() ? "-" : w.seq.c_str(), w.t - g_s7503_t0, now - g_s7503_t0); }
void s7503_decide_locked(S7503W& w, double now, bool expire) {
  /* tokens "cls@sw"; skip draw-path re-uploads; decide on the first meaningful one (two after a set) */
  std::vector<std::string> k; size_t p = 0; while (p < w.seq.size()) { size_t q = w.seq.find(',', p); std::string t = w.seq.substr(p, q == std::string::npos ? std::string::npos : q - p);
    t = t.substr(0, t.find('@')); if (t != "up" && t != "vin") k.push_back(t); if (q == std::string::npos) break; p = q + 1; }
  if (w.present && !w.ctl) { s7503_finish_locked(w, 1, now); return; }
  if (w.ctl == 2) { if (w.seq.find("vi@") != std::string::npos || expire) s7503_finish_locked(w, w.seq.find("vi@") != std::string::npos ? 1 : 3, now); return; }
  if (k.empty()) { if (expire) s7503_finish_locked(w, 3, now); return; }
  const std::string& f = k[0];
  if (f == "fill") s7503_finish_locked(w, 0, now);
  else if (f == "wb") s7503_finish_locked(w, 2, now);
  else if (f == "set") { if (k.size() >= 2) s7503_finish_locked(w, k[1] == "fill" ? 0 : k[1] == "wb" ? 2 : 1, now); else if (expire) s7503_finish_locked(w, 3, now); }
  else s7503_finish_locked(w, 1, now); }
void s7503_ev_locked(S7503W& w, const char* c, double now) {
  if (w.done || w.nev >= 12) return; ++w.nev; char t[40]; std::snprintf(t, sizeof t, "%s%s@%d", w.seq.empty() ? "" : ",", c, g_rs64_swap_n.load(std::memory_order_relaxed) - w.sw); w.seq += t;
  s7503_decide_locked(w, now, false); }
void s7503_arm_locked(uint32_t a, uint32_t bytes, uint32_t width, const char* fn, bool present, int ctl, double now) {
  for (auto& w : g_s7503) if (!w.done && w.a == a && w.ctl == ctl) return;  /* one open watch per fb */
  if (g_s7503.size() >= 4000) return;
  S7503W w{a, bytes, width, fn ? fn : "-", now, g_rs64_swap_n.load(std::memory_order_relaxed), ctl, 0, present, {}, 0, {}}; g_s7503.push_back(w); g_s7503_act.fetch_add(1);
  if (g_s7503_rows < 300 || ctl) std::fprintf(stderr, "[s7503] arm%s fb=%06X w=%u bytes=%u fn=%s path=%s vi=%06X sw=%d t=%.3f\n", ctl == 1 ? " CTL-C" : ctl == 2 ? " CTL-V" : "",
    a, width, bytes, w.fn.c_str(), present ? "present" : "draw", rs64_vi_committed_origin() & 0xFFFFFFu, w.sw, now - g_s7503_t0);
  if (present && !ctl) s7503_decide_locked(g_s7503.back(), now, false); }
template <class F> void s7503_each(F f) { if (g_s7503_act.load(std::memory_order_relaxed) <= 0) return; std::lock_guard<std::mutex> lk(g_s7503_mu); const double now = s7503_now();
  for (auto& w : g_s7503) if (!w.done) f(w, now); }
}
// s7504 class FB: is the allocator header that RT64 uploads on the present path (s7503 shape 1) inside the VI scanout window, and
// what does it look like against the frame around it? ROGUESQ_S7504_FB=1 (+ROGUESQ_S7504_DIR=<dir> for PPMs). At the upload, guest RAM
// == RT64's native copy except the uploaded words (s7501 diffpx), so RAM over the VI window is the presented image. Per call: the writer
// range words, VI regs (origin/width/h,v start/x,y scale) -> visible cols x rows, header (x,y) from the VI origin, inwin, the header
// pixels vs the 3x3-ring mean of the 16 pixels around them, frame nz per mille / mean luma / distinct colours, and a PPM of the window.
// tag=ctl: the same dump of the committed VI fb every 5 s from t=35 s, 6 tries (s7504 run 1: the single t=35 try hit a black
// pre-flight frame both arms); positive control = any try shows content.
static void s7504_fb(const char* tag, uint32_t fb, uint32_t width, uint32_t lo, uint32_t hi, double t) {
  static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7504_FB"); return e && *e && *e != '0'; }();
  static int left = 8, cleft = 6; int& bud = (tag[0] == 'c') ? cleft : left; if (!on || bud <= 0) return; uint8_t* rd = (uint8_t*)g_recomp_rdram_for_wp_raw; if (!rd) return; --bud;
  const auto* vi = ultramodern::renderer::get_vi_regs();
  const uint32_t org = vi->VI_ORIGIN_REG & 0xFFFFFFu, vw = vi->VI_WIDTH_REG & 0xFFFu, hs = vi->VI_H_START_REG, vs = vi->VI_V_START_REG;
  const uint32_t xs = vi->VI_X_SCALE_REG & 0xFFFu, ys = vi->VI_Y_SCALE_REG & 0xFFFu, st = vi->VI_STATUS_REG;
  const uint32_t h0 = (hs >> 16) & 0x3FFu, h1 = hs & 0x3FFu, v0 = (vs >> 16) & 0x3FFu, v1 = vs & 0x3FFu;
  const uint32_t cols = (h1 > h0) ? (h1 - h0) * xs / 1024u : 0u, rows = (v1 > v0) ? ((v1 - v0) / 2u) * ys / 1024u : 0u;
  auto px = [&](uint32_t a) -> uint16_t { a &= 0xFFFFFEu; return (a + 2 <= 0x1000000u) ? *(uint16_t*)(rd + (a ^ 2u)) : 0; };
  auto lum = [](uint16_t c) { return (double)(((c >> 11) & 31) * 299 + ((c >> 6) & 31) * 587 + ((c >> 1) & 31) * 114) / (31.0 * 1000.0); };
  const uint32_t w0 = (lo & 3u) == 0 ? *(uint32_t*)(rd + (lo & 0xFFFFFCu)) : 0, w1 = *(uint32_t*)(rd + ((lo + 4) & 0xFFFFFCu));
  const uint32_t stride = vw ? vw * 2u : 1u; int hx = -1, hy = -1; bool inwin = false;
  if (lo >= org && vw) { hy = (int)((lo - org) / stride); hx = (int)(((lo - org) % stride) / 2u); inwin = (uint32_t)hy < rows && (uint32_t)hx < std::min(cols, vw); }
  double ring = 0; int nr = 0; uint16_t hp[4] = {};
  for (int k = 0; k < 4; ++k) hp[k] = px(lo + 2u * k);
  if (hy >= 0) for (int dy = -2; dy <= 2; ++dy) for (int dx = -2; dx <= 5; ++dx) { if (dy == 0 && dx >= 0 && dx < 4) continue; const int y = hy + dy, x = hx + dx;
    if (y < 0 || x < 0 || (uint32_t)x >= vw) continue; ring += lum(px(org + (uint32_t)y * stride + 2u * (uint32_t)x)); ++nr; }
  uint64_t nz = 0, n = 0; double ls = 0; std::set<uint16_t> col; std::string path = "-";
  const uint32_t R = std::min<uint32_t>(rows, 720), C = std::min<uint32_t>(std::min(cols, vw), 1600);
  std::vector<uint8_t> img; img.reserve((size_t)R * C * 3);
  for (uint32_t y = 0; y < R; ++y) for (uint32_t x = 0; x < C; ++x) { const uint16_t c = px(org + y * stride + 2u * x); ++n; nz += c != 0; ls += lum(c);
    if (col.size() < 4096) col.insert(c); img.push_back((uint8_t)(((c >> 11) & 31) * 255 / 31)); img.push_back((uint8_t)(((c >> 6) & 31) * 255 / 31)); img.push_back((uint8_t)(((c >> 1) & 31) * 255 / 31)); }
  if (const char* d = std::getenv("ROGUESQ_S7504_DIR"); d && *d && R && C) { char fp[512]; std::snprintf(fp, sizeof fp, "%s/s7504_%s_%06X_t%.0f.ppm", d, tag, fb, t);
    if (FILE* f = std::fopen(fp, "wb")) { std::fprintf(f, "P6\n%u %u\n255\n", C, R); std::fwrite(img.data(), 1, img.size(), f); std::fclose(f); path = fp; } }
  std::fprintf(stderr, "[s7504] fb tag=%s fb=%06X w=%u wr=[%06X,%06X) words=%08X,%08X vi_org=%06X vi_w=%u h=%u-%u v=%u-%u xs=%u ys=%u st=%08X cols=%u rows=%u"
    " hx=%d hy=%d inwin=%d hpx=%04X,%04X,%04X,%04X hlum=%.3f,%.3f,%.3f,%.3f ring=%.3f nr=%d nz_pm=%llu meanlum=%.3f ncol=%zu ppm=%s t=%.3f\n",
    tag, fb, width, lo, hi, w0, w1, org, vw, h0, h1, v0, v1, xs, ys, st, cols, rows, hx, hy, inwin ? 1 : 0, hp[0], hp[1], hp[2], hp[3],
    lum(hp[0]), lum(hp[1]), lum(hp[2]), lum(hp[3]), nr ? ring / nr : 0.0, nr, (unsigned long long)(n ? nz * 1000 / n : 0), n ? ls / n : 0.0, col.size(), path.c_str(), t); }
extern "C" void rs64_s7503_arm(uint32_t a, uint32_t bytes, uint32_t width, const char* fn, int present) {
  if (!s7503_on() || !fn) return;
  if (!(std::strstr(fn, "rs_malloc") || std::strstr(fn, "rs_free") || std::strstr(fn, "coalesceFreeHeap") || std::strstr(fn, "buildHeapFreeList") || std::strstr(fn, "packTlut"))) return;
  std::lock_guard<std::mutex> lk(g_s7503_mu); const double now = s7503_now(); if (g_s7503_t0 == 0) g_s7503_t0 = now; s7503_arm_locked(a & 0xFFFFFFu, bytes, width, fn, present != 0, 0, now); }
static void s7503_set(uint32_t kind, uint32_t addr) {
  if (!s7503_on()) return; addr &= 0xFFFFFFu; if (kind == 0) { std::lock_guard<std::mutex> lk(g_s7503_mu); g_s7503_lastc = addr; }
  s7503_each([&](S7503W& w, double now) { if (w.a == addr && kind <= 1) s7503_ev_locked(w, "set", now); }); }
static void s7503_fill(uint32_t c) { if (!s7503_on()) return; c &= 0xFFFFFFu; s7503_each([&](S7503W& w, double now) { if (w.a == c) s7503_ev_locked(w, "fill", now); }); }
static void s7503_draw(uint32_t c, uint32_t z, uint32_t f) { if (!s7503_on()) return; c &= 0xFFFFFFu; z &= 0xFFFFFFu;
  s7503_each([&](S7503W& w, double now) { if (w.a == c) s7503_ev_locked(w, "draw", now); else if ((f & 3u) && w.a == z) s7503_ev_locked(w, (f & 1u) ? "zread" : "zupd", now); }); }
static void s7503_tex(uint32_t lo, uint32_t hi) { if (!s7503_on()) return; lo &= 0xFFFFFFu; hi &= 0xFFFFFFu;
  s7503_each([&](S7503W& w, double now) { if (lo < w.a + w.bytes && hi > w.a) s7503_ev_locked(w, "tex", now); }); }
static void s7503_up(uint32_t a, int fl) { if (!s7503_on()) return; a &= 0xFFFFFFu; s7503_each([&](S7503W& w, double now) { if (w.a == a) s7503_ev_locked(w, (fl & 2) ? "upP" : "up", now); }); }
static void s7503_wb(uint32_t kind, uint32_t base) { if (!s7503_on() || kind > 1) return; base &= 0xFFFFFFu; s7503_each([&](S7503W& w, double now) { if (w.a == base) s7503_ev_locked(w, "wb", now); }); }
// s7505 class FC: over a whole run, how often does ANY live heap header (rs_malloc chain, s7472 layout) sit on a SCANNED pixel of the
// committed VI framebuffer? Generalises FB (which only looked at upload-armed allocator writes). Per swap (rs64_s7503_swap): VI regs ->
// origin, stride (VI_WIDTH x bpp from VI_STATUS type), visible cols x rows (s7504 rule: x < min(cols, vw), y < rows; the odd fb rows of a
// field-stride VI fall outside cols); rs64_s7496_overlap walks every arena chain over [origin, origin + rows*stride) and each 16 B header
// whose first pixel is in-window is a hit. Episodes = consecutive swaps with the same header in-window; per episode one row with the
// frame mean luma (subsampled), header pixel luma vs a 2-row ring, fl, t. ROGUESQ_S7505_FC=1 (needs S7503_FA, i.e. the FB recipe).
// Controls: synth = the classifier on origin + 40 rows (must be in-window every swap with rows > 40); ctl = every 30th swap the SAME
// walk + classifier on a window of the same geometry placed at the first arena head (real headers there, must hit > 0).
struct S7505E { uint32_t hdr, fl, sz; int x, y, first, last, shown; double t0, ml, hl, ring; bool open; };
static void s7505_fc(int n, double now) {
  static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7505_FC"); return e && *e && *e != '0'; }(); if (!on) return;
  uint8_t* rd = (uint8_t*)g_recomp_rdram_for_wp_raw; if (!rd) return;
  static std::map<uint32_t, S7505E> eps; static uint64_t swaps = 0, walked = 0, bad = 0, hits = 0, neps = 0, lit = 0, lng = 0, synth = 0, synth_n = 0,
    ctl_sw = 0, ctl_hit = 0, ctl_bad = 0, rows_out = 0, novi = 0; static double last = 0, maxml = 0;
  const auto* vi = ultramodern::renderer::get_vi_regs();
  const uint32_t org = rs64_vi_committed_origin() & 0xFFFFFFu, vw = vi->VI_WIDTH_REG & 0xFFFu, hs = vi->VI_H_START_REG, vs = vi->VI_V_START_REG;
  const uint32_t xs = vi->VI_X_SCALE_REG & 0xFFFu, ys = vi->VI_Y_SCALE_REG & 0xFFFu, st = vi->VI_STATUS_REG, bpp = ((st & 3u) == 3u) ? 4u : 2u;
  const uint32_t h0 = (hs >> 16) & 0x3FFu, h1 = hs & 0x3FFu, v0 = (vs >> 16) & 0x3FFu, v1 = vs & 0x3FFu;
  const uint32_t cols = (h1 > h0) ? (h1 - h0) * xs / 1024u : 0u, rows = (v1 > v0) ? ((v1 - v0) / 2u) * ys / 1024u : 0u, stride = vw * bpp;
  auto t = now - g_s7503_t0;
  auto flush = [&](bool all) {
    for (auto it = eps.begin(); it != eps.end();) { S7505E& e = it->second;
      if (all || e.last < n) { ++neps; const bool L = e.ml > 0.05, G = e.shown > 2; lit += L; lng += G;
        if (rows_out < 300) { ++rows_out; std::fprintf(stderr, "[s7505] ep hdr=%06X fl=%u sz=%X x=%d y=%d shown=%d sw=%d-%d t=%.3f ml=%.3f hlum=%.3f ring=%.3f lit=%d long=%d\n",
          e.hdr, e.fl, e.sz, e.x, e.y, e.shown, e.first, e.last, e.t0, e.ml, e.hl, e.ring, L ? 1 : 0, G ? 1 : 0); }
        it = eps.erase(it); } else ++it; } };
  auto sum = [&] { std::fprintf(stderr, "[s7505] fc sum t=%.1f swaps=%llu novi=%llu walked=%llu bad=%llu hits=%llu eps=%llu lit=%llu long=%llu synth=%llu/%llu ctl=%llu/%llu ctlbad=%llu maxml=%.3f\n", t,
      (unsigned long long)swaps, (unsigned long long)novi, (unsigned long long)walked, (unsigned long long)bad, (unsigned long long)hits, (unsigned long long)neps,
      (unsigned long long)lit, (unsigned long long)lng, (unsigned long long)synth, (unsigned long long)synth_n, (unsigned long long)ctl_hit, (unsigned long long)ctl_sw,
      (unsigned long long)ctl_bad, maxml); };
  ++swaps;
  if (!org || !vw || !rows || !cols) { ++novi; flush(false); if (now - last >= 10.0) { last = now; sum(); } return; }
  const uint32_t vc = std::min(cols, vw);
  auto inwin = [&](uint32_t base, uint32_t a, int& x, int& y) { if (a < base) return false; y = (int)((a - base) / stride); x = (int)(((a - base) % stride) / bpp);
    return (uint32_t)y < rows && (uint32_t)x < vc; };
  auto lum = [&](uint32_t a) -> double { a &= 0xFFFFFCu; if (a + 4 > 0x1000000u) return 0;
    if (bpp == 2) { const uint16_t c = *(uint16_t*)(rd + ((a & ~1u) ^ 2u)); return (((c >> 11) & 31) * 299 + ((c >> 6) & 31) * 587 + ((c >> 1) & 31) * 114) / (31.0 * 1000.0); }
    const uint32_t c = *(uint32_t*)(rd + a); return (((c >> 24) & 255) * 299 + ((c >> 16) & 255) * 587 + ((c >> 8) & 255) * 114) / (255.0 * 1000.0); };
  { int x, y; ++synth_n; synth += (rows > 40 && inwin(org, org + 40u * stride, x, y)) ? 1 : 0; }
  struct Ctx { std::vector<std::array<uint32_t, 3>> h; } c;
  auto cb = [](uint32_t h, uint32_t sz, uint32_t fl, uint32_t, double, void* u) { ((Ctx*)u)->h.push_back({h & 0xFFFFFFu, sz, fl}); };
  const int nv = rs64_s7496_overlap(org, org + rows * stride, cb, &c);
  if (nv < 0) ++bad; else { walked += (uint64_t)nv; double ml = -1;
    for (auto& h : c.h) { int x, y; if (!inwin(org, h[0], x, y)) continue; ++hits;
      auto it = eps.find(h[0]);
      if (it != eps.end() && it->second.last == n - 1) { it->second.last = n; ++it->second.shown; continue; }
      if (it != eps.end()) { flush(false); }
      if (ml < 0) { double s = 0; uint64_t k = 0; for (uint32_t yy = 0; yy < rows; yy += 4) for (uint32_t xx = 0; xx < vc; xx += 4) { s += lum(org + yy * stride + xx * bpp); ++k; } ml = k ? s / k : 0; maxml = std::max(maxml, ml); }
      double hl = 0; for (uint32_t k = 0; k < 16; k += bpp) hl = std::max(hl, lum(h[0] + k));
      double rg = 0; int nr = 0; for (int dy = -2; dy <= 2; dy += 4) { const int yy = y + dy; if (yy < 0 || (uint32_t)yy >= rows) continue;
        for (int dx = 0; dx < (int)(16 / bpp); ++dx) { const int xx = x + dx; if ((uint32_t)xx >= vc) continue; rg += lum(org + (uint32_t)yy * stride + (uint32_t)xx * bpp); ++nr; } }
      eps[h[0]] = S7505E{h[0], h[2], h[1], x, y, n, n, 1, t, ml, hl, nr ? rg / nr : 0.0, true}; } }
  flush(false);
  if (swaps % 30 == 0) { static const uint32_t heads[3] = {0x8010FEFCu, 0x8010FF00u, 0x8010FF18u}; uint32_t h0a = 0;
    for (uint32_t hd : heads) { const uint32_t v = *(uint32_t*)(rd + (hd & 0xFFFFFCu)); if (v >= 0x80000000u && v < rs64_ram_top) { h0a = v & 0xFFFFFFu; break; } }
    if (h0a) { ++ctl_sw; Ctx cc; const int m = rs64_s7496_overlap(h0a, h0a + rows * stride, cb, &cc); int got = 0;
      if (m < 0) ++ctl_bad; else for (auto& h : cc.h) { int x, y; if (inwin(h0a, h[0], x, y)) { got = 1; break; } } ctl_hit += got; } }
  if (now - last >= 10.0) { last = now; sum(); } }
extern "C" void rs64_s7503_swap(int n, uint32_t req) {
  if (!s7503_on()) return; std::lock_guard<std::mutex> lk(g_s7503_mu); const double now = s7503_now(); if (g_s7503_t0 == 0) g_s7503_t0 = now;
  const uint32_t vo = rs64_vi_committed_origin() & 0xFFFFFFu; req &= 0xFFFFFFu;
  for (auto& w : g_s7503) { if (w.done) continue; const int ds = n - w.sw;
    /* vi = origin / swap target within 16 rows of the fb base (RT64 presents the fb at origin - row offset); a hit deeper inside the
       extent is another fb nested in a stale record (run 1: VI 67CF00 = live 67CA00 inside stale 650E00) -> "vin", not live */
    const uint32_t near = std::max<uint32_t>(w.w, 320u) * 4u * 16u;
    if (ds <= 3) { const bool vn = (vo >= w.a && vo - w.a < near) || (req >= w.a && req - w.a < near);
      const bool vi = !vn && ((vo >= w.a && vo < w.a + w.bytes) || (req >= w.a && req < w.a + w.bytes));
      if (vn && w.seq.find("vi@") == std::string::npos) s7503_ev_locked(w, "vi", now);
      else if (vi && w.seq.find("vin@") == std::string::npos && w.nev < 12) { ++w.nev; char t[40]; std::snprintf(t, sizeof t, "%svin@%d", w.seq.empty() ? "" : ",", ds); w.seq += t; } }
    if (!w.done && now - w.t >= 5.0 && ds >= 3) s7503_decide_locked(w, now, true); }
  if (now - g_s7503_t0 >= 30.0) {
    if (g_s7503_ctlc == -2 && g_s7503_lastc != 0xFFFFFFFFu) { g_s7503_ctlc = -1; s7503_arm_locked(g_s7503_lastc, 0x100u, 0, "ctl_cimg", false, 1, now); }
    if (g_s7503_ctlv == -2 && vo) { g_s7503_ctlv = -1; s7503_arm_locked(vo, 0x100u, 0, "ctl_vi", false, 2, now); } }
  if (now - g_s7503_last >= 10.0) { g_s7503_last = now; s7503_sum_locked(now); }
  { static double ctl_t = 35.0; if (now - g_s7503_t0 >= ctl_t && vo) { ctl_t += 5.0;  /* s7504 control: live VI fb, per swap */
      s7504_fb("ctl", vo, 0, vo + 40u * 1600u, vo + 40u * 1600u + 4u, now - g_s7503_t0); } }
  s7505_fc(n, now);
  if (g_s7503.size() > 3000) { std::vector<S7503W> keep; for (auto& w : g_s7503) if (!w.done) keep.push_back(w); g_s7503.swap(keep); } }
// s7500 class EY: resurrection of a stale-covered image. s7499_ex scores pairs (A writeback covers image B, B last set >= 2 swaps
// earlier or never written back) as dead; EY asks whether such a B is ever SET again, and what touches it first after that.
// ROGUESQ_S7500_EY=1 (needs S7493_WBLIVE + S7499_EX). Per covered B (kind, base): cover = latest A + wb# + swap. When the RDP stream
// sets B again: `[s7500] reset` (gap in swaps since the cover and since B's own previous set), then the FIRST event on B classifies
// it: fill (fill rect with colour image == B: clear / z-clear idiom), draw (colour draw into B, no z compare), zread (z-compare draw
// with depth image == B before any clear: reads A's bytes as depth), tex (texture load overlapping B's extent: fb-as-texture read),
// up (RT64 checkRAM found B's RAM changed and uploaded it into B's GPU image, i.e. consumed A's bytes; updisc = it discarded instead),
// wb (B written back). Hooks: lib/rt64 rt64_rdp.cpp drawTris/drawRect (rs64_s7500_draw), loadTile/loadBlockOperation
// (rs64_s7500_tex), rt64_framebuffer_manager.cpp uploadRAM (rs64_s7500_up); fill via rs64_s7497_zdraw k=2. Read classes = zread,
// tex, up. Positive controls ROGUESQ_S7500_CTL=1: (a) ctlB = the first covered B is reset artificially at cover time and must log
// `reset ... CTL`; (b) ctlA = the first covering A itself is entered as a tracked image, so A's own next set must classify a first
// event (fill/draw/...) through the same hooks, proving the event keys match real images.
extern "C" int rs64_s7500_on = [] { const char* e = std::getenv("ROGUESQ_S7500_EY"); return (e && *e && *e != '0') ? 1 : 0; }();
namespace {
struct S7500B { uint32_t kind, base, lo, hi, akind, abase, aw; uint64_t wb; int csw, bsw, rsw, state, ctl, cyc; double rt; std::string seq; };
std::mutex g_s7500_mu; std::map<uint64_t, S7500B> g_s7500; std::atomic<int> g_s7500_pend{0};
uint64_t g_s7500_n[9] = {}, g_s7500_cov = 0, g_s7500_reset = 0; std::atomic<uint64_t> g_s7500_hook[5] = {}; int g_s7500_rows = 0, g_s7500_ctla = -2, g_s7500_ctlb = -2;
std::string g_s7500_ctla_cls = "none"; double g_s7500_t0 = 0, g_s7500_last = 0;
const char* s7500_cls(int c) { static const char* k[9] = {"fill", "draw", "zread", "tex", "up", "updisc", "wb", "none", "zupd"}; return k[c % 9]; }
bool s7500_ctl() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7500_CTL"); return e && *e && *e != '0'; }(); return on; }
void s7500_sum_locked(double now) {
  uint64_t pend = 0, cov0 = 0; for (auto& kv : g_s7500) { if (kv.second.state == 1) ++pend; else if (kv.second.state == 0) ++cov0; }
  std::fprintf(stderr, "[s7500] sum t=%.1f tracked=%zu covers=%llu covered_unset=%llu resets=%llu pending=%llu first fill=%llu draw=%llu zread=%llu tex=%llu up=%llu updisc=%llu wb=%llu zupd=%llu"
    " read=%llu hooks draw=%llu tex=%llu up=%llu fill=%llu set=%llu ctlA=%s ctlA_cls=%s ctlB=%s\n", now - g_s7500_t0, g_s7500.size(), (unsigned long long)g_s7500_cov,
    (unsigned long long)cov0, (unsigned long long)g_s7500_reset, (unsigned long long)pend,
    (unsigned long long)g_s7500_n[0], (unsigned long long)g_s7500_n[1], (unsigned long long)g_s7500_n[2], (unsigned long long)g_s7500_n[3], (unsigned long long)g_s7500_n[4],
    (unsigned long long)g_s7500_n[5], (unsigned long long)g_s7500_n[6], (unsigned long long)g_s7500_n[8], (unsigned long long)(g_s7500_n[2] + g_s7500_n[3] + g_s7500_n[4]),
    (unsigned long long)g_s7500_hook[0].load(), (unsigned long long)g_s7500_hook[1].load(), (unsigned long long)g_s7500_hook[2].load(), (unsigned long long)g_s7500_hook[3].load(), (unsigned long long)g_s7500_hook[4].load(),
    g_s7500_ctla == 1 ? "ok" : g_s7500_ctla == -1 ? "pending" : g_s7500_ctla == 0 ? "FAIL" : "unarmed", g_s7500_ctla_cls.c_str(),
    g_s7500_ctlb == 1 ? "ok" : g_s7500_ctlb == -1 ? "pending" : "unarmed"); }
void s7500_tick_locked(double now) { if (g_s7500_t0 == 0) g_s7500_t0 = now; if (now - g_s7500_last >= 10.0) { g_s7500_last = now; s7500_sum_locked(now); } }
// first-event classification of a pending (state 1) entry; later events (up to 6) only extend its logged sequence.
void s7500_event_locked(S7500B& b, int c, const char* extra, double now) {
  if (b.state != 1) return; const int sw = g_rs64_swap_n.load(std::memory_order_relaxed);
  if (b.seq.size() < 120) { char t[64]; std::snprintf(t, sizeof t, "%s%s@%d", b.seq.empty() ? "" : ",", s7500_cls(c), sw - b.rsw); b.seq += t; }
  if (b.seq.find(',') != std::string::npos) { if (std::count(b.seq.begin(), b.seq.end(), ',') >= 5) { b.state = 2; g_s7500_pend.fetch_sub(1);
      static int srows = 0; if (++srows <= 60) std::fprintf(stderr, "[s7500] seq B kind=%u base=%06X%s %s\n", b.kind, b.base, b.ctl ? " CTL" : "", b.seq.c_str()); } return; }
  if (!b.ctl) ++g_s7500_n[c];
  if (b.ctl == 1 && g_s7500_ctla == -1) { g_s7500_ctla = 1; g_s7500_ctla_cls = s7500_cls(c); }
  const bool rd = c == 2 || c == 3 || c == 4;
  if (++g_s7500_rows <= 80 || (rd && g_s7500_rows <= 400))
    std::fprintf(stderr, "[s7500] first cls=%s%s B kind=%u base=%06X ext=[%06X,%06X) A kind=%u base=%06X w=%u wb#%llu reset_after=%.3fs sw=%d %s t=%.3f\n", s7500_cls(c),
      b.ctl == 1 ? " CTL-A" : b.ctl == 2 ? " CTL-B" : "", b.kind, b.base, b.lo, b.hi, b.akind, b.abase, b.aw, (unsigned long long)b.wb, now - b.rt, sw, extra, now - g_s7500_t0); }
}
static double s7500_now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
static void s7500_reset_locked(S7500B& b, double now, const char* why) {
  const int sw = g_rs64_swap_n.load(std::memory_order_relaxed); b.state = 1; b.rsw = sw; b.rt = now; b.seq.clear(); ++b.cyc; g_s7500_pend.fetch_add(1);
  if (!b.ctl) ++g_s7500_reset;
  if (++g_s7500_rows <= 80 || b.ctl)
    std::fprintf(stderr, "[s7500] reset%s B kind=%u base=%06X ext=[%06X,%06X) A kind=%u base=%06X w=%u wb#%llu gap_cover=%d gap_bset=%d cyc=%d t=%.3f\n", why,
      b.kind, b.base, b.lo, b.hi, b.akind, b.abase, b.aw, (unsigned long long)b.wb, sw - b.csw, sw - b.bsw, b.cyc, now - g_s7500_t0); }
static void s7500_cover(uint32_t bk, uint32_t bb, uint32_t be, uint32_t ak, uint32_t ab, uint32_t aw, uint64_t wb, int sw, int bsw) {
  if (!rs64_s7500_on || bk > 1) return;
  std::lock_guard<std::mutex> lk(g_s7500_mu); const double now = s7500_now(); s7500_tick_locked(now);
  const uint64_t key = ((uint64_t)bk << 32) | bb; auto it = g_s7500.find(key); ++g_s7500_cov;
  if (it == g_s7500.end()) it = g_s7500.emplace(key, S7500B{bk, bb, bb, be, ak, ab, aw, wb, sw, bsw, 0, 0, 0, 0, 0.0, {}}).first;
  S7500B& b = it->second; if (b.ctl) return;
  if (b.state != 0) { if (b.state == 1) g_s7500_pend.fetch_sub(1); b.state = 0; }  // re-covered: a new cycle starts at the next set
  b.akind = ak; b.abase = ab; b.aw = aw; b.wb = wb; b.csw = sw; b.bsw = bsw; if (be > b.hi) b.hi = be;
  if (s7500_ctl() && g_s7500_ctlb == -2) { g_s7500_ctlb = -1;
    S7500B c = b; c.ctl = 2; /* distinct key (kind|4): no hook ever looks it up */ auto ci = g_s7500.emplace((((uint64_t)bk | 4u) << 32) | bb, c).first;
    s7500_reset_locked(ci->second, now, " CTL"); ci->second.state = 2; g_s7500_pend.fetch_sub(1); g_s7500_ctlb = 1; }
  if (s7500_ctl() && g_s7500_ctla == -2) { g_s7500_ctla = -1;
    S7500B a{ak, ab, ab, ab + 0x100u, ak, ab, aw, wb, sw, sw, 0, 0, 1, 0, 0.0, {}}; if (!g_s7500.emplace(((uint64_t)ak << 32) | ab, a).second) g_s7500_ctla = -2; } }
static void s7500_set(uint32_t kind, uint32_t addr) {
  if (!rs64_s7500_on || kind > 1) return; addr &= 0xFFFFFFu;
  std::lock_guard<std::mutex> lk(g_s7500_mu); const double now = s7500_now(); s7500_tick_locked(now); ++g_s7500_hook[4];
  auto it = g_s7500.find(((uint64_t)kind << 32) | addr); if (it == g_s7500.end()) return;
  S7500B& b = it->second; if (b.state == 0) s7500_reset_locked(b, now, b.ctl == 1 ? " CTL-A" : ""); }
static void s7500_wb(uint32_t kind, uint32_t base) {
  s7503_wb(kind, base);
  if (!rs64_s7500_on || g_s7500_pend.load() <= 0) return;
  std::lock_guard<std::mutex> lk(g_s7500_mu); auto it = g_s7500.find(((uint64_t)kind << 32) | (base & 0xFFFFFFu));
  if (it != g_s7500.end()) s7500_event_locked(it->second, 6, "", s7500_now()); }
extern "C" void rs64_s7500_draw(uint32_t caddr, uint32_t zaddr, uint32_t f) {
  s7503_draw(caddr, zaddr, f);
  g_s7500_hook[0].fetch_add(1, std::memory_order_relaxed);
  if (g_s7500_pend.load(std::memory_order_relaxed) <= 0) return;
  std::lock_guard<std::mutex> lk(g_s7500_mu); const double now = s7500_now(); caddr &= 0xFFFFFFu; zaddr &= 0xFFFFFFu;
  auto c = g_s7500.find(caddr); if (c != g_s7500.end() && c->second.state == 1) s7500_event_locked(c->second, 1, "", now);
  if (f & 3u) { auto z = g_s7500.find((1ull << 32) | zaddr); if (z != g_s7500.end() && z->second.state == 1) s7500_event_locked(z->second, (f & 1u) ? 2 : 8, "", now); }
  /* z-clear idiom / colour drawn at a depth image's address */
  auto cz = g_s7500.find((1ull << 32) | caddr); if (cz != g_s7500.end() && cz->second.state == 1) s7500_event_locked(cz->second, 1, "cimg=zaddr", now); }
static void s7500_fill(uint32_t caddr) {
  if (!rs64_s7500_on) return; g_s7500_hook[3].fetch_add(1, std::memory_order_relaxed);
  if (g_s7500_pend.load(std::memory_order_relaxed) <= 0) return;
  std::lock_guard<std::mutex> lk(g_s7500_mu); const double now = s7500_now(); caddr &= 0xFFFFFFu;
  for (uint32_t k = 0; k < 2; ++k) { auto it = g_s7500.find(((uint64_t)k << 32) | caddr); if (it != g_s7500.end() && it->second.state == 1) s7500_event_locked(it->second, 0, "", now); } }
extern "C" void rs64_s7500_tex(uint32_t lo, uint32_t hi) {
  s7503_tex(lo, hi);
  g_s7500_hook[1].fetch_add(1, std::memory_order_relaxed);
  if (g_s7500_pend.load(std::memory_order_relaxed) <= 0) return;
  std::lock_guard<std::mutex> lk(g_s7500_mu); const double now = s7500_now(); lo &= 0xFFFFFFu; hi &= 0xFFFFFFu;
  for (auto& kv : g_s7500) { S7500B& b = kv.second; if (b.state == 1 && lo < b.hi && hi > b.lo) { char t[48]; std::snprintf(t, sizeof t, "tex=[%06X,%06X)", lo, hi); s7500_event_locked(b, 3, t, now); } } }
extern "C" void rs64_s7500_up(uint32_t addr, uint32_t w, uint32_t siz, uint32_t diffpx, int fl) {
  s7503_up(addr, fl);
  std::lock_guard<std::mutex> lk(g_s7500_mu); ++g_s7500_hook[2]; const double now = s7500_now(); s7500_tick_locked(now); addr &= 0xFFFFFFu;
  if (g_s7500_pend.load(std::memory_order_relaxed) <= 0) return;
  for (uint32_t k = 0; k < 2; ++k) { auto it = g_s7500.find(((uint64_t)k << 32) | addr); if (it != g_s7500.end() && it->second.state == 1) { char t[72];
      std::snprintf(t, sizeof t, "up w=%u siz=%u diffpx=%u path=%s", w, siz, diffpx, (fl & 2) ? "present" : "draw"); s7500_event_locked(it->second, (fl & 1) ? 5 : 4, t, now); } } }
// s7501 class EZ: who wrote the RDRAM behind each RT64 checkRAM upload? RT64 uploads a framebuffer (copyRAMToNativeAndChanges) when
// its RDRAM hash moved since RT64 last hashed it. ROGUESQ_S7501_EZ=1. Hooks: lib/rt64 rt64_framebuffer_manager.cpp checkRAM (every fb,
// every workload: rs64_s7501_chk -> seen / hash epoch), hashTracking + rt64_state.cpp s7387 skip (rs64_s7501_hash), uploadRAM
// (rs64_s7501_up with the byte bbox of words that differ from RT64's own last native copy). Writers go into one time-stamped ring:
// wb (rs64_wbw_post, exact base via rs64_s7493_base: wbself when base == the uploaded fb, else wbo = another image's writeback),
// sp_gfx / sp_aud / pi (rs64_s7486_hostread kinds 6-8, before the copy), and guest stores: every seen fb's bytes are marked in the s7475
// store bitmap (needs ROGUESQ_S7475_CANARY + STORE_DIAG), so rs64_s7475_store hands them here first -> cpu (fn = recompiled fn),
// zmem (fn zmemcpy_host), os (fn os_*). Upload classes: new (fb never hashed before: first adoption of whatever RAM was there),
// hash (0 words differ from the native copy), a writer class (newest ring event in (prev hash, now] overlapping the bbox; mask = all
// classes seen), none (no writer: unexplained), trunc (window older than the ring). Control ROGUESQ_S7501_CTL=1: from t>=30 s, after an
// upload the host XORs one word in the middle of that fb's RAM and logs a ctl event; the next upload of that fb whose bbox covers the
// word MUST class ctl (retries every 20 s, max 12). Rows `[s7501] up`, `[s7501] sum` every 10 s. Measurement only (the ctl word is
// the only guest-RAM change, one 32-bit word per try).
extern "C" int rs64_s7501_on = [] { const char* e = std::getenv("ROGUESQ_S7501_EZ"); return (e && *e && *e != '0') ? 1 : 0; }();
extern "C" unsigned char* g_rs64_s7475_bm;
namespace {
struct S7501E { uint32_t lo, hi, base, pc; double t; int cls; const char* fn; };
struct S7501F { uint32_t bytes = 0, hbytes = 0, pbytes = 0; double hash_t = 0, pend_t = -1, seen = 0, mark_t = 0; bool marked = false; uint64_t ups = 0; double up_t = 0, up_t3 = 0, first_t = 0; };  /* up_t: last upload = RT64 native copy re-synced to RAM */
constexpr uint32_t kS7501Ring = 1u << 21;
std::mutex g_s7501_mu; std::vector<S7501E> g_s7501_ring; uint64_t g_s7501_rn = 0; std::map<uint32_t, S7501F> g_s7501_fb;
std::atomic<uint32_t> g_s7501_base{0xFFFFFFFFu};
enum { Z_WB, Z_SPG, Z_SPA, Z_PI, Z_ZMEM, Z_OS, Z_CPU, Z_CTL, Z_WBSELF, Z_NEW, Z_HASH, Z_NONE, Z_TRUNC, Z_RESIZE, Z_SHORT, Z_REVERT, Z_N };
const char* s7501_cls(int c) { static const char* k[Z_N] = {"wbo", "sp_gfx", "sp_aud", "pi", "zmem", "os", "cpu", "ctl", "wbself", "new", "hash", "none", "trunc", "resize", "short", "revert"}; return k[c % Z_N]; }
uint64_t g_s7501_n[Z_N] = {}, g_s7501_ev[Z_N] = {}, g_s7501_ups = 0, g_s7501_chk = 0; double g_s7501_t0 = 0, g_s7501_last = 0;
int g_s7501_rows = 0, g_s7501_ctl = -2, g_s7501_ctries = 0, g_s7501_clost = 0; uint32_t g_s7501_ctla = 0, g_s7501_ctlfb = 0; double g_s7501_ctlt = 0;
std::map<uint32_t, uint64_t> g_s7501_cpupc;  // pc -> stores into seen fbs
/* s7502 FA-pre: per-4KB-page newest writer (survives the ring wrap -> resolves trunc windows), uploads only the pre-scan window
   start attributes (race: the writer stored between RT64's previous RAM copy and that upload's log stamp), its pre-scan stamp */
constexpr uint32_t kS7501Pages = 0x1800000u >> 12; std::vector<S7501E> g_s7501_pg; uint64_t g_s7501_race = 0, g_s7501_pgres = 0;
thread_local double t_s7501_pre = 0;
double s7501_now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
bool s7501_ctl_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7501_CTL"); return e && *e && *e != '0'; }(); return on; }
inline bool now_ok_s7501(const S7501F& f) { return f.marked; }
void s7501_mark(uint32_t a, uint32_t n, bool on) {  // a = phys
  if (!g_rs64_s7475_bm) return;
  for (uint32_t o = a; o < a + n && o < 0x1800000u; ) {
    if ((o & 7u) == 0 && o + 8u <= a + n) { g_rs64_s7475_bm[o >> 3] = on ? 0xFFu : 0u; o += 8u; continue; }
    if (on) g_rs64_s7475_bm[o >> 3] |= (unsigned char)(1u << (o & 7u)); else g_rs64_s7475_bm[o >> 3] &= (unsigned char)~(1u << (o & 7u)); ++o; } }
void s7501_push_locked(uint32_t lo, uint32_t hi, int cls, uint32_t base, uint32_t pc, const char* fn, double now) {
  if (g_s7501_ring.empty()) g_s7501_ring.resize(kS7501Ring);
  g_s7501_ring[g_s7501_rn++ & (kS7501Ring - 1)] = S7501E{lo, hi, base, pc, now, cls, fn}; ++g_s7501_ev[cls];
  if (g_s7501_pg.empty()) g_s7501_pg.resize(kS7501Pages);
  for (uint32_t pg = lo >> 12; pg <= ((hi ? hi - 1 : lo) >> 12) && pg < kS7501Pages; ++pg) g_s7501_pg[pg] = S7501E{lo, hi, base, pc, now, cls, fn}; }
void s7501_sum_locked(double now) {
  std::string top; { std::vector<std::pair<uint64_t, uint32_t>> v; for (auto& kv : g_s7501_cpupc) v.push_back({kv.second, kv.first});
    std::sort(v.rbegin(), v.rend()); char t[40]; for (size_t i = 0; i < v.size() && i < 6; ++i) { std::snprintf(t, sizeof t, "%s%08X:%llu", i ? "," : "", v[i].second, (unsigned long long)v[i].first); top += t; } }
  std::string b; char t[48]; for (int c = 0; c < Z_N; ++c) { std::snprintf(t, sizeof t, " %s=%llu", s7501_cls(c), (unsigned long long)g_s7501_n[c]); b += t; }
  std::string e; for (int c = 0; c <= Z_CTL; ++c) { std::snprintf(t, sizeof t, "%s%s:%llu", c ? "," : "", s7501_cls(c), (unsigned long long)g_s7501_ev[c]); e += t; }
  std::fprintf(stderr, "[s7501] sum t=%.1f ups=%llu fbs=%zu chk=%llu cls%s ev=%s cpu_pcs=%s ctlst=%s ctl_tries=%d ctl_lost=%d bm=%d race=%llu pgres=%llu\n", now - g_s7501_t0, (unsigned long long)g_s7501_ups,
    g_s7501_fb.size(), (unsigned long long)g_s7501_chk, b.c_str(), e.c_str(), top.empty() ? "none" : top.c_str(),
    g_s7501_ctl == 1 ? "ok" : g_s7501_ctl == -1 ? "pending" : g_s7501_ctl == 0 ? "idle" : "unarmed", g_s7501_ctries, g_s7501_clost, g_rs64_s7475_bm != nullptr, (unsigned long long)g_s7501_race, (unsigned long long)g_s7501_pgres); }
void s7501_tick_locked(double now) {
  if (g_s7501_t0 == 0) g_s7501_t0 = now;
  if (now - g_s7501_last < 10.0) return; g_s7501_last = now; s7501_sum_locked(now);
  for (auto& kv : g_s7501_fb) { S7501F& f = kv.second;  // expire fbs unseen for 5 s (their bytes may be heap again); re-mark live ones
    if (f.marked && now - f.seen > 5.0) { s7501_mark(kv.first, f.bytes, false); f.marked = false; }
    else if (!f.marked && now - f.seen <= 5.0) { s7501_mark(kv.first, f.bytes, true); f.marked = true; }
    else if (f.marked) s7501_mark(kv.first, f.bytes, true); } }
}  // namespace
extern "C" void rs64_s7501_w(uint32_t addr, uint32_t len, int kind) {  // host DMA writes (upstream_compat rs64_s7486_hostread kinds 6-8)
  if (!rs64_s7501_on || !len) return; const uint32_t a = addr & 0x1FFFFFFu;
  std::lock_guard<std::mutex> lk(g_s7501_mu);
  /* only DMA writes overlapping a tracked fb enter the ring (s7501 run 1: 99M-187M sp_gfx events/run wrapped the ring in ~2 s) */
  bool hit = false; for (auto it = g_s7501_fb.lower_bound(a + len); it != g_s7501_fb.begin(); ) { --it; if (it->first + it->second.bytes > a && now_ok_s7501(it->second)) { hit = true; break; } }
  if (hit) s7501_push_locked(a, a + len, kind == 6 ? Z_SPG : kind == 7 ? Z_SPA : Z_PI, 0, 0, nullptr, s7501_now()); }
extern "C" int rs64_s7501_cpu(uint32_t pc, uint32_t va, int w, const char* fn) {  // rs64_s7475_store first: 1 = an fb byte (claimed)
  if (!rs64_s7501_on) return 0; const uint32_t a = va & 0x1FFFFFFu;
  std::lock_guard<std::mutex> lk(g_s7501_mu);
  /* s7502: walk back to the nearest MARKED fb covering a; an expired small fb record starting inside a live one (boot 320x224
     images at 6A0E00/6C3E00 inside the 640x340 67CA00) used to swallow the store -> the EZ `none` uploads at t~18.05 */
  auto it = g_s7501_fb.upper_bound(a); bool cov = false;
  for (int k = 0; k < 64 && it != g_s7501_fb.begin(); ++k) { --it; if (it->second.marked && a < it->first + it->second.bytes) { cov = true; break; } }
  if (!cov) return 0;
  const int c = (fn && !std::strncmp(fn, "zmemcpy", 7)) ? Z_ZMEM : (fn && !std::strncmp(fn, "os_", 3)) ? Z_OS : Z_CPU;
  if (c == Z_CPU) ++g_s7501_cpupc[pc];
  const double now = s7501_now();
  /* coalesce: a store adjacent to one of the last 4 events from the same pc within 5 ms extends it (memset / decode loops) */
  for (uint64_t i = 1; i <= 4 && i <= g_s7501_rn; ++i) { S7501E& e = g_s7501_ring[(g_s7501_rn - i) & (kS7501Ring - 1)];
    if (e.cls == c && e.pc == pc && e.base == it->first && now - e.t < 0.005 && a <= e.hi + 8u && a + (uint32_t)w + 8u >= e.lo) {
      e.lo = std::min(e.lo, a); e.hi = std::max(e.hi, a + (uint32_t)w); e.t = now; ++g_s7501_ev[c];
      if (!g_s7501_pg.empty() && (a >> 12) < kS7501Pages) g_s7501_pg[a >> 12] = e; return 1; } }
  s7501_push_locked(a, a + (uint32_t)w, c, it->first, pc, fn, now); return 1; }
static void s7501_wb(uint32_t phys, uint32_t bytes) {
  const uint32_t b = g_s7501_base.exchange(0xFFFFFFFFu); if (!rs64_s7501_on || !bytes) return;
  std::lock_guard<std::mutex> lk(g_s7501_mu); s7501_push_locked(phys & 0x1FFFFFFu, (phys & 0x1FFFFFFu) + bytes, Z_WB, b & 0x1FFFFFFu, 0, nullptr, s7501_now()); }
extern "C" void rs64_s7501_chk(uint32_t addr, uint32_t bytes, int differs) {
  std::lock_guard<std::mutex> lk(g_s7501_mu); const double now = s7501_now(); s7501_tick_locked(now); ++g_s7501_chk; addr &= 0x1FFFFFFu;
  S7501F& f = g_s7501_fb[addr]; f.seen = now; if (f.first_t == 0) f.first_t = now;
  if (bytes != f.bytes) { if (f.marked) s7501_mark(addr, f.bytes, false); f.bytes = bytes; f.marked = false; }
  /* re-mark every pass: the s7475 canary clears bitmap bits when it (un)marks heap slack / freed records over reused fb memory */
  s7501_mark(addr, bytes, true); f.marked = true; f.mark_t = now;
  if (differs) { f.pend_t = f.hash_t; f.pbytes = f.hbytes; f.hash_t = now; f.hbytes = bytes; }
  /* control from checkRAM too: an fb not re-hashed for >= 2 s (not being drawn), so the poke is not adopted by hashTracking */
  else if (s7501_ctl_on() && g_s7501_ctl != 1 && g_s7501_t0 > 0 && now - g_s7501_t0 >= 30.0 && g_s7501_ctries < 40 && f.hash_t > 0 && now - f.hash_t >= 2.0 &&
           bytes >= 16 && (g_s7501_ctl != -1 || g_s7501_ctlt == 0 || now - g_s7501_ctlt > 10.0)) {
    volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
    if (rd) { const uint32_t a = (addr + bytes / 2) & ~3u; volatile uint32_t* p = (volatile uint32_t*)(rd + a); *p = *p ^ 0x00FF00FFu;
      g_s7501_ctl = -1; g_s7501_ctla = a; g_s7501_ctlfb = addr; g_s7501_ctlt = now; ++g_s7501_ctries; s7501_push_locked(a, a + 4, Z_CTL, addr, 0, "ctl", now);
      std::fprintf(stderr, "[s7501] ctl poke(chk) fb=%06X word=%06X idle=%.1fs try=%d t=%.3f\n", addr, a, now - f.hash_t, g_s7501_ctries, now - g_s7501_t0); } } }
extern "C" void rs64_s7501_pre() { t_s7501_pre = s7501_now(); }  /* s7502: RT64 uploadRAM, before its diff scan + RAM copy */
extern "C" void rs64_s7501_hash(uint32_t addr, uint32_t bytes) {
  std::lock_guard<std::mutex> lk(g_s7501_mu); const double now = s7501_now(); addr &= 0x1FFFFFFu;
  S7501F& f = g_s7501_fb[addr]; f.seen = now; if (f.first_t == 0) f.first_t = now; f.hash_t = now; f.hbytes = bytes; f.pend_t = -1; if (!f.bytes) f.bytes = bytes;
  if (g_s7501_ctl == -1 && addr == g_s7501_ctlfb && g_s7501_ctlt > 0 && g_s7501_clost < 1000) { ++g_s7501_clost;  /* fb re-hashed after the poke: the upload window (since last upload) still holds it, no retry */
    if (g_s7501_clost <= 3) std::fprintf(stderr, "[s7501] ctl rehash (fb %06X re-hashed after poke, kept) try=%d\n", addr, g_s7501_ctries); } }
extern "C" void rs64_s7501_up(uint32_t addr, uint32_t w, uint32_t h, uint32_t siz, uint32_t bytes, uint32_t diffpx, int fl, uint32_t blo, uint32_t bhi, uint32_t nchg) {
  std::lock_guard<std::mutex> lk(g_s7501_mu); const double now = s7501_now(); s7501_tick_locked(now); addr &= 0x1FFFFFFu; ++g_s7501_ups;
  S7501F& f = g_s7501_fb[addr]; f.seen = now; if (!f.bytes) f.bytes = bytes; ++f.ups; if (f.first_t == 0) f.first_t = now;
  const bool pend = f.pend_t >= 0; const double wh = pend ? f.pend_t : f.hash_t;
  /* window = since RT64's native copy last matched RAM (this fb's previous upload, else first sighting), not since the last re-hash:
     hashTracking / an overlapping fb's draw re-hash RAM without refreshing nativeSwappedRAM (s7501 run 1, L4 ctl word classed revert) */
  const double ws = wh <= 0 ? wh : (f.up_t > 0 ? f.up_t : f.first_t), ws_old = wh <= 0 ? wh : (f.up_t3 > 0 ? f.up_t3 : f.first_t);
  f.up_t = (t_s7501_pre > 0 && t_s7501_pre <= now) ? t_s7501_pre : now; f.up_t3 = now; t_s7501_pre = 0; const uint32_t wsb = pend ? f.pbytes : f.hbytes; f.pend_t = -1;
  if (fl & 2) { f.hash_t = now; f.hbytes = bytes; }
  const bool resized = ws > 0 && wsb != 0 && wsb != bytes, shortnat = (fl & 4) != 0;  /* hash range grew/shrank; RT64 native copy shorter than RAMBytes */  /* present path adopts the hash after the upload */
  const uint32_t lo = addr + blo, hi = addr + bhi;
  int cls = Z_NONE; uint32_t mask = 0, rmask = 0; uint64_t nwin = 0; const S7501E* top = nullptr; const S7501E* rtop = nullptr; bool trunc = false;
  if (ws <= 0) cls = Z_NEW;
  else if (nchg == 0) cls = Z_HASH;
  else {
    const uint64_t n = std::min<uint64_t>(g_s7501_rn, kS7501Ring); uint64_t i = 0;
    for (; i < n; ++i) { const S7501E& e = g_s7501_ring[(g_s7501_rn - 1 - i) & (kS7501Ring - 1)]; if (e.t <= ws) break;
      if (e.lo < hi && e.hi > lo) { const int c = (e.cls == Z_WB && e.base == addr) ? Z_WBSELF : e.cls; mask |= 1u << c; ++nwin; if (!top) top = &e; } }
    if (i == n && n == kS7501Ring) trunc = true;
    S7501E pgtop{}; bool pgres = false;
    if (!top && trunc && !g_s7501_pg.empty()) {  /* s7502: window older than the ring -> newest per-page writer over the bbox, inside the window */
      for (uint32_t pg = lo >> 12; pg <= ((hi ? hi - 1 : lo) >> 12) && pg < kS7501Pages; ++pg) { const S7501E& e = g_s7501_pg[pg];
        if (e.t > ws && e.lo < hi && e.hi > lo && (!pgres || e.t > pgtop.t)) { pgtop = e; pgres = true; } }
      if (pgres) { top = &pgtop; trunc = false; ++g_s7501_pgres; mask |= 1u << ((pgtop.cls == Z_WB && pgtop.base == addr) ? Z_WBSELF : pgtop.cls); } }
    if (top && !pgres && ws_old > ws) {  /* race: every overlapping writer in the window sits in [pre-scan, log stamp) of the previous upload */
      bool late = false; for (uint64_t j = 0; j < n; ++j) { const S7501E& e = g_s7501_ring[(g_s7501_rn - 1 - j) & (kS7501Ring - 1)]; if (e.t <= ws_old) break;
        if (e.lo < hi && e.hi > lo) { late = true; break; } }
      if (!late) { ++g_s7501_race; std::fprintf(stderr, "[s7502] race fb=%06X bbox=[%06X,%06X) gap=%.4fs top=%s pc=%08X fn=%s t=%.3f\n", addr, lo, hi, ws_old - ws, s7501_cls(top->cls), top->pc, top->fn ? top->fn : "-", now - g_s7501_t0); } }
    if (pgres) std::fprintf(stderr, "[s7502] pgres fb=%06X bbox=[%06X,%06X) win=%.1fs top=%s pc=%08X fn=%s at=%.3f t=%.3f\n", addr, lo, hi, now - ws, s7501_cls(pgtop.cls), pgtop.pc, pgtop.fn ? pgtop.fn : "-", pgtop.t - g_s7501_t0, now - g_s7501_t0);
    if (top) cls = (top->cls == Z_WB && top->base == addr) ? Z_WBSELF : top->cls; else if (trunc) cls = Z_TRUNC; else if (resized) cls = Z_RESIZE; else if (shortnat) cls = Z_SHORT;
    if (cls == Z_NONE) {  /* a writer in the window over the fb but outside the still-different bytes: it changed RAM back to RT64's own copy */
      for (uint64_t j = 0; j < n; ++j) { const S7501E& e = g_s7501_ring[(g_s7501_rn - 1 - j) & (kS7501Ring - 1)]; if (e.t <= ws) break;
        if (e.lo < addr + bytes && e.hi > addr) { const int c = (e.cls == Z_WB && e.base == addr) ? Z_WBSELF : e.cls; rmask |= 1u << c; if (!rtop) rtop = &e; } }
      if (rtop) cls = Z_REVERT; } }
  const bool isctl = g_s7501_ctl == -1 && g_s7501_ctla >= lo && g_s7501_ctla < hi;  /* any fb whose bbox covers the poked word (fbs overlap) */
  if (isctl && (mask & (1u << Z_CTL))) { g_s7501_ctl = 1; std::fprintf(stderr, "[s7501] ctl DETECTED fb=%06X poked_fb=%06X word=%06X cls=%s try=%d\n", addr, g_s7501_ctlfb, g_s7501_ctla, s7501_cls(cls), g_s7501_ctries); }
  else if (isctl) std::fprintf(stderr, "[s7501] ctl MISSED fb=%06X word=%06X cls=%s mask=%X try=%d\n", addr, g_s7501_ctla, s7501_cls(cls), mask, g_s7501_ctries);
  if (cls != Z_CTL && !isctl) ++g_s7501_n[cls];
  if (cls == Z_CPU && top) rs64_s7503_arm(addr, bytes, w, top->fn, (fl & 2) ? 1 : 0);  /* s7503 FA */
  if (cls == Z_CPU && top && (fl & 2) && top->fn && (std::strstr(top->fn, "rs_malloc") || std::strstr(top->fn, "rs_free") || std::strstr(top->fn, "coalesceFreeHeap") ||
      std::strstr(top->fn, "buildHeapFreeList") || std::strstr(top->fn, "packTlut"))) s7504_fb("hdr", addr, w, top->lo, top->hi, now - g_s7501_t0);  /* s7504 FB */
  if (++g_s7501_rows <= 400) {
    std::string m; for (int c = 0; c < Z_N; ++c) if (mask & (1u << c)) { if (!m.empty()) m += '|'; m += s7501_cls(c); }
    std::fprintf(stderr, "[s7501] up fb=%06X w=%u h=%u siz=%u bytes=%u diffpx=%u nchg=%u bbox=[%06X,%06X) path=%s%s win=%.3fs cls=%s mask=%s nwin=%llu top=[%06X,%06X) base=%06X pc=%08X fn=%s ups=%llu hbytes=%u%s%s rmask=%X rtop=%s:[%06X,%06X) sw=%d t=%.3f\n",
      addr, w, h, siz, bytes, diffpx, nchg, lo, hi, (fl & 2) ? "present" : "draw", (fl & 1) ? " discard" : "", ws > 0 ? now - ws : -1.0, s7501_cls(cls),
      m.empty() ? "-" : m.c_str(), (unsigned long long)nwin, top ? top->lo : 0, top ? top->hi : 0, top ? top->base : 0, top ? top->pc : 0,
      (top && top->fn) ? top->fn : "-", (unsigned long long)f.ups, wsb, resized ? " RESIZED" : "", shortnat ? " SHORTNAT" : "", rmask, rtop ? s7501_cls(rtop->cls) : "-", rtop ? rtop->lo : 0, rtop ? rtop->hi : 0, g_rs64_swap_n.load(std::memory_order_relaxed), now - g_s7501_t0); }
  /* positive control: poke one word of this fb (host write, logged as ctl) */
  if (s7501_ctl_on() && g_s7501_ctl != 1 && now - g_s7501_t0 >= 30.0 && g_s7501_ctries < 40 && (g_s7501_ctl != -1 || g_s7501_ctlt == 0 || now - g_s7501_ctlt > 10.0) && bytes >= 16) {
    volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
    if (rd) { const uint32_t a = (addr + bytes / 2) & ~3u; volatile uint32_t* p = (volatile uint32_t*)(rd + a); *p = *p ^ 0x00FF00FFu;
      const double tp = s7501_now() + 1e-6;  /* strictly after this upload's window edge (present path sets hash_t = now) */
      g_s7501_ctl = -1; g_s7501_ctla = a; g_s7501_ctlfb = addr; g_s7501_ctlt = tp; ++g_s7501_ctries; s7501_push_locked(a, a + 4, Z_CTL, addr, 0, "ctl", tp);
      std::fprintf(stderr, "[s7501] ctl poke fb=%06X word=%06X try=%d t=%.3f\n", addr, a, g_s7501_ctries, now - g_s7501_t0); } } }
extern "C" void rs64_s7493_base(uint32_t b) { g_s7493_next_base.store(b); g_s7497_base.store(b); g_s7498_base.store(b); g_s7501_base.store(b); }
static void s7493_wb(uint32_t phys, uint32_t bytes, uint32_t kind, uint32_t width, uint32_t rows) {
    if (!s7493_on() || kind > 1 || !bytes) return;
    static const uint64_t ctl_k = [] { const char* e = std::getenv("ROGUESQ_S7493_WBLIVE_CTL"); return e ? (uint64_t)std::strtoull(e, nullptr, 0) : 0ull; }();
    std::lock_guard<std::mutex> lk(g_s7493_mu); const double now = s7493_now(); if (g_s7493_t0 == 0) g_s7493_t0 = now;
    const int sw = g_rs64_swap_n.load(std::memory_order_relaxed); const uint64_t k = ++g_s7493_wb;
    auto& mp = g_s7493_img[kind]; bool found = false; uint32_t base = 0; double aget = -1; int ages = -1; uint32_t iw = 0;
    /* s7493 v3: RT64 hands the exact image base (rs64_s7493_base, colorFb/depthFb->addressStart) before each post; look that image up.
       v1 (greatest base <= phys) matched older images in between; v2 (youngest covering same-width image) masked the L15 control. */
    { const uint32_t eb = g_s7493_next_base.exchange(0xFFFFFFFFu); base = eb;
      if (eb != 0xFFFFFFFFu) { auto it = mp.find(eb & 0xFFFFFFu); if (it != mp.end()) { found = true; aget = now - it->second.t; ages = sw - it->second.sw; iw = it->second.width; } }
      else ++g_s7493_nobase; }
    for (uint32_t i = 0; i < s7493_nwatch(); i++) { const uint32_t wa = s7493_watch(i); if (wa >= phys && wa < phys + bytes && g_s7493_wlog < 60) { ++g_s7493_wlog;
        std::fprintf(stderr, "[s7493] watch %06X wb #%llu kind=%u phys=%06X bytes=%u w=%u rows=%u found=%d base=%06X age_sw=%d age_s=%.3f sw=%d t=%.3f\n", wa, (unsigned long long)k, kind, phys, bytes, width, rows, (int)found, base, ages, aget, sw, now - g_s7493_t0); } }
    const int cls = !found ? 3 : ages <= 0 ? 0 : ages == 1 ? 1 : 2; g_s7493_cnt[kind][cls]++;
    const bool isctl = cls >= 2 && g_s7493_ctl_kind == (int)kind && (base & 0xFFFFFFu) == g_s7493_ctl_base;
    if (isctl) g_s7493_ctl_never++;
    if ((cls >= 2 && g_s7493_logged < 20) || k <= 40 || (isctl && g_s7493_ctl_never <= 3)) { if (cls >= 2 && !isctl) ++g_s7493_logged;
        std::fprintf(stderr, "[s7493] wb #%llu %s kind=%u phys=%06X bytes=%u w=%u rows=%u base=%06X iw=%u age_sw=%d age_s=%.3f sw=%d t=%.3f%s\n", (unsigned long long)k,
            cls == 0 ? "age0" : cls == 1 ? "age1" : cls == 2 ? "age>=2" : "never", kind, phys, bytes, width, rows, base, iw, ages, aget, sw, now - g_s7493_t0, isctl ? " CTL" : ""); }
    if (ctl_k && k == ctl_k && found) { mp.erase(base); g_s7493_ctl_base = base; g_s7493_ctl_kind = (int)kind; g_s7493_ctl_armed++;
        std::fprintf(stderr, "[s7493] ctl armed at wb #%llu: erased + blacklisted kind=%u base=%06X (its next writebacks must be age>=2|never CTL)\n", (unsigned long long)k, kind, base); }
    if (now - g_s7493_last_sum >= 10.0) { g_s7493_last_sum = now;
        std::fprintf(stderr, "[s7493] sum t=%.1f wb=%llu sets=%llu/%llu color age0=%llu age1=%llu age2=%llu never=%llu depth age0=%llu age1=%llu age2=%llu never=%llu ctl_armed=%llu ctl_never=%llu nobase=%llu\n",
            now - g_s7493_t0, (unsigned long long)g_s7493_wb, (unsigned long long)g_s7493_sets[0], (unsigned long long)g_s7493_sets[1],
            (unsigned long long)g_s7493_cnt[0][0], (unsigned long long)g_s7493_cnt[0][1], (unsigned long long)g_s7493_cnt[0][2], (unsigned long long)g_s7493_cnt[0][3],
            (unsigned long long)g_s7493_cnt[1][0], (unsigned long long)g_s7493_cnt[1][1], (unsigned long long)g_s7493_cnt[1][2], (unsigned long long)g_s7493_cnt[1][3],
            (unsigned long long)g_s7493_ctl_armed, (unsigned long long)g_s7493_ctl_never, (unsigned long long)g_s7493_nobase); }
}

// s7551 class GK instrument (ROGUESQ_S7551_GK=1, off by default). RT64 copyNativeToRAM writes FULL rows of the pair's
// span; bytes outside the drawn rect come from the retained native target, revalidated from RAM only at checkRDRAM (DL
// start). At each checkRDRAM we snapshot every recently written-back span; around each writeback we diff
// snapshot / pre / post per byte: gch = bytes something other than RT64's writeback changed since DL start, clob = of those,
// bytes the writeback then replaced, split inside/outside the pair's draw rect columns (rect via rs64_s7551_gk_rect).
// Control ROGUESQ_S7551_GK_PLANT=1: every 16th check the host XORs 4 bytes of the span (outside the last rect when it can)
// right after the snapshot; those bytes must be seen changed and clobbered (plants/pseen/pclob) and are excluded from gch.
namespace s7551 {
static bool envon(const char* n) { const char* e = std::getenv(n); return e && *e && *e != '0'; }
static const bool on = envon("ROGUESQ_S7551_GK");
static const bool plant = envon("ROGUESQ_S7551_GK_PLANT");
struct Span { uint32_t phys = 0, bytes = 0, kind = 0, width = 0, rows = 0; int32_t rl = 0, rr = 0;
              std::vector<uint8_t> snap; uint64_t seq = 0, used = 0; uint32_t plantAt = 0xFFFFFFFFu; };
struct Cnt { uint64_t wb = 0, nosnap = 0, bytes = 0, gch = 0, gchIn = 0, gchOut = 0, clob = 0, clobIn = 0, clobOut = 0, revert = 0,
             rtOut = 0, plants = 0, pseen = 0, pclob = 0, gwb = 0, cwb = 0; };
static std::mutex mu;
static std::vector<Span> spans;
static uint64_t seq = 0, checks = 0;
static std::vector<uint32_t> g_plants; // plant addresses of the current check (host XOR, control)
// s7552 class GL: classify rtOut pixels (16-bit colour, outside the rect, unchanged since DL start, changed by the writeback)
// against RT64's own requantisation F(pre,d) = Float4ToRGBA16(RGBA16ToFloat4(pre), d): c8=(c5<<3)|(c5>>2); c5'=min(c8+d,255)>>3,
// alpha kept. d = the fb's bestDitherPattern value at (x,y): MAGICSQ / BAYER table, NOISE any 0..7, DISABLE 0.
static thread_local int32_t t_dith = -1;
struct GL { uint64_t outPx = 0, rtPx = 0, mPat = 0, mAny = 0, mZero = 0, unm = 0, alpha = 0, up = 0, down = 0, d1 = 0, d2 = 0, d3 = 0,
            e0 = 0, e1 = 0, e2 = 0, e4 = 0, e16 = 0, inChg = 0, inAny = 0, wbPat[5] = {0, 0, 0, 0, 0}, rtPat[5] = {0, 0, 0, 0, 0}, b4 = 0; };
static GL gl;
struct GLKey { uint32_t phys, w, rows; int32_t rl, rr; int32_t pat; uint64_t n; };
static std::vector<GLKey> glk;
static const uint8_t kMS[16] = { 0, 6, 1, 7, 4, 2, 5, 3, 3, 5, 2, 4, 7, 1, 6, 0 };
static const uint8_t kBY[16] = { 0, 4, 1, 5, 4, 0, 5, 1, 3, 7, 2, 6, 7, 3, 6, 2 };
static inline uint16_t F(uint16_t v, uint32_t d) {
    uint16_t o = v & 1u;
    for (int sh = 11; sh >= 1; sh -= 5) { const uint32_t c5 = (v >> sh) & 31u, c8 = (c5 << 3) | (c5 >> 2); o |= (uint16_t)((std::min<uint32_t>(c8 + d, 255u) >> 3) << sh); }
    return o; }
static int nlogGL = 0; static uint32_t nlogGLPh = 0xFFFFFFFFu;
static Cnt c[2];
static thread_local int32_t t_rect[4] = { 0, 0, 0, 0 };
// s7553 class GM: per out-of-rect rtPx pixel (both kinds), is the column inside the pair's raw (pre-scissor) draw union / scissor
// union, and does post equal what RT64 itself wrote at this span's previous writeback (last) -> RT64 re-emits its own earlier output
// although RAM moved on (pre != last) = stale native; post outside every draw and != last = foreign content.
static thread_local int32_t t_raw[8] = { 0, 0, 0, 0, 0, 0, 0, 0 }; // rawL rawR rawT rawB scL scR scT scB
struct GM { uint64_t rt = 0, rawIn = 0, rawRowIn = 0, scIn = 0, hasLast = 0, eqLast = 0, eqLastMoved = 0, dark = 0, bright = 0, zd1 = 0, zd4 = 0, zd64 = 0, zbig = 0, wchg = 0, wb = 0, noRaw = 0, near1 = 0, zSameZ = 0, preIsLast = 0; };
static std::vector<uint8_t> g_shadow, g_shadowOk; // s7553 v2: per-byte last value RT64 wrote back (16 MB), any geometry
static GM gm[2];
static std::vector<std::pair<uint32_t, uint32_t>> g_prevW; // phys -> width of the previous writeback there
static inline bool bpp_ok_s7553(uint32_t bytes, uint32_t rows, uint32_t width) { return rows && width && (bytes / rows) / width == 2 && (bytes / rows) % 2 == 0; }
static int nlogGM = 0; static uint32_t nlogGMPh = 0xFFFFFFFFu;
static thread_local std::vector<uint8_t> t_pre;
static thread_local uint32_t t_prePhys = 0, t_preBytes = 0;
static std::chrono::steady_clock::time_point t0 = std::chrono::steady_clock::now(), tlast = t0;
static int nlog = 0; static uint32_t nlogPh = 0xFFFFFFFFu;
static void report(bool force) {
    const auto now = std::chrono::steady_clock::now();
    if (!force && std::chrono::duration<double>(now - tlast).count() < 5.0) return;
    tlast = now;
    const double t = std::chrono::duration<double>(now - t0).count();
    for (int k = 0; k < 2; k++) { const Cnt& x = c[k];
        std::fprintf(stderr, "[s7551] t=%.1f ph=%u kind=%s checks=%llu spans=%zu wb=%llu nosnap=%llu bytes=%llu gwb=%llu gch=%llu gchIn=%llu gchOut=%llu "
            "cwb=%llu clob=%llu clobIn=%llu clobOut=%llu revert=%llu rtOut=%llu plants=%llu pseen=%llu pclob=%llu\n", t, rs64_phase_ord(), k ? "Z" : "C",
            (unsigned long long)checks, spans.size(), (unsigned long long)x.wb, (unsigned long long)x.nosnap, (unsigned long long)x.bytes,
            (unsigned long long)x.gwb, (unsigned long long)x.gch, (unsigned long long)x.gchIn, (unsigned long long)x.gchOut, (unsigned long long)x.cwb,
            (unsigned long long)x.clob, (unsigned long long)x.clobIn, (unsigned long long)x.clobOut, (unsigned long long)x.revert,
            (unsigned long long)x.rtOut, (unsigned long long)x.plants, (unsigned long long)x.pseen, (unsigned long long)x.pclob);
        c[k] = Cnt{}; }
    checks = 0;
    for (int k = 0; k < 2; k++) { const GM& m = gm[k];
        std::fprintf(stderr, "[s7553] t=%.1f ph=%u kind=%s wb=%llu rt=%llu rawIn=%llu rawRowIn=%llu scIn=%llu noRaw=%llu hasLast=%llu eqLast=%llu eqLastMoved=%llu dark=%llu bright=%llu zd1=%llu zd4=%llu zd64=%llu zbig=%llu wchg=%llu near1=%llu zSameZ=%llu preIsLast=%llu\n",
            t, rs64_phase_ord(), k ? "Z" : "C", (unsigned long long)m.wb, (unsigned long long)m.rt, (unsigned long long)m.rawIn, (unsigned long long)m.rawRowIn, (unsigned long long)m.scIn,
            (unsigned long long)m.noRaw, (unsigned long long)m.hasLast, (unsigned long long)m.eqLast, (unsigned long long)m.eqLastMoved, (unsigned long long)m.dark, (unsigned long long)m.bright,
            (unsigned long long)m.zd1, (unsigned long long)m.zd4, (unsigned long long)m.zd64, (unsigned long long)m.zbig, (unsigned long long)m.wchg, (unsigned long long)m.near1, (unsigned long long)m.zSameZ, (unsigned long long)m.preIsLast);
        gm[k] = GM{}; }
    { const GL& g = gl;
      std::fprintf(stderr, "[s7552] t=%.1f ph=%u outPx=%llu rtPx=%llu mPat=%llu mAny=%llu mZero=%llu unm=%llu alpha=%llu up=%llu down=%llu d1=%llu d2=%llu d3=%llu "
          "e0=%llu e1=%llu e2=%llu e4=%llu e16=%llu inChg=%llu inAny=%llu b4=%llu wbPat=%llu,%llu,%llu,%llu,%llu rtPat=%llu,%llu,%llu,%llu,%llu\n", t, rs64_phase_ord(),
          (unsigned long long)g.outPx, (unsigned long long)g.rtPx, (unsigned long long)g.mPat, (unsigned long long)g.mAny, (unsigned long long)g.mZero,
          (unsigned long long)g.unm, (unsigned long long)g.alpha, (unsigned long long)g.up, (unsigned long long)g.down, (unsigned long long)g.d1,
          (unsigned long long)g.d2, (unsigned long long)g.d3, (unsigned long long)g.e0, (unsigned long long)g.e1, (unsigned long long)g.e2,
          (unsigned long long)g.e4, (unsigned long long)g.e16, (unsigned long long)g.inChg, (unsigned long long)g.inAny, (unsigned long long)g.b4,
          (unsigned long long)g.wbPat[0], (unsigned long long)g.wbPat[1], (unsigned long long)g.wbPat[2], (unsigned long long)g.wbPat[3], (unsigned long long)g.wbPat[4],
          (unsigned long long)g.rtPat[0], (unsigned long long)g.rtPat[1], (unsigned long long)g.rtPat[2], (unsigned long long)g.rtPat[3], (unsigned long long)g.rtPat[4]);
      std::sort(glk.begin(), glk.end(), [](const GLKey& a, const GLKey& b) { return a.n > b.n; });
      for (size_t i = 0; i < glk.size() && i < 8; i++) if (glk[i].n)
          std::fprintf(stderr, "[s7552-key] t=%.1f phys=0x%06X w=%u rows=%u rect=%d-%d pat=%d rtPx=%llu\n", t, glk[i].phys, glk[i].w, glk[i].rows, glk[i].rl, glk[i].rr, glk[i].pat, (unsigned long long)glk[i].n);
      gl = GL{}; glk.clear(); }
    std::fflush(stderr);
}
static void check(uint8_t* rd) {
    if (!on || !rd) return;
    std::lock_guard<std::mutex> lk(mu);
    ++seq; ++checks;
    size_t total = 0;
    for (size_t i = 0; i < spans.size();) { // drop spans unused for 600 checks
        if (seq - spans[i].used > 600) { spans.erase(spans.begin() + i); continue; } ++i; }
    Span* best = nullptr;
    for (Span& s : spans) {
        if (total + s.bytes > (6u << 20)) { s.seq = 0; continue; }
        total += s.bytes; s.snap.resize(s.bytes); std::memcpy(s.snap.data(), rd + s.phys, s.bytes); s.seq = seq; s.plantAt = 0xFFFFFFFFu;
        if (s.kind == 0 && s.width && s.rows && (!best || s.used > best->used)) best = &s;
    }
    g_plants.clear();
    if (plant && (seq % 16) == 0) for (Span& q : spans) { // every fresh span gets one 4-byte plant (outside its last rect when it can)
        if (q.seq != seq || !q.width || !q.rows) continue;
        const uint32_t rowB = q.bytes / q.rows, bpp = rowB / q.width ? rowB / q.width : 1;
        uint32_t col = q.width / 2;
        if (q.rr < (int32_t)q.width - 2) col = q.width - 2; else if (q.rl > 2) col = 0;
        const uint32_t a = q.phys + (((q.rows / 2) * rowB + col * bpp) & ~3u);
        bool dup = false; for (uint32_t p : g_plants) if (a < p + 4 && p < a + 4) dup = true;
        if (dup || a + 4 > q.phys + q.bytes) continue;
        for (int b = 0; b < 4; b++) rd[a + b] ^= 0x5A;
        g_plants.push_back(a); c[q.kind].plants++;
        { static uint32_t ph0 = 0xFFFFFFFFu; static int n = 0; const uint32_t ph = rs64_phase_ord(); if (ph != ph0) { ph0 = ph; n = 0; }
          if (q.kind == 1 && n++ < 4) std::fprintf(stderr, "[s7551-plant] ph=%u seq=%llu Z addr=0x%06X span=0x%06X+%u w=%u rows=%u\n", ph, (unsigned long long)seq, a, q.phys, q.bytes, q.width, q.rows); }
    }
    (void)best;
}
static void pre(uint8_t* rd, uint32_t phys, uint32_t bytes) {
    if (!on || !rd || !bytes || (uint64_t)phys + bytes > 0x1000000u) return;
    t_pre.resize(bytes); std::memcpy(t_pre.data(), rd + phys, bytes); t_prePhys = phys; t_preBytes = bytes;
}
static void post(uint8_t* rd, uint32_t phys, uint32_t bytes, uint32_t kind, uint32_t width, uint32_t rows) {
    if (!on || !rd || !bytes || !rows || !width || kind > 1 || (uint64_t)phys + bytes > 0x1000000u) return;
    if (t_prePhys != phys || t_preBytes != bytes) return;
    std::lock_guard<std::mutex> lk(mu);
    Cnt& x = c[kind]; ++x.wb;
    { static uint32_t ph0 = 0xFFFFFFFFu; static int n = 0; const uint32_t ph = rs64_phase_ord(); if (ph != ph0) { ph0 = ph; n = 0; }
      if (kind == 1 && n++ < 6) std::fprintf(stderr, "[s7551-zwb] ph=%u seq=%llu phys=0x%06X bytes=%u w=%u rows=%u plants=%zu\n", ph, (unsigned long long)seq, phys, bytes, width, rows, g_plants.size()); }
    const int32_t rl = t_rect[kind * 2], rr = t_rect[kind * 2 + 1];
    Span* s = nullptr;
    for (Span& q : spans) if (q.seq == seq && q.phys <= phys && phys + bytes <= q.phys + q.bytes) { s = &q; break; }
    if (!s) {
        ++x.nosnap;
        Span* ex = nullptr; for (Span& q : spans) if (q.phys == phys && q.kind == kind) { ex = &q; break; }
        if (!ex && spans.size() < 16) { spans.emplace_back(); ex = &spans.back(); }
        if (ex) { ex->phys = phys; ex->bytes = std::max(ex->bytes, bytes); ex->kind = kind; ex->width = width; ex->rows = rows; ex->rl = rl; ex->rr = rr; ex->used = seq; ex->seq = 0; }
    } else {
        s->used = seq; if (s->phys == phys) { s->kind = kind; s->width = width; s->rows = rows; s->rl = rl; s->rr = rr; }
        const uint32_t rowB = bytes / rows, bpp = rowB / width ? rowB / width : 1, off = phys - s->phys;
        const uint8_t* sv = s->snap.data() + off; const uint8_t* pv = t_pre.data(); const uint8_t* qv = rd + phys;
        x.bytes += bytes;
        uint64_t g = 0, cl = 0; uint32_t firstG = 0xFFFFFFFFu, firstC = 0xFFFFFFFFu;
        for (uint32_t i = 0; i < bytes; i++) {
            const uint32_t rel = ((phys + i) ^ 3u) - phys; const uint32_t col = (rel % rowB) / bpp; const bool in = (int32_t)col >= rl && (int32_t)col < rr;
            bool isPlant = false; for (uint32_t p : g_plants) if (phys + i >= p && phys + i < p + 4) { isPlant = true; break; }
            if (pv[i] != sv[i]) {
                if (isPlant) { x.pseen++; if (qv[i] != pv[i]) x.pclob++; continue; }
                ++g; (in ? x.gchIn : x.gchOut)++; if (firstG == 0xFFFFFFFFu) firstG = i;
                if (qv[i] != pv[i]) { ++cl; (in ? x.clobIn : x.clobOut)++; if (qv[i] == sv[i]) x.revert++; if (firstC == 0xFFFFFFFFu) firstC = i; }
            } else if (qv[i] != pv[i] && !in) x.rtOut++;
        }
        x.gch += g; x.clob += cl; if (g) x.gwb++; if (cl) x.cwb++;
        if (kind == 0) { // s7552 class GL
            const int32_t pat = t_dith >= 0 && t_dith <= 3 ? t_dith : 4; gl.wbPat[pat]++;
            const uint32_t base = g_s7493_next_base.load();
            if (bpp != 2 || (phys & 3u) || rowB % 2) gl.b4++;
            else {
                const uint32_t y0 = (base != 0xFFFFFFFFu && base <= phys) ? (phys - base) / rowB : 0;
                uint64_t keyN = 0;
                for (uint32_t L = 0; L + 2 <= bytes; L += 2) {
                    const uint32_t A = ((phys + L) ^ 2u) - phys; // stored halfword offset
                    if (A + 2 > bytes) continue;  // s7560 class AO: bytes % 4 == 2 -> last L has A = L + 2 = bytes (2-byte over-read of t_pre / snap; s7553 loop already guards this)
                    uint16_t sv16, pv16, qv16; std::memcpy(&sv16, s->snap.data() + off + A, 2); std::memcpy(&pv16, t_pre.data() + A, 2); std::memcpy(&qv16, rd + phys + A, 2);
                    const uint32_t col = (L % rowB) / 2, y = y0 + L / rowB; const bool in = (int32_t)col >= rl && (int32_t)col < rr;
                    bool isPlant = false; for (uint32_t p : g_plants) if (phys + L + 2 > p && phys + L < p + 4) { isPlant = true; break; }
                    if (isPlant) continue;
                    bool any = false; for (uint32_t d = 0; d < 8 && !any; d++) any = F(pv16, d) == qv16;
                    if (in) { if (qv16 != pv16) { gl.inChg++; if (any) gl.inAny++; } continue; }
                    gl.outPx++;
                    if (pv16 != sv16 || qv16 == pv16) continue;
                    gl.rtPx++; gl.rtPat[pat]++; keyN++;
                    const uint32_t di = ((y & 3u) << 2) | (col & 3u);
                    const uint32_t dp = pat == 0 ? kMS[di] : pat == 1 ? kBY[di] : 0u;
                    const bool mp = (pat == 0 || pat == 1 || pat == 3) ? F(pv16, dp) == qv16 : any;
                    if (mp) gl.mPat++; if (any) gl.mAny++; if (F(pv16, 0) == qv16) gl.mZero++;
                    if ((pv16 ^ qv16) & 1u) gl.alpha++;
                    int dmax = 0; bool up = false, down = false;
                    for (int sh = 11; sh >= 1; sh -= 5) { const int dd = (int)((qv16 >> sh) & 31u) - (int)((pv16 >> sh) & 31u); if (dd > 0) up = true; if (dd < 0) down = true; dmax = std::max(dmax, std::abs(dd)); }
                    if (up) gl.up++; if (down) gl.down++; if (dmax == 1) gl.d1++; else if (dmax == 2) gl.d2++; else if (dmax >= 3) gl.d3++;
                    const int32_t ed = std::min(std::abs((int32_t)col - rl), std::abs((int32_t)col - (rr - 1)));
                    if (ed == 0) gl.e0++; else if (ed == 1) gl.e1++; else if (ed < 4) gl.e2++; else if (ed < 16) gl.e4++; else gl.e16++;
                    if (!any) { gl.unm++;
                        const uint32_t ph = rs64_phase_ord(); if (ph != nlogGLPh) { nlogGLPh = ph; nlogGL = 0; }
                        if (nlogGL++ < 16) std::fprintf(stderr, "[s7552-unm] ph=%u phys=0x%06X w=%u rows=%u rect=%d-%d pat=%d x=%u y=%u pre=%04X post=%04X\n", ph, phys, width, rows, rl, rr, pat, col, y, pv16, qv16); }
                }
                if (keyN) { bool f = false; for (GLKey& k : glk) if (k.phys == phys && k.w == width && k.rows == rows && k.rl == rl && k.rr == rr && k.pat == pat) { k.n += keyN; f = true; break; }
                    if (!f && glk.size() < 256) glk.push_back(GLKey{ phys, width, rows, rl, rr, pat, keyN }); }
            }
        }
        const uint32_t ph = rs64_phase_ord(); if (ph != nlogPh) { nlogPh = ph; nlog = 0; }
        if (g && nlog++ < 24) {
            const uint32_t f = firstC != 0xFFFFFFFFu ? firstC : firstG, rel = ((phys + f) ^ 3u) - phys, fw = (phys + f) & ~3u;
            uint32_t sw = 0, pw = 0, qw = 0;  /* s7560 class AO: fw = (phys+f)&~3 can start before phys (unaligned phys) or end past phys+bytes (bytes % 4 != 0) */
            if (fw >= phys && (uint64_t)fw + 4u <= (uint64_t)phys + bytes) { std::memcpy(&sw, s->snap.data() + (fw - s->phys), 4); std::memcpy(&pw, rd + fw, 4); std::memcpy(&qw, t_pre.data() + (fw - phys), 4); }
            std::fprintf(stderr, "[s7551-ev] ph=%u kind=%s phys=0x%06X bytes=%u w=%u rows=%u rect=%d-%d gch=%llu clob=%llu first=0x%06X row=%u col=%u snap=%08X pre=%08X post=%08X\n",
                ph, kind ? "Z" : "C", phys, bytes, width, rows, rl, rr, (unsigned long long)g, (unsigned long long)cl, fw, rel / rowB, (rel % rowB) / bpp, sw, qw, pw);
        }
    }
    { // s7553 class GM (uses s, t_pre, the span's previous writeback output)
        GM& m = gm[kind]; ++m.wb;
        const uint32_t ph = rs64_phase_ord(); if (ph != nlogGMPh) { nlogGMPh = ph; nlogGM = 0; }
        bool fw = false; for (auto& pw : g_prevW) if (pw.first == phys) { fw = true; if (pw.second != width) { ++m.wchg; if (nlogGM++ < 24) std::fprintf(stderr, "[s7553-w] ph=%u kind=%s phys=0x%06X w=%u prevW=%u rows=%u\n", ph, kind ? "Z" : "C", phys, width, pw.second, rows); } pw.second = width; break; }
        if (!fw && g_prevW.size() < 64) g_prevW.push_back({ phys, width });
        if (g_shadow.empty()) { g_shadow.assign(0x1000000u, 0); g_shadowOk.assign(0x1000000u, 0); }
        const int32_t rl = t_rect[kind * 2], rr = t_rect[kind * 2 + 1];
        const bool rawNull = t_raw[0] == 0 && t_raw[1] == 0;
        if (s && bpp_ok_s7553(bytes, rows, width) && !(phys & 1u)) {
            const uint32_t rowB = bytes / rows, off = phys - s->phys, base = g_s7493_next_base.load();
            const uint32_t y0 = (kind == 0 && base != 0xFFFFFFFFu && base <= phys) ? (phys - base) / rowB : 0;
            for (uint32_t L = 0; L + 2 <= bytes; L += 2) {
                const uint32_t A = ((phys + L) ^ 2u) - phys; if (A + 2 > bytes) continue;
                uint16_t sv16, pv16, qv16; std::memcpy(&sv16, s->snap.data() + off + A, 2); std::memcpy(&pv16, t_pre.data() + A, 2); std::memcpy(&qv16, rd + phys + A, 2);
                const int32_t col = (int32_t)((L % rowB) / 2), y = (int32_t)(y0 + L / rowB);
                if (col >= rl && col < rr) continue;
                if (pv16 != sv16 || qv16 == pv16) continue;
                bool isPlant = false; for (uint32_t p : g_plants) if (phys + L + 2 > p && phys + L < p + 4) { isPlant = true; break; }
                if (isPlant) continue;
                ++m.rt; if (rawNull) ++m.noRaw;
                const bool rin = !rawNull && col >= t_raw[0] && col < t_raw[1]; if (rin) { ++m.rawIn; if (y >= t_raw[2] && y < t_raw[3]) ++m.rawRowIn; }
                if (col >= t_raw[4] && col < t_raw[5]) ++m.scIn;
                uint16_t lv16 = 0; const bool lastOk = g_shadowOk[phys + A] && g_shadowOk[phys + A + 1];
                if (lastOk) { ++m.hasLast; std::memcpy(&lv16, g_shadow.data() + phys + A, 2); if (lv16 == pv16) ++m.preIsLast; if (lv16 == qv16) { ++m.eqLast; if (pv16 != lv16) ++m.eqLastMoved; }
                    if (kind == 0) { int dm = 0; for (int sh = 11; sh >= 1; sh -= 5) dm = std::max(dm, std::abs((int)((qv16 >> sh) & 31u) - (int)((lv16 >> sh) & 31u))); if (dm <= 1) ++m.near1; } }
                if (kind == 1 && (qv16 >> 2) == (pv16 >> 2)) ++m.zSameZ;
                if (kind == 0) { bool up = false, dn = false; for (int sh = 11; sh >= 1; sh -= 5) { const int dd = (int)((qv16 >> sh) & 31u) - (int)((pv16 >> sh) & 31u); if (dd > 0) up = true; if (dd < 0) dn = true; } if (dn && !up) ++m.dark; if (up && !dn) ++m.bright; }
                else { const int dz = std::abs((int)qv16 - (int)pv16); if (dz <= 1) ++m.zd1; else if (dz <= 4) ++m.zd4; else if (dz <= 64) ++m.zd64; else ++m.zbig; }
                if (nlogGM++ < 24) std::fprintf(stderr, "[s7553-px] ph=%u kind=%s phys=0x%06X w=%u rows=%u x=%d y=%d rect=%d-%d raw=%d-%d,%d-%d sc=%d-%d,%d-%d snap=%04X pre=%04X post=%04X last=%s%04X\n",
                    ph, kind ? "Z" : "C", phys, width, rows, col, y, rl, rr, t_raw[0], t_raw[1], t_raw[2], t_raw[3], t_raw[4], t_raw[5], t_raw[6], t_raw[7], sv16, pv16, qv16, lastOk ? "" : "na:", lv16);
            }
        }
        std::memcpy(g_shadow.data() + phys, rd + phys, bytes); std::memset(g_shadowOk.data() + phys, 1, bytes);
    }
    for (Span& q : spans) if (q.seq == seq && q.phys < phys + bytes && phys < q.phys + q.bytes) { // RT64's own output is not a guest change
        const uint32_t a = std::max(q.phys, phys), e = std::min(q.phys + q.bytes, phys + bytes);
        std::memcpy(q.snap.data() + (a - q.phys), rd + a, e - a);
        if (q.plantAt >= a && q.plantAt < e) q.plantAt = 0xFFFFFFFFu;
    }
    for (size_t k = 0; k < g_plants.size();) { if (g_plants[k] < phys + bytes && phys < g_plants[k] + 4) g_plants.erase(g_plants.begin() + k); else ++k; }
    report(false);
}
} // namespace s7551
extern "C" void rs64_s7551_gk_check(uint8_t* rd) { s7551::check(rd); }
extern "C" void rs64_s7553_rects(int32_t a, int32_t b, int32_t c2, int32_t d, int32_t e, int32_t f, int32_t g, int32_t h) {
    s7551::t_raw[0] = a; s7551::t_raw[1] = b; s7551::t_raw[2] = c2; s7551::t_raw[3] = d; s7551::t_raw[4] = e; s7551::t_raw[5] = f; s7551::t_raw[6] = g; s7551::t_raw[7] = h; } // s7553 class GM
extern "C" void rs64_s7552_dith(int32_t p) { s7551::t_dith = p; } // s7552: colorFb->bestDitherPattern() of the next colour writeback
extern "C" void rs64_s7551_gk_rect(int32_t cl, int32_t cr, int32_t zl, int32_t zr) {
    s7551::t_rect[0] = cl; s7551::t_rect[1] = cr; s7551::t_rect[2] = zl; s7551::t_rect[3] = zr; }

// s6938 G1e H-wb-dead instrument (ROGUESQ_G1E_WBW=1, off by default). After each RT64 colour/depth
// writeback into RDRAM, the written pages are made PROT_NONE. The first touch of each page faults here:
// we record phys, host pc/lr offset (resolve with atos) and read/write (ESR WnR), unprotect, retry.
// At the next writeback over the same range the range is scored live (read in between) or dead
// (overwritten unread, all interior pages still armed) or unk. Control: ROGUESQ_G1E_WBW_CTL=1 reads
// one byte of an armed range once a second from the reporter (tagged ctl), so the trap path must fire.
#ifndef _WIN32
namespace {
constexpr uint32_t kWbwPage = 16384, kWbwPages = 0x1000000u / kWbwPage, kWbwMax = 32, kWbwRing = 8192;
struct WbwRange { std::atomic<uint32_t> start{0}, end{0}; uint32_t kind = 0, width = 0, rows = 0; bool active = false;
    std::atomic<uint32_t> reads{0}, writes{0}, ctlReads{0}; };
struct WbwEv { uint32_t phys, idx, wr, ctl; uint64_t pc, lr; };
struct WbwKey { uint32_t kind, addr, width; bool operator<(const WbwKey& o) const { return std::tie(kind, addr, width) < std::tie(o.kind, o.addr, o.width); } };
struct WbwStat { uint64_t wb = 0, live = 0, dead = 0, unk = 0, readsN = 0, ctl = 0, wrOnly = 0; };
std::atomic<uint8_t*> g_wbw_rd{nullptr};
std::atomic<uint8_t> g_wbw_armed[kWbwPages];
std::atomic<uint8_t> g_wbw_ever[kWbwPages];
WbwRange g_wbw_r[kWbwMax];
WbwEv g_wbw_ring[kWbwRing];
std::atomic<uint32_t> g_wbw_head{0};
std::atomic<uint64_t> g_wbw_edge{0}, g_wbw_drop{0};
uint32_t g_wbw_tail = 0;
volatile __thread int t_wbw_ctl = 0;
volatile __thread int t_wbw_self = 0; // RT64 own hash reads: counted, page re-armed after
__thread uint32_t t_wbw_rearm[1024]; __thread uint32_t t_wbw_rearmN = 0;
std::atomic<uint64_t> g_wbw_selfN{0};
std::map<WbwKey, WbwStat> g_wbw_stat;
std::map<std::tuple<uint32_t, uint64_t, uint64_t, uint32_t>, uint64_t> g_wbw_pcs; // kind, pc, lr, wr
uint64_t g_wbw_slide = 0;
int wbw_on() { static const int v = [] { const char* e = std::getenv("ROGUESQ_G1E_WBW"); return (e && *e && *e != '0') ? 1 : 0; }(); return v; }
}

static bool wbw_try_handle_fault(siginfo_t* info, void* ucontext_raw) {
    if (!wbw_on() || !info) return false;
    uint8_t* rd = g_wbw_rd.load(std::memory_order_acquire);
    uintptr_t fa = (uintptr_t)info->si_addr;
    if (!rd || fa < (uintptr_t)rd || fa >= (uintptr_t)rd + 0x1000000u) return false;
    uint32_t phys = (uint32_t)(fa - (uintptr_t)rd), pg = phys / kWbwPage;
    if (!g_wbw_ever[pg].load(std::memory_order_acquire)) return false;
    mprotect(rd + (size_t)pg * kWbwPage, kWbwPage, PROT_READ | PROT_WRITE);
    if (t_wbw_self) { g_wbw_selfN.fetch_add(1); if (t_wbw_rearmN < 1024) t_wbw_rearm[t_wbw_rearmN++] = pg; return true; }
    if (!g_wbw_armed[pg].exchange(0)) return true; // concurrent second fault, page already released
    ucontext_t* uc = (ucontext_t*)ucontext_raw;
    uint64_t pc = 0, lr = 0; uint32_t wr = 0;
    if (uc && uc->uc_mcontext) { pc = uc->uc_mcontext->__ss.__pc; lr = uc->uc_mcontext->__ss.__lr; wr = (uc->uc_mcontext->__es.__esr >> 6) & 1u; }
    uint32_t idx = kWbwMax;
    for (uint32_t i = 0; i < kWbwMax; i++) {
        uint32_t s = g_wbw_r[i].start.load(std::memory_order_acquire), e = g_wbw_r[i].end.load(std::memory_order_acquire);
        if (e > s && phys >= s && phys < e) { idx = i; break; }
    }
    if (idx == kWbwMax) g_wbw_edge.fetch_add(1);
    else if (t_wbw_ctl) g_wbw_r[idx].ctlReads.fetch_add(1);
    else if (wr) g_wbw_r[idx].writes.fetch_add(1);
    else g_wbw_r[idx].reads.fetch_add(1);
    uint32_t h = g_wbw_head.fetch_add(1);
    if (h - g_wbw_tail < kWbwRing) g_wbw_ring[h % kWbwRing] = WbwEv{ phys, idx, wr, (uint32_t)t_wbw_ctl, pc, lr };
    else g_wbw_drop.fetch_add(1);
    return true;
}

static void wbw_close_range(uint32_t i) {
    WbwRange& r = g_wbw_r[i];
    if (!r.active) return;
    uint32_t s = r.start.load(), e = r.end.load();
    uint32_t p0 = (s + kWbwPage - 1) / kWbwPage, p1 = e / kWbwPage; // interior pages
    bool intact = true;
    for (uint32_t p = p0; p < p1; p++) if (!g_wbw_armed[p].load()) { intact = false; break; }
    WbwStat& st = g_wbw_stat[WbwKey{ r.kind, s, r.width }];
    uint32_t rd = r.reads.load(), ctl = r.ctlReads.load();
    st.readsN += rd; st.ctl += ctl;
    if (rd > 0) st.live++;
    else if (intact && p1 > p0 && ctl == 0) st.dead++;
    else if (r.writes.load() > 0 && ctl == 0) st.wrOnly++;
    else st.unk++;
    r.active = false; r.start.store(0); r.end.store(0);
}

static void wbw_report(uint8_t* rd) {
    static auto t0 = std::chrono::steady_clock::now();
    static auto last = t0;
    auto now = std::chrono::steady_clock::now();
    if (now - last < std::chrono::seconds(1)) return;
    last = now;
    static const bool s_ctl = [] { const char* e = std::getenv("ROGUESQ_G1E_WBW_CTL"); return e && *e && *e != '0'; }();
    if (s_ctl) { // positive control: touch the middle of the first active colour range
        for (uint32_t i = 0; i < kWbwMax; i++) if (g_wbw_r[i].active) {
            uint32_t m = (g_wbw_r[i].start.load() + g_wbw_r[i].end.load()) / 2;
            t_wbw_ctl = 1; volatile uint8_t v = rd[m]; (void)v; t_wbw_ctl = 0; break;
        }
    }
    uint32_t h = g_wbw_head.load();
    if (h - g_wbw_tail > kWbwRing) g_wbw_tail = h - kWbwRing;
    for (; g_wbw_tail != h; g_wbw_tail++) {
        const WbwEv& ev = g_wbw_ring[g_wbw_tail % kWbwRing];
        uint32_t kind = ev.idx < kWbwMax ? g_wbw_r[ev.idx].kind : 9u;
        if (ev.ctl) kind = 8u;
        g_wbw_pcs[{ kind, ev.pc - g_wbw_slide, ev.lr - g_wbw_slide, ev.wr }]++;
    }
    double t = std::chrono::duration<double>(now - t0).count();
    for (auto& kv : g_wbw_stat) {
        const WbwStat& s = kv.second;
        std::fprintf(stderr, "[wbw] t=%.0f %s addr=%06X w=%u wb=%llu live=%llu dead=%llu unk=%llu wronly=%llu reads=%llu ctl=%llu\n", t,
            kv.first.kind ? "Z" : "C", kv.first.addr, kv.first.width, (unsigned long long)s.wb, (unsigned long long)s.live, (unsigned long long)s.dead,
            (unsigned long long)s.unk, (unsigned long long)s.wrOnly, (unsigned long long)s.readsN, (unsigned long long)s.ctl);
    }
    std::fprintf(stderr, "[wbw] t=%.0f edge=%llu drop=%llu self=%llu\n", t, (unsigned long long)g_wbw_edge.load(), (unsigned long long)g_wbw_drop.load(), (unsigned long long)g_wbw_selfN.load());
    g_wbw_stat.clear();
    static int n = 0;
    if (++n % 10 == 0) {
        for (auto& kv : g_wbw_pcs) std::fprintf(stderr, "[wbw-pc] t=%.0f kind=%u pc=0x%llx lr=0x%llx wr=%u n=%llu\n", t, std::get<0>(kv.first),
            (unsigned long long)std::get<1>(kv.first), (unsigned long long)std::get<2>(kv.first), std::get<3>(kv.first), (unsigned long long)kv.second);
        g_wbw_pcs.clear();
    }
    std::fflush(stderr);
}

// RT64 self-check reads (hashTracking, checkRDRAM storeRAM/checkRAM): on=1 tags faults as self,
// on=0 re-protects the pages those reads released so a later game reader still faults.
extern "C" void rs64_wbw_self(int on) {
    if (!wbw_on()) return;
    if (on) { t_wbw_rearmN = 0; t_wbw_self = 1; return; }
    t_wbw_self = 0;
    uint8_t* rd = g_wbw_rd.load();
    for (uint32_t i = 0; i < t_wbw_rearmN && rd; i++) {
        uint32_t pg = t_wbw_rearm[i];
        if (g_wbw_armed[pg].load()) mprotect(rd + (size_t)pg * kWbwPage, kWbwPage, PROT_NONE);
    }
    t_wbw_rearmN = 0;
}

// Called on the RT64 thread immediately before copyNativeToRAM of [phys, phys+bytes).
extern "C" void rs64_s7541_span(int, const uint8_t*, uint32_t, uint32_t); extern "C" int rs64_s7539_on; // s7541
extern "C" void rs64_wbw_pre(uint8_t* rd, uint32_t phys, uint32_t bytes) {
    s7551::pre(rd, phys, bytes); // s7551
    if (rs64_s7539_on && rd && bytes) rs64_s7541_span(2, rd, phys, bytes); // s7541
    if (!wbw_on() || !rd || bytes == 0 || (uint64_t)phys + bytes > 0x1000000u) return;
    if (!g_wbw_rd.load()) {
        for (uint32_t i = 0; i < _dyld_image_count(); i++) if (_dyld_get_image_header(i)->filetype == MH_EXECUTE) { g_wbw_slide = (uint64_t)_dyld_get_image_vmaddr_slide(i); break; }
        std::fprintf(stderr, "[wbw] armed slide=0x%llx (atos: pc - slide is the unslid address)\n", (unsigned long long)g_wbw_slide);
        g_wbw_rd.store(rd);
    }
    wbw_report(rd);
    uint32_t e = phys + bytes;
    for (uint32_t i = 0; i < kWbwMax; i++) {
        uint32_t s0 = g_wbw_r[i].start.load(), e0 = g_wbw_r[i].end.load();
        if (g_wbw_r[i].active && s0 < e && phys < e0) wbw_close_range(i);
    }
    for (uint32_t p = phys / kWbwPage; p <= (e - 1) / kWbwPage; p++) {
        if (g_wbw_armed[p].exchange(0)) mprotect(rd + (size_t)p * kWbwPage, kWbwPage, PROT_READ | PROT_WRITE);
    }
}

// Called right after copyNativeToRAM: arm the range.
extern "C" void rs64_s7491_hst(uint32_t a, uint32_t w, const char* kind);  /* s7492 class EQ: RT64 writeback -> fn=os_rt64fb */
static void s7497_wb(uint32_t, uint32_t, uint32_t);
extern "C" void rs64_wbw_post(uint8_t* rd, uint32_t phys, uint32_t bytes, uint32_t kind, uint32_t width, uint32_t rows) {
    s7551::post(rd, phys, bytes, kind, width, rows); // s7551
    if (rs64_s7539_on && rd && bytes) rs64_s7541_span(3, rd, phys, bytes); // s7541
    {   static std::atomic<uint64_t> n{0}; const uint64_t k = ++n;  /* s7492: first-call / periodic marker = the hook's reach control */
        if (k == 1 || (k & (k - 1)) == 0) std::fprintf(stderr, "[s7492] rt64 writeback #%llu phys=%06X bytes=%u kind=%u w=%u rows=%u\n",
                                                       (unsigned long long)k, phys, bytes, kind, width, rows); }
    s7493_wb(phys, bytes, kind, width, rows); s7497_wb(phys, bytes, kind); s7498_wb(phys, bytes, kind, width, rows);
    s7501_wb(phys, bytes);  /* s7501 class EZ */
    if (bytes && phys < 0x1800000u) rs64_s7491_hst(0x80000000u | phys, bytes, "os_rt64fb");
    if (!wbw_on() || !rd || bytes == 0 || (uint64_t)phys + bytes > 0x1000000u) return;
    uint32_t slot = kWbwMax;
    for (uint32_t i = 0; i < kWbwMax; i++) if (!g_wbw_r[i].active) { slot = i; break; }
    if (slot == kWbwMax) { wbw_close_range(0); slot = 0; }
    WbwRange& r = g_wbw_r[slot];
    r.kind = kind; r.width = width; r.rows = rows; r.reads.store(0); r.writes.store(0); r.ctlReads.store(0);
    r.start.store(phys); r.end.store(phys + bytes); r.active = true;
    g_wbw_stat[WbwKey{ kind, phys, width }].wb++;
    uint32_t e = phys + bytes;
    for (uint32_t p = phys / kWbwPage; p <= (e - 1) / kWbwPage; p++) {
        g_wbw_ever[p].store(1);
        g_wbw_armed[p].store(1, std::memory_order_release);
        mprotect(rd + (size_t)p * kWbwPage, kWbwPage, PROT_NONE);
    }
}
#else
extern "C" void rs64_s7541_span(int, const uint8_t*, uint32_t, uint32_t); extern "C" int rs64_s7539_on; // s7541
extern "C" void rs64_wbw_pre(uint8_t* rd, uint32_t phys, uint32_t bytes) { s7551::pre(rd, phys, bytes); if (rs64_s7539_on && rd && bytes) rs64_s7541_span(2, rd, phys, bytes); }
extern "C" void rs64_wbw_self(int) {}
extern "C" void rs64_s7491_hst(uint32_t a, uint32_t w, const char* kind);
static void s7497_wb(uint32_t, uint32_t, uint32_t);
extern "C" void rs64_wbw_post(uint8_t* rd, uint32_t phys, uint32_t bytes, uint32_t kind, uint32_t width, uint32_t rows) { s7551::post(rd, phys, bytes, kind, width, rows); if (rs64_s7539_on && rd && bytes) rs64_s7541_span(3, rd, phys, bytes); s7493_wb(phys, bytes, kind, width, rows); s7501_wb(phys, bytes); s7497_wb(phys, bytes, kind); s7498_wb(phys, bytes, kind, width, rows); if (bytes && phys < 0x1800000u) rs64_s7491_hst(0x80000000u | phys, bytes, "os_rt64fb"); }
static bool wbw_try_handle_fault(void*, void*) { return false; }
#endif

// ROGUESQ_LOG_FL_ZERO_WATCH: macOS soft-watch on the fail136c freelist
// zero-node (default KSEG0 0x801F3CC0 → phys 0x1F3CC0). Polls 16-byte
// header every 250us; logs mutations + 5s heartbeat (positive control).
// Discriminates H-oob-store (write to zeros with guest_pc) vs allocator
// paths (pair with [fl-hdr-write]/[fl-zero-watch] from fixup). Override
// phys via ROGUESQ_FL_ZERO_ADDR=<hex offset into RDRAM>.
// s646: also drives mprotect arm for [fl-zero-fault] (see above).
static void start_fl_zero_poller() {
    static std::thread t{[]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        uint32_t slot = 0x1F3CC0u; /* 0x801F3CC0 & 0x7FFFFF */
        if (const char* e = std::getenv("ROGUESQ_FL_ZERO_ADDR")) {
            unsigned long v = strtoul(e, nullptr, 0);
            if (v > 0 && v < 0x2000000u) slot = (uint32_t)v;
        }
        slot &= 0x1FFFFFFu;  /* s6572: widened for RAMTOP>8MB */
#ifndef _WIN32
        g_flz_fault_rdram.store(rdram, std::memory_order_release);
        g_flz_fault_slot.store(slot, std::memory_order_relaxed);
        g_flz_fault_enabled.store(1, std::memory_order_release);
#endif
        auto rbyte = [&](uint32_t a) -> uint8_t {
            return rdram[(a & 0x1FFFFFF) ^ 3];
        };
        auto snap16 = [&](uint8_t out[16]) {
            for (int i = 0; i < 16; ++i) out[i] = rbyte(slot + (uint32_t)i);
        };
        auto be_u16 = [](const uint8_t* b) -> uint16_t {
            return (uint16_t)((b[0] << 8) | b[1]);
        };
        auto be_u32 = [](const uint8_t* b) -> uint32_t {
            return ((uint32_t)b[0] << 24) | ((uint32_t)b[1] << 16)
                 | ((uint32_t)b[2] << 8) | (uint32_t)b[3];
        };
        const bool flz_always = [] {
            const char* e = std::getenv("ROGUESQ_FL_ZERO_ALWAYS");
            return e && *e && *e != '0';
        }();
        uint8_t prev[16];
        snap16(prev);
        fprintf(stderr,
            "[fl-zero-poll] n=0 event=arm phys=0x%08X kseg=0x%08X bytes="
            "%02X%02X%02X%02X %02X%02X%02X%02X %02X%02X%02X%02X %02X%02X%02X%02X "
            "flags=0x%X size=0x%X fault_watch=%d\n",
            slot, slot | 0x80000000u,
            prev[0], prev[1], prev[2], prev[3],
            prev[4], prev[5], prev[6], prev[7],
            prev[8], prev[9], prev[10], prev[11],
            prev[12], prev[13], prev[14], prev[15],
            (unsigned)be_u16(prev), (unsigned)be_u32(prev + 4),
#ifndef _WIN32
            1
#else
            0
#endif
        );
        fflush(stderr);
        // Boot posctrl: arm while header is zeros so the first write to this
        // page produces [fl-zero-fault] (proves SEGV path LIVE in same run).
#ifndef _WIN32
        if (be_u16(prev) == 0 && be_u32(prev + 4) == 0) {
            g_flz_fault_want.store(1, std::memory_order_release); /* boot */
            fl_zero_fault_arm();
            fprintf(stderr,
                "[fl-zero-fault] event=arm_boot_zero slot=0x%X page=%zu\n",
                slot, fl_zero_page_size());
            fflush(stderr);
        }
#endif
#ifndef _WIN32
        if (flz_always) {
            g_flz_fault_want.store(2, std::memory_order_release);
            fl_zero_fault_arm();
            fprintf(stderr, "[fl-zero-fault] event=arm_always slot=0x%X\n", slot);
            fflush(stderr);
        }
#endif
        uint64_t n_change = 0;
        uint64_t n_poll = 0;
        uint64_t n_to_zero = 0;
        auto t0 = std::chrono::steady_clock::now();
        auto last_hb = t0;
        for (;;) {
            uint8_t cur[16];
            snap16(cur);
            ++n_poll;
            if (memcmp(cur, prev, 16) != 0) {
                ++n_change;
                auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                    std::chrono::steady_clock::now() - t0).count();
                uint16_t pf = be_u16(prev), cf = be_u16(cur);
                uint32_t psz = be_u32(prev + 4), csz = be_u32(cur + 4);
                const char* kind = "write";
                if (csz == 0 && (cf & 0x8u) == 0 && (psz != 0 || (pf & 0x3u) != 0)) {
                    kind = "to_zero";
                    ++n_to_zero;
                }
                fprintf(stderr,
                    "[fl-zero-poll] n=%llu event=%s t_ms=%lld phys=0x%08X "
                    "prev_f=0x%X prev_sz=0x%X cur_f=0x%X cur_sz=0x%X "
                    "prev=%02X%02X%02X%02X%02X%02X%02X%02X "
                    "cur=%02X%02X%02X%02X%02X%02X%02X%02X "
                    "guest_pc=0x%08X to_zero_n=%llu\n",
                    (unsigned long long)n_change, kind, (long long)ms, slot,
                    (unsigned)pf, psz, (unsigned)cf, csz,
                    prev[0], prev[1], prev[2], prev[3],
                    prev[4], prev[5], prev[6], prev[7],
                    cur[0], cur[1], cur[2], cur[3],
                    cur[4], cur[5], cur[6], cur[7],
                    (unsigned)g_rs64_last_guest_pc,
                    (unsigned long long)n_to_zero);
                // s643: host BT on to_zero. Poller is a side thread, so frames
                // are poller-local (Outcome B expected unless a host bulk path
                // is somehow on this thread). Posctrl = menu to_zero #1 prints
                // ≥1 [fl-zero-poll-bt] line. Cap 32 frames; rate-limit 16.
                // s644: also sample OTHER threads' stacks ([fl-zero-poll-gbt])
                // — only path that can name a guest writer from a side-thread
                // detect. Same rate-limit / to_zero gate.
#ifndef _WIN32
                if (kind[0] == 't' && n_to_zero <= 16) {
                    void* bt_frames[32];
                    int bt_n = backtrace(bt_frames, 32);
                    fprintf(stderr,
                        "[fl-zero-poll-bt] n=%llu to_zero_n=%llu frames=%d "
                        "guest_pc=0x%08X t_ms=%lld prev_f=0x%X prev_sz=0x%X\n",
                        (unsigned long long)n_change,
                        (unsigned long long)n_to_zero, bt_n,
                        (unsigned)g_rs64_last_guest_pc, (long long)ms,
                        (unsigned)pf, psz);
                    char** syms = backtrace_symbols(bt_frames, bt_n);
                    for (int bi = 0; bi < bt_n; ++bi) {
                        Dl_info dli;
                        const char* sname = nullptr;
                        if (dladdr(bt_frames[bi], &dli) && dli.dli_sname) {
                            sname = dli.dli_sname;
                        }
                        fprintf(stderr,
                            "[fl-zero-poll-bt]   [%2d] %s%s%s\n", bi,
                            sname ? sname : "",
                            sname ? " | " : "",
                            (syms && syms[bi]) ? syms[bi] : "?");
                    }
                    free(syms);
#if defined(__APPLE__) && defined(__aarch64__)
                    fl_zero_sample_game_threads(
                        n_change, n_to_zero, (long long)ms,
                        (unsigned)pf, (unsigned)psz);
#endif
                }
#endif
                fflush(stderr);
                memcpy(prev, cur, 16);
#ifndef _WIN32
                // Want mprotect arm only for freelist-shaped header (0x2/0x60)
                // — the s640 H-oob-store destroy window. Disarm on to_zero or
                // any other shape so boot/menu texture traffic is not trapped
                // after the boot-zero posctrl has fired.
                // want: 1=boot-zero, 2=freelist (s647 discriminates BT/SS rate).
                if ((cf == 0x2u && csz == 0x60u) || (flz_always && kind[0] != 't')) {
                    if (g_flz_fault_want.load(std::memory_order_relaxed) != 2) {
                        fprintf(stderr,
                            "[fl-zero-fault] event=arm_freelist t_ms=%lld "
                            "slot=0x%X f=0x2 sz=0x60\n",
                            (long long)ms, slot);
                        fflush(stderr);
                    }
                    g_flz_fault_want.store(2, std::memory_order_release);
                } else {
                    if (g_flz_fault_want.load(std::memory_order_relaxed)) {
                        // s647: on freelist to_zero, emit last-fault correlate
                        // so even a missed in_hdr still names a suspect leaf.
                        if (kind[0] == 't' && ((pf == 0x2u && psz == 0x60u) || flz_always)) {
                            uint64_t ring_w = g_flz_fault_ring_w.load(
                                std::memory_order_relaxed);
                            fprintf(stderr,
                                "[fl-zero-fault] event=to_zero_correlate "
                                "t_ms=%lld last_n=%llu last_in_hdr=%d "
                                "last_fa=0x%llx last_pc=0x%llx last_lr=0x%llx "
                                "last_sym=%s last_want=%d busy_rearm_n=%llu "
                                "fault_hdr=%llu ring_w=%llu\n",
                                (long long)ms,
                                (unsigned long long)g_flz_last_n.load(
                                    std::memory_order_relaxed),
                                g_flz_last_in_hdr.load(std::memory_order_relaxed),
                                (unsigned long long)g_flz_last_fa.load(
                                    std::memory_order_relaxed),
                                (unsigned long long)g_flz_last_pc.load(
                                    std::memory_order_relaxed),
                                (unsigned long long)g_flz_last_lr.load(
                                    std::memory_order_relaxed),
                                g_flz_last_sym,
                                g_flz_last_want.load(std::memory_order_relaxed),
                                (unsigned long long)g_flz_busy_rearm_n.load(
                                    std::memory_order_relaxed),
                                (unsigned long long)g_flz_fault_hdr_n.load(
                                    std::memory_order_relaxed),
                                (unsigned long long)ring_w);
                            // Dump last min(16, ring_w) faults oldest→newest.
                            uint64_t dump_n = ring_w < (uint64_t)kFlzFaultRing
                                ? ring_w : (uint64_t)kFlzFaultRing;
                            uint64_t start = ring_w - dump_n;
                            for (uint64_t k = 0; k < dump_n; ++k) {
                                const FlzFaultRingRec& r =
                                    g_flz_fault_ring[(start + k) %
                                        (uint64_t)kFlzFaultRing];
                                if (r.n == 0 && r.fa == 0) continue;
                                fprintf(stderr,
                                    "[fl-zero-fault] event=fault_ring "
                                    "i=%llu n=%llu in_hdr=%d near_hdr=%d late=%d "
                                    "fa=0x%llx pc=0x%llx sym=%s+0x%llx lr=0x%llx "
                                    "guest_pc=0x%08X want=%d\n",
                                    (unsigned long long)k,
                                    (unsigned long long)r.n,
                                    r.in_hdr, r.near_hdr, r.late,
                                    (unsigned long long)r.fa,
                                    (unsigned long long)r.pc,
                                    r.sym[0] ? r.sym : "none",
                                    (unsigned long long)r.pc_off,
                                    (unsigned long long)r.lr,
                                    (unsigned)r.guest_pc,
                                    r.want);
                            }
                            fflush(stderr);
                        }
                        g_flz_fault_want.store(0, std::memory_order_release);
                        fl_zero_fault_disarm();
                        fprintf(stderr,
                            "[fl-zero-fault] event=disarm t_ms=%lld "
                            "cur_f=0x%X cur_sz=0x%X kind=%s\n",
                            (long long)ms, (unsigned)cf, csz, kind);
                        fflush(stderr);
                    }
                }
#endif
            }
#ifndef _WIN32
            // Re-arm every poll tick while freelist-shaped (or boot-zero).
            // Faults clear armed; busy re-arm spinner (below) is faster for
            // want==2; this is the boot-zero + idle fallback.
            int want_now = g_flz_fault_want.load(std::memory_order_relaxed);
            if (want_now &&
                !g_flz_fault_armed.load(std::memory_order_relaxed)) {
                uint16_t cf = be_u16(prev);
                uint32_t csz = be_u32(prev + 4);
                if ((cf == 0x2u && csz == 0x60u) || (cf == 0 && csz == 0) || flz_always) {
                    fl_zero_fault_arm();
                } else {
                    g_flz_fault_want.store(0, std::memory_order_release);
                }
            }
#endif
            auto now = std::chrono::steady_clock::now();
            if (now - last_hb >= std::chrono::seconds(5)) {
                auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                    now - t0).count();
                fprintf(stderr,
                    "[fl-zero-poll] n=%llu event=heartbeat t_ms=%lld phys=0x%08X "
                    "flags=0x%X size=0x%X polls=%llu changes=%llu to_zero=%llu "
                    "fault_n=%llu fault_hdr=%llu fault_late=%llu fault_armed=%d "
                    "busy_rearm=%llu want=%d ring_w=%llu\n",
                    (unsigned long long)n_change, (long long)ms, slot,
                    (unsigned)be_u16(prev), (unsigned)be_u32(prev + 4),
                    (unsigned long long)n_poll, (unsigned long long)n_change,
                    (unsigned long long)n_to_zero,
#ifndef _WIN32
                    (unsigned long long)g_flz_fault_n.load(std::memory_order_relaxed),
                    (unsigned long long)g_flz_fault_hdr_n.load(std::memory_order_relaxed),
                    (unsigned long long)g_flz_fault_late_n.load(std::memory_order_relaxed),
                    g_flz_fault_armed.load(std::memory_order_relaxed),
                    (unsigned long long)g_flz_busy_rearm_n.load(std::memory_order_relaxed),
                    g_flz_fault_want.load(std::memory_order_relaxed),
                    (unsigned long long)g_flz_fault_ring_w.load(std::memory_order_relaxed)
#else
                    0ull, 0ull, 0ull, 0, 0ull, 0, 0ull
#endif
                );
                fflush(stderr);
                last_hb = now;
            }
            // s647: freelist window uses 10µs poll; boot/idle stay 250µs.
#ifndef _WIN32
            if (g_flz_fault_want.load(std::memory_order_relaxed) == 2) {
                std::this_thread::sleep_for(std::chrono::microseconds(10));
            } else {
                std::this_thread::sleep_for(std::chrono::microseconds(250));
            }
#else
            std::this_thread::sleep_for(std::chrono::microseconds(250));
#endif
        }
    }};
    t.detach();

#ifndef _WIN32
    // s647: freelist-window re-arm spinner. After a neighbor thrash SEGV the
    // page is RW until re-armed — the 250µs poller gap let freelist to_zero
    // complete with in_hdr=0 (s646 Outcome B). Hold off ≥20µs after the last
    // fault (so the restarted store finishes; earlier re-arm SEGV-loops),
    // then re-arm. Net race window ~20µs vs ~250µs.
    static std::thread rearm_spin{[]{
        uint64_t last_log = 0;
        for (;;) {
            int want = g_flz_fault_want.load(std::memory_order_relaxed);
            if (want == 2 &&
                !g_flz_fault_armed.load(std::memory_order_relaxed) &&
                g_flz_fault_enabled.load(std::memory_order_relaxed)) {
                auto now_ns = (uint64_t)std::chrono::duration_cast<
                    std::chrono::nanoseconds>(
                    std::chrono::steady_clock::now().time_since_epoch()).count();
                uint64_t last_f = g_flz_last_fault_ns.load(std::memory_order_acquire);
                if (last_f != 0 && now_ns < last_f + 20000ull) {
                    // Hold-off window: sleep the remainder.
                    uint64_t rem = last_f + 20000ull - now_ns;
                    std::this_thread::sleep_for(
                        std::chrono::nanoseconds((long long)rem));
                    continue;
                }
                fl_zero_fault_arm();
                uint64_t n = g_flz_busy_rearm_n.fetch_add(1, std::memory_order_relaxed) + 1;
                if (n <= 8 || n - last_log >= 64) {
                    last_log = n;
                    fprintf(stderr,
                        "[fl-zero-fault] event=busy_rearm n=%llu armed=%d "
                        "last_n=%llu last_in_hdr=%d last_sym=%s\n",
                        (unsigned long long)n,
                        g_flz_fault_armed.load(std::memory_order_relaxed),
                        (unsigned long long)g_flz_last_n.load(
                            std::memory_order_relaxed),
                        g_flz_last_in_hdr.load(std::memory_order_relaxed),
                        g_flz_last_sym);
                    fflush(stderr);
                }
            } else if (want == 2) {
                std::this_thread::sleep_for(std::chrono::microseconds(5));
            } else {
                std::this_thread::sleep_for(std::chrono::milliseconds(2));
            }
        }
    }};
    rearm_spin.detach();
#endif
}

static void start_memwp_watchdog() {
#ifndef _WIN32
    // Hardware-breakpoint watchdog is Win32-only (DR0 debug registers).
    fprintf(stderr, "[hwbp] not supported on this platform\n");
#else
    static std::thread wp_thread{[]{
        uint8_t* rdram = nullptr;
        while (!(rdram = (uint8_t*)g_recomp_rdram_for_wp_raw)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        // Default watch is rdram+0x3CBC4 (N64-logo low-mem fb writeback hunt).
        // Override via ROGUESQ_HWBP_ADDR=<hex offset> for new investigations.
        uint32_t watch_off = 0x3CBC4u;
        if (const char* e = std::getenv("ROGUESQ_HWBP_ADDR"); e && *e) {  // s7730
            unsigned long v = strtoul(e, nullptr, 0);
            if (v > 0 && v < 0x800000u) watch_off = (uint32_t)v;
        }
        uintptr_t addr = (uintptr_t)(rdram + watch_off);
        g_wp_addr = addr;
        AddVectoredExceptionHandler(1, memwp_veh);
        fprintf(stderr, "[hwbp] watching VA 0x%llX (rdram+0x%X), initial=0x%08X\n",
            (unsigned long long)addr, watch_off, *(uint32_t*)(rdram + watch_off));
        fflush(stderr);
        // Re-arm cadence: most game threads are created in the first ~2 s of boot.
        // After that, fresh threads are rare (RT64 lazy workers, the occasional
        // file IO). 1 s is plenty and keeps SuspendThread/SetThreadContext churn
        // off the SDL pump's back. Per-thread arm itself is silent.
        for (;;) {
            arm_hwbp_all_threads(addr);
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }};
    wp_thread.detach();
#endif
}

// ---------------------------------------------------------------------------
// Input (SDL2 gamepad plus keyboard fallback — one logical controller)
// ---------------------------------------------------------------------------
static SDL_GameController* controller = nullptr;

// s7201 pad hot-plug. Old path: a pad opened only on its own ADDED while none was open, so a second pad connected
// at boot (its ADDED came while pad 1 was open) was never adopted after pad 1 was removed: input dead until a
// replug. Now on removal of ours (or if ours reports detached without an event) we adopt the first remaining
// game controller. ROGUESQ_PAD_HOTPLUG=0 = old behaviour.
// Forced arm ROGUESQ_PAD_HOTPLUG_TEST=<sec>: attach two SDL virtual gamepads (P1 holds A + stick right, P2 holds
// X = N64 B + stick up), detach P1 at <sec>, log the pad word sent to the guest once per second ([pad-hp] word).
static bool rs64_pad_hotplug_on() {
    static const bool on = [] { const char* e = getenv("ROGUESQ_PAD_HOTPLUG"); return !(e && e[0] == '0'); }();
    return on;
}
static double rs64_pad_test_s() {
    static const double t = [] { const char* e = getenv("ROGUESQ_PAD_HOTPLUG_TEST"); return e ? atof(e) : 0.0; }();
    return t;
}
static void rs64_pad_adopt(SDL_JoystickID skip) {
    if (controller) return;
    const int n = SDL_NumJoysticks();
    for (int i = 0; i < n; ++i) {
        if (!SDL_IsGameController(i) || SDL_JoystickGetDeviceInstanceID(i) == skip) continue;
        controller = SDL_GameControllerOpen(i);
        if (controller) {
            fprintf(stderr, "[pad-hp] adopt idx=%d id=%d name=%s (of %d)\n", i, (int)SDL_JoystickGetDeviceInstanceID(i),
                    SDL_GameControllerName(controller) ? SDL_GameControllerName(controller) : "?", n);
            return;
        }
    }
    fprintf(stderr, "[pad-hp] adopt: no game controller among %d joysticks\n", n);
}
static void rs64_pad_test_tick() {
    const double t_det = rs64_pad_test_s();
    if (t_det <= 0) return;
    static double t0 = -1; static int stage = 0; static SDL_Joystick* j1 = nullptr; static SDL_Joystick* j2 = nullptr;
    static SDL_JoystickID id1 = -1;
    const double now = (double)std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count() / 1000.0;
    if (t0 < 0) t0 = now;
    if (stage == 0) {
        auto attach = [](const char* name) -> int {
            SDL_VirtualJoystickDesc d; SDL_zero(d);
            d.version = SDL_VIRTUAL_JOYSTICK_DESC_VERSION; d.type = SDL_JOYSTICK_TYPE_GAMECONTROLLER;
            d.naxes = SDL_CONTROLLER_AXIS_MAX; d.nbuttons = SDL_CONTROLLER_BUTTON_MAX; d.name = name;
            return SDL_JoystickAttachVirtualEx(&d);
        };
        const int i1 = attach("RS64 virtual P1"); const int i2 = attach("RS64 virtual P2");
        j1 = i1 >= 0 ? SDL_JoystickOpen(i1) : nullptr; j2 = i2 >= 0 ? SDL_JoystickOpen(i2) : nullptr;
        id1 = j1 ? SDL_JoystickInstanceID(j1) : -1;
        if (j1) { SDL_JoystickSetVirtualButton(j1, SDL_CONTROLLER_BUTTON_A, 1); SDL_JoystickSetVirtualAxis(j1, SDL_CONTROLLER_AXIS_LEFTX, 32767); }
        if (j2) { SDL_JoystickSetVirtualButton(j2, SDL_CONTROLLER_BUTTON_X, 1); SDL_JoystickSetVirtualAxis(j2, SDL_CONTROLLER_AXIS_LEFTY, -32767); }
        fprintf(stderr, "[pad-hp] test attach i1=%d i2=%d id1=%d err=%s njoy=%d\n", i1, i2, (int)id1, SDL_GetError(), SDL_NumJoysticks());
        stage = 1;
    } else if (stage == 1 && now - t0 >= t_det) {
        int idx = -1;
        for (int i = 0; i < SDL_NumJoysticks(); ++i) if (SDL_JoystickGetDeviceInstanceID(i) == id1) idx = i;
        if (j1) { SDL_JoystickClose(j1); j1 = nullptr; }
        const int rc = idx >= 0 ? SDL_JoystickDetachVirtual(idx) : -1;
        fprintf(stderr, "[pad-hp] test detach P1 idx=%d rc=%d t=%.1f\n", idx, rc, now - t0);
        stage = 2;
    }
}

// s7593 class EX (quit path). Cmd+Q / window close / SIGTERM all become SDL_QUIT, and before s7593 the only consumer was the
// SDL_PeepEvents loop in poll_input(), i.e. the guest's osContStartReadData. A guest that is not polling (a load, a stall, a
// hang) left the quit queued: the app ignored Cmd+Q until the next poll. ROGUESQ_S7593_MAINQUIT (default 1; =0 = old) also
// peeks for SDL_QUIT on the main thread right after SDL_PumpEvents (update_gfx), so quit no longer waits on the guest.
// Levers (unset = off): ROGUESQ_S7593_QUIT_AT=<s> pushes SDL_QUIT <s> seconds after the first update_gfx;
// ROGUESQ_S7593_QUIT_ON_GAP_MS=<ms> pushes it the first time the guest has not polled input for <ms> (after
// ROGUESQ_S7593_QUIT_AFTER=<s>, default 20); ROGUESQ_S7593_POLLGAP=1 logs every poll gap >= 250 ms.
// Plants (ROGUESQ_S7593_PLANT): nopoll = poll_input skips its SDL drain for 20 s after the push (a guest that stops
// polling); crash = an at_quick_exit handler faults; hang = an at_quick_exit handler never returns; exit = std::exit (s5380).
static int64_t rs64_s7593_now_ns() {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
static std::atomic<int64_t> g_s7593_last_poll_ns{0};
static std::atomic<int64_t> g_s7593_push_ns{0};
static std::atomic<int64_t> g_s7593_max_gap_ns{0};
static double rs64_s7593_epoch() { return std::chrono::duration<double>(std::chrono::system_clock::now().time_since_epoch()).count(); }
static const std::string& rs64_s7593_plant() {
    static const std::string p = [] { const char* e = std::getenv("ROGUESQ_S7593_PLANT"); return std::string(e ? e : ""); }();
    return p;
}
[[noreturn]] static void rs64_s7593_quit_now(const char* who) {
    static std::atomic<bool> once{false};
    if (once.exchange(true)) { for (;;) std::this_thread::sleep_for(std::chrono::hours(1)); } // the other consumer is exiting
    const int64_t p = g_s7593_push_ns.load(), n = rs64_s7593_now_ns();
    fprintf(stderr, "[main] SDL_QUIT received, exiting\n");
    fprintf(stderr, "[s7593] quit by=%s latency_ms=%.1f max_poll_gap_ms=%.1f wall=%.3f plant=%s\n", who, p ? (n - p) / 1e6 : -1.0,
            g_s7593_max_gap_ns.load() / 1e6, rs64_s7593_epoch(), rs64_s7593_plant().c_str());
    // s7429 class CL: write a save still inside the saving thread's 10 ms coalescing window.
    fprintf(stderr, "[s7429-quit] save flush=%d\n", ultramodern::flush_save_file());
    fflush(stderr);
    const std::string& pl = rs64_s7593_plant();
    if (pl == "crash") std::at_quick_exit([] { fprintf(stderr, "[s7593] plant crash\n"); fflush(stderr); *(volatile int*)8 = 1; });
    if (pl == "hang") std::at_quick_exit([] { fprintf(stderr, "[s7593] plant hang\n"); fflush(stderr); for (;;) pause(); });
    if (pl == "exit") std::exit(EXIT_SUCCESS);
    // quick_exit: exit() here runs static destructors while guest/audio threads
    // are live and ends in std::terminate -> SIGABRT (s5380).
    std::quick_exit(EXIT_SUCCESS);
}
static void rs64_s7593_push_quit(const char* why, double t) {
    if (g_s7593_push_ns.load()) return;
    g_s7593_push_ns.store(rs64_s7593_now_ns());
    SDL_Event q{}; q.type = SDL_QUIT; SDL_PushEvent(&q);
    const int64_t lp = g_s7593_last_poll_ns.load();
    fprintf(stderr, "[s7593] quit pushed why=%s t=%.1f wall=%.3f since_poll_ms=%.1f origin=0x%08X\n", why, t, rs64_s7593_epoch(),
            lp ? (g_s7593_push_ns.load() - lp) / 1e6 : -1.0, (unsigned)rs64_vi_committed_origin());
    fflush(stderr);
}
#ifndef _WIN32
// s7594 class SG (signal dispositions). SDL turns SIGINT/SIGTERM into SDL_QUIT; before s7594 SIGHUP (closing the Terminal that
// launched the game), SIGQUIT (Ctrl+\\) and SIGPIPE (a dead stdout/stderr reader, e.g. `| tee` that exits) kept their default
// dispositions and killed the process with no save flush and no log line. ROGUESQ_S7594_SIG (default 1; =0 = old) installs a
// flag-only handler for HUP/QUIT (the main tick turns it into the normal quit path: save flush + quick_exit) and SIG_IGN for
// PIPE (the async-stderr writer already stops on EPIPE). HUP/QUIT are taken only when inherited as SIG_DFL (nohup keeps working). ROGUESQ_S7594_DISP=1 prints every signal disposition at the first main
// tick. Plant ROGUESQ_S7594_PLANT=term resets SIGTERM to SIG_DFL there (positive control: TERM must become rc 143, no flush).
static volatile sig_atomic_t g_s7594_sig = 0;
static void rs64_s7594_handler(int sig) { if (!g_s7594_sig) g_s7594_sig = sig; }
static bool rs64_s7594_on() { static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7594_SIG"); return !(e && *e == '0'); }(); return on; }
static void rs64_s7594_install() {
    if (!rs64_s7594_on()) return;
    struct sigaction sa {}; sa.sa_handler = rs64_s7594_handler; sigemptyset(&sa.sa_mask); sa.sa_flags = SA_RESTART;
    for (int sg : {SIGHUP, SIGQUIT}) { // like SDL: only over SIG_DFL, so an inherited ignore (nohup, a background job) is kept
        struct sigaction o {};
        if (sigaction(sg, nullptr, &o) == 0 && !(o.sa_flags & SA_SIGINFO) && o.sa_handler == SIG_DFL) sigaction(sg, &sa, nullptr);
    }
    signal(SIGPIPE, SIG_IGN);
}
static void rs64_s7594_first_tick() {
    const char* pl = std::getenv("ROGUESQ_S7594_PLANT");
    if (pl && !strcmp(pl, "term")) { signal(SIGTERM, SIG_DFL); fprintf(stderr, "[s7594] plant term: SIGTERM -> SIG_DFL\n"); }
    const char* d = std::getenv("ROGUESQ_S7594_DISP");
    if (!(d && *d == '1')) return;
    sigset_t cur; sigemptyset(&cur); pthread_sigmask(SIG_BLOCK, nullptr, &cur);
    for (int s = 1; s < NSIG; s++) {
        struct sigaction o {}; if (sigaction(s, nullptr, &o) != 0) continue;
        const void* h = (o.sa_flags & SA_SIGINFO) ? (const void*)o.sa_sigaction : (const void*)o.sa_handler;
        const char* k = h == (const void*)SIG_DFL ? "DFL" : h == (const void*)SIG_IGN ? "IGN" : "handler";
        Dl_info di {}; const char* who = (h && h != (const void*)SIG_IGN && dladdr(h, &di) && di.dli_fname) ? di.dli_fname : "-";
        const char* sl = who ? strrchr(who, '/') : nullptr;
        fprintf(stderr, "[s7594] disp sig=%d name=%s kind=%s lib=%s flags=0x%x main_blocked=%d\n", s, sys_signame[s], k,
                sl ? sl + 1 : who, (unsigned)o.sa_flags, sigismember(&cur, s));
    }
    fflush(stderr);
}
#endif
// Main thread, after SDL_PumpEvents.
static void rs64_s7593_main_tick() {
#ifndef _WIN32
    static bool s7594_first = (rs64_s7594_first_tick(), true); (void)s7594_first;
    if (g_s7594_sig) {
        const int sg = g_s7594_sig;
        fprintf(stderr, "[s7594] signal %d (%s) -> quit path\n", sg, sys_signame[sg]);
        static char who[24]; snprintf(who, sizeof who, "sig%s", sys_signame[sg]);
        rs64_s7593_quit_now(who);
    }
#endif
    static const double at = [] { const char* e = std::getenv("ROGUESQ_S7593_QUIT_AT"); return (e && *e) ? std::atof(e) : -1.0; }();
    static const double gap = [] { const char* e = std::getenv("ROGUESQ_S7593_QUIT_ON_GAP_MS"); return (e && *e) ? std::atof(e) : -1.0; }();
    static const double after = [] { const char* e = std::getenv("ROGUESQ_S7593_QUIT_AFTER"); return (e && *e) ? std::atof(e) : 20.0; }();
    static const bool mainq = [] { const char* e = std::getenv("ROGUESQ_S7593_MAINQUIT"); return !(e && *e == '0'); }();
    static const int64_t t0 = rs64_s7593_now_ns();
    const int64_t n = rs64_s7593_now_ns();
    const double t = (n - t0) / 1e9;
    if (at >= 0 && t >= at) rs64_s7593_push_quit("at", t);
    if (gap > 0 && t >= after) {
        const int64_t lp = g_s7593_last_poll_ns.load();
        if (lp && (n - lp) / 1e6 >= gap) rs64_s7593_push_quit("gap", t);
    }
    if (mainq) {
        SDL_Event e;
        if (SDL_PeepEvents(&e, 1, SDL_PEEKEVENT, SDL_QUIT, SDL_QUIT) > 0) rs64_s7593_quit_now("main");
    }
}

// G6a (s7617) rumble. The game strobes the Rumble Pak motor (osMotorStart/Stop, ~30 Hz on/off, s7516), which reaches us
// through ultramodern __osMotorAccess -> set_rumble. Mirroring each edge does nothing useful on DualShock 4 over macOS (short
// SDL rumble calls are dropped), so edges are recorded with timestamps and poll_input (the thread that owns `controller`)
// turns the motor's on-fraction over the last 100 ms into a strength and sends SDL_GameControllerRumble with a 150 ms
// duration, refreshed while the duty stays > 0 and cancelled once it drops to 0. A guest that stops polling (load) lets
// the last call expire on its own. Port 0 reports a Rumble Pak so the game sends pulses at all (saves use EEPROM: osPfs*
// is only reached on save device 2, s7516). ROGUESQ_RUMBLE=0 restores the old shape (no pak, no rumble).
// ROGUESQ_RUMBLE_SCALE 0..2 (default 1). ROGUESQ_LOG_RUMBLE=1 logs edges / SDL calls / a 5 s summary.
// ROGUESQ_RUMBLE_TEST=1 attaches a virtual gamepad whose Rumble callback logs what SDL delivers to a device (positive control).
#include <deque>
extern "C" long long rs64_s5773_ms(void);
static int s7671_key = 0; static unsigned s7671_btn = 0;  // s7671 rumble lever: last autopilot key (>0 = just fired)
static bool rs64_rumble_on() {
    static const bool on = [] { const char* e = getenv("ROGUESQ_RUMBLE"); return !(e && e[0] == '0'); }();
    return on;
}
static float rs64_rumble_scale() {
    static const float s = [] { const char* e = getenv("ROGUESQ_RUMBLE_SCALE"); float v = e && *e ? (float)atof(e) : 1.0f;
        return v < 0.0f ? 0.0f : (v > 2.0f ? 2.0f : v); }();
    return s;
}
static bool rs64_rumble_log() {
    static const bool on = [] { const char* e = getenv("ROGUESQ_LOG_RUMBLE"); return e && *e && *e != '0'; }();
    return on;
}
static int64_t rs64_rumble_now_us() {
    return std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
static std::mutex g_rumble_mtx;
static std::deque<std::pair<int64_t, bool>> g_rumble_edges;
static bool g_rumble_state = false, g_rumble_base = false;
static std::atomic<long> g_rumble_calls{0}, g_rumble_on_edges{0}, g_rumble_vpad_calls{0}, g_rumble_vpad_nonzero{0};
static void set_rumble(int channel, bool on) {
    g_rumble_calls.fetch_add(1, std::memory_order_relaxed);
    if (channel != 0) return;
    std::lock_guard<std::mutex> lk(g_rumble_mtx);
    if (on == g_rumble_state) return;
    g_rumble_state = on;
    if (on) g_rumble_on_edges.fetch_add(1, std::memory_order_relaxed);
    g_rumble_edges.push_back({rs64_rumble_now_us(), on});
    if (g_rumble_edges.size() > 512) { g_rumble_base = g_rumble_edges.front().second; g_rumble_edges.pop_front(); }
}
static float rs64_rumble_duty(int64_t now) {
    constexpr int64_t W = 100000;
    std::lock_guard<std::mutex> lk(g_rumble_mtx);
    while (!g_rumble_edges.empty() && g_rumble_edges.front().first < now - 2 * W) {
        g_rumble_base = g_rumble_edges.front().second; g_rumble_edges.pop_front();
    }
    const int64_t t0 = now - W; bool st = g_rumble_base; int64_t t = t0, on = 0;
    for (const auto& e : g_rumble_edges) {
        if (e.first <= t0) { st = e.second; continue; }
        if (st) on += e.first - t;
        t = e.first; st = e.second;
    }
    if (st) on += now - t;
    const float d = (float)on / (float)W;
    return d < 0.0f ? 0.0f : (d > 1.0f ? 1.0f : d);
}
static int SDLCALL rs64_rumble_vpad_cb(void*, Uint16 lo, Uint16 hi) {
    const long n = g_rumble_vpad_calls.fetch_add(1, std::memory_order_relaxed) + 1;
    if (lo || hi) g_rumble_vpad_nonzero.fetch_add(1, std::memory_order_relaxed);
    if (rs64_rumble_log() && (n <= 40 || n % 200 == 0))
        fprintf(stderr, "[rumble-vpad] n=%ld lo=%u hi=%u\n", n, (unsigned)lo, (unsigned)hi);
    // s7638: return 1, not 0. sdl2-compat hands this SDL2 int callback to SDL3, whose Rumble returns bool, so 0 reads as
    // failure and SDL_GameControllerRumble returned -1 although the call was delivered (scratch/s7638/vpad_rc.c: cb 0 -> rc -1,
    // cb 1 or -1 -> rc 0). That was the s7617 "SDL returns -1 for the virtual pad" open item; real pads are not affected.
    return 1;
}
// s7638 G6a fallback chain (the G6a spec's SDL_JoystickRumble / SDL_Haptic fallbacks). Path 0 = SDL_GameControllerRumble,
// 1 = SDL_JoystickRumble on the pad's joystick, 2 = SDL_Haptic rumble (subsystem initialised lazily, only if 0 and 1 fail).
// A failing path advances to the next; when all fail the chain idles 5 s and re-probes from 0. A new `controller` pointer
// resets the chain. ROGUESQ_RUMBLE_FORCE_PATH=joy|haptic starts at that path (positive control for the fallbacks).
enum { RS64_RP_GC = 0, RS64_RP_JOY = 1, RS64_RP_HAPTIC = 2, RS64_RP_NONE = 3 };
static int g_rumble_path = RS64_RP_GC;
static const char* rs64_rumble_path_name(int p) { return p == 0 ? "gc" : p == 1 ? "joy" : p == 2 ? "haptic" : "none"; }
static int rs64_rumble_first_path() {
    static const int f = [] { const char* e = getenv("ROGUESQ_RUMBLE_FORCE_PATH");
        if (e && !strcmp(e, "joy")) return (int)RS64_RP_JOY; if (e && !strcmp(e, "haptic")) return (int)RS64_RP_HAPTIC; return (int)RS64_RP_GC; }();
    return f;
}
static int rs64_rumble_send(float s, Uint16 lo, Uint16 hi, int64_t now) {
    static SDL_GameController* s_pad = nullptr;
    static SDL_Haptic* s_hap = nullptr;
    static bool s_hap_init = false;
    static int64_t s_none_t = 0;
    if (controller != s_pad) {
        if (s_hap) { SDL_HapticClose(s_hap); s_hap = nullptr; s_hap_init = false; }
        s_pad = controller; g_rumble_path = rs64_rumble_first_path();
    }
    if (g_rumble_path == RS64_RP_NONE) {
        if (now - s_none_t < 5000000) return -1;
        g_rumble_path = rs64_rumble_first_path();
    }
    const Uint32 ms = s > 0.0f ? 150 : 0;
    for (;;) {
        int rc = -1;
        if (g_rumble_path == RS64_RP_GC) rc = SDL_GameControllerRumble(controller, lo, hi, ms);
        else if (g_rumble_path == RS64_RP_JOY) {
            SDL_Joystick* j = SDL_GameControllerGetJoystick(controller);
            rc = j ? SDL_JoystickRumble(j, lo, hi, ms) : -1;
        } else if (g_rumble_path == RS64_RP_HAPTIC) {
            if (!s_hap) {
                SDL_Joystick* j = SDL_GameControllerGetJoystick(controller);
                if (j && SDL_InitSubSystem(SDL_INIT_HAPTIC) == 0 && SDL_JoystickIsHaptic(j) == 1) s_hap = SDL_HapticOpenFromJoystick(j);
                s_hap_init = s_hap && SDL_HapticRumbleInit(s_hap) == 0;
            }
            if (s_hap && s_hap_init) rc = s > 0.0f ? SDL_HapticRumblePlay(s_hap, s, ms) : SDL_HapticRumbleStop(s_hap);
        }
        if (rc == 0) return 0;
        if (rs64_rumble_log()) fprintf(stderr, "[rumble] path %s failed rc=%d err=%s\n", rs64_rumble_path_name(g_rumble_path), rc, SDL_GetError());
        if (++g_rumble_path >= RS64_RP_NONE) { g_rumble_path = RS64_RP_NONE; s_none_t = now; return rc; }
    }
}
static void rs64_rumble_test_attach() {
    static bool done = false;
    if (done) return;
    done = true;
    const char* e = getenv("ROGUESQ_RUMBLE_TEST");
    if (!(e && *e && *e != '0')) return;
    SDL_VirtualJoystickDesc d; SDL_zero(d);
    d.version = SDL_VIRTUAL_JOYSTICK_DESC_VERSION; d.type = SDL_JOYSTICK_TYPE_GAMECONTROLLER;
    d.naxes = SDL_CONTROLLER_AXIS_MAX; d.nbuttons = SDL_CONTROLLER_BUTTON_MAX; d.name = "RS64 rumble test pad";
    d.Rumble = rs64_rumble_vpad_cb;
    const int idx = SDL_JoystickAttachVirtualEx(&d);
    if (controller) { SDL_GameControllerClose(controller); controller = nullptr; }
    if (idx >= 0) controller = SDL_GameControllerOpen(idx);
    fprintf(stderr, "[rumble] test pad attach idx=%d open=%d err=%s\n", idx, controller ? 1 : 0, SDL_GetError());
}
static void rs64_rumble_tick() {
    static int64_t s_sent_t = 0, s_sum_t = 0;
    static float s_sent = 0.0f, s_max_duty = 0.0f;
    static long s_sdl_on = 0, s_sdl_off = 0, s_sdl_fail = 0;
    rs64_rumble_test_attach();
    const int64_t now = rs64_rumble_now_us();
    // ROGUESQ_RUMBLE_TEST=1 also injects a synthetic motor train 20-21 s after the first poll (on 13 ms / off 20 ms, like
    // the game's ~30 Hz strobe) so the duty -> SDL -> device chain has a positive control that does not wait on a game event.
    {
        static const bool test = [] { const char* e = getenv("ROGUESQ_RUMBLE_TEST"); return e && *e && *e != '0'; }();
        static int64_t s_t0 = 0; static int s_inj = 0;
        if (test) {
            if (!s_t0) s_t0 = now;
            const int64_t dt = now - s_t0 - 20000000;
            if (dt >= 0 && dt < 1000000) {
                const bool want = (dt % 33000) < 13000;
                set_rumble(0, want); if (s_inj == 0) fprintf(stderr, "[rumble] inject start\n"); s_inj = 1;
            } else if (s_inj == 1 && dt >= 1000000) {
                // s7669 positive control for the long-run detector: ROGUESQ_S7669_STUCK_PLANT=1 leaves the motor ON for 3 s after
                // the train (a planted "stuck" motor), so the detector below must report one run of ~3000+ ms.
                static const bool plant = [] { const char* e = getenv("ROGUESQ_S7669_STUCK_PLANT"); return e && *e == '1'; }();
                if (plant && dt < 4000000) { if (dt < 1040000) set_rumble(0, true); }
                else { set_rumble(0, false); s_inj = 2; fprintf(stderr, "[rumble] inject end plant=%d\n", plant ? 1 : 0); }
            }
        }
    }
    const float duty = rs64_rumble_duty(now);
    if (duty > s_max_duty) s_max_duty = duty;
    float s = 0.0f;
    // Floor 0.25: the game's PWM duty sits at 0.1-0.5, which is faint on modern motors.
    if (rs64_rumble_on() && duty > 0.0f) s = (0.25f + 0.75f * duty) * rs64_rumble_scale();
    if (s > 1.0f) s = 1.0f;
    const bool due = s > 0.0f ? (std::fabs(s - s_sent) > 0.02f || now - s_sent_t > 50000) : (s_sent > 0.0f);
    if (due) {
        int rc = -1;
        if (controller) {
            const Uint16 lo = (Uint16)(s * 65535.0f), hi = (Uint16)(s * 0.6f * 65535.0f);
            rc = rs64_rumble_send(s, lo, hi, now);
        }
        if (rc != 0) ++s_sdl_fail; else if (s > 0.0f) ++s_sdl_on; else ++s_sdl_off;
        if (rs64_rumble_log() && (s_sdl_on + s_sdl_off + s_sdl_fail <= 40))
            fprintf(stderr, "[rumble] sdl s=%.2f duty=%.2f rc=%d path=%s pad=%d has=%d err=%s\n", s, duty, rc,
                    rs64_rumble_path_name(g_rumble_path), controller ? 1 : 0,
                    controller ? (int)SDL_GameControllerHasRumble(controller) : -1, rc ? SDL_GetError() : "");
        s_sent = s; s_sent_t = now;
    }
    // s7669 long-run detector (ROGUESQ_LOG_RUMBLE=1): every continuous s>0 run is logged at its end with its length; a run longer
    // than ROGUESQ_RUMBLE_LONG_MS (default 2000) is tagged LONG. A motor left on across an abort / menu / load shows here.
    if (rs64_rumble_log()) {
        static int64_t s_run_t0 = 0; static float s_run_max = 0.0f; static long s_runs = 0, s_long = 0;
        static const int64_t long_us = [] { const char* e = getenv("ROGUESQ_RUMBLE_LONG_MS"); return (int64_t)(e && *e ? atoi(e) : 2000) * 1000; }();
        if (s > 0.0f) { if (!s_run_t0) { s_run_t0 = now; s_run_max = 0.0f; } if (s > s_run_max) s_run_max = s; }
        else if (s_run_t0) {
            const int64_t len = now - s_run_t0; ++s_runs; const bool lg = len > long_us; if (lg) ++s_long;
            fprintf(stderr, "[rumble] run n=%ld ms=%lld max_s=%.2f%s long_total=%ld wall_ms=%lld\n", s_runs, (long long)(len / 1000),
                    s_run_max, lg ? " LONG" : "", s_long, (long long)rs64_s5773_ms());
            s_run_t0 = 0;
        }
    }
    if (rs64_rumble_log() && now - s_sum_t > 5000000) {
        s_sum_t = now;
        fprintf(stderr, "[rumble] sum on=%d scale=%.2f motor_calls=%ld on_edges=%ld max_duty=%.2f sdl_on=%ld sdl_off=%ld sdl_fail=%ld vpad=%ld vpad_nz=%ld pad=%d path=%s\n",
                rs64_rumble_on() ? 1 : 0, rs64_rumble_scale(), g_rumble_calls.load(), g_rumble_on_edges.load(), s_max_duty,
                s_sdl_on, s_sdl_off, s_sdl_fail, g_rumble_vpad_calls.load(), g_rumble_vpad_nonzero.load(), controller ? 1 : 0,
                rs64_rumble_path_name(g_rumble_path));
        s_max_duty = 0.0f;
    }
}
#include "rs64_controls_panel.h"  // s7620 G6b step 3 (F6 panel)
static void poll_input() {
    {
        static const bool gl = [] { const char* e = std::getenv("ROGUESQ_S7593_POLLGAP"); return e && *e == '1'; }();
        const int64_t n = rs64_s7593_now_ns(), lp = g_s7593_last_poll_ns.exchange(n);
        if (lp && n - lp > g_s7593_max_gap_ns.load()) g_s7593_max_gap_ns.store(n - lp);
        if (gl && lp && n - lp >= 250000000) {
            fprintf(stderr, "[s7593] pollgap ms=%.0f origin=0x%08X\n", (n - lp) / 1e6, (unsigned)rs64_vi_committed_origin());
        }
        const int64_t p = g_s7593_push_ns.load();
        if (p && rs64_s7593_plant() == "nopoll" && n - p < 20000000000LL) return; // plant: a guest that stopped polling
    }
    // Heartbeat: a quiet [pad-sdl] site=key after title 1024 is
    // H-poll-stopped if this dies, H-sdl-late-drop if it keeps climbing.
    {
        static int s_poll_n = 0;
        ++s_poll_n;
        if (s_poll_n <= 16 || (s_poll_n % 32) == 0) {
            fprintf(stderr,
                "[pad-sdl] site=poll n=%d vi_width=%u origin=0x%08X\n",
                s_poll_n,
                (unsigned)rs64_vi_committed_width(),
                (unsigned)rs64_vi_committed_origin());
            fflush(stderr);
        }
    }

    SDL_Event e;
    // On macOS only the main thread may pump Cocoa events (update_gfx does);
    // here we must only dequeue already-pumped events.
    while (SDL_PeepEvents(&e, 1, SDL_GETEVENT, SDL_FIRSTEVENT, SDL_LASTEVENT) > 0) {
        if (e.type == SDL_QUIT) rs64_s7593_quit_now("poll");
        rs64_panel_feed(e);  // s7620 G6b: F6 Controls panel (toggle + mouse while open)
        if ((e.type == SDL_KEYDOWN || e.type == SDL_KEYUP) &&
            (e.key.keysym.sym == SDLK_RETURN || e.key.keysym.sym == SDLK_z)) {
            static int s_pad_sdl_n = 0;
            ++s_pad_sdl_n;
            if (s_pad_sdl_n <= 16 || (s_pad_sdl_n % 32) == 0) {
                fprintf(stderr,
                    "[pad-sdl] site=key n=%d ev=%s key=%s repeat=%d vi_width=%u origin=0x%08X\n",
                    s_pad_sdl_n,
                    (e.type == SDL_KEYDOWN) ? "down" : "up",
                    (e.key.keysym.sym == SDLK_RETURN) ? "return" : "z",
                    e.key.repeat ? 1 : 0,
                    (unsigned)rs64_vi_committed_width(),
                    (unsigned)rs64_vi_committed_origin());
                fflush(stderr);
            }
        }
        if (e.type == SDL_CONTROLLERDEVICEADDED) {
            fprintf(stderr, "[pad-hp] added idx=%d open=%d\n", (int)e.cdevice.which, controller ? 1 : 0);
            if (!controller) {
                controller = SDL_GameControllerOpen(e.cdevice.which);
            }
        }
        if (e.type == SDL_CONTROLLERDEVICEREMOVED && controller) {
            const bool ours = SDL_JoystickInstanceID(SDL_GameControllerGetJoystick(controller)) == e.cdevice.which;
            fprintf(stderr, "[pad-hp] removed id=%d ours=%d\n", (int)e.cdevice.which, ours ? 1 : 0);
            if (ours) {
                SDL_GameControllerClose(controller);
                controller = nullptr;
                if (rs64_pad_hotplug_on()) rs64_pad_adopt(e.cdevice.which);
            }
        }
#ifdef _WIN32
        if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_F12) {
            fprintf(stderr, "[F12] manual minidump requested\n");
            fflush(stderr);
            write_minidump_safe(nullptr);
        }
#endif
        if (e.type == SDL_KEYDOWN && !e.key.repeat && e.key.keysym.sym == SDLK_F9) {
            g_audio_route_cycle.fetch_add(1, std::memory_order_acq_rel);
        }
        if (e.type == SDL_AUDIODEVICEADDED || e.type == SDL_AUDIODEVICEREMOVED) {
            static int n_aev = 0;
            if (++n_aev <= 32)
                fprintf(stderr, "[s7199-aev] n=%d type=%s which=%u capture=%d\n", n_aev,
                        e.type == SDL_AUDIODEVICEADDED ? "added" : "removed", (unsigned)e.adevice.which,
                        (int)e.adevice.iscapture);
        }
        if (e.type == SDL_AUDIODEVICEREMOVED && !e.adevice.iscapture) {
            g_audio_hp_removed.fetch_or(1u << (e.adevice.which & 31u), std::memory_order_acq_rel);
        }
        if (e.type == SDL_AUDIODEVICEADDED && !e.adevice.iscapture) {
            g_audio_hp_added.fetch_add(1, std::memory_order_acq_rel);
        }
        // Diagnostic: log F1-F4 to confirm the keys are reaching the SDL
        // queue at all. If we see these logs, SDL is delivering keypresses
        // to our process — RT64's filter (which runs before SDL_PollEvent)
        // may have already consumed them, or it may not be installed.
        if (e.type == SDL_KEYDOWN) {
            const auto& sym = e.key.keysym.sym;
            if (sym == SDLK_F1 || sym == SDLK_F2 || sym == SDLK_F3 || sym == SDLK_F4) {
                fprintf(stderr, "[input] SDL_KEYDOWN sym=%d (F%d) reached PollEvent\n",
                        (int)sym, (int)(sym - SDLK_F1 + 1));
                fflush(stderr);
            }
        }
    }
    if (rs64_pad_hotplug_on()) {
        // A pad that went away without a REMOVED reaching us (event consumed elsewhere) reads all-zero forever.
        if (controller && !SDL_GameControllerGetAttached(controller)) {
            const SDL_JoystickID id = SDL_JoystickInstanceID(SDL_GameControllerGetJoystick(controller));
            fprintf(stderr, "[pad-hp] open pad id=%d detached without event\n", (int)id);
            SDL_GameControllerClose(controller);
            controller = nullptr;
            rs64_pad_adopt(id);
        }
    }
    rs64_pad_test_tick();
    rs64_rumble_tick();
}

extern "C" long long rs64_s5773_ms(void) {
    return (long long)std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
}

extern "C" unsigned long rs64_s5773_ord(void) {
    static std::atomic<unsigned long> n{0};
    return n.fetch_add(1, std::memory_order_relaxed) + 1;
}

#include "rs64_stick_gate.h"
// s7618 G6b: the pre-table mapping, verbatim, kept behind ROGUESQ_BIND_OLD=1 and as the ROGUESQ_BIND_CHECK reference.
static void rs64_bind_old_sdl(uint16_t* out_btn, float* out_x, float* out_y) {
    uint16_t btn = 0;
    float stick_x = 0.0f;
    float stick_y = 0.0f;

    auto gamepad_button = [&](uint16_t mask, SDL_GameControllerButton sdl) {
        if (controller && SDL_GameControllerGetButton(controller, sdl)) btn |= mask;
    };

    // Rogue Squadron N64 → modern gamepad mapping:
    //   A (fire)        → face A
    //   B (bombs)       → face X
    //   Z (brake)       → left trigger (digital, via axis threshold below)
    //   R (boost)       → right shoulder
    //   L (targeting)   → left shoulder
    //   C-Up (view)     → right stick up (handled via axis) — face Y as fallback
    //   C-Down          → face B
    //   C-Left          → right stick left (axis) — d-left as fallback
    //   C-Right         → right stick right (axis) — d-right as fallback
    //   D-Pad           → d-pad
    //   Start           → start
    gamepad_button(N64_A_BUTTON,     SDL_CONTROLLER_BUTTON_A);
    gamepad_button(N64_B_BUTTON,     SDL_CONTROLLER_BUTTON_X);
    gamepad_button(N64_START_BUTTON, SDL_CONTROLLER_BUTTON_START);
    gamepad_button(N64_U_JPAD,       SDL_CONTROLLER_BUTTON_DPAD_UP);
    gamepad_button(N64_D_JPAD,       SDL_CONTROLLER_BUTTON_DPAD_DOWN);
    gamepad_button(N64_L_JPAD,       SDL_CONTROLLER_BUTTON_DPAD_LEFT);
    gamepad_button(N64_R_JPAD,       SDL_CONTROLLER_BUTTON_DPAD_RIGHT);
    gamepad_button(N64_L_TRIG,       SDL_CONTROLLER_BUTTON_LEFTSHOULDER);   // targeting computer
    gamepad_button(N64_R_TRIG,       SDL_CONTROLLER_BUTTON_RIGHTSHOULDER);  // boost/accelerate
    gamepad_button(N64_U_CBUTTONS,   SDL_CONTROLLER_BUTTON_Y);
    gamepad_button(N64_D_CBUTTONS,   SDL_CONTROLLER_BUTTON_B);
    gamepad_button(N64_L_CBUTTONS,   SDL_CONTROLLER_BUTTON_BACK);
    gamepad_button(N64_R_CBUTTONS,   SDL_CONTROLLER_BUTTON_GUIDE);
    // Owner request 2026-11-05: C-Right (keyboard L: V-wing boost, X-wing wing close) had no usable pad button, its only
    // binding is the PS/Guide button. Added on L3 so the thumb stays on the stick.
    gamepad_button(N64_R_CBUTTONS,   SDL_CONTROLLER_BUTTON_LEFTSTICK);
    // Z trigger (brake) from left analog trigger axis
    if (controller && SDL_GameControllerGetAxis(controller, SDL_CONTROLLER_AXIS_TRIGGERLEFT) > 16000) {
        btn |= N64_Z_TRIG;
    }
    // Owner request 2026-11-05: secondary weapon also on the right analog trigger (R2). Owner confirmed it fires from
    // PS5 Share/Create = SDL BACK = N64 C-Left, not N64 A (R2 -> A did nothing for it).
    if (controller && SDL_GameControllerGetAxis(controller, SDL_CONTROLLER_AXIS_TRIGGERRIGHT) > 16000) {
        btn |= N64_L_CBUTTONS;
    }

    if (controller) {
        const int16_t ax = SDL_GameControllerGetAxis(controller, SDL_CONTROLLER_AXIS_LEFTX);
        const int16_t ay = SDL_GameControllerGetAxis(controller, SDL_CONTROLLER_AXIS_LEFTY);
        stick_x = ax / 32767.0f;
        stick_y = -(ay / 32767.0f); // N64 Y is inverted vs SDL
    }

    // Keyboard fallback. SDL scancodes use physical keys, so these bindings
    // are stable across keyboard layouts. Keyboard and gamepad combine, with
    // keyboard WASD taking precedence for a non-zero analog-stick direction.
    const Uint8* keys = SDL_GetKeyboardState(nullptr);
    auto key = [&](SDL_Scancode scancode) { return keys && keys[scancode]; };
    if (key(SDL_SCANCODE_Z))      btn |= N64_A_BUTTON;
    if (key(SDL_SCANCODE_X))      btn |= N64_B_BUTTON;
    if (key(SDL_SCANCODE_C))      btn |= N64_Z_TRIG;
    if (key(SDL_SCANCODE_RETURN)) btn |= N64_START_BUTTON;
    if (key(SDL_SCANCODE_UP))     btn |= N64_U_JPAD;
    if (key(SDL_SCANCODE_DOWN))   btn |= N64_D_JPAD;
    if (key(SDL_SCANCODE_LEFT))   btn |= N64_L_JPAD;
    if (key(SDL_SCANCODE_RIGHT))  btn |= N64_R_JPAD;
    if (key(SDL_SCANCODE_Q))      btn |= N64_L_TRIG;
    if (key(SDL_SCANCODE_E))      btn |= N64_R_TRIG;
    if (key(SDL_SCANCODE_I))      btn |= N64_U_CBUTTONS;
    if (key(SDL_SCANCODE_K))      btn |= N64_D_CBUTTONS;
    if (key(SDL_SCANCODE_J))      btn |= N64_L_CBUTTONS;
    if (key(SDL_SCANCODE_L))      btn |= N64_R_CBUTTONS;

    const float keyboard_x = (key(SDL_SCANCODE_D) ? 1.0f : 0.0f) -
                             (key(SDL_SCANCODE_A) ? 1.0f : 0.0f);
    const float keyboard_y = (key(SDL_SCANCODE_W) ? 1.0f : 0.0f) -
                             (key(SDL_SCANCODE_S) ? 1.0f : 0.0f);
    if (keyboard_x != 0.0f || keyboard_y != 0.0f) {
        constexpr float diagonal = 0.70710678f;
        stick_x = keyboard_x * (keyboard_y != 0.0f ? diagonal : 1.0f);
        stick_y = keyboard_y * (keyboard_x != 0.0f ? diagonal : 1.0f);
    }

    *out_btn = btn; *out_x = stick_x; *out_y = stick_y;
}

#include "rs64_bindings.h"
static bool rs64_bind_flag(const char* n) { const char* e = getenv(n); return e && *e && *e != '0'; }
static void rs64_bind_snapshot(rs64_input_snapshot* s) {
    s->have_pad = controller != nullptr;
    for (int b = 0; b < SDL_CONTROLLER_BUTTON_MAX; b++)
        s->pad_btn[b] = controller && SDL_GameControllerGetButton(controller, (SDL_GameControllerButton)b);
    for (int a = 0; a < SDL_CONTROLLER_AXIS_MAX; a++)
        s->pad_axis[a] = controller ? SDL_GameControllerGetAxis(controller, (SDL_GameControllerAxis)a) : 0;
    s->keys = SDL_GetKeyboardState(&s->nkeys);
}
static bool rs64_snap_same(const rs64_input_snapshot& a, const rs64_input_snapshot& b, const uint8_t* keycopy) {
    if (a.have_pad != b.have_pad || memcmp(a.pad_btn, b.pad_btn, sizeof a.pad_btn) || memcmp(a.pad_axis, b.pad_axis, sizeof a.pad_axis)) return false;
    return !b.keys || !keycopy || !memcmp(keycopy, b.keys, (size_t)std::min(b.nkeys, (int)SDL_NUM_SCANCODES));
}
// ROGUESQ_BIND_SELFTEST=1: virtual pad + written keyboard state stepped once per poll (implies BIND_CHECK).
static SDL_Joystick* s_bind_vpad = nullptr;
static void rs64_bind_selftest_step(long step) {
    static bool attached = false;
    if (!attached) {
        attached = true;
        SDL_VirtualJoystickDesc d; SDL_zero(d);
        d.version = SDL_VIRTUAL_JOYSTICK_DESC_VERSION; d.type = SDL_JOYSTICK_TYPE_GAMECONTROLLER;
        d.naxes = SDL_CONTROLLER_AXIS_MAX; d.nbuttons = SDL_CONTROLLER_BUTTON_MAX; d.name = "RS64 bind test pad";
        const int idx = SDL_JoystickAttachVirtualEx(&d);
        if (controller) { SDL_GameControllerClose(controller); controller = nullptr; }
        if (idx >= 0) controller = SDL_GameControllerOpen(idx);
        s_bind_vpad = controller ? SDL_GameControllerGetJoystick(controller) : nullptr;
        fprintf(stderr, "[bind-selftest] vpad idx=%d open=%d\n", idx, controller ? 1 : 0);
    }
    if (!s_bind_vpad) return;
    static const int16_t axv[] = {-32768, -16001, -16000, 0, 15999, 16000, 16001, 32767};
    uint8_t* keys = const_cast<uint8_t*>(SDL_GetKeyboardState(nullptr));
    static const int mk[] = {SDL_SCANCODE_Z, SDL_SCANCODE_X, SDL_SCANCODE_C, SDL_SCANCODE_RETURN, SDL_SCANCODE_UP, SDL_SCANCODE_DOWN,
        SDL_SCANCODE_LEFT, SDL_SCANCODE_RIGHT, SDL_SCANCODE_Q, SDL_SCANCODE_E, SDL_SCANCODE_I, SDL_SCANCODE_K, SDL_SCANCODE_J,
        SDL_SCANCODE_L, SDL_SCANCODE_W, SDL_SCANCODE_A, SDL_SCANCODE_S, SDL_SCANCODE_D};
    // Hold each state for 4 polls so the main thread's joystick update lands before the compare.
    const long k = step / 4;
    const long nb = SDL_CONTROLLER_BUTTON_MAX, na = SDL_CONTROLLER_AXIS_MAX * 8, nk = 18;
    for (int b = 0; b < SDL_CONTROLLER_BUTTON_MAX; b++) SDL_JoystickSetVirtualButton(s_bind_vpad, b, 0);
    for (int a = 0; a < SDL_CONTROLLER_AXIS_MAX; a++) SDL_JoystickSetVirtualAxis(s_bind_vpad, a, 0);
    if (keys) for (int i : mk) keys[i] = 0;
    long r = k % (nb + na + nk + 200);
    if (r < nb) SDL_JoystickSetVirtualButton(s_bind_vpad, (int)r, 1);
    else if ((r -= nb) < na) SDL_JoystickSetVirtualAxis(s_bind_vpad, (int)(r / 8), axv[r % 8]);
    else if ((r -= na) < nk) { if (keys) keys[mk[r]] = 1; }
    else {  // pseudo-random combos
        uint32_t h = (uint32_t)(k * 2654435761u);
        for (int b = 0; b < SDL_CONTROLLER_BUTTON_MAX; b++) { h = h * 1103515245u + 12345u; SDL_JoystickSetVirtualButton(s_bind_vpad, b, (h >> 28) == 0); }
        for (int a = 0; a < SDL_CONTROLLER_AXIS_MAX; a++) { h = h * 1103515245u + 12345u; SDL_JoystickSetVirtualAxis(s_bind_vpad, a, axv[(h >> 16) & 7]); }
        if (keys) for (int i : mk) { h = h * 1103515245u + 12345u; keys[i] = (h >> 29) == 0; }
    }
    SDL_GameControllerUpdate();  // apply the virtual state now (the stable-snapshot guard covers a concurrent pump)
}
// s7619 G6b step 2: overrides from controls.json beside the executable (ROGUESQ_CONTROLS=<path> picks another file).
// Missing file = built-in defaults; a file with any error is rejected whole (defaults kept) with one stderr line.
// ROGUESQ_CONTROLS_DUMP=1 prints the active table as controls.json text to stderr (a starting point for editing).
#include "rs64_bindings_json.h"
std::string rs64_bind_path() {
    if (const char* e = getenv("ROGUESQ_CONTROLS"); e && *e) return e;
    char* base = SDL_GetBasePath(); std::string path = base ? std::string(base) + "controls.json" : "controls.json"; if (base) SDL_free(base);
    return path;
}
static rs64_bind_table rs64_bind_load() {
    const std::string path = rs64_bind_path();
    rs64_bind_table t = rs64_bind_defaults();
    std::ifstream f(path, std::ios::binary);
    if (!f) {
        fprintf(stderr, "[controls] no %s: built-in defaults\n", path.c_str());
    } else {
        std::stringstream ss; ss << f.rdbuf();
        std::string err;
        if (rs64_bind_parse_json(ss.str(), &t, &err))
            fprintf(stderr, "[controls] loaded %s: %zu button bindings\n", path.c_str(), t.buttons.size());
        else
            fprintf(stderr, "[controls] %s rejected (%s): built-in defaults\n", path.c_str(), err.c_str());
    }
    if (rs64_bind_flag("ROGUESQ_CONTROLS_DUMP")) fprintf(stderr, "[controls] active table:\n%s", rs64_bind_to_json(t).c_str());
    return t;
}
// s7620 G6b step 3: the table is live (the F6 panel edits it); g_bind_mu guards it and the capture state.
#include "rs64_controls_panel.h"
static std::mutex g_bind_mu;
static rs64_bind_table& rs64_bind_live_ref() { static rs64_bind_table t = rs64_bind_load(); return t; }  // call under g_bind_mu
static std::atomic<int> g_cap_target{0};
static std::atomic<bool> g_cap_add{false};
static std::atomic<unsigned> g_cap_gen{0};
static std::string g_cap_last;
rs64_bind_table rs64_bind_live_get() { std::lock_guard<std::mutex> lk(g_bind_mu); return rs64_bind_live_ref(); }
void rs64_bind_live_set(const rs64_bind_table& t, const char* why) {
    { std::lock_guard<std::mutex> lk(g_bind_mu); rs64_bind_live_ref() = t; }
    fprintf(stderr, "[controls] table set (%s): %zu button bindings\n", why, t.buttons.size());
}
static std::vector<int>* rs64_bind_dir(rs64_bind_table* t, int target) {
    switch (target) { case RS64_TGT_UP: return &t->key_up; case RS64_TGT_DOWN: return &t->key_down;
                      case RS64_TGT_LEFT: return &t->key_left; case RS64_TGT_RIGHT: return &t->key_right; }
    return nullptr;
}
void rs64_bind_clear(rs64_bind_table* t, int target) {
    if (std::vector<int>* d = rs64_bind_dir(t, target)) { d->clear(); return; }
    t->buttons.erase(std::remove_if(t->buttons.begin(), t->buttons.end(), [&](const rs64_button_bind& e) { return e.n64_mask == (uint16_t)target; }), t->buttons.end());
}
bool rs64_bind_apply(rs64_bind_table* t, int target, const rs64_bind_source& src, bool add) {
    if (std::vector<int>* d = rs64_bind_dir(t, target)) {
        if (src.kind != RS64_SRC_KEY) return false;
        if (!add) d->clear();
        if (std::find(d->begin(), d->end(), src.id) == d->end()) d->push_back(src.id);
        return true;
    }
    if (target <= 0 || target > 0xFFFF) return false;
    if (!add) rs64_bind_clear(t, target);
    for (const auto& e : t->buttons)
        if (e.n64_mask == (uint16_t)target && e.src.kind == src.kind && e.src.id == src.id) return true;
    t->buttons.push_back({(uint16_t)target, src});
    return true;
}
void rs64_bind_capture_arm(int target, bool add) {
    g_cap_add.store(add);
    g_cap_target.store(target);
    g_cap_gen.fetch_add(1);
    if (target) fprintf(stderr, "[controls] capture armed target=%d add=%d\n", target, add ? 1 : 0);
}
int rs64_bind_capture_target() { return g_cap_target.load(); }
bool rs64_bind_capture_add() { return g_cap_add.load(); }
std::string rs64_bind_capture_last() { std::lock_guard<std::mutex> lk(g_bind_mu); return g_cap_last; }
bool rs64_bind_save(std::string* msg) {
    const std::string text = rs64_bind_to_json(rs64_bind_live_get()), path = rs64_bind_path();
    char buf[512];
    // s7666: NO_SAVE_WRITE protects the default file beside the exe; an explicit ROGUESQ_CONTROLS path is caller-owned
    // (the save->reload round-trip test writes one under scratch/), so it is written even then.
    const char* explicit_path = getenv("ROGUESQ_CONTROLS");
    if (getenv("ROGUESQ_NO_SAVE_WRITE") && !(explicit_path && *explicit_path)) {
        snprintf(buf, sizeof buf, "NOT saved (ROGUESQ_NO_SAVE_WRITE): would write %zu bytes to %s", text.size(), path.c_str());
        *msg = buf; fprintf(stderr, "[controls] %s\n", buf); return false;
    }
    const std::string tmp = path + ".tmp";
    bool ok = false;
    if (FILE* f = fopen(tmp.c_str(), "wb")) { ok = fwrite(text.data(), 1, text.size(), f) == text.size(); ok = (fclose(f) == 0) && ok; }
    ok = ok && rename(tmp.c_str(), path.c_str()) == 0;
    snprintf(buf, sizeof buf, ok ? "Saved to %s" : "SAVE FAILED: %s", path.c_str());
    *msg = buf; fprintf(stderr, "[controls] %s\n", buf); return ok;
}
// Capture: the first source that turns on after arming (one already held at arming must be released first).
static void rs64_bind_capture_step(const rs64_input_snapshot& s) {
    static unsigned gen = 0;
    static bool b_btn[SDL_CONTROLLER_BUTTON_MAX], b_pos[SDL_CONTROLLER_AXIS_MAX], b_neg[SDL_CONTROLLER_AXIS_MAX], b_key[SDL_NUM_SCANCODES];
    const int target = g_cap_target.load();
    if (!target) return;
    constexpr int thr = 16000;
    const int nk = std::min(s.nkeys, (int)SDL_NUM_SCANCODES);
    auto key = [&](int k) { return s.keys && k < nk && s.keys[k] != 0; };
    const unsigned g = g_cap_gen.load();
    if (g != gen) {  // baseline at arming
        gen = g;
        for (int i = 0; i < SDL_CONTROLLER_BUTTON_MAX; i++) b_btn[i] = s.have_pad && s.pad_btn[i];
        for (int i = 0; i < SDL_CONTROLLER_AXIS_MAX; i++) { b_pos[i] = s.have_pad && s.pad_axis[i] > thr; b_neg[i] = s.have_pad && s.pad_axis[i] < -thr; }
        for (int i = 0; i < SDL_NUM_SCANCODES; i++) b_key[i] = key(i);
        return;
    }
    bool got = false, cancel = false; rs64_bind_source src{RS64_SRC_KEY, 0, 0};
    auto edge = [&](bool now, bool& base, rs64_bind_source cand) { if (now && !base && !got) { got = true; src = cand; } base = base && now; };
    for (int i = 0; i < SDL_NUM_SCANCODES; i++) {
        const bool now = key(i);
        if (i == SDL_SCANCODE_F6) { b_key[i] = now; continue; }
        if (i == SDL_SCANCODE_ESCAPE) { if (now && !b_key[i]) cancel = true; b_key[i] = now; continue; }
        edge(now, b_key[i], {RS64_SRC_KEY, i, 0});
    }
    const bool keys_only = target < 0;
    for (int i = 0; i < SDL_CONTROLLER_BUTTON_MAX; i++) { const bool now = s.have_pad && s.pad_btn[i]; if (keys_only) b_btn[i] = now; else edge(now, b_btn[i], {RS64_SRC_PAD_BUTTON, i, 0}); }
    for (int i = 0; i < SDL_CONTROLLER_AXIS_MAX; i++) {
        const bool p = s.have_pad && s.pad_axis[i] > thr, n = s.have_pad && s.pad_axis[i] < -thr;
        if (keys_only) { b_pos[i] = p; b_neg[i] = n; continue; }
        edge(p, b_pos[i], {RS64_SRC_AXIS_POS, i, thr});
        edge(n, b_neg[i], {RS64_SRC_AXIS_NEG, i, thr});
    }
    if (cancel) { g_cap_target.store(0); fprintf(stderr, "[controls] capture cancelled (Esc)\n"); return; }
    if (!got) return;
    {
        std::lock_guard<std::mutex> lk(g_bind_mu);
        rs64_bind_apply(&rs64_bind_live_ref(), target, src, g_cap_add.load());
        g_cap_last = rs64_bind_source_name(src);
    }
    g_cap_target.store(0);
    fprintf(stderr, "[controls] captured target=%d add=%d src=%s\n", target, g_cap_add.load() ? 1 : 0, rs64_bind_source_name(src).c_str());
}
void rs64_panel_test_action(const char* what);
// ROGUESQ_BIND_PANEL_TEST=1 (implies SELFTEST): drive the panel's own actions at fixed polls and report the
// old-code-vs-table mismatches per phase. Expected: defaults 0, bind A->pad:b >0, capture logged, reset 0, open 0.
static void rs64_bind_panel_test_step(long polls, long stable, long mism) {
    static long ph_start = 0, ph_stable = 0, ph_mism = 0; static const char* ph = "defaults";
    auto close_phase = [&](const char* next) {
        fprintf(stderr, "[bind-panel-test] phase=%s polls=%ld..%ld stable=%ld mismatches=%ld\n", ph, ph_start, polls, stable - ph_stable, mism - ph_mism);
        ph = next; ph_start = polls; ph_stable = stable; ph_mism = mism;
    };
    // s7666: ROGUESQ_BIND_PANEL_TEST=2 presses Save while A=pad:b is bound (poll 1200) and not after Reset, so the file
    // a second run loads is non-default (round-trip test: scratch/s7666/run.zsh).
    static const bool save_bound = [] { const char* e = getenv("ROGUESQ_BIND_PANEL_TEST"); return e && *e == '2'; }();
    if (polls == 900) {
        close_phase("bindA_padb");
        rs64_bind_table t = rs64_bind_live_get();
        rs64_bind_apply(&t, RS64_N64_A, {RS64_SRC_PAD_BUTTON, SDL_CONTROLLER_BUTTON_B, 0}, false);
        rs64_bind_live_set(t, "panel test bind A=pad:b");
    } else if (polls == 1200 && save_bound) {
        rs64_panel_test_action("save");
    } else if (polls == 1800) {
        close_phase("capture");
        rs64_bind_capture_arm(RS64_N64_B, true);
    } else if (polls == 2100) {
        close_phase("reset");
        fprintf(stderr, "[bind-panel-test] capture pending=%d last=%s\n", rs64_bind_capture_target(), rs64_bind_capture_last().c_str());
        rs64_panel_test_action("reset");
        const rs64_bind_table t = rs64_bind_live_get();
        rs64_bind_table r; std::string err;
        const bool ok = rs64_bind_parse_json(rs64_bind_to_json(t), &r, &err) && rs64_bind_to_json(r) == rs64_bind_to_json(t);
        fprintf(stderr, "[bind-panel-test] json roundtrip=%d bytes=%zu\n", ok ? 1 : 0, rs64_bind_to_json(t).size());
        if (!save_bound) rs64_panel_test_action("save");
    } else if (polls == 3000) {
        close_phase("open");
        rs64_panel_set_open(true);
    } else if (polls == 3600) {
        close_phase("end");
    }
}
static void rs64_bind_poll(uint16_t* btn, float* sx, float* sy) {
    static const bool s_panel_test = rs64_bind_flag("ROGUESQ_BIND_PANEL_TEST");
    static const bool s_selftest = s_panel_test || rs64_bind_flag("ROGUESQ_BIND_SELFTEST");
    static const bool s_check = s_selftest || rs64_bind_flag("ROGUESQ_BIND_CHECK");
    rs64_input_snapshot s;
    rs64_bind_snapshot(&s);
    rs64_bind_capture_step(s);
    { std::lock_guard<std::mutex> lk(g_bind_mu); rs64_bind_eval(rs64_bind_live_ref(), s, btn, sx, sy); }
    if (!s_check) return;
    // Same-run compare: verbatim old SDL code vs the table on the same snapshot; plus a planted mutant (pad A<->X) that must differ.
    static long polls = 0, stable = 0, mism = 0, mut_mism = 0, nonzero = 0, pad_live = 0;
    static const rs64_bind_table s_mut = [] { rs64_bind_table t = rs64_bind_defaults(); std::swap(t.buttons[0].n64_mask, t.buttons[1].n64_mask); return t; }();
    static uint8_t keycopy[SDL_NUM_SCANCODES];
    if (s.keys) memcpy(keycopy, s.keys, (size_t)std::min(s.nkeys, (int)SDL_NUM_SCANCODES));
    uint16_t ob; float ox, oy;
    rs64_bind_old_sdl(&ob, &ox, &oy);
    rs64_input_snapshot s2;
    rs64_bind_snapshot(&s2);
    polls++;
    if (rs64_snap_same(s, s2, s.keys ? keycopy : nullptr)) {
        stable++;
        if (ob || ox != 0.0f || oy != 0.0f) nonzero++;
        { bool live = false; for (bool v : s.pad_btn) live |= v; for (int16_t v : s.pad_axis) live |= v != 0; if (live) pad_live++; }
        if (ob != *btn || memcmp(&ox, sx, 4) || memcmp(&oy, sy, 4)) {
            if (++mism <= 20) fprintf(stderr, "[bind-check] MISMATCH poll=%ld old=%04X %g %g table=%04X %g %g\n", polls, ob, ox, oy, *btn, *sx, *sy);
        }
        uint16_t mb; float mx, my;
        rs64_bind_eval(s_mut, s, &mb, &mx, &my);
        if (mb != ob) mut_mism++;
        if (s_selftest && polls % 97 == 0)
            fprintf(stderr, "[bind-sample] poll=%ld btn=%04X x=%g y=%g lt=%d rt=%d\n", polls, ob, ox, oy,
                    s.pad_axis[SDL_CONTROLLER_AXIS_TRIGGERLEFT], s.pad_axis[SDL_CONTROLLER_AXIS_TRIGGERRIGHT]);
    }
    if (polls % 600 == 0)
        fprintf(stderr, "[bind-check] polls=%ld stable=%ld nonzero=%ld pad_live=%ld mismatches=%ld mutant_mismatches=%ld\n", polls, stable, nonzero, pad_live, mism, mut_mism);
    if (s_panel_test) rs64_bind_panel_test_step(polls, stable, mism);
    if (s_selftest) rs64_bind_selftest_step(polls);
}

#ifdef __APPLE__
extern "C" void rs64_s7640_at_plant(void);
#endif
// s7643 class TS-2 positive control: ROGUESQ_S7643_PLANT=1 bumps this plain (deliberately unsynchronised) counter from the main
// thread (update_gfx) and the game thread (get_n64_input), so a TSan build of main.cpp must report one race pair. Default off.
static bool rs64_s7643_plant_on() { static const bool p = [] { const char* e = std::getenv("ROGUESQ_S7643_PLANT"); return e && *e == '1'; }(); return p; }
static volatile int g_rs64_s7643_plant = 0;
static bool get_n64_input(int controller_num, uint16_t* buttons, float* x, float* y) {
#ifdef __APPLE__
    if (rs64_s7643_plant_on()) g_rs64_s7643_plant = g_rs64_s7643_plant + 1; // s7643 plant (game thread)
    {   // s7640 class AT positive control (see rs64_display_mac.mm)
        static const bool plant = [] { const char* e = std::getenv("ROGUESQ_S7640_AT_PLANT"); return e && *e == '1'; }();
        static std::atomic<bool> done{false};
        if (plant && !done.exchange(true)) rs64_s7640_at_plant();
    }
#endif
    if (controller_num != 0) {
        *buttons = 0; *x = 0.0f; *y = 0.0f;
        return false;
    }

    uint16_t btn = 0;
    float stick_x = 0.0f;
    float stick_y = 0.0f;
    // s7618 G6b: mapping from a table (rs64_bindings.h; defaults == the old hard-coded map). ROGUESQ_BIND_OLD=1 = old code.
    // ROGUESQ_BIND_CHECK=1 evaluates both every poll and logs [bind-check] mismatches (a stable-snapshot guard skips polls
    // where SDL state changed between the reads); ROGUESQ_BIND_SELFTEST=1 drives a virtual pad + keyboard through a sweep.
    static const bool s_bind_old = [] { const char* e = getenv("ROGUESQ_BIND_OLD"); return e && *e && *e != '0'; }();
    if (s_bind_old) {
        rs64_bind_old_sdl(&btn, &stick_x, &stick_y);
    } else {
        rs64_bind_poll(&btn, &stick_x, &stick_y);
    }
    if (rs64_panel_is_open()) { btn = 0; stick_x = 0.0f; stick_y = 0.0f; }  // s7620: F6 panel owns the inputs while open
    {   // s7668: game-thread view of the panel gate (polls gated while open / passed while closed), logged on each change.
        static const bool on = std::getenv("ROGUESQ_PANEL_TEST_WINDOW") != nullptr;
        static int last = -1; static long n = 0;
        if (on) { const int o = rs64_panel_is_open() ? 1 : 0; n++;
            if (o != last) { fprintf(stderr, "[s7668] game-thread gate=%d after %ld polls in previous state\n", o, n); last = o; n = 0; } }
    }
    // ---- Autopilot: deterministic in-game input (wasted-run fix, 2026-08-26) --
    // The game is normally driven to the hangar/mission by synthetic keypresses
    // posted to the window (winctl -> CGEventPostToPid). Those drop silently
    // when window focus is lost, so a "driven" run idles at an early VI width
    // and the probe's phase gate times out, wasting the whole run (s2506 needed
    // three attempts, 0 presses seen by the game on the failed one). ROGUESQ_
    // AUTOPILOT injects the same schedule from inside the input poll: no OS
    // focus/keypost, so delivery is deterministic. It ORs into btn below, so the
    // existing [pad-host] edge log confirms each press.
    //   ROGUESQ_AUTOPILOT="3:start,7:start,15:a,..."  comma-sep <seconds>:<key>
    //     (bare "<sec>" = start). key: start,a,b,z,up,down,left,right.
    //     Times are from process start (like PROBE_KEYS' default).
    //   ROGUESQ_AUTOPILOT_HOLD_MS   press hold, default 150 (matches winctl).
    //   ROGUESQ_AUTOPILOT_STOP_WIDTH  stop all presses once this VI width is
    //     reached (set 512 to stop at the hangar, avoiding a mash into stubbed
    //     mission code that blacks the screen).
    //   s6747: "<sec>:w<width>" is a phase gate, not a press: the schedule waits
    //     there until the committed VI width equals <width>, then rebases its
    //     clock so that instant reads <sec>. Later events keep their absolute
    //     times, now relative to the gate (hangar->crawl drifts by seconds per run).
    {
        struct ApEv { double t; uint16_t btn; float sx, sy; uint32_t waitw; };
        static bool     s_init = false;
        static bool     s_on = false;
        static ApEv     s_ev[512];
        static int      s_nev = 0;
        static int      s_idx = 0;
        static Uint32   s_t0 = 0;
        static double   s_hold = 0.150;
        static uint32_t s_stop_w = 0;
        static uint16_t s_held = 0;
        static float    s_held_sx = 0.0f, s_held_sy = 0.0f;
        static double   s_release_at = 0.0;
        // s7371: ROGUESQ_AUTOPILOT_CLOCK=frames keys every event time (and the hold, and the w<width> rebase) to game
        // frames = cumulative RDP fullsyncs / ROGUESQ_AUTOPILOT_FPS (default 30) instead of wall time, so a slow build
        // (TSan, ~13 gfx tasks/s) walks the same route as full speed. Default (unset / "wall") = old wall clock.
        static bool     s_frames = false;
        static double   s_fps = 30.0;
        static double   s_base = 0.0;   // clock value at schedule start / last gate rebase (seconds in the chosen domain)
        auto ap_now = [&]() -> double {
            return s_frames ? (double)rs64_dpc_get_cumulative_fullsyncs() / s_fps : SDL_GetTicks() / 1000.0;
        };
        if (!s_init) {
            s_init = true;
            const char* spec = std::getenv("ROGUESQ_AUTOPILOT");
            if (spec && *spec) {
                if (const char* h = std::getenv("ROGUESQ_AUTOPILOT_HOLD_MS"))
                    s_hold = atof(h) / 1000.0;
                if (const char* sw = std::getenv("ROGUESQ_AUTOPILOT_STOP_WIDTH"))
                    s_stop_w = (uint32_t)strtoul(sw, nullptr, 0);
                auto keybtn = [](const char* n) -> uint16_t {
                    if (!strcmp(n, "start") || !strcmp(n, "return")) return N64_START_BUTTON;
                    if (!strcmp(n, "a"))     return N64_A_BUTTON;
                    if (!strcmp(n, "b"))     return N64_B_BUTTON;
                    if (!strcmp(n, "z"))     return N64_Z_TRIG;
                    if (!strcmp(n, "l"))     return N64_L_TRIG;
                    if (!strcmp(n, "r"))     return N64_R_TRIG;
                    if (!strcmp(n, "up"))    return N64_U_JPAD;
                    if (!strcmp(n, "down"))  return N64_D_JPAD;
                    if (!strcmp(n, "left"))  return N64_L_JPAD;
                    if (!strcmp(n, "right")) return N64_R_JPAD;
                    // s6802: C buttons, same names as rs64_oracle --press (cup cdown cleft cright).
                    if (!strcmp(n, "cup"))    return N64_U_CBUTTONS;
                    if (!strcmp(n, "cdown"))  return N64_D_CBUTTONS;
                    if (!strcmp(n, "cleft"))  return N64_L_CBUTTONS;
                    if (!strcmp(n, "cright")) return N64_R_CBUTTONS;
                    // s5435: an unknown name used to become START silently (start pauses flight).
                    fprintf(stderr, "[autopilot] WARNING unknown key '%s' -> START\n", n);
                    return N64_START_BUTTON;
                };
                char buf[8192];
                strncpy(buf, spec, sizeof(buf) - 1);
                buf[sizeof(buf) - 1] = '\0';
                char* save = nullptr;
                for (char* tok = strtok_r(buf, ",", &save);
                     tok && s_nev < 512; tok = strtok_r(nullptr, ",", &save)) {
                    double t = 0.0; char kbuf[16]; kbuf[0] = '\0';
                    unsigned ww = 0;
                    if (sscanf(tok, " %lf:w%u", &t, &ww) == 2 && ww) {
                        s_ev[s_nev].t = t; s_ev[s_nev].btn = 0; s_ev[s_nev].sx = s_ev[s_nev].sy = 0.0f;
                        s_ev[s_nev].waitw = ww; s_nev++; continue;
                    }
                    if (sscanf(tok, " %lf:%15[a-z]", &t, kbuf) < 1) continue;
                    s_ev[s_nev].t = t; s_ev[s_nev].waitw = 0;
                    // s5418: stick pseudo-keys (sl/sr/su/sd) for in-mission flight.
                    s_ev[s_nev].sx = s_ev[s_nev].sy = 0.0f;
                    if (!strcmp(kbuf, "sl")) { s_ev[s_nev].btn = 0; s_ev[s_nev].sx = -1.0f; }
                    else if (!strcmp(kbuf, "sr")) { s_ev[s_nev].btn = 0; s_ev[s_nev].sx = 1.0f; }
                    else if (!strcmp(kbuf, "su")) { s_ev[s_nev].btn = 0; s_ev[s_nev].sy = 1.0f; }
                    else if (!strcmp(kbuf, "sd")) { s_ev[s_nev].btn = 0; s_ev[s_nev].sy = -1.0f; }
                    // s5914: stick+A combos (sla/sra/sua/sda): one held event carries both, since only one event is held at a time.
                    else if (!strcmp(kbuf, "sla")) { s_ev[s_nev].btn = N64_A_BUTTON; s_ev[s_nev].sx = -1.0f; }
                    else if (!strcmp(kbuf, "sra")) { s_ev[s_nev].btn = N64_A_BUTTON; s_ev[s_nev].sx = 1.0f; }
                    else if (!strcmp(kbuf, "sua")) { s_ev[s_nev].btn = N64_A_BUTTON; s_ev[s_nev].sy = 1.0f; }
                    else if (!strcmp(kbuf, "sda")) { s_ev[s_nev].btn = N64_A_BUTTON; s_ev[s_nev].sy = -1.0f; }
                    else s_ev[s_nev].btn = keybtn(kbuf);
                    s_nev++;
                }
                if (const char* ck = std::getenv("ROGUESQ_AUTOPILOT_CLOCK")) s_frames = !strcmp(ck, "frames");
                if (const char* fp = std::getenv("ROGUESQ_AUTOPILOT_FPS")) { const double f = atof(fp); if (f > 0.0 && f < 1000.0) s_fps = f; }
                if (s_nev > 0) { s_on = true; s_t0 = SDL_GetTicks(); s_base = ap_now(); }
                fprintf(stderr, "[autopilot] armed: %d events hold=%.0fms stop_width=%u clock=%s fps=%.1f\n",
                        s_nev, s_hold * 1000.0, s_stop_w, s_frames ? "frames" : "wall", s_fps);
                fflush(stderr);
            }
        }
        if (s_on) {
            const double el = ap_now() - s_base;
            const bool stop = (s_stop_w != 0 && rs64_vi_committed_width() == s_stop_w);
            if ((s_held || s_held_sx != 0.0f || s_held_sy != 0.0f) && el >= s_release_at) { s_held = 0; s_held_sx = s_held_sy = 0.0f; }
            if (!stop && s_idx < s_nev && s_ev[s_idx].waitw && el >= s_ev[s_idx].t &&
                rs64_vi_committed_width() == s_ev[s_idx].waitw) {
                s_base = ap_now() - s_ev[s_idx].t;
                fprintf(stderr, "[autopilot] gate %d/%d width=%u reached at %s %.1f s -> clock rebased to %.1f\n",
                        s_idx + 1, s_nev, s_ev[s_idx].waitw, s_frames ? "frames" : "wall", el, s_ev[s_idx].t);
                fflush(stderr);
                s_idx++;
            } else if (!stop && !s_held && s_held_sx == 0.0f && s_held_sy == 0.0f && s_idx < s_nev && !s_ev[s_idx].waitw && el >= s_ev[s_idx].t) {
                s_held = s_ev[s_idx].btn;
                s_held_sx = s_ev[s_idx].sx; s_held_sy = s_ev[s_idx].sy;
                s_release_at = el + s_hold;
                (fprintf)(stderr, "[autopilot] fire %d/%d t=%.1f btn=0x%04X vi_width=%u wall=%.1f fs=%u\n",
                        s_idx + 1, s_nev, el, (unsigned)s_held,
                        (unsigned)rs64_vi_committed_width(), (SDL_GetTicks() - s_t0) / 1000.0,
                        (unsigned)rs64_dpc_get_cumulative_fullsyncs());
                fflush(stderr);
                s7671_key = s_idx + 1; s7671_btn = (unsigned)s_held;
                s_idx++;
            }
            // s7671 TEST-ONLY lever: ROGUESQ_S7671_FX_ON_KEY=1 arms the game's port-0 rumble effect slot on every autopilot key
            // press, writing the same fields startRumbleEffect 0x80002ADC writes (slot 0x80110520: +0x70 effect ptr, +0x74/+0x80
            // = 0, +0x84 = handle from 0x80110744, then +0x6C/+0x6B = 1), so an effect is LIVE when a pause/abort/confirm key
            // lands. The game's SI service turns it into osMotorStart/Stop as usual. ROGUESQ_S7671_FX=<hex offset into the
            // 0x8010BBD0 effect table> picks the effect (default 0x54, updatePlayerCraftPhysics). Skipped while 0x80110740
            // (suspended) is set. No lock is taken (startRumbleEffect's 0x80110750 queue is guest-only): test use only.
            // ROGUESQ_S7671_FX_TRAIN_MS=N: after each START press keep re-arming every 200 ms for N ms, so an effect is live
            // through whatever transition the press starts (abort -> beginMissionEndTransition); `[s7671-fx] train end` marks the last.
            if (s7671_key) {
                static const bool fx = [] { const char* e = std::getenv("ROGUESQ_S7671_FX_ON_KEY"); return e && *e == '1'; }();
                static const uint32_t fxo = [] { const char* e = std::getenv("ROGUESQ_S7671_FX"); return e && *e ? (uint32_t)strtoul(e, nullptr, 16) : 0x54u; }();
                static const long long train = [] { const char* e = std::getenv("ROGUESQ_S7671_FX_TRAIN_MS"); return e && *e ? atoll(e) : 0LL; }();
                static long long s_tr_end = 0, s_tr_last = 0;
                const long long nowms = rs64_s5773_ms();
                bool fire = false;
                if (s7671_key > 0) { fire = true; if (train > 0 && s7671_btn == 0x1000u) s_tr_end = nowms + train; s7671_key = -s7671_key; }
                else if (s_tr_end) {
                    if (nowms >= s_tr_end) { fprintf(stderr, "[s7671-fx] train end key=%d wall_ms=%lld\n", -s7671_key, nowms); s_tr_end = 0; }
                    else if (nowms - s_tr_last >= 200) fire = true;
                }
                volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
                if (fx && rd && fire) {
                    s_tr_last = nowms;
                    auto w32 = [&](uint32_t a, uint32_t v) { rd[a + 3] = v >> 24; rd[a + 2] = v >> 16; rd[a + 1] = v >> 8; rd[a] = v; };
                    const uint8_t susp = rd[0x110740u ^ 3];
                    uint32_t h = rs64_rdram_u32(rd, 0x110744u);
                    // The descriptor is {u32 len, u16* curveA, u16* curveB} (processPolledControllerData 0x8000286C-0x800028F4);
                    // before the effect table is resident (boot) it holds junk and the SI service faults on it (s7671 arm A,
                    // SIGBUS at t=6 s on ptr 0x3F000000), so arm only when both curve pointers are KSEG0 RAM (word 0 is not a plain length: 0x00FA0014 in mission).
                    const uint32_t d = (0x8010BBD0u + fxo) & 0xFFFFFFu, dl = rs64_rdram_u32(rd, d),
                                   da = rs64_rdram_u32(rd, d + 4), db = rs64_rdram_u32(rd, d + 8);
                    const bool ok = da >= 0x80000400u && da < 0x80800000u && db >= 0x80000400u && db < 0x80800000u;
                    if (!ok) fprintf(stderr, "[s7671-fx] skip key=%d desc len=%u a=0x%08X b=0x%08X\n", -s7671_key, dl, da, db);
                    if (!susp && ok) {
                        const uint32_t s = 0x110520u;
                        w32(s + 0x70, 0x8010BBD0u + fxo); w32(s + 0x74, 0); w32(s + 0x80, 0); w32(s + 0x84, h);
                        w32(0x110744u, h + 1 == 0xFFFFFFFFu ? 0 : h + 1);
                        rd[(s + 0x6C) ^ 3] = 1; rd[(s + 0x6B) ^ 3] = 1;
                    }
                    if (ok) fprintf(stderr, "[s7671-fx] arm key=%d btn=0x%04X fx=0x%08X handle=%u susp=%u wall_ms=%lld\n", -s7671_key,
                            s7671_btn, 0x8010BBD0u + fxo, h, (unsigned)susp, (long long)rs64_s5773_ms());
                }
            }
            if (stop) { s_held = 0; s_held_sx = s_held_sy = 0.0f; }
            btn |= s_held;
            if (s_held_sx != 0.0f) stick_x = s_held_sx;
            if (s_held_sy != 0.0f) stick_y = s_held_sy;
        }
    }

    // s5891: ROGUESQ_PLPOS_POKE="x,y,z;x,y,z;..." is a TEST-ONLY lever. After mission poll m>=ROGUESQ_PLPOS_POKE_FROM (default 3000)
    // the ship pos (+0x4C/50/54) is re-written every poll to waypoint k, advancing every 450 polls (~15 s). Logs [plpoke].
    {
        static const char* pk = std::getenv("ROGUESQ_PLPOS_POKE");
        static const unsigned from = std::getenv("ROGUESQ_PLPOS_POKE_FROM") ? (unsigned)atoi(std::getenv("ROGUESQ_PLPOS_POKE_FROM")) : 3000u;
        static unsigned m = 0;
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        static const bool any_origin = std::getenv("ROGUESQ_PLPOS_POKE_ANY") != nullptr;  // s6893: dd>1 and wide move the origin and put the player in the spill arena
        if (pk && *pk && rd && (any_origin || ((uint32_t)rs64_vi_committed_origin() & 0xFFFFFFu) == 0x690400u)) {
            const uint32_t p = rs64_rdram_u32(rd, 0x137DB8u + 4) & 0xFFFFFFu;
            if (p >= 0x1000u && p < (any_origin ? 0xFFFF00u : 0x7FFF00u) && ++m >= from) {
                float wp[64][3]; unsigned nw = 0; const char* c = pk;
                while (nw < 64 && sscanf(c, "%f,%f,%f", &wp[nw][0], &wp[nw][1], &wp[nw][2]) == 3) { nw++; c = strchr(c, ';'); if (!c) break; c++; }
                if (nw) {
                    static const unsigned dwell = [] { const char* e = std::getenv("ROGUESQ_PLPOS_POKE_DWELL"); const unsigned d = e ? (unsigned)atoi(e) : 450u; return d ? d : 1u; }();  // s7363: 0 would divide by zero  // s5892
                    const unsigned k = ((m - from) / dwell) % nw;
                    for (int i = 0; i < 3; i++) { uint32_t u; memcpy(&u, &wp[k][i], 4); const uint32_t b = (p + 0x4C + 4 * i) & ~3u; volatile uint8_t* w = const_cast<volatile uint8_t*>(rd); w[b + 3] = u >> 24; w[b + 2] = u >> 16; w[b + 1] = u >> 8; w[b] = u; }
                    if (((m - from) % dwell) == 0) fprintf(stderr, "[plpoke] m=%u k=%u/%u pos=(%g,%g,%g)\n", m, k, nw, (double)wp[k][0], (double)wp[k][1], (double)wp[k][2]);
                }
            }
        }
    }

    // s5821: ROGUESQ_LOG_PLPOS=1 logs ship pos (+0x4C/+0x50/+0x54) with the injected stick/buttons ~2 Hz in-mission,
    // so held-key phases can be compared inside ONE run (s5820: 150ms taps every 3s moved the ship ~0.05/update).
    {
        static int s_lp = -1; static unsigned s_n = 0;
        static const unsigned s_every = std::getenv("ROGUESQ_PLPOS_EVERY") ? (unsigned)atoi(std::getenv("ROGUESQ_PLPOS_EVERY")) : 30u;  // s5920
        if (s_lp < 0) { const char* g = std::getenv("ROGUESQ_LOG_PLPOS"); s_lp = (g && *g == '1') ? 1 : 0; }
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (s_lp && rd && ((uint32_t)rs64_vi_committed_origin() & 0xFFFFFFu) == 0x690400u && (++s_n % s_every) == 0) {
            const uint32_t p = rs64_rdram_u32(rd, 0x137DB8u + 4) & 0xFFFFFFu;
            if (p >= 0x1000u && p < 0x7FFF00u) {
                float v[3]; for (int i = 0; i < 3; i++) { uint32_t u = rs64_rdram_u32(rd, p + 0x4C + 4 * i); memcpy(&v[i], &u, 4); }
                fprintf(stderr, "[plpos] el=%.1f n=%u pos=(%g,%g,%g) sx=%.1f sy=%.1f btn=0x%04X\n",
                        (double)SDL_GetTicks() / 1000.0, s_n, (double)v[0], (double)v[1], (double)v[2], (double)stick_x, (double)stick_y, (unsigned)btn);
                if (s_every < 30u) {  // s5920: tilt matrices (+0x74 / +0xC0, 9 floats each) -> forward vector offline
                    float m1[9], m2[9]; for (int i = 0; i < 9; i++) { uint32_t u = rs64_rdram_u32(rd, p + 0x74 + 4 * i); memcpy(&m1[i], &u, 4); u = rs64_rdram_u32(rd, p + 0xC0 + 4 * i); memcpy(&m2[i], &u, 4); }
                    fprintf(stderr, "[plmat] n=%u A=%g,%g,%g,%g,%g,%g,%g,%g,%g B=%g,%g,%g,%g,%g,%g,%g,%g,%g\n", s_n, (double)m1[0],(double)m1[1],(double)m1[2],(double)m1[3],(double)m1[4],(double)m1[5],(double)m1[6],(double)m1[7],(double)m1[8],(double)m2[0],(double)m2[1],(double)m2[2],(double)m2[3],(double)m2[4],(double)m2[5],(double)m2[6],(double)m2[7],(double)m2[8]);
                }
            }
        }
    }

    // s6686: ROGUESQ_LOG_GRIDSPAWN=1 walks the DAT-item activation grid (801375D8: +4/+8 origin, +14/+18 dims,
    // +1C u16 cell heads; 12-byte records in pool *80136FCC, +2 next, +4 state, +6 cell, +8 descriptor).
    // Original updateActiveGridCellState 80047368 activates a linked state-3 record when the craft record
    // 80137DC0 (+0/+8 x/z; 801375F8 when 8010CA1C&8) is within +-1.5 cells and XZ distance 48, and
    // isDatItemConditionMet passes; activation unlinks the record. Logs every Nth mission poll: linked total,
    // records within 48, records that vanished since the last sample (activation control) and every "Tank" item.
    {
        static int s_gs = -1; static unsigned s_n = 0;
        static const unsigned s_every = std::getenv("ROGUESQ_GRIDSPAWN_EVERY") ? (unsigned)atoi(std::getenv("ROGUESQ_GRIDSPAWN_EVERY")) : 60u;
        static std::vector<uint32_t> s_prev, s_tanks;
        if (s_gs < 0) { const char* g = std::getenv("ROGUESQ_LOG_GRIDSPAWN"); s_gs = (g && *g == '1') ? 1 : 0; }
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (s_gs && rd && ((uint32_t)rs64_vi_committed_origin() & 0xFFFFFFu) == 0x690400u && (++s_n % s_every) == 0) {
            auto u16 = [&](uint32_t a) -> uint32_t { return (rs64_rdram_u32(rd, a & ~3u) >> ((a & 2u) ? 0 : 16)) & 0xFFFFu; };
            auto fl = [&](uint32_t a) -> float { uint32_t u = rs64_rdram_u32(rd, a); float f; memcpy(&f, &u, 4); return f; };
            auto name = [&](uint32_t d) -> std::string { std::string s; for (uint32_t i = 0; i < 24; i++) { uint32_t c = rs64_rdram_u8(rd, d + 0xA8u + i); if (c < 0x20 || c > 0x7E) break; s.push_back((char)c); } return s; };
            const uint32_t G = 0x1375D8u;
            const float ox = fl(G + 4), oz = fl(G + 8);
            const uint32_t w = rs64_rdram_u32(rd, G + 0x14), h = rs64_rdram_u32(rd, G + 0x18);
            const uint32_t cells = rs64_rdram_u32(rd, G + 0x1C) & 0xFFFFFFu, pool = rs64_rdram_u32(rd, 0x136FCCu) & 0xFFFFFFu;
            const uint32_t rec = (rs64_rdram_u32(rd, 0x10CA1Cu) & 8u) ? 0x1375F8u : 0x137DC0u;  // getCraftRecordByIdx(0) = 80137DBC+4 (delay-slot addiu)
            const float px = fl(rec), pz = fl(rec + 8);
            const unsigned b39 = rs64_rdram_u8(rd, 0x130B39u), pend = rs64_rdram_u32(rd, 0x1375D4u);
            if (w && h && w <= 1024 && h <= 1024 && w * h <= 65536u && cells < 0x7F0000u && pool < 0x7F0000u) {
                std::vector<uint32_t> cur; unsigned near48 = 0, steps = 0;
                for (uint32_t c = 0; c < w * h; c++) {
                    uint32_t idx = u16(cells + 2 * c);
                    for (int k = 0; idx != 0xFFFFu && k < 4096; k++, steps++) {
                        const uint32_t r = pool + 12u * idx, d = rs64_rdram_u32(rd, r + 8) & 0xFFFFFFu;
                        if (d >= 0x1000u && d < 0x7FFF00u) {
                            cur.push_back(d);
                            const float dx = fl(d + 0x10) - px, dz = fl(d + 0x18) - pz;
                            if (dx * dx + dz * dz <= 48.0f * 48.0f) near48++;
                            if (u16(d) == 0x14u && name(d).find("Tank") != std::string::npos &&
                                std::find(s_tanks.begin(), s_tanks.end(), d) == s_tanks.end()) s_tanks.push_back(d);
                        }
                        idx = u16(r + 2);
                    }
                }
                std::sort(cur.begin(), cur.end());
                fprintf(stderr, "[gridspawn] el=%.1f n=%u p=(%g,%g) pcell=(%d,%d) o=(%g,%g) dims=%ux%u linked=%zu near48=%u b39=%u pend=%u steps=%u\n",
                        (double)SDL_GetTicks() / 1000.0, s_n, (double)px, (double)pz, (int)((px - ox) * 0.25f), (int)((pz - oz) * 0.25f),
                        (double)ox, (double)oz, w, h, cur.size(), near48, b39, pend, steps);
                unsigned gone = 0;
                for (uint32_t d : s_prev) if (!std::binary_search(cur.begin(), cur.end(), d) && gone++ < 12) {
                    const float dx = fl(d + 0x10) - px, dz = fl(d + 0x18) - pz;
                    fprintf(stderr, "[gridspawn-act] n=%u desc=%06X type=%u name=%s dist=%.1f slot=%04X\n", s_n, d, u16(d), name(d).c_str(),
                            (double)std::sqrt(dx * dx + dz * dz), u16(d + 6));
                }
                for (uint32_t d : s_tanks) {
                    const float tx = fl(d + 0x10), tz = fl(d + 0x18), dx = tx - px, dz = tz - pz;
                    fprintf(stderr, "[gridspawn-tank] n=%u desc=%06X name=%s pos=(%g,%g) tcell=(%d,%d) dist=%.1f linked=%d slot=%04X\n",
                            s_n, d, name(d).c_str(), (double)tx, (double)tz, (int)((tx - ox) * 0.25f), (int)((tz - oz) * 0.25f),
                            (double)std::sqrt(dx * dx + dz * dz), (int)std::binary_search(cur.begin(), cur.end(), d), u16(d + 6));
                }
                s_prev.swap(cur);
            }
        }
    }

    // s5685: ROGUESQ_ALT_HOLD=<deadband> is a TEST-ONLY closed-loop autopilot. s5684 measured stick_y moving
    // ship pos y (sy=+1 -> +0.12/poll, sy=-1 -> -0.19/poll). Latch the ship y on the first mission poll and
    // drive stick_y toward it whenever no scripted stick_y is held. Logs ~1 Hz (control: err/sy visible).
    {
        static float s_ah_db = -1.0f;
        static bool s_ah_have = false;
        static double s_ah_target = 0.0;
        static unsigned s_ah_n = 0, s_ah_act = 0;
        if (s_ah_db < -0.5f) { const char* g = std::getenv("ROGUESQ_ALT_HOLD"); s_ah_db = (g && *g) ? (float)atof(g) : 0.0f; }
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (s_ah_db > 0.0f && rd && ((uint32_t)rs64_vi_committed_origin() & 0xFFFFFFu) == 0x690400u) {
            const uint32_t p = rs64_rdram_u32(rd, 0x137DB8u + 4) & 0xFFFFFFu;
            if (p >= 0x1000u && p < 0x7FFF00u) {
                uint32_t u = rs64_rdram_u32(rd, p + 0x50); float y; memcpy(&y, &u, 4);
                if (y == y && y > -1.0e6f && y < 1.0e6f) {
                    if (!s_ah_have && y == 0.0f) { /* s5783: pre-spawn y==0 latch made the hold climb into the ceiling */ }
                    else {
                    if (!s_ah_have) { s_ah_have = true; s_ah_target = y; fprintf(stderr, "[althold] target y=%.3f db=%.2f\n", (double)y, (double)s_ah_db); }
                    const double err = (double)y - s_ah_target;
                    if (stick_y == 0.0f) {
                        if (err > s_ah_db) { stick_y = -1.0f; s_ah_act++; }
                        else if (err < -s_ah_db) { stick_y = 1.0f; s_ah_act++; }
                    }
                    if ((++s_ah_n % 60) == 1)
                        fprintf(stderr, "[althold] n=%u y=%.3f err=%.3f sy=%.1f acted=%u\n", s_ah_n, (double)y, err, (double)stick_y, s_ah_act);
                }
                    }
            }
        }
    }

    // s5929: ROGUESQ_AIM=<deadband rad> + ROGUESQ_AIM_TARGETS="x,y,z;..." is a TEST-ONLY closed-loop aim autopilot
    // (G1: s5928 found the scripted stick never steers toward class-1 NPCs). Steers the ship toward the nearest
    // not-yet-visited target whenever no scripted stick is held. Actuation starts at SDL el >= ROGUESQ_AIM_FROM_S
    // (default 0); before that it logs the same errors with stick=0 = the in-run zero-stick control.
    // CALIBRATION (offline, scratch/agent/m6/s5920b_steer/run.log, PLE=2, 4867 [plpos]/[plmat] rows):
    //  - forward axis: the +0x74/+0xC0 "tilt" matrices are a constant 10-deg roll in ALL rows (incl. stick windows),
    //    so NO matrix row/column is forward. Forward is therefore the velocity: pos(n) - pos(n-4) (A-held flight
    //    moves 0.075-0.125 u/poll along a fixed heading; heading = atan2(dx,dz) is constant without stick input).
    //  - yaw sign: sx=+1 held -> heading atan2(dx,dz) DECREASES ~45 deg/s (e.g. 4.3 -> -100.6 deg in 2.4 s, ship
    //    circles r~2.5 u); sx=-1 -> heading INCREASES (-111.6 -> 9.1 in 2.4 s). So sx = -k*yaw_err.
    //  - pitch sign: sy=+1 held raised y (-6.5 -> -0.1, and loops if held); sy=-1 dropped y (-9.8 -> -18.1).
    //    sy is a pitch RATE, so sy = +k*(desired climb angle - current climb angle atan2(vy, |vxz|)).
    // Logs [aim] ~1 Hz: target idx, dist, yaw/pitch error (deg), stick out, actuation count.
    {
        static float s_aim_db = -1.0f;
        static float s_tg[64][3]; static unsigned s_ntg = 0; static bool s_vis[64];
        static double s_from = 0.0;
        static float s_hist[8][3]; static unsigned s_hn = 0;
        static unsigned s_n = 0, s_act = 0, s_cur = 64, s_cur_polls = 0, s_visits = 0;
        static double s_sum_ctl = 0, s_sum_act = 0; static unsigned s_cnt_ctl = 0, s_cnt_act = 0;
        if (s_aim_db < -0.5f) {
            const char* g = std::getenv("ROGUESQ_AIM"); s_aim_db = (g && *g) ? (float)atof(g) : 0.0f;
            const char* t = std::getenv("ROGUESQ_AIM_TARGETS");
            while (t && *t && s_ntg < 64 && sscanf(t, "%f,%f,%f", &s_tg[s_ntg][0], &s_tg[s_ntg][1], &s_tg[s_ntg][2]) == 3) { s_vis[s_ntg] = false; s_ntg++; t = strchr(t, ';'); if (!t) break; t++; }
            const char* f = std::getenv("ROGUESQ_AIM_FROM_S"); s_from = (f && *f) ? atof(f) : 0.0;
            if (s_aim_db > 0.0f) fprintf(stderr, "[aim] armed db=%.3f targets=%u from_s=%.1f\n", (double)s_aim_db, s_ntg, s_from);
        }
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (s_aim_db > 0.0f && s_ntg && rd && ((uint32_t)rs64_vi_committed_origin() & 0xFFFFFFu) == 0x690400u) {
            const uint32_t p = rs64_rdram_u32(rd, 0x137DB8u + 4) & 0xFFFFFFu;
            if (p >= 0x1000u && p < 0x7FFF00u) {
                float v[3]; for (int i = 0; i < 3; i++) { uint32_t u = rs64_rdram_u32(rd, p + 0x4C + 4 * i); memcpy(&v[i], &u, 4); }
                if (v[0] == v[0] && v[1] == v[1] && v[2] == v[2] && !(v[0] == 0.0f && v[2] == 0.0f)) {
                    memcpy(s_hist[s_hn % 8], v, sizeof v); s_hn++;
                    // nearest unvisited target; visited when within 1.5 u or after 600 polls (~40 s) on it
                    auto d2 = [&](unsigned k) { float a = s_tg[k][0]-v[0], b = s_tg[k][1]-v[1], c = s_tg[k][2]-v[2]; return a*a+b*b+c*c; };
                    if (s_cur < s_ntg && (d2(s_cur) < 2.25f || s_cur_polls > 600)) { s_vis[s_cur] = true; s_visits++; s_cur = 64; }
                    if (s_cur >= s_ntg) {
                        unsigned nv = 0; for (unsigned k = 0; k < s_ntg; k++) nv += s_vis[k] ? 0 : 1;
                        if (!nv) for (unsigned k = 0; k < s_ntg; k++) s_vis[k] = false;
                        float best = 1e30f; for (unsigned k = 0; k < s_ntg; k++) if (!s_vis[k] && d2(k) < best) { best = d2(k); s_cur = k; }
                        s_cur_polls = 0;
                    }
                    s_cur_polls++;
                    const unsigned L = 4;
                    double yerr = 0, perr = 0; bool valid = false;
                    // s7363 (class AN): the nearest-target search leaves s_cur = 64 (one past s_tg) when no target has a finite
                    // d2 < 1e30 (a "nan" or far ROGUESQ_AIM_TARGETS entry, or an inf ship position): no aim this poll.
                    if (s_hn > L && s_cur < s_ntg) {
                        const float* o = s_hist[(s_hn - 1 - L) % 8];
                        const double dx = v[0]-o[0], dy = v[1]-o[1], dz = v[2]-o[2], hs = std::sqrt(dx*dx+dz*dz);
                        if (hs > 0.02 * L && hs < 2.0 * L) {  // moving, and not a respawn/teleport jump
                            const double tx = s_tg[s_cur][0]-v[0], ty = s_tg[s_cur][1]-v[1], tz = s_tg[s_cur][2]-v[2];
                            yerr = std::atan2(tx, tz) - std::atan2(dx, dz);
                            while (yerr > M_PI) yerr -= 2 * M_PI; while (yerr < -M_PI) yerr += 2 * M_PI;
                            perr = std::atan2(ty, std::sqrt(tx*tx+tz*tz)) - std::atan2(dy, hs);
                            valid = true;
                        }
                    }
                    const double el = (double)SDL_GetTicks() / 1000.0;
                    const bool on = el >= s_from;
                    if (valid) { if (on) { s_sum_act += std::fabs(yerr); s_cnt_act++; } else { s_sum_ctl += std::fabs(yerr); s_cnt_ctl++; } }
                    if (on && valid && stick_x == 0.0f && stick_y == 0.0f) {
                        // s5929 run 1 (s5929_aim): k=2 both axes chattered sx=+-1 at |yerr|~180 (wrap flips the sign each
                        // sample, net no turn) and sy=0.2-0.4 never lifted the ship off y~-18. Fix: latch the turn
                        // direction while |yerr|>120 deg; pitch gain 6 (full stick at ~10 deg).
                        static float s_turn = 0.0f;
                        if (std::fabs(yerr) > 2.0944 && s_turn != 0.0f) stick_x = s_turn;
                        else if (std::fabs(yerr) > s_aim_db) stick_x = (float)std::max(-1.0, std::min(1.0, -2.0 * yerr));
                        s_turn = (std::fabs(yerr) > 2.0944) ? (s_turn != 0.0f ? s_turn : (yerr > 0 ? -1.0f : 1.0f)) : 0.0f;
                        if (std::fabs(perr) > s_aim_db) stick_y = (float)std::max(-1.0, std::min(1.0, 6.0 * perr));
                        if (stick_x != 0.0f || stick_y != 0.0f) s_act++;
                    }
                    if ((++s_n % 16) == 1)
                        fprintf(stderr, "[aim] el=%.1f %s tgt=%u d=%.2f yerr=%.1f perr=%.1f sx=%.2f sy=%.2f act=%u visits=%u pos=(%.2f,%.2f,%.2f) mean|yerr| ctl=%.1f(%u) act=%.1f(%u)\n",
                                el, on ? "ON" : "ctl", s_cur, s_cur < s_ntg ? std::sqrt((double)d2(s_cur)) : -1.0, yerr * 57.29578, perr * 57.29578, (double)stick_x, (double)stick_y,
                                s_act, s_visits, (double)v[0], (double)v[1], (double)v[2],
                                s_cnt_ctl ? s_sum_ctl / s_cnt_ctl * 57.29578 : 0.0, s_cnt_ctl, s_cnt_act ? s_sum_act / s_cnt_act * 57.29578 : 0.0, s_cnt_act);
                }
            }
        }
    }

    // s5492: ROGUESQ_GODMODE=1 is a TEST-ONLY lever for M6 endurance soaks. The player
    // record table at 0x80137DB8 (stride 0x2A0, found via getPlayerHealthPercentage)
    // holds float health at +0xC4 and max health at +0xC8; refill slot 0 whenever it
    // is alive but damaged. Logs each refill (control: shows damage really arrives).
    {
        static int s_god = -1;
        static unsigned s_god_n = 0;
        if (s_god < 0) { const char* g = std::getenv("ROGUESQ_GODMODE"); s_god = (g && *g == '1') ? 1 : 0; }
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (s_god && rd) {
            auto rdf = [&](uint32_t p) { uint32_t u = rs64_rdram_u32(rd, p); float f; memcpy(&f, &u, 4); return f; };
            const uint32_t base = 0x137DB8u;
            const float cur = rdf(base + 0xC4), mx = rdf(base + 0xC8);
            // s5730: death probe + revive arm. [god-dead] logs (uncapped to 60) every time health is <=0 or drops
            // below 1/3 max; ROGUESQ_GODMODE2=1 also refills when cur<=0 (revive) to test whether GAME OVER is health death.
            static int s_god2 = -1; static unsigned s_dead_n = 0; static bool s_was_dead = false;
            if (s_god2 < 0) { const char* g2 = std::getenv("ROGUESQ_GODMODE2"); s_god2 = (g2 && *g2 == '1') ? 1 : 0; }
            const bool dead = (mx > 0.0f && mx < 1.0e6f && cur <= 0.0f && cur > -1.0e6f);
            if (dead != s_was_dead || (mx > 0.0f && cur > 0.0f && cur < mx / 3.0f && s_dead_n < 60)) {
                s_was_dead = dead;
                if (s_dead_n++ < 60) fprintf(stderr, "[god-dead] n=%u dead=%d cur=%.2f max=%.2f origin=0x%06X revive=%d\n", s_dead_n, (int)dead, cur, mx, (unsigned)rs64_vi_committed_origin() & 0xFFFFFFu, s_god2);
            }
            // s5732: ROGUESQ_GODMODE3=1 starts a tight host thread (~20 us poll) that revives cur<=0 before the
            // game's per-frame death check can latch, and (mode 2) only logs the pre-death health trajectory
            // without reviving (control arm: shows damage magnitude, one-hit overkill vs. drain).
            static int s_god3 = -1; static std::atomic<int> s_g3_dead{0}, s_g3_rev{0};
            if (s_god3 < 0) {
                const char* g3 = std::getenv("ROGUESQ_GODMODE3"); s_god3 = (g3 && *g3 == '1') ? 1 : (g3 && *g3 == '2') ? 2 : 0;
                if (s_god3) {
                    const int mode = s_god3; volatile uint8_t* rdp = rd;
                    std::thread([rdp, mode]() {
                        struct Smp { float v; long long us; };
                        Smp ring[64]; unsigned rn = 0; float last = -12345.0f; unsigned dumps = 0;
                        for (;;) {
                            std::this_thread::sleep_for(std::chrono::microseconds(20));
                            uint32_t u = rs64_rdram_u32(rdp, 0x137DB8u + 0xC4); float c; memcpy(&c, &u, 4);
                            uint32_t um = rs64_rdram_u32(rdp, 0x137DB8u + 0xC8); float m; memcpy(&m, &um, 4);
                            // s5734: objective-counter watch (0x138060..0x13808C, 12 words): log every change with health + origin.
                            { static uint32_t oc[12]; static bool ocinit = false; static unsigned ocn = 0;
                              for (int i = 0; i < 12; i++) {
                                  const uint32_t v = rs64_rdram_u32(rdp, 0x138060u + 4u * i);
                                  if (!ocinit || v != oc[i]) {
                                      if (ocinit && ocn++ < 120) fprintf(stderr, "[objc] +0x%02X %08x->%08x hp=%.1f origin=0x%06X t=%lld\n", 0x60 + 4 * i, oc[i], v, c, (unsigned)rs64_vi_committed_origin() & 0xFFFFFFu,
                                          (long long)std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());
                                      oc[i] = v;
                                  }
                              }
                              ocinit = true; }
                            // s5737: phase-machine watch. 0x10CA20 = mission phase (1=death respawn timer, 3=results/game-over,
                            // 4=mode1), 0x130B10 word = lives byte (+0), 0x130B14 word = mode byte B14 (+0), 0x10C9E8 = player index.
                            // Logged with hp so the death path (phase 1, lives--) is separable from the objective path (a0==3/2).
                            { static uint32_t pw[4]; static bool pinit = false; static unsigned pn = 0;
                              static const uint32_t pa[4] = {0x10CA20u, 0x130B10u, 0x130B14u, 0x10C9E8u};
                              for (int i = 0; i < 4; i++) {
                                  const uint32_t v = rs64_rdram_u32(rdp, pa[i]);
                                  if (!pinit || v != pw[i]) {
                                      if (pinit && pn++ < 200) fprintf(stderr, "[phase] @%06X %08x->%08x hp=%.1f origin=0x%06X t=%lld\n", pa[i], pw[i], v, c, (unsigned)rs64_vi_committed_origin() & 0xFFFFFFu,
                                          (long long)std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());
                                      pw[i] = v;
                                  }
                              }
                              pinit = true; }
                            // s5738: player-record snapshot ring (0x2A0 bytes @0x137DB8, one per >=100 ms) dumped at dead#1..3 so the
                            // killing event (position/velocity vs terrain) can be read offline. Words are logged raw (big-endian already swapped by rs64_rdram_u32).
                            { static uint32_t snap[8][0xA8]; static long long snapt[8]; static unsigned sn = 0; static long long lastsnap = 0; static unsigned sdumps = 0;
                              const long long nowus = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();
                              if (m > 0.0f && m < 1.0e6f) {
                                  if (c > 0.0f && nowus - lastsnap >= 100000) { lastsnap = nowus; for (int i = 0; i < 0xA8; i++) snap[sn & 7][i] = rs64_rdram_u32(rdp, 0x137DB8u + 4 * i); snapt[sn & 7] = nowus; sn++; }
                                  else if (c <= 0.0f && c > -1.0e6f && sdumps < 3 && sn > 0) {
                                      sdumps++;
                                      fprintf(stderr, "[snap] death#%u nsnap=%u (oldest first; t=ms before death)\n", sdumps, sn > 8 ? 8u : sn);
                                      for (unsigned k = sn > 8 ? sn - 8 : 0; k < sn; k++) {
                                          fprintf(stderr, "[snap] t=-%lld:", (nowus - snapt[k & 7]) / 1000);
                                          for (int i = 0; i < 0xA8; i++) fprintf(stderr, " %08x", snap[k & 7][i]);
                                          fprintf(stderr, "\n");
                                      }
                                      std::this_thread::sleep_for(std::chrono::milliseconds(30)); // pre-revive: also dump the post-death record
                                      fprintf(stderr, "[snap] post:");
                                      for (int i = 0; i < 0xA8; i++) fprintf(stderr, " %08x", rs64_rdram_u32(rdp, 0x137DB8u + 4 * i));
                                      fprintf(stderr, "\n");
                                  }
                              } }
                            // s5763: ROGUESQ_FORCEKILL_MS=N forces a real death: up to 3 times, once the mission origin has been
                            // committed for N ms (and >=20 s apart), host-writes cur=0.0 so the game's own death path (lives--) runs.
                            { static long long fk_ms = -2, fk_t0 = 0, fk_last = 0; static int fk_n = 0;
                              if (fk_ms == -2) { const char* e = std::getenv("ROGUESQ_FORCEKILL_MS"); fk_ms = e ? atoll(e) : -1; }
                              if (fk_ms >= 0 && fk_n < 3 && ((unsigned)rs64_vi_committed_origin() & 0xFFFFFFu) == 0x62BD00u && m > 0.0f && m < 1.0e6f && c > 0.0f) {
                                  const long long nowms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();
                                  if (fk_t0 == 0) fk_t0 = nowms;
                                  if (nowms - fk_t0 >= fk_ms && nowms - fk_last >= 20000) {
                                      fk_last = nowms; fk_n++;
                                      const uint32_t b0 = (0x137DB8u + 0xC4) & ~3u;
                                      const_cast<uint8_t*>(rdp)[b0] = 0; const_cast<uint8_t*>(rdp)[b0 + 1] = 0; const_cast<uint8_t*>(rdp)[b0 + 2] = 0; const_cast<uint8_t*>(rdp)[b0 + 3] = 0;
                                      fprintf(stderr, "[forcekill] n=%d hp %.1f->0 origin=0x%06X\n", fk_n, c, (unsigned)rs64_vi_committed_origin() & 0xFFFFFFu);
                                  }
                              } }
                            if (!(m > 0.0f && m < 1.0e6f)) continue;
                            if (c != last) { ring[rn++ & 63] = { c, (long long)std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count() }; last = c; }
                            if (c <= 0.0f && c > -1.0e6f) {
                                s_g3_dead++;
                                if (dumps++ < 6) {
                                    fprintf(stderr, "[god3] dead#%d mode=%d cur=%.2f max=%.2f origin=0x%06X history(newest last):", s_g3_dead.load(), mode, c, m, (unsigned)rs64_vi_committed_origin() & 0xFFFFFFu);
                                    unsigned k = rn > 12 ? rn - 12 : 0;
                                    for (; k < rn; ++k) fprintf(stderr, " %.1f@%lld", ring[k & 63].v, ring[k & 63].us - ring[(rn - 1) & 63].us);
                                    fprintf(stderr, "\n");
                                }
                                if (mode == 1) {
                                    const uint32_t b = (0x137DB8u + 0xC4) & ~3u; uint32_t w; memcpy(&w, &m, 4);
                                    const_cast<uint8_t*>(rdp)[b + 3] = w >> 24; const_cast<uint8_t*>(rdp)[b + 2] = w >> 16;
                                    const_cast<uint8_t*>(rdp)[b + 1] = w >> 8;  const_cast<uint8_t*>(rdp)[b] = w;
                                    s_g3_rev++; last = m;
                                } else { std::this_thread::sleep_for(std::chrono::milliseconds(50)); }
                            }
                        }
                    }).detach();
                }
            }
            if (dead && s_god2) {
                const uint32_t p = base + 0xC4, b = p & ~3u; uint32_t u; memcpy(&u, &mx, 4);
                const_cast<uint8_t*>(rd)[b + 3] = u >> 24; const_cast<uint8_t*>(rd)[b + 2] = u >> 16;
                const_cast<uint8_t*>(rd)[b + 1] = u >> 8;  const_cast<uint8_t*>(rd)[b] = u;
            }
            if (mx > 0.0f && mx < 1.0e6f && cur > 0.0f && cur < mx) {
                const uint32_t p = base + 0xC4, b = p & ~3u; uint32_t u; memcpy(&u, &mx, 4);
                const_cast<uint8_t*>(rd)[b + 3] = u >> 24; const_cast<uint8_t*>(rd)[b + 2] = u >> 16;
                const_cast<uint8_t*>(rd)[b + 1] = u >> 8;  const_cast<uint8_t*>(rd)[b] = u;
                if (++s_god_n <= 20 || (s_god_n % 200) == 0)
                    fprintf(stderr, "[godmode] refill #%u cur=%.2f max=%.2f\n", s_god_n, cur, mx);
            }
        }
    }

    // s5773: lives-byte watch outside the godmode block. The death route runs with
    // GODMODE off, so the GODMODE3 [phase] poll never starts. Change lines begin
    // only after a mission origin so boot traffic cannot eat the cap.
    {
        static int s_on = -1;
        if (s_on < 0) {
            const char* e = std::getenv("ROGUESQ_LOG_MTM");
            s_on = (e && e[0] && e[0] != '0') ? 1 : 0;
        }
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (s_on && rd) {
            static uint8_t prev[4];
            static int inited = 0, armed = 0, mission = 0;
            static unsigned nch = 0;
            uint8_t b[4];
            for (int i = 0; i < 4; i++) b[i] = (uint8_t)rs64_rdram_u8(rd, 0x130B10u + (uint32_t)i);
            const unsigned origin = (unsigned)rs64_vi_committed_origin() & 0xFFFFFFu;
            if (!armed) {
                armed = 1;
                std::fprintf(stderr, "[livesctl] armed ord=%lu t=%lld origin=0x%06X b=%u,%u,%u,%u\n",
                    rs64_s5773_ord(), rs64_s5773_ms(), origin, b[0], b[1], b[2], b[3]);
                std::fflush(stderr);
            }
            const int mis = (origin == 0x62BD00u || origin == 0x690400u || origin == 0x620400u);
            if (mis && !mission) {
                mission = 1;
                std::fprintf(stderr, "[livesctl] mission ord=%lu t=%lld origin=0x%06X b=%u,%u,%u,%u\n",
                    rs64_s5773_ord(), rs64_s5773_ms(), origin, b[0], b[1], b[2], b[3]);
                std::fflush(stderr);
            }
            if (inited && mission) {
                for (int i = 0; i < 4; i++) {
                    if (b[i] != prev[i] && nch < 80) {
                        nch++;
                        std::fprintf(stderr, "[livesbyte] ord=%lu t=%lld i=%d %u->%u origin=0x%06X b=%u,%u,%u,%u\n",
                            rs64_s5773_ord(), rs64_s5773_ms(), i, prev[i], b[i], origin, b[0], b[1], b[2], b[3]);
                        std::fflush(stderr);
                    }
                }
            }
            for (int i = 0; i < 4; i++) prev[i] = b[i];
            inited = 1;
        }
    }

    // s6726: ROGUESQ_LIVES_CAP=<n> is a TEST-ONLY harness lever (G1d game-over screen): while the
    // player-0 lives byte 0x80130B10 holds a plausible count above n (2..9), set it to n, so the
    // next life loss reaches the game's own lives==0 GAME OVER path (M6-S5759-DEATH-CHAIN.md).
    // Every change of the byte is logged ([livescap], cap 40) as the positive control.
    {
        static int s_cap = -2;
        if (s_cap == -2) { const char* e = std::getenv("ROGUESQ_LIVES_CAP"); s_cap = (e && *e) ? std::atoi(e) : -1; }
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (s_cap >= 0 && rd) {
            static int s_prev = -1;
            static unsigned s_n = 0;
            const uint8_t v = (uint8_t)rs64_rdram_u8(rd, 0x130B10u);
            uint8_t w = v;
            if (v >= 2 && v <= 9 && v > s_cap) { const_cast<uint8_t*>(rd)[0x130B10u ^ 3u] = (uint8_t)s_cap; w = (uint8_t)s_cap; }
            if ((int)w != s_prev && s_n < 40) {
                s_n++;
                std::fprintf(stderr, "[livescap] t=%lld read=%u now=%u origin=0x%06X\n", rs64_s5773_ms(), v, w,
                    (unsigned)rs64_vi_committed_origin() & 0xFFFFFFu);
                std::fflush(stderr);
            }
            s_prev = w;
        }
    }

    // s5680: ROGUESQ_PLAYER_DUMP=1 logs the whole player record (0x137DB8, 0x2A0 bytes) as hex words
    // at ~1 Hz while the mission origin 0x690400 is up, plus the stick/button state, so field
    // tracking vs stick input can be found offline. Passive, read-only.
    {
        static int s_pd = -1;
        static std::chrono::steady_clock::time_point s_pd_last;
        if (s_pd < 0) { const char* g = std::getenv("ROGUESQ_PLAYER_DUMP"); s_pd = (g && *g == '1') ? 1 : (g && *g == '2') ? 2 : 0; }
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        // s5682: mode 2 = every poll (not 1 Hz), first 400 polls per mission window: ship object (record+0x04)
        // pos vec3 +0x4C/50/54 and record vel +0xD0/D4/D8 as floats, with stick. Pairs pos deltas vs vel offline.
        if (s_pd == 2 && rd && ((uint32_t)rs64_vi_committed_origin() & 0xFFFFFFu) == 0x690400u) {
            static unsigned s_pd2_n = 0;
            static bool s_pd2_armed = false;
            if (!s_pd2_armed && (stick_x != 0 || stick_y != 0)) s_pd2_armed = true;  // s5683: log only once input is live
            if (s_pd2_armed && s_pd2_n < 600) {
                s_pd2_n++;
                auto f = [&](uint32_t a) { uint32_t u = rs64_rdram_u32(rd, a); float v; memcpy(&v, &u, 4); return (double)v; };
                const uint32_t p = rs64_rdram_u32(rd, 0x137DB8u + 4) & 0xFFFFFFu;
                fprintf(stderr, "[pd2] n=%u t=%lld ship=%06x pos=%.4f,%.4f,%.4f vel=%.4f,%.4f,%.4f sx=%.2f sy=%.2f\n", s_pd2_n,
                        (long long)std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count(),
                        (unsigned)p, f(p + 0x4C), f(p + 0x50), f(p + 0x54), f(0x137DB8u + 0xD0), f(0x137DB8u + 0xD4), f(0x137DB8u + 0xD8),
                        (double)stick_x, (double)stick_y);
            }
        }
        if (s_pd && rd && ((uint32_t)rs64_vi_committed_origin() & 0xFFFFFFu) == 0x690400u) {
            const auto now = std::chrono::steady_clock::now();
            if (now - s_pd_last >= std::chrono::seconds(1)) {
                s_pd_last = now;
                fprintf(stderr, "[pdump] sx=%.2f sy=%.2f btn=0x%04X :", (double)stick_x, (double)stick_y, (unsigned)btn);
                for (uint32_t o = 0; o < 0x2A0; o += 4) fprintf(stderr, " %08x", rs64_rdram_u32(rd, 0x137DB8u + o));
                fprintf(stderr, "\n");
                // s5681: follow KSEG0 pointers in the record; dump 0x100 bytes of each distinct target.
                uint32_t seen[32]; unsigned ns = 0;
                for (uint32_t o = 0; o < 0x2A0 && ns < 32; o += 4) {
                    const uint32_t p = rs64_rdram_u32(rd, 0x137DB8u + o);
                    if ((p >> 24) != 0x80u || (p & 0xFFFFFFu) < 0x1000u || (p & 0xFFFFFFu) > 0x7FFF00u || (p & 3)) continue;
                    bool dup = false; for (unsigned i = 0; i < ns; i++) if (seen[i] == p) dup = true;
                    if (dup) continue;
                    seen[ns++] = p;
                    fprintf(stderr, "[pptr] off=%03X tgt=%08x sx=%.2f sy=%.2f :", (unsigned)o, (unsigned)p, (double)stick_x, (double)stick_y);
                    for (uint32_t q = 0; q < 0x100; q += 4) fprintf(stderr, " %08x", rs64_rdram_u32(rd, (p & 0xFFFFFFu) + q));
                    fprintf(stderr, "\n");
                }
            }
        }
    }

    // s5604: ROGUESQ_MISSION_WIN=<n> is a TEST-ONLY lever for the mission-1 -> mission-2
    // route. activateObjectiveCompleteFlag (0x800C76B0) ORs bit (id-1) into the byte at
    // 0x80130B15 for ids 1..8; this sets all eight bits once, after <n> polls with the
    // mask still zero and the mission scanout origin 0x690400 up. One-shot, logged.
    {
        static int s_win = -1;
        static unsigned s_win_polls = 0;
        static bool s_win_done = false;
        if (s_win < 0) { const char* w = std::getenv("ROGUESQ_MISSION_WIN"); s_win = (w && *w) ? std::atoi(w) : 0; }
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        if (s_win > 0 && rd && !s_win_done) {
            const uint32_t org = (uint32_t)rs64_vi_committed_origin();
            if ((org & 0xFFFFFFu) == 0x690400u && ++s_win_polls >= (unsigned)s_win) {
                const uint32_t a = 0x130B15u ^ 3u;  // byte address inside big-endian word storage
                const uint8_t before = rd[a];
                static const bool s_nopoke = std::getenv("ROGUESQ_MISSION_WIN_NOPOKE") != nullptr;  // s5615 negative control: log only, no writes
                if (!s_nopoke) const_cast<uint8_t*>(rd)[a] = 0xFF;
                // s5605: the mask byte is HUD-only; lv0_checkComplexObjectives ends the mission on
                // get(3)>=9 (word 0x80138068) or get(2)>=3 (0x80138064, the loss counter - not poked).
                // s5612: ROGUESQ_MISSION_WIN_REAL=1 pokes get(10) (0x80138084) = 6 instead: lv0's get(3)>=9 and get(2)>=3
                // gates both call 800C7738 (event 2 -> gate 4 -> requestSpeechResponseMode2 -> B14=2, the LOSE arm); only
                // get(10)>=6 (0x80101224) runs objectives 3,4 + 800C776C (event 3 -> gate 3 -> Mode1 -> B14=1, the WIN arm).
                static const bool s_real = std::getenv("ROGUESQ_MISSION_WIN_REAL") != nullptr;
                const uint32_t c = s_real ? 0x138084u : 0x138068u;
                // rdram words are host-native little-endian (same layout as the godmode float poke above)
                const uint32_t cb = rd[c] | (rd[c + 1] << 8) | (rd[c + 2] << 16) | ((uint32_t)rd[c + 3] << 24);
                if (!s_nopoke) {
                    const_cast<uint8_t*>(rd)[c + 3] = 0; const_cast<uint8_t*>(rd)[c + 2] = 0;
                    const_cast<uint8_t*>(rd)[c + 1] = 0; const_cast<uint8_t*>(rd)[c] = s_real ? 6 : 9;
                }
                s_win_done = true;
                fprintf(stderr, "[mission-win] polls=%u mask 0x%02X -> 0xFF counter(0x%06X) %u -> %u origin=0x%08X\n", s_win_polls, before, c, cb, s_real ? 6u : 9u, org);
            }
        }
        // s5606: after the poke, log every change of the mission-state flag word 0x8010C9E0
        // (800C7738 ORs bit 0x4 into it unless 0x8010CA20 != 0; 800C776C ORs 0x8) plus the VI
        // origin, so the soak shows whether the end gate fired and what the game did next.
        if (s_win > 0 && rd && s_win_done) {
            // s5614: dump get(1..10) (words 0x80138060+4*(n-1)) every 30 polls, and on any change
            // of get(2)/get(3)/get(10), to see which lv0 threshold counter crosses first.
            {
                static unsigned s_dp = 0, s_dn = 0;
                static uint32_t s_pv[10] = {};
                uint32_t v[10]; bool chg = false;
                for (int i = 0; i < 10; ++i) {
                    const uint32_t o = 0x138060u + 4u * i;
                    v[i] = rd[o] | (rd[o + 1] << 8) | (rd[o + 2] << 16) | ((uint32_t)rd[o + 3] << 24);
                    if (v[i] != s_pv[i]) chg = true;
                }
                if ((chg || (++s_dp % 120) == 0) && s_dn < 2000) {
                    fprintf(stderr, "[mission-win] get %u %u %u %u %u %u %u %u %u %u origin=0x%08X\n", v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], (unsigned)rs64_vi_committed_origin());
                    memcpy(s_pv, v, sizeof v); ++s_dn;
                }
            }
            static uint32_t s_prev_fl = 0xFFFFFFFFu;
            static unsigned s_fl_n = 0;
            const uint32_t f = 0x10C9E0u;
            const uint32_t fl = rd[f] | (rd[f + 1] << 8) | (rd[f + 2] << 16) | ((uint32_t)rd[f + 3] << 24);
            // s5608: gate (0x8010CA20), sub-phase byte (0x8010C9F0) and phase timer float (0x8010C9EC)
            // drive the 800FA858 end-sequence switch; log gate/subphase changes plus a heartbeat.
            {
                auto w32 = [&](uint32_t o) { return (uint32_t)(rd[o] | (rd[o + 1] << 8) | (rd[o + 2] << 16) | ((uint32_t)rd[o + 3] << 24)); };
                static uint32_t s_pg = 0xFFFFFFFFu, s_ps = 0xFFFFFFFFu;
                static unsigned s_hb = 0, s_gn = 0;
                const uint32_t g2 = w32(0x10CA20u), sp = rd[0x10C9F0u ^ 3u], tm = w32(0x10C9ECu), f2 = w32(0x10CA1Cu);
                float tf; memcpy(&tf, &tm, 4);
                // s5610: mainGameLoop (0x8003E3C4) switches on byte 0x80130B14 (1 = level-complete arm,
                // 2 = lose-a-life arm) once bit 0x100 of word 0x80130B50 exits its mission loop
                // (0x8003E304); log both so the soak shows which half of that handshake is missing.
                const uint32_t b14 = rd[0x130B14u ^ 3u], b50 = w32(0x130B50u);
                static uint32_t s_pb14 = 0xFFFFFFFFu, s_pb50 = 0xFFFFFFFFu;
                if ((g2 != s_pg || sp != s_ps || b14 != s_pb14 || b50 != s_pb50 || (++s_hb % 120) == 0) && s_gn < 200) {
                    fprintf(stderr, "[mission-win] seq gate=%u subphase=%u timer=%.3f vflags(0x8010CA1C)=%08X flag=%08X b14=%u b50=%08X origin=0x%08X\n",
                            g2, sp, tf, f2, fl, b14, b50, (unsigned)rs64_vi_committed_origin());
                    s_pg = g2; s_ps = sp; s_pb14 = b14; s_pb50 = b50; ++s_gn;
                }
            }
            if (fl != s_prev_fl && s_fl_n < 64) {
                const uint32_t g = 0x10CA20u;
                const uint32_t gate = rd[g] | (rd[g + 1] << 8) | (rd[g + 2] << 16) | ((uint32_t)rd[g + 3] << 24);
                fprintf(stderr, "[mission-win] flagword 0x8010C9E0 %08X -> %08X gate(0x8010CA20)=%u origin=0x%08X\n",
                        s_prev_fl, fl, gate, (unsigned)rs64_vi_committed_origin());
                s_prev_fl = fl;
                ++s_fl_n;
            }
        }
    }

    // s6399: ROGUESQ_POSE_LOCK=1 is a TEST-ONLY no-input hover arm for G3c edge comparison. Once the mission
    // origin is live, all stick/button input is zeroed so every arm flies the same straight line from spawn
    // (autopilot attitude diverged per arm, s6397/s6398). Logs pos every 30 polls to pair frames offline.
    {
        static int s_pl = -1;
        static unsigned s_pln = 0;
        if (s_pl < 0) { const char* g = std::getenv("ROGUESQ_POSE_LOCK"); s_pl = (g && *g && *g != '0') ? 1 : 0; }
        volatile uint8_t* rd = g_recomp_rdram_for_wp_raw;
        static bool s_pl_live = false;  // wide (ASPECT) flight uses a different VI origin than 0x690400, so latch on a live ship pos instead
        if (s_pl && rd) {
            const uint32_t p = rs64_rdram_u32(rd, 0x137DB8u + 4) & 0x1FFFFFFFu;
            float v[3] = {0, 0, 0};
            const bool pv = p >= 0x1000u && p < rs64_ram_top - 0x80000100u; // s6881: spill puts the player above 8 MB in wide + dd, which left the lock off
            if (pv) for (int i = 0; i < 3; i++) { uint32_t u = rs64_rdram_u32(rd, p + 0x4C + 4 * i); memcpy(&v[i], &u, 4); }
            if (pv && (v[0] != 0.0f || v[1] != 0.0f || v[2] != 0.0f)) s_pl_live = true;
            // s6879: no origin gate. 16:9 flight swaps 0x58B038 / 0x6xxxxx, so a >= 0x600000 test let harness keys through on every other frame.
            // s6934: not while the game's pause menu is live. The route's Start can land in flight, and with the pad zeroed nothing could close the menu (s6933 arms, caps=0).
            if (s_pl_live && !rs64_g1d_pause_live()) { stick_x = 0.0f; stick_y = 0.0f; btn = 0; }
            // s6412: ROGUESQ_POSE_REF=<file> pins attitude across arms. First arm to lock writes the player object's
            // 0x100 bytes there; later arms overwrite every unit-range float word (attitude/matrix candidates, |f| in
            // [1e-6,1.0001]; pos 0x4C..0x57 excluded) of their object with the reference each poll.
            if (s_pl_live && pv) {
                static int s_ref_state = 0;  // 0 untried, 1 wrote file, 2 applying
                static uint32_t s_ref[64];
                static const char* s_ref_path = std::getenv("ROGUESQ_POSE_REF");
                if (s_ref_path && *s_ref_path && s_ref_state == 0) {
                    FILE* fr = fopen(s_ref_path, "rb");
                    if (fr && fread(s_ref, 4, 64, fr) == 64) { s_ref_state = 2; fprintf(stderr, "[poselock] ref loaded from %s\n", s_ref_path); }
                    else {
                        if (fr) fclose(fr);
                        fr = fopen(s_ref_path, "wb");
                        for (int i = 0; i < 64; i++) s_ref[i] = rs64_rdram_u32(rd, p + 4 * i);
                        if (fr) { fwrite(s_ref, 4, 64, fr); fprintf(stderr, "[poselock] ref written to %s\n", s_ref_path); }
                        s_ref_state = 1;
                    }
                    if (fr) fclose(fr);
                }
                if (s_ref_state == 2) {
                    static bool s_ref_logged = false;
                    for (int i = 0; i < 64; i++) {
                        static int s_pin_position = -1;
                        if (s_pin_position < 0) { const char* g = std::getenv("ROGUESQ_POSE_PIN_POSITION"); s_pin_position = (g && *g && *g != '0') ? 1 : 0; }
                        if (!s_pin_position && i >= 0x4C / 4 && i < 0x58 / 4) continue;
                        float f; memcpy(&f, &s_ref[i], 4);
                        const float a = f < 0 ? -f : f;
                        if (!(a >= 1e-6f && a <= 1.0001f)) continue;
                        *(volatile uint32_t*)(rd + ((p + 4 * i) & ~3u)) = s_ref[i];
                        if (!s_ref_logged) fprintf(stderr, "[poselock] pin off=0x%02X val=%.5f\n", 4 * i, (double)f);
                    }
                    s_ref_logged = true;
                }
            }
            if (s_pl_live && (s_pln++ % 30) == 0) {
                fprintf(stderr, "[poselock] n=%u pos=%.2f,%.2f,%.2f\n", s_pln - 1, (double)v[0], (double)v[1], (double)v[2]);
            }
        }
    }

    // s7513 class FJ: host stick -> OEM N64 gate (85 cardinal / 70,70 diagonal), see rs64_stick_gate.h. ROGUESQ_STICK_GATE=0 = old 127.
    {
        static const rs64_stick_gate_cfg s_gate = [] {
            const rs64_stick_gate_cfg g = rs64_stick_gate_parse(std::getenv("ROGUESQ_STICK_GATE"));
            fprintf(stderr, "[stick-gate] on=%d card=%.0f diag=%.0f\n", (int)g.on, (double)g.card, (double)g.diag);
            return g;
        }();
        // s7764: ROGUESQ_LOG_STICK_GATE=1 prints host -> guest stick counts (in, out) once per wall second while the stick is
        // deflected, so STICK_GATE on vs =0 can be told apart in flight (on: |out| <= 85 counts, =0: 127 * in).
        static const bool s_glog = [] { const char* e = std::getenv("ROGUESQ_LOG_STICK_GATE"); return e && *e && *e != '0'; }();
        const float in_x = stick_x, in_y = stick_y;
        rs64_stick_gate_apply(s_gate, &stick_x, &stick_y);
        if (s_glog && (in_x != 0.0f || in_y != 0.0f)) {
            static long long s_gl_last = 0; static unsigned s_gl_n = 0;
            const long long ms = rs64_s5773_ms();
            if (ms - s_gl_last >= 1000 && s_gl_n < 600) {
                s_gl_last = ms; s_gl_n++;
                fprintf(stderr, "[stick-gate] sample on=%d in=%.3f,%.3f out_counts=%d,%d\n", (int)s_gate.on, (double)in_x, (double)in_y,
                        (int)(127.0f * stick_x), (int)(127.0f * stick_y));
            }
        }
    }
    *x = stick_x;
    *y = stick_y;
    *buttons = btn;
    {   // s7766 input latency: ROGUESQ_S7766_INLAT=1 -> one [inlat] row per guest pad read (osContGetReadData) with the
        // mach_absolute_time clock of [g3c] m= and the present ring, and the exact value the guest gets. Offline:
        // tools/s7766_inlat.py joins a stick step's first poll to the first [g3c] VI whose camera responds and to the present.
        static const bool on = [] { const char* e = std::getenv("ROGUESQ_S7766_INLAT"); return e && *e == '1'; }();
        if (on) fprintf(stderr, "[inlat] m=%llu btn=%04x sx=%d sy=%d\n", (unsigned long long)mach_absolute_time(), (unsigned)btn,
                        (int)(127.0f * stick_x), (int)(127.0f * stick_y));
    }
    if (rs64_pad_test_s() > 0) {  // s7201 [pad-hp] word: what the guest gets, once per wall second
        static long long s_last = 0;
        const long long ms = rs64_s5773_ms();
        if (ms - s_last >= 1000) {
            s_last = ms;
            fprintf(stderr, "[pad-hp] word ms=%lld btn=0x%04X x=%.2f y=%.2f pad=%s\n", ms, (unsigned)btn, stick_x, stick_y,
                    controller && SDL_GameControllerName(controller) ? SDL_GameControllerName(controller) : "none");
        }
    }

    // s1944: host Start/A rising edges on the outgoing pad word (always-on).
    // Discriminates late winctl/focus drops vs title 1024 ignoring a live pad.
    {
        static uint16_t s_prev_pad = 0;
        static int s_pad_host_n = 0;
        const uint16_t rise = (uint16_t)(btn & ~s_prev_pad);
        s_prev_pad = btn;
        if (rise & (N64_START_BUTTON | N64_A_BUTTON)) {
            ++s_pad_host_n;
            if (s_pad_host_n <= 16 || (s_pad_host_n % 32) == 0) {
                fprintf(stderr,
                    "[pad-host] n=%d start=%d a=%d btn=0x%04X vi_width=%u origin=0x%08X\n",
                    s_pad_host_n,
                    (rise & N64_START_BUTTON) ? 1 : 0,
                    (rise & N64_A_BUTTON) ? 1 : 0,
                    (unsigned)btn,
                    (unsigned)rs64_vi_committed_width(),
                    (unsigned)rs64_vi_committed_origin());
                fflush(stderr);
            }
        }
    }

    // s577 item -7: host START edge probe (always-on). Discriminates H-edge1
    // (host never sees 2nd RETURN) vs H-edge2 (host sees it but guest new=0).
    {
        static int s_prev_start = 0;
        static long s_host_start_n = 0;
        const int start_now = (btn & N64_START_BUTTON) ? 1 : 0;
        if (start_now != s_prev_start) {
            fprintf(stderr, "[host-start] n=%ld edge %d->%d btn=0x%04X\n",
                    s_host_start_n, s_prev_start, start_now, (unsigned)btn);
            fflush(stderr);
            s_prev_start = start_now;
        } else if (s_host_start_n < 5 || (s_host_start_n % 2000) == 0) {
            fprintf(stderr, "[host-start] n=%ld held=%d btn=0x%04X\n",
                    s_host_start_n, start_now, (unsigned)btn);
            fflush(stderr);
        }
        s_host_start_n++;
    }
    return true;
}


static ultramodern::input::connected_device_info_t get_connected_device_info(int controller_num) {
    if (controller_num == 0) {
        // s7516 class FM positive control: ROGUESQ_PAK_SHAPE_CTL=1 reports a Rumble Pak on port 0 (set_rumble stays a no-op),
        // so the game's present-gated osMotorStart/Stop paths run and the [s7516-pak] log must show them. Since G6a the pak is reported by default (ROGUESQ_RUMBLE=0 = no pak).
        static const int pak_ctl = [] { const char* e = getenv("ROGUESQ_PAK_SHAPE_CTL"); return (e && *e && *e != '0') ? 1 : 0; }();
        // G6a (s7617): a Rumble Pak by default so the game sends motor pulses; ROGUESQ_RUMBLE=0 = old no-pak shape.
        if (pak_ctl || rs64_rumble_on()) return { ultramodern::input::Device::Controller, ultramodern::input::Pak::RumblePak };
        return { ultramodern::input::Device::Controller, ultramodern::input::Pak::None };
    }
    return { ultramodern::input::Device::None, ultramodern::input::Pak::None };
}

// ---------------------------------------------------------------------------
// Graphics (SDL2 window creation — rt64 takes over from here)
// ---------------------------------------------------------------------------
// G1f (s6688): window size follows the game aspect, fullscreen toggle, ROGUESQ_FULLSCREEN=1.
// rs64_g1f_* are filled by rs64_g1d_apply_aspect_policy() before the window exists.
static SDL_Window* g_rs64_window = nullptr;
static std::atomic<bool> g_rs64_fs_toggle{false};
static int rs64_g1f_win_w = 640, rs64_g1f_win_h = 480;
static bool rs64_g1f_fullscreen = false;
// s7767: ROGUESQ_FULLSCREEN=2 opens in SDL exclusive fullscreen (SDL_WINDOW_FULLSCREEN: no macOS Space, window above the
// shield) instead of desktop/borderless (=1), to test whether the compositor leg of present->photon latency drops.
static bool rs64_g1f_fs_exclusive = false;
#ifdef __APPLE__
extern "C" double rs64_display_top_inset_frac(void);
extern "C" double rs64_display_top_inset_frac_at(int x, int w, int h);
#endif
// s7226 G1f: the display the game targets at boot (auto aspect, notch band, window fit, window placement).
// ROGUESQ_WIN_DISPLAY=<n> (SDL display index, listed in the [g1f] display rows) or =mouse (the display under the
// cursor at launch). Else, if ROGUESQ_WINDOW_POS=x,y is set, the display containing that point (ROGUESQ_G1F_POSDISP=0 = old).
// Else display 0 (the macOS main display), as before. Needs SDL video initialised.
static int rs64_g1f_target_display() {
    static int td = -1;
    if (td >= 0) return td;
    td = 0;
    const int nd = SDL_GetNumVideoDisplays();
    for (int i = 0; i < nd; i++) {
        SDL_Rect b{}; SDL_GetDisplayBounds(i, &b);
        const char* nm = SDL_GetDisplayName(i);
        std::fprintf(stderr, "[g1f] display %d: \"%s\" %dx%d at %d,%d\n", i, nm ? nm : "?", b.w, b.h, b.x, b.y);
    }
    auto at_point = [nd](int x, int y) {
        for (int i = 0; i < nd; i++) {
            SDL_Rect b{};
            if (SDL_GetDisplayBounds(i, &b) == 0 && x >= b.x && x < b.x + b.w && y >= b.y && y < b.y + b.h) return i;
        }
        return -1;
    };
    const char* how = "default";
    if (const char* e = std::getenv("ROGUESQ_WIN_DISPLAY"); e && *e) {
        if (!std::strcmp(e, "mouse")) {
            int mx = 0, my = 0; SDL_GetGlobalMouseState(&mx, &my);
            const int i = at_point(mx, my);
            if (i >= 0) td = i;
            how = "mouse";
        } else {
            const int i = std::atoi(e);
            if (i >= 0 && i < nd) td = i; else std::fprintf(stderr, "[g1f] ROGUESQ_WIN_DISPLAY=%s out of range (0..%d), using 0\n", e, nd - 1);
            how = "ROGUESQ_WIN_DISPLAY";
        }
    } else if (const char* wp = std::getenv("ROGUESQ_WINDOW_POS")) {
        const char* pd = std::getenv("ROGUESQ_G1F_POSDISP");
        int x, y;
        if (!(pd && *pd == '0') && sscanf(wp, "%d,%d", &x, &y) == 2) {
            const int i = at_point(x, y);
            if (i >= 0) td = i;
            how = "ROGUESQ_WINDOW_POS";
        }
    }
    std::fprintf(stderr, "[g1f] target display %d (%s)\n", td, how);
    return td;
}
static bool rs64_g1f_optin = false;  // ASPECT or FULLSCREEN set: high-DPI drawable; unset = retail window
// s7202 display hot-plug: the event watch records display add/remove/move; update_gfx (main thread) logs where the
// window went and, if a display was removed while fullscreen, leaves and re-enters desktop fullscreen so macOS builds
// the fullscreen Space on a display that still exists. ROGUESQ_DISPLAY_HOTPLUG=0 = old (witness only).
static std::atomic<int> g_rs64_disp_ev{0};
static std::atomic<int> g_rs64_disp_removed{0};
static void* g_rs64_nswin = nullptr;
static void* g_rs64_layer = nullptr;
#ifdef __APPLE__
extern "C" void rs64_window_state_log(void* nswindow, void* metal_layer, const char* tag);
#endif
static void rs64_display_hotplug_tick() {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_DISPLAY_HOTPLUG"); return !(e && *e == '0'); }();
    static double t_ev = -1.0, t_rm = -1.0; static int logs = 0, step = 0;
    if (!g_rs64_window) return;
    const double now = (double)SDL_GetPerformanceCounter() / SDL_GetPerformanceFrequency();
    if (g_rs64_disp_ev.exchange(0)) { t_ev = now; logs = 0; }
    // s7222: remember the bounds of the display the fullscreen window sits on; a removal of ANOTHER display (window's
    // display still present at the same bounds) must not cycle fullscreen (it cost a resize + ~3 s at ~18/s).
    // ROGUESQ_HOTPLUG_ANY=1 = old behaviour (cycle on any removal while fullscreen).
    static const bool any = [] { const char* e = std::getenv("ROGUESQ_HOTPLUG_ANY"); return e && *e == '1'; }();
    static SDL_Rect fsb{0, 0, 0, 0};
    const bool pend = g_rs64_disp_removed.exchange(0) != 0;
    if (!pend && t_rm < 0.0 && (SDL_GetWindowFlags(g_rs64_window) & SDL_WINDOW_FULLSCREEN)) {
        const int di = SDL_GetWindowDisplayIndex(g_rs64_window);
        SDL_Rect b; if (di >= 0 && SDL_GetDisplayBounds(di, &b) == 0) fsb = b;
    }
    if (pend) {
        const bool fs = (SDL_GetWindowFlags(g_rs64_window) & SDL_WINDOW_FULLSCREEN) != 0;
        bool still = false;
        const int nd = SDL_GetNumVideoDisplays();
        for (int i = 0; i < nd && fsb.w > 0; i++) {
            SDL_Rect b; if (SDL_GetDisplayBounds(i, &b) == 0 && b.x == fsb.x && b.y == fsb.y && b.w == fsb.w && b.h == fsb.h) still = true;
        }
        fprintf(stderr, "[g1f] display removed fullscreen=%d hotplug=%d own_display=%d,%d,%dx%d still_present=%d any=%d\n", (int)fs, (int)on,
                fsb.x, fsb.y, fsb.w, fsb.h, (int)still, (int)any);
        if (on && fs && (any || !still)) { t_rm = now; step = 0; }
        else if (on && fs) fprintf(stderr, "[g1f] hotplug: window's display still present, no fullscreen cycle\n");
    }
#ifdef __APPLE__
    static const double at[] = {0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0};
    if (t_ev >= 0.0 && logs < 7 && now - t_ev >= at[logs]) {
        char tag[32]; std::snprintf(tag, sizeof(tag), "+%.1fs", at[logs]);
        rs64_window_state_log(g_rs64_nswin, g_rs64_layer, tag);
        logs++;
    }
#endif
    if (t_rm >= 0.0) {
        if (step == 0 && now - t_rm >= 0.3) {
            SDL_SetWindowFullscreen(g_rs64_window, 0);
            fprintf(stderr, "[g1f] hotplug: leave fullscreen\n"); step = 1;
        } else if (step == 1 && now - t_rm >= 1.5) {
            SDL_SetWindowFullscreen(g_rs64_window, SDL_WINDOW_FULLSCREEN_DESKTOP);
            SDL_RaiseWindow(g_rs64_window);
            int ww = 0, wh = 0; SDL_GetWindowSize(g_rs64_window, &ww, &wh);
            fprintf(stderr, "[g1f] hotplug: re-enter fullscreen on display %d window %dx%d\n", SDL_GetWindowDisplayIndex(g_rs64_window), ww, wh);
            t_rm = -1.0; t_ev = now; logs = 0;
        }
    }
}

// Size a window of aspect r to ~90% of the usable desktop of display 0.
static void rs64_g1f_fit_window(double r) {
    SDL_Rect ub{0, 0, 1280, 800};
    if (SDL_WasInit(SDL_INIT_VIDEO) && SDL_GetDisplayUsableBounds(rs64_g1f_target_display(), &ub) != 0) ub = {0, 0, 1280, 800};
    double h = ub.h * 0.9, w = h * r;
    if (w > ub.w * 0.9) { w = ub.w * 0.9; h = w / r; }
    rs64_g1f_win_w = ((int)w) & ~1;
    rs64_g1f_win_h = ((int)h) & ~1;
}

// Test lever: ROGUESQ_FS_TEST_TOGGLE_S="a[,b]" pushes a synthetic F11 keydown a (and b) seconds
// after the window opens, through the same event watch as a real key. Harness keys never reach
// SDL on macOS (s5416), so this is the only way to drive the toggle path unattended.
static void rs64_g1f_test_toggle_tick() {
    static const char* e = std::getenv("ROGUESQ_FS_TEST_TOGGLE_S");
    static double at[2] = {-1.0, -1.0};
    static int next = 0;
    static Uint64 t0 = 0;
    if (!e || !g_rs64_window || next >= 2) return;
    if (!t0) {
        t0 = SDL_GetPerformanceCounter();
        at[0] = std::atof(e);
        const char* c = std::strchr(e, ',');
        at[1] = c ? std::atof(c + 1) : -1.0;
    }
    const double t = (double)(SDL_GetPerformanceCounter() - t0) / SDL_GetPerformanceFrequency();
    if (at[next] < 0.0) { next = 2; return; }
    if (t < at[next]) return;
    SDL_Event ev{};
    ev.type = SDL_KEYDOWN;
    ev.key.windowID = SDL_GetWindowID(g_rs64_window);
    ev.key.state = SDL_PRESSED;
    ev.key.keysym.sym = SDLK_F11;
    ev.key.keysym.scancode = SDL_SCANCODE_F11;
    SDL_PushEvent(&ev);
    fprintf(stderr, "[g1f] test F11 pushed t=%.1f\n", t);
    next++;
}

// s7592 class TH runtime witness plant: ROGUESQ_S7592_PLANT_FROM=<k> starts one parked (never-ending) detached thread for every
// test resize / test F11 event from the k-th on (0-based, counted across both lists), so an outside thread sampler sees +1 per
// planted event while the earlier events in the same run stay unplanted (same-run positive control). Unset = off.
static void rs64_s7592_plant_event(const char* what) {
    static const int from = [] { const char* e = std::getenv("ROGUESQ_S7592_PLANT_FROM"); return (e && *e) ? std::atoi(e) : -1; }();
    static int n = 0;
    const int k = n++;
    if (from < 0) return;
    const bool pl = k >= from;
    if (pl) std::thread([] { pthread_setname_np("s7592-plant"); for (;;) std::this_thread::sleep_for(std::chrono::hours(1)); }).detach();
    fprintf(stderr, "[s7592] event k=%d %s planted=%d\n", k, what, (int)pl);
}

// s6888 test levers, same reason as above: ROGUESQ_WIN_TEST_RESIZE_S="t:w:h,.." calls SDL_SetWindowSize t seconds after the window opens (AX set size in s6887 never reached the
// drawable); ROGUESQ_FS_TEST_TOGGLE_LIST_S="t,t,.." pushes F11 at each t, for more than the two toggles above.
static void rs64_g1f_test_list_tick() {
    static const char* er = std::getenv("ROGUESQ_WIN_TEST_RESIZE_S");
    static const char* ef = std::getenv("ROGUESQ_FS_TEST_TOGGLE_LIST_S");
    if ((!er && !ef) || !g_rs64_window) return;
    static Uint64 t0 = 0;
    if (!t0) t0 = SDL_GetPerformanceCounter();
    const double t = (double)(SDL_GetPerformanceCounter() - t0) / SDL_GetPerformanceFrequency();
    while (er && *er && t >= std::atof(er)) {
        int w = 0, h = 0;
        if (std::sscanf(er, "%*f:%d:%d", &w, &h) == 2 && w > 0 && h > 0) {
            SDL_SetWindowSize(g_rs64_window, w, h);
            int dw = 0, dh = 0;
#if defined(__APPLE__)
            SDL_Metal_GetDrawableSize(g_rs64_window, &dw, &dh);
#endif
            fprintf(stderr, "[g1f] test resize t=%.1f %dx%d drawable %dx%d\n", t, w, h, dw, dh);
            rs64_s7592_plant_event("resize");
        }
        const char* c = std::strchr(er, ',');
        er = c ? c + 1 : nullptr;
    }
    while (ef && *ef && t >= std::atof(ef)) {
        SDL_Event ev{};
        ev.type = SDL_KEYDOWN;
        ev.key.windowID = SDL_GetWindowID(g_rs64_window);
        ev.key.state = SDL_PRESSED;
        ev.key.keysym.sym = SDLK_F11;
        ev.key.keysym.scancode = SDL_SCANCODE_F11;
        SDL_PushEvent(&ev);
        fprintf(stderr, "[g1f] test F11 list t=%.1f\n", t);
        rs64_s7592_plant_event("f11");
        const char* c = std::strchr(ef, ',');
        ef = c ? c + 1 : nullptr;
    }
}

// s7668: ROGUESQ_PANEL_TEST_WINDOW="open_s,close_s[,open_s,close_s..]" opens/closes the F6 panel at those seconds after the
// window opens (main thread, the same rs64_panel_set_open F6 calls), so a test can hold the panel open across a level-select ->
// mission load and a fullscreen toggle. Default unset = no effect.
static void rs64_s7668_panel_window_tick() {
    static const char* e = std::getenv("ROGUESQ_PANEL_TEST_WINDOW");
    if (!e || !*e || !g_rs64_window) return;
    static Uint64 t0 = 0; static bool next_open = true;
    if (!t0) t0 = SDL_GetPerformanceCounter();
    const double t = (double)(SDL_GetPerformanceCounter() - t0) / SDL_GetPerformanceFrequency();
    while (e && *e && t >= std::atof(e)) {
        fprintf(stderr, "[s7668] panel test t=%.1f set_open=%d\n", t, next_open ? 1 : 0);
        rs64_panel_set_open(next_open); next_open = !next_open;
        const char* c = std::strchr(e, ',');
        e = c ? c + 1 : nullptr;
    }
}

static void rs64_g1f_apply_fs_toggle() {
    rs64_g1f_test_toggle_tick();
    rs64_g1f_test_list_tick();
    if (!g_rs64_window || !g_rs64_fs_toggle.exchange(false)) return;
    const bool fs = (SDL_GetWindowFlags(g_rs64_window) & SDL_WINDOW_FULLSCREEN) != 0;
    SDL_SetWindowFullscreen(g_rs64_window, fs ? 0 : SDL_WINDOW_FULLSCREEN_DESKTOP);
    int ww = 0, wh = 0, dw = 0, dh = 0;
    SDL_GetWindowSize(g_rs64_window, &ww, &wh);
#if defined(__APPLE__)
    SDL_Metal_GetDrawableSize(g_rs64_window, &dw, &dh);
#endif
    fprintf(stderr, "[g1f] fullscreen %s window %dx%d drawable %dx%d\n", fs ? "off" : "on", ww, wh, dw, dh);
}

ultramodern::gfx_callbacks_t::gfx_data_t create_gfx() {
    SDL_SetHint(SDL_HINT_WINDOWS_DPI_AWARENESS, "permonitorv2");
    SDL_SetHint(SDL_HINT_GAMECONTROLLER_USE_BUTTON_LABELS, "0");
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER | SDL_INIT_AUDIO) != 0) {
        fprintf(stderr, "SDL_Init failed: %s\n", SDL_GetError());
        exit(EXIT_FAILURE);
    }
    // s5416 key-delivery witness: SDL_AddEventWatch fires at event push time,
    // before RT64's filter or any PollEvent consumer, so it sees every key
    // and focus event SDL receives from Cocoa.
    SDL_AddEventWatch([](void*, SDL_Event* ev) -> int {
        static std::atomic<int> n{0};
        const bool key = ev->type == SDL_KEYDOWN || ev->type == SDL_KEYUP;
        const bool win = ev->type == SDL_WINDOWEVENT &&
            (ev->window.event == SDL_WINDOWEVENT_FOCUS_GAINED ||
             ev->window.event == SDL_WINDOWEVENT_FOCUS_LOST);
        // G1f: F11, Alt+Enter, Cmd+Ctrl+F toggle fullscreen; applied by update_gfx on the main thread.
        if (ev->type == SDL_KEYDOWN && !ev->key.repeat) {
            const SDL_Keycode k = ev->key.keysym.sym;
            const Uint16 m = ev->key.keysym.mod;
            if (k == SDLK_F11 || (k == SDLK_RETURN && (m & KMOD_ALT)) ||
                (k == SDLK_f && (m & KMOD_GUI) && (m & KMOD_CTRL)))
                g_rs64_fs_toggle.store(true);
        }
        if (ev->type == SDL_WINDOWEVENT && ev->window.event == SDL_WINDOWEVENT_SIZE_CHANGED)
            fprintf(stderr, "[g1f] resized %dx%d\n", ev->window.data1, ev->window.data2);
        if (ev->type == SDL_WINDOWEVENT && ev->window.event == SDL_WINDOWEVENT_DISPLAY_CHANGED)
            fprintf(stderr, "[g1f] display changed -> %d\n", ev->window.data1);  // s7201 witness for the display hot-plug unit
        if (ev->type == SDL_DISPLAYEVENT)
        {
            fprintf(stderr, "[g1f] display event %d display=%u\n", (int)ev->display.event, (unsigned)ev->display.display);
            g_rs64_disp_ev.store(1);
            if (ev->display.event == SDL_DISPLAYEVENT_DISCONNECTED) g_rs64_disp_removed.store(1);
        }
        if (ev->type == SDL_WINDOWEVENT && ev->window.event == SDL_WINDOWEVENT_DISPLAY_CHANGED) g_rs64_disp_ev.store(1);
        static std::atomic<int> any{0};
        const bool first = any.fetch_add(1) < 40;
        if (first) { fprintf(stderr, "[keywitness] anyevent type=0x%X\n", (unsigned)ev->type); fflush(stderr); }
        if ((key || win) && n.fetch_add(1) < 400) {
            fprintf(stderr, "[keywitness] type=0x%X %s=%d scancode=%d\n", (unsigned)ev->type,
                    key ? "sym" : "winev", key ? (int)ev->key.keysym.sym : (int)ev->window.event,
                    key ? (int)ev->key.keysym.scancode : 0);
            fflush(stderr);
        }
        return 1;
    }, nullptr);
    return nullptr;
}

// Defined in rt64_render_context.cpp
namespace recomp {
    std::unique_ptr<ultramodern::renderer::RendererContext>
    create_render_context(uint8_t* rdram, ultramodern::renderer::WindowHandle window_handle, bool developer_mode);
}

ultramodern::renderer::WindowHandle create_window(ultramodern::gfx_callbacks_t::gfx_data_t) {
    // s6891 test lever: ROGUESQ_WINDOW_POS=x,y opens the window at global top-left coords (negative allowed), so a measurement can sit on a display nothing covers:
    // CoreAnimation gives no presentedTime for a fully covered window (s6890). Unset = centered, as before.
    int rs64_win_x = SDL_WINDOWPOS_CENTERED, rs64_win_y = SDL_WINDOWPOS_CENTERED;
    if (const char* wp = std::getenv("ROGUESQ_WINDOW_POS")) {
        int x, y;
        if (sscanf(wp, "%d,%d", &x, &y) == 2) { rs64_win_x = x; rs64_win_y = y; }
    } else if (rs64_g1f_optin) {
        // s7226: open centred on the target display (0 unless ROGUESQ_WIN_DISPLAY picks another).
        const int td = rs64_g1f_target_display();
        rs64_win_x = rs64_win_y = SDL_WINDOWPOS_CENTERED_DISPLAY(td);
    }
    SDL_Window* sdl_window = SDL_CreateWindow(
        "Star Wars: Rogue Squadron 64 Recompiled",
        rs64_win_x, rs64_win_y,
        rs64_g1f_win_w, rs64_g1f_win_h,
        SDL_WINDOW_RESIZABLE | SDL_WINDOW_SHOWN | (rs64_g1f_optin ? SDL_WINDOW_ALLOW_HIGHDPI : 0) |
            (rs64_g1f_fullscreen ? (rs64_g1f_fs_exclusive ? SDL_WINDOW_FULLSCREEN : SDL_WINDOW_FULLSCREEN_DESKTOP) : 0)
    );
    if (!sdl_window) {
        fprintf(stderr, "SDL_CreateWindow failed: %s\n", SDL_GetError());
        exit(EXIT_FAILURE);
    }
    g_rs64_window = sdl_window;
    { int px = 0, py = 0; SDL_GetWindowPosition(sdl_window, &px, &py);
      fprintf(stderr, "[g1f] window %dx%d fullscreen=%d at %d,%d\n", rs64_g1f_win_w, rs64_g1f_win_h, (int)rs64_g1f_fullscreen + (int)rs64_g1f_fs_exclusive, px, py); }
#if defined(_WIN32)
    SDL_SysWMinfo wm{};
    SDL_VERSION(&wm.version);
    SDL_GetWindowWMInfo(sdl_window, &wm);
    return { wm.info.win.window };
#elif defined(__APPLE__)
    SDL_SysWMinfo wm{};
    SDL_VERSION(&wm.version);
    SDL_GetWindowWMInfo(sdl_window, &wm);
    SDL_MetalView view = SDL_Metal_CreateView(sdl_window);
    g_rs64_nswin = (void*)wm.info.cocoa.window; g_rs64_layer = SDL_Metal_GetLayer(view);
    { int dw = 0, dh = 0; SDL_Metal_GetDrawableSize(sdl_window, &dw, &dh); fprintf(stderr, "[g1f] drawable %dx%d\n", dw, dh); }
    return ultramodern::renderer::WindowHandle{ wm.info.cocoa.window, SDL_Metal_GetLayer(view) };
#else
    return sdl_window;
#endif
}

void update_gfx(ultramodern::gfx_callbacks_t::gfx_data_t) {
    // Pump SDL events on the main thread (the one that owns the SDL window).
    // Win32 routes window messages to the window-owning thread's queue, so
    // SDL_PumpEvents on any other thread won't dispatch them. Without this,
    // the window appears "Not Responding" and F1/F2/F3/F4 keypresses never
    // reach RT64's developer-mode filter — even though poll_input() on the
    // game thread also calls SDL_PollEvent, that thread doesn't own the
    // window so messages stay queued.
    //
    // RT64's SDL_SetEventFilter installed via Application::sdlEventFilter
    // intercepts F1-F4 here (filters run before SDL_PollEvent dequeues), so
    // the controller-input poll on the game thread never sees those keys.
    SDL_PumpEvents();
    if (rs64_s7643_plant_on()) g_rs64_s7643_plant = g_rs64_s7643_plant + 1; // s7643 plant (main thread)
    // s7639 class ST: publish the window size for the F6 panel's draw hook (RT64 present thread), so that hook no longer
    // calls the main-thread-only SDL_GetWindowFromID / SDL_GetWindowSize itself. Cheap: a cached-field read.
    if (g_rs64_window) { int w = 0, h = 0; SDL_GetWindowSize(g_rs64_window, &w, &h);
        static const uint32_t id = SDL_GetWindowID(g_rs64_window); rs64_panel_note_window(w, h, id); }
    rs64_s7593_main_tick();
    rs64_s7668_panel_window_tick();
    rs64_g1f_apply_fs_toggle();
    rs64_display_hotplug_tick();
}

// ---------------------------------------------------------------------------
// Thread naming
// ---------------------------------------------------------------------------
static std::string get_game_thread_name(const OSThread* t) {
    switch (t->id) {
    case 1:  return "[Game] IDLE";
    case 3:  return "[Game] MAIN";
    case 4:  return "[Game] EEPROM";  // entry func_8006F2CC: save writer (osEepromLongWrite), not GRAPH
    case 5:  return "[Game] SCHED";
    case 10: return "[Game] AUDIOMGR";
    case 18: return "[Game] DMAMGR";
    default: return "[Game] " + std::to_string(t->id);
    }
}

// ---------------------------------------------------------------------------
// Game registration
// ---------------------------------------------------------------------------
// ROM hash: xxHash3-64 of rogue_squadron.z64 (USA v1.0, 16MB)
static constexpr uint64_t RS64_ROM_HASH = 0x6B66A44153594DEAULL;

std::vector<recomp::GameEntry> supported_games = {
    {
        .rom_hash             = RS64_ROM_HASH,
        .internal_name        = "ROGUE SQUADRON",
        .game_id              = u8"rs64.n64.us.1.0",
        .mod_game_id          = "rs64",
        .save_type            = recomp::SaveType::Eep4k,
        .is_enabled           = true,
        .entrypoint_address   = get_entrypoint_address(),
        .entrypoint           = rs64_entrypoint_with_rdram_capture,
    },
};

// ---------------------------------------------------------------------------
// main()
// ---------------------------------------------------------------------------
#ifndef _WIN32
// POSIX fallback for the Win32 symbolized stack printer.
void print_stack_with_symbols(void** frames, USHORT count) {
    char** syms = backtrace_symbols(frames, count);
    for (USHORT i = 0; i < count; i++) {
        fprintf(stderr, "  [%2u] %s\n", (unsigned)i, syms ? syms[i] : "?");
    }
    free(syms);
}
#endif

// The recompiled output contains syscall instructions only inside data
// misclassified as code (each preceded by INVALID-word traps); if one is ever
// reached something is deeply wrong, so just abort loudly.
extern "C" void recomp_syscall_handler(uint8_t* rdram, recomp_context* ctx, int32_t instruction_vram) {
    (void)rdram; (void)ctx;
    fprintf(stderr, "[FATAL] syscall reached at vram 0x%08X\n", (uint32_t)instruction_vram);
    fflush(stderr);
    abort();
}

#ifdef _WIN32
// One-shot init of DbgHelp symbol resolution — done lazily on first crash.
static void ensure_dbghelp_init() {
    static bool init = false;
    if (init) return;
    init = true;
    SymSetOptions(SYMOPT_LOAD_LINES | SYMOPT_DEFERRED_LOADS | SYMOPT_UNDNAME);
    SymInitialize(GetCurrentProcess(), nullptr, TRUE);
}

// Print stack frames with symbol resolution. Each frame becomes:
//   [ N] 0xADDR  module!function+0xOFF  (file:line)
void print_stack_with_symbols(void** frames, USHORT count) {
    ensure_dbghelp_init();
    HANDLE proc = GetCurrentProcess();
    HMODULE exe_base = GetModuleHandleW(nullptr);
    constexpr DWORD kNameMax = 512;
    char buf[sizeof(SYMBOL_INFO) + kNameMax];
    SYMBOL_INFO* sym = reinterpret_cast<SYMBOL_INFO*>(buf);
    for (USHORT i = 0; i < count; i++) {
        DWORD64 addr = (DWORD64)(uintptr_t)frames[i];
        uintptr_t rva = (uintptr_t)frames[i] - (uintptr_t)exe_base;
        sym->SizeOfStruct = sizeof(SYMBOL_INFO);
        sym->MaxNameLen = kNameMax - 1;
        DWORD64 disp = 0;
        const char* name = "?";
        if (SymFromAddr(proc, addr, &disp, sym)) {
            name = sym->Name;
        }
        IMAGEHLP_LINE64 line{}; line.SizeOfStruct = sizeof(line);
        DWORD lineDisp = 0;
        if (SymGetLineFromAddr64(proc, addr, &lineDisp, &line)) {
            fprintf(stderr, "  [%2u] 0x%llX rva 0x%llX  %s+0x%llX  (%s:%lu)\n",
                (unsigned)i, (unsigned long long)addr, (unsigned long long)rva,
                name, (unsigned long long)disp, line.FileName, (unsigned long)line.LineNumber);
        } else {
            fprintf(stderr, "  [%2u] 0x%llX rva 0x%llX  %s+0x%llX\n",
                (unsigned)i, (unsigned long long)addr, (unsigned long long)rva,
                name, (unsigned long long)disp);
        }
    }
}

// Full-memory minidump so we can inspect rdram contents post-mortem.
// ep may be null (SIGABRT path) — we still capture process+thread state.
static void write_minidump_safe(EXCEPTION_POINTERS* ep) {
    char path[MAX_PATH];
    SYSTEMTIME st;
    GetLocalTime(&st);
    CreateDirectoryA("dumps", NULL);
    CreateDirectoryA("dumps/crash-dumps", NULL);
    snprintf(path, sizeof(path),
        "dumps/crash-dumps/crash_%04u%02u%02u_%02u%02u%02u.dmp",
        st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond);
    HANDLE hFile = CreateFileA(path, GENERIC_WRITE, 0, NULL,
        CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) {
        fprintf(stderr, "[CRASH] CreateFile(%s) failed err=%lu\n",
            path, GetLastError());
        return;
    }
    MINIDUMP_EXCEPTION_INFORMATION mei{};
    PMINIDUMP_EXCEPTION_INFORMATION pmei = nullptr;
    if (ep) {
        mei.ThreadId = GetCurrentThreadId();
        mei.ExceptionPointers = ep;
        mei.ClientPointers = FALSE;
        pmei = &mei;
    }
    // Default to a lighter dump type. The earlier MiniDumpWithFullMemory
    // captured the full process address space (≈5 GB on this app, dominated
    // by D3D12/Vulkan render targets and texture caches). The symbolicated
    // stack trace in the .log already covers the common debug case; the
    // dump only needs threads + stacks + indirectly-referenced memory.
    // Set ROGUESQ_FULL_DUMP=1 to restore the full 5 GB dump for deep-dives.
    static const bool s_full_dump = []{
        const char *e = std::getenv("ROGUESQ_FULL_DUMP");
        return e && *e && *e != '0';
    }();
    MINIDUMP_TYPE dumpType = s_full_dump
        ? MiniDumpWithFullMemory
        : (MINIDUMP_TYPE)(MiniDumpNormal
                          | MiniDumpWithIndirectlyReferencedMemory
                          | MiniDumpWithDataSegs
                          | MiniDumpWithThreadInfo
                          | MiniDumpWithUnloadedModules);
    BOOL ok = MiniDumpWriteDump(GetCurrentProcess(), GetCurrentProcessId(),
        hFile, dumpType, pmei, NULL, NULL);
    CloseHandle(hFile);
    if (ok) {
        fprintf(stderr, "[CRASH] Minidump written: %s%s\n",
            path, s_full_dump ? " (full memory)" : " (lite)");
    } else {
        fprintf(stderr, "[CRASH] MiniDumpWriteDump failed err=%lu\n", GetLastError());
    }
    fflush(stderr);
}

static LONG WINAPI crash_handler(EXCEPTION_POINTERS* ep) {
    DWORD code = ep->ExceptionRecord->ExceptionCode;
    uintptr_t addr = (uintptr_t)ep->ExceptionRecord->ExceptionAddress;
    fprintf(stderr, "[CRASH] Exception 0x%08lX at 0x%llX\n", code, (unsigned long long)addr);
    if (code == EXCEPTION_ACCESS_VIOLATION && ep->ExceptionRecord->NumberParameters >= 2) {
        fprintf(stderr, "[CRASH] Access violation %s address 0x%llX\n",
            ep->ExceptionRecord->ExceptionInformation[0] ? "writing" : "reading",
            (unsigned long long)ep->ExceptionRecord->ExceptionInformation[1]);
    }
    // Capture stack BEFORE minidump — if the process is killed mid-minidump
    // (e.g. by an external watchdog), we still want the trace in stderr.
    void* frames[32];
    USHORT count = RtlCaptureStackBackTrace(0, 32, frames, nullptr);
    fprintf(stderr, "[CRASH] Stack trace (%u frames):\n", (unsigned)count);
    print_stack_with_symbols(frames, count);
    fflush(stderr);
    write_minidump_safe(ep);
    fflush(stderr);
    return EXCEPTION_CONTINUE_SEARCH;
}
#endif // _WIN32

static void rs64_m5_apply_drain_tick_policy() {
    if (std::getenv("ROGUESQ_DRAIN_INLOOP_TICK") != nullptr) {
        return;
    }
#ifdef _WIN32
    _putenv_s("ROGUESQ_DRAIN_INLOOP_TICK", "0");
#else
    setenv("ROGUESQ_DRAIN_INLOOP_TICK", "0", 0);
#endif
}

// G1c (s6578): ROGUESQ_DRAW_DISTANCE=<dd> with dd > 1 bundles the validated pool/heap recipe
// (s6567 RAMTOP guards, s6569 malloc spill, s6099 DL-chunk arena, s6058 terrain pool x ceil(dd)); px2-px5 hold
// clean with it (s6567, s6574) and px>=2 faults without it (s6549-s6551). Explicit env values win; dd<=1 untouched.
extern "C" void rs64_s7258_merge_reinit();
extern "C" int g_rs64_s7030;  /* s7037: upstream_compat.cpp fog/off-map cull arm */
// s7358 class AI (tools/s7358_envparse_census.py): owner numeric knobs reach sizes unvalidated. ROGUESQ_DRAW_DISTANCE is read by
// ~12 host and fixup sites with bare atof: the terrain multiplier (apply_s6036_dd) clamps it to [0.25,4] / [0.25,8] (DD_UNSAFE)
// but its `v < 0.25` test lets NaN through (pre-fix arm "nan": multiplier nan -> assert in buildVisibleTerrainGridAroundCamera,
// SIGABRT), a typo like "x4" reads 0 -> silent 0.25x terrain, and the tile pool (rs64_s6893_tilepool_size) sizes ceil(dd)^2*2
// unclamped (pre-fix arm "d12": k=288, spill req 0x677DC0 arena full, SIGBUS). Normalise once, before any lazy reader runs:
// not a number / not finite -> unset (retail, warned), above the 8.0 terrain ceiling -> 8 (warned). ROGUESQ_FB_WIDTH set by
// hand bypasses the aspect policy's 1024 clamp (s6142: >1024 stalls the guest); negative atoi became a huge uint32 width in
// upstream_compat's VI widen. Clamp it the same way. ROGUESQ_S7358_ENVCHECK=0 = old.
static void rs64_s7358_sanitize_env() {
    const char* off = std::getenv("ROGUESQ_S7358_ENVCHECK");
    if (off && *off == '0') return;
    auto num = [](const char* e, double& v) {
        char* end = nullptr; v = std::strtod(e, &end);
        if (end == e) return false;
        while (*end && std::isspace((unsigned char)*end)) end++;
        return *end == '\0' && std::isfinite(v);
    };
    if (const char* e = std::getenv("ROGUESQ_DRAW_DISTANCE"); e && *e) {
        double v = 0;
        if (!num(e, v)) {
            std::fprintf(stderr, "[s7358-env] ROGUESQ_DRAW_DISTANCE=%s is not a finite number: ignored (retail draw distance)\n", e);
            unsetenv("ROGUESQ_DRAW_DISTANCE");
        } else if (v > 8.0) {
            std::fprintf(stderr, "[s7358-env] ROGUESQ_DRAW_DISTANCE=%s is above the 8.0 terrain ceiling: using 8\n", e);
            setenv("ROGUESQ_DRAW_DISTANCE", "8", 1);
        }
        // s7712: the terrain multiplier (apply_s6036) caps at 4.0 unless ROGUESQ_DD_UNSAFE is a non-'0' value, but the dd bundle
        // (rs64_g1c_apply_dd_policy: pools px, OSMEM 12, dd>=6 off-map cull, dd>=8 px8/WIDEWIN_R auto) and the tile pool read the raw
        // string, so dd6/dd8 without UNSAFE drew at 4x while sizing for 6/8 (s7712 arm B: "[dd] multiplier 4" + "[ddbundle] dd=6.00").
        // Apply the same cap here so every reader sees the drawn value. ROGUESQ_S7712_DDCAP=0 = old.
        const char* u = std::getenv("ROGUESQ_DD_UNSAFE"); const char* dc = std::getenv("ROGUESQ_S7712_DDCAP");
        const bool unsafe = u && *u && *u != '0';
        if (!(dc && *dc == '0') && !unsafe && (e = std::getenv("ROGUESQ_DRAW_DISTANCE")) && *e && num(e, v) && v > 4.0) {
            std::fprintf(stderr, "[s7712-dd] ROGUESQ_DRAW_DISTANCE=%s needs ROGUESQ_DD_UNSAFE=1 above 4: using 4 for every reader\n", e);
            setenv("ROGUESQ_DRAW_DISTANCE", "4", 1);
        }
    }
    // s7713 (multi-reader clamp census, tools/s7713_multireader_census.py): recomp.cpp and upstream_compat's guest top treat an
    // OSMEM_MB outside 4..16 (atoi) as 8, but the dd bundle (rs64_g1c_apply_dd_policy) tested the raw atoi > 8 and armed SPILL_HI +
    // RAMTOP 24 for e.g. 20 or 32 while the guest got 8 MB: an unqualified hybrid of the two layouts. Normalise to the 8 the
    // memory readers already use, so every reader agrees. ROGUESQ_S7713_OSMEMCAP=0 = old.
    if (const char* e = std::getenv("ROGUESQ_OSMEM_MB"); e && *e) {
        const char* oc = std::getenv("ROGUESQ_S7713_OSMEMCAP");
        const int v = std::atoi(e);
        if (!(oc && *oc == '0') && (v < 4 || v > 16)) {
            std::fprintf(stderr, "[s7713-osmem] ROGUESQ_OSMEM_MB=%s is outside 4..16: using 8 for every reader (recomp.cpp does)\n", e);
            setenv("ROGUESQ_OSMEM_MB", "8", 1);
        }
    }
    if (const char* e = std::getenv("ROGUESQ_FB_WIDTH"); e && *e) {
        double v = 0;
        if (!num(e, v) || v < 0.0) {
            std::fprintf(stderr, "[s7358-env] ROGUESQ_FB_WIDTH=%s is not a width: ignored\n", e);
            unsetenv("ROGUESQ_FB_WIDTH");
        } else if (v > 1024.0) {
            std::fprintf(stderr, "[s7358-env] ROGUESQ_FB_WIDTH=%s is above the 1024 limit (s6142): using 1024\n", e);
            setenv("ROGUESQ_FB_WIDTH", "1024", 1);
        }
    }
}

static void rs64_g1c_apply_dd_policy() {
    const char* e = std::getenv("ROGUESQ_DRAW_DISTANCE");
    double dd = (e && *e) ? std::atof(e) : 1.0;
    if (!(dd > 1.0 + 1e-3)) return;
    int px = (int)std::ceil(dd);
    std::fprintf(stderr, "[ddbundle] dd=%.2f px=%d (ramtop16 spill dlpoolx4MB)\n", dd, px);
    // s7037: px > 5 (10240 cells) is opt-in via ROGUESQ_DD_POOLX_MAX=<6..8> (default 5, the s7019 clamp).
    // s7293: dd>=8 with WIDEWIN at <=16:9 width (FB_WIDTH <= 796) auto-raises the clamp to 8 and WIDEWIN_R to 128. s7292 (L4 16:9
    // dd8, 1 run/arm, ctl px8 depth 128 / ref depth 80 PASS): total emitted cells/call ref 6902 / px8(R88) 7316 / px8+R128 11322,
    // win77-97 11.83 / 11.84 / 12.06 ms, all 60.0/s. s7297: width gate dropped. s7296 (L4 21:9 dd8, 1 run/arm, ctl flat 30 + px8
    // depth 128 PASS): total_emit ref(px5,R88) 7466 / px8 7909 / px8+R128 11818, win77-97 12.98 / 13.54 / 13.65 ms, all 60.0/s.
    // Explicit ROGUESQ_DD_POOLX_MAX / _WIDEWIN_R win; ROGUESQ_DD_PX8_AUTO=0 turns it off.
    { const char* pm = std::getenv("ROGUESQ_DD_POOLX_MAX"); int mx = (pm && *pm) ? std::atoi(pm) : 5; if (mx < 1) mx = 1; if (mx > 8) mx = 8;
      const char* ww = std::getenv("ROGUESQ_DD_WIDEWIN"); const char* fw = std::getenv("ROGUESQ_FB_WIDTH"); const char* pa = std::getenv("ROGUESQ_DD_PX8_AUTO");
      if (!(pm && *pm) && dd >= 8.0 - 1e-3 && ww && *ww && ww[0] != '0' && !(pa && pa[0] == '0')) {
          mx = 8; setenv("ROGUESQ_DD_WIDEWIN_R", "128", 0);
          std::fprintf(stderr, "[s7293] dd%.0f px8 auto poolx_max=8 widewin_r=%s fbw=%s\n", dd, std::getenv("ROGUESQ_DD_WIDEWIN_R"), fw ? fw : "-");
      }
      if (px > mx) px = mx; }
    // s7037 G1c bundle: s7034-s7036 qualified the fog-depth off-map cull (R=2, K=0.6, height gate off) at 21:9 dd6 WIDEWIN
    // (L1/L4/L5 ~505 s, 0 crashes, rsp -1.3..-2.8 ms, image <=0.18 at frozen poses). Default it on for dd>=6 with WIDEWIN on;
    // any explicit ROGUESQ_DD_OFFMAPCULL* wins (=-1 = off). g_rs64_s7030 latches at static init, before this runs, so arm it here.
    { const char* ww = std::getenv("ROGUESQ_DD_WIDEWIN");
      if (dd >= 6.0 - 1e-3 && ww && *ww && ww[0] != '0' && !std::getenv("ROGUESQ_DD_OFFMAPCULL")) {
          setenv("ROGUESQ_DD_OFFMAPCULL", "2", 1);
          // s7050 made 21:9 default to K=0.5 (L12 +0.9/+0.7 fps); s7051 reverted it: on L4 21:9 K=0.5 shaves the far horizon
          // band (0.23-0.33 mean dLum vs K=0.6, 0.7% px, visible by eye; KEDGE does not cover it). K=0.5 stays an explicit opt-in.
          // s7056: level-scoped instead: wider than 16:9 (FB_WIDTH > 796) and no explicit K -> K=0.5 on L12 only (s7050 gain), L4 keeps 0.6.
          { const char* fw = std::getenv("ROGUESQ_FB_WIDTH");
            if (fw && std::atoi(fw) > 796 && !std::getenv("ROGUESQ_DD_OFFMAPCULL_K")) setenv("ROGUESQ_DD_OFFMAPCULL_KLEVEL", "12:0.5,13:0.5", 0);
            // s7062: 21:9 L9 WIDEWIN cap 8192 (s7061: holds the dense burst ~60 fps where 10240 dips; frozen poses 0.00 vs 10240 in
            // 2 runs while the 6144 control shows 1.18/0.99/0.25). Auto only when no explicit _CAP; an explicit _CAPLEVEL wins.
            if (fw && std::atoi(fw) > 796 && !std::getenv("ROGUESQ_DD_WIDEWIN_CAP")) setenv("ROGUESQ_DD_WIDEWIN_CAPLEVEL", "9:8192", 0); }
          setenv("ROGUESQ_DD_OFFMAPCULL_K", "0.6", 0); setenv("ROGUESQ_DD_OFFMAPCULL_H", "off", 0);
          // s7047: eye-to-edge K gate (s7046) folded in: off-map cells on a map side within 12 cells of the eye use K=0.8, which hides
          // L12's hard horizon cut (frozen poses 0.07 vs 0.81, 2 runs) for ~0.3 ms rsp (L12 59.6/59.9 vs 59.8 fps same run). =0 disables.
          setenv("ROGUESQ_DD_OFFMAPCULL_KEDGE", "0.8,12", 0);
          g_rs64_s7030 = 1;
          std::fprintf(stderr, "[s7037] dd bundle offmapcull=2 k=%s h=%s kedge=%s klevel=%s caplevel=%s (auto)\n", std::getenv("ROGUESQ_DD_OFFMAPCULL_K"), std::getenv("ROGUESQ_DD_OFFMAPCULL_H"), std::getenv("ROGUESQ_DD_OFFMAPCULL_KEDGE"), std::getenv("ROGUESQ_DD_OFFMAPCULL_KLEVEL") ? std::getenv("ROGUESQ_DD_OFFMAPCULL_KLEVEL") : "-", std::getenv("ROGUESQ_DD_WIDEWIN_CAPLEVEL") ? std::getenv("ROGUESQ_DD_WIDEWIN_CAPLEVEL") : "-");
      } }
    // s7258: the s7247 WIDEWIN stack (R=48 + MERGE 0.4/E16) rides with the dd bundle whenever WIDEWIN is on. s7257 (AC, same run,
    // control dd6rd flat 30 PASS): L4 21:9 dd6 window 14.04 -> 9.82 ms, late dip s 9 -> 0; s7259 L12 21:9 dd6 (control offd PASS):
    // p50 12.02 -> 8.94 ms, <55/s beyond route 20 -> 0 s. s7260 extends it to dd2-dd5 (s7247 image check dd4 clean, s7248 dd4
    // fixed-on 60/s). Any explicit ROGUESQ_DD_WIDEWIN_R / _MERGE / _MERGE_E wins; ROGUESQ_DD_WIDEWIN_STACK=0 turns it off.
    // s7266: auto R 48 -> 88. R=48 skipped 92-95% of the wide-only cells (they sit 32-96 cells out, s7265_ww_r_predict), erasing
    // the side-edge gain (s7264). s7265_ww_r_cost (L4 21:9 dd4 AC, control w0d DUTY flat30 21 s PASS): win77-97 r0 12.42 / r72 11.58
    // / r88 12.03 ms all 60/s, 0 flat runs; s7265_ww_r_edge (control c219 STACK=0 L/R hard80 -8.0/-8.8 PASS): r88 -7.6/-9.6 kept.
    { const char* ww = std::getenv("ROGUESQ_DD_WIDEWIN"); const char* st = std::getenv("ROGUESQ_DD_WIDEWIN_STACK");
      if (ww && *ww && ww[0] != '0' && !(st && st[0] == '0')) {
          // s7287: L12 at dd>=6 keeps R=48 (r88 flat 30 at t=77-84 on L12 16:9 dd6 in s7286 and s7287; r48 60/s 10.95 ms, same run).
          // dd4 L12 r88 held 59.3/s (s7287 d4), dd5 unmeasured. An explicit _RLEVEL (or _RLEVEL=none) wins.
          if (dd >= 6.0) setenv("ROGUESQ_DD_WIDEWIN_RLEVEL", "12:48", 0);
          setenv("ROGUESQ_DD_WIDEWIN_R", "88", 0); setenv("ROGUESQ_DD_WIDEWIN_MERGE", "0.4", 0); setenv("ROGUESQ_DD_WIDEWIN_MERGE_E", "16", 0);
          rs64_s7258_merge_reinit();
          std::fprintf(stderr, "[s7258] dd%.0f widewin stack r=%s rlevel=%s merge=%s e=%s (auto)\n", dd, std::getenv("ROGUESQ_DD_WIDEWIN_R"), std::getenv("ROGUESQ_DD_WIDEWIN_RLEVEL") ? std::getenv("ROGUESQ_DD_WIDEWIN_RLEVEL") : "-", std::getenv("ROGUESQ_DD_WIDEWIN_MERGE"), std::getenv("ROGUESQ_DD_WIDEWIN_MERGE_E"));
      } }
    char b[16];
    std::snprintf(b, sizeof b, "%d", px);
    // s6858: the spill arena defaults to 0x80800000-0x80C00000, which is game heap once osMemSize > 8 MB (21:9 sets
    // OSMEM_MB=12 itself). lvl1/lvl9 16:9+OSMEM12+dd4 then crashed 9/9 at mission load (HMT material name pointer
    // 0xA7751264 / 0x80000003 in loadTextureToMemory's strncmp). Move it above 16 MB (the s6593 SPILL_HI + RAMTOP 20 layout).
    // Owner crash 2026-11-05: the final mission (LEVEL=15) at dd>1 16:9 needs more than 8 MB heap + the 4 MB spill arena at
    // mission load (0xB7FC0 x3, 0x170000, 0x30000): "[spill] arena full", rs_malloc NULL, then a NULL store in whichever
    // caller came next. Same reqs fit with the 21:9 layout, so all dd>1 use it. ROGUESQ_OSMEM_MB=8 = old layout.
    setenv("ROGUESQ_OSMEM_MB", "12", 0);
    const char* om = std::getenv("ROGUESQ_OSMEM_MB");
    if (om && std::atoi(om) > 8) {
        setenv("ROGUESQ_SPILL_HI", "1", 0);
        setenv("ROGUESQ_RAMTOP_MB", "24", 0);  /* s7326: 8 MB spill arena 0x81000000-0x81800000 (was 20 = 4 MB) */
        std::fprintf(stderr, "[ddbundle] osmem=%s MB > 8 -> spill arena 0x81000000, ramtop 24 MB\n", om);
    }
    setenv("ROGUESQ_RAMTOP_MB", "16", 0);
    setenv("ROGUESQ_MALLOC_SPILL", "1", 0);
    setenv("ROGUESQ_DLPOOLX", "1", 0);
    setenv("ROGUESQ_DLPOOLX_MB", "4", 0);
    setenv("ROGUESQ_DLPOOLX_AT", "3000", 0);
    setenv("ROGUESQ_DD_POOLX", b, 0);
    // s6908 G5h: cutscene levels author a pool of 400-600 (table 0x800B090C), and our window clamp reads it as an area cap; 4096 = the 64x64 slot limit. =0 old.
    setenv("ROGUESQ_DD_POOLMIN", "4096", 0);
    // s6788 G3e: the s6540 per-swap span-bypass cap (120 cells) made dd>1 terrain bistable: the retail span test rejects
    // ~1500 in-window cells in most swaps (pose-dependent), so terrain flipped between full dd and LESS than retail
    // (lvl1 dd4 median tris 816 vs dd1 1083; 47 in-flight drop edges in 180 s). Unlimited accept: 4 drops, median 1407.
    // Denser frames then exceed the synthetic LLE ucode iteration guard (431 fires at 65536), so raise it as well.
    setenv("ROGUESQ_BYPASS_MAXCELLS", "-1", 0);
    setenv("ROGUESQ_UCODE_CAP", "1048576", 0);
}

// G1d (s6121): ROGUESQ_ASPECT=<w>:<h> with w/h > 4:3 derives the game-side widescreen
// knobs (framebuffer width = round(448*r), projection + viewport scales = width/512).
// Explicit ROGUESQ_FB_WIDTH / VPW_SCALE / ASPECT_SCALE win. 4:3, orig, expand: untouched (retail).
// G1f (s6688): ROGUESQ_ASPECT=auto takes the aspect of display 0 (clamped to 4:3..1024/448,
// the verified framebuffer widths) and rewrites itself to "<r>:1" for both consumers;
// the window opens at the game aspect, sized to the desktop. ROGUESQ_FULLSCREEN=1 starts
// in desktop fullscreen. Game width is fixed at boot: a later resize letterboxes.
static void rs64_g1d_apply_aspect_policy() {
    const char* fs = std::getenv("ROGUESQ_FULLSCREEN");
    rs64_g1f_fullscreen = fs && std::atoi(fs) != 0;
    rs64_g1f_fs_exclusive = fs && std::atoi(fs) == 2;
    const char* as = std::getenv("ROGUESQ_ASPECT");
    rs64_g1f_optin = (as && *as) || rs64_g1f_fullscreen;  // s7730: "" = unset
    if (!rs64_g1f_optin) return;
    SDL_InitSubSystem(SDL_INIT_VIDEO);  // refcounted; create_gfx's SDL_Init keeps it
    // s6929 G1d: under ROGUESQ_VI_SHAPE a 1024-column picture is 1280x458, so the widest window is 2.795, not 1024/448.
    const char* vsh = std::getenv("ROGUESQ_VI_SHAPE");
    const bool vshape = vsh && *vsh && *vsh != '0';
    const double amax = vshape ? 1024.0 * 1.25 / 458.0 : 1024.0 / 448.0;
    if (as && !std::strcmp(as, "auto")) {
        SDL_DisplayMode dm{};
        double r = 4.0 / 3.0;
        const int td = rs64_g1f_target_display();
        if (SDL_GetDesktopDisplayMode(td, &dm) == 0 && dm.h > 0) r = (double)dm.w / dm.h;
#ifdef __APPLE__
        // s6930: desktop fullscreen stops below the notch band (3024x1898 of 3024x1964), so the whole-panel aspect left
        // side bars. Windowed auto keeps the panel aspect. ROGUESQ_G1F_NOTCH=0 = old.
        const char* nt = std::getenv("ROGUESQ_G1F_NOTCH");
        if (dm.h > 0 && rs64_g1f_fullscreen && !(nt && *nt == '0')) {
            SDL_Rect db{};
            const double top = SDL_GetDisplayBounds(td, &db) == 0 ? rs64_display_top_inset_frac_at(db.x, db.w, db.h)
                                                                   : rs64_display_top_inset_frac();
            if (top > 0.0 && top < 0.5) r /= 1.0 - top;
            std::fprintf(stderr, "[g1f] notch band %.4f of display height\n", top);
        }
#endif
        r = std::clamp(r, 4.0 / 3.0, amax);
        char rb[32];
        std::snprintf(rb, sizeof rb, "%.4f:1", r);
        setenv("ROGUESQ_ASPECT", rb, 1);
        std::fprintf(stderr, "[g1f] ROGUESQ_ASPECT=auto display=%dx%d -> %s\n", dm.w, dm.h, rb);
        as = std::getenv("ROGUESQ_ASPECT");
    }
    const char* c = as ? std::strchr(as, ':') : nullptr;
    double wr = c ? std::atof(as) : 0.0, hr = c ? std::atof(c + 1) : 0.0;
    rs64_g1f_fit_window(wr > 0.0 && hr > 0.0 ? std::clamp(wr / hr, 4.0 / 3.0, amax) : 4.0 / 3.0);
    if (!c && !rs64_g1f_fullscreen) { rs64_g1f_win_w = 640; rs64_g1f_win_h = 480; }
    // ROGUESQ_WINDOW_FIT=0: pre-G1f window (640x480, no high-DPI, no fullscreen, no RT64 aspect rewrite).
    const char* wf = std::getenv("ROGUESQ_WINDOW_FIT");
    const bool fit = !wf || std::atoi(wf) != 0;
    if (!fit) { rs64_g1f_win_w = 640; rs64_g1f_win_h = 480; rs64_g1f_optin = false; rs64_g1f_fullscreen = false; }
    if (!c) return;
    double w = std::atof(as), h = std::atof(c + 1);
    if (!(w > 0.0 && h > 0.0) || w / h <= 4.0 / 3.0 + 1e-3) return;
    int fbw = (int)(448.0 * w / h + 0.5);
    // s6928 G1d: ROGUESQ_VI_SHAPE=1 shows a column 1.25 dots wide on 458 half-lines (the retail flight raster), so the
    // window needs fewer columns: 16:9 652, 21:9 856. The 340-row lever (s6927) answers the square-column present, so off.
    if (vshape) {
        fbw = (((int)(458.0 / 1.25 * w / h + 0.5)) + 2) & ~3;
        if (fbw <= 512) return;  // s6929: the 512 picture is already 1.397, narrower windows just letterbox it
        if (fbw == 640) fbw = 644;  // s6929: at 640 the presenter cannot tell flight (par 1.25) from a 640 mode (par 1)
        setenv("ROGUESQ_G1D_340PERSP", "0", 0);
    } else if ((fbw & 3) && fbw > 512 && fbw <= 1024) {
        // s7188: ASPECT=auto on a non-standard display (built-in panel below the notch: 1.5916 -> 713) gave an ODD
        // width: RGBA16 row stride 1426 B (not 8-aligned) and the 339-row menus (SELECT LEVEL / AVAILABLE CRAFT /
        // hangar) even the width and scissor at xh 711, leaving 2 undrawn right columns instead of the 1 every even
        // width shows (RDP stream, s7188 capscissor). Round to a multiple of 4 like the VI_SHAPE path (16:9 796 and
        // the 1024 clamp are already aligned, so the verified widths do not move). RT64's output aspect follows the
        // rounded width (s6688 rule). ROGUESQ_FBW_ALIGN=0 keeps the unrounded width.
        const char* al = std::getenv("ROGUESQ_FBW_ALIGN");
        if (!(al && *al == '0')) {
            const int f0 = fbw;
            fbw = (fbw + 2) & ~3;
            char ab[32];
            std::snprintf(ab, sizeof ab, "%d:448", fbw);
            if (fit) { setenv("ROGUESQ_ASPECT", ab, 1); as = std::getenv("ROGUESQ_ASPECT"); }
            std::fprintf(stderr, "[g1d] FB_WIDTH %d -> %d (multiple of 4, s7188)\n", f0, fbw);
        }
    }
    char b[32];
    if (fbw > 1024) {
        fbw = 1024;  // s6142: 1024 renders, 1032/1045 do not (stripe garbage, guest stall); cap source unnamed
        // s6688: RT64's output aspect must match the clamped game width, or 21:9 stretches ~2%.
        if (fit) setenv("ROGUESQ_ASPECT", "1024:448", 1);
    }
    std::snprintf(b, sizeof b, "%d", fbw);
    setenv("ROGUESQ_FB_WIDTH", b, 0);
    if (fbw > 796) setenv("ROGUESQ_OSMEM_MB", "12", 0);  // s6425: 21:9 (w1024) framebuffers exhaust the 8 MB heap -> level-1 load_level_hmp NULL-dst crash (s6424 a219 3/3); 16:9 fits in 8 MB
    // s6930: exact, n/512 needs 9 places. %.4f read 652 as 1.2734: viewport 651.98, truncated, evened by the game, so
    // scissor lrx 649 and 3 black columns at the right at 652 and 584. Passing ROGUESQ_VPW_SCALE=1.2734 shows the old.
    std::snprintf(b, sizeof b, "%.9f", fbw / 512.0);
    setenv("ROGUESQ_VPW_SCALE", b, 0);
    setenv("ROGUESQ_ASPECT_SCALE", b, 0);
    std::fprintf(stderr, "[g1d] ROGUESQ_ASPECT=%s -> FB_WIDTH=%d scales=%s\n", as, fbw, b);
    // s6159: HUD anchor + radar-disc region shift derived from fb width. Calibrated at w796 only
    // (A=142=(fbw-512)/2, R-A=192 at w796; w1024 overshot ~55px with slope 0.676 so linear 2-pt fit 0.434*ex+68.7, region 520..630 x 20..135 = right edge - 276/-166 scaled by fbw/796);
    // other widths are extrapolation until verified. ROGUESQ_HUD_ANCHOR_AUTO=0 disables.
    const char* au = std::getenv("ROGUESQ_HUD_ANCHOR_AUTO");
    if (!au || std::atoi(au) != 0) {
        const double ex = fbw - 512.0, A = ex / 2.0, k = fbw / 796.0;
        char hb[64], rg[96], sh[32];
        // Right-half add is applied on top of a position that already includes A,
        // so the on-screen right edge lands at retail+second. second must be the
        // extra width (fbw-512) to keep the retail inset; A+RA overshoots 796 by 50 px.
        std::snprintf(hb, sizeof hb, "%.1f,%.1f", A, ex);
        std::snprintf(rg, sizeof rg, "%.0f,%.0f,20,135", fbw - 276.0 * k, fbw - 166.0 * k);
        // s6928: at VI_SHAPE widths the formula above misses the disc at 652 (fit from 796 and 1024 only, cone left behind).
        // The ring sits at retail x 435 plus the centring shift A; 380..490 around it reads 522..632 at 796, the calibrated 520..630.
        if (vsh && *vsh && *vsh != '0') std::snprintf(rg, sizeof rg, "%.0f,%.0f,20,135", A + 380.0, A + 490.0);
        // Disc tris are selected pre-shift. The shift that kept the wedge inside the
        // ring was (second - A); with second = ex that is A. RA leaves the wedge behind.
        std::snprintf(sh, sizeof sh, "%.0f", A);
        setenv("ROGUESQ_HUD_ANCHOR", hb, 0);
        setenv("ROGUESQ_LOG_REGION", rg, 0);
        setenv("ROGUESQ_SHIFT_REGION", sh, 0);
        std::fprintf(stderr, "[g1d] hud anchor=%s disc region=%s shift=%s\n", hb, rg, sh);
    }
}


// s6979 G1e: async stderr (ROGUESQ_STDERR_ASYNC, DEFAULT ON, =0 old direct writes). ORIGIN ours: the build writes ~190 KB/s of
// diagnostic stderr by default (62 MB per 330 s soak); stderr is unbuffered, so every fprintf is a write() syscall on the calling
// thread. The s6979 thread census (ROGUESQ_G1E_THREADS) caught the Gfx thread in UNINTERRUPTIBLE write() from
// rsp_dpc_submit_impl / RT64 State::updateScreen / FramebufferRenderer::submitRasterScene for 2-5 ms inside late 21:9 send_dl
// windows (normal windows ~0). Here fd 2 becomes a pipe: a USER_INTERACTIVE reader moves it into memory, a UTILITY writer does the
// blocking writes to the original fd. ROGUESQ_STDERR_ASYNC_AT=<s> switches on at <s> s (same-run A/B); marker
// "[stderr-async] on t=<mach s>". rs64_stderr_async_restore() (crash/abort/exit) drains up to 300 ms and puts the original fd back.
#if !defined(_WIN32)
#include <sys/ioctl.h>
#include <mach/mach_time.h>
#include <pthread/qos.h>
namespace s6979se {
static int orig = -1, rd = -1; static std::atomic<int> on{0}; static std::atomic<size_t> queued{0}; static std::atomic<uint64_t> dropped{0};
static std::mutex m; static std::condition_variable cv; static std::deque<std::string> q;
static void reader() {
    pthread_setname_np("stderr-rd"); pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
    std::vector<char> b(1 << 16);
    for (;;) {
        const ssize_t n = read(rd, b.data(), b.size()); if (n <= 0) { if (n < 0 && errno == EINTR) continue; return; }
        if (queued.load() > (256u << 20)) { dropped += (uint64_t)n; continue; }
        { std::lock_guard<std::mutex> l(m); q.emplace_back(b.data(), (size_t)n); queued += (size_t)n; } cv.notify_one();
    }
}
static void wr_all(const char *d, size_t n) {
    size_t o = 0; while (o < n) { const ssize_t w = write(orig, d + o, n - o); if (w < 0) { if (errno == EINTR) continue; break; } o += (size_t)w; }
}
// s7431 class CN: per-tag line cap, applied here on the writer thread (game threads pay nothing). ORIGIN ours: s7431 measured a
// no-logging-env owner-recipe flight (FPS60 dd4 16:9, lvl1) writing 39.5 MB of stderr in 260 s, ~1.6 MB per 10 s in flight,
// from 37 default-on diagnostic tags that print every frame/task with no budget ([s5855] 800 KB/10s, [vi-mode-table],
// [osViSetMode], [dpc-fwd], [s2020-svc], [s3290-stall], [lle ...) - into the owner's Terminal scrollback (26 GB seen, s6979).
// ROGUESQ_STDERR_CAP unset: on iff the original stderr is a terminal (owner launches; soak harnesses pipe/redirect and keep every
// line their gates parse); =1 force on; =0 off. Each tag (first token up to space/'#'/':') gets CAP_BURST (default 200) lines,
// then a token bucket of ROGUESQ_STDERR_CAP_RATE lines/s (default 0.2); a line costs 1 + bytes/512 tokens. Lines containing CRASH/crash/abort/FATAL/fatal/SIG/
// ERROR/assert always pass. Every 30 s with drops: one "[stderr-cap] dropped" summary line (itself bounded).
static int cap_on = 0; static double cap_burst = 200, cap_rate = 0.2;
static bool must_pass(const char *b, size_t n) {
    static const char *k[] = {"CRASH", "crash", "abort", "FATAL", "fatal", "SIG", "ERROR", "assert", "[stderr-"};
    for (const char *w : k) { const size_t wl = strlen(w); for (size_t i = 0; i + wl <= n && i < 512; i++) if (!memcmp(b + i, w, wl)) return true; }
    return false;
}
struct capst { double tok; double t; uint64_t dl, db; };
static void writer() {
    pthread_setname_np("stderr-wr"); pthread_set_qos_class_self_np(QOS_CLASS_UTILITY, 0);
    std::unordered_map<std::string, capst> tags; std::string part; uint64_t dl = 0, db = 0; auto t0 = std::chrono::steady_clock::now();
    double last_sum = 0;
    auto now_s = [&] { return std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count(); };
    auto line = [&](const char *b, size_t n) {  // n includes the '\n' (or not, for a timed-out partial)
        if (must_pass(b, n)) { wr_all(b, n); return; }
        size_t e = 0; while (e < n && e < 48 && b[e] != ' ' && b[e] != '#' && b[e] != ':' && b[e] != '\n' && b[e] != '\t') e++;
        auto it = tags.find(std::string(b, e)); const double t = now_s();
        if (it == tags.end()) it = tags.emplace(std::string(b, e), capst{cap_burst, t, 0, 0}).first;
        capst &c = it->second; c.tok = std::min(cap_burst, c.tok + (t - c.t) * cap_rate); c.t = t;
        const double cost = 1.0 + (double)n / 512.0;  // long lines ([s5855] ~5 KB) cost more
        if (c.tok >= cost) { c.tok -= cost; wr_all(b, n); } else { c.dl++; c.db += n; dl++; db += n; }
    };
    for (;;) {
        std::string s_; bool got = false;
        { std::unique_lock<std::mutex> l(m);
          if (cap_on && !part.empty()) got = cv.wait_for(l, std::chrono::milliseconds(200), [] { return !q.empty(); });
          else { cv.wait(l, [] { return !q.empty(); }); got = true; }
          if (got) { s_ = std::move(q.front()); q.pop_front(); } }
        if (!cap_on) { wr_all(s_.data(), s_.size()); queued -= s_.size(); continue; }
        if (!got) { line(part.data(), part.size()); part.clear(); continue; }  // flush a stuck partial line
        size_t o = 0;
        for (;;) {
            const char *nl = (const char *)memchr(s_.data() + o, '\n', s_.size() - o);
            if (!nl) { part.append(s_.data() + o, s_.size() - o); break; }
            const size_t e = (size_t)(nl - s_.data()) + 1;
            if (part.empty()) line(s_.data() + o, e - o); else { part.append(s_.data() + o, e - o); line(part.data(), part.size()); part.clear(); }
            o = e;
        }
        if (part.size() > (64u << 10)) { line(part.data(), part.size()); part.clear(); }
        queued -= s_.size();
        const double t = now_s();
        if (dl && t - last_sum >= 30) {
            last_sum = t; std::vector<std::pair<uint64_t, std::string>> v;
            for (auto &kv : tags) if (kv.second.dl) v.push_back({kv.second.db, kv.first});
            std::sort(v.rbegin(), v.rend()); char h[512];
            int k = snprintf(h, sizeof h, "[stderr-cap] dropped t=%.0f lines=%llu bytes=%llu tags=%zu top:", t, (unsigned long long)dl, (unsigned long long)db, v.size());
            for (size_t i = 0; i < v.size() && i < 5 && k > 0 && k < (int)sizeof h - 64; i++) k += snprintf(h + k, sizeof h - k, " %s=%llu", v[i].second.c_str(), (unsigned long long)v[i].first);
            if (k > 0 && k < (int)sizeof h - 1) { h[k++] = '\n'; wr_all(h, (size_t)k); }
        }
    }
}
static void switch_on() {
    int p[2]; if (pipe(p) != 0) return;
    rd = p[0]; std::thread(reader).detach(); std::thread(writer).detach();
    fflush(stderr); dup2(p[1], STDERR_FILENO); close(p[1]); on = 1;
    mach_timebase_info_data_t tb; mach_timebase_info(&tb);
    fprintf(stderr, "[stderr-async] on t=%.6f cap=%d burst=%.0f rate=%g\n", (double)mach_absolute_time() * tb.numer / tb.denom / 1e9, cap_on, cap_burst, cap_rate);
}
static void init() {
    const char *e = std::getenv("ROGUESQ_STDERR_ASYNC"); if (e && *e && std::atoi(e) == 0) return;
    orig = dup(STDERR_FILENO); if (orig < 0) return;
    { const char *c = std::getenv("ROGUESQ_STDERR_CAP"); cap_on = (c && *c) ? (std::atoi(c) != 0) : isatty(orig);
      if (const char *b = std::getenv("ROGUESQ_STDERR_CAP_BURST")) if (atof(b) >= 1) cap_burst = atof(b);
      if (const char *r = std::getenv("ROGUESQ_STDERR_CAP_RATE")) if (atof(r) >= 0) cap_rate = atof(r); }
    const char *a = std::getenv("ROGUESQ_STDERR_ASYNC_AT"); const int at = (a && *a) ? std::atoi(a) : 0;
    if (at > 0) std::thread([at] { std::this_thread::sleep_for(std::chrono::seconds(at)); switch_on(); }).detach();
    else switch_on();
    // positive control for the crash path through the pipe: ROGUESQ_TEST_CRASH_AT=<s> writes to a null pointer at <s> s
    const char *c = std::getenv("ROGUESQ_TEST_CRASH_AT"); const int ct = (c && *c) ? std::atoi(c) : 0;
    if (ct > 0) std::thread([ct] { std::this_thread::sleep_for(std::chrono::seconds(ct)); fprintf(stderr, "[stderr-async] test crash now\n"); *(volatile int *)nullptr = 1; }).detach();
}
}
extern "C" void rs64_stderr_async_restore() { // async-signal tolerant: atomics, ioctl, usleep, dup2 only
    using namespace s6979se;
    if (!on.exchange(0)) return;
    for (int i = 0; i < 300; i++) { int n = 0; ioctl(rd, FIONREAD, &n); if (n == 0 && queued.load() == 0) break; usleep(1000); }
    dup2(orig, STDERR_FILENO);
}
#else
extern "C" void rs64_stderr_async_restore() {}
#endif
// s7354 class AE positive control: ROGUESQ_S7354_RACE_CTL=1 plants a deliberate unsynchronised write/write race on a plain
// static between two host threads, so a ThreadSanitizer run (tools/build_tsan.sh) proves in the same run that it reports.
static int s7354_race_ctl_var;
static void s7354_race_ctl_start() {
    const char* e = std::getenv("ROGUESQ_S7354_RACE_CTL"); if (!e || *e != '1') return;
    std::thread([] { for (int i = 0; i < 100000; i++) s7354_race_ctl_var++; }).detach();
    std::thread([] { for (int i = 0; i < 100000; i++) s7354_race_ctl_var++; }).detach();
    std::fprintf(stderr, "[s7354] race control armed\n");
}
// s7382 class AX: host thread QoS / priority census, runtime half. ROGUESQ_S7382_QOS=1 (default off) starts a sampler that at
// each second listed in ROGUESQ_S7382_QOS_AT (default 30,60,...,240) prints one "[s7382] thr" row per thread of the process:
// mach thread id, name, QoS class + relative priority (pthread_get_qos_class_np via pthread_from_mach_thread_np), base and
// current mach priority (THREAD_EXTENDED_INFO), whether a time-constraint (real-time) policy is set, cumulative user+system CPU
// us. tools/s7382_thread_qos_census.py --runtime folds the CPU deltas per interval. P vs E cluster is not observable per thread
// with public API; the QoS tier / base priority is what the scheduler uses to place it. Control ROGUESQ_S7382_QOS_CTL=1 plants
// a thread "s7382-ctl" at QOS_CLASS_BACKGROUND (5 ms spin / 5 ms sleep; BG timer slack stretches the sleep): it must print
// qos=0x09 pri=4, and its cpu_us delta must match its own spin wall time (dump ctl_spin_us) within 15%.
#ifdef __APPLE__
static std::atomic<uint64_t> s7382_ctl_spin_us{0}; // control: the ctl thread's own spin wall time, to check the CPU accounting
static void s7382_qos_dump(double t) {
    thread_act_array_t th = nullptr; mach_msg_type_number_t n = 0;
    if (task_threads(mach_task_self(), &th, &n) != KERN_SUCCESS) return;
    for (mach_msg_type_number_t i = 0; i < n; i++) {
        thread_extended_info_data_t xi{}; mach_msg_type_number_t c = THREAD_EXTENDED_INFO_COUNT;
        thread_identifier_info_data_t ii{}; mach_msg_type_number_t ci = THREAD_IDENTIFIER_INFO_COUNT;
        if (thread_info(th[i], THREAD_EXTENDED_INFO, (thread_info_t)&xi, &c) != KERN_SUCCESS) { mach_port_deallocate(mach_task_self(), th[i]); continue; }
        thread_info(th[i], THREAD_IDENTIFIER_INFO, (thread_info_t)&ii, &ci);
        qos_class_t q = QOS_CLASS_UNSPECIFIED; int rp = 0;
        pthread_t pt = pthread_from_mach_thread_np(th[i]); if (pt) pthread_get_qos_class_np(pt, &q, &rp);
        for (char* k = xi.pth_name; *k; k++) if (*k == ' ' || *k == '=') *k = '_'; // one token for the fold
        thread_time_constraint_policy_data_t tc{}; mach_msg_type_number_t ct = THREAD_TIME_CONSTRAINT_POLICY_COUNT; boolean_t def = TRUE;
        thread_policy_get(th[i], THREAD_TIME_CONSTRAINT_POLICY, (thread_policy_t)&tc, &ct, &def);
        std::fprintf(stderr, "[s7382] thr t=%.1f tid=%llu name=%s qos=0x%02x rp=%d pri=%d cur=%d rt=%d cpu_us=%llu run=%d\n", t,
            (unsigned long long)ii.thread_id, xi.pth_name[0] ? xi.pth_name : "-", (unsigned)q, rp, xi.pth_priority, xi.pth_curpri, def ? 0 : 1,
            (unsigned long long)((xi.pth_user_time + xi.pth_system_time) / 1000), xi.pth_run_state);
        mach_port_deallocate(mach_task_self(), th[i]);
    }
    vm_deallocate(mach_task_self(), (vm_address_t)th, n * sizeof(thread_act_t));
    std::fprintf(stderr, "[s7382] dump t=%.1f threads=%u ctl_spin_us=%llu\n", t, (unsigned)n, (unsigned long long)s7382_ctl_spin_us.load());
}
static void s7382_qos_start() {
    const char* e = std::getenv("ROGUESQ_S7382_QOS"); if (!e || *e != '1') return;
    std::vector<int> at; { const char* a = std::getenv("ROGUESQ_S7382_QOS_AT"); std::string s = (a && *a) ? a : "30,60,90,120,150,180,210,240";
        size_t p = 0; while (p < s.size()) { at.push_back(std::atoi(s.c_str() + p)); size_t k = s.find(',', p); if (k == std::string::npos) break; p = k + 1; } }
    const char* c = std::getenv("ROGUESQ_S7382_QOS_CTL");
    if (c && *c == '1') std::thread([] {
        pthread_setname_np("s7382-ctl"); pthread_set_qos_class_self_np(QOS_CLASS_BACKGROUND, 0);
        for (;;) { auto t0 = std::chrono::steady_clock::now(); volatile unsigned x = 0;
            while (std::chrono::steady_clock::now() - t0 < std::chrono::milliseconds(5)) x++;
            s7382_ctl_spin_us.fetch_add((uint64_t)std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - t0).count());
            std::this_thread::sleep_for(std::chrono::milliseconds(5)); } }).detach();
    std::thread([at] {
        pthread_setname_np("s7382-qos");
        const auto t0 = std::chrono::steady_clock::now();
        for (int s : at) { std::this_thread::sleep_until(t0 + std::chrono::seconds(s));
            s7382_qos_dump(std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count()); } }).detach();
    std::fprintf(stderr, "[s7382] qos sampler armed ctl=%d dumps=%zu\n", (c && *c == '1') ? 1 : 0, at.size());
}
#else
static void s7382_qos_start() {}
#endif
// s7355 class AF (async-signal safety of the crash reporter). See the sigaction install in main().
#ifdef __APPLE__
#include <pthread/introspection.h>
static bool rs64_s7355_env_is(const char* k, const char* v) { const char* e = std::getenv(k); return e && std::strcmp(e, v) == 0; }
static int g_rs64_s7355_strsignal = 0; // ROGUESQ_S7355_STRSIGNAL=1 restores the pre-s7355 strsignal() call (negative arm)
static const char* rs64_s7355_signame(int sig) {
    switch (sig) {
        case SIGSEGV: return "Segmentation fault: 11"; case SIGBUS: return "Bus error: 10";
        case SIGABRT: return "Abort trap: 6"; case SIGILL: return "Illegal instruction: 4";
        case SIGFPE: return "Floating point exception: 8"; case SIGTRAP: return "Trace/BPT trap: 5";
        default: return "signal";
    }
}
static constexpr size_t kRs64AltStack = 128 * 1024; // the handler's own frames: fprintf, dladdr, backtrace, ctx-scan
static void rs64_s7355_altstack_here() {
    stack_t cur{};
    if (sigaltstack(nullptr, &cur) == 0 && !(cur.ss_flags & SS_DISABLE)) return; // already has one
    void* p = mmap(nullptr, kRs64AltStack, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
    if (p == MAP_FAILED) return;
    stack_t ss{}; ss.ss_sp = p; ss.ss_size = kRs64AltStack; ss.ss_flags = 0;
    if (sigaltstack(&ss, nullptr) != 0) munmap(p, kRs64AltStack);
}
static void rs64_s7355_altstack_drop() {
    stack_t cur{};
    if (sigaltstack(nullptr, &cur) != 0 || (cur.ss_flags & (SS_DISABLE | SS_ONSTACK)) || cur.ss_size != kRs64AltStack) return;
    stack_t off{}; off.ss_flags = SS_DISABLE;
    if (sigaltstack(&off, nullptr) == 0) munmap(cur.ss_sp, kRs64AltStack);
}
static pthread_introspection_hook_t g_rs64_s7355_prev_hook = nullptr;
static std::atomic<uint64_t> g_rs64_s7355_altN{0};
static void rs64_s7355_thread_hook(unsigned int event, pthread_t thread, void* addr, size_t size) {
    // START and TERMINATE run on the thread itself (pthread/introspection.h), so sigaltstack applies to it.
    if (event == PTHREAD_INTROSPECTION_THREAD_START && thread == pthread_self()) { rs64_s7355_altstack_here(); g_rs64_s7355_altN.fetch_add(1); }
    else if (event == PTHREAD_INTROSPECTION_THREAD_TERMINATE && thread == pthread_self()) rs64_s7355_altstack_drop();
    if (g_rs64_s7355_prev_hook) g_rs64_s7355_prev_hook(event, thread, addr, size);
}
#if defined(__has_feature)
#if __has_feature(thread_sanitizer)
#define RS64_TSAN_BUILD 1
#endif
#endif
static void rs64_s7355_altstack_install() {
#ifdef RS64_TSAN_BUILD
    // s7366: under ThreadSanitizer the TERMINATE callout runs after TSan has torn the thread's state down; the
    // instrumented hook then trips "CHECK failed: thr->slot != 0" and the next pthread_create waits forever (game hangs in
    // create_gfx / SDL_InitAudio). TSan installs its own signal handling, so the TSan arm skips the hook.
    fprintf(stderr, "[s7355] sigaltstack hook skipped: ThreadSanitizer build (s7366)\n");
    return;
#endif
    rs64_s7355_altstack_here(); // main thread
    g_rs64_s7355_prev_hook = pthread_introspection_hook_install(rs64_s7355_thread_hook); // every thread created later
    fprintf(stderr, "[s7355] sigaltstack on: %zu KB per thread (main + introspection hook); ROGUESQ_ALTSTACK=0 disables\n",
        kRs64AltStack / 1024);
}
extern "C" void _malloc_fork_prepare(void); // libsystem_malloc: takes every malloc zone lock (as fork() does)
__attribute__((noinline)) static int rs64_s7355_overflow(int n) { volatile char buf[4096]; buf[0] = (char)n; return rs64_s7355_overflow(n + 1) + buf[0]; }
// Same-run positive controls for the crash reporter (both off by default):
//  ROGUESQ_TEST_STACK_OVERFLOW_AT=<s>  a host thread recurses until its stack overflows at <s> s
//  ROGUESQ_TEST_CRASH_MALLOC_AT=<s>    a host thread takes the malloc zone locks, then writes to a null pointer at <s> s
// Either must yield a "[CRASH] caught signal" report; with ROGUESQ_ALTSTACK=0 / ROGUESQ_S7355_STRSIGNAL=1 they did not.
static void rs64_s7355_test_triggers() {
    g_rs64_s7355_strsignal = rs64_s7355_env_is("ROGUESQ_S7355_STRSIGNAL", "1");
    const char* a = std::getenv("ROGUESQ_TEST_STACK_OVERFLOW_AT"); const int at = (a && *a) ? std::atoi(a) : 0;
    if (at > 0) std::thread([at] { std::this_thread::sleep_for(std::chrono::seconds(at));
        fprintf(stderr, "[s7355] test stack overflow now (altN=%llu)\n", (unsigned long long)g_rs64_s7355_altN.load());
        rs64_s7355_overflow(0); }).detach();
    const char* m = std::getenv("ROGUESQ_TEST_CRASH_MALLOC_AT"); const int mt = (m && *m) ? std::atoi(m) : 0;
    if (mt > 0) std::thread([mt] { std::this_thread::sleep_for(std::chrono::seconds(mt));
        fprintf(stderr, "[s7355] test crash with malloc locks held now\n");
        _malloc_fork_prepare(); *(volatile int*)nullptr = 1; }).detach();
}
#endif
// s7427 class CJ: runtime half of tools/s7427_env_policy_order.py. ROGUESQ_S7427_PLANT=1 = positive control: a function-local
// static latch of a policy var (ROGUESQ_OSMEM_MB) read before the policy; the env trace must list it.
extern "C" void rs64_s7427_policy_done();
extern "C" void rs64_s7427_policy_begin();
extern "C" int rs64_s7427_tg_fix_reinit();
extern "C" int rs64_g5b_tg_fix;
static __attribute__((noinline)) int s7427_plant_latch() { static const int v = [] { const char* e = std::getenv("ROGUESQ_OSMEM_MB"); return (e && *e) ? 1 : 0; }(); return v; }  // s7730
// s7467 class DW: planted positive control for the ASan+UBSan arm (tools/build_asan.sh). ROGUESQ_S7467_ASAN_PLANT=1 does
// one 1-byte heap over-read (ASan heap-buffer-overflow) and one signed-int overflow (UBSan) at boot. Compiled only into a
// sanitizer build (the over-read would be plain UB elsewhere); a recoverable build (-fsanitize-recover) keeps running after.
#if defined(__has_feature)
#  if __has_feature(address_sanitizer)
#    define RS64_S7467_ASAN 1
#  endif
#endif
// s7468 class DY: ucode-TU plant (src/rsp/factor5_ucode_nmac.cpp), proves the ucode TUs are ASan-instrumented.
extern "C" void rs64_s7468_ucode_plant(unsigned idx);
static void rs64_s7467_asan_plant() {
    const char* p = std::getenv("ROGUESQ_S7467_ASAN_PLANT"); if (!p || *p != '1') return;
#if defined(RS64_S7467_ASAN)
    char* volatile b = static_cast<char*>(std::malloc(16));
    volatile char c = b[16];                     // heap-buffer-overflow READ of size 1, 0 bytes past a 16-byte region
    volatile int big = 0x7FFFFFFF; volatile int one = 1;
    volatile int ov = big + one;                 // UBSan signed-integer-overflow
    std::free(b);
    std::fprintf(stderr, "[s7467] asan plant fired c=%d ov=%d\n", (int)c, (int)ov);
#else
    std::fprintf(stderr, "[s7467] asan plant requested but this build has no ASan: skipped\n");
#endif
}

extern "C" void rs64_settings_apply(int argc, char** argv);  // s7663 src/main/rs64_settings.cpp
int main(int argc, char* argv[]) {
    rs64_settings_apply(argc, argv);  // s7663: settings.txt / --preset; re-execs (same pid) when it sets anything
    rs64_s7467_asan_plant();
#if defined(RS64_S7467_ASAN)
    { const char* p = std::getenv("ROGUESQ_S7468_UCODE_PLANT"); if (p && *p == '1') rs64_s7468_ucode_plant(0x1000); }
#endif
    { const char* p = std::getenv("ROGUESQ_S7427_PLANT"); if (p && *p == '1') std::fprintf(stderr, "[s7427] plant latch=%d\n", s7427_plant_latch()); }
    s7354_race_ctl_start();
    s7382_qos_start();
#if !defined(_WIN32)
    s6979se::init(); std::atexit([] { rs64_stderr_async_restore(); }); std::at_quick_exit([] { rs64_stderr_async_restore(); });
#endif
    rs64_s7427_policy_begin();
    // s6989 G1e: ROGUESQ_QOS_ALL=1 = one owner knob for the five QoS opt-ins (s6975-s6988). Each stays individually
    // overridable (=0 wins; setenv overwrite=0). GFX_QOS is read by a file-scope static in events.cpp before main, so that
    // reader checks QOS_ALL itself; the other four are read lazily on their threads, after this.
    { const char* e = std::getenv("ROGUESQ_QOS_ALL"); if (e && *e == '1') {
        for (const char* n : {"ROGUESQ_GFX_QOS", "ROGUESQ_GUEST_QOS", "ROGUESQ_PRESENT_QOS", "ROGUESQ_WL_QOS", "ROGUESQ_UPLOAD_QOS"}) setenv(n, "1", 0);
        std::fprintf(stderr, "[s6989] QOS_ALL gfx=%s guest=%s present=%s wl=%s upload=%s\n", std::getenv("ROGUESQ_GFX_QOS"), std::getenv("ROGUESQ_GUEST_QOS"),
            std::getenv("ROGUESQ_PRESENT_QOS"), std::getenv("ROGUESQ_WL_QOS"), std::getenv("ROGUESQ_UPLOAD_QOS")); } }
    rs64_s7358_sanitize_env();
    rs64_g1d_apply_aspect_policy();
    rs64_g1c_apply_dd_policy();

    // The drain-loop tick is a port-only injection; keep the retail-shaped
    // path as the default while retaining an explicit rollback arm.
    rs64_m5_apply_drain_tick_policy();
    // s7427 class CJ: static-init latches of policy vars re-read after the policy (see rs64_s7427_tg_fix_reinit).
    { const int pre = rs64_s7427_tg_fix_reinit();
      if (pre != rs64_g5b_tg_fix) std::fprintf(stderr, "[s7427] g5b_tg_fix %d -> %d (post-policy DRAW_DISTANCE)\n", pre, rs64_g5b_tg_fix); }
    rs64_s7427_policy_done();

#ifdef _WIN32
    // Log PE base so we can resolve absolute addresses from SEH logs to RVAs
    // (RVA = abs_addr - pe_base). Logged once on startup; helps with the
    // cinematic-loop AV diagnostics.
    HMODULE hSelf = GetModuleHandleW(NULL);
    fprintf(stderr, "[main] PE base=%p\n", (void*)hSelf);
    fflush(stderr);
#endif

    // RT64's RT64_LOG_PRINTF macro (debug builds) writes to GlobalLogFile via
    // unchecked fprintf + fflush. Pristine RT64 expects RT64::Application::start
    // to open it (we bypass Application), so without redirection the pointer
    // stays NULL and any RT64 debug-log call asserts in the CRT.
    //
    // Routing to stderr works but RT64 calls these macros at high rate (every
    // fullSync), and the per-call fflush starves the SDL message pump → game
    // window goes "Not Responding". Send writes to NUL instead — same effect
    // as the fork's `if(false) fprintf` cruft, but stays in our repo.
#ifdef _WIN32
    const char* null_dev = "NUL";
#else
    const char* null_dev = "/dev/null";
#endif
    if (FILE *nul = fopen(null_dev, "w")) {
        RT64::GlobalLogFile = nul;
    } else {
        RT64::GlobalLogFile = stderr;  // last-resort fallback
    }
    // Hardware-breakpoint watchdog on rdram+0x3CBC4 (where a corruption was
    // first observed). Useful for tracing the writer when investigating the
    // bug; emits a stack-traced [hwbp-hit] line for every write to the
    // watched address. Default off — set ROGUESQ_HWBP=1 to enable, or just
    // ROGUESQ_HWBP_ADDR=<offset> to enable + watch a different address.
    {
        const char *e = std::getenv("ROGUESQ_HWBP");
        const char *e_addr = std::getenv("ROGUESQ_HWBP_ADDR");
        bool flag_enabled = (e && *e && *e != '0');
        // ADDR enables the watchdog if it parses to a non-zero number — accepts
        // "0x470", "1136", etc. Don't test *e_addr against '0' (broken for "0x...").
        bool addr_enabled = false;
        if (e_addr && *e_addr) {
            unsigned long v = std::strtoul(e_addr, nullptr, 0);
            if (v != 0) addr_enabled = true;
        }
        if (flag_enabled || addr_enabled) {
            fprintf(stderr, "[hwbp] watchdog enabled (ROGUESQ_HWBP=%s ROGUESQ_HWBP_ADDR=%s)\n",
                    e ? e : "(unset)", e_addr ? e_addr : "(unset, defaults to 0x3CBC4)");
            fflush(stderr);
            start_memwp_watchdog();
        }
    }

    start_b50_poller();
    start_state_poller();
    start_level_poller();
    start_m5_exact_route_poller();
    start_phase_poller();
    start_m5_voice_slot_poller();
    {
        const char* e = std::getenv("ROGUESQ_LOG_FS_SLOT");
        if (e && *e && *e != '0') {
            fprintf(stderr, "[fs-slot] poller enabled (ROGUESQ_LOG_FS_SLOT=%s addr=%s)\n",
                    e, getenv("ROGUESQ_FS_SLOT_ADDR") ? getenv("ROGUESQ_FS_SLOT_ADDR")
                                                      : "0x76DF60");
            fflush(stderr);
            start_fs_slot_poller();
        }
    }

    {
        const char* e = std::getenv("ROGUESQ_LOG_FL_ZERO_WATCH");
        if (e && *e && *e != '0') {
            fprintf(stderr, "[fl-zero-poll] poller enabled (ROGUESQ_LOG_FL_ZERO_WATCH=%s addr=%s)\n",
                    e, getenv("ROGUESQ_FL_ZERO_ADDR") ? getenv("ROGUESQ_FL_ZERO_ADDR")
                                                      : "0x1F3CC0");
            fflush(stderr);
            start_fl_zero_poller();
        }
    }

    {
        const char* e = std::getenv("ROGUESQ_LOG_VTX_WRITE_FAULT");
        if (e && *e && *e != '0') {
            fprintf(stderr, "[vtx-write-fault] watcher enabled\n");
            fflush(stderr);
            start_vtx_write_fault_watch();
        }
    }

    {
        const char* e = std::getenv("ROGUESQ_LOG_M5_HOST_WRITE_FAULT");
        if (e && *e && *e != '0') {
            fprintf(stderr, "[m5-host-write-fault] watcher enabled\n");
            fflush(stderr);
            start_m5_host_write_fault_watch();
        }
    }

    {
        const char* e = std::getenv("ROGUESQ_LOG_M5_TASK_WRITE_FAULT");
        if (e && *e && *e != '0') {
            fprintf(stderr, "[m5-task-write-fault] watcher enabled\n");
            fflush(stderr);
            start_m5_task_write_fault_watch();
        }
    }

#if defined(__APPLE__) && defined(__aarch64__)
    // Must run before the sigaction() install below and outside any signal
    // context -- see rs64_build_local_symbol_table's own comment.
    rs64_build_local_symbol_table();
#endif

#ifdef _WIN32
    SetUnhandledExceptionFilter(crash_handler);
    signal(SIGABRT, [](int){
        rs64_stderr_async_restore();
        fprintf(stderr, "[ABORT] caught SIGABRT, dumping stack:\n");
        void* frames[32];
        USHORT count = RtlCaptureStackBackTrace(0, 32, frames, nullptr);
        print_stack_with_symbols(frames, count);
        // No EXCEPTION_POINTERS on the abort path — passing nullptr makes
        // VS open the dump without the "unhandled exception" dialog.
        write_minidump_safe(nullptr);
        _Exit(3);
    });
    // Route CRT debug asserts to stderr instead of the blocking dialog.
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(_CRT_ASSERT, _CRTDBG_FILE_STDERR);
    _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(_CRT_ERROR, _CRTDBG_FILE_STDERR);
    // Hook fires BEFORE abort() runs — gives us a chance to dump the stack
    // for "vector subscript out of range" and similar STL bounds checks.
    _CrtSetReportHook([](int reportType, char* message, int*) -> int {
        fprintf(stderr, "[CRT_REPORT type=%d] %s\n", reportType,
            message ? message : "(null)");
        void* frames[48];
        USHORT count = RtlCaptureStackBackTrace(0, 48, frames, nullptr);
        HMODULE base = GetModuleHandleW(nullptr);
        for (USHORT i = 0; i < count; i++) {
            uintptr_t rva = (uintptr_t)frames[i] - (uintptr_t)base;
            fprintf(stderr, "  [%2u] 0x%llX  rva 0x%llX\n", (unsigned)i,
                (unsigned long long)(uintptr_t)frames[i],
                (unsigned long long)rva);
        }
        fflush(stderr);
        // Return 1 to SUPPRESS the abort. STL bounds-check assertions ("vector
        // subscript out of range") fire when a Factor5 ucode handler indexes
        // past a vector limit due to state we can't fully replicate yet. The
        // resulting abort kills the game even though continuing with whatever
        // garbage the out-of-bounds read returned often lets play continue.
        // Trade-off: occasional visual glitches over a hard crash. Print first.
        return 1;
    });
    // MSVC debug iterators call _invalid_parameter on bounds-check failure
    // (e.g. "vector subscript out of range"). Default handler aborts silently;
    // ours prints a stack trace first.
    _set_invalid_parameter_handler([](const wchar_t* expr, const wchar_t* func,
                                       const wchar_t* file, unsigned int line,
                                       uintptr_t) {
        fprintf(stderr, "[INVALID_PARAM] expr=%ls func=%ls file=%ls:%u\n",
            expr ? expr : L"(null)", func ? func : L"(null)",
            file ? file : L"(null)", line);
        void* frames[48];
        USHORT count = RtlCaptureStackBackTrace(0, 48, frames, nullptr);
        HMODULE base = GetModuleHandleW(nullptr);
        for (USHORT i = 0; i < count; i++) {
            uintptr_t rva = (uintptr_t)frames[i] - (uintptr_t)base;
            fprintf(stderr, "  [%2u] 0x%llX  rva 0x%llX\n", (unsigned)i,
                (unsigned long long)(uintptr_t)frames[i],
                (unsigned long long)rva);
        }
        fflush(stderr);
        _Exit(4);
    });
#else
    {
        // s7355 class AF: the crash report must survive (a) a crash taken inside malloc/free (strsignal() aborts on the
        // held malloc lock, measured tools/s7355_sighandler_ctl.cpp, so the whole report was lost) and (b) a stack
        // overflow (no sigaltstack: the kernel cannot build the handler frame and kills the process silently).
#ifdef __APPLE__
        (void)wbw_on(); // pre-warm its getenv/static-guard init outside signal context
        if (!rs64_s7355_env_is("ROGUESQ_ALTSTACK", "0")) rs64_s7355_altstack_install();
        rs64_s7355_test_triggers();
#endif
        struct sigaction sa {};
        // s646: no SA_RESETHAND — [fl-zero-fault] mprotect watch must survive
        // multiple recoverable write faults. Real crashes re-raise with
        // SIG_DFL below so we still terminate.
        sa.sa_flags = SA_SIGINFO | SA_ONSTACK; // s7355: SA_ONSTACK is a no-op on threads without an altstack
        sigemptyset(&sa.sa_mask);
        sa.sa_sigaction = [](int sig, siginfo_t* info, void* ucontext_raw) {
            if (sig == SIGSEGV || sig == SIGBUS) {
                if (wbw_try_handle_fault(info, ucontext_raw)) {
                    return;
                }
            }
            if (sig == SIGSEGV || sig == SIGBUS) {
                if (m5_host_fault_try_handle(info, ucontext_raw)) {
                    return;
                }
            }
            if (sig == SIGSEGV || sig == SIGBUS) {
                if (m5_task_fault_try_handle(info, ucontext_raw)) {
                    return;
                }
            }
            if (sig == SIGSEGV || sig == SIGBUS) {
                if (vtx_fault_try_handle_fault(info, ucontext_raw)) {
                    return;
                }
            }
            // s646/s647: freelist page-fault watch (PROT_READ trap). Recoverable.
            // (s647: SIGTRAP/SS path REFUTED — do not re-add.)
            if (sig == SIGSEGV || sig == SIGBUS) {
                if (fl_zero_try_handle_fault(info, ucontext_raw)) {
                    return;
                }
            }
            rs64_stderr_async_restore(); // s6979: crash text goes straight to the original fd
            fprintf(stderr, "[CRASH] caught signal %d (%s), dumping stack:\n",
#ifdef __APPLE__
                sig, g_rs64_s7355_strsignal ? strsignal(sig) : rs64_s7355_signame(sig)); // s7355: no strsignal (mallocs)
#else
                sig, strsignal(sig));
#endif
            // s194: dump siginfo + the ARM64 register file at fault time --
            // SA_SIGINFO already gave us these two params, previously
            // discarded. si_addr/__far is the exact faulting virtual address;
            // x0-x28 let us identify which register held the bad pointer
            // directly, without disassembling the crashing instruction.
            if (info) {
                fprintf(stderr, "[CRASH][siginfo] si_addr=%p si_code=%d si_errno=%d\n",
                    info->si_addr, info->si_code, info->si_errno);
            }
#if defined(__APPLE__) && defined(__aarch64__)
            if (ucontext_raw) {
                ucontext_t* uc = static_cast<ucontext_t*>(ucontext_raw);
                if (uc->uc_mcontext) {
                    const auto& ss = uc->uc_mcontext->__ss;
                    const auto& es = uc->uc_mcontext->__es;
                    fprintf(stderr,
                        "[CRASH][mcontext] pc=0x%llx far=0x%llx esr=0x%x exception=0x%x\n",
                        (unsigned long long)ss.__pc, (unsigned long long)es.__far,
                        (unsigned)es.__esr, (unsigned)es.__exception);
                    for (int i = 0; i < 29; i++) {
                        fprintf(stderr, "[CRASH][mcontext] x%-2d=0x%016llx\n",
                            i, (unsigned long long)ss.__x[i]);
                    }
                    fprintf(stderr,
                        "[CRASH][mcontext] fp=0x%016llx lr=0x%016llx sp=0x%016llx cpsr=0x%08x\n",
                        (unsigned long long)ss.__fp, (unsigned long long)ss.__lr,
                        (unsigned long long)ss.__sp, (unsigned)ss.__cpsr);
                    // s4882: name the zero-extended guest register. The faulting
                    // address is rdram + 0x80000000 + (u32 guest), so a ctx slot
                    // holding a ZERO-extended 0x8xxxxxxx value is the writer's
                    // victim. Scan this thread's stack for recomp_context-shaped
                    // blocks (r0==0) and print every slot that matches far.
                    {
                        const uintptr_t stk_top = (uintptr_t)pthread_get_stackaddr_np(pthread_self());
                        // s4882b: x5 sat 0x170 BELOW sp in the first capture, so start
                        // below sp (dead frames) -- the s4882a scan from sp found 0 hits.
                        const uintptr_t lo = ((uintptr_t)ss.__sp - 0x2000) & ~(uintptr_t)7;
                        // s7355: clamp to the thread's mapped stack. After a stack overflow sp sits on the guard page, so
                        // sp-0x2000 faulted inside the handler (signal blocked -> the process hung with no report).
                        const uintptr_t stk_lo = stk_top - (uintptr_t)pthread_get_stacksize_np(pthread_self());
                        const uintptr_t lo_c = lo < stk_lo ? stk_lo : lo;
                        const uint64_t far_ = (uint64_t)es.__far;
                        int hits = 0;
                        for (uintptr_t p = lo_c; p + 32 * 8 <= stk_top && p < lo + 0x40000 && hits < 8; p += 8) {
                            const volatile uint64_t* c = (const volatile uint64_t*)p;
                            if (c[0] != 0) continue;
                            for (int r = 1; r < 32; r++) {
                                const uint64_t v = c[r];
                                if ((v >> 32) == 0 && (uint32_t)v >= 0x80000000u &&
                                    (uint32_t)(far_ - v) - 0x80000000u < 0x10u) {
                                    fprintf(stderr, "[CRASH][ctx-scan] ctx=0x%llx r%d=0x%llx (stack+0x%llx)\n",
                                        (unsigned long long)p, r, (unsigned long long)v,
                                        (unsigned long long)(p - lo));
                                    for (int q = 1; q < 32; q++)
                                        fprintf(stderr, "[CRASH][ctx-scan]   r%-2d=0x%016llx\n", q, (unsigned long long)c[q]);
                                    hits++;
                                    break;
                                }
                            }
                        }
                        fprintf(stderr, "[CRASH][ctx-scan] hits=%d\n", hits);
                    }
                    // s206: symbolize the raw faulting pc directly via dladdr,
                    // bypassing backtrace()'s frame-pointer walk entirely. s194/
                    // s199 showed backtrace_symbols_fd duplicating "processSceneNode
                    // + 8772" (an lr value) at both the crashing frame and its
                    // caller's frame -- consistent with pc landing in a leaf
                    // function that never established its own frame record, which
                    // a fp-chain walker can't see past. dladdr looks up pc's
                    // enclosing symbol from the same Mach-O symbol table
                    // independent of any frame chain, so it resolves correctly
                    // even for a frameless leaf.
                    // s480 (item -310 fix): try our own local+exported symbol
                    // table FIRST -- it covers internal-linkage ("t") symbols
                    // dladdr() can't see, closing the exact misattribution
                    // gap item -310 found after heapFreeListDequeue. Fall
                    // back to dladdr() only if the table is empty (nm failed
                    // at startup) or somehow has no entry below pc.
                    const RS64LocalSymbol* localSym = rs64_lookup_local_symbol((uint64_t)ss.__pc);
                    Dl_info dli{};
                    if (localSym) {
                        fprintf(stderr,
                            "[CRASH][pc-symbol] pc=0x%llx sym=%s+%llu (local-symtab)\n",
                            (unsigned long long)ss.__pc, localSym->name.c_str(),
                            (unsigned long long)((uint64_t)ss.__pc - localSym->addr));
                    } else if (dladdr((void*)(uintptr_t)ss.__pc, &dli) && dli.dli_sname) {
                        fprintf(stderr,
                            "[CRASH][pc-symbol] pc=0x%llx sym=%s+%lld base=%p (dladdr-fallback)\n",
                            (unsigned long long)ss.__pc, dli.dli_sname,
                            (long long)((uintptr_t)ss.__pc - (uintptr_t)dli.dli_saddr),
                            dli.dli_fbase);
                    } else {
                        fprintf(stderr,
                            "[CRASH][pc-symbol] pc=0x%llx sym=<unresolved>\n",
                            (unsigned long long)ss.__pc);
                    }
                }
            }
            // s265: last guest MIPS instruction address stamped by
            // submitSceneNodeRender's breadcrumb (see recomp.h /
            // fixup_game_funcs.py). 0 means the crash is not inside that
            // function's instrumented range (or it never ran this soak).
            fprintf(stderr, "[CRASH][last-guest-pc] pc=0x%08x\n", g_rs64_last_guest_pc);
#else
            (void)ucontext_raw;
#endif
            // s171: snapshot of [vi-fs-decision] state at crash time — tests
            // whether the s169/s170 runtime-scheduler SIGSEGV is adjacent to
            // a stall-clear FIRE event (H1) or independent of stall state (H2).
            // decisionsSinceFire small (single digits) => H1; large/never => H2.
            uint64_t decisionN = 0, lastFireDecisionN = 0;
            int lastFireWasStalled = 0, stalledNow = 0;
            rs64_get_vifs_crash_snapshot(&decisionN, &lastFireDecisionN, &lastFireWasStalled, &stalledNow);
            fprintf(stderr,
                "[CRASH][vifs-snapshot] decisionN=%llu lastFireDecisionN=%llu "
                "decisionsSinceFire=%llu lastFireWasStalled=%d stalledNow=%d\n",
                (unsigned long long)decisionN, (unsigned long long)lastFireDecisionN,
                (unsigned long long)(decisionN - lastFireDecisionN), lastFireWasStalled, stalledNow);
            void* frames[64];
            int count = backtrace(frames, 64);
            backtrace_symbols_fd(frames, count, STDERR_FILENO);
            fflush(stderr);
            // Without SA_RESETHAND, raise(sig) would recurse into this handler.
            signal(sig, SIG_DFL);
            raise(sig);
        };
        sigaction(SIGSEGV, &sa, nullptr);
        sigaction(SIGBUS, &sa, nullptr);
        sigaction(SIGABRT, &sa, nullptr);
    }
#endif
#ifndef _WIN32
    rs64_s7594_install();
#endif

    rs64_register_overlays();

    // s7575 positive control for the do_break witness: ROGUESQ_S7575_BREAK_CTL=1 calls do_break once at startup
    // (after the crash handler is installed) so the [do_break] line + [CRASH] backtrace must land in the log.
    if (const char* e = std::getenv("ROGUESQ_S7575_BREAK_CTL"); e && e[0] == '1') {
        do_break(0x80054744u);
    }

    // Use the working directory as the config/data path (portable mode).
    // ROGUESQ s7596 class FS (FS-2): the throwing current_path() aborts boot when getcwd fails (the launch folder was
    // deleted or made unsearchable under a running shell). Fall back to "." (relative paths still resolve).
    std::filesystem::path rs_cwd;
    {
        std::error_code cwd_ec;
        rs_cwd = std::filesystem::current_path(cwd_ec);
        if (cwd_ec || rs_cwd.empty()) {
            fprintf(stderr, "[s7596-io] current_path failed: %s; using \".\"\n", cwd_ec.message().c_str());
            rs_cwd = ".";
        }
    }
    recomp::register_config_path(rs_cwd);

    for (const auto& game : supported_games) {
        recomp::register_game(game);
    }

    // Check if the ROM is already stored; if not, try to import it from common filenames.
    recomp::check_all_stored_roms();
    std::u8string rs_game_id = supported_games[0].game_id;
    if (!recomp::is_rom_valid(rs_game_id)) {
        static const char* rom_candidates[] = {
            "rogue_squadron.z64",
            "rogue squadron.z64",
            "RogueSquadron.z64",
            "rs64.z64",
        };
        for (const char* name : rom_candidates) {
            std::filesystem::path p = rs_cwd / name;
            auto result = recomp::select_rom(p, rs_game_id);
            if (result == recomp::RomValidationError::Good) {
                fprintf(stderr, "[ROM] Imported %s\n", name);
                break;
            }
        }
    }
    // Re-check after any import attempt so is_rom_valid reflects the new file.
    recomp::check_all_stored_roms();
    if (!recomp::is_rom_valid(rs_game_id)) {
        fprintf(stderr,
            "[ROM] Place your Rogue Squadron (USA v1.0) ROM named\n"
            "      'rogue_squadron.z64' next to the executable and restart.\n");
    }

    recomp::start(recomp::Configuration{
        .project_version = { 0, 1, 0 },
        .window_handle = {},
        .rsp_callbacks = {
            .get_rsp_microcode = get_rsp_microcode,
        },
        .renderer_callbacks = {
            .create_render_context = recomp::create_render_context,
        },
        .audio_callbacks = {
            .queue_samples        = queue_samples,
            .get_frames_remaining = get_frames_remaining,
            .set_frequency        = set_frequency,
        },
        .input_callbacks = {
            .poll_input                = poll_input,
            .get_input                 = get_n64_input,
            .set_rumble                = set_rumble,
            .get_connected_device_info = get_connected_device_info,
        },
        .gfx_callbacks = {
            .create_gfx    = create_gfx,
            .create_window = create_window,
            .update_gfx    = update_gfx,
        },
        .events_callbacks = {
            .vi_callback = nullptr,
            .gfx_init_callback = []() {
                std::u8string game_id = u8"rs64.n64.us.1.0";
                if (recomp::is_rom_valid(game_id)) {
                    recomp::start_game(game_id);
                }
            },
        },
        .error_handling_callbacks = {
            .message_box = [](const char* msg) { fprintf(stderr, "[Error] %s\n", msg); },
        },
        .threads_callbacks = {
            .get_game_thread_name = get_game_thread_name,
        },
        .message_queue_control = {},
    });

    return EXIT_SUCCESS;
}
