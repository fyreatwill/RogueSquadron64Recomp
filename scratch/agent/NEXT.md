# NEXT work unit (classify the four unmatched bridge E9 slots)

HYPOTHESIS-ID: m3-e9-command-boundary

Build one phase-gated, telemetry-only probe that keeps the current E9 boundary
records and also logs every RT64 command start and pending completion whose
address lies in the exact bridge submit range, with submit serial/task/range
attached. Keep runtime behavior and mitigation code unchanged. Require the
existing positive controls in the same run.

Competing hypotheses and discriminator:

- H-range-association: the four s836 unmatched records are not in the parser
  call/range that the current task label suggests. An exact range record tied
  to a different parser call selects this.
- H-pending-path: an unmatched slot belongs to a split command and appears in
  pending metadata before completion. A pending record tied to the slot selects
  this.
- H-other-filter: an unmatched slot is a parser command start or span in the
  exact range but reaches no E9 completion record. An in-range start/span with
  no completion selects this.

The 582 s836 span-covered slots remain settled boundary-overcount evidence and
are not re-litigated. The run must reach VI 1024 and fire the existing four
E9 provenance controls before any null is interpreted.

Expected commands: add all records in one build, run the established
phase-gated VI-1024 recipe from `build/` with `ROGUESQ_LOG_E9_BOUNDARY=1`,
capture one log, and inspect bounded windows. No mitigation is authorized.
