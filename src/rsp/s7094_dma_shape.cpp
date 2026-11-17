// s7094: passive census of every RSP DMA the runtime services (librecomp rsp.hpp dma_rdram_to_dmem / dma_dmem_to_rdram),
// classified against the hardware SP DMA rules (cxd4 su.c MT_DMA_* / SP_DMA_READ / SP_DMA_WRITE, n64brew):
//   MEM_ADDR & 0x1FF8 (bit 12 = IMEM), DRAM_ADDR & 0xFFFFF8, LEN = ((raw & 0xFFF) | 7) + 1 per row,
//   rows = ((raw >> 12) & 0xFF) + 1, DRAM stride = len + (raw >> 20), DMEM offset wraps & 0xFF8 inside the 4 KB bank.
// The runtime copies raw+1 bytes from mem & 0xFFF, clipped at 0x1000, one row, so it equals hardware only when
// mem & 7 == 0, raw & 7 == 7, raw < 0x1000 and (mem & 0xFFF) + raw + 1 <= 0x1000. Every DMA whose shape breaks one of
// those is tallied by flag. All distinct (dir, bank, mem, len, dram&7) shapes are kept (512 max) and dumped to
// build/rs64_s7094.log every 5 s (SIGKILL-safe). ROGUESQ_S7094_DMASHAPE=1 arms it; =ctl is the positive control
// (count bits read from raw & 0x7FF000 << 1, i.e. any raw >= 0x800 flags as "count").
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <mutex>
extern "C" int rs64_s7094_on = [] {
    const char* e = getenv("ROGUESQ_S7094_DMASHAPE");
    int v = (e && *e && *e != '0') ? (strcmp(e, "ctl") == 0 ? 2 : 1) : 0;
    const char* g = getenv("ROGUESQ_S7324_RCPREF");  // s7324 class G rides this hook (src/rsp/s7324_rcp_spill.cpp)
    if (!v && g && *g && *g != '0') v = 1;
    const char* h = getenv("ROGUESQ_S7486_HOSTUAF");  // s7486 class EK host-read UAF watch rides this hook (upstream_compat.cpp rs64_s7486_hostread)
    if (!v && h && *h && *h != '0') v = 1;
    const char* z = getenv("ROGUESQ_S7501_EZ");  // s7501 class EZ: RSP DMEM->RDRAM writes into tracked framebuffers ride this hook
    if (!v && z && *z && *z != '0') v = 1;
    const char* ft = getenv("ROGUESQ_S7523_SLOWRDP");  // s7524 FT writer attribution rides this hook (src/rsp/s7523_slow_rdp.cpp rs64_s7523_dma)
    if (!v && ft && *ft && *ft != '0') v = 1;
    if (v) fprintf(stderr, "[s7094] dma shape census armed mode=%s\n", v == 2 ? "ctl" : "on");
    return v;
}();
namespace {
enum { F_IMEM, F_MEM7, F_LEN7, F_COUNT, F_SKIP, F_WRAP, F_DRAM7, F_DRAMHI, F_ZEROLEN, F_CTL, F_N };
const char* kFlag[F_N] = {"imem", "mem_lo3", "len_not7", "count", "skip", "dmem_wrap", "dram_lo3", "dram_hi8", "len_ffffffff", "ctl_count_mask7ff"};
struct Shape { uint32_t dir, aud, mem, len, d7, flags; uint64_t n; uint32_t dram_first; };
std::mutex g_mu;
Shape g_sh[512]; uint32_t g_nsh = 0; uint64_t g_over = 0;
uint64_t g_tot[2][2], g_fl[2][2][F_N], g_viol[2][2];
time_t g_last = 0;
uint32_t classify(uint32_t mem, uint32_t dram, uint32_t raw, int mode) {
    uint32_t f = 0;
    const uint32_t cnt = mode == 2 ? ((raw >> 11) & 0xFF) : ((raw >> 12) & 0xFF);
    if (mem & 0x1000) f |= 1u << F_IMEM;
    if (mem & 7) f |= 1u << F_MEM7;
    if ((raw & 7) != 7) f |= 1u << F_LEN7;
    if (cnt) f |= 1u << F_COUNT;
    if (raw >> 20) f |= 1u << F_SKIP;
    if ((mem & 0xFF8) + ((raw & 0xFFF) | 7) + 1 > 0x1000) f |= 1u << F_WRAP;
    if (dram & 7) f |= 1u << F_DRAM7;
    if (dram & 0xFF000000u) f |= 1u << F_DRAMHI;
    if (raw == 0xFFFFFFFFu) f |= 1u << F_ZEROLEN;
    if ((raw >> 11) & 0x1FF) f |= 1u << F_CTL;  // same-run positive control: mutated count mask, never a violation
    return f;
}
void dump_locked() {
    FILE* o = fopen("rs64_s7094.log", "w");
    if (!o) return;
    fprintf(o, "s7094 mode=%d distinct=%u overflow=%llu\n", rs64_s7094_on, g_nsh, (unsigned long long)g_over);
    for (int d = 0; d < 2; d++) for (int a = 0; a < 2; a++) {
        fprintf(o, "TOT dir=%s bank=%s n=%llu viol=%llu", d ? "wr" : "rd", a ? "aud" : "gfx",
                (unsigned long long)g_tot[d][a], (unsigned long long)g_viol[d][a]);
        for (int k = 0; k < F_N; k++) fprintf(o, " %s=%llu", kFlag[k], (unsigned long long)g_fl[d][a][k]);
        fprintf(o, "\n");
    }
    for (uint32_t i = 0; i < g_nsh; i++) {
        const Shape& s = g_sh[i];
        fprintf(o, "SH dir=%s bank=%s mem=0x%04X len=0x%08X dram7=%u dram0=0x%08X n=%llu flags=", s.dir ? "wr" : "rd",
                s.aud ? "aud" : "gfx", s.mem, s.len, s.d7, s.dram_first, (unsigned long long)s.n);
        for (int k = 0; k < F_N; k++) if (s.flags & (1u << k)) fprintf(o, "%s,", kFlag[k]);
        fprintf(o, "\n");
    }
    fclose(o);
}
// Self-test: every flag must fire on its synthetic shape and none on the canonical shape (detector control).
const bool g_selftest = [] {
    if (!rs64_s7094_on) return true;
    struct T { uint32_t mem, dram, raw, want; } t[] = {
        {0x170, 0x100000, 0x10F, 0}, {0x1080, 0, 0xF7F, 1u << F_IMEM}, {0x174, 0, 0xF, 1u << F_MEM7},
        {0x170, 0, 0x10, 1u << F_LEN7}, {0x0, 0, 0x100F, 1u << F_COUNT}, {0x0, 0, 0x0010000F, 1u << F_SKIP},
        {0xFF8, 0, 0xF, 1u << F_WRAP}, {0x0, 4, 0xF, 1u << F_DRAM7}, {0x0, 0x01000000, 0xF, 1u << F_DRAMHI}};
    int bad = 0;
    for (auto& x : t) { uint32_t f = classify(x.mem, x.dram, x.raw, 1) & ~(1u << F_CTL); if (f != x.want) { bad++; fprintf(stderr, "[s7094] selftest BAD mem=%X raw=%X got=%X want=%X\n", x.mem, x.raw, f, x.want); } }
    uint32_t fz = classify(0, 0, 0xFFFFFFFFu, 1);
    if (!(fz & (1u << F_ZEROLEN)) || !(fz & (1u << F_COUNT)) || !(fz & (1u << F_SKIP))) bad++;
    fprintf(stderr, "[s7094] selftest %s (%d bad of %zu)\n", bad ? "FAIL" : "pass", bad, sizeof(t) / sizeof(t[0]) + 1);
    return bad == 0;
}();
}  // namespace
extern "C" int rs64_s7324_on; extern "C" void rs64_s7324_dma(int dir, uint32_t dram, uint32_t raw_len, int aud);
extern "C" int rs64_s7331_on; extern "C" void rs64_s7331_dma(int dir, uint32_t mem, uint32_t dram, uint32_t raw_len, int aud);
extern "C" void rs64_s7486_hostread(int kind, uint32_t addr, uint32_t len);
extern "C" int rs64_s7523_on; extern "C" void rs64_s7523_dma(int dir, uint32_t mem, uint32_t dram, uint32_t raw, int aud);
extern "C" void rs64_s7094_dma_shape(int dir, uint32_t mem, uint32_t dram, uint32_t raw, int aud_in) {
    if (rs64_s7523_on) rs64_s7523_dma(dir, mem, dram, raw, aud_in);  // s7524 FT writer attribution
    if (!dir && !(mem & 0x1000)) rs64_s7486_hostread(aud_in ? 1 : 0, dram, raw >= 0xFFFu ? 0x1000u : raw + 1u);  // s7486 EK (no-op unless armed)
    if (dir && !(mem & 0x1000)) rs64_s7486_hostread(aud_in ? 7 : 6, dram, raw >= 0xFFFu ? 0x1000u : raw + 1u);  // s7489 EN host-write kinds (no-op unless ROGUESQ_S7489_HOSTWRITE)
    if (rs64_s7324_on && !(mem & 0x1000)) rs64_s7324_dma(dir, dram, raw, aud_in);
    if (rs64_s7331_on && !(mem & 0x1000)) rs64_s7331_dma(dir, mem, dram, raw, aud_in);  // s7331 reset dangling-writer attribution  // IMEM boot DMAs are skipped by the runtime
    const uint32_t aud = aud_in ? 1u : 0u;
    const uint32_t f = classify(mem, dram, raw, rs64_s7094_on);
    const uint32_t vmask = f & ~((1u << F_IMEM) | (1u << F_CTL));  // IMEM DMAs are skipped by design (ucode is recompiled), not a shape defect
    std::lock_guard<std::mutex> lk(g_mu);
    const int d = dir ? 1 : 0;
    g_tot[d][aud]++;
    if (vmask) g_viol[d][aud]++;
    for (int k = 0; k < F_N; k++) if (f & (1u << k)) g_fl[d][aud][k]++;
    const uint32_t m = mem & 0x1FFF, d7 = dram & 7;
    uint32_t i = 0;
    for (; i < g_nsh; i++) { const Shape& s = g_sh[i]; if (s.dir == (uint32_t)d && s.aud == aud && s.mem == m && s.len == raw && s.d7 == d7) break; }
    if (i < g_nsh) g_sh[i].n++;
    else if (g_nsh < 512) g_sh[g_nsh++] = Shape{(uint32_t)d, aud, m, raw, d7, f, 1, dram};
    else g_over++;
    const time_t now = time(nullptr);
    if (now - g_last >= 5) { g_last = now; dump_locked(); }
}
