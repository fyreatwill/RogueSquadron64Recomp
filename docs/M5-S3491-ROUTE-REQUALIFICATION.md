# M5 Session 3491 — selector-load route requalification

The prescribed `ROGUESQ_AUDIO_UCODE=0`, LLE-only, ungated, spin-yield
capture was retried with the new selector-load witness. The 30-second arm
crashed before title at guest PC `0x8000834C`; the host stack identified
`spTaskSchedulerThread+9556`, and the selector-load/writer controls and rows
were all zero.

The corrective 60-second retry used the same route and capture fields. It
also crashed before title, this time with `fillSampleStreamRange+932` below
`musyxRenderVoiceSamples` and `musyxSynthFrame`. It produced no title phase,
selector controls, or selector rows. Thus the title discriminator remains
unevaluable, not null. The failure is reproducible in the prescribed route
and is not explained by the shorter watchdog.

This selects the route-specific audio/scheduler blocker as the immediate
qualification problem, while leaving selector-load and writer-input
hypotheses open. It does not prove that the audio environment variable was
honored for every task; that is the next check.

ORIGIN: diagnostic-only route and crash observations; no audio state,
selector value, or task field was rewritten, skipped, or validated.

Evidence: `scratch/agent/s3490_m5_upstream_selector/` and
`scratch/agent/s3490_m5_fixed_retry/`.
