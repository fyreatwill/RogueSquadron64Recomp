# Next work unit: identify the zero DMEM payload producer

HYPOTHESIS-ID: m5-zero-dmem-producer

S3693 qualified the DMA boundary. The port produced 3,178 hangar input-DMA
rows and 512 source-range DMA-to-RDRAM rows; those rows were phase-visible but
had zero payload and zero post-write span. The DMEM-side writer census was
active, and no hangar scalar writer fired.

Competing hypotheses:

- `H-ZeroDMEMProducer`: the port creates zero payload in DMEM before the DMA.
- `H-DMEMJoinMismatch`: the zero payload belongs to another route or DMEM
  lifetime, not the observed hangar DMA row.
- `H-RetailSourceIsDifferent`: retail's phase-gated writer PCs use a source
  path that the port does not reproduce.

Discriminating measurement: one phase-scoped table for all 512 hangar
DMA-to-RDRAM rows, joining the immediately preceding DMEM scalar/vector
store, RSP source, memset, or host-side producer with payload FNV/nonzero
fields and route identity. The retail arm must retain its positive controls
and phase-gated writer-PC histogram. A same-route zero DMEM producer selects
`H-ZeroDMEMProducer`; a contradictory route join selects
`H-DMEMJoinMismatch`; no corresponding port producer alongside retail writer
PCs selects `H-RetailSourceIsDifferent`. Missing controls is unevaluable.

Before building, obtain retail ground truth with whole-RDRAM, source-span,
writer-PC, title, hangar, and type-2 controls. Then batch all DMEM producer
fields into one build and run the real-audio and silent arms together. Kill
both game processes with SIGKILL and run from `build/`.
