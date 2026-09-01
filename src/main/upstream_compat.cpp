// Upstream-librecomp gap-filler: libultra _recomp bindings that the
// recompiled game calls but upstream librecomp doesn't provide. Stubbed
// to safe defaults — none of these primitives have meaningful semantics
// on a non-N64 host (cache management, controller pak access, etc.).
//
// All taken verbatim from MikeSemicolonD/N64ModernRuntime fork additions.
// Lifted into our repo so we don't have to maintain a librecomp fork.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <thread>
#include <mutex>
#include <chrono>
#if !defined(_WIN32)
#include <dlfcn.h>
#endif

#ifdef _WIN32
// For RtlCaptureStackBackTrace + GetCurrentThreadId in the task-submit
// stack-trace gate. Keep these out of broader code so we don't pull in
// windows.h elsewhere.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <dbghelp.h>
#include <timeapi.h>
#pragma comment(lib, "dbghelp.lib")
#pragma comment(lib, "winmm.lib")
#else
#include "win_compat.h"
#endif

#include <atomic>

#include "recomp.h"
#include "librecomp/helpers.hpp"
#include "ultramodern/ultramodern.hpp"

extern "C" bool rs64_audio_current_route_snapshot(
    uint32_t* phase, uint32_t* width, uint32_t* origin, uint32_t* ordinal,
    uint32_t* row, int* exit_reason, const char** arm);

extern "C" uint32_t rs64_phase_ord(void);
extern "C" volatile uint32_t g_rs64_last_guest_pc;
extern "C" void rs64_m5_vi_commit_handoff(uint32_t caller, uint32_t requested_width,
                                            uint32_t mode_ptr);

namespace {

struct M5ViCommitSnapshot {
    std::atomic<uint32_t> next_sequence{0};
    std::atomic<uint32_t> latest_sequence{0xFFFFFFFFu};
    std::atomic<uint32_t> caller{0};
    std::atomic<uint32_t> requested_width{0};
    std::atomic<uint32_t> width{0};
    std::atomic<uint32_t> origin{0};
    std::atomic<uint32_t> phase{0};
};

static M5ViCommitSnapshot g_m5_vi_commit;

enum class ViBoundaryEdge : uint32_t {
    Swap = 0,
    Commit = 1,
    Screen = 2,
};

static bool vi_boundary_log_enabled() {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* specific = std::getenv("ROGUESQ_LOG_VI_COMMIT");
        return (all && *all && *all != '0') ||
               (specific && *specific && *specific != '0');
    }();
    return enabled;
}

static std::atomic<uint32_t> g_vi_boundary_ordinal{0};
static std::atomic<uint32_t> g_vi_boundary_rows[3][2]{};
static std::atomic<uint32_t> g_vi_boundary_summary_armed{0};
static std::atomic<uint32_t> g_vi_screen_request{0};

static void vi_boundary_summary() {
    static const char* edges[] = {"swap", "commit", "screen"};
    static const uint32_t origins[] = {0x00696100u, 0x00696600u};
    std::fprintf(stderr, "[vi-boundary-summary] begin\n");
    for (uint32_t edge = 0; edge < 3; ++edge) {
        for (uint32_t origin = 0; origin < 2; ++origin) {
            uint32_t rows = g_vi_boundary_rows[edge][origin].load(std::memory_order_relaxed);
            if (rows > 64u) rows = 64u;
            std::fprintf(stderr,
                "[vi-boundary-summary] edge=%s origin=0x%06X rows=%u cap=64\n",
                edges[edge], origins[origin], rows);
        }
    }
    std::fprintf(stderr, "[vi-boundary-summary] end\n");
    std::fflush(stderr);
}

static bool vi_boundary_target(uint32_t origin, uint32_t* origin_index) {
    origin &= 0x00FFFFFFu;
    if (origin == 0x00696100u) {
        *origin_index = 0;
        return true;
    }
    if (origin == 0x00696600u) {
        *origin_index = 1;
        return true;
    }
    return false;
}

}

extern "C" void rs64_vi_boundary_set_screen_request(uint32_t framebuffer) {
    g_vi_screen_request.store(framebuffer, std::memory_order_relaxed);
}

extern "C" uint32_t rs64_vi_boundary_screen_request() {
    return g_vi_screen_request.load(std::memory_order_relaxed);
}

extern "C" void rs64_vi_boundary_log(const char* edge, uint32_t requested_fb,
                                      uint32_t committed_origin, uint32_t width) {
    if (!vi_boundary_log_enabled() || width != 640u) return;

    ViBoundaryEdge edge_id;
    if (std::strcmp(edge, "swap") == 0) {
        edge_id = ViBoundaryEdge::Swap;
    }
    else if (std::strcmp(edge, "commit") == 0) {
        edge_id = ViBoundaryEdge::Commit;
    }
    else if (std::strcmp(edge, "screen") == 0) {
        edge_id = ViBoundaryEdge::Screen;
    }
    else {
        return;
    }

    uint32_t origin_index = 0;
    const uint32_t origin = committed_origin & 0x00FFFFFFu;
    if (!vi_boundary_target(origin, &origin_index)) return;

    if (g_vi_boundary_summary_armed.exchange(1, std::memory_order_relaxed) == 0) {
        std::atexit(vi_boundary_summary);
    }

    const uint32_t edge_index = static_cast<uint32_t>(edge_id);
    const uint32_t row = g_vi_boundary_rows[edge_index][origin_index].fetch_add(
        1, std::memory_order_relaxed);
    if (row >= 64u) return;

    const uint32_t ordinal = g_vi_boundary_ordinal.fetch_add(1, std::memory_order_relaxed);
    const uint32_t request = requested_fb & 0x00FFFFFFu;
    std::fprintf(stderr,
        "[vi-boundary] edge=%s origin=0x%06X requested_fb=0x%06X "
        "committed_origin=0x%06X width=%u phase=%u row=%u ordinal=%u\n",
        edge, origin, request, origin, width, rs64_phase_ord(), row, ordinal);
    std::fflush(stderr);
}

extern "C" void __osContRamRead_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    _return<s32>(ctx, -1);  // no rumble pak
}

extern "C" void __osContRamWrite_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    _return<s32>(ctx, -1);  // no rumble pak
}

extern "C" void __osPfsSelectBank_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    _return<s32>(ctx, 1);  // PFS_ERR_NOPACK — no memory pak
}

extern "C" void osDpGetCounters_recomp(uint8_t* rdram, recomp_context* ctx) {
    // Zero out the 8 DP counters. buf_ptr stays gpr (64-bit) so the
    // sign-extended MIPS address survives MEM_W's KSEG0 unmasking.
    gpr buf_ptr = ctx->r4;
    for (int i = 0; i < 8; i++) {
        MEM_W(i * 4, buf_ptr) = 0;
    }
}

extern "C" void osViGetCurrentField_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    ctx->r2 = 0;  // always field 0 (progressive / non-interlaced)
}

// Override upstream's `assert(false)` in ultra_translation.cpp:32. The real
// libultra osYieldThread voluntarily yields to the scheduler. On the host
// the closest equivalent is std::this_thread::yield(); blocking briefly is
// fine — the game only calls this from idle/wait paths.
//
// This symbol is defined in upstream librecomp too (with the assert), but
// the linker picks our definition first because /FORCE:MULTIPLE is enabled
// (already used for the patches/heap_guards.c override). Same trick.
extern "C" void osYieldThread_recomp(uint8_t* /*rdram*/, recomp_context* /*ctx*/) {
    std::this_thread::yield();
}

// RS64 fix: game calls osViBlack(1) twice during boot at funcs_0.c:2083 and
// :2142 and never osViBlack(0). That keeps ultramodern's VI_STATE_BLACK set
// forever → hStart forced to 0 → VI::visible() returns false in RT64 →
// PresentEarly matcher fails → no presents fire. Override the recomp wrapper
// so the game's calls are no-ops (visibility stays on by default).
extern "C" void osViBlack_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    static int s_count = 0;
    int n = ++s_count;
    if (n <= 8) {
        fprintf(stderr, "[osViBlack #%d] active=%u (ignored — RS64 fix)\n",
                n, (uint32_t)ctx->r4);
        fflush(stderr);
    }
}

// Diagnostic: log osViSwapBuffer calls. The game tells VI which fb to display
// via this call. If the address doesn't match any prior SET_COLOR_IMAGE
// address, RT64 has no rendered content for it → black screen.
extern "C" void osViSwapBuffer_recomp(uint8_t* rdram, recomp_context* ctx) {
    static int s_count = 0;
    int n = ++s_count;
    uint32_t fb = (uint32_t)ctx->r4;

    static int s_log_callers = -1;
    if (s_log_callers < 0) {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_VI_CALLERS");
        s_log_callers = ((all && *all && *all != '0') ||
                         (own && *own && *own != '0')) ? 1 : 0;
    }
    {
        const auto* vi = ultramodern::renderer::get_vi_regs();
        rs64_vi_boundary_log("swap", fb,
                             vi->VI_ORIGIN_REG & 0x00FFFFFFu,
                             vi->VI_WIDTH_REG);
    }
    if (s_log_callers) {
        struct CallerRow {
            uint32_t caller;
            uintptr_t host_ra;
            uint32_t fb_phys;
            uint32_t width;
            uint32_t origin;
            uint32_t count;
        };
        static CallerRow rows[128]{};
        static uint32_t row_count = 0;
        const uint32_t caller = static_cast<uint32_t>(ctx->r31 - 8u);
        const uintptr_t host_ra = reinterpret_cast<uintptr_t>(__builtin_return_address(0));
        const uintptr_t self_addr = reinterpret_cast<uintptr_t>(&osViSwapBuffer_recomp);
        const uint32_t guest_pc = static_cast<uint32_t>(g_rs64_last_guest_pc);
        const uint32_t fb_phys = fb & 0x00FFFFFFu;
        const auto* vi = ultramodern::renderer::get_vi_regs();
        const uint32_t width = vi->VI_WIDTH_REG;
        const uint32_t origin = vi->VI_ORIGIN_REG & 0x00FFFFFFu;
        const uint32_t phase = rs64_phase_ord();
        const char* host_symbol = "?";
#if !defined(_WIN32)
        Dl_info host_info{};
        if (dladdr(reinterpret_cast<void*>(host_ra), &host_info) && host_info.dli_sname) {
            host_symbol = host_info.dli_sname;
        }
#endif
        if (n <= 16) {
            std::fprintf(stderr,
                "[vi-callers-control] n=%d caller=0x%08X guest_pc=0x%08X "
                "host_ra=0x%llX host_symbol=%s self=0x%llX fb=0x%06X width=%u "
                "origin=0x%06X phase=%u\n",
                n, caller, guest_pc, (unsigned long long)host_ra, host_symbol,
                (unsigned long long)self_addr, fb_phys, width, origin, phase);
            std::fflush(stderr);
        }
        if (width == 640u && (origin == 0x00696100u || origin == 0x00696600u)) {
            uint32_t index = row_count;
            for (uint32_t i = 0; i < row_count; ++i) {
                if (rows[i].caller == caller && rows[i].host_ra == host_ra &&
                    rows[i].fb_phys == fb_phys &&
                    rows[i].width == width && rows[i].origin == origin) {
                    index = i;
                    break;
                }
            }
            if (index == row_count && row_count < 128u) {
                rows[row_count++] = {caller, host_ra, fb_phys, width, origin, 0u};
            }
            if (index < row_count) {
                const uint32_t count = ++rows[index].count;
                if (count <= 16u || (count % 128u) == 0u) {
                    std::fprintf(stderr,
                        "[vi-callers] phase=%u caller=0x%08X guest_pc=0x%08X "
                        "host_ra=0x%llX host_symbol=%s fb=0x%06X width=%u "
                        "origin=0x%06X count=%u\n",
                        phase, caller, guest_pc, (unsigned long long)host_ra,
                        host_symbol, fb_phys, width, origin, count);
                    std::fflush(stderr);
                }
            }
        }
    }

    // EXPERIMENT 2026-05-13: ROGUESQ_FB_REDIRECT_HIRES — if the game asks VI
    // to display a lo-res fb (0x806BA000 / 0x806DD000 are 320×224 buffers,
    // ~0x23000 apart), redirect to the hi-res scratch fb at 0x8062B800
    // instead. Tests the hypothesis that attribution text lives in the
    // hi-res scratch but VI is swapping to an empty lo-res target.
    //
    // Empirically: SET_CIMG fires for both fb classes per frame, but ALL
    // texrects target 0x62B800 — the lo-res buffers only receive fillRect
    // clears. So this redirect should pull the actual drawn content into
    // VI's sampling stream.
    static int s_redirect = -1;
    if (s_redirect < 0) {
        const char* v = std::getenv("ROGUESQ_FB_REDIRECT_HIRES");
        s_redirect = (v && *v && v[0] != '0') ? 1 : 0;
        if (s_redirect) {
            fprintf(stderr, "[fb-redirect] lo-res VI swaps will be redirected to 0x8062B800 (hi-res scratch)\n");
            fflush(stderr);
        }
    }
    if (s_redirect) {
        const uint32_t phys = fb & 0x00FFFFFF;
        // Lo-res-fb signature: addresses 0x6BA000 / 0x6DD000 / 0x7DD000
        // (under 0x800000, in the small-fb cluster). Hi-res scratch is at
        // 0x62B800 — leave that untouched; redirect anything else in the
        // "expected VI fb" range to the hi-res scratch.
        if ((phys == 0x6BA000) || (phys == 0x6DD000) || (phys == 0x7DD000)) {
            uint32_t orig = fb;
            fb = 0x8062B800;
            if (n <= 8 || (n & 63) == 0) {
                fprintf(stderr, "[fb-redirect #%d] 0x%08X -> 0x%08X\n", n, orig, fb);
                fflush(stderr);
            }
        }
    }

    if (n <= 16 || (n & 63) == 0) {
        fprintf(stderr, "[osViSwapBuffer #%d] fb=0x%08X\n", n, fb);
        fflush(stderr);
    }
    // ROGUESQ_LOG_VI_FB_CONTENT=1: sample a few non-zero bytes from the fb
    // RDRAM to verify whether the game is writing attribution pixels into it
    // (vs the fb being empty and attribution rendering happening elsewhere).
    static int s_dump_fb = -1;
    if (s_dump_fb < 0) {
        const char* v = std::getenv("ROGUESQ_LOG_VI_FB_CONTENT");
        s_dump_fb = (v && *v && v[0] != '0') ? 1 : 0;
    }
    if (s_dump_fb && (n <= 64 || (n & 31) == 0)) {
        auto scan_fb = [&](uint32_t target_addr, const char* label) {
            const uint32_t phys = target_addr & 0x00FFFFFF;
            size_t nonzero = 0;
            uint32_t first_nz_off = 0xFFFFFFFFu;
            uint32_t first_nz_val = 0;
            const uint32_t scan = 320u * 224u * 2u;
            for (uint32_t i = 0; i < scan; i += 2) {
                uint32_t off = phys + i;
                uint8_t b0 = rdram[off ^ 3];
                uint8_t b1 = rdram[(off + 1) ^ 3];
                if (b0 || b1) {
                    if (first_nz_off == 0xFFFFFFFFu) {
                        first_nz_off = i;
                        first_nz_val = (uint32_t)((b0 << 8) | b1);
                    }
                    ++nonzero;
                }
            }
            fprintf(stderr, "[vi-fb-content #%d %s] addr=0x%08X nz_px=%zu/%u first@%u=0x%04X\n",
                    n, label, target_addr, nonzero, scan / 2u, first_nz_off, first_nz_val);
        };
        scan_fb(fb, "VI");
        // Also scan the hi-res scratch fb (0x8062B800) so we can see if
        // experimental op_02 output landed there.
        scan_fb(0x8062B800u, "hiRes");
        fflush(stderr);
    }
    extern void osViSwapBuffer(uint8_t* rdram, int32_t frameBufPtr);
    osViSwapBuffer(rdram, (int32_t)fb);
}

