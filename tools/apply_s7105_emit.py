#!/usr/bin/env python3
"""s7105 fps60-wall-mesh-emit: does every terrain cell near the eye that the stream keeps (s7104 'K') reach the CPU emit of an F5
TRI_GEN, and with which LOD byte? Writes 'ce' lines into the ROGUESQ_S7101_CHASE file (s7101_cf). Needs ROGUESQ_S7104_CELL=1 (eye cell).

Static read (s7105):
  buildGridCellMeshForFace 0x8004317C (a0 = distance list head, walked via node+4; a1 = out chain-start slot). Per node: LOD tier from
    node+8 dist^2 vs table 0x8009DE94 (0x800431E0..0x80043294), lod byte a2 -> elem+0x10 (elem = *(node+0x14) + 0x20), morph shorts
    elem+0x16..0x1E, buildGridCellMesh 0x8004B930, then the render chain link elem+0 / elem+4 (0x800434B0..0x80043518); the chain is cut
    at the first node under the far cutoff 0x8009DEB4 and that element becomes the chain start (*a1, returned in s5/v0).
    Post pass 0x80043528..0x80043770 forces lod 1 on neighbours of lod-2 cells (seam fix). Node +0xC/+0x10 are window-relative col/row
    (bounds *(0x80132DB4)/*(0x80132DBC)); absolute = + *(0x80132DB0) / *(0x80132DB8).
  renderFlatMeshFaceGroup 0x8001108C: s0 = *(s1+0x20), loop L_800113F0 .. 0x800119A4 s0 = *(s0+0): EVERY element writes one 0x28-byte
    TRI_GEN (0x05) command (height path L_80011714 for lod != 2, flat 4-corner path for lod 2 + flat flags). There is no per-cell cull
    in this CPU loop. renderUnlitMeshFaces 0x80011C9C: same walk, emits only elements with +0x2E bit 1 (and clears it).
So a near cell can only miss the CPU emit by (a) not being in the list, (b) not being on the chain the renderer walks, or (c) the
renderer walking a different chain. Hooks:
  X  bgcmf exit L_80043780: flush the previous generation's record, then rebuild the 7x7 near table (ring<=3 around the s7104 eye cell)
     from the list (walked both ways from a0), and walk the chain from s5 via +0 marking near elements found on it.
  R  renderFlatMeshFaceGroup start (0x800113D8, s0 = *(s1+0x20)): call count, and whether the start equals the chain start.
  V  per emitted element (rfm 0x800119A4 with v0 = cmd; rum after the 0x8001207C store with a3 = cmd): visit count, w0 of the cmd.
Line: ce m=<mach at build> fc=<frame> gen=<n> ec=<x,z> nl=<list nodes> ch=<chain len> rc=<rfm calls> rs=<rfm calls starting at the
  chain start> rv=<rfm visits> uv=<rum visits> lod=<hist lod0,1,2,other over the whole list> g=<49 x 4 hex: dup count, lod, on-chain,
  visits(cap 15), row-major dz=-3..3 dx=-3..3> w=<w0 of the last emitted cmd for the 9 ring<=1 cells, '........' if none>
Gate: ROGUESQ_S7105_EMIT=1, ROGUESQ_S7104_CELL=1 and the CHASE file open. Measurement only. Idempotent.
Positive control: lod= must show more than one tier (far cells drop to lower tiers), rv > 0 with rs > 0, and the far ring-3 cells must
carry lower-detail lod bytes than ring 0."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7105 emit"

PRE9 = (
    '/* ' + MARK + ' state */\n'
    'int g_s7105_on = -1; uint32_t g_s7105_el[49], g_s7105_w0[49], g_s7105_start, g_s7105_rc, g_s7105_rs, g_s7105_rv, g_s7105_uv;\n'
    'uint8_t g_s7105_vis[49];\n'
    'static uint8_t s7105_dup[49], s7105_lod[49], s7105_ch[49]; static uint32_t s7105_gen, s7105_nl, s7105_chn, s7105_fc, s7105_h[4];\n'
    'static int s7105_ex, s7105_ez, s7105_have; static unsigned long long s7105_m;\n'
    'static void s7105_exit(uint8_t* rdram, recomp_context* ctx) {\n'
    '  if (g_s7105_on < 0) { const char* e = getenv("ROGUESQ_S7105_EMIT"); g_s7105_on = (e && *e && *e != \'0\') ? 1 : 0; }\n'
    '  if (!g_s7105_on || !s7101_cf || s7104_en != 1) return; extern uint64_t mach_absolute_time(void);\n'
    '  if (s7105_have) { FILE* f = s7101_cf;\n'
    '    fprintf(f, "ce m=%llu fc=%u gen=%u ec=%d,%d nl=%u ch=%u rc=%u rs=%u rv=%u uv=%u lod=%u,%u,%u,%u g=", s7105_m, s7105_fc, s7105_gen,\n'
    '      s7105_ex, s7105_ez, s7105_nl, s7105_chn, g_s7105_rc, g_s7105_rs, g_s7105_rv, g_s7105_uv, s7105_h[0], s7105_h[1], s7105_h[2], s7105_h[3]);\n'
    '    for (int i = 0; i < 49; i++) fprintf(f, "%x%x%x%x", s7105_dup[i] > 15 ? 15 : s7105_dup[i], s7105_lod[i] & 15, s7105_ch[i] ? 1 : 0, g_s7105_vis[i] > 15 ? 15 : g_s7105_vis[i]);\n'
    '    fputs(" w=", f); for (int dz = -1; dz <= 1; dz++) for (int dx = -1; dx <= 1; dx++) { int i = (dz + 3) * 7 + dx + 3;\n'
    '      if (g_s7105_vis[i]) fprintf(f, "%08x", g_s7105_w0[i]); else fputs("........", f); if (dz != 1 || dx != 1) fputc(\',\', f); }\n'
    '    fputc(\'\\n\', f); }\n'
    '  s7105_gen++; s7105_have = 1; s7105_m = (unsigned long long)mach_absolute_time(); s7105_fc = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x8011A890u);\n'
    '  memset(g_s7105_el, 0, sizeof g_s7105_el); memset(g_s7105_vis, 0, 49); memset(g_s7105_w0, 0, sizeof g_s7105_w0); memset(s7105_dup, 0, 49);\n'
    '  memset(s7105_lod, 0xF, 49); memset(s7105_ch, 0, 49); memset(s7105_h, 0, sizeof s7105_h); g_s7105_rc = g_s7105_rs = g_s7105_rv = g_s7105_uv = 0;\n'
    '  s7105_ex = s7104_ex; s7105_ez = s7104_ez; s7105_nl = 0; s7105_chn = 0;\n'
    '  int64_t h = (int64_t)(int32_t)0x80132000; int x0 = (int32_t)MEM_W(0xDB0, h), z0 = (int32_t)MEM_W(0xDB8, h);\n'
    '  uint32_t st = (uint32_t)MEM_W(0x38, ctx->r29);\n'
    '  for (int ps = 0; ps < 2; ps++) { uint32_t nd = ps ? (st ? (uint32_t)MEM_W(0x0, (int64_t)(int32_t)st) : 0) : st;\n'
    '    while (nd >= 0x80000000u && nd < 0x84000000u && s7105_nl < 40000) { int64_t nb = (int64_t)(int32_t)nd; s7105_nl++;\n'
    '      uint32_t mesh = (uint32_t)MEM_W(0x14, nb); uint8_t lv = (mesh >= 0x80000000u && mesh < 0x84000000u) ? (uint8_t)MEM_BU(0x30, (int64_t)(int32_t)mesh) : 0xEE;\n'
    '      s7105_h[lv < 3 ? lv : 3]++;\n'
    '      int dx = (int32_t)MEM_W(0xC, nb) + x0 - s7105_ex, dz = (int32_t)MEM_W(0x10, nb) + z0 - s7105_ez;\n'
    '      if (dx >= -3 && dx <= 3 && dz >= -3 && dz <= 3) { int i = (dz + 3) * 7 + dx + 3; s7105_dup[i]++; g_s7105_el[i] = mesh + 0x20; s7105_lod[i] = lv; }\n'
    '      nd = (uint32_t)MEM_W(ps ? 0x0 : 0x4, nb); } }\n'
    '  g_s7105_start = (uint32_t)ctx->r21;\n'
    '  for (uint32_t e = g_s7105_start; e >= 0x80000000u && e < 0x84000000u && s7105_chn < 40000; e = (uint32_t)MEM_W(0, (int64_t)(int32_t)e)) {\n'
    '    s7105_chn++; for (int i = 0; i < 49; i++) if (g_s7105_el[i] == e) s7105_ch[i] = 1; }\n'
    '}\n'
)
PRE4 = (
    '/* ' + MARK + ' externs */\n'
    'extern int g_s7105_on; extern uint32_t g_s7105_el[49], g_s7105_w0[49], g_s7105_start, g_s7105_rc, g_s7105_rs, g_s7105_rv, g_s7105_uv;\n'
    'extern uint8_t g_s7105_vis[49];\n'
    'static inline void s7105_visit(uint8_t* rdram, uint32_t el, uint32_t cmd, int un) {\n'
    '  if (g_s7105_on != 1) return; if (un) g_s7105_uv++; else g_s7105_rv++;\n'
    '  for (int i = 0; i < 49; i++) if (g_s7105_el[i] == el) { if (g_s7105_vis[i] < 255) g_s7105_vis[i]++; g_s7105_w0[i] = (uint32_t)MEM_W(0, (int64_t)(int32_t)cmd); } }\n'
)
FN9 = "RECOMP_FUNC void buildGridCellMeshForFace(uint8_t* rdram, recomp_context* ctx) {\n"
E9 = [("L_80043780:\n", "L_80043780:\n    s7105_exit(rdram, ctx); /* " + MARK + " */\n")]
FNR = "RECOMP_FUNC void renderFlatMeshFaceGroup(uint8_t* rdram, recomp_context* ctx) {\n"
ER = [("    // 0x800113D8: lw          $s0, 0x20($s1)\n    ctx->r16 = MEM_W(ctx->r17, 0X20);\n",
       "    // 0x800113D8: lw          $s0, 0x20($s1)\n    ctx->r16 = MEM_W(ctx->r17, 0X20);\n"
       "    if (g_s7105_on == 1) { g_s7105_rc++; if ((uint32_t)ctx->r16 == g_s7105_start) g_s7105_rs++; } /* " + MARK + " */\n"),
      ("    // 0x800119A4: lw          $s0, 0x0($s0)\n",
       "    s7105_visit(rdram, (uint32_t)ctx->r16, (uint32_t)ctx->r2, 0); /* " + MARK + " */\n    // 0x800119A4: lw          $s0, 0x0($s0)\n")]
FNU = "RECOMP_FUNC void renderUnlitMeshFaces(uint8_t* rdram, recomp_context* ctx) {\n"
EU = [('    _rogue_unlit_mesh_tracer_check("C", ctx->r16, 0X0);\nL_80012080:\n',
       '    s7105_visit(rdram, (uint32_t)ctx->r16, (uint32_t)ctx->r7, 1); /* ' + MARK + ' */\n'
       '    _rogue_unlit_mesh_tracer_check("C", ctx->r16, 0X0);\nL_80012080:\n')]

def patch(path, pre, fns):
    t = path.read_text(errors="surrogateescape")
    if MARK in t:
        print(path.name, "s7105 emit already applied"); return
    first = None
    for fn, edits in fns:
        i = t.index(fn); j = t.index("\nRECOMP_FUNC ", i + len(fn)); body = t[i:j]
        for a, r in edits:
            n = body.count(a)
            if n != 1: sys.exit("s7105: %s anchor count %d for %r" % (fn[:50], n, a[:70]))
            body = body.replace(a, r)
        t = t[:i] + body + t[j:]
        first = i if first is None else min(first, i)
    t = t[:first] + pre + t[first:]
    path.write_text(t, errors="surrogateescape")
    print(path.name, "s7105 emit applied")

# funcs_9: state must follow the s7104 statics (s7104_en/ex/ez) defined before streamTerrainGridCellsByDistance
p9 = BASE / "funcs_9.c"; t9 = p9.read_text(errors="surrogateescape")
if "PATCH: s7104 cellcull" not in t9: sys.exit("s7105: needs apply_s7104_cellcull first")
if t9.index("static int s7104_en") > t9.index(FN9): sys.exit("s7105: s7104 state is not before buildGridCellMeshForFace")
patch(p9, PRE9, [(FN9, E9)])
patch(BASE / "funcs_4.c", PRE4, [(FNR, ER), (FNU, EU)])
