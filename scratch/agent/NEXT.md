# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: overdrain floor, same-run DRAIN 34 vs ALT=28, owner dd4 recipe, locked 60 Hz built-in
HYPOTHESIS-ID: g1e-present-drain
s6951: DRAIN=34 clears the formed level (p50 23 vs off 39) with 6-7 drops per dosed block and ~12 early-run drops; 40 only lowers it.
Clean baseline here is p50 23-26, p99 27.6-29.5. Question: is 34 the right trigger, or does a lower one clear faster with no clean-block cost?
Hypotheses: H-floor (28 fires in clean blocks too: no-dose ALT blocks get drops > 2 per 20 s, so 34 is the floor) vs H-faster (28 clears the
level in fewer drops and keeps clean blocks at 0-1) vs H-same (28 and 34 indistinguishable: pick 34, the safer margin).
1. Only the built-in attached, owner idle > 120 s, screen unlocked (ioreg -n Root -d1 -a | grep CGSSessionScreenIsLocked prints nothing).
2. env ARMS="60:4:f28:ROGUESQ_PRESENT_DRAIN=34,ROGUESQ_PRESENT_DRAIN_TOGGLE=20,ROGUESQ_PRESENT_DRAIN_ALT=28+ST" zsh tools/g1e_owner_hz_arms.zsh
3. python3 tools/g1e_drain_blocks.py scratch/s6932/ring_f28.txt --from 95 --stall 110:17,124:17,138:17,152:50,166:50,180:50,194:200,208:200,222:200
Control caveat (s6951 a34): with both limits armed the level may never form, then dosed-block clear speed is untestable; the no-dose
clean-block drop count (blocks 3-7) still answers H-floor. If no level forms after 95 s, report H-floor only and do not rerun more than once.
If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md, g1e-present-drain section) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
