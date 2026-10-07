# Next work unit: add and qualify the non-scalar pre-clear writer census

HYPOTHESIS-ID: m5-pre-clear-nonscalar-writer

Session 4161 qualified the active DMA callback and found no target-span DMA
row. Sessions 4159/4161 closed the generated scalar-store class: all 664
intersecting scalar stores were zero-valued bytes from `0x800078EC`. The
non-scalar guest class still has no positive-control row and must be added
before a null can discriminate.

Competing hypotheses and discriminator:

- H-other-guest-writer: a non-scalar guest operation (memset/copy/unaligned or
  an uninstrumented store class) writes the span; the census shows a nonzero
  guest write with a distinct writer PC before the clear.
- H-host-dma-writer: an active host/RSP DMA write reaches the target span; a
  qualified target-span DMA row appears after the callback.
- H-preclear-snapshot-artifact: the earlier nonzero snapshot is not a live
  target-span write; the complete phase-gated census shows no nonzero pre-clear
  write from either source, despite positive controls.

Exact work: add the regeneration-safe non-scalar guest-write census for
`0x1797B0..0x179A48`, joined by ordinal/order to the existing `0x800078EC`
clear marker. Batch source, destination, width, value/FNV, writer-PC, and
ordering fields in one build and one run. Use:

`zsh scratch/agent/run_s4159_m5_preclear_span_census.sh`

Require whole-RDRAM, title, hangar, and both probe-control gates before
interpreting rows. A distinct non-scalar guest row selects
H-other-guest-writer; a nonzero DMA row selects H-host-dma-writer; no nonzero
row with all controls selects H-preclear-snapshot-artifact. Missing
non-scalar positive-control rows require fixing the census before any
conclusion.
