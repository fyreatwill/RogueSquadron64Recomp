// s7752: render one gfx task's RDP stream (plain big-endian bytes: a ROGUESQ_S7751_SNAP tail, tools/s7752_port_task/harness
// output, or tools/s7751_cxd4_task/replay output) through angrylion-plus on top of that task's snapshot RDRAM, and write the
// whole resulting 16 MB RDRAM so two streams of the same task can be pixel-diffed (tools/s7752_render_diff.py).
// usage: rdp_render <snap.bin> <stream.rdp> <out.ram>    Commands run in <=32 KB whole-command chunks staged at 0xFF0000.
// Build: zsh tools/s7752_port_task/build.sh (links the 16 MB core that tools/angrylion_replay/build16.sh makes).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include "n64video.h"
#define RAM 0x1000000u
#define STAGE 0xFF0000u
void msg_error(const char *f,...){} void msg_warning(const char *f,...){}
static uint8_t *rdram; static uint32_t dpr[DP_NUM_REG], vir[VI_NUM_REG], mi;
static uint32_t *dpp[DP_NUM_REG], *vip[VI_NUM_REG]; static uint8_t dmem[0x2000];
static void intr(void) {}
static uint32_t be(const uint8_t *b) { return (uint32_t)b[0] << 24 | (uint32_t)b[1] << 16 | (uint32_t)b[2] << 8 | b[3]; }
static void run(const uint8_t *s, uint32_t n) {
    for (uint32_t i = 0; i < n; i += 4) { uint32_t w = be(s + i); memcpy(rdram + STAGE + i, &w, 4); }
    dpr[DP_STATUS] = 0; dpr[DP_CURRENT] = STAGE; dpr[DP_START] = STAGE; dpr[DP_END] = STAGE + n;
    n64video_process_list();
}
int main(int ac, char **av) {
    if (ac < 4) { fprintf(stderr, "usage: rdp_render snap.bin stream.rdp out.ram\n"); return 2; }
    FILE *f = fopen(av[1], "rb"); if (!f) return 2;
    uint32_t hdr[5]; if (fread(hdr, 4, 5, f) != 5 || hdr[0] != 0x31353753u || hdr[4] != RAM) { fprintf(stderr, "bad snap\n"); return 2; }
    rdram = calloc(1, RAM); fseek(f, 4096, SEEK_CUR); if (fread(rdram, 1, RAM, f) != RAM) return 2; fclose(f);
    f = fopen(av[2], "rb"); if (!f) return 2; fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    uint8_t *s = malloc(n); if (fread(s, 1, n, f) != (size_t)n) return 2; fclose(f);
    if (strstr(av[2], ".bin")) { /* snap: stream is the tail */ uint32_t nb; memcpy(&nb, s + 20 + 4096 + RAM, 4); memmove(s, s + 24 + 4096 + RAM, nb); n = nb; }
    for (int i = 0; i < DP_NUM_REG; i++) dpp[i] = &dpr[i];
    for (int i = 0; i < VI_NUM_REG; i++) vip[i] = &vir[i];
    struct n64video_config c; n64video_config_init(&c);
    c.gfx.rdram = rdram; c.gfx.rdram_size = RAM; c.gfx.dmem = dmem; c.gfx.vi_reg = vip; c.gfx.dp_reg = dpp;
    c.gfx.mi_intr_reg = &mi; c.gfx.mi_intr_cb = intr; c.parallel = false; c.num_workers = 1;
    n64video_init(&c);
    uint32_t a = 0, start = 0, cmds = 0, high = 0;
    while (a + 8 <= (uint32_t)n) {
        uint32_t w0 = be(s + a), w1 = be(s + a + 4), op = (w0 >> 24) & 0x3F, l = 8;
        if (op >= 8 && op <= 15) l = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0); else if (op == 0x24 || op == 0x25) l = 16;
        if ((op == 0x3F || op == 0x3E || op == 0x3D) && (w1 & 0xFFFFFF) >= STAGE - 0x100000) high++;
        if (a + l - start > 0x8000) { run(s + start, a - start); start = a; }
        a += l; cmds++;
    }
    if (a > start) run(s + start, a - start);
    f = fopen(av[3], "wb"); fwrite(rdram, 1, RAM, f); fclose(f);
    printf("rdp_render cmds=%u bytes=%ld images_near_stage=%u\n", cmds, n, high);
    return high ? 3 : 0;
}
