# Next work unit: M5 task-data producer boundary

HYPOTHESIS-ID: m5-task-data-producer-boundary

Session 3752 closed the source-DMA producer/read class: the qualified real
arm joined the expected `0x1798B0 -> DMEM 0xCB0` descriptor, but the task-data
object at `0x80171E70` was already zero. Move one boundary upstream and census
the bounded producer/read class that populates that task-data object. Do not
repeat the nine closed route loads, the invalid route-preparation hook, or
alter `0x800078EC`.

Competing hypotheses:

- `H-TaskDataProducerAbsent`: no nonzero task-data producer or task identity
  appears before the qualified source DMA after controls and both phases.
- `H-TaskDataProducerPresent`: a nonzero producer populates the joined task
  data, but a later task handoff clears or selects another object.
- `H-TaskDataJoinMismatch`: a producer is present, but its task generation,
  pointer, or route identity does not match the qualified source-DMA rows.

Discriminator: one phase-gated census must log every bounded task-data producer
and reader candidate, task pointer/generation, route ordinal/row, payload FNV
and nonzero count, plus the existing source-DMA join. A nonzero producer joined
to `0x80171E70` selects `H-TaskDataProducerPresent`; a producer with a distinct
task identity selects `H-TaskDataJoinMismatch`; no producer rows after live
controls and both phases selects `H-TaskDataProducerAbsent`. Missing controls
or either target phase is unevaluable.

Ground truth before building: run the retail oracle with the whole-RDRAM
positive control first, then source-span and task-data watches plus the known
retail writer-PC attribution. Add only bounded hooks through regeneration-safe
fixup scripts. Run qualified real and silent arms from `build/` with the
explicit autopilot schedule; kill every arm with SIGKILL.
