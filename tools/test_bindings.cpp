// s7618 G6b: offline proof that rs64_bind_defaults() reproduces the pre-s7618 get_n64_input mapping bit for bit.
// Build+run: c++ -std=c++17 -I src/main -I /opt/homebrew/include tools/test_bindings.cpp -o /tmp/tb && /tmp/tb
// /tmp/tb mutant  -> plants one swapped table entry and must report mismatches (exit 0 only if it does).
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <random>
#include "rs64_bindings.h"
static long cases = 0, fails = 0;
static void cmp(const rs64_bind_table& t, const rs64_input_snapshot& s, const char* what) {
    uint16_t b0, b1; float x0, y0, x1, y1;
    rs64_bind_legacy(s, &b0, &x0, &y0);
    rs64_bind_eval(t, s, &b1, &x1, &y1);
    cases++;
    if (b0 != b1 || std::memcmp(&x0, &x1, 4) || std::memcmp(&y0, &y1, 4)) {
        if (fails < 10) std::printf("MISMATCH %s: legacy %04X %g %g table %04X %g %g\n", what, b0, x0, y0, b1, x1, y1);
        fails++;
    }
}
int main(int argc, char** argv) {
    const bool mutant = argc > 1 && !std::strcmp(argv[1], "mutant");
    rs64_bind_table t = rs64_bind_defaults();
    if (mutant) { std::swap(t.buttons[0].n64_mask, t.buttons[1].n64_mask); } // A<->X on the pad
    static uint8_t keys[SDL_NUM_SCANCODES];
    const int16_t axv[] = {-32768, -32767, -16001, -16000, -15999, -1, 0, 1, 15999, 16000, 16001, 16002, 32766, 32767};
    for (int pad = 0; pad < 2; pad++) {
        for (int kb = 0; kb < 2; kb++) {
            rs64_input_snapshot s; s.have_pad = pad; s.keys = kb ? keys : nullptr; s.nkeys = SDL_NUM_SCANCODES;
            std::memset(keys, 0, sizeof keys);
            cmp(t, s, "idle");
            for (int b = 0; b < SDL_CONTROLLER_BUTTON_MAX; b++) { s.pad_btn[b] = true; cmp(t, s, "button"); s.pad_btn[b] = false; }
            for (int a = 0; a < SDL_CONTROLLER_AXIS_MAX; a++) for (int16_t v : axv) { s.pad_axis[a] = v; cmp(t, s, "axis"); s.pad_axis[a] = 0; }
            for (int a = 0; a < SDL_CONTROLLER_AXIS_MAX; a++) for (int b = 0; b < SDL_CONTROLLER_AXIS_MAX; b++)
                for (int16_t v : axv) for (int16_t w : axv) { s.pad_axis[a] = v; s.pad_axis[b] = w; cmp(t, s, "axis pair"); s.pad_axis[a] = s.pad_axis[b] = 0; }
            for (int k = 0; k < SDL_NUM_SCANCODES; k++) { keys[k] = 1; cmp(t, s, "key"); keys[k] = 0; }
            // every pair of the 18 mapped keys (incl. WASD diagonals and opposite pairs) with and without pad stick
            const int mk[] = {SDL_SCANCODE_Z, SDL_SCANCODE_X, SDL_SCANCODE_C, SDL_SCANCODE_RETURN, SDL_SCANCODE_UP, SDL_SCANCODE_DOWN,
                SDL_SCANCODE_LEFT, SDL_SCANCODE_RIGHT, SDL_SCANCODE_Q, SDL_SCANCODE_E, SDL_SCANCODE_I, SDL_SCANCODE_K, SDL_SCANCODE_J,
                SDL_SCANCODE_L, SDL_SCANCODE_W, SDL_SCANCODE_A, SDL_SCANCODE_S, SDL_SCANCODE_D};
            for (int st = 0; st < 2; st++) {
                s.pad_axis[SDL_CONTROLLER_AXIS_LEFTX] = st ? 20000 : 0; s.pad_axis[SDL_CONTROLLER_AXIS_LEFTY] = st ? -32768 : 0;
                for (int i : mk) for (int j : mk) { keys[i] = keys[j] = 1; cmp(t, s, "key pair"); keys[i] = keys[j] = 0; }
                s.pad_axis[SDL_CONTROLLER_AXIS_LEFTX] = s.pad_axis[SDL_CONTROLLER_AXIS_LEFTY] = 0;
            }
        }
    }
    // random combos: any buttons, any axes, a random key subset
    std::mt19937 rng(7618);
    for (int n = 0; n < 200000; n++) {
        rs64_input_snapshot s; s.have_pad = rng() & 1; s.keys = (rng() & 7) ? keys : nullptr; s.nkeys = SDL_NUM_SCANCODES;
        for (int b = 0; b < SDL_CONTROLLER_BUTTON_MAX; b++) s.pad_btn[b] = (rng() % 4) == 0;
        for (int a = 0; a < SDL_CONTROLLER_AXIS_MAX; a++) s.pad_axis[a] = (rng() & 1) ? axv[rng() % 14] : (int16_t)(rng() & 0xFFFF);
        std::memset(keys, 0, sizeof keys);
        for (int k = 0; k < 6; k++) keys[4 + rng() % 80] = 1;   // scancodes 4..83 cover letters, digits, Return, arrows
        cmp(t, s, "random");
    }
    std::printf("%s cases=%ld mismatches=%ld\n", mutant ? "MUTANT" : "DEFAULTS", cases, fails);
    return mutant ? (fails > 0 ? 0 : 1) : (fails == 0 ? 0 : 1);
}
