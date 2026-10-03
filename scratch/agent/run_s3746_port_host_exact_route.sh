#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s3746_port_host_exact_route_fixed"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 3

COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_M5_C88_VALUE=0
  ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
  ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_STAGE_BYTES=1
  ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_ROUTE_PREPARE=1
  ROGUESQ_LOG_M5_SOURCE_WRITER=1 ROGUESQ_LOG_M5_SOURCE_PRODUCER=1
  ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_LOG_M5_FAMILY_PROVENANCE=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512)

env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp > "$OUT/real.log" 2>&1 &
real_pid=$!
env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=0 ./RogueSquadron64Recomp > "$OUT/silent.log" 2>&1 &
silent_pid=$!
trap 'kill -KILL "$real_pid" "$silent_pid" 2>/dev/null || true' EXIT INT TERM

sleep 70
kill -KILL "$real_pid" "$silent_pid" 2>/dev/null || true
wait "$real_pid" "$silent_pid" 2>/dev/null || true

for arm in real silent; do
  log="$OUT/$arm.log"
  {
    print -r -- "$arm"
    for marker in '[m5-host-write-api-control]' '[m5-host-write]' \
      '[m5-rsp-source-hook-control]' '[phase] 1024' '[phase] 512' \
      '[m5-exact-route-dma]' '[m5-source-range-writer]' '[CRASH]' '[ABORT]'; do
      print -r -- "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)"
    done
    grep -a -E '\[m5-host-write-hook-control\]|\[m5-host-write\]|\[phase\] (1024|512)' "$log" | tail -40 || true
  } >> "$OUT/summary.txt"
done
