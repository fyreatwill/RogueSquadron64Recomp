# NEXT (s7729)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then any
new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`).

Closed, do not repeat: s7726/s7727 Objective-C over-release (0 zombies both owner routes); s7728 reader-predicate splits
(truth census false/no + host LOG_ALL pass, 0+0 after the fix).

If nothing above applies, take the first open rung of the item-3c ladder per CURRENT-TRUTH Next steps (owner-look items are not
work units for the agent; pick a bounded engineering item instead). Candidate if nothing else: the 81 sites s7714 leaves
unmodelled (`python3 tools/s7714_truth_census.py --unmodelled`): classify them in one pass (model / opaque-by-design) so the
census covers every reader. Owner defaults: never flip.
