# NEXT: G1 — who sends msg 2 (silent destroy) vs msg 5 (counted teardown) to class-1 NPCs in lv0
s5813: 47/54 tracked class-1 NPCs got msg 2 (frees without counter), 8 got msg 5 (counted teardown).
Hypotheses: (a) msg 2 = offscreen/distance/timeout despawn (by design); (b) msg 2 = kill path that should be msg 5 but the port takes the wrong branch (e.g. flag/hp compare); (c) msg 2 = level-cleanup sweep.
Discriminator (one build, one run): in rs5813_msg for tracked NPC and msg 2/5, log the caller of npcProbeDriod (ra), VI frame count, NPC desc hp fields (+0x70.. descriptor), and whether the NPC was ever hit. Positive control: msg5 count==8, msg2==47 as in s5813. Run scratch/agent/g1_inv1.sh <tag> 400.
Outcomes: msg2 ra == level-cleanup/timeout caller -> (a)/(c), then look at what kills in the real game (oracle); msg2 ra == same hit-resolve caller as msg5 -> (b), diff the branch condition.
HYPOTHESIS-ID: g1-mission-progression
