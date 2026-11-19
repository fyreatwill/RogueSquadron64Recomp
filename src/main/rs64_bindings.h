// s7618 G6b step 1: the pad + keyboard -> N64 controller map as a table instead of hard-coded calls in get_n64_input.
// The built-in defaults (rs64_bind_defaults) are EXACTLY the pre-s7618 mapping; rs64_bind_legacy below is a
// transliteration of that old code over the same snapshot, kept so tools/test_bindings.cpp (offline) and
// ROGUESQ_BIND_CHECK=1 (runtime, against the verbatim old SDL-reading code in main.cpp) can prove the two agree.
// Pure: no SDL calls, only SDL's enum headers, so the harness builds without linking SDL.
#pragma once
#include <cstdint>
#include <vector>
#if __has_include(<SDL2/SDL_gamecontroller.h>)
#include <SDL2/SDL_gamecontroller.h>
#include <SDL2/SDL_scancode.h>
#else
#include <SDL_gamecontroller.h>
#include <SDL_scancode.h>
#endif

struct rs64_input_snapshot {
    bool have_pad = false;                              // a controller is open
    bool pad_btn[SDL_CONTROLLER_BUTTON_MAX] = {};
    int16_t pad_axis[SDL_CONTROLLER_AXIS_MAX] = {};
    const uint8_t* keys = nullptr;                      // SDL_GetKeyboardState, indexed by scancode; may be null
    int nkeys = 0;
};

enum rs64_bind_kind : uint8_t {
    RS64_SRC_PAD_BUTTON = 0, // id = SDL_GameControllerButton
    RS64_SRC_AXIS_POS   = 1, // id = SDL_GameControllerAxis, fires when value > threshold
    RS64_SRC_AXIS_NEG   = 2, // fires when value < -threshold
    RS64_SRC_KEY        = 3, // id = SDL_Scancode
};

struct rs64_bind_source { rs64_bind_kind kind; int id; int threshold; };
struct rs64_button_bind { uint16_t n64_mask; rs64_bind_source src; };

struct rs64_bind_table {
    std::vector<rs64_button_bind> buttons;  // OR of every source that fires
    // Analog stick from the pad (value / 32767, y inverted), overridden by the keyboard direction keys when any is held.
    int stick_axis_x = SDL_CONTROLLER_AXIS_LEFTX, stick_axis_y = SDL_CONTROLLER_AXIS_LEFTY;
    bool stick_invert_y = true;
    std::vector<int> key_up, key_down, key_left, key_right;  // scancodes; any held = that direction
};

// N64 masks (libultra PR/controller.h), duplicated here so the header stands alone.
enum : uint16_t {
    RS64_N64_A = 0x8000, RS64_N64_B = 0x4000, RS64_N64_Z = 0x2000, RS64_N64_START = 0x1000,
    RS64_N64_DU = 0x0800, RS64_N64_DD = 0x0400, RS64_N64_DL = 0x0200, RS64_N64_DR = 0x0100,
    RS64_N64_L = 0x0020, RS64_N64_R = 0x0010,
    RS64_N64_CU = 0x0008, RS64_N64_CD = 0x0004, RS64_N64_CL = 0x0002, RS64_N64_CR = 0x0001,
};

