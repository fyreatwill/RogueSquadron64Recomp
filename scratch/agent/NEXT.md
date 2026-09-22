# Next work unit: M5 retail/port source-layout join

HYPOTHESIS-ID: m5-retail-port-source-layout

Session 3729 selected `H-RetailSourceNonzero`: retail retains nonzero source
content while the qualified port's corresponding image source is zero. Do one
batched diagnostic port run that captures the same source range, task-data
range, writer PCs, and phase/timing fields as the oracle, then join by target
VI phase and source-DMA ordinal. Do not change behavior.

Competing hypotheses:

- `H-PortSourceWriterDivergence`: the port's source writer/content producer
  differs from retail before the same image-task handoff.
- `H-PortSourceClearOrdering`: the port has matching producer content but a
  later legitimate clear erases it before the source DMA.
- `H-SourceLayoutMismatch`: the ranges or source-DMA descriptor mapping differ
  even though the producer timing is equivalent.

Discriminator: in one port run, source bytes nonzero before the source DMA
with a matching producer sequence select `H-PortSourceClearOrdering` if the
later clear is final; a writer/content mismatch selects
`H-PortSourceWriterDivergence`; matching writer/content timing but different
DMA source/task joins selects `H-SourceLayoutMismatch`. The phase/RSP controls
and a nonzero source snapshot are required; a missing target phase is
unevaluable.

Exact command basis: adapt the port arm in
`scratch/agent/run_s3728_m5_image_payload.sh`, retain all passive M5 logs,
and add the source/task/output payload fields to the existing phase-gated
image-DMA table. Save the result under
`scratch/agent/s3730_m5_source_layout_join/`, then write
`docs/M5-S3730-*.md`.
