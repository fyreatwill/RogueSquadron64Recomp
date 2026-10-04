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
        env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 "$@" \
            ./RogueSquadron64Recomp >"$log" 2>&1 &
        local pid=$!
        sleep 180
        kill -9 "$pid" 2>/dev/null || true
        wait "$pid" 2>/dev/null || true
    )
}

run_arm declared-size
run_arm legacy-size env ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1
