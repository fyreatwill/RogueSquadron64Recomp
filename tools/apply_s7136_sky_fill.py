#!/usr/bin/env python3
"""s7136 G3 wide sky-side corner holes (class (a)): under ROGUESQ_ASPECT the horizon clear covers the whole viewport.

ORIGIN (s7136, offline on the s7134 Z1 21:9 capture swap 7533 and the s7135 W1 16:9 capture swap 7542, plus a code read):
- The sky is the 'horiz_sky' HOB, loaded by 0x8005AB34 (generated name loadSkyHorizonHob). It sorts the polys into 8 azimuth
  sectors (centroid atan2 / (pi/4), rodata 0x8003AE24) plus 8 'top' bins (polys within 10 units of the max height, <= 30),
  each a render object at S+0x1C+0x5C*k (S = 0x8056E010 on L6). The top bins carry vertex colours A8988000 / A89880FF: the
  band's top row fades to alpha 0 toward (168,152,128).
- The horizon clear builder 0x8005B51C (s7133) fills the GROUND side with fill colour ACE1 (RGBA5551 = 173,156,132), i.e. the
  same beige the band fades into; the sky side relies on the opaque band.
- In the hole frames no top-fade tri reaches the RDP stream, the band (op E, cc 127E24FFFFFFFF, om 002C..., affine, no Z) spans
  the full screen width (21:9 x -77..908 of 1024; 16:9 -169..790 of 796, so it is projected 3D geometry, NOT a 4:3 screen-space
  placement: H-band-scale refuted), and its vertex rays reach at most ~+17 deg elevation. The hole pixels sit at +5..+17 deg,
  just above the band's top edge (az -95..-75); the 4:3 corner of the same pose is at +4 deg, inside the band. So retail never
  looks above the band at this pose; the 21:9 / 16:9 corner does, and nothing paints there (H-fill-rect selected).
The writer is the game's own clear builder; its two rects are retail-correct for a 4:3 view, which never sees past the band top.
Fix: when ASPECT k != 1, after the builder appends its rect pair (count += 2 at 0x8005BC88), widen the pair's first rect to the
whole viewport {0, 0, w-1, h-1} (w, h = cam+0x12 / +0x16 as the builder uses). Same colour, same position in the DL (before the
band), so the band and terrain still draw over it; only pixels nothing else paints change, and they get the band's fade colour.
  ROGUESQ_HORIZON_SKYFILL: default on (no-op when k == 1, i.e. 4:3 retail); =0 restores retail; =tog odd mach seconds only.
  [s7136] stderr once per mach second: frames widened.
Idempotent; listed in fixup_game_funcs_vendored.py right after apply_s7135_pitch_gate.py."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7136 sky fill"
P = BASE / "funcs_13.c"
T = P.read_text()
if MARK in T:
    print("s7136 already applied"); sys.exit(0)
A = "    // 0x8005BC8C: lw          $ra, 0xBC($sp)\n"
assert T.count(A) == 1, "anchor 0x8005BC8C not unique"
i = T.index(A)
st = T.rfind("    // 0x8005BC88: sw          $v0, 0x0($v1)\n", 0, i)
assert st > 0 and i - st < 1200, "0x8005BC88 store not right before the anchor"
NEW = r'''    { /* PATCH: s7136 sky fill */ static int md7136 = -1; static float k7136 = 1.0f; static unsigned long long sec7136; static unsigned n7136;
      extern uint64_t mach_absolute_time(void);
      if (md7136 < 0) { const char* e = getenv("ROGUESQ_HORIZON_SKYFILL"); md7136 = (e && *e == '0') ? 0 : (e && !strcmp(e, "tog")) ? 2 : 1;
        const char* a = getenv("ROGUESQ_ASPECT_SCALE"); k7136 = (a && *a) ? (float)atof(a) : 1.0f; if (!(k7136 > 0.0f)) k7136 = 1.0f; }
      if (md7136 && k7136 != 1.0f) {
        unsigned long long s = mach_absolute_time() / 24000000ull; int on = md7136 == 1 || (md7136 == 2 && (s & 1));
        if (s != sec7136) { if (n7136) fprintf(stderr, "[s7136] sec %llu skyfill %u mode=%d\n", sec7136, n7136, md7136); n7136 = 0; sec7136 = s; }
        if (on) {
          int32_t cnt = (int32_t)MEM_W(0, ctx->r3); uint32_t lst = (uint32_t)MEM_W(4, ctx->r3); uint32_t cam = (uint32_t)MEM_W(0, ctx->r22);
          if (cnt >= 2 && cnt < 64 && (lst >> 24) == 0x80 && (cam >> 24) == 0x80) {
            gpr r = (gpr)(int32_t)(lst + (uint32_t)(cnt - 2) * 8u); gpr c = (gpr)(int32_t)cam;
            int w = (int)(uint16_t)MEM_HU(0x12, c), h = (int)(uint16_t)MEM_HU(0x16, c);
            if (w > 0 && w <= 2048 && h > 0 && h <= 1024) {
              MEM_H(0, r) = 0; MEM_H(2, r) = 0; MEM_H(4, r) = (int16_t)(w - 1); MEM_H(6, r) = (int16_t)(h - 1); n7136++; } } } } }
'''
# The steep-pitch early return (0x8005B5F0 bc1t L_8005BC8C) jumps straight to the epilogue with $v1 = garbage, so the block must go
# BEFORE that label: it may only run on the fall-through path from the count += 2 store (s7136 first build crashed there, SIGBUS).
LBL = "L_8005BC8C:\n"
if T[i - len(LBL):i] == LBL: i -= len(LBL)
T = T[:i] + NEW + T[i:]
for inc in ("#include <string.h>", "#include <stdlib.h>", "#include <stdio.h>"):
    if inc not in T: T = inc + "\n" + T
P.write_text(T); print("s7136 applied")
