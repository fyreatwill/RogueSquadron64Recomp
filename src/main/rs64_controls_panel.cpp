// s7620 G6b step 3: F6 Controls panel drawn over the presented frame.
// RT64's own F1 inspector has no Metal backend (rt64_inspector.cpp: D3D12/Vulkan only), so the panel owns a separate
// ImGui context and draws through RT64's public post-VI hook (rhi/rt64_render_hooks.h, called on the present thread
// right before the swap chain is presented) with ImGui's Metal backend. Closed panel = the hook returns at once:
// nothing is encoded, the presented frame is untouched.
// Threads: the input poll thread feeds mouse events (rs64_panel_feed); the present thread builds and draws the frame;
// both under g_mu. Binding changes go through main.cpp's rs64_bind_* API (its own mutex).
#include "rs64_controls_panel.h"
#include "rs64_bindings_json.h"
#include <atomic>
#include <chrono>
#include <cstdio>
#include <mutex>
#include <cmath>
#include <cstring>
#include <cstdlib>
#include <pthread.h>
#include "imgui/imgui.h"
#include "rhi/rt64_render_hooks.h"
#include "plume_metal.h"
#if __has_include(<SDL2/SDL.h>)
#include <SDL2/SDL.h>
#else
#include <SDL.h>
#endif

// rs64_imgui_metal.mm
bool rs64_imgui_metal_init(void* mtl_device);
void rs64_imgui_metal_new_frame(void* mtl_texture);
void rs64_imgui_metal_render(ImDrawData* dd, void* mtl_cmdbuf, void* mtl_encoder);
void rs64_imgui_metal_shutdown();

