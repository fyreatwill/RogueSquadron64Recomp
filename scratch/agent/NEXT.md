# NEXT: G1 - s5839: forced P hits restricted to class-1 shapes; measure objective counter 1 delta.
s5838 (inconclusive): victim snapshot used wrong pointers and teleport hit arbitrary NPCs (ids 0x58-0x1C8), not class-1 (0x18-0x2D, s5828).
Step: in tools/apply_s5835_sphere_probe.py TELE gate, only teleport when the candidate slot id (or desc +0x70) is class-1; log objective counter 1 (see s5787/s5788 for address; player counter bump at 0x80130B80 per s5833) before/after each forced P SEND, N sends as control.
Outcomes: counter climbs -> G1 is steering only (stick yaw ignored, s5821); no climb -> msg-5 receiver for class-1 ignores player-sourced hits (check shooter id test).
Run: env ROGUESQ_LOG_HITS=1 ROGUESQ_TELE_BOLT=1 zsh scratch/agent/g1_fire.sh s5839 320
HYPOTHESIS-ID: g1-mission-progression
