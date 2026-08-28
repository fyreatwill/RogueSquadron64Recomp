#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s2968_m5_step1_image_vs_silent
BUILD=$ROOT/build
mkdir -p "$OUT"

COMMON=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
  ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 ROGUESQ_LOG_M5_B40_ROUTE=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024
  PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1
  PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start'
)

cleanup() {
  for pid in "${silent_pid:-}" "${image_pid:-}"; do
    [[ -n "$pid" ]] && kill -9 "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

( cd "$BUILD" && exec env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=0 \
    zsh "$ROOT/tools/probe.sh" "$OUT/silent" 90 1 ) > "$OUT/silent.driver.log" 2>&1 &
silent_pid=$!
( cd "$BUILD" && exec env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=1 \
    zsh "$ROOT/tools/probe.sh" "$OUT/image" 90 1 ) > "$OUT/image.driver.log" 2>&1 &
image_pid=$!

wait "$silent_pid"; silent_rc=$?
wait "$image_pid"; image_rc=$?
print "silent_rc=$silent_rc image_rc=$image_rc" > "$OUT/ports.done"
exit 0
