# NEXT: FPS60 tick timers - last 3 kept-but-unexercised sites, then close the class
HYPOTHESIS-ID: g3-fps60-tick-timers

State (s6824): tools/fixup_fps60_ticks.py steps 8 sites. UNFIX = 800DAB64, 800E32CC, 800E1E28, 800C96B8, 800806AC,
800B5350, 800BC778 (C-down press edge, s6824). Tick trace rows pc=2 now carry the button word 0x80130B88 + config.
Unexercised: 8007CD50 (npcTexturedEffectUpdateWithSlotChain +0xA0), 800FB4F8 (tickMissionTransitionAndTeardown),
800F8708 (executeActorType4Effect +0x92, ran 8x on lvl11 FPS60 only).
Hypotheses per site: H-tick (keep) / H-event (UNFIX) / H-dead.
Step 1: scratch/s6823/census.sh with EEPS="scratch/s6769/lvl16.eep scratch/s6770/lvl17.eep" (FPS60, 300 s) and the same
for a30 (drop ROGUESQ_FPS60). tools/g3_tick_site_census.py + g3_tick_timer_durations.py on the dumps.
Step 2: for any site that runs in both arms, ex/gs a30 vs FPS60: 2x => per tick (keep), equal => event (UNFIX). Positive
control 8006C024 (2.0x in s6824). 800FB4F8 = mission teardown: let a mission end (lives cap ROGUESQ_LIVES_CAP=1 + death).
If none runs: close the class (8 kept; list the 3 as static-only single-source) and take the next G-ladder rung.
