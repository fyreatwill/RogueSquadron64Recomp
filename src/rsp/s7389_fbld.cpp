// s7389 framebuffer-load watch, host half. Question: does any guest CPU code READ rendered framebuffer / Z-buffer
// pixels? With ROGUESQ_RENDER_TO_RAM=0 RT64 never writes rendered pixels back to RDRAM, so such a reader would see
// stale memory (lens-flare Z tests, screenshots, fades that read the fb). rs64_fbpg[] marks 4 KB physical pages
// named by RDP SetColorImage (op 0x3F) / SetZImage (op 0x3E) in the gfx RDP stream (rs64_s7389_scan, called per
// submit from dpc_bridge). The guest-side check lives in include/fbld/recomp.h and is compiled in ONLY in build_fbld
// (cmake -DROGUESQ_FB_LDWATCH=ON); in every other build rs64_fbpg stays zero and nothing calls rs64_fbld_hit.
// Env: ROGUESQ_S7389_FBLD=1 enables marking; ROGUESQ_S7389_CTL=<lo>:<hi> (hex phys) marks a non-fb range as kind
// "ctl" (positive control: guest data the game reads every frame must report hits through the same macro path).
// Output (stderr): [s7389-new] first hit per (file,line,kind,live); [s7389-sum] every ~20 s. Offline:
// tools/s7389_fbld_report.py <log> classifies each line load/store from the generated source. Diagnostic only.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <string>
#include <unordered_map>

extern "C" volatile uint32_t rs64_vi_n_g;
extern "C" { uint32_t rs64_fbpg[4096]; }
static uint32_t s_pg_c[4096], s_pg_z[4096];  // last VI (+1) a page was named as colour / Z image
static uint8_t s_pg_ctl[4096];
static int s_on = -1;
static std::mutex s_mu;
struct Row { uint64_t n = 0; uint32_t page = 0, first_vi = 0; int w = 0; };
static std::unordered_map<std::string, Row> s_rows;
static uint64_t s_hits[3][2], s_new_lines, s_cimg, s_zimg;
static uint32_t s_last_cimg, s_last_zimg, s_last_sum_vi;
static constexpr uint32_t kLiveVi = 8;  // named within the last 8 VIs = a framebuffer in current use

static bool fbld_on() {
    if (s_on < 0) {
        const char *e = std::getenv("ROGUESQ_S7389_FBLD");
        s_on = (e && *e && *e != '0') ? 1 : 0;
        if (s_on) {
            if (const char *c = std::getenv("ROGUESQ_S7389_CTL")) {
                unsigned lo = 0, hi = 0;
                if (sscanf(c, "%x:%x", &lo, &hi) == 2 && hi > lo && hi <= 0x1000000u)
                    for (unsigned p = lo >> 12; p <= ((hi - 1) >> 12); ++p) { s_pg_ctl[p] = 1; rs64_fbpg[p] = 1; }
                fprintf(stderr, "[s7389] ctl range 0x%06X-0x%06X\n", lo, hi);
            }
            fprintf(stderr, "[s7389] fb-load watch armed (marks from the gfx RDP stream)\n");
        }
    }
    return s_on == 1;
}

static void mark(uint32_t *arr, uint32_t addr, uint32_t bytes, uint32_t vi) {
    if (addr >= 0x1000000u) return;
    uint32_t end = addr + bytes; if (end > 0x1000000u) end = 0x1000000u;
    for (uint32_t p = addr >> 12; p <= ((end - 1) >> 12); ++p) { arr[p] = vi + 1; rs64_fbpg[p] = 1; }
}

