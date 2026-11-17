// s7513 class FJ: host analog stick -> OEM N64 controller gate.
//
// The game reads the pad stick as s8 counts and scales it to its own range: tickControllerInput (0x800BF0D0) divides
// x by 75.0f (ROM 0x800A622C) and y by 80.0f (0x800A6230) and clamps to [-1, 1] (0x800A6220/24, dead zone 0.015 at
// 0x800A6228); getControllerStick{X,Y}Percentage (0x8007A068/A8) multiply by 1/128 unclamped. Those constants fit a
// real pad, whose stick gate is an octagon reaching about 85 counts at the cardinals and (70, 70) at the diagonals.
// ultramodern sends (int8_t)(127 * x), so a full host stick reached 127 counts: full turn at 59% (x) / 63% (y) of host
// travel, ~1.6x retail sensitivity, and the unclamped percentage readers saw ~1.5x their retail maximum.
//
// rs64_stick_gate maps the host vector (unit disk; keyboard diagonals arrive as 0.7071) onto that octagon: the
// direction is kept, |v| (clamped to 1) scales the octagon boundary radius in that direction, and the result is
// rounded to whole counts and returned pre-divided by 127 (+ a quarter-count bias away from zero) so that
// ultramodern's truncating (int8_t)(127 * x) yields exactly the rounded count.
// ROGUESQ_STICK_GATE: unset or 1 = on (85,70); 0 = old raw 127 scale; "C,D" = custom cardinal / diagonal counts.
#pragma once
#include <cmath>
#include <cstdio>

struct rs64_stick_gate_cfg { bool on; float card; float diag; };

// Integer counts the guest will receive for host vector (x, y) under the gate.
inline void rs64_stick_gate_counts(const rs64_stick_gate_cfg& g, float x, float y, int* cx, int* cy) {
    if (!g.on) { *cx = (int)(127.0f * x); *cy = (int)(127.0f * y); return; }  // old path: ultramodern truncation
    const float r = std::sqrt(x * x + y * y);
    if (!(r > 0.0f)) { *cx = 0; *cy = 0; return; }
    const float m = r > 1.0f ? 1.0f : r;
    // Fold into the first octant (0..45 deg): a = major axis, b = minor axis, unit direction.
    float a = std::fabs(x) / r, b = std::fabs(y) / r;
    const bool swapped = b > a;
    if (swapped) { const float t = a; a = b; b = t; }
    // Octagon edge from P0 = (card, 0) to P1 = (diag, diag); normal n = (diag, card - diag), n.P0 = diag * card.
    const float denom = g.diag * a + (g.card - g.diag) * b;
    const float bound = denom > 0.0f ? (g.diag * g.card) / denom : g.card;
    float ox = m * bound * (std::fabs(x) / r), oy = m * bound * (std::fabs(y) / r);
    int ix = (int)std::lround(ox), iy = (int)std::lround(oy);
    if (ix > 127) ix = 127;
    if (iy > 127) iy = 127;
    *cx = x < 0.0f ? -ix : ix;
    *cy = y < 0.0f ? -iy : iy;
}

// Rewrite (x, y) so that (int8_t)(127 * x) == the gated count.
inline void rs64_stick_gate_apply(const rs64_stick_gate_cfg& g, float* x, float* y) {
    if (!g.on) return;
    int cx, cy;
    rs64_stick_gate_counts(g, *x, *y, &cx, &cy);
    auto enc = [](int c) { return c == 0 ? 0.0f : ((float)c + (c > 0 ? 0.25f : -0.25f)) / 127.0f; };
    *x = enc(cx);
    *y = enc(cy);
}

inline rs64_stick_gate_cfg rs64_stick_gate_parse(const char* e) {
    rs64_stick_gate_cfg g{true, 85.0f, 70.0f};
    if (!e || !e[0] || (e[0] == '1' && e[1] == 0)) return g;
    if (e[0] == '0' && e[1] == 0) { g.on = false; return g; }
    float c = 0, d = 0;
    if (std::sscanf(e, "%f,%f", &c, &d) == 2 && c >= 1.0f && c <= 127.0f && d >= 1.0f && d <= 127.0f) { g.card = c; g.diag = d; }
    return g;
}
