# Session 2968 M5 Step 1 audit

The Debug target rebuilt successfully. The retail oracle passed its
whole-RDRAM positive control (`10000` callbacks), then reached title
`1024 @ 0x00790400` and hangar `512 @ 0x006AB400`.

The same-build port pair used the existing AUTOPILOT and phase-gated probe.
Both silent (`ROGUESQ_AUDIO_UCODE=0`) and Factor 5 image (`=1`) arms
dispatched 66 audio tasks, remained at VI 640, and reached neither title nor
hangar. Both had zero task-contract/image-stage, audio-return, service/slot,
or PCM-boundary rows and zero crash/abort markers.

The downstream A/B discriminator is unevaluable in this recipe. The matching
pre-title stall rules out an audio-arm-specific route difference, but does not
distinguish audio degeneracy from an image contract gap. No audio behavior was
changed.
