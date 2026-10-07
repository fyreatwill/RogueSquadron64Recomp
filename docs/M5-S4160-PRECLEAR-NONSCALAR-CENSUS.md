# M5 s4160 pre-clear non-scalar census

The independent retail oracle passed the whole-RDRAM control (11,166 writes),
the target-span control (1,166 writes), and both title VI 1024 and hangar VI
512 phase gates. Its target-span writer families included `0x80007670`,
`0x800078EC`, `0x8001E2C0`, and `0x8001FAxx`; the hangar final snapshot was
zero, so ordering remains necessary.

The rebuilt port passed the phase and existing census controls. The widened
host/RSP census reported 516 rows, all for the existing
`0x178C80..0x178F18` image-input field; it reported no row intersecting the
`0x1797B0..0x179A48` pre-clear target. The RT64 writeback witness produced no
target-span row. The existing pre-clear snapshot still showed 607 nonzero
bytes at hangar entry and zero after the `0x800078EC` clear.

Selection: H-host-dma-writer is not observed in the instrumented host/RSP and
RT64-writeback paths on this qualified run. H-other-guest-writer and
H-preclear-snapshot-artifact remain unevaluable because the regeneration-safe
non-scalar guest census is incomplete and the existing
`rs64_m5_source_range_dma_write` hook is not wired into the active DMA path.

ORIGIN: independent retail write watch, host/RSP census, RT64 writeback
callback, and existing guest clear snapshot. No guest, audio, wait, cap,
predicate, slot, or writeback behavior changed; the new callback only observes
after the copy.

Evidence: `scratch/agent/s4159_m5_preclear_span_census/`.
