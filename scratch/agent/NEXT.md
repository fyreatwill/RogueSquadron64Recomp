# Next work unit: native SDL silent-control route qualification

HYPOTHESIS-ID: m5-sdl-backend-boundary

The 4066 native declared-real arm crashed in `spTaskSchedulerThread` before
title/hangar both in concurrent A/B and native-only isolation. The dummy
declared-real arm reached both phases and drained positively, but that does
not qualify native output. M3 remains externally blocked on the missing MIPS
toolchain.

Competing hypotheses:

- Hnative-backend: native SDL device startup itself causes the pre-target
  scheduler failure; the native silent arm will also fail before both phases.
- Hreal-route: the native failure depends on the Factor 5 image/real-audio
  route; native silent will reach title 1024 and hangar 512 with the normal
  host-device rows.
- Hroute-schedule: the native arm remains pre-target despite silent mode, so
  no sink conclusion is possible and the route dependency needs a new angle.

Discriminating measurement: run one same-build native-SDL `ROGUESQ_AUDIO_UCODE=0`
silent arm using `scratch/agent/run_s4066_m5_native_isolated.sh` after the
retail oracle positive-control marker fires. Keep the whole-RDRAM control,
`PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, host queue/drain logs,
and SIGKILL cleanup. Native silent reaching both target phases selects
Hreal-route; native silent repeating the pre-target crash selects
Hnative-backend; any other pre-target termination is Hroute-schedule and is
unevaluable. Do not infer sink behavior from a missing phase.
