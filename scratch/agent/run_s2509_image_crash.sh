#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s2509_m5_image_crash"
BUILD="$ROOT/build"
mkdir -p "$OUT/single-image" "$OUT/pair-image" "$OUT/pair-silent"

run_arm() {
    local name="$1" audio="$2"
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 \
        ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
        ROGUESQ_AUDIO_UCODE="$audio" ROGUESQ_LOG_PHASE=1 \
        ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
        ROGUESQ_LOG_M5_GATE_CONTRACT=1 PROBE_PHASE_WIDTH=1024 \
        PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
        'PROBE_KEYS=3:start 7:start 11:start 15:a 30:start 45:start 60:a 75:start 90:a 105:start' \
        zsh "$ROOT/tools/probe.sh" "$OUT/$name" 120 0.5 \
        > "$OUT/$name.driver.log" 2>&1
}

run_arm single-image 1 & single_pid=$!
run_arm pair-silent 0 & silent_pid=$!
run_arm pair-image 1 & image_pid=$!
sleep 120
for pid in "$single_pid" "$silent_pid" "$image_pid"; do
    kill -9 "$pid" 2>/dev/null || true
done
wait "$single_pid"; single_rc=$?
wait "$silent_pid"; pair_silent_rc=$?
wait "$image_pid"; pair_image_rc=$?

print "single_image_rc=$single_rc pair_silent_rc=$pair_silent_rc pair_image_rc=$pair_image_rc" > "$OUT/driver.log"
exit 0
