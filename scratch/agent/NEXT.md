# NEXT (s7802)
HYPOTHESIS-ID: g6c-standins-rehold-fold
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit.

Unit: fold the 5 still-queued s7797 stand-in re-holds (L3, L6, L7, L8, L9) as the loop runs them. Pass = loop line
alive=1/1 crash_arms=0 stall_arms=0, and in the log `tag=g1eq_rLx ... level_ok=1` + `s7797 Lx standins_on_line=1 spawns>0`
(`grep -E 'tag=|s7797 L' scratch/agent/soak_results/s7797_standins_rehold_Lx_*.log`). Once all 19 levels pass, G6c's "300 s holds on
all 19 levels with STANDINS=1" proof is complete: record it in CURRENT-TRUTH item 13 and OWNER-REVIEW-QUEUE (G6c item), then the
thread waits only on the owner's look.
Hypotheses: H-clean (5/5 pass) -> G6c hold coverage 19/19; H-crash (one dies) -> name the writer from its crash report /
backtrace before anything else; H-void (level_ok=0 or no standins line) -> the recipe, not the game: re-queue it.
If the soaks have not run yet, do not wait: take the next non-owner item (ITERATION.md 3c ladder; every rung is closed or
owner-judged, so pick an engineering audit with a commit, e.g. another NEEDS-INPUT/REPORT sweep row whose capture is retained).
