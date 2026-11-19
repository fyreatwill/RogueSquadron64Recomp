#!/usr/bin/env python3
"""s7625 G6c step 3b fix: the stand-ins' view-test far bound scales with the draw distance.
ORIGIN (s7625 measurement, tools/apply_s7625_viewtest_reason.py): of the stand-ins in front of the camera, the far exit
(0x8001DDA8 radius path: z - r >= view+0x28) rejects the most (L1 18325, L4 53368 of 42796/161033 calls; view far 30.8 / 27.8 at
dd4, i.e. the retail object far: our dd bundle scales the projection far, not this one). Upstream does the same multiply at
0x8001E078 (far_check). The +-125 box test (0x8001DCEC/DD38, convertMat3x4ToN64Mtx fixed-point reach) runs before the far
test on the radius path and stays retail, so a widened far can never pass an object the LLE matrix cannot hold.
After the lwc1 $f0, 0x28($s1) at 0x8001DD9C (radius path) and 0x8001E074 (point path): $f0 *= rs64_vt_farmul when it is not
1.0. The host (src/main/rs64_standins.cpp) sets rs64_vt_farmul only around its own addNpcToVisibilityBucket call; every other
caller sees 1.0 = retail. Idempotent; RS64_REPLAY after apply_s7625_viewtest_reason.py."""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7625 standins far"
f = D / "funcs_6.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
for pc in ("8001DD9C", "8001E074"):
    a = "    { RS64_S7484_LD(0x%su, ctx->r17, 0X28, 4); ctx->f0.u32l = MEM_W(ctx->r17, 0X28); }\n" % pc
    assert t.count(a) == 1, (pc, t.count(a))
    t = t.replace(a, a + "    { extern float rs64_vt_farmul; if (__builtin_expect(rs64_vt_farmul != 1.0f, 0)) ctx->f0.fl *= rs64_vt_farmul; } /* %s */\n" % TAG, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
