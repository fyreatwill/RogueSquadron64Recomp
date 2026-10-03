# Next work unit: M5 image-task source/output boundary

HYPOTHESIS-ID: m5-image-stage-source-output

Use the existing s3762 capture and current source joins to identify the first
legitimate producer boundary for the zero-valued image-stage/PCM payload. Do
not add another task-data value field, change an audio gate, or implement a
writeback/fill mitigation.

Competing hypotheses:

- `H-M5-InputProducerGap`: the image task receives a zero-valued input because
  the producer before image-stage input is absent or clears it.
- `H-M5-OutputConsumerGap`: image-stage input/output is already the selected
  boundary, and the first missing contract is after image-stage output or at
  its consumer.
- `H-M5-Accounting`: the apparent boundary is a join/window artifact; the
  existing source/output ordinals or phase controls do not align.

Discriminator: build no new instrument initially. Extract the same phase-5
image-stage rows, input-DMA rows, PCM source/consumer rows, and task join rows
for the final shared ordinal from
`scratch/agent/s3762_m5_step1_silent_repeat/image.log`; classify whether the
first zero payload is before or after the image-stage output, and verify the
same ordinal/phase keys. `H-M5-InputProducerGap` requires a named producer
before the input DMA; `H-M5-OutputConsumerGap` requires a named post-stage
consumer; `H-M5-Accounting` is selected by missing controls or mismatched
keys. Require oracle whole-RDRAM positive control and title/hangar phases.

Exact commands:

`grep -a -E '^(\[audtask-image-stage|\[audtask-image-dma-join|\[m5-input-dma|\[audtask-join|\[audio-join-pcm|\[pcm-boundary)' scratch/agent/s3762_m5_step1_silent_repeat/image.log | grep 'phase=5 width=512' | tail -80`

`grep -a -E '^(oracle_gate|silent_hangar|image_hangar)' scratch/agent/s3762_m5_step1_silent_repeat/driver.log`
