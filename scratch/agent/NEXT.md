# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

Read scratch/agent/SOAK-RESULTS.md tail for the s4880 verdict (soak_results/s4880/summary.txt).
- arm1 crashes >> arm0 (e.g. >=3 vs 0): dedup causes startup crash; inspect run_1_*.log crash frames, name the writer of the bad si_addr/x1, decide gate or rollback to default-off.
- Similar rates / both nonzero: crash is pre-existing; pull the crash register values from the logs and trace the writer (ORIGIN question) rather than guarding.
- reached_summary 0/5 on either arm: invalid, fix harness first.
Then pick the next M5 contract boundary from docs/M5-AUDIO-PLAN.md (steps 0-11 all qualified/closed; add step 12 for the next boundary).
