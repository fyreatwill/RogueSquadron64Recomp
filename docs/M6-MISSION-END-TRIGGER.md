# M6 mission-end trigger (s5464, offline, ledger-derived)

Question (NEXT.md s5463): what ends mission 1 so a soak can reach results?
Answer: the FAIL results screen is already reachable and understood well enough; only the SUCCESS path is unreached.

## Established (with source session)
| Fact | Source | Strength |
|---|---|---|
| z-only autopilot flight ends at ~swap 8000-8100 with fade -> "MISSION" banner -> results ("AMBUSH AT MOS E...", MISSION FAILED / GAME OVER, 2 ships remaining, time 0:00) | s5432, s5433, s5434 | 3 runs, visual |
| No explosion/damage frame precedes the fade; HUD intact | s5433 | single-source visual |
| Results screen waits for input; `start`/`a` restarts the mission (briefing -> flight -> second flight clean) | s5435, s5436/5437 (3/3 x 1200 s) | repeated |
| The ~10-12 min exit to title (origin 0x790400) is the autopilot 'r' key, not a game event | s5421/s5422 (two-arm, same-run control) | confirmed |
| A flown hold without start-key pauses and without 'r' never left the mission in 480 s | s5445 | 2/2 |

## Hypotheses for the fail trigger (undecided; RAM never read)
- H1 timer / objective loss: fail fires at a fixed elapsed time or when a non-player objective is lost. Predicts constant onset swap count regardless of input. Onset ~8000-8100 in 3 runs fits; the s5445 nostart runs (480 s) not failing cuts against a pure timer.
- H2 out-of-bounds: autopilot drifts out of the play area. Predicts onset varies with stick input; s5439/s5451 stick-variation soaks showed no evidence inputs changed the mission.
- H3 cheat/debug path (applyCheatCodeFromInput, S4486 audit) could force a SUCCESS results screen. Untested.
The banner changed MISSION FAILED -> GAME OVER between s5433 and s5434, so a ship-lost path is not excluded.

## Discriminator not yet run
Dump a game-state RDRAM window at the VI-phase transition into results vs ~100 swaps earlier; words that change only at results entry name the condition. One build, one run. Positive control: same dump across title->hangar must show changes.

## Consequence
Fail-path results and restart already have endurance coverage (s5435-s5437, s5449); more fail-path soaks add no information. The unreached region is the success/debrief path (needs H3 or real combat) — a new unit, not a repeat soak.
