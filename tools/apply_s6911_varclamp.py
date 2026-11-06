#!/usr/bin/env python3
"""s6911 G5h: dd4 floating horizon triangles. selectGridCellTileVariant (0x80046030) indexes the level map with the cell's raw x,z (lh 0x18/0x1A, stride
0x80136DF8) while clampGridCellLookup gave that cell its flags from the clamped edge cell. A dd>1 window runs far past the map (LEVEL=4: 94x94 map, window to
row 143), so a flagged border cell reads past the map array, takes a junk tile index and copies 25 junk height bytes into its pool slot.
ORIGIN: retail code, out-of-map cells only reached this far because of our dd window. rs64_s6911_mapidx clamps x,z to the map at dd>1 in levels 0..18.
ROGUESQ_DD_VARCLAMP=0 old, =tog on in odd seconds of the 24 MHz mach clock. dd1 never active. Runs after apply_s6909_dlreclaim in RS64_REPLAY.
Usage: apply_s6911_varclamp.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6911 varclamp"
f = D / "funcs_10.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "    // 0x80046180: sll         $v0, $v0, 1\n"
assert t.count(A) == 1, t.count(A)
H = ("    { extern int32_t rs64_s6911_mapidx(int32_t, int32_t, int32_t, uint32_t, uint32_t); ctx->r2 = (gpr)rs64_s6911_mapidx((int32_t)ctx->r2, (int32_t)MEM_H(ctx->r10, 0X18), "
     "(int32_t)MEM_H(ctx->r10, 0X1A), (uint32_t)MEM_HU(ctx->r8, 0X38), (uint32_t)MEM_HU(ctx->r8, 0X3A)); } /* " + TAG + " */\n")
t = t.replace(A, H + A, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
