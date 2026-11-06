// s6906 G5f: transient straight line detector over presented frames (g5b_capture raw: u64 mach, u32 w, u32 h, w*h*3 bytes).
// A pixel is a candidate when frame i differs from both neighbours by > T while the neighbours agree with each other
// within T/2, which rejects moving edges (they leave prev != next). Candidates feed a Hough transform; a peak is a line
// when it holds >= minRun pixels along a gap-tolerant run and most candidates in a band around it sit within +-2 px.
// Control: inject=N draws a synthetic 1 px line, alpha 0.6, random position, into every Nth frame IN MEMORY only and
// reports how many came back.
// usage: g5f_lines <raw> <out.txt> [T=40] [minRun=70] [inject=0]
// out.txt: idx mach x0 y0 x1 y1 run thin_frac r g b block injected
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <vector>
#include <algorithm>
struct Hdr { uint64_t t; uint32_t w, h; };
struct L { double x0, y0, x1, y1; int run; double frac; int r, g, b; };
static int W, H;
static const int NT = 180;
static std::vector<L> detect(const uint8_t *p, const uint8_t *c, const uint8_t *n, int T, int minRun) {
    std::vector<int> xs, ys; std::vector<uint8_t> mask((size_t)W * H, 0);
    for (int y = 1; y < H - 1; y++) for (int x = 1; x < W - 1; x++) { const size_t o = ((size_t)y * W + x) * 3; int dp = 0, dn = 0, pn = 0;
        for (int k = 0; k < 3; k++) { dp = std::max(dp, abs(c[o + k] - p[o + k])); dn = std::max(dn, abs(c[o + k] - n[o + k])); pn = std::max(pn, abs(p[o + k] - n[o + k])); }
        if (dp > T && dn > T && pn < T / 2) { mask[(size_t)y * W + x] = 1; xs.push_back(x); ys.push_back(y); } }
    std::vector<L> out; if (xs.size() < (size_t)minRun / 2 || xs.size() > 40000) return out;
    static std::vector<float> cs(NT), sn(NT); static bool init = false; if (!init) { init = true; for (int i = 0; i < NT; i++) { cs[i] = cosf(i * M_PI / NT); sn[i] = sinf(i * M_PI / NT); } }
    const int D = (int)hypot(W, H) + 2; std::vector<int> acc((size_t)NT * 2 * D);
    for (int round = 0; round < 3; round++) {
        std::fill(acc.begin(), acc.end(), 0);
        for (size_t i = 0; i < xs.size(); i++) { if (!mask[(size_t)ys[i] * W + xs[i]]) continue; for (int t = 0; t < NT; t++) acc[(size_t)t * 2 * D + (int)lrintf(xs[i] * cs[t] + ys[i] * sn[t]) + D]++; }
        int bt = 0, br = 0, bv = 0; for (int t = 0; t < NT; t++) for (int r = 0; r < 2 * D; r++) if (acc[(size_t)t * 2 * D + r] > bv) { bv = acc[(size_t)t * 2 * D + r]; bt = t; br = r; }
        if (bv < minRun / 2) break;
        const double rho = br - D, cx = cs[bt], sy = sn[bt];
        std::vector<std::pair<double, size_t>> on; long band = 0;
        for (size_t i = 0; i < xs.size(); i++) { if (!mask[(size_t)ys[i] * W + xs[i]]) continue; const double d = fabs(xs[i] * cx + ys[i] * sy - rho); const double s = -xs[i] * sy + ys[i] * cx;
            if (d <= 2.0) on.push_back({s, i}); else if (d <= 10.0) band++; }
        std::sort(on.begin(), on.end());
        size_t bi = 0, bj = 0, i0 = 0; for (size_t i = 1; i <= on.size(); i++) if (i == on.size() || on[i].first - on[i - 1].first > 6.0) { if (on.empty()) break; if (on[i - 1].first - on[i0].first > on[bj].first - on[bi].first) { bi = i0; bj = i - 1; } i0 = i; }
        const int run = on.empty() ? 0 : (int)(on[bj].first - on[bi].first);
        const size_t cnt = bj >= bi && !on.empty() ? bj - bi + 1 : 0;
        const double frac = (double)on.size() / (double)(on.size() + band + 1);
        if (run >= minRun && cnt >= (size_t)run / 2 && frac > 0.6) {
            long r = 0, g = 0, b = 0; for (size_t q = bi; q <= bj; q++) { const size_t i = on[q].second, o = ((size_t)ys[i] * W + xs[i]) * 3; r += c[o]; g += c[o + 1]; b += c[o + 2]; }
            const size_t a = on[bi].second, e = on[bj].second; out.push_back({(double)xs[a], (double)ys[a], (double)xs[e], (double)ys[e], run, frac, (int)(r / cnt), (int)(g / cnt), (int)(b / cnt)});
        }
        for (auto &q : on) mask[(size_t)ys[q.second] * W + xs[q.second]] = 0;
    }
    return out;
}
int main(int ac, char **av) {
    if (ac < 3) return 2;
    FILE *f = fopen(av[1], "rb"); if (!f) return 1; FILE *o = fopen(av[2], "w"); if (!o) return 1;
    const int T = ac > 3 ? atoi(av[3]) : 40, minRun = ac > 4 ? atoi(av[4]) : 70, inj = ac > 5 ? atoi(av[5]) : 0;
    Hdr h; if (fread(&h, 16, 1, f) != 1) return 1; W = h.w; H = h.h; fseeko(f, 0, SEEK_SET); const size_t fs = (size_t)W * H * 3;
    std::vector<uint8_t> b[3]; for (auto &v : b) v.resize(fs); uint64_t ts[3] = {0, 0, 0}; long idx = 0, found = 0, injn = 0, injhit = 0, blk[2] = {0, 0}, frames[2] = {0, 0};
    double ix0 = 0, iy0 = 0, ix1 = 0, iy1 = 0; srand(6906);
    auto rd = [&](int s) { Hdr q; if (fread(&q, 16, 1, f) != 1 || fread(b[s].data(), 1, fs, f) != fs) return false; ts[s] = q.t; return true; };
    if (!rd(0) || !rd(1)) return 1;
    int P = 0, C = 1, N = 2;
    for (idx = 1; rd(N); idx++) {
        bool did = false;
        if (inj && idx % inj == 0) { did = true; injn++; ix0 = 40 + rand() % (W - 80); iy0 = 40 + rand() % (H - 80); const double a = (rand() % 360) / 57.3, len = 90 + rand() % 200;
            ix1 = std::min(W - 3.0, std::max(2.0, ix0 + cos(a) * len)); iy1 = std::min(H - 3.0, std::max(2.0, iy0 + sin(a) * len));
            const int st = (int)hypot(ix1 - ix0, iy1 - iy0) + 1; for (int i = 0; i <= st; i++) { const int x = (int)lrint(ix0 + (ix1 - ix0) * i / st), y = (int)lrint(iy0 + (iy1 - iy0) * i / st); uint8_t *q = &b[C][((size_t)y * W + x) * 3]; for (int k = 0; k < 3; k++) q[k] = (uint8_t)(q[k] * 0.4 + 255 * 0.6); } }
        const int bl = (ts[C] / 24000000ull) & 1; frames[bl]++;
        for (auto &l : detect(b[P].data(), b[C].data(), b[N].data(), T, minRun)) {
            bool hit = false; if (did) { const double dx = ix1 - ix0, dy = iy1 - iy0, dn = hypot(dx, dy); const double d0 = fabs((l.x0 - ix0) * dy - (l.y0 - iy0) * dx) / dn, d1 = fabs((l.x1 - ix0) * dy - (l.y1 - iy0) * dx) / dn; hit = d0 < 4 && d1 < 4; if (hit) injhit++; }
            if (!hit) { found++; blk[bl]++; }
            fprintf(o, "%ld %llu %.0f %.0f %.0f %.0f %d %.2f %d %d %d %d %d\n", idx, (unsigned long long)ts[C], l.x0, l.y0, l.x1, l.y1, l.run, l.frac, l.r, l.g, l.b, bl, (int)hit);
        }
        const int t = P; P = C; C = N; N = t;
    }
    printf("frames %ld (cull-off %ld, on %ld) %dx%d lines %ld (off %ld, on %ld) injected %ld recovered %ld\n", idx, frames[0], frames[1], W, H, found, blk[0], blk[1], injn, injhit);
}
