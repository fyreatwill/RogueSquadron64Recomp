#!/bin/zsh
# s7614 HM witness: audio OSTask* held in events_context.sp_task_queue between submit_rsp_task (enqueue) and task_thread_func
# (consume). Logs all 16 OSTask words at both edges (ROGUESQ_LOG_M5_TASK_LIFETIME); offline pairing in tools/s7614_hm_census.py --witness.
set -u
ROOT="$(pwd)"; OUT="$ROOT/scratch/s7614"; mkdir -p "$OUT"; cd "$ROOT/build" || exit 2
env ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1 \
    ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_AUDIO_DRAIN=1 \
    ./RogueSquadron64Recomp >"$OUT/witness.log" 2>&1 &
pid=$!
sleep ${WSECS:-90}
kill -KILL $pid 2>/dev/null; wait $pid 2>/dev/null
grep -a -c '^\[m5-task-lifetime\]' "$OUT/witness.log"
