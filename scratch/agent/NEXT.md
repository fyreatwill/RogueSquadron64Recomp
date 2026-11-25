# NEXT (s7948)
HYPOTHESIS-ID: owner-handoff-regression
s7947: handoff regression 4/4 PASS after the pad/panel work; wrapper tools/s7947_owner_handoff_all.zsh (planted-fail control).
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines, esp. s7947_handoff_fast
   (expect handoff_pass=1 control_fail_seen=1; a 0 in either = wrapper or gate regression -> name the commit, fix).
1. Every Next-steps item is closed or waiting on the owner. Agent-testable options, pick ONE:
   a. `python3 tools/s7651_gate_sweep.py` (--jobs 2): confirm 0 RED / 0 HOLLOW after s7941-s7947 (last full sweep predates the pad work).
      Hypotheses: H-green / H-red (a pad-work file tripped a census such as s7613 HP statics -> fix) / H-hollow.
   b. If green: take ladder 3c's first non-closed rung that does not need the owner; otherwise BLOCKED is NOT allowed (3c) —
      write the owner-waiting list into the session entry and do an M3 idiom-class audit instead.
