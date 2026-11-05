// s6895 G5b: per triangle of a ROGUESQ_G5B_FRAME capture, compare what the RDP rasterises (edge walk with lft, y-scissor,
// x-scissor, empty rows skipped) with the polygon RT64 draws (rt64_gbi_rdp.cpp: H(y1) H(y2) [L(y2)] (xl,ym) [M(ym) M(y1)]).
// usage: g5b_rt64_excess cap.bin out.csv [minExcess=3000]  -> one line per tri whose RT64 area beats the RDP area by minExcess.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <vector>
#include <algorithm>
struct P { double x, y; };
static double clipArea(std::vector<P> p, double x0, double y0, double x1, double y1) {
    auto cl = [&](auto in, auto ix) { std::vector<P> o; for (size_t i = 0; i < p.size(); i++) { P a = p[(i + p.size() - 1) % p.size()], b = p[i]; if (in(b)) { if (!in(a)) o.push_back(ix(a, b)); o.push_back(b); } else if (in(a)) o.push_back(ix(a, b)); } p = o; };
    auto ixx = [](double X) { return [X](P a, P b) { double t = (X - a.x) / (b.x - a.x); return P{X, a.y + t * (b.y - a.y)}; }; };
    auto ixy = [](double Y) { return [Y](P a, P b) { double t = (Y - a.y) / (b.y - a.y); return P{a.x + t * (b.x - a.x), Y}; }; };
    cl([&](P a) { return a.x >= x0; }, ixx(x0)); if (p.empty()) return 0; cl([&](P a) { return a.x <= x1; }, ixx(x1)); if (p.empty()) return 0;
    cl([&](P a) { return a.y >= y0; }, ixy(y0)); if (p.empty()) return 0; cl([&](P a) { return a.y <= y1; }, ixy(y1)); if (p.empty()) return 0;
    double s = 0; for (size_t i = 0; i < p.size(); i++) { P a = p[i], b = p[(i + 1) % p.size()]; s += a.x * b.y - b.x * a.y; } return fabs(s) / 2;
}
int main(int ac, char **av) {
    FILE *f = fopen(av[1], "rb"); FILE *g = fopen(av[2], "w"); if (!f || !g) return 1; double minE = ac > 3 ? atof(av[3]) : 3000;
    static char ib[1 << 22]; setvbuf(f, ib, _IOFBF, sizeof ib);
    FILE *h = fopen(ac > 4 ? av[4] : "negw.csv", "w"); long nbad = 0; fprintf(h, "swap,mach,ord,op,om,hw,rt,w1,w2,w3,yh,ym,yl,xh,xm,xl,dh,dm,dl\n");
    fprintf(g, "swap,mach,ord,off,op,lft,om,hw,rt,tri3,yh,ym,yl,xh,xm,xl,dh,dm,dl,z\n");
    uint32_t tag, sw = 0, om = 0, omh = 0, sc[2] = {0, 0}; uint64_t t = 0; long ord = 0; std::vector<uint8_t> c(1 << 21); long tris = 0, flagged = 0;
    while (fread(&tag, 4, 1, f) == 1) {
        if (tag == 0x50415753u) { fread(&t, 8, 1, f); fread(&sw, 4, 1, f); ord = 0; continue; }
        if (tag == 0x204D4152u) { fseeko(f, 0x1000000, SEEK_CUR); continue; }
        uint32_t lo, n; fread(&lo, 4, 1, f); fread(&n, 4, 1, f); if (n > c.size()) c.resize(n); fread(c.data(), 1, n, f);
        auto rw = [&](uint32_t a) { uint32_t v; memcpy(&v, c.data() + a, 4); return v; };
        for (uint32_t a = 0; a + 8 <= n;) { uint32_t w0 = rw(a), w1 = rw(a + 4), op = (w0 >> 24) & 0x3F, l = 8;
            if (op == 0x24 || op == 0x25) l = 16; if (op == 0x2F) { om = w1; omh = w0; } if (op == 0x2D) { sc[0] = w0; sc[1] = w1; }
            if (op >= 8 && op <= 15) { l = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0); if (a + l > n) break; ord++; tris++;
                auto sx = [](uint32_t v) { return (double)(((int32_t)(v << 18)) >> 18) / 4.0; }; auto fx = [&](uint32_t o) { return (double)(int32_t)rw(a + o) / 65536.0; };
                int lft = (w0 >> 23) & 1; double yl = sx(w0 & 0x3FFF), ym = sx((w1 >> 16) & 0x3FFF), yh = sx(w1 & 0x3FFF), xl = fx(8), dl = fx(12), xh = fx(16), dh = fx(20), xm = fx(24), dm = fx(28);
                double sx0 = ((sc[0] >> 12) & 0xFFF) / 4.0, sy0 = (sc[0] & 0xFFF) / 4.0, sx1 = ((sc[1] >> 12) & 0xFFF) / 4.0, sy1 = (sc[1] & 0xFFF) / 4.0; if (sx1 <= sx0 || sy1 <= sy0) { a += l; continue; }
                double yF = floor(yh), hw = 0; int ys = (int)std::max(ceil(yh), sy0), ye = (int)std::min(ceil(yl), sy1);
                for (int y = ys; y < ye; y++) { double xa = xh + dh * (y - yF), xb = y < ym ? xm + dm * (y - yF) : xl + dl * (y - ym); double L = lft ? xa : xb, Rr = lft ? xb : xa; L = std::max(L, sx0); Rr = std::min(Rr, sx1); if (Rr > L) hw += Rr - L; }
                // float32, in rt64_gbi_rdp.cpp's order: its rounding is part of what is under test
                float fyh = (float)yh, fyl = (float)yl, fym = (float)ym, fxh = (float)xh, fdh = (float)dh, fxm = (float)xm, fdm = (float)dm, fxl = (float)xl, fdl = (float)dl, fyF = floorf(fyh), fhI = fxh - fdh * fyF, fmI = fxm - fdm * fyF;
                double hI = fhI, mI = fmI, y1 = fyh, y2 = fyl, x1 = fdh * fyh + fhI, x2 = fdh * fyl + fhI, x3 = fxl, y3 = fym;
                double tri3 = clipArea({{x1, y1}, {x2, y2}, {x3, y3}}, sx0, sy0, sx1, sy1);
                double xC = xl + dl * (y2 - y3), xE = dm * y3 + mI, xF = dm * y1 + mI, e = 1.0 / 256; bool uC = (y2 - y3) >= 1 && fabs(xC - x2) > e, uE = (y3 - y1) >= 1 && (fabs(xE - x3) > e || fabs(xF - x1) > e);
                std::vector<P> q{{x1, y1}, {x2, y2}}; if (uC) q.push_back({xC, y2}); q.push_back({x3, y3}); if (uE) { q.push_back({xE, y3}); q.push_back({xF, y1}); }
                double rt = 0; for (size_t i = 1; i + 1 < q.size(); i++) rt += clipArea({q[0], q[i], q[i + 1]}, sx0, sy0, sx1, sy1); // fan, as emitted
                // s6895: RT64's per-vertex W (rt64_gbi_rdp.cpp) feeds gl clip w = 65536000/W. W<=0 at a vertex: GPU clips against w>0,
                // and the screen polygon is no longer the RDP's. The RDP only ever evaluates W on the rows it draws.
                if ((op & 2) && (omh & 0x80000)) { uint32_t tb = a + 32 + ((op & 4) ? 64 : 0); auto T = [&](int i) { return rw(tb + i * 4); };
                    auto pk = [&](int i, int j) { return (int32_t)((T(i) & 0xFFFF0000u) | (T(j) >> 16)); };
                    float wb = pk(1, 5) / 65536.0f, wdx = pk(3, 7) / 65536.0f, wde = pk(9, 13) / 65536.0f;
                    float d1 = fyh - fyF, d2 = fyl - fyF, d3 = fym - fyF, x3o = fdh * fym + fhI, dx3 = fxl - x3o, w1 = wb + wde * d1, w2 = wb + wde * d2, w3 = wb + wde * d3 + wdx * dx3;
                    if ((w1 <= 0 || w2 <= 0 || w3 <= 0) && hw > 0) { nbad++; fprintf(h, "%u,%llu,%ld,%02X,%08X,%.0f,%.0f,%.1f,%.1f,%.1f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.4f,%.4f,%.4f\n", sw, (unsigned long long)t, ord, op, om, hw, rt, w1, w2, w3, yh, ym, yl, xh, xm, xl, dh, dm, dl); } }
                if (rt - hw > minE || tri3 - hw > minE || hw > 40000 || rt > 40000) { flagged++; fprintf(g, "%u,%llu,%ld,%u,%02X,%d,%08X,%.0f,%.0f,%.0f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.3f,%.3f,%.3f,%08X\n", sw, (unsigned long long)t, ord, lo + a, op, lft, om, hw, rt, tri3, yh, ym, yl, xh, xm, xl, dh, dm, dl, (op & 1) ? rw(a + l - 16) : 0); }
            }
            a += l; }
    }
    fclose(g); fclose(h); printf("tris %ld flagged %ld negW %ld\n", tris, flagged, nbad);
}
