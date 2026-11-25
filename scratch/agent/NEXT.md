# NEXT (s7928)
HYPOTHESIS-ID: g5-owner-looks-standing
s7927 closed the s7925/s7926 datum: the port SKIPS retail's flight-entry MusyX wait (gate 0x800A0F50 == 0 at musyxNoopStub);
B40=1 restores one early wait only. Harmless, so it is parked unless the owner reports flight-entry audio trouble.
0. `python3 tools/crash_reports.py --since 2026-11-24` first; a new report outranks everything. Fold new SOAK-RESULTS lines;
   a freeze_arms>0 verdict is a G5c datum (tools/s7920_hold_class.py on its ring).
1. Take the top open, not-owner-gated item of CURRENT-TRUTH "Next steps", or a "single-source" label a second line could
   settle (grep -n single-source docs/CURRENT-TRUTH.md); else the first unclosed rung of ITERATION.md 3c.
   Expected: a code/tool change with a same-run control, or a new crash/stall datum.
