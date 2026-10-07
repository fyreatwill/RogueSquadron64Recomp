# Next work unit: attribute the non-scalar pre-clear writer

HYPOTHESIS-ID: m5-pre-clear-nonscalar-writer

Session 4159 closed the generated guest scalar-store class: the target-valid
port captured all 664 intersecting scalar stores, all zero-valued bytes from
`0x800078EC`. Retail independently recorded nonzero earlier span bytes. The
next unit must identify the remaining port writer without changing behavior.

Competing hypotheses and discriminator:

- H-host-dma-writer: a host/RSP DMA write populates the span before the guest
  clear; the census will show a nonzero host/DMA writeback with a source,
  destination, and ordering witness before `0x800078EC`.
- H-other-guest-writer: a non-scalar guest operation (memset/copy/unaligned or
  an uninstrumented store class) writes it; the census will show a nonzero
  guest write with a distinct writer PC before the clear.
- H-preclear-snapshot-artifact: the earlier nonzero snapshot is not a live
  target-span write on this qualified route; the complete phase-gated write
  census will show no nonzero pre-clear write from either source, despite the
  positive controls.

Exact work: add one regeneration-safe, phase-scoped RDRAM-write census that
  covers host/RSP writeback and every non-scalar guest write intersecting
  `0x1797B0..0x179A48`, joined by ordinal/order to the existing
  `0x800078EC` clear marker. Batch all source, destination, width, value/FNV,
  writer-PC, and ordering fields in one build and one run. Run the independent
  retail controls and the qualified port recipe together using:

`zsh scratch/agent/run_s4159_m5_preclear_span_census.sh`

Require whole-RDRAM, title, hangar, and both probe-control gates before
interpreting rows. Do not change guest, audio, wait, cap, predicate, slot, or
writeback behavior. A host/DMA row before the clear selects H-host-dma-writer;
a distinct non-scalar guest row selects H-other-guest-writer; no nonzero row
with all controls selects H-preclear-snapshot-artifact or an instrument gap,
and requires fixing the census before any conclusion.
