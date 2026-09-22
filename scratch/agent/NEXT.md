# Next work unit: identify the stale-input payload boundary

HYPOTHESIS-ID: m5-stale-input-payload

S3690 selected `H-StaleInputAcrossReuse`: 244/244 absent-generation hangar
source rows joined an earlier/equal input-DMA task identity. The next unit is
one phase-scoped instrumentation change and one qualified capture.

Competing hypotheses:

- `H-StaleInputPayload`: the earlier input task already transfers the zero
  payload seen by the hangar source witness.
- `H-SourceOverwrittenAfterInput`: the selected input task transfers nonzero
  data, but RDRAM is overwritten before the source witness observes it.
- `H-StaleTaskPointerOnly`: the task-data pointer is stale while the input
  payload identity belongs to a distinct task.

Discriminating measurement: add input-DMA source FNV/nonzero and task-data
pointer fields, carry them through the source witness, and classify every
absent-generation hangar row in one table against the later stage row. Title
input rows must be the same-run nonzero positive control. Input/source equal
zero selects `H-StaleInputPayload`; nonzero input followed by a changed source
selects `H-SourceOverwrittenAfterInput`; a pointer/payload identity mismatch
selects `H-StaleTaskPointerOnly`. Missing controls or rows are unevaluable.

Before building, obtain the independent retail ground-truth capture with the
whole-RDRAM, descriptor, source-span, title, hangar, and type-2 controls. Keep
the silent and real-audio port arms in one build/run, phase-gate on VI, and do
not alter guest state or add a mitigation. The implementation belongs in the
runtime input-DMA hook and its source-witness fields; export submodule patches
if `lib/` changes.

Commands after the instrument is written:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3690_m5_stale_input_payload.sh

Kill both processes with SIGKILL. The recipe must launch and watchdog both
arms itself, run from `build/`, and retain positive controls in the same
capture.
