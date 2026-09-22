# Next work unit: M5 image-task/output payload boundary

HYPOTHESIS-ID: m5-image-payload-boundary

Run one phase-gated real-audio/silent paired capture using the existing
validated route. Join, by route ordinal, the source DMA, DMEM source window,
output DMA, image-stage callback, PCM source/consumer rows, and task
completion. Preserve all RSP/phase controls and do not change task, selector,
clear, audio-route, or payload behavior.

Competing hypotheses:

- `H-ImageProducerZero`: source and DMEM payload are legitimately zero before
  output.
- `H-ImageWritebackGap`: source/DMEM is nonzero but output writeback is zero or
  missing/ordered incorrectly.
- `H-ConsumerPayloadGap`: output is nonzero but the downstream image/PCM
  consumer sees a different or zero span.

Discriminator: a same-build handoff table. Zero source/DMEM selects
`H-ImageProducerZero`; nonzero DMEM with zero output selects
`H-ImageWritebackGap`; nonzero output with zero consumer payload selects
`H-ConsumerPayloadGap`. The real arm must reach VI 1024 and 512 and fire the
RSP positive control; the silent arm must reach the same phases and fire its
control, otherwise the comparison is unevaluable.

Exact command basis: adapt the existing phase-gated M5 image/payload capture
script and run both arms concurrently from `build/`, with SIGKILL cleanup.
Save output under `scratch/agent/s3732_m5_image_payload/` and write
`docs/M5-S3732-*.md`.
