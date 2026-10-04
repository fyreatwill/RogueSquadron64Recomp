# Next work unit: classify the next M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-class

Run one same-build, phase-gated retail/port qualification for candidate PCs
`0x80005060`, `0x80005064`, and `0x80005068`, using the existing oracle and
port controls. Build `RogueSquadron64Recomp` once before the paired run. Do
not add instrumentation: the existing whole-RDRAM, title-1024, hangar-512,
oracle-completion, and port image-DMA controls are the ground-truth contract.

Competing hypotheses:

- H1: at least one candidate is a legitimate retail target-phase writer; it
  will execute in the qualified phase and produce a post-target scalar row.
- H2: candidates execute in the target phase but do not produce a qualified
  post-target scalar; they are wrappers, unrelated stores, or non-writers.
- H3: candidates do not execute in the qualified target phase; this bounded
  class is not the missing writer.
- H4: controls fail (missing positive control, route phase, or crash), so the
  candidate result is unevaluable and must not be promoted.

Discriminator: the retail oracle must pass all positive controls, including
whole-RDRAM writes, title VI 1024, hangar VI 512, and completion. Then classify
each PC by target-phase execution, candidate-span rows, post-target rows, and
scalar samples. The paired port must reach hangar with image-DMA joins and no
crash/abort; otherwise port payload is unevaluable. H1/H2/H3 are bounded to
this exact candidate set.