namespace {
std::mutex g_mu;
ImGuiContext* g_ctx = nullptr;
bool g_metal_ok = false;
std::atomic<bool> g_open{false};
std::atomic<uint32_t> g_window_id{0};
std::atomic<uint64_t> g_win_size{0};
std::atomic<uint32_t> g_win_id{0};    // s7639: SDL window ID, main thread (chk arm only)  // s7639: window size in points, (w << 32) | h, written by the main thread only
std::string g_msg;              // status line (save result etc.)
// s7941: the row list, shared by the mouse table and the pad cursor (main.cpp rs64_panel_pad_step moves g_pad_row).
const int k_targets[] = {RS64_N64_A, RS64_N64_B, RS64_N64_Z, RS64_N64_START, RS64_N64_L, RS64_N64_R,
    RS64_N64_CU, RS64_N64_CD, RS64_N64_CL, RS64_N64_CR, RS64_N64_DU, RS64_N64_DD, RS64_N64_DL, RS64_N64_DR,
    RS64_TGT_UP, RS64_TGT_DOWN, RS64_TGT_LEFT, RS64_TGT_RIGHT};
constexpr int k_nrows = (int)(sizeof k_targets / sizeof k_targets[0]);
std::atomic<int> g_pad_row{0};
long g_draws = 0;

const char* tgt_name(int t) {
    switch (t) { case RS64_TGT_UP: return "Stick up"; case RS64_TGT_DOWN: return "Stick down";
                 case RS64_TGT_LEFT: return "Stick left"; case RS64_TGT_RIGHT: return "Stick right"; }
    for (const auto& n : rs64_n64_names) if (n.mask == t) return n.name;
    return "?";
}
const char* tgt_label(int t) {
    switch (t) {
    case RS64_N64_A: return "A"; case RS64_N64_B: return "B"; case RS64_N64_Z: return "Z"; case RS64_N64_START: return "Start";
    case RS64_N64_DU: return "D-Up"; case RS64_N64_DD: return "D-Down"; case RS64_N64_DL: return "D-Left"; case RS64_N64_DR: return "D-Right";
    case RS64_N64_L: return "L"; case RS64_N64_R: return "R";
    case RS64_N64_CU: return "C-Up"; case RS64_N64_CD: return "C-Down"; case RS64_N64_CL: return "C-Left"; case RS64_N64_CR: return "C-Right";
    }
    return tgt_name(t);
}
std::string sources_of(const rs64_bind_table& t, int target) {
    std::string s;
    auto add = [&](const std::string& n) { if (!s.empty()) s += ",  "; s += n; };
    if (target > 0) { for (const auto& e : t.buttons) if (e.n64_mask == target) add(rs64_bind_source_name(e.src)); }
    else {
        const std::vector<int>& v = target == RS64_TGT_UP ? t.key_up : target == RS64_TGT_DOWN ? t.key_down
                                  : target == RS64_TGT_LEFT ? t.key_left : t.key_right;
        for (int k : v) add(std::string("key:") + SDL_GetScancodeName((SDL_Scancode)k));
    }
    return s.empty() ? std::string("(unbound)") : s;
}

void draw_ui() {
    // s7937: ROGUESQ_PANEL_RECTS=1 logs widget rects (window points, the coordinate space SDL mouse events use) whenever
    // the layout moves, so a driver can click the real widgets with OS mouse events (tools/s7937_panel_e2e.zsh).
    static const bool s_rects = [] { const char* v = getenv("ROGUESQ_PANEL_RECTS"); return v && *v == '1'; }();
    static std::string s_rect_last; std::string rect_now;
    auto note_rect = [&](const char* name) {
        if (!s_rects) return;
        const ImVec2 a = ImGui::GetItemRectMin(), b = ImGui::GetItemRectMax();
        char buf[96]; snprintf(buf, sizeof buf, " %s=%.0f,%.0f,%.0f,%.0f", name, a.x, a.y, b.x, b.y); rect_now += buf;
    };
    const ImGuiIO& io = ImGui::GetIO();
    ImGui::SetNextWindowPos(ImVec2(io.DisplaySize.x * 0.5f, io.DisplaySize.y * 0.5f), ImGuiCond_Always, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(io.DisplaySize.x * 0.9f, io.DisplaySize.y * 0.9f), ImGuiCond_Always);
    ImGui::SetNextWindowBgAlpha(0.92f);
    ImGui::Begin("Controls  (F6 or Esc closes; the game gets no input while this is open)", nullptr,
                 ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoCollapse | ImGuiWindowFlags_NoSavedSettings);
    rs64_bind_table t = rs64_bind_live_get();
    const int cap = rs64_bind_capture_target();
    if (cap != 0)
        ImGui::TextColored(ImVec4(1, 0.85f, 0.2f, 1), "%s %s: press a pad button, pull a trigger / push a stick, or press a key  (Esc cancels)",
                           rs64_bind_capture_add() ? "ADD to" : "BIND", tgt_label(cap));
    else
        ImGui::TextWrapped("Bind = replace that button's inputs with the next one you press.  Add = keep them and add one.  Save writes controls.json.");
    // s7942: wrapped (TextDisabled does not wrap; at 640x480 it cut off "Circle/B = close").
    ImGui::PushStyleColor(ImGuiCol_Text, ImGui::GetStyleColorVec4(ImGuiCol_TextDisabled));
    ImGui::TextWrapped("Pad: D-pad up/down picks a row, Cross/A = Bind, Square/X = Add, Triangle/Y = Save, L1 = Clear row, hold R3 1 s = Reset to defaults, Circle/B = close.  Open: touchpad click or Share/Back+Start.");
    ImGui::PopStyleColor();
    ImGui::Separator();
    const int* targets = k_targets;
    const int prow = g_pad_row.load();
    static int s_prow_drawn = -1;
    const bool prow_moved = prow != s_prow_drawn;
    if (prow_moved) { s_prow_drawn = prow; fprintf(stderr, "[controls-panel] pad row=%d target=%s (drawn)\n", prow, tgt_label(k_targets[prow])); }
    if (ImGui::BeginTable("binds", 3, ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersInnerH | ImGuiTableFlags_ScrollY,
                          ImVec2(0, -ImGui::GetFrameHeightWithSpacing() * 3.2f))) {
        ImGui::TableSetupColumn("N64", ImGuiTableColumnFlags_WidthFixed, ImGui::CalcTextSize("> Stick right (keys)").x);
        ImGui::TableSetupColumn("Inputs", ImGuiTableColumnFlags_WidthStretch);
        ImGui::TableSetupColumn("", ImGuiTableColumnFlags_WidthFixed, ImGui::CalcTextSize("Bind  Add  Clear____").x);
        for (int ri = 0; ri < k_nrows; ri++) {
            const int tg = targets[ri];
            ImGui::TableNextRow();
            if (ri == prow) ImGui::TableSetBgColor(ImGuiTableBgTarget_RowBg1, ImGui::GetColorU32(ImVec4(0.25f, 0.45f, 0.85f, 0.55f)));
            ImGui::PushID(tg);
            ImGui::TableNextColumn();
            if (ri == prow && prow_moved) ImGui::SetScrollHereY(0.5f);
            const char* mark = ri == prow ? "> " : "  ";
            if (tg < 0) ImGui::Text("%s%s (keys)", mark, tgt_label(tg)); else ImGui::Text("%s%s", mark, tgt_label(tg));
            if (ri == prow && s_rects) {  // s7942: cursor row rect + the table's scroll clip (y) + visibility, for a pixel witness
                note_rect("prow");
                const ImVec2 wp = ImGui::GetWindowPos(), ws = ImGui::GetWindowSize();
                char buf[96]; snprintf(buf, sizeof buf, " prow_i=%d clip=%.0f,%.0f vis=%d", ri, wp.y, wp.y + ws.y, ImGui::IsItemVisible() ? 1 : 0);
                rect_now += buf;
            }
            ImGui::TableNextColumn();
            if (cap == tg) ImGui::TextColored(ImVec4(1, 0.85f, 0.2f, 1), "...waiting...  %s", sources_of(t, tg).c_str());
            else ImGui::TextWrapped("%s", sources_of(t, tg).c_str());
            ImGui::TableNextColumn();
            if (ImGui::SmallButton("Bind")) rs64_bind_capture_arm(tg, false);
            if (tg == RS64_N64_A) note_rect("bindA");
            ImGui::SameLine();
            if (ImGui::SmallButton("Add")) rs64_bind_capture_arm(tg, true);
            ImGui::SameLine();
            if (ImGui::SmallButton("Clear")) { rs64_bind_clear(&t, tg); rs64_bind_live_set(t, "panel clear"); }
            ImGui::PopID();
        }
        ImGui::EndTable();
    }
    ImGui::Separator();
    if (ImGui::Button("Reset to defaults")) { rs64_bind_capture_arm(0, false); rs64_bind_live_set(rs64_bind_defaults(), "panel reset"); g_msg = "Defaults restored (not saved yet)."; }
    note_rect("reset");
    ImGui::SameLine();
    if (ImGui::Button("Save")) { std::string m; rs64_bind_save(&m); g_msg = m; }
    note_rect("save");
    ImGui::SameLine();
    if (ImGui::Button("Close")) { rs64_bind_capture_arm(0, false); g_open.store(false); }
    note_rect("close");
    ImGui::SameLine();
    ImGui::TextDisabled("controls.json");
    if (!g_msg.empty()) ImGui::TextWrapped("%s", g_msg.c_str());
    if (s_rects && rect_now != s_rect_last) {
        s_rect_last = rect_now;
        fprintf(stderr, "[panel-rect] disp=%.0fx%.0f%s\n", io.DisplaySize.x, io.DisplaySize.y, rect_now.c_str());
    }
    ImGui::End();
}

void hook_init(plume::RenderInterface*, plume::RenderDevice* device) {
    std::lock_guard<std::mutex> lk(g_mu);
    auto* md = static_cast<plume::MetalDevice*>(device);
    IMGUI_CHECKVERSION();
    ImGuiContext* prev = ImGui::GetCurrentContext();
    g_ctx = ImGui::CreateContext();
    ImGui::SetCurrentContext(g_ctx);
    ImGuiIO& io = ImGui::GetIO();
    io.IniFilename = nullptr;
    io.LogFilename = nullptr;
    io.BackendFlags |= ImGuiBackendFlags_RendererHasVtxOffset;
    ImGui::StyleColorsDark();
    g_metal_ok = md && md->mtl && rs64_imgui_metal_init((void*)md->mtl);
    fprintf(stderr, "[controls-panel] init metal=%d\n", g_metal_ok ? 1 : 0);
    ImGui::SetCurrentContext(prev);
}

void hook_draw(plume::RenderCommandList* list, plume::RenderFramebuffer* fb) {
    if (!g_open.load(std::memory_order_acquire)) return;
    std::lock_guard<std::mutex> lk(g_mu);
    if (!g_ctx || !g_metal_ok || !list || !fb) return;
    auto* cl = static_cast<plume::MetalCommandList*>(list);
    auto* mfb = static_cast<plume::MetalFramebuffer*>(fb);
    if (mfb->colorAttachments.empty()) return;
    ImGuiContext* prev = ImGui::GetCurrentContext();
    ImGui::SetCurrentContext(g_ctx);
    ImGuiIO& io = ImGui::GetIO();
    const float fw = (float)mfb->width, fh = (float)mfb->height;
    // s7639 class ST: this hook runs on RT64's present thread, and SDL3 documents SDL_GetWindowFromID / SDL_GetWindowSize
    // as main-thread-only. update_gfx (main thread) publishes the size via rs64_panel_note_window(); ROGUESQ_S7639_ST=0
    // restores the old direct calls, =chk computes both and logs disagreements (and this thread's main-ness) once a second.
    static const int st_mode = [] { const char* v = getenv("ROGUESQ_S7639_ST"); return !v || !*v ? 1 : !strncmp(v, "chk", 3) ? 2 : v[0] == '0' ? 0 : 1; }();
    static const int st_plant = [] { const char* v = getenv("ROGUESQ_S7639_ST"); return v && !strcmp(v, "chkp") ? 1 : 0; }();  // control
    int ww = 0, wh = 0;
    auto old_size = [&](int& a, int& b) {
        if (SDL_Window* w = g_window_id.load() ? SDL_GetWindowFromID(g_window_id.load()) : nullptr) SDL_GetWindowSize(w, &a, &b);
    };
    if (st_mode == 0) old_size(ww, wh);
    else {
        const uint64_t v = g_win_size.load(std::memory_order_acquire);
        ww = (int)(uint32_t)(v >> 32) + st_plant; wh = (int)(uint32_t)v;
        if (st_mode == 2) {
            // Check arm: the self-test opens the panel with no F6/mouse event, so g_window_id may still be 0; use the
            // window's real ID (published with the size) so the old SDL path actually runs, then compare after fallback.
            if (!g_window_id.load()) g_window_id.store(g_win_id.load());
            int ow = 0, oh = 0; old_size(ow, oh);
            if (ow <= 0 || oh <= 0) { ow = (int)fw; oh = (int)fh; }
            if (ww <= 0 || wh <= 0) { ww = (int)fw; wh = (int)fh; }
            static long n = 0, bad = 0; static auto t0 = std::chrono::steady_clock::now();
            n++; if (ow != ww || oh != wh) bad++;
            const auto t = std::chrono::steady_clock::now();
            if (t - t0 >= std::chrono::seconds(1)) {
                t0 = t;
                fprintf(stderr, "[s7639-st] chk n=%ld bad=%ld cached=%dx%d sdl=%dx%d draw_main=%d\n", n, bad, ww, wh, ow, oh, pthread_main_np());
            }
        }
    }
    if (ww <= 0 || wh <= 0) { ww = (int)fw; wh = (int)fh; }
    // s7668: across a fullscreen toggle the drawable resizes ~33 draws before update_gfx republishes the window size, and
    // fb/win then differ in aspect, so DisplayFramebufferScale squashed the panel for ~0.5 s. A HiDPI fb is an exact multiple
    // of the window (same aspect); a different aspect means the cached size is stale: draw at fb size until it catches up.
    // ROGUESQ_S7668_ASPECT=0 restores the old behaviour.
    static const bool s7668 = [] { const char* v = getenv("ROGUESQ_S7668_ASPECT"); return !(v && *v == '0'); }();
    if (s7668 && std::fabs((double)fw * wh - (double)fh * ww) > 0.01 * (double)fw * wh) {
        static long stale = 0;
        if (++stale == 1 || stale % 60 == 0) fprintf(stderr, "[controls-panel] stale window size %dx%d vs fb %.0fx%.0f (n=%ld): using fb\n", ww, wh, fw, fh, stale);
        ww = (int)fw; wh = (int)fh;
    }
    io.DisplaySize = ImVec2((float)ww, (float)wh);
    io.DisplayFramebufferScale = ImVec2(fw / (float)ww, fh / (float)wh);
    io.FontGlobalScale = std::min(3.0f, std::max(1.0f, (float)wh / 540.0f));
    static auto last = std::chrono::steady_clock::now();
    const auto now = std::chrono::steady_clock::now();
    io.DeltaTime = std::max(1e-4f, std::chrono::duration<float>(now - last).count());
    last = now;
    rs64_imgui_metal_new_frame((void*)mfb->colorAttachments[0].getTexture());
    ImGui::NewFrame();
    draw_ui();
    ImGui::Render();
    ImDrawData* dd = ImGui::GetDrawData();
    cl->setFramebuffer(fb);
    cl->checkActiveRenderEncoder();
    rs64_imgui_metal_render(dd, (void*)cl->mtl, (void*)cl->activeRenderEncoder);
    cl->endActiveRenderEncoder();
    static float s_lfw = 0, s_lfh = 0; static int s_lww = 0, s_lwh = 0;  // s7668: log every size change while open
    const bool resized = fw != s_lfw || fh != s_lfh || ww != s_lww || wh != s_lwh;
    s_lfw = fw; s_lfh = fh; s_lww = ww; s_lwh = wh;
    if (++g_draws == 1 || g_draws % 600 == 0 || resized)
        fprintf(stderr, "[controls-panel] draw n=%ld fb=%.0fx%.0f win=%dx%d lists=%d vtx=%d\n", g_draws, fw, fh, ww, wh,
                dd ? dd->CmdListsCount : -1, dd ? dd->TotalVtxCount : -1);
    ImGui::SetCurrentContext(prev);
}

void hook_deinit() {
    std::lock_guard<std::mutex> lk(g_mu);
    if (!g_ctx) return;
    ImGuiContext* prev = ImGui::GetCurrentContext();
    ImGui::SetCurrentContext(g_ctx);
    if (g_metal_ok) rs64_imgui_metal_shutdown();
    ImGui::DestroyContext(g_ctx);
    g_ctx = nullptr; g_metal_ok = false;
    ImGui::SetCurrentContext(prev == g_ctx ? nullptr : prev);
}
}  // namespace

