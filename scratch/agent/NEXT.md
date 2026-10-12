# Next work unit

HYPOTHESIS-ID: m5-a15-spin-yield-necessity

A14 is qualified (s4694). Next: A15, `ROGUESQ_SPIN_YIELD` (canonical recipes all
set it to 1; the plan says default off and "route control only"). Question: with
all A11-A14 yields/guards in place, is SPIN_YIELD=1 still required to reach
title+hangar, or is it masking another spin?

Hypotheses:
- H-A15-needed: SPIN_YIELD=0 stalls before title or hangar (VI/SI starvation);
  the remaining spin sites are named by a per-site row.
- H-A15-redundant: SPIN_YIELD=0 reaches title+hangar with the same VI counts
  (+/-10%); the flag can be retired as a default-off control.
- H-A15-route-absent: neither arm reaches hangar -> unevaluable.

Discriminating run (ONE build, arms concurrent, phase-gated on VI 1024/512 rows):
1. Add per-site hit/yield counters for each ROGUESQ_SPIN_YIELD site (grep
   `ROGUESQ_SPIN_YIELD` in src/ and tools/) logged at phase>=3, plus a
   positive control (SPIN_YIELD=1 arm must show yields > 0).
2. Reuse `scratch/agent/run_s4694_m5_a14_shutdown_boundary.sh`; replace the two
   arms with SPIN_YIELD=1 / SPIN_YIELD=0 (keep A14 yield on in both), drop the
   retail oracle (no new retail question). SIGKILL all, save to
   `scratch/agent/s4695_m5_a15_spin_yield/`.
3. Outcome table: VI rows at 1024 and 512 per arm, per-site spin counts, any
   timeout rows. Unexplained carry-over from s4694: yield-off arm lacked an
   `[m5-status-store]` 02->03 row at PC 0x8009B30C though slot0 read 03.
