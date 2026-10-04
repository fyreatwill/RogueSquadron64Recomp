# Next work unit: localize the native-backend startup defect

HYPOTHESIS-ID: m5-native-backend-origin

Session 4067 selected Hnative-backend: native SDL crashed in
`spTaskSchedulerThread+9632` with `ROGUESQ_AUDIO_UCODE=0`, before title or
hangar, while the dummy real arm reached both phases. The next unit must keep
the retail whole-RDRAM positive control and run native-SDL silent and
`SDL_AUDIODRIVER=dummy` silent arms in one same-build capture. Do not compare
sink output unless both arms reach the phase gates.

Competing hypotheses:

- Hdevice-init: native SDL device initialization perturbs startup; native
  silent crashes pre-target while dummy silent reaches title 1024 and hangar
  512 with the normal scheduler markers.
- Hshared-scheduler: the crash is independent of audio backend; both silent
  arms fail at the same scheduler/guest boundary before target phases.
- Hroute-topology: backend selection changes timing but neither arm is
  deterministically phase-qualified; the run must be repeated with a new
  scheduler breadcrumb rather than interpreted as sink evidence.

Discriminating measurement: build once, launch the retail oracle, then launch
both port arms from `build/` with `ROGUESQ_AUDIO_UCODE=0`,
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, the
existing phase gates, and scheduler/task-route breadcrumbs. Use SIGKILL for
both port processes and retain separate logs. Native-only pre-target failure
with dummy reaching both phases selects Hdevice-init; matching pre-target
`spTaskSchedulerThread` failure selects Hshared-scheduler; mixed or unstable
termination is Hroute-topology and is unevaluable. The retail positive-control
threshold must fire in the same run.

Exact command sequence:

1. Add the two-arm recipe as
   `scratch/agent/run_s4068_m5_native_dummy_silent.sh`, based on
   `scratch/agent/run_s4066_m5_native_isolated.sh`; set
   `ROGUESQ_AUDIO_UCODE=0` explicitly for both arms and set
   `SDL_AUDIODRIVER=dummy` only for the dummy arm.
2. Run `zsh scratch/agent/run_s4068_m5_native_dummy_silent.sh` from the repo
   root after confirming the Debug binary and ROM exist.
3. Summarize phase markers, crash PC/guest PC, scheduler breadcrumbs, and the
   retail positive-control marker; do not infer native sink behavior from a
   pre-target arm.
