#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s4011_m5_candidate_writers_qualified
BUILD=$ROOT/build
mkdir -p "$OUT"

ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start

if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ||
      ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" ]]; then
    print -r -- 'setup_missing' > "$OUT/driver.log"
    exit 2
fi

cleanup() {
    for pid in "${oracle_pid:-}" "${declared_pid:-}" "${legacy_pid:-}"; do
        [[ -n "$pid" ]] && kill -KILL "$pid" 2>/dev/null || true
    done
}
trap cleanup EXIT INT TERM

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 75 \
    --watch-write 0x0:0x800000 --watch-write 0x165000:0x16C000 \
    --watch-write 0x173CB0:0x173DB0 --watch-write 0x1798B0:0x179A48 \
    --watch-write 0x149470:0x1494B0 --pc-task-dump 0x80033FCC --pc-task-type 2 \
    --pc-task-join --pc-field-dump 0x80015BC8,0x8000F3A0 \
    --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
    --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 \
    --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 \
    --post-value-watch 2 --post-value-watch 3 \
    --post-value-pc 0x80005294,0x80005298,0x8000529C --post-value-pc-detail \
    --vi-trace --hit-cap 20 --press "$PRESS" --hold-ms 150 > "$OUT/retail.log" 2>&1 &
oracle_pid=$!

run_port() {
    local name="$1"
    shift
    ( cd "$BUILD" && env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
        ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
        ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
        PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_PHASE=1 \
        ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1 \
        ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1 \
        ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 \
        ROGUESQ_LOG_M5_EXACT_ROUTE=1 ROGUESQ_LOG_M5_SOURCE_RANGE=1 \
        ROGUESQ_LOG_M5_ROUTE_PREPARE=1 ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 \
        ROGUESQ_AUDIO_UCODE=1 "$@" ./RogueSquadron64Recomp ) > "$OUT/$name.log" 2>&1 &
    print $!
}

declared_pid=$(run_port declared-real)
legacy_pid=$(run_port legacy-real env ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1)
print "oracle=$oracle_pid declared=$declared_pid legacy=$legacy_pid" > "$OUT/driver.log"

for _ in {1..480}; do
    alive=0
    for pid in "$oracle_pid" "$declared_pid" "$legacy_pid"; do
        kill -0 "$pid" 2>/dev/null && alive=1
    done
    (( alive )) || break
    sleep 0.25
done

for pid in "$oracle_pid" "$declared_pid" "$legacy_pid"; do
    kill -KILL "$pid" 2>/dev/null || true
done
for pid in "$oracle_pid" "$declared_pid" "$legacy_pid"; do
    wait "$pid" 2>/dev/null || true
done

for name in retail declared-real legacy-real; do
    log="$OUT/$name.log"
    print -r -- "--- $name ---" >> "$OUT/driver.log"
    grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|audtask-abi|audtask-image-dma-join|post-target-summary|post-target-rows|oracle] done|\[CRASH\]|\[ABORT\]|last-guest-pc|\[phase\]' "$log" \
        | tail -160 >> "$OUT/driver.log" || true
done
