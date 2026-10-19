Single next work unit (s5591): fold s5589_plume_lldb_c and _d (queued; loop runs them; do NOT run the game yourself).
Commands: grep -n s5589 scratch/agent/SOAK-RESULTS.md ; cat scratch/agent/soak_results/s5589_plume_lldb_c/summary (and d) ; head -8 run1.game
Control: each boot needs a TITLE line (titles=N/3). a/b failed with getcwd EPERM under lldb (s5590).
Outcomes:
  - titles>0 and stop reason/CRASHMARK -> read bt, name writer of si_addr=0x58 deref, fix root cause.
  - titles=3/3 clean -> queue e f; after ~20 clean boots pivot to M6 mission-hold soaks.
  - Still getcwd failure -> loop-context (TCC) cause: use lldb attach (s5453 pattern) instead of launch.
HYPOTHESIS-ID: plume-title-extended-hold
