#!/usr/bin/env python3
"""s7022 G1c: per-call host timing of streamTerrainGridCellsByDistance (funcs_9.c), ROGUESQ_S7022_ST=1 (off = one global test).
Splits each call into setup (entry -> L_80042CD4, before the row loop) and loop (L_80042CD4 -> return), counts outer rows
(L_80042CF8) and inner cells (L_80042D3C), and buckets by the s7012 tog3 cap phase. Printed as [s7022-st] by rs64_s7022_st
(src/main/upstream_compat.cpp). Measurement only, no behaviour change. Usage: apply_s7022_streamtime.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7022 streamtime"
f = D / "funcs_9.c"; t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
def rep(old, new, n=1):
    global t
    assert t.count(old) == n, (old[:70], t.count(old)); t = t.replace(old, new)
rep('#include "funcs.h"\n', '#include "funcs.h"\nextern int g_rs64_s7022; extern unsigned long long mach_absolute_time(void); '
    'extern void rs64_s7022_st(unsigned long long t0, unsigned long long t1, unsigned long long t2, unsigned it, unsigned rw); /* %s */\n' % TAG)
S = "RECOMP_FUNC void streamTerrainGridCellsByDistance(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n"
rep(S, S + "    const unsigned long long s7022_t0 = g_rs64_s7022 ? mach_absolute_time() : 0; unsigned long long s7022_t1 = 0; unsigned s7022_it = 0, s7022_rw = 0; /* %s */\n" % TAG)
i0 = t.index(S); i1 = t.index("RECOMP_FUNC void buildGridCellMeshForFace(", i0); body = t[i0:i1]
def brep(old, new):
    global body
    assert body.count(old) == 1, (old, body.count(old)); body = body.replace(old, new)
brep("L_80042CD4:\n", "L_80042CD4:\n    if (g_rs64_s7022) s7022_t1 = mach_absolute_time(); /* %s */\n" % TAG)
brep("L_80042CF8:\n", "L_80042CF8:\n    s7022_rw++; /* %s */\n" % TAG)
brep("L_80042D3C:\n", "L_80042D3C:\n    s7022_it++; /* %s */\n" % TAG)
brep("    // 0x80043174: jr          $ra\n    // 0x80043178: addiu       $sp, $sp, 0x80\n    ctx->r29 = ADD32(ctx->r29, 0X80);\n    return;\n",
     "    if (g_rs64_s7022) rs64_s7022_st(s7022_t0, s7022_t1, mach_absolute_time(), s7022_it, s7022_rw); /* %s */\n"
     "    // 0x80043174: jr          $ra\n    // 0x80043178: addiu       $sp, $sp, 0x80\n    ctx->r29 = ADD32(ctx->r29, 0X80);\n    return;\n" % TAG)
t = t[:i0] + body + t[i1:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
