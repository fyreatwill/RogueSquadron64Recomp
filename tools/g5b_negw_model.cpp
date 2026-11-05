// s6895 G5b: predicts what RT64's GPU path does with vertices of non-positive W, from a ROGUESQ_G5B_FRAME capture.
// RT64 emits clip w = 65536000/W (rt64_gbi_rdp.cpp, RasterVS xyz*=w). W<0 at a vertex: the GPU keeps the w>0 part, whose screen image
// runs from the positive vertices to infinity AWAY from the negative one. All three negative: nothing is drawn. The RDP only
// evaluates W on rows it draws, so it paints the plain triangle. Painter's model on an 8 px grid, last tri owns the cell.
// usage: g5b_negw_model cap.bin out.csv -> swap,mach,nneg,nall,c_wedge,c_lost,c_lost_terrain,c_total
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <vector>
#include <algorithm>
struct P { double x, y; };
static const int GW = 100, GH = 56, S = 8; static uint8_t own[GH][GW]; // 0 none 1 plain 2 wedge
static uint8_t hwo[GH][GW]; // what the RDP alone would leave: 1 painted
static void paint(const P *o, int k, uint8_t (*g)[GW], uint8_t v) {
    double x0 = 1e18, x1 = -1e18, y0 = 1e18, y1 = -1e18, ar = 0; for (int i = 0; i < k; i++) { int j = (i + 1) % k; x0 = fmin(x0, o[i].x); x1 = fmax(x1, o[i].x); y0 = fmin(y0, o[i].y); y1 = fmax(y1, o[i].y); ar += o[i].x * o[j].y - o[j].x * o[i].y; }
    if (ar == 0) return; double sg = ar > 0 ? 1 : -1;
    int gx0 = std::max(0, (int)floor(fmax(x0, -8) / S)), gx1 = std::min(GW - 1, (int)ceil(fmin(x1, 900) / S)), gy0 = std::max(0, (int)floor(fmax(y0, -8) / S)), gy1 = std::min(GH - 1, (int)ceil(fmin(y1, 500) / S));
    for (int y = gy0; y <= gy1; y++) for (int x = gx0; x <= gx1; x++) { double px = x * S + 4, py = y * S + 4; bool in = true;
        for (int i = 0; i < k && in; i++) { int j = (i + 1) % k; if (sg * ((o[j].x - o[i].x) * (py - o[i].y) - (o[j].y - o[i].y) * (px - o[i].x)) < 0) in = false; }
        if (in) g[y][x] = v; }
}
int main(int ac, char **av) {
    FILE *f = fopen(av[1], "rb"); FILE *g = fopen(av[2], "w"); if (!f || !g) return 1;
    static char ib[1 << 22]; setvbuf(f, ib, _IOFBF, sizeof ib); fprintf(g, "swap,mach,nneg,nall,c_wedge,c_lost,c_total\n");
    uint32_t tag, sw = 0, omh = 0; uint64_t t = 0; std::vector<uint8_t> c(1 << 21); long nneg = 0, nall = 0; bool have = false;
    auto flush = [&] { if (have) { long cw = 0, cl = 0, ct = 0; for (int y = 0; y < GH; y++) for (int x = 0; x < GW; x++) { ct += own[y][x] != 0; cw += own[y][x] == 2; cl += hwo[y][x] && !own[y][x]; }
        fprintf(g, "%u,%llu,%ld,%ld,%ld,%ld,%ld\n", sw, (unsigned long long)t, nneg, nall, cw, cl, ct); } memset(own, 0, sizeof own); memset(hwo, 0, sizeof hwo); nneg = nall = 0; };
    while (fread(&tag, 4, 1, f) == 1) {
        if (tag == 0x50415753u) { flush(); have = true; fread(&t, 8, 1, f); fread(&sw, 4, 1, f); continue; }
        if (tag == 0x204D4152u) { fseeko(f, 0x1000000, SEEK_CUR); continue; }
        uint32_t lo, n; fread(&lo, 4, 1, f); fread(&n, 4, 1, f); if (n > c.size()) c.resize(n); fread(c.data(), 1, n, f);
        auto rw = [&](uint32_t a) { uint32_t v; memcpy(&v, c.data() + a, 4); return v; };
        for (uint32_t a = 0; a + 8 <= n;) { uint32_t w0 = rw(a), w1 = rw(a + 4), op = (w0 >> 24) & 0x3F, l = 8;
            if (op == 0x24 || op == 0x25) l = 16; if (op == 0x2F) omh = w0;
            if (op >= 8 && op <= 15) { l = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0); if (a + l > n) break;
                auto sx = [](uint32_t v) { return (float)(((int32_t)(v << 18)) >> 18) / 4.0f; }; auto fx = [&](uint32_t o) { return (float)((double)(int32_t)rw(a + o) / 65536.0); };
                float yl = sx(w0 & 0x3FFF), ym = sx((w1 >> 16) & 0x3FFF), yh = sx(w1 & 0x3FFF), xl = fx(8), dl = fx(12), xh = fx(16), dh = fx(20), xm = fx(24), dm = fx(28); (void)dl; (void)xm; (void)dm;
                float yF = floorf(yh), hI = xh - dh * yF; P v[3] = {{dh * yh + hI, yh}, {dh * yl + hI, yl}, {xl, ym}};
                float W[3] = {1, 1, 1};
                if ((op & 2) && (omh & 0x80000)) { uint32_t tb = a + 32 + ((op & 4) ? 64 : 0); auto T = [&](int i) { return rw(tb + i * 4); }; auto pk = [&](int i, int j) { return (int32_t)((T(i) & 0xFFFF0000u) | (T(j) >> 16)); };
                    float wb = pk(1, 5) / 65536.0f, wdx = pk(3, 7) / 65536.0f, wde = pk(9, 13) / 65536.0f, d1 = yh - yF, d2 = yl - yF, d3 = ym - yF, dx3 = xl - (dh * ym + hI);
                    W[0] = wb + wde * d1; W[1] = wb + wde * d2; W[2] = wb + wde * d3 + wdx * dx3; }
                int neg = (W[0] <= 0) + (W[1] <= 0) + (W[2] <= 0); paint(v, 3, hwo, 1);
                if (neg == 0) paint(v, 3, own, 1);
                else if (neg == 3) nall++;
                else { nneg++; const double K = 1e5; P q[4]; int k = 0;
                    if (neg == 1) { int b = W[0] <= 0 ? 0 : W[1] <= 0 ? 1 : 2, A = (b + 1) % 3, C = (b + 2) % 3; q[k++] = v[A]; q[k++] = v[C]; q[k++] = {v[C].x + K * (v[C].x - v[b].x), v[C].y + K * (v[C].y - v[b].y)}; q[k++] = {v[A].x + K * (v[A].x - v[b].x), v[A].y + K * (v[A].y - v[b].y)}; }
                    else { int A = W[0] > 0 ? 0 : W[1] > 0 ? 1 : 2, B = (A + 1) % 3, C = (A + 2) % 3; q[k++] = v[A]; q[k++] = {v[A].x + K * (v[A].x - v[B].x), v[A].y + K * (v[A].y - v[B].y)}; q[k++] = {v[A].x + K * (v[A].x - v[C].x), v[A].y + K * (v[A].y - v[C].y)}; }
                    paint(q, k, own, 2); }
            }
            a += l; }
    }
    flush(); fclose(g);
}
