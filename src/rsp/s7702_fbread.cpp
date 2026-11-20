// s7702 (G1d 21:9 follow-up): does the GAME ever read a colour buffer back? RT64 skips the RDRAM write-back of a 768-wide colour image
// (SKIP_WILD_W, lib/rt64 rt64_state.cpp rs64_writeback_sane: allowlist 320/512/640/1024 + ROGUESQ_FB_WIDTH), which the 21:9 cutscene
// playlist uses (s7701). If the game reads that buffer (RDP texture from the framebuffer, RSP DMA from it), the skip shows stale RAM.
// RDP: every SETCIMG / SETZIMG in the hardware DPC stream enters a 16-entry history (addr, width, siz). Every SETTIMG whose 24-bit
// address falls inside a history colour image (480 rows, conservative) or Z image is a hit, keyed by the image width, whether it is
// the current colour image, and whether a LOADBLOCK/LOADTILE/LOADTLUT follows before the next SETTIMG. RSP: every DMA read (gfx/aud).
// Controls: boot self-test of the matcher (inside hit at row 10, below-start miss, past-480-rows miss) and a live control once per
// second: the current colour image + 5 rows must match (proves the history carries live stream data).
// ROGUESQ_S7702_FBREAD=1 ; dump build/rs64_s7702.log (cwd-relative) every 2 s, SIGKILL-safe.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <chrono>
extern "C" int rs64_s7702_on = [] {
    const char* e = getenv("ROGUESQ_S7702_FBREAD");
    int v = (e && *e && *e != '0') ? 1 : 0;
    if (v) fprintf(stderr, "[s7702] colour-buffer read census armed\n");
    return v;
}();
namespace {
struct Img { uint32_t addr, w, siz, z; double t; };
Img g_h[16]; int g_nh = 0;
uint32_t g_cur = 0xFFFFFFFFu, g_cur_w = 0, g_cur_siz = 0;
std::mutex g_mu;
double now_s() { static const auto t0 = std::chrono::steady_clock::now();
    return std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count(); }
// widths seen as colour images
struct Wc { uint32_t w, siz; uint64_t n; }; Wc g_wc[32]; int g_nwc = 0;
// hits: key (src 0=timg 1=dma_gfx 2=dma_aud, z, cur, w)
struct Hk { uint32_t src, z, cur, w, img, age; uint64_t n, loaded; double t0, t1; uint32_t rmin, rmax; }; Hk g_hk[256]; int g_nhk = 0;
// age bucket of the image's last SETCIMG/SETZIMG at the read: 0 <50 ms, 1 <500 ms, 2 <5 s, 3 older (stale: memory likely reused)
const char* kAge[4] = {"lt50ms", "lt500ms", "lt5s", "stale"};
uint32_t agebucket(double d) { return d < 0.05 ? 0u : d < 0.5 ? 1u : d < 5.0 ? 2u : 3u; }
struct Ex { uint32_t src, a, img, w, siz, row, cur, z; double t; uint32_t ld, age; }; Ex g_ex[256]; int g_nex = 0;
uint64_t g_n_timg = 0, g_n_cimg = 0, g_n_zimg = 0, g_n_dma = 0, g_ctl_n = 0, g_ctl_ok = 0;
int g_self = -1; double g_last_dump = -10, g_last_ctl = -10;
int g_pend_ex = -1; Hk* g_pend_hk = nullptr;
uint32_t rowbytes(uint32_t w, uint32_t siz) { return (w << siz) >> 1; }
// returns history index or -1; row out
int match(uint32_t a, uint32_t* row) {
    for (int i = g_nh - 1; i >= 0; --i) {
        const Img& m = g_h[i]; const uint32_t rb = rowbytes(m.w, m.siz);
        if (!rb) continue;
        if (a >= m.addr && a < m.addr + rb * 480u) { *row = (a - m.addr) / rb; return i; }
    }
    return -1;
}
void push(uint32_t a, uint32_t w, uint32_t siz, uint32_t z) {
    for (int i = 0; i < g_nh; ++i) if (g_h[i].addr == a && g_h[i].z == z) {
        Img m = g_h[i]; m.w = w; m.siz = siz; m.t = now_s();
        memmove(&g_h[i], &g_h[i + 1], (g_nh - i - 1) * sizeof(Img)); g_h[g_nh - 1] = m; return; }
    if (g_nh == 16) { memmove(&g_h[0], &g_h[1], 15 * sizeof(Img)); g_nh = 15; }
    g_h[g_nh++] = Img{a, w, siz, z, now_s()};
}
void selftest() {
    Img save[16]; int ns = g_nh; memcpy(save, g_h, sizeof save); g_nh = 0;
    push(0x100000, 768, 2, 0); uint32_t r = 0; int bad = 0;
    if (match(0x100000 + 768 * 2 * 10 + 4, &r) != 0 || r != 10) bad++;
    if (match(0x0FFFF8, &r) >= 0) bad++;
    if (match(0x100000 + 768 * 2 * 480, &r) >= 0) bad++;
    g_nh = ns; memcpy(g_h, save, sizeof save);
    g_self = bad == 0;
    fprintf(stderr, "[s7702] selftest %s (%d bad)\n", g_self ? "pass" : "FAIL", bad);
}
void hit(uint32_t src, uint32_t a, int idx, uint32_t row, double t) {
    const Img& m = g_h[idx]; const uint32_t cur = (!m.z && m.addr == g_cur) ? 1u : 0u;
    const uint32_t ag = agebucket(t - m.t);
    Hk* k = nullptr;
    for (int i = 0; i < g_nhk; ++i) if (g_hk[i].src == src && g_hk[i].z == m.z && g_hk[i].cur == cur && g_hk[i].w == m.w && g_hk[i].img == m.addr && g_hk[i].age == ag) { k = &g_hk[i]; break; }
    if (!k && g_nhk < 256) { k = &g_hk[g_nhk++]; *k = Hk{src, m.z, cur, m.w, m.addr, ag, 0, 0, t, t, row, row}; }
    int e = -1;
    if (k) { const bool first4 = k->n < 4; k->n++; k->t1 = t; if (row < k->rmin) k->rmin = row; if (row > k->rmax) k->rmax = row;
        if (first4 && g_nex < 256) { e = g_nex; g_ex[g_nex++] = Ex{src, a, m.addr, m.w, m.siz, row, cur, m.z, t, 0, ag}; } }
    if (src == 0) { g_pend_hk = k; g_pend_ex = e; }
}
void dump_locked(double t) {
    FILE* f = fopen("rs64_s7702.log", "w");
    if (!f) return;
    fprintf(f, "s7702 t=%.1f self=%d timg=%llu cimg=%llu zimg=%llu dma_rd=%llu ctl_live=%llu/%llu\n", t, g_self,
            (unsigned long long)g_n_timg, (unsigned long long)g_n_cimg, (unsigned long long)g_n_zimg, (unsigned long long)g_n_dma,
            (unsigned long long)g_ctl_ok, (unsigned long long)g_ctl_n);
    for (int i = 0; i < g_nwc; ++i) fprintf(f, "cimg_width w=%u siz=%u n=%llu\n", g_wc[i].w, g_wc[i].siz, (unsigned long long)g_wc[i].n);
    static const char* kS[3] = {"timg", "dma_gfx", "dma_aud"};
    for (int i = 0; i < g_nhk; ++i) fprintf(f, "hit src=%s img=%s@0x%06X cur=%u w=%u age=%s n=%llu loaded=%llu rows=%u..%u t=%.1f..%.1f\n", kS[g_hk[i].src],
            g_hk[i].z ? "z" : "colour", g_hk[i].img, g_hk[i].cur, g_hk[i].w, kAge[g_hk[i].age], (unsigned long long)g_hk[i].n,
            (unsigned long long)g_hk[i].loaded, g_hk[i].rmin, g_hk[i].rmax, g_hk[i].t0, g_hk[i].t1);
    for (int i = 0; i < g_nex; ++i) fprintf(f, "ex src=%s a=0x%06X img=0x%06X(%s) w=%u siz=%u row=%u cur=%u ld=0x%02X age=%s t=%.1f\n", kS[g_ex[i].src],
            g_ex[i].a, g_ex[i].img, g_ex[i].z ? "z" : "c", g_ex[i].w, g_ex[i].siz, g_ex[i].row, g_ex[i].cur, g_ex[i].ld, kAge[g_ex[i].age], g_ex[i].t);
    fclose(f);
}
void tick_locked() {
    const double t = now_s();
    if (g_self < 0) selftest();
    if (t - g_last_ctl >= 1.0 && g_cur != 0xFFFFFFFFu) { g_last_ctl = t; g_ctl_n++; uint32_t r = 0;
        const int i = match(g_cur + rowbytes(g_cur_w, g_cur_siz) * 5u, &r); if (i >= 0 && g_h[i].addr == g_cur && r == 5) g_ctl_ok++; }
    if (t - g_last_dump >= 2.0) { g_last_dump = t; dump_locked(t); }
}
}  // namespace

