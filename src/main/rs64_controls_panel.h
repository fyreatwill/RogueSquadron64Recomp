// s7620 G6b step 3: F6 Controls panel. The live binding table, capture and save live in main.cpp (they own the
// controller and the paths); the ImGui panel + RT64 present hook live in rs64_controls_panel.cpp; the Metal ImGui
// backend bridge lives in rs64_imgui_metal.mm.
#pragma once
#include <cstdint>
#include <string>
#include "rs64_bindings.h"
union SDL_Event;

// Targets: an N64 button mask (RS64_N64_*), or one of the keyboard stick directions below.
enum : int { RS64_TGT_UP = -1, RS64_TGT_DOWN = -2, RS64_TGT_LEFT = -3, RS64_TGT_RIGHT = -4 };

// ---- main.cpp ----
rs64_bind_table rs64_bind_live_get();
void rs64_bind_live_set(const rs64_bind_table& t, const char* why);
// Bind target to src: add=false replaces the target's list, add=true appends. Stick directions take keys only.
bool rs64_bind_apply(rs64_bind_table* t, int target, const rs64_bind_source& src, bool add);
void rs64_bind_clear(rs64_bind_table* t, int target);
// Capture the next NEW pad button / axis past 16000 / key for target (0 = cancel). State: 0 idle, 1 waiting.
void rs64_bind_capture_arm(int target, bool add);
int rs64_bind_capture_target();
bool rs64_bind_capture_add();
std::string rs64_bind_capture_last();   // name of the last captured source ("" if none / cancelled)
bool rs64_bind_save(std::string* msg);  // writes controls.json unless ROGUESQ_NO_SAVE_WRITE
std::string rs64_bind_path();

// ---- rs64_controls_panel.cpp ----
void rs64_panel_install_hooks();        // before RT64 Application::setup
bool rs64_panel_is_open();
void rs64_panel_set_open(bool open);
void rs64_panel_note_window(int w, int h, uint32_t id);  // s7639: MAIN thread only (update_gfx); the draw hook reads it
void rs64_panel_feed(const SDL_Event& e);  // input poll thread; F6 toggles, mouse/keys go to ImGui while open
// s7941 pad navigation: row cursor (wraps), target per row (RS64_N64_* or RS64_TGT_*), status line.
int rs64_panel_row_count();
int rs64_panel_pad_row();
int rs64_panel_row_target(int row);
void rs64_panel_pad_move(int d);
void rs64_panel_set_msg(const std::string& m);
