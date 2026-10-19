Single next work unit (s5589): fold s5587_plume_hold_d (b,c already folded in s5588: both TITLE+alive, 0 crash; total 3/3) (one title boot each, held 120 s). Loop runs them; do NOT run the game yourself.
Commands:
  grep -n s5587 scratch/agent/SOAK-RESULTS.md
  cat scratch/agent/soak_results/s5587_plume_hold_*/summary
Control: each run needs "TITLE" and "ALIVE_AT_+120" lines; otherwise null.
Prior: s5584 run1, hold_b, hold_c = TITLE+alive, no crash (N=3).
Outcomes:
  - Any CRASHMARK -> read backtrace in run1.game (main.cpp:10190), name writer of si_addr=0x58 deref, fix root cause.
  - 4/4 total alive, 0 crash -> plume thread closed; BLOCKED.md asking human: goal met or new target?
  - Soak absent again -> BLOCKED.md asking why loop skips soak_queue.
HYPOTHESIS-ID: plume-title-extended-hold
