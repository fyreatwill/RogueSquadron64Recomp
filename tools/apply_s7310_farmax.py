#!/usr/bin/env python3
"""s7310 g5f-219-left-sliver: ceiling on the dd-scaled projection far plane. The s6701 cap (apply_s6031_far.py) only keeps far <= 65534-near.
s7310 (L1 PIN=1 same pose, 21:9): with the scaled far above ~33.3k-43.6k the sky-dome panels touching the screen edge arrive in the RDP stream
with clip vertices pinned to x=0/y=0 and texture W ~0, drawn as vertical streaks (the 21:9 dd8 left sliver) and a warped dome periphery
(right-edge moon arc, top corners). Far 8070.8 x4 / x4.05 / x4.12 (<= 33252) clean; x5.40 / x5.42 / x6 / x8 pinned; dd8 with far x4 is
pixel-identical to dd8 on terrain at that pose. Not perspNorm (x5.40 still has perspNorm 3), not the s6418 far clip, not aspect.
ROGUESQ_DD_FARMAX=<units> (default 32767) caps the scaled far; 0 = off (s6701 cap only). Only reached when the far scale is active
(dd>1 or DD_FAR), and never lowers far below the game's own value, so dd1/retail is untouched. Runs after apply_s6031_far.
Usage: apply_s7310_farmax.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7310 farmax"
f = D / "funcs_4.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "float lim = 65534.0f - nf, sf = (float)(ff * mf);"
N = A + (" { /* " + TAG + " */ static float fm7310 = -1.0f; if (fm7310 < 0.0f) { const char* e = getenv(\"ROGUESQ_DD_FARMAX\");"
         " fm7310 = (e && *e) ? (float)atof(e) : 32767.0f; if (fm7310 < 0.0f) fm7310 = 0.0f; fprintf(stderr, \"[s7310] far max %g\\n\", fm7310); }"
         " if (fm7310 > 0.0f && fm7310 < lim) lim = fm7310; }")
assert t.count(A) == 1, t.count(A)
t = t.replace(A, N, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
