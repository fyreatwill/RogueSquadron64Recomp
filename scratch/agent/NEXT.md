# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: fold the s6971 16:9 lock-target pair (V10 vs V6), then hand the recipe to the owner
HYPOTHESIS-ID: g1e-submit-phase-lock
s6971: 16:9 replica agreed (V lock flat 23.3, slow% 0.4, 4 isolated drops; N ACQ8-alone 20.8/23.2 slow% 7.9, 5 drops). Lock stays
recommended at both aspects. V's 4 drops tripped the pre-registered drop test, so a target split is queued.
0. Fold soaks s6971_169_V10 / s6971_169_V6 (SOAK-RESULTS.md, scratch/s6971q):
   python3 tools/g1e_lock_arms_score.py V10=scratch/s6971q/ring_V10.txt --from 95 --locked V10 --target 10 --bins 15
   python3 tools/g1e_lock_arms_score.py V6=scratch/s6971q/ring_V6.txt --from 95 --locked V6 --target 6 --bins 15
   H-target-matters: V6 drops <= 1 and slow% ~0 while V10 drops >= 3 -> an earlier target absorbs the late frames at 16:9;
     consider the default target 6 (lat should fall ~4 ms too); a 21:9 V6 arm must confirm before changing it.
   H-noise: V6 and V10 drop counts within 2 of each other -> the isolated drops are drain noise; keep target 10, close the split.
   H-V6-worse: V6 slow% > 2 or not ENGAGED near 6 -> too close to vsync (frames miss the edge); keep 10.
   rc 2 = human active: requeue the script from soak_queue/done.
1. Then G1e item 7 goes back to paused: owner tries the recipe; defaults stay off until the owner chooses.
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE, VI_LOCK stay opt-in, owner decides. VI_RT default on.
Owner reports override all of this.
