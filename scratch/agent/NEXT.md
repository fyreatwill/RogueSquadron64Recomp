# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4879: dedup is default-on (0.99 synth entries/msg; AI-ring producer 1 per entry). Open question: does dedup change the startup-crash rate (1/3 DEDUP=1 vs 0/1 DEDUP=0, tiny sample)?
Unit: enqueue a soak recipe in scratch/agent/soak_queue/ that runs scratch/agent/run_s4878_dedup.sh with arm 1 and 0 x5 each sequentially (zsh, per-run copy of run.log, count SIGSEGV at spTaskSchedulerThread startup) and compare crash counts. Hypotheses: H-dedup-causes-crash (arm1 crashes >> arm0) vs H-known-intermittent (equal rates). Then pick next M5 de-stub step from docs/M5-AUDIO-PLAN.md.
