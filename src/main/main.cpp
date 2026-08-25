#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <csignal>
#include <vector>
#include <mutex>
#include <cinttypes>
#include <filesystem>
#include <thread>
#include <chrono>
#include <atomic>

#include "ultramodern/ultra64.h"
#include "ultramodern/ultramodern.hpp"
#include "ultramodern/events.hpp"
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
extern "C" uint32_t rs64_vi_committed_width();
extern "C" uint32_t rs64_vi_committed_origin();
extern "C" void rs64_audio_route_set(const char* arm, uint32_t phase,
                                       uint32_t width, uint32_t origin,
                                       uint32_t ordinal, uint32_t row,
                                       int exit_reason);
extern "C" void rs64_audio_join_image_stage(const char* arm,
                                               uint32_t ordinal, uint32_t row,
                                               uint32_t phase, uint32_t width,
                                               uint32_t origin, uint32_t stage,
                                               uint32_t dest, uint32_t len,
                                               uint32_t fnv, uint32_t nonzero,
                                               uint32_t dest_valid);
extern "C" void rs64_audio_join_image_complete(const char* arm,
                                                  uint32_t ordinal, uint32_t row,
                                                  uint32_t phase, uint32_t width,
                                                  uint32_t origin);
extern "C" bool rs64_audio_current_route_snapshot(
    uint32_t* phase, uint32_t* width, uint32_t* origin, uint32_t* ordinal,
    uint32_t* row, int* exit_reason, const char** arm);
extern "C" uint64_t rs64_audio_join_m5_event(
    const char* kind, uint32_t site, uint32_t active, const char* arm,
    uint32_t phase, uint32_t width, uint32_t origin, uint32_t ordinal,
    uint32_t row, uint32_t idx, uint32_t dest, uint32_t value0,
    uint32_t value1, uint32_t value2, uint32_t value3);

// Wrapper: captures rdram into the watchdog global on first call so the
// hwbp/poll diagnostic threads can attach. Forwards to the real entrypoint.
extern "C" volatile uint8_t* volatile g_recomp_rdram_for_wp_raw;
extern "C" void rs64_entrypoint_with_rdram_capture(uint8_t* rdram, recomp_context* ctx) {
    g_recomp_rdram_for_wp_raw = rdram;
    recomp_entrypoint(rdram, ctx);
}
// The game's N64 "main" function — renamed to avoid clash with C main()
extern "C" void rs_main(uint8_t* rdram, recomp_context* ctx);
gpr get_entrypoint_address();

// ---------------------------------------------------------------------------
// RSP microcode dispatch
// ---------------------------------------------------------------------------
extern RspExitReason factor5_ucode(uint8_t* rdram, uint32_t ucode_addr);
extern "C" uint32_t rs64_phase_ord(void);
extern RspExitReason factor5_ucode_b(uint8_t* rdram, uint32_t ucode_addr);
extern "C" void rs64_dpc_defer_begin();
extern "C" void rs64_dpc_reset();
extern "C" void rs64_dpc_defer_end(int commit);
extern "C" void rs64_dpc_get_task_range(uint32_t *first_lo, uint32_t *first_hi,
                                         uint32_t *last_lo, uint32_t *last_hi,
                                         uint32_t *min_lo, uint32_t *max_hi);
extern RspExitReason factor5_boot (uint8_t* rdram, uint32_t ucode_addr);
extern uint8_t dmem[];
extern "C" void rs64_dpc_drain_histogram(uint32_t out[64]);
extern "C" uint32_t rs64_dpc_get_last_fullsync_addr();
extern "C" void rs64_rdp_advance_reset();
extern "C" void rs64_rdp_advance_report(uint32_t task, uint32_t guestDl,
                                          uint32_t guestE9);
extern "C" void rs64_e9prov_aligned(uint32_t task, uint32_t guestDl,
                                      uint32_t guestE9);
