# M5 s3559 — image output join was route-invalid

The planned image-task output join was not interpretable in this iteration.
The independent retail control passed: a whole-RDRAM watch recorded 59,854
writes in 75 seconds, the VI trace reached the hangar origin `0x006AB400`,
and the watched output/source spans recorded 640 and 49,214 writes.

The same-build port pair used the validated LLE-solo, spin-yield, and
AUTOPILOT recipe. The silent `ROGUESQ_AUDIO_UCODE=0` arm reached title
`0x00790400` at width 1024 and captured 65 frames. Its log contained 2,542
audio-task ABI rows, 2,542 stub task rows, 2,461 PCM-source rows, and 2,451
PCM-consumer rows; these are controls for the silent arm, not image output.

The image arm exited before width 1024 in the concurrent pair with
`last-guest-pc=0x8000834C`, and the identical image recipe run alone reached
only width 640 before the 180-second phase wait expired. It emitted no target
phase image-stage, DMA-join, completion-join, downstream, or PCM rows. The
first result is a crash; the single-arm retry is a pre-title route stall, so
the shared-runtime-contention explanation is not selected.

This selects `H-RouteOnly` for the s3559 discriminator. The image destination,
`field348+0x100`, PCM spans, slot/status, voice/reap, and MORT relationships
are unevaluable. No task field, output, gate, slot, PCM, or writeback behavior
was changed.

The next probe must qualify the pre-title image route at the existing
`0x8000834C` boundary with a complete caller/input/phase table, and must not
repeat the target-phase join until the image arm reaches title and hangar.
