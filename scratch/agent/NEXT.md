# NEXT work unit (s2973)

HYPOTHESIS-ID: m5-port-route-preparation

## Unit

Run one phase-gated port route-preparation census using the existing
regeneration-safe M5 route probes. Launch silent and image arms concurrently
from one Debug build, with the validated AUTOPILOT and the retail oracle's
positive-control recipe retained. Add no new instrumentation and change no
behavior. Capture pre-target route preparation, VI-commit transition,
identity-edge, route-state, and target-candidate rows, keyed by arm and VI
phase, to explain the s2972 port stop at VI 640.

## Competing hypotheses and discriminator

- H-route-prep-absent: after the port reaches VI 640, no route-preparation
  row has `target=1`; the target handoff is never prepared on the port.
- H-route-identity-stale: target preparation rows exist, but the subsequent
  VI transition or identity-edge rows do not commit the requested title/hangar
  origin; the port route state is stale or rejected before presentation.
- H-audio-arm-route: the route-preparation/identity table diverges between
  silent and image arms, making the audio dispatch arm part of the route stop.

The discriminator is one complete table of all route-prepare rows (including
`target` and requested width/origin), VI-transition rows, identity-edge rows,
route-state rows, target-candidate rows, and phase transitions for both arms.
Target preparation with no commit selects H-route-identity-stale; no target
preparation in either arm selects H-route-prep-absent; an arm-only difference
selects H-audio-arm-route. A missing phase transition keeps downstream audio
rows unevaluable but does not erase pre-target route evidence.

## Commands

1. Build once: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
2. Run the existing corrected pair wrapper from
   `scratch/agent/s2972_m5_step1_qualified_route/run_pair.sh`, copied or
   parameterized into a new s2973 artifact directory. Add
   `ROGUESQ_LOG_M5_ROUTE_PREPARE=1`, `ROGUESQ_LOG_M5_ROUTE_TRANSITION=1`,
   `ROGUESQ_LOG_M5_IDENTITY_EDGES=1`, `ROGUESQ_LOG_M5_ROUTE_STATE=1`, and
   `ROGUESQ_LOG_M5_ROUTE_CANDIDATE=1` to both arms. Keep
   `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and
   `PROBE_LEAVE_OK=1`; terminate the oracle and both game process groups with
   SIGKILL.
3. Summarize every arm's route table and select exactly one hypothesis. Do
   not interpret service/slot/PCM nulls unless a target phase is observed.
