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
std::string g_msg;              // status line (save result etc.)
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
    ImGui::Separator();
    static const int targets[] = {RS64_N64_A, RS64_N64_B, RS64_N64_Z, RS64_N64_START, RS64_N64_L, RS64_N64_R,
        RS64_N64_CU, RS64_N64_CD, RS64_N64_CL, RS64_N64_CR, RS64_N64_DU, RS64_N64_DD, RS64_N64_DL, RS64_N64_DR,
        RS64_TGT_UP, RS64_TGT_DOWN, RS64_TGT_LEFT, RS64_TGT_RIGHT};
    if (ImGui::BeginTable("binds", 3, ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersInnerH | ImGuiTableFlags_ScrollY,
                          ImVec2(0, -ImGui::GetFrameHeightWithSpacing() * 3.2f))) {
        ImGui::TableSetupColumn("N64", ImGuiTableColumnFlags_WidthFixed, ImGui::CalcTextSize("Stick right (keys)").x);
        ImGui::TableSetupColumn("Inputs", ImGuiTableColumnFlags_WidthStretch);
        ImGui::TableSetupColumn("", ImGuiTableColumnFlags_WidthFixed, ImGui::CalcTextSize("Bind  Add  Clear____").x);
        for (int tg : targets) {
            ImGui::TableNextRow();
            ImGui::PushID(tg);
            ImGui::TableNextColumn();
            if (tg < 0) ImGui::Text("%s (keys)", tgt_label(tg)); else ImGui::TextUnformatted(tgt_label(tg));
            ImGui::TableNextColumn();
            if (cap == tg) ImGui::TextColored(ImVec4(1, 0.85f, 0.2f, 1), "...waiting...  %s", sources_of(t, tg).c_str());
            else ImGui::TextWrapped("%s", sources_of(t, tg).c_str());
            ImGui::TableNextColumn();
            if (ImGui::SmallButton("Bind")) rs64_bind_capture_arm(tg, false);
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
    ImGui::SameLine();
    if (ImGui::Button("Save")) { std::string m; rs64_bind_save(&m); g_msg = m; }
    ImGui::SameLine();
    if (ImGui::Button("Close")) { rs64_bind_capture_arm(0, false); g_open.store(false); }
    ImGui::SameLine();
    ImGui::TextDisabled("controls.json");
    if (!g_msg.empty()) ImGui::TextWrapped("%s", g_msg.c_str());
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
    int ww = 0, wh = 0;
    if (SDL_Window* w = g_window_id.load() ? SDL_GetWindowFromID(g_window_id.load()) : nullptr) SDL_GetWindowSize(w, &ww, &wh);
    if (ww <= 0 || wh <= 0) { ww = (int)fw; wh = (int)fh; }
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
    if (++g_draws == 1 || g_draws % 600 == 0)
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
