// s7106 (fps60-wall-rsp-clip): how many RDP triangles does each F5 gfx-ucode command produce, and in particular each TRI_GEN
// (0x05) of the 9 terrain cells around the eye (ring <= 1)? FPS60 near-wall flicker: s7105 showed the CPU emits those cells'
// TRI_GENs on every episode frame; s7098 showed the wall is absent from the RDP stream. So: does the ucode turn them into 0 tris?
//
// Mechanism (static read, build/factor5_ucode/factor5_ucode_recompiled.c): the ucode appends RDP commands to a DMEM output
// buffer at 0xD60, fill pointer r16; the flush routine L_112C (r10 = r16 - 0xD60) DMAs [0xD60, r16) to the RDRAM FIFO, kicks
// DPC_END and resets r16 = 0xD60. The command dispatch loop L_1090 fetches r19/r20 at DMEM r17. So the RDP bytes produced by
// command k are DMEM [r16 at fetch k, r16 at fetch k+1), split by any flush in between. Hooks (tools/fixup_factor5_ucode.py,
// marker "s7106 rsptri"): rs64_s7106_fetch at every fetch (before the s6896 TG edge fix edits p8/p9), rs64_s7106_flush at the
// flush entry. Both parse [pos, r16) with the RDP length table (tri 32 + 64 shade + 64 tex + 16 z, texrect 16, rest 8) and
// add the triangles to the command being processed.
// Near-cell keys: tools/apply_s7106_rsptri.py publishes, from the CPU emit (s7105_visit), words 8 and 9 (+0x20/+0x24: the
// grid bases + step, F5Rogue.cpp TriGen*_BuildVtxData) of the last TRI_GEN emitted for each ring <= 1 cell into g_s7106_k8/k9.
// A fetched TRI_GEN whose (w0, p8, p9) matches slot j is attributed to near cell j. The CPU runs a frame ahead of the RSP, but
// the near cells' keys are stable from frame to frame (the same world cell), so the match is by cell, not by frame.
// Control (independent line): dpc_bridge.cpp rs64_spike_scan counts every forwarded RDP triangle (rs64_s7106_btri); per swap,
// tall (this DMEM parse) must equal tbr (the bridge) within the swap-boundary skew. Fixed counts: mode-0 sub-0 TRI_GENs (5x5
// grid) should carry the GLideN64 default order count when unclipped, mode-2 quads 2.
// One line per swap (ROGUESQ_S7106_RSPTRI=<file>, "1" = rs64_s7106.txt in the cwd):
//   rt m=<mach> sw=<swap> ntg=<TRI_GENs> ttg=<their tris> tall=<all tris parsed> tbr=<bridge tris> mis=<parse overruns>
//   c<k>=<cmds>,<tris>,<zero-tri cmds>,<min>,<max>[,<mode tris>:<count>] for k = 0 (mode0 sub0), 1 (mode0 sub1), 2 (mode 2), 3 other
//   n=<9 x seen,tris,zero,degenerate,minx,miny,maxx,maxy (px, '-' if none)> separated by ';', row-major dz -1..1, dx -1..1
//   kp=<published slots> k4=<eye cell w0,p8,p9>
// s7107 (fps60-wall-painter), ROGUESQ_S7107_TAG=1 on top of S7106_RSPTRI: every RDP triangle the DMEM parse sees pushes one tag
// byte into an SPSC FIFO; dpc_bridge.cpp pops one per forwarded triangle (rs64_s7107_pop) and stores it in the pad byte of the
// ROGUESQ_G5B_TRIS record. The order is the same on both sides (s7106: tall == tbr on 8505/8505 swaps). Tag: 0..48 = 7x7 cell
// (dz+3)*7 + dx+3 around the eye (24 = eye cell; keys from tools/apply_s7107_painter.py), 0x40|class = a TRI_GEN matching no
// published key, 0x80|op = a triangle produced by a non-TRI_GEN command (op = w0>>24 & 0x7F), 0xFD = before any fetch,
// 0xFF = popped from an empty FIFO (desync). rt line gains q=<depth at swap>,<empty pops>,<pushes>,<pops>,<FIFO overflows>.
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mach/mach_time.h>
extern "C" int rs64_swap_n(void);
extern "C" {
uint32_t g_s7106_kw[9], g_s7106_k8[9], g_s7106_k9[9];
uint32_t g_s7107_kw[49], g_s7107_k8[49], g_s7107_k9[49];
int rs64_s7107_tag = [] {
    const char* e = getenv("ROGUESQ_S7107_TAG");
    int v = (e && *e && *e != '0') ? 1 : 0;
    if (v) fprintf(stderr, "[s7107] per-triangle source-cell tag FIFO armed\n");
    return v;
}();
int rs64_s7106_on = [] {
    const char* e = getenv("ROGUESQ_S7106_RSPTRI");
    int v = (e && *e && *e != '0') ? 1 : 0;
    if (v) fprintf(stderr, "[s7106] per-command RSP triangle census armed\n");
    return v;
}();
}
namespace {
std::atomic<uint32_t> g_btri{0};
FILE* g_f = nullptr;
struct Cls { uint32_t n, t, z, mn, mx; uint32_t h[48]; };
struct Near { uint32_t seen, t, z, dg; int x0, y0, x1, y1; };
struct {
    int sw = -1; uint32_t ntg, ttg, tall, mis; Cls c[4]; Near nr[9];
} S;
uint32_t g_pos = 0xD60;
int g_cls = -1, g_near = -1;  // command being processed: class (-1 = not a TRI_GEN), near-cell slot
uint32_t g_cmdtris = 0;
uint8_t g_tag = 0xFD;  // s7107: tag of the command being processed
constexpr uint32_t kQ = 1u << 22;
uint8_t g_q[kQ];
std::atomic<uint32_t> g_qh{0}, g_qt{0};  // head = pushes, tail = pops (monotonic)
std::atomic<uint32_t> g_qempty{0}; uint32_t g_qover = 0, g_qpush_sw = 0; std::atomic<uint32_t> g_qpop_sw{0};
inline void qpush(uint8_t v) {
    const uint32_t h = g_qh.load(std::memory_order_relaxed);
    if (h - g_qt.load(std::memory_order_acquire) >= kQ) { g_qover++; return; }
    g_q[h & (kQ - 1)] = v; g_qh.store(h + 1, std::memory_order_release); g_qpush_sw++;
}
inline uint32_t rdw(const uint8_t* dm, uint32_t a) {
    uint32_t v = 0;
    for (int q = 0; q < 4; ++q) v = (v << 8) | dm[((a + q) & 0xFFFu) ^ 3u];
    return v;
}
inline int sx14(uint32_t v) { return (int)(v << 18) >> 18; }
void reset_swap(int sw) {
    memset(&S, 0, sizeof S); S.sw = sw;
    for (auto& c : S.c) c.mn = 0xFFFFFFFFu;
    for (auto& n : S.nr) { n.x0 = n.y0 = 1 << 30; n.x1 = n.y1 = -(1 << 30); }
}
void emit_swap() {
    if (!g_f || S.sw < 0) return;
    const uint32_t br = g_btri.exchange(0, std::memory_order_relaxed);
    fprintf(g_f, "rt m=%llu sw=%d ntg=%u ttg=%u tall=%u tbr=%u mis=%u", (unsigned long long)mach_absolute_time(), S.sw, S.ntg, S.ttg,
            S.tall, br, S.mis);
    for (int k = 0; k < 4; ++k) {
        const Cls& c = S.c[k];
        int best = -1; for (int i = 0; i < 48; ++i) if (c.h[i] && (best < 0 || c.h[i] > c.h[best])) best = i;
        fprintf(g_f, " c%d=%u,%u,%u,%u,%u,%d:%u", k, c.n, c.t, c.z, c.n ? c.mn : 0, c.mx, best, best >= 0 ? c.h[best] : 0);
    }
    fputs(" n=", g_f);
    for (int j = 0; j < 9; ++j) {
        const Near& n = S.nr[j];
        if (n.t) fprintf(g_f, "%u,%u,%u,%u,%d,%d,%d,%d", n.seen, n.t, n.z, n.dg, n.x0, n.y0, n.x1, n.y1);
        else fprintf(g_f, "%u,0,%u,0,-", n.seen, n.z);
        if (j < 8) fputc(';', g_f);
    }
    int kp = 0; for (int j = 0; j < 9; ++j) kp += g_s7106_kw[j] != 0;
    fprintf(g_f, " kp=%d k4=%08x,%08x,%08x", kp, g_s7106_kw[4], g_s7106_k8[4], g_s7106_k9[4]);
    if (rs64_s7107_tag) {
        int kq = 0; for (int j = 0; j < 49; ++j) kq += g_s7107_kw[j] != 0;
        fprintf(g_f, " q=%u,%u,%u,%u,%u kq=%d", g_qh.load() - g_qt.load(), g_qempty.exchange(0), g_qpush_sw, g_qpop_sw.exchange(0), g_qover, kq);
        g_qpush_sw = 0;
    }
    fputc('\n', g_f);
}
// Parse RDP commands in DMEM [g_pos, end) and attribute their triangles to the current command.
void parse(const uint8_t* dm, uint32_t end) {
    uint32_t a = g_pos;
    while (a < end) {
        const uint32_t w0 = rdw(dm, a), op = (w0 >> 24) & 0x3F;
        const uint32_t len = (op >= 0x08 && op <= 0x0F) ? 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0)
                             : (op == 0x24 || op == 0x25) ? 16 : 8;
        if (a + len > end) { S.mis++; break; }
        if (op >= 0x08 && op <= 0x0F) {
            S.tall++; g_cmdtris++;
            if (rs64_s7107_tag) qpush(g_tag);
            if (g_near >= 0) {
                Near& n = S.nr[g_near];
                const uint32_t w1 = rdw(dm, a + 4);
                const int yl = sx14(w0 & 0x3FFF) / 4, ym = sx14((w1 >> 16) & 0x3FFF) / 4, yh = sx14(w1 & 0x3FFF) / 4;
                const int xl = (int32_t)rdw(dm, a + 8) >> 16, xh = (int32_t)rdw(dm, a + 16) >> 16, xm = (int32_t)rdw(dm, a + 24) >> 16;
                n.dg += yl <= yh;
                const int xs[3] = {xl, xh, xm};
                for (int x : xs) { if (x < n.x0) n.x0 = x; if (x > n.x1) n.x1 = x; }
                if (yh < n.y0) n.y0 = yh; if (yl > n.y1) n.y1 = yl; (void)ym;
            }
        }
        a += len;
    }
    g_pos = a < end ? end : a;
}
void close_cmd() {
    if (g_cls >= 0) {
        Cls& c = S.c[g_cls];
        c.n++; c.t += g_cmdtris; c.z += g_cmdtris == 0;
        if (g_cmdtris < c.mn) c.mn = g_cmdtris; if (g_cmdtris > c.mx) c.mx = g_cmdtris;
        c.h[g_cmdtris < 47 ? g_cmdtris : 47]++;
        S.ttg += g_cmdtris;
        if (g_near >= 0) { Near& n = S.nr[g_near]; n.seen++; n.t += g_cmdtris; n.z += g_cmdtris == 0; }
    }
    g_cls = -1; g_near = -1; g_cmdtris = 0;
}
}  // namespace

