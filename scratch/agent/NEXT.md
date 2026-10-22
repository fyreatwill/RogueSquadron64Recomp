# NEXT (s5922): what is tmsg2, and why did it rise only while poked onto k=4..13?

HYPOTHESIS-ID: g1-mission-progression

Context (s5921): poking ship onto class-1 centres (0 u) did not step tmsg5 (2->6 slow drift). tmsg2 rose 3->19 in m 4200-7000 (waypoints k=4..13), flat after.
Hypotheses: (A) tmsg2 = in-range/proximity message to class-1 (then msg5 needs another precondition, e.g. aim/own bolt); (B) tmsg2 = unrelated (wave spawn timer) coincident; (C) tmsg2 tracks ship altitude/area.
Discriminator: offline from m6/s5921_poke/run.log: correlate [npcmsg] tmsg2 deltas with [plpoke] k windows and the second lap (k=0..3 at m 7800+, tmsg2 step?). Then grep the msg2 handler in recompiled class-1 fn. Positive control: tmsg3/4 (always rising) must show in the same parse.
Outcome A -> find msg5 precondition; B -> pivot to bolt spawn pos log.
