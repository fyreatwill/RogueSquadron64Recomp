// s7618 G6b: offline proof that rs64_bind_defaults() reproduces the pre-s7618 get_n64_input mapping bit for bit.
// s7619 step 2: also proves controls.json parsing (rs64_bindings_json.h): empty/defaults-dump files == defaults over the
// whole sweep, a remap moves exactly the intended bit (positive control), malformed files fall back to defaults.
// Build+run: c++ -std=c++17 -I src/main -I lib/rt64/src/contrib -I /opt/homebrew/include tools/test_bindings.cpp \
//            -L/opt/homebrew/lib -lSDL2 -o /tmp/tb && /tmp/tb
// /tmp/tb mutant  -> plants one swapped table entry and must report mismatches (exit 0 only if it does).
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <random>
#include "rs64_bindings_json.h"
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
static long sweep(const rs64_bind_table& t) {
    const long f0 = fails;
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
    return fails - f0;
}
static int bad = 0;
static void expect(bool ok, const char* what) { std::printf("%s %s\n", ok ? "ok  " : "FAIL", what); if (!ok) bad++; }
static uint16_t press(const rs64_bind_table& t, int padbtn, int key) {
    static uint8_t keys[SDL_NUM_SCANCODES]; std::memset(keys, 0, sizeof keys);
    rs64_input_snapshot s; s.have_pad = true; s.keys = keys; s.nkeys = SDL_NUM_SCANCODES;
    if (padbtn >= 0) s.pad_btn[padbtn] = true;
    if (key >= 0) keys[key] = 1;
    uint16_t b; float x, y; rs64_bind_eval(t, s, &b, &x, &y); return b;
}
int main(int argc, char** argv) {
    const bool mutant = argc > 1 && !std::strcmp(argv[1], "mutant");
    rs64_bind_table t = rs64_bind_defaults();
    if (mutant) { std::swap(t.buttons[0].n64_mask, t.buttons[1].n64_mask); } // A<->X on the pad
    long m = sweep(t);
    std::printf("%s cases=%ld mismatches=%ld\n", mutant ? "MUTANT" : "DEFAULTS", cases, m);
    if (mutant) return m > 0 ? 0 : 1;
    if (m) return 1;
    // (a) files that must equal the defaults: empty object, version only, the full defaults dump, empty sections
    const std::string dump = rs64_bind_to_json(rs64_bind_defaults());
    const char* same[] = {"{}", "{\"version\":1}", "{\"buttons\":{},\"stick\":{}}", dump.c_str()};
    for (const char* f : same) {
        rs64_bind_table p; std::string err; const bool ok = rs64_bind_parse_json(f, &p, &err);
        const long mm = sweep(p);
        std::printf("same-file parse=%d mismatches=%ld err='%s' (%.40s)\n", ok, mm, err.c_str(), f);
        expect(ok && mm == 0, "defaults-equivalent file == legacy over the whole sweep");
    }
    { rs64_bind_table p; std::string err; rs64_bind_parse_json(dump, &p, &err);
      expect(rs64_bind_to_json(p) == dump, "defaults dump round-trips text-identical"); }
    // (b) positive control: A -> pad:b only. Pad A now gives nothing, pad B gives A|CD, key Z no longer gives A.
    {
        rs64_bind_table p; std::string err;
        const bool ok = rs64_bind_parse_json("{\"buttons\":{\"a\":[\"pad:b\"]}}", &p, &err);
        const long mm = sweep(p);
        std::printf("remap A->pad:b parse=%d err='%s' sweep_mismatches=%ld\n", ok, err.c_str(), mm);
        expect(ok && mm > 0, "remap file differs from legacy (instrument sees it)");
        expect(press(p, SDL_CONTROLLER_BUTTON_A, -1) == 0, "pad A unbound");
        expect(press(p, SDL_CONTROLLER_BUTTON_B, -1) == (RS64_N64_A | RS64_N64_CD), "pad B -> A|CD");
        expect(press(p, -1, SDL_SCANCODE_Z) == 0, "key Z no longer A (list replaced)");
        expect(press(p, SDL_CONTROLLER_BUTTON_X, -1) == RS64_N64_B, "unlisted B keeps pad X");
        rs64_bind_table q; rs64_bind_parse_json("{\"buttons\":{\"Z\":[\"axis-:righty:1000\",\"key:Space\"]},\"stick\":{\"invert_y\":false,\"up\":[\"key:Up\"]}}", &q, &err);
        expect(press(q, -1, SDL_SCANCODE_SPACE) == RS64_N64_Z && press(q, -1, SDL_SCANCODE_C) == 0, "Z -> Space, C unbound");
        expect(q.key_up.size() == 1 && q.key_up[0] == SDL_SCANCODE_UP && !q.stick_invert_y && q.key_down == p.key_down, "stick fields parsed");
    }
    // (c) malformed / invalid files: rejected, table == defaults
    const char* badf[] = {"", "{", "[]", "{\"version\":2}", "{\"buttons\":{\"Q\":[\"pad:a\"]}}",
        "{\"buttons\":{\"A\":[\"pad:nosuch\"]}}", "{\"buttons\":{\"A\":\"pad:a\"}}", "{\"buttons\":{\"A\":[\"axis+:lefttrigger:99999\"]}}",
        "{\"buttons\":{\"A\":[\"key:NoSuchKey\"]}}", "{\"stick\":{\"up\":[\"pad:a\"]}}", "{\"extra\":1}",
        "{\"buttons\":{\"A\":[\"pad:b\"],\"B\":[\"wat\"]}}"};
    for (const char* f : badf) {
        rs64_bind_table p; std::string err; const bool ok = rs64_bind_parse_json(f, &p, &err);
        const long mm = sweep(p);
        std::printf("bad-file parse=%d mismatches=%ld err='%s' (%s)\n", ok, mm, err.c_str(), f);
        expect(!ok && mm == 0 && !err.empty(), "malformed file rejected, defaults kept");
    }
    std::printf("TOTAL cases=%ld checks_failed=%d\n", cases, bad);
    return bad ? 1 : 0;
}