void rs64_panel_install_hooks() {
    const char* e = getenv("ROGUESQ_CONTROLS_PANEL");
    if (e && *e == '0') { fprintf(stderr, "[controls-panel] disabled (ROGUESQ_CONTROLS_PANEL=0)\n"); return; }
    RT64::SetRenderHooks(hook_init, hook_draw, hook_deinit);
}

void rs64_panel_note_window(int w, int h, uint32_t id) {
    g_win_id.store(id, std::memory_order_relaxed);
    g_win_size.store(((uint64_t)(uint32_t)w << 32) | (uint32_t)h, std::memory_order_release);
}

bool rs64_panel_is_open() { return g_open.load(std::memory_order_acquire); }

void rs64_panel_set_open(bool open) {
    if (!open) rs64_bind_capture_arm(0, false);
    if (g_open.exchange(open) != open) fprintf(stderr, "[controls-panel] %s\n", open ? "open" : "closed");
}

void rs64_panel_feed(const SDL_Event& e) {
    if (e.type == SDL_KEYDOWN && !e.key.repeat) {
        if (e.key.keysym.sym == SDLK_F6) { g_window_id.store(e.key.windowID); rs64_panel_set_open(!rs64_panel_is_open()); return; }
        // Esc: the capture logic in main.cpp cancels a pending capture itself; with none pending it closes the panel.
        if (e.key.keysym.sym == SDLK_ESCAPE && rs64_panel_is_open() && rs64_bind_capture_target() == 0) { rs64_panel_set_open(false); return; }
    }
    if (!rs64_panel_is_open()) return;
    // Keys are NOT fed to ImGui: a key pressed to bind must not also activate a focused widget. Mouse only.
    std::lock_guard<std::mutex> lk(g_mu);
    if (!g_ctx) return;
    ImGuiContext* prev = ImGui::GetCurrentContext();
    ImGui::SetCurrentContext(g_ctx);
    ImGuiIO& io = ImGui::GetIO();
    switch (e.type) {
    case SDL_MOUSEMOTION: g_window_id.store(e.motion.windowID); io.AddMousePosEvent((float)e.motion.x, (float)e.motion.y); break;
    case SDL_MOUSEBUTTONDOWN:
    case SDL_MOUSEBUTTONUP: {
        const int b = e.button.button == SDL_BUTTON_LEFT ? 0 : e.button.button == SDL_BUTTON_RIGHT ? 1 : e.button.button == SDL_BUTTON_MIDDLE ? 2 : -1;
        g_window_id.store(e.button.windowID);
        io.AddMousePosEvent((float)e.button.x, (float)e.button.y);
        if (b >= 0) io.AddMouseButtonEvent(b, e.type == SDL_MOUSEBUTTONDOWN);
        break;
    }
    case SDL_MOUSEWHEEL: io.AddMouseWheelEvent((float)e.wheel.x, (float)e.wheel.y); break;
    case SDL_WINDOWEVENT:
        if (e.window.event == SDL_WINDOWEVENT_FOCUS_LOST) io.AddFocusEvent(false);
        else if (e.window.event == SDL_WINDOWEVENT_FOCUS_GAINED) io.AddFocusEvent(true);
        break;
    default: break;
    }
    ImGui::SetCurrentContext(prev);
}

// Test hook (ROGUESQ_BIND_PANEL_TEST): press the panel's buttons by name from the input thread, through the same
// actions the widgets call.
void rs64_panel_test_action(const char* what) {
    if (!strcmp(what, "reset")) { rs64_bind_capture_arm(0, false); rs64_bind_live_set(rs64_bind_defaults(), "panel reset"); }
    else if (!strcmp(what, "save")) { std::string m; rs64_bind_save(&m); std::lock_guard<std::mutex> lk(g_mu); g_msg = m; }
}

// s7941 pad navigation (cursor state; the input logic lives in main.cpp rs64_panel_pad_step).
int rs64_panel_row_count() { return k_nrows; }
int rs64_panel_pad_row() { return g_pad_row.load(); }
int rs64_panel_row_target(int row) { return row >= 0 && row < k_nrows ? k_targets[row] : 0; }
void rs64_panel_pad_move(int d) { g_pad_row.store((g_pad_row.load() + d + k_nrows) % k_nrows); }
void rs64_panel_set_msg(const std::string& m) { std::lock_guard<std::mutex> lk(g_mu); g_msg = m; }
