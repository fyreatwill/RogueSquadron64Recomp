#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s3691_m5_stale_input_payload"
BIN="$ROOT/build/RogueSquadron64Recomp"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 3

run_arm() {
    local name="$1"
    local audio="$2"
    env ROGUESQ_AUDIO_UCODE="$audio" ROGUESQ_LLE_FORCE=1 \
        ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
        ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 \
        ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_STAGE_CALLS=1 \
        ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 \
        ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 \
        PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
        PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
        ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
        ROGUESQ_AUTOPILOT_STOP_WIDTH=512 "$BIN" > "$OUT/$name.log" 2>&1 &
    echo $!
}

real_pid="$(run_arm real 1)"
silent_pid="$(run_arm silent 0)"
sleep 70
kill -KILL "$real_pid" "$silent_pid" 2>/dev/null || true
wait "$real_pid" 2>/dev/null || true
wait "$silent_pid" 2>/dev/null || true

for name in real silent; do
    grep -a -E '^\[(phase|m5-input-dma|m5-source-range-reader|audtask-image-stage-row|audtask-image-join|CRASH|ABORT)' \
        "$OUT/$name.log" > "$OUT/$name.summary.log" || true
done
