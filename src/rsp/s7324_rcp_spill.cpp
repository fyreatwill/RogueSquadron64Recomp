// s7324 class G (spill-rcp-ref): does the RCP ever get handed a spill-arena address (0x81000000-0x813FFFFF = phys 0x01xxxxxx)?
// The RSP DMA masks DRAM_ADDR to 0xFFFFF8 (rsp.hpp, as hardware) and the RDP address field is 24/26 bits, so a spill block read
// by the RCP either carries bits 24+ ("direct": hardware drops them) or was masked first ("alias": reads phys 0x00xxxxxx, which
// is heap/static, not the block). Sources: every RSP DMA (gfx/audio bank, rd/wr; hook in s7094_dma_shape.cpp, raw dram before
// the mask) and every RDP SETTIMG/SETZIMG/SETCIMG in the hardware DPC stream (hook at rs64_dpc_record_submit, dpc_bridge.cpp).
// Each address is classed by rs64_s7324_class (upstream_compat.cpp, needs ROGUESQ_S7317_ALLOCMAP=1): none / heap / alias-only /
// alias+heap / direct-live-spill / direct-other. First 8 examples per (source, class>=2) with block, req and host allocator.
// ROGUESQ_S7324_RCPREF=1|ctl (ctl: once per second the lowest live spill block start S is classed into ctl counters as the
// direct form S & 0x1FFFFFFF (must be direct-live) and the masked form S & 0xFFFFFF (must be alias-only or alias+heap)).
// Dump: build/rs64_s7324.log every 5 s (SIGKILL-safe).
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <mutex>
#include <atomic>
#include <chrono>
extern "C" int rs64_s7324_class(uint32_t addr, uint32_t* blk, uint32_t* req, void** pc);
extern "C" uint32_t rs64_s7324_lowspill();
extern "C" void rs64_s7324_sym(void* pc, char* out, size_t n);
extern "C" void rs64_s7324_near(uint32_t x, uint32_t* lo, uint32_t* loend, uint32_t* hi);
// s7325: audio RSP DMAs (rd/wr) whose address is in no live heap block (class none / alias_only) are classed against the
// freed-block history and the guest heap walk (rs64_s7325_gap, upstream_compat.cpp): static / hdrgap / freed / untracked;
// audio reads starting inside a live heap block but running past its end are counted as cross_end. Distinct table DG
// (src, addr, len) with first-sight neighbour owners, freed record (age, freer frames, allocator) and the guest header class.
// ctl: once per second the last freed ptr must class freed (or be live again: reused) and the end of the last malloc'd block, when
// its successor is <= 0x20 away, must class hdrgap. Dump: build/rs64_s7325.log beside the s7324 log.
struct S7325Out { uint32_t lo, loend, hi, lreq, hreq; void* lopc[3]; void* hipc[3]; uint32_t fptr, freq; double fage; void* fpc[4]; void* apc[3];
                  int gk; uint32_t gfl, gh, gsz; };
