#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s2886_m5_route_contract"
mkdir -p "$OUT"

SCHEDULE='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start 66:start 76:start 86:start 96:start'
COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1
  ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
  ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1
  ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_STAGE_CALLS=1
  ROGUESQ_LOG_M5_IDENTITY_EDGES=1 ROGUESQ_AUTOPILOT="$SCHEDULE")

run_arm() {
  local arm="$1" audio="$2"
  (cd "$ROOT/build" && env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE="$audio" \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
    PROBE_LEAVE_OK=1 PROBE_KEYS="$SCHEDULE" \
    zsh "$ROOT/tools/probe.sh" "$OUT/$arm" 180 0.5) >"$OUT/$arm.driver" 2>&1
}

if [[ "${SUMMARY_ONLY:-0}" != 1 ]]; then
  run_arm image 1 &
  IMAGE_PID=$!
  run_arm silent 0 &
  SILENT_PID=$!
  wait "$IMAGE_PID"
  IMAGE_RC=$?
  wait "$SILENT_PID"
  SILENT_RC=$?
else
  IMAGE_RC=not-run
  SILENT_RC=not-run
fi

print "image_rc=$IMAGE_RC silent_rc=$SILENT_RC" > "$OUT/summary.txt"
for arm in image silent; do
  log="$OUT/$arm/run.log"
  print -- "--- $arm ---" >> "$OUT/summary.txt"
  for marker in '[phase]' '[audtask-dispatch]' '[audtask-abi]' '[audtask-dma-row]' \
      '[audtask-dma-range]' '[audtask-image-stage]' '[audio-return]' '[audio-route]' \
      '[audio-sp-route]' '[m5-gate]' '[slot-alloc]' '[slot-sb]' '[init-desc]' \
      '[filter-voice-audit]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' \
      '[m5-route-state]' '[m5-route-prepare]' '[m5-stage-call]' '[CRASH]' '[ABORT]'; do
    print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/summary.txt"
  done
  print "title=$(grep -a -c 'origin=0x00790400' "$log" 2>/dev/null || true) hangar=$(grep -a -c 'origin=0x006AB400' "$log" 2>/dev/null || true)" >> "$OUT/summary.txt"
done
