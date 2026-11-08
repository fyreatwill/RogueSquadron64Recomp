# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: DRAIN=28 vs off, same run, owner dd4 recipe, locked 60 Hz built-in (does 28 clear a formed level faster than 34 did?)
HYPOTHESIS-ID: g1e-present-drain
s6952: 34 vs ALT=28 same run formed no level (limits armed in every block), so 28's clearing was untestable; 28 costs nothing on clean blocks.
s6951 o34 design (34 vs off, toggle 20 s, stall course) formed the level in off blocks after 200 ms doses (p50 38.6/39.4) and 34 cleared it
(p50 23.0/23.1, 6/1 drops in the first dosed-after block). Repeat that design with 28 so 28 has its own same-run off control.
Hypotheses: H-faster (28 blocks right after a formed off block reach p50 <= 25 with fewer drops than s6951's 34: <= 3 in that block)
vs H-same (same drops, ~6) vs H-overdrain (28 drops > 2 in no-dose blocks; s6952 says no, recheck).
Positive control: at least one off block after the 200 ms doses must read acq>5% > 30 (formed level); if none forms, the run is a null for clearing.
1. Only the built-in attached, owner idle > 120 s, screen unlocked (ioreg -n Root -d1 -a | grep CGSSessionScreenIsLocked prints nothing).
2. env ARMS="60:4:o28:ROGUESQ_PRESENT_DRAIN=28,ROGUESQ_PRESENT_DRAIN_TOGGLE=20+ST" zsh tools/g1e_owner_hz_arms.zsh
3. python3 tools/g1e_drain_blocks.py scratch/s6932/ring_o28.txt --from 95 --stall 110:17,124:17,138:17,152:50,166:50,180:50,194:200,208:200,222:200
   Compare to s6951: python3 tools/g1e_drain_blocks.py scratch/s6951/ring_o34.txt (same flags).
If 28 is not clearly better (fewer drops AND lower p50 after a formed block), close the slug with 34 and move on (G1e item 7 / owner reports).
If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md, g1e-present-drain section) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
