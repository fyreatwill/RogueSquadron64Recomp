# NEXT: G1 - s5848: with fire on, keep class-2 NPCs (descs 0x80319e5c/cce/a9c) alive so counter 2 stays <3; does counter 1 climb past 8 and does a win arm fire?
s5847 result: the mission end is the FAIL arm (c2=3,c1=8,c10=0 at lv0_checkComplexObjectives+2412 -> setHudEnableBit4). Win needs c1>=21 or c10>=6 (s5826/s5807).
Hypotheses: H1 class-2 NPCs are killed by player fire/friendly fire -> c2=3 -> fail (protect them -> run continues, c1 may climb). H2 c2 also rises from despawn/out-of-range, so protecting hp doesn't help. H3 c1 plateaus at 8 regardless (needs distinct bool ids, s5827) so the mission is only winnable by flying to more spawns.
Step: add a class-2-only invuln (find how ROGUESQ_NPC_INVULN is applied in tools/apply_s5818_destroy_health.py / getNpcCurrentHealth wrapper; restrict to NPCs whose desc is one of the three class-2 descs) as env ROGUESQ_NPC_INVULN_C2=1; build; run `env ROGUESQ_TELE_BOLT=1 ROGUESQ_NPC_INVULN_C2=1 ROGUESQ_LOG_HUDBIT=1 zsh scratch/agent/g1_fire.sh s5848 720`, and the control without the env in the same iteration (queue as soak if long).
Discriminator: [m47] c2 at end. c2<3 and mission still alive at hold end -> H1 confirmed; c2 reaches 3 anyway -> H2 (find the third increment writer); c1 >8 -> H3 refuted.
Positive control: [mend] endMissionCleanup fires in the control run.
HYPOTHESIS-ID: g1-mission-progression
