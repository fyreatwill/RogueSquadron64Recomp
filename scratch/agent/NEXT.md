# Next work unit: M5 exact retail-to-port byte join

HYPOTHESIS-ID: m5-exact-retail-port-byte-join

Add an oracle-side export of exact sampled byte offsets and subrange FNV for
the already watched source span, then run one batched retail/port capture.
This is the next experiment after the s3735 maintenance compaction. Do not
change port behavior or add a mitigation.

Competing hypotheses:

- `H-ExactLayoutEquivalent`: retail and port source subranges have matching
  nonzero positions/FNV; the port payload is nevertheless zero.
- `H-LayoutDivergent`: the exact nonzero positions/FNV differ, proving the
  current comparison is misaligned.
- `H-RetailOnlyProducer`: retail positions are populated while the same port
  positions remain zero in source-DMA payloads.

Discriminator: the oracle whole-RDRAM positive-control count and both target
phases must be nonzero, and both port arms must pass their controls. Matching
positions/FNV selects `H-ExactLayoutEquivalent`; nonmatching positions/FNV
selects `H-LayoutDivergent`; matching retail positions with zero port payload
selects `H-RetailOnlyProducer`. Any missing control or target phase is
unevaluable.

Exact command basis: adapt
`scratch/agent/run_s3733_m5_retail_source_payload.sh` and
`scratch/agent/run_s3730_m5_source_layout.sh`; update the oracle export and
the port/retail byte/FNV fields in one build, then run the paired capture.
