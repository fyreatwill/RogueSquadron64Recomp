// s7752: replay the PORT's own fixed-up gfx ucode (factor5_ucode_lean, the TU the live game runs) offline on a
// ROGUESQ_S7751_SNAP task snapshot, capturing the raw RDP bytes the ucode hands rsp_dpc_submit with the same windowing
// as src/rsp/s7751_task_snap.cpp. Same inputs as tools/s7751_cxd4_task/replay, so the three-way compare
//   live port stream (snap tail) / offline port replay / offline cxd4 replay
// splits H-snapshot (live != offline port, offline port == cxd4) from a real port divergence (live == offline port != cxd4).
// Env knobs mirror the live ones: ROGUESQ_G5B_TG_FIX=0|1 (default 1 = live dd>1 policy), ROGUESQ_UCODE_CAP.
// usage: harness <snap.bin> <out.rdp>   exit 0 ok, 2 usage/io
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <atomic>

enum class RspExitReason { Invalid, Broke, ImemOverrun, UnhandledJumpTarget, Unsupported, SwapOverlay, UnhandledResumeTarget };
extern RspExitReason factor5_ucode_lean(uint8_t* rdram, uint32_t ucode_addr);

uint8_t dmem[0x1000];
uint8_t dmem_audio[0x1000];
uint16_t rspReciprocals[512];
uint32_t g_rsp_dpc_start, g_rsp_dpc_end, g_rsp_dpc_current;
const uint8_t* g_rsp_dma_shadow2_data = nullptr; uint32_t g_rsp_dma_shadow2_addr = 0, g_rsp_dma_shadow2_size = 0;
uint32_t g_rsp_last_chunk_dram, g_rsp_last_chunk_dmem, g_rsp_last_chunk_len;

static std::vector<uint8_t> g_out;
static uint32_t g_base = 0xFFFFFFFFu, g_last = 0, g_submits = 0;
static constexpr uint32_t kRam = 0x01000000u;
void rsp_dpc_submit(uint8_t* rdram, uint32_t start, uint32_t end) {
    g_submits++;
    const uint32_t sp = start & 0x00FFFFFFu, ep = end & 0x00FFFFFFu;
    if (ep <= sp || ep > kRam) return;
    uint32_t from = (sp != g_base) ? sp : g_last;
    if (sp != g_base) g_base = sp;
    if (from < sp || from > ep) from = sp;
    for (uint32_t a = from; a < ep; a++) g_out.push_back(rdram[a ^ 3u]);
    g_last = ep;
}
static uint32_t s_last = 0xFFFFFFFFu; static int s_rep = 0;
uint32_t rs64_dpc_current_read() {  // dpc_bridge.cpp default path (s7523/s7521/s7095 off)
    uint32_t v = g_rsp_dpc_current;
    if (v == s_last) { if (++s_rep >= 64) { s_rep = 0; return v + 8; } } else { s_last = v; s_rep = 0; }
    return v;
}

