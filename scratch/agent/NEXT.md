# NEXT (s5890): why does c1 plateau at 8 with class-2 invulnerable? (b) reachability/aim vs (c) class-1 shield semantics
Context (s5889): INVULN=1 run: c1 8 flat, c2=0, alive 600 s; (a) refuted.
Discriminator: one INVULN=1 run (scratch/agent/s5889_inv.sh 1) adding per-class-1-desc log: HIT msg-5 count per desc and player distance (ROGUESQ_LOG_PLPOS) to the 13 un-triggered class-1 descs. Outcomes: never hit + far => (b), steer toward them; hit but not torn down => (c), inspect class-1 hp/shield fields (+0x28..+0x48 from [ctr1] trig).
HYPOTHESIS-ID: g1-mission-progression