extern "C" int rs64_s7325_gap(uint32_t x, S7325Out* o, int guest);
extern "C" void rs64_s7325_ctl(uint32_t* fr, uint32_t* hg);
extern "C" void rs64_s7325_reconcile(FILE* o);
extern "C" int rs64_s7324_on = [] {
    const char* e = getenv("ROGUESQ_S7324_RCPREF");
    int v = (e && *e && *e != '0') ? (strcmp(e, "ctl") == 0 ? 2 : 1) : 0;
    if (v) fprintf(stderr, "[s7324] rcp spill-reference census armed mode=%s allocmap=%s\n", v == 2 ? "ctl" : "on",
                   getenv("ROGUESQ_S7317_ALLOCMAP") ? getenv("ROGUESQ_S7317_ALLOCMAP") : "(unset: classes will read none)");
    return v;
}();
namespace {
enum { S_DMA_RD_GFX, S_DMA_RD_AUD, S_DMA_WR_GFX, S_DMA_WR_AUD, S_TIMG, S_ZIMG, S_CIMG, S_N };
const char* kSrc[S_N] = {"dma_rd_gfx", "dma_rd_aud", "dma_wr_gfx", "dma_wr_aud", "rdp_timg", "rdp_zimg", "rdp_cimg"};
const char* kCls[6] = {"none", "heap", "alias_only", "alias_heap", "direct_spill", "direct_other"};
struct Ex { uint32_t addr, blk, req, len; void* pc[3]; };
std::mutex g_mu;
uint64_t g_n[S_N][6], g_ctl_n = 0, g_ctl_ok_dir = 0, g_ctl_ok_alias = 0, g_ctl_nospill = 0;
Ex g_ex[S_N][6][8]; int g_nex[S_N][6];
time_t g_last_dump = 0, g_last_ctl = 0;
// distinct (src, class>=2, 24-bit addr, len) with count and the nearest live heap blocks at first sight (static vs heap-gap triage)
struct Di { uint32_t src, cls, a24, len, raw0, lo, loend, hi; uint64_t n; };
Di g_di[4096]; uint32_t g_ndi = 0; uint64_t g_di_over = 0;
uint64_t g_tag[S_N][6][3];
const char* kGap[6] = {"live", "static", "hdrgap", "freed", "untracked", "cross_end"};
uint64_t g_gap[2][6];  // [rd/wr aud][kind]
struct Dg { uint32_t src, kind, x, len; uint64_t n; S7325Out o; };
Dg g_dg[8192]; uint32_t g_ndg = 0; uint64_t g_dg_over = 0;
uint64_t g_c5_n = 0, g_c5_fok = 0, g_c5_freuse = 0, g_c5_fbad = 0, g_c5_fnone = 0, g_c5_hn = 0, g_c5_hok = 0, g_c5_hbad = 0;
// s7330 audio-freed-song-read: which audio task reads a just-freed block? Audio task submits (osSpTaskStartGo type 2, guest thread)
// get a seq; the RSP runs one task at a time and the guest submits the next only after SP completion, so the running audio task at
// an audio DMA is the latest submitted one. Per task: submit, first and last audio DMA wall time (last DMA ~ task end). Per freed-class
// audio DMA (every hit, not distinct): time, seq, free time (now - fage), freed ptr, bulk flag (no host freer frames = guest bulk free).
// Guest wait edges (waitForMusyXAudioTaskDone entry/seed/exit) from the s2031 helper. ctl: every audio DMA must attribute (seq > 0,
// submit <= now < submit + 0.1 s). Dump build/rs64_s7330.log beside the s7325 log.
double s7330_now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
struct T7330 { uint64_t seq; double sub, first, last; uint32_t ndma, data; };
T7330 g_t30[65536]; uint64_t g_seq30 = 0;
struct H7330 { double t, ft; uint64_t seq; uint32_t dir, x, len, fptr, freq, bulk; };
H7330 g_h30[8192]; uint32_t g_nh30 = 0; uint64_t g_h30_over = 0;
struct W7330 { double t; uint32_t edge, pc; };
W7330 g_w30[8192]; uint64_t g_nw30 = 0;
uint64_t g_c30_n = 0, g_c30_ok = 0, g_c30_noseq = 0, g_c30_late = 0, g_c30_neg = 0;
double g_c30_maxdt = 0;
void s7330_dma_locked(double now) {
    g_c30_n++;
    if (!g_seq30) { g_c30_noseq++; return; }
    T7330& t = g_t30[g_seq30 & 65535];
    const double dt = now - t.sub;
    if (dt < 0) g_c30_neg++; else if (dt >= 0.1) g_c30_late++; else g_c30_ok++;
    if (dt > g_c30_maxdt) g_c30_maxdt = dt;
    if (!t.ndma++) t.first = now;
    t.last = now;
}
void dump7330_locked() {
    FILE* o = fopen("rs64_s7330.log", "w");
    if (!o) return;
    fprintf(o, "s7330 ctl aud_dma=%llu attr_ok=%llu noseq=%llu late=%llu neg=%llu maxdt=%.4f tasks=%llu hits=%u hit_over=%llu waits=%llu\n",
            (unsigned long long)g_c30_n, (unsigned long long)g_c30_ok, (unsigned long long)g_c30_noseq, (unsigned long long)g_c30_late,
            (unsigned long long)g_c30_neg, g_c30_maxdt, (unsigned long long)g_seq30, g_nh30, (unsigned long long)g_h30_over, (unsigned long long)g_nw30);
    uint64_t lastdump = 0;
    for (uint32_t i = 0; i < g_nh30; i++) { const H7330& h = g_h30[i];
        fprintf(o, "HIT t=%.6f dir=%s x=%08X len=%X seq=%llu fptr=%08X freq=%X ft=%.6f bulk=%u\n", h.t, h.dir ? "wr" : "rd", h.x, h.len,
                (unsigned long long)h.seq, h.fptr, h.freq, h.ft, h.bulk);
        const uint64_t lo = h.seq > 4 ? h.seq - 4 : 1, hi = h.seq + 4;
        for (uint64_t s = (lo > lastdump ? lo : lastdump + 1); s <= hi && s <= g_seq30; s++) {
            if (g_seq30 - s >= 65536) continue; const T7330& t = g_t30[s & 65535];
            fprintf(o, "TASK seq=%llu sub=%.6f first=%.6f last=%.6f ndma=%u data=%08X\n", (unsigned long long)t.seq, t.sub, t.first, t.last, t.ndma, t.data);
            lastdump = s; } }
    const uint64_t w0 = g_nw30 > 8192 ? g_nw30 - 8192 : 0;
    for (uint64_t i = w0; i < g_nw30; i++) { const W7330& w = g_w30[i & 8191];
        fprintf(o, "WAIT t=%.6f edge=%u pc=%08X\n", w.t, w.edge, w.pc); }
    fclose(o);
}
void dump7325_locked() {
    FILE* o = fopen("rs64_s7325.log", "w");
    if (!o) return;
    fprintf(o, "s7325 ctl_n=%llu freed_ok=%llu freed_reused=%llu freed_bad=%llu freed_none=%llu hdr_n=%llu hdr_ok=%llu hdr_bad=%llu\n",
            (unsigned long long)g_c5_n, (unsigned long long)g_c5_fok, (unsigned long long)g_c5_freuse, (unsigned long long)g_c5_fbad,
            (unsigned long long)g_c5_fnone, (unsigned long long)g_c5_hn, (unsigned long long)g_c5_hok, (unsigned long long)g_c5_hbad);
    for (int d = 0; d < 2; d++) { fprintf(o, "GAP %s", d ? "dma_wr_aud" : "dma_rd_aud"); for (int k = 0; k < 6; k++) fprintf(o, " %s=%llu", kGap[k], (unsigned long long)g_gap[d][k]); fprintf(o, "\n"); }
    for (uint32_t i = 0; i < g_ndg; i++) { const Dg& g = g_dg[i]; char lo[3][128], hi[3][128], fr[4][128], al[3][128];
        for (int j = 0; j < 3; j++) { rs64_s7324_sym(g.o.lopc[j], lo[j], 128); rs64_s7324_sym(g.o.hipc[j], hi[j], 128); rs64_s7324_sym(g.o.apc[j], al[j], 128); }
        for (int j = 0; j < 4; j++) rs64_s7324_sym(g.o.fpc[j], fr[j], 128);
        fprintf(o, "DG %s %s x=%08X len=%X n=%llu lo=%08X+%X(%s<%s) hi=%08X+%X(%s<%s) freed=%08X+%X age=%.3f freer=%s<%s<%s<%s alloc=%s<%s<%s guest=%d fl=%X h=%08X sz=%X\n",
                kSrc[g.src], kGap[g.kind], g.x, g.len, (unsigned long long)g.n, g.o.lo, g.o.lreq, lo[1], lo[2], g.o.hi, g.o.hreq, hi[1], hi[2],
                g.o.fptr, g.o.freq, g.o.fage, fr[0], fr[1], fr[2], fr[3], al[0], al[1], al[2], g.o.gk, g.o.gfl, g.o.gh, g.o.gsz); }
    fprintf(o, "DG_OVERFLOW %llu\n", (unsigned long long)g_dg_over);
    rs64_s7325_reconcile(o);
    fclose(o);
}
void dg_note(int src, int kind, uint32_t x, uint32_t len, const S7325Out* pre) {
    uint32_t i = 0;
    for (; i < g_ndg; i++) if (g_dg[i].src == (uint32_t)src && g_dg[i].x == x && g_dg[i].len == len && g_dg[i].kind == (uint32_t)kind) break;
    if (i < g_ndg) { g_dg[i].n++; return; }
    if (g_ndg >= 8192) { g_dg_over++; return; }
    Dg& g = g_dg[g_ndg++]; g.src = src; g.kind = kind; g.x = x; g.len = len; g.n = 1;
    if (pre) g.o = *pre; else rs64_s7325_gap(x, &g.o, 1);
}  // raw address top byte 0x00 / 0x80 / other, per class
void dump_locked() {
    FILE* o = fopen("rs64_s7324.log", "w");
    if (!o) return;
    fprintf(o, "s7324 mode=%d ctl_n=%llu ctl_direct_ok=%llu ctl_alias_ok=%llu ctl_nospill=%llu\n", rs64_s7324_on,
            (unsigned long long)g_ctl_n, (unsigned long long)g_ctl_ok_dir, (unsigned long long)g_ctl_ok_alias, (unsigned long long)g_ctl_nospill);
    for (int s = 0; s < S_N; s++) {
        fprintf(o, "SRC %s", kSrc[s]);
        for (int c = 0; c < 6; c++) fprintf(o, " %s=%llu", kCls[c], (unsigned long long)g_n[s][c]);
        fprintf(o, " | tag00/80/other:");
        for (int c = 0; c < 6; c++) fprintf(o, " %llu/%llu/%llu", (unsigned long long)g_tag[s][c][0], (unsigned long long)g_tag[s][c][1], (unsigned long long)g_tag[s][c][2]);
        fprintf(o, "\n");
    }
    for (int s = 0; s < S_N; s++) for (int c = 2; c < 6; c++) for (int k = 0; k < g_nex[s][c]; k++) {
        const Ex& e = g_ex[s][c][k]; char a[3][128];
        for (int j = 0; j < 3; j++) rs64_s7324_sym(e.pc[j], a[j], sizeof a[j]);
        fprintf(o, "EX %s %s addr=%08X len=%X blk=%08X req=%X owner=%s < %s < %s\n", kSrc[s], kCls[c], e.addr, e.len, e.blk, e.req, a[0], a[1], a[2]);
    }
    for (uint32_t i = 0; i < g_ndi; i++) { const Di& d = g_di[i];
        fprintf(o, "DI %s %s a24=%06X len=%X raw0=%08X n=%llu near_lo=%08X..%08X near_hi=%08X\n", kSrc[d.src], kCls[d.cls], d.a24, d.len, d.raw0,
                (unsigned long long)d.n, d.lo, d.loend, d.hi); }
    fprintf(o, "DI_OVERFLOW %llu\n", (unsigned long long)g_di_over);
    fclose(o);
}
void note(int src, uint32_t addr, uint32_t len) {
    uint32_t blk, req; void* pc[3];
    const int c = rs64_s7324_class(addr, &blk, &req, pc);
    std::lock_guard<std::mutex> lk(g_mu);
    g_n[src][c]++;
    if (c >= 2 && g_nex[src][c] < 8) g_ex[src][c][g_nex[src][c]++] = Ex{addr, blk, req, len, {pc[0], pc[1], pc[2]}};
    g_tag[src][c][(addr >> 24) == 0 ? 0 : (addr >> 24) == 0x80 ? 1 : 2]++;
    if (c == 2 || c >= 4) {
        const uint32_t a24 = addr & 0xFFFFFFu; uint32_t i = 0;
        for (; i < g_ndi; i++) if (g_di[i].src == (uint32_t)src && g_di[i].cls == (uint32_t)c && g_di[i].a24 == a24 && g_di[i].len == len) break;
        if (i < g_ndi) g_di[i].n++;
        else if (g_ndi < 4096) { uint32_t lo, le, hi; rs64_s7324_near(0x80000000u | a24, &lo, &le, &hi); g_di[g_ndi++] = Di{(uint32_t)src, (uint32_t)c, a24, len, addr, lo, le, hi, 1}; }
        else g_di_over++;
    }
    if (src == S_DMA_RD_AUD || src == S_DMA_WR_AUD) {
        const int d = src == S_DMA_WR_AUD;
        const double now30 = s7330_now(); s7330_dma_locked(now30);
        if (c == 1) { if (addr + len > blk + req) { g_gap[d][5]++; uint32_t x = 0x80000000u | (addr & 0xFFFFFFu); dg_note(src, 5, x, len, nullptr); } }
        else if (c == 0 || c == 2) {
            const uint32_t x = 0x80000000u | (addr & 0xFFFFFFu); S7325Out o; const int k = rs64_s7325_gap(x, &o, 0);
            g_gap[d][k]++;
            if (k == 3) { if (g_nh30 < 8192) g_h30[g_nh30++] = H7330{now30, s7330_now() - o.fage, g_seq30, (uint32_t)d, x, len, o.fptr, o.freq, o.fpc[0] ? 0u : 1u};
                          else g_h30_over++; }
            if (k >= 2) { uint32_t i = 0; for (; i < g_ndg; i++) if (g_dg[i].src == (uint32_t)src && g_dg[i].x == x && g_dg[i].len == len && g_dg[i].kind == (uint32_t)k) break;
                if (i < g_ndg) g_dg[i].n++; else { S7325Out o2; rs64_s7325_gap(x, &o2, 1); dg_note(src, k, x, len, &o2); } }
        }
    }
    const time_t now = time(nullptr);
    if (rs64_s7324_on == 2 && now != g_last_ctl) {
        g_c5_n++; uint32_t fr, hg; rs64_s7325_ctl(&fr, &hg); S7325Out o;
        if (!fr) g_c5_fnone++;
        else { const int k = rs64_s7325_gap(fr, &o, 0); if (k == 3) g_c5_fok++; else if (k == 0) g_c5_freuse++; else g_c5_fbad++; }
        if (hg) { g_c5_hn++; if (rs64_s7325_gap(hg, &o, 0) == 2) g_c5_hok++; else g_c5_hbad++; }
        g_last_ctl = now; g_ctl_n++;
        const uint32_t S = rs64_s7324_lowspill();
        if (!S) g_ctl_nospill++;
        else {
            uint32_t b2, r2; void* p2[3];
            if (rs64_s7324_class(S & 0x1FFFFFFFu, &b2, &r2, p2) == 4 && b2 == S) g_ctl_ok_dir++;
            const int ca = rs64_s7324_class(S & 0xFFFFFFu, &b2, &r2, p2);
            if ((ca == 2 || ca == 3) && b2 == S) g_ctl_ok_alias++;
        }
    }
    if (now - g_last_dump >= 5) { g_last_dump = now; dump_locked(); dump7325_locked(); dump7330_locked(); }
}
}  // namespace
extern "C" void rs64_s7324_dma(int dir, uint32_t dram, uint32_t raw_len, int aud) {
    note((dir ? 2 : 0) + (aud ? 1 : 0), dram, raw_len + 1);
}
// RDP image commands from the hardware stream [lo, hi). rd8(addr) reads one RDRAM byte at physical addr. Commands longer than
// 8 bytes (triangles 0x08-0x0F, texrects 0x24/0x25) are stepped over; a command crossing hi is resumed when the next range starts
// at the previous hi.
extern "C" void rs64_s7324_rdp(uint32_t lo, uint32_t hi, uint8_t (*rd8)(uint32_t)) {
    static uint32_t s_carry_at = 0xFFFFFFFFu, s_carry = 0;
    lo &= 0xFFFFFF; hi = (hi - 1) % 0x1000000u + 1;
    uint32_t a = lo;
    if (lo == s_carry_at) a += s_carry;
    s_carry_at = 0xFFFFFFFFu; s_carry = 0;
    static const uint8_t tri_len[8] = {4, 6, 12, 14, 12, 14, 20, 22};  // 64-bit words, 0x08-0x0F
    while (a + 8 <= hi) {
        const uint32_t w0 = (uint32_t)rd8(a) << 24 | (uint32_t)rd8(a + 1) << 16 | (uint32_t)rd8(a + 2) << 8 | rd8(a + 3);
        const uint32_t w1 = (uint32_t)rd8(a + 4) << 24 | (uint32_t)rd8(a + 5) << 16 | (uint32_t)rd8(a + 6) << 8 | rd8(a + 7);
        const uint32_t op = (w0 >> 24) & 0x3F;
        uint32_t n = 8;
        if (op >= 0x08 && op <= 0x0F) n = tri_len[op - 8] * 8u;
        else if (op == 0x24 || op == 0x25) n = 16;
        else if (op == 0x3D) note(S_TIMG, w1 & 0x3FFFFFFu, (w0 & 0xFFF) + 1);
        else if (op == 0x3E) note(S_ZIMG, w1 & 0x3FFFFFFu, 0);
        else if (op == 0x3F) note(S_CIMG, w1 & 0x3FFFFFFu, (w0 & 0xFFF) + 1);
        if (a + n > hi) { s_carry_at = hi; s_carry = a + n - hi; break; }
        a += n;
    }
}

