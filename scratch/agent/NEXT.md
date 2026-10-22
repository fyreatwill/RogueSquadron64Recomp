# NEXT: G1 — hold A (thrust) toward the ground-troop NPC and re-test the range gate
s5821 result: ship moves only while A is held (~2.2 u/s in x,z); stick alone moves nothing. Last NPC distance d2~187 vs threshold 144 at start pos ~ (43,45).
Hypotheses: (a) approaching to within the 48-unit radius keeps the class-1 troops alive (despawn-by-design confirmed); (b) troops still destroy for another reason when in range; (c) A-thrust direction does not head toward the NPC (needs sr/su steering with A held).
Discriminator: g1_pos.sh variant with A events continuous from el 240 and sr/su added as stick events in the same hold (autopilot is single-event: use a combined key if needed - add "a+sr" support or run A then A phases alternating), watch [rng] rows (raise per-ra cap) for d2 falling below 144 and gtdest count. Control: s5821 'none' phase (pos frozen).
Keep hold < 350 s (end-of-mission crash fix not in build until full regen).
HYPOTHESIS-ID: g1-mission-progression
