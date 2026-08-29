# NEXT work unit — audit the pre-title route boundary

HYPOTHESIS-ID: m5-port-route-boundary

Session 3224 resolved the route-selection dependency with a local, retail-
qualified route: `3:start,7:start,11:start,15:a,30:start,45:start,60:a,75:start,90:a`.
Retail passed the whole-RDRAM positive control and reached title 1024 and
hangar 512. A same-build port silent/image pair using the same route passed
audio-dispatch controls (69 rows per arm) but both stopped at VI 640 origin
`0x0066A500`; neither reached title or hangar. A12 remains closed.

## Competing hypotheses

- `H-PortInputBoundary`: the port's internal autopilot schedule or phase-
  relative input handling diverges from the retail route before title.
- `H-PortStateBoundary`: a non-input title/state publication differs before
  the first 1024 VI transition.
- `H-PortSchedulerBoundary`: host scheduling or queue progress prevents the
  same route transition despite valid input/state evidence.

## Discriminator

Run one same-build capture of both arms with route, pad-host/pad-SDL, VI-caller,
queue/recv, and route-state controls. Positive control: both arms' dispatch
rows and initial VI transition. Independent boundary: retail oracle's
whole-RDRAM control plus title/hangar phases. The first post-640 divergence
among input delivery, state publication, or scheduler/queue progress selects
the hypothesis. Do not infer target-phase audio nulls while 1024 is absent.

## Exact start

Build `cmake --build build --config Debug --target RogueSquadron64Recomp`, then
run both arms concurrently from `build/` with `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LOG_ALL=1`, and the route above via `ROGUESQ_AUTOPILOT`; add
`ROGUESQ_LOG_VI_CALLERS=1`, `ROGUESQ_RECV_TRACE=1`, and
`ROGUESQ_LOG_M5_ROUTE_STATE=1`. Capture non-dot final paths and SIGKILL at the
watchdog boundary.
