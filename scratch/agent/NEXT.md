# NEXT: G1 - s5853: why do player bolts never hit class-1 ground-troop spheres at close range?
s5852b: A really held (589/725 samples) and survivors passed within 0.8-15 u with 30-57 A samples each; still c1=8. s5836: 0 player-bolt sphere hits / 28679 tests.
Hypotheses: H2a bolt segment/direction wrong (horizontal at player altitude, targets 2-4 u below); H2b NPC sphere radius/centre wrong (r2 0.065); H3 survivor NPC not alive at pass time (despawned/respawned, msg-2 out-of-range).
Discriminating measurement (ONE build, ONE run, g1_fireall.sh): in the projectile loop at 0x8005D1C8-0x8005D360 log, when player within 5 u xz of a class-1 NPC (+0x70==1): bolt pos, bolt dir, NPC pos, NPC sphere centre/radius, NPC alive/state word, min segment distance. Positive control: N (NPC) bolts hit (141 sphere hits s5833). Outcomes: dist small but no hit -> H2b; dist large vertically/dir off -> H2a; NPC absent in list -> H3.
Run: env ROGUESQ_NPC_INVULN=1 zsh scratch/agent/g1_fireall.sh s5853 720
HYPOTHESIS-ID: g1-mission-progression
