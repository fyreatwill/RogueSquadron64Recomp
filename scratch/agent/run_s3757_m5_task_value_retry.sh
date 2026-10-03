#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s3757_m5_task_value_retry"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 3

COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_DRAIN_INLOOP_TICK=1
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_TASK_WRITE_FAULT=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024
  PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1)

env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp > "$OUT/real.log" 2>&1 &
real_pid=$!
env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=0 ./RogueSquadron64Recomp > "$OUT/silent.log" 2>&1 &
silent_pid=$!
trap 'kill -KILL "$real_pid" "$silent_pid" 2>/dev/null || true' EXIT INT TERM

sleep 75
kill -KILL "$real_pid" "$silent_pid" 2>/dev/null || true
wait "$real_pid" "$silent_pid" 2>/dev/null || true

for arm in real silent; do
  log="$OUT/$arm.log"
  {
    print "$arm"
    for marker in '[m5-task-write-fault-control]' '[m5-task-write-fault]' '[m5-task-write-post]' '[phase]'; do
      print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)"
    done
    grep -a -E '^\[(m5-task-write-fault|m5-task-write-post|phase|CRASH|ABORT|autopilot)\]' "$log" | tail -180 || true
  } > "$OUT/${arm}-summary.txt"
done
