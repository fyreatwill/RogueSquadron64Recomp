/* s7900: tools/s7751_cxd4_task/replay.c plus an SP DMA read log. Each RDRAM->SP DMA appends one text line
 *   dma <rdp_bytes_out_so_far> <dram_addr> <sp_addr> <rd_len_reg>
 * to $S7900_DMA_LOG (default /dev/stderr), so every RDP output byte range can be tied to the RDRAM fetched before it.
 * Optional $S7900_POKE="addr:hexword[,addr:hexword]" overwrites big-endian guest words in RDRAM before the boot (the nudge control).
 * build: zsh tools/s7900_dma_trace/run.sh  (patches a copy of cxd4 su.c; the include path picks that copy's lto.c) */
#include <stdio.h>
#include <stdlib.h>
static FILE* g_dmalog; static unsigned long* g_bytes_p;
void s7900_dma_hook(unsigned int dram, unsigned int sp, unsigned int len) {
    if (!g_dmalog) { const char* p = getenv("S7900_DMA_LOG"); g_dmalog = p ? fopen(p, "w") : stderr; }
    fprintf(g_dmalog, "dma %lu %06X %04X %08X\n", g_bytes_p ? *g_bytes_p : 0ul, dram & 0xFFFFFFu, sp & 0x1FFFu, len);
}
#define main s7751_main
#include "../s7751_cxd4_task/replay.c"
#undef main
/* replay.c reads the snapshot into g_ram inside its main; apply pokes by hooking InitiateRSP order: we poke the snapshot file copy instead. */
int main(int argc, char** argv) {
    g_bytes_p = &g_bytes;
    const char* pk = getenv("S7900_POKE");
    if (pk && *pk && argc >= 3) {   /* write a patched copy of the snapshot and replay that */
        FILE* f = fopen(argv[1], "rb"); if (!f) { perror(argv[1]); return 2; }
        fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
        unsigned char* b = malloc(n); if (fread(b, 1, n, f) != (size_t)n) return 2; fclose(f);
        const unsigned int hdr_ram = 20 + 4096;   /* header 5 words, DMEM 4 KB, then RDRAM (host word-native, ^3 byte layout) */
        char* s = strdup(pk); for (char* t = strtok(s, ","); t; t = strtok(NULL, ",")) {
            unsigned int a, v; if (sscanf(t, "%x:%x", &a, &v) != 2) continue; a &= 0xFFFFFCu;
            *(unsigned int*)(b + hdr_ram + a) = v; fprintf(stderr, "[s7900] poke %06X = %08X\n", a, v);
        }
        static char tmp[512]; snprintf(tmp, sizeof tmp, "%s.poke.bin", argv[2]);
        FILE* o = fopen(tmp, "wb"); fwrite(b, 1, n, o); fclose(o); free(b); argv[1] = tmp;
    }
    return s7751_main(argc, argv);
}
