# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.
# NOTE: CURRENT-TRUTH is ~59 KB; if Step 0 prints >60000 do the maintenance iteration first.

# NEXT: G1e — late present command buffer (s6984): queue wait vs slow GPU execution. ONE build, ONE ABBA run.
HYPOTHESIS-ID: g1e-late-present
State (s6984, offline over 6 loaded arms): residual lates encode Q on time (VI->Q-end not larger, AUC 0.2-0.6); the present
pass's executeCommandLists+fence wait (Q gpu_ms) is 1.5-1.9 vs 0.36 ms (AUC 0.90-0.97) and Q->on-glass 30 vs 23 ms.
Hypotheses:
- H-gpuq: the present cmd buffer waits in the GPU queue behind the game workload or another process (WindowServer). Predicts
  GPUStartTime - commit large on lates, GPUEnd-GPUStart normal.
- H-gpuclk: the GPU executes slowly (clock/power budget shared with the CPU burst). Predicts GPUEnd-GPUStart inflated on lates,
  start delay normal; should also inflate the game workload's own cmd buffers.
- H-cpu-wait: the fence wait thread itself is descheduled (present thread default QoS). Predicts both GPU stamps normal, CPU
  wall of wait() inflated; fixed by present-thread QoS.
Instrument (lib/rt64 rt64_present_queue.cpp + plume metal; export.sh + commit): on the present cmd buffer read GPUStartTime/
GPUEndTime (CFTimeInterval, mach-based) and log them in the Q row as gs_ms (start - commit) and ge_ms (end - start); also the
present thread's QoS class. Arms: scratch/s6983/drive.sh (burst at ~120 s, GFX_QOS=1 GUEST_QOS=1), ABBA with
ROGUESQ_PRESENT_QOS (new, USER_INTERACTIVE on the present thread) off/on. Score with g1e_late_leg.py --sum (add gs/ge keys).
Positive control: gs+ge <= gpu_ms on every row; the burst gives ~25 lates/min.
