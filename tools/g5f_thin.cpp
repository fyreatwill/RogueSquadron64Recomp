// s6906 G5f: census of long thin triangles in a ROGUESQ_G5B_TRIS stream (records are written BEFORE the cull, so every
// triangle is here, and the cull verdict is recomputed with the bound from rs64_spike_scan).
// Thin = visible hull span >= minLen px and hull width (2*area/span) <= maxW px, after clipping to the image rect.
// Transient = no triangle of similar midpoint, angle and span in the previous or next swap. Cull block = same clock as
// ROGUESQ_CULL_SPIKE=tog: (mach/24000000)&1, taken at the swap stamp, so a triangle in a block edge can be mislabelled.
// usage: g5f_thin <tris.bin> <out.txt> [minLen=80] [maxW=4] [height=240]
// out.txt: one line per thin triangle: swap mach op cw timg z span width angle cx cy transient would_cull v0x v0y..v4x v4y
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <vector>
#include <map>
#include <algorithm>
#pragma pack(push,1)
struct R { uint8_t op, pad; uint16_t cw; uint32_t timg, z; int16_t c[10]; };
#pragma pack(pop)
struct T { uint32_t sw; uint64_t t; R r; double span, wid, ang, cx, cy; bool cullb; };
struct P { double x, y; };
static double g_ymax = 0;
static std::vector<P> clip(std::vector<P> p, double x0, double y0, double x1, double y1) {
    auto pass = [&](auto in, auto cut) { std::vector<P> o; for (size_t i = 0; i < p.size(); i++) { P a = p[i], b = p[(i + 1) % p.size()]; bool ia = in(a), ib = in(b);
        if (ia) o.push_back(a); if (ia != ib) o.push_back(cut(a, b)); } p = o; };
    auto cx = [](double X) { return [X](P a, P b) { double t = (X - a.x) / (b.x - a.x); return P{X, a.y + t * (b.y - a.y)}; }; };
    auto cy = [](double Y) { return [Y](P a, P b) { double t = (Y - a.y) / (b.y - a.y); return P{a.x + t * (b.x - a.x), Y}; }; };
    pass([&](P a) { return a.x >= x0; }, cx(x0)); if (p.empty()) return p; pass([&](P a) { return a.x <= x1; }, cx(x1)); if (p.empty()) return p;
    pass([&](P a) { return a.y >= y0; }, cy(y0)); if (p.empty()) return p; pass([&](P a) { return a.y <= y1; }, cy(y1)); return p;
}
int main(int ac, char **av) {
    if (ac < 3) return 2;
    FILE *f = fopen(av[1], "rb"); if (!f) return 1; FILE *o = fopen(av[2], "w"); if (!o) return 1;
    const double minL = ac > 3 ? atof(av[3]) : 80, maxW = ac > 4 ? atof(av[4]) : 4, H = ac > 5 ? atof(av[5]) : 240;
    static char buf[1 << 22]; setvbuf(f, buf, _IOFBF, sizeof buf);
    uint64_t t = 0; uint32_t sw = 0, m; long nsw = 0, n = 0; std::vector<std::vector<T>> win; std::vector<T> cur;
    long on_sw[2] = {0, 0}, thin[2][2] = {{0, 0}, {0, 0}}, cullable[2] = {0, 0}, wtr[2] = {0, 0}, cwc[4] = {0, 0, 0, 0};
    std::map<int, long> byop, bytex;
    auto similar = [](const T &a, const T &b) { double da = fabs(a.ang - b.ang); if (da > 90) da = 180 - da;
        return da < 8 && hypot(a.cx - b.cx, a.cy - b.cy) < 40 && fabs(a.span - b.span) < 0.4 * a.span + 8; };
    auto emit = [&](std::vector<T> *pv, std::vector<T> &c, std::vector<T> *nx) {
        for (auto &a : c) { bool tr = true;
            if (pv) for (auto &b : *pv) if (similar(a, b)) { tr = false; break; }
            if (tr && nx) for (auto &b : *nx) if (similar(a, b)) { tr = false; break; }
            thin[a.cullb][tr]++; byop[a.r.op]++; if (tr) bytex[(int)(a.r.timg >> 8)]++;
            fprintf(o, "%u %llu %02X %u %08X %08X %.1f %.2f %.1f %.1f %.1f %d %d", a.sw, (unsigned long long)a.t, a.r.op, a.r.cw, a.r.timg, a.r.z, a.span, a.wid, a.ang, a.cx, a.cy, (int)tr, (int)a.cullb);
            for (int i = 0; i < 10; i++) fprintf(o, " %.1f", a.r.c[i] / 4.0); fputc('\n', o); } };
    std::vector<T> a0, a1; bool have0 = false, have1 = false;
    auto roll = [&] { if (have1) emit(have0 ? &a0 : nullptr, a1, &cur); a0.swap(a1); have0 = have1; a1 = cur; have1 = true; cur.clear(); };
    while (fread(&m, 4, 1, f) == 1) {
        if (m == 0xF5F5F5F5u) { roll(); nsw++; if (fread(&t, 8, 1, f) != 1 || fread(&sw, 4, 1, f) != 1) break; on_sw[(t / 24000000ull) & 1]++; continue; }
        R r; memcpy(&r, &m, 4); if (fread((char *)&r + 4, sizeof r - 4, 1, f) != 1) break; n++;
        const double W = r.cw ? r.cw : 320; cwc[r.cw <= 320 ? 0 : r.cw <= 640 ? 1 : r.cw <= 800 ? 2 : 3]++;
        std::vector<P> p; for (int i = 0; i < 5; i++) p.push_back({r.c[i * 2] / 4.0, r.c[i * 2 + 1] / 4.0});
        const double xr = 320.0 + 640.0 + (W > 640 ? W - 320.0 : 0.0); bool bad = false;
        for (auto &q : p) if (q.x < -640 || q.x > xr || q.y < -640 || q.y > H + 640) bad = true;
        if (bad) { cullable[(t / 24000000ull) & 1]++; fprintf(stderr, "bad %u %llu %02X %u %d", sw, (unsigned long long)t, r.op, r.cw, (int)((t / 24000000ull) & 1)); for (int i = 0; i < 10; i++) fprintf(stderr, " %.0f", r.c[i] / 4.0); fputc(10, stderr); }
        { static double ymx = 0; for (int i = 0; i < 5; i++) if (r.cw > 640 && !bad && r.c[i * 2 + 1] / 4.0 > ymx && r.c[i * 2 + 1] / 4.0 < 700) { ymx = r.c[i * 2 + 1] / 4.0; g_ymax = ymx; } }
        auto v = clip(p, 0, 0, W, H); if (v.size() < 3) continue;
        double L = 0, a = 0; P e0{}, e1{}; for (size_t i = 0; i < v.size(); i++) for (size_t j = i + 1; j < v.size(); j++) { double d = hypot(v[i].x - v[j].x, v[i].y - v[j].y); if (d > L) { L = d; e0 = v[i]; e1 = v[j]; } }
        if (L < minL) continue;
        for (size_t i = 0; i < v.size(); i++) { size_t j = (i + 1) % v.size(); a += v[i].x * v[j].y - v[j].x * v[i].y; } a = fabs(a) / 2;
        const double wd = 2 * a / L; if (wd > maxW) continue;
        (void)wtr; cur.push_back({sw, t, r, L, wd, fmod(atan2(e1.y - e0.y, e1.x - e0.x) * 57.29578 + 180, 180), (e0.x + e1.x) / 2, (e0.y + e1.y) / 2, (bool)((t / 24000000ull) & 1)});
    }
    roll(); roll();
    printf("swaps %ld (cull-off blocks %ld, on blocks %ld) tris %ld; cw<=320 %ld, 321-640 %ld, 641-800 %ld, >800 %ld\n", nsw, on_sw[0], on_sw[1], n, cwc[0], cwc[1], cwc[2], cwc[3]);
    printf("outside the cull bound: off blocks %ld, on blocks %ld\n", cullable[0], cullable[1]);
    printf("thin visible (min %.0f px, width <= %.1f): off blocks persist %ld transient %ld; on blocks persist %ld transient %ld\n", minL, maxW, thin[0][0], thin[0][1], thin[1][0], thin[1][1]);
    printf("max in-bound y at cw>640: %.1f\n", g_ymax);
    printf("by op:"); for (auto &k : byop) printf(" %02X:%ld", k.first, k.second); printf("\n");
    std::vector<std::pair<long, int>> tx; for (auto &k : bytex) tx.push_back({k.second, k.first}); std::sort(tx.rbegin(), tx.rend());
    printf("transient by timg page:"); for (size_t i = 0; i < tx.size() && i < 8; i++) printf(" %06X00:%ld", tx[i].second, tx[i].first); printf("\n");
}
