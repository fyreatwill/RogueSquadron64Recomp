# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: does LOCK (+implied ACQ8) beat ACQ8 alone at 16:9 too?
HYPOTHESIS-ID: g1e-submit-phase-lock
s6969: at 21:9 LOCK+ACQ8 lat p50 23.4 vs ACQ8 alone 29.7 vs neither 39 (lvl 0/0/57%); LOCK alone 99% at level. ROGUESQ_VI_LOCK=1 now
implies DRAIN_ACQ=8 (=0 opts out; verified V1/V0 same build).
0. Fold soaks s6969_169_V / s6969_169_N (SOAK-RESULTS.md, scratch/s6969q): rows from tools/g1e_lock_arms_score.py --from 95.
   H-lock-helps-169: V lat p50 < N by >= 3 ms, both ~0% at level, drops comparable -> recommend ROGUESQ_VI_LOCK=1 in the owner recipe
   line in docs/OWNER-OPT-INS.md (both aspects). H-169-neutral: V ~ N (16:9 W already sits mid-interval, s6968 l1 before W 5.6, lat 27.7)
   -> recommend LOCK for 21:9 only, ACQ8 for 16:9. If V shows a level or many drops, test ROGUESQ_VI_LOCK_TARGET_MS=6 at 16:9
   (target may be aspect-specific: 16:9 RSP cost is lower).
   One run per arm: if the split is < 3 ms, requeue each once before concluding (soak queue, not a babysat run).
1. Then G1e item 7 resumes its paused state: ask the owner (OWNER-OPT-INS) to try the recipe; defaults stay off until the owner chooses.
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE, VI_LOCK stay opt-in, owner decides. VI_RT default on.
Owner reports override all of this.
