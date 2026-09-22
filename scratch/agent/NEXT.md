# Next work unit: close the port-versus-retail hangar-writer gap

HYPOTHESIS-ID: m5-hangar-writer-gap

S3692 added a complete scalar-store witness. Retail had hangar writers at
`0x800078EC`, `0x80007670`, and `0x8001F...` sites. The port produced 384
title rows, all `0x800078EC` zero-fill stores, and all 3,178 hangar input rows
carried that stale writer snapshot; no hangar scalar writer fired.

Competing hypotheses:

- `H-MissingGeneratedWriter`: a retail hangar writer family is absent from
  the port dispatch.
- `H-WriterOutsidePhaseGate`: the port writer runs but route publication makes
  it invisible to the phase gate.
- `H-NonScalarWriterPath`: the port writes through `rs_memset` or a DMA/host
  path not covered by the scalar witness.

Discriminating measurement: one phase-scoped table for every title and
hangar input-DMA row, joining the immediately preceding scalar, memset, or
host/DMA writer event, while the retail arm supplies the PC histogram. A
matching hangar writer selects `H-WriterOutsidePhaseGate` only if the port
event is present outside the gate; a missing scalar plus matching memset/DMA
event selects `H-NonScalarWriterPath`; no port event with retail attribution
selects `H-MissingGeneratedWriter`. Missing positive controls or missing title
nonzero rows is unevaluable.

Before building, obtain retail ground truth with whole-RDRAM, source-span,
writer-PC, title, hangar, and type-2 controls. Then batch scalar, memset, and
host/DMA event fields into one build and run the real-audio and silent arms
together. Kill both game processes with SIGKILL and run from `build/`.

Required commands once the instrument is written:

    cmake --build build -j8
    env zsh scratch/agent/run_s3692_m5_input_payload_writer.sh
