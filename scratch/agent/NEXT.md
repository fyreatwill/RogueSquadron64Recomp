# NEXT (s7937)
HYPOTHESIS-ID: next-ladder-rung
s7936 closed retained-gate-inputs-regen: gate_sweep_allowed_red.txt is empty, s7723 CONTROLS PASS bad=0 skipped=0.
0. `python3 tools/crash_reports.py --since 2026-11-25` first; a new report outranks everything. Fold new SOAK-RESULTS lines
   (freeze_arms>0 = G5c datum, tools/s7920_hold_class.py on its ring).
1. s7936 full sweep DONE: 258 gates, 0 RED (scratch/s7936/sweep.log). Nothing to fix there.
2. Else: the gate/retention meta-thread (s7920-s7936) is done; stop adding gates. Take the first CURRENT-TRUTH Next-steps item
   that is not owner-gated, or the first unclosed ITERATION.md 3c rung that produces a game-side datum or code change
   (e.g. G1e frame-rate measurement per level if not closed, or the owner-parked rare dd4/dd8 gfx SIGBUS only on a side-effect hit).
   Write the 2-4 hypotheses + discriminator here before building.
