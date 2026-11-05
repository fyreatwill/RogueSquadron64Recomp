// s6897 G5b: finds letterboxed cutscene runs in a g5b_capture raw file: dark strips top and bottom, lit middle.
// Per run also prints interior near-black share peak, so scripted-cutscene scenes (the "black steps" scene) can be
// found without sampling. Also bins scene frames by ROGUESQ_G5B_TG_FIX=tog parity (on = odd mach second, 120 ms band set aside).
// usage: g5b_letterbox <raw> [...]
#include <cstdio>
#include <cstdint>
#include <vector>
struct Hdr { uint64_t t; uint32_t w, h; };
static double band(const uint8_t *b, uint32_t w, uint32_t y0, uint32_t y1) { double s = 0; long n = 0; for (uint32_t y = y0; y < y1; y++) for (uint32_t x = 0; x < w; x += 2) { const uint8_t *p = b + (y * w + x) * 3; s += (p[0] + p[1] + p[2]) / 3.0; n++; } return s / n; }
int main(int c, char **v) {
    for (int a = 1; a < c; a++) {
        FILE *f = fopen(v[a], "rb"); if (!f) continue; Hdr h; std::vector<uint8_t> b; long n = 0, rs = -1, re = -1, kmax = 0, st[2][2] = {}; uint64_t first = 0; double ts = 0, te = 0, peak = 0;
        printf("%s\n", v[a]);
        while (fread(&h, 16, 1, f) == 1) {
            b.resize((size_t)h.w * h.h * 3); if (fread(b.data(), 1, b.size(), f) != b.size()) break;
            if (!first) first = h.t; double t = (h.t - first) / 24e6;
            double top = band(b.data(), h.w, h.h * 6 / 100, h.h * 9 / 100), bot = band(b.data(), h.w, h.h * 93 / 100, h.h * 97 / 100), mid = band(b.data(), h.w, h.h * 30 / 100, h.h * 50 / 100);
            if (top < 6 && bot < 6 && mid > 40) {
                long k = 0, tot = 0; for (uint32_t y = h.h * 15 / 100; y < h.h * 85 / 100; y++) for (uint32_t x = h.w * 4 / 100; x < h.w * 93 / 100; x++) { uint8_t *p = &b[(y * h.w + x) * 3]; tot++; if (p[0] < 8 && p[1] < 8 && p[2] < 8) k++; }
                double s = (double)k / tot; if (rs < 0) { rs = n; ts = t; peak = 0; kmax = 0; } re = n; te = t; if (s > peak) peak = s; if (s > 0.03) kmax++;
                double sec = h.t / 24e6, ph = sec - (uint64_t)sec; if (ph > 0.12 && ph < 0.88) { int on = (uint64_t)sec & 1; st[on][0]++; st[on][1] += s > 0.03; }
            } else if (rs >= 0 && n - re > 30) { if (re - rs > 10) printf("  frames %ld..%ld t %.2f..%.2f black peak %.3f frames>3%% %ld\n", rs, re, ts, te, peak, kmax); rs = -1; }
            n++;
        }
        if (rs >= 0 && re - rs > 10) printf("  frames %ld..%ld t %.2f..%.2f black peak %.3f frames>3%% %ld\n", rs, re, ts, te, peak, kmax);
        printf("  total frames %ld; scene frames fix-on seconds %ld (black>3%% %ld), fix-off seconds %ld (black>3%% %ld)\n", n, st[1][0], st[1][1], st[0][0], st[0][1]); fclose(f);
    }
}
