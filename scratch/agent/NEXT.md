# NEXT work unit (s2402) — repair route-validity, then capture the clear edge

HYPOTHESIS-ID: m5-image-stage-route-order-perturbation

## Work unit

First repair the same-build two-arm driver so both arms reach the 1024 title
origin with the lifecycle activation control before interpreting the already
landed identity-edge table. Use the qualified LLE/image route,
`ROGUESQ_STUB_MISSING_FUNCS=1`, `PROBE_PHASE_WIDTH=1024`, and the existing
route/stage probes. Keep both arms in one build and concurrent; use a bounded
launch/watchdog schedule that does not add `ROGUESQ_LOG_ALL`. Do not change
task data, audio, gate, fallback, dispatch, VI, output behavior, or mitigation.

Before building, arm the retail oracle's whole-RDRAM positive control and the
target-origin control. In the port, keep one activation-control row per arm
and the phase-keyed clear-edge table. If the route controls pass in both arms,
use that single capture to distinguish where the accepted route identity is
cleared between `rs64_audio_route_prepare` and `rs64_audio_image_stage`.

## Competing hypotheses and discriminator

- H-HostClearBetweenPrepareStage: the host-side route identity is explicitly
  cleared between preparation and stage entry.
- H-GuestClearBeforeHostStage: a guest-side edge clears the source state before
  the host stage callback observes it.
- H-SeparateIdentityRead: the accepted identity remains live, but stage entry
  reads a different identity source.
- H-RouteDriverStillInvalid: at least one arm fails to reach target, so no
  clear-edge hypothesis is testable.

The first discriminator is both-arm route validity: each arm must emit its
activation row, target-origin row, and target stage rows. If either is absent,
select `H-RouteDriverStillInvalid` and do not interpret null identity rows. If
both pass, the single phase-keyed table has one row per retained stage call
with preparation sequence, clear-edge sequence/PC/source, stage sequence,
route-valid state, route ordinal/row, and arm. A clear event between equal
preparation and stage sequence selects the corresponding clear edge; no clear
with invalid stage identity selects separate-source use.

## Exact command shape

`cmake --build build -j2`

Run the two same-build arms with the controls from
the repaired driver, plus the oracle control recipe in
`tools/oracle/README.md`; use `env ... zsh ...` for env-prefixed commands.
Require one activation-control row and target-origin rows in both port arms.
Reduce only route-valid logs with the existing identity reducer.

Expected outcomes: both-arm route failure selects `H-RouteDriverStillInvalid`;
host clear rows select `H-HostClearBetweenPrepareStage`; guest clear rows select
`H-GuestClearBeforeHostStage`; no clear rows with persisting accepted identity
select `H-SeparateIdentityRead`.
