# NEXT: G1 — class-1 (+0x70==1) NPC spawned-vs-torn-down tally in lv0
s5811: counter 1 increments in npcProbeDriod when a descriptor with +0x70==1 is torn down (after unregisterAndFreeNpcSlot/popNpcSlotFromTail). 8 teardowns in a 405 s hold; target >=21.
Hypotheses: H-nospawn (fewer than 21 class-1 descriptors ever get created in lv0 -> port skips an upstream spawn/script); H-nokill (>=21 spawned, autopilot only tears down 8 -> input/targeting limit, not a port bug).
Discriminator (one build, one run): find where descriptors with +0x70 written (grep generated code for the store of +0x70 on the descriptor alloc path; the class-1 spawner is NOT updateDestructionDebrisNpc), log under ROGUESQ_LOG_HUDBIT a per-spawn tally of +0x70 value (classes 0/1/2/3) plus teardown tally in npcProbeDriod (reuse s5811 sites), with `all spawns counted` positive control (sum of classes == total spawns). Run scratch/agent/g1_inv1.sh <tag> 400.
Outcomes: class-1 spawns <21 -> H-nospawn: trace which script/spawn call is missing vs oracle. class-1 spawns >=21 with only 8 torn down -> H-nokill: count alive class-1 at hold end, then drive fire at them.
HYPOTHESIS-ID: g1-mission-progression
