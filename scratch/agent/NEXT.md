# NEXT (s7724)
HYPOTHESIS-ID: owner-looks-or-deferred-scorers

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green.

s7723 closed sweep-needs-input-retain: 11 of the 39 s7718 NEEDS-INPUT scorers are now sweep gates over their retained
scratch/ captures (S7723_RETAINED in tools/s7651_gate_sweep.py, .zst read via tools/rs64_zopen.py), with planted RED controls
in tools/s7723_retained_controls.py (11/11 PASS, itself a gate). Sweep 0 RED 0 HOLLOW.

Ladder: every engineering rung is closed or awaiting the owner's look (CURRENT-TRUTH Next steps 2-9). If no new crash report
and no owner report, the one remaining bounded offline unit is CURRENT-TRUTH item 32's deferred-retainable scorers (one
iteration, then stop scorer work for good):
1. s7433 + s7435-s7438: their input dirs (scratch/s7433, scratch/s7435) hold sample_*.txt.zst + samples.idx + run.tlog; teach
   the glob to accept *.txt.zst via tools/rs64_zopen.py, ARGS row with the CONTROL PASS + verdict regex.
2. s7367 (scratch/s7367 tl_v10.bin.* + v10/run.log.zst) and s7369 (tl_c1.bin.* + c1/): log read via zopen; check verdicts
   match the ledger (s7367 VERDICT CLEAN? / s7369 H-cycle2/H-slow) before adding a row; if a verdict has no control, classify
   H-no-control like s7391 instead.
3. s7467 (scratch/s7467r san_* + log_*.txt.zst), s7624 (fb_L1 + log_L1f.txt.zst --control), s7589 (hrH/hr.tsv + --warm/
   --plant-at from PORTING-STATE s7589).
4. Each new row gets a mutation in tools/s7723_retained_controls.py MUT (drop the control row -> RED). Sweep must end 0 RED 0 HOLLOW.
Owner defaults: never flip.
