# NEXT (s7932)
HYPOTHESIS-ID: g5-owner-looks-standing
s7931 settled s7928's route reading (two lines): same save -> port and retail take the same runVideoFrameTick caller sequence
(tools/s7931_route_pair.py, 6/6, controls pass); the 4-vs-3 menu gap was the save + FORCE pokes. MusyX wait thread fully closed.
0. `python3 tools/crash_reports.py --since 2026-11-25` first; a new report outranks everything. Fold new SOAK-RESULTS lines;
   a freeze_arms>0 verdict is a G5c datum (tools/s7920_hold_class.py on its ring).
1. Take the top open, not-owner-gated item of CURRENT-TRUTH "Next steps", or a "single-source" label a second line could
   settle (grep -n single-source docs/CURRENT-TRUTH.md: the remaining one is item 8 "rare dd4/dd8 gfx SIGBUS", owner-gated);
   else the first unclosed rung of ITERATION.md 3c.
   Candidate (s7931 side finding, class audit): s7928's row was in ARGS but not EXTRA_GATES, so it never ran. Enumerate every
   ARGS key in tools/s7651_gate_sweep.py that is neither a tools/s7*_census.py nor in EXTRA_GATES (python: set(ARGS) minus the
   swept set), classify each (add to EXTRA_GATES if its inputs are retained, else mark NEEDS-INPUT with a reason), and add a
   self-check to the sweep that fails when an ARGS row is unswept. Expected: a tool change with a planted-unswept control.
