# M5 Session 3504 — real audio with forced LLE disabled

The existing selector witness build was run from `build/` with the same real
audio, spin-yield, missing-function, phase, route, and autopilot settings as
the failed Sessions 3502–3503 arm, except `ROGUESQ_LLE_FORCE=0`. The run was
bounded to 30 seconds and the process was terminated with SIGKILL.

The startup control fired and the run reached VI width 640 at origin
`0x00696100`. Real audio dispatch remained active through at least 1,664
tasks (`[audtask-dispatch] n=1664 real_ucode=1`), and the prior
`spTaskSchedulerThread+9556`, guest PC `0x8000834C` crash did not occur. The
run emitted no 1024 title transition, no 512 hangar transition, no
`[audio-return]` rows, and no selector rows before termination.

This selects a new pre-title route/advance failure for the LLE-off arm and
refutes the narrower claim that real audio necessarily reproduces the
`0x8000834C` crash. It does not qualify the selector comparison or identify a
selector/table writer. The real-audio behavior is single-source in this
iteration; the prior route crash is independently documented in Sessions
3502–3503.

ORIGIN: diagnostic-only route, phase, audio-dispatch, and selector
observations; no audio state, selector value, task field, or output was
rewritten, skipped, or validated.

Capture: `scratch/agent/s3504_m5_lle_off_real_audio/run.log`.
