# NEXT: G1 - s5846: why does the mission end at endMissionCleanup (win, timeout or fail)?
s5845: counter 1 reached 17 and the mission ended at ~VI 42112 exactly as at counter 8 (s5824). Need the end reason.
Step: (1) full regen (make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake) so the s5818 stale-slot guard lands; (2) offline: grep the generated mainGameLoop for the branch calling endMissionCleanup, name the flag it tests (win/lose/timer), then add one log of that flag + mission timer at call time, run g1_fire.sh with TELE_BOLT.
Discriminator: flag/timer value at the endMissionCleanup call. Win flag set -> G1 win reached by forced hits, then build real steering; timer expiry -> counter is irrelevant, find objective gate; fail flag -> player death/other.
HYPOTHESIS-ID: g1-mission-progression
