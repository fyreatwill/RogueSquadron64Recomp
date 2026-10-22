# NEXT: G1 - player bolts: 0/28679 sphere hits. Aim-miss or segment-setup defect?
s5833: player bolts reach findSegmentObjectSphereHit (0x8005D248, a1=r19 s3 segment ptr, a2=sp+0x88, a3=sp+0x58, a0=NPC shape ctx+0xC) with 64 candidates each, never hit; NPC bolts hit 141/45187.
Hypotheses: (a) player bolts geometrically miss (autopilot doesn't aim); (b) segment/velocity setup for player bolts is wrong (zero-length, unscaled, wrong frame) so it can never intersect; (c) candidate shape/position stale for player-frame candidates.
Step: extend tools/apply_s5833_proj_loop.py (or new s5834): at the CAND hook, for player (P) bolts and for NPC bolts, log segment length (|seg end - start|) distribution and min over candidates of point-to-segment distance minus shape radius; print the first 20 P bolts' segment words and the best candidate. Control: N bolts' HIT events must show min-dist<=radius; P with zero-length segments selects (b). Also hold fire with a KNOWN-near target if one exists (check NPC distances from [plpos] logs).
Run: env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fire.sh s5834 320 (one run, all keys).
HYPOTHESIS-ID: g1-mission-progression
