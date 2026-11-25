# NEXT (s7926)
HYPOTHESIS-ID: g5-owner-looks-standing
s7925 made the G5c transition pairing two-source (port MusyX wait `M` rows in the present ring, sweep row S7925_WAITPAIR).
Every ladder item is closed or awaiting the owner's look (CURRENT-TRUTH headline + Next steps).
0. `python3 tools/crash_reports.py --since 2026-11-24` first; a new report outranks everything. Fold any new SOAK-RESULTS line;
   a freeze_arms>0 verdict is a G5c datum: open its ring with tools/s7920_hold_class.py and name the hold.
1. Otherwise take the top open item of CURRENT-TRUTH "Next steps" that is not owner-gated, or another explicit
   "single-source" label in CURRENT-TRUTH that a second line could settle (grep -n single-source docs/CURRENT-TRUTH.md);
   if none, the first unclosed rung of ITERATION.md 3c (G6 order: G6a -> G6b -> G6c; all LANDED, owner-gated).
   Small open datum (harmless): retail's 8th MusyX wait (vi=4369, flight entry) has no port M row; rs64_s7925_wait_mark never
   prints a trailing fast= count, so "skipped" vs "< 0.05 ms" is undecided.
   Expected: either a code/tool change with a same-run control or a new crash/stall datum.
