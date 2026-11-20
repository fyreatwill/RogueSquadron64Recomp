# NEXT (s7680)
HYPOTHESIS-ID: g6c-standin-near-release

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7679 released the one held ghost (L5 attract sub 0x32 "shield", spawned-but-never-drawn) with ROGUESQ_S7679_NEAR=15 (default in STANDINS).
Open questions, ONE run each at most:
1. Does the release fire anywhere in FLIGHT (it should not: in-flight held_dmin >= 28 in s7674/s7676)? Run the forced-level flight recipe
   used by s7675_ghost_L1/L4 (scratch/agent/soak_queue/done/s7675_ghost_*.sh) on L5 (the shield level, 0-based 5) with STANDINS_LOG=1:
   count [s7679-rel] lines and score with tools/s7675_ghost_score.py (rc 0 expected). H-flight-ghost (sub 0x32 also held near in flight,
   release fires) vs H-attract-only (0 releases). Positive control: ROGUESQ_S7679_NEAR=99 on the same run family must release many holds.
2. Residual shield 38->15: if a flight case exists, look at the 0x32 handler (0x8003D518) for the condition that keeps it from calling
   addNpcToVisibilityBucket (a hit/flash timer?) and exclude stand-ins while that condition holds, instead of a depth cut.
If both are clean, G6c waits on the owner's look; take the next ladder rung (G5 owner items awaiting look -> next open engineering rung).
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, no repeat-hold soaks.
