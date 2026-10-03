# M5 s3761 — Step 1 silent-control qualification

Date: 2026-10-02

## Work unit

Ran the same-build concurrent image/silent Step 1 contract recipe with the
retail oracle positive control, phase-gated at VI widths 1024 and 512. The
competing explanations were a repeatable silent-route pre-target crash,
concurrent-pair perturbation, or run instability.

## Result

The retail oracle passed its whole-RDRAM positive control (`10000` callbacks)
and reached both title (`0x00790400`, width 1024) and hangar (`0x006AB400`,
width 512). The image arm reached title and hangar and emitted the expected
Step 1 rows: 6,560 audio-task ABI/DMA rows, 26,248 image-stage rows, 561
audio-return rows, 2,571 audio-route rows, and PCM source/consumer rows.

The silent arm emitted no title or hangar target rows and crashed before title
at `spTaskSchedulerThread+9556`, with `si_addr=0x400128d47` and last guest PC
`0x8000834c`. The driver classified the pair as failed because
`silent_hangar=0`, `image_hangar=1`; cleanup used SIGKILL.

## Interpretation

For this qualified capture, the silent pre-target crash is selected and
concurrent pair perturbation is not supported: the image arm reached hangar in
the same run and the oracle controls were valid. This does not prove a
production-wide repeatability rate, and it does not make downstream silent
audio-contract nulls interpretable. Keep Step 1 open and use a new silent-route
stability discriminator before changing an audio gate or task-data
instrumentation.

Evidence: `scratch/agent/s3761_m5_step1_silent_qualification/driver.log`,
`oracle.log`, `image.log`, and `silent.log`.
