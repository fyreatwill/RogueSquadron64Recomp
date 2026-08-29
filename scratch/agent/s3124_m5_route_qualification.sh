#!/bin/zsh
set -u

ROOT="/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s3124_m5_route_qualification"
mkdir -p "$OUT"

COMMON=(ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_M5_C88_VALUE=0
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1
  ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
  ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1
  ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_STAGE_CALLS=1
  ROGUESQ_LOG_M5_PORT_LOAD=1 ROGUESQ_LOG_M5_DESCRIPTOR=1
  ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,20:start,25:a,30:start')

launch() {
  local name="$1" audio="$2"
  (cd "$BUILD" && exec env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE="$audio" \
    ./RogueSquadron64Recomp) > "$OUT/$name.log" 2>&1 &
  print -r -- "$!"
}

IMAGE_PID=$(launch image 1)
SILENT_PID=$(launch silent 0)
trap 'kill -9 "$IMAGE_PID" "$SILENT_PID" 2>/dev/null || true' EXIT INT TERM
sleep 120
kill -9 "$IMAGE_PID" "$SILENT_PID" 2>/dev/null || true
wait "$IMAGE_PID" "$SILENT_PID" 2>/dev/null || true

for name in image silent; do
  log="$OUT/$name.log"
  print -- "--- $name ---"
  for marker in '[phase]' '[audtask-dispatch]' '[audtask-abi]' '[audtask-dma-row]' \
    '[audtask-image-stage]' '[audio-return]' '[m5-gate]' '[pcm-boundary-source]' \
    '[pcm-boundary-consumer]' '[m5-route-state]' '[m5-route-candidate]' \
    '[CRASH]' '[ABORT]'; do
    print "$marker=$(grep -a -F -c "$marker" "$log" || true)"
  done
  print "title=$(grep -a -c '^\\[phase\\] vi_width=1024 .*origin=0x00790400' "$log" || true) hangar=$(grep -a -c '^\\[phase\\] vi_width=512 .*origin=0x006AB400' "$log" || true)"
done > "$OUT/summary.txt"
