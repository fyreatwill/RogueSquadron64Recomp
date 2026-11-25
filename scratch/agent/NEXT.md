# NEXT (s7927)
HYPOTHESIS-ID: g5-owner-looks-standing
s7926 added ROGUESQ_S7926_WAITALL=1 (m row per MusyX wait call) + tools/s7926_wait_all.py and queued soak s7926_waitall (idle-gated).
0. `python3 tools/crash_reports.py --since 2026-11-24` first; a new report outranks everything. Fold new SOAK-RESULTS lines;
   a freeze_arms>0 verdict is a G5c datum (tools/s7920_hold_class.py on its ring).
1. If s7926_waitall ran: read the `s7926 control ...` line in scratch/agent/soak_results/s7926_waitall_*.log (or rerun
   `python3 tools/s7926_wait_all.py scratch/s7926_waitall/ring_q4.txt`). Control must read 6/6 PASS. SKIPPED = the port never
   calls waitForMusyXAudioTaskDone at flight entry (then check whether the retail call's gate 0x800A0F50 path is reached at all);
   FAST = the call happens but the gate is clear (no spin). Record it in CURRENT-TRUTH item 0a and close the datum.
2. Otherwise take the top open, not-owner-gated item of CURRENT-TRUTH "Next steps", or a "single-source" label a second line could
   settle (grep -n single-source docs/CURRENT-TRUTH.md); else the first unclosed rung of ITERATION.md 3c.
   Expected: a code/tool change with a same-run control or a new crash/stall datum.
