// s6906 G5f: does a same-run toggle change the picture beyond motion? (1) Adjacent presented frames straddling each 1 s
// flip (lag-corrected) vs adjacent pairs mid block: mean abs diff and share of pixels moved > 40. (2) Runs of frames with
// a large black area (luma < 12 over > bigshare of the frame): start, length, block at start, block share.
// usage: g5f_flip_diff <raw> [lag_s=0.06] [skip=2000] [bigshare=0.15]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <algorithm>
struct H { uint64_t t; uint32_t w, h; };
int main(int c, char **v) {
    FILE *f = fopen(v[1], "rb"); if (!f) return 1; double lag = c > 2 ? atof(v[2]) : .06; long skip = c > 3 ? atol(v[3]) : 2000; double big = c > 4 ? atof(v[4]) : .15;
    H h; fread(&h, 16, 1, f); fseeko(f, 0, SEEK_SET); int W = h.w, Hh = h.h; size_t fs = (size_t)W * Hh * 3; std::vector<uint8_t> a(fs), b(fs); long i = 0; uint64_t pt = 0;
    std::vector<double> mad[3], mv[3]; long runs = 0, rs = -1, rb = 0, ron = 0, blackfr[2] = {0, 0}, fr[2] = {0, 0};
    while (fread(&h, 16, 1, f) == 1 && fread(b.data(), 1, fs, f) == fs) {
        int bl = ((h.t - (uint64_t)(lag * 24e6)) / 24000000ull) & 1, pb = ((pt - (uint64_t)(lag * 24e6)) / 24000000ull) & 1;
        long dark = 0, n = 0; for (int y = 30; y < Hh; y += 2) for (int x = 0; x < 900; x += 2) { const uint8_t *p = &b[((size_t)y * W + x) * 3]; n++; if (p[0] < 12 && p[1] < 12 && p[2] < 12) dark++; }
        bool bk = (double)dark / n > big;
        if (i >= skip) { fr[bl]++; if (bk) blackfr[bl]++; if (bk && rs < 0) { rs = i; rb = bl; ron = 0; } if (bk) ron += bl; if (!bk && rs >= 0) { printf("black run %ld len %ld start block %ld on-share %.2f\n", rs, i - rs, rb, (double)ron / (i - rs)); rs = -1; runs++; } }
        if (i > skip) { int k = bl != pb ? (pb == 0 ? 0 : 1) : (i % 60 == 30 ? 2 : -1);
            if (k >= 0) { double s = 0; long m = 0, cnt = 0; for (int y = 30; y < Hh; y += 2) for (int x = 0; x < 900; x += 2) { const size_t o = ((size_t)y * W + x) * 3; int d = 0; for (int q = 0; q < 3; q++) d = std::max(d, abs(a[o + q] - b[o + q])); s += d; cnt++; if (d > 40) m++; } mad[k].push_back(s / cnt); mv[k].push_back((double)m / cnt); } }
        a.swap(b); pt = h.t; i++;
    }
    const char *nm[3] = {"off->on", "on->off", "mid"}; for (int k = 0; k < 3; k++) { auto &d = mad[k], &e = mv[k]; if (d.empty()) continue; std::sort(d.begin(), d.end()); std::sort(e.begin(), e.end()); printf("%s n %zu MAD p50 %.2f p90 %.2f moved>40 p50 %.4f p90 %.4f\n", nm[k], d.size(), d[d.size() / 2], d[d.size() * 9 / 10], e[e.size() / 2], e[e.size() * 9 / 10]); }
    printf("frames off %ld on %ld; big-black frames off %ld on %ld; runs %ld\n", fr[0], fr[1], blackfr[0], blackfr[1], runs);
}
