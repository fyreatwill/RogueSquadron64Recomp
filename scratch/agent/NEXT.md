# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: fold the s6972 16:9 lock-target pair (V10 vs V13), then hand the recipe to the owner
HYPOTHESIS-ID: g1e-submit-phase-lock
s6972: V10 vs V6 both 0 drops; V6 +4.0 ms (lat = const + 16.7 - W). Later target is the only side that can cut latency.
0. Fold soaks s6972_169_V10 / s6972_169_V13 (SOAK-RESULTS.md, scratch/s6972q):
   python3 tools/g1e_lock_arms_score.py V10=scratch/s6972q/ring_V10.txt --from 95 --locked V10 --target 10 --bins 15
   python3 tools/g1e_lock_arms_score.py V13=scratch/s6972q/ring_V13.txt --from 95 --locked V13 --target 13 --bins 15
   H-later-wins: V13 lat <= 21, slow% <= 1, drops <= V10+2 -> tell the owner TARGET_MS=13 saves ~3 ms; a 21:9 V13 arm must confirm before any recommendation change.
   H-edge-miss: V13 slow% > 2 or drops > V10+3 or W not ENGAGED near 13 -> game frames finish too close to the vsync edge; keep 10, close the target thread.
   rc 2 = human active: requeue the script from soak_queue/done.
1. Then G1e item 7 goes back to paused: owner tries the recipe; defaults stay off until the owner chooses.
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE, VI_LOCK stay opt-in, owner decides. VI_RT default on.
Owner reports override all of this.
