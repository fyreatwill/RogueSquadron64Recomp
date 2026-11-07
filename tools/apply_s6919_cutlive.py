#!/usr/bin/env python3
"""s6919 G5h far band: the s6418 far clip block ran at every dd. It latched 0x8009DEB4 once at boot and wrote that value back every frame just before
buildGridCellMeshForFace read it, so the game's per scene cutoff (computeGridLayerScrollOffset, 57-229 in AT THE MOVIES) never reached the near/far cut.
ORIGIN: ours, s6418. rs64_s6919_keep leaves the game's value alone when the dd scale is not active: ROGUESQ_CUT_LIVE default on, =0 old, =tog odd seconds.
At dd>1 the scale keeps the latched base unless ROGUESQ_DD_CUT_LIVE=1 or tog, which scales the game's value instead. Also records what the chain reads at 0x800434F4
for the ROGUESQ_G5H_BAND row. Runs after apply_s6904_fog in RS64_REPLAY.
Usage: apply_s6919_cutlive.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6919 cutlive"
f = D / "funcs_9.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "if (org6418 && !off6418) { union { uint32_t u; float f; } c; c.u = org6418; if (me6036"
assert t.count(A) == 1, t.count(A)
B = ("{ extern int rs64_s6919_keep(int); extern uint32_t rs64_s6919_base(uint32_t, uint32_t, int); /* " + TAG + " */ "
     "s6919_dda = me6036 != 1.0f && MEM_W(4, (int64_t)(int32_t)0x80136DC0) != 0; s6919_keep = rs64_s6919_keep(s6919_dda); "
     "org6418 = rs64_s6919_base(org6418, (uint32_t)MEM_W(0, (int64_t)(int32_t)0x8009DEB4), s6919_dda); }\n        "
     "if (org6418 && !off6418 && !s6919_keep) { union { uint32_t u; float f; } c; c.u = org6418; if (me6036")
t = t.replace(A, B, 1)
C = "{ /* PATCH: s6418 farclip */ static uint32_t org6418 = 0; static int off6418 = -1;"
assert t.count(C) == 1, t.count(C)
t = t.replace(C, C + " int s6919_dda, s6919_keep;", 1)
W = "MEM_W(0, (int64_t)(int32_t)0x8009DEB4) = (int32_t)c.u; } }\n"
assert t.count(W) == 1, t.count(W)
t = t.replace(W, "{ extern void rs64_s6919_wrote(uint32_t); rs64_s6919_wrote(c.u); } " + W, 1)
H = "    // 0x800434F4: lw          $v0, 0x4($s0)\n"
assert t.count(H) == 1, t.count(H)
t = t.replace(H, "    { extern void rs64_s6919_cut(uint8_t*, uint32_t); rs64_s6919_cut(rdram, (uint32_t)ctx->r16); } /* " + TAG + " */\n" + H, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
