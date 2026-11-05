#!/usr/bin/env python3
"""s6902 G5b: instrument only. ROGUESQ_DD_FWDWIN=tog flipped every mach second, out of phase with the [g1b] wall seconds, so every [g1b] line mixed
both arms and the game-rate cost of FWDWIN could not be read in one run. ROGUESQ_DD_FWDWIN_TOGS=<sec> sets the half period (default 1 = unchanged)
and, above 1, prints [fwdtog] on=<0|1> at each flip, so a run.log splits by arm in stream order (tools/g5b_fwdtog_rate.py drops seconds with a flip).
Runs after apply_s6901_fwdwin in RS64_REPLAY.  Usage: apply_s6902_fwdtog.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6902 fwdtog"
f = D / "funcs_9.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "            if (on6037 && edge6874 && px1 > px0 && pz1 > pz0 && (on6901 == 1 || (on6901 == 2 && ((mach_absolute_time() / 24000000u) & 1u)))) {\n"
N = r'''            /* PATCH: s6902 fwdtog */ static uint64_t per6902 = 0; static int last6902 = -1; int ph6902 = 0;
            if (on6901 == 2) { if (!per6902) { const char* e = getenv("ROGUESQ_DD_FWDWIN_TOGS"); int s = (e && *e) ? atoi(e) : 1; per6902 = (uint64_t)(s > 0 ? s : 1) * 24000000u; }
              ph6902 = (int)((mach_absolute_time() / per6902) & 1u);
              if (ph6902 != last6902) { last6902 = ph6902; if (per6902 > 24000000u) fprintf(stderr, "[fwdtog] on=%d\n", ph6902); } }
            if (on6037 && edge6874 && px1 > px0 && pz1 > pz0 && (on6901 == 1 || ph6902)) {
'''
assert t.count(A) == 1, t.count(A)
f.write_text(t.replace(A, N, 1), errors="surrogateescape"); print("applied", TAG)
