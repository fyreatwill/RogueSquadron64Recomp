/* s7751: replay one captured gfx task (src/rsp/s7751_task_snap.cpp, ROGUESQ_S7751_SNAP) through the independent
 * cxd4 RSP interpreter (scalar C build, ~/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4, compiled in via lto.c)
 * and write the RDP command bytes it hands the DPC, in the same plain big-endian format as the port's capture.
 * The boot is the hardware one: osSpTaskLoad's _VirtualToPhysicalTask on the OSTask, the task at DMEM 0xFC0,
 * rspboot (OSTask.ucode_boot) DMA'd to IMEM 0, PC = 0; rspboot then loads the ucode text/data itself.
 * The RDP is modelled as instant (DPC_CURRENT = DPC_END after every list), like the port's bridge.
 * usage: replay <snap.bin> <out_rdp.bin>     build: zsh tools/s7751_cxd4_task/run.sh */
#define _DARWIN_C_SOURCE 1
#include <sys/mman.h>
#include "lto.c"
#ifndef MAP_ANON
#define MAP_ANON 0x1000
#endif

static unsigned int r_mi, r_spmem, r_spdram, r_rd, r_wr, r_spst, r_full, r_busy, r_pc, r_sem;
static unsigned int r_dst, r_dend, r_dcur, r_dstat, r_clk, r_bb, r_pb, r_tmem;
static unsigned char* g_ram; static unsigned char g_spmem[0x2000];
static FILE* g_out; static unsigned long g_lists, g_bytes;

static void on_alarm(int sig) {
    (void)sig;
    fprintf(stderr, "[s7751r-alarm] lists=%lu bytes=%lu dpc start=%08X cur=%08X end=%08X status=%08X sp_status=%08X sem=%08X spdram=%08X spmem=%08X sp_pc=%08X\n",
            g_lists, g_bytes, r_dst, r_dcur, r_dend, r_dstat, r_spst, r_sem, r_spdram, r_spmem, r_pc);
    fflush(g_out); alarm(5);
}
static void cb_none(void) {}
static void cb_rdp(void) {
    unsigned int a = r_dcur & 0x00FFFFF8u, e = r_dend & 0x00FFFFF8u;
    const int xbus = (r_dstat & 1u) != 0;
    if (e > a) {
        for (unsigned int i = a; i < e; i++) {
            unsigned char b = xbus ? g_spmem[(i & 0xFFFu) ^ 3u] : g_ram[i ^ 3u];
            fputc(b, g_out);
        }
        g_bytes += e - a; g_lists++;
    }
    r_dcur = r_dend;
}
static m64p_error stub_cmd(m64p_command c, int p, void* d) { (void)c; if (d && p > 0) memset(d, 0, (size_t)p); return M64ERR_SUCCESS; }
static int stub_bool(m64p_handle h, const char* n) { (void)h; (void)n; return 0; }