extern "C" {
volatile uint32_t g_rs64_last_guest_pc;
int rs64_e9prov_force = 0, rs64_g1e_dmem = 1, rs64_g1e_fast = 1, rs64_g5b_tg_on = 0, rs64_s7094_on = 0, rs64_s7095_on = 0,
    rs64_s7096_on = 0, rs64_s7106_on = 0, rs64_s7112_on = 0, rs64_s7521_on = 0, rs64_s7523_on = 0, rs64_s7535_on = 0;
int rs64_g5b_tg_fix = 1;
uint64_t rs64_g1e_ucode_iters = 0;
volatile uint32_t rs64_ucode_cap_fires_g = 0;
uint64_t g_tg_hits = 0;
// copy of src/rsp/dpc_bridge.cpp rs64_g5b_tg_edge, modes 0/1 only (no REACH lever, no parity toggle)
int rs64_g5b_tg_edge(uint32_t w0, uint32_t* p8, uint32_t* p9) {
    if (((w0 >> 8) & 0xFF) != 2) return 0;
    const int v0 = (int)(*p9 & 0xFFFF), a = (int16_t)(*p8 >> 16), b = (int16_t)(*p9 >> 16);
    int hit = 0;
    if (a + v0 > 32767) { *p8 = (*p8 & 0xFFFFu) | ((uint32_t)(uint16_t)(32767 - v0) << 16); hit = 1; }
    if (b + v0 > 32767) { *p9 = (*p9 & 0xFFFFu) | ((uint32_t)(uint16_t)(32767 - v0) << 16); hit = 1; }
    g_tg_hits += hit;
    return hit;
}
uint32_t rs64_m4_y8000_step(uint32_t) { return 0; }
uint32_t rs64_s7523_end_read() { return g_rsp_dpc_end; }
uint32_t rs64_s7523_status_read() { return 0; }
#define V(n) void n() {}
V(rs64_e9prov_1364_jump) V(rs64_e9prov_clip_1e48_ra) V(rs64_e9prov_frame_pop) V(rs64_e9prov_frame_push) V(rs64_e9prov_frame_resume)
V(rs64_e9prov_guest) V(rs64_e9prov_l1298_12a0_res) V(rs64_e9prov_l12a0_source) V(rs64_e9prov_l1db0_predecessor) V(rs64_e9prov_l1db0_reset)
V(rs64_e9prov_ovl24_jal17f0) V(rs64_e9prov_ovl_route) V(rs64_e9prov_source_end) V(rs64_e9prov_unwind) V(rs64_f5_host_bulk_payload)
V(rs64_f5_host_write_begin) V(rs64_g1d_blk_dma) V(rs64_g1e_cpu_sample) V(rs64_g5b_trigen) V(rs64_m5_audio_dmem_dma_write)
V(rs64_m5_audio_input_dma) V(rs64_m5_audio_source_dma) V(rs64_m5_exact_route_dma_write) V(rs64_m5_host_write_census)
V(rs64_m5_source_range_dma_write) V(rs64_note_imem_overrun) V(rs64_probe_audio_dma_write) V(rs64_probe_dma_write_origin) V(rs64_s4209_read)
V(rs64_s4239_dma) V(rs64_s7094_dma_shape) V(rs64_s7095_end) V(rs64_s7095_end_read) V(rs64_s7095_start) V(rs64_s7095_status_read)
V(rs64_s7095_status_write) V(rs64_s7096_end) V(rs64_s7096_start) V(rs64_s7106_fetch) V(rs64_s7106_flush) V(rs64_s7112_tri)
V(rs64_s7521_imem) V(rs64_s7522_disp) V(rs64_s7522_ovl28) V(rs64_s7523_end) V(rs64_s7523_pre_submit) V(rs64_s7523_start)
V(rs64_s7535_dma) V(rs64_s7535_wr) V(rsp_task_log_and_reset)
}

static void init_recip() {  // lib/N64ModernRuntime/librecomp/src/rsp.cpp
    rspReciprocals[0] = (uint16_t)~0;
    for (uint16_t index = 1; index < 512; index++) {
        uint64_t a = index + 512;
        uint64_t b = ((uint64_t)1 << 34) / a;
        rspReciprocals[index] = (uint16_t)((b + 1) >> 8);
    }
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s <snap.bin> <out.rdp>\n", argv[0]); return 2; }
    if (const char* e = getenv("ROGUESQ_G5B_TG_FIX"); e && *e) rs64_g5b_tg_fix = *e != '0';
    if (const char* e = getenv("S7752_G1E_FAST"); e && *e) rs64_g1e_fast = *e != '0';
    FILE* f = fopen(argv[1], "rb"); if (!f) { perror(argv[1]); return 2; }
    uint32_t hdr[5]; if (fread(hdr, 4, 5, f) != 5 || hdr[0] != 0x31353753u) { fprintf(stderr, "bad header\n"); return 2; }
    const uint32_t ram = hdr[4];
    std::vector<uint8_t> rdram(0x02000000u, 0);  // 32 MB: masked DMA reach + slack
    if (fread(dmem, 1, 4096, f) != 4096 || fread(rdram.data(), 1, ram, f) != ram) { fprintf(stderr, "short read\n"); return 2; }
    fclose(f);
    init_recip();
    const uint32_t ucode_addr = ((uint32_t)dmem[0xFD0 ^ 3] << 24) | ((uint32_t)dmem[0xFD1 ^ 3] << 16) | ((uint32_t)dmem[0xFD2 ^ 3] << 8) | dmem[0xFD3 ^ 3];
    RspExitReason r = factor5_ucode_lean(rdram.data(), ucode_addr);
    FILE* o = fopen(argv[2], "wb"); if (!o) { perror(argv[2]); return 2; }
    fwrite(g_out.data(), 1, g_out.size(), o); fclose(o);
    fprintf(stderr, "[s7752] serial=%u ucode=0x%08X exit=%d submits=%u rdp_bytes=%zu tg_fix=%d tg_hits=%llu cap_fires=%u\n", hdr[2], ucode_addr,
            (int)r, g_submits, g_out.size(), rs64_g5b_tg_fix, (unsigned long long)g_tg_hits, rs64_ucode_cap_fires_g);
    return 0;
}