// Diagnostic: log osViSetMode calls + decode the OS_VI_MODE struct contents.
// OS_VI_MODE layout (libultra):
//   type      u32 at +0x00
//   comRegs.ctrl/width/burst/vSync/hSync/leap/hStart/xScale/vCurrent (9 u32) +0x04
//     → width at +0x08, xScale at +0x20
//   fldRegs[0].origin/yScale/vStart/vBurst/vIntr (5 u32) at +0x28
//     → yScale at +0x2C
//   fldRegs[1] at +0x3C (same layout)
// Total 80 bytes. We dump the first 80 bytes raw + key fields decoded so we
// can tell which mode is lo-res (width=320, xScale~0x200) vs hi-res
// (width=640, xScale~0x400).
extern "C" void osViSetMode_recomp(uint8_t* rdram, recomp_context* ctx) {
    static int s_count = 0;
    int n = ++s_count;
    static int selector_control = -1;
    if (selector_control < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_VI_SELECTOR");
        selector_control = (e && *e && *e != '0') ? 1 : 0;
    }
    if (selector_control && n == 1) {
        fprintf(stderr, "[vi-selector-positive] osViSetMode_recomp is live\n");
        fflush(stderr);
    }
    uint32_t mode_ptr = (uint32_t)ctx->r4;
    uint32_t rdram_off = mode_ptr & 0x00FFFFFF;
    auto read_u32 = [&](uint32_t off) -> uint32_t {
        uint32_t v = 0;
        for (int i = 0; i < 4; ++i) {
            v = (v << 8) | rdram[(rdram_off + off + i) ^ 3];
        }
        return v;
    };
    uint32_t type    = read_u32(0x00);
    uint32_t ctrl    = read_u32(0x04);
    uint32_t width   = read_u32(0x08);
    uint32_t xScale  = read_u32(0x20);
    uint32_t yScale  = read_u32(0x2C);
    uint32_t ra      = (uint32_t)ctx->r31;
    const char* site = "?";
#if !defined(_WIN32)
    Dl_info di{};
    if (dladdr(__builtin_return_address(0), &di) && di.dli_sname) {
        site = di.dli_sname;
    }
#endif
    fprintf(stderr,
        "[osViSetMode #%d] mode_ptr=0x%08X  type=0x%08X ctrl=0x%08X "
        "width=%u xScale=0x%08X yScale=0x%08X ra=0x%08X site=%s\n",
        n, mode_ptr, type, ctrl, width, xScale, yScale, ra, site);
    fflush(stderr);
    {
        auto guest_u8 = [rdram](uint32_t guest) -> uint32_t {
            if (guest < 0x80000000u || guest >= 0x80800000u) return 0xFFu;
            return rdram[(guest - 0x80000000u) ^ 3u];
        };
        auto guest_u32 = [&guest_u8](uint32_t guest) -> uint32_t {
            return (guest_u8(guest) << 24) | (guest_u8(guest + 1u) << 16) |
                   (guest_u8(guest + 2u) << 8) | guest_u8(guest + 3u);
        };
        const uint32_t slot0 = guest_u32(0x80128D50u + 8u);
        const uint32_t slot1 = guest_u32(0x80128DA0u + 8u);
        const uint32_t slot2 = guest_u32(0x80128DF0u + 8u);
        const uint32_t slot3 = guest_u32(0x80128E40u + 8u);
        const uint32_t pendingA = guest_u32(0x80128E94u);
        const uint32_t pendingB = guest_u32(0x80128E90u);
        fprintf(stderr,
            "[vi-mode-table] call=%d mode_ptr=0x%08X requested_width=%u "
            "slot0=%u slot1=%u slot2=%u slot3=%u "
            "pendingA=0x%08X pendingB=0x%08X pending_mask9=0x%X "
            "sel=%02X/%02X/%02X\n",
            n, mode_ptr, width, slot0, slot1, slot2, slot3,
            pendingA, pendingB, (pendingA | pendingB) & 0x9u,
            guest_u8(0x8011A865u), guest_u8(0x8011A864u),
            guest_u8(0x8011A862u));
        fflush(stderr);
    }
    static const bool log_transition = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_VI_TRANSITION");
        return (all && *all && *all != '0') || (own && *own && *own != '0');
    }();
    if (log_transition) {
        static bool phase_640_seen = false;
        const uint32_t committed_width = ultramodern::renderer::get_vi_regs()->VI_WIDTH_REG;
        if (committed_width >= 640) {
            phase_640_seen = true;
        }
        if (phase_640_seen) {
            fprintf(stderr,
                "[vi-transition-producer] call=%d committed_width=%u requested_width=%u mode_ptr=0x%08X\n",
                n, committed_width, width, mode_ptr);
            fflush(stderr);
        }
    }
    extern void osViSetMode(uint8_t* rdram, int32_t modePtr);
    osViSetMode(rdram, (int32_t)ctx->r4);
    rs64_m5_vi_commit_handoff(static_cast<uint32_t>(g_rs64_last_guest_pc), width, mode_ptr);
}

extern "C" uint32_t rs64_vi_committed_width() {
    static const bool log_post_consumer = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_POST_CONSUMER");
        const char* own = std::getenv("ROGUESQ_LOG_ALL");
        return (all && *all && *all != '0') ||
               (own && *own && *own != '0');
    }();
    if (log_post_consumer) {
        const uint32_t pc = static_cast<uint32_t>(g_rs64_last_guest_pc);
        if (pc >= 0x800356ACu && pc < 0x80035B00u) {
            const auto* vi = ultramodern::renderer::get_vi_regs();
            const uint32_t width = vi->VI_WIDTH_REG;
            const uint32_t origin = vi->VI_ORIGIN_REG & 0x00FFFFFFu;
            const bool target = (width == 1024u && origin == 0x00790400u) ||
                                (width == 512u && origin == 0x006AB400u);
            static uint32_t last_phase = 0xFFFFFFFFu;
            static uint32_t rows = 0;
            const uint32_t phase = rs64_phase_ord();
            if (phase != last_phase) {
                last_phase = phase;
                rows = 0;
            }
            if (target && rows++ < 32u) {
                std::fprintf(stderr,
                    "[m5-post-consumer] pc=0x%08X width=%u origin=0x%06X phase=%u row=%u\n",
                    pc, width, origin, phase, rows - 1u);
                std::fflush(stderr);
            }
        }
    }
    return ultramodern::renderer::get_vi_regs()->VI_WIDTH_REG;
}

extern "C" uint32_t rs64_vi_committed_origin() {
    return ultramodern::renderer::get_vi_regs()->VI_ORIGIN_REG;
}

extern "C" uint32_t rs64_phase_ord(void);

extern "C" void rs64_m5_vi_commit_handoff(uint32_t caller,
                                            uint32_t requested_width,
                                            uint32_t mode_ptr) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_TRANSITION");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const auto* vi = ultramodern::renderer::get_vi_regs();
    const uint32_t seq = g_m5_vi_commit.next_sequence.fetch_add(1, std::memory_order_relaxed);
    if (seq >= 128u) return;
    g_m5_vi_commit.latest_sequence.store(seq, std::memory_order_release);
    g_m5_vi_commit.caller.store(caller, std::memory_order_relaxed);
    g_m5_vi_commit.requested_width.store(requested_width, std::memory_order_relaxed);
    g_m5_vi_commit.width.store(vi->VI_WIDTH_REG, std::memory_order_relaxed);
    g_m5_vi_commit.origin.store(vi->VI_ORIGIN_REG & 0x00FFFFFFu, std::memory_order_relaxed);
    g_m5_vi_commit.phase.store(rs64_phase_ord(), std::memory_order_relaxed);
    static bool target_control = false;
    if (!target_control && vi->VI_WIDTH_REG >= 640u) {
        std::fprintf(stderr,
            "[m5-port-vi-control] seq=%u caller=0x%08X requested_width=%u "
            "committed_width=%u committed_origin=0x%06X phase=%u\n",
            seq, caller, requested_width, vi->VI_WIDTH_REG,
            vi->VI_ORIGIN_REG & 0x00FFFFFFu, rs64_phase_ord());
        std::fflush(stderr);
        target_control = true;
    }
    if (vi->VI_WIDTH_REG == 1024u &&
        (vi->VI_ORIGIN_REG & 0x00FFFFFFu) == 0x00790400u) {
        std::fprintf(stderr,
            "[m5-port-retail-target] seq=%u caller=0x%08X requested_width=%u "
            "committed_width=%u committed_origin=0x%06X phase=%u\n",
            seq, caller, requested_width, vi->VI_WIDTH_REG,
            vi->VI_ORIGIN_REG & 0x00FFFFFFu, rs64_phase_ord());
        std::fflush(stderr);
    }
    std::fprintf(stderr,
        "[m5-route-transition] edge=vi-commit seq=%u caller=0x%08X "
        "mode_ptr=0x%08X requested_width=%u committed_width=%u "
        "committed_origin=0x%06X phase=%u\n",
        seq, caller, mode_ptr, requested_width, vi->VI_WIDTH_REG,
        vi->VI_ORIGIN_REG & 0x00FFFFFFu, rs64_phase_ord());
    std::fflush(stderr);
}

extern "C" void rs64_m5_route_prepare_handoff(uint32_t prepare_seq,
                                                uint32_t phase,
                                                uint32_t width,
                                                uint32_t origin,
                                                uint32_t accepted) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_TRANSITION");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    static std::mutex mutex;
    static uint32_t row_phase = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    std::lock_guard<std::mutex> lock(mutex);
    if (row_phase != phase) {
        row_phase = phase;
        rows = 0;
    }
    if (rows++ >= 32u) return;
    const uint32_t key = (width << 24) ^ (origin & 0x00FFFFFFu);
    const uint32_t commit_key = (g_m5_vi_commit.width.load(std::memory_order_acquire) << 24) ^
                                g_m5_vi_commit.origin.load(std::memory_order_relaxed);
    std::fprintf(stderr,
        "[m5-route-transition] edge=route-prepare seq=%u phase=%u width=%u "
        "origin=0x%06X accepted=%u commit_seq=%u commit_caller=0x%08X "
        "commit_width=%u commit_origin=0x%06X commit_phase=%u key_match=%u\n",
        prepare_seq, phase, width, origin & 0x00FFFFFFu, accepted,
        g_m5_vi_commit.latest_sequence.load(std::memory_order_acquire),
        g_m5_vi_commit.caller.load(std::memory_order_relaxed),
        g_m5_vi_commit.width.load(std::memory_order_relaxed),
        g_m5_vi_commit.origin.load(std::memory_order_relaxed),
        g_m5_vi_commit.phase.load(std::memory_order_relaxed), key == commit_key ? 1u : 0u);
    std::fflush(stderr);
}

static thread_local uint32_t g_m5_host_current_seq = 0xFFFFFFFFu;
extern "C" void rs64_m5_host_edge(const char* edge, uint32_t task_seq,
                                    uint32_t data_ptr, uint32_t mq,
                                    uint32_t source, uint32_t sent,
                                    int32_t valid_count, int32_t msg_count);

extern "C" uint32_t rs64_m5_host_action_begin(uint32_t data_ptr) {
    static std::atomic<uint32_t> next_seq{0};
    g_m5_host_current_seq = next_seq.fetch_add(1, std::memory_order_relaxed);
    rs64_m5_host_edge("action-dequeue", g_m5_host_current_seq, data_ptr,
                      0, 0, 1, -1, -1);
    return g_m5_host_current_seq;
}

extern "C" uint32_t rs64_m5_host_send_begin(uint32_t data_ptr) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_ORDER");
        return (all && *all && *all != '0') || (own && *own && *own != '0');
    }();
    if (enabled) {
        std::fprintf(stderr, "[m5-route-order] edge=send-enter seq=%u data=0x%08X "
                             "phase=%u width=%u origin=0x%06X\n",
                     g_m5_host_current_seq, data_ptr, rs64_phase_ord(),
                     rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu);
        std::fflush(stderr);
    }
    return g_m5_host_current_seq;
}

extern "C" uint32_t rs64_m5_host_current_seq(void) {
    return g_m5_host_current_seq;
}

extern "C" void rs64_m5_host_edge(const char* edge, uint32_t task_seq,
                                    uint32_t data_ptr, uint32_t mq,
                                    uint32_t source, uint32_t sent,
                                    int32_t valid_count, int32_t msg_count) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_ORDER");
        return (all && *all && *all != '0') || (own && *own && *own != '0');
    }();
    if (!enabled) return;
    static std::mutex mutex;
    static uint32_t phase = 0xFFFFFFFFu;
    static uint32_t edge_rows[12] = {};
    const uint32_t now_phase = rs64_phase_ord();
    std::lock_guard<std::mutex> lock(mutex);
    if (phase != now_phase) {
        phase = now_phase;
        for (uint32_t& count : edge_rows) count = 0;
    }
    uint32_t edge_index = 11;
    if (edge && std::strcmp(edge, "action-dequeue") == 0) edge_index = 0;
    else if (edge && std::strcmp(edge, "sp-complete-enter") == 0) edge_index = 1;
    else if (edge && std::strcmp(edge, "sp-complete-return") == 0) edge_index = 2;
    else if (edge && std::strcmp(edge, "send-enter") == 0) edge_index = 3;
    else if (edge && std::strcmp(edge, "send-return") == 0) edge_index = 4;
    else if (edge && std::strcmp(edge, "dp-complete") == 0) edge_index = 5;
    else if (edge && std::strcmp(edge, "external-enqueue") == 0) edge_index = 6;
    else if (edge && std::strcmp(edge, "external-delivery") == 0) edge_index = 7;
    else if (edge && std::strcmp(edge, "displaylist-submitted") == 0) edge_index = 8;
    else if (edge && std::strcmp(edge, "displaylist-parsed") == 0) edge_index = 9;
    else if (edge && std::strcmp(edge, "displaylist-completed-enter") == 0) edge_index = 10;
    if (edge_rows[edge_index]++ >= (edge_index == 3 ? 2048u : 512u)) return;
    std::fprintf(stderr,
        "[m5-route-order] edge=%s seq=%u data=0x%08X mq=0x%08X source=%u "
        "sent=%u valid=%d capacity=%d phase=%u width=%u origin=0x%06X\n",
        edge ? edge : "?", task_seq, data_ptr, mq, source, sent,
        valid_count, msg_count, now_phase, rs64_vi_committed_width(),
        rs64_vi_committed_origin() & 0x00FFFFFFu);
    std::fflush(stderr);
}

namespace {

static bool rs64_m5_route_fingerprint_enabled() {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_C88_ROUTE_FINGERPRINT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    return enabled;
}

static std::mutex g_rs64_m5_route_fingerprint_mutex;
static uint32_t g_rs64_m5_route_fingerprint_phase = 0xFFFFFFFFu;
static uint32_t g_rs64_m5_route_fingerprint_width = 0;
static uint32_t g_rs64_m5_route_fingerprint_origin = 0;
static uint32_t g_rs64_m5_route_fingerprint_b40 = 0;
static uint32_t g_rs64_m5_route_fingerprint_route = 0;
static uint32_t g_rs64_m5_route_fingerprint_keyon = 0;
static uint32_t g_rs64_m5_route_fingerprint_last_pc = 0;
static uint32_t g_rs64_m5_route_fingerprint_snapshots = 0;

static bool rs64_m5_route_fingerprint_target(uint32_t width, uint32_t origin) {
    origin &= 0x00FFFFFFu;
    return (width == 640u && (origin == 0x00696100u || origin == 0x00696600u)) ||
           (width == 1024u && origin == 0x00790400u) ||
           (width == 512u && origin == 0x006AB400u);
}

static void rs64_m5_route_fingerprint_reset_locked(uint32_t phase,
                                                    uint32_t width,
                                                    uint32_t origin) {
    g_rs64_m5_route_fingerprint_phase = phase;
    g_rs64_m5_route_fingerprint_width = width;
    g_rs64_m5_route_fingerprint_origin = origin & 0x00FFFFFFu;
    g_rs64_m5_route_fingerprint_b40 = 0;
    g_rs64_m5_route_fingerprint_route = 0;
    g_rs64_m5_route_fingerprint_keyon = 0;
    g_rs64_m5_route_fingerprint_last_pc = 0;
    g_rs64_m5_route_fingerprint_snapshots = 0;
}

static void rs64_m5_route_fingerprint_emit_locked(const char* edge) {
    const char* c88 = std::getenv("ROGUESQ_M5_C88_VALUE");
    const unsigned c88_value = (c88 && c88[0] && c88[0] != '0') ? 1u : 0u;
    std::fprintf(stderr,
        "[m5-route-fingerprint] edge=%s arm=c88_%u c88=%u phase=%u width=%u "
        "origin=0x%06X route_state_count=%u b40_count=%u key_on_count=%u "
        "last_guest_pc=0x%08X snapshot=%u\n",
        edge, c88_value, c88_value, g_rs64_m5_route_fingerprint_phase,
        g_rs64_m5_route_fingerprint_width, g_rs64_m5_route_fingerprint_origin,
        g_rs64_m5_route_fingerprint_route, g_rs64_m5_route_fingerprint_b40,
        g_rs64_m5_route_fingerprint_keyon,
        g_rs64_m5_route_fingerprint_last_pc,
        g_rs64_m5_route_fingerprint_snapshots);
    std::fflush(stderr);
}

static void rs64_m5_route_fingerprint_note_locked(unsigned kind, uint32_t pc) {
    const uint32_t phase = rs64_phase_ord();
    if (g_rs64_m5_route_fingerprint_phase != phase) {
        rs64_m5_route_fingerprint_reset_locked(
            phase, rs64_vi_committed_width(), rs64_vi_committed_origin());
    }
    if (kind == 1u) {
        ++g_rs64_m5_route_fingerprint_b40;
    } else if (kind == 2u) {
        ++g_rs64_m5_route_fingerprint_route;
    } else if (kind == 3u) {
        ++g_rs64_m5_route_fingerprint_keyon;
    }
    if (pc != 0u && pc != 0xFFFFFFFFu) {
        g_rs64_m5_route_fingerprint_last_pc = pc;
    } else if (g_rs64_last_guest_pc != 0u) {
        g_rs64_m5_route_fingerprint_last_pc =
            static_cast<uint32_t>(g_rs64_last_guest_pc);
    }
}

static void rs64_m5_route_fingerprint_note(unsigned kind, uint32_t pc) {
    if (!rs64_m5_route_fingerprint_enabled()) return;
    std::lock_guard<std::mutex> lock(g_rs64_m5_route_fingerprint_mutex);
    rs64_m5_route_fingerprint_note_locked(kind, pc);
}

}

