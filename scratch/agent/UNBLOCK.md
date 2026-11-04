Route 1 — refuted.

Block (s6865, NEEDS-HUMAN: gate-defect): the Stop gate counts turn ends while a run is in flight, and ITERATION.md does not say whether iterations may wait on runs.

Evidence:
- ITERATION.md does say: "waiting on an in-flight or queued soak" is listed as never a block, and the Soak queue section gives the route.
- The observation that proved the gate change unnecessary: the unreported arm ran in one foreground Bash call (19:21:25-19:25:00) with no turn end and no gate involvement. g1_lvl1s6865liveb: flight 135 s, alive, 0 stalls, 0 crash lines.
- Arm A had already finished clean before the stop: g1_lvl5s6865regen, flight 306 s, alive, 0 stalls, 0 crash lines.

No gate or contract file changed. s4563-dead-code-removal closed H-dead, one run per arm. Details: PORTING-STATE Session 6866.
