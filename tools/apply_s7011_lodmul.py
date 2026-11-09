#!/usr/bin/env python3
"""s7011 G5e: coarser terrain LOD tiers at dd>1 (ROGUESQ_DD_LODMUL=<f>, opt-in, unset = no change).
Why: s7010 put the ROGUESQ_DD_WIDEWIN frame cost in the LLE gfx ucode (+3.6 ms/task), and the s7011 code-read shows the stream
(streamTerrainGridCellsByDistance 0x80042D50..0x80042DA8) already skips every cell whose frustum span is empty (-0x80) or misses the
cell's height range, i.e. the game culls cells to its own 3D view pyramid (eye 0x80130C10 + 4 far corners, 0x800439C0..A14) before
streaming. So the extra wide-window cells are inside the view and a 2D wedge cull cannot remove them; the remaining lever is fewer
triangles per cell. buildGridCellMeshForFace picks a mesh tier per node by dist^2 vs the 4 floats 0x8009DE94..A0 (s6417), and
s6421 showed scaling them up (finer) costs +14% RSP; this scales them DOWN (coarser sooner) by LODMUL in flight at dd>1.
ROGUESQ_DD_LODMUL_TOG=1 applies it on odd (mach/24e6) seconds only, same parity and [s7010-clk] anchor as WIDEWIN=tog, so
tools/g5e_cost_by_parity.py splits the run. Prints the original tiers once ([s7011] tiers=...).
ORIGIN: not a mitigation; a deliberate feature scale of a retail LOD constant table (fixed per s6417/s6418).
Runs after apply_s6418_farclip (needs its s6421 block) in RS64_REPLAY. Usage: apply_s7011_lodmul.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7011 lodmul"
f = D / "funcs_9.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "if (on6421) for (int i = 0; i < 4; i++) { union { uint32_t u; float f; } c; c.u = org6421[i]; if (me6036 != 1.0f && MEM_W(4, (int64_t)(int32_t)0x80136DC0) != 0) c.f *= me6036 * me6036; MEM_W(0, (int64_t)(int32_t)(0x8009DE94 + 4 * i)) = (int32_t)c.u; } } }\n"
assert t.count(A) == 1, t.count(A)
N = A + ("      { /* " + TAG + " */ extern float rs64_s7011_lodmul(void); extern int rs64_s7011_en(void); static uint32_t org7011[4]; static int got7011 = 0;\n"
     "        if (rs64_s7011_en()) { if (!got7011) { got7011 = 1; for (int i = 0; i < 4; i++) org7011[i] = (uint32_t)MEM_W(0, (int64_t)(int32_t)(0x8009DE94 + 4 * i));\n"
     "            union { uint32_t u; float f; } p[4]; for (int i = 0; i < 4; i++) p[i].u = org7011[i]; fprintf(stderr, \"[s7011] tiers=%g %g %g %g\\n\", p[0].f, p[1].f, p[2].f, p[3].f); }\n"
     "          const float m7011 = (me6036 != 1.0f && MEM_W(4, (int64_t)(int32_t)0x80136DC0) != 0) ? rs64_s7011_lodmul() : 1.0f;\n"
     "          for (int i = 0; i < 4; i++) { union { uint32_t u; float f; } c; c.u = org7011[i]; c.f *= m7011; MEM_W(0, (int64_t)(int32_t)(0x8009DE94 + 4 * i)) = (int32_t)c.u; } } }\n")
assert N.startswith(A)
N = A[:-len(" }\n")] + "\n" + N[len(A):] + "      }\n"  # keep the block inside the s6036 hook scope (me6036)
t = t.replace(A, N)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
