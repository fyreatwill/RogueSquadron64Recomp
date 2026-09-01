# NEXT work unit — qualify the pre-title audio route blocker

HYPOTHESIS-ID: m5-pretitle-audio-route

Session 3517 qualified the retail producer range and added a port entry witness,
but both port attempts remained at VI 640 and never reached the 512 target
phase. Do not repeat those schedules unchanged.

The single work unit is one bounded audio-route qualification: inspect the
existing audio dispatch/gate and run one fresh silent-control route plus one
fresh real-audio route in the same built tree, both with phase and crash
controls. The discriminator is whether real audio crashes before title in the
known `fillSampleStreamRange` family while silent audio reaches the same phase;
failed phase controls make the arm unevaluable.

Competing hypotheses:

- `H-RealAudioRouteCrash`: real audio crashes before title while silent audio
  reaches title/hangar; the audio route is the blocker.
- `H-SilentRouteIndependentBlocker`: both arms stop before title, selecting a
  shared route blocker rather than audio-specific corruption.
- `H-RealAudioReachesTarget`: real audio reaches the target phase, reopening
  the selector producer/context join.
- `H-CaptureInvalid`: startup, phase, or crash controls fail, so neither arm
  is interpretable.

Run from `build/` with the existing validated autopilot and phase-gated probe;
retain `ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT=1` and the new producer context
log. Build both audio arms before running them. Use SIGKILL and non-dot final
capture paths.
