# Next work unit: mission-qualified run of the s4994 mission-origin s4540 caller sample

HYPOTHESIS-ID: m5-s4540-mission-sample

Premise correction (s5009): the per-origin bad-row budget was already run in s4993 (0 bad rows at mission origins, 2,602 pre-mission). Do NOT redo it.
Do: enqueue a soak recipe (soak_queue/) using the already-qualified mission route (s4993/s4959 recipe that reached origin 0x690400 at ~181 s) with tools/apply_s4994_s4540_mission_sample.py built in. Success = mission sample rows appear at 0x00690400/0x00620400 with crash=0.
Outcomes: rows show current 20/0x8018C720 -> mission path is current, stale pair is pre-mission-only (close thread). Rows show stale 32/0x801714D0 -> uninstrumented reader/propagation. Zero rows with route controls passed -> no ordinary caller in mission.
No guard, rewrite, or mitigation. Owner question pending in BLOCKED.md.
