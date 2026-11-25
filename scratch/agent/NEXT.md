# NEXT (s7935)
HYPOTHESIS-ID: g5-owner-looks-standing
s7934 closed the stat-only gate-input gap (gate_trace "stats", sweep keys them, manifest pins named ones; S7934_STATKEY).
0. `python3 tools/crash_reports.py --since 2026-11-25` first; a new report outranks everything. Fold new SOAK-RESULTS lines;
   a freeze_arms>0 verdict is a G5c datum (tools/s7920_hold_class.py on its ring).
1. Take the top open, not-owner-gated item of CURRENT-TRUTH "Next steps", or a "single-source" label a second line could
   settle; else the first unclosed rung of ITERATION.md 3c.
   Candidate (retained-input class, last loose end): the 7 allow-listed RED gates (s7433/5/6/7/8, s7441, s7723) lost their
   captures to the prune before s7893. Either regenerate the inputs (s7435-family = /usr/bin/sample of a live owner-recipe run:
   one game run, queue as a soak with SOAK_NEEDS_IDLE) and drop them from tools/gate_sweep_allowed_red.txt, or convert each
   to a control-only gate (planted input) and record that the live verdict is historical. Discriminator: does the regenerated
   capture reproduce each tool's recorded s74xx verdict (same busy-on/off share within its stated tolerance)?
   Prefer: dry-run the prune (`env DRY_RUN=1 KEEP_DAYS=2 bash ~/.local/bin/rs64-scratch-prune.sh`; grep gate inputs) as a
   cheap standing check after any new capture-reading gate lands.
