# Next work unit: M5 post-clear producer and retail timing

HYPOTHESIS-ID: m5-post-clear-producer-order

Use the s3766 caller join as the fixed boundary: `0x8008F2CC` allocates and
clears `0x801797B0..0x80179A48`, then the port reaches the zero-valued
`0x800078EC` source-span writes and input DMA `0x1798B0 -> DMEM 0xCB0`.
Identify the first post-clear producer/handoff that should populate the buffer,
and compare its phase/ordering with the independent retail producer rows. Do
not suppress or replace the clear.

Competing hypotheses:

- `H-M5-PostClearProducerAbsent`: the qualified port never executes a
  legitimate nonzero producer after the expected initialization.
- `H-M5-PostClearProducerClears`: a legitimate producer runs, then a later
  clear/overwrite returns the source to zero before input DMA.
- `H-M5-PostClearJoinMismatch`: the retail and port producer windows do not
  describe the same buffer/task, or their route/phase join is invalid.

Discriminator: one phase-scoped table containing allocation/clear, every
already-censused source-span writer, first nonzero transition, source DMA, and
the retail oracle's corresponding writer/order rows. `Absent` requires the
positive controls and no nonzero post-clear producer; `Clears` requires a
nonzero post-clear producer followed by a later zero writer before DMA;
`JoinMismatch` requires a failed buffer/task/phase join. Require the oracle
whole-RDRAM positive control and both title/hangar phases.

Exact commands:

`grep -a -E '^\[(m5-static-rsmemset|field348-writer|m5-input-dma|audtask-image-stage|audtask-image-dma-join|audtask-join)' scratch/agent/s3416_m5_entry_input/image.log | grep 'phase=5 width=512' | tail -240`

`grep -a -E '^(oracle_gate|silent_hangar|image_hangar)' scratch/agent/s3762_m5_step1_silent_repeat/driver.log`