extern "C" void rs64_e9prov_task_join_report(uint32_t task);
extern "C" void rs64_e9prov_task_begin(uint32_t task, uint32_t root_dl);
extern "C" void rs64_e9prov_task_end(uint32_t task);
extern "C" void rs64_inline_probe_trigen_stage(uint32_t dl_ptr, uint32_t boot_130,
                                                  uint32_t staged_130, uint32_t skipped_host_130,
                                                  uint32_t boot_ff0, uint32_t staged_ff0,
                                                  uint32_t skipped_host_ff0);
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
static thread_local uint32_t g_rs64_m5_field348_static_callsite = 0;
static thread_local uint32_t g_rs64_m5_pcm_callsite = 0;

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
Rs64PcmWriterState g_rs64_pcm_writer[16];
std::mutex g_rs64_pcm_writer_mutex;
uint32_t g_rs64_pcm_writer_phase_key = 0xFFFFFFFFu;
uint64_t g_rs64_pcm_writer_sequence = 0;
uint32_t g_rs64_pcm_writer_printed[16] = {};
bool g_rs64_pcm_writer_control = false;

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

void rs64_pcm_writer_phase_reset(uint32_t key) {
    if (key == g_rs64_pcm_writer_phase_key) return;
    g_rs64_pcm_writer_phase_key = key;
    std::memset(g_rs64_pcm_writer, 0, sizeof(g_rs64_pcm_writer));
    std::memset(g_rs64_pcm_writer_printed, 0,
                sizeof(g_rs64_pcm_writer_printed));
    g_rs64_pcm_writer_control = false;
}

void rs64_pcm_writer_note(uint32_t phys, uint32_t len, uint32_t pc,
                          uint32_t kind, uint32_t value) {
    if (!rs64_pcm_writer_enabled() || len == 0) return;
    uint32_t phase = 0, width = 0, origin = 0, key = 0;
    if (!rs64_pcm_writer_phase(phase, width, origin, key)) return;
    const uint32_t end = phys + len;
    if (phys >= rs64_pcm_ring_last || end <= rs64_pcm_ring_first) return;

    std::lock_guard<std::mutex> lock(g_rs64_pcm_writer_mutex);
    rs64_pcm_writer_phase_reset(key);
    if (!g_rs64_pcm_writer_control) {
        std::fprintf(stderr,
                     "[pcm-writer-control] phase=%u width=%u origin=0x%06X"
                     " kind=%u phys=0x%06X len=0x%X\n",
                     phase, width, origin, kind, phys, len);
        std::fflush(stderr);
        g_rs64_pcm_writer_control = true;
    }

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
    rs64_pcm_writer_note(addr & 0x007FFFFFu, len, 0u, 2u, 0u);
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

static bool rs64_filter_voice_guest_span_ok(uint32_t base, uint32_t span) {
    const uint32_t segment = base & 0xE0000000u;
    const uint32_t phys = base & 0x1FFFFFFFu;
    const bool rdram_segment = segment == 0x80000000u || segment == 0xA0000000u;
    return rdram_segment && phys <= 0x800000u && span <= 0x800000u - phys;
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
    const uint32_t table = table_used ? ra + 0xD4u + a0 : 0u;
    const bool source_ok = rs64_filter_voice_guest_span_ok(source, 26u);
    const bool output_ok = rs64_filter_voice_guest_span_ok(output, 40u);
    const bool table_ok = !table_used || rs64_filter_voice_guest_span_ok(table, 1u);
    const uint32_t phase = rs64_phase_ord();
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

extern "C" void rs64_filter_voice_call_probe(uint32_t site, uint32_t sp,
                                               uint32_t ra, uint32_t a0,
                                               uint32_t a1, uint32_t a2,
                                               uint32_t a3) {
    rs64_filter_voice_audit_row("call", site, sp, ra, a0, a1, a2, a3);
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
static thread_local uint32_t s_pending_task_data_ptr  = 0;
static thread_local uint32_t s_pending_task_ucode_data = 0;
static thread_local uint32_t s_pending_task_ucode_data_size = 0;

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
};

static thread_local Rs64AudioRouteIdentity g_rs64_audio_identity;
static std::atomic<uint32_t> g_rs64_audio_ordinal{0};
static uint32_t g_rs64_audio_phase_key = 0xFFFFFFFFu;
static uint32_t g_rs64_audio_phase_row = 0;
static thread_local uint32_t g_rs64_audio_break_pc = 0;
static thread_local uint32_t g_rs64_m5_init_voice_caller_pc = 0;
static thread_local uint64_t g_rs64_m5_init_voice_event = 0;
static std::atomic<uint64_t> g_rs64_m5_init_voice_next_event{1};

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
          (vi_width == 512u && vi_origin == 0x006AB400u))) return;

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

