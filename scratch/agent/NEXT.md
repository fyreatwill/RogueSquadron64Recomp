# Next work unit: M5 retail-to-port source byte/layout join

HYPOTHESIS-ID: m5-retail-port-byte-layout-join

Build one batched port/retail capture that samples the same source subranges
and computes phase-gated byte counts/FNVs at the retail source boundary and
the port source-DMA handoff. Keep the whole-RDRAM oracle positive control and
the validated Start/autopilot schedules. Do not add a mitigation or change
port behavior.

Competing hypotheses:

- `H-LayoutEquivalent`: retail and port sample the same nonzero source layout,
  and the port zero is introduced after the corresponding handoff.
- `H-LayoutDivergent`: retail's nonzero bytes occupy a different source
  layout/range, so the current port comparison is misaligned.
- `H-RetailOnlyProducer`: the aligned retail source is nonzero but the port's
  corresponding producer input is already zero before its source DMA.

Discriminator: the oracle positive-control count and both target phases must
be nonzero, and both arms must pass their source controls. Matching nonzero
byte positions/FNV across aligned subranges selects `H-LayoutEquivalent`;
nonzero retail with zero port at matched positions selects
`H-RetailOnlyProducer`; a shifted/nonmatching retail pattern selects
`H-LayoutDivergent`. Any missing control or target phase is unevaluable.

Exact command basis: adapt the fixed oracle command in
`scratch/agent/run_s3733_m5_retail_source_payload.sh` and the qualified port
source-DMA capture nearest `scratch/agent/run_s3730_m5_source_layout_join.sh`.
Add all byte/FNV fields in one build/run.
