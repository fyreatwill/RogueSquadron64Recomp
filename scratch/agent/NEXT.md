# NEXT: does altitude hold stop the terrain crash?

s5777 closed the geometry question. Do not log another angle or vec, and
do not re-read `stepObjectOrientationTowardTarget`. On the steer schedule
every `site=0x800B2EC4` death was a real terrain normal (unit, nearly +Y,
angles match the dots). The spline jal `0x800B0D9C` stays parked.

`ROGUESQ_ALT_HOLD` already exists. It latches ship y on the first
`0x690400` poll and drives `stick_y` only when the scripted stick is 0.
`su`/`sd` keys block it. It does not arm on any other origin. s5686 ran it
with godmode on, so lives could not move; that result does not say whether
the return-2 death stops.

The work unit is one run. No new log, no rebuild, unless
`build/RogueSquadron64Recomp` is older than the s5777 link.

- Copy `scratch/agent/s5776_geom.sh` to `scratch/agent/s5777_althold.sh`.
  Keep `GODV=0`, `HOLD=420`, `MISSION_RE=62BD00`, `ROGUESQ_LOG_MTM=1`,
  `ROGUESQ_NO_SAVE_WRITE=1`. Set `TAG=s5777_althold`.
- In the flight loop, emit only `a sl a sr`. No `su`, no `sd`.
- Add `ROGUESQ_ALT_HOLD=2.0` to `XENV`.
- Before launch, `ioreg` must not show `"CGSSessionScreenIsLocked"=Yes`.

Require, in `scratch/agent/m6/s5777_althold/run.log`: `[livesctl] mission`,
one `kind=ret1`, and an `[althold] target` line whose later `[althold]`
rows reach `acted>0`. A run with no ret1, or no `[althold] target`, is a
null. Do not interpret its deaths.

- H-hold-stops: while `acted` is increasing, there is no `kind=ret2` and
  no lives 3->2. The hit was the descent. Next is whether that airborne
  run reaches a win, not another orientation log.
- H-hold-still-dies: `acted>0` and a `kind=ret2` geom line still precedes
  a lives drop. Holding the latched y does not stop the test. Do not tune
  the deadband and do not add a field.
- Null: no `[althold] target`. Name whether origin `0x690400` occurred.
  Do not classify the deaths.

HYPOTHESIS-ID: g1-real-input-win
