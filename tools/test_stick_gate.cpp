// s7513: offline checks for src/main/rs64_stick_gate.h. Build+run: c++ -std=c++17 -I src/main tools/test_stick_gate.cpp -o /tmp/tsg && /tmp/tsg
#include <cstdio>
#include <cstdint>
#include "rs64_stick_gate.h"
static int fails = 0;
static void expect(const char* what, int got, int want) { if (got != want) { std::printf("FAIL %s got %d want %d\n", what, got, want); fails++; } }
// What the guest byte will be: the path through ultramodern's (int8_t)(127 * x).
static int guest(float v) { return (int)(int8_t)(127.0f * v); }
int main() {
    const rs64_stick_gate_cfg on = rs64_stick_gate_parse(nullptr), off = rs64_stick_gate_parse("0");
    struct { float x, y; int ex, ey; const char* n; } cases[] = {
        {1, 0, 85, 0, "right"}, {-1, 0, -85, 0, "left"}, {0, 1, 0, 85, "up"}, {0, -1, 0, -85, "down"},
        {0.70710678f, 0.70710678f, 70, 70, "kbd diag"}, {-0.70710678f, -0.70710678f, -70, -70, "kbd diag neg"},
        {1, 1, 70, 70, "square corner (r>1 clamps)"}, {0.5f, 0, 43, 0, "half right"}, {0, 0, 0, 0, "centre"},
        {-32768.0f / 32767.0f, 0, -85, 0, "SDL min axis"}, {0.01f, 0, 1, 0, "tiny"},
    };
    for (auto& c : cases) {
        float x = c.x, y = c.y;
        rs64_stick_gate_apply(on, &x, &y);
        char b[96];
        std::snprintf(b, sizeof b, "%s x", c.n); expect(b, guest(x), c.ex);
        std::snprintf(b, sizeof b, "%s y", c.n); expect(b, guest(y), c.ey);
    }
    // Monotone along the octant and never outside the gate: sweep angles at full deflection.
    int maxr = 0, minr = 999;
    for (int i = 0; i <= 3600; i++) {
        const float t = i * 3.14159265f / 1800.0f; float x = std::cos(t), y = std::sin(t);
        rs64_stick_gate_apply(on, &x, &y);
        const int gx = guest(x), gy = guest(y);
        const int ax = gx < 0 ? -gx : gx, ay = gy < 0 ? -gy : gy;
        if (ax > 85 || ay > 85) { std::printf("FAIL sweep %d out of gate %d,%d\n", i, gx, gy); fails++; break; }
        const int l1 = ax > ay ? ax : ay; if (l1 > maxr) maxr = l1; if (l1 < minr) minr = l1;
    }
    expect("sweep max axis", maxr, 85);
    expect("sweep min major axis (diag)", minr, 70);
    // Off restores the old scale exactly.
    float x = 1, y = -1; rs64_stick_gate_apply(off, &x, &y); expect("off x", guest(x), 127); expect("off y", guest(y), -127);
    // Mutant control: a gate with the wrong cardinal must fail the "right" case (proves expect() can fire).
    const rs64_stick_gate_cfg bad = rs64_stick_gate_parse("90,70");
    x = 1; y = 0; rs64_stick_gate_apply(bad, &x, &y);
    const int mut = guest(x);
    std::printf("mutant(90,70) right=%d -> %s\n", mut, mut != 85 ? "ctl PASS (detected)" : "ctl FAIL");
    if (mut == 85) fails++;
    // Game-side view (ROM rule): x/75, y/80 clamped to 1.
    float gx = 1, gy = 1; rs64_stick_gate_apply(on, &gx, &gy);
    std::printf("full right: game x = %.3f (old %.3f); host travel to saturate x: gate %.0f%% old %.0f%%\n",
                std::fmin(1.0f, guest(1.0f * 85 / 127 + 0.25f / 127) / 75.0f), std::fmin(1.0f, 127 / 75.0f), 100 * 75 / 85.0, 100 * 75 / 127.0);
    std::printf("%s (%d failures)\n", fails ? "FAILED" : "ALL PASS", fails);
    return fails ? 1 : 0;
}
