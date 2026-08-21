# NEXT work unit (s2125) — phase-repaired port completion-wait pump A/B

HYPOTHESIS-ID: m5-port-wait-pump-ab

## Work unit

Build once, then run the same two phase-keyed port arms concurrently with the
current audio implementation unchanged. Add `ROGUESQ_SPIN_YIELD=1` to both
arms to repair the s2124 target-coverage split; the only treatment difference
remains `ROGUESQ_AUDIO_WAIT_NOPUMP=1`. Do not edit waits, guards, task fields,
or generated C in this unit.

## Competing hypotheses and discriminator

- `H-PumpRequired`: both arms pass the positive controls and pump-on reaches
  the first wait return and hangar, while pump-off records a target-phase
  countdown stall without the return or later route.
- `H-PumpIrrelevant`: both arms reach title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400` with matching countdown seed/exit, worker/status rows,
  and no meaningful `waitmusyx-spin2` split.
- `H-SecondFlagOwner`: both arms match the first wait, then split at the
  second `0x8014974C` spin or status-3 shutdown; the spin-2, worker, and
  status rows identify that owner.
- `H-CoverageFailure`: either arm lacks the positive controls or title/hangar
  coverage, so absent target wait rows remain uninterpretable.

The discriminator is one same-build, two-arm table keyed by VI width/origin:
LLE/task controls; title/hangar transitions; M5 gate entry/seed/exit;
`waitmusyx-spin2` arm/heartbeat; audio-drain entry/return/iterations;
synth entry/exit; worker/status transitions; guard fires; and terminal
outcome. Select a pump hypothesis only if both arms reach target phases.
No mitigation is authorized by any outcome.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp

    env GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_WAITMUSYX_SPIN2=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_POSTWAIT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2125_pump_on 30 12 > scratch/agent/s2125_pump_on_driver.log 2>&1 &
    ON_PID=$!
    env GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_WAITMUSYX_SPIN2=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_POSTWAIT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_AUDIO_WAIT_NOPUMP=1' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2125_pump_off 30 12 > scratch/agent/s2125_pump_off_driver.log 2>&1 &
    OFF_PID=$!
    wait $ON_PID; ON_RC=$?
    wait $OFF_PID; OFF_RC=$?
    printf 'pump_on_rc=%s pump_off_rc=%s\n' "$ON_RC" "$OFF_RC"

Inspect only bounded rows, never whole logs:

    rg -n '\[phase\]|\[m5-gate\]|\[waitmusyx-spin2|\[audio-wait-pump-stall\]|\[audio-drain-(enter|heartbeat|exit)\]|\[waitforslot-guard-fire\]|\[synth-(entry|exit)\]|\[audio-return\]|\[CRASH\]|\[ABORT\]' scratch/s73_post_a_scene/s2125_pump_on/run.log scratch/s73_post_a_scene/s2125_pump_off/run.log | tail -240
