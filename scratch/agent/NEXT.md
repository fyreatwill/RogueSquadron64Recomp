# NEXT: G1 - s5851: why are 13 of 21 lv0 class-1 targets never torn down? (positions)
s5850: win == tear down all 21 distinct class-1 descriptors (docs/M6-LV0-OBJECTIVE-TARGETS.md); autopilot gets 8 (17 with TELE_BOLT).
Hypotheses: H1 survivors are far from the autopilot's flight path (player never within shot range); H2 they spawn only briefly (range despawn msg 2) and respawn out of reach; H3 shots miss at range (s5836 min segment distance).
Discriminating measurement: one run logging player (craft record 0) x,y,z every ~60 VI plus per-descriptor kill VI; offline compare min player-to-target distance for K vs - targets (decisive if survivors' min distance >> killed ones').
Then: waypoint the autopilot (g1_fire.sh) to survivors; c10: scan descriptors for +0x70/+0x80==10 across all NPC classes.
HYPOTHESIS-ID: g1-mission-progression
