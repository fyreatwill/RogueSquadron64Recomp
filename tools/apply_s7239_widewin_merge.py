#!/usr/bin/env python3
"""s7240 G1c: WIDEWIN far-terrain 2x2 merge mesh (design docs/WIDEWIN-MERGE-PLAN.md, s7239).
ROGUESQ_DD_WIDEWIN_MERGE=<frac> (opt-in, unset/0 = off): in renderFlatMeshFaceGroup, while the s7009 wide window is active, four flat
lod-2 TRI_GEN cells forming an aligned 2x2 block whose node dist2 are all >= (frac^2 * farcut 0x8009DEB4) are drawn as ONE quad:
the anchor (even x/V0, even z/V0) command is rewritten (corner heights rebased to the anchor's y origin, corner colours from the
partners, spacing 2*V0) and the three partner commands are dropped by taking the DL cursor +0x28 back. _MERGE_TOG=1: only on
rs64_tog_odd seconds (same [s7010-clk] anchor). One [s7239] tally line per phase every 2 s.
Hooks: H1 buildGridCellMeshForFace L_8004323C (elem -> dist2 host hash), H2 0x800113DC (pair the group's list), H3 0x80011884
(after the w9 store: capture the command of anchors/partners), H4 0x800119A8 (drop), H5 L_800119BC (patch the anchors).
ORIGIN: not a mitigation, an opt-in feature knob for the WIDEWIN cost-vs-coverage trade (no defect is being hidden).
Usage: apply_s7239_widewin_merge.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7239 widewin merge"

def body_patch(path, fn, edits, pre):
    t = path.read_text(errors="surrogateescape")
    if TAG in t: print(path.name, "already applied"); return
    i = t.index(fn); j = t.index("\nRECOMP_FUNC ", i + len(fn)); b = t[i:j]
    for a, r in edits:
        n = b.count(a)
        if n != 1: sys.exit("s7239: %s anchor count %d for %r" % (path.name, n, a[:60]))
        b = b.replace(a, r)
    t = t[:i] + pre + b + t[j:]
    path.write_text(t, errors="surrogateescape"); print(path.name, "applied", TAG)

body_patch(D / "funcs_9.c", "RECOMP_FUNC void buildGridCellMeshForFace(uint8_t* rdram, recomp_context* ctx) {\n",
    [("L_8004323C:\n", "L_8004323C:\n    if (g_rs64_s7239_on) rs64_s7239_node((uint32_t)MEM_W(0X14, ctx->r16) + 0x20u, (uint32_t)MEM_W(0X8, ctx->r16)); /* %s */\n" % TAG)],
    "extern int g_rs64_s7239_on; extern void rs64_s7239_node(uint32_t, uint32_t); /* %s */\n" % TAG)

body_patch(D / "funcs_4.c", "RECOMP_FUNC void renderFlatMeshFaceGroup(uint8_t* rdram, recomp_context* ctx) {\n",
    [("    // 0x800113DC: addiu       $v0, $v0, 0x8\n",
      "    if (g_rs64_s7239_on) rs64_s7239_group(rdram, (uint32_t)ctx->r17, (uint32_t)ctx->r16, g_rs64_ww); /* %s */\n"
      "    // 0x800113DC: addiu       $v0, $v0, 0x8\n" % TAG),
     ("    // 0x80011884: lw          $v1, 0x2C($s1)\n",
      "    if (g_rs64_s7239_act) rs64_s7239_cmd(rdram, (uint32_t)ctx->r16, (uint32_t)ctx->r7); /* %s */\n"
      "    // 0x80011884: lw          $v1, 0x2C($s1)\n" % TAG),
     ("    // 0x800119A8: addiu       $v0, $v0, 0x28\n    ctx->r2 = ADD32(ctx->r2, 0X28);\n",
      "    // 0x800119A8: addiu       $v0, $v0, 0x28\n"
      "    ctx->r2 = ADD32(ctx->r2, g_rs64_s7239_skip ? 0 : 0X28); g_rs64_s7239_skip = 0; /* %s */\n" % TAG),
     ("L_800119BC:\n", "L_800119BC:\n    if (g_rs64_s7239_act) rs64_s7239_end(rdram); /* %s */\n" % TAG)],
    "extern int g_rs64_ww, g_rs64_s7239_on, g_rs64_s7239_act, g_rs64_s7239_skip; /* %s */\n"
    "extern void rs64_s7239_group(uint8_t*, uint32_t, uint32_t, int); extern void rs64_s7239_cmd(uint8_t*, uint32_t, uint32_t); extern void rs64_s7239_end(uint8_t*);\n" % TAG)
