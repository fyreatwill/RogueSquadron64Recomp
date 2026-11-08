# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: fold the s6970 16:9 replica pair, then hand the recipe to the owner
HYPOTHESIS-ID: g1e-submit-phase-lock
s6970: 16:9 dd4 FPS60, one run per arm: V (VI_LOCK=1, implied ACQ8) lat 23.3/24.6, slow% 0, 0 drops; N (ACQ8 alone) 20.2/36.5,
bimodal 20 vs 36 ms episodes, slow% 26, 8 drops. OWNER-OPT-INS now recommends VI_LOCK=1 at both aspects.
0. Fold soaks s6970_169_N_r2 / s6970_169_V_r2 (SOAK-RESULTS.md, scratch/s6970q):
   python3 tools/g1e_lock_arms_score.py N=scratch/s6970q/ring_N.txt V=scratch/s6970q/ring_V.txt --from 95 --locked V
   H-replicates: V slow% ~0, 0-2 drops, lat p50 ~23; N slow% > 10 or drops > 3 -> recommendation stands, two runs; close the 16:9 split.
   H-N-lucky-bad: N flat ~20 ms, slow% ~0, few drops -> ACQ8 alone is equal or better at 16:9 (3 ms lower p50); soften the
   OWNER-OPT-INS line to "LOCK for 21:9, either at 16:9" and note it.
   H-V-unstable: V shows slow% > 5 or drops > 3 -> try ROGUESQ_VI_LOCK_TARGET_MS=6 at 16:9 (queue an arm), the target may be aspect-specific.
   rc 2 = human active: requeue the script from soak_queue/done.
1. Then G1e item 7 goes back to paused: owner tries the recipe; defaults stay off until the owner chooses.
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE, VI_LOCK stay opt-in, owner decides. VI_RT default on.
Owner reports override all of this.
