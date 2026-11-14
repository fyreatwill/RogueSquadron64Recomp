// s7363 class AN two-arm control (ASan). Each case is the site's logic lifted verbatim, pre (HEAD) vs post (s7363):
//  aim  : main.cpp ROGUESQ_AIM nearest-target search; a "nan" target leaves s_cur = 64 and the aim block read s_tg[64].
//  snap : s7097_edit_census.cpp word_snap with an unaligned DPC start: (a & ~3) - g_glo underflows.
//  grow : events.cpp g_row append; a truncated snprintf pushes n past the buffer and the closing "\n" write lands beyond it.
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <algorithm>

static float s_tg[64][3]; static unsigned s_ntg; static bool s_vis[64];
static double aim(bool post) {
    s_ntg = 0; const char* t = "nan,0,0";   // one ROGUESQ_AIM_TARGETS entry that sscanf %f accepts as NaN
    while (t && *t && s_ntg < 64 && sscanf(t, "%f,%f,%f", &s_tg[s_ntg][0], &s_tg[s_ntg][1], &s_tg[s_ntg][2]) == 3) { s_vis[s_ntg] = false; s_ntg++; t = strchr(t, ';'); if (!t) break; t++; }
    unsigned s_cur = 64; const float v[3] = {1, 2, 3};
    auto d2 = [&](unsigned k) { float a = s_tg[k][0]-v[0], b = s_tg[k][1]-v[1], c = s_tg[k][2]-v[2]; return a*a+b*b+c*c; };
    if (s_cur >= s_ntg) { float best = 1e30f; for (unsigned k = 0; k < s_ntg; k++) if (!s_vis[k] && d2(k) < best) { best = d2(k); s_cur = k; } }
    double tx = 0;
    if (!post || s_cur < s_ntg) tx = s_tg[s_cur][0] - v[0];
    return tx + (post ? (s_cur < s_ntg ? std::sqrt((double)d2(s_cur)) : -1.0) : std::sqrt((double)d2(s_cur)));
}

static uint32_t snap(bool post) {
    const uint32_t G = 64, kEnd = 0x1000000u, lo = 0x100042u, hi = 0x100100u;   // DPC start not 4-aligned
    std::vector<uint8_t> rd(kEnd, 0xAB);
    uint32_t g_glo, g_ghi;
    if (post) { g_glo = (lo >= G ? lo - G : 0) & ~3u; g_ghi = (std::min<uint32_t>(hi + G, kEnd) + 3u) & ~3u; }
    else      { g_glo = lo >= G ? lo - G : 0; g_ghi = std::min<uint32_t>(hi + G, kEnd); }
    std::vector<uint8_t> g_cur(rd.begin() + g_glo, rd.begin() + g_ghi);
    const uint32_t a = g_glo + 0;   // i == 0: the first byte of the window changed
    uint32_t v; memcpy(&v, &g_cur[(a & ~3u) - g_glo], 4);
    return v;
}

static int grow(bool post) {
    char buf[2048]; int n = std::snprintf(buf, sizeof(buf), "G %.6f os=%d", 1.0, 3);
    for (int i = 0; i < 64 && n < (int)sizeof(buf) - 48; i++) {
        const double cpu = 1e300, blk = 1e300;   // %.3f of 1e300 prints 305 chars: the append truncates
        const int w = std::snprintf(buf + n, sizeof(buf) - n, " %d.%d:%.3f/%.3f", i, 7, cpu, blk / 1e3);
        if (post) { if (w > 0) n = std::min(n + w, (int)sizeof(buf) - 2); } else n += w;
    }
    std::snprintf(buf + n, sizeof(buf) - n, "\n");
    return n;
}

int main(int argc, char** argv) {
    if (argc < 3) return 2;
    const bool post = !strcmp(argv[2], "post");
    if (!strcmp(argv[1], "aim"))  printf("aim %s -> %g\n", argv[2], aim(post));
    if (!strcmp(argv[1], "snap")) printf("snap %s -> %08X\n", argv[2], snap(post));
    if (!strcmp(argv[1], "grow")) printf("grow %s -> n=%d\n", argv[2], grow(post));
    return 0;
}
