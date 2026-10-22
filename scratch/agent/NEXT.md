# NEXT: G1 — do class-1 NPCs receive msg 5 (damage) from player fire at all?
s5831: updateDestructionDebrisNpc never sees class 1 (control: cls0/2/3 tallied; hits dmg=12 land on cls0/2). Class-1 handle msgs in their own update fns.
Hypotheses: (a) class-1 gets msg 5 only rarely (8/54 counted) because fire misses/collision radius; (b) msg 5 arrives often but their handler gates the kill (rand()&3, range 144); (c) msg 5 is never sent to them except via death arm.
Step: patch slotDispatcherIter (where update fn is called with msg) to tally (slot+0x70 class, msg) with the same [hitsum] format under ROGUESQ_LOG_HITS=1; same g1_fire.sh run (env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fire.sh <tag> 320). Control: cls0/2/3 counts must match s5831 magnitude. Outcome: cls1 m5 ~0 -> (a)/(c); cls1 m5 >> 8 -> (b).
HYPOTHESIS-ID: g1-mission-progression
