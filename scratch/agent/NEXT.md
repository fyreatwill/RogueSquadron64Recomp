# NEXT work unit — M5 route repair/handoff

HYPOTHESIS-ID: m5-route-repair-handoff

## Single work unit

Use a genuinely new port-side handoff edge to explain the reproducible
pre-title VI-640 stop. Retain the retail and port positive controls. The
candidate should be tied to the already-grounded retail
`bufferArbiterProducerMark` handoff at `0x8001BCE4`, but must not repeat the
selector-byte watch or modify audio behavior.

## Competing hypotheses

- H-ProducerHandoff: the port fails to publish or consume the producer mark
  that precedes target VI routing; retail executes the mark in title/hangar,
  while port does not or sees a different state.
- H-RoutePredicate: the producer mark is present and consumed, but the port’s
  target predicate rejects the resulting state before VI-1024/512.
- H-Ordering: both values exist, but publication/consumer ordering differs
  across the retrace or message boundary.
- H-NotHandoff: the handoff matches; the first divergence is another upstream
  state machine edge, so stop expanding this candidate without a new trace.

## Discriminating measurement

One phase-keyed table must join, for retail and port, producer-mark entry and
value, consumer entry and value, live VI width/origin, pending mode/selector
state, and the first target-route predicate result. The whole-RDRAM oracle
watch and its title/hangar phases are required positive controls; the port
AUTOPILOT arm and selector-positive marker are required port controls. The
first divergent row selects the hypothesis: missing/different producer
(H-ProducerHandoff), equal handoff but rejected predicate (H-RoutePredicate),
equal values with reordered publication (H-Ordering), or equal complete
table (H-NotHandoff). Missing target phase makes downstream rows unevaluable.

## Exact commands

1. Inspect the existing retail `bufferArbiterProducerMark` oracle recipe and
   port route diagnostics; do not add a field without a corresponding retail
   or port join key.
2. Build one Debug `RogueSquadron64Recomp` target carrying the complete
   handoff table.
3. Run the retail oracle and port AUTOPILOT capture with
   `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and the whole-RDRAM
   positive control; include the existing title/hangar route schedule.
4. Write `scratch/agent/s<session>_m5_route_handoff/AUDIT.md` with all rows,
   controls, selected/refuted hypotheses, and unevaluable phases. Any route
   change requires an `ORIGIN:` naming its writer and legitimacy; otherwise
   make no behavior change.
