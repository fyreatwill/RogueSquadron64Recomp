# NEXT: G3 texture/render fidelity at the OWNER recipe (dd4, 16:9, FPS60) with the fixed replay tool
HYPOTHESIS-ID: g3-owner-recipe-fidelity
Why: s7124 closed retail-settings flight fidelity (L1, L6) after fixing frame_replay.c's stale-snapshot bug. The owner plays
ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9; s7098 compared that recipe only for geometry drops, with the buggy
20-swap-stale snapshot (floor 0.043). Texture fidelity at the owner recipe is unmeasured.
Hypotheses:
  H-equal : with own snapshots, dd4 16:9 replays match RT64 to the retail floor (frac>40 median ~0.01-0.025, no region >=1000 px).
  H-wide  : the 16:9 / dd4 edits (HUD anchor walker, far terrain, sky z) render differently in RT64 vs angrylion: coherent blocks at
            the HUD, horizon band or far terrain.
  H-hi    : images above 8 MB (cimg 0x98AA00) or the >1024 width trip an RT64 texture/framebuffer path: whole-frame offsets or colour blocks.
Discriminator, one run: copy tools/s7124_arm.zsh and replace its XENV_EXTRA FPS60=0/DD=1 with the owner recipe
(ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9), EVERY=1 FROM=5000 MAX_MB=12000, L6 (and L4 if time). Window size changes:
re-derive the capture rect with tools/s7123_present_rect.py. Index with tools/s7124_capidx.py, replay with build16.sh's frame_replay16
(scratch/s7124/al16), score own vs SNAP_FROM=<first swap> (same-run control, must flag the radar block) with tools/s7122_fidelity.py,
sheet with tools/s7122_sheet.py. Note FPS60 doubles presented frames per swap: check the lag calibration picks the right one.
Delete the stream after replay (12 GB).
Outcomes: H-equal -> G3 closed at the owner recipe. H-wide/H-hi -> name the material/command and the walker that produced it.
