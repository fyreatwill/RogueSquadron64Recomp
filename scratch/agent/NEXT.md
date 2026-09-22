# Next work unit: M5 image-task/output payload boundary

HYPOTHESIS-ID: m5-image-output-payload-boundary

The s3727 same-build retry was control-valid: both arms reached VI 1024 and
VI 512, RSP/task controls fired, and the callback table selected a distinct
real-arm image owner/thread. The remaining boundary is the zero image-task
payload. Build one diagnostic-only table joining source DMA, DMEM window,
output-DMA payload, image-stage, PCM source/consumer, and task completion by
route ordinal. Do not change selector, clear, task, audio-route, or payload
behavior.

Competing hypotheses:

- `H-ImageProducerZero`: the image task receives legitimate zero source/DMEM
  data before output.
- `H-ImageWritebackGap`: the task produces nonzero data but output writeback is
  absent or ordered incorrectly.
- `H-ConsumerPayloadGap`: output writeback is nonzero but the downstream PCM
  consumer sees a different or zero span.

Discriminator: source/DMEM/output/consumer hashes and nonzero counts in one
same-build, phase-gated table. Matching nonzero DMEM with zero output selects
`H-ImageWritebackGap`; nonzero output with zero or mismatched consumer payload
selects `H-ConsumerPayloadGap`; zero source and DMEM before the image task
selects `H-ImageProducerZero`. The positive controls are both VI transitions,
RSP-source/task controls, and real image-stage rows; a missing control is
unevaluable, not a null.

Build/run: add all fields through the regeneration-safe fixup path in one
build, run real and silent arms concurrently with the validated route, phase
gate on VI 512, retain passive breadcrumbs, SIGKILL both processes, and write
a new `docs/M5-S3728-*.md` evidence note.
