# M5 Session 3492 — silent audio dispatch gate

The independent retail preflight was run before using the port witness. Its
whole-RDRAM control recorded 10,000 writes, and the phase-qualified
`0x80033FCC` task handoff recorded 666 type-2 tasks. The retail task pointer
was `0x80149470`, with `data_ptr=0x80171CE0` and `data_size` 1–2.

The prescribed port silent arm (`ROGUESQ_AUDIO_UCODE=0`, LLE-only,
spin-yield, ungated) was run for the existing 30-second watchdog with
`ROGUESQ_LOG_AUDIO_RETURN=1`. The dispatch witness printed 47 samples:
`n=0..39`, then `128,256,384,512,640,768,896`, and every sample reported
`real_ucode=0`. Thus the selected callback was `musyx_stub`, not the real
Factor 5 audio ucode. No `audio-return` row or `fillSampleStreamRange` crash
appeared. The run reached VI 640 origin `0x0066A500`, then reported
`[audio-wait-pump-stall] countdown=16 after 64 musyxSynthFrame pumps`; it did
not reach a title origin or any selector control.

The positive controls are independent: retail whole-RDRAM/task controls fired,
and the port dispatch marker fired with the selected arm value. This selects
`H-SilentGateHonored` at the dispatch boundary and refutes
`H-SilentGateBypassed` for the observed tasks. It does not establish that the
silent route is healthy: the separate wait-pump stall remains the reason the
silent arm cannot qualify the selector boundary. `H-NonAudioSchedulerFault`
is not selected because the observed callback was the intended stub and no
non-audio scheduler crash followed it.

No code or runtime behavior changed. The next capture should use the already
qualified real-audio arm to reach title and exercise the selector witness.
