#!/usr/bin/env python3
"""s7023 G1c: callee/self split of streamTerrainGridCellsByDistance's loop (funcs_9.c), on top of apply_s7022_streamtime.py, same switch
ROGUESQ_S7022_ST=1. Adds mach time around getGridCellValueAt and processGridCellByDistance (ticks + call counts), the inclusive time of
the call-path region (L_80042DC4 -> next cell / row end), and per-call deltas of the s6493 path counters (spaneq skip [4], span reject [5],
call path [6], poolcap [3]). Printed as [s7023-cs] by rs64_s7023_cs (src/main/upstream_compat.cpp). Measurement only.
Usage: apply_s7023_calleetime.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7023 calleetime"
f = D / "funcs_9.c"; t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
assert "PATCH: s7022 streamtime" in t, "apply_s7022_streamtime.py first"
def rep(old, new, n=1):
    global t
    assert t.count(old) == n, (old[:70], t.count(old)); t = t.replace(old, new)
rep('#include "funcs.h"\n', '#include "funcs.h"\nextern void rs64_s7023_cs(const unsigned long long* v); /* %s */\n' % TAG)
S = "RECOMP_FUNC void streamTerrainGridCellsByDistance(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n"
i0 = t.index(S); i1 = t.index("RECOMP_FUNC void buildGridCellMeshForFace(", i0); body = t[i0:i1]
def brep(old, new):
    global body
    assert body.count(old) == 1, (old, body.count(old)); body = body.replace(old, new)
# v: 0 c0 ticks, 1 n0, 2 c1 ticks, 3 n1, 4 call-path region ticks, 5 region entries, 6..9 s6493 [3],[4],[5],[6] at entry (deltas at exit)
CP = "if (s7023_cp) { s7023_v[4] += mach_absolute_time() - s7023_cp; s7023_cp = 0; } /* %s */\n" % TAG
brep("unsigned s7022_it = 0, s7022_rw = 0; /* PATCH: s7022 streamtime */\n",
     "unsigned s7022_it = 0, s7022_rw = 0; /* PATCH: s7022 streamtime */\n"
     "    unsigned long long s7023_v[10] = {0}, s7023_cp = 0; if (g_rs64_s7022) { s7023_v[6] = g_s6493[3]; s7023_v[7] = g_s6493[4]; s7023_v[8] = g_s6493[5]; s7023_v[9] = g_s6493[6]; } /* %s */\n" % TAG)
brep("L_80042D3C:\n", "L_80042D3C:\n    " + CP)
brep("L_80043070:\n", "L_80043070:\n    " + CP)
brep("L_80042DC4:\n", "L_80042DC4:\n    if (g_rs64_s7022) { s7023_cp = mach_absolute_time(); s7023_v[5]++; } /* %s */\n" % TAG)
brep("    getGridCellValueAt(rdram, ctx);\n",
     "    { unsigned long long s7023_a = g_rs64_s7022 ? mach_absolute_time() : 0; getGridCellValueAt(rdram, ctx);"
     " if (g_rs64_s7022) { s7023_v[0] += mach_absolute_time() - s7023_a; s7023_v[1]++; } } /* %s */\n" % TAG)
brep("    processGridCellByDistance(rdram, ctx);\n",
     "    { unsigned long long s7023_a = g_rs64_s7022 ? mach_absolute_time() : 0; processGridCellByDistance(rdram, ctx);"
     " if (g_rs64_s7022) { s7023_v[2] += mach_absolute_time() - s7023_a; s7023_v[3]++; } } /* %s */\n" % TAG)
brep("    if (g_rs64_s7022) rs64_s7022_st(",
     "    if (g_rs64_s7022) { " + CP.split(" /*")[0] + " s7023_v[6] = g_s6493[3] - s7023_v[6]; s7023_v[7] = g_s6493[4] - s7023_v[7];"
     " s7023_v[8] = g_s6493[5] - s7023_v[8]; s7023_v[9] = g_s6493[6] - s7023_v[9]; rs64_s7023_cs(s7023_v); } /* %s */\n"
     "    if (g_rs64_s7022) rs64_s7022_st(" % TAG)
t = t[:i0] + body + t[i1:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
