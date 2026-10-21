# NEXT: fold s5730_deada / s5730_deadb from SOAK-RESULTS.md (m6/<tag>/run.log).
Context: mission cycles end at the game's GAME OVER results screen (s5728_supc fbd frame 9000), not via setObjectiveBoolean. Added `[god-dead]` probe and ROGUESQ_GODMODE2=1 revive.
H-DEATH: health hits <=0 -> a: [god-dead] dead=1 shortly before the origin leaves the mission; b: revive keeps flight alive, cycles drop to 0-1 / flight outlives ~226 s.
H-FAILCOND: Game Over from a non-health fail condition (objective timer, ally loss, out-of-bounds) -> a: no dead=1 line; b: cycles unchanged (2-3). Next probe then: the mission-state/game-over writer (grep decomp for "GAME OVER" string xref / results-screen entry; log its caller).
H-NOISE: [god-dead] absent in both => control failed, rebuild check.
Control: `grep -c god-dead m6/<tag>/run.log` > 0 (near-death lines fire when health < max/3).
HYPOTHESIS-ID: g1-gameover-cause
