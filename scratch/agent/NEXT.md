# NEXT: G1 — why do class-1 teardowns go silent (msg 2) vs counted (msg 5)?
s5828: spawned class-1 ids 1F,20,21,28,2D (and 2B,18,19,29,2A) all spawn near the idle player; only some get counter-1 sets. Id space >= 0x18..0x2D.
Hypotheses: (a) counted path requires NPC killed by damage (health 0) vs silent = despawn on range/timer; (b) counted path depends on a descriptor word (w[0x1C..0x23]: 0x0A,1,1,id,1,0x6F/6E/71,1,1,0xE0/DF/E2) differing per id; (c) order/slot-based.
Discriminator: offline first - diff descriptor words of counted ids (18,19,2B,2A,29) vs silent (1F,20,21,28,2D) in s5828_desc/run.log [spawn1] lines; then read npcProbeDriod branch (funcs_36.c ~23800-23920) for which field selects msg 5.
HYPOTHESIS-ID: g1-mission-progression
