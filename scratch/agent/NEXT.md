# NEXT: G1c phase 2 — next binding limit above dd4 on the owner path (21:9 WIDEWIN)
HYPOTHESIS-ID: g1c-dd-headroom
Context: s7018 closed gfx-host-glue (walks 0.2-0.45 ms/frame). Owner path L1 21:9 dd4 MELT WIDEWIN=1 CULL=1 runs 59.3-59.9 fps,
gfx rsp ~12.6 ms/frame. dd6/dd8 were qualified for crashes long ago (s6466/s6602, pre-WIDEWIN, pre-FAST) but never timed on the
owner path, and dd>4 needs ROGUESQ_DD_UNSAFE=1. DRAW_DISTANCE is a boot-time knob, so arms are separate runs (not same-run tog):
compare whole-run fps/rsp, not small deltas; the terrain-fraction scorer is phase-free enough for a flight hold.
Hypotheses: H-rsp-cliff (dd6/dd8 push rsp + run past ~16.7 ms -> P(>=2VI) > 0.1, fps < 50), H-pool (the 8192-cell WIDEWIN pool /
window caps the cell count so dd6/dd8 cost ~= dd4 and add no terrain), H-heap/crash (spill arena or gfx SIGBUS at dd8, s6466 att1),
H-free (dd6/dd8 hold 59+ fps with more far terrain -> offer in OWNER-OPT-INS).
Run: copy scratch/s7018/arm.zsh; arms dd4 (control), dd6, dd8 with "ROGUESQ_DD_UNSAFE=1 ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=1
ROGUESQ_G1E_TL=...", NOCAP unset for one framebuffer capture each (terrain fraction, tools/g5e_edge_score.py), L1 21:9 CULL=1, 320 s.
Report fps, rsp mean/p90, P(>=2VI), pool use (site 18), crash lines, terrain fraction per arm.
