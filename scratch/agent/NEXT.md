# NEXT: G1 — who sends msg 2 (silent destroy) to class-1 NPCs, vs msg 5 (death arm, counted)?
s5829: descriptor words do not discriminate; counted sets (ids 0x18,0x19, deterministic) come from npcProbeDriod copy 2 (L_800CBCBC, reached from rand()&3 death-effect arms). Copy 1 (+0x6C gate) never ran.
Hypotheses: (a) msg 2 is a broadcast/range or cleanup despawn from a global sender; (b) msg 2 is sent per-NPC when player distance/timer expires; (c) msg 5 reaches only NPCs the player's shots hit (approach-driven, s5825).
Discriminator: one build, log in npcProbeDriod dispatch (class-1 NPCs only): msg, id, and ra/caller of the sender (backtrace at msg enqueue), with a mark-everything positive control; run g1_approach.sh. Outcome splits: msg-2 sender distance-based vs global.
HYPOTHESIS-ID: g1-mission-progression
