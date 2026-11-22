# NEXT (s7801)
HYPOTHESIS-ID: post-s7790-gate-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. 7 s7797 stand-in re-holds still queued (L2,3,6,7,8,9,18). Fold every verdict (pass = alive=1/1 crash_arms=0
stall_arms=0 and `s7797 Lx standins_on_line=1 spawns>0` in the log). Any crash/stall outranks the unit.

Unit: the G6c stand-in threads are closed apart from the owner's look (dd2 handoff H-clean L4/L1/L12, s7800). The tree has changed since the
last full gate run (s7693, pre-s7790 vendored-block prune). Rerun every closed gate on the current tree:
  python3 tools/s7651_gate_sweep.py --jobs 2 ; echo $?      # iron rule 0: never raise --jobs
  python3 tools/s7719_regen_gate.py --strict ; echo $?
Hypotheses: H-clean (all rc 0, BLIND=0) -> gates hold post-s7790; H-drift (a census reports a new site or a tool broke on the pruned
fixup file) -> classify it and fix the tool or the site this session; H-blind (a gate reads 0 because its input moved) -> check
each gate's positive control line in its output.
