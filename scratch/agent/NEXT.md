# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e batch contiguous DPC_END bumps (cut the submit call count that s6954 showed drives the dd4 tail)
HYPOTHESIS-ID: g1e-dd4-submit-batch
s6954 (scratch/s6954/split.txt): sd_wall ~ 101 ns/call + 2.4 ns/byte (R2 0.88); interpreter, rsp_dpc_submit and the task-end commit
each cost ~65 ns per DPC_END bump, flat per call; slow tasks = +19% calls, +2.7% bytes (~26-30 bytes, 3-4 RDP commands per call).
Unit: in src/rsp/dpc_bridge.cpp rsp_dpc_submit, when start == the pending range's end (and no wrap/shadow/prewrap/skyz/spike state
needs per-bump handling: read submit_impl first and list every per-call side effect), extend the pending range instead of calling
submit_impl; flush on non-contiguous start, DPC wrap, task end (before defer_end) and any reader of DPC_CURRENT. ROGUESQ_G1E_BATCH
default off until qualified, =tog flips every 10 s at [g1b] boundaries.
Hypotheses: H-percall (fewer calls -> submit+commit fall ~in proportion: expect -1.5 to -3 ms/task) vs H-percmd (cost is per RDP
command inside submit_impl/commit walkers, batching moves it, not removes it: sub+com flat) vs H-semantic (some bump needs its own
call: equivalence fails). Discriminator: same-run tog with ROGUESQ_G1E_TRING (AQ=3): sub+com per task and calls per task by arm.
Equivalence: hash of the byte stream handed to RT64 per task, on vs off, over a boot+flight (BATCH_CHECK=1 runs both paths? or
compare RDP command count + bytes per task by arm and frame captures). Positive control: calls per task must drop in on blocks.
Run: env OUT=scratch/s6955 zsh tools/g1e_xt_flight.zsh b 360 "ROGUESQ_G1E_AQ=3 ROGUESQ_G1E_BATCH=tog ROGUESQ_G1E_TRING=$PWD/scratch/s6955/tring.txt"
If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
