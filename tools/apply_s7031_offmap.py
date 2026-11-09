#!/usr/bin/env python3
"""s7031 G1c: off-map cell census + cull in the s7030 hook (funcs_9.c streamTerrainGridCellsByDistance, L_80042DC4).
Passes the cell's grid x/z (s4 + win[0x80132DB0], fp + win[0x80132DB8], the exact a0/a1 later given to getGridCellValueAt at
0x80042E14/0x80042E1C) to rs64_s7031_cell, which applies the clamp-branch test of getGridCellValueAt (x<0 || x>=dims[0x38] ||
z<0 || z>=dims[0x3A], dims at 0x80136DC0) and the ring distance outside the map edge. ROGUESQ_DD_OFFMAPCULL=<R> | tog3 with
ROGUESQ_DD_OFFMAPCULL_R=a,b,c (R<0 = off) culls off-map cells more than R rings outside the edge (same span-reject path as s7030).
Requires apply_s7030_fogcull.py. Usage: apply_s7031_offmap.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7031 offmap"
f = D / "funcs_9.c"; t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
old = "if (g_rs64_s7030 && rs64_s7030_cell(ctx->f20.fl * g_rs64_s7030_f[0] + ctx->f22.fl * g_rs64_s7030_f[1])) "
assert t.count(old) == 1, t.count(old)
new = ("if (g_rs64_s7030 && rs64_s7031_cell(ctx->f20.fl * g_rs64_s7030_f[0] + ctx->f22.fl * g_rs64_s7030_f[1], "
       "(int32_t)ADD32(ctx->r20, MEM_W(0x2DB0, (int64_t)(int32_t)0x80130000)), (int32_t)ADD32(ctx->r30, MEM_W(0x2DB8, (int64_t)(int32_t)0x80130000)))) /* %s */ " % TAG)
t = t.replace(old, new)
t = t.replace('extern int rs64_s7030_cell(float d);', 'extern int rs64_s7030_cell(float d); extern int rs64_s7031_cell(float d, int32_t x, int32_t z);', 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
