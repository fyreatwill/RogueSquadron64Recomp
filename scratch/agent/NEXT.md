# Next work unit: M5 retail source-payload boundary

HYPOTHESIS-ID: m5-retail-source-payload-boundary

Run one independent retail-oracle capture using the existing validated Start
schedule. Watch the full source span `0x1797B0..0x179A48`, the source/output
task ranges, target-phase writer PCs, and type-2 task descriptors at both
`0x00790400` and `0x006AB400`. Keep the whole-RDRAM positive control and do
not change port behavior.

Competing hypotheses:

- `H-RetailSourceZero`: retail source/output payload is also zero at the
  target boundary.
- `H-RetailSourceNonzero`: retail retains nonzero source bytes and writer PCs,
  confirming a port-versus-retail producer divergence.
- `H-RetailOutputOnly`: only the retail output span is nonzero, moving the
  discrepancy downstream of source production.

Discriminator: the oracle's positive-control count must be nonzero and both
target phases must be reached. Nonzero source bytes plus target-phase writer
PCs selects `H-RetailSourceNonzero`; zero source and output selects
`H-RetailSourceZero`; source-zero/output-nonzero selects
`H-RetailOutputOnly`. A missing positive control or target phase is
unevaluable, not a null result.

Exact command basis: adapt the oracle portion of
`scratch/agent/run_s3732_m5_image_payload.sh`, save output under
`scratch/agent/s3733_m5_retail_source_payload/`, and write
`docs/M5-S3733-RETAIL-SOURCE-PAYLOAD.md`.
