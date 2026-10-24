# NEXT: G1d step 2d - quantify the aspect lever, then widen the framebuffer
HYPOTHESIS-ID: g1d-widescreen
s6106 read k3p0/k0p4 dumps: 3D view visibly changes with ROGUESQ_ASPECT_SCALE (qualitative, scenes not phase-matched).
Work unit: queue 3 soaks (k=0.5, 1.0, 2.0) on lvl1 with same recipe as s6105, compare the SAME early frame index (phase-gate on first flight VI; fixed-camera intro) and measure width of a rigid object (craft/ring) per k; expect width ~ 1/k. Then ONE build widening game colour image/scissor/VI width under ROGUESQ_ASPECT=16:9 and a 16:9 window screenshot. Then HUD x anchoring (note ring HUD goes through the projection).
