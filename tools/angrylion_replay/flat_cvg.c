// s6799 G3: do 1-subscanline ("flat", height <= 0.25 px) terrain triangles light pixels on real RDP hardware?
// usage: flat_cvg tris.txt   lines "F|C w0..w7" (hex, raw edge words from an RS64_RDP_BIN_PORT dump; F = flat, C = normal
// control). Each triangle is re-issued as op 0x08 (no shade/tex/z: exact edge words kept) over a sky-filled 512-wide
// RGBA16 image in three modes: FILL (does the edge walk emit any span?), the game's terrain mode (2-cycle, othermode
// 18AC00:C8112220 = alpha_cvg_sel, no AA, combiner -> PRIM) and the same mode with AA_EN set. Reports lit pixels and
// summed |delta| vs sky per class. Build: D=/Users/williambuckley/Documents/Tools/g3_angrylion;
// clang -O1 -I$D/src/src/core -I$D/src/src tools/angrylion_replay/flat_cvg.c $D/build/libalp-core.a -lc++ -o /tmp/flat_cvg
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include "n64video.h"
#define W 512
#define H 448
#define FB 0x100000
#define ZB 0x300000
#define SKY 0x7BDFu
void msg_error(const char *f,...){} void msg_warning(const char *f,...){}
static uint8_t *rdram; static uint32_t dpr[DP_NUM_REG], vir[VI_NUM_REG], mi;
static uint32_t *dpp[DP_NUM_REG], *vip[VI_NUM_REG]; static uint8_t dmem[0x2000];
static uint32_t cmd[512]; static int n;
static void put(uint32_t a, uint32_t b) { cmd[n++] = a; cmd[n++] = b; }
static void flush(void) {
    for (int i = 0; i < n; i++) ((uint32_t*)rdram)[0x1000 + i] = cmd[i];
    dpr[DP_STATUS] = 0; dpr[DP_CURRENT] = 0x4000; dpr[DP_START] = 0x4000; dpr[DP_END] = 0x4000 + 4*n;
    n64video_process_list(); n = 0;
}
static uint16_t px(int i) { uint8_t *p = rdram + FB + ((2*i) ^ 2); return (uint16_t)(p[0] | (p[1] << 8)); } // host-endian halfword swap
static void clear(void) { for (int i = 0; i < W*H; i++) { uint8_t *p = rdram + FB + ((2*i) ^ 2); p[0] = SKY & 0xFF; p[1] = SKY >> 8; } }
static void stats(int *lit, long *dsum) {
    *lit = 0; *dsum = 0;
    for (int i = 0; i < W*H; i++) { uint16_t v = px(i); if (v != SKY) { (*lit)++;
        int dr = abs((int)(v >> 11) - (int)(SKY >> 11)), dg = abs((int)((v >> 6) & 31) - (int)((SKY >> 6) & 31)), db = abs((int)((v >> 1) & 31) - (int)((SKY >> 1) & 31)); *dsum += dr + dg + db; } }
}
static int g_acc;
static void run(const uint32_t *w, int mode, int *lit, long *dsum) {
    if (!g_acc) clear();
    put(0xFF100000u | (W-1), FB); put(0xFE000000u, ZB);
    put(0xED000000u, ((uint32_t)W << 14) | ((uint32_t)H << 2));
    if (mode == 0) { put(0xEF000000u | (3u << 20), 0); put(0xF7000000u, 0x80018001u); }
    else {
        put(0xEF000000u | 0x18AC00u, mode == 2 ? (0xC8112220u | 8u) : 0xC8112220u);
        put(0xFC000000u | (15u<<20) | (31u<<15) | (7u<<12) | (7u<<9) | (15u<<5) | 31u,
            (15u<<28) | (15u<<24) | (7u<<21) | (7u<<18) | (3u<<15) | (7u<<12) | (3u<<9) | (0u<<6) | (7u<<3) | 0u);
        put(0xFA000000u, 0x804020FFu); put(0xF8000000u, 0x7090C0FFu);
    }
    put((w[0] & 0xC0FFFFFFu) | 0x08000000u, w[1]); put(w[2], w[3]); put(w[4], w[5]); put(w[6], w[7]);
    flush(); stats(lit, dsum);  // no FULL_SYNC: it raises the MI interrupt through a NULL callback
}
int main(int argc, char **argv) {
    rdram = calloc(1, 0x800000);
    for (int i = 0; i < DP_NUM_REG; i++) dpp[i] = &dpr[i];
    for (int i = 0; i < VI_NUM_REG; i++) vip[i] = &vir[i];
    struct n64video_config c; n64video_config_init(&c);
    c.gfx.rdram = rdram; c.gfx.rdram_size = 0x800000; c.gfx.dmem = dmem; c.gfx.vi_reg = vip; c.gfx.dp_reg = dpp;
    c.gfx.mi_intr_reg = &mi; c.gfx.mi_intr_cb = NULL; c.parallel = false; c.num_workers = 1;
    n64video_init(&c);
    // ACC=1: accumulate every F triangle of the file into one image in game mode, report lit px in the region
    // x0..x1,y0..y1 (env REG="x0,x1,y0,y1") and write rows y0-10..y1+10 as /tmp/flat_acc.pgm (lit = 255).
    if (getenv("ACC")) {
        int x0 = 0, x1 = W, y0 = 0, y1 = H; if (getenv("REG")) sscanf(getenv("REG"), "%d,%d,%d,%d", &x0, &x1, &y0, &y1);
        FILE *f = fopen(argv[1], "r"); char line[512]; int nt = 0; clear(); g_acc = 1;
        while (f && fgets(line, sizeof line, f)) { char k; uint32_t w[8]; int l; long d;
            if (sscanf(line, "%c %x %x %x %x %x %x %x %x", &k, &w[0],&w[1],&w[2],&w[3],&w[4],&w[5],&w[6],&w[7]) == 9 && k == 'F') { run(w, 1, &l, &d); nt++; } }
        int reg = 0, all = 0; for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) if (px(y*W + x) != SKY) { all++; if (x >= x0 && x < x1 && y >= y0 && y < y1) reg++; }
        printf("ACC flat tris=%d lit_px all=%d region(%d-%d,%d-%d)=%d\n", nt, all, x0, x1, y0, y1, reg);
        FILE *o = fopen("/tmp/flat_acc.pgm", "wb"); int ya = y0 - 10 < 0 ? 0 : y0 - 10, yb = y1 + 10 > H ? H : y1 + 10;
        fprintf(o, "P5 %d %d 255\n", W, yb - ya); for (int y = ya; y < yb; y++) for (int x = 0; x < W; x++) fputc(px(y*W + x) != SKY ? 255 : 0, o); fclose(o);
        return 0;
    }
    FILE *f = fopen(argv[1], "r"); char line[512];
    const char *mn[3] = {"fill", "game(cvg-alpha)", "game+AA"};
    int cnt[2] = {0}, anyl[2][3] = {{0}}; long lsum[2][3] = {{0}}, dsum[2][3] = {{0}};
    while (f && fgets(line, sizeof line, f)) {
        char k; uint32_t w[8];
        if (sscanf(line, "%c %x %x %x %x %x %x %x %x", &k, &w[0],&w[1],&w[2],&w[3],&w[4],&w[5],&w[6],&w[7]) != 9) continue;
        int ci = (k == 'F') ? 0 : 1; cnt[ci]++;
        for (int m = 0; m < 3; m++) { int l; long d; run(w, m, &l, &d); lsum[ci][m] += l; dsum[ci][m] += d; if (l) anyl[ci][m]++; }
    }
    for (int ci = 0; ci < 2; ci++) for (int m = 0; m < 3; m++)
        printf("%s n=%d mode=%-16s tris_lit=%d lit_px=%ld sum|d|=%ld mean|d|/px=%.2f\n", ci ? "CONTROL(normal)" : "FLAT", cnt[ci], mn[m],
               anyl[ci][m], lsum[ci][m], dsum[ci][m], lsum[ci][m] ? (double)dsum[ci][m] / lsum[ci][m] : 0.0);
    return 0;
}
