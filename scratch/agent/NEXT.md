# Next work unit: read s5406 lldb title-boot soak
HYPOTHESIS-ID: m6-title-boot-plume-sigsegv

Read scratch/agent/SOAK-RESULTS.md tail and soak_results/s5406_plume_lldb_title/summary.
- titles<8/10: lldb perturbs boot; null worthless, adjust (e.g. attach instead) and requeue.
- STOP in some run: read that run's `bt 30`; name the createFramebuffer caller and the
  writer of the null attachment texture (640 mode switch); fix root cause, not a guard.
- titles~10/10 and no STOP: crash did not recur (0/28 total); requeue with 20 boots and
  fall back to the keyed mission endurance (3 more runs, different mission content).
