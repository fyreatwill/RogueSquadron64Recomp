// s6895 G5b: painter's model of each swap from a ROGUESQ_G5B_TRIS stream. Terrain (othermode C8112220) has no Z compare, so
// the last tri over a cell owns it. Per swap, on an 8 px grid over the colour image: cells whose last painter is the sky pass
// (op 0E), a sheet (op&1, hull>minA), other Z tris; cells never painted. usage: g5b_paint_model tris.bin out.csv [minA=40000]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <vector>
#include <algorithm>
#include <map>
#pragma pack(push,1)
struct R { uint8_t op, pad; uint16_t cw; uint32_t timg, z; int16_t c[10]; };
#pragma pack(pop)
static const int GW = 128, GH = 64, S = 8;
static uint8_t own[GH][GW];
struct P { double x, y; };
static int hull(P *p, int n, P *o) {
    std::sort(p, p + n, [](P a, P b) { return a.x < b.x || (a.x == b.x && a.y < b.y); });
    auto cr = [](P a, P b, P c) { return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x); };
    int k = 0; for (int i = 0; i < n; i++) { while (k >= 2 && cr(o[k - 2], o[k - 1], p[i]) <= 0) k--; o[k++] = p[i]; }
    for (int i = n - 2, t = k + 1; i >= 0; i--) { while (k >= t && cr(o[k - 2], o[k - 1], p[i]) <= 0) k--; o[k++] = p[i]; }
    return k > 1 ? k - 1 : k;
}
int main(int ac, char **av) {
    FILE *f = fopen(av[1], "rb"); FILE *g = fopen(av[2], "w"); if (!f || !g) return 1; double minA = ac > 3 ? atof(av[3]) : 40000;
    static char buf[1 << 22]; setvbuf(f, buf, _IOFBF, sizeof buf);
    fprintf(g, "swap,mach,n,n0E,nZ,nsheet,c_none,c_sky,c_sheet,c_z,c_o,cw,skyidx0,skyidx1,sheetidx0\n");
    uint64_t t = 0; uint32_t sw = 0, m; long n = 0, n0 = 0, nz = 0, ns = 0, s0 = -1, s1 = -1, h0 = -1; int cw = 0; bool have = false;
    auto flush = [&] { if (have) { long c[5] = {}; for (auto &r : own) for (int v : r) c[v]++;
        fprintf(g, "%u,%llu,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%d,%ld,%ld,%ld\n", sw, (unsigned long long)t, n, n0, nz, ns, c[0], c[1], c[2], c[3], c[4], cw, s0, s1, h0); }
        memset(own, 0, sizeof own); n = n0 = nz = ns = 0; s0 = s1 = h0 = -1; };
    while (fread(&m, 4, 1, f) == 1) {
        if (m == 0xF5F5F5F5u) { flush(); have = true; if (fread(&t, 8, 1, f) != 1 || fread(&sw, 4, 1, f) != 1) break; continue; }
        R r; memcpy(&r, &m, 4); if (fread((char *)&r + 4, sizeof r - 4, 1, f) != 1) break;
        n++; if (r.cw > cw || (n == 1)) cw = r.cw;
        P p[5], o[12]; for (int i = 0; i < 5; i++) p[i] = { r.c[i * 2] / 4.0, r.c[i * 2 + 1] / 4.0 };
        int k = hull(p, 5, o); double a = 0; for (int i = 0; i < k; i++) { int j = (i + 1) % k; a += o[i].x * o[j].y - o[j].x * o[i].y; } a = fabs(a) / 2;
        int cls = r.op == 0x0E ? 1 : (r.op & 1) ? (a >= minA ? 2 : 3) : 4;
        if (cls == 1) { n0++; if (s0 < 0) s0 = n; s1 = n; } if (r.op & 1) nz++; if (cls == 2) { ns++; if (h0 < 0) h0 = n; }
        if (k < 3) continue; double x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9; for (int i = 0; i < k; i++) { x0 = fmin(x0, o[i].x); x1 = fmax(x1, o[i].x); y0 = fmin(y0, o[i].y); y1 = fmax(y1, o[i].y); }
        int gx0 = std::max(0, (int)floor(x0 / S)), gx1 = std::min(GW - 1, (int)ceil(x1 / S)), gy0 = std::max(0, (int)floor(y0 / S)), gy1 = std::min(GH - 1, (int)ceil(y1 / S));
        for (int y = gy0; y <= gy1; y++) for (int x = gx0; x <= gx1; x++) { double px = x * S + S / 2.0, py = y * S + S / 2.0; bool in = true;
            for (int i = 0; i < k && in; i++) { int j = (i + 1) % k; if ((o[j].x - o[i].x) * (py - o[i].y) - (o[j].y - o[i].y) * (px - o[i].x) < 0) in = false; }
            if (in) own[y][x] = cls; }
    }
    flush(); fclose(g);
}
