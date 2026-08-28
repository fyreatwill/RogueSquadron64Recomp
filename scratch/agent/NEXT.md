# NEXT work unit (s2988) — M5 buffer-arbiter route repair A/B

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Unit

Run one same-build paired port capture with the existing host-side retrace
transition repair enabled only in the treatment arm:
`ROGUESQ_FORCE_BUFFER_PROGRESS=1`. Keep the control identical with that
variable unset. Retain LLE/task positive controls, title/hangar VI phase gates,
route-state and target-contract logs, and crash/abort markers.

## Competing hypotheses and discriminator

- `H-buffer-repair`: forced 4→5→0 retrace transitions unblock the route; the
  treatment reaches title or hangar while control remains at pre-title VI 640.
- `H-repair-irrelevant`: both arms have the same phase boundary and route rows;
  the transition driver is not the missing handoff.
- `H-repair-harmful`: the treatment crashes, aborts, or loses the task-positive
  control before a target phase, showing this repair is unsafe for this route.

The discriminating measurement is a single table comparing each arm’s LLE task
positive-control count, phase widths/origins, `bufferArbiterProducerMark`
route/target rows, and crash/abort markers. A target phase in treatment selects
`H-buffer-repair`; equal pre-title phases select `H-repair-irrelevant`;
degraded treatment selects `H-repair-harmful`.

## Commands

1. Build `Debug` target `RogueSquadron64Recomp`.
2. Run `scratch/agent/run_s2988_m5_buffer_repair_ab.sh`, which launches both
   arms from `build/` and writes results under
   `scratch/agent/s2988_m5_buffer_repair_ab/`.
3. Summarize both logs and phase/task controls in the session ledger.

