# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — residual late presents after PRESENT_QOS (s6985): the scheduled-handler present() hop vs compositor latch.
HYPOTHESIS-ID: g1e-late-present-hop
State (s6985): fence-wait tail = present thread wake, fixed by opt-in ROGUESQ_PRESENT_QOS=1 (lates 92/99 -> 50/75 ABBA).
Residual lates: Q on time, gpu_ms 0.68, but Q->on-glass 31.7 vs 23.2 ms. In plume_metal.cpp MetalSwapChain::present the
drawable is presented from presentBuffer->addScheduledHandler (drawableMtl->present() on a Metal dispatch thread).
Hypotheses:
- H-hop: the scheduled handler (default-QoS dispatch thread) runs late under load, so present() misses the vsync latch.
  Predicts sh = (handler entry - presentBuffer commit) inflated on lates; fixed by presentBuffer->presentDrawable(drawable)
  (encoded, no CPU hop).
- H-latch: present() is called on time but the compositor/WindowServer latches a vsync late (WindowServer busy under load).
  Predicts sh normal on lates; presentDrawable arm no help.
- H-gpu-tail: the present buffer's own GPU completion comes after the latch deadline (ge of presentBuffer).
Instrument: in MetalSwapChain::present stamp commit time, scheduled-handler entry (sh) and presentBuffer GPUEnd (pe);
write them into the existing P row (or a new S row keyed by presentId/mtl). Arm ROGUESQ_PRESENT_ENCODED=1:
presentBuffer->presentDrawable(drawableMtl) instead of present() in the scheduled handler.
Run: copy scratch/s6985/drive.sh to scratch/s6986, all arms PRESENT_QOS=1, ABBA E0 E1 E1b E0b with ENCODED off/on.
Score: scratch/s6985/score.sh pattern + sh/pe keys in tools/g1e_late_leg.py.
Positive control: sh > 0 on every non-skip present; burst gives 50-75 lates/arm.