inline rs64_bind_table rs64_bind_defaults() {
    rs64_bind_table t;
    auto pb = [&](uint16_t m, SDL_GameControllerButton b) { t.buttons.push_back({m, {RS64_SRC_PAD_BUTTON, (int)b, 0}}); };
    auto ax = [&](uint16_t m, SDL_GameControllerAxis a, int thr) { t.buttons.push_back({m, {RS64_SRC_AXIS_POS, (int)a, thr}}); };
    auto ky = [&](uint16_t m, SDL_Scancode s) { t.buttons.push_back({m, {RS64_SRC_KEY, (int)s, 0}}); };
    pb(RS64_N64_A, SDL_CONTROLLER_BUTTON_A);
    pb(RS64_N64_B, SDL_CONTROLLER_BUTTON_X);
    pb(RS64_N64_START, SDL_CONTROLLER_BUTTON_START);
    pb(RS64_N64_DU, SDL_CONTROLLER_BUTTON_DPAD_UP);
    pb(RS64_N64_DD, SDL_CONTROLLER_BUTTON_DPAD_DOWN);
    pb(RS64_N64_DL, SDL_CONTROLLER_BUTTON_DPAD_LEFT);
    pb(RS64_N64_DR, SDL_CONTROLLER_BUTTON_DPAD_RIGHT);
    pb(RS64_N64_L, SDL_CONTROLLER_BUTTON_LEFTSHOULDER);
    pb(RS64_N64_R, SDL_CONTROLLER_BUTTON_RIGHTSHOULDER);
    pb(RS64_N64_CU, SDL_CONTROLLER_BUTTON_Y);
    pb(RS64_N64_CD, SDL_CONTROLLER_BUTTON_B);
    pb(RS64_N64_CL, SDL_CONTROLLER_BUTTON_BACK);
    pb(RS64_N64_CR, SDL_CONTROLLER_BUTTON_GUIDE);
    pb(RS64_N64_CR, SDL_CONTROLLER_BUTTON_LEFTSTICK);       // owner 2026-11-05: L3 -> C-Right
    ax(RS64_N64_Z, SDL_CONTROLLER_AXIS_TRIGGERLEFT, 16000);  // L2 -> Z (brake)
    ax(RS64_N64_CL, SDL_CONTROLLER_AXIS_TRIGGERRIGHT, 16000); // owner 2026-11-05: R2 -> C-Left (secondary weapon)
    ky(RS64_N64_A, SDL_SCANCODE_Z);
    ky(RS64_N64_B, SDL_SCANCODE_X);
    ky(RS64_N64_Z, SDL_SCANCODE_C);
    ky(RS64_N64_START, SDL_SCANCODE_RETURN);
    ky(RS64_N64_DU, SDL_SCANCODE_UP);
    ky(RS64_N64_DD, SDL_SCANCODE_DOWN);
    ky(RS64_N64_DL, SDL_SCANCODE_LEFT);
    ky(RS64_N64_DR, SDL_SCANCODE_RIGHT);
    ky(RS64_N64_L, SDL_SCANCODE_Q);
    ky(RS64_N64_R, SDL_SCANCODE_E);
    ky(RS64_N64_CU, SDL_SCANCODE_I);
    ky(RS64_N64_CD, SDL_SCANCODE_K);
    ky(RS64_N64_CL, SDL_SCANCODE_J);
    ky(RS64_N64_CR, SDL_SCANCODE_L);
    t.key_up = {SDL_SCANCODE_W}; t.key_down = {SDL_SCANCODE_S};
    t.key_left = {SDL_SCANCODE_A}; t.key_right = {SDL_SCANCODE_D};
    return t;
}

inline bool rs64_snap_key(const rs64_input_snapshot& s, int sc) {
    return s.keys && sc >= 0 && sc < s.nkeys && s.keys[sc];
}

inline bool rs64_bind_fires(const rs64_input_snapshot& s, const rs64_bind_source& src) {
    switch (src.kind) {
    case RS64_SRC_PAD_BUTTON: return s.have_pad && src.id >= 0 && src.id < SDL_CONTROLLER_BUTTON_MAX && s.pad_btn[src.id];
    case RS64_SRC_AXIS_POS:   return s.have_pad && src.id >= 0 && src.id < SDL_CONTROLLER_AXIS_MAX && s.pad_axis[src.id] > src.threshold;
    case RS64_SRC_AXIS_NEG:   return s.have_pad && src.id >= 0 && src.id < SDL_CONTROLLER_AXIS_MAX && s.pad_axis[src.id] < -src.threshold;
    case RS64_SRC_KEY:        return rs64_snap_key(s, src.id);
    }
    return false;
}

inline void rs64_bind_eval(const rs64_bind_table& t, const rs64_input_snapshot& s, uint16_t* btn, float* sx, float* sy) {
    uint16_t b = 0;
    for (const auto& e : t.buttons) if (rs64_bind_fires(s, e.src)) b |= e.n64_mask;
    float x = 0.0f, y = 0.0f;
    if (s.have_pad) {
        auto axv = [&](int a) -> int16_t { return (a >= 0 && a < SDL_CONTROLLER_AXIS_MAX) ? s.pad_axis[a] : 0; };
        x = axv(t.stick_axis_x) / 32767.0f;
        y = axv(t.stick_axis_y) / 32767.0f;
        if (t.stick_invert_y) y = -y;
    }
    auto any = [&](const std::vector<int>& v) { for (int k : v) if (rs64_snap_key(s, k)) return true; return false; };
    const float kx = (any(t.key_right) ? 1.0f : 0.0f) - (any(t.key_left) ? 1.0f : 0.0f);
    const float ky = (any(t.key_up) ? 1.0f : 0.0f) - (any(t.key_down) ? 1.0f : 0.0f);
    if (kx != 0.0f || ky != 0.0f) {
        constexpr float diagonal = 0.70710678f;
        x = kx * (ky != 0.0f ? diagonal : 1.0f);
        y = ky * (kx != 0.0f ? diagonal : 1.0f);
    }
    *btn = b; *sx = x; *sy = y;
}

