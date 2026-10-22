# NEXT: G1 - s5840: find shape->NPC owner link, then class-1 forced hit.
s5839: intersectSegmentWithObjectSphere a0 is a shape record (0x8035xxxx/0x8021xxxx); +0x34 is not the NPC descriptor, class tally c1=0.
Step: in the s5835 probe, for the first ~30 P tests dump 0x40 words of a0; also keep a ring of NPC ptrs from the s5812 spawn1 log (npc=r17, class-1 only) and report which a0 word (offset) equals a recorded NPC ptr. Alternative: capture the owner arg held in audioCueDispatcherNpcHandler's candidate loop. Positive control: N-shooter tests on same shapes must show the same offset.
Outcomes: offset found -> gate TELE on owner class==1 and read [ctr1] delta (g1_fire.sh s5841 320, env ROGUESQ_LOG_HITS=1 ROGUESQ_TELE_BOLT=1 ROGUESQ_LOG_HUDBIT=1); no offset -> owner reached via the slot table (tb=*0x80130BB0, id*8), scan those nodes instead.
HYPOTHESIS-ID: g1-mission-progression
