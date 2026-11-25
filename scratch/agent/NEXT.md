# NEXT (s7936)
HYPOTHESIS-ID: retained-gate-inputs-regen
s7935 re-captured the profiler inputs (scratch/s7935): s7433/5/6/7/8 + s7441 GREEN, dropped from tools/gate_sweep_allowed_red.txt.
0. `python3 tools/crash_reports.py --since 2026-11-25` first; a new report outranks everything. Fold new SOAK-RESULTS lines;
   a freeze_arms>0 verdict is a G5c datum (tools/s7920_hold_class.py on its ring).
1. Last allow-listed RED: s7723_retained_controls.py (inputs scratch/s7392/run, s7393/own, s7394/ownfix, s7396/own, s7397/own,
   s7399/own run.log; pruned 2026-11-23). Read each tool's PORTING-STATE entry (grep '^## Session 739[2-9]') for its launcher
   (e.g. tools/s7392_mq_run.zsh, keyed s7386 route => SOAK_NEEDS_IDLE if it drives keys), re-run ONE game run per input
   sequentially (iron rule: one game at a time), copy logs into scratch/s7936/<tool>/, point the S7723_RETAINED rows at them.
   Discriminator: each report reproduces its recorded verdict (control PASS + same class counts as the s739x entry).
   Hypotheses: H-repro (all reproduce -> rows re-pointed, allow-list empty); H-drift (a class count moved -> name the change
   since s739x that moved it, as s7935 did for rs64_s7463_hash, before re-pinning); H-route (keyed route fails -> queue soak).
2. Else take the top open, not-owner-gated CURRENT-TRUTH Next-steps item or the first unclosed ITERATION.md 3c rung.
