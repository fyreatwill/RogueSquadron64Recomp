#!/usr/bin/env python3
"""s7111 fps60-wall-margin: same-run, margin-scaled arm for the s7103 camera re-push (applyPlayerVehicleStateUpdate exit).

s7111 offline (tools/s7111_margin.py on s7110 data): the push-out corner rays are exactly f20 = 2*near long (L/f20 p50 1.000) and
the retail push puts pos exactly f20 before the hit, so a pushed corner ends ON the wall; the next push for another corner can put
it back in. Ticks feeding an eye-cell near-z loss leave a corner inside on 85% vs 18% of all flight ticks (42% in a +-3 s control).
This arm makes the s7103 re-push clear the corners with a margin:
  ROGUESQ_S7103_CAMFIX=tog1  re-push only in odd absolute mach seconds (mach/24e6 & 1, the tools/s7108_split.py clock)
  ROGUESQ_S7111_PUSHK=<k>    re-push distance k*f20 instead of f20 (default 1.0 = s7103 behaviour)
Default off = retail. Runs after apply_s7103_camfix.py. Usage: apply_s7111_camfixk.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7111 camfixk"
f = D / "funcs_10.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A1 = 'getenv("ROGUESQ_S7103_CAMFIX"); md = !e || !*e || *e == \'0\' ? 0 : (!strcmp(e, "tog") ? 2 : 1); t0 = mach_absolute_time(); }\n  if (md < 2) return md;'
N1 = ('getenv("ROGUESQ_S7103_CAMFIX"); md = !e || !*e || *e == \'0\' ? 0 : (!strcmp(e, "tog1") ? 3 : !strcmp(e, "tog") ? 2 : 1); t0 = mach_absolute_time(); }\n'
      '  if (md == 3) return (int)((mach_absolute_time() / 24000000ull) & 1); /* ' + TAG + ' */\n  if (md < 2) return md;')
A2 = "float v = hp[q] - s7103_f20 * d[q] / n;"
N2 = "float v = hp[q] - s7111_k() * s7103_f20 * d[q] / n; /* " + TAG + " */"
A3 = "static int s7103_ray(uint8_t* rdram, recomp_context* ctx, uint32_t s1, const float* d, float* hp) {\n"
N3 = ("static float s7111_k(void) { static float k = -1.0f; if (k < 0.0f) { const char* e = getenv(\"ROGUESQ_S7111_PUSHK\"); k = e && *e ? (float)atof(e) : 1.0f;\n"
      "  if (!(k >= 1.0f && k <= 4.0f)) k = 1.0f; } return k; } /* " + TAG + " */\n" + A3)
for a in (A1, A2, A3):
    assert t.count(a) == 1, (a[:60], t.count(a))
t = t.replace(A1, N1, 1).replace(A2, N2, 1).replace(A3, N3, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
