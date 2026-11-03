# NEXT: FPS60 tick timers - settle the 7 never-exercised whitelisted sites
HYPOTHESIS-ID: g3-fps60-tick-timers

State (s6822): tools/fixup_fps60_ticks.py steps 12 sites; 800DAB64/800E32CC/800E1E28 reverted (event-gated, the step doubled
them). Runtime-verified per tick: 8006C024, 8007030C (s6821 lvl14), 80044938 (s6822 lvl13). Never executed on lvl2-19:
800C96B8 npcTurretUpdate, 8007CD50 npcTexturedEffectUpdateWithSlotChain, 800806AC attachedAudioVisualEmitterNpcHandler,
800B5350 playXwingEngineSound, 800BC778 computeTieInterceptorOrientation, 800F8708 executeActorType4Effect,
800FB4F8 tickMissionTransitionAndTeardown. 800AF5A0/800B41B8 run only before the first mission tick (step 1 there).
lvl6/11/16/17 never left the intro cinematic in 150 s with start presses at 6-50 s.

Hypotheses per site: H-tick (decrement runs every tick -> keep the step), H-event (decrement sits behind an event/timer
gate -> drop, like s6822's three), H-dead (handler not used by any level -> harmless either way).
Step 1 (offline, discriminating): for each of the 7, read the generated C / disasm around the decrement and list the
branches that guard it between function entry and the store; a guard on anything other than the counter itself
(random, distance, another timer, an event flag) => H-event, move to UNFIX. Also grep setupNpcUpdateFunctions for the
handler's NPC type ids to see which levels can spawn it.
Step 2 (run, if any H-tick sites remain): scratch/s6822/census.sh with EEPS=lvl6/11/16/17 eeps, SECS=300 and AP presses
extended past the intro (e.g. 60:start,70:start,...,120:start); then scratch/s6822/arms.sh on the level that hits them;
python3 tools/g3_tick_countdown_span.py --sites=<list> a30 b60off b60fix. Positive control in every arm: 8006C024
span a30 ~0.23 / off ~0.10 / fix ~0.20-0.25. Discriminator: ex/gs equal at both rates => event-gated (drop).