extern "C" void rs64_m5_route_fingerprint_phase(uint32_t width,
                                                   uint32_t origin) {
    if (!rs64_m5_route_fingerprint_enabled()) return;
    std::lock_guard<std::mutex> lock(g_rs64_m5_route_fingerprint_mutex);
    const uint32_t phase = rs64_phase_ord();
    if (g_rs64_m5_route_fingerprint_phase == phase) {
        if (rs64_m5_route_fingerprint_target(
                g_rs64_m5_route_fingerprint_width,
                g_rs64_m5_route_fingerprint_origin)) {
            rs64_m5_route_fingerprint_emit_locked("phase-exit");
        }
    }
    rs64_m5_route_fingerprint_reset_locked(phase + 1u, width, origin);
}

extern "C" void rs64_m5_route_fingerprint_snapshot(uint32_t width,
                                                      uint32_t origin) {
    if (!rs64_m5_route_fingerprint_enabled()) return;
    std::lock_guard<std::mutex> lock(g_rs64_m5_route_fingerprint_mutex);
    const uint32_t phase = rs64_phase_ord();
    if (g_rs64_m5_route_fingerprint_phase != phase) {
        rs64_m5_route_fingerprint_reset_locked(phase, width, origin);
    }
    g_rs64_m5_route_fingerprint_width = width;
    g_rs64_m5_route_fingerprint_origin = origin & 0x00FFFFFFu;
    g_rs64_m5_route_fingerprint_last_pc =
        static_cast<uint32_t>(g_rs64_last_guest_pc);
    const uint32_t snapshot = g_rs64_m5_route_fingerprint_snapshots++;
    if (rs64_m5_route_fingerprint_target(width, origin) &&
        (snapshot < 4u || (snapshot % 64u) == 0u)) {
        rs64_m5_route_fingerprint_emit_locked("snapshot");
    }
}

extern "C" void rs64_m5_route_fingerprint_keyon(uint32_t site) {
    rs64_m5_route_fingerprint_note(3u, site);
}

static std::atomic<uint32_t> g_rs64_m5_b40_route_ordinal{0xFFFFFFFFu};

extern "C" void rs64_m5_b40_route_event(const char* edge, uint32_t pc,
                                         uint32_t b40_stored, uint32_t value,
                                         uint32_t b40_return) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_B40_ROUTE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    rs64_m5_route_fingerprint_note(1u, pc);

    static std::atomic<uint32_t> phase_seen{0xFFFFFFFFu};
    static std::atomic<uint32_t> phase_row{0};
    static std::atomic<uint32_t> last_b40_stored{0xFFFFFFFFu};
    static std::atomic<uint32_t> last_b40_return{0xFFFFFFFFu};
    const uint32_t phase = rs64_phase_ord();
    uint32_t prior = phase_seen.load(std::memory_order_relaxed);
    if (prior != phase && phase_seen.compare_exchange_strong(
            prior, phase, std::memory_order_relaxed)) {
        phase_row.store(0, std::memory_order_relaxed);
    }
    const uint32_t ordinal = phase_row.fetch_add(1, std::memory_order_relaxed);
    g_rs64_m5_b40_route_ordinal.store(ordinal, std::memory_order_relaxed);
    if (ordinal >= 512u) return;

    if (b40_stored != 0xFFFFFFFFu) {
        last_b40_stored.store(b40_stored & 0xFFu, std::memory_order_relaxed);
    }
    if (b40_return != 0xFFFFFFFFu) {
        last_b40_return.store(b40_return, std::memory_order_relaxed);
    }
    const uint32_t stored = last_b40_stored.load(std::memory_order_relaxed);
    const uint32_t returned = last_b40_return.load(std::memory_order_relaxed);
    const char* b40 = std::getenv("ROGUESQ_M5_B40_VALUE");
    const char* c88 = std::getenv("ROGUESQ_M5_C88_VALUE");
    const char* arm = (b40 && b40[0] && b40[0] != '0') ? "treatment" : "control";
    std::fprintf(stderr,
        "[m5-b40-route] arm=%s b40=%u c88=%u ordinal=%u phase=%u width=%u "
        "origin=0x%06X edge=%s pc=0x%08X b40_stored=0x%02X value=0x%08X "
        "b40_return=0x%08X\n",
        arm, (b40 && b40[0] && b40[0] != '0') ? 1u : 0u,
        (c88 && c88[0] && c88[0] != '0') ? 1u : 0u, ordinal, phase,
        rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu,
        edge ? edge : "?", pc, stored & 0xFFu, value, returned);
    std::fflush(stderr);
}

static thread_local uint32_t g_rs64_m5_route_state_call_ordinal = 0xFFFFFFFFu;
static thread_local uint32_t g_rs64_m5_route_state_entry_a1 = 0xFFFFFFFFu;
static thread_local uint32_t g_rs64_m5_route_state_audio_nonzero = 2u;

static uint32_t rs64_m5_route_state_guest_byte(uint8_t* rdram, uint32_t guest) {
    if (rdram == nullptr || guest < 0x80000000u || guest >= 0x80800000u) {
        return 0xFFFFFFFFu;
    }
    return rdram[guest - 0x80000000u];
}

static void rs64_m5_route_state_log(uint8_t* rdram, const char* edge,
                                     uint32_t pc, uint32_t call_ordinal,
                                     uint32_t a0, uint32_t a1, uint32_t a2,
                                     uint32_t a3, uint32_t a1_gate,
                                     uint32_t audio_nonzero,
                                     uint32_t function_nonzero) {
    const uint32_t phase = rs64_phase_ord();
    rs64_m5_route_fingerprint_note(2u, pc);
    const uint32_t limit = phase == 7u ? 512u : 16u;
    if (call_ordinal >= limit) return;

    const char* b40 = std::getenv("ROGUESQ_M5_B40_VALUE");
    const char* c88 = std::getenv("ROGUESQ_M5_C88_VALUE");
    const uint32_t state_1ad0 = rs64_m5_route_state_guest_byte(rdram, 0x80141AD0u);
    const uint32_t state_3b038 = rs64_m5_route_state_guest_byte(rdram, 0x8013B038u);
    const uint32_t state_1ad1 = rs64_m5_route_state_guest_byte(rdram, 0x80141AD1u);
    const uint32_t audio = audio_nonzero == 0xFFFFFFFFu
        ? g_rs64_m5_route_state_audio_nonzero : audio_nonzero;
    std::fprintf(stderr,
        "[m5-route-state] arm=%s b40=%u c88=%u edge=%s phase=%u target=%u "
        "call_ordinal=%u route_ordinal=%u width=%u origin=0x%06X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X a1_gate=0x%08X "
        "state_1ad0=0x%02X state_3b038=0x%02X state_1ad1=0x%02X "
        "audio_nonzero=%u function_nonzero=%u\n",
        (b40 && b40[0] && b40[0] != '0') ? "treatment" : "control",
        (b40 && b40[0] && b40[0] != '0') ? 1u : 0u,
        (c88 && c88[0] && c88[0] != '0') ? 1u : 0u,
        edge ? edge : "?", phase, phase == 7u ? 1u : 0u, call_ordinal,
        g_rs64_m5_b40_route_ordinal.load(std::memory_order_relaxed),
        rs64_vi_committed_width(), rs64_vi_committed_origin() & 0x00FFFFFFu,
        a0, a1, a2, a3, a1_gate, state_1ad0, state_3b038, state_1ad1,
        audio, function_nonzero);
    std::fflush(stderr);
}

extern "C" uint32_t rs64_m5_route_state_callsite(uint8_t* rdram,
                                                   uint32_t pc, uint32_t a0,
                                                   uint32_t a1, uint32_t a2,
                                                   uint32_t a3) {
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t next_ordinal = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        next_ordinal = 0;
    }
    g_rs64_m5_route_state_call_ordinal = next_ordinal++;
    g_rs64_m5_route_state_entry_a1 = a1;
    g_rs64_m5_route_state_audio_nonzero = 2u;
    const char* all = std::getenv("ROGUESQ_LOG_ALL");
    const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_STATE");
    if ((all && all[0] && all[0] != '0') || (own && own[0] && own[0] != '0')) {
        rs64_m5_route_state_log(rdram, "callsite", pc,
                                g_rs64_m5_route_state_call_ordinal,
                                a0, a1, a2, a3, a1, 0xFFFFFFFFu, 2u);
    }
    return g_rs64_m5_route_state_call_ordinal;
}

extern "C" void rs64_m5_route_state_event(uint8_t* rdram, const char* edge,
                                            uint32_t pc, uint32_t a0,
                                            uint32_t a1, uint32_t a2,
                                            uint32_t a3,
                                            uint32_t audio_nonzero,
                                            uint32_t function_nonzero) {
    const char* all = std::getenv("ROGUESQ_LOG_ALL");
    const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_STATE");
    if (!((all && all[0] && all[0] != '0') ||
          (own && own[0] && own[0] != '0'))) return;

    if (edge && edge[0] == 'e' && edge[1] == 'n') {
        g_rs64_m5_route_state_entry_a1 = a1;
    }
    if (edge && edge[0] == 'a' && edge[1] == 'u') {
        g_rs64_m5_route_state_audio_nonzero = audio_nonzero ? 1u : 0u;
    }
    rs64_m5_route_state_log(rdram, edge, pc,
                            g_rs64_m5_route_state_call_ordinal,
                            a0, a1, a2, a3,
                            g_rs64_m5_route_state_entry_a1,
                            audio_nonzero, function_nonzero);
}

extern "C" void rs64_m5_selector_route_caller(const char* name, uint32_t pc,
                                                uint32_t ra, uint32_t a0,
                                                uint32_t a1, uint32_t a2,
                                                uint32_t a3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_ROUTE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-route-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    if (!((width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-route] ordinal=%u phase=%u width=%u origin=0x%06X "
        "name=%s pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X\n",
        rows++, phase, width, origin, name ? name : "?", pc, ra, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_mixer_callsite(const char* name,
                                                   uint32_t pc, uint32_t ra,
                                                   uint32_t a0, uint32_t a1,
                                                   uint32_t a2, uint32_t a3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_MIXER_CALLSITE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-mixer-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    if (!((width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-selector-mixer] ordinal=%u phase=%u width=%u origin=0x%06X "
        "name=%s pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X\n",
        rows++, phase, width, origin, name ? name : "?", pc, ra, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_s3352_m5_consumer_entry(uint8_t* rdram, uint32_t pc) {
    (void)rdram;
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_CONSUMER_ENTRY");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-consumer-entry-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    if (!((width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
          (width == 512u && (origin == 0x006AB400u || origin == 0x006AB800u)))) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows >= 128u) return;
    std::fprintf(stderr,
        "[m5-consumer-entry] ordinal=%u phase=%u width=%u origin=0x%06X pc=0x%08X\n",
        rows++, phase, width, origin, pc);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_tick_edge(const char* edge, uint32_t pc,
                                              uint32_t taken, uint32_t a0,
                                              uint32_t a1, uint32_t a2,
                                              uint32_t a3, uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_TICK");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-tick-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    if (!((width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
          (width == 512u && (origin == 0x006AB400u || origin == 0x006AB800u)))) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-tick] ordinal=%u phase=%u width=%u origin=0x%06X "
        "edge=%s pc=0x%08X taken=%u a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X value=0x%08X\n",
        rows++, phase, width, origin, edge ? edge : "?", pc, taken,
        a0, a1, a2, a3, value);
    std::fflush(stderr);
}

extern "C" void rs64_m5_route_candidate(uint8_t* rdram, uint32_t pc,
                                           uint32_t caller, uint32_t s0,
                                           uint32_t s1, uint32_t a0,
                                           uint32_t a1, uint32_t a2,
                                           uint32_t v0) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_CANDIDATE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || rdram == nullptr) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 512u) return;
    const auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint8_t* p = rdram + (guest - 0x80000000u);
        return (static_cast<uint32_t>(p[0]) << 24) |
               (static_cast<uint32_t>(p[1]) << 16) |
               (static_cast<uint32_t>(p[2]) << 8) | p[3];
    };
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    std::fprintf(stderr,
        "[m5-route-candidate] n=%u phase=%u width=%u origin=0x%06X "
        "arm=%s active=%u ordinal=%u row=%u pc=0x%08X caller=0x%08X "
        "s0=0x%08X s1=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X v0=0x%08X "
        "m0=0x%08X m4=0x%08X m8=0x%08X mc=0x%08X st1ad0=0x%02X "
        "st3b038=0x%02X st1ad1=0x%02X exit=%d\n",
        rows, rs64_phase_ord(), width, origin, arm ? arm : "n/a",
        active ? 1u : 0u, ordinal, route_row, pc, caller, s0, s1, a0,
        a1, a2, v0, word(a0), word(a0 + 4u), word(a0 + 8u), word(a0 + 12u),
        rs64_m5_route_state_guest_byte(rdram, 0x80141AD0u),
        rs64_m5_route_state_guest_byte(rdram, 0x8013B038u),
        rs64_m5_route_state_guest_byte(rdram, 0x80141AD1u), exit_reason);
    std::fflush(stderr);
    ++rows;
}

extern "C" void rs64_m5_route_prepare_inputs(
    uint8_t* rdram, uint32_t pc, uint32_t caller, uint32_t sp,
    uint32_t s0, uint32_t s1, uint32_t s2, uint32_t s3, uint32_t s4,
    uint32_t s5, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t v0,
    uint32_t message_type, uint32_t source_word, uint32_t source_byte,
    uint32_t branch_state) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_PREPARE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || rdram == nullptr) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 256u) return;
    const uint32_t route_target =
        ((width == 1024u && origin == 0x00790400u) ||
         (width == 512u && origin == 0x006AB400u)) ? 1u : 0u;
    const uint32_t branch = message_type == 2u ? 2u :
                            message_type >= 3u ? 3u :
                            message_type == 1u ? 1u : 0u;
    uint32_t ordinal = 0xFFFFFFFFu, route_row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    const bool active = rs64_audio_current_route_snapshot(
        nullptr, nullptr, nullptr, &ordinal, &route_row, &exit_reason, &arm);
    std::fprintf(stderr,
        "[route-prep] n=%u phase=%u width=%u origin=0x%06X target=%u "
        "accepted=%u pc=0x%08X caller=0x%08X sp=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X s3=0x%08X s4=0x%08X s5=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X v0=0x%08X msg=0x%02X branch=%u "
        "source_word=0x%08X source_byte=0x%02X branch_state=0x%04X "
        "active=%u ordinal=%u row=%u exit=%d\n",
        rows, rs64_phase_ord(), width, origin, route_target, route_target,
        pc, caller, sp, s0, s1, s2, s3, s4, s5, a0, a1, a2, v0,
        message_type, branch, source_word, source_byte, branch_state,
        active ? 1u : 0u, ordinal, route_row, exit_reason);
    std::fflush(stderr);
    ++rows;
}

extern "C" void rs64_m5_producer_mark_handoff(uint8_t* rdram, uint32_t edge,
                                                 uint32_t caller, uint32_t s0,
                                                 uint32_t s1, uint32_t a0,
                                                 uint32_t a1, uint32_t a2,
                                                 uint32_t v0) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_ROUTE_HANDOFF");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !rdram) return;
    static std::mutex mutex;
    static uint32_t key = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t phase = rs64_phase_ord();
    const uint32_t next_key = (width << 24) ^ origin;
    std::lock_guard<std::mutex> lock(mutex);
    if (key != next_key) { key = next_key; rows = 0; }
    if (rows++ >= 512u) return;
    const auto byte = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= 0x80800000u) return 0xFFu;
        return rdram[(guest - 0x80000000u) ^ 3u];
    };
    const auto word = [&byte](uint32_t guest) -> uint32_t {
        return (byte(guest) << 24) | (byte(guest + 1u) << 16) |
               (byte(guest + 2u) << 8) | byte(guest + 3u);
    };
    const uint32_t target = ((width == 1024u && origin == 0x00790400u) ||
                             (width == 512u && origin == 0x006AB400u)) ? 1u : 0u;
    std::fprintf(stderr,
        "[m5-route-handoff] edge=%s n=%u phase=%u width=%u origin=0x%06X "
        "target=%u caller=0x%08X s0=0x%08X s1=0x%08X a0=0x%08X a1=0x%08X "
        "a2=0x%08X v0=0x%08X count=%u states=%u,%u,%u,%u,%u,%u "
        "pending=0x%08X/0x%08X sel=%02X/%02X/%02X\n",
        edge == 0u ? "entry" : (edge == 1u ? "exit" : "call"), rows - 1u,
        phase, width, origin, target,
        caller, s0, s1, a0, a1, a2, v0, byte(0x80128EADu),
        byte(0x80128EAAu), byte(0x80128EABu), byte(0x80128EACu),
        byte(0x80128EADu), byte(0x80128EAEu), byte(0x80128EAFu),
        word(0x80128E94u), word(0x80128E90u), byte(0x8012A865u),
        byte(0x8012A864u), byte(0x8012A862u));
    std::fflush(stderr);
}

