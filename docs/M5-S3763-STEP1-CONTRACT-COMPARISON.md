# M5 s3763 — Step 1 contract comparison

Session 3762 is a valid same-build comparison: the retail oracle whole-RDRAM
watch fired (`10000`), and the image and silent port arms both reached title
VI 1024 and hangar VI 512. The capture is therefore interpretable at both
target phases.

## Measured comparison

| Row | Silent (`musyx_stub`) | Image (`factor5_ucode_b`) | Interpretation |
|---|---:|---:|---|
| Task dispatch | 50 | 50 | Shared route control |
| ABI / DMA rows | 659 / 659 | 665 / 665 | Same task family; image has six additional task rows |
| Image-stage rows | 0 | 2,693 | Expected arm-specific difference |
| Audio return | 278 | 283 | Same return path; small task-count difference |
| Audio route / SP route | 870 / 870 | 885 / 885 | Shared completion/queue path with image's extra tasks |
| PCM source / consumer | 70 / 285 | 70 / 285 | Shared PCM boundary activity and counts |
| Slot allocation/status probes | 0 / 0 | 0 / 0 | No slot contract edge selected |
| Voice audit | 0 | 0 | No voice contract edge selected |
| Target phases | title + hangar | title + hangar | Both arms are phase-qualified |

The phase-5 terminal rows show the same SP enqueue, external delivery, guest
receive, and route return sequence. The image arm's task joins are real image
work with DMA rows; the silent arm's corresponding terminal task has
`dma_count=0` and completes through the intentional stub. That difference is
the selected-arm behavior, not evidence of a missing downstream edge.

## Result

`H-M5-ImageStageOnly` is selected for the measured Step 1 row. The capture
does not select a slot, voice, PCM, or route de-stubbing change: the shared
PCM rows are zero-valued in both arms, and the image-stage payloads are also
zero-valued. This is a contract boundary still needing explanation, not a
permission to add a writeback or fill mitigation.

The next discriminator must therefore separate an image-task input/source
producer gap from an image-stage output/consumer gap. It must use the existing
oracle positive control and both target phases, and must name the writer before
any behavior change.

