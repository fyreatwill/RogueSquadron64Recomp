// s6894 G5b: finds transient frames in a g5b_capture raw file. A terrain drop is a picture that differs from what came
// before AND what comes after while those two agree: for run length k (1..K), frame n..n+k-1 vs a=n-1, b=n+k.
// Per pixel-block (8x8 mean luma): T = share of blocks with |x-a|>th and |x-b|>th, same sign, and |a-b|<th/2.
// Steady motion fails the a~b test; a scene cut fails it too. HUD is included: it does not flash in steady play.
// usage: g5b_drops <raw> <out.csv> [th=24] [minT=0.04] [K=3] [dumpdir] [dump-from-s]
// Output csv: idx,t_s,gap_ms,k,T,dark,bright (dark = share of flagged blocks that got darker). Dumps a,x,b as PPM.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cmath>
#include <vector>
#include <string>
#include <mach/mach_time.h>
struct Hdr { uint64_t t; uint32_t w, h; };
int main(int c, char **v) {
    if (c < 3) return 2;
    FILE *f = fopen(v[1], "rb"); if (!f) return 3;
    FILE *o = fopen(v[2], "w");
    double th = c > 3 ? atof(v[3]) : 24, minT = c > 4 ? atof(v[4]) : 0.04; int K = c > 5 ? atoi(v[5]) : 3;
    const char *dump = c > 6 ? v[6] : nullptr; double dumpFrom = c > 7 ? atof(v[7]) : 0;
    Hdr h; if (fread(&h, 16, 1, f) != 1) return 4;
    size_t fs = (size_t)h.w * h.h * 3, rec = 16 + fs; int bw = h.w / 8, bh = h.h / 8, nb = bw * bh;
    mach_timebase_info_data_t tb; mach_timebase_info(&tb);
    fseeko(f, 0, SEEK_END); long n = ftello(f) / rec; fseeko(f, 0, SEEK_SET);
    std::vector<std::vector<float>> L(n, std::vector<float>(nb)); std::vector<uint64_t> T(n); std::vector<uint8_t> b(fs);
    for (long i = 0; i < n; i++) {
        fread(&h, 16, 1, f); fread(b.data(), 1, fs, f); T[i] = h.t;
        auto &l = L[i]; std::fill(l.begin(), l.end(), 0.f);
        for (uint32_t y = 0; y < (uint32_t)bh * 8; y++) for (uint32_t x = 0; x < (uint32_t)bw * 8; x++) { uint8_t *p = &b[(y * h.w + x) * 3]; l[(y / 8) * bw + x / 8] += 0.3f * p[0] + 0.59f * p[1] + 0.11f * p[2]; }
        for (auto &e : l) e /= 64;
    }
    auto sec = [&](uint64_t t) { return (double)(t - T[0]) * tb.numer / tb.denom / 1e9; };
    fprintf(o, "idx,t_s,gap_ms,k,T,dark,mach\n");
    // interval census
    long g20 = 0, g34 = 0, g50 = 0, g250 = 0; double gmax = 0;
    for (long i = 1; i < n; i++) { double g = (sec(T[i]) - sec(T[i - 1])) * 1e3; g20 += g > 20; g34 += g > 34; g50 += g > 50; g250 += g > 250; if (g > gmax) gmax = g; }
    long hits = 0, lastEnd = -1; int dumped = 0;
    for (long i = 1; i < n - 1; i++) {
        double best = 0, bd = 0; int bk = 0;
        for (int k = 1; k <= K && i + k < n; k++) {
            auto &A = L[i - 1], &B = L[i + k]; int m = 0, dk = 0;
            for (int j = 0; j < nb; j++) {
                if (fabsf(A[j] - B[j]) >= th / 2) continue;
                bool all = true; int sg = 0;
                for (int q = 0; q < k && all; q++) { float d1 = L[i + q][j] - A[j], d2 = L[i + q][j] - B[j]; int s = d1 > 0 ? 1 : -1; if (fabsf(d1) <= th || fabsf(d2) <= th || d1 * d2 < 0 || (sg && s != sg)) all = false; sg = s; }
                if (all) { m++; dk += sg < 0; }
            }
            double t = (double)m / nb; if (t > best) { best = t; bd = m ? (double)dk / m : 0; bk = k; }
        }
        if (best >= minT && i > lastEnd) {
            hits++; lastEnd = i + bk - 1;
            fprintf(o, "%ld,%.3f,%.1f,%d,%.4f,%.2f,%llu\n", i, sec(T[i]), (sec(T[i]) - sec(T[i - 1])) * 1e3, bk, best, bd, (unsigned long long)T[i]);
            if (dump && dumped < 400 && sec(T[i]) >= dumpFrom) {
                long idx[3] = {i - 1, i, i + bk}; const char *nm[3] = {"a", "x", "b"};
                for (int q = 0; q < 3; q++) { fseeko(f, idx[q] * rec + 16, SEEK_SET); fread(b.data(), 1, fs, f); char p[512]; snprintf(p, 512, "%s/%06ld_%s.ppm", dump, i, nm[q]); FILE *w = fopen(p, "wb"); fprintf(w, "P6\n%u %u\n255\n", h.w, h.h); fwrite(b.data(), 1, fs, w); fclose(w); }
                dumped++;
            }
        }
    }
    printf("frames=%ld span=%.1fs rate=%.2f/s gaps>20ms=%ld >34ms=%ld >50ms=%ld >250ms=%ld max=%.0fms transients=%ld\n", n, sec(T[n - 1]), (n - 1) / sec(T[n - 1]), g20, g34, g50, g250, gmax, hits);
}
