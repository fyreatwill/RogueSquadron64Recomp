// s7094: RSP DMA runtime model vs cxd4. Both memories keep each 32-bit word byte-reversed (byte a at a^3), so raw arrays
// compare directly. Classes: CANON = the shape every RS64 ucode site is supposed to use (mem&7==0, raw&7==7, raw<0x1000,
// fits the 4 KB bank, DRAM < 8 MB); then each hardware feature the runtime does not model, one at a time.
// Exit 0 iff CANON (fast + slow, read + write) has 0 diffs; per-class diff rates are printed for the census to map.
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <cstdlib>
// ---------- runtime side (live rsp.hpp text, hooks stubbed) ----------
static uint8_t g_dm[0x2000], g_rd[0x1000000];
#define RS64_DMEM_BASE g_dm
#include "rspmemb.inc"
#define MEM_B(offset, reg) (*(int8_t*)(rdram + ((((reg) + (offset)) ^ 3) - 0xFFFFFFFF80000000)))
static int rs64_g1e_fast = 0, rs64_s7094_on = 0; static uint8_t dmem_audio[1];
static uint32_t g_rsp_last_chunk_dram, g_rsp_last_chunk_dmem, g_rsp_last_chunk_len, g_rs64_last_guest_pc;
static const uint8_t* g_rsp_dma_shadow2_data = nullptr; static uint32_t g_rsp_dma_shadow2_addr, g_rsp_dma_shadow2_size;
static uint64_t g_s4248_dma_rd_bytes, g_s4248_dma_rd_calls, g_s4248_dma_wr_bytes, g_s4248_dma_wr_calls;
#define NOP(...) ((void)0)
#define rs64_s7094_dma_shape NOP
#define rs64_m5_audio_input_dma NOP
#define rs64_m5_audio_dmem_dma_write NOP
#define rs64_m5_audio_source_dma NOP
#define rs64_s4209_read NOP
#define rs64_s4239_dma NOP
#define rs64_f5_host_write_begin NOP
#define rs64_probe_dma_write_origin NOP
#define rs64_g1d_blk_dma NOP
#define rs64_m5_host_write_census NOP
#define rs64_f5_host_bulk_payload NOP
#define rs64_m5_exact_route_dma_write NOP
#define rs64_m5_source_range_dma_write NOP
#define rs64_probe_audio_dma_write NOP
#include "rt_dma.inc"
// ---------- cxd4 side (su.c verbatim) ----------
typedef uint32_t u32; typedef u32* pu32;
static uint8_t c_dm[0x2000], c_rd[0x1000000];
#define DMEM c_dm
#define DRAM c_rd
static unsigned long su_max_address = 0x007FFFFFul;
static u32 SR[32]; static u32 c_cr[16]; static pu32 CR[16];
// cxd4 CR[n] points at SP register n (0 MEM_ADDR, 1 DRAM_ADDR, 2 RD_LEN, 3 WR_LEN, 4 STATUS, 6 DMA_BUSY), and
// GET_RCP_REG reads the same registers, so both alias c_cr here.
enum { SP_RD_LEN_REG = 2, SP_WR_LEN_REG = 3, SP_STATUS_REG = 4, SP_DMA_BUSY_REG = 6 };
#define GET_RCP_REG(r) c_cr[r]
#define SP_STATUS_DMA_BUSY 4
void SP_DMA_READ(void); void SP_DMA_WRITE(void);
#include "cx_mt.inc"
#define register
#include "cx_dma.inc"
#undef register
// ---------- driver ----------
static uint64_t rs = 0x9E3779B97F4A7C15ull;
static uint64_t rnd() { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
enum { CANON, MEM7, LEN7, COUNT, SKIPC, WRAP, DRAM7, NCLS };
static const char* kCls[NCLS] = {"CANON", "mem_lo3", "len_not7", "count+skip", "skip_only", "dmem_wrap", "dram_lo3"};
static void gen(int cls, uint32_t& mem, uint32_t& dram, uint32_t& raw) {
    for (;;) {
        uint32_t len8 = 8 * (1 + rnd() % 64 + (rnd() % 4 == 0 ? rnd() % 448 : 0));
        mem = (rnd() & 0xFF8); dram = (rnd() & 0x7FFFF8); raw = len8 - 1;
        if (mem + len8 > 0x1000) mem = 0x1000 - len8;
        if (dram + len8 > 0x800000) dram = 0x800000 - len8;
        switch (cls) {
            case MEM7: mem |= 1 + rnd() % 7; if (mem + len8 > 0x1000) continue; break;
            case LEN7: raw &= ~7u; raw |= rnd() % 7; break;
            case COUNT: { uint32_t c = 1 + rnd() % 3, sk = rnd() % 64; raw |= (c << 12) | (sk << 20);
                if (mem + (c + 1) * len8 > 0x1000 || dram + (c + 1) * (len8 + sk) > 0x800000) continue; break; }
            case SKIPC: raw |= (1 + rnd() % 64) << 20; break;
            case WRAP: mem = 0x1000 - 8 * (1 + rnd() % (len8 / 8)); if (len8 <= 8) continue; mem &= 0xFF8; if (mem + len8 <= 0x1000) continue; break;
            case DRAM7: dram |= 1 + rnd() % 7; break;
        }
        return;
    }
}
int main(int argc, char** argv) {
    for (int i = 0; i < 16; i++) CR[i] = &c_cr[i];
    const int N = 20000; long tot_bad = 0, canon_bad = 0, cmp = 0;
    for (int cls = 0; cls < NCLS; cls++) for (int dir = 0; dir < 2; dir++) for (int fast = 0; fast < 2; fast++) {
        long bad = 0;
        for (int it = 0; it < N; it++) {
            uint32_t mem, dram, raw; gen(cls, mem, dram, raw);
            for (int i = 0; i < 0x2000; i++) g_dm[i] = c_dm[i] = (uint8_t)rnd();
            // only randomise the DRAM window touched (+-4 KB) to keep it fast; rest stays as previous iteration (both equal)
            uint32_t lo = dram > 0x1000 ? dram - 0x1000 : 0, hi = dram + 0x9000 > 0x800000 ? 0x800000 : dram + 0x9000;
            for (uint32_t i = lo; i < hi; i++) g_rd[i] = c_rd[i] = (uint8_t)rnd();
            rs64_g1e_fast = fast;
            if (dir == 0) dma_rdram_to_dmem(g_rd, mem, dram, raw); else dma_dmem_to_rdram(g_rd, mem, dram, raw);
            SR[1] = mem; MT_DMA_CACHE(1); SR[2] = dram; MT_DMA_DRAM(2); SR[3] = raw;
            if (dir == 0) MT_DMA_READ_LENGTH(3); else MT_DMA_WRITE_LENGTH(3);
            bool diff = memcmp(g_dm, c_dm, 0x1000) != 0 || memcmp(g_rd + lo, c_rd + lo, hi - lo) != 0;
            cmp++; if (diff) bad++;
        }
        tot_bad += bad; if (cls == CANON) canon_bad += bad;
        printf("  %-11s %s %s  bad %6ld / %d\n", kCls[cls], dir ? "wr" : "rd", fast ? "fast" : "slow", bad, N);
    }
    printf("[s7094] compares %ld, CANON bad %ld, all-class bad %ld\n", cmp, canon_bad, tot_bad);
    return canon_bad ? 1 : 0;
}
