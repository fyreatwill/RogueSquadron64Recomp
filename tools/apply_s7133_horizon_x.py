#!/usr/bin/env python3
"""s7133 G3 21:9 side-band holes: widescreen x fix for the flight camera's horizon-split background clear.

Writer named by the s6843 store watch (s7133, ROGUESQ_STORE_WATCH=138D18:138DE4): 0x8005B51C (generated name
setupWalkerSpriteTileQuad, really the horizon clear-rect builder) writes camera 0x80138D18 +0x74 count and the two u16 rects at
+0x7C..+0x8B that emitFrameRdpInitDl clears. It projects three horizon points through the camera with
ndc_x = x/z * cot(fov/2) * 0.75 (rodata 0x8003AE44, = 1/(4:3)), then places the split at pixel x = w/2 + (w/2) * ndc_x
(0x8005B770, w = camera+0x10 viewport width). Under ROGUESQ_ASPECT the viewport is widened by k = ROGUESQ_ASPECT_SCALE and
guPerspective's aspect by the same k (s6104), so the true NDC is ndc_x / k: the game puts the split k times too far from the
centre (2x at 21:9), and the region between the true horizon and the misplaced split is neither cleared nor drawn (stale pixels).
The two slopes (dy/dx at 0x8005B7FC, dx/dy at 0x8005BA60) use the same 0.75-scaled NDC in a ratio with pixel distances, which
reproduces the retail pixel slope exactly at any k, so only this one product is scaled.
  ROGUESQ_HORIZON_XFIX: default on (no-op when k == 1, i.e. 4:3 / retail); =0 restores retail; =tog applies it on odd mach seconds
  (mach/24e6 & 1, the s7114_parity clock) for same-run A/B.
Idempotent; listed in fixup_game_funcs_vendored.py before apply_s7069_callsite_gate.py."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7133 horizon x"
P = BASE / "funcs_13.c"
T = P.read_text()
if MARK in T:
    print("s7133 already applied"); sys.exit(0)
A = "    // 0x8005B770: mul.s       $f6, $f4, $f14\n"
OLD = "    ctx->f6.fl = MUL_S(ctx->f4.fl, ctx->f14.fl);\n"
i = T.index(A); assert T.count(A) == 1
j = T.index(OLD, i); assert T.index("// 0x8005B774:", i) > j
NEW = OLD + ("    { /* " + MARK + " */ static float k7133 = -1.0f; static int md7133 = -1; extern uint64_t mach_absolute_time(void);\n"
             "      if (md7133 < 0) { const char* e = getenv(\"ROGUESQ_HORIZON_XFIX\"); md7133 = (e && *e == '0') ? 0 : (e && !strcmp(e, \"tog\")) ? 2 : 1;\n"
             "        const char* a = getenv(\"ROGUESQ_ASPECT_SCALE\"); k7133 = (a && *a) ? (float)atof(a) : 1.0f; if (!(k7133 > 0.0f)) k7133 = 1.0f;\n"
             "        if (md7133 && k7133 != 1.0f) fprintf(stderr, \"[s7133] horizon clear x / %g mode=%d\\n\", (double)k7133, md7133); }\n"
             "      if (k7133 != 1.0f && (md7133 == 1 || (md7133 == 2 && ((mach_absolute_time() / 24000000ull) & 1)))) ctx->f6.fl = ctx->f6.fl / k7133; }\n")
T = T[:j] + NEW + T[j + len(OLD):]
P.write_text(T); print("s7133 applied")
