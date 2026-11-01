#include <memory>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <mutex>
#include <string_view>
#include <vector>
#include <deque>
#include <condition_variable>
#include <thread>
#include <pthread.h>
#include <pthread/qos.h>

#define HLSL_CPU
#include "hle/rt64_application.h"

#include "ultramodern/ultramodern.hpp"
#include "ultramodern/renderer_context.hpp"

// Shared Application accessor for the LLE DPC bridge (src/rsp/dpc_bridge.cpp).
// The bridge needs to forward Factor 5 raw RDP byte ranges via
// processDisplayLists(isHLE=false). Set on construction, cleared on shutdown.
static std::atomic<RT64::Application*> g_rt64_app{nullptr};
// s6705 G1e async RDP consumer (see ultramodern::rdpq below); flipped on the Gfx thread by ROGUESQ_RDP_ASYNC_TOGGLE.
extern "C" int rs64_rdp_async_on;
int rs64_rdp_async_on = [] { const char *e = std::getenv("ROGUESQ_RDP_ASYNC"); return (e && *e && *e != '0') ? 1 : 0; }();
namespace RT64 { extern volatile int g_s4280_n; } // rt64_rdp.cpp s4280 cimg events
namespace ultramodern { void rs64_rdpq_drain(); void rs64_rdpq_task_enter(); void rs64_rdpq_task_exit(); }
extern "C" uint32_t rs64_phase_ord(void);

// Host-side observations only; no rendering decision depends on them.
static std::atomic<uint32_t> g_rs64_g1d_join_phase{UINT32_MAX};
static std::atomic<uint32_t> g_rs64_g1d_join_lo{0};
static std::atomic<uint32_t> g_rs64_g1d_join_hi{0};
static std::atomic<uint32_t> g_rs64_g1d_join_ci_w{0};
static std::atomic<uint32_t> g_rs64_g1d_join_ci_a{0};
static std::atomic<uint32_t> g_rs64_g1d_join_cis{0};

struct Rs64G1dCiObservation {
    uint32_t width;
    uint32_t address;
    uint32_t lo;
    uint32_t hi;
};
static std::mutex g_rs64_g1d_ci_mutex;
static std::vector<Rs64G1dCiObservation> g_rs64_g1d_ci_frame;

