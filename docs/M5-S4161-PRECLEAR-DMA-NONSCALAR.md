# M5 session 4161 — pre-clear DMA/non-scalar boundary

The rebuilt port reached title VI 1024 and hangar VI 512 with the
whole-RDRAM/host-write positive controls. The runner used the previously
qualified autopilot schedule and enabled the phase-scoped span census.

The generated scalar census emitted 664 target-span rows in hangar. Every row
was a zero-valued byte store from guest PC `0x800078EC`, covering
`0x1797B0..0x179A48`. The active `dma_dmem_to_rdram` path also reached the
host-write control, but `rs64_m5_source_range_dma_write` emitted zero
target-span rows. No RT64/source-range DMA writer was observed.

This is a qualified negative for the instrumented host/RSP DMA class, not a
negative for all non-scalar guest writers: the generated non-scalar guest
census did not yet have a positive-control row. H-other-guest-writer versus
H-preclear-snapshot-artifact therefore remains unevaluable. ORIGIN: the
legitimate host/RSP DMA callback and guest scalar-store rows; no game value or
write path was suppressed or changed.