extern "C" void rs64_m5_b40_read(uint8_t* /*rdram*/, uint32_t read_pc,
                                  uint32_t value, uint32_t branch_pc,
                                  uint32_t branch_taken) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_B40_READ");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;

    static std::atomic<uint32_t> phase_key{0xFFFFFFFFu};
    static std::atomic<uint32_t> phase_row{0};
    const uint32_t key = (width << 24) ^ origin;
    uint32_t prior = phase_key.load(std::memory_order_relaxed);
    if (prior != key && phase_key.compare_exchange_strong(
            prior, key, std::memory_order_relaxed)) {
        phase_row.store(0, std::memory_order_relaxed);
    }
    const uint32_t row = phase_row.fetch_add(1, std::memory_order_relaxed);
    if (row >= 4096u) return;

    const char* b40 = std::getenv("ROGUESQ_M5_B40_VALUE");
    const char* c88 = std::getenv("ROGUESQ_M5_C88_VALUE");
    std::fprintf(stderr,
        "[m5-b40-read] arm=%s b40=%u c88=%u row=%u phase=%u width=%u "
        "origin=0x%06X pc=0x%08X value=0x%02X branch_pc=0x%08X "
        "branch_dir=%u route_ordinal=%u\n",
        (b40 && b40[0] && b40[0] != '0') ? "treatment" : "control",
        (b40 && b40[0] && b40[0] != '0') ? 1u : 0u,
        (c88 && c88[0] && c88[0] != '0') ? 1u : 0u, row,
        rs64_phase_ord(), width, origin & 0x00FFFFFFu, read_pc,
        value & 0xFFu, branch_pc, branch_taken,
        g_rs64_m5_b40_route_ordinal.load(std::memory_order_relaxed));
    std::fflush(stderr);
}

extern "C" void rs64_m5_b40_route_title_transition(void) {
    static std::atomic<bool> seen{false};
    bool expected = false;
    if (!seen.compare_exchange_strong(expected, true, std::memory_order_relaxed)) return;
    rs64_m5_b40_route_event("title-transition", 0u, 0xFFFFFFFFu,
                            0xFFFFFFFFu, 0xFFFFFFFFu);
}

extern "C" int rs64_is_hangar_vi(void) {
    ultramodern::renderer::ViRegs *vi = ultramodern::renderer::get_vi_regs();
    if (vi->VI_WIDTH_REG != 512u) return 0;
    const uint32_t o = vi->VI_ORIGIN_REG & 0x00FFFFFFu;
    return (o == 0x006ab400u || o == 0x006ab800u) ? 1 : 0;
}

extern "C" void osViSetXScale_recomp(uint8_t* rdram, recomp_context* ctx) {
    static int s_count = 0;
    int n = ++s_count;
    if (n <= 4) {
        fprintf(stderr, "[osViSetXScale #%d] scale=%f\n", n, (double)ctx->f12.fl);
        fflush(stderr);
    }
    extern void osViSetXScale(float scale);
    osViSetXScale(ctx->f12.fl);
}

extern "C" void osViSetYScale_recomp(uint8_t* rdram, recomp_context* ctx) {
    static int s_count = 0;
    int n = ++s_count;
    if (n <= 4) {
        fprintf(stderr, "[osViSetYScale #%d] scale=%f\n", n, (double)ctx->f12.fl);
        fflush(stderr);
    }
    extern void osViSetYScale(float scale);
    osViSetYScale(ctx->f12.fl);
}

// osGetMemSize override — defaults to 8MB (Expansion Pak present, hi-res
// mode available). ROGUESQ_MEM_SIZE_MB=4 forces 4MB to test base-N64 lo-res
// path. 2026-05-13 test confirmed 4MB alone crashes boot in mainBootstrapWorker
// (game still goes hi-res because the mode flag is gated on more than memsize),
// so the env var is a knob, not a recommended setting.
extern "C" void osGetMemSize_recomp(uint8_t* /*rdram*/, recomp_context* ctx) {
    static int s_mb = -1;
    if (s_mb < 0) {
        const char* v = std::getenv("ROGUESQ_MEM_SIZE_MB");
        s_mb = (v && *v) ? std::atoi(v) : 8;
        if (s_mb != 8) {
            fprintf(stderr, "[osGetMemSize] reporting %d MB (env override)\n", s_mb);
            fflush(stderr);
        }
    }
    ctx->r2 = (gpr)(s_mb * 1024 * 1024);
}

// zmemcpy is stubbed in rogue_squadron.toml because the original MIPS code
// at 0x80018F4C contains a `cache 0x0D` instruction unsupported by N64Recomp.
// The toml comment claims "the runtime provides memcpy" but no such
// implementation existed — leaving zmemcpy as an empty body. That made
// zlib's inflate_flush a no-op (it calls zmemcpy to copy from the sliding
// window to the user's next_out buffer), so every decompressed asset stayed
// all-zero. This is the actual implementation: byte-by-byte copy honoring
// the recompile's XOR-3 byte swizzle on each access.
//
// Signature: void zmemcpy(Bytef *dest, const Bytef *source, uInt len);
//   a0/r4 = dest (MIPS virtual address)
//   a1/r5 = source (MIPS virtual address)
//   a2/r6 = len (byte count)
extern "C" void zmemcpy(uint8_t* rdram, recomp_context* ctx) {
    // Use the full 64-bit register values for the bounds check. The MEM_BU
    // macro does (reg + offset) ^ 3 - 0xFFFFFFFF80000000 in 64-bit, so
    // truncating to uint32_t can mask sign-extension issues.
    uint64_t dest_full = (uint64_t)ctx->r4;
    uint64_t src_full  = (uint64_t)ctx->r5;
    uint64_t len_full  = (uint64_t)ctx->r6;
    constexpr uint64_t KSEG0_BASE = 0xFFFFFFFF80000000ull;
    constexpr uint64_t KSEG0_END  = 0xFFFFFFFF80800000ull;
    constexpr uint32_t KSEG0_BASE_LO = 0x80000000u;
    constexpr uint32_t KSEG0_END_LO  = 0x80800000u;
    auto in_range = [](uint64_t addr_full, uint64_t n) {
        // Accept either sign-extended (0xFFFFFFFF80...) or zero-extended (0x80...)
        // as long as it lands within the 8MB rdram region.
        if (addr_full >= KSEG0_BASE && addr_full + n <= KSEG0_END) return true;
        uint32_t lo = (uint32_t)addr_full;
        if (lo >= KSEG0_BASE_LO && (uint64_t)lo + n <= KSEG0_END_LO &&
            (addr_full >> 32) == 0) return true;
        return false;
    };
    if (len_full > 0 && (!in_range(dest_full, len_full) || !in_range(src_full, len_full))) {
        static int s_warned = 0;
        if (s_warned++ < 8) {
            fprintf(stderr, "[zmemcpy] OOB skip dst=0x%016llX src=0x%016llX len=%llu\n",
                    (unsigned long long)dest_full,
                    (unsigned long long)src_full,
                    (unsigned long long)len_full);
            fflush(stderr);
        }
        ctx->r2 = ctx->r4;  // zlib's zmemcpy returns nothing meaningful
        return;
    }
    // Use full gpr (uint64_t) values for MEM_BU/MEM_B. Truncating to uint32_t
    // breaks the macro's `- 0xFFFFFFFF80000000` arithmetic under C integer
    // promotion (uint32 + int64 = the uint32 gets zero-extended, so subtracting
    // a sign-extended int64 produces a 4GB-offset host pointer → AV).
    gpr dest_reg = ctx->r4;
    gpr src_reg  = ctx->r5;
    uint32_t len = (uint32_t)len_full;
    for (uint32_t i = 0; i < len; ++i) {
        ctx->r2 = MEM_BU(i, src_reg);
        MEM_B(i, dest_reg) = ctx->r2;
    }
    ctx->r2 = ctx->r4;  // zlib's zmemcpy returns nothing meaningful
}

// heapWalker cycle-detection state. Updated by hooks in funcs_3.c (entry +
// loop-top). When the walk revisits its starting pointer, the hook breaks
// out of the loop instead of spinning forever.
extern "C" unsigned g_heapwalker_initial = 0;
extern "C" unsigned g_heapwalker_iter = 0;

// tickTextureMaterialExpiry cycle-detection state. Inner walk over the
// material list can loop forever when a node's next ptr points back into
// the visited set. KSEG0 guards prevent AVs but not cycles. Reset at
// function entry; capped iter count + first-node-revisit triggers bailout.
extern "C" unsigned g_tick_walker_first = 0;
extern "C" unsigned g_tick_walker_iter  = 0;

// Watchdog for the cinematic inner loop. cinematicLoopBody iterates many
// times per cutscene playback; if it stops iterating for more than 2 seconds
// while the rest of the runtime keeps ticking, the game thread is hung in
// some callee. We capture the game thread's stack to find which one.
#ifdef _WIN32
static std::atomic<DWORD> g_cine_tid{0};
static std::atomic<uint64_t> g_cine_iter{0};
static std::atomic<uint64_t> g_cine_last_ms{0};

extern "C" void rs64_cine_dump_if_stuck(void);
extern "C" void rs64_cine_progress_log(void);
extern "C" void rs64_cine_start_watchdog_thread(void);

extern "C" void rs64_cine_iter_tick(unsigned iter) {
    g_cine_tid.store(GetCurrentThreadId(), std::memory_order_relaxed);
    g_cine_iter.store(iter, std::memory_order_relaxed);
    g_cine_last_ms.store(GetTickCount64(), std::memory_order_relaxed);
    // First tick spawns the dedicated watchdog thread.
    rs64_cine_start_watchdog_thread();
}

// Spawn a dedicated watchdog thread the first time iter_tick fires. The
// gfx_thread's update_screen path could itself be deadlocked behind the
// same mutex chain that's hanging the game thread (events_context.message_mutex
// in ultramodern, in particular), so polling from gfx_thread isn't reliable.
// A standalone thread that only uses Sleep + atomics is immune.
extern "C" void rs64_cine_start_watchdog_thread(void) {
    static std::atomic<bool> s_started{false};
    bool was = s_started.exchange(true, std::memory_order_relaxed);
    if (was) return;
    std::thread([]() {
        for (;;) {
            ::Sleep(500);
            rs64_cine_progress_log();
            rs64_cine_dump_if_stuck();
        }
    }).detach();
}

// Periodic progress log so we can see whether the inner loop is iterating
// at all and at what rate. Called from update_screen on a coarse schedule.
extern "C" void rs64_cine_progress_log(void) {
    static uint64_t s_last_log_ms = 0;
    static uint64_t s_last_log_iter = 0;
    uint64_t now = GetTickCount64();
    if (now - s_last_log_ms < 2000) return;  // 2s cadence
    uint64_t cur = g_cine_iter.load(std::memory_order_relaxed);
    uint64_t delta = cur - s_last_log_iter;
    uint64_t age_ms = (g_cine_last_ms.load() ? now - g_cine_last_ms.load() : 0);
    fprintf(stderr, "[cine-progress] iter=%llu delta=%llu in %llums (idle=%llums)\n",
            (unsigned long long)cur, (unsigned long long)delta,
            (unsigned long long)(now - s_last_log_ms),
            (unsigned long long)age_ms);
    fflush(stderr);
    s_last_log_ms = now;
    s_last_log_iter = cur;
}

extern void print_stack_with_symbols(void** frames, USHORT count);

extern "C" void rs64_cine_dump_if_stuck(void) {
    static std::atomic<bool> s_dumped{false};
    if (s_dumped.load(std::memory_order_relaxed)) return;

    uint64_t last = g_cine_last_ms.load(std::memory_order_relaxed);
    if (last == 0) return;  // never started iterating

    uint64_t now = GetTickCount64();
    if (now - last < 2000) return;  // not stuck yet

    DWORD tid = g_cine_tid.load(std::memory_order_relaxed);
    if (tid == 0) return;

    bool expected = false;
    if (!s_dumped.compare_exchange_strong(expected, true)) return;  // single shot

    fprintf(stderr, "[cine-watchdog] freeze detected: tid=%lu iter=%llu idle=%llums — opening thread\n",
            tid, (unsigned long long)g_cine_iter.load(), (unsigned long long)(now - last));
    fflush(stderr);

    // Try several access masks — some Win10 builds reject the wide masks.
    DWORD masks[] = {
        THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT,
        THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT | THREAD_QUERY_LIMITED_INFORMATION,
        0x1F03FF,  // pre-Vista THREAD_ALL_ACCESS
        0x1FFFFF,  // Vista+ THREAD_ALL_ACCESS
    };
    HANDLE hThread = NULL;
    DWORD last_err = 0;
    for (DWORD m : masks) {
        hThread = OpenThread(m, FALSE, tid);
        if (hThread) {
            fprintf(stderr, "[cine-watchdog] OpenThread succeeded with mask=0x%lX\n", m);
            break;
        }
        last_err = GetLastError();
    }
    if (hThread == NULL) {
        fprintf(stderr, "[cine-watchdog] OpenThread failed for tid=%lu last_err=%lu (cur tid=%lu)\n",
                tid, last_err, GetCurrentThreadId());
        fflush(stderr);
        s_dumped.store(false, std::memory_order_relaxed);
        return;
    }
    fprintf(stderr, "[cine-watchdog] opened, suspending\n"); fflush(stderr);
    DWORD susp = SuspendThread(hThread);
    if (susp == (DWORD)-1) {
        fprintf(stderr, "[cine-watchdog] SuspendThread failed err=%lu\n", GetLastError());
        fflush(stderr);
        CloseHandle(hThread);
        return;
    }
    fprintf(stderr, "[cine-watchdog] suspended (prev count=%lu), getting context\n", susp); fflush(stderr);
    CONTEXT ctx{};
    ctx.ContextFlags = CONTEXT_ALL;
    if (!GetThreadContext(hThread, &ctx)) {
        fprintf(stderr, "[cine-watchdog] GetThreadContext failed err=%lu\n", GetLastError());
        fflush(stderr);
        ResumeThread(hThread);
        CloseHandle(hThread);
        return;
    }
    fprintf(stderr,
        "[cine-watchdog] game thread tid=%lu hung at RIP=0x%llX RSP=0x%llX RBP=0x%llX\n",
        tid, (unsigned long long)ctx.Rip, (unsigned long long)ctx.Rsp, (unsigned long long)ctx.Rbp);
    fflush(stderr);

    // Stack walk.
    STACKFRAME64 frame{};
    frame.AddrPC.Offset    = ctx.Rip; frame.AddrPC.Mode    = AddrModeFlat;
    frame.AddrFrame.Offset = ctx.Rbp; frame.AddrFrame.Mode = AddrModeFlat;
    frame.AddrStack.Offset = ctx.Rsp; frame.AddrStack.Mode = AddrModeFlat;
    void* frames[48];
    USHORT count = 0;
    HANDLE hProcess = GetCurrentProcess();
    SymInitialize(hProcess, NULL, TRUE);
    fprintf(stderr, "[cine-watchdog] walking stack\n"); fflush(stderr);
    while (count < 48) {
        if (!StackWalk64(IMAGE_FILE_MACHINE_AMD64, hProcess, hThread, &frame, &ctx,
                         NULL, SymFunctionTableAccess64, SymGetModuleBase64, NULL))
            break;
        if (frame.AddrPC.Offset == 0) break;
        frames[count++] = (void*)(uintptr_t)frame.AddrPC.Offset;
    }
    fprintf(stderr, "[cine-watchdog] walked %u frames, resuming + symbolizing\n", count); fflush(stderr);
    ResumeThread(hThread);
    CloseHandle(hThread);
    print_stack_with_symbols(frames, count);
    fflush(stderr);
}
#else
extern "C" void rs64_cine_iter_tick(unsigned) {}
extern "C" void rs64_cine_dump_if_stuck(void) {}
#endif

// Yield the cinematic CPU thread every N iterations to break the iter-810
// OS-level thread starvation stall. Empirically a kernel I/O call (stderr
// flush) unsticks it; Win32 Sleep alone does not. SwitchToThread yields to
// any ready thread on the same CPU.
extern "C" void rs64_cine_yield(void) {
    static int s_count = 0;
    ++s_count;
    // ~Every 16 iters: yield + flush stderr. Cheap enough to do hot.
    if ((s_count & 0xF) == 0) {
#ifdef _WIN32
        ::SwitchToThread();
#else
        std::this_thread::yield();
#endif
        std::fflush(stderr);
    }
}

// Pace the 32-iteration attribution-display loop inside
// runIdleFramesAndLoadSaveData (each iter renders one attribution frame).
// On real N64, each iter waits for the previous frame to complete via
// waitForPrevFrameDone → waitForPostSwapAck → which we patched to NOBLOCK
// (boot deadlock workaround). Without the wait, all 32 frames flash by in
// <1ms and the attribution screen is never visible.
// Sleep here so attribution displays for ~5 seconds (configurable).
//
// ROGUESQ_ATTRIBUTION_SLEEP_MS=N (default 150ms × 32 iters ≈ 4.8 sec).
// Set to 0 to disable.
extern "C" void rs64_idle_pace(void) {
#ifdef _WIN32
    static int s_sleep_ms = -1;
    if (s_sleep_ms < 0) {
        const char* e = std::getenv("ROGUESQ_ATTRIBUTION_SLEEP_MS");
        s_sleep_ms = (e && *e) ? std::atoi(e) : 150;
        if (s_sleep_ms < 0) s_sleep_ms = 0;
        if (s_sleep_ms > 5000) s_sleep_ms = 5000;
        fprintf(stderr, "[idle-pace] attribution sleep_ms=%d (32 iters ≈ %ds total)\n",
                s_sleep_ms, (s_sleep_ms * 32) / 1000);
        fflush(stderr);
    }
    if (s_sleep_ms == 0) return;
    ::Sleep((DWORD)s_sleep_ms);
#endif
}

