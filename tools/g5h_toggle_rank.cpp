// s6921 G5h: which shots does a 1 s =tog lever visibly change? Per toggle in a g5b_capture raw: mean abs diff of frames G either side of the edge (across) against the same gap inside
// each state (within), so camera motion cancels. The same statistic at mid-second, where no lever edge sits, is the same-run control. Picture cuts are dropped: within, or any one-frame step inside the gap, above cut.
// usage: g5h_toggle_rank RAW [G=8] [cut=14] [top=16] [y0pct=0] [y1pct=100]; prints the ratio distribution at true and mid-second edges, then the top toggles (rel s, frame, to-state, across, within).
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <algorithm>
using namespace std;
struct R { double ac, wi, rt; size_t i; int to; };
int main(int c, char **a) {
    FILE *f = fopen(a[1], "rb"); if (!f) return 1;
    int G = c > 2 ? atoi(a[2]) : 8; double cut = c > 3 ? atof(a[3]) : 14; size_t top = c > 4 ? atoi(a[4]) : 16; int p0 = c > 5 ? atoi(a[5]) : 0, p1 = c > 6 ? atoi(a[6]) : 100;
    uint64_t t0; uint32_t w, h; fread(&t0, 8, 1, f); fread(&w, 4, 1, f); fread(&h, 4, 1, f);
    size_t n = (size_t)w * h * 3, fs = 16 + n; fseeko(f, 0, SEEK_END); size_t N = ftello(f) / fs; vector<uint64_t> T(N);
    for (size_t i = 0; i < N; i++) { fseeko(f, i * fs, SEEK_SET); fread(&T[i], 8, 1, f); }
    size_t y0 = (size_t)h * p0 / 100 * w * 3, y1 = (size_t)h * p1 / 100 * w * 3;
    vector<uint8_t> A(n), B(n), C(n), D(n);
    auto get = [&](size_t i, vector<uint8_t> &b) { fseeko(f, i * fs + 16, SEEK_SET); fread(b.data(), 1, n, f); };
    auto mad = [&](vector<uint8_t> &x, vector<uint8_t> &y) { double s = 0; for (size_t i = y0; i < y1; i++) s += abs((int)x[i] - y[i]); return s / (y1 - y0); };
    vector<R> real, mid; size_t dropped = 0;
    auto add = [&](size_t i, vector<R> &o, int to) {
        if (i < (size_t)3 * G + 1 || i + 3 * G + 1 >= N) return;
        get(i - G, A); get(i + G, B); get(i - 3 * G, C); get(i + 3 * G, D);
        double ac = mad(A, B), wi = (mad(C, A) + mad(B, D)) / 2;
        get(i - G, A); for (size_t k = i - G + 1; k <= i + G; k++) { get(k, B); bool jump = mad(A, B) > cut; A.swap(B); if (jump) { dropped++; return; } }  // a picture cut inside the gap
        if (wi > cut) { dropped++; return; }
        o.push_back({ac, wi, ac / (wi + 0.25), i, to});
    };
    for (size_t i = 1; i < N; i++) {
        uint64_t s0 = T[i - 1] / 24000000, s1 = T[i] / 24000000;
        if ((s0 & 1) != (s1 & 1)) add(i, real, (int)(s1 & 1));
        else if (T[i - 1] % 24000000 < 12000000 && T[i] % 24000000 >= 12000000) add(i, mid, (int)(s1 & 1));
    }
    auto show = [&](const char *l, vector<R> v) {
        if (v.empty()) { printf("%s none\n", l); return; }
        vector<double> d; for (auto &x : v) d.push_back(x.rt); sort(d.begin(), d.end()); size_t m = d.size();
        printf("%s n %zu ratio p50 %.2f p90 %.2f p99 %.2f max %.2f\n", l, m, d[m / 2], d[m * 9 / 10], d[m * 99 / 100], d[m - 1]);
    };
    printf("%s %ux%u frames %zu dropped %zu\n", a[1], w, h, N, dropped); show("toggle ", real); show("control", mid);
    sort(real.begin(), real.end(), [](const R &x, const R &y) { return x.rt > y.rt; });
    for (size_t i = 0; i < top && i < real.size(); i++) printf("  t=%7.2f frame %zu to %d across %.2f within %.2f ratio %.2f\n", (T[real[i].i] - t0) / 24e6, real[i].i, real[i].to, real[i].ac, real[i].wi, real[i].rt);
}
