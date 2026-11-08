# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: acq-signature present drain trigger (21:9 over-drain)
HYPOTHESIS-ID: g1e-present-drain-acq
s6964: the 21:9 present level is the sticky drawable-queue level (acq_ms ~10-13 per present, frame GPU wait <=3.5 ms). ROGUESQ_PRESENT_DRAIN=34
clears it (3/3 same run) but in run d2 the base latency sat at ~35 ms (acq p50 1-2 ms, not the level) and the 34 trigger skipped ~1 frame/s for no gain.
1. Add ROGUESQ_PRESENT_DRAIN_ACQ=<N> in lib/rt64/src/contrib/plume/plume_metal.cpp rs64_present_drain_check (s6889/s6950 code near line 2121): drain one
   present only after N consecutive presents whose acquire wait > 5 ms (needs the previous present's acq: rt64_present_queue.cpp rs64PrAcq, pass it in
   or keep a static in plume). Keep the latency trigger as-is; ALT block logic so DRAIN_TOGGLE can A/B acq-trigger vs latency-34 in one run.
   Then ./submodule-patches/export.sh + commit (lib/ rule).
2. Run: env R=$PWD/scratch/s6965 HOLD=230 ARMS="4:a1:ROGUESQ_G1B=1+ROGUESQ_G1E_AQ=2+ROGUESQ_ASPECT=21:9+<acq vs 34 toggle env> 4:a2:<same>"
   zsh tools/g1e_owner_quiet_arms.zsh; score with tools/g1e_drain_blocks.py --from 100 and tools/g1e_present_split.py.
   Outcomes: acq blocks clear the level with ~0 D rows in a 35 ms-base run -> acq trigger replaces 34 in OWNER-OPT-INS; level reforms under acq ->
   latency is the needed signal, keep 34 and note the 21:9 cost; no level forms in either run -> null, rerun (needs a level block in off/other arm).
Owner reports override all of this. Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE stay opt-in, owner decides.
