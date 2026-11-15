# NEXT (s7381)
HYPOTHESIS-ID: host-spin-wait

s7380 closed class AV (condvars) as H-shutdown: 0 in-play lost wakeups; 9 destructor stop notifies + 3 start races fixed.

Work unit: class AW, every host busy-wait / spin loop that polls another thread's state (src/, lib/rt64/src,
lib/N64ModernRuntime/ultramodern, plume Metal backend; contrib except plume excluded). Known instances: RT64
WorkloadQueue::advanceToNextWorkload and PresentQueue::advanceToNextPresent (`do { lock; check barrier } while` with no
yield), RasterShaderCache::setup (activeCount spin), any `while (!flag) {}` / `while (x.load() ...)` / sleep_for(0) polls in
the port (events.cpp, rsp/dpc bridge, audio).
Per site: what it waits for, which thread sets it, pure spin / yield / sleep(N) / bounded, whether it can run during play,
and measured hit rate + spin time (one counter build: iterations and wall us per site, dumped per 10 s).
Hypotheses: H-idle (spins exist but never iterate in play: 0 cost), H-burn (>=1 spin iterates in play and burns a P-core:
convert to condvar/yield, measure VI and frame time before/after), H-starve (a spin holds a mutex the setter needs).
Discriminator: census tool tools/s7381_spin_census.py (--check exits 1 on an unreviewed row; --controls plants a pure spin
that must be flagged) + one counter build (env ROGUESQ_S7381_SPIN=1, default off) smoke run
`env SECS=260 zsh scratch/s7326/run.zsh s7381_spin 'ROGUESQ_S7381_SPIN=1'`; positive control: a site forced to spin
(advanceToNextWorkload with a 1-slot barrier under ROGUESQ_S7381_SPIN_CTL=1) must show iterations > 0.
Any H-burn row: fix with a condvar or yield (env gate =0 old), smoke both arms, TSan via scratch/s7379/tsan_run.zsh.
