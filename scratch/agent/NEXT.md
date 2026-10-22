# NEXT: G1 — log d2 + NPC ptr at each gtdest (key the [rng] logger to destroys)
s5822: moving the ship (A held) raises gtdest 0->27, idle 0; d2 at destroy unseen because [rng] logging caps at 20 rows/result and is spent early.
Hypotheses: (a) destroys occur when d2>=144 (ship left radius) = despawn by design; (b) destroys occur with d2<144 = second destroy path (collision/motion).
Discriminator: in tools/apply_s5818_destroy_health.py, record the last [rng] result/d2 per NPC ptr and print it in the [gtdest] line (cap 80), then regen (make_elf -> N64Recomp -> fixup -> cmake), rerun scratch/agent/g1_approach.sh. Fraction of gtdest with d2<144 splits a vs b. Control: res=0 and res=1 rows both present.
Also fold in the s5820 end-of-mission crash cap fix via the same regen.
HYPOTHESIS-ID: g1-mission-progression
