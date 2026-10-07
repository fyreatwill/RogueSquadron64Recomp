#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s4110_m5_image_boundary
BUILD=$ROOT/build
mkdir -p "$OUT"

COMMON=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1
  ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_AUDIO_RETURN=1
  ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_B40_ROUTE=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_SP_TASKS=1
  ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024
  PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1
  PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start'
)

cleanup() {
  for pid in "${arm_pid:-}"; do
    [[ -n "$pid" ]] && kill -9 "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

run_arm() {
  local name=$1 legacy=$2
  local extra=()
  [[ "$legacy" == "1" ]] && extra+=(ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1)
  ( cd "$BUILD" && exec env "${COMMON[@]}" "${extra[@]}" ROGUESQ_AUDIO_UCODE=1 \
      zsh "$ROOT/tools/probe.sh" "$OUT/$name" 45 1 ) > "$OUT/$name.driver.log" 2>&1 &
  arm_pid=$!
  wait "$arm_pid"
  local rc=$?
  print "$name rc=$rc" >> "$OUT/driver.log"
  unset arm_pid
  return 0
}

print "retail_ranges=0x178C80:0x178F18 0x166000:0x168000 0x1798B0:0x179A48" > "$OUT/driver.log"
run_arm declared 0
run_arm legacy 1

for name in declared legacy; do
  log="$OUT/$name/run.log"
  print "--- $name ---" >> "$OUT/driver.log"
  for marker in '[phase] vi_width=1024' '[phase] vi_width=512' '[audtask-image-stage]' '[audtask-image-stage-row]' '[audtask-image-join]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[audtask-abi]' '[audio-return]' '[CRASH]' '[ABORT]'; do
    print -r -- "$(print -r -- "$marker" | tr -d '[]')=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
  done
  grep -a '^\[audtask-image-stage\]' "$log" | tail -16 >> "$OUT/driver.log" || true
done

print "completed=1" >> "$OUT/driver.log"
