#!/usr/bin/env python3
"""s7233 G1c: WIDEWIN-only distance limit (ROGUESQ_DD_WIDEWIN_R=<cells>, opt-in, unset/0 = s7009 as is).
s7232: WIDEWIN's extra triangles in the L4 21:9 heavy window are 42% zero-height and 58% tiny (+2557 tri/task for +42 kpx). This knob
skips a terrain cell in streamTerrainGridCellsByDistance when (a) the s7009 wide window is active this frame, (b) the cell lies outside
the retail-equivalent window (min(w,64) x min(d,64) placed by the same s6901 fwdwin rule), and (c) its centre is farther than R cells from
the eye. Skipped cells take the game's own empty-cell path (slot word cleared at 0x80043020), so the mesh builder sees no cell there.
_R_TOG=1: only on rs64_tog_odd seconds (xor8 split, [s7010-clk] anchor). Every non-empty wide cell is tallied by eye distance (8-cell
bins) into one [s7233] line per 512 stream calls, split by phase; the [g1cf] line carries wr=<R in force at the last stream call>.
ORIGIN: not a mitigation, a measurement/feature knob for the WIDEWIN cost-vs-coverage trade (no defect is being hidden).
Runs after apply_s7012_widewin_cap in RS64_REPLAY.  Usage: apply_s7233_widewin_r.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7233 widewin r"
f = D / "funcs_9.c"; t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
# 1. latch reset at binPolygon entry (s7009 resets g_rs64_ww there)
A = "    g_rs64_ww = 0; /* PATCH: s7009 widewin */\n"
assert t.count(A) == 1, t.count(A)
t = t.replace(A, A + "    g_rs64_s7233_r = 0; /* %s */\n" % TAG)
# 2. after the wide placement: hand the retail-equivalent window + eye to the host
A = "                if (rs64_g3e_on()) rs64_g3e_trace(15, (uint32_t)x0, (uint32_t)x1, (uint32_t)z0, (uint32_t)z1); } }\n"
assert t.count(A) == 1, t.count(A)
N = ("                if (ww7009) { const int32_t w64 = w < 64 ? w : 64, d64 = d < 64 ? d : 64; int32_t bx, bz; /* %s */\n"
     "                  bx = (int32_t)floorf(qx.f + kk6905 * dx - 0.5f * (float)w64); if (bx > px1 - w64) bx = px1 - w64; if (bx < px0) bx = px0;\n"
     "                  bz = (int32_t)floorf(qz.f + kk6905 * dz - 0.5f * (float)d64); if (bz > pz1 - d64) bz = pz1 - d64; if (bz < pz0) bz = pz0;\n"
     "                  rs64_s7233_win(bx, bx + w64, bz, bz + d64, qx.f, qz.f); }\n") % TAG
t = t.replace(A, N + A)
# 3. stream: non-empty cell path (L_80042D6C) -> skip to the empty-cell path when the host says so
A = "L_80042D6C:\n"
assert t.count(A) == 1, t.count(A)
t = t.replace(A, A + "    if (g_rs64_ww && rs64_s7233_cell((int32_t)ctx->r20 + (int32_t)MEM_W(0x2DB0, (int64_t)(int32_t)0x80130000), "
              "(int32_t)ctx->r30 + (int32_t)MEM_W(0x2DB8, (int64_t)(int32_t)0x80130000))) { ctx->r2 = ADD32(ctx->r22, ctx->r10); goto L_80043020; } /* %s */\n" % TAG)
A = '#include "funcs.h"\n'
t = t.replace(A, A + "extern int g_rs64_s7233_r; extern void rs64_s7233_win(int, int, int, int, float, float); extern int rs64_s7233_cell(int, int); /* %s */\n" % TAG, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
