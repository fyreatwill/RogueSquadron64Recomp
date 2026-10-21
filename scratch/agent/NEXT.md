# NEXT: G1 — what increments objective counter 2 in mission 0x620400 (fail at count >= 3)?

s5786: setHudEnableBit4 caller = lv0_checkComplexObjectives site `getObjectiveCount(2) >= 3` (0x801011B4..0x801011E0), then speech 0x229, then mtm(2). Timer and bools 0x64/0x65 not involved.
- H-friendly-loss: counter 2 counts friendlies/targets lost; increments come from a game-side kill/destroy event (legit game rule) -> then the question is why friendlies die (our flight/AI/collision port bug?).
- H-ours: increments follow our fire input (btn 0x8000) hitting friendlies -> noalt arm (queued s5786_hudb_noalt) should show the same increments or none.
- H-port-bug: counter 2 incremented by a path that should not run (e.g. wrong damage/collision result).
Discriminator: patch setObjectiveCount/addObjectiveCount (find via `grep -n 'RECOMP_FUNC void .*ObjectiveCount' funcs_35.c`) to log value+host backtrace under ROGUESQ_LOG_HUDBIT; same recipe, both arms (queue both, rule 13). Control: counter 2 increments at least once in the failing arm before the fail.
HYPOTHESIS-ID: g1-mission-progression
