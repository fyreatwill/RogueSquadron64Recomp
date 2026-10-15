# Next work unit
HYPOTHESIS-ID: mission-phase-vi-progress-and-m5-row
1. Offline (no game run): from scratch/agent/s4950_route_soak/run{1..5}.log derive a per-run VI-progress metric (e.g. last [phase]/VI count vs wall time; time from mission entry to kill) to replace the invalid `stalled=1` grep (stalled=1 appears at title/hangar/mission VIs alike, s4952). Report whether any run shows VI progress halting after mission entry.
2. Then write a mission-phase M5 qualification row in docs/M5-AUDIO-PLAN.md using the s4950 mission route as the phase control (new positive controls required).
Owner-only (not decided by the loop): declaring the recomp milestone done.
