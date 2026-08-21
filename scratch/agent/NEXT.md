# NEXT work unit (s2124) — port completion-wait pump A/B

HYPOTHESIS-ID: m5-port-wait-pump-ab

## Work unit

Build the current tree once, then run both phase-keyed port arms in the same
iteration with the audio implementation held constant and the existing wait
diagnostics enabled:

- pump-on control: unset `ROGUESQ_AUDIO_WAIT_NOPUMP`;
- pump-off treatment: `ROGUESQ_AUDIO_WAIT_NOPUMP=1`.

Use the existing `run_mission_keys.sh` driver and run both arms concurrently;
the driver owns each process's window and writes its own run log. Do not edit
waits, guards, task fields, or generated C in this unit. The retail s2123
census already established the guest countdown/worker/status contract; this
unit measures whether the current port pump is the missing completion edge.

## Competing hypotheses and discriminator

- `H-PumpRequired`: pump-on reaches the wait return and qualified hangar,
  while pump-off logs the countdown seed and blind-spin entry with a nonzero
  countdown, but no wait return or target-phase route.
- `H-PumpIrrelevant`: both arms reach title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`, with matching countdown seed/exit, worker/status rows,
  and no meaningful `waitmusyx-spin2` divergence.
- `H-SecondFlagOwner`: both arms pass the first countdown wait, but diverge at
  the second `0x8014974C` spin or status-3 shutdown; the `waitmusyx-spin2`,
  service-worker, and status rows identify that separate completion owner.
- `H-CoverageFailure`: the positive LLE/task controls or VI phase controls do
  not fire in either arm, so a missing wait row is not interpretable.

The discriminator is one same-build, two-arm table keyed by VI width/origin:
positive LLE/audio dispatch controls; title/hangar transitions; M5 gate
entry/seed/exit; `waitmusyx-spin2` arm/heartbeat; audio-drain entry/return,
iteration and guard fires; synth entry/exit; worker/status transitions; and
terminal outcome. `H-PumpRequired` requires a passing control plus a pump-off
countdown stall; `H-PumpIrrelevant` requires matching target rows in both
arms; `H-SecondFlagOwner` requires matched first-wait rows and a later
second-spin/status split; otherwise select `H-CoverageFailure`. No mitigation
is authorized by any outcome.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp

    env GAME_EXTRA_ENV='ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_WAITMUSYX_SPIN2=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_POSTWAIT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2124_pump_on 30 12 > scratch/agent/s2124_pump_on_driver.log 2>&1 &
    ON_PID=$!
    env GAME_EXTRA_ENV='ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_WAITMUSYX_SPIN2=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_POSTWAIT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_AUDIO_WAIT_NOPUMP=1' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2124_pump_off 30 12 > scratch/agent/s2124_pump_off_driver.log 2>&1 &
    OFF_PID=$!
    wait $ON_PID; ON_RC=$?
    wait $OFF_PID; OFF_RC=$?
    printf 'pump_on_rc=%s pump_off_rc=%s\n' "$ON_RC" "$OFF_RC"

Inspect only bounded rows, never whole logs:

    rg -n '\[phase\]|\[m5-gate\]|\[waitmusyx-spin2|\[audio-wait-pump-stall\]|\[audio-drain-(enter|heartbeat|exit)\]|\[waitforslot-guard-fire\]|\[synth-(entry|exit)\]|\[audio-return\]|\[CRASH\]|\[ABORT\]' scratch/s73_post_a_scene/s2124_pump_on/run.log scratch/s73_post_a_scene/s2124_pump_off/run.log | tail -240
