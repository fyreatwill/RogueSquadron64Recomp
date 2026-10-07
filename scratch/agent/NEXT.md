# Next work unit: complete the non-scalar pre-clear writer census

HYPOTHESIS-ID: m5-pre-clear-nonscalar-writer

Session 4160 did not observe a host/RSP or RT64-writeback writer into the
exact target span, but the non-scalar guest class and dormant DMA callback
remain instrument gaps. Session 4159 closed the generated scalar-store class:
all 664 intersecting scalar stores were zero-valued bytes from `0x800078EC`.

Competing hypotheses and discriminator:

- H-other-guest-writer: a non-scalar guest operation (memset/copy/unaligned or
  an uninstrumented store class) writes the span; the census shows a nonzero
  guest write with a distinct writer PC before the clear.
- H-source-range-hook-gap: the active RSP DMA-to-RDRAM path is not reaching the
  existing range callback; wiring it produces the missing source, destination,
  payload, and ordering witness.
- H-preclear-snapshot-artifact: the earlier nonzero snapshot is not a live
  target-span write; the complete phase-gated census shows no nonzero pre-clear
  write from either source, despite positive controls.

Exact work: wire `rs64_m5_source_range_dma_write` into the active
`dma_dmem_to_rdram` path, then add the regeneration-safe non-scalar guest
write census for `0x1797B0..0x179A48`, joined by ordinal/order to the existing
`0x800078EC` clear marker. Batch source, destination, width, value/FNV,
writer-PC, and ordering fields in one build and one run. Use:

`zsh scratch/agent/run_s4159_m5_preclear_span_census.sh`

Require whole-RDRAM, title, hangar, and both probe-control gates before
interpreting rows. A nonzero DMA row after the callback is qualified selects
H-source-range-hook-gap or H-host-dma-writer; a distinct non-scalar guest row
selects H-other-guest-writer; no nonzero row with all controls selects
H-preclear-snapshot-artifact. Missing positive-control rows require fixing the
census before any conclusion.
