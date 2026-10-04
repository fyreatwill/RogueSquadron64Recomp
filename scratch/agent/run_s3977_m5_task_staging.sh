#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
BUILD="$ROOT/build"
LOGDIR="$ROOT/scratch/agent/soak_results/s3977_m5_task_staging"
mkdir -p "$LOGDIR"

run_arm() {
    local name="$1"
    shift
    local log="$LOGDIR/$name.log"
    (
        cd "$BUILD"
        env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
            ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
            ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
            ROGUESQ_AUTOPILOT_STOP_WIDTH=512 \
            PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 \
            PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
            ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 \
            ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 "$@" \
            ./RogueSquadron64Recomp >"$log" 2>&1 &
        local pid=$!
        sleep 180
        kill -9 "$pid" 2>/dev/null || true
        wait "$pid" 2>/dev/null || true
    )
}

run_arm declared-size
run_arm legacy-size env ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1
