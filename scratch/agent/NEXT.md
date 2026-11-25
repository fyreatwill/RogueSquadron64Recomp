# NEXT (s7931)
HYPOTHESIS-ID: g5-owner-looks-standing
s7930 only repaired s7929's exit contract (s7612 RG census: 5 diag-gated rows, 1 stale row dropped). s7929 only repaired s7928's exit contract (hostarr cnt[i&3]; SN scanner taint blind spot fixed, 17 rows added). The unit
below is unchanged and still open.
s7928 closed the MusyX wait thread: the port takes retail's flight-entry wait (mainGameLoop@0x8003E360, gate 1 in both); the
8-vs-6 count = B40 boot wait + one route-dependent menu transition. s7927 SKIPPED is superseded.
0. `python3 tools/crash_reports.py --since 2026-11-24` first; a new report outranks everything. Fold new SOAK-RESULTS lines;
   a freeze_arms>0 verdict is a G5c datum (tools/s7920_hold_class.py on its ring).
1. Take the top open, not-owner-gated item of CURRENT-TRUTH "Next steps", or a "single-source" label a second line could
   settle (grep -n single-source docs/CURRENT-TRUTH.md); else the first unclosed rung of ITERATION.md 3c.
   Candidate: the s7928 route-difference reading (port 3 menu transitions between initScenes vs retail 4) is single-source;
   settle it by driving the oracle with the port autopilot's press schedule (tools/g3_menu_pair.sh RP mapping) and
   re-running `tools/s7928_gate_writers.py <ring> --oracle <log>` (expect equal caller sequences except the B40 boot wait).
   Oracle note: use the HLE RSP (omit --rsp) and a time-sorted --press list, or retail stalls in the 640 intro.
   Expected: a code/tool change with a same-run control, or a new crash/stall datum.
