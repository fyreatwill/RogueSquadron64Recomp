# NEXT: G1c - H-fade: ROGUESQ_FORCE_FOG in-flight arm
HYPOTHESIS-ID: g1c-draw-distance
s6028: cell count (x0.25/x2) moved tri/task -8%/+8.7%, noise-level; not the extend lever. Remaining hypotheses: H-fade (haze hides distant terrain; test ROGUESQ_FORCE_FOG on lvl1 flight and measure distant-terrain pixel fraction in fixed-camera framebuffer), H-farplane (far-clip constant in terrain submit path; grep for it near buildVisibleTerrainGridAroundCamera), H-budget (DL/vertex caps).
Find how ROGUESQ_FORCE_FOG is wired (grep lib/ and tools/), queue a soak with it vs the retail control (s6027_ret recipe style, XENV_EXTRA), and compare the fbd framebuffer captures. Outcome: distant pixels change => fade is the limiter; no change => go far-plane.