static unsigned int rd32(const unsigned char* m, unsigned int a) { return *(const unsigned int*)(m + (a & ~3u)); }

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s snap.bin out_rdp.bin\n", argv[0]); return 2; }
    FILE* f = fopen(argv[1], "rb"); if (!f) { perror(argv[1]); return 2; }
    unsigned int hdr[5]; if (fread(hdr, 4, 5, f) != 5 || hdr[0] != 0x31353753u) { fprintf(stderr, "bad header\n"); return 2; }
    const unsigned int ram_size = hdr[4];
    /* 16 MB + an unmapped guard so InitiateRSP's SIGSEGV probe finds the top (su_max_address). */
    unsigned char* base = mmap(NULL, ram_size + 0x10000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
    mprotect(base + ram_size, 0x10000, PROT_NONE);
    g_ram = base;
    unsigned char snap_dmem[4096];
    if (fread(snap_dmem, 1, 4096, f) != 4096 || fread(g_ram, 1, ram_size, f) != ram_size) { fprintf(stderr, "short read\n"); return 2; }
    fclose(f);

    /* OSTask (16 words) as the runner left it at DMEM 0xFC0; apply osVirtualToPhysical to the pointer fields. */
    unsigned int t[16];
    for (int i = 0; i < 16; i++) t[i] = rd32(snap_dmem, 0xFC0u + 4u * i);
    static const int ptr_idx[] = {2, 4, 6, 8, 10, 11, 12, 14};
    for (unsigned k = 0; k < sizeof ptr_idx / sizeof ptr_idx[0]; k++) { unsigned int* v = &t[ptr_idx[k]]; if (*v) *v &= 0x1FFFFFFFu; }
    fprintf(stderr, "[s7751r] serial=%u vi=%u type=%u flags=%X boot=%06X/%X ucode=%06X/%X udata=%06X/%X stack=%06X/%X out=%06X..%06X data=%06X/%X yield=%06X/%X\n",
            hdr[2], hdr[3], t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9], t[10], t[11], t[12], t[13], t[14], t[15]);
    if (t[0] != 1 || !t[2] || !t[3] || t[3] > 0x1000) { fprintf(stderr, "not a bootable gfx task\n"); return 3; }

    memset(g_spmem, 0, sizeof g_spmem);
    for (int i = 0; i < 16; i++) *(unsigned int*)(g_spmem + 0xFC0 + 4 * i) = t[i];
    memcpy(g_spmem + 0x1000, g_ram + t[2], t[3]);   /* rspboot -> IMEM 0 (word-native copy, both sides ^3 layout) */
    r_spst = 0; r_pc = 0x000; r_dstat = 0; r_dst = r_dend = r_dcur = 0;

    RSP_INFO ri; memset(&ri, 0, sizeof ri);
    ri.RDRAM = g_ram; ri.DMEM = g_spmem; ri.IMEM = g_spmem + 0x1000;
    ri.MI_INTR_REG = &r_mi; ri.SP_MEM_ADDR_REG = &r_spmem; ri.SP_DRAM_ADDR_REG = &r_spdram; ri.SP_RD_LEN_REG = &r_rd;
    ri.SP_WR_LEN_REG = &r_wr; ri.SP_STATUS_REG = &r_spst; ri.SP_DMA_FULL_REG = &r_full; ri.SP_DMA_BUSY_REG = &r_busy;
    ri.SP_PC_REG = &r_pc; ri.SP_SEMAPHORE_REG = &r_sem; ri.DPC_START_REG = &r_dst; ri.DPC_END_REG = &r_dend;
    ri.DPC_CURRENT_REG = &r_dcur; ri.DPC_STATUS_REG = &r_dstat; ri.DPC_CLOCK_REG = &r_clk; ri.DPC_BUFBUSY_REG = &r_bb;
    ri.DPC_PIPEBUSY_REG = &r_pb; ri.DPC_TMEM_REG = &r_tmem;
    ri.CheckInterrupts = cb_none; ri.ProcessDlistList = cb_none; ri.ProcessAlistList = cb_none; ri.ProcessRdpList = cb_rdp; ri.ShowCFB = cb_none;
    CoreDoCommand = stub_cmd; ConfigGetParamBool = stub_bool;   /* CFG_HLE_GFX = 0: run the real F5 ucode, LLE */
    g_out = fopen(argv[2], "wb"); if (!g_out) { perror(argv[2]); return 2; }
    unsigned int cyc = 0;
    signal(SIGALRM, on_alarm); alarm(5);
    /* macOS raises SIGBUS (not SIGSEGV) on the PROT_NONE guard; cxd4's size probe only traps SIGSEGV. */
    struct sigaction sb = {.sa_handler = seg_av_handler}, sb_prev; sigaction(SIGBUS, &sb, &sb_prev);
    InitiateRSP(ri, &cyc);
    sigaction(SIGBUS, &sb_prev, NULL);
    fprintf(stderr, "[s7751r] su_max_address=0x%lX\n", su_max_address);
    int runs = 0;
    for (; runs < 2000000; runs++) {         /* resume on a non-BREAK exit (semaphore/timeout), like the core's re-kick */
        DoRspCycles(0x7FFFFFFF);
        if (r_spst & SP_STATUS_BROKE) break;
        r_spst &= ~1u;
    }
    fclose(g_out);
    fprintf(stderr, "[s7751r] done runs=%d sp_status=%08X pc=%03X rdp_lists=%lu rdp_bytes=%lu\n", runs + 1, r_spst, r_pc, g_lists, g_bytes);
    return (r_spst & SP_STATUS_BROKE) ? 0 : 4;
}