static void summary(uint32_t vi) {
    std::lock_guard<std::mutex> lk(s_mu);
    fprintf(stderr, "[s7389-sum] vi=%u cimg=%llu zimg=%llu last_c=0x%06X last_z=0x%06X keys=%zu "
            "color live/stale=%llu/%llu z live/stale=%llu/%llu ctl=%llu\n", vi,
            (unsigned long long)s_cimg, (unsigned long long)s_zimg, s_last_cimg, s_last_zimg, s_rows.size(),
            (unsigned long long)s_hits[0][1], (unsigned long long)s_hits[0][0], (unsigned long long)s_hits[1][1],
            (unsigned long long)s_hits[1][0], (unsigned long long)(s_hits[2][0] + s_hits[2][1]));
    for (auto &kv : s_rows)
        fprintf(stderr, "[s7389-row] %s n=%llu page=0x%06X first_vi=%u w=%d\n", kv.first.c_str(),
                (unsigned long long)kv.second.n, kv.second.page, kv.second.first_vi, kv.second.w);
    fflush(stderr);
}

extern "C" void rs64_s7389_scan(uint32_t lo, uint32_t hi, const uint8_t *rdram) {
    if (!fbld_on() || !rdram || hi <= lo || hi - lo > 0x100000u || hi > 0x1000000u) return;
    const uint32_t vi = rs64_vi_n_g;
    static uint32_t s_cw = 320, s_bpp = 2;
    auto rd = [&](uint32_t a) { uint32_t v; memcpy(&v, rdram + (a & 0xFFFFFCu), 4); return v; };
    for (uint32_t a = lo & ~3u, step = 8; a + 8 <= hi; a += step) {
        const uint32_t w0 = rd(a), w1 = rd(a + 4), op = (w0 >> 24) & 0x3F;
        step = (op == 0x24 || op == 0x25) ? 16u
             : (op >= 0x08 && op <= 0x0F) ? 32u + ((op & 4) ? 64u : 0u) + ((op & 2) ? 64u : 0u) + ((op & 1) ? 16u : 0u) : 8u;
        if (op == 0x3F) {
            s_cw = (w0 & 0x3FFu) + 1u; const uint32_t siz = (w0 >> 19) & 3u; s_bpp = siz == 3 ? 4u : siz == 2 ? 2u : 1u;
            const uint32_t addr = w1 & 0xFFFFFFu; mark(s_pg_c, addr, s_cw * s_bpp * 256u, vi);
            ++s_cimg; s_last_cimg = addr;
        } else if (op == 0x3E) {
            const uint32_t addr = w1 & 0xFFFFFFu; mark(s_pg_z, addr, s_cw * 2u * 256u, vi);
            ++s_zimg; s_last_zimg = addr;
        }
    }
    if (vi - s_last_sum_vi >= 1200u) { s_last_sum_vi = vi; summary(vi); }
}

extern "C" void rs64_fbld_hit(uint32_t phys, const char *file, int line, int width) {
    const uint32_t p = phys >> 12, vi = rs64_vi_n_g;
    int kind; bool live;
    if (s_pg_ctl[p]) { kind = 2; live = true; }
    else {
        const uint32_t c = s_pg_c[p], z = s_pg_z[p];
        const bool lc = c && vi + 1 - c <= kLiveVi, lz = z && vi + 1 - z <= kLiveVi;
        if (lz || (!lc && z >= c)) { kind = 1; live = lz; } else { kind = 0; live = lc; }
    }
    static const char *kn[3] = {"color", "z", "ctl"};
    const char *base = strrchr(file, '/'); base = base ? base + 1 : file;
    char key[160]; snprintf(key, sizeof key, "%s:%d kind=%s live=%d", base, line, kn[kind], live ? 1 : 0);
    std::lock_guard<std::mutex> lk(s_mu);
    ++s_hits[kind][live ? 1 : 0];
    Row &r = s_rows[key];
    if (r.n++ == 0) {
        r.page = phys & ~0xFFFu; r.first_vi = vi; r.w = width;
        if (s_new_lines++ < 3000) { fprintf(stderr, "[s7389-new] vi=%u %s phys=0x%06X w=%d\n", vi, key, phys, width); fflush(stderr); }
    }
}
