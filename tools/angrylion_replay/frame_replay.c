// s6895 G5b: replay swaps from a ROGUESQ_G5B_FRAME capture through angrylion-plus's RDP core and write the colour image.
// usage: frame_replay cap.bin outdir swap [swap...]    (sorted ascending). For each swap: uses the newest 'RAM ' snapshot at or
// before it, runs that swap's ranges, writes outdir/f<swap>.rgb (w h u32 then RGB8) for the widest 16-bit colour image.
// KILL_AREA=<px>: zero tris whose rough area exceeds it. Positive control: the colour image is pre-filled magenta, "painted" counts pixels the replay changed.
// Build: D=~/Documents/Tools/g3_angrylion; clang -O1 -I$D/src/src/core -I$D/src/src tools/angrylion_replay/frame_replay.c $D/build/libalp-core.a -lc++ -o frame_replay
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include "n64video.h"
#define RAM 0x1000000u
void msg_error(const char *f,...){} void msg_warning(const char *f,...){}
static uint8_t *rdram, *snap; static uint32_t dpr[DP_NUM_REG], vir[VI_NUM_REG], mi;
static uint32_t *dpp[DP_NUM_REG], *vip[VI_NUM_REG]; static uint8_t dmem[0x2000];
static void intr(void) {}
static uint32_t rw(const uint8_t *b, uint32_t a) { uint32_t v; memcpy(&v, b + a, 4); return v; }
int main(int ac, char **av) {
    if (ac < 4) return 1;
    FILE *f = fopen(av[1], "rb"); if (!f) return 1;
    rdram = calloc(1, RAM); snap = calloc(1, RAM);
    for (int i = 0; i < DP_NUM_REG; i++) dpp[i] = &dpr[i];
    for (int i = 0; i < VI_NUM_REG; i++) vip[i] = &vir[i];
    struct n64video_config c; n64video_config_init(&c);
    c.gfx.rdram = rdram; c.gfx.rdram_size = RAM; c.gfx.dmem = dmem; c.gfx.vi_reg = vip; c.gfx.dp_reg = dpp;
    c.gfx.mi_intr_reg = &mi; c.gfx.mi_intr_cb = intr; c.parallel = false; c.num_workers = 1;
    n64video_init(&c);
    long killA = getenv("KILL_AREA") ? atol(getenv("KILL_AREA")) : 0, killed = 0;
    int wi = 3, want = atoi(av[wi]); uint32_t tag, sw = 0; uint64_t t; int have = 0, active = 0; uint32_t cimg = 0, cw = 0; long nr = 0;
    static char ibuf[1 << 22]; setvbuf(f, ibuf, _IOFBF, sizeof ibuf);
    uint8_t *cmd = malloc(0x200000);
    for (;;) {
        int eof = fread(&tag, 4, 1, f) != 1;
        if (eof || tag == 0x50415753u) {
            if (active) { // finish the frame
                int h = 448; uint32_t *px = malloc(4); free(px);
                char p[512]; snprintf(p, sizeof p, "%s/f%d.rgb", av[2], want); FILE *o = fopen(p, "wb");
                uint32_t hdr[2] = {cw, (uint32_t)h}; fwrite(hdr, 4, 2, o); long lit = 0;
                for (int y = 0; y < h; y++) for (uint32_t x = 0; x < cw; x++) {
                    uint32_t a = (cimg + 2 * (y * cw + x)) ^ 2; uint16_t v = (uint16_t)(rdram[a] | (rdram[a + 1] << 8));
                    uint8_t q[3] = {(uint8_t)((v >> 11 & 31) << 3), (uint8_t)((v >> 6 & 31) << 3), (uint8_t)((v >> 1 & 31) << 3)};
                    if (v != 0xF83Eu) lit++; fwrite(q, 1, 3, o); }
                fclose(o); printf("swap %d ranges %ld cimg %06X w %u painted %ld of %u killed %ld\n", want, nr, cimg, cw, lit, cw * h, killed); killed = 0; fflush(stdout);
                active = 0; if (++wi >= ac) break; want = atoi(av[wi]);
            }
            if (eof) break;
            if (fread(&t, 8, 1, f) != 1 || fread(&sw, 4, 1, f) != 1) break;
            if ((int)sw == want) { if (!have) { fprintf(stderr, "no snapshot before %d\n", want); return 2; }
                memcpy(rdram, snap, RAM); active = 1; nr = 0; cimg = 0; cw = 0; }
            else if ((int)sw > want) { fprintf(stderr, "swap %d absent\n", want); if (++wi >= ac) break; want = atoi(av[wi]); }
            continue;
        }
        if (tag == 0x204D4152u) { if (fread(snap, 1, RAM, f) != RAM) break; have = 1; if (active) { /* keep frame's own view */ } else if ((int)sw == want) { memcpy(rdram, snap, RAM); active = 1; nr = 0; cimg = 0; cw = 0; } continue; }
        if (tag != 0x20474E52u) { fprintf(stderr, "bad tag %08X\n", tag); return 3; }
        uint32_t lo, n; if (fread(&lo, 4, 1, f) != 1 || fread(&n, 4, 1, f) != 1) break;
        if (n > 0x200000) { fseek(f, n, SEEK_CUR); continue; }
        if (fread(cmd, 1, n, f) != n) break;
        if (!active) continue;
        for (uint32_t a = 0; a + 8 <= n;) { uint32_t w0 = rw(cmd, a), w1 = rw(cmd, a + 4), op = (w0 >> 24) & 0x3F, l = 8;
            if (op >= 8 && op <= 15) l = 32 + ((op & 4) ? 64 : 0) + ((op & 2) ? 64 : 0) + ((op & 1) ? 16 : 0); else if (op == 0x24 || op == 0x25) l = 16;
            else if (op == 0x3F) { uint32_t w = (w0 & 0x3FF) + 1; if (w >= cw && ((w0 >> 19) & 3) == 2) { cw = w; if (cimg != (w1 & 0xFFFFFF)) { cimg = w1 & 0xFFFFFF; for (uint32_t i = 0; i < w * 448; i++) { uint32_t q = (cimg + 2 * i) ^ 2; rdram[q] = 0x3E; rdram[q + 1] = 0xF8; } } } }
            if (killA > 0 && op >= 8 && op <= 15 && a + l <= n) { // zero a big terrain tri: NOPs in its place
                int32_t xl = (int32_t)rw(cmd, a + 8) >> 16, xh = (int32_t)rw(cmd, a + 16) >> 16, xm = (int32_t)rw(cmd, a + 24) >> 16;
                int yl = ((int32_t)(w0 << 18) >> 18) / 4, yh = ((int32_t)(w1 << 18) >> 18) / 4; int wd = abs(xh - xl) > abs(xh - xm) ? abs(xh - xl) : abs(xh - xm);
                if ((long)wd * (yl - yh) / 2 > killA) { memset(cmd + a, 0, l); killed++; } }
            a += l; }
        memcpy(rdram + lo, cmd, n); // DP addresses are 24-bit: commands must sit below 16 MB, so run them where the game put them
        dpr[DP_STATUS] = 0; dpr[DP_CURRENT] = lo; dpr[DP_START] = lo; dpr[DP_END] = lo + n;
        n64video_process_list(); nr++;
    }
    return 0;
}
