#!/usr/bin/env python3
"""s7024 G1c: per-branch time and counts inside getGridCellValueAt (0x80048508, funcs_10.c), same switch ROGUESQ_S7022_ST=1.
Branch id b (set at labels, accumulated at the single exit L_8004893C into g_s7024[{n,ticks,walk}][b]):
 1 clamp (L_80048554 -> clampGridCellLookup), 2 direct 0x8000-flag table hit (L_80048564 early return),
 3 node path fell through without a later tag (should be 0), 4 node path type-4 -> return 0, 5 free-head check reached (transient),
 6 free list empty -> return 0, 7 L_80048674 with 0x1E==0xFFFF (fresh: float write only), 9 0x1E!=0xFFFF (release old slot + float).
walk = node-list iterations at L_80048618. Flushed per stream call by rs64_s7023_cs -> [s7024-gv]. Measurement only.
Usage: apply_s7024_gvbranch.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7024 gvbranch"
f = D / "funcs_10.c"; t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
def rep(old, new, n=1):
    global t
    assert t.count(old) == n, (old[:70], t.count(old)); t = t.replace(old, new)
rep('#include "funcs.h"\n', '#include "funcs.h"\nextern int g_rs64_s7022; extern unsigned long long mach_absolute_time(void); extern unsigned long long g_s7024[3][10]; /* %s */\n' % TAG)
S = "RECOMP_FUNC void getGridCellValueAt(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
i0 = t.index(S); i1 = t.index("RECOMP_FUNC void clampGridCellLookup(", i0); body = t[i0:i1]
def brep(old, new):
    global body
    assert body.count(old) == 1, (old, body.count(old)); body = body.replace(old, new)
brep(S, S + "    const unsigned long long s7024_t = g_rs64_s7022 ? mach_absolute_time() : 0; int s7024_b = 3; unsigned s7024_w = 0; /* %s */\n" % TAG)
brep("L_80048554:\n", "L_80048554:\n    s7024_b = 1; /* %s */\n" % TAG)
brep("L_80048564:\n", "L_80048564:\n    s7024_b = 2; /* %s */\n" % TAG)
brep("L_800485C4:\n", "L_800485C4:\n    s7024_b = 3; /* %s */\n" % TAG)
brep("L_80048618:\n", "L_80048618:\n    s7024_w++; /* %s */\n" % TAG)
brep("    ctx->r2 = MEM_HU(ctx->r2, 0X6FC0);\n", "    ctx->r2 = MEM_HU(ctx->r2, 0X6FC0); s7024_b = 5; /* %s */\n" % TAG)
brep("L_8004866C:\n", "L_8004866C:\n    s7024_b = (s7024_b == 5) ? 6 : 4; /* %s */\n" % TAG)
brep("L_80048674:\n", "L_80048674:\n    s7024_b = 7; /* %s */\n" % TAG)
brep("    skip_2:\n", "    skip_2:\n    s7024_b = 9; /* %s */\n" % TAG)
brep("L_8004893C:\n", "L_8004893C:\n    if (g_rs64_s7022) { g_s7024[0][s7024_b]++; g_s7024[1][s7024_b] += mach_absolute_time() - s7024_t; g_s7024[2][s7024_b] += s7024_w; } /* %s */\n" % TAG)
t = t[:i0] + body + t[i1:]
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
