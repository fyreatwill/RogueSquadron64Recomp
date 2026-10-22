# NEXT: G1 — does flying toward class-1 ground troops keep them alive (in range) so counted kills can happen?
s5819: despawn is by design (ref==player, d2 187 vs thr 144 while player idles at ~55 raw units). Hypotheses: (a) with a player that closes to <48 raw units, the range gate passes and the 50 destroys drop to ~0 and msg-5 kills rise; (b) NPCs flee/move away so still despawn even when approached (then a spawn-side or movement bug); (c) autopilot can't steer toward the NPC.
Discriminator: one run with the s5819 [rng] + [gtdest] instrument, autopilot altered to hold stick toward NPC xz (or throttle forward), compare destroys-via-3 and [rng] res=1 counts in the SAME mission phase vs idle control (s5819_rng2: 48 gtdest). Control: res=1 rows in-mission must appear.
Command: build a g1_fly variant of scratch/agent/g1_inv1.sh (copy; change the sl/a/sr/b/su/sd schedule to forward/up steering), tag s5820_fly, 400.
HYPOTHESIS-ID: g1-mission-progression
