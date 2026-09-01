# NEXT work unit — qualify the real-audio route at fillSampleStreamRange

HYPOTHESIS-ID: m5-real-audio-route-qualification

Session 3493 selected `H-RealAudioRouteFails`: dispatch selected
`real_ucode=1`, but the port crashed before title at guest PC `0x8000B650`
inside `fillSampleStreamRange`. The independent retail control was positive,
so the zero selector rows are unevaluable.

Competing hypotheses and discriminating outcomes:

- `H-RealAudioRouteTransient`: a bounded retry with the same qualified route
  reaches title and fires the selector controls.
- `H-RealAudioRouteStableCrash`: the same route reproducibly fails at or below
  `0x8000B650` before title, despite positive dispatch and phase controls.
- `H-RouteFailureElsewhere`: the retry reaches title or fails at a different
  audio/scheduler boundary, moving the next probe to that site.

Discriminating measurement: one same-build real-audio route capture with the
existing whole-RDRAM/dispatch/phase controls and `ROGUESQ_LOG_AUDIO_RETURN=1`;
the outcome is title reachability plus the first crash guest PC. Do not
interpret selector zeros unless title is reached.

Exact command: use `env ROGUESQ_LOG_AUDIO_RETURN=1 zsh
scratch/agent/run_s3493_m5_real_selector.sh`. Keep SIGKILL watchdog behavior
and capture under `scratch/agent/s3493_m5_real_selector/`. If title is reached,
then the following iteration may run the selector join; otherwise record the
route failure and choose the newly identified boundary.