// s7330 entry points: audio task submit (osSpTaskStartGo_recomp, type 2) and guest wait edges (s2031 helper in funcs_23.c).
extern "C" void rs64_s7330_aud_submit(uint32_t data_ptr) {
    if (!rs64_s7324_on) return;
    std::lock_guard<std::mutex> lk(g_mu);
    const uint64_t s = ++g_seq30; g_t30[s & 65535] = T7330{s, s7330_now(), 0, 0, 0, data_ptr};
}
namespace plume { bool rs64_pring_on(); double rs64_pring_now(); void rs64_pring_write(const char *row); }
// s7925 G5c: port-side MusyX wait marker for tools/s7922_transition_table.py (its pairing past the hangar anchor was ordinal,
// single-source: the port log had no wait marker). While ROGUESQ_PRESENT_RING is on, every waitForMusyXAudioTaskDone call that
// lasts >= 0.05 ms writes one row "M <entry t> pc=0x80091EB0 dur_ms=<entry->exit> fast=<shorter calls since last row>" on the
// present-ring clock (mach_absolute_time). Retail's wait-taken marker is 0x80091EC4 (gate 0x800A0F50 != 0); the untaken path
// returns in microseconds, so dur_ms separates the two without reading guest RAM. Off when the ring is off (no cost).
static void rs64_s7925_wait_mark(const char* edge, uint32_t pc) {
    static const bool on = plume::rs64_pring_on();
    if (!on) return;
    static thread_local double t_in = -1.0;
    static thread_local unsigned fast = 0;
    // s7926: ROGUESQ_S7926_WAITALL=1 also writes one "m <entry t> dur_ms=<d>" row for EVERY call (slow ones too, so the 6 known
    // slow waits are the same-run positive control of this path), capped at 4096 rows; an entry that re-enters before its exit
    // writes "m <t> unpaired=1". Settles s7925's open datum: is retail's 8th wait (flight entry) skipped or merely < 0.05 ms?
    static const bool all = [] { const char* e = getenv("ROGUESQ_S7926_WAITALL"); return e && *e == '1'; }();
    static thread_local unsigned nall = 0;
    char row[128];
    if (pc == 0x80091EB0u && !strcmp(edge, "wait-entry")) {
        const double now = plume::rs64_pring_now();
        if (all && t_in >= 0 && nall < 4096) { ++nall; snprintf(row, sizeof(row), "m %.6f unpaired=1\n", t_in); plume::rs64_pring_write(row); }
        t_in = now; return;
    }
    if (pc != 0x80091FBCu || strcmp(edge, "wait-exit") || t_in < 0) return;
    const double d_ms = (plume::rs64_pring_now() - t_in) * 1e3;
    if (all && nall < 4096) { ++nall; snprintf(row, sizeof(row), "m %.6f dur_ms=%.4f\n", t_in, d_ms); plume::rs64_pring_write(row); }
    if (d_ms < 0.05) { ++fast; t_in = -1.0; return; }
    snprintf(row, sizeof(row), "M %.6f pc=0x80091EB0 dur_ms=%.3f fast=%u\n", t_in, d_ms, fast);
    plume::rs64_pring_write(row);
    fast = 0; t_in = -1.0;
}
// s7928: ROGUESQ_S7928_GATEW=1 (needs the present ring) writes one row "G <t> pc=<writer> v=<byte after the store>" for every
// guest store to the MusyX gate byte 0x800A0F50 (the 7 s2031 writer sites in funcs_23.c call this right after their store),
// capped at 4096 rows. v=-1 before the first osViSwapBuffer (no rdram yet). Names the writer that leaves the gate 0 at flight
// entry (s7927: the port skips retail's flight-entry wait). Same-run control: each slow M row must follow a G row with v!=0.
extern "C" uint8_t* rs64_s7928_rdram(void);
static void rs64_s7928_gate_write(const char* edge, uint32_t pc) {
    static const bool on = [] { const char* e = getenv("ROGUESQ_S7928_GATEW"); return e && *e == '1' && plume::rs64_pring_on(); }();
    if (!on || strcmp(edge, "writer")) return;
    static std::atomic<unsigned> n{0};
    if (n.fetch_add(1) >= 4096) return;
    const uint8_t* rd = rs64_s7928_rdram();
    const int v = rd ? (int)rd[(0x800A0F50u - 0x80000000u) ^ 3u] : -1;
    char row[96];
    snprintf(row, sizeof(row), "G %.6f pc=0x%08X v=%d\n", plume::rs64_pring_now(), pc, v);
    plume::rs64_pring_write(row);
}
// s7928: with ROGUESQ_S7928_GATEW=1 each runVideoFrameTick caller site (0x8003E29C/0x8003E360 mainGameLoop, 0x800A9C70
// initSceneForMission, 0x800C5A18 menuOverlayInit; runVideoFrameTick calls musyxNoopStub first thing) writes
// "C <t> pc=<site> n=<call # at that site> g=<gate byte>" for its first 16 calls and every 600th after.
extern "C" void rs64_s7928_tick_caller(uint32_t pc) {
    static const bool on = [] { const char* e = getenv("ROGUESQ_S7928_GATEW"); return e && *e == '1' && plume::rs64_pring_on(); }();
    if (!on) return;
    static std::atomic<unsigned> cnt[4];
    const int i = pc == 0x8003E29Cu ? 0 : pc == 0x8003E360u ? 1 : pc == 0x800A9C70u ? 2 : 3;
    const unsigned n = cnt[i].fetch_add(1) + 1;
    if (n > 16 && n % 600) return;
    const uint8_t* rd = rs64_s7928_rdram();
    char row[96];
    snprintf(row, sizeof(row), "C %.6f pc=0x%08X n=%u g=%d\n", plume::rs64_pring_now(), pc, n,
             rd ? (int)rd[(0x800A0F50u - 0x80000000u) ^ 3u] : -1);
    plume::rs64_pring_write(row);
}
extern "C" void rs64_s7330_gate(const char* edge, uint32_t pc) {
    if (edge) { rs64_s7925_wait_mark(edge, pc); rs64_s7928_gate_write(edge, pc); }
    if (!rs64_s7324_on || !edge) return;
    uint32_t e = 0;
    if (!strcmp(edge, "wait-entry")) e = 1; else if (!strcmp(edge, "wait-seed")) e = 2; else if (!strcmp(edge, "wait-exit")) e = 3; else return;
    std::lock_guard<std::mutex> lk(g_mu);
    g_w30[g_nw30++ & 8191] = W7330{s7330_now(), e, pc};
}
