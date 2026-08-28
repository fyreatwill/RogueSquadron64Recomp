# NEXT work unit (s2989) — M5 independent buffer-arbiter signal handoff

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Unit

Use a new, independently grounded port-side handoff candidate in the
`bufferArbiterProducerMark` call/signal chain. Keep the rejected
`ROGUESQ_FORCE_BUFFER_PROGRESS` driver disabled. First use the retail oracle
and static map to select one producer or signal edge; then batch one
phase-scoped probe for that edge and run the existing route capture only if
the candidate has a concrete port callsite.

## Competing hypotheses and discriminator

- `H-new-handoff-equivalent`: the candidate executes at the port’s VI-640
  boundary and matches the retail handoff/state tuple; the missing route is
  elsewhere.
- `H-new-handoff-missing`: retail executes the candidate in title/hangar but
  the port has no corresponding target-phase execution, selecting this edge as
  the next repair boundary.
- `H-new-handoff-route`: a bounded change at the selected edge reaches title or
  hangar without degrading the task positive control.

The discriminator is one table with retail PC attribution, port candidate
rows, LLE audio-task positive-control counts, VI phase transitions, target
route rows, and crash/abort markers. A candidate must pass its positive control
and phase gate before any route conclusion is accepted.

## Commands

Inspect `tools/oracle/README.md`,
`scratch/agent/s2971_m5_route_qualification/RESULTS.md`, and the existing
buffer-arbiter call chain. Do not build until the candidate and outcomes are
written here. Then build Debug and run a new capture under
`scratch/agent/s2989_m5_new_handoff/`, using SIGKILL/watchdog semantics and
`PROBE_PHASE_WIDTH=512 PROBE_KEYS_FROM_PHASE=1`.

