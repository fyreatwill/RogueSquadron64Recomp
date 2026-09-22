# Next work unit: M5 port writer-family census at the exact source boundary

HYPOTHESIS-ID: m5-port-writer-family-census

Run one batched port capture that enumerates every phase-gated store touching
`0x1797B0..0x179A48`, retaining the retail oracle snapshot and writer control
as an independent reference. Do not change port behavior or add a mitigation.
Keep whole-RDRAM, both target phases, and both real/silent port controls
mandatory.

Competing hypotheses:

- `H-PortEarlierWriterAbsent`: no port store reaches the exact source span
  before the zero-valued DMA; the retail-only writer boundary is real.
- `H-PortWriterUnlogged`: a port writer reaches the span but the current
  phase-gated instrumentation misses its instruction family.
- `H-PortWriterLegitimateClear`: the port has a legitimate nonzero producer,
  then clears the object before the source DMA; the current zero rows are an
  ordering artifact.

Discriminator: the all-store port census must report the writer PC, store
value/nonzero status, and ordering for every target-span store in both target
phases. No target-span store plus valid controls selects
`H-PortEarlierWriterAbsent`; stores absent from the existing M5 writer hook but
present in the all-store census selects `H-PortWriterUnlogged`; a nonzero store
followed by the clear selects `H-PortWriterLegitimateClear`. Missing any
control or phase is unevaluable.

Exact command basis: adapt
`scratch/agent/run_s3737_m5_retail_writer_join.sh`; add the phase-gated
all-store source-span census to the existing real/silent arms, retain
`--watch-write 0x0:0x800000`, both source watches, both
`--phase-snapshot-watch` options, and
`ROGUESQ_LOG_M5_SOURCE_TRANSITION=1`, `ROGUESQ_LOG_M5_SOURCE_WRITER=1`, and
`ROGUESQ_LOG_M5_INPUT_WRITER=1`.
