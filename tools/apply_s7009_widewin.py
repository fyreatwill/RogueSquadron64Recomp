#!/usr/bin/env python3
"""s7009 G5e: let the dd>1 terrain window grow past 64 cells per axis (ROGUESQ_DD_WIDEWIN, opt-in, default off = old).
ORIGIN: the 64 limit is the game's table layout, not a choice: the per-cell height span tables min 0x80130DB0 / max 0x80131DB0 are
[64 rows][64 cols] bytes (index (row<<6)+col: scanConvertTriangleToSpanTable 0x80042610/0x80042758, binPolygonIntoTerrainGrid clear
0x80042A64, streamTerrainGridCellsByDistance 0x80042D3C) and the slot array 0x80132DC0 is [64][64] words (index (row<<8)+4*col: stream
0x80042D2C, buildGridCellMeshForFace neighbour reads 0x80043564/0x800435A8/0x800435DC/0x80043620/0x800436A8/0x8004370C). Columns are world x,
rows world z, fixed axes (s7009 code-read), so a 21:9 side face (s7008: 18-22 cells deep on 98% of calls) needs both axes to reach 128.
All 9 base sites and 11 shift sites live in those 3 functions (+ the two edge walkers, which keep their s6883 host spill for rows >= 80);
no other function in RecompiledFuncs addresses the tables. Pipeline order buildVisibleTerrainGridAroundCamera: binPolygon -> stream ->
meshBuild, so g_rs64_ww is latched in binPolygon (reset at its entry) and every later site of that frame follows it.
Wide layout (guest RAM above the 8 MB the game is told about, CPU-only, the RSP never reads these): min 0x83000000 [128][128] B, max
0x83004000, slots 0x83008000 [128][128] W (0x10000), end 0x83018000. The s6049/s6880 store bound, the s6882 x-narrowing and the s6883
cell bound (src/main/upstream_compat.cpp) follow g_rs64_ww. Window placement (s6901 fwdwin) per axis min(bounds, N) with
N = ROGUESQ_DD_WIDEWIN_N (64..128, default 128); the area cap (cell pool 0x80130C4C) is spent first on the forward axis down to 64, then on
the side axis down to 64, then the old rule. ROGUESQ_DD_WIDEWIN=1 on, =tog odd mach seconds (same-run control), unset/0 = old.
Trace: site 17 = ww, w, d, cap per placed window; site 18 = stream ran out of pool (a3, ww, row, col).
Runs after apply_s6908_poolmin in RS64_REPLAY.  Usage: apply_s7009_widewin.py [RecompiledFuncs dir]"""
import re, sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7009 widewin"
f = D / "funcs_9.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
MIN, MAX, SLOT = "0x83000000u", "0x83004000u", "0x83008000u"

def site(pc, old, new, want=None):
    global t
    pat = re.compile(r"(// 0x%s: [^\n]*\n\s*)%s" % (pc, re.escape(old)))
    n = len(pat.findall(t))
    assert n >= 1 and (want is None or n == want), (pc, n)
    t = pat.sub(lambda m: m.group(1) + new, t)

def gbase(reg, src, imm, wide):
    return "%s = g_rs64_ww ? (gpr)(int64_t)(int32_t)%s : ADD32(%s, %s); /* %s */" % (reg, wide, src, imm, TAG)

# 9 base sites
for pc, reg, src, imm, wide in [("800425D4", "ctx->r12", "ctx->r2", "0X1DB0", MAX), ("8004271C", "ctx->r12", "ctx->r2", "0XDB0", MIN),
                                ("80042A48", "ctx->r10", "ctx->r2", "0XDB0", MIN), ("80042A50", "ctx->r9", "ctx->r2", "0X1DB0", MAX),
                                ("80042CF0", "ctx->r13", "ctx->r2", "0X1DB0", MAX), ("80042D20", "ctx->r10", "ctx->r2", "0X2DC0", SLOT),
                                ("80042D48", "ctx->r14", "ctx->r14", "0XDB0", MIN), ("80043530", "ctx->r8", "ctx->r2", "0X2DC0", SLOT),
                                ("80043688", "ctx->r7", "ctx->r2", "0X2DC0", SLOT)]:
    site(pc, "%s = ADD32(%s, %s);" % (reg, src, imm), gbase(reg, src, imm, wide))
