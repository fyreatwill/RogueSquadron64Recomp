# NEXT: G1 - s5861: per-bolt 3D distance to class-1 troops (H21 vs H22)
s5860 (offline): H20 refuted - autopilot passes within 0.4-3 u xz of many survivors while firing; survivors show large vertical offset (3D-xz gap 4-6 u), killed ones don't (not clean; plpos is 1 Hz).
Hypotheses: H21 hit-test target set/predicate excludes class-1 troops (bolts pass within hit radius, no hit); H22 bolts never get within radius because of altitude/aim (steer autopilot vertically).
Instrument (one build): extend the s5838 SEND/tick hooks (tools/apply_s5838_send_effect.py pattern, funcs_13.c audioCueDispatcherNpcHandler) or a bolt-update hook to log each live bolt's position per tick and min 3D distance to every class-1 descriptor (spawn1 desc floats w[4..6]); print per-bolt min distance histogram every 4096 ticks. Positive control: a bolt's min distance to the msg-5 victim debris node (known hit) must be ~< hit radius.
Outcomes: bolts within radius of a troop yet no msg to it -> H21; min distance always >> radius, dy-dominated -> H22.
Run: env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fireall.sh s5861 300
HYPOTHESIS-ID: g1-mission-progression
