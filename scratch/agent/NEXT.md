# NEXT (s7710)
HYPOTHESIS-ID: owner-items-standing

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
scratch/agent/CONTRACT-CARRY.md if it exists. If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay 8/8 (s7709 gate).

The loop-tooling thread (s7708 carry, s7709 test gate) is closed. Take the first open G-rung in ITERATION.md 3c that is not
waiting only on the owner's look (CURRENT-TRUTH Next steps item 4 lists the owner-decision defaults; do not flip them).
Write the 2-4 hypotheses and the discriminating measurement here before building anything.
Standing check after any src/ or lib/ change: `python3 tools/s7651_gate_sweep.py --jobs 2` (expect 130 GREEN, 0 RED).