// Pace cinematicLoopBody to a target frame rate. Without this, the loop
// runs at >1000 Hz on the host (no pacing from NOBLOCK-patched osRecvMesg
// waits), racing through the cinematic in <2 seconds and skipping past
// the attribution screen, fade, and N64-logo segments before they're
// visible. Default 30 Hz to match N64 native cinematic rate.
// Configure via ROGUESQ_CINE_TARGET_FPS env var: 0 = disabled, positive
// int = target FPS.
extern "C" void rs64_cine_pace(void) {
#ifdef _WIN32
    static int s_target_fps = -1;
    if (s_target_fps < 0) {
        const char* e = std::getenv("ROGUESQ_CINE_TARGET_FPS");
        s_target_fps = (e && *e) ? std::atoi(e) : 30;
        if (s_target_fps < 0) s_target_fps = 0;
        if (s_target_fps > 240) s_target_fps = 240;
        fprintf(stderr, "[cine-pace] init target_fps=%d (env='%s')\n",
                s_target_fps, e ? e : "(null)");
        fflush(stderr);
        // Bump Windows timer resolution to 1ms so Sleep(33) actually sleeps
        // ~33ms instead of the default ~15.6ms quantum.
        timeBeginPeriod(1);
    }
    if (s_target_fps == 0) return;  // disabled
    uint32_t target_interval_ms = 1000u / (uint32_t)s_target_fps;
    static uint64_t s_last_ms = 0;
    static uint32_t s_calls = 0;
    static uint32_t s_sleeps = 0;
    uint64_t now = GetTickCount64();
    if (s_last_ms == 0) {
        s_last_ms = now;
        return;
    }
    uint64_t elapsed = now - s_last_ms;
    if (elapsed < (uint64_t)target_interval_ms) {
        ::Sleep((DWORD)(target_interval_ms - elapsed));
        ++s_sleeps;
    }
    s_last_ms = GetTickCount64();
    ++s_calls;
    if (s_calls <= 5 || (s_calls & 0x3F) == 0) {
        fprintf(stderr, "[cine-pace] call=%u sleeps=%u elapsed=%llums interval=%ums\n",
                s_calls, s_sleeps, (unsigned long long)elapsed, target_interval_ms);
        fflush(stderr);
    }
#endif
}

// Diagnostic helper for [[patches.hook]] entries that need to log to
// stderr — the hook code lives in funcs_*.c which doesn't include stdio.
// Format args: 4 unsigned 32-bit values + a tag string.
extern "C" void rs64_dbg_log4(const char* tag, unsigned a, unsigned b, unsigned c, unsigned d) {
    static int s_log = -1;
    if (s_log < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_HOOKS");
        s_log = (e && *e && *e != '0') ? 1 : 0;
    }
    if (!s_log) return;
    fprintf(stderr, "[hook] %s a=0x%08X b=0x%08X c=0x%08X d=0x%08X\n",
            tag ? tag : "?", a, b, c, d);
    fflush(stderr);
}

// Optional task-submission diagnostic. Gated by ROGUESQ_LOG_TASKSUBMIT.
// When enabled, logs task type + data_ptr/size + first 32 bytes of the DL
// buffer for the first 4 tasks + every 64th. Originally added 2026-05-09
// to investigate why GFX tasks were submitted with data_size=0; finding:
// Factor 5's task protocol uses data_ptr but ignores data_size (the DL
// chains via G_DL jumps to static setup code in .text). data_size=0 is
// normal for Factor 5 cinematic tasks.
extern void print_stack_with_symbols(void** frames, USHORT count);
extern "C" void rs64_set_pending_task_guest_ptr(uint32_t guest_ptr);
extern "C" void rs64_m5_descriptor_start(uint8_t* rdram, uint32_t task_ptr);
extern "C" void rs64_sp_reset_yield_request();

static bool rs64_guest_range_valid(uint64_t addr, uint64_t size) {
    constexpr uint64_t kseg0_base = 0xFFFFFFFF80000000ull;
    constexpr uint64_t kseg0_end = 0xFFFFFFFF80800000ull;
    if (addr >= kseg0_base && size <= kseg0_end - addr) return true;

    const uint32_t low = static_cast<uint32_t>(addr);
    return (addr >> 32) == 0 && low >= 0x80000000u &&
           size <= 0x00800000ull - (low - 0x80000000u);
}

extern "C" void osSpTaskStartGo_recomp(uint8_t* rdram, recomp_context* ctx) {
    if (!rs64_guest_range_valid(static_cast<uint64_t>(ctx->r4), sizeof(OSTask))) {
        ctx->r2 = 0;
        return;
    }
    rs64_sp_reset_yield_request();
    rs64_m5_descriptor_start(rdram, (uint32_t)ctx->r4);
    rs64_set_pending_task_guest_ptr((uint32_t)ctx->r4);
    static int s_log = -1;
    if (s_log < 0) {
        const char* e = std::getenv("ROGUESQ_LOG_TASKSUBMIT");
        s_log = (e && *e && *e != '0') ? 1 : 0;
    }
    // Separate gate: print host-side stack on first GFX submit so we can
    // identify which game thread / function chain is driving submission.
    // One-shot per task type — once we know who submits GFX vs audio, the
    // log is noise.
    {
        static int s_log_stk = -1;
        if (s_log_stk < 0) {
            const char* e = std::getenv("ROGUESQ_LOG_TASKSUBMIT_STACK");
            s_log_stk = (e && *e && *e != '0') ? 1 : 0;
        }
        if (s_log_stk) {
            OSTask* task = TO_PTR(OSTask, ctx->r4);
            static bool s_logged_gfx = false;
            static bool s_logged_audio = false;
            const bool is_gfx = (task->t.type == 1u);
            const bool is_audio = (task->t.type == 2u);
            if ((is_gfx && !s_logged_gfx) || (is_audio && !s_logged_audio)) {
                if (is_gfx) s_logged_gfx = true;
                if (is_audio) s_logged_audio = true;
                fprintf(stderr,
                    "[task-submit-stack] tid=%lu type=0x%X data_ptr=0x%08X ucode=0x%08X\n",
                    GetCurrentThreadId(),
                    (unsigned)task->t.type,
                    (unsigned)task->t.data_ptr,
                    (unsigned)task->t.ucode);
                void* frames[24];
                USHORT count = RtlCaptureStackBackTrace(0, 24, frames, nullptr);
                print_stack_with_symbols(frames, count);
                fflush(stderr);
            }
        }
    }
    if (s_log) {
        OSTask* task = TO_PTR(OSTask, ctx->r4);
        static int n = 0;
        ++n;
        // Log first 4, every 64th, AND every GFX task regardless of count
        // (audio tasks fire at high rate and would mask GFX in normal sampling).
        const bool is_gfx = (task->t.type == 1u);
        if (n <= 4 || (n & 63) == 0 || is_gfx) {
            fprintf(stderr,
                "[task-submit #%d] type=0x%X flags=0x%X data_ptr=0x%08X data_size=%u ucode=0x%08X ucode_size=%u\n",
                n,
                (unsigned)task->t.type,
                (unsigned)task->t.flags,
                (unsigned)task->t.data_ptr,
                (unsigned)task->t.data_size,
                (unsigned)task->t.ucode,
                (unsigned)task->t.ucode_size);
            uint32_t dp = (uint32_t)task->t.data_ptr;
            if (task->t.type == M_GFXTASK && dp >= 0x80000000u && dp < 0x80800000u) {
                uint32_t off = dp - 0x80000000u;
                fprintf(stderr, "  data_ptr[0..32]:");
                for (int i = 0; i < 32; ++i) {
                    fprintf(stderr, " %02X", (unsigned)rdram[(off + i) ^ 3]);
                }
                fprintf(stderr, "\n");
            }
            fflush(stderr);
        }
    }
    ultramodern::submit_rsp_task(rdram, ctx->r4);
}

// Optional sender-trace for osSendMesg. Captures host stack on the first
// send to each unique queue address — quickly maps which game functions
// drive which queues. Gated by ROGUESQ_LOG_SENDMESG_STACK=1.
//
// We override the librecomp default (link warning re: duplicate symbol is
// expected; lld-link picks our version). The behavior is identical otherwise.
extern "C" int32_t osSendMesg(uint8_t* rdram, int32_t mq_, OSMesg mesg, s32 flag);
extern "C" int32_t osRecvMesg(uint8_t* rdram, int32_t mq_, PTR(OSMesg) mesg, s32 flag);
extern "C" uint32_t rs64_phase_ord(void);

static void log_m5_frame_sync_edge(uint8_t* rdram, const char* edge,
                                   uint32_t mq_addr, uint32_t msg,
                                   int32_t flag) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FRAME_SYNC");
        return (all && *all && *all != '0') || (own && *own && *own != '0');
    }();
    if (!enabled || (mq_addr != 0x80138D10u && mq_addr != 0x80128CF0u)) return;
    static std::atomic<uint32_t> rows{0};
    const uint32_t phase = rs64_phase_ord();
    const uint32_t row = rows.fetch_add(1, std::memory_order_relaxed);
    if (phase >= 4u && row >= 256u) return;
    std::fprintf(stderr,
        "[m5-frame-sync] row=%u phase=%u edge=%s guest_pc=0x%08X mq=0x%08X "
        "msg=0x%08X flag=%d valid=%d first=%d count=%d\n",
        row, phase, edge, (unsigned)g_rs64_last_guest_pc, mq_addr, msg,
        (int)flag, (int)TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq_addr)->validCount,
        (int)TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq_addr)->first,
        (int)TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))mq_addr)->msgCount);
    std::fflush(stderr);
    if (row == 0) {
        std::fprintf(stderr, "[m5-frame-sync-positive] wrapper edge is live\n");
        std::fflush(stderr);
    }
}

static void log_a1_queue_boundary(uint32_t mq_addr, PTR(OSMesg) msg, s32 flag,
                                  int32_t result, const OSMesgQueue& before,
                                  const OSMesgQueue& after) {
    static const bool enabled = [] {
        const char* e = std::getenv("ROGUESQ_LOG_A1_QUEUE");
        return e && *e && *e != '0';
    }();
    if (!enabled || mq_addr != 0x8010FEE0u) return;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase >= 4u && rows >= 256u) return;
    ++rows;
    std::fprintf(stderr,
        "[a1-queue] row=%u phase=%u guest_pc=0x%08X mq=0x%08X msg=0x%08X flag=%d "
        "pre_valid=%d pre_first=%d pre_count=%d pre_msg=0x%08X result=%d "
        "post_valid=%d post_first=%d post_count=%d post_msg=0x%08X\n",
        rows, phase, (unsigned)g_rs64_last_guest_pc, mq_addr, (uint32_t)msg, (int)flag,
        before.validCount, before.first, before.msgCount, (uint32_t)before.msg,
        (int)result, after.validCount, after.first, after.msgCount, (uint32_t)after.msg);
    std::fflush(stderr);
}

static bool submit_boundary_log_enabled() {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* specific = std::getenv("ROGUESQ_LOG_SUBMIT_BOUNDARY");
        return (all && *all && *all != '0') || (specific && *specific && *specific != '0');
    }();
    return enabled;
}

static void log_submit_boundary(uint8_t* rdram, const char* kind, uint32_t mq, uint32_t flag) {
    if (!submit_boundary_log_enabled()) return;
    static std::atomic<uint32_t> phase_seen{0xFFFFFFFFu};
    static std::atomic<uint32_t> phase_rows{0};
    const uint32_t phase = rs64_phase_ord();
    uint32_t prior = phase_seen.load(std::memory_order_relaxed);
    if (prior != phase && phase_seen.compare_exchange_strong(prior, phase, std::memory_order_relaxed)) {
        phase_rows.store(0, std::memory_order_relaxed);
    }
    const uint32_t row = phase_rows.fetch_add(1, std::memory_order_relaxed);
    if (row >= 256) return;
    const uint32_t gate0 = rdram[0x11A89Fu ^ 3u];
    const uint32_t gate1 = rdram[0x11A8A0u ^ 3u];
    const uint32_t obj = mq == 0x8011A408u ? 0x11A408u : 0u;
    std::fprintf(stderr,
        "[submit-boundary] phase=%u row=%u kind=%s mq=0x%08X flag=%u guest_pc=0x%08X gate89f=%u gate8a0=%u obj_valid=%u obj_msg=0x%08X obj_count=%u\n",
        phase, row, kind, mq, flag, (unsigned)g_rs64_last_guest_pc,
        gate0, gate1, obj ? 1u : 0u,
        obj ? ((uint32_t)rdram[(obj + 0x0Cu) ^ 3u] << 24 |
               (uint32_t)rdram[(obj + 0x0Du) ^ 3u] << 16 |
               (uint32_t)rdram[(obj + 0x0Eu) ^ 3u] << 8 |
               (uint32_t)rdram[(obj + 0x0Fu) ^ 3u]) : 0u,
        obj ? ((uint32_t)rdram[(obj + 0x08u) ^ 3u] << 24 |
               (uint32_t)rdram[(obj + 0x09u) ^ 3u] << 16 |
               (uint32_t)rdram[(obj + 0x0Au) ^ 3u] << 8 |
               (uint32_t)rdram[(obj + 0x0Bu) ^ 3u]) : 0u);
    std::fflush(stderr);
}

static void log_m5_dp_event_boundary(const char* edge, uint32_t mq_addr,
                                     uint32_t msg, int32_t flag, int32_t result,
                                     const OSMesgQueue& before,
                                     const OSMesgQueue& after) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_DP_EVENT");
        return (all && *all && *all != '0') || (own && *own && *own != '0');
    }();
    if (!enabled || mq_addr != 0x8011A408u) return;
    static std::atomic<uint32_t> phase_seen{0xFFFFFFFFu};
    static std::atomic<uint32_t> phase_rows{0};
    const uint32_t phase = rs64_phase_ord();
    uint32_t prior = phase_seen.load(std::memory_order_relaxed);
    if (prior != phase && phase_seen.compare_exchange_strong(
            prior, phase, std::memory_order_relaxed)) {
        phase_rows.store(0, std::memory_order_relaxed);
    }
    const uint32_t row = phase_rows.fetch_add(1, std::memory_order_relaxed);
    if (row >= 256u) return;
    std::fprintf(stderr,
        "[m5-dp-event] phase=%u row=%u edge=%s guest_pc=0x%08X mq=0x%08X "
        "msg=0x%08X flag=%d result=%d pre_valid=%d pre_first=%d pre_count=%d "
        "pre_msg=0x%08X post_valid=%d post_first=%d post_count=%d post_msg=0x%08X\n",
        phase, row, edge, (unsigned)g_rs64_last_guest_pc, mq_addr, msg, (int)flag,
        (int)result, before.validCount, before.first, before.msgCount,
        (uint32_t)before.msg, after.validCount, after.first, after.msgCount,
        (uint32_t)after.msg);
    std::fflush(stderr);
    if (row == 0) {
        std::fprintf(stderr, "[m5-dp-event-positive] DP queue wrapper is live\n");
        std::fflush(stderr);
    }
}

// VI-640 blocked-thread graph (temp, env-gated). Stable host tid, not guest pc.
static bool recv_trace_enabled() {
    static const bool enabled = [] {
        const char* e = std::getenv("ROGUESQ_RECV_TRACE");
        return e && *e && *e != '0';
    }();
    return enabled;
}

static bool sendmesg_stack_enabled() {
    static const bool enabled = [] {
        const char* e = std::getenv("ROGUESQ_LOG_SENDMESG_STACK");
        return e && *e && *e != '0';
    }();
    return enabled;
}

struct RecvMqStat {
    uint32_t mq = 0;
    uint64_t last_tid = 0;
    uint32_t guest_tid = 0;
    uint32_t rplus = 0;
    uint32_t rminus = 0;
    uint32_t sends = 0;
    uint32_t logged_rplus = 0;
    uint32_t logged_rminus = 0;
    uint32_t stack_logged = 0;
    uint32_t send_stack_logged = 0;
};

static constexpr uint32_t kRecvMqCap = 384;
static RecvMqStat g_recv_stats[kRecvMqCap];
static std::atomic<uint32_t> g_recv_n{0};
static std::recursive_mutex g_recv_mu;

static uint32_t rs64_guest_tid(uint8_t* rdram) {
    PTR(OSThread) t = ultramodern::this_thread();
    if (!t) return 0;
    return (uint32_t)TO_PTR(OSThread, t)->id;
}

static RecvMqStat* recv_stat_for(uint32_t mq) {
    std::lock_guard<std::recursive_mutex> lock(g_recv_mu);
    const uint32_t n = g_recv_n.load(std::memory_order_relaxed);
    for (uint32_t i = 0; i < n && i < kRecvMqCap; i++) {
        if (g_recv_stats[i].mq == mq) return &g_recv_stats[i];
    }
    if (n >= kRecvMqCap) return nullptr;
    g_recv_stats[n].mq = mq;
    g_recv_n.store(n + 1, std::memory_order_relaxed);
    return &g_recv_stats[n];
}

static void recv_trace_dump() {
    RecvMqStat copy[kRecvMqCap];
    uint32_t n = 0;
    {
        std::lock_guard<std::recursive_mutex> lock(g_recv_mu);
        n = g_recv_n.load(std::memory_order_relaxed);
        if (n > kRecvMqCap) n = kRecvMqCap;
        for (uint32_t i = 0; i < n; i++) copy[i] = g_recv_stats[i];
    }
    const uint64_t ms = GetTickCount64();
    uint32_t blocked = 0;
    for (uint32_t i = 0; i < n; i++) {
        const RecvMqStat& s = copy[i];
        const int32_t net = (int32_t)s.rplus - (int32_t)s.rminus;
        if (net > 0) blocked++;
        std::fprintf(stderr,
            "[recvsum] t_ms=%llu mq=0x%08X tid=%lu gid=%u R+=%u R-=%u net=%d S+=%u\n",
            (unsigned long long)ms, s.mq, (unsigned long)s.last_tid, s.guest_tid,
            s.rplus, s.rminus, (int)net, s.sends);
    }
    std::fprintf(stderr, "[recvsum] t_ms=%llu queues=%u blocked=%u\n",
        (unsigned long long)ms, n, blocked);
    std::fflush(stderr);
}