// Transliteration of the pre-s7618 get_n64_input mapping block over a snapshot (reference for the harness only).
inline void rs64_bind_legacy(const rs64_input_snapshot& s, uint16_t* buttons, float* x, float* y) {
    uint16_t btn = 0; float stick_x = 0.0f, stick_y = 0.0f;
    auto gb = [&](uint16_t m, SDL_GameControllerButton b) { if (s.have_pad && s.pad_btn[b]) btn |= m; };
    gb(RS64_N64_A, SDL_CONTROLLER_BUTTON_A); gb(RS64_N64_B, SDL_CONTROLLER_BUTTON_X);
    gb(RS64_N64_START, SDL_CONTROLLER_BUTTON_START);
    gb(RS64_N64_DU, SDL_CONTROLLER_BUTTON_DPAD_UP); gb(RS64_N64_DD, SDL_CONTROLLER_BUTTON_DPAD_DOWN);
    gb(RS64_N64_DL, SDL_CONTROLLER_BUTTON_DPAD_LEFT); gb(RS64_N64_DR, SDL_CONTROLLER_BUTTON_DPAD_RIGHT);
    gb(RS64_N64_L, SDL_CONTROLLER_BUTTON_LEFTSHOULDER); gb(RS64_N64_R, SDL_CONTROLLER_BUTTON_RIGHTSHOULDER);
    gb(RS64_N64_CU, SDL_CONTROLLER_BUTTON_Y); gb(RS64_N64_CD, SDL_CONTROLLER_BUTTON_B);
    gb(RS64_N64_CL, SDL_CONTROLLER_BUTTON_BACK); gb(RS64_N64_CR, SDL_CONTROLLER_BUTTON_GUIDE);
    gb(RS64_N64_CR, SDL_CONTROLLER_BUTTON_LEFTSTICK);
    if (s.have_pad && s.pad_axis[SDL_CONTROLLER_AXIS_TRIGGERLEFT] > 16000) btn |= RS64_N64_Z;
    if (s.have_pad && s.pad_axis[SDL_CONTROLLER_AXIS_TRIGGERRIGHT] > 16000) btn |= RS64_N64_CL;
    if (s.have_pad) {
        stick_x = s.pad_axis[SDL_CONTROLLER_AXIS_LEFTX] / 32767.0f;
        stick_y = -(s.pad_axis[SDL_CONTROLLER_AXIS_LEFTY] / 32767.0f);
    }
    auto key = [&](SDL_Scancode c) { return rs64_snap_key(s, c); };
    if (key(SDL_SCANCODE_Z)) btn |= RS64_N64_A;      if (key(SDL_SCANCODE_X)) btn |= RS64_N64_B;
    if (key(SDL_SCANCODE_C)) btn |= RS64_N64_Z;      if (key(SDL_SCANCODE_RETURN)) btn |= RS64_N64_START;
    if (key(SDL_SCANCODE_UP)) btn |= RS64_N64_DU;    if (key(SDL_SCANCODE_DOWN)) btn |= RS64_N64_DD;
    if (key(SDL_SCANCODE_LEFT)) btn |= RS64_N64_DL;  if (key(SDL_SCANCODE_RIGHT)) btn |= RS64_N64_DR;
    if (key(SDL_SCANCODE_Q)) btn |= RS64_N64_L;      if (key(SDL_SCANCODE_E)) btn |= RS64_N64_R;
    if (key(SDL_SCANCODE_I)) btn |= RS64_N64_CU;     if (key(SDL_SCANCODE_K)) btn |= RS64_N64_CD;
    if (key(SDL_SCANCODE_J)) btn |= RS64_N64_CL;     if (key(SDL_SCANCODE_L)) btn |= RS64_N64_CR;
    const float kx = (key(SDL_SCANCODE_D) ? 1.0f : 0.0f) - (key(SDL_SCANCODE_A) ? 1.0f : 0.0f);
    const float ky = (key(SDL_SCANCODE_W) ? 1.0f : 0.0f) - (key(SDL_SCANCODE_S) ? 1.0f : 0.0f);
    if (kx != 0.0f || ky != 0.0f) {
        constexpr float diagonal = 0.70710678f;
        stick_x = kx * (ky != 0.0f ? diagonal : 1.0f);
        stick_y = ky * (kx != 0.0f ? diagonal : 1.0f);
    }
    *buttons = btn; *x = stick_x; *y = stick_y;
}
