# Next work unit: M5 pre-input producer boundary

HYPOTHESIS-ID: m5-pre-input-producer-boundary

Use the existing source-DMA/task-data joins and the retail oracle to identify
the first legitimate producer or clear before image input DMA
`0x1798B0 -> DMEM 0xCB0`. Do not add another task-data value field, change an
audio gate, or implement a writeback/fill mitigation.

Competing hypotheses:

- `H-M5-ProducerBeforeInput`: evidence names a legitimate nonzero producer
  before input, followed by a clear or route mismatch.
- `H-M5-ProducerAbsent`: positive controls pass but no legitimate producer
  writes the source span before input.
- `H-M5-JoinMismatch`: the source-DMA join is not the task-data object used by
  the image task, or phase/ordinal alignment is false.

Discriminator: first extract existing source-DMA, task-data writer, and oracle
rows for the same phase-5 route ordinals. If they are insufficient, build one
instrument containing all three arms and all producer classes in one run.
`H-M5-ProducerBeforeInput` requires a named legitimate writer and a later
clear/mismatch; `H-M5-ProducerAbsent` requires positive controls plus no writer
before input; `H-M5-JoinMismatch` requires a failed source/task join or missing
phase control. Require oracle whole-RDRAM positive control and title/hangar
phases.

Exact commands:

`grep -a -E '^(\[m5-input-dma|\[audtask-image-stage|\[audtask-image-dma-join|\[audtask-join)' scratch/agent/s3762_m5_step1_silent_repeat/image.log | grep 'phase=5 width=512' | tail -100`

`grep -a -E '^(oracle_gate|silent_hangar|image_hangar)' scratch/agent/s3762_m5_step1_silent_repeat/driver.log`
