# NEXT: 21:9 holes, the two classes left after s7134 (CURRENT-TRUTH item 29: (b) no-clear strip first, then (a) sky-side fill)
HYPOTHESIS-ID: g3-owner-recipe-219
State (s7134): sky-corner class = the sky-band mesh ends (H-skyband); culling is refuted (ROGUESQ_CULL_XFIX=1 and =all leave it intact).
The fix-off capture with both classes is scratch/s7134/Z1.cap (+ Z1.idx, Z1.rects, Z1r/ replays):
clear-class burst 7527-7537 (bottom-left sky), no-clear class 7558-7571 (right-edge beige ground strip, 0 clear rects).

Unit (b) first. Code read only, no build to start:
- Read 0x8005B51C (generated name setupWalkerSpriteTileQuad, funcs_13.c) from the s7133 patch point (0x8005B770) back to the branch
  that leaves the count at camera+0x74 = 0 (the 8005BC24..BC78 branches, the count += 2 at 0x8005BC88). Find the on-screen test
  that decides "horizon not on screen / whole screen is sky". Expect another use of the 0.75-scaled ndc_x (|ndc| < 1 against 4:3) or
  a pixel bound at w/2 in 4:3 units.
- Hypotheses: H-vis43 (that test uses the unscaled ndc_x, so at 21:9 a horizon that crosses the outer side band reads as off-screen
  and nothing is cleared); H-side (the builder has no branch for a horizon that enters through the left/right edge, only top/bottom,
  and 4:3 rarely hits it); H-other (the frames are a different state, e.g. a camera cut, and nothing would clear them in retail either).
- Discriminator: from the Z1 RAM snapshot nearest 7560 (G5B 'RAM ' block), recompute the three projected horizon points with the
  s7133 formula, at k = 1 and k = 2. If the k = 2 points cross the screen but the 0.75 path says they do not, that is H-vis43. Patch
  it in apply_s7133_horizon_x.py (same ROGUESQ_HORIZON_XFIX gate) and rerun the Z1 recipe:
  zsh tools/s7134_arm.zsh 6 X1 "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  then index (tools/s7098_rt64_vs_al.py index), replay (scratch/s7134/replay_F2.zsh pattern, 6 chunks), and score
  (tools/s7134_score.py X1 X1r.log X1.rects). Pass = no-clear swaps over 3000 px 13 -> 0, with the clear-class burst still present
  as the pose marker.
Unit (a) after: under ASPECT > 1, give the sky side a fill (one FillRect from the horizon line to the far edge in the fog/sky
colour that emitFrameRdpInitDl already uses for the ground rects). Opt-in first, then the same recipe; pass = clear-class swaps over
3000 px 11 -> 0, and 16:9 still 0. Owner sheet for both.
Owner save rule applies. CURRENT-TRUTH is 58.7 KB: keep edits net-zero.
