# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: same-run DRAIN trigger A/B, 40 vs 34 ms, owner dd4 recipe, locked 60 Hz built-in
HYPOTHESIS-ID: g1e-present-drain
s6950 (same run, 20 s toggle): DRAIN=40 lowers the post-stall level (lat p50 34.1 vs 37.2, 4/4 pairs) but on blocks keep acq>5 ms 16-30%,
because the formed level's median (36-38 ms) sits under the 40 trigger. Hypotheses: H-threshold (a trigger under the level median, 34,
clears it: ALT blocks acq>5% < 10 and p50 <= 30, with drops/block that stay few) vs H-reform (the level re-forms within ~1 s of any drop
whatever the trigger, so 34 only adds drops: ALT acq>5% still > 15 with drops/block >> 3) vs H-overdrain (34 fires on the clean baseline
~23-25 ms + peaks, dropping presents in clean blocks: drops in no-dose ALT blocks).
1. Check only the built-in is attached, owner idle > 120 s, screen unlocked (ioreg -n Root -d1 -a | grep CGSSessionScreenIsLocked prints nothing).
2. env ARMS="60:4:a34:ROGUESQ_PRESENT_DRAIN=40,ROGUESQ_PRESENT_DRAIN_TOGGLE=20,ROGUESQ_PRESENT_DRAIN_ALT=34+ST" zsh tools/g1e_owner_hz_arms.zsh
   (even blocks limit 40, odd blocks limit 34; build already carries ALT, s6950).
3. python3 tools/g1e_drain_blocks.py scratch/s6932/ring_a34.txt --from 95 --stall 110:17,124:17,138:17,152:50,166:50,180:50,194:200,208:200,222:200
   In this table on=1 means limit 40, on=0 means limit 34. Control: on=1 post-dose blocks must again show the partial level (acq>5% >15); if not, the run did not test anything.
If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md, g1e-present-drain section) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
