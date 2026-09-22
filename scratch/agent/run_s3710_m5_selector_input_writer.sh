#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s3710_m5_selector_input_writer"
mkdir -p "$OUT"
cd "$BUILD" || exit 2
[[ -x ./RogueSquadron64Recomp && -f ./rogue_squadron.z64 ]] || exit 2

common=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
  ROGUESQ_LOG_M5_INPUT_WRITER=1 ROGUESQ_LOG_M5_SOURCE_WRITER=1
  ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_M5_DESCRIPTOR=1 ROGUESQ_LOG_M5_DOWNSTREAM=1
  ROGUESQ_LOG_M5_STATIC_CALLS=1 ROGUESQ_LOG_M5_WRITER_SETUP=1
  ROGUESQ_LOG_M5_CLEAR_BRANCH=1 ROGUESQ_LOG_M5_CALLER_ROUTE=1
  ROGUESQ_LOG_M5_SELECTOR_INPUT=1 ROGUESQ_LOG_M5_SELECTOR_SOURCE=1
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1
  PROBE_LEAVE_OK=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512
)

for arm in real silent; do
  : > "$OUT/$arm.log"
  audio=1
  [[ "$arm" == silent ]] && audio=0
  env "${common[@]}" ROGUESQ_AUDIO_UCODE="$audio" \
    ./RogueSquadron64Recomp >"$OUT/$arm.log" 2>&1 &
  eval "PID_$arm=$!"
done

deadline=$((SECONDS + 120))
while (( SECONDS < deadline )); do
  alive=0
  for arm in real silent; do
    pid="${(P)${:-PID_$arm}}"
    if kill -0 "$pid" 2>/dev/null; then
      alive=1
    else
      wait "$pid" 2>/dev/null || true
    fi
  done
  (( !alive )) && break
  sleep 1
done
for arm in real silent; do
  pid="${(P)${:-PID_$arm}}"
  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" 2>/dev/null
    wait "$pid" 2>/dev/null || true
  fi
done
