# M5 Session 3673 — joined source-span input DMA to the live audio task

The single-arm build added the active `s_pending_audio_task` data pointer and
size to each bounded `m5-source-range-reader` row. The existing concurrent
55-second oracle/port recipe was then run with real audio, LLE, spin-yield,
and autopilot enabled.

All controls passed: the oracle whole-RDRAM watch recorded 98,644 writes and
both title/hangar phase histograms; the port reached title and hangar, emitted
the RSP-source hook control, 1,822 type-2 ABI/DMA rows, and 1,024 source-span
reader rows. No crash or abort marker was present.

The 512 title reader rows all carried task data pointer `0x80171CE0`.
Their two repeating chunks had `source_nz=112` and `source_nz=216`, with
source and post-DMEM hashes/nonzero counts equal. The 512 hangar reader rows
all carried `0x80171E70`; every row had zero source and post-DMEM payload.
The reader's live task pointer agrees with the task ABI rows in the same
phase-gated run.

This selects `H-SameTaskInput` for the observed source-span input and
`H-HangarZeroProducer` for the hangar zero: the zero is already present at the
RDRAM source before staging. It refutes `H-InterleavedTaskInput` and
`H-HangarZeroTransform` for these rows. This is two-line port evidence from
the live task pointer and ABI/task-object rows; the oracle is an independent
drive/phase control, not an observer of port DMA internals.

The result does not resolve ownership of the interleaved `0x80173B20` /
`0x80173CB0` objects used by other image stages, nor the producer of the
hangar-zero source bytes. No mitigation or game-state change was made.

Evidence: `src/main/main.cpp`,
`scratch/agent/s3671_m5_dma_order/summary.log`, and
`scratch/agent/s3671_m5_dma_order/port.log`.
