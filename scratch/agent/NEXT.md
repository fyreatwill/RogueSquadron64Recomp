# NEXT (s7572)
HYPOTHESIS-ID: s6892-walker-writer

19d CLOSED s7571 (all 12 retail-route chains decided). docs/COMPENSATION-CHAINS.md has ONE UNKNOWN lever left: ROGUESQ_S6892
(G5a walker pointer repair, tools/apply_s6892_walker_guard.py, default on; logs build/rs64_s6892.log). The writer of
*(s2+0x18) in cinematicSplineWalkerNpcHandler (caller of initVec4TripletFromArgs, owner crash on Liberation of Gerrard V =
LEVEL=4, half way) was never named. Read PORTING-STATE '^## Session 6892 ' and CURRENT-TRUTH G5a lines first.
Hypotheses: H-spill (dd>1 spill arena: object at 0x8082C870 at dd2, never used at dd1), H-overrun (dd/wide terrain writes land
in the actor), H-fps60 (actor ticks twice, freed/reused), H-uninit (retail bug).
Discriminator, one build: a write watch on the actor's +0x18 slot (every store, guest PC + caller) armed from the cutscene actor
allocation, plus the allocator arena of each such actor, in arms dd1 and dd2 at the owner recipe (FPS60, 16:9), LEVEL=4 forced
route, with the s6892 fire log. Positive control: watch fires on the legitimate initial store of +0x18 in every arm.
If the half-way event cannot be driven, find the event's trigger offline first (the walker's spawn path) and force it.
Outcome: name the writer -> classify S6892 (CHAIN of dd spill / GUARD of retail bug) in tools/s7565_comp_chain.py.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
Run template: scratch/s7571/run.zsh (g1e_owner_quiet_arms, ALLOW_SLOW; ARMS "dd:tag:ENV+ENV").
