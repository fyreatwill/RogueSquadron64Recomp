# NEXT: G1 — identify msg-5 receivers 800cabd4 and 800d93c0 (class-1 damage path?)
s5832: only 3 update fns ever get msg 5 (8006cbb0=249, 800cabd4=6, 800d93c0=3). Class-1 NPCs never reach updateDestructionDebrisNpc.
Hypotheses: (a) 800cabd4/800d93c0 are the class-1 handlers and rarely receive msg 5 because the upstream sender's hit test (radius/collision) rarely passes for them; (b) they are unrelated objects and class-1 never receives msg 5 at all.
Step: log, at the dispatch call for those two fns, obj (r4) +0x34 descriptor and its +0x70 class (fix s5832's keying: try r16/r17 slot->obj chain), plus dump their first 40 instructions from the recompiled source (grep funcs_*.c) to read the msg-5 arm. Then find the msg-5 sender (grep "ori.*0x5" near sendMsg callers) and its range gate. Control: 8006cbb0 must show class 0/2.
Outcome: class 1 confirmed on both -> read sender gate; class != 1 -> (b), find class-1 handler fn by tallying all update fns for objects with class 1.
HYPOTHESIS-ID: g1-mission-progression
