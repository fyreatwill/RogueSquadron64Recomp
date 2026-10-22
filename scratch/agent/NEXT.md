# NEXT: G1 - s5841: capture the NPC arg from the caller's candidate loop (0x8005D1C8, audioCueDispatcherNpcHandler) at the sphere test.
s5840: sphere a0 = 0xB4-stride pool node, no NPC pointer in 0x100 bytes (0/32). Owner not stored in the shape.
Step: in tools/apply_s5835_sphere_probe.py, hook the candidate loop (find which saved register holds the NPC/slot node when it calls intersectSegmentWithObjectSphere, e.g. print ctx->r16..r23 and stack words at call time for the first 30 P calls, compare to spawn1 npc ptrs offline), store as rs5841_npc, gate TELE on *(npc+0x34)+0x70==1. Run: env ROGUESQ_LOG_HITS=1 ROGUESQ_TELE_BOLT=1 ROGUESQ_LOG_HUDBIT=1 zsh scratch/agent/g1_fire.sh s5841 320.
Outcomes: register found + [ctr1] climbs on forced class-1 P hits -> steering-only (build aim); no climb -> msg-5 receiver ignores player hits. Register not found -> use slot table *0x80130BB0 id*8.
HYPOTHESIS-ID: g1-mission-progression
