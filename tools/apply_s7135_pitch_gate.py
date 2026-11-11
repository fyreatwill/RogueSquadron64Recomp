#!/usr/bin/env python3
"""s7135 G3 21:9 no-clear strip: make the horizon clear builder's steep-pitch gate aspect-aware.

ORIGIN (s7135, code read + capture): 0x8005B51C (generated name setupWalkerSpriteTileQuad, the horizon clear-rect builder)
returns with NO rects when the camera forward vector's horizontal length is < 0.5 (rodata 0x8003AE34, compare 0x8005B5E8,
branch 0x8005B5F0), i.e. when the camera pitches more than 60 deg up or down. Forward = 3rd rotation column of
*(0x80138D1C)+0x28 (copied by 0x80059D18). tools/s7135_campitch.py on the s7134 Z1 capture (L6, 21:9, fix-off for s7133):
the gate trips at swap 7557 (horiz 0.492) and the 0-rect class starts at 7558 and lasts the whole dive to horiz 0.403.
Retail reasoning: at 4:3 (fov 65, tx = 4/3 ty) a pitch > 60 deg keeps every screen corner ray at least ~20 deg below the
horizon (worst case over roll: -0.335 elevation), so the ground there is near and the terrain covers the whole screen.
Under ROGUESQ_ASPECT the view is k times wider (s6104, k = ROGUESQ_ASPECT_SCALE = 2 at 21:9), and the corner rays
reach -0.02..-0.2 elevation (horizon_vis, same capture): ground far beyond the terrain range, which the builder's
margin band would clear but the gate has skipped. Those pixels keep the previous frame (the right-edge strip).
The value 0.5 is the game's legitimate retail constant; ASPECT invalidates the assumption behind it.
Fix: replace the threshold h0 = 0.5 by h* with g(h*, Dk) = g(h0, D0), where g(h, D) = -sqrt(1 - h^2) + h * D is the
worst-case corner elevation over roll, D = tan(fov/2) * sqrt(1 + (4/3 * k)^2), fov = *(cam+0x20) (cam = *(a0)). At k = 1
h* = h0 exactly (retail no-op). 21:9 fov 65: h* ~ 0.335 (about 70 deg pitch).
  ROGUESQ_HORIZON_GATEFIX: default on (no-op when k == 1); =0 restores retail; =tog applies it in odd mach seconds.
  [s7135] stderr: once per (fov, k) the threshold, and once per mach second the count of frames the retail gate would
  have skipped but the fixed one did not (positive control: > 0 in a steep dive at 21:9).
Idempotent; listed in fixup_game_funcs_vendored.py right after apply_s7133_horizon_x.py."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7135 pitch gate"
P = BASE / "funcs_13.c"
T = P.read_text()
if MARK in T:
    print("s7135 already applied"); sys.exit(0)
A = "    // 0x8005B5E4: lwc1        $f0, -0x51CC($at)\n"
OLD = "    ctx->f0.u32l = MEM_W(ctx->r1, -0X51CC);\n"
i = T.index(A); assert T.count(A) == 1
j = T.index(OLD, i); assert j == i + len(A)
NEW = OLD + r'''    { /* PATCH: s7135 pitch gate */ static int md7135 = -1; static float k7135 = 1.0f, fov7135 = -1.0f, thr7135 = 0.5f;
      static unsigned long long sec7135; static unsigned n7135, r7135; extern uint64_t mach_absolute_time(void);
      if (md7135 < 0) { const char* e = getenv("ROGUESQ_HORIZON_GATEFIX"); md7135 = (e && *e == '0') ? 0 : (e && !strcmp(e, "tog")) ? 2 : 1;
        const char* a = getenv("ROGUESQ_ASPECT_SCALE"); k7135 = (a && *a) ? (float)atof(a) : 1.0f; if (!(k7135 > 0.0f)) k7135 = 1.0f; }
      if (md7135 && k7135 != 1.0f) {
        uint32_t cam = (uint32_t)MEM_W(ctx->r22, 0); uint32_t fw = (uint32_t)MEM_W(0x20, (gpr)(int32_t)cam); float fov, h0 = ctx->f0.fl; memcpy(&fov, &fw, 4);
        if (fov > 1.0f && fov < 170.0f && h0 > 0.0f && h0 < 1.0f) {
          if (fov != fov7135) { double t = tan(fov * 3.14159265358979 / 360.0), D0 = t * sqrt(1.0 + 16.0 / 9.0), Dk = t * sqrt(1.0 + 16.0 / 9.0 * k7135 * k7135);
            double tg = -sqrt(1.0 - (double)h0 * h0) + h0 * D0, lo = 0.0, hi = h0; int it;
            for (it = 0; it < 40; it++) { double m = 0.5 * (lo + hi); if (-sqrt(1.0 - m * m) + m * Dk < tg) lo = m; else hi = m; }
            fov7135 = fov; thr7135 = (float)(0.5 * (lo + hi));
            fprintf(stderr, "[s7135] pitch gate fov %g k %g horiz threshold %g -> %g mode=%d\n", (double)fov, (double)k7135, (double)h0, (double)thr7135, md7135); }
          { unsigned long long s = mach_absolute_time() / 24000000ull; int on = md7135 == 1 || (md7135 == 2 && (s & 1));
            if (s != sec7135) { if (n7135 || r7135) fprintf(stderr, "[s7135] sec %llu retail-skip %u rescued %u\n", sec7135, n7135, r7135); n7135 = r7135 = 0; sec7135 = s; }
            if (ctx->f20.fl < h0) { n7135++; if (on && !(ctx->f20.fl < thr7135)) r7135++; }
            if (on) ctx->f0.fl = thr7135; } } } }
'''
T = T[:j] + NEW + T[j + len(OLD):]
for inc in ("#include <math.h>", "#include <string.h>"):
    if inc not in T: T = inc + "\n" + T
P.write_text(T); print("s7135 applied")
