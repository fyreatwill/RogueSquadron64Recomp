# NEXT (s7925)
HYPOTHESIS-ID: g5-owner-looks-standing
s7924 landed freeze_arms in the soak verdict line (G5c freezes now visible). Every ladder item is closed or awaiting the owner's look
(CURRENT-TRUTH headline + Next steps).
0. `python3 tools/crash_reports.py --since 2026-11-24` first; a new report outranks everything. Fold any new SOAK-RESULTS line;
   a freeze_arms>0 verdict is a G5c datum: open its ring with tools/s7920_hold_class.py and name the hold.
1. Otherwise take the top open item of CURRENT-TRUTH "Next steps" that is not owner-gated; if none, the first unclosed rung of
   ITERATION.md 3c (G6 order: G6a rumble -> G6b rebinding -> G6c stand-ins; check each item's state in CURRENT-TRUTH before work).
   Expected: either a code/tool change with a same-run control or a new crash/stall datum.
