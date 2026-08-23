#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2191_m5_second_origin"
mkdir -p "$OUT"
cd "$BUILD" || exit 2

ENVV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_CUTSCENE_A2_50=1 ROGUESQ_LOG_M5_WRITER_PARITY=1'
env ${=ENVV} ./RogueSquadron64Recomp > "$OUT/run.log" 2>&1 &
PID=$!
DEADLINE=$((SECONDS + 150))
found=0
while kill -0 "$PID" 2>/dev/null; do
    if grep -a -q '\[phase\] vi_width=640 .*origin=0x00696600' "$OUT/run.log"; then
        found=1
        break
    fi
    if (( SECONDS >= DEADLINE )); then
        break
    fi
    sleep 1
done

if (( found )); then
    print "second origin reached; collecting 15s"
    sleep 15
    kill -9 "$PID" 2>/dev/null
    wait "$PID" 2>/dev/null
    exit 0
fi

if kill -0 "$PID" 2>/dev/null; then
    print "second origin timeout; killing"
    kill -9 "$PID" 2>/dev/null
    wait "$PID" 2>/dev/null
    exit 5
fi

wait "$PID" 2>/dev/null
print "game exited before second origin"
exit 4
