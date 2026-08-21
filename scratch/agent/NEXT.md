# NEXT work unit (s2126) — M5 drain in-loop tick A/B

HYPOTHESIS-ID: m5-drain-inloop-tick-ab

## Work unit

Build once, then run the same two phase-keyed port arms concurrently with the
current audio implementation and pump unchanged. Both arms use
`ROGUESQ_SPIN_YIELD=1`; the only treatment difference is
`ROGUESQ_DRAIN_INLOOP_TICK=0`. The control keeps the default drain tick.
Do not change the drain timeout, status writes, waits, guards, task fields, or
generated C in this unit.

## Competing hypotheses and discriminator

- `H-DrainTickRequired`: both arms pass the positive controls and target
  phases, but tick-off enters `drainAudioAndFinalizeSpeechBuffer` without a
  clean return or develops a timeout/forced-idle row; the default arm returns
  with a named status transition.
- `H-DrainTickIrrelevant`: both arms reach title `1024 @ 0x00790400` and
  hangar `512 @ 0x006AB400`, with matching drain enter/return/iteration and
  worker/status rows, and neither arm fires the drain timeout.
- `H-WorkerStatusOwner`: both arms reach the drain, but split at the status-3
  worker entry or status-zero store; the named writer and return rows identify
  the owner independently of the injected tick.
- `H-CoverageFailure`: either arm lacks the LLE/audio positive controls or
  title/hangar coverage, so absent drain rows cannot distinguish the other
  hypotheses.

The discriminator is one same-build, two-arm table keyed by VI width/origin:
LLE/audio controls; title/hangar transitions; drain entry, heartbeat, return,
iteration, timeout, and forced-idle rows; named worker entry/status-zero
stores; slot/status transitions; and terminal outcome. Select a drain
hypothesis only if both arms reach the target phases and the drain rows are
present. A timeout or forced-idle row is failure evidence, not a successful
contract. No mitigation is authorized by any outcome.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp

    env GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_WAITMUSYX_SPIN2=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_POSTWAIT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2126_drain_tick_on 30 12 > scratch/agent/s2126_drain_tick_on_driver.log 2>&1 &
    ON_PID=$!
    env GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_WAITMUSYX_SPIN2=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_POSTWAIT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_DRAIN_INLOOP_TICK=0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2126_drain_tick_off 30 12 > scratch/agent/s2126_drain_tick_off_driver.log 2>&1 &
    OFF_PID=$!
    wait $ON_PID; ON_RC=$?
    wait $OFF_PID; OFF_RC=$?
    printf 'drain_tick_on_rc=%s drain_tick_off_rc=%s\n' "$ON_RC" "$OFF_RC"

Inspect only bounded rows, never whole logs:

    rg -n '\[phase\]|\[audtask-dispatch\]|\[audio-drain-(enter|heartbeat|exit)\]|\[drain-(timeout|forced-idle|return)\]|\[serviceVoicePoolFrame|\[status|\[slot|\[waitforslot-guard-fire\]|\[CRASH\]|\[ABORT\]' scratch/s73_post_a_scene/s2126_drain_tick_on/run.log scratch/s73_post_a_scene/s2126_drain_tick_off/run.log | tail -260
