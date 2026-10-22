# NEXT: G1 — do real-input kills raise counter 1 (arm D needs get(1)>=21)?
s5823: ground-troop destroys are out-of-range despawns (29/29 d2>=151). So kills must come from player fire.
Hypotheses: (a) fire button held with A kills troops and counter 1 rises past 8 -> mission can be won from real input; (b) fire hits nothing/does no damage (hp stays 10/20) -> port defect in weapon/damage path; (c) kills happen but are not counted (count path skipped).
Discriminator: copy scratch/agent/g1_approach.sh, in the phase table hold A plus the fire button (find it: grep CURRENT-TRUTH/PROJECT-OVERVIEW for the N64 fire button, B 0x4000 likely) in one phase and A alone in another within ONE run; log [gtdest] hp, [ctr1], and hp<=0 destroys per phase. Control: NPC_INVULN unset in the fire phase so kills are possible; A-only phase is the same-run negative.
HYPOTHESIS-ID: g1-mission-progression
