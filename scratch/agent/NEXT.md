# NEXT (s7313): does the presented window lag the RDP stream on the first run after a rebuild?
HYPOTHESIS-ID: present-stale-after-rebuild
Datum (s7312, single instance): batch 1 arm l1f0 (first game run after a cmake rebuild of the main exe) froze at L1 pose 106.294,-6.799,69.769
with an RDP stream identical to s7310 d8 (swap 4063), but both window captures 1.5 and 2.2 s into the 15 s freeze showed another scene
(level craft over dark rock, not the banked craft against sky). The batch-2 repeat on the same binary (also first-after-rebuild!) matched s7310
pixel for pixel. Frames: scratch/s7312/a1/l1f0/f0_{1,2}.png vs scratch/s7312/b1/l1f0/f0_2.png. If the window can show a stale frame for
seconds, that may be part of the owner's "terrain drops" / "buffering" reports (G5b/G5c).
Hypotheses:
- H-shader: RT64 pipeline compile after a fresh binary (or first use of a material) holds presentation on an old frame. Predicts: stale frames
  cluster right after launch/new materials; the RT64 log shows pipeline creation around the freeze.
- H-capture: screencapture -l grabbed a stale WindowServer backing store (window not front/occluded). Predicts: the game's own presented
  framebuffer (RT64 readback / G5B present ring) at that moment is correct while the PNG is not.
- H-present-lag: RT64 presents frames late (queue backlog) under recorder I/O (MAX_MB 1600). Predicts: present stamps lag swap stamps by >1 s.
Discriminator, one build, one batch: L1 l1f0 recipe from scratch/s7312/run2.zsh x3 (same binary), each with ROGUESQ_PRESENT_RING (present wall
stamps vs swap mach stamps) and an in-game framebuffer dump at the freeze (check ROGUESQ_G5B_* / fbd options in tools/g3_optin_pose_arms.sh
callers), plus a window capture. Compare PNG vs in-game fb vs RDP stream per arm. First arm right after `touch src/main/rt64_render_context.cpp`
+ rebuild, to try to reproduce the batch-1 condition. If it never recurs in 3 arms + a positive control (a deliberately occluded window
capture should show the stale effect for H-capture), record it and close as non-reproducible.
Commands: env LEVEL=1 PIN=1 TAGP=s7313 FZ=106.28 zsh tools/g3_optin_pose_arms.sh scratch/s7313/a <arms>   (OUTDIR must be repo-relative)
Needs an unlocked screen and an idle host (the arms script checks both).
