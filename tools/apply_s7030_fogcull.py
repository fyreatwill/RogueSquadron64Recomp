#!/usr/bin/env python3
"""s7030 G1c: fogged-cell cull in streamTerrainGridCellsByDistance (funcs_9.c), ROGUESQ_DD_FOGCULL=<k> | tog3 (factors from
ROGUESQ_DD_FOGCULL_K=a,b,c, cycled on (mach/24e6)%3 seconds like s7012). At function entry rs64_s7030_begin reads the eye
(a0, grid units) and the 4 frustum far corners (0x80130C1C.., same space) and takes the horizontal forward unit vector.
At the call path (L_80042DC4, before getGridCellValueAt) a cell whose near-edge forward depth (f20*fx + f22*fz - 0.71)
exceeds k * fog end (rs64_s6904_fog's scaled end, grid units = world/2) goes to the game's own span-reject path
(L_80042DB0: both span bytes 0x7F, next cell), i.e. the cell is not streamed this frame. k=0 culls nothing; the
per-phase depth histogram (depth / fog end) is kept in every phase. Printed as [s7030] by rs64_s7030_cell's reporter.
Usage: apply_s7030_fogcull.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7030 fogcull"
f = D / "funcs_9.c"; t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
def rep(old, new, n=1):
    global t
    assert t.count(old) == n, (old[:70], t.count(old)); t = t.replace(old, new)
rep('#include "funcs.h"\n', '#include "funcs.h"\nextern int g_rs64_s7030; extern float g_rs64_s7030_f[2]; extern void rs64_s7030_begin(uint8_t*, uint32_t); '
    'extern int rs64_s7030_cell(float d); /* %s */\n' % TAG)
S = "RECOMP_FUNC void streamTerrainGridCellsByDistance(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n"
rep(S, S + "    if (g_rs64_s7030) rs64_s7030_begin(rdram, U32(ctx->r4)); /* %s */\n" % TAG)
i0 = t.index(S); i1 = t.index("RECOMP_FUNC void buildGridCellMeshForFace(", i0); body = t[i0:i1]
assert body.count("L_80042DB0:\n") == 1 and body.count("L_80042DC4:\n") == 1
body = body.replace("L_80042DC4:\n", "L_80042DC4:\n    if (g_rs64_s7030 && rs64_s7030_cell(ctx->f20.fl * g_rs64_s7030_f[0] + ctx->f22.fl * g_rs64_s7030_f[1])) "
                    "{ ctx->r2 = ADD32(ctx->r5, ctx->r13); goto L_80042DB0; } /* %s: v0 = a1+t5 as on the reject edge */\n" % TAG)
t = t[:i0] + body + t[i1:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
