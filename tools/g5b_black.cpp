// s6894 G5b: finds terrain holes in a g5b_capture raw file: share of pixels near black in the picture interior
// (x 4..93%, y 15..85%, clear of title bar, bars and letterbox). Prints runs of frames over a threshold.
// usage: g5b_black <raw> [minShare=0.05]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
struct Hdr { uint64_t t; uint32_t w, h; };
int main(int c, char **v) {
    FILE *f = fopen(v[1], "rb"); if (!f) return 1; double th = c > 2 ? atof(v[2]) : 0.05;
    Hdr h; std::vector<uint8_t> b; long n = 0, hot = 0, rs = -1; double t0 = 0, peak = 0, rt = 0; uint64_t first = 0;
    while (fread(&h, 16, 1, f) == 1) {
        b.resize((size_t)h.w * h.h * 3); if (fread(b.data(), 1, b.size(), f) != b.size()) break;
        if (!first) first = h.t; double t = (h.t - first) / 24e6;
        long k = 0, tot = 0;
        for (uint32_t y = h.h * 15 / 100; y < h.h * 85 / 100; y++) for (uint32_t x = h.w * 4 / 100; x < h.w * 93 / 100; x++) { uint8_t *p = &b[(y * h.w + x) * 3]; tot++; if (p[0] < 6 && p[1] < 6 && p[2] < 6) k++; }
        double s = (double)k / tot;
        if (s > th) { hot++; if (rs < 0) { rs = n; rt = t; peak = 0; } if (s > peak) peak = s; }
        else if (rs >= 0) { printf("  run frames %ld..%ld t %.2f..%.2f peak %.3f\n", rs, n - 1, rt, t, peak); rs = -1; }
        n++;
    }
    if (rs >= 0) printf("  run frames %ld..%ld t %.2f..end peak %.3f\n", rs, n - 1, rt, peak);
    printf("frames %ld over %.2f: %ld\n", n, th, hot);
}