extern "C" void rs64_s7702_rdp(uint32_t lo, uint32_t hi, uint8_t (*rd8)(uint32_t)) {
    std::lock_guard<std::mutex> lk(g_mu);
    static uint32_t s_carry_at = 0xFFFFFFFFu, s_carry = 0;
    lo &= 0xFFFFFF; hi = (hi - 1) % 0x1000000u + 1;
    uint32_t a = lo;
    if (lo == s_carry_at) a += s_carry;
    s_carry_at = 0xFFFFFFFFu; s_carry = 0;
    static const uint8_t tri_len[8] = {4, 6, 12, 14, 12, 14, 20, 22};
    const double t = now_s();
    while (a + 8 <= hi) {
        const uint32_t w0 = (uint32_t)rd8(a) << 24 | (uint32_t)rd8(a + 1) << 16 | (uint32_t)rd8(a + 2) << 8 | rd8(a + 3);
        const uint32_t w1 = (uint32_t)rd8(a + 4) << 24 | (uint32_t)rd8(a + 5) << 16 | (uint32_t)rd8(a + 6) << 8 | rd8(a + 7);
        const uint32_t op = (w0 >> 24) & 0x3F;
        uint32_t n = 8;
        if (op >= 0x08 && op <= 0x0F) n = tri_len[op - 8] * 8u;
        else if (op == 0x24 || op == 0x25) n = 16;
        else if (op == 0x3F) {  // SETCIMG
            const uint32_t ad = w1 & 0xFFFFFFu, w = (w0 & 0xFFF) + 1, siz = (w0 >> 19) & 3;
            g_n_cimg++; g_cur = ad; g_cur_w = w; g_cur_siz = siz; push(ad, w, siz, 0);
            int k = -1; for (int i = 0; i < g_nwc; ++i) if (g_wc[i].w == w && g_wc[i].siz == siz) { k = i; break; }
            if (k < 0 && g_nwc < 32) { k = g_nwc++; g_wc[k] = Wc{w, siz, 0}; }
            if (k >= 0) g_wc[k].n++;
        } else if (op == 0x3E) {  // SETZIMG: Z buffer has the current colour image's width, 16-bit
            g_n_zimg++; if (g_cur_w) push(w1 & 0xFFFFFFu, g_cur_w, 2, 1);
        } else if (op == 0x3D) {  // SETTIMG
            g_n_timg++; g_pend_hk = nullptr; g_pend_ex = -1;
            uint32_t r = 0; const int i = match(w1 & 0xFFFFFFu, &r);
            if (i >= 0) hit(0, w1 & 0xFFFFFFu, i, r, t);
        } else if (op == 0x33 || op == 0x34 || op == 0x30) {  // LOADBLOCK / LOADTILE / LOADTLUT consume the pending SETTIMG
            if (g_pend_hk) { g_pend_hk->loaded++; g_pend_hk = nullptr; }
            if (g_pend_ex >= 0) { g_ex[g_pend_ex].ld = op; g_pend_ex = -1; }
        }
        if (a + n > hi) { s_carry_at = hi; s_carry = a + n - hi; break; }
        a += n;
    }
    tick_locked();
}

extern "C" void rs64_s7702_dma(int dir, uint32_t dram, uint32_t raw_len, int aud) {
    if (dir) return;  // reads only (RDRAM -> SP mem)
    std::lock_guard<std::mutex> lk(g_mu);
    g_n_dma++;
    const uint32_t a = dram & 0xFFFFF8u; uint32_t r = 0; const int i = match(a, &r);
    if (i >= 0) hit(aud ? 2u : 1u, a, i, r, now_s());
    (void)raw_len;
}
