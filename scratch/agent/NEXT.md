# NEXT work unit — re-qualify the real-audio selector route

HYPOTHESIS-ID: m5-real-audio-route-qualification

Session 3495's fresh retail arm qualified its controls and observed 78 title
rows at each selector PC, but both fresh port attempts failed before title;
the fixed direct-PID retry crashed at guest PC `0x8000834C`. Do not use the
prior s3494 port log as an animated A/B arm.

Competing hypotheses and discriminating outcomes:

- `H-TransientAudioScheduler`: the real-audio/LLE route is flaky and a fresh
  direct-PID run reaches title and fires both selector controls.
- `H-StableAudioSchedulerCrash`: the same route consistently dies at
  `0x8000834C` before title and selector controls.
- `H-SelectorRouteOther`: the route reaches title but selector controls are
  absent, separating selector wiring from the scheduler/audio failure.

Discriminating measurement: one direct-PID port run with the existing
real-audio/LLE/spin-yield environment, title VI gating, selector controls,
and audio-return/dispatch breadcrumbs. Title plus both controls selects the
qualified arm and permits the selector comparison next iteration; another
`0x8000834C` pre-title crash selects stable route failure; title without
controls selects a selector-route defect. No selector values are interpreted
unless the positive controls fire.

Exact starting point: use the direct-PID watchdog form from Session 3495,
launching from `build/` with `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
`ROGUESQ_LOG_PHASE=1`, `ROGUESQ_LOG_VI_TRANSITION=1`,
`ROGUESQ_LOG_M5_TASK_WRITER=1`, and `ROGUESQ_LOG_AUDIO_RETURN=1`.
Use SIGKILL and a capture path under `scratch/agent/`.
