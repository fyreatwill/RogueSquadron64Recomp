# NEXT (s7282): fold the GPU-contention pair, then next non-owner-gated rung
HYPOTHESIS-ID: g5c-gpu-contention
State: G5c QoS split CLOSED s7281 (GUEST+PRESENT = freezes on L4+L12; QOS_ALL +~2 fps under CPU load). Recommendation QOS_ALL=1, owner decides default.
Queued soaks (SOAK_NEEDS_IDLE=120): scratch/agent/soak_queue/s7281_l12_gpu_qos.sh (QOS_ALL=1), s7281_l12_gpu_none.sh (no QoS),
both LOAD=gpu (scratch/s7277/gpu_busy Metal saturator toggled every 60 s from +150 s), L12, owner PLAIN FS 16:9 recipe.
Baseline s7277 L12 gpu none: 16.6 fps on-load, off 60.0, no gaps >= 250, max 132 ms, gpu95 26 ms.
Hypotheses / outcomes:
  - H-gpu-share: both arms ~16-17 fps on-load -> the GPU timeslice is the limit; CPU QoS cannot help. Possible lever to try next:
    nothing in-process short of lowering our own GPU work (RESMULT/dd) - write it up for the owner, close.
  - H-cpu-feed: qos arm clearly higher (> ~25 fps) -> the saturator's driver/WindowServer threads were starving our submit threads; QOS_ALL covers it; add to OWNER-OPT-INS.
  - none arm not ~16.6 (e.g. 60) -> the saturator did not saturate this time (check gpu95 and the .gpu file); void, re-queue.
Fold: SOAK-RESULTS.md tail; scored output scratch/agent/soak_results/s7281_l12_gpu_*.log; witnesses printed at the end of each log.
If not run yet, do not babysit; take the next non-owner-gated rung. Do not change defaults without the owner.
