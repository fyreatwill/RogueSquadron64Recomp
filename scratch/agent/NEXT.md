# NEXT work unit (s2879) — m5-new-route-state-discriminator

HYPOTHESIS-ID: m5-new-route-state-discriminator

## Work unit

Choose one genuinely new, ground-truth-first post-dispatch route-state
discriminator from the documented M5 boundary. The autopilot qualification
failed symmetrically at pre-title VI 640, so do not interpret downstream audio
or repeat the consumer census. Before adding port instrumentation, use the
retail oracle to qualify the candidate address/range and its phase behavior,
including the whole-RDRAM positive control. Then build one batched port probe
for all candidate keys and both image/silent arms, only if the oracle selects
a useful discriminator.

## Competing hypotheses and discriminator

- H-route-state-key: a new retail phase-live scheduler/state key is absent or
  differs on the port and explains the pre-title route stop.
- H-route-equivalent: the candidate key is present and phase-equivalent, so it
  does not explain the route stop and selects a different route-state class.
- H-arm-specific: image and silent arms differ at the candidate key or phase
  gate, selecting an audio-arm route effect.

The discriminating measurement is a single phase-gated retail/port table with
whole-RDRAM control count, candidate-key writes/values and PCs, title/hangar
reachability, last VI width/origin, and crash/abort markers. A positive
control that does not fire invalidates the table; a port-invalid pre-title
result leaves the candidate unevaluable rather than supporting H-route-state.

## Exact next commands

Read `tools/oracle/README.md` and `docs/F5-UCODE-REFERENCE.md`, select a new
post-dispatch range, then run the oracle positive control and candidate watch
from its documented launcher. Only after that result qualifies a candidate,
create the regeneration-safe probe and run both arms concurrently from
`build/` with SIGKILL watchdog cleanup. Record the table under
`scratch/agent/s2879_m5_new_route_state/`; run `git diff --check` before
committing.
