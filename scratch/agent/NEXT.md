# NEXT work unit (bounded pre-chain writer attribution)

HYPOTHESIS-ID: m3-prechain-writer-attribution

The s791 source audit found disjoint consumers for s785-s790. The next unit
must identify whether the known RT64 writeback writer also precedes the other
pre-chain failures. Do not add a guard from a near-zero fault shape.

## Competing hypotheses

- H-shared-writer: the RT64 writeback path is a common upstream writer.
  Prediction: phase-scoped telemetry shows a writeback/free-list event before
  each crash family in one run or in the existing aligned records.
- H-independent-writers: each failure has a distinct upstream origin.
  Prediction: at least one crash occurs with writeback/free-list controls
  quiet in the relevant phase, or source paths remain disjoint.
- H-writer-unresolved: corruption precedes all available telemetry.
  Prediction: controls are positive but no writer event temporally precedes
  the crash or identifies its destination.

## Discriminating measurement

One build/run carrying existing passive provenance, free-list, and writeback
telemetry, with budgets reset at VI 640 and VI 1024. Correlate the last
writeback destination/range and free-list fault/restore event against the
first pre-chain crash. Positive control is the existing `scope=control`
provenance record; a counter that merely fires is not a result.

## Exact audit

1. Use the existing low-noise reachability recipe and arm all passive
   breadcrumbs plus the positive control.
2. Record whether writeback/free-list events precede the crash in the same
   phase; do not interpret runs that die before the phase gate.
3. Select H-shared-writer, H-independent-writers, or H-writer-unresolved from
   the correlation. No mitigation is allowed.

Expected outcomes: a same-phase writeback predecessor selects H-shared-writer;
quiet/disjoint paths select H-independent-writers; positive controls without a
writer predecessor select H-writer-unresolved. A pre-gate death is unevaluable
and requires the fixed version now, not a conclusion.
