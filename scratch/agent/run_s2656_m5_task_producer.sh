#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2656_m5_task_producer"
mkdir -p "$OUT"
cd "$BUILD" || exit 2
[[ -x ./RogueSquadron64Recomp && -f ./rogue_squadron.z64 ]] || exit 2

common=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_M5_C88_VALUE=0
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_PORT_LOAD=1
  ROGUESQ_LOG_M5_DESCRIPTOR=1 ROGUESQ_LOG_PCM_BOUNDARY=1
  ROGUESQ_LOG_M5_HOST_BOUNDARY=1
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1
  PROBE_LEAVE_OK=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512
)

for arm in image silent; do
  : > "$OUT/$arm.log"
  audio=1
  [[ "$arm" == silent ]] && audio=0
  env "${common[@]}" ROGUESQ_AUDIO_UCODE="$audio" ./RogueSquadron64Recomp >"$OUT/$arm.log" 2>&1 &
  eval "PID_$arm=$!"
done

deadline=$((SECONDS + 100))
for arm in image silent; do eval "alive_$arm=1"; done
while (( SECONDS < deadline )); do
  for arm in image silent; do
    eval "alive=\${alive_$arm}"
    if (( alive )) && ! kill -0 "${(P)${:-PID_$arm}}" 2>/dev/null; then
      pid="${(P)${:-PID_$arm}}"
      wait "$pid" 2>/dev/null; rc=$?
      print "$arm exited rc=$rc t=${SECONDS}s"
      eval "alive_$arm=0"
    fi
  done
  eval "ai=\${alive_image}"; eval "as=\${alive_silent}"
  (( !ai && !as )) && break
  sleep 1
done
for arm in image silent; do
  pid="${(P)${:-PID_$arm}}"
  eval "alive=\${alive_$arm}"
  if (( alive )); then kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; print "$arm SIGKILL at t=${SECONDS}s"; fi
done
print "logs: $(wc -c "$OUT"/*.log)"
