# Next work unit (M5 host-queue validation)

HYPOTHESIS-ID: m5-host-queue-result

WORK UNIT: run the existing phase-gated audio route after the host bridge
change that makes SDL queue success a prerequisite for PCM consumer joins.

Competing hypotheses:

* H-host-queue-valid: title/hangar source and consumer rows remain paired and
  no host-error rows occur; the SDL boundary is not the missing edge.
* H-host-queue-failed: source rows continue but host-error rows appear and
  consumer joins are suppressed; the prior consumer evidence was false.
* H-route-invalid: title/hangar or source controls are absent, so the host
  boundary cannot be evaluated.

DISCRIMINATING MEASUREMENT: run the same-build image arm with phase-gated
source, host, and consumer controls. Require title/hangar and nonzero source
PCM. Compare `[m5-audio-host-error]`, queue return/byte deltas, and consumer
join counts. Success with no errors selects H-host-queue-valid; errors plus
suppressed joins select H-host-queue-failed; missing route/source controls
select H-route-invalid.

Exact commands:

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_AUDIO_HOST=1 zsh tools/run_m5_yield_ab.sh

Do not infer a host result from a pre-title run; consume the queued soak
verdict before changing this unit.
