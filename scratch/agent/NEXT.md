# NEXT (s7671)
HYPOTHESIS-ID: rumble-abort-live-effect

s7670 closed the F6 panel at a live window resize (H-ok; old-path control shows 1 squashed draw per resize; scratch/s7670).
First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything). Otherwise an owner report; else the
gap s7669 left: abort a mission WHILE a rumble effect is live (s7669 effects only fired at mission start, abort came later).
Route: s7326 hangar route at the owner recipe, ROGUESQ_LOG_RUMBLE=1, force a hit/rumble effect (forced-hit lever, or the s7669
stuck plant timing) within ~0.3 s of the abort key. Hypotheses: H-game-stops (serviceRumblePakMotors stops the motor at
beginMissionEndTransition: run ends <=2 s), H-host-stuck (our rumble thread keeps the last duty after the game stops sending),
H-game-stuck (game never sends Stop on that path). Discriminator: `[rumble] run` durations around the abort (scratch/s7669/score.py),
same-run control arm ROGUESQ_RUMBLE=0, planted stuck arm ROGUESQ_S7669_STUCK_PLANT=1 must FAIL. One game at a time, SIGKILL only,
never touch build/saves, <=2 CPU-heavy jobs. No repeat-hold soaks (G4 parked).
