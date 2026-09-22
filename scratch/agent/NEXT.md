# Next work unit: M5 full-span source producer census

HYPOTHESIS-ID: m5-retail-port-source-layout

Run one diagnostic-only, phase-gated real-audio port capture that extends the
source producer census from `0x1797B0..0x179930` to the full retail-measured
span `0x1797B0..0x179A48`. Join every producer/store or DMA segment to the
source DMA, clear sequence, route ordinal, and payload hash. Keep the existing
retail source witness and positive controls as the independent comparison;
do not change behavior.

Competing hypotheses:

- `H-UninstrumentedPortProducer`: a port producer writes the retail-shaped
  nonzero source bytes in the extension or an unobserved path.
- `H-PortSourceClearOrdering`: a port producer creates nonzero content, then a
  legitimate later clear erases it before the source DMA.
- `H-PortSourceWriterDivergence`: no complete port producer row carries the
  retail-shaped nonzero content before the source DMA; the zero fill remains
  the final observed writer.

Discriminator: a full-span nonzero producer segment before the source DMA
selects `H-UninstrumentedPortProducer`; an ordered nonzero producer followed
by the known clear selects `H-PortSourceClearOrdering`; an exhaustive
zero-only producer/clear sequence with zero source DMA selects
`H-PortSourceWriterDivergence`. The RSP/source positive controls, target VI,
and source-DMA joins must all fire; otherwise the result is unevaluable.

Exact command basis: extend `scratch/agent/run_s3730_m5_source_layout.sh`
and the source-range hook's upper bound to `0x179A48`, then run it from
`build/` with SIGKILL cleanup. Capture both A/B arms in one build/run if the
real arm is stable; otherwise record the pre-target failure and rerun the
fixed arm immediately. Save results under
`scratch/agent/s3731_m5_full_span_producer/` and write
`docs/M5-S3731-*.md`.
