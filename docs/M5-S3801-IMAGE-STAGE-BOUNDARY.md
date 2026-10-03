# M5 s3801 — image-stage source versus consumer boundary

The independent retail preflight had a live whole-RDRAM positive control and
reached title VI `0x00790400`/1024 and hangar VI `0x006AB400`/512. Its added
candidate stage watches produced no attributable target hit in this capture,
so that result is not used as a retail null. Existing qualified retail ground
truth remains the source span `0x1797B0..0x179A48`, written in hangar by
`0x800078EC`.

The same Debug build launched image and silent arms concurrently. Both arms
reached title and hangar, and both passed phase, PCM source/consumer, audio
return, and no-crash/no-abort controls. The image arm produced 2,240
`audtask-image-stage` rows, 1,118 image-stage queue rows, 618 source-DMA
reader rows, and 16 stage-byte rows. Its hangar joins repeatedly showed:

- source DMA `0x1798B0 -> DMEM 0xCB0`, `FNV=762B22A5`, `nz=0`;
- stage-3 DMEM/DMA/destination payload with the same zero hash and `nz=0`;
- a live destination and consumer callback after the zero payload arrived.

The silent arm produced zero image-stage, source-DMA-reader, stage-byte, and
image-queue rows, while still producing 80 PCM-source, 295 PCM-consumer, and
287 audio-return rows. Therefore the image/silent difference is real and the
image consumer path is live, but its input is zero before output publication.
At this discriminator `H-M5-ProducerAbsent` / source-input gap is selected;
output-only and instrumentation-scope explanations are refuted. This does
not identify the legitimate writer of the zero-valued source span.

ORIGIN: diagnostic-only source/stage/consumer logging; no game state, task,
audio, scheduler, or rendering behavior changed.

Artifacts: `scratch/agent/s3801_m5_image_stage_boundary/`, recipe
`scratch/agent/run_m5_image_stage_boundary.sh`.
