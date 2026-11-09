#!/usr/bin/env python3
"""s7032 G1c: pass the cell's eye-relative grid offsets (f20, f22) to the off-map cull so it can tell whether the EYE is over the map.
s7032 frozen-pose arms: OFFMAPCULL=2 is invisible while the camera flies over the map, but once no-input flight carries the craft out
over the off-map plateau, the cut leaves a sky void a few cells ahead (|d| 39 vs A/A 0.01). rs64_s7032_cell gates the ring cull on the
eye cell (x - f20, z - f22) being on the map (ROGUESQ_DD_OFFMAPCULL_EYE=0 = s7031 ungated). Requires apply_s7031_offmap.py.
Usage: apply_s7032_eyegate.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7032 eyegate"
f = D / "funcs_9.c"; t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
old = "if (g_rs64_s7030 && rs64_s7031_cell(ctx->f20.fl * g_rs64_s7030_f[0] + ctx->f22.fl * g_rs64_s7030_f[1], "
assert t.count(old) == 1, t.count(old)
t = t.replace(old, "if (g_rs64_s7030 && rs64_s7032_cell(ctx->f20.fl, ctx->f22.fl, ctx->f20.fl * g_rs64_s7030_f[0] + ctx->f22.fl * g_rs64_s7030_f[1], ")
t = t.replace("/* PATCH: s7031 offmap */", "/* PATCH: s7031 offmap */ /* %s */" % TAG, 1)
t = t.replace('extern int rs64_s7031_cell(float d, int32_t x, int32_t z);',
              'extern int rs64_s7031_cell(float d, int32_t x, int32_t z); extern int rs64_s7032_cell(float ox, float oz, float d, int32_t x, int32_t z);', 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
