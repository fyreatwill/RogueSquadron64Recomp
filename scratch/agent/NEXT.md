# NEXT (s7891)
HYPOTHESIS-ID: g3-cinematic-half-frame-phase
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: G3 det render coverage CLOSED s7890 (19/19 missions render-exact on det ticks). The one render-level difference left
in every pair is pre-flight island A: the opening cinematic's 64 PRIM-FF tris are offset by 0.51 x per-frame speed - 0.016,
identical in p1 and p2 (m6 s7870, m11 s7871). Refuted: dt (s7872), snapshot value (s7873), raw clock + audio clock (s7874).
Parked s7874 by rule 8 with two hypotheses open. This unit is the ONE new discriminator between them, not another lever:
  H-index      the game's own cinematic state is half a frame off (frame-counter / spline-time origin differs): guest RAM differs.
  H-retail-rdp the guest state is equal and the oracle's RDP capture is taken half a frame late/early (harness): RAM equal, RDP differs.
Measurement (ONE port run + reuse the retained retail pair scratch/s7872/v10/r1, or one fresh oracle run if RAM words were not kept):
  per frame in the cinematic window, dump the cinematic camera/spline time word(s) from guest RAM on BOTH sides at the same
  point in the frame (the VI the gfx task is submitted). Find the word: the spline walker used by the opening cinematic
  (cinematicSplineWalkerNpcHandler / camera spline param; grep symbols) - confirm it moves monotonically through island A.
  Pair frames with the s7868 offset (-529 for v10). Outcomes: spline-time delta == 0.5 frame step on paired frames -> H-index
  (game state; then find the init-order of that counter); delta == 0 while RDP differs -> H-retail-rdp (oracle capture lag;
  fix the oracle's capture point, re-score island A). Positive control: plant a +1-frame shift in the port dump and require the
  comparator to report a 1.0-step delta. If neither (delta not 0 or 0.5): stop, write the table, close the slug as timing class.
Budget: this is iteration 4 on this slug overall but the first since parking; 1 iteration, then close either way.
Tools: tools/s7872_frame_clock.py (retail CPO1 trace pattern), scratch/s7870/phase_a.py (0.51 regression), tools/oracle/README.md.
