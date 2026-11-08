# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e target thread CLOSED (s6973: 10 final). G1e item 7 paused until owner tries ROGUESQ_VI_LOCK=1.
HYPOTHESIS-ID: g1e-vilock-isolated-drops
Take the next applicable item: the residual isolated drops under VI_LOCK (s6971 r2: 4 in 165 s; s6973 V10: 2 in one bin).
Hypotheses: H-drain (ACQ8 false-fires on a single slow acquire while locked: drop follows an acq>5 run of exactly 8),
H-hitch (a late game frame >6.7 ms over target, which the lock cannot absorb), H-gpu (frame GPU wait spike).
Offline first, no build: for each drop in scratch/s6972q/ring_V10.txt and scratch/s6971q ring files, print the 12 presents
before it (W, Q, acq, gpu, lat) with tools/g1e_present_split.py; the term that spikes before every drop selects.
If H-drain: raise ACQ trigger hysteresis while locked (lib/rt64 plume_metal.cpp, then submodule-patches/export.sh), queue an A/B soak pair.
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE, VI_LOCK stay opt-in, owner decides. VI_RT default on.
Owner reports override all of this.
