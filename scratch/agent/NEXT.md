# NEXT (s7720)
HYPOTHESIS-ID: sweep-scoring-audit

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green.

regen-replay-drift is CLOSED (s7719): fresh front == s7558 pristine, replay H-mirrored in BOTH directions (s7423 forward + new
--reverse, controls PASS), and tools/s7719_regen_gate.py now runs it inside the gate sweep (2.6 min, one CPU). Do not iterate it.

s7719 found a sweep SCORING hole: s7363/s7364/s7366 print "OPEN n" but exit 0 without --check, so the s7718 sweep scored
OPEN 19/22/6 as GREEN (fixed: ARGS now pass --check with an "OPEN 0" pattern). The same hole may exist elsewhere.
Unit: for EVERY gate the sweep runs, does rc 0 + its pattern actually imply "0 open"? One offline pass:
1. Fold scratch/s7719/sweep.txt (s7719 full sweep, in flight at commit; else run a fresh `python3 tools/s7651_gate_sweep.py --jobs 2`), list each GREEN gate's last output line.
2. Flag any GREEN whose output contains a nonzero open/unclassified/OPEN/RED/FAIL/MISMATCH count (regex over the captured tail,
   e.g. `\b(OPEN|open|unclassified|UNRESOLVED|FAIL)\D{0,3}[1-9]`), and any tool with a --check/--strict flag the sweep does not pass.
3. Each flagged gate: add ARGS (flag + pattern) so the count scores, then review its rows by hand (verdict TSVs) to GREEN.
Hypotheses: H-clean (s7363/4/6 were the only hollow GREENs), H-more (>=1 other GREEN hides a nonzero count / unused --check).
Positive control: the scanner must flag a planted copy of the s7718 sweep row `s7363_hostarr_census.py GREEN 0 ... OPEN 19`.
Standing check: `python3 tools/s7651_gate_sweep.py --jobs 2`. Owner defaults: never flip.
