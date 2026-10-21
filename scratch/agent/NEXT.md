# NEXT: G1 — where does the probe droid aim (is the player the intended target, with NPCs collateral, or are NPCs targeted)? (H1 vs H2'')
Evidence (s5796): class-2 NPCs are legitimately in the projectile scan list (6/8 victims). Membership is not the bug; question is aim.
Hypotheses: H1 aim = player, NPCs are collateral on the ray; H2'' droid aim vector points at an NPC (wrong target pick); H5 droids shouldn't be alive/firing yet (mission scripting).
Discriminator: offline read of the droid fire routine (npcProbeDroid handler, spawns projectile with desc at s5794 shooter log) to find the aim vector source; then one run logging at fire time droid pos, aim dir, player pos (pl=80165df8) and the angle between aim and (player-droid). Outcome: angle ~0 -> H1; aim toward victim -> H2''. Control: [shooter] lines fire.
HYPOTHESIS-ID: g1-mission-progression
