# NEXT: G1 — which objective never advances once the class-2 NPC fail path is removed

Work unit: run `scratch/agent/g1_inv1.sh <tag> 600` (ROGUESQ_NPC_INVULN=1, LOG_HUDBIT=1) with `[ccosnap]`
boolean-array snapshots armed; tabulate bools/counters (kill count 0x138060.., waypoint, timer) at mission
onset, mid, and end. Positive control: at least one bool/counter must change.

Hypotheses: (a) the enemy-kill objective never increments because autopilot never hits droids;
(b) objective advances but the win check is gated on a bool the port never sets (e.g. dialogue-flag bool 7);
(c) mission timer/other fail path fires. Discriminator: which values change between onset and end.
If (a): next engineering step = an aim-assist autopilot (stick toward nearest hostile) in main.cpp.

HYPOTHESIS-ID: g1-mission-progression
