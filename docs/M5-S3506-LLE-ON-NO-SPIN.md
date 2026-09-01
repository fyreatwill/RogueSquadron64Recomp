# M5 Session 3506 — LLE-on/no-spin route discriminator

The bounded run used `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_SPIN_YIELD=0`, the validated autopilot, and the existing batched
controls. Startup, phase, dispatch, frame-sync, DP, host-boundary, and writer
controls all fired. Real audio dispatched through at least 1,664 tasks.

The run reached VI 640 at origin `0x0066A500` and remained there through the
30-second SIGKILL. It did not reach title 1024 or hangar 512, produced no
target-phase selector rows, and emitted no crash or abort marker.

This selects the broader no-spin advance blocker and rules out a spin-yield
dependency within the forced-LLE arm. The result is diagnostic-only: no audio,
selector, task, or output state was rewritten, skipped, or validated.
