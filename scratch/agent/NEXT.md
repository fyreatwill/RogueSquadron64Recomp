# NEXT (s7410)
HYPOTHESIS-ID: fr1-callee-saved-preservation

s7409 closed class BS (H-consistent; tools/s7409_fodd_census.py + build_fodd live probe, L5 dd8/dd1 CONTROL PASS).
Fold the queued s7409_fodd_levels soak (L4/L7/L12) if it ran: pass = rc 0 (CONTROL PASS + H-consistent per level).
Class BT: callee-saved register preservation across the 7 hand-asm FR=1 routines (transformAndEmitFaceVertices,
evalCubicSplineAtTime, mat3x4Multiply, transformVec3ByMat34, rotateVec3ByMat3x3, quaternionToMat3x4, projectPointToScreen)
and the 3 FR=1 callees (fetchIndexedVertexPosition, fetchVertexPositionPrimary, normalizeVec3InPlace).
Model: callers are GCC FR=0 o32: f20,f22,..,f30 (64-bit pairs incl. the odd high word = f(N).u32h) plus s0-s8, sp, ra
must survive. In FR=1 the routine sees 32 independent regs: a write to f20.fl (= low word of the caller's f20 double) or to any
even callee-saved slot without sdc1 save / ldc1 restore clobbers the caller. Odd own slots (f21.u32l..) are invisible to FR=0
callers, so writing them is harmless.
1. Offline: per routine, list writes to f20-f31 (.fl/.d/.u32l/.u64) and r16-r23/r30/r29/r31, and the sdc1/ldc1 (sd/ld, sw/lw)
   save/restore pairs; row = preserved / clobbered-unsaved. Plant control: delete one ldc1 restore in a copy -> must flag.
2. Live (build_fodd pattern, own dir build_fsv, copy the owner save into build_fsv/saves!): snapshot f20-f30 .u64 + s-regs at
   entry, compare at every return; positive control: a planted post-return clobber of f20 every Nth call must be flagged.
3. Hypotheses: H-preserved (all rows saved/restored, live diffs 0), H-clobber-live (a live routine changes a callee-saved
   reg -> fix in a fixup script, export.sh if lib/), H-clobber-dead (only in never-called projectPointToScreen/quaternion paths).
