# NEXT work unit — repair title-scoped source-writer witness

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3459 reached title with the prescribed LLE/spin-yield route, but the
existing writer witness emitted zero title rows. Its positive control fired
only in width-640 phase, so the source-value join remains unevaluable.

Competing hypotheses and discriminating outcomes:

- `H-WitnessGate`: title rows are suppressed by the host phase/origin gate; a
  title-scoped control plus rows after correcting the gate selects this.
- `H-GeneratedRoute`: title execution does not reach the generated
  instrumented stores; a title control elsewhere plus absent store rows
  selects this.
- `H-TitleNoStore`: the title path reaches the instrumented functions but does
  not execute the source-slot stores; function-entry evidence plus absent
  store rows selects this.
- `H-ControlFailure`: no title-scoped positive control fires; the result is
  unevaluable and the witness must not be used for value conclusions.

Before building, repair only the witness gate or add a regeneration-safe
title function-entry control so all four outcomes are distinguishable. Then
build and run:
`cmake --build build --config Debug --target RogueSquadron64Recomp`
followed by
`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_WRITER_PARITY=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 tools/probe.sh scratch/agent/s3460_m5_source_value_witness 45 0.5`.
The discriminator is a title-scoped positive control plus the first
phase/PC/ordinal source-writer value joined to the producer load: corrected
gate selects `H-WitnessGate`, title entry without stores selects
`H-GeneratedRoute` or `H-TitleNoStore` using the entry control, and absent
title control selects `H-ControlFailure`. Do not alter audio waits, slots,
dispatch, clear behavior, or PCM writeback.