static void recv_trace_start_dumper() {
    static std::once_flag once;
    std::call_once(once, [] {
        std::fprintf(stderr, "[recvtrace] enabled=1 dumper=10s\n");
        std::fflush(stderr);
        std::thread([] {
            for (;;) {
                std::this_thread::sleep_for(std::chrono::seconds(10));
                recv_trace_dump();
            }
        }).detach();
    });
}

static void recv_trace_enter(uint8_t* rdram, uint32_t mq, int32_t flag, uint64_t tid) {
    if (!recv_trace_enabled() || flag != OS_MESG_BLOCK) return;
    recv_trace_start_dumper();
    RecvMqStat* s = recv_stat_for(mq);
    if (!s) return;
    const uint32_t gid = rs64_guest_tid(rdram);
    bool want_line = false;
    bool want_stack = false;
    {
        std::lock_guard<std::recursive_mutex> lock(g_recv_mu);
        s->last_tid = tid;
        s->guest_tid = gid;
        s->rplus++;
        if (s->logged_rplus < 8) {
            s->logged_rplus++;
            want_line = true;
        }
        if (s->stack_logged == 0) {
            s->stack_logged = 1;
            want_stack = true;
        }
    }
    if (want_line) {
        std::fprintf(stderr, "[recvtrace] R+ mq=0x%08X flag=%d tid=%lu gid=%u\n",
            mq, (int)flag, (unsigned long)tid, gid);
        std::fflush(stderr);
    }
    if (mq == 0x8011A818u) {
        auto be_u8 = [&](uint32_t kseg) -> unsigned {
            const uint32_t phys = kseg - 0x80000000u;
            return (unsigned)rdram[phys ^ 3u];
        };
        std::fprintf(stderr,
            "[framesync-gate] mq=0x8011A818 89C=%u 89D=%u 89E=%u 89F=%u 8A0=%u 28D44=%u\n",
            be_u8(0x8011A89Cu), be_u8(0x8011A89Du), be_u8(0x8011A89Eu),
            be_u8(0x8011A89Fu), be_u8(0x8011A8A0u), be_u8(0x80128D44u));
        std::fflush(stderr);
    }
    if (want_stack) {
        std::fprintf(stderr, "[recvbt] mq=0x%08X tid=%lu gid=%u\n",
            mq, (unsigned long)tid, gid);
        void* frames[24];
        USHORT count = RtlCaptureStackBackTrace(0, 24, frames, nullptr);
        print_stack_with_symbols(frames, count);
        std::fflush(stderr);
    }
}

static void recv_trace_exit(uint32_t mq, int32_t flag, uint64_t tid, int32_t result) {
    if (!recv_trace_enabled() || flag != OS_MESG_BLOCK) return;
    RecvMqStat* s = recv_stat_for(mq);
    if (!s) return;
    bool want_line = false;
    {
        std::lock_guard<std::recursive_mutex> lock(g_recv_mu);
        s->rminus++;
        if (s->logged_rminus < 8) {
            s->logged_rminus++;
            want_line = true;
        }
    }
    if (want_line) {
        std::fprintf(stderr, "[recvtrace] R- mq=0x%08X tid=%lu r=%d\n",
            mq, (unsigned long)tid, (int)result);
        std::fflush(stderr);
    }
}

static void recv_trace_scheduler_type(uint8_t* rdram, uint32_t msg_addr,
                                      int32_t result) {
    if (!recv_trace_enabled() || result != 0 || msg_addr < 0x80000000u ||
        msg_addr >= 0x80800000u) return;
    static std::atomic<uint32_t> rows{0};
    const uint32_t row = rows.fetch_add(1, std::memory_order_relaxed);
    if (row >= 256u) return;
    const uint32_t msg_phys = msg_addr - 0x80000000u;
    const unsigned type = (unsigned)rdram[msg_phys ^ 3u];
    auto be_u8 = [&](uint32_t kseg) -> unsigned {
        const uint32_t p = kseg - 0x80000000u;
        return (unsigned)rdram[p ^ 3u];
    };
    std::fprintf(stderr,
        "[recv-scheduler-type] phase=%u row=%u msg=0x%08X type=0x%02X "
        "89F=%u 28D44=%u\n",
        rs64_phase_ord(), row, msg_addr, type, be_u8(0x8011A89Fu),
        be_u8(0x80128D44u));
    std::fflush(stderr);
}

extern "C" void rs64_m5_scheduler_recv_identity(uint8_t* rdram, uint32_t pc,
                                                   uint32_t caller,
                                                   uint32_t output_slot,
                                                   uint32_t result) {
    if (!recv_trace_enabled() || result != 0 || rdram == nullptr) return;
    if (output_slot < 0x80000000u || output_slot >= 0x80800000u) return;
    const uint32_t slot_phys = output_slot - 0x80000000u;
    const uint32_t msg_addr =
        (static_cast<uint32_t>(rdram[slot_phys ^ 3u]) << 24) |
        (static_cast<uint32_t>(rdram[(slot_phys + 1u) ^ 3u]) << 16) |
        (static_cast<uint32_t>(rdram[(slot_phys + 2u) ^ 3u]) << 8) |
        static_cast<uint32_t>(rdram[(slot_phys + 3u) ^ 3u]);
    unsigned type = 0xFFu;
    if (msg_addr >= 0x80000000u && msg_addr < 0x80800000u) {
        type = rdram[(msg_addr - 0x80000000u) ^ 3u];
    }
    static std::atomic<uint32_t> bucket{0xFFFFFFFFu};
    static std::atomic<uint32_t> rows{0};
    const uint32_t phase = rs64_phase_ord();
    if (bucket.load(std::memory_order_relaxed) != phase &&
        bucket.exchange(phase, std::memory_order_relaxed) != phase) {
        rows.store(0, std::memory_order_relaxed);
    }
    const uint32_t row = rows.fetch_add(1, std::memory_order_relaxed);
    if (row >= 256u) return;
    auto be_u8 = [rdram](uint32_t guest) -> unsigned {
        if (guest < 0x80000000u || guest >= 0x80800000u) return 0xFFu;
        return rdram[(guest - 0x80000000u) ^ 3u];
    };
    std::fprintf(stderr,
        "[recv-scheduler-identity] phase=%u row=%u pc=0x%08X caller=0x%08X "
        "slot=0x%08X msg=0x%08X type=0x%02X 89F=%u 28D44=%u\n",
        phase, row, pc, caller, output_slot, msg_addr, type,
        be_u8(0x8011A89Fu), be_u8(0x80128D44u));
    std::fflush(stderr);
}

static void sendtgt_note(uint32_t mq, uint64_t tid, bool want_stack) {
    if (!recv_trace_enabled() && !want_stack) return;
    if (recv_trace_enabled()) recv_trace_start_dumper();
    RecvMqStat* s = recv_stat_for(mq);
    if (!s) return;
    bool first = false;
    bool do_stack = false;
    {
        std::lock_guard<std::recursive_mutex> lock(g_recv_mu);
        s->sends++;
        if (s->sends == 1) first = true;
        if (want_stack && s->send_stack_logged == 0) {
            s->send_stack_logged = 1;
            do_stack = true;
        }
    }
    if (first && recv_trace_enabled()) {
        std::fprintf(stderr, "[sendtgt] mq=0x%08X tid=%lu\n", mq, (unsigned long)tid);
        std::fflush(stderr);
    }
    if (do_stack) {
        std::fprintf(stderr, "[sendmesg] tid=%lu mq=0x%08X\n", (unsigned long)tid, mq);
        void* frames[24];
        USHORT count = RtlCaptureStackBackTrace(0, 24, frames, nullptr);
        print_stack_with_symbols(frames, count);
        std::fflush(stderr);
    }
}

struct Rs64M5FrequencyPending {
    uint32_t queue;
    uint32_t msg;
    uint32_t callsite;
    uint32_t state;
    bool valid;
};

static thread_local Rs64M5FrequencyPending g_rs64_m5_frequency_pending{0, 0, 0, 0, false};

struct Rs64M5PointerCandidate {
    uint32_t pc;
    uint32_t addr;
    uint32_t value;
    uint32_t phase;
};

static thread_local Rs64M5PointerCandidate g_rs64_m5_pointer_latest[4]{};

struct Rs64M5ZcfreeEdge {
    uint32_t s1;
    uint32_t a0;
    uint32_t ra;
    uint32_t ordinal;
    bool valid;
};

static thread_local Rs64M5ZcfreeEdge g_rs64_m5_zcfree_edge{0, 0, 0, 0, false};

extern "C" void rs64_m5_state_pointer_entry(uint8_t* rdram,
                                               recomp_context* ctx) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool title_phase = width == 1024u &&
        (origin == 0x00790400u || origin == 0x00790800u);
    const bool hangar_phase = width == 512u &&
        (origin == 0x006AB400u || origin == 0x006AB800u);
    if (!title_phase && !hangar_phase) return;
    const uint32_t s1 = U32(ctx->r17);
    if (!((s1 >= 0x80194000u && s1 < 0x80196000u) ||
          (s1 >= 0x801B0000u && s1 < 0x801C0000u))) return;
    extern void rs64_m5_state_pointer_consumer(uint32_t s1);
    rs64_m5_state_pointer_consumer(s1);
    static uint32_t rows = 0;
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-state-pointer-entry] ordinal=%u phase=%u width=%u origin=0x%06X "
        "s1=0x%08X state_word=0x%08X a0=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, s1,
        U32(MEM_W(0, ctx->r17)), U32(ctx->r4), U32(ctx->r31));
    std::fflush(stderr);
}

static thread_local uint32_t g_rs64_m5_state_call_pc = 0;
static thread_local uint32_t g_rs64_m5_state_call_s0 = 0;

extern "C" void rs64_m5_state_pointer_callsite(recomp_context* ctx,
                                                 uint32_t call_pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 1024u) return;
    g_rs64_m5_state_call_pc = call_pc;
    g_rs64_m5_state_call_s0 = U32(ctx->r16);
    std::fprintf(stderr,
        "[m5-state-pointer-callsite] ordinal=%u phase=%u width=%u origin=0x%06X "
        "call_pc=0x%08X s0=0x%08X s1=0x%08X a0=0x%08X a1=0x%08X "
        "a2=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, call_pc, U32(ctx->r16),
        U32(ctx->r17), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_zcfree_edge(recomp_context* ctx) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    g_rs64_m5_zcfree_edge = {U32(ctx->r17), U32(ctx->r4), U32(ctx->r31), rows++, true};
    if (g_rs64_m5_zcfree_edge.ordinal >= 1024u) return;
    std::fprintf(stderr,
        "[m5-zcfree-edge] ordinal=%u phase=%u width=%u origin=0x%06X "
        "s1=0x%08X a0=0x%08X ra=0x%08X\n",
        g_rs64_m5_zcfree_edge.ordinal, rs64_phase_ord(), width, origin,
        g_rs64_m5_zcfree_edge.s1, g_rs64_m5_zcfree_edge.a0,
        g_rs64_m5_zcfree_edge.ra);
    std::fflush(stderr);
    if (g_rs64_m5_zcfree_edge.ordinal == 0) {
        std::fprintf(stderr, "[m5-zcfree-edge-positive] sole caller edge is live\n");
        std::fflush(stderr);
    }
}

struct Rs64M5DownstreamStore {
    uint32_t pc;
    uint32_t addr;
    uint32_t value;
    uint32_t edge_ordinal;
    uint32_t edge_s1;
    uint32_t ordinal;
};

static thread_local Rs64M5DownstreamStore g_rs64_m5_downstream_latest{0, 0, 0, 0, 0, 0};

