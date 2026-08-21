# NEXT work unit (s2128) — renderer-recovery M5 drain in-loop tick A/B

HYPOTHESIS-ID: m5-drain-inloop-tick-ab

## Work unit

Build once, then run both forced-LLE port arms concurrently with the current
audio implementation and pump unchanged. Use the phase-gated `tools/probe.sh`
recipe below, which keeps capturing after the title gate and sends the same
phase-relative navigation keys to both arms. The only treatment difference is
`ROGUESQ_DRAIN_INLOOP_TICK=0`; the control leaves it unset/default-on.

The s2126 pair failed treatment coverage at VI 640; s2127 reversed the
coverage failure: tick-off reached title/hangar, while the default-tick
control crashed in RT64 `fullSync`/Metal barriers at VI 640 with last guest PC
`0x8000834c`. This is a renderer-recovery retry of the same work unit. Do not
interpret any arm split unless both arms reach title `1024 @ 0x00790400` and
hangar `512 @ 0x006AB400`.

## Competing hypotheses and discriminator

- `H-DrainTickRequired`: both arms pass controls and target phases, but tick-off
  develops a drain timeout/forced-idle or lacks a clean return while control
  returns with the named status transition.
- `H-DrainTickIrrelevant`: both arms reach title/hangar with matching drain
  entry/heartbeat/return/iteration and worker/status rows, with no timeout.
- `H-WorkerStatusOwner`: both arms reach the drain, but split at the named
  status-3 worker entry or status-zero store; writer and return rows identify
  the owner independently of the injected tick.
- `H-CoverageFailure`: either arm lacks positive LLE/audio controls or title/
  hangar coverage; absent drain rows cannot distinguish the other hypotheses.

The discriminator is one same-build, two-arm table keyed by VI width/origin:
LLE/audio controls; title/hangar transitions; drain entry, heartbeat, return,
iteration, timeout, and forced-idle rows; named worker entry/status-zero
stores; slot/status transitions; and terminal outcome. Select a drain
hypothesis only if both arms reach the target phases. A timeout, pre-target
crash, or forced-idle row is failure evidence, not a successful contract. No
mitigation is authorized by any outcome.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_WAITMUSYX_SPIN2=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_POSTWAIT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 25:start 40:start 60:a 72:start 73:a' zsh tools/probe.sh scratch/agent/s2128_drain_tick_on 180 1 > scratch/agent/s2128_drain_tick_on_driver.log 2>&1 &
    ON_PID=$!
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_WAITMUSYX_SPIN2=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_POSTWAIT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_DRAIN_INLOOP_TICK=0 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 25:start 40:start 60:a 72:start 73:a' zsh tools/probe.sh scratch/agent/s2128_drain_tick_off 180 1 > scratch/agent/s2128_drain_tick_off_driver.log 2>&1 &
    OFF_PID=$!
    wait $ON_PID; ON_RC=$?
    wait $OFF_PID; OFF_RC=$?
    printf 'drain_tick_on_rc=%s drain_tick_off_rc=%s\n' "$ON_RC" "$OFF_RC"

Inspect only bounded rows, never whole logs:

    rg -n '\[phase\]|\[lle task\]|\[audtask-dispatch\]|\[audio-drain-(enter|heartbeat|exit)\]|\[drain-(timeout|forced-idle|return)\]|\[m5-(route-state|postwait|caller-edge)|\[waitmusyx-spin2-arm\]|\[slot-ret-caller\]|\[waitforslot-guard-fire\]|\[CRASH\]|\[ABORT\]' scratch/agent/s2128_drain_tick_on/run.log scratch/agent/s2128_drain_tick_off/run.log | tail -300
