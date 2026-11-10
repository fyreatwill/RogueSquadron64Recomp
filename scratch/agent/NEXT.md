# NEXT: FPS60 near-wall flicker: log the y-clamp inputs, and add a same-run fix arm for the push vs y-clamp fight
HYPOTHESIS-ID: fps60-wall-camera
Context (s7102, single run, 1 episode): in applyPlayerVehicleStateUpdate 0x8004CD00 the corner push (corners 0-2) and the
y clamp after the loop (0x8004CFD4..0x8004D04C: h = 0x80067D90(x=+0x4C, z=+0x54, 0x80138058, out sp+0x78); if h - y < +0xB8
then y = out.y - +0xB8) alternate tick by tick at the episode ("flips" push/all-miss/push: 105 per 1000 ticks in the episode vs 3.2
lim1 / 0.8 lim2 in flight). Corner 3 is not involved (H-corner4 not supported). x,z of the clamp sample is the matrix copy
+0x4C/+0x54, refreshed only on hit ticks (stale on miss ticks).
First fold soak results s7102_push_r1/r2 (scratch/s7102/corner_r*.txt, fight_r*.txt, split_r*.txt): more episodes for the
CAM4 split and the flip rate per lim.
Unit (one build, one run, scratch/s7099/arm.zsh 6 4 <tag> "... ROGUESQ_S7101_CHASE=<file>" 120 240):
 1. Extend tools/apply_s7102_pushlog.py yf/pe lines with h (f0 after 0x80067D90), out point sp+0x78..0x80, margin +0xB8, the
    sample x,z (+0x4C/+0x54) vs pos x,z (+0x10/+0x18), and whether the branch was taken (log on both sides).
 2. Fix arm ROGUESQ_S7103_CAMFIX=tog (30 s halves), candidates chosen from the logged inputs:
    (a) sample the clamp at pos x,z (+0x10/+0x18) instead of the stale matrix x,z;
    (b) run the corner push again after the clamp moves y (so the clamp never leaves the near plane in the wall).
    Default off = retail.
Hypotheses:
 H-stale  the clamp samples the ground at a stale x,z (miss ticks), so h is wrong -> (a) removes the flips
 H-squeeze  the gap between ground+margin and the wall is narrower than the near-plane push, so no position satisfies both -> (a) does
           not help, (b) does (the push wins and the clamp cannot leave the near plane inside the wall)
 H-retail  the same flips happen at lim2 at the same per-tick rate (pooled with the r1/r2 soaks) -> it is retail behaviour that 60 fps only shows more often
Outcomes: flips/1000 ticks and episodes per CAMFIX half; owner before/after frames if an arm wins. Default stays retail.