extern "C" void rs64_m5_downstream_store(uint8_t* rdram, recomp_context* ctx,
                                           char width, uint32_t pc,
                                           uint32_t addr, uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_DOWNSTREAM");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    static const bool late_only = [] {
        const char* e = std::getenv("ROGUESQ_M5_DOWNSTREAM_LATE_ONLY");
        return e && e[0] && e[0] != '0';
    }();
    if (late_only && pc < 0x80001DFCu) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows >= 2048u) return;
    g_rs64_m5_downstream_latest = {
        pc, addr, value, g_rs64_m5_zcfree_edge.ordinal,
        g_rs64_m5_zcfree_edge.s1, rows
    };
    if (rows == 0) {
        std::fprintf(stderr, "[m5-downstream-store-positive] downstream store census is live\n");
        std::fflush(stderr);
    }
    std::fprintf(stderr,
        "[m5-downstream-store] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "pc=0x%08X width=%c addr=0x%08X value=0x%08X edge_ord=%u edge_s1=0x%08X "
        "caller_s1=0x%08X caller_ra=0x%08X\n",
        rows++, rs64_phase_ord(), origin, pc, width, U32(addr), U32(value),
        g_rs64_m5_zcfree_edge.ordinal, g_rs64_m5_zcfree_edge.s1,
        U32(ctx->r17), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_producer_input(uint8_t* rdram,
                                         recomp_context* ctx,
                                         uint32_t producer_pc,
                                         uint32_t call_pc,
                                         uint32_t target_pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_OUTPUT_STATE_FIELDS");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows >= 1024u) return;
    const uint32_t source_ptr = U32(ctx->r4);
    const uint32_t source_word =
        (source_ptr >= 0x80000000u && source_ptr <= 0x807FFFFCu)
            ? (static_cast<uint32_t>(rdram[source_ptr - 0x80000000u]) << 24 |
               static_cast<uint32_t>(rdram[source_ptr - 0x80000000u + 1]) << 16 |
               static_cast<uint32_t>(rdram[source_ptr - 0x80000000u + 2]) << 8 |
               static_cast<uint32_t>(rdram[source_ptr - 0x80000000u + 3]))
            : 0xFFFFFFFFu;
    std::fprintf(stderr,
        "[m5-producer-input] ordinal=%u phase=%u width=%u origin=0x%06X "
        "producer_pc=0x%08X source_ptr=0x%08X source_word=0x%08X "
        "loaded_s0=0x%08X call_pc=0x%08X target_pc=0x%08X s1=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, producer_pc, source_ptr,
        source_word, U32(ctx->r16), call_pc, target_pc, U32(ctx->r17),
        U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_output_state_fields(uint8_t* rdram,
                                                recomp_context* ctx,
                                                uint32_t pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_OUTPUT_STATE_FIELDS");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows >= 2048u) return;
    const uint32_t s0 = U32(ctx->r16);
    const uint32_t s1 = U32(ctx->r17);
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = (guest - 0x80000000u) ^ 3u;
        return (static_cast<uint32_t>(rdram[p]) << 24) |
               (static_cast<uint32_t>(rdram[p + 1]) << 16) |
               (static_cast<uint32_t>(rdram[p + 2]) << 8) |
               static_cast<uint32_t>(rdram[p + 3]);
    };
    auto byte = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= 0x80800000u) return 0xFFFFFFFFu;
        return rdram[guest - 0x80000000u];
    };
    std::fprintf(stderr,
        "[m5-output-state-fields] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X s0=0x%08X s1=0x%08X source_word=0x%08X "
        "branch_selector=0x%08X source_byte=0x%02X branch_state=0x%04X "
        "output_v0=0x%08X output_v1=0x%08X state_word=0x%08X "
        "a0=0x%08X a1=0x%08X ra=0x%08X pre_call_pc=0x%08X "
        "pre_call_s0=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, s0, s1,
        word(s0 + 0x60u), U32(ctx->r2), byte(s0 + 0x22u),
        word(s1 + 0x22u) & 0xFFFFu, U32(ctx->r2), U32(ctx->r3),
        word(s1), U32(ctx->r4), U32(ctx->r5), U32(ctx->r31),
        g_rs64_m5_state_call_pc, g_rs64_m5_state_call_s0);
    std::fflush(stderr);
    if (rows == 1) {
        std::fprintf(stderr, "[m5-output-state-fields-positive] four-PC schema witness is live\n");
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_table_selection(uint8_t* rdram,
                                           recomp_context* ctx,
                                           uint32_t pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_TABLE_SELECTION");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows >= 2048u) return;
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return (static_cast<uint32_t>(rdram[p]) << 24) |
               (static_cast<uint32_t>(rdram[p + 1]) << 16) |
               (static_cast<uint32_t>(rdram[p + 2]) << 8) |
               static_cast<uint32_t>(rdram[p + 3]);
    };
    const uint32_t entry = U32(ctx->r3);
    const uint32_t selected = U32(ctx->r16);
    std::fprintf(stderr,
        "[m5-table-selection] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X entry=0x%08X index=0x%08X table_base=0x%08X "
        "selected=0x%08X selected_word=0x%08X a0=0x%08X s1=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, entry, U32(ctx->r6),
        word(U32(ctx->r17)), selected, word(selected), U32(ctx->r4),
        U32(ctx->r17), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_state_pointer_checkpoint(uint8_t* rdram,
                                                    recomp_context* ctx,
                                                    const char* edge) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool title_phase = width == 1024u &&
        (origin == 0x00790400u || origin == 0x00790800u);
    const bool hangar_phase = width == 512u &&
        (origin == 0x006AB400u || origin == 0x006AB800u);
    if (!title_phase && !hangar_phase) return;
    static uint32_t rows = 0;
    if (rows >= 1024u) return;
    const uint32_t s1 = U32(ctx->r17);
    if (!((s1 >= 0x80194000u && s1 < 0x80196000u) ||
          (s1 >= 0x801B0000u && s1 < 0x801C0000u))) return;
    std::fprintf(stderr,
        "[m5-state-pointer-checkpoint] edge=%s ordinal=%u phase=%u width=%u "
        "origin=0x%06X s1=0x%08X state_word=0x%08X state=0x%08X "
        "output_v0=0x%08X output_v1=0x%08X a0=0x%08X a1=0x%08X ra=0x%08X\n",
        edge, rows++, rs64_phase_ord(), width, origin, s1,
        U32(MEM_W(0, ctx->r17)), U32(ctx->r16), U32(ctx->r2), U32(ctx->r3),
        U32(ctx->r4), U32(ctx->r5), U32(ctx->r31));
    std::fflush(stderr);
    if (rows == 1) {
        std::fprintf(stderr, "[m5-state-pointer-checkpoint-positive] ordered witness is live\n");
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_pointer_span_store(char width, uint32_t pc,
                                             uint32_t addr, uint32_t value) {
    static const bool source_span_enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SOURCE_SPAN");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    const uint32_t source_phys = addr & 0x1FFFFFFFu;
    const uint32_t source_size = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
    const uint32_t source_origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool source_title = rs64_vi_committed_width() == 1024u &&
        (source_origin == 0x00790400u || source_origin == 0x00790800u);
    const bool source_hit = source_phys < 0x0018DD50u &&
        source_phys + source_size > 0x0018DD20u;
    const bool source_hit2 = source_phys < 0x0018FB90u &&
        source_phys + source_size > 0x0018FB60u;
    if (source_span_enabled && source_title && (source_hit || source_hit2)) {
        static uint32_t source_rows = 0;
        static bool source_control = false;
        if (!source_control) {
            std::fprintf(stderr,
                "[m5-source-span-control] phase=%u width=1024 origin=0x%06X "
                "spans=0x18DD20:0x18DD50,0x18FB60:0x18FB90\n",
                rs64_phase_ord(), source_origin);
            std::fflush(stderr);
            source_control = true;
        }
        if (source_rows < 4096u) {
            std::fprintf(stderr,
                "[m5-source-span] ordinal=%u phase=%u width=1024 origin=0x%06X "
                "pc=0x%08X width=%c phys=0x%06X span=%s offset=0x%X value=0x%08X\n",
                source_rows++, rs64_phase_ord(), source_origin, pc, width,
                source_phys, source_hit ? "dd" : "fb",
                source_phys - (source_hit ? 0x0018DD20u : 0x0018FB60u), value);
            std::fflush(stderr);
        }
    }
    static const bool task_writer_enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_TASK_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    const uint32_t store_phys = addr & 0x1FFFFFFFu;
    const uint32_t store_span = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
    const uint32_t title_origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool title_phase = rs64_vi_committed_width() == 1024u &&
        (title_origin == 0x00790400u || title_origin == 0x00790800u);
    if (task_writer_enabled && title_phase &&
        store_phys < 0x001494B0u && store_phys + store_span > 0x00149470u) {
        static uint32_t rows = 0;
        static bool control = false;
        if (!control) {
            std::fprintf(stderr,
                "[m5-task-writer-control] phase=%u width=1024 origin=0x%06X span=0x149470:0x1494B0\n",
                rs64_phase_ord(), title_origin);
            std::fflush(stderr);
            control = true;
        }
        if (rows < 2048u) {
            std::fprintf(stderr,
                "[m5-task-writer] ordinal=%u phase=%u width=1024 origin=0x%06X "
                "pc=0x%08X width=%c phys=0x%06X field=0x%X value=0x%08X\n",
                rows++, rs64_phase_ord(), title_origin, pc, width, store_phys,
                store_phys - 0x00149470u, value);
            std::fflush(stderr);
        }
    }
    if (task_writer_enabled && title_phase && store_phys == 0x00149750u &&
        store_span == 4u) {
        static uint32_t pointer_rows = 0;
        static bool pointer_control = false;
        if (!pointer_control) {
            std::fprintf(stderr,
                "[m5-selector-pointer-control] phase=%u width=1024 origin=0x%06X addr=0x80149750\n",
                rs64_phase_ord(), title_origin);
            std::fflush(stderr);
            pointer_control = true;
        }
        if (pointer_rows < 1024u) {
            std::fprintf(stderr,
                "[m5-selector-pointer-store] ordinal=%u phase=%u width=1024 origin=0x%06X "
                "pc=0x%08X value=0x%08X\n",
                pointer_rows++, rs64_phase_ord(), title_origin, pc, value);
            std::fflush(stderr);
        }
    }
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t phys = addr & 0x1FFFFFFFu;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u) ||
        phys < 0x00110000u || phys >= 0x00112000u) return;
    static uint32_t rows = 0;
    static bool control = false;
    if (!control) {
        std::fprintf(stderr,
            "[m5-state-pointer-writer-control] phase=%u width=1024 origin=0x%06X\n",
            rs64_phase_ord(), origin);
        std::fflush(stderr);
        control = true;
    }
    if (value < 0x80110000u || value >= 0x80112000u) return;
    static constexpr uint32_t candidate_pcs[4] = {
        0x800027C4u, 0x800027D0u, 0x800027DCu, 0x80003C28u
    };
    for (unsigned i = 0; i < 4; ++i) {
        if (pc == candidate_pcs[i]) {
            g_rs64_m5_pointer_latest[i] = {pc, addr, value, rs64_phase_ord()};
            break;
        }
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-state-pointer-store] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "pc=0x%08X width=%c addr=0x%08X phys=0x%06X value=0x%08X\n",
        rows++, rs64_phase_ord(), origin, pc, width, addr, phys, value);
    std::fflush(stderr);
}

extern "C" void rs64_m5_mix_entry(uint8_t* rdram, recomp_context* ctx, uint32_t pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_MIX_ENTRY");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !rdram) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const bool target = (width == 1024u &&
                         (origin == 0x00790400u || origin == 0x00790800u)) ||
                        (width == 512u && origin == 0x006AB400u);
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    static uint32_t control = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (!target || rows >= 256u) return;
    if (control == 0) {
        std::fprintf(stderr,
            "[m5-mix-entry-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
        control = 1;
    }
    std::fprintf(stderr,
        "[m5-mix-entry] ordinal=%u phase=%u width=%u origin=0x%06X pc=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X ra=0x%08X\n",
        rows++, phase, width, origin, pc, U32(ctx->r4), U32(ctx->r5),
        U32(ctx->r6), U32(ctx->r7), U32(ctx->r16), U32(ctx->r17),
        U32(ctx->r18), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_writer(uint32_t v0, uint32_t s0, uint32_t s1,
                                          uint32_t s2, uint32_t a0, uint32_t a1,
                                          uint32_t a2, uint32_t a3, uint32_t ra,
                                          uint32_t value) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_TASK_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-writer-control] phase=%u width=1024 origin=0x%06X pc=0x80091074\n",
            rs64_phase_ord(), origin);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-selector-writer] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "v0=0x%08X s0=0x%08X s1=0x%08X s2=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X ra=0x%08X value=0x%08X\n",
        rows++, rs64_phase_ord(), origin, v0, s0, s1, s2, a0, a1, a2, a3, ra, value);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_load(uint32_t index, uint32_t table_addr,
                                        uint32_t value, uint32_t s0, uint32_t s1,
                                        uint32_t s2, uint32_t a0, uint32_t a1,
                                        uint32_t a2, uint32_t ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_TASK_WRITER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-load-control] phase=%u width=1024 origin=0x%06X pc=0x80091060\n",
            rs64_phase_ord(), origin);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-selector-load] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "index=0x%08X table_addr=0x%08X value=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), origin, index, table_addr, value,
        s0, s1, s2, a0, a1, a2, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_producer(uint8_t* rdram, uint32_t pc,
                                             uint32_t a0, uint32_t a1,
                                             uint32_t a2, uint32_t a3,
                                             uint32_t index, uint32_t ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_PRODUCER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || !rdram) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-producer-control] phase=%u width=1024 origin=0x%06X pc=0x%08X\n",
            rs64_phase_ord(), origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    const auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return (static_cast<uint32_t>(rdram[p]) << 24) |
               (static_cast<uint32_t>(rdram[p + 1]) << 16) |
               (static_cast<uint32_t>(rdram[p + 2]) << 8) |
               static_cast<uint32_t>(rdram[p + 3]);
    };
    const uint32_t table = 0x80149758u + ((index & 0xFFu) * 4u);
    std::fprintf(stderr,
        "[m5-selector-producer] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "pc=0x%08X index=0x%08X table=0x%08X table_word=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), origin, pc, index, table, word(table),
        a0, a1, a2, a3, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_table_store(uint32_t pc, uint32_t addr,
                                                 uint32_t value, uint32_t v0,
                                                 uint32_t s0, uint32_t s1,
                                                 uint32_t s2, uint32_t a0,
                                                 uint32_t a1, uint32_t a2,
                                                 uint32_t a3, uint32_t ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_TABLE");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool selector_table_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!selector_table_phase) return;
    if (addr != 0x80149758u && addr != 0x8014975Cu) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-table-control] phase=%u width=%u origin=0x%06X\n",
            rs64_phase_ord(), width, origin);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-selector-table-store] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X addr=0x%08X value=0x%08X v0=0x%08X s0=0x%08X "
        "s1=0x%08X s2=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X "
        "a3=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, pc, addr, value, v0, s0, s1, s2,
        a0, a1, a2, a3, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_store_context(uint32_t pc, uint32_t v0,
                                                  uint32_t s0, uint32_t s1,
                                                  uint32_t s2, uint32_t a0,
                                                  uint32_t a1, uint32_t a2,
                                                  uint32_t a3, uint32_t ra) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-store-context-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-selector-store-context] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X v0=0x%08X s0=0x%08X s1=0x%08X s2=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X ra=0x%08X\n",
        rows++, phase, width, origin, pc, v0, s0, s1, s2, a0, a1, a2, a3, ra);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_alloc_edge(const char* stage, uint32_t pc,
                                               uint32_t a0, uint32_t a1,
                                               uint32_t a2, uint32_t a3,
                                               uint32_t v0, uint32_t s0,
                                               uint32_t s1, uint32_t s2) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_ALLOC");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-alloc-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-selector-alloc] ordinal=%u phase=%u width=%u origin=0x%06X stage=%s "
        "pc=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X v0=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X\n",
        rows++, phase, width, origin, stage ? stage : "?", pc, a0, a1, a2,
        a3, v0, s0, s1, s2);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_input_load(uint32_t pc, uint32_t value,
                                                uint32_t source, uint32_t s1,
                                                uint32_t a0, uint32_t a2,
                                                uint32_t a3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_INPUT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && (origin == 0x006AB400u || origin == 0x006AB800u));
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) { phase_seen = phase; rows = 0; }
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-input-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-input] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X value=0x%08X source=0x%08X s1=0x%08X "
        "a0=0x%08X a2=0x%08X a3=0x%08X\n",
        rows++, phase, width, origin, pc, value, source, s1, a0, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_store_entry(uint32_t pc, uint32_t ra,
                                                uint32_t a0, uint32_t a1,
                                                uint32_t a2, uint32_t a3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_STORE_ENTRY");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-store-entry-control] pc=0x%08X width=%u origin=0x%06X\n",
            pc, width, origin);
        std::fflush(stderr);
    }
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-store-entry] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X\n",
        rows++, phase, width, origin, pc, ra, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_producer_context(uint32_t pc, uint32_t ra,
                                                     uint32_t a0, uint32_t a1,
                                                     uint32_t a2, uint32_t a3,
                                                     uint32_t s0, uint32_t s1,
                                                     uint32_t s2) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_SELECTOR_PRODUCER_CONTEXT");
        return all && all[0] && all[0] != '0';
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    const bool target_phase =
        (width == 1024u && (origin == 0x00790400u || origin == 0x00790800u)) ||
        (width == 512u && origin == 0x006AB400u);
    if (!target_phase) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-producer-context-control] phase=%u width=%u origin=0x%06X pc=0x%08X\n",
            phase, width, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-producer-context] ordinal=%u phase=%u width=%u origin=0x%06X "
        "pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X "
        "s0=0x%08X s1=0x%08X s2=0x%08X\n",
        rows++, phase, width, origin, pc, ra, a0, a1, a2, a3, s0, s1, s2);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_ai_boundary(uint32_t pc, uint32_t ra,
                                                uint32_t a0, uint32_t a1,
                                                uint32_t a2, uint32_t s0,
                                                uint32_t s1, uint32_t v0) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_SELECTOR_AI_BOUNDARY");
        return all && all[0] && all[0] != '0';
    }();
    if (!enabled) return;
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-ai-boundary-probe-control] pc=0x%08X ra=0x%08X\n",
            pc, ra);
        std::fflush(stderr);
    }
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    if (width != 512u || origin != 0x006AB400u) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-ai-boundary-control] phase=%u width=512 origin=0x%06X pc=0x%08X\n",
            phase, origin, pc);
        std::fflush(stderr);
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-ai-boundary] ordinal=%u phase=%u width=512 origin=0x%06X "
        "pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X "
        "s0=0x%08X s1=0x%08X v0=0x%08X\n",
        rows++, phase, origin, pc, ra, a0, a1, a2, s0, s1, v0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_ai_callsite(uint32_t callsite,
                                                uint32_t a0, uint32_t a1,
                                                uint32_t a2, uint32_t s0,
                                                uint32_t s1, uint32_t v0) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_SELECTOR_AI_BOUNDARY");
        return all && all[0] && all[0] != '0';
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    const uint32_t width = rs64_vi_committed_width();
    static bool control_seen = false;
    if (!control_seen) {
        control_seen = true;
        std::fprintf(stderr,
            "[m5-selector-ai-callsite-control] callsite=0x%08X width=%u origin=0x%06X\n",
            callsite, width, origin);
        std::fflush(stderr);
    }
    if (width != 512u || origin != 0x006AB400u) return;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t phase = rs64_phase_ord();
    if (phase != phase_seen) {
        phase_seen = phase;
        rows = 0;
    }
    if (rows >= 256u) return;
    std::fprintf(stderr,
        "[m5-selector-ai-callsite] ordinal=%u phase=%u width=512 origin=0x%06X "
        "callsite=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X s0=0x%08X s1=0x%08X v0=0x%08X\n",
        rows++, phase, origin, callsite, a0, a1, a2, s0, s1, v0);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_caller(uint32_t caller_pc,
                                         uint32_t ra, uint32_t a0,
                                         uint32_t a1, uint32_t a2,
                                         uint32_t a3) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_CALLER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-caller-control] phase=%u width=1024 origin=0x%06X pc=0x%08X\n",
            rs64_phase_ord(), origin, caller_pc);
        std::fflush(stderr);
    }
    if (rows >= 1024u) return;
    std::fprintf(stderr,
        "[m5-selector-caller] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "pc=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X\n",
        rows++, rs64_phase_ord(), origin, caller_pc, ra, a0, a1, a2, a3);
    std::fflush(stderr);
}

extern "C" void rs64_m5_selector_precall(uint32_t pc, uint32_t stage,
                                             uint32_t index, uint32_t address,
                                             uint32_t value, uint32_t a0,
                                             uint32_t a1, uint32_t a2,
                                             uint32_t s0, uint32_t s1) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_SELECTOR_PRECALL");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (rs64_vi_committed_width() != 1024u ||
        (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows == 0) {
        std::fprintf(stderr,
            "[m5-selector-precall-control] phase=%u width=1024 origin=0x%06X\n",
            rs64_phase_ord(), origin);
        std::fflush(stderr);
    }
    if (rows >= 2048u) return;
    std::fprintf(stderr,
        "[m5-selector-precall] ordinal=%u phase=%u width=1024 origin=0x%06X "
        "stage=%u pc=0x%08X index=0x%08X address=0x%08X value=0x%08X "
        "a0=0x%08X a1=0x%08X a2=0x%08X s0=0x%08X s1=0x%08X\n",
        rows++, rs64_phase_ord(), origin, stage, pc, index, address, value,
        a0, a1, a2, s0, s1);
    std::fflush(stderr);
}

