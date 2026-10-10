/* rdplog: minimal mupen64plus video plugin that records the RDP command stream.
 * Works with an LLE RSP plugin (cxd4): ProcessRDPList walks DPC_START..END, appends the raw
 * commands to $RS64_RDP_BIN as records {u32 magic 'RDPC', u32 vi_origin, u32 vi_width, u32 nbytes,
 * u32 seq, words[nbytes/4]} (each word is the big-endian N64 value, stored as a host u32), and on
 * FULL_SYNC (0x29) raises the DP interrupt so the game progresses. A text summary per full sync goes
 * to $RS64_RDP_LOG (default stderr).
 * Build: tools/oracle/rdplog/build.sh */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define M64P_PLUGIN_PROTOTYPES 1
#include "m64p_types.h"
#include "m64p_plugin.h"

static GFX_INFO G;
static FILE *binf, *logf_;
static uint32_t seq, counts[64], cimg[3], timg[3], nbytes_total, nsync;
static uint64_t binbytes;

static uint32_t rd32(const unsigned char *base, uint32_t off) { return *(const uint32_t *)(base + off); }

static uint32_t cmdlen(uint32_t id)
{
    switch (id) {
    case 0x08: return 32;  case 0x09: return 48;  case 0x0A: return 96;  case 0x0B: return 112;
    case 0x0C: return 96;  case 0x0D: return 112; case 0x0E: return 160; case 0x0F: return 176;
    case 0x24: case 0x25: return 16;
    default: return 8;
    }
}

EXPORT m64p_error CALL PluginStartup(m64p_dynlib_handle h, void *ctx, void (*dbg)(void *, int, const char *)) { return M64ERR_SUCCESS; }
EXPORT m64p_error CALL PluginShutdown(void) { if (binf) fclose(binf); return M64ERR_SUCCESS; }
EXPORT m64p_error CALL PluginGetVersion(m64p_plugin_type *t, int *v, int *a, const char **n, int *c)
{
    if (t) *t = M64PLUGIN_GFX;
    if (v) *v = 0x00010000;
    if (a) *a = 0x020500;
    if (n) *n = "rs64-rdplog";
    if (c) *c = 0;
    return M64ERR_SUCCESS;
}
EXPORT int CALL InitiateGFX(GFX_INFO gi)
{
    const char *b = getenv("RS64_RDP_BIN"), *l = getenv("RS64_RDP_LOG");
    G = gi;
    if (b) binf = fopen(b, "wb");
    logf_ = l ? fopen(l, "w") : stderr;
    return 1;
}
EXPORT void CALL ChangeWindow(void) {}
EXPORT void CALL MoveScreen(int x, int y) {}
EXPORT void CALL ProcessDList(void) {}
EXPORT void CALL RomClosed(void) { if (binf) fflush(binf); if (logf_) fflush(logf_); }
EXPORT int CALL RomOpen(void) { return 1; }
EXPORT void CALL ShowCFB(void) {}
EXPORT void CALL UpdateScreen(void) {}
EXPORT void CALL ViStatusChanged(void) {}
EXPORT void CALL ViWidthChanged(void) {}
EXPORT void CALL ReadScreen2(void *d, int *w, int *h, int f) {}
EXPORT void CALL SetRenderingCallback(void (*cb)(int)) {}
EXPORT void CALL ResizeVideoOutput(int w, int h) {}
EXPORT void CALL FBRead(unsigned int a) {}
EXPORT void CALL FBWrite(unsigned int a, unsigned int s) {}
EXPORT void CALL FBGetFrameBufferInfo(void *p) {}

static void flush_summary(void)
{
    uint32_t tri = 0, i;
    for (i = 0x08; i <= 0x0F; i++) tri += counts[i];
    fprintf(logf_, "[rdp] sync=%u vi_origin=0x%x vi_width=%u bytes=%u tri=%u (", nsync,
            G.VI_ORIGIN_REG ? *G.VI_ORIGIN_REG & 0xFFFFFF : 0, G.VI_WIDTH_REG ? *G.VI_WIDTH_REG : 0,
            nbytes_total, tri);
    for (i = 0x08; i <= 0x0F; i++) fprintf(logf_, "%u%s", counts[i], i < 0x0F ? "," : "");
    fprintf(logf_, ") texrect=%u+%u fillrect=%u settile=%u loadblk=%u loadtile=%u loadtlut=%u settimg=%u setcimg=%u"
            " cimg=fmt%u/sz%u/w%u@0x%x last_timg=0x%x\n",
            counts[0x24], counts[0x25], counts[0x36], counts[0x35], counts[0x33], counts[0x34], counts[0x30],
            counts[0x3D], counts[0x3F], cimg[0] >> 8, cimg[0] & 0xFF, cimg[1], cimg[2], timg[2]);
    fflush(logf_);
    memset(counts, 0, sizeof counts);
    nbytes_total = 0;
}

EXPORT void CALL ProcessRDPList(void)
{
    uint32_t start = *G.DPC_START_REG & 0xFFFFF8, end = *G.DPC_END_REG & 0xFFFFF8, p;
    int xbus = *G.DPC_STATUS_REG & 1;
    uint32_t cur = *G.DPC_CURRENT_REG & 0xFFFFF8;
    if (cur >= start && cur <= end) start = cur; /* resume: earlier END writes already consumed START..CURRENT */
    const unsigned char *base = xbus ? G.DMEM : G.RDRAM;
    uint32_t mask = xbus ? 0xFFF : 0xFFFFFF;
    if (end > start) {
        const char *bw = getenv("RS64_RDP_BIN_WIDTH");
        if (binf && binbytes < (1ull << 29) && (!bw || (G.VI_WIDTH_REG && *G.VI_WIDTH_REG == (uint32_t)atoi(bw)))) {
            uint32_t hdr[5] = { 0x52445043, G.VI_ORIGIN_REG ? *G.VI_ORIGIN_REG & 0xFFFFFF : 0,
                                G.VI_WIDTH_REG ? *G.VI_WIDTH_REG : 0, end - start, seq++ };
            fwrite(hdr, 4, 5, binf);
            for (p = start; p < end; p += 4) {
                uint32_t w = rd32(base, p & mask);
                fwrite(&w, 4, 1, binf);
            }
            binbytes += 20 + (end - start);
        }
        for (p = start; p + 8 <= end;) {
            uint32_t w0 = rd32(base, p & mask), w1 = rd32(base, (p + 4) & mask);
            uint32_t id = (w0 >> 24) & 0x3F, len = cmdlen(id);
            counts[id]++;
            nbytes_total += len;
            if (id == 0x3F) { cimg[0] = ((w0 >> 21 & 7) << 8) | (w0 >> 19 & 3); cimg[1] = (w0 & 0x3FF) + 1; cimg[2] = w1 & 0xFFFFFF; }
            if (id == 0x3D) { timg[1] = (w0 & 0x3FF) + 1; timg[2] = w1 & 0xFFFFFF; }
            if (id == 0x29) { nsync++; flush_summary(); *G.MI_INTR_REG |= 0x20; G.CheckInterrupts(); }
            p += len;
        }
    }
    *G.DPC_CURRENT_REG = *G.DPC_END_REG;
}
