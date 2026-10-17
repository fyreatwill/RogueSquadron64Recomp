# Next: attribute the runtime writer of 0x9DEAC during the W hold
HYPOTHESIS-ID: m6-mission-input
Result s5077: floats at 0x9DEAC stop changing ~3.5 s after stick release (momentum). Static writers: 0x800448B0, 0x80045540, 0x8004562C, 0x80045658, 0x8004567C (swc1 -0x2154($v0), $v0=0x800A0000).
Hypotheses: Hpos (ship/flight code writes it) vs Hscroll (grid-layer scroll code only).
Unit: env-gated per-site counters added via the fixup script (not hand-edit), positive control = all five sites counted in W window; rerun scratch/agent/s5077_watch.sh once. Hscroll predicts only 0x8004562C/58/7C fire; Hpos predicts 0x800448B0/0x80045540 fire during W/D and not ctlA.