extern "C" void rs64_m5_state_pointer_consumer(uint32_t s1) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_STATE_POINTER");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t rows = 0;
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-state-pointer-consumer] ordinal=%u phase=%u width=1024 origin=0x%06X s1=0x%08X "
        "edge_s1=%08X edge_a0=%08X edge_ra=%08X edge_ord=%u edge_match=%u "
        "c0=%08X/%08X/%08X/%u c1=%08X/%08X/%08X/%u c2=%08X/%08X/%08X/%u c3=%08X/%08X/%08X/%u "
        "down_pc=%08X down_addr=%08X down_value=%08X down_ord=%u\n",
        rows++, rs64_phase_ord(), origin, s1,
        g_rs64_m5_zcfree_edge.s1, g_rs64_m5_zcfree_edge.a0,
        g_rs64_m5_zcfree_edge.ra, g_rs64_m5_zcfree_edge.ordinal,
        g_rs64_m5_zcfree_edge.valid && g_rs64_m5_zcfree_edge.s1 == s1 ? 1u : 0u,
        g_rs64_m5_pointer_latest[0].pc, g_rs64_m5_pointer_latest[0].addr,
        g_rs64_m5_pointer_latest[0].value, g_rs64_m5_pointer_latest[0].phase,
        g_rs64_m5_pointer_latest[1].pc, g_rs64_m5_pointer_latest[1].addr,
        g_rs64_m5_pointer_latest[1].value, g_rs64_m5_pointer_latest[1].phase,
        g_rs64_m5_pointer_latest[2].pc, g_rs64_m5_pointer_latest[2].addr,
        g_rs64_m5_pointer_latest[2].value, g_rs64_m5_pointer_latest[2].phase,
        g_rs64_m5_pointer_latest[3].pc, g_rs64_m5_pointer_latest[3].addr,
        g_rs64_m5_pointer_latest[3].value, g_rs64_m5_pointer_latest[3].phase,
        g_rs64_m5_downstream_latest.pc, g_rs64_m5_downstream_latest.addr,
        g_rs64_m5_downstream_latest.value, g_rs64_m5_downstream_latest.ordinal);
    std::fflush(stderr);
}

static void rs64_m5_frequency_producer(uint8_t* rdram, recomp_context* ctx,
                                       uint32_t mq_addr, uint32_t msg,
                                       int32_t flag) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_PRODUCERS");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 512u) return;
    const uint32_t s0 = U32(ctx->r16);
    const uint32_t s1 = U32(ctx->r17);
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return (static_cast<uint32_t>(rdram[p]) << 24) |
               (static_cast<uint32_t>(rdram[p + 1]) << 16) |
               (static_cast<uint32_t>(rdram[p + 2]) << 8) |
               static_cast<uint32_t>(rdram[p + 3]);
    };
    auto byte = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= 0x80800000u) return 0xFFFFFFFFu;
        return rdram[guest - 0x80000000u];
    };
    static std::atomic<uint32_t> send_seq{0};
    const uint32_t sequence = send_seq.fetch_add(1, std::memory_order_relaxed);
    std::fprintf(stderr,
        "[m5-frequency-producer] ordinal=%u seq=%u phase=%u width=%u origin=0x%06X "
        "mq=0x%08X msg=0x%08X flag=%d s0=0x%08X s1=0x%08X source_word=0x%08X "
        "source_byte=0x%02X branch_selector=0x%08X branch_state=0x%04X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X v0=0x%08X v1=0x%08X ra=0x%08X\n",
        rows++, sequence, rs64_phase_ord(), width, origin, mq_addr, msg, (int)flag, s0, s1,
        word(s0 + 0x60u), byte(s0 + 0x22u), U32(ctx->r2),
        word(s1 + 0x22u) & 0xFFFFu, U32(ctx->r4), U32(ctx->r5),
        U32(ctx->r6), U32(ctx->r7), U32(ctx->r2), U32(ctx->r3), U32(ctx->r31));
    std::fflush(stderr);
}

static void rs64_m5_frequency_receive_join(uint8_t* rdram,
                                             recomp_context* ctx,
                                             uint32_t mq_addr,
                                             int32_t flag,
                                             int32_t result,
                                             uint32_t delivered_hint) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_RECEIVES");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled || result != 0 || mq_addr != 0x8010FEE0u) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 512u) return;
    uint32_t delivered = delivered_hint;
    const uint32_t slot = U32(ctx->r5);
    if (delivered == 0xFFFFFFFFu && slot >= 0x80000000u && slot <= 0x807FFFFCu) {
        const uint32_t p = slot - 0x80000000u;
        delivered = (static_cast<uint32_t>(rdram[p]) << 24) |
                    (static_cast<uint32_t>(rdram[p + 1]) << 16) |
                    (static_cast<uint32_t>(rdram[p + 2]) << 8) |
                    static_cast<uint32_t>(rdram[p + 3]);
    }
    std::fprintf(stderr,
        "[m5-frequency-receive] ordinal=%u phase=%u width=%u origin=0x%06X "
        "mq=0x%08X msg=0x%08X flag=%d result=%d slot=0x%08X delivered=0x%08X "
        "guest_pc=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, mq_addr, (uint32_t)ctx->r5,
        (int)flag, (int)result, slot, delivered,
        (unsigned)g_rs64_last_guest_pc, U32(ctx->r31));
    std::fflush(stderr);
    if (rows == 1) {
        std::fprintf(stderr, "[m5-frequency-receive-positive] post-receive join is live\n");
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_frequency_consumer(uint8_t* rdram,
                                               recomp_context* ctx,
                                               uint32_t callsite) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_CONSUMERS");
        const char* output = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_OUTPUT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0') ||
               (output && output[0] && output[0] != '0');
    }();
    if (!enabled || U32(ctx->r4) != 0x8010FEE0u || U32(ctx->r2) != 0) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 512u) return;
    const uint32_t state = U32(ctx->r16);
    g_rs64_m5_frequency_pending = {U32(ctx->r4), U32(ctx->r5), callsite, state, true};
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return (static_cast<uint32_t>(rdram[p]) << 24) |
               (static_cast<uint32_t>(rdram[p + 1]) << 16) |
               (static_cast<uint32_t>(rdram[p + 2]) << 8) |
               static_cast<uint32_t>(rdram[p + 3]);
    };
    std::fprintf(stderr,
        "[m5-frequency-consumer] ordinal=%u phase=%u width=%u origin=0x%06X "
        "callsite=0x%08X mq=0x%08X msg_slot=0x%08X result=%d state=0x%08X "
        "state_word=0x%08X state_next=0x%08X a0=0x%08X a1=0x%08X "
        "a2=0x%08X a3=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, callsite, U32(ctx->r4),
        U32(ctx->r5), (int)U32(ctx->r2), state, word(state),
        word(state + 0x1E8u), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),
        U32(ctx->r7), U32(ctx->r31));
    std::fflush(stderr);
    if (rows == 1) {
        std::fprintf(stderr, "[m5-frequency-consumer-positive] post-receive witness is live\n");
        std::fflush(stderr);
    }
}

extern "C" void rs64_m5_frequency_output_use(uint8_t* rdram,
                                                 recomp_context* ctx,
                                                 uint32_t callsite,
                                                 uint32_t output_pc) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_OUTPUT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    if (!g_rs64_m5_frequency_pending.valid ||
        g_rs64_m5_frequency_pending.callsite != callsite) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 512u) return;
    std::fprintf(stderr,
        "[m5-frequency-output] ordinal=%u phase=%u width=%u origin=0x%06X "
        "queue=0x%08X msg=0x%08X callsite=0x%08X state=0x%08X "
        "output_pc=0x%08X output=0x%08X a0=0x%08X a1=0x%08X "
        "a2=0x%08X a3=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, g_rs64_m5_frequency_pending.queue,
        g_rs64_m5_frequency_pending.msg, callsite,
        g_rs64_m5_frequency_pending.state, output_pc, U32(ctx->r3), U32(ctx->r4),
        U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r31));
    std::fflush(stderr);
    if (rows == 1) {
        std::fprintf(stderr, "[m5-frequency-output-positive] first post-consumer output is live\n");
        std::fflush(stderr);
    }
    g_rs64_m5_frequency_pending.valid = false;
}

extern "C" void osSendMesg_recomp(uint8_t* rdram, recomp_context* ctx) {
    const uint32_t mq_addr = (uint32_t)ctx->r4;
    rs64_m5_frequency_producer(rdram, ctx, mq_addr, (uint32_t)ctx->r5,
                               (s32)ctx->r6);
    sendtgt_note(mq_addr, GetCurrentThreadId(),
                 recv_trace_enabled() || sendmesg_stack_enabled());
    log_m5_frame_sync_edge(rdram, "send", mq_addr, (uint32_t)ctx->r5,
                           (s32)ctx->r6);
    if (mq_addr == 0x8011A818u || mq_addr == 0x8011A7E8u || mq_addr == 0x8011A408u) {
        log_submit_boundary(rdram, "send", mq_addr, (uint32_t)ctx->r6);
    }
    if ((uint32_t)ctx->r4 == 0x8011A408u) {
        const OSMesgQueue before = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        const int32_t result = osSendMesg(rdram, (int32_t)ctx->r4,
                                          (OSMesg)ctx->r5, (s32)ctx->r6);
        const OSMesgQueue after = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        ctx->r2 = result;
        log_m5_dp_event_boundary("send", (uint32_t)ctx->r4, (uint32_t)ctx->r5,
                                 (s32)ctx->r6, result, before, after);
    } else {
        ctx->r2 = osSendMesg(rdram, (int32_t)ctx->r4, (OSMesg)ctx->r5, (s32)ctx->r6);
    }
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_M5_DOWNSTREAM");
        return all && all[0] && all[0] != '0';
    }();
    if (enabled) {
        const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
        if (rs64_vi_committed_width() == 1024u &&
            (origin == 0x00790400u || origin == 0x00790800u)) {
            static uint32_t rows = 0;
            if (rows < 512u) {
                std::fprintf(stderr,
                    "[m5-os-send-return] ordinal=%u phase=%u origin=0x%06X "
                    "caller_ra=0x%08X mq=0x%08X msg=0x%08X flag=0x%08X result=0x%08X "
                    "s1=0x%08X s0=0x%08X\n",
                    rows++, rs64_phase_ord(), origin, U32(ctx->r31), U32(ctx->r4),
                    U32(ctx->r5), U32(ctx->r6), U32(ctx->r2), U32(ctx->r17), U32(ctx->r16));
                std::fflush(stderr);
            }
        }
    }
}

static void rs64_m5_frequency_contract(uint8_t* rdram, recomp_context* ctx) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_CONTRACT");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;

    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;

    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) {
        bucket = key;
        rows = 0;
    }
    if (rows >= 256u) return;

    const uint32_t s0 = U32(ctx->r16);
    const uint32_t s1 = U32(ctx->r17);
    auto word = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return (static_cast<uint32_t>(rdram[p]) << 24) |
               (static_cast<uint32_t>(rdram[p + 1]) << 16) |
               (static_cast<uint32_t>(rdram[p + 2]) << 8) |
               static_cast<uint32_t>(rdram[p + 3]);
    };
    auto byte = [rdram](uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= 0x80800000u) return 0xFFFFFFFFu;
        return rdram[guest - 0x80000000u];
    };
    const uint32_t source_word = word(s0 + 0x60u);
    const uint32_t source_byte = byte(s0 + 0x22u);
    const uint32_t branch_state = word(s1 + 0x22u) & 0xFFFFu;
    std::fprintf(stderr,
        "[m5-frequency-contract] n=%u phase=%u width=%u origin=0x%06X "
        "s0=0x%08X s1=0x%08X source_word=0x%08X source_byte=0x%02X "
        "branch_selector=0x%08X branch_state=0x%04X a0=0x%08X a1=0x%08X "
        "a2=0x%08X a3=0x%08X v0=0x%08X v1=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, s0, s1, source_word,
        source_byte, U32(ctx->r2), branch_state, U32(ctx->r4), U32(ctx->r5),
        U32(ctx->r6), U32(ctx->r7), U32(ctx->r2), U32(ctx->r3), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void rs64_m5_frequency_caller(uint8_t* rdram, recomp_context* ctx,
                                           uint32_t callsite) {
    static const bool enabled = [] {
        const char* all = std::getenv("ROGUESQ_LOG_ALL");
        const char* own = std::getenv("ROGUESQ_LOG_M5_FREQUENCY_CALLERS");
        return (all && all[0] && all[0] != '0') ||
               (own && own[0] && own[0] != '0');
    }();
    if (!enabled) return;
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (width != 1024u || (origin != 0x00790400u && origin != 0x00790800u)) return;
    static uint32_t bucket = 0xFFFFFFFFu;
    static uint32_t rows = 0;
    const uint32_t key = (width << 24) ^ origin;
    if (key != bucket) { bucket = key; rows = 0; }
    if (rows >= 256u) return;
    const uint32_t s0 = U32(ctx->r16);
    const uint32_t s1 = U32(ctx->r17);
    auto word = [](uint8_t* rdram, uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest > 0x807FFFFCu) return 0xFFFFFFFFu;
        const uint32_t p = guest - 0x80000000u;
        return (static_cast<uint32_t>(rdram[p]) << 24) |
               (static_cast<uint32_t>(rdram[p + 1]) << 16) |
               (static_cast<uint32_t>(rdram[p + 2]) << 8) |
               static_cast<uint32_t>(rdram[p + 3]);
    };
    auto byte = [](uint8_t* rdram, uint32_t guest) -> uint32_t {
        if (guest < 0x80000000u || guest >= 0x80800000u) return 0xFFFFFFFFu;
        return rdram[guest - 0x80000000u];
    };
    std::fprintf(stderr,
        "[m5-frequency-caller] ordinal=%u phase=%u width=%u origin=0x%06X "
        "callsite=0x%08X s0=0x%08X s1=0x%08X source_word=0x%08X "
        "source_byte=0x%02X branch_selector=0x%08X branch_state=0x%04X "
        "a0=0x%08X a1=0x%08X a2=0x%08X a3=0x%08X v0=0x%08X v1=0x%08X ra=0x%08X\n",
        rows++, rs64_phase_ord(), width, origin, callsite, s0, s1,
        word(rdram, s0 + 0x60u), byte(rdram, s0 + 0x22u), U32(ctx->r2),
        word(rdram, s1 + 0x22u) & 0xFFFFu, U32(ctx->r4), U32(ctx->r5),
        U32(ctx->r6), U32(ctx->r7), U32(ctx->r2), U32(ctx->r3), U32(ctx->r31));
    std::fflush(stderr);
}

extern "C" void osRecvMesg_recomp(uint8_t* rdram, recomp_context* ctx) {
    const uint32_t mq_addr = (uint32_t)ctx->r4;
    const int32_t flag = (s32)ctx->r6;
    const uint64_t tid = GetCurrentThreadId();
    uint32_t delivered_hint = 0xFFFFFFFFu;
    if (mq_addr == 0x8010FEE0u) {
        const OSMesgQueue& queue = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        if (queue.msg != NULLPTR && queue.first >= 0 && queue.first < queue.msgCount) {
            delivered_hint = (uint32_t)TO_PTR(OSMesg, queue.msg)[queue.first];
        }
    }
    rs64_m5_frequency_contract(rdram, ctx);
    recv_trace_enter(rdram, mq_addr, flag, tid);
    log_m5_frame_sync_edge(rdram, "recv", mq_addr, (uint32_t)ctx->r5, flag);
    if (mq_addr == 0x8011A818u || mq_addr == 0x8011A7E8u || mq_addr == 0x8011A408u) {
        log_submit_boundary(rdram, "recv", mq_addr, (uint32_t)flag);
    }
    if (mq_addr == 0x8011A408u) {
        const OSMesgQueue before = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        const int32_t result = osRecvMesg(rdram, (int32_t)ctx->r4,
                                          (PTR(OSMesg))ctx->r5, flag);
        const OSMesgQueue after = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        ctx->r2 = result;
        const int32_t consumed = after.msgCount > 0
            ? (after.first + after.msgCount - 1) % after.msgCount : 0;
        const uint32_t scheduler_msg =
            (result == 0 && after.msgCount > 0)
                ? (uint32_t)(uintptr_t)TO_PTR(OSMesg, after.msg)[consumed] : 0u;
        recv_trace_scheduler_type(rdram, scheduler_msg, result);
        log_m5_dp_event_boundary("recv", mq_addr, (uint32_t)ctx->r5,
                                 flag, result, before, after);
    } else if (mq_addr == 0x8010FEE0u) {
        const OSMesgQueue before = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        const int32_t result = osRecvMesg(rdram, (int32_t)ctx->r4,
                                          (PTR(OSMesg))ctx->r5, flag);
        const OSMesgQueue after = *TO_PTR(OSMesgQueue, (PTR(OSMesgQueue))ctx->r4);
        ctx->r2 = result;
        log_a1_queue_boundary(mq_addr, (PTR(OSMesg))ctx->r5, flag,
                              result, before, after);
    } else {
        ctx->r2 = osRecvMesg(rdram, (int32_t)ctx->r4, (PTR(OSMesg))ctx->r5, flag);
    }
    rs64_m5_frequency_receive_join(rdram, ctx, mq_addr, flag, (int32_t)ctx->r2,
                                   delivered_hint);
    recv_trace_exit(mq_addr, flag, tid, (int32_t)ctx->r2);
}

// Override upstream's osStopThread_recomp because upstream's osStopThread
// asserts(false) when called with a non-self thread handle (threads.cpp:278).
// RS64's func_80000C68 stops other threads. We replicate libultra's actual
// semantics: remove the target thread from any queue it's blocked on and
// mark it STOPPED so the scheduler doesn't try to schedule it. The host
// std::thread is parked in wait_for_resumed until a future osStartThread.
extern "C" void osStopThread_recomp(uint8_t* rdram, recomp_context* ctx) {
    PTR(OSThread) t_ = (PTR(OSThread))(int32_t)ctx->r4;
    if (t_ == NULLPTR) {
        // Self-stop: same path upstream takes — yield to scheduler.
        ultramodern::run_next_thread_and_wait(PASS_RDRAM1);
        return;
    }
    OSThread* t = TO_PTR(OSThread, t_);
    if (t->state != OSThreadState::STOPPED) {
        if (t->queue != NULLPTR) {
            ultramodern::thread_queue_remove(PASS_RDRAM t->queue, t_);
        }
        t->state = OSThreadState::STOPPED;
    }
}
