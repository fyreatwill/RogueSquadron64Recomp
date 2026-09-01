# M5 Session 3518 — same-build audio route pair

The existing Debug tree was rebuilt before the pair. The independent retail
oracle ran first and passed its whole-RDRAM positive control (10,000 callbacks),
then reached title VI 1024 and hangar VI 512. Both port arms were launched
concurrently with the validated LLE/spin-yield/autopilot route and phase gates.

The silent arm (`ROGUESQ_AUDIO_UCODE=0`) crashed before title. Its crash
reported `last-guest-pc=0x8000B650`, the `fillSampleStreamRange` family, with no
title or hangar phase. The real image arm (`ROGUESQ_AUDIO_UCODE=1`) reached
title VI 1024 and hangar VI 512, emitted 87 audio-task dispatch rows and 533
audio-return rows, and ran without a crash before the bounded stop.

This selects a route-specific silent-arm failure and reopens the selector
producer/context investigation on the real image route. It does not prove
that the image arm's audio contract is correct, nor identify the writer of the
silent-arm crash input.

ORIGIN: diagnostic-only same-build audio-arm toggle and phase/crash logging;
no audio, selector, task, or output state was rewritten or skipped.

Evidence: `scratch/agent/s3518_m5_audio_route_pair/driver.log`,
`silent.log`, `image.log`, and `oracle.log`.
