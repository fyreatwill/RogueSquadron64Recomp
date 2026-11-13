# NEXT (s7283): fold the GPU dose-response pair, then next non-owner-gated rung
HYPOTHESIS-ID: g5c-gpu-contention
State: s7282 H-gpu-share (QOS_ALL and none both 16.0 fps on-load under the 35.8 ms/cb saturator, 0 freezes). G5c stays closed.
Queued (SOAK_NEEDS_IDLE=120): scratch/agent/soak_queue/s7282_l12_gpu_i5000.sh and s7282_l12_gpu_i80000.sh (no QoS, GPU_ITER saturator).
Check first: the tail of each log prints the saturator's ms/cb (expect ~9 and ~143); if not, void.
Hypotheses / outcomes (on-load gen/s):
  - H-timeslice: ~16 in both -> fair GPU sharing; nothing in-process helps. Close thread, owner note already in OWNER-OPT-INS.
  - H-fifo: ~45-60 at i5000 and <~6 at i80000 (fps ~ 1/(k*ms_cb), k ~ 1.75) -> our frame waits behind ~k foreign buffers.
    Next: count RT64 MTLCommandBuffer commits per presented frame (lib/rt64 Metal backend) and test merging them, opt-in.
  - mixed (fps scales but not 1/cb) -> both; report k fit, do the commit count anyway (cheap).
Control: SIGSTOP 3/3 CAUGHT in each log; else void.
If not run yet, do not babysit; take the next non-owner-gated rung (CURRENT-TRUTH next steps; most are owner-look gated -> ITERATION 3c ladder).
Do not change defaults without the owner.
