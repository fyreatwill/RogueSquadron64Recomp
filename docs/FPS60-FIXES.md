# FPS60 fixes (one page)

`ROGUESQ_FPS60=1` makes flight produce a game frame on every VI (60/s) instead of every second VI (retail ~30/s).
Most of the game moves by delta time and is fine at 60 Hz. A few places add a fixed step once per tick, so at 60 Hz
they ran twice as fast in game time. Each row below names one fix. All of them are ON whenever `ROGUESQ_FPS60=1` is
set. Each has its own `=0` switch to put back the uncorrected 60 Hz behaviour for A/B comparison. None of them changes
anything without FPS60 (retail stays exactly as it is).

Run it: `cd build && env ROGUESQ_FPS60=1 ./RogueSquadron64Recomp`. Frame rate (s6776/s6810, no logging): ~60 game fps on
lvl1 and lvl5 at draw distance 1-4.

| Fix | Switch (`=0` turns it off) | What ran at the wrong rate at 60 Hz | Fixed to | Verified (same-build A/B) | Code | Session |
|---|---|---|---|---|---|---|
| The lever itself | `ROGUESQ_FPS60=1` | Flight frame limiter byte 0x80128EAF held at 2 (one frame per 2 VIs) | Clamped 2 -> 1 while it reads 2 | lvl1/5/10 300 s holds 0 crash; frame counter 0x8011A890 30.06/s retail vs 58.8-59.9/s | `lib/N64ModernRuntime/ultramodern/src/events.cpp` `g1e::apply` | s6255-s6261, s6703 |
| Terrain scrape deflection | `ROGUESQ_FPS60_SCRAPE` | Collision resolver turns the craft K*dt per contact pass, so 60 Hz deflected half as much per pass and the craft hugged the ground (7 contact ticks instead of 2) | Contact-case multiplies use max(dt, 1/30); the sweep keeps the real dt | lvl14, 3 seeds: contact ticks 30 Hz 2 / fix 4 / off 7; hits per s 0.116 / 0.094 / 0.041 (the fix leaves 2 extra contacts from 60 Hz surface sampling) | `tools/fixup_fps60_scrape.py` | s6817 |
| Scrape damage | `ROGUESQ_FPS60_SCRAPE_DMG` | 20 hp per contact tick | Scaled by dt*30 | seed 1 scrape hp: 30 Hz 40 / fix 40 / off 80 | `tools/fixup_fps60_scrape.py` | s6819 |
| Off-range NPC despawn grace | `ROGUESQ_FPS60_DESPAWN` | NPC is removed after 21 failed range ticks (0.70 s at 30 Hz, 0.35 s at 60 Hz) and re-created, so edge NPCs churned twice as often | Threshold round(21/(30*dt)), clamped 21-42 | lvl14, 3 seeds: TIE re-create every 40 VI (30 Hz) / 41 (fix) / 20 (off) | `tools/fixup_fps60_despawn.py` | s6820 |
| Mission tick timers (+-1 per tick) | `ROGUESQ_FPS60_TICKS` | 6 countdowns/count-ups (NPC lifetime, curved-path countdown, throttle charge, effect state debounce, cutscene gate, stage advancer) ran 2x | Step = number of 1/30 s game-time boundaries crossed this tick (0/1 at 60 Hz); 1 outside a mission tick | Per-level census lvl2-19: fixed sites match 30 Hz rate per game second; 8 per-event sites (C-down presses, burst counts) deliberately left at step 1; s6833: the lives decrement in the respawn routine (0x800FB4F8, once per respawn) also left at 1 | `tools/fixup_fps60_ticks.py` | s6821-s6825 |
| Float per-tick quanta | `ROGUESQ_FPS60_FQUANTA` | Guided-craft accel/speed and drop terms, smoke-puff growth (x1.1/tick), effect wobble phase, two constant-1/30 player-vehicle steps, hangar craft tilt, player-death spline speed ramp (+-2/tick) and scale (x1.01/tick) | Multiplied by k = dt*30 (pow(x, k) for growth factors) | accel slope 30 Hz 12 / fix 12.0 / off 24.0; hangar tilt rise 0.167 / fix 0.183 / off 0.083 s; spline ramp 60.0 / fix 60.0 / off 120.0 u/s^2 | `tools/fixup_fps60_float_quanta.py` | s6826-s6830 |
| Integer step ramp | `ROGUESQ_FPS60_INTSTEP` | Curved-path NPC speed ramp +0x20 per tick (advanceNpcOnCurvedPath +0x1E) | Step x game-time tick count | lvl14 ramp 30 Hz 0.267 s / off 0.133 / fix 0.250 (up n=7, down n=8, s6832 400 s soak) | `tools/fixup_fps60_int_step.py` | s6831-s6832 |

Diagnostic only (no value change): `tools/fixup_fps60_float_trace.py` hooks the per-tick float sites into the
`ROGUESQ_TICK_TRACE=<file>` recorder used to find the rows above.

Bundle qualification (s6832 soaks, all rows on, FPS60 + `ROGUESQ_DRAW_DISTANCE=4`, 300 s holds): lvl1 and lvl10 alive at
end, 0 crash lines, 0 VI stalls; ~42 / ~55 drawn frames per s over the run (above the retail ~30 cap, so FPS60 was live).

## What was checked and is NOT a 60 Hz problem
- Mission clocks, craft path per real second and audio (audio ticks per VI, VI stays 60/s): s6256-s6258.
- The lvl14 cutscene starting later at FPS60 (s6813-s6814): that was the passive player dying later, not a slow script.
- The "fewer hits land at FPS60" reading (s6815-s6816): a path difference after the terrain scrape, fixed by the scrape row.
- Census of 41 integer |step|>1 sites (s6831): 40 are memory strides, decoders, layout cursors or audio offsets.
- Shake while turning (G3c/G3d): retail judder plus the old ~17 fps bug fixed in s6696, not FPS60.

## What only the owner can judge
How FPS60 feels to play: turning, NPC motion, explosions, the hangar. To check one fix by eye, run the same scene
twice, with and without its `=0` switch, e.g.
`cd build && env ROGUESQ_FPS60=1 ROGUESQ_FPS60_FQUANTA=0 ./RogueSquadron64Recomp`.
