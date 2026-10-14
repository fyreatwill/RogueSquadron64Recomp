# Find what differed between s4794 (stalled 2/5) and s4799/s4800 (0/16)

HYPOTHESIS-ID: vi640-stall-trigger-delta

s4800: load 5-12 and ROGUESQ_LOG_SWAP_ACK_WAIT on/off are both ruled out as the sole trigger.
Hypotheses: H1 binary changed between s4794 and s4799 (rebuild/apply script); H2 s4794 recipe had
an env/arg or the `sample` call itself that perturbs; H3 stall depends on something outside the
recipe (ROM/save state, window focus, display). Discriminator: diff `scratch/agent/soak_results/s4793/`
recipe+env vs s4800, `git log --since=2026-10-13 -- tools lib submodule-patches build` and binary mtime
vs s4794 run time; then rerun the s4794 recipe verbatim 5x. If it still shows 0/5, the stall is not
currently reproducible: park the VI-640 thread and switch to M5-AUDIO-PLAN next step.
