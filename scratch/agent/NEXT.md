# NEXT: G1 - s5855: with the who-classifier removed, do any bolts (which include the player's) reach class-1 survivor spheres?
s5854: +0xF8 is a weapon-record id; player id is s2 (0x38 on all 1025 spawns). P/N split in s5833-s5853 void.
Hypotheses: H7 bolts DO hit/approach class-1 NPCs but the kill arm (msg 5) is not triggered for survivors (receiver/health side); H8 bolts never come within radius of survivors (aim/range: bolt lifetime/speed short); H9 survivors respawn/despawn (msg 2) before being hit.
Discriminating measurement (one build, one run): in apply_s5835_sphere_probe, make the newmin print fire for w=1 too (or ignore w) keyed by candidate id, c1f; log per class-1 id: tests, min v2 (bolt-seg to sphere), hits, SEND; plus msg arm (2 vs 5) per id. Positive control: ROGUESQ_TELE_BOLT=1 forced geometry run must show hits on class-1. Outcomes: min sep < r2 with hit but no kill -> H7; min sep >> r2 -> H8; ids never tested while alive -> H9.
Run: env ROGUESQ_LOG_HITS=1 ROGUESQ_NPC_INVULN=1 zsh scratch/agent/g1_fireall.sh s5855 300
HYPOTHESIS-ID: g1-mission-progression
