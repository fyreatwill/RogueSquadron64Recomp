#!/usr/bin/env python3
"""s7104 fps60-wall-terrain-cull: per-call keep/cull verdict of every terrain cell within +-3 cells of the eye in
streamTerrainGridCellsByDistance (funcs_9.c), written as 'cc' lines into the ROGUESQ_S7101_CHASE file (s7101_cf).

Static read (s7104) of the per-cell loop (col = s4/r20, row = fp/r30, span index a1 = col + row*64):
  E  0x80042D64  A == B == -128: the footprint polygon never covered this cell (empty sentinel) -> skip
  S  0x80042D8C/0x80042DA4  A < rec[3] or rec[4] < B (A = span byte 0x80130DB0+a1, B = 0x80131DB0+a1, rec = cell record
     *(t0+4) + (id & 0x1FFF)*30, signed bytes): the view pyramid's height span misses the cell's height range -> reject (0x7F)
  F  s7030 fog/off-map cull (our opt-in, bundled for dd>=6 only) taken on the reject edge
  C  0x80042DE0  kept count a3 reached the pool cap *(u16*)0x80130C4C -> that row ends (jumps to the row end 0x80043070)
  N  0x80042EA8  0x80048508(x, z, 1) returned 0 (no mesh/patch for the cell) -> 0x7E, uncounted
  K  0x80042EC8  inserted into the distance-sorted list
  .  not visited this call (outside the window x0..x0+w / z0..z0+d, or after a C)
The eye cell is floor(p.x), floor(p.z) with p = *(sp+0x80), the first argument: the eye in cell units, the same term the loop's
per-cell distance f20/f22 subtracts (0x80042CF8..D18, 0x80042BB8). Flushed at the epilogue L_80043138: 0x80043070 is only the row end
(the v1 instrument flushed there and logged one row per line, s7104 first run discarded).
Line: cc m=<mach> fc=<frame> e=<eye x,y,z> ec=<eye cell x,z> win=<x0,w,z0,d> kept=<a3> cap=<cap> n=<E,S,F,C,N,K whole window>
      g=<49 verdicts, row-major dz=-3..3, dx=-3..3> a=<A hex x49> b=<B> r3=<rec3> r4=<rec4>  (hex bytes, '..' if not visited)
Gate: ROGUESQ_S7104_CELL=1 and the CHASE file open. Measurement only, no behaviour change. Idempotent.
Positive control: the whole-window n= counts must show E and S verdicts firing in ordinary flight."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7104 cellcull"
FN = "RECOMP_FUNC void streamTerrainGridCellsByDistance(uint8_t* rdram, recomp_context* ctx) {\n"
PRE = (
    '/* ' + MARK + ' state */\n'
    'extern FILE* s7101_cf; static int s7104_en = -1, s7104_live, s7104_cur = -1, s7104_ex, s7104_ez; static uint32_t s7104_n[6];\n'
    'static char s7104_g[49]; static int8_t s7104_a[49], s7104_b[49], s7104_r3[49], s7104_r4[49]; static float s7104_e[3];\n'
    'static void s7104_visit(uint8_t* rdram, recomp_context* ctx) {\n'
    '  if (s7104_en < 0) { const char* e = getenv("ROGUESQ_S7104_CELL"); s7104_en = (e && *e && *e != \'0\') ? 1 : 0; }\n'
    '  s7104_cur = -1; if (!s7104_en || !s7101_cf) return;\n'
    '  if (!s7104_live) { s7104_live = 1; memset(s7104_g, \'.\', 49); memset(s7104_n, 0, sizeof s7104_n);\n'
    '    uint32_t ep = (uint32_t)MEM_W(0x80, ctx->r29); for (int q = 0; q < 3; q++) { uint32_t u = (uint32_t)MEM_W(4 * q, (int64_t)(int32_t)ep); memcpy(&s7104_e[q], &u, 4); }\n'
    '    s7104_ex = (int)floorf(s7104_e[0]); s7104_ez = (int)floorf(s7104_e[2]); }\n'
    '  int dx = (int32_t)ctx->r20 + (int32_t)MEM_W(0x2DB0, (int64_t)(int32_t)0x80130000) - s7104_ex;\n'
    '  int dz = (int32_t)ctx->r30 + (int32_t)MEM_W(0x2DB8, (int64_t)(int32_t)0x80130000) - s7104_ez;\n'
    '  if (dx < -3 || dx > 3 || dz < -3 || dz > 3) return; s7104_cur = (dz + 3) * 7 + dx + 3; s7104_g[s7104_cur] = \'V\';\n'
    '  s7104_a[s7104_cur] = (int8_t)ctx->r4; s7104_b[s7104_cur] = (int8_t)MEM_B(0, ADD32(ctx->r5, ctx->r13)); }\n'
    'static void s7104_mark(char v, int k) { if (!s7104_live) return; if (k >= 0) s7104_n[k]++; if (s7104_cur >= 0) s7104_g[s7104_cur] = v; }\n'
    'static void s7104_flush(uint8_t* rdram, recomp_context* ctx) {\n'
    '  if (!s7104_live) return; s7104_live = 0; s7104_cur = -1; if (!s7101_cf) return; extern uint64_t mach_absolute_time(void);\n'
    '  int64_t h = (int64_t)(int32_t)0x80132000; FILE* f = s7101_cf;\n'
    '  fprintf(f, "cc m=%llu fc=%u e=%.4g,%.4g,%.4g ec=%d,%d win=%d,%d,%d,%d kept=%d cap=%u n=%u,%u,%u,%u,%u,%u g=%.49s a=",\n'
    '    (unsigned long long)mach_absolute_time(), (uint32_t)MEM_W(0, (int64_t)(int32_t)0x8011A890u), s7104_e[0], s7104_e[1], s7104_e[2], s7104_ex, s7104_ez,\n'
    '    (int32_t)MEM_W(0xDB0, h), (int32_t)MEM_W(0xDB4, h), (int32_t)MEM_W(0xDB8, h), (int32_t)MEM_W(0xDBC, h), (int32_t)ctx->r7,\n'
    '    (unsigned)MEM_HU(0xC4C, (int64_t)(int32_t)0x80130000), s7104_n[0], s7104_n[1], s7104_n[2], s7104_n[3], s7104_n[4], s7104_n[5], s7104_g);\n'
    '  const int8_t* arr[4] = {s7104_a, s7104_b, s7104_r3, s7104_r4}; const char* nm[4] = {"", " b=", " r3=", " r4="};\n'
    '  for (int k = 0; k < 4; k++) { fputs(nm[k], f); for (int i = 0; i < 49; i++) { if (s7104_g[i] == \'.\' || (k >= 2 && s7104_g[i] == \'E\')) fputs("..", f); else fprintf(f, "%02x", (uint8_t)arr[k][i]); } }\n'
    '  fputc(\'\\n\', f); }\n'
)
# (anchor, replacement) pairs, applied inside the function body only
EDITS = [
    ("    ctx->r4 = MEM_B(ctx->r21, 0X0);\n    if (s6505_key) { /* PATCH: s6513 span filter */\n",
     "    ctx->r4 = MEM_B(ctx->r21, 0X0);\n    s7104_visit(rdram, ctx); /* " + MARK + " */\n    if (s6505_key) { /* PATCH: s6513 span filter */\n"),
    ("        g_s6493[4]++; if (s6505_key) s6513_nskip++; /* PATCH: s6493 streamcum */\n",
     "        g_s6493[4]++; if (s6505_key) s6513_nskip++; /* PATCH: s6493 streamcum */\n        s7104_mark('E', 0); /* " + MARK + " */\n"),
    ("    ctx->r2 = MEM_B(ctx->r3, 0X3);\n",
     "    ctx->r2 = MEM_B(ctx->r3, 0X3);\n    if (s7104_cur >= 0) { s7104_r3[s7104_cur] = (int8_t)MEM_B(ctx->r3, 0X3); s7104_r4[s7104_cur] = (int8_t)MEM_B(ctx->r3, 0X4); } /* " + MARK + " */\n"),
    ("L_80042DB0:\n", "L_80042DB0:\n    if (s7104_cur >= 0 && s7104_g[s7104_cur] == 'P') s7104_mark('F', 2); else s7104_mark('S', 1); /* " + MARK + " */\n"),
    ("L_80042DC4:\n", "L_80042DC4:\n    if (s7104_live) { if (s7104_cur >= 0) s7104_g[s7104_cur] = 'P'; } /* " + MARK + " */\n"),
    ("        g_s6493[3]++; /* PATCH: s6493 streamcum */\n",
     "        g_s6493[3]++; /* PATCH: s6493 streamcum */\n        s7104_mark('C', 3); /* " + MARK + " */\n"),
    ("    ctx->r2 = MEM_W(ctx->r16, 0X14); if (ctx->r2 == 0) g_s6493[9]++; /* PATCH: s6493 streamcum */\n",
     "    ctx->r2 = MEM_W(ctx->r16, 0X14); if (ctx->r2 == 0) g_s6493[9]++; /* PATCH: s6493 streamcum */\n    if (ctx->r2 == 0) s7104_mark('N', 4); /* " + MARK + " */\n"),
    ("L_80042EC8:\n", "L_80042EC8:\n    s7104_mark('K', 5); /* " + MARK + " */\n"),
    ("L_80043138:\n", "L_80043138:\n    s7104_flush(rdram, ctx); /* " + MARK + " */\n"),
]
p = BASE / "funcs_9.c"
t = p.read_text(errors="surrogateescape")
if MARK in t:
    print("funcs_9.c s7104 cellcull already applied"); sys.exit(0)
i = t.index(FN); j = t.index("\nRECOMP_FUNC ", i + len(FN))
body = t[i:j]
# s7420: the regen replay never applies the s6500-s6526 funcs_9 chain (env-gated observation, unwired since s6864), so the two
# s6513-bearing anchors fall back to their pre-s6513 text there; the hook lands on the same guest line either way.
FALLBACK = {
    EDITS[0][0]: ("    ctx->r4 = MEM_B(ctx->r21, 0X0);\n",
                  "    ctx->r4 = MEM_B(ctx->r21, 0X0);\n    s7104_visit(rdram, ctx); /* " + MARK + " */\n"),
    EDITS[1][0]: ("        g_s6493[4]++; /* PATCH: s6493 streamcum */\n",
                  "        g_s6493[4]++; /* PATCH: s6493 streamcum */\n        s7104_mark('E', 0); /* " + MARK + " */\n"),
}
for a, r in EDITS:
    n = body.count(a)
    if n != 1 and a in FALLBACK and "s6513" not in body:
        a, r = FALLBACK[a]; n = body.count(a)
    if n != 1: sys.exit("s7104: anchor count %d for %r" % (n, a[:70]))
    body = body.replace(a, r)
t = t[:i] + PRE + body + t[j:]
p.write_text(t, errors="surrogateescape")
print("funcs_9.c s7104 cellcull applied (%d edits)" % len(EDITS))
