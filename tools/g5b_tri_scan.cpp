// s6894 G5b: one pass over a ROGUESQ_G5B_TRIS stream. Per swap: count and summed area of "sheet" triangles, meaning
// z-buffered tris (op&1) over minArea. Prints each flagged swap, its mach time, its z range, and the biggest sheet.
// usage: g5b_tri_scan <tris.bin> [minArea=100000]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <vector>
#include <map>
#pragma pack(push,1)
struct R { uint8_t op, pad; uint16_t cw; uint32_t timg, z; int16_t c[10]; };
#pragma pack(pop)
int main(int ac, char **av) {
    FILE *f = fopen(av[1], "rb"); if (!f) return 1; double minA = ac > 2 ? atof(av[2]) : 100000;
    static char buf[1 << 22]; setvbuf(f, buf, _IOFBF, sizeof buf);
    uint64_t t = 0; uint32_t sw = 0, m; long nsw = 0, nflag = 0, n = 0; double sum = 0, best = 0; R bb{}; int cnt = 0; uint32_t zmin = ~0u, zmax = 0;
    std::map<uint32_t, long> tex;
    auto flush = [&] { if (cnt) { nflag++; tex[bb.timg]++; printf("swap %u mach %llu n=%ld sheets=%d sum=%.0f op=%02X timg=%08X z=%08X..%08X big=%.0f", sw, (unsigned long long)t, n, cnt, sum, bb.op, bb.timg, zmin, zmax, best); for (int i = 0; i < 10; i += 2) printf(" %.0f,%.0f", bb.c[i] / 4.0, bb.c[i + 1] / 4.0); putchar('\n'); } n = 0; sum = 0; best = 0; cnt = 0; zmin = ~0u; zmax = 0; };
    while (fread(&m, 4, 1, f) == 1) {
        if (m == 0xF5F5F5F5u) { flush(); nsw++; if (fread(&t, 8, 1, f) != 1 || fread(&sw, 4, 1, f) != 1) break; continue; }
        R r; memcpy(&r, &m, 4); if (fread((char *)&r + 4, sizeof r - 4, 1, f) != 1) break;
        n++; if (!(r.op & 1)) continue;
        double a = 0; for (int i = 0; i < 5; i++) { int j = (i + 1) % 5; a += (double)r.c[i * 2] * r.c[j * 2 + 1] - (double)r.c[j * 2] * r.c[i * 2 + 1]; } a = fabs(a) / 32;
        if (a < minA) continue; cnt++; sum += a; if (r.z < zmin) zmin = r.z; if (r.z > zmax) zmax = r.z; if (a > best) { best = a; bb = r; }
    }
    flush(); fprintf(stderr, "swaps %ld flagged %ld\n", nsw, nflag); for (auto &k : tex) fprintf(stderr, "  timg %08X %ld\n", k.first, k.second);
}