extern "C" void rs64_s7106_btri(void) { g_btri.fetch_add(1, std::memory_order_relaxed); }
extern "C" uint8_t rs64_s7107_pop(void) {
    if (!rs64_s7107_tag) return 0xFF;
    const uint32_t tl = g_qt.load(std::memory_order_relaxed);
    if (tl == g_qh.load(std::memory_order_acquire)) { g_qempty.fetch_add(1, std::memory_order_relaxed); return 0xFF; }
    const uint8_t v = g_q[tl & (kQ - 1)]; g_qt.store(tl + 1, std::memory_order_release); g_qpop_sw.fetch_add(1, std::memory_order_relaxed);
    return v;
}

extern "C" void rs64_s7106_flush(const uint8_t* dm, uint32_t r16) {
    if (r16 >= g_pos && r16 <= 0x1000u) parse(dm, r16);
    g_pos = 0xD60;
}

extern "C" void rs64_s7106_fetch(const uint8_t* dm, uint32_t r17, uint32_t w0, uint32_t r16) {
    if (!g_f) {
        static bool tried = false; if (tried) return; tried = true;
        const char* e = getenv("ROGUESQ_S7106_RSPTRI");
        g_f = fopen(strcmp(e, "1") == 0 ? "rs64_s7106.txt" : e, "w");
        if (!g_f) { fprintf(stderr, "[s7106] cannot open %s\n", e); return; }
        setvbuf(g_f, nullptr, _IOFBF, 1 << 20); reset_swap(rs64_swap_n());
    }
    if (r16 < g_pos) g_pos = 0xD60;  // the task start reset r16 without passing the flush hook
    if (r16 <= 0x1000u) parse(dm, r16);
    close_cmd();
    const int sw = rs64_swap_n();
    if (sw != S.sw) { emit_swap(); reset_swap(sw); }
    g_tag = (uint8_t)(0x80u | ((w0 >> 24) & 0x7Fu));
    if ((w0 >> 24) != 0x05) return;
    S.ntg++;
    const uint32_t mode = (w0 >> 8) & 0xFF, sub = w0 & 0xFF;
    g_cls = mode == 0 ? (sub == 0 ? 0 : 1) : mode == 2 ? 2 : 3;
    const uint32_t p8 = rdw(dm, r17 + 0x20), p9 = rdw(dm, r17 + 0x24);
    for (int j = 0; j < 9; ++j)
        if (g_s7106_kw[j] == w0 && g_s7106_k8[j] == p8 && g_s7106_k9[j] == p9) { g_near = j; break; }
    if (rs64_s7107_tag) {
        g_tag = (uint8_t)(0x40u | (uint32_t)g_cls);
        for (int j = 0; j < 49; ++j)
            if (g_s7107_kw[j] == w0 && g_s7107_k8[j] == p8 && g_s7107_k9[j] == p9) { g_tag = (uint8_t)j; break; }
    }
}
