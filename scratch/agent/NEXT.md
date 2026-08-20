# NEXT work unit (s2027)

HYPOTHESIS-ID: m5-drain-shutdown-status-boundary

## Work unit

Recover the missing phase-valid arm for the corrected drain-tick A/B. Use the
currently rebuilt binary, whose strings must first prove it contains both
`ROGUESQ_DRAIN_INLOOP_TICK` and `[drain-inloop-gate]`. Run the same
forced-LLE `tools/probe.sh` wrapper and eleven-Start schedule concurrently in
two arms. Keep every passive audio/status variable identical and toggle only
`ROGUESQ_DRAIN_INLOOP_TICK`: arm A unset/on, arm B `0`. Do not add
instrumentation, change default audio, or enable the opt-in audio image.

The s2026 tick-on arm is the positive route reference: it reached VI 1024 and
VI 512, emitted the s2006 control, and saw status `0x00`/`zero_skip=1` with no
store. The s2026 tick-off arm crashed in `matchKeywordWithPriority+88` before
VI 1024 and never reached the gate. Since the gate is inside the later drain
function, that pre-gate crash is an anchor failure, not drain evidence.

## Competing hypotheses and discriminator

- H1 drain boundary: both arms are phase-valid; tick-off reaches call 3 and
  exposes status 3 followed by worker entry and the `0x8009B7EC` store, while
  tick-on does not.
- H2 worker boundary: both arms are phase-valid and reach call 3, but neither
  emits worker entry/store; the drain toggle is not the missing dispatch.
- H3 anchor crash: tick-off again dies before VI 1024 and before
  `[drain-inloop-gate]`, selecting `matchKeywordWithPriority+88` as the next
  boundary and forbidding any drain/status conclusion.
- H4 route/timing instability: both arms reach the phase controls but have
  different route/terminal signatures without a status/store split; do not
  call that a drain result until the phase-gated table is complete.

The single discriminating table has one row per arm: gate `en`, first VI 1024
and VI 512, s2006 entry/exit controls, audio-drain enter/exit, drain return,
shutdown call-3 evidence, s2008 writer rows, s2020 service entry/exit, s2022
status and `zero_skip`, independent worker entry, and the store edge. A row is
usable only if it reaches VI 1024/512 and emits the s2006 control. The outcomes
above select H1, H2, H3, or H4 respectively; a terminal crash after the table
is complete does not erase the table.

## Commands

~~~sh
strings build/RogueSquadron64Recomp | rg 'ROGUESQ_DRAIN_INLOOP_TICK|drain-inloop-gate'
probe_env=(
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1
  ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1
  ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1
  ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1
  ROGUESQ_LOG_S2008_STATUS_WRITERS=1
  'PROBE_KEYS=6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start'
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
)
env "${probe_env[@]}" zsh tools/probe.sh scratch/s73_post_a_scene/s2027-tick-on 120 2 > scratch/agent/s2027-tick-on.stdout 2>&1 &
pid_a=$!
env "${probe_env[@]}" ROGUESQ_DRAIN_INLOOP_TICK=0 zsh tools/probe.sh scratch/s73_post_a_scene/s2027-tick-off 120 2 > scratch/agent/s2027-tick-off.stdout 2>&1 &
pid_b=$!
wait "$pid_a"; rc_a=$?
wait "$pid_b"; rc_b=$?
printf 'tick-on rc=%s\ntick-off rc=%s\n' "$rc_a" "$rc_b"
~~~

Consume only bounded counts and selected rows from each `run.log`; do not
cat the logs.