# 11 shift sites: span (<<6 -> <<7), slot rows (<<8 -> <<9)
for pc, reg, src, sh in [("80042610", "ctx->r9", "ctx->r5", 6), ("80042758", "ctx->r9", "ctx->r5", 6), ("80042A64", "ctx->r5", "ctx->r7", 6),
                         ("80042D3C", "ctx->r2", "ctx->r30", 6), ("80042D2C", "ctx->r22", "ctx->r30", 8),
                         ("80043564", "ctx->r2", "ctx->r2", 8), ("800435A8", "ctx->r2", "ctx->r2", 8), ("800435DC", "ctx->r3", "ctx->r6", 8),
                         ("80043620", "ctx->r3", "ctx->r6", 8), ("800436A8", "ctx->r2", "ctx->r2", 8), ("8004370C", "ctx->r3", "ctx->r6", 8)]:
    site(pc, "%s = S32(%s << %d);" % (reg, src, sh), "%s = S32(%s << (g_rs64_ww ? %d : %d));" % (reg, src, sh + 1, sh))
# s6049/s6880 store bound
pat = re.compile(r"\(uint32_t\)\(U32\((ctx->r\d+)\) - 0x80130DB0u\) >= 0x2000u")
n = len(pat.findall(t)); assert n >= 7, n
t = pat.sub(lambda m: "(uint32_t)(U32(%s) - (g_rs64_ww ? %s : 0x80130DB0u)) >= (g_rs64_ww ? 0x8000u : 0x2000u)" % (m.group(1), MIN), t)
# s6882 x narrowing
A = "((int64_t)(int32_t)ctx->r5 << 6) - (int64_t)(int32_t)0x80130DB0;"
assert t.count(A) == 2, t.count(A)
t = t.replace(A, "((int64_t)(int32_t)ctx->r5 << (g_rs64_ww ? 7 : 6)) - (int64_t)(int32_t)(g_rs64_ww ? %s : 0x80130DB0u);" % MIN)
A = "0x1FFF - rel"
assert t.count(A) == 4, t.count(A)
t = t.replace(A, "(g_rs64_ww ? 0x7FFF : 0x1FFF) - rel")
# latch reset at binPolygon entry
A = "RECOMP_FUNC void binPolygonIntoTerrainGrid(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n"
assert t.count(A) == 1
t = t.replace(A, A + "    g_rs64_ww = 0; /* %s */\n" % TAG)
# window placement
A = ("int32_t w = px1 - px0 < 64 ? px1 - px0 : 64, d = pz1 - pz0 < 64 ? pz1 - pz0 : 64, a; dx /= n; dz /= n; fw6901 = 1;\n"
     "                while (cap > 0 && w * d > cap && (w > 1 || d > 1)) { if ((fabsf(dx) >= fabsf(dz) && d > 1) || w <= 1) d--; else w--; }\n")
assert t.count(A) == 1, t.count(A)
N = ("const int ww7009 = rs64_s7009_arm(); const int32_t lim7009 = ww7009 ? rs64_s7009_n() : 64; /* " + TAG + " */\n"
     "                int32_t w = px1 - px0 < lim7009 ? px1 - px0 : lim7009, d = pz1 - pz0 < lim7009 ? pz1 - pz0 : lim7009, a; dx /= n; dz /= n; fw6901 = 1;\n"
     "                while (cap > 0 && w * d > cap && (w > 1 || d > 1)) { if (ww7009) { const int fx = fabsf(dx) >= fabsf(dz); int32_t* fa = fx ? &w : &d; int32_t* sa = fx ? &d : &w;\n"
     "                    if (*fa > 64) { (*fa)--; continue; } if (*sa > 64) { (*sa)--; continue; } }\n"
     "                  if ((fabsf(dx) >= fabsf(dz) && d > 1) || w <= 1) d--; else w--; }\n"
     "                g_rs64_ww = ww7009; if (rs64_g3e_on()) rs64_g3e_trace(17, (uint32_t)ww7009, (uint32_t)w, (uint32_t)d, (uint32_t)cap);\n")
t = t.replace(A, N, 1)
# pool exhaustion in stream
A = "    // 0x80042DDC: slt         $v0, $a3, $v0\n    ctx->r2 = SIGNED(ctx->r7) < SIGNED(ctx->r2) ? 1 : 0;\n"
assert t.count(A) == 1, t.count(A)
t = t.replace(A, A + "    if (ctx->r2 == 0 && rs64_g3e_on()) rs64_g3e_trace(18, (uint32_t)ctx->r7, (uint32_t)g_rs64_ww, (uint32_t)ctx->r30, (uint32_t)ctx->r20); /* %s */\n" % TAG)
# declarations
A = '#include "funcs.h"\n'
t = t.replace(A, A + "extern int g_rs64_ww; extern int rs64_s7009_arm(void); extern int rs64_s7009_n(void); /* %s */\n" % TAG, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
