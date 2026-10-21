# NEXT: name the path that makes stepObjectOrientationTowardTarget return 2

s5774 closed the debris-caller census. Do not rerun it. On the level-select
death route, two full 3-life cycles, controls passed (`[livesctl] mission`,
lives 3->2 twice, `[debris-call]` on the player slot). Every player-slot
0x0190 store is the next stderr line after one of two jals:

- 4/6, the 3->2 and 1->0 deaths: jal 0x800B2EC4 in updatePlayerCraftPhysics,
  a1=1, halfword 0x0001. That jal is reached only from the arm taken when
  stepObjectOrientationTowardTarget returns low byte 2 (beq at 0x800B2928
  to L_800B2D2C). The return-1 arm calls spawnNpcDestructionDebris or the
  hp<=0 jal 0x800B2A08, which stayed at 0.
- 2/6, the 2->1 deaths: jal 0x800B0D9C in updateSplineCraftTransform, a1=1,
  halfword 0x0008, immediately after spawnNpcDestructionDebris stored bit
  0x8 (0x0001 -> 0x0008 at 0x800B08DC). Park this path until the 4/6 path
  is named. It is not the first death of a cycle.

The single work unit is the 4/6 path: which instruction makes
stepObjectOrientationTowardTarget (funcs_43.c, entry 0x800FEF10) return 2.
Static trace from the epilogue backwards. 0x800FFCF8 is NOT that return. It
compares stack byte sp+0x497 to the immediate 2. Do not grep `addiu $v0, 2`
and stop.

Competing hypotheses and the discriminating measurement:

- H1: one epilogue writes a return whose low byte is 2, and the predicate
  above it is readable (terrain, altitude, or a collision byte). Evidence:
  exactly one path reaches `jr ra` with that value, and naming the compare
  is the result. No run.
- H2: several paths return 2. Evidence: more than one such epilogue. Then
  add one per-path counter and rerun `zsh scratch/agent/s5774_debris.sh`.
  The path that logs immediately before each `[debris-call] site=0x800B2EC4`
  is the one. Require `[livesctl] mission`, a lives 3->2 line, and at least
  one `site=0x800B2EC4` line in the same run. Screen unlocked
  (`ioreg` must not show `"CGSSessionScreenIsLocked"=Yes`).
- H3: the function never stores the immediate 2 into the return register.
  The 2 is a callee return or a loaded byte. Evidence: the epilogue copies
  v0 from a `jal` or a load. Name that producer before instrumenting.

HYPOTHESIS-ID: g1-orient-ret2
