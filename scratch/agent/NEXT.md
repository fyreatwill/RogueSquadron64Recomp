# NEXT: FPS60 tick timers - runtime-verify the 13 whitelisted s6821 sites that lvl14 never exercised
HYPOTHESIS-ID: g3-fps60-tick-timers

State (s6821): tools/fixup_fps60_ticks.py steps 15 mission timers by game time under FPS60 (ROGUESQ_FPS60_TICKS=0 = off)
and traces all 109 non-stack counter sites (ROGUESQ_TICK_TRACE=<file>). lvl14 s1 verified two live ones (curved-path
countdown 0.233/0.100/0.200 s, multi-event lifetime 0.200/0.100/0.200 s for a30/off/fix). NOT exercised on lvl14:
npcTurretUpdate 0x800C96B8 (+0x88), npcTieVariantTickAttachmentEffect 0x800DAB64, npcTexturedEffectUpdateWithSlotChain
0x8007CD50, attachedAudioVisualEmitterNpcHandler 0x800806AC, npcTrainCarUpdate 0x800E32CC, tickTrainCarStateMachine
0x800E1E28, accumulateShipThrottleCharge 0x800B41B8, executeActorType4Effect 0x800F8708, computeTieInterceptorOrientation
0x800BC778 / playXwingEngineSound 0x800B5350, cinematicStageAdvancer 0x800AF5A0, tickMissionTransitionAndTeardown 0x800FB4F8.

Step 1 (offline): find which levels run each handler - the NPC type -> handler table (setupNpcUpdateFunctions) and the
per-level dat spawn lists; pick the fewest levels covering most sites (trains: a level with train cars; turrets + forced
hits destroy them via the s5841 TELE lever; mission transition = let a mission end/abort).
Step 2: one recipe per chosen level = scratch/s6821/arms.sh with SAVE_FROM/level swapped (G1 forced level-select route:
ROGUESQ_FORCE_UNLOCK + ROGUESQ_FORCE_SAVE_MISSION + ROGUESQ_NO_SAVE_WRITE), arms a30 / b60off / b60fix, then
`python3 tools/g3_tick_timer_durations.py <a30> <b60off> <b60fix> --sites=<list> --min-runs=1`.
Discriminator per site: off median run ~= a30/2 and fix ~= a30 -> frame-locked + fixed; off ~= a30 -> not per tick (drop
it from FIX in fixup_fps60_ticks.py); fix != a30 and != off -> step semantics wrong for that site (read it again).
Also: any crash/regression in b60fix vs b60off is a datum (fix arm must stay clean).
