# NEXT work unit (s2870) — M5-route-requalification

HYPOTHESIS-ID: M5-route-requalification

## Work unit

Re-qualify the known port route with one image arm only, using the longer
validated autopilot schedule and the same passive route/task/audio markers.
The current pair's pre-title stop makes its downstream nulls unevaluable;
this unit is route qualification, not an audio publication conclusion.

## Competing hypotheses and discriminator

- H-route-recoverable: a single image arm with the validated long schedule
  reaches title and hangar and emits task-return/SP-completion markers.
- H-route-still-failing: it remains at pre-title `VI 640 @ 0x0066A500` despite
  the known-good schedule and controls.
- H-route-crash: it reaches a crash/abort before either target phase.

The discriminator is one phase-gated table containing `[phase]`, dispatch,
task ABI, image-stage, audio-return, audio-SP-route, and crash/abort rows.
Title plus hangar selects H-route-recoverable; pre-title selects
H-route-still-failing; a crash marker selects H-route-crash. No downstream
null is interpretable unless both target phases qualify.

## Exact command

Build if needed:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Run one image arm from `build/` for 120 seconds, using
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1`,
`ROGUESQ_SPIN_YIELD=1`, all existing M5 markers, and autopilot
`6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,66:start,76:start`.
Use `PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1`, capture under
`scratch/agent/s2870_route_requalification/`, and SIGKILL the game after the
window.
