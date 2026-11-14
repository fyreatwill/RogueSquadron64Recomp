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
extern "C" int rs64_s7324_class(uint32_t addr, uint32_t* blk, uint32_t* req, void** pc);
extern "C" uint32_t rs64_s7324_lowspill();
extern "C" void rs64_s7324_sym(void* pc, char* out, size_t n);
extern "C" void rs64_s7324_near(uint32_t x, uint32_t* lo, uint32_t* loend, uint32_t* hi);
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
uint64_t g_tag[S_N][6][3];  // raw address top byte 0x00 / 0x80 / other, per class
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
    const time_t now = time(nullptr);
    if (rs64_s7324_on == 2 && now != g_last_ctl) {
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
    if (now - g_last_dump >= 5) { g_last_dump = now; dump_locked(); }
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
