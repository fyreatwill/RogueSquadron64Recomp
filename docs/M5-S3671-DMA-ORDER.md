# M5 Session 3671 — source-span DMA ordering capture

The single 55-second capture ran the independent retail oracle and the
real-audio port concurrently. The oracle positive control recorded 98,456
whole-RDRAM writes and 930 type-2 task rows. The port reached title VI
`0x00790400` (1024) and hangar VI `0x006AB400` (512), with 1,775 audio-task
ABI rows, 7,221 DMA rows, and no crash or abort markers.

In the port's target phase, the task stream was dominated by data pointer
`0x80171E70`; the preceding phase also contained `0x80171CE0`. The
source-span rows for `0x1797B0..0x179930` were `dmem_to_rdram` writebacks,
not RDRAM-to-DMEM reads. Their payload nonzero count was zero, including the
`0x1798B0..0x179930` rows and the `0x1797B0` rows. The same zero payload hashes
recurred across changing route ordinals.

This rejects `H-DmaConsumesInitializedRecord` as an interpretation of these
observed rows and supports `H-ZeroPayloadWriteback` for the port's target
writeback path. It does not establish the ordering of the input/source DMA
that feeds DMEM, nor an exact writeback-to-task ownership edge; the current
instrument reports the opposite DMA direction for the watched span. The
object interleave remains visible in task rows but is not joined to a source
read event. This is single-source port evidence for the DMA direction and
payload; the oracle line independently validates that the retail capture was
driven and reached task activity.

ORIGIN: diagnostic-only oracle and port tracing; no guest or host state was
rewritten, skipped, or guarded.

Evidence: `scratch/agent/s3671_m5_dma_order/oracle.log`,
`scratch/agent/s3671_m5_dma_order/port.log`,
`scratch/agent/s3671_m5_dma_order/summary.log`, and
`scratch/agent/run_s3671_m5_dma_order.sh`.
