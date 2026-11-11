#!/usr/bin/env python3
"""s7110 fps60-wall-nearfix: same-run arm for the projection near plane. ROGUESQ_DD_NEAR=<m> scales only the guPerspective near
arg in setupCameraMatrices (apply_s6031_far.py); the push-out (applyPlayerVehicleStateUpdate) keeps using the camera struct near.
ROGUESQ_DD_NEAR_TOG=1 applies the DD_NEAR scale only in odd absolute mach seconds (mach/24e6 & 1, the same clock as
S7108_CAMWIDE=tog and tools/s7108_split.py), so one run carries both arms. Unset = DD_NEAR exactly as before. Runs after
apply_s6916 fartog. Usage: apply_s7110_neartog.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7110 neartog"
f = D / "funcs_4.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = ' if (tg && ((mach_absolute_time() / 24000000ull) & 1)) mf = 0.0; }'
N = A + (' { /* ' + TAG + ' */ extern uint64_t mach_absolute_time(void); static int tn = -1; if (tn < 0) tn = rs6031_env("ROGUESQ_DD_NEAR_TOG") > 0.0;'
         ' if (tn && !((mach_absolute_time() / 24000000ull) & 1)) mn = 0.0; }')
assert t.count(A) == 1, t.count(A)
t = t.replace(A, N, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
