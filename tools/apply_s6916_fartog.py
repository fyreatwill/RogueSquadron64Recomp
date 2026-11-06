#!/usr/bin/env python3
"""s6916 G5h: same-run control for the dd far plane. The shot 79 sea slab goes when ROGUESQ_DD_FAR=1 at dd4 (non-sky 0.55 -> 0.07), but that was a separate run
and one shot. ROGUESQ_DD_FAR_TOG=1 drops the far scale on odd seconds of the 24 MHz mach clock, so one playlist run shows what every shot loses without it.
Default off: unset leaves the far scale exactly as before. Runs after apply_s6903 cinegate. Usage: apply_s6916_fartog.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6916 fartog"
f = D / "funcs_4.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = 'double mf = g_rs64_dd_scene ? rs6031_far() : 0.0, mn = rs6031_env("ROGUESQ_DD_NEAR");'
N = A + (' { /* ' + TAG + ' */ extern uint64_t mach_absolute_time(void); static int tg = -1; if (tg < 0) tg = rs6031_env("ROGUESQ_DD_FAR_TOG") > 0.0;'
         ' if (tg && ((mach_absolute_time() / 24000000ull) & 1)) mf = 0.0; }')
assert t.count(A) == 1, t.count(A)
t = t.replace(A, N, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
