# NEXT (s7213): mode-switch box census at 21:9 and 4:3: does any LIT frame get a stale-rs box?
HYPOTHESIS-ID: mode-switch-pillarbox
Context: s7212 closed the 16:9 L17 route: the only non-full viewport (`fb 796x444 vp 166,0 1028x764`) is ~8 presents of the stale
last-drawn target via vi-follow-draw mode=3 with flight-era rs (2.251,3.0); those presents are black 208-byte fill swaps -> invisible.
Hypotheses: H-fill-only (every stale-rs box at every aspect lands on fill/fade swaps: close the class); H-lit (some mode switch at 21:9 or
4:3, e.g. hangar -> intro, intro -> flight, flight -> ER, boot logos, shows a lit frame in a wrong box: fix computeHDSize box shape from
the present VI + current shared rs in rt64_vi_renderer.cpp, opt-out env, and rerun the arm).
Discriminator, 2 runs (one at a time): tools/s7141_arm.zsh with ROGUESQ_VI_SHAPE_LOG=1 ROGUESQ_G5B_FRAME_EVERY=100000 at
ROGUESQ_ASPECT=21:9 (CW/CH from the window) and at 4:3, full route, then: for each `[g1d-vishape-vp]` line whose vp does not fill the
window (and is not a 320-wide RDRAM upload, which is genuine 4:3 content), find its swap ([fbw]/[region-gate] swap#) and that swap's
RDP bytes in the s7098 index (208 = fill only). Lit (>1 KB) on any -> place a window capture over it (DL/DU from the swap mach time,
tools/s7212_pillar_scan.py <raw> x0 x1 <mach>; control must PASS) and fix. Delete raws afterwards.
