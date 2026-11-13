# NEXT (s7269): fold s7268_169_split — why does 16:9 auto R=88 show little side gain?
HYPOTHESIS-ID: widewin-169-tv
State (s7268): 16:9 R=88 cost OK (10.92 ms 60/s). s7267 edge: 16:9 s88 L/R -0.2/-2.1 vs s7264 16:9 STACK=0 -3.8/-5.1 (cross-run);
21:9 R=88 right side swung -9.6 -> -3.6 between runs, so single-run side numbers are noisy (~6).
Fold: `python3 tools/s7268_edge_delta.py scratch/s7268e c219` (VOID unless c219 drops >=3 on a side -> re-queue).
Also s0 must show a 16:9 side gain (sum >= ~6), else the 16:9 gain is unmeasurable on this route.
Outcomes:
- H-noise: s88b side gain ~ s0 -> R=88 keeps the 16:9 gain; close thread: OWNER-OPT-INS 16:9 line, CT closed note, new slug.
- H-merge16: m88 ~ s0, s88b small -> merge eats 16:9 gain; make auto MERGE aspect-gated (main.cpp [s7258] block) and queue a 16:9
  cost check (MERGE=0 R=88 heavy window, w0d control) before landing as default.
- H-real16: s0 gain, m88 + s88b small -> R=88 still trims 16:9 sides; try aspect-dependent R (e.g. 16:9 R=104) with cost soak.
- Any crash -> backtrace first.
If the soak has not run (owner active): do not wait; take ladder 3c next open owner-look item (G5h cutscenes background at dd2/dd4).
