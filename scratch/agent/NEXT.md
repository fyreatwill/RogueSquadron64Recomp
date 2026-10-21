# NEXT: which call sets player death bit 0x8?

s5778 closed the altitude question. Do not change `ROGUESQ_ALT_HOLD`, do
not add a deadband, and do not log another orientation angle. While the
hold commanded sy=+1 (`acted` 0→2960), lives still went 3→0 three times.
8/9 drops start at `[killset]` pc=0x800B08DC (player slot 0x180,
0x0001→0x0008). The 9th is the closed return-2 path at 0x800B2EC4.

`spawnNpcDestructionDebris` (entry 0x800B0850) has exactly two jals:

- 0x800B146C in `tickCinematicObjectStateMachine`, taken when its float <= 0
- 0x800B2A58 in `updatePlayerCraftPhysics`, taken when byte sp+0x175 != 0
  after that function's own float<=0 check

The work unit is one build and one run. Add a fixup (same shape as
`tools/apply_s5774_debris_caller.py`, hooked from
`tools/fixup_game_funcs_vendored.py`) that logs those two sites only:
pc, a0, and the player-slot halfword. Do not hand-edit `funcs_30.c`.
Rebuild only what that file needs. Reuse `scratch/agent/s5777_althold.sh`
unchanged so the flight is the same one, not a new schedule. Screen must
not show `CGSSessionScreenIsLocked=Yes`.

Control: a `[killset]` line `pc=0x800B08DC before=0x0001 after=0x0008`
and, in front of each of those, exactly one of the two new site lines.
Zero site lines is a null. Do not interpret a run that never prints that
killset transition.

- H-cine: every 0x0001→0x0008 is 0x800B146C. The life loss is the
  cinematic countdown. Next is what that float is, not a stick change.
- H-phys: every 0x0001→0x0008 is 0x800B2A58. Next is what sets sp+0x175.
- H-split: both sites fire on that transition. Report the two counts.
  Do not add a third site.

HYPOTHESIS-ID: g1-bit8-caller