extern "C" void rs64_g1d_join_swap(uint32_t frame, uint32_t fb,
                                     uint32_t vi_width, uint32_t vi_origin) {
    static int enabled = -1;
    static uint32_t last_phase = UINT32_MAX;
    static uint32_t phase_rows = 0;
    if (enabled < 0) {
        const char* route = std::getenv("ROGUESQ_LOG_RDP_ROUTE");
        const char* dump = std::getenv("ROGUESQ_FB_DUMP_VI");
        enabled = ((route && *route && *route != '0') ||
                   (dump && *dump && *dump != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    const uint32_t phase = rs64_phase_ord();
    if (phase != last_phase) { last_phase = phase; phase_rows = 0; }
    if (phase_rows++ < 160) {
        std::vector<Rs64G1dCiObservation> cis;
        {
            std::lock_guard<std::mutex> lock(g_rs64_g1d_ci_mutex);
            cis.swap(g_rs64_g1d_ci_frame);
        }
        std::fprintf(stderr,
            "[g1d-join] phase=%u frame=%u fb=0x%06X vi_w=%u vi_o=0x%06X "
            "rdp_lo=0x%06X rdp_hi=0x%06X ci_n=%u last_ci_w=%u last_ci_a=0x%06X\n",
            phase, frame, fb & 0xFFFFFFu, vi_width, vi_origin & 0xFFFFFFu,
            g_rs64_g1d_join_lo.load(), g_rs64_g1d_join_hi.load(),
            g_rs64_g1d_join_cis.load(), g_rs64_g1d_join_ci_w.load(),
            g_rs64_g1d_join_ci_a.load());
        std::fprintf(stderr, "[g1d-frame-ci] phase=%u frame=%u n=%zu", phase, frame, cis.size());
        for (const auto& ci : cis) {
            std::fprintf(stderr, " %u@0x%06X[0x%06X-0x%06X]",
                         ci.width, ci.address, ci.lo, ci.hi);
        }
        std::fputc('\n', stderr);
        std::fflush(stderr);
    }
}

extern "C" uint64_t rs64_dpc_get_last_submit_serial();
extern "C" bool rs64_dpc_take_synthetic_consumer(uint64_t *serial);
extern "C" uint32_t rs64_e9prov_current_task();
extern "C" uint32_t rs64_e9prov_current_root_dl();
extern "C" uint32_t rs64_e9prov_current_scope();
extern "C" volatile uint32_t g_rs64_last_guest_pc;
extern uint32_t g_rsp_dpc_start;
extern uint32_t g_rsp_dpc_end;
extern "C" int rs64_is_hangar_vi(void);
extern "C" void rs64_s4899_vi(uint32_t vi, uint32_t width);
extern "C" void rs64_s4597_target_store(char width, uint32_t pc, uint32_t addr, uint32_t value);
extern "C" void rs64_m5_b40_route_title_transition(void);
extern "C" void rs64_m5_route_fingerprint_phase(uint32_t width,
                                                  uint32_t origin);
extern "C" void rs64_m5_route_fingerprint_snapshot(uint32_t width,
                                                     uint32_t origin);
extern "C" void rs64_vi_boundary_log(const char* edge, uint32_t requested_fb,
                                      uint32_t committed_origin, uint32_t width);
extern "C" uint32_t rs64_vi_boundary_screen_request(void);
extern "C" uint32_t rs64_m5_host_send_begin(uint32_t data_ptr);
extern "C" void rs64_m5_host_edge(const char* edge, uint32_t task_seq,
                                    uint32_t data_ptr, uint32_t mq,
                                    uint32_t source, uint32_t sent,
                                    int32_t valid_count, int32_t msg_count);

// Interval-scoped diagnostics (session 25).
//
// The RT64-side censuses (ROGUESQ_LOG_FLOOR and friends) keep their `seen` set
// and print budget in run-lifetime statics, so whichever phase runs first
// consumes the whole budget and every later phase reports nothing. That is the
// same trap session 18 hit with "first N" counters, and it is why the hangar
// floor band has never actually been attributed: the census fires during boot
// and the title screen and is exhausted long before the hangar starts at ~55s.
//
// Publishing a counter that ticks on every VI-width change lets those censuses
// reset per phase, and lets each line say which phase it belongs to instead of
// relying on log-line interleave after the fact.
static std::atomic<uint32_t> g_rs64_phase_ord{0};
extern "C" void rs64_bump_phase_ord(void) {
    g_rs64_phase_ord.fetch_add(1, std::memory_order_relaxed);
}
extern "C" { volatile uint32_t rs64_vi_n_g = 0; } // s5816
extern "C" uint32_t rs64_phase_ord(void) {
    return g_rs64_phase_ord.load(std::memory_order_relaxed);
}
extern "C" void rs64_m5_selector_ai_call_latch_join(uint32_t width,
                                                       uint32_t origin,
                                                       uint32_t phase);

// Shared wall-clock epoch (s234) so guest-side diagnostics (funcs_*.c PATCH
// blocks, via extern "C" declaration) can emit timestamps directly
// comparable to the [phase] line below and to host-side hold_NN.png capture
// timing — one clock, not a second independently-skewed one per diagnostic.
static const std::chrono::steady_clock::time_point g_rs64_t0 = std::chrono::steady_clock::now();
extern "C" double rs64_elapsed_seconds(void) {
    return std::chrono::duration<double>(std::chrono::steady_clock::now() - g_rs64_t0).count();
}

extern "C" void rs64_dpc_get_cumulative_histogram(uint32_t out[64]);
extern "C" uint32_t rs64_dpc_get_cumulative_fullsyncs();
extern "C" void rs64_cine_dump_if_stuck(void);
extern "C" void rs64_cine_progress_log(void);
// LLE GFX entry — runs the RSP recompile (factor5_boot + factor5_ucode)
// against this task's data. Defined in main.cpp. OSTask comes from
// ultramodern/ultra64.h (already included via ultramodern.hpp).
extern "C" int rs64_run_lle_gfx(uint8_t* rdram, const OSTask* task);

// s4267: per-second phase aggregates (ROGUESQ_S4267=1). Phases: 0 pipeline wait, 1 tex-upload wait (fb), 2 fb uploaders+gfx worker wait,
// 3 drawdata/transforms uploaders+worker+tex wait, 4 RT64 State::fullSync total, 5 processDisplayLists (RDP submit), 6 rs64_run_lle_gfx, 7 send_dl total.
#include <chrono>
#include <mutex>
#include <string>
#include <atomic>
extern "C" uint32_t rs64_ram_top; // s6132
extern std::atomic<uint64_t> g_rs64_rt64_tri_accepted, g_rs64_rt64_rect_accepted;
volatile uint32_t g_rs64_g1cf_tasks = 0, g_rs64_g1cf_dsize = 0;  // s6070 g1cf: gfx tasks / dl bytes since last VI
extern "C" { volatile int g_rs64_dd_blk = 0; }  // s6070: set by the s6036 dd patch (funcs_9.c): 1 = dd multiplier active this call
static struct G1cf { uint32_t subs = 0, bytes = 0, tri = 0, maxlen = 0, lastlen = 0; uint64_t rt0 = 0, rr0 = 0; } s_g1cf;  // s6070
extern "C" void rs64_g1d_tb2(const char* tag);

namespace s4267 {
static const bool on = [] { const char* e = std::getenv("ROGUESQ_S4267"); return e && *e && *e != '0'; }();
static std::mutex m;
static const auto t0 = std::chrono::steady_clock::now();
struct A { uint64_t n = 0; double sum = 0, mx = 0; };
static A agg[36];
static int last_sec = -1;
static void flush_locked(int sec) {
    static const char* nm[36] = {"pipeline","texwait","fbwait","ddwait","fullSync","procDL","lleRun","sendDl","fsFlush","fsSubmitFb","fsMisc","fsValidate","fsUpload","fsRspPipe","fsRender","fsEvict","fsProj","fsAdvance","fsTail","fsRsz","fsTiles","fsRenderSync","fsEvictOnly","fsPostEvict","fsScript","fsUpdScreen","ctlSleep","usUpload","usCopyHash","usAdvance","usPre","usRest","usResize","usMemcpy","usHash","pad"};
    std::string o;
    char b[96];
    for (int i = 0; i < 35; ++i) {
        std::snprintf(b, sizeof b, " %s=%llu/%.0fms/max%.0f", nm[i], (unsigned long long)agg[i].n, agg[i].sum, agg[i].mx);
        o += b; agg[i] = A{};
    }
    std::fprintf(stderr, "[s4267] t=%d%s\n", sec, o.c_str());
}
struct T {
    int p; std::chrono::steady_clock::time_point a = std::chrono::steady_clock::now();
    explicit T(int ph) : p(ph) {}
    ~T();
};
}
extern "C" void rs64_s4267_acc(int phase, double ms) {
    if (!s4267::on) return;
    std::lock_guard<std::mutex> lk(s4267::m);
    const int sec = (int)std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - s4267::t0).count();
    if (s4267::last_sec >= 0 && sec != s4267::last_sec) s4267::flush_locked(s4267::last_sec);
    s4267::last_sec = sec;
    auto& a = s4267::agg[phase]; a.n++; a.sum += ms; if (ms > a.mx) a.mx = ms;
}
s4267::T::~T() { if (on) rs64_s4267_acc(p, std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - a).count()); }

// RDP/RSP register state owned by this file
static uint8_t DMEM[0x1000];
static uint8_t IMEM[0x1000];

static unsigned int MI_INTR_REG      = 0;
static unsigned int DPC_START_REG    = 0;
static unsigned int DPC_END_REG      = 0;
static unsigned int DPC_CURRENT_REG  = 0;
static unsigned int DPC_STATUS_REG   = 0;
static unsigned int DPC_CLOCK_REG    = 0;
static unsigned int DPC_BUFBUSY_REG  = 0;
static unsigned int DPC_PIPEBUSY_REG = 0;
static unsigned int DPC_TMEM_REG     = 0;

static void dummy_check_interrupts() {}

static ultramodern::renderer::SetupResult map_result(RT64::Application::SetupResult r) {
    switch (r) {
    case RT64::Application::SetupResult::Success:                  return ultramodern::renderer::SetupResult::Success;
    case RT64::Application::SetupResult::DynamicLibrariesNotFound: return ultramodern::renderer::SetupResult::DynamicLibrariesNotFound;
    case RT64::Application::SetupResult::InvalidGraphicsAPI:       return ultramodern::renderer::SetupResult::InvalidGraphicsAPI;
    case RT64::Application::SetupResult::GraphicsAPINotFound:      return ultramodern::renderer::SetupResult::GraphicsAPINotFound;
    case RT64::Application::SetupResult::GraphicsDeviceNotFound:   return ultramodern::renderer::SetupResult::GraphicsDeviceNotFound;
    }
    return ultramodern::renderer::SetupResult::GraphicsDeviceNotFound;
}

// ---------------------------------------------------------------------------
// RT64Context — wraps RT64::Application as a RendererContext
// ---------------------------------------------------------------------------
namespace recomp {

class RT64Context : public ultramodern::renderer::RendererContext {
public:
    std::unique_ptr<RT64::Application> app;
    static inline std::atomic<bool> s_hle_disabled{false};

    RT64Context(uint8_t* rdram, ultramodern::renderer::WindowHandle window_handle, bool debug) {
        static unsigned char dummy_rom_header[0x40] = {};

        RT64::Application::Core appCore{};
#if defined(_WIN32)
        appCore.window = window_handle.window;
#elif defined(__linux__) || defined(__ANDROID__)
        appCore.window = window_handle;
#elif defined(__APPLE__)
        appCore.window.window = window_handle.window;
        appCore.window.view   = window_handle.view;
#endif

        appCore.checkInterrupts = dummy_check_interrupts;
        appCore.HEADER  = dummy_rom_header;
        appCore.RDRAM   = rdram;
        appCore.DMEM    = DMEM;
        appCore.IMEM    = IMEM;

        appCore.MI_INTR_REG     = &MI_INTR_REG;
        appCore.DPC_START_REG   = &DPC_START_REG;
        appCore.DPC_END_REG     = &DPC_END_REG;
        appCore.DPC_CURRENT_REG = &DPC_CURRENT_REG;
        appCore.DPC_STATUS_REG  = &DPC_STATUS_REG;
        appCore.DPC_CLOCK_REG   = &DPC_CLOCK_REG;
        appCore.DPC_BUFBUSY_REG = &DPC_BUFBUSY_REG;
        appCore.DPC_PIPEBUSY_REG= &DPC_PIPEBUSY_REG;
        appCore.DPC_TMEM_REG    = &DPC_TMEM_REG;

        ultramodern::renderer::ViRegs* vi = ultramodern::renderer::get_vi_regs();
        appCore.VI_STATUS_REG         = &vi->VI_STATUS_REG;
        appCore.VI_ORIGIN_REG         = &vi->VI_ORIGIN_REG;
        appCore.VI_WIDTH_REG          = &vi->VI_WIDTH_REG;
        appCore.VI_INTR_REG           = &vi->VI_INTR_REG;
        appCore.VI_V_CURRENT_LINE_REG = &vi->VI_V_CURRENT_LINE_REG;
        appCore.VI_TIMING_REG         = &vi->VI_TIMING_REG;
        appCore.VI_V_SYNC_REG         = &vi->VI_V_SYNC_REG;
        appCore.VI_H_SYNC_REG         = &vi->VI_H_SYNC_REG;
        appCore.VI_LEAP_REG           = &vi->VI_LEAP_REG;
        appCore.VI_H_START_REG        = &vi->VI_H_START_REG;
        appCore.VI_V_START_REG        = &vi->VI_V_START_REG;
        appCore.VI_V_BURST_REG        = &vi->VI_V_BURST_REG;
        appCore.VI_X_SCALE_REG        = &vi->VI_X_SCALE_REG;
        appCore.VI_Y_SCALE_REG        = &vi->VI_Y_SCALE_REG;

        RT64::ApplicationConfiguration appConfig;
        appConfig.useConfigurationFile = false;
        appConfig.detectDataPath = false;

        app = std::make_unique<RT64::Application>(appCore, appConfig);
        // Dev mode default: ON for Debug builds (so F1 inspector is available),
        // OFF for Release. Override either way with ROGUESQ_HLE_DEV_MODE=0/1.
        // The inspector can be unstable with our HLE flow under load — fall
        // back to ROGUESQ_HLE_DEV_MODE=0 if it locks up an investigation.
#ifdef _DEBUG
        bool dev_mode_on = true;
#else
        bool dev_mode_on = false;
#endif
        if (const char* v = std::getenv("ROGUESQ_HLE_DEV_MODE")) {
            dev_mode_on = (v[0] && v[0] != '0');
        }
        app->userConfig.developerMode = debug || dev_mode_on;
        app->userConfig.displayBuffering = RT64::UserConfiguration::DisplayBuffering::Triple;
        // G1d (s6103): ROGUESQ_ASPECT=orig|expand|<w>:<h> selects RT64 output aspect. Opt-in; unset = retail (Original).
        if (const char* as = std::getenv("ROGUESQ_ASPECT")) {
            using AR = RT64::UserConfiguration::AspectRatio;
            if (!strcmp(as, "expand") || !strcmp(as, "auto")) { app->userConfig.aspectRatio = AR::Expand; app->userConfig.extAspectRatio = AR::Expand; }
            else if (const char* c = strchr(as, ':')) { double w = atof(as), h = atof(c + 1); if (w > 0 && h > 0) { app->userConfig.aspectRatio = AR::Manual; app->userConfig.aspectTarget = w / h; } }
            fprintf(stderr, "[g1d] ROGUESQ_ASPECT=%s applied\n", as);
        }
        if (const char* rm = std::getenv("ROGUESQ_RESMULT")) { double m = std::atof(rm); if (m > 0.0) app->userConfig.resolutionMultiplier = m; }

        // PresentEarly ON by default. Our cinematic stays on a single VI fb
        // address; without PresentEarly, RT64's updateScreen only pushes a
        // present when VI changes or RDRAM at VI_ORIGIN changes — neither
        // happens for HLE single-buffer flow, so rendered fbPairs never
        // reach the swapchain. PresentEarly pushes presents directly from
        // fullSync. Opt out via ROGUESQ_HLE_PRESENT_EARLY=0.
        bool present_early = true;
        if (const char* v = std::getenv("ROGUESQ_HLE_PRESENT_EARLY")) {
            present_early = (v[0] && v[0] != '0');
        }
        if (present_early) {
            app->enhancementConfig.presentation.mode =
                RT64::EnhancementConfiguration::Presentation::Mode::PresentEarly;
        }

        // 2026-05-10: Apply Zelda64Recomp's RT64 enhancement-config settings.
        // Without these, RT64's textureLOD selection and gbi branching take
        // different paths that cause our texture lookups to sample stale or
        // empty TMEM regions → glyph texrects render invisibly.
        //
        // forceBranch=true: forces gbi depth branches, preventing LODs from
        // kicking in for textures that don't have proper mipmap chains.
        //
        // textureLOD.scale=true: scales LODs based on output resolution so
        // higher-res rendering doesn't bias toward LOD 0 unnecessarily.
        app->enhancementConfig.f3dex.forceBranch = true;
        app->enhancementConfig.textureLOD.scale = true;
        // Diagnostic: ROGUESQ_GFX_API=vulkan forces Vulkan instead of the
        // default D3D12 (Automatic on Windows). Lets us isolate whether crashes
        // are DX12-specific or apply to both backends.
        if (const char* api = std::getenv("ROGUESQ_GFX_API")) {
            if (std::string_view(api) == "vulkan") {
                app->userConfig.graphicsAPI = RT64::UserConfiguration::GraphicsAPI::Vulkan;
                fprintf(stderr, "[RT64] graphics API forced to Vulkan via ROGUESQ_GFX_API\n");
            } else if (std::string_view(api) == "d3d12") {
                app->userConfig.graphicsAPI = RT64::UserConfiguration::GraphicsAPI::D3D12;
                fprintf(stderr, "[RT64] graphics API forced to D3D12 via ROGUESQ_GFX_API\n");
            }
        }

        uint32_t thread_id = 0;
#ifdef _WIN32
        thread_id = window_handle.thread_id;
#endif
        setup_result = map_result(app->setup(thread_id));
        if (setup_result != ultramodern::renderer::SetupResult::Success) {
            fprintf(stderr, "[RT64] setup failed: %d\n", (int)setup_result);
            app = nullptr;
        }
        else {
            // Propagate construction-time enhancementConfig changes (e.g.
            // PresentEarly) into RT64's internal state. setup() initializes
            // before these are read, so without this call the changes stay
            // dormant.
            app->updateEnhancementConfig();
            // ROGUESQ_NO_GPU_COPY=1 — force framebuffer.copyWithGPU off so
            // texture loads that overlap a tracked color image fall back to
            // RDRAM instead of a GPU tile-copy. Hangar-floor A/B: the
            // remaining orange/black band looks like a mis-mapped FB sample.
            if (const char *v = std::getenv("ROGUESQ_NO_GPU_COPY")) {
                if (v[0] && v[0] != '0') {
                    app->emulatorConfig.framebuffer.copyWithGPU = false;
                    app->updateEmulatorConfig();
                    fprintf(stderr, "[RT64] framebuffer.copyWithGPU forced OFF via ROGUESQ_NO_GPU_COPY\n");
                }
            }
            fprintf(stderr, "[RT64] enhancementConfig: presentMode=%d forceBranch=%d textureLOD.scale=%d copyWithGPU=%d\n",
                    (int)app->enhancementConfig.presentation.mode,
                    (int)app->enhancementConfig.f3dex.forceBranch,
                    (int)app->enhancementConfig.textureLOD.scale,
                    (int)app->emulatorConfig.framebuffer.copyWithGPU);
            fflush(stderr);
        }
        if (app && app->appWindow) {
            // Diagnostic: dump the post-setup state of RT64's window/filter
            // so we know whether F1-F4 keypresses can reach the inspector.
            fprintf(stderr,
                "[RT64] post-setup: sdlWindow=%p sdlEventFilterInstalled=%d windowHook=%p developerMode=%d usesWindowMessageFilter=%d\n",
                (void*)app->appWindow->sdlWindow,
                (int)app->appWindow->sdlEventFilterInstalled,
#ifdef _WIN32
                (void*)app->appWindow->windowHook,
#else
                (void*)nullptr,
#endif
                (int)app->userConfig.developerMode,
                (int)app->usesWindowMessageFilter());
            fflush(stderr);
        }
        g_rt64_app.store(app.get());
    }

    bool valid() override {
        return app != nullptr;
    }

    bool update_config(const ultramodern::renderer::GraphicsConfig&,
                       const ultramodern::renderer::GraphicsConfig&) override {
        return true;
    }

    void enable_instant_present() override {
        // PresentEarly is set at construction (see ctor); this host hook
        // would re-apply it, but constructor-time setup is sufficient.
        // Respects ROGUESQ_HLE_PRESENT_EARLY=0 opt-out.
        if (app) {
            bool present_early = true;
            if (const char* v = std::getenv("ROGUESQ_HLE_PRESENT_EARLY")) {
                present_early = (v[0] && v[0] != '0');
            }
            if (present_early) {
                app->enhancementConfig.presentation.mode =
                    RT64::EnhancementConfiguration::Presentation::Mode::PresentEarly;
                app->updateEnhancementConfig();
            }
        }
    }

    void send_dl(const OSTask* task) override {
        s4267::T s4267_total(7);
        struct RdpqScope { RdpqScope() { ultramodern::rs64_rdpq_task_enter(); } ~RdpqScope() { ultramodern::rs64_rdpq_task_exit(); } } rdpq_scope; // s6705
        const uint32_t m5_task_seq = rs64_m5_host_send_begin(
            static_cast<uint32_t>(task->t.data_ptr));
        // ROGUESQ_LLE_FORCE=1: route this GFX task through the LLE RSP
        // recompile path INSTEAD of HLE. factor5_gfx_runner reproduces what
        // real-hardware RSP would do — runs boot+main ucode against DMEM,
        // emits RDP byte stream via mtc0 DPC_END writes, src/rsp/dpc_bridge.cpp
        // forwards those bytes to RT64 via processDisplayLists(isHLE=false).
        // This is the path needed for Factor 5's op 0x02 (vertex transform)
        // to actually emit triangles — HLE drops it.
        static int s_lle_force = -1;
        if (s_lle_force < 0) {
            const char* v = std::getenv("ROGUESQ_LLE_FORCE");
            s_lle_force = (v && *v && v[0] != '0') ? 1 : 0;
            if (s_lle_force) {
                fprintf(stderr, "[lle-force] LLE path enabled for M_GFXTASK; "
                                "HLE send_dl will skip processDisplayLists\n");
                fflush(stderr);
            }
        }
        // s1890: rs64_is_hangar_vi() reads shared VI regs from the render
        // thread every M_GFXTASK, unconditionally, since the s1856/s1872
        // hangar-gate work (post-s844). ROGUESQ_SKIP_HANGAR_PROBE=1 disables
        // that read to test whether it is implicated in the s1888/s1889
        // VI-1024 reachability regression.
        static int s_skip_hangar_probe = -1;
        if (s_skip_hangar_probe < 0) {
            const char* v = std::getenv("ROGUESQ_SKIP_HANGAR_PROBE");
            s_skip_hangar_probe = (v && *v && v[0] != '0') ? 1 : 0;
        }
        const bool in_hangar = s_skip_hangar_probe ? false : (rs64_is_hangar_vi() != 0);
        // Hangar LLE does not require LLE_FORCE. Attribution LLE never
        // leaves VI 640 (s1856, s1872), so the hangar census uses HLE
        // through the frontend and switches to LLE-solo only at hangar
        // origins 0x006ab400 / 0x006ab800.
        if (app && (s_lle_force || in_hangar)) {
            // Gate LLE to attribution-shape DLs only. Cinematic-phase tasks
            // hit Unhandled jump target in factor5_ucode_recompiled and
            // corrupt RT64's deferred state (which then asserts 4-bit
            // readback downstream). Attribution DL signature: data_ptr =
            // 0x80720108 for task #1, 0x80720318 for task #2 of the same
            // phase (observed). Both live in the 0x80720000 page. Restrict
            // LLE to data_ptr in that page so cinematic tasks bypass it.
            //
            // ROGUESQ_LLE_UNGATED=1 disables this gate (debug/regression).
            const uint32_t dlp = (uint32_t)task->t.data_ptr;
            static int s_lle_ungated = -1;
            if (s_lle_ungated < 0) {
                const char* v = std::getenv("ROGUESQ_LLE_UNGATED");
                s_lle_ungated = (v && *v && v[0] != '0') ? 1 : 0;
            }
            const bool in_attribution_page = ((dlp & 0xFFFF0000u) == 0x80720000u);
            static int s_lle_hangar_only = -1;
            if (s_lle_hangar_only < 0) {
                const char* v = std::getenv("ROGUESQ_LLE_HANGAR_ONLY");
                s_lle_hangar_only = (v && *v && v[0] != '0') ? 1 : 0;
            }
            const bool lle_this = s_lle_ungated
                || in_hangar
                || (s_lle_force && in_attribution_page && !s_lle_hangar_only);
            if (lle_this) {
                static int s_n = 0;
                int n = ++s_n;
                int r;
                { s4267::T s4267_run(6); r = rs64_run_lle_gfx(app->core.RDRAM, task); }
                if (n <= 8 || (n & 31) == 0) {
                    const char *gate = in_attribution_page ? "attr"
                        : (in_hangar ? "hangar" : "ungated");
                    fprintf(stderr, "[lle send_dl #%d] gate=%s exit=%d task->ucode=0x%08X dl=0x%08X\n",
                            n, gate,
                            r, (unsigned)task->t.ucode, dlp);
                    fflush(stderr);
                }
                // ROGUESQ_LLE_SOLO=1 skips the HLE fallthrough below. By default
                // we run HLE in parallel so HLE's green fillRect-override marker
                // stays visible alongside whatever LLE produces.
                static int s_lle_solo = -1;
                if (s_lle_solo < 0) {
                    const char* v = std::getenv("ROGUESQ_LLE_SOLO");
                    s_lle_solo = (v && *v && v[0] != '0') ? 1 : 0;
                }
                if (s_lle_solo || in_hangar) {
                    rs64_m5_host_edge("send-return", m5_task_seq,
                                      static_cast<uint32_t>(task->t.data_ptr),
                                      0, 0, 1, -1, -1);
                    return;
                }
                // Fall through to HLE below.
            } else {
                // Cinematic / N64-logo / other tasks: HLE only. Skip LLE.
                static int s_skip_count = 0;
                int sn = ++s_skip_count;
                if (sn <= 4 || (sn & 127) == 0) {
                    fprintf(stderr, "[lle send_dl skip #%d] non-attribution DL dl=0x%08X (LLE bypassed)\n",
                            sn, dlp);
                    fflush(stderr);
                }
            }
        }

        // Standard HLE pipeline (matches Zelda64Recompiled / Starfox64Recomp).
        // RT64's GBI database now includes the Factor 5 ucode signatures (see
        // lib/rt64/src/gbi/rt64_gbi_f3dfactor5.cpp), so loadUCodeGBI matches
        // and dispatches commands via the F3DFACTOR5 handlers.
        //
        // Mask 0x3FFFFFF strips the KSEG0 bits to get the physical RDRAM
        // offset that processDisplayLists expects.
        // ROGUESQ_LOG_OPCODE_HIST=1: per-call opcode histogram of the first
        // 256 DL commands at task->t.data_ptr. Lets us compare which
        // F3DFACTOR5 opcodes fire during attribution vs N64-logo phase to
        // test the "some opcode carries attribution-glyph semantics but is
        // currently no-op'd in our HLE" hypothesis.
        if (app) {
            // ROGUESQ_DUMP_UCODE=path — dump task ucode (IMEM) + ucode_data
            // (DMEM-bound segment) to disk on the first call so the F3DFACTOR5
            // ucode can be disassembled offline to decode op 0x02 semantics.
            static int s_dumped_ucode = 0;
            if (!s_dumped_ucode) {
                const char* dump_path = std::getenv("ROGUESQ_DUMP_UCODE");
                if (dump_path && *dump_path) {
                    s_dumped_ucode = 1;
                    const uint32_t ucode_phys = (uint32_t)task->t.ucode & 0x3FFFFFF;
                    const uint32_t udata_phys = (uint32_t)task->t.ucode_data & 0x3FFFFFF;
                    const uint32_t udata_size = task->t.ucode_data_size ? task->t.ucode_data_size : 0x800;
                    uint8_t* rdram = app->core.RDRAM;
                    // Standard RSP ucode IMEM is 4KB. Dump 8KB to be safe.
                    char ipath[512], dpath[512];
                    snprintf(ipath, sizeof ipath, "%s.imem.bin", dump_path);
                    snprintf(dpath, sizeof dpath, "%s.dmem.bin", dump_path);
                    FILE* f = fopen(ipath, "wb");
                    if (f) {
                        uint8_t buf[0x2000];
                        for (uint32_t i = 0; i < sizeof(buf); ++i) {
                            uint32_t off = ucode_phys + i;
                            buf[i] = (off < (rs64_ram_top - 0x80000000u)) ? rdram[off ^ 3] : 0;
                        }
                        fwrite(buf, 1, sizeof(buf), f);
                        fclose(f);
                        fprintf(stderr, "[dump-ucode] wrote IMEM %u bytes to %s (src=0x%08X)\n",
                                (unsigned)sizeof(buf), ipath, ucode_phys);
                    }
                    f = fopen(dpath, "wb");
                    if (f) {
                        std::vector<uint8_t> buf(udata_size);
                        for (uint32_t i = 0; i < udata_size; ++i) {
                            uint32_t off = udata_phys + i;
                            buf[i] = (off < (rs64_ram_top - 0x80000000u)) ? rdram[off ^ 3] : 0;
                        }
                        fwrite(buf.data(), 1, udata_size, f);
                        fclose(f);
                        fprintf(stderr, "[dump-ucode] wrote DMEM %u bytes to %s (src=0x%08X)\n",
                                udata_size, dpath, udata_phys);
                    }
                    fflush(stderr);
                }
            }
            // ROGUESQ_DUMP_VTXDATA=path — dump 64 KB starting at RAM
            // 0x80700000 and 0x80710000 on the first send_dl call. These
            // are the addresses op 0x01 references in attribution DLs
            // (alternating between consecutive submissions). Offline
            // decode reveals what vertex / asset data the F3DFACTOR5
            // ucode reads to drive op 0x02's matrix-vertex pipeline.
            static int s_dumped_vtx = 0;
            if (!s_dumped_vtx) {
                const char* dump_path = std::getenv("ROGUESQ_DUMP_VTXDATA");
                if (dump_path && *dump_path) {
                    s_dumped_vtx = 1;
                    uint8_t* rdram = app->core.RDRAM;
                    // Extended dump set: add the .data segment region around
                    // the state-setup sub-DL (0x80037658) to search for
                    // static vertex arrays.
                    for (uint32_t base : { 0x00700000u, 0x00710000u, 0x00037000u }) {
                        char path[512];
                        snprintf(path, sizeof path, "%s.0x%08X.bin", dump_path, base);
                        FILE* f = fopen(path, "wb");
                        if (f) {
                            uint8_t buf[0x10000];
                            for (uint32_t i = 0; i < sizeof(buf); ++i) {
                                uint32_t off = base + i;
                                buf[i] = (off < (rs64_ram_top - 0x80000000u)) ? rdram[off ^ 3] : 0;
                            }
                            fwrite(buf, 1, sizeof(buf), f);
                            fclose(f);
                            fprintf(stderr, "[dump-vtxdata] wrote 64 KB to %s\n", path);
                        }
                    }
                    fflush(stderr);
                }
            }
            static int s_op_hist = -1;
            if (s_op_hist < 0) {
                const char* v = std::getenv("ROGUESQ_LOG_OPCODE_HIST");
                s_op_hist = (v && *v && v[0] != '0') ? 1 : 0;
            }
            if (s_op_hist) {
                static int s_oh_count = 0;
                int ohn = ++s_oh_count;
                const uint32_t dl_phys = (uint32_t)task->t.data_ptr & 0x3FFFFFF;
                uint8_t* rdram = app->core.RDRAM;
                uint32_t hist[256] = {0};
                uint32_t total = 0;
                // Walk up to 256 8-byte commands (or stop on G_ENDDL=0xDF or
                // a zeroed slot). Follow at most 2 G_DL jumps so we get a
                // representative sample even when Factor 5 chains via G_DL.
                uint32_t addr = dl_phys;
                uint32_t stack[16];
                int sp = 0;
                int jumps_left = 16;
                // Track first 8 instances of each "interesting" no-op'd
                // opcode so we can see if their payloads encode something
                // meaningful (like a DMA src/dst pair).
                uint64_t op02_payloads[8] = {0};
                int op02_count = 0;
                uint64_t op80_payloads[8] = {0};
                int op80_count = 0;
                for (int i = 0; i < 1024; ++i) {
                    if (addr + 8u > (rs64_ram_top - 0x80000000u)) break;
                    uint8_t op = rdram[addr ^ 3];
                    hist[op]++;
                    total++;
                    if (op == 0x02 && op02_count < 8) {
                        uint64_t w = 0;
                        for (int k = 0; k < 8; ++k) {
                            w = (w << 8) | rdram[(addr + k) ^ 3];
                        }
                        op02_payloads[op02_count++] = w;
                    }
                    if (op == 0x80 && op80_count < 8) {
                        uint64_t w = 0;
                        for (int k = 0; k < 8; ++k) {
                            w = (w << 8) | rdram[(addr + k) ^ 3];
                        }
                        op80_payloads[op80_count++] = w;
                    }
                    // F3D-style G_ENDDL = 0xB8 (Factor 5 uses F3D's 0xB8,
                    // not F3DEX2's 0xDF). Pop on B8.
                    if (op == 0xB8) {
                        if (sp > 0) { addr = stack[--sp]; continue; }
                        break;
                    }
                    if (op == 0xDF) break;
                    // F3D G_DL = 0x06, F3DEX2 G_DL = 0xDE.
                    // 0x06 in Factor 5: branch=byte1 (0=push, 1=branch).
                    if ((op == 0x06 || op == 0xDE) && jumps_left > 0) {
                        uint8_t branch = rdram[(addr + 1) ^ 3];
                        uint32_t w1 = 0;
                        for (int k = 0; k < 4; ++k) {
                            w1 = (w1 << 8) | rdram[(addr + 4 + k) ^ 3];
                        }
                        uint32_t target = w1 & 0x3FFFFFF;
                        if (branch == 0) {  // G_DL push: save return addr
                            if (sp < 16) stack[sp++] = addr + 8;
                        }
                        addr = target;
                        jumps_left--;
                        continue;
                    }
                    addr += 8;
                }
                // Dump full DL bytes for the first call so we can hand-decode
                // the attribution DL structure.
                if (ohn == 1) {
                    uint32_t a = dl_phys;
                    int dump_stack_sp = 0;
                    uint32_t dump_stack[16];
                    int dump_jumps = 16;
                    fprintf(stderr, "[opcode-hist #1 FULL DL DUMP] start=0x%08X\n", dl_phys);
                    for (int i = 0; i < 256; ++i) {
                        if (a + 8u > (rs64_ram_top - 0x80000000u)) break;
                        uint64_t w = 0;
                        for (int k = 0; k < 8; ++k) {
                            w = (w << 8) | rdram[(a + k) ^ 3];
                        }
                        uint8_t op = rdram[a ^ 3];
                        fprintf(stderr, "  %08X: %016llX  op=%02X\n",
                                a, (unsigned long long)w, op);
                        if (op == 0xB8) {
                            if (dump_stack_sp > 0) { a = dump_stack[--dump_stack_sp]; continue; }
                            break;
                        }
                        if (op == 0xDF) break;
                        if ((op == 0x06 || op == 0xDE) && dump_jumps > 0) {
                            uint8_t branch = rdram[(a + 1) ^ 3];
                            uint32_t w1 = 0;
                            for (int k = 0; k < 4; ++k) {
                                w1 = (w1 << 8) | rdram[(a + 4 + k) ^ 3];
                            }
                            uint32_t target = w1 & 0x3FFFFFF;
                            if (branch == 0) {
                                if (dump_stack_sp < 16) dump_stack[dump_stack_sp++] = a + 8;
                            }
                            a = target;
                            dump_jumps--;
                            continue;
                        }
                        a += 8;
                    }
                    fflush(stderr);
                }
                fprintf(stderr, "[opcode-hist #%d] dl=0x%08X total=%u", ohn, dl_phys, total);
                for (int op = 0; op < 256; ++op) {
                    if (hist[op]) {
                        fprintf(stderr, " %02X=%u", op, hist[op]);
                    }
                }
                fprintf(stderr, "\n");
                if (op02_count > 0) {
                    fprintf(stderr, "[opcode-hist #%d op02 payloads]", ohn);
                    for (int k = 0; k < op02_count; ++k) {
                        fprintf(stderr, " %016llX", (unsigned long long)op02_payloads[k]);
                    }
                    fprintf(stderr, "\n");
                }
                if (op80_count > 0) {
                    fprintf(stderr, "[opcode-hist #%d op80 payloads]", ohn);
                    for (int k = 0; k < op80_count; ++k) {
                        fprintf(stderr, " %016llX", (unsigned long long)op80_payloads[k]);
                    }
                    fprintf(stderr, "\n");
                }
                fflush(stderr);
            }
        }
        if (app) {
            static int s_count = 0;
            static uint32_t s_last_ucode = 0;
            static uint32_t s_last_data = 0;
            int n = ++s_count;
            const bool ucode_changed = (task->t.ucode != s_last_ucode) || (task->t.ucode_data != s_last_data);
            if (n <= 8 || (n & 63) == 0 || ucode_changed) {
                // Capture workload state pre- and post-DL so we can see
                // fbPair growth and presentEarly matcher activity.
                int wq_wc_pre = app->workloadQueue ? (int)app->workloadQueue->writeCursor : -1;
                int pq_wc_pre = app->presentQueue ? (int)app->presentQueue->writeCursor : -1;
                fprintf(stderr,
                    "[hle send_dl #%d]%s type=%u ucode=0x%08X data=0x%08X dl=0x%08X size=%u wq=%d pq=%d\n",
                    n, ucode_changed ? " [UCODE-CHANGE]" : "",
                    (unsigned)task->t.type, (unsigned)task->t.ucode,
                    (unsigned)task->t.ucode_data, (unsigned)task->t.data_ptr,
                    (unsigned)task->t.data_size,
                    wq_wc_pre, pq_wc_pre);
                fflush(stderr);
            }
            s_last_ucode = task->t.ucode;
            s_last_data = task->t.ucode_data;
            if (s_hle_disabled.load(std::memory_order_relaxed)) {
                rs64_m5_host_edge("send-return", m5_task_seq,
                                  static_cast<uint32_t>(task->t.data_ptr),
                                  0, 0, 1, -1, -1);
                return;
            }
            app->state->rsp->reset();
            app->interpreter->loadUCodeGBI(
                task->t.ucode & 0x3FFFFFF,
                task->t.ucode_data & 0x3FFFFFF,
                true);
#ifdef _WIN32
            static std::atomic<int> s_seh_streak{0};
            __try {
                int wq_wc_pre = app->workloadQueue ? (int)app->workloadQueue->writeCursor : -1;
                int pq_wc_pre = app->presentQueue ? (int)app->presentQueue->writeCursor : -1;
                app->processDisplayLists(app->core.RDRAM,
                                         task->t.data_ptr & 0x3FFFFFF,
                                         0,
                                         /*isHLE*/ true);
                s_seh_streak.store(0, std::memory_order_relaxed);
                // Post-DL: see if workload + present cursors moved. Track
                // distinct transition patterns so we can spot when pq
                // *should* be advancing but isn't.
                if (n <= 8 || (n & 63) == 0) {
                    int wq_wc_post = app->workloadQueue ? (int)app->workloadQueue->writeCursor : -1;
                    int pq_wc_post = app->presentQueue ? (int)app->presentQueue->writeCursor : -1;
                    int wc = app->workloadQueue ? (int)app->workloadQueue->writeCursor : 0;
                    auto& wl = app->workloadQueue->workloads[wc];
                    auto& wlPrev = app->workloadQueue->workloads[(wc + app->workloadQueue->workloads.size() - 1) % app->workloadQueue->workloads.size()];
                    fprintf(stderr,
                        "[hle send_dl #%d post] wq=%d->%d pq=%d->%d nextFbPairs=%u prevFbPairs=%u\n",
                        n, wq_wc_pre, wq_wc_post, pq_wc_pre, pq_wc_post,
                        (unsigned)wl.fbPairCount, (unsigned)wlPrev.fbPairCount);
                    fflush(stderr);
                }

                // Default ON: needed for stability in cinematic phase (workload's
                // fbPairCount grows unbounded without flushing). Disable via
                // ROGUESQ_HLE_AUTO_FULLSYNC=0 to investigate cases where it might
                // double-fire and overwrite a present.
                static bool s_auto_fullsync = []() {
                    const char* v = std::getenv("ROGUESQ_HLE_AUTO_FULLSYNC");
                    if (v && v[0]) return v[0] != '0';
                    return true;
                }();
                if (app->state) {
                    // Conditional fullSync. Factor 5's cinematic DLs emit fullSync
                    // mid-DL but the post-fullSync workload accumulates fbPairs
                    // unbounded (60→229+ in one DL) without committing, eventually
                    // tripping RT64's internal limits. We flush when the current
                    // workload has uncommitted work; the gate skips the case where
                    // Factor 5's natural fullSync already advanced the cursor
                    // (next workload starts empty so needs_flush=false).
                    // Override OFF via ROGUESQ_HLE_AUTO_FULLSYNC=0 (default ON).
                    if (s_auto_fullsync) {
                        int wc = app->state->ext.workloadQueue->writeCursor;
                        auto& wl = app->state->ext.workloadQueue->workloads[wc];
                        const bool needs_flush = (wl.fbPairCount > wl.fbPairSubmitted) ||
                                                 (app->state->drawCall.triangleCount > 0);
                        if (needs_flush) {
                            app->state->dlCpuProfiler.start();
                            app->state->fullSync();
                            app->state->dlCpuProfiler.end();
                        }
                    }
                }
            }
            __except (EXCEPTION_EXECUTE_HANDLER) {
                // Log and try to keep going. The previous behavior latched
                // s_hle_disabled on first SEH and killed all subsequent
                // rendering — too aggressive: transient boot AVs would
                // permanently kill the screen. Only latch-off if SEHs
                // hit 3 IN A ROW with no successful submission between.
                int streak = s_seh_streak.fetch_add(1, std::memory_order_relaxed) + 1;
                fprintf(stderr, "[hle send_dl] SEH streak=%d in processDisplayLists "
                                "ucode=0x%08X data=0x%08X dl=0x%08X%s\n",
                                streak,
                                (unsigned)task->t.ucode, (unsigned)task->t.ucode_data,
                                (unsigned)task->t.data_ptr,
                                streak >= 3 ? " — HLE submission DISABLED" : "");
                fflush(stderr);
                if (streak >= 3) {
                    s_hle_disabled.store(true, std::memory_order_relaxed);
                }
                if (app && app->state) {
                    app->state->dlCpuProfiler.startedTimestamp = RT64::Timestamp{};
                }
            }
#else
            app->processDisplayLists(app->core.RDRAM,
                                     task->t.data_ptr & 0x3FFFFFF,
                                     0,
                                     /*isHLE*/ true);
#endif
            rs64_m5_host_edge("send-return", m5_task_seq,
                              static_cast<uint32_t>(task->t.data_ptr),
                              0, 0, 1, -1, -1);
        }
    }

    void update_screen() override {
        ultramodern::rs64_rdpq_drain(); // s6705: no-op unless ROGUESQ_RDP_ASYNC queued ranges outside a task
        if (app) {
            ultramodern::renderer::ViRegs* boundary_vi =
                ultramodern::renderer::get_vi_regs();
            rs64_vi_boundary_log("screen", rs64_vi_boundary_screen_request(),
                                 boundary_vi->VI_ORIGIN_REG,
                                 boundary_vi->VI_WIDTH_REG);

            // Always log first 4 + every 64th update_screen so we can tell
            // whether VI events are firing at all. The visual-output question
            // depends entirely on this being called regularly.
            static int s_n = 0;
            static bool s_filter_logged = false;
            ++s_n;
            { rs64_s4899_vi((uint32_t)s_n, ultramodern::renderer::get_vi_regs()->VI_WIDTH_REG); } // s4899
            rs64_vi_n_g = (uint32_t)s_n; // s5816 VI counter for guest-side diagnostics

            // Watchdog moved to its own thread (rs64_cine_start_watchdog_thread)
            // because the gfx_thread can itself be deadlocked on the same mutex
            // chain that's hanging the game thread.

            // Host-side buffer-arbiter state-machine driver. Under HLE, the game's
            // bufferArbiterProducerMark blocks on a recv that's supposed to be
            // signaled by viRetraceHandlerThread; if that signal misses (timing),
            // slot states stagnate in 0/1/2 and func_8000BF60's scan loop spins
            // waiting for state 3 or 4. We auto-advance any slot in state 2 → 3
            // (CONSUMED), state 3 → 4 (PRESENTED), state 4 → 5 (DISPLAYED),
            // state 5 → 0 (FREE). This mimics what viRetraceHandlerThread would
            // naturally do over multiple ticks but condenses it into one
            // update_screen pass. Gated by ROGUESQ_FORCE_BUFFER_PROGRESS=1.
            static const bool s_force_buffer = [](){
                const char *v = std::getenv("ROGUESQ_FORCE_BUFFER_PROGRESS");
                return v && v[0] && v[0] != '0';
            }();
            if (s_force_buffer && app->core.RDRAM) {
                // Slot state array at 0x80128EAA[N]; count byte at 0x80128EAD.
                // Conservative driver: only advance the retrace-thread's
                // transitions (4 PRESENTED → 5 DISPLAYED → 0 FREE).
                // Producer-mark's transitions (2→3 and X→4) are left to fire
                // naturally via bufferArbiterProducerMark — bypassing those
                // would cause ultramodern sync invariants to break (saw an AV
                // in ultramodern's mesgqueue/threads area on the aggressive
                // version of this driver at iter 1255).
                const uint32_t STATE_BASE = 0x128EAA;
                const uint32_t COUNT_ADDR = 0x128EAD;
                if (COUNT_ADDR < (rs64_ram_top - 0x80000000u)) {
                    uint8_t total = app->core.RDRAM[COUNT_ADDR ^ 3];
                    if (total > 0 && total <= 8) {
                        for (uint8_t i = 0; i < total; i++) {
                            uint32_t addr = STATE_BASE + i;
                            if (addr >= (rs64_ram_top - 0x80000000u)) continue;
                            uint8_t state = app->core.RDRAM[addr ^ 3];
                            switch (state) {
                                case 4: app->core.RDRAM[addr ^ 3] = 5; break;  // PRESENTED → DISPLAYED
                                case 5: app->core.RDRAM[addr ^ 3] = 0; break;  // DISPLAYED → FREE
                                default: break;  // leave 0/1/2/3 to game code
                            }
                        }
                    }
                }
            }

            // Game-state poller: read engine globals via RDRAM and log changes.
            // Tells us whether the game is actually progressing past boot, even
            // when the screen is black. Enable via ROGUESQ_LOG_GAMESTATE=1.
            static const bool s_log_gs = [](){
                const char *v = std::getenv("ROGUESQ_LOG_GAMESTATE");
                return v && v[0] && v[0] != '0';
            }();
            if (s_log_gs && app->core.RDRAM && (s_n & 63) == 0) {
                // Globals from docs/game-architecture.md. RDRAM is little-endian
                // word-swap relative to MIPS BE — use byte index ^ 3.
                auto rb = [&](uint32_t addr) -> uint8_t {
                    if (addr >= (rs64_ram_top - 0x80000000u)) return 0;
                    return app->core.RDRAM[addr ^ 3];
                };
                auto rw = [&](uint32_t addr) -> uint32_t {
                    return (uint32_t(rb(addr)) << 24) | (uint32_t(rb(addr+1)) << 16) |
                           (uint32_t(rb(addr+2)) <<  8) |  uint32_t(rb(addr+3));
                };
                uint8_t curLevel = rb(0x130B70);
                uint8_t curCraft = rb(0x130B41);
                uint32_t cineStatePtr = rw(0x0B0934);
                uint8_t cineStage = rb(0x0B0938);
                uint32_t curCutsceneFile = rw(0x0B1904);
                uint8_t unk20 = rb(0x130B60);  // gGameSettings+0x20 (menu sub-state)
                uint8_t unk21 = rb(0x130B61);  // gGameSettings+0x21 (cinematic sub-state)
                uint8_t unk22 = rb(0x130B62);  // gGameSettings+0x22 (mission sub-state)

                static uint8_t s_last_level = 0xFF, s_last_craft = 0xFF;
                static uint32_t s_last_cineState = 0xFFFFFFFF;
                static uint8_t s_last_cineStage = 0xFF;
                static uint32_t s_last_cutscene = 0xFFFFFFFF;
                static uint8_t s_last_u20 = 0xFF, s_last_u21 = 0xFF, s_last_u22 = 0xFF;
                bool changed = (curLevel != s_last_level) || (curCraft != s_last_craft) ||
                               (cineStatePtr != s_last_cineState) || (cineStage != s_last_cineStage) ||
                               (curCutsceneFile != s_last_cutscene) ||
                               (unk20 != s_last_u20) || (unk21 != s_last_u21) || (unk22 != s_last_u22);
                if (changed || (s_n & 511) == 0) {
                    fprintf(stderr,
                        "[gamestate vi=#%d] level=%u craft=%u u20=%u u21=%u u22=%u cineState=0x%08X cineStage=%u cutscene=0x%08X%s\n",
                        s_n, curLevel, curCraft, unk20, unk21, unk22,
                        cineStatePtr, cineStage, curCutsceneFile,
                        changed ? " [CHANGED]" : "");
                    // Dump first 32 bytes of cutscene struct (filename field). Helps confirm WHICH cutscene.
                    if (curCutsceneFile >= 0x80000000 && curCutsceneFile < rs64_ram_top) {
                        uint32_t off = curCutsceneFile - 0x80000000;
                        fprintf(stderr, "  cutscene-filename: \"");
                        for (int i = 0; i < 32 && (off + i) < (rs64_ram_top - 0x80000000u); i++) {
                            uint8_t b = app->core.RDRAM[(off + i) ^ 3];
                            if (b >= 0x20 && b < 0x7F) fputc(b, stderr);
                            else if (b == 0) break;
                            else fputc('?', stderr);
                        }
                        fprintf(stderr, "\"\n");
                    }
                    fflush(stderr);
                    s_last_level = curLevel;
                    s_last_craft = curCraft;
                    s_last_cineState = cineStatePtr;
                    s_last_cineStage = cineStage;
                    s_last_cutscene = curCutsceneFile;
                    s_last_u20 = unk20;
                    s_last_u21 = unk21;
                    s_last_u22 = unk22;
                }
            }
            // Log once when the SDL filter actually installs.
            if (!s_filter_logged && app->appWindow && app->appWindow->sdlEventFilterInstalled) {
                fprintf(stderr,
                    "[RT64] sdlEventFilter NOW installed at update_screen #%d (sdlWindow=%p)\n",
                    s_n, (void*)app->appWindow->sdlWindow);
                fflush(stderr);
                s_filter_logged = true;
            }
            // Phase marker. The game's phases are distinguishable by VI width
            // (512 = hangar, 1024 = the hi-res tiled phase before it), and
            // session 17 wasted several captures because run-to-run timing
            // varies by tens of seconds — the Factor 5 logo landed at 18s in
            // one run and 44s in another, so fixed capture windows kept
            // missing the phase they were aimed at. This fires the instant the
            // width changes, so a capture harness can gate on the phase itself
            // rather than on elapsed time.
            {
                static uint32_t s_last_width = 0xFFFFFFFF;
                ultramodern::renderer::ViRegs* pvi = ultramodern::renderer::get_vi_regs();
                const uint32_t w = pvi->VI_WIDTH_REG;
                if (w != s_last_width) {
                    const double el = rs64_elapsed_seconds();
                    fprintf(stderr,
                        "[phase] vi_width=%u (was %u) origin=0x%08X at %.1fs update_screen #%d\n",
                        w, s_last_width == 0xFFFFFFFF ? 0u : s_last_width,
                        pvi->VI_ORIGIN_REG, el, s_n);
                    fflush(stderr);
                    s_last_width = w;
                    // Publish the phase change so RT64-side censuses can scope
                    // themselves to one phase (see rs64_phase_ord below).
                    rs64_m5_route_fingerprint_phase(w, pvi->VI_ORIGIN_REG);
                    rs64_bump_phase_ord();
                    rs64_m5_selector_ai_call_latch_join(
                        w, pvi->VI_ORIGIN_REG & 0x00FFFFFFu, rs64_phase_ord());
                    if (w == 640u && (pvi->VI_ORIGIN_REG & 0x00FFFFFFu) == 0x006A2900u) {
                        rs64_s4597_target_store('C', 0xFFFFFFFFu, 0x8017C000u, 0u);
                    }
                    if (w == 1024u && (pvi->VI_ORIGIN_REG & 0x00FFFFFFu) == 0x00790400u) {
                        rs64_m5_b40_route_title_transition();
                    }
                }
                rs64_m5_route_fingerprint_snapshot(w, pvi->VI_ORIGIN_REG);
                // s4636: dump the VI colour image (512 wide, 16bpp, 260 rows)
                // every 8th update_screen while width==512, so the RDRAM edge
                // columns can be compared offline against the screenshot edge.
                static const char* s_edge_dir = std::getenv("ROGUESQ_EDGE_DUMP");
                static int s_edge_files = 0;
                // s4639: col-511 snapshot of both hangar buffers at each of the
                // first 24 512-wide VI updates (H-stale discriminator).
                static const char* s_bw = std::getenv("ROGUESQ_BUF_WATCH");
                static int s_snap_n = 0;
                if (s_bw && s_bw[0] != '0' && w == 512u && s_snap_n < 24 && app->core.RDRAM) {
                    s_snap_n++;
                    const uint8_t* rd = app->core.RDRAM;
                    uint32_t nz[2] = {0, 0}, nzb[2] = {0, 0};
                    static const uint32_t bases[2] = {0x656400u, 0x6AB400u};
                    for (int b = 0; b < 2; ++b)
                        for (uint32_t r = 0; r < 240; ++r) {
                            const uint32_t o = bases[b] + r * 1024u;
                            if (rd[(o + 1022u) ^ 3] | rd[(o + 1023u) ^ 3]) nz[b]++;
                            if (rd[(o + 1020u) ^ 3] | rd[(o + 1021u) ^ 3]) nzb[b]++;
                        }
                    fprintf(stderr,
                        "[s4639-snap] n=%d vi_n=%d org=%06X col511_nz 656400=%u 6AB400=%u col510_nz 656400=%u 6AB400=%u\n",
                        s_snap_n, (int)s_n, pvi->VI_ORIGIN_REG & 0x00FFFFFFu, nz[0], nz[1], nzb[0], nzb[1]);
                }
                if (s_edge_dir && w == 512u && (s_n & 7) == 0 && s_edge_files < 400) {
                    const uint8_t* rd = app->core.RDRAM;
                    const uint32_t org = pvi->VI_ORIGIN_REG & 0x00FFFFFFu;
                    char path[512];
                    snprintf(path, sizeof(path), "%s/edge_%05d_%08X.bin", s_edge_dir, s_n, org);
                    if (FILE* f = fopen(path, "wb")) {
                        std::vector<uint8_t> buf(512u * 2u * 260u);
                        for (uint32_t i = 0; i < buf.size(); i++) {
                            uint32_t off = org + i;
                            buf[i] = (off < (rs64_ram_top - 0x80000000u)) ? rd[off ^ 3] : 0;
                        }
                        fwrite(buf.data(), 1, buf.size(), f);
                        fclose(f);
                        s_edge_files++;
                    }
                }
            }

            {   // s6070 g1c: per-VI frame summary (ROGUESQ_G1CF=1), unbudgeted, tagged with the dd toggle state
                static int s_f = -1;
                if (s_f < 0) { const char *e = std::getenv("ROGUESQ_G1CF"); s_f = (e && *e && *e != '0') ? 1 : 0; }
                if (s_f) {
                    uint64_t t1 = g_rs64_rt64_tri_accepted.load(), r1 = g_rs64_rt64_rect_accepted.load();
                    fprintf(stderr, "[g1cf] vi=%d dd=%d tasks=%u dsize=%u subs=%u bytes=%u tri=%u rt64tri=%llu rt64rect=%llu maxlen=%u lastlen=%u\n",
                            s_n, g_rs64_dd_blk, g_rs64_g1cf_tasks, g_rs64_g1cf_dsize, s_g1cf.subs, s_g1cf.bytes, s_g1cf.tri,
                            (unsigned long long)(t1 - s_g1cf.rt0), (unsigned long long)(r1 - s_g1cf.rr0), s_g1cf.maxlen, s_g1cf.lastlen);
                    s_g1cf = G1cf(); s_g1cf.rt0 = t1; s_g1cf.rr0 = r1; g_rs64_g1cf_tasks = 0; g_rs64_g1cf_dsize = 0;
                }
            }
            if (s_n <= 4 || (s_n & 63) == 0) {
                ultramodern::renderer::ViRegs* vi = ultramodern::renderer::get_vi_regs();
                // Sample 16 bytes at VI_ORIGIN to see if there's actual pixel
                // data there. If all zeros, VI is sampling an empty buffer.
                uint32_t origin = vi->VI_ORIGIN_REG & 0x00FFFFFF;
                uint32_t any_nonzero = 0;
                if (app && app->core.RDRAM && origin > 0 && origin + 16 < (rs64_ram_top - 0x80000000u)) {
                    for (int i = 0; i < 16; i++) {
                        any_nonzero |= app->core.RDRAM[origin + i];
                    }
                }
                // Also log presentQueue + workloadQueue cursors so we can
                // see whether PresentEarly is pushing presents and the
                // workload worker is consuming them. If presents stay flat
                // while workloads advance, the matcher is failing.
                int pq_wc = app->presentQueue ? (int)app->presentQueue->writeCursor : -1;
                int wq_wc = app->workloadQueue ? (int)app->workloadQueue->writeCursor : -1;
                fprintf(stderr,
                    "[vi] update_screen #%d origin=0x%08X width=%u status=0x%X v_current=%u nonzero=%d fs=%u pq.wc=%d wq.wc=%d\n",
                    s_n, vi->VI_ORIGIN_REG, vi->VI_WIDTH_REG,
                    vi->VI_STATUS_REG, vi->VI_V_CURRENT_LINE_REG, any_nonzero != 0,
                    rs64_dpc_get_cumulative_fullsyncs(),
                    pq_wc, wq_wc);
                // Every 256 updates, also dump the cumulative opcode histogram.
                if ((s_n & 255) == 0) {
                    uint32_t hist[64];
                    rs64_dpc_get_cumulative_histogram(hist);
                    uint32_t total = 0;
                    for (int i = 0; i < 64; ++i) total += hist[i];
                    fprintf(stderr, "  [opcode-hist total=%u top:", total);
                    uint32_t copy[64];
                    for (int i = 0; i < 64; ++i) copy[i] = hist[i];
                    for (int slot = 0; slot < 6; ++slot) {
                        int max_idx = 0;
                        for (int i = 0; i < 64; ++i) {
                            if (copy[i] > copy[max_idx]) max_idx = i;
                        }
                        if (copy[max_idx] == 0) break;
                        fprintf(stderr, " op%02X=%u", max_idx, copy[max_idx]);
                        copy[max_idx] = 0;
                    }
                    fprintf(stderr, "]\n");
                }
                fflush(stderr);
            }
            app->updateScreen();
        }
    }

    void shutdown() override {
        ultramodern::rs64_rdpq_drain(); // s6705
        if (app) {
            g_rt64_app.store(nullptr);
            app->end();
            app.reset();
        }
    }

    uint32_t get_display_framerate() const override {
        if (app && app->presentQueue) {
            return app->presentQueue->ext.sharedResources->swapChainRate;
        }
        return 60;
    }

    float get_resolution_scale() const override {
        return app ? float(app->userConfig.resolutionMultiplier) : 1.0f;
    }
};

std::unique_ptr<ultramodern::renderer::RendererContext>
create_render_context(uint8_t* rdram, ultramodern::renderer::WindowHandle window, bool developer_mode) {
    return std::make_unique<RT64Context>(rdram, window, developer_mode);
}

} // namespace recomp

// Free-function bridge for the LLE DPC pipeline (see src/rsp/dpc_bridge.cpp).
// Forwards raw RDP byte ranges from the recompiled Factor 5 ucode into the
// live RT64::Application for rasterization (isHLE=false).
namespace ultramodern {
    // Catch AVs from RT64's processDisplayLists. Currently
    // RT64::RDP::updateCallTexcoords (rt64_rdp.cpp:1343) reads
    // workload.drawData.callTiles[drawCall.tileIndex + t] before that
    // vector has been populated, when Factor 5's ucode emits a TEXRECT
    // without prior tile setup. The OOB returns garbage in release
    // builds (and our _ITERATOR_DEBUG_LEVEL=0 path) which then AVs on
    // the load. Catch the SEH exception here and skip the submission;
    // we lose that frame's content but the game continues running.
    // SEH-protected submission. RT64's processDisplayLists can AV in
    // RDP::updateCallTexcoords (rt64_rdp.cpp:1343) when Factor 5's ucode
    // emits a TEXRECT-like sequence without prior tile setup —
    // drawCall.tileCount > 0 but workload.drawData.callTiles is empty,
    // so the indexed read goes past end.
    //
    // After the AV, even if we reset dlCpuProfiler, downstream RT64 state
    // is corrupted in multiple places (next assert is at
    // rt64_framebuffer_manager.cpp:248). Rather than chase each, we
    // disable submission entirely after the first SEH. Game continues to
    // run, just without further graphics output. Better than crashing.
    // TODO: pre-validate at dpc_bridge to drop bad commands BEFORE submit.
    static std::atomic<bool> s_rdp_disabled{false};

    // s6705 G1e: ROGUESQ_RDP_ASYNC=1 moves RT64 processing of LLE RDP ranges onto one worker thread so the RSP keeps
    // running while RT64 interprets. The ucode reuses its RDP output ring within a task, so each range's command words are
    // COPIED at submit time and RT64 reads the copy (processDisplayLists takes the command base pointer; textures still come
    // from core.RDRAM, read later than in sync mode, like the real RDP). Contiguous submits are merged up to 4 KB. Ordering
    // is FIFO; send_dl (RAII guard) and update_screen drain the queue, so dp_complete and present still follow every
    // range of the task. Submits outside send_dl run synchronously. ROGUESQ_RDP_ASYNC_TOGGLE=<s> (events.cpp) flips it.
    namespace rdpq {
        struct Job { uint32_t lo = 0, hi = 0; std::vector<uint8_t> w; };
        static std::mutex m;
        static std::condition_variable cv_job, cv_idle;
        static std::deque<Job> q;
        static std::vector<std::vector<uint8_t>> pool;
        static bool busy = false, started = false;
        static Job pend;               // producer-side merge buffer (Gfx thread only)
        static bool pend_has = false;
        static int in_task = 0;        // Gfx thread only
        static uint64_t n_jobs = 0, n_ranges = 0;
        static bool task_async = false; // a range of the current task went to the worker
        // s6706 G1e: per-task split of an async task (ROGUESQ_G1B=1 only): RSP phase (enter -> drain entry), drain wait,
        // worker busy before/after drain entry, producer copy cost, last job; sync tasks log RT64 time inline. One
        // [g1e-aq] line per wall second per arm (as = mode at task entry).
        static const bool aq_on = [] { const char *e = std::getenv("ROGUESQ_G1B"); return e && *e && *e != '0'; }();
        using aclk = std::chrono::steady_clock;
        static inline double aq_ms(aclk::time_point a, aclk::time_point b) { return std::chrono::duration<double, std::milli>(b - a).count(); }
        static std::atomic<uint64_t> wk_busy_ns{0};
        static std::atomic<uint32_t> wk_last_bytes{0}; static std::atomic<uint64_t> wk_last_ns{0}, wk_max_ns{0};
        static aclk::time_point aq_t0 = aclk::now(), task_t0;
        static int task_mode = 0;
        static double t_copy = 0, t_sync = 0; static uint64_t t_bytes = 0, t_jobs = 0, t_calls = 0;
        struct AqAcc { uint64_t n = 0; double rsp = 0, drain = 0, wk = 0, wk_tail = 0, copy = 0, sync = 0, bytes = 0, jobs = 0, calls = 0,
                       pend_jobs = 0, last_kb = 0, last_ms = 0, max_ms = 0, total = 0; };
        static AqAcc aq[2]; static int aq_sec = -1;
        static void aq_print(int sec) {
            for (int a = 0; a < 2; ++a) {
                AqAcc &x = aq[a]; if (!x.n) continue; const double n = (double)x.n;
                std::fprintf(stderr, "[g1e-aq] t=%d as=%d n=%llu total=%.2f rsp=%.2f drain=%.2f wk=%.2f wk_tail=%.2f copy=%.3f sync_rt64=%.2f "
                    "kB=%.1f jobs=%.1f calls=%.1f pend_jobs=%.2f last_kB=%.2f last_ms=%.2f max_job_ms=%.2f\n", sec, a, (unsigned long long)x.n,
                    x.total / n, x.rsp / n, x.drain / n, x.wk / n, x.wk_tail / n, x.copy / n, x.sync / n, x.bytes / n / 1024.0, x.jobs / n,
                    x.calls / n, x.pend_jobs / n, x.last_kb / n, x.last_ms / n, x.max_ms / n);
                x = AqAcc{};
            }
        }
        static void worker() {
            pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
            pthread_setname_np("RS64 RDP async");
            for (;;) {
                Job j;
                {
                    std::unique_lock<std::mutex> lk(m);
                    cv_job.wait(lk, [] { return !q.empty(); });
                    j = std::move(q.front()); q.pop_front(); busy = true;
                }
                RT64::Application *app = g_rt64_app.load();
                const aclk::time_point jt0 = aq_on ? aclk::now() : aclk::time_point{};
                if (app && !s_rdp_disabled.load(std::memory_order_relaxed))
                    app->processDisplayLists(j.w.data() - j.lo, j.lo, j.hi, /*isHLE*/ false);
                if (aq_on) {
                    const uint64_t ns = (uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(aclk::now() - jt0).count();
                    wk_busy_ns += ns; wk_last_ns = ns; wk_last_bytes = (uint32_t)j.w.size();
                    if (ns > wk_max_ns.load()) wk_max_ns = ns;
                }
                {
                    std::lock_guard<std::mutex> lk(m);
                    j.w.clear(); pool.push_back(std::move(j.w)); busy = false;
                    if (q.empty()) cv_idle.notify_all();
                }
            }
        }
        static void flush_pend() {
            if (!pend_has) return;
            pend_has = false;
            if (aq_on) { t_bytes += pend.w.size(); ++t_jobs; }
            std::lock_guard<std::mutex> lk(m);
            if (!started) { started = true; std::thread(worker).detach(); }
            q.push_back(std::move(pend)); ++n_jobs;
            pend = Job{};
            if (!pool.empty()) { pend.w = std::move(pool.back()); pool.pop_back(); }
            cv_job.notify_one();
        }
        static void drain() {
            flush_pend();
            if (!started) return;
            std::unique_lock<std::mutex> lk(m);
            cv_idle.wait(lk, [] { return q.empty() && !busy; });
        }
        // true = queued; false = caller must process synchronously.
        static bool submit(RT64::Application *app, uint32_t lo, uint32_t hi) {
            if (!rs64_rdp_async_on || !in_task || !app->core.RDRAM) { drain(); return false; }
            const aclk::time_point ct0 = aq_on ? aclk::now() : aclk::time_point{};
            if (pend_has && (lo != pend.hi || pend.w.size() >= 4096)) flush_pend();
            if (!pend_has) { pend.lo = lo; pend.hi = lo; pend.w.clear(); pend_has = true; }
            const uint8_t *src = app->core.RDRAM + lo;
            pend.w.insert(pend.w.end(), src, src + (hi - lo));
            pend.hi = hi; ++n_ranges; task_async = true;
            if (aq_on) { t_copy += aq_ms(ct0, aclk::now()); ++t_calls; }
            return true;
        }
    }
    void rs64_rdpq_drain() { rdpq::drain(); }
    void rs64_rdpq_task_enter() {
        using namespace rdpq;
        if (in_task++ == 0 && aq_on) {
            task_t0 = aclk::now(); task_mode = rs64_rdp_async_on ? 1 : 0; t_copy = t_sync = 0; t_bytes = t_jobs = t_calls = 0;
            wk_busy_ns = 0; wk_max_ns = 0; wk_last_ns = 0; wk_last_bytes = 0;
        }
    }
    // The bridge's s4280 cimg walk (rs64_dpc_defer_end) maps RT64's SetColorImage events back to RDRAM by pointer offset,
    // meaningless for a copied range; it skips async tasks and the events they left are cleared here once drained.
    void rs64_rdpq_task_exit() {
        using namespace rdpq;
        if (--in_task == 0 && aq_on) {
            const aclk::time_point d0 = aclk::now();
            double pj = 0; uint64_t wk0;
            { std::lock_guard<std::mutex> lk(m); pj = (double)q.size() + (busy ? 1 : 0) + (pend_has ? 1 : 0); wk0 = wk_busy_ns.load(); }
            drain();
            const aclk::time_point d1 = aclk::now();
            AqAcc &x = aq[task_mode]; ++x.n;
            x.rsp += aq_ms(task_t0, d0); x.drain += aq_ms(d0, d1); x.total += aq_ms(task_t0, d1);
            const uint64_t wk1 = wk_busy_ns.load();
            x.wk += wk1 / 1e6; x.wk_tail += (wk1 - wk0) / 1e6; x.copy += t_copy; x.sync += t_sync;
            x.bytes += t_bytes; x.jobs += t_jobs; x.calls += t_calls; x.pend_jobs += pj;
            x.last_kb += wk_last_bytes / 1024.0; x.last_ms += wk_last_ns / 1e6; x.max_ms += wk_max_ns / 1e6;
            const int sec = (int)(aq_ms(aq_t0, d1) / 1000.0);
            if (aq_sec < 0) aq_sec = sec;
            if (sec != aq_sec) { aq_print(aq_sec); aq_sec = sec; }
        }
        rdpq::drain(); if (rdpq::task_async) { rdpq::task_async = false; RT64::g_s4280_n = 0; } }
}
extern "C" int rs64_rdpq_task_async() { return ultramodern::rdpq::task_async ? 1 : 0; }
namespace ultramodern {

    static void run_rdp_submission(RT64::Application* app, uint32_t lo_phys, uint32_t hi_phys) {
        if (s_rdp_disabled.load(std::memory_order_relaxed)) {
            return;
        }
        static const bool log_e9_consumer = [] {
            const char *e = std::getenv("ROGUESQ_LOG_E9_UNIFIED");
            const char *advance = std::getenv("ROGUESQ_LOG_RDP_ADVANCE");
            const char *all = std::getenv("ROGUESQ_LOG_ALL");
            return (e && *e && *e != '0') || (advance && *advance && *advance != '0') ||
                   (all && *all && *all != '0');
        }();
        if (log_e9_consumer) {
            const uint32_t task = rs64_e9prov_current_task();
            const uint32_t scope = rs64_e9prov_current_scope();
            uint64_t synthetic = 0;
            const bool is_synthetic = rs64_dpc_take_synthetic_consumer(&synthetic);
            if (scope != 0) {
                if (is_synthetic) {
                    fprintf(stderr,
                            "[e9-synthetic-consumer] synthetic=%llu task=%u scope=%s "
                            "serial=%llu lo=0x%06X hi=0x%06X\n",
                            (unsigned long long)synthetic, task,
                            scope == 1 ? "control" : "sec2",
                            (unsigned long long)rs64_dpc_get_last_submit_serial(),
                            lo_phys, hi_phys);
                } else {
                    fprintf(stderr,
                            "[e9-ordinary-consumer] serial=%llu task=%u scope=%s lo=0x%06X hi=0x%06X\n",
                            (unsigned long long)rs64_dpc_get_last_submit_serial(), task,
                            scope == 1 ? "control" : "sec2", lo_phys, hi_phys);
                }
                fflush(stderr);
            }
        }
#ifdef _WIN32
        __try {
            app->processDisplayLists(app->core.RDRAM, lo_phys, hi_phys, /*isHLE*/ false);
        }
        __except (EXCEPTION_EXECUTE_HANDLER) {
            // Reset the profiler timer too in case anything still tries to
            // touch it (the disable flag should prevent that, but be safe).
            if (app->state) {
                app->state->dlCpuProfiler.startedTimestamp = RT64::Timestamp{};
            }
            s_rdp_disabled.store(true, std::memory_order_relaxed);
            fprintf(stderr, "[rdp-submit] SEH in processDisplayLists "
                            "lo=0x%08X hi=0x%08X — RDP submission DISABLED for the rest "
                            "of this session (RT64 state corrupted by AV).\n",
                            lo_phys, hi_phys);
            // Dump cumulative opcode histogram so we can see what kinds of
            // commands the game submitted before the crash. Tells us
            // whether actual rendering work (TEXRECT, FILLRECT, triangles)
            // was happening.
            uint32_t hist[64];
            rs64_dpc_get_cumulative_histogram(hist);
            uint32_t total = 0;
            for (int i = 0; i < 64; ++i) total += hist[i];
            fprintf(stderr, "[rdp-submit] cumulative opcode histogram (total=%u):\n", total);
            // Print top 12 by count
            uint32_t copy[64];
            for (int i = 0; i < 64; ++i) copy[i] = hist[i];
            for (int slot = 0; slot < 12; ++slot) {
                int max_idx = 0;
                for (int i = 0; i < 64; ++i) {
                    if (copy[i] > copy[max_idx]) max_idx = i;
                }
                if (copy[max_idx] == 0) break;
                fprintf(stderr, "  op 0x%02X = %u\n", max_idx, copy[max_idx]);
                copy[max_idx] = 0;
            }
            fflush(stderr);
        }
#else
        if (rdpq::submit(app, lo_phys, hi_phys)) return; // s6705: queued for the async consumer
        const auto st0 = (rdpq::aq_on && rdpq::in_task) ? rdpq::aclk::now() : rdpq::aclk::time_point{}; // s6706
        { s4267::T s4267_pd(5); app->processDisplayLists(app->core.RDRAM, lo_phys, hi_phys, /*isHLE*/ false); }
        if (rdpq::aq_on && rdpq::in_task) { rdpq::t_sync += rdpq::aq_ms(st0, rdpq::aclk::now()); rdpq::t_bytes += hi_phys - lo_phys; ++rdpq::t_calls; }
#endif
    }

    void submit_rdp_range(uint32_t lo_phys, uint32_t hi_phys) {
        RT64::Application *app = g_rt64_app.load();
        if (app && hi_phys > lo_phys) {
            // s6165: join RDP targets to the VI state at the same submission.
            // The budget is per phase so boot traffic cannot hide menu frames.
            static int s_route = -1;
            static int s_words = -1;
            static uint32_t s_route_phase = UINT32_MAX;
            static uint32_t s_route_rows = 0;
            static uint32_t s_word_phase = UINT32_MAX;
            static uint32_t s_word_rows = 0;
            if (s_route < 0) {
                const char* e = std::getenv("ROGUESQ_LOG_RDP_ROUTE");
                s_route = (e && *e && *e != '0') ? 1 : 0;
            }
            if (s_words < 0) {
                const char* e = std::getenv("ROGUESQ_LOG_RDP_WORDS");
                s_words = (e && *e && *e != '0') ? 1 : 0;
            }
            if (s_route || s_words) {
                const uint32_t phase = rs64_phase_ord();
                if (phase != s_route_phase) {
                    s_route_phase = phase;
                    s_route_rows = 0;
                }
                const auto* vi = ultramodern::renderer::get_vi_regs();
                const uint32_t viw = vi ? vi->VI_WIDTH_REG : 0;
                const uint32_t vio = vi ? vi->VI_ORIGIN_REG : 0;
                if (s_route_rows < 160 && viw >= 320 && viw <= 1024 && app->core.RDRAM) {
                    const uint8_t* r = app->core.RDRAM;
                    uint32_t a = lo_phys;
                    bool saw_ci = false, saw_sc = false;
                    while (a + 8 <= hi_phys) {
                        const uint32_t w0 = (uint32_t(r[a ^ 3]) << 24) |
                                            (uint32_t(r[(a + 1) ^ 3]) << 16) |
                                            (uint32_t(r[(a + 2) ^ 3]) << 8) |
                                            uint32_t(r[(a + 3) ^ 3]);
                        const uint32_t w1 = (uint32_t(r[(a + 4) ^ 3]) << 24) |
                                            (uint32_t(r[(a + 5) ^ 3]) << 16) |
                                            (uint32_t(r[(a + 6) ^ 3]) << 8) |
                                            uint32_t(r[(a + 7) ^ 3]);
                        const uint32_t op = (w0 >> 24) & 0x3F;
                        uint32_t n = 8;
                        if (op >= 8 && op <= 15) n = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
                        else if (op == 0x24 || op == 0x25) n = 16;
                        if (s_words && phase >= 4u) {
                            if (phase != s_word_phase) {
                                s_word_phase = phase;
                                s_word_rows = 0;
                            }
                            if (s_word_rows < 20000u) {
                                std::fprintf(stderr,
                                    "[g1d-word] phase=%u row=%u addr=0x%06X op=0x%02X w0=0x%08X w1=0x%08X vi_w=%u vi_o=0x%06X\n",
                                    phase, s_word_rows, a, op, w0, w1, viw, vio & 0xFFFFFFu);
                                ++s_word_rows;
                            }
                        }
                        if (phase >= 4u) {
                            static int s_cmd_log = -1;
                            static uint32_t s_cmd_phase = UINT32_MAX;
                            static uint32_t s_cmd_rows = 0;
                            if (s_cmd_log < 0) {
                                const char *e = std::getenv("ROGUESQ_LOG_G1D_CMD");
                                s_cmd_log = (e && *e && *e != '0') ? 1 : 0;
                            }
                            if (s_cmd_log) {
                                if (phase != s_cmd_phase) { s_cmd_phase = phase; s_cmd_rows = 0; }
                                const bool rect = (op == 0x24 || op == 0x25 ||
                                                   op == 0x2D || op == 0x36);
                                const bool draw = (op >= 0x08 && op <= 0x0F) || rect;
                                const bool structural = (op == 0x2D || op == 0x3F);
                                static uint32_t s_ti_w0 = 0, s_ti_w1 = 0;
                                if (op == 0x3D) { s_ti_w0 = w0; s_ti_w1 = w1; }
                                static uint32_t s_st_w0[8], s_st_w1[8], s_lb_w0 = 0, s_lb_w1 = 0, s_lb_op = 0;
                                if (op == 0x35) { s_st_w0[(w1 >> 24) & 7] = w0; s_st_w1[(w1 >> 24) & 7] = w1; }
                                if (op == 0x33 || op == 0x34) { s_lb_w0 = w0; s_lb_w1 = w1; s_lb_op = op; }
                                if (rect && (op == 0x24 || op == 0x25) && s_cmd_rows < 4000u) {
                                    // s6230: SETTIMG source + content probe for each texrect
                                    const uint32_t ta = s_ti_w1 & 0x7FFFFFu;
                                    uint32_t h = 2166136261u; uint32_t hist[256] = {0}; uint32_t distinct = 0;
                                    uint32_t b0 = 0;
                                    if (ta + 64 <= 0x800000u) {
                                        for (uint32_t i = 0; i < 64; ++i) {
                                            const uint8_t bb = r[(ta + i) ^ 3];
                                            h = (h ^ bb) * 16777619u;
                                            if (!hist[bb]++) ++distinct;
                                            if (i < 4) b0 = (b0 << 8) | bb;
                                        }
                                    }
                                    std::fprintf(stderr,
                                        "[g1d-tex] phase=%u row=%u addr=0x%06X tex=0x%06X fmt=%u siz=%u w=%u hash=0x%08X distinct64=%u b0=0x%08X\n",
                                        phase, s_cmd_rows, a, ta, (s_ti_w0 >> 21) & 7, (s_ti_w0 >> 19) & 3,
                                        (s_ti_w0 & 0xFFF) + 1, h, distinct, b0);
                                    {
                                        // s6231: SETTILE/LOAD params in force + full 4096 B tile dump
                                        const uint32_t t7 = (w1 >> 24) & 7;
                                        std::fprintf(stderr,
                                            "[g1d-tex2] phase=%u row=%u addr=0x%06X tile=%u st_w0=0x%08X st_w1=0x%08X st7_w0=0x%08X st0_w0=0x%08X ld_op=0x%02X ld_w0=0x%08X ld_w1=0x%08X\n",
                                            phase, s_cmd_rows, a, t7, s_st_w0[t7], s_st_w1[t7], s_st_w0[7], s_st_w0[0], s_lb_op, s_lb_w0, s_lb_w1);
                                        static uint32_t s_dumped = 0;
                                        if (s_dumped < 70u && ta + 4096 <= 0x800000u) {
                                            char fn[160];
                                            std::snprintf(fn, sizeof(fn), "scratch/agent/m6/s6231_tiles/%02u_%06X.bin", s_dumped, ta);
                                            if (FILE* df = std::fopen(fn, "wb")) {
                                                uint8_t buf[4096];
                                                for (uint32_t i = 0; i < 4096; ++i) buf[i] = r[(ta + i) ^ 3];
                                                std::fwrite(buf, 1, 4096, df); std::fclose(df);
                                            }
                                            ++s_dumped;
                                        }
                                    }
                                }
                                if ((draw || structural) && s_cmd_rows < 4000u) {
                                    uint32_t x0 = 0, y0 = 0, x1 = 0, y1 = 0;
                                    bool central = false;
                                    if (rect) {
                                        x0 = ((w0 >> 12) & 0xFFF) >> 2;
                                        y0 = (w0 & 0xFFF) >> 2;
                                        x1 = ((w1 >> 12) & 0xFFF) >> 2;
                                        y1 = (w1 & 0xFFF) >> 2;
                                        if (x0 > x1) { const uint32_t t = x0; x0 = x1; x1 = t; }
                                        if (y0 > y1) { const uint32_t t = y0; y0 = y1; y1 = t; }
                                        central = x0 < (viw * 2u) / 3u && x1 > viw / 3u && y1 > y0;
                                    }
                                    const char *kind = (op == 0x3F) ? "cimg" :
                                        (op == 0x2D) ? "scissor" :
                                        (op == 0x24) ? "texrect" :
                                        (op == 0x25) ? "texrectflip" :
                                        (op == 0x36) ? "fillrect" : "tri";
                                    std::fprintf(stderr,
                                        "[g1d-cmd] phase=%u row=%u addr=0x%06X op=0x%02X kind=%s "
                                        "rect=%u,%u-%u,%u central=%u w0=0x%08X w1=0x%08X "
                                        "task=%u root_dl=0x%06X guest_pc=0x%08X "
                                        "dpc=0x%06X-0x%06X submit=%llu\n",
                                        phase, s_cmd_rows++, a, op, kind,
                                        x0, y0, x1, y1, central ? 1u : 0u, w0, w1,
                                        rs64_e9prov_current_task(),
                                        rs64_e9prov_current_root_dl() & 0x7FFFFFu,
                                        (uint32_t)g_rs64_last_guest_pc,
                                        g_rsp_dpc_start & 0x3FFFFFFu,
                                        g_rsp_dpc_end & 0x3FFFFFFu,
                                        (unsigned long long)rs64_dpc_get_last_submit_serial());
                                }
                            }
                        }
                        if (op == 0x3F) {
                            if (g_rs64_g1d_join_phase.load(std::memory_order_relaxed) != phase)
                                g_rs64_g1d_join_cis.store(0, std::memory_order_relaxed);
                            g_rs64_g1d_join_phase.store(phase, std::memory_order_relaxed);
                            g_rs64_g1d_join_lo.store(lo_phys, std::memory_order_relaxed);
                            g_rs64_g1d_join_hi.store(hi_phys, std::memory_order_relaxed);
                            g_rs64_g1d_join_ci_w.store((w0 & 0x3FF) + 1u, std::memory_order_relaxed);
                            g_rs64_g1d_join_ci_a.store(w1 & 0xFFFFFFu, std::memory_order_relaxed);
                            g_rs64_g1d_join_cis.fetch_add(1, std::memory_order_relaxed);
                            {
                                std::lock_guard<std::mutex> lock(g_rs64_g1d_ci_mutex);
                                if (g_rs64_g1d_ci_frame.size() < 64) {
                                    g_rs64_g1d_ci_frame.push_back({(w0 & 0x3FF) + 1u,
                                                                    w1 & 0xFFFFFFu,
                                                                    lo_phys, hi_phys});
                                }
                            }
                            std::fprintf(stderr, "[rdp-route] phase=%u lo=0x%06X len=%u ci_w=%u ci_a=0x%06X vi_w=%u vi_o=0x%06X\n",
                                phase, lo_phys, hi_phys - lo_phys, (w0 & 0x3FF) + 1, w1 & 0xFFFFFF, viw, vio & 0xFFFFFF);
                            saw_ci = true;
                        } else if (op == 0x2D) {
                            std::fprintf(stderr, "[rdp-route] phase=%u lo=0x%06X len=%u sc=%u,%u-%u,%u vi_w=%u vi_o=0x%06X\n",
                                phase, lo_phys, hi_phys - lo_phys, (w0 >> 12) & 0xFFF, w0 & 0xFFF,
                                (w1 >> 12) & 0xFFF, w1 & 0xFFF, viw, vio & 0xFFFFFF);
                            saw_sc = true;
                        }
                        a += n;
                    }
                    if (saw_ci || saw_sc) ++s_route_rows;
                    std::fflush(stderr);
                }
            }
            {
                // s6206: phase-4 color/texture image addresses inside the
                // early-image span. A summary line fires even when the hit
                // count is zero, so a miss is not a silent scanner.
                static int s_img = -1;
                static uint32_t s_subs = 0, s_ci = 0, s_ti = 0, s_ci_hit = 0, s_ti_hit = 0;
                static uint32_t s_hits = 0;
                static uint32_t s_last_ci = 0, s_last_ti = 0;
                static int s_logged_ci = 0;
                // Distinct phase-4 TI addresses in [0xA6A000, 0xB00000).
                // The 48-line hit log stays capped. Past 256 kept addresses,
                // below-pool addresses are dropped (ov=1) but max still
                // moves, and above-pool addresses go in the side buffer so
                // that count stays exact until abcap.
                static uint32_t s_ti_set[256];
                static uint32_t s_ti_extra[256];
                static uint32_t s_ti_n = 0;
                static uint32_t s_ti_extra_n = 0;
                static uint32_t s_ti_min = 0xFFFFFFFFu;
                static uint32_t s_ti_max = 0;
                static uint32_t s_ti_ov = 0;
                static uint32_t s_ti_extra_ov = 0;
                static int s_ti_saw_ctl = 0;
                static int s_ti_saw_wide = 0;
                if (s_img < 0) {
                    const char* e = std::getenv("ROGUESQ_LOG_G1D_TASK");
                    s_img = (e && *e && *e != '0') ? 1 : 0;
                }
                if (s_img && app->core.RDRAM && rs64_phase_ord() == 4u) {
                    const uint8_t* r = app->core.RDRAM;
                    uint32_t a = lo_phys;
                    while (a + 8 <= hi_phys) {
                        const uint32_t w0 = (uint32_t(r[a ^ 3]) << 24) |
                                            (uint32_t(r[(a + 1) ^ 3]) << 16) |
                                            (uint32_t(r[(a + 2) ^ 3]) << 8) |
                                            uint32_t(r[(a + 3) ^ 3]);
                        const uint32_t w1 = (uint32_t(r[(a + 4) ^ 3]) << 24) |
                                            (uint32_t(r[(a + 5) ^ 3]) << 16) |
                                            (uint32_t(r[(a + 6) ^ 3]) << 8) |
                                            uint32_t(r[(a + 7) ^ 3]);
                        const uint32_t op = (w0 >> 24) & 0x3F;
                        uint32_t ncmd = 8;
                        if (op >= 8 && op <= 15) {
                            ncmd = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0);
                        } else if (op == 0x24 || op == 0x25) {
                            ncmd = 16;
                        }
                        if (op == 0x3F || op == 0x3D) {
                            const uint32_t addr = w1 & 0x00FFFFFFu;
                            const bool hit = addr >= 0x00A6A000u && addr < 0x00B00000u;
                            if (op == 0x3F) { ++s_ci; s_last_ci = addr; if (hit) ++s_ci_hit; }
                            else { ++s_ti; s_last_ti = addr; if (hit) ++s_ti_hit; }
                            if (hit && s_hits < 48u) {
                                ++s_hits;
                                std::fprintf(stderr,
                                    "[g1d-img-hit] kind=%s addr=0x%06X w0=0x%08X w1=0x%08X pc=0x%08X n=%u\n",
                                    op == 0x3F ? "ci" : "ti", addr, w0, w1,
                                    (uint32_t)g_rs64_last_guest_pc, s_hits);
                                std::fflush(stderr);
                            }
                            if (op == 0x3D && hit) {
                                if (addr < s_ti_min) s_ti_min = addr;
                                if (addr > s_ti_max) s_ti_max = addr;
                                if (addr == 0x00A6AA10u) s_ti_saw_ctl = 1;
                                if (addr == 0x00AE5F20u) s_ti_saw_wide = 1;
                                {
                                    static const uint32_t k_tb[3] = {0x00A6AA10u, 0x00AE5F20u, 0x00AE6B20u};
                                    static bool s_tb_done[3] = {false, false, false};
                                    static uint32_t s_tb_hits[3] = {0, 0, 0};
                                    for (int ti = 0; ti < 3; ++ti) {
                                        if (addr == k_tb[ti] && ++s_tb_hits[ti] == 2u) rs64_g1d_tb2("ti-hit2");
                                        if (addr != k_tb[ti] || s_tb_done[ti]) continue;
                                        s_tb_done[ti] = true;
                                        rs64_g1d_tb2("ti-hit1");
                                        uint32_t wv[8];
                                        for (uint32_t k = 0; k < 8u; ++k) {
                                            uint32_t v = 0;
                                            for (uint32_t b = 0; b < 4u; ++b)
                                                v = (v << 8) | r[(addr + k * 4u + b) ^ 3u];
                                            wv[k] = v;
                                        }
                                        std::fprintf(stderr,
                                            "[g1d-tb] addr=0x%06X %08X %08X %08X %08X %08X %08X %08X %08X\n",
                                            addr, wv[0], wv[1], wv[2], wv[3], wv[4], wv[5], wv[6], wv[7]);
                                        std::fflush(stderr);
                                    }
                                }
                                bool seen = false;
                                for (uint32_t i = 0; i < s_ti_n; ++i) {
                                    if (s_ti_set[i] == addr) { seen = true; break; }
                                }
                                if (!seen) {
                                    for (uint32_t i = 0; i < s_ti_extra_n; ++i) {
                                        if (s_ti_extra[i] == addr) { seen = true; break; }
                                    }
                                }
                                if (!seen) {
                                    if (s_ti_n < 256u) {
                                        s_ti_set[s_ti_n++] = addr;
                                    } else {
                                        s_ti_ov = 1u;
                                        uint32_t pool_now = 0;
                                        const uint32_t ram_bytes = rs64_ram_top > 0x80000000u
                                            ? (rs64_ram_top - 0x80000000u) : 0u;
                                        if (0x1163ECu <= ram_bytes) {
                                            for (uint32_t b = 0; b < 4u; ++b) {
                                                pool_now = (pool_now << 8) | r[(0x1163E8u + b) ^ 3u];
                                            }
                                        }
                                        const uint32_t pool_phys = pool_now & 0x00FFFFFFu;
                                        if (pool_phys != 0u && addr >= pool_phys) {
                                            if (s_ti_extra_n < 256u) s_ti_extra[s_ti_extra_n++] = addr;
                                            else s_ti_extra_ov = 1u;
                                        }
                                    }
                                }
                            }
                        }
                        a += ncmd;
                    }
                    ++s_subs;
                    if ((s_ci > 0u && !s_logged_ci) || s_subs <= 4u ||
                        (s_ci == 0u && s_subs <= 64u) || (s_subs % 16u) == 0u) {
                        std::fprintf(stderr,
                            "[g1d-img] phase=4 subs=%u ci=%u ti=%u ci_hit=%u ti_hit=%u last_ci=0x%06X last_ti=0x%06X pc=0x%08X\n",
                            s_subs, s_ci, s_ti, s_ci_hit, s_ti_hit, s_last_ci, s_last_ti,
                            (uint32_t)g_rs64_last_guest_pc);
                        uint32_t pool = 0;
                        const uint32_t ram_bytes = rs64_ram_top > 0x80000000u
                            ? (rs64_ram_top - 0x80000000u) : 0u;
                        if (0x1163ECu <= ram_bytes) {
                            for (uint32_t b = 0; b < 4u; ++b)
                                pool = (pool << 8) | r[(0x1163E8u + b) ^ 3u];
                        }
                        const uint32_t pool_phys = pool & 0x00FFFFFFu;
                        uint32_t above = 0;
                        uint32_t low = 0;
                        uint32_t listed[8];
                        auto take_above = [&](uint32_t a) {
                            if (pool_phys == 0u || a < pool_phys) return;
                            if (above < 8u) listed[above] = a;
                            if (above == 0u || a < low) low = a;
                            ++above;
                        };
                        for (uint32_t i = 0; i < s_ti_n; ++i) take_above(s_ti_set[i]);
                        for (uint32_t i = 0; i < s_ti_extra_n; ++i) take_above(s_ti_extra[i]);
                        char addr_txt[96];
                        addr_txt[0] = 0;
                        if (above >= 1u && above <= 8u) {
                            for (uint32_t i = 1; i < above; ++i) {
                                const uint32_t v = listed[i];
                                uint32_t j = i;
                                while (j > 0u && listed[j - 1u] > v) {
                                    listed[j] = listed[j - 1u];
                                    --j;
                                }
                                listed[j] = v;
                            }
                            size_t used = 0;
                            for (uint32_t i = 0; i < above; ++i) {
                                used += static_cast<size_t>(std::snprintf(
                                    addr_txt + used, sizeof(addr_txt) - used,
                                    "%s0x%06X", i ? "," : "", listed[i]));
                            }
                        }
                        const uint32_t n_known = s_ti_n + s_ti_extra_n;
                        std::fprintf(stderr,
                            "[g1d-ti] n=%u min=0x%06X max=0x%06X above=%u low=0x%06X ov=%u abcap=%u pool=0x%08X saw=%s%s%s%s%s%s\n",
                            n_known, n_known ? s_ti_min : 0u, n_known ? s_ti_max : 0u,
                            above, above ? low : 0u, s_ti_ov, s_ti_extra_ov, pool,
                            s_ti_saw_ctl ? "0xA6AA10" : "",
                            (s_ti_saw_ctl && s_ti_saw_wide) ? "," : "",
                            s_ti_saw_wide ? "0xAE5F20" : "",
                            (!s_ti_saw_ctl && !s_ti_saw_wide) ? "none" : "",
                            addr_txt[0] ? " addrs=" : "",
                            addr_txt);
                        std::fflush(stderr);
                        if (s_ci > 0u) s_logged_ci = 1;
                    }
                }
            }
            // Diagnostic: log the LAST submission's last bytes so we can see
            // what RDP commands trigger RT64's vector-OOB assert. Gate behind
            // ROGUESQ_LOG_RDP_SUBMIT=1.
            static int s_log = -1;
            if (s_log < 0) {
                const char* e = std::getenv("ROGUESQ_LOG_RDP_SUBMIT");
                s_log = (e && *e && *e != '0') ? 1 : 0;
            }
            if (s_log) {
                static int s_count = 0;
                ++s_count;
                uint32_t len = hi_phys - lo_phys;
                fprintf(stderr, "[rdp-submit #%d] lo=0x%08X hi=0x%08X len=%u\n",
                        s_count, lo_phys, hi_phys, len);
                // Dump first 32 bytes of submission (4 commands worth)
                if (len >= 8 && app->core.RDRAM) {
                    uint8_t* bytes = app->core.RDRAM + lo_phys;
                    int dump_len = (int)std::min<uint32_t>(len, 64);
                    fprintf(stderr, "  bytes: ");
                    for (int i = 0; i < dump_len; ++i) {
                        fprintf(stderr, "%02X ", bytes[i]);
                        if ((i & 7) == 7 && i + 1 < dump_len) fprintf(stderr, "\n         ");
                    }
                    fprintf(stderr, "\n");
                }
                fflush(stderr);
            }
            {   // s4517: raw RDP byte dump (RS64_RDP_BIN_PORT=path) for retail rdp.bin diff.
                static FILE *s_bin = nullptr; static int s_bin_init = 0; static uint64_t s_bin_total = 0;
                if (!s_bin_init) { s_bin_init = 1; const char *e = std::getenv("RS64_RDP_BIN_PORT"); if (e && *e) s_bin = fopen(e, "wb"); }
                if (s_bin && app->core.RDRAM && s_bin_total < (600ull << 20)) {
                    uint32_t hdr[4] = {0x50445250u, lo_phys, hi_phys - lo_phys, rs64_phase_ord()};
                    fwrite(hdr, 4, 4, s_bin);
                    fwrite(app->core.RDRAM + lo_phys, 1, hi_phys - lo_phys, s_bin);
                    s_bin_total += 16 + (hi_phys - lo_phys);
                }
            }
            {   // s6070 g1cf: per-VI accumulation (tri counted from the RDP stream, independent of the s5424 gate)
                s_g1cf.subs++; s_g1cf.bytes += hi_phys - lo_phys; s_g1cf.lastlen = hi_phys - lo_phys;
                if (hi_phys - lo_phys > s_g1cf.maxlen) s_g1cf.maxlen = hi_phys - lo_phys;
                if (app->core.RDRAM) { const uint8_t *r = app->core.RDRAM; uint32_t a = lo_phys;
                    while (a + 8 <= hi_phys) { uint32_t op = r[a ^ 3] & 0x3F, n = 8;
                        if (op >= 0x08 && op <= 0x0F) { n = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0); ++s_g1cf.tri; }
                        else if (op == 0x24 || op == 0x25) n = 16;
                        a += n; } }
            }
            {   // s5424: per-submission RDP command census (ROGUESQ_LOG_RDP_TRICOUNT=1) for flight-vs-hangar geometry volume.
                static int s_tc = -1;
                if (s_tc < 0) { const char *e = std::getenv("ROGUESQ_LOG_RDP_TRICOUNT"); s_tc = (e && *e && *e != '0') ? 1 : 0; }
                if (s_tc && app->core.RDRAM) {
                    const uint8_t *r = app->core.RDRAM;
                    uint32_t tri = 0, trect = 0, frect = 0, other = 0, a = lo_phys;
                    while (a + 8 <= hi_phys) {
                        uint32_t op = r[a ^ 3] & 0x3F, n = 8;
                        if (op >= 0x08 && op <= 0x0F) { n = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0); ++tri; }
                        else if (op == 0x24 || op == 0x25) { n = 16; ++trect; }
                        else if (op == 0x36) { ++frect; }
                        else ++other;
                        a += n;
                    }
                    static uint32_t s_tc_n[64]; uint32_t tco = rs64_phase_ord() & 63;
                    if (s_tc_n[tco]++ < 4000)  // s5441: per-phase cap (log flood: 1.2M lines/phase)
                    fprintf(stderr, "[tricnt] ord=%u len=%u tri=%u trect=%u frect=%u other=%u\n",
                            rs64_phase_ord(), hi_phys - lo_phys, tri, trect, frect, other);
                }
            }
            static int s_dr = -1;
            uint64_t dr_t0 = 0, dr_r0 = 0;
            if (s_dr < 0) { const char *e = std::getenv("ROGUESQ_LOG_RT64_DRAWN"); s_dr = (e && *e && *e != '0') ? 1 : 0; }
            if (s_dr) { dr_t0 = g_rs64_rt64_tri_accepted.load(); dr_r0 = g_rs64_rt64_rect_accepted.load(); }
            run_rdp_submission(app, lo_phys, hi_phys);
            static uint32_t s_dr_n[64];
            if (s_dr && s_dr_n[rs64_phase_ord() & 63]++ < 4000) fprintf(stderr, "[rt64drawn] ord=%u tri=%llu rect=%llu\n", rs64_phase_ord(),
                              (unsigned long long)(g_rs64_rt64_tri_accepted.load() - dr_t0),
                              (unsigned long long)(g_rs64_rt64_rect_accepted.load() - dr_r0));
        }
    }
}
