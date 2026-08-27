#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2580_m5_image_isolated}
OUT="$ROOT/scratch/agent/$TAG"
mkdir -p "$OUT"
cd "$BUILD" || exit 2

trap 'if [[ -n "${GAME_PID:-}" ]] && kill -0 "$GAME_PID" 2>/dev/null; then kill -9 "$GAME_PID" 2>/dev/null; fi' EXIT INT TERM

env \
  ROGUESQ_LLE_FORCE=1 \
  ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_AUDIO_UCODE=1 \
  ROGUESQ_M5_C88_VALUE=0 \
  ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_AUDIO_RETURN=1 \
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 \
  ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
  ROGUESQ_LOG_VI_CALLERS=1 \
  ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 \
  ROGUESQ_LOG_M5_PCM_WRITER=1 \
  ROGUESQ_LOG_M5_B40_ROUTE=1 \
  ROGUESQ_LOG_M5_ROUTE_STATE=1 \
  PROBE_PHASE_WIDTH=1024 \
  PROBE_KEYS_FROM_PHASE=1 \
  ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
  ./RogueSquadron64Recomp > "$OUT/run.log" 2>&1 &
GAME_PID=$!

deadline=$((SECONDS + 90))
while (( SECONDS < deadline )); do
  if ! kill -0 "$GAME_PID" 2>/dev/null; then
    wait "$GAME_PID" 2>/dev/null
    print "game_exited rc=$?" > "$OUT/status"
    exit 1
  fi
  sleep 1
done

kill -9 "$GAME_PID" 2>/dev/null
wait "$GAME_PID" 2>/dev/null
print "watchdog=90s SIGKILL" > "$OUT/status"
exit 0
