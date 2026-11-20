# NEXT (s7718)
HYPOTHESIS-ID: gate-sweep-coverage

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
scratch/agent/CONTRACT-CARRY.md if it exists. If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay 8/8.

setenv-after-static-init is CLOSED (s7717: static + runtime H-clean; s7427 in the sweep via EXTRA_GATES). Do not iterate it.

s7717 found a closed-class gate (s7427) that had gone RED without anyone noticing, because the s7651 sweep only discovers
tools/s7*_census.py. Finish that coverage in ONE pass:
1. List every tools/*.py that prints a VERDICT or has a planted control (--control/--controls/--plant/--selftest) and is not in
   the sweep (s7717 list: scratch/s7717/unswept_gates.txt; widen it beyond s7* names: g5b_*, apply_* checkers, s6*).
2. Classify each: GATE (offline, deterministic: add to EXTRA_GATES + ARGS with a regex for control AND verdict), NEEDS-INPUT
   (needs a capture: keep one retained input under scratch/<sNNNN>/ the way s7658 did, or a NEEDS_INPUT row), REPORT (no
   verdict exit: REPORT row), DEAD (superseded: say by what, e.g. s7426 B-D by s7714/s7716).
   Known: s7421_regen_drift, s7423_live_stale, s7628_standins_sheet (positional input), s7431_stderr_volume (--control <v>),
   s7336_host_arena_table (no verdict exit).
3. Any newly swept gate that comes up RED is a real finding: review it like s7717 did the s7713 OSMEM row (benign -> reviewed
   accept row with the mechanism; real -> fix + two-arm witness).
Hypotheses: H-green (every unswept gate is green or merely needs input), H-drift (>=1 more closed class went RED unseen).
Positive control: the sweep's wiring control as in s7717 (remove one reviewed row -> RED, restore -> GREEN) for each new gate.
Standing check: `python3 tools/s7651_gate_sweep.py --jobs 2` (iron rule 0: never more than --jobs 2). Owner defaults: never flip.
