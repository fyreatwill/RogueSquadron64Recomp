# Next work unit: M5 exact retail-to-port byte join

HYPOTHESIS-ID: m5-exact-retail-port-byte-join

Add an oracle-side exact byte-position/FNV export for the same source subranges
already watched by the port capture, then run one batched port/retail capture.
Keep the whole-RDRAM oracle positive control and the validated Start/autopilot
schedules. Do not add a mitigation or change port behavior.

Competing hypotheses:

- `H-ExactLayoutEquivalent`: exact nonzero positions/FNVs match across retail
  and the corresponding port source subranges.
- `H-LayoutDivergent`: retail's exact nonzero positions/FNV differ, proving the
  current comparison is misaligned.
- `H-RetailOnlyProducer`: exact retail source bytes are populated but the port
  source-DMA payload remains zero at those same positions.

Discriminator: the oracle positive-control count and both target phases must
be nonzero, and both arms must pass their source controls. Matching nonzero
byte positions/FNV selects `H-ExactLayoutEquivalent`; nonmatching positions/FNV
selects `H-LayoutDivergent`; matching retail positions with zero port payload
selects `H-RetailOnlyProducer`. Any missing control or target phase is
unevaluable.

Exact command basis: adapt
`scratch/agent/run_s3733_m5_retail_source_payload.sh` and
`scratch/agent/run_s3730_m5_source_layout.sh`; add the oracle export and all
port/retail byte/FNV fields in one build/run.
