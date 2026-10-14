# Next work unit (M5 A13 drain boundary)

HYPOTHESIS-ID: m5-a13-drain-boundary

WORK UNIT: run the existing phase-gated A13 default-versus-
`ROGUESQ_DRAIN_INLOOP_TICK=1` validation, with the retail writer controls in
the same invocation.

Competing hypotheses:

* H-A13-default-valid: both port arms reach title/hangar, the default-off
  drain returns cleanly with zero timeout rows, and the explicit tick arm does
  not supply a missing terminal status transition; A13 needs no behavior change.
* H-A13-tick-required: the default-off arm lacks a clean drain return or
  times out while the tick-on arm has a named status/slot transition and clean
  return; the in-loop tick remains a required control-path difference.
* H-A13-route-invalid: title/hangar or the task/SP/PCM controls are absent in
  either arm, so drain behavior cannot be evaluated.

DISCRIMINATING MEASUREMENT: require title and hangar in both port logs, task/SP
completion, nonzero PCM, `[drain-exit]`, `[drain-timeout]`, status/slot rows,
and the retail whole-RDRAM/VI/writer controls. A clean default return with zero
timeouts selects H-A13-default-valid; a tick-only clean return with a default
timeout selects H-A13-tick-required; missing phase or positive controls selects
H-A13-route-invalid.

Exact commands:

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s4693_m5_a13_drain_boundary.sh

Do not infer A13 from a pre-title drain row or from a port-only null; consume
the retail and phase-gated controls together.
