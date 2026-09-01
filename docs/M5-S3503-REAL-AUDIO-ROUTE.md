# M5 Session 3503 — real-audio route retry remains pre-title blocked

Ran one phase-gated real-audio/LLE/spin-yield/autopilot retry from `build/`
with `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_STUB_MISSING_FUNCS=1`, the existing
phase, audio-return, selector, caller, and producer witnesses, and the
validated Start schedule. The probe reached only VI widths 0 and 320, then
the process emitted a SIGSEGV crash marker at host
`spTaskSchedulerThread+9556`, guest PC `0x8000834C`. The startup control was
therefore live, while the 1024 title control, dispatch/return rows, and all
selector controls/rows were zero.

This is a fresh same-recipe reproduction of the real-audio qualification
blocker from Session 3502. It selects `H-AudioRouteCrash` and rules out a
missing post-title selector observation for this run. Selector-table writer,
index, and value hypotheses remain unevaluable; no audio, selector, task, or
output state was rewritten, skipped, or validated.

ORIGIN: diagnostic-only route, phase, selector, audio-dispatch, and crash
observations; the run added no mitigation or behavior change.

Capture: `build/scratch/agent/s3503_m5_route_retry/run.log`.
