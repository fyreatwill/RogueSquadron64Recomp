#!/usr/bin/env python3
"""s7114 fps60-wall-lod fix arm: draw the terrain cells near the eye at the full 5x5 mesh the camera collision tests.

Why (s7114, tools/s7114_hsrc.py): the y-clamp sampler 0x80067D90 and the eye cell's TriGen read the SAME 25 height bytes (pointer
tl + 5 == params[2] on 10449/10449 joined ticks), and at lod 0 without edge options the drawn surface equals the collision surface
exactly. But buildGridCellMeshForFace (0x8004317C) overrides the distance tier with per-cell flags in mesh+0x14 (lhu a3 at
0x80043254): bit 3 forces lod 1 (TriGen0001, nodes 0/2/4 only) and bit 2 forces lod 2 (flat 4 corners), 0x8004332C..0x800433E0, so
near cells are drawn decimated (eye cell lod 1 on ~56% of ticks). The decimated surface leaves the collision surface by up to ~1 u in
the eye cell (per-tick cell max p50 0.20 u at lod 1) and every eye-cell near-plane loss in s7114 run a fell on such a cell.
ROGUESQ_S7114_NEARLOD=<r2>  (opt-in, unset/0 = retail): for nodes whose dist^2 (node+8, the tier metric) is < r2, clear a3 bits 3..2
  before the override, so they keep their distance tier (dist^2 < 16 = lod 0 with its geomorph weight). Sensible r2: 16 (the lod-0
  tier radius). Applies in flight and menus alike (it only refines terrain).
ROGUESQ_S7114_NEARLOD_TOG=1: apply only in odd absolute mach seconds (mach/24e6 & 1, the tools/s7108_split.py clock) for a same-run
  split. Note the bit-3 path also zeroes some bytes at mesh+0x55.. when *(0x80130B4C) & 0x08000000; skipping it skips those too.
ORIGIN: not a mitigation of a corrupt value; it disables a retail LOD decimation (game-authored per-cell flags) near the eye.
Idempotent; listed in fixup_game_funcs_vendored.py after apply_s7114_hsrc.py. Usage: apply_s7114_nearlod.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7114 nearlod"
f = D / "funcs_9.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("funcs_9.c s7114 nearlod already applied"); sys.exit(0)
FN = "RECOMP_FUNC void buildGridCellMeshForFace(uint8_t* rdram, recomp_context* ctx) {\n"
A = "L_8004332C:\n    // 0x8004332C: andi        $v0, $a3, 0x8\n"
i = t.index(FN); j = t.index("\nRECOMP_FUNC ", i + len(FN)); body = t[i:j]
assert body.count(A) == 1, body.count(A)
PRE = ('/* ' + TAG + ' */\n'
       'static float s7114_nl_r2(void) { static float r2 = -1.0f; static int tog = -1; extern uint64_t mach_absolute_time(void);\n'
       '  if (r2 < 0.0f) { const char* e = getenv("ROGUESQ_S7114_NEARLOD"); r2 = e && *e ? (float)atof(e) : 0.0f; if (!(r2 > 0.0f)) r2 = 0.0f;\n'
       '    const char* g = getenv("ROGUESQ_S7114_NEARLOD_TOG"); tog = g && *g && *g != \'0\'; if (r2 > 0.0f) fprintf(stderr, "[s7114] nearlod r2=%g tog=%d\\n", r2, tog); }\n'
       '  if (r2 > 0.0f && tog && !((mach_absolute_time() / 24000000ull) & 1)) return 0.0f; return r2; }\n')
L = ("L_8004332C:\n"
     "    { float r2 = s7114_nl_r2(); if (r2 > 0.0f) { union { uint32_t u; float f; } d; d.u = (uint32_t)MEM_W(8, ctx->r16); if (d.f < r2) ctx->r7 &= ~(uint64_t)0xC; } } /* " + TAG + " */\n"
     "    // 0x8004332C: andi        $v0, $a3, 0x8\n")
body = body.replace(A, L)
t = t[:i] + PRE + body + t[j:]
f.write_text(t, errors="surrogateescape"); print("funcs_9.c s7114 nearlod applied")
