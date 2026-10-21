# NEXT: G1 — per-NPC fate of class-1 NPCs in lv0 (why 48 of 56 spawned are not torn down)
s5812: 56 class-1 spawns (spawn arm of npcProbeDriod, L_800CAC40), only 8 teardowns -> H-nokill. 
Hypotheses: (a) HIT msgs (msg 5) never reach them (player shots/collision path); (b) they are freed without the teardown arm (timeout/offscreen) ; (c) HITs arrive but descriptor hp not depleted (damage halfword wrong); (d) autopilot never aims.
Discriminator (one build, one run): in npcProbeDriod log per message-type counts keyed by class-1 NPC (dispatch switch on a1): spawn, HIT(5), teardown, plus count of NPCs freed via other path (rs_free of 0x11C obj / unregisterAndFreeNpcSlot without teardown arm). Positive control: spawn count == s5812's 56-range and teardown == 8. Run scratch/agent/g1_inv1.sh <tag> 400.
Outcomes: HIT=0 -> (a) trace shot->NPC message path; HIT>0, teardown small -> (c) log hp before/after; silent frees large -> (b).
HYPOTHESIS-ID: g1-mission-progression
