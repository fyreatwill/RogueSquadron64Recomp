# M5 Session 3672 — exposed input DMA ordering

The new phase-gated port witness matched RDRAM-to-DMEM input DMAs overlapping
`0x1797B0..0x179930` and retained the existing DMEM-to-RDRAM writeback rows.
The concurrent 55-second capture passed the oracle whole-RDRAM control, oracle
task activity, port title and hangar VI controls, the RSP-source hook control,
and 1,800 port audio task rows. It produced 1,024 input-span rows: 512 in
title (`0x00790400`) and 512 in hangar (`0x006AB400`), plus 512 writeback
rows. There were no crash or abort markers.

Title input DMAs carried nonzero source payloads (`source_nz=112` and `216`
for the two chunks), and their post-DMEM hashes/nonzero counts matched the
source-RDRAM values. Hangar input DMAs carried zero payloads, with matching
zero post-DMEM values. The observed input direction therefore exists and is
not globally zero-valued; the hangar arm's zero input remains a live clue.

This selects `H-InputDmaObserved` for the port and refutes
`H-OnlyWritebackObserved`. `H-InputDmaZeroPayload` is phase-specific only,
not a global explanation. The direction/value rows are single-source port
evidence; the oracle independently validates the drive, VI, and task controls
but does not observe the port's DMA implementation.

Evidence: `scratch/agent/s3671_m5_dma_order/summary.log`,
`port.log`, and `oracle.log`.

ORIGIN: diagnostic-only input-DMA overlap/hash witness; no guest state,
RDRAM, DMEM, task, selector, or audio output was rewritten or skipped.
