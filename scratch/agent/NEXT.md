# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e commit term: gate the default-on commit-side diagnostics, measure com by arm
HYPOTHESIS-ID: g1e-dd4-commit-diag
s6955 landed ROGUESQ_G1E_BATCH (default on): ranges per task 47.7k -> 184, wall -0.47 ms, but the commit term (~3.3 ms/task, where RT64
processDisplayLists runs) stayed flat, so its per-call scaling is per RDP command. Before profiling RT64, check the boring thing first:
rs64_dpc_defer_end_impl (src/rsp/dpc_bridge.cpp) runs, on EVERY commit, the s4272 latewrite per-word compare over the whole shadow
(~365k words per dd4 task), plus the s4280 SetColorImage attribution loops (linear scan of g_s4272_sh per event; with batching that's
only ~184 entries) and s4284 tallies. All of them are diagnostics: their output is stderr counters only.
Unit: ROGUESQ_G1E_CDIAG (default 0 = skip the latewrite compare loop and the s4280/s4284 block; =1 old; =tog 10 s blocks, latched at
defer_end). Hypotheses: H-diag (the latewrite loop is a measurable share of com: expect -0.2 to -0.6 ms/task) vs H-rt64 (com is RT64's
per-command work: flat). Discriminator: same-run tog, com and sd_wall per task by arm (tools/g1e_batch_arms.py, add a column for the
arm or reuse the batch column with ROGUESQ_G1E_BATCH fixed on). Positive control: the [s4272-latetot] line must stop advancing in off
blocks and advance in on blocks (cmpWords). If H-rt64: xctrace a 30 s windowed flight (XT=1) and rank RT64 functions under the commit.
Run: env OUT=scratch/s6956 zsh tools/g1e_xt_flight.zsh d 360 "ROGUESQ_G1E_AQ=3 ROGUESQ_G1E_CDIAG=tog ROGUESQ_G1E_TRING=$PWD/scratch/s6956/tring.txt"
If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
