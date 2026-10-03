#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/s3838_m5_task_contract_target_stability"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 2
run_arm() {
  local tag="$1"
  shift
  env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
    PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 \
    ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_FAMILY_EDGE=1 ROGUESQ_LOG_M5_FAMILY_STORE=1 \
    ROGUESQ_LOG_M5_TASK_LIFETIME=1 ROGUESQ_LOG_M5_STAGE_CALLS=1 \
    ROGUESQ_LOG_M5_STAGE_BYTES=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_PCM_WRITER=1 \
    ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_EXACT_ROUTE=1 \
    ROGUESQ_LOG_M5_SOURCE_RANGE=1 ROGUESQ_LOG_M5_ROUTE_PREPARE=1 \
    ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_DYNAMIC_CALLBACK=1 \
    ROGUESQ_AUDIO_UCODE=1 "$@" ./RogueSquadron64Recomp > "$OUT/$tag.log" 2>&1 &
  print -r -- "$!"
}
off_pid=$(run_arm logger_off)
on_pid=$(run_arm logger_on ROGUESQ_LOG_M5_TASK_CONTRACT=1)
print -r -- "logger_off_pid=$off_pid logger_on_pid=$on_pid" > "$OUT/driver.log"
for tick in {1..720}; do
  alive=0
  kill -0 "$off_pid" 2>/dev/null && alive=1
  kill -0 "$on_pid" 2>/dev/null && alive=1
  (( alive )) || break
  sleep 0.25
done
kill -KILL "$off_pid" "$on_pid" 2>/dev/null || true
wait "$off_pid" 2>/dev/null || true
wait "$on_pid" 2>/dev/null || true
for tag in logger_off logger_on; do
  for marker in '[phase]' 'origin=0x00790400' 'origin=0x006ab400' '[audtask-abi]' 'CRASH' 'ABORT'; do
    print -r -- "$tag:${marker// /_}=$(grep -a -F -c "$marker" "$OUT/$tag.log" || true)" >> "$OUT/driver.log"
  done
done
