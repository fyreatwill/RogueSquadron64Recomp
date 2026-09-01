# M5 Session 3493 — real-audio selector qualification

The independent retail preflight ran first with the whole-RDRAM positive
control and the phase-qualified `0x80033FCC` audio-task watch. The control
reached 10,000 writes; the execution watch recorded 6,358 hits, and its task
dump recorded 1,257 phase-qualified type-2 rows, including title origins.

The port used the prescribed LLE/spin-yield/ungated route with
`ROGUESQ_AUDIO_UCODE=1` and `ROGUESQ_LOG_AUDIO_RETURN=1`. Its dispatch control
fired 48 times and reported `real_ucode=1`, so the real-audio arm was selected.
It did not reach a title origin: selector-load and selector-writer controls and
rows were all zero, as was the audio-return marker. The run crashed in
`fillSampleStreamRange` at guest PC `0x8000B650`.

This selects `H-RealAudioRouteFails` and refutes neither selector hypothesis,
because the selector phase was never reached. It rules out a dispatch-setting
failure for this run: the independent task control and the port dispatch
control both fired, with opposite route outcomes. The next work unit must
qualify the real-audio route at `fillSampleStreamRange` before attempting the
selector join.

ORIGIN: diagnostic-only oracle, dispatch, phase, selector, and crash
observations; no audio state, selector value, task field, or route behavior was
rewritten, skipped, or validated.
