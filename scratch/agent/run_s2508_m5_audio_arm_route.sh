#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s2508_m5_audio_arm_route/attempt2"
mkdir -p "$OUT/silent" "$OUT/image"

run_arm() {
    local name="$1"
    local audio="$2"
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 \
        ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
        ROGUESQ_M5_C88_VALUE=0 ROGUESQ_STUB_MISSING_FUNCS=1 \
        ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 \
        ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
        ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 \
        ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 \
        PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
        PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
        'PROBE_KEYS=3:start 7:start 11:start 15:a 30:start 45:start 60:a 75:start 90:a 105:start' \
        ROGUESQ_AUDIO_UCODE="$audio" zsh "$ROOT/tools/probe.sh" "$OUT/$name" 120 0.5 \
        > "$OUT/$name.driver.log" 2>&1
}

run_arm silent 0 & p1=$!
run_arm image 1 & p2=$!
print "silent_pid=$p1 image_pid=$p2" > "$OUT/driver.log"
wait "$p1"; r1=$?
wait "$p2"; r2=$?
print "silent_rc=$r1 image_rc=$r2" >> "$OUT/driver.log"
exit 0
