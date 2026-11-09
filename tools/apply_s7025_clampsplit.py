#!/usr/bin/env python3
"""s7025 G1c: time split inside clampGridCellLookup (0x80048948, funcs_10.c), same switch ROGUESQ_S7022_ST=1. Measurement only.
g_s7025[0..1] = calls / mach ticks entry->exit (L_80048B8C), [2..3] = create path (L_80048AC4 -> exit: processGridCellByDistance +
nested getGridCellValueAt alloc + link), [4] = retries through L_80048B58. The rest of the array (index pre segments: tick, snapshot,
get, validate; hit/miss/ival; record-index spread) is filled by rs64_s6963_pre in src/main/upstream_compat.cpp. Flushed per stream
call by rs64_s7023_cs -> [s7025-cl]. Usage: apply_s7025_clampsplit.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7025 clampsplit"
f = D / "funcs_10.c"; t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
t = t.replace('#include "funcs.h"\n', '#include "funcs.h"\nextern unsigned long long g_s7025[32]; extern int g_s7025_in; /* %s */\n' % TAG, 1)
S = "RECOMP_FUNC void clampGridCellLookup(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
i0 = t.index(S); i1 = t.index("RECOMP_FUNC", i0 + len(S)); body = t[i0:i1]
def brep(old, new):
    global body
    assert body.count(old) == 1, (old, body.count(old)); body = body.replace(old, new)
brep(S, S + "    const unsigned long long s7025_t = g_rs64_s7022 ? mach_absolute_time() : 0; unsigned long long s7025_c = 0, s7025_c0 = 0; /* %s */\n" % TAG)
brep("L_80048AC4:\n", "L_80048AC4:\n    if (s7025_t) { s7025_c = mach_absolute_time(); g_s7025_in = 1; } /* %s */\n" % TAG)
brep("    after_0:\n", "    after_0:\n    if (s7025_c) { const unsigned long long e0 = mach_absolute_time(); g_s7025[20] += e0 - s7025_c; s7025_c0 = e0; g_s7025_in = 0; } /* %s */\n" % TAG)
brep("    after_1:\n", "    after_1:\n    if (s7025_c) g_s7025[21] += mach_absolute_time() - s7025_c0; /* %s */\n" % TAG)
brep("L_80048B58:\n", "L_80048B58:\n    if (s7025_t) g_s7025[4]++; /* %s */\n" % TAG)
brep("L_80048B8C:\n", "L_80048B8C:\n    if (s7025_t) { const unsigned long long e = mach_absolute_time(); g_s7025[0]++; g_s7025[1] += e - s7025_t;"
     " if (s7025_c) { g_s7025[2]++; g_s7025[3] += e - s7025_c; } } /* %s */\n" % TAG)
t = t[:i0] + body + t[i1:]
# processGridCellByDistance: calls made inside a clamp create ([22]), and its sendServiceMessage call ([23] n, [24] ticks, [25] n inside create)
P = "RECOMP_FUNC void processGridCellByDistance(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
j0 = t.index(P); j1 = t.index("RECOMP_FUNC", j0 + len(P)); pb = t[j0:j1]
assert pb.count(P) == 1; pb = pb.replace(P, P + "    if (g_s7025_in) g_s7025[22]++; /* %s */\n" % TAG)
SS = "    sendServiceMessage(rdram, ctx);\n        goto after_2;\n"
assert pb.count(SS) == 1
pb = pb.replace(SS, "    { const unsigned long long s7025_s = g_rs64_s7022 ? mach_absolute_time() : 0; sendServiceMessage(rdram, ctx);"
    " if (s7025_s) { g_s7025[23]++; g_s7025[24] += mach_absolute_time() - s7025_s; g_s7025[25] += g_s7025_in; } } /* %s */\n        goto after_2;\n" % TAG)
t = t[:j0] + pb + t[j1:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