static void rs64_audio_route_prepare(const char* arm) {
    g_rs64_audio_identity.valid = false;
    if (!rs64_audio_probe_enabled()) {
        return;
    }
    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    const bool target_phase =
        (width == 1024u && origin == 0x00790400u) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    const uint32_t key = (width << 24) ^ origin;
    if (key != g_rs64_audio_phase_key) {
        g_rs64_audio_phase_key = key;
        g_rs64_audio_phase_row = 0;
    }
    g_rs64_audio_identity = {
        true, arm, phase, width, origin,
        g_rs64_audio_ordinal.fetch_add(1, std::memory_order_relaxed),
        g_rs64_audio_phase_row++
    };
}

static void rs64_audio_hash_dmem(uint32_t addr, uint32_t len,
                                  uint32_t& fnv, uint32_t& nonzero) {
    fnv = 2166136261u;
    nonzero = 0;
    for (uint32_t i = 0; i < len; ++i) {
        const uint8_t b = dmem[((addr + i) & 0xFFFu) ^ 3u];
        fnv = (fnv * 16777619u) ^ b;
        nonzero += b != 0;
    }
}

static void rs64_audio_hash_dmem_dma(uint32_t addr, uint32_t len,
                                     uint32_t& fnv, uint32_t& nonzero) {
    fnv = 2166136261u;
    nonzero = 0;
    for (uint32_t i = 0; i < len; ++i) {
        const uint8_t b = dmem[((addr + (i ^ 3u)) & 0xFFFu) ^ 3u];
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
    if (!((width_n == 1024u && origin == 0x00790400u) ||
          (width_n == 512u && origin == 0x006AB400u))) return;

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
    std::lock_guard<std::mutex> lock(mutex);

    const uint64_t ordinal = store_ordinal++;
    const uint32_t phase = rs64_phase_ord();
    const uint32_t phase_key = (width_n << 24) ^ origin;
    const uint32_t phase_slot = width_n == 1024u ? 0u : 1u;
    const bool overlaps_field348 =
        (phys < spans[0] + 0x180u && phys + len > spans[0]) ||
        (phys < spans[1] + 0x180u && phys + len > spans[1]);
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
        if (printed[i] < 512u || (new_pc && unique_n[i] <= 64u)) {
            std::fprintf(stderr,
                "[field348-writer] ordinal=%llu phase=%u width=%u "
                "origin=0x%06X span=%u phys=0x%06X len=%u pc=0x%08X "
                "value=0x%08X value_fnv=%08X value_nz=%u total=%u unique=%u\n",
                static_cast<unsigned long long>(ordinal), phase, width_n, origin,
                i + 1u, phys, len, pc, logged_value, value_fnv, value_nz,
                total[i], unique_n[i]);
            std::fflush(stderr);
            ++printed[i];
        }
    }
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
        ((phys < 0x179930u && phys + len > 0x1797B0u) ? 2u : 0u);
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
    const bool overlap_2 = len != 0u && phys < 0x179930u && end > 0x1797B0u;
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
    if (stage >= 2) {
        rs64_audio_hash_dmem_dma(dmem_a, len_a, dma_fnv_a, dma_nz_a);
        rs64_audio_join_image_stage(
            route.arm, route.ordinal, route.row, route.phase, route.width,
            route.origin, stage, (dest & 0xFFFFF8u) & 0x007FFFFFu, dest_len,
            dma_fnv_a, dma_nz_a,
            dest_valid ? 1u : 0u);
    }
    std::fprintf(stderr,
        "[audtask-image-stage] arm=%s ordinal=%u row=%u phase=%u width=%u"
        " origin=0x%06X stage=%u r2=0x%03X field348=0x%08X field44=0x%08X"
        " dest=0x%08X dmem_a=0x%03X len_a=0x%X fnv_a=%08X nz_a=%u"
        " dmem_b=0x%03X len_b=0x%X fnv_b=%08X nz_b=%u"
        " field348_fnv=%08X field348_nz=%u field348_valid=%u"
        " dma_fnv_a=%08X dma_nz_a=%u dest_valid=%u dest_fnv=%08X dest_nz=%u\n",
        route.arm, route.ordinal, route.row, route.phase, route.width,
        route.origin, stage, r2, field348, field44, dest, dmem_a, len_a,
        fnv_a, nz_a, dmem_b, len_b, fnv_b, nz_b, field348_fnv,
        field348_nz, field348_valid ? 1u : 0u, dma_fnv_a, dma_nz_a,
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
    g_rs64_audio_identity.valid = false;
}

static RspExitReason musyx_stub_probe(uint8_t* rdram, uint32_t ucode_addr) {
    rs64_audio_route_prepare("musyx_stub");
    const RspExitReason reason = musyx_stub(rdram, ucode_addr);
    rs64_log_audio_return("musyx_stub", reason);
    return reason;
}

static RspExitReason factor5_ucode_b_probe(uint8_t* rdram, uint32_t ucode_addr) {
    g_rs64_audio_break_pc = 0;
    rs64_audio_route_prepare("factor5_ucode_b");
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
static void rs64_dump_ucode(uint8_t* rdram, uint32_t phys) {
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
    uint32_t c130 = ((uint32_t)dmem[0x130 ^ 3] << 24) | ((uint32_t)dmem[0x131 ^ 3] << 16) |
                    ((uint32_t)dmem[0x132 ^ 3] << 8) | (uint32_t)dmem[0x133 ^ 3];
    uint32_t h = 0;
    for (uint32_t a = 0x60; a < 0xE0; ++a) h = h * 31 + dmem[a ^ 3];
    fprintf(stderr, "[rcanary t%d %s] 0x130=0x%08X tblhash=0x%08X\n", task_n, tag, c130, h);
}

// Serializes every LLE gfx task (OSTask pokes + boot + main ucode) against
// the single shared global dmem[]. The old "tasks are serialized (single
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
extern "C" void rs64_dmem_lock()   { g_lle_task_mutex.lock(); }
extern "C" void rs64_dmem_unlock() { g_lle_task_mutex.unlock(); }

static RspExitReason factor5_gfx_runner(uint8_t* rdram, uint32_t ucode_addr) {
    std::lock_guard<std::recursive_mutex> lle_lock(g_lle_task_mutex);
    uint32_t dl_ptr           = s_pending_task_data_ptr;
    uint32_t ucode_data_addr  = s_pending_task_ucode_data;
    uint32_t ucode_data_size  = s_pending_task_ucode_data_size;

    // Mimic SP_BOOT (silicon-level RSP boot ucode): zero DMEM[0..0xFC0] then
    // populate DMEM[0..ucode_data_size]. Leave DMEM[0xFC0..0x1000] alone —
    // that's the OSTask region the boot ucode reads.
    //
    std::memset(dmem, 0, 0xFC0);
    // Always load each task's ucode data from live RDRAM. Before shared-DMEM
    // serialization, a concurrent audio task could overwrite this area while
    // GFX was running; a first-task snapshot only hid that race and could make
    // later phase changes stale. g_lle_task_mutex now models the single RSP.
    if (ucode_data_addr != 0 && ucode_data_size != 0 && ucode_data_size <= 0xFC0) {
        dma_rdram_to_dmem(rdram, 0, ucode_data_addr & 0x00FFFFFF, ucode_data_size - 1);
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
            if (sh2_phys + sh2_size > 0x800000) sh2_size = 0x800000 - sh2_phys;
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
                for (uint32_t k = 0; k < sh2_size; k++) {
                    if ((uint8_t)MEM_B(0, (int64_t)(int32_t)(sh2_phys + k + 0x80000000)) != s_sh2_buf[k]) {
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
            const char* e = std::getenv("ROGUESQ_LOG_SPBOOT");
            s_log = (e && *e && *e != '0') ? 1 : 0;
        }
        if (s_log) {
            static int s_n = 0;
            ++s_n;
            if (s_n <= 4) {
                fprintf(stderr,
                    "[spboot] task #%d ucode_data=0x%08X size=0x%X DMEM[0..0x10]:",
                    s_n, ucode_data_addr, ucode_data_size);
                for (int i = 0; i < 0x10; ++i) {
                    fprintf(stderr, " %02X", dmem[i ^ 3]);
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
    uint32_t embedded_ucode = ((uint32_t)dmem[0xFD0 ^ 3] << 24) | ((uint32_t)dmem[0xFD1 ^ 3] << 16) |
                              ((uint32_t)dmem[0xFD2 ^ 3] << 8) | (uint32_t)dmem[0xFD3 ^ 3];
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

    auto poke_be32 = [](uint32_t off, uint32_t val) {
        for (int i = 0; i < 4; ++i) {
            dmem[(off + i) ^ 3] = (uint8_t)(val >> (24 - 8*i));
        }
    };
    auto peek_be32 = [](uint32_t off) {
        return ((uint32_t)dmem[(off + 0) ^ 3] << 24) |
               ((uint32_t)dmem[(off + 1) ^ 3] << 16) |
               ((uint32_t)dmem[(off + 2) ^ 3] << 8) |
               (uint32_t)dmem[(off + 3) ^ 3];
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
            uint32_t ring_base = ((uint32_t)dmem[0x100 ^ 3] << 24) | ((uint32_t)dmem[0x101 ^ 3] << 16) |
                                 ((uint32_t)dmem[0x102 ^ 3] << 8) | (uint32_t)dmem[0x103 ^ 3];
            poke_be32(0x108, ring_base);
        }
        // Reset the DL-stack-pointer byte. The ucode runs with $18 = 0x100
        // (set by L_1DB0's bootstrap), so $18+0x52 = DMEM[0x152]. Op_0F's
        // L_12C4 handler decrements this by 8 each call and exits the
        // dispatch loop when it goes negative. After task #1 underflows the
        // byte is left negative; subsequent tasks would exit immediately with
        // 0 RDP work emitted. Reset to 0x18 (3 stack entries) at task start.
        dmem[0x152 ^ 3] = 0x18;
        // Resident-segment cache byte (L_1DB0 clears it). Forcing an invalid
        // id (0xFF) to make the loader always reload was tried 2026-07-12 and
        // INCREASED failures — the entry path apparently relies on 0 here.
        dmem[0x153 ^ 3] = 0;

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
                    fprintf(stderr, " %02X", dmem[i ^ 3]);
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
    const uint32_t task_serial = g_rs64_lle_task_n.fetch_add(1, std::memory_order_relaxed) + 1;
    rs64_e9prov_task_begin(task_serial, dl_ptr);
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
    RspExitReason r = factor5_ucode(rdram, ucode_addr);
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
            const char* e = std::getenv("ROGUESQ_LOG_E9_UNIFIED");
            s_e9_unified = (e && *e && *e != '0') ? 1 : 0;
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
extern "C" int rs64_run_lle_gfx(uint8_t* rdram, const OSTask* task) {
    std::lock_guard<std::recursive_mutex> lle_lock(g_lle_task_mutex);
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
            dmem[(off + j) ^ 3] = (uint8_t)(val >> (24 - j * 8));
        }
    };
    poke(0xFC0 + 0x00, (uint32_t)task->t.type);
    poke(0xFC0 + 0x04, (uint32_t)task->t.flags);
    poke(0xFC0 + 0x08, (uint32_t)task->t.ucode_boot);
    poke(0xFC0 + 0x0C, (uint32_t)task->t.ucode_boot_size);
    poke(0xFC0 + 0x10, (uint32_t)task->t.ucode);
    poke(0xFC0 + 0x14, (uint32_t)task->t.ucode_size);
    poke(0xFC0 + 0x18, (uint32_t)task->t.ucode_data);
    poke(0xFC0 + 0x1C, (uint32_t)task->t.ucode_data_size);
    poke(0xFC0 + 0x20, (uint32_t)task->t.dram_stack);
    poke(0xFC0 + 0x24, (uint32_t)task->t.dram_stack_size);
    poke(0xFC0 + 0x28, (uint32_t)task->t.output_buff);
    poke(0xFC0 + 0x2C, (uint32_t)task->t.output_buff_size);
    poke(0xFC0 + 0x30, (uint32_t)task->t.data_ptr);
    poke(0xFC0 + 0x34, (uint32_t)task->t.data_size);
    poke(0xFC0 + 0x38, (uint32_t)task->t.yield_data_ptr);
    poke(0xFC0 + 0x3C, (uint32_t)task->t.yield_data_size);
    fprintf(stderr, "[lle task] flags=0x%X yield_ptr=0x%08X yield_size=0x%X data=0x%08X dsize=0x%X out=0x%08X\n",
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
    case M_AUDTASK:
        g_rs64_audio_break_pc = 0;
        // The image arm is default; set ROGUESQ_AUDIO_UCODE=0 for the stub
        // control used by the incremental audio qualification steps.
        {
            static int s_use_real_audio_ucode = -1;
            if (s_use_real_audio_ucode < 0) {
                const char* e = getenv("ROGUESQ_AUDIO_UCODE");
                s_use_real_audio_ucode = !(e && e[0] == '0');
            }
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
                        s_audtask_n, s_use_real_audio_ucode);
            }
            s_audtask_n++;
            if (s_use_real_audio_ucode) return &factor5_ucode_b_probe;
        }
        return &musyx_stub_probe;
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
static uint32_t audio_sample_rate = 48000;

static void set_frequency(uint32_t freq) {
    if (audio_device) {
        SDL_CloseAudioDevice(audio_device);
        audio_device = 0;
    }
    audio_sample_rate = freq;

    SDL_AudioSpec desired{};
    desired.freq     = (int)freq;
    desired.format   = AUDIO_S16SYS;
    desired.channels = 2;
    desired.samples  = 1024;

    audio_device = SDL_OpenAudioDevice(nullptr, 0, &desired, nullptr, 0);
    if (!audio_device) {
        fprintf(stderr, "[Audio] SDL_OpenAudioDevice failed: %s\n", SDL_GetError());
        return;
    }
    SDL_PauseAudioDevice(audio_device, 0);
}

static void queue_samples(int16_t* samples, size_t num_samples, uint32_t rdram_addr) {
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
    if (audio_device) {
        SDL_QueueAudio(audio_device, samples, (Uint32)(num_samples * sizeof(int16_t)));
    }

    static int s_log_pcm_boundary = -1;
    if (s_log_pcm_boundary < 0) {
        const char* all = getenv("ROGUESQ_LOG_ALL");
        const char* own = getenv("ROGUESQ_LOG_PCM_BOUNDARY");
        const bool all_enabled = all && all[0] && all[0] != '0';
        const bool own_enabled = own && own[0] && own[0] != '0';
        s_log_pcm_boundary = (all_enabled || own_enabled) ? 1 : 0;
    }
    if (s_log_pcm_boundary) {
        const uint32_t width = rs64_vi_committed_width();
        const uint32_t origin = rs64_vi_committed_origin();
        const bool phase_allowed =
            (width == 1024u && origin == 0x00790400u) ||
            (width == 512u && origin == 0x006AB400u);
        static uint32_t s_phase_key = 0xFFFFFFFFu;
        static uint32_t s_phase_n = 0;
        if (phase_allowed) {
            const uint32_t phase_key = (width << 24) ^ origin;
            if (phase_key != s_phase_key) {
                s_phase_key = phase_key;
                s_phase_n = 0;
            }
            const uint32_t n = s_phase_n++;
            const size_t full_byte_count = num_samples * sizeof(int16_t);
            const uint8_t* p = reinterpret_cast<const uint8_t*>(samples);
            uint32_t fnv = 2166136261u;
            uint32_t nonzero = 0;
            for (size_t i = 0; i < full_byte_count; i++) {
                fnv = (fnv * 16777619u) ^ p[i];
                nonzero += p[i] != 0;
            }
            ultramodern::rs64_audio_join_pcm(
                "consumer", rs64_phase_ord(), width, origin, n, rdram_addr,
                static_cast<uint32_t>(num_samples),
                static_cast<uint32_t>(full_byte_count), fnv, nonzero);
            if (n < 40 || (n % 128) == 0) {
                fprintf(stderr,
                    "[pcm-boundary-consumer] n=%u phase=%u width=%u origin=0x%06X"
                    " rdram=0x%08X samples=%zu bytes=%zu fnv=0x%08X nz=%u\n",
                    n, rs64_phase_ord(), width, origin, rdram_addr, num_samples,
                    full_byte_count, fnv, nonzero);
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
    if (!audio_device) return 0;
    Uint32 queued = SDL_GetQueuedAudioSize(audio_device);
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
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
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
    if (n <= 128) {
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
    return (uintptr_t)rdram + (uintptr_t)(slot & 0x7FFFFFu);
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
            if (v > 0 && v < 0x800000u) slot = (uint32_t)v;
        }
        slot &= 0x7FFFFFu;
#ifndef _WIN32
        g_flz_fault_rdram.store(rdram, std::memory_order_release);
        g_flz_fault_slot.store(slot, std::memory_order_relaxed);
        g_flz_fault_enabled.store(1, std::memory_order_release);
#endif
        auto rbyte = [&](uint32_t a) -> uint8_t {
            return rdram[(a & 0x7FFFFF) ^ 3];
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
                if (cf == 0x2u && csz == 0x60u) {
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
                        if (kind[0] == 't' && pf == 0x2u && psz == 0x60u) {
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
                if ((cf == 0x2u && csz == 0x60u) || (cf == 0 && csz == 0)) {
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
        if (const char* e = std::getenv("ROGUESQ_HWBP_ADDR")) {
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

static void poll_input() {
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
        if (e.type == SDL_QUIT) {
            fprintf(stderr, "[main] SDL_QUIT received, exiting\n");
            fflush(stderr);
            exit(EXIT_SUCCESS);
        }
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
            if (!controller) {
                controller = SDL_GameControllerOpen(e.cdevice.which);
            }
        }
        if (e.type == SDL_CONTROLLERDEVICEREMOVED && controller) {
            if (SDL_GameControllerGetJoystick(controller) ==
                SDL_JoystickFromInstanceID(e.cdevice.which)) {
                SDL_GameControllerClose(controller);
                controller = nullptr;
            }
        }
#ifdef _WIN32
        if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_F12) {
            fprintf(stderr, "[F12] manual minidump requested\n");
            fflush(stderr);
            write_minidump_safe(nullptr);
        }
#endif
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
}

static bool get_n64_input(int controller_num, uint16_t* buttons, float* x, float* y) {
    if (controller_num != 0) {
        *buttons = 0; *x = 0.0f; *y = 0.0f;
        return false;
    }

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
    // Z trigger (brake) from left analog trigger axis
    if (controller && SDL_GameControllerGetAxis(controller, SDL_CONTROLLER_AXIS_TRIGGERLEFT) > 16000) {
        btn |= N64_Z_TRIG;
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

    *x = stick_x;
    *y = stick_y;
    *buttons = btn;

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

static void set_rumble(int, bool) {}

static ultramodern::input::connected_device_info_t get_connected_device_info(int controller_num) {
    if (controller_num == 0) {
        return { ultramodern::input::Device::Controller, ultramodern::input::Pak::None };
    }
    return { ultramodern::input::Device::None, ultramodern::input::Pak::None };
}

// ---------------------------------------------------------------------------
// Graphics (SDL2 window creation — rt64 takes over from here)
// ---------------------------------------------------------------------------
ultramodern::gfx_callbacks_t::gfx_data_t create_gfx() {
    SDL_SetHint(SDL_HINT_WINDOWS_DPI_AWARENESS, "permonitorv2");
    SDL_SetHint(SDL_HINT_GAMECONTROLLER_USE_BUTTON_LABELS, "0");
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER | SDL_INIT_AUDIO) != 0) {
        fprintf(stderr, "SDL_Init failed: %s\n", SDL_GetError());
        exit(EXIT_FAILURE);
    }
    return nullptr;
}

// Defined in rt64_render_context.cpp
namespace recomp {
    std::unique_ptr<ultramodern::renderer::RendererContext>
    create_render_context(uint8_t* rdram, ultramodern::renderer::WindowHandle window_handle, bool developer_mode);
}

ultramodern::renderer::WindowHandle create_window(ultramodern::gfx_callbacks_t::gfx_data_t) {
    SDL_Window* sdl_window = SDL_CreateWindow(
        "Star Wars: Rogue Squadron 64 Recompiled",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        640, 480,
        SDL_WINDOW_RESIZABLE | SDL_WINDOW_SHOWN
    );
    if (!sdl_window) {
        fprintf(stderr, "SDL_CreateWindow failed: %s\n", SDL_GetError());
        exit(EXIT_FAILURE);
    }
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

int main(int argc, char* argv[]) {
    (void)argc; (void)argv;

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
    start_phase_poller();
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

#if defined(__APPLE__) && defined(__aarch64__)
    // Must run before the sigaction() install below and outside any signal
    // context -- see rs64_build_local_symbol_table's own comment.
    rs64_build_local_symbol_table();
#endif

#ifdef _WIN32
    SetUnhandledExceptionFilter(crash_handler);
    signal(SIGABRT, [](int){
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
        struct sigaction sa {};
        // s646: no SA_RESETHAND — [fl-zero-fault] mprotect watch must survive
        // multiple recoverable write faults. Real crashes re-raise with
        // SIG_DFL below so we still terminate.
        sa.sa_flags = SA_SIGINFO;
        sigemptyset(&sa.sa_mask);
        sa.sa_sigaction = [](int sig, siginfo_t* info, void* ucontext_raw) {
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
            fprintf(stderr, "[CRASH] caught signal %d (%s), dumping stack:\n",
                sig, strsignal(sig));
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

    rs64_register_overlays();

    // Use the working directory as the config/data path (portable mode).
    recomp::register_config_path(std::filesystem::current_path());

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
            std::filesystem::path p = std::filesystem::current_path() / name;
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
