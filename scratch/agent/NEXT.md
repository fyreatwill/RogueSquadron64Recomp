# NEXT: G1 - player bolts: segment well-formed (s5834). Aim-miss (a) vs stale shape centre (c)?
s5834: P segments nonzero (|dir|^2=0.53, horizontal, at player altitude), 0/32869 hits; N 138/40859. (b) refuted.
Step: hook return of 0x8006AE58 (called at 0x8006A97C in findSegmentObjectSphereHit; v0=s2 shape centre ptr) via a new apply_s5835 patch in funcs_16.c: log centre xyz plus distance from segment point for first 20 P and N candidates, and min P-bolt-to-centre distance per 4096 calls. Control: N hits must have point-to-centre dist <= radius-ish. If P min dist is large (>>radius) -> aim; if centres are stale/zero -> (c). Also try F1/F2 variants where autopilot steers toward an NPC if possible.
Run: env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fire.sh s5835 320
HYPOTHESIS-ID: g1-mission-progression
