# NEXT (s7371)
s7370 was the maintenance iteration (CURRENT-TRUTH 61.0 -> 26.7 KB). This unit = CURRENT-TRUTH Next steps item 1.

HYPOTHESIS-ID: tsan-mission-coverage
Goal: the class-AE (s7354) LIMIT. TSan runtime coverage has never reached mission threads (present / workload / audio under load). With the s7369
ucode exemption the TSan arm runs ~13 gfx tasks/s, but ROGUESQ_AUTOPILOT events are wall-clock-timed, so the route diverges from the
owner route whenever game speed differs (s7369 c2 split at press 4 and never called initMission).
Work unit (one build): add ROGUESQ_AUTOPILOT_CLOCK=frames to the autopilot (main.cpp ~11223): event times count game frames
(rs64_dpc_get_cumulative_fullsyncs() / 30 per "second", or a swap count) instead of wall time; default stays wall. Positive control: the
normal build/ with CLOCK=frames reaches initMission on the s7366 AP2 route (same as wall clock at full speed). Then
`env RECIPE=... zsh scratch/s7366/tsan_run.zsh ../s7370/m1 900 "ROGUESQ_AUTOPILOT_CLOCK=frames"` and
`python3 tools/s7354_tsan_report.py scratch/s7370/m1/tsan*`.
Hypotheses for the mission-phase report: H-clean (only SEM/BENIGN/EXT rows, as at boot), H-race (a new B row on a mission-only host
path: present queue, workload, audio backlog trim, spill reset), H-stall (TSan still too slow in flight: tasks/s < 2 -> report flight
coverage as partial).
