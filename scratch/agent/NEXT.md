# Next work unit: complete the inline guest-write census at the pre-clear span

HYPOTHESIS-ID: m5-pre-clear-inline-writer

Session 4162 qualified the `rs_memset`/`zmemcpy` operation-entry class. Its
only target row was the expected zero `rs_memset` fill; no distinct nonzero
writer was observed. The remaining gap is direct or inline guest code that is
not represented by those operation entries, versus a stale/non-live pre-clear
snapshot.

Competing hypotheses and discriminator:

- H-inline-guest-writer: a direct, uninstrumented guest store or inline copy
  reaches `0x1797B0..0x179A48`; a complete phase-gated target-span write table
  shows a distinct guest PC and value/order before `0x800078EC`.
- H-host-dma-writer: a host/RSP path writes the span; the same run shows a
  nonzero target-span DMA/writeback row joined before the clear.
- H-preclear-snapshot-artifact: all guest and host/DMA writer arms are
  positive-controlled but no nonzero target-span write exists before the
  clear; the earlier nonzero snapshot is not a live writer event.

Exact work: add one regeneration-safe whole-target-page guest write witness
for direct/inline stores, retaining the existing scalar, `rs_memset`/`zmemcpy`,
host/DMA, clear-order, and independent retail controls. Run one rebuilt
capture:

`zsh scratch/agent/run_s4159_m5_preclear_span_census.sh`

Require whole-RDRAM/host-write, title, hangar, scalar, and non-scalar controls.
A distinct nonzero guest row selects H-inline-guest-writer; a qualified
nonzero DMA row selects H-host-dma-writer; no nonzero row from either complete
arm selects H-preclear-snapshot-artifact. If the new witness cannot produce a
positive control in both target phases, fix the witness and do not interpret
its null.
