// G3c(b): replay logged [spike] RDP triangles through angrylion-plus's RDP core.
// usage: replay run.log   (reads "[spike] ..." lines produced by dpc_bridge.cpp, plus a built-in sane control)
// Encoding mirrors dpc_bridge.cpp:3416-3419: V = (xh,yh)(xm',ym)(xl,ym)(xl',yl)(xh',yl).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include "n64video.h"
#define W 320
#define H 240
void msg_error(const char *f,...){} void msg_warning(const char *f,...){}
static uint8_t *rdram; static uint32_t dpr[DP_NUM_REG], vir[VI_NUM_REG], mi;
static uint32_t *dpp[DP_NUM_REG], *vip[VI_NUM_REG]; static uint8_t dmem[0x2000];
static uint32_t cmd[256]; static int n;
static void put(uint32_t a, uint32_t b) { cmd[n++] = a; cmd[n++] = b; }
static void flush(void) {
    for (int i = 0; i < n; i++) ((uint32_t*)rdram)[0x1000 + i] = cmd[i]; // host-endian words, as mupen's rdram
    dpr[DP_STATUS] = 0; dpr[DP_CURRENT] = 0x4000; dpr[DP_START] = 0x4000; dpr[DP_END] = 0x4000 + 4*n;
    n64video_process_list(); n = 0;
}
static int32_t fx(double v) { return (int32_t)(v * 65536.0); }
static uint32_t y14(double y) { return ((int32_t)(y * 4.0)) & 0x3fff; }
static int lit(void) { // count pixels != 0 in 16bpp color image at 0x100000
    int c = 0; for (int i = 0; i < W*H; i++) { uint8_t *p = rdram + 0x100000 + 2*i; if (p[0]|p[1]) c++; } return c; }
static int tri(double xh,double yh,double xm,double ym,double xl,double yl,double dl,double dh,double dm,int lft) {
    memset(rdram + 0x100000, 0, W*H*2);
    put(0xFF100000u | (W-1), 0x100000);                 // SET_COLOR_IMAGE RGBA16 width W
    put(0xED000000u, (W<<14)|(H<<2));                   // SET_SCISSOR 0,0 .. W,H
    put(0xEF000000u | (3u<<20), 0x00000000);            // SET_OTHER_MODES cycle=FILL
    put(0xF7000000u, 0xFFFFFFFFu);                      // SET_FILL_COLOR white
    put(0x08000000u | (lft<<23) | y14(yl), (y14(ym)<<16) | y14(yh));
    put(fx(xl), fx(dl)); put(fx(xh), fx(dh)); put(fx(xm), fx(dm));
    flush(); return lit();
}
int main(int argc, char **argv) {
    rdram = calloc(1, 0x800000);
    for (int i = 0; i < DP_NUM_REG; i++) dpp[i] = &dpr[i];
    for (int i = 0; i < VI_NUM_REG; i++) vip[i] = &vir[i];
    struct n64video_config c; n64video_config_init(&c);
    c.gfx.rdram = rdram; c.gfx.rdram_size = 0x800000; c.gfx.dmem = dmem; c.gfx.vi_reg = vip; c.gfx.dp_reg = dpp;
    c.gfx.mi_intr_reg = &mi; c.gfx.mi_intr_cb = NULL; c.parallel = false; c.num_workers = 1;
    n64video_init(&c);
    // positive control: sane in-screen triangle (10,10),(100,10),(10,100): major edge H->L on right
    int ctl = tri(10,10, 10,10, 100,100, -1.0,0, 0, 1);
    printf("CONTROL sane tri lit=%d (model area 4050)\n", ctl);
    if (ctl < 3000) { puts("CONTROL FAILED"); return 2; }
    if (argc < 2) return 0;
    FILE *f = fopen(argv[1], "r"); char line[4096]; int tot = 0, seen = 0, vis = 0;
    while (f && fgets(line, sizeof line, f)) {
        int swap; char *v = strstr(line, "[spike] swap="); if (!v) continue;
        sscanf(v, "[spike] swap=%d", &swap);
        char *V = strstr(line, " V="); if (!V) continue;
        double p[5][2]; if (sscanf(V, " V=(%lf,%lf)(%lf,%lf)(%lf,%lf)(%lf,%lf)(%lf,%lf)", &p[0][0],&p[0][1],&p[1][0],&p[1][1],&p[2][0],&p[2][1],&p[3][0],&p[3][1],&p[4][0],&p[4][1]) != 10) continue;
        double yh=p[0][1], ym=p[1][1], yl=p[3][1], xh=p[0][0], xm=p[1][0], xl=p[2][0];
        double dl=(yl!=ym)?(p[3][0]-xl)/(yl-ym):0, dh=(yl!=yh)?(p[4][0]-xh)/(yl-yh):0, dm=(ym!=yh)?(xm-xh)/(ym-yh):0;
        // dm: slope of the upper minor edge; reconstruct from the logged midpoint only when ym!=yh
        dm = (ym!=yh) ? (xm - xh)/(ym-yh) : 0;  // approx (xm was logged as xm+dm*(ym-yh))
        int lft = (xl > xh) ? 1 : 0;  // major edge on left when minor (xl) is to its right
        int l = tri(xh,yh,xm,ym,xl,yl,dl,dh,dm,lft);
        seen++; if (l) vis++; tot += l;
        printf("swap=%d lit_px=%d  (xh=%.1f xm=%.1f xl=%.1f ends=%.1f,%.1f yh=%.2f yl=%.2f)\n", swap, l, xh,xm,xl,p[3][0],p[4][0],yh,yl);
    }
    printf("TOTAL polys=%d with_lit_pixels=%d lit_sum=%d\n", seen, vis, tot);
    return 0;
}
