# NEXT work unit (s2977)

HYPOTHESIS-ID: m5-route-preparation-port-comparison

## Unit

Implement one bounded phase-scoped port measurement for route preparation at
the corresponding port guest PC. Retain the same-run positive control and
capture route predecessor, arguments, and live VI width/origin in title and
hangar. Do not change the predicate yet.

## Competing hypotheses and discriminator

- H-port-route-matches: port reaches the same route call with predecessor and
  target-phase fields matching retail.
- H-port-route-absent: port does not execute the route call in either target
  phase despite reaching the phase controls.
- H-port-predicate-mismatch: port executes the route call, but predecessor or
  argument/state fields differ from retail.

The discriminator is one same-run table of port route-PC executions in the
already-qualified title and hangar phases, compared with s2976's retail table.
The positive control must fire and both target phase controls must be reached.
Matching rows select H-port-route-matches; phase-reached zero rows select
H-port-route-absent; differing rows select H-port-predicate-mismatch.

## Commands

Use the port's existing phase-aware trace command from the Debug build, with
the route PC and positive-control instrumentation batched in one run. Save
output to `scratch/agent/s2977_m5_route_port/` and record the positive-control
count, phase controls, route rows, and selected hypothesis. If the port route
PC is not yet identified, use the existing `bufferArbiterProducerMark`
handoff probe at `0x8001BCE4` as the route control and document that identity
mapping in the artifact before interpreting nulls.
