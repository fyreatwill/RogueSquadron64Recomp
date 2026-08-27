#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2673_m5_ring_writer_ground_truth"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
WINCTL="$BUILD/winctl"
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" ||
      ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" ||
      ! -x "$WINCTL" ]]; then
    print "prerequisite failure" > "$OUT/driver.log"
    exit 2
fi

ORACLE_PID=0
GAME_PID=0
KEY_PID=0
trap 'for pid in "$KEY_PID" "$GAME_PID" "$ORACLE_PID"; do
    if [[ "$pid" != 0 ]] && kill -0 "$pid" 2>/dev/null; then kill -9 "$pid" 2>/dev/null; fi
done' EXIT INT TERM

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 180 \
    --watch-write 0x0:0x800000 \
    --watch-write 0x166450:0x169450 \
    --watch-write 0x1798B0:0x179A48 \
    --watch-write 0x141AD0:0x141AF0 \
    --watch-pc 0x800078EC \
    --pc-phase-log-width 0x006AB400:512 \
    --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start \
    > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!

gate=0
deadline=$((SECONDS + 120))
while (( SECONDS < deadline )); do
    if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" &&
       grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" &&
       grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
        gate=1
        print "oracle_gate=passed whole_rdram=10000 title=1 hangar=1" >> "$OUT/driver.log"
        break
    fi
    if ! kill -0 "$ORACLE_PID" 2>/dev/null; then break; fi
    sleep 1
done
if (( gate == 0 )); then
    print "oracle_gate=failed" >> "$OUT/driver.log"
    exit 5
fi

(
    cd "$BUILD" || exit 2
    exec env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
        ROGUESQ_LLE_SOLO=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_STUB_MISSING_FUNCS=1 \
        ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
        ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_PCM_WRITER=1 \
        ROGUESQ_LOG_M5_STAGE_BYTES=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 \
        ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp
) > "$OUT/port-image.log" 2>&1 &
GAME_PID=$!

(
    for at in 6 11 16 21 26 31 36 41; do
        sleep "$at"
        if ! kill -0 "$GAME_PID" 2>/dev/null; then exit 0; fi
        "$WINCTL" activate "$GAME_PID" >/dev/null 2>&1 || true
        /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $GAME_PID to true" >/dev/null 2>&1 || true
        "$WINCTL" key "$GAME_PID" 36 >/dev/null 2>&1 || true
    done
) &
KEY_PID=$!

target=0
deadline=$((SECONDS + 100))
while (( SECONDS < deadline )); do
    if (( target == 0 )) && grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port-image.log"; then
        target=1
        print "port_hangar=observed" >> "$OUT/driver.log"
        break
    fi
    if ! kill -0 "$GAME_PID" 2>/dev/null; then break; fi
    sleep 1
done
kill -9 "$GAME_PID" 2>/dev/null || true
wait "$GAME_PID" 2>/dev/null || true
oracle_deadline=$((SECONDS + 220))
while (( SECONDS < oracle_deadline )); do
    if ! kill -0 "$ORACLE_PID" 2>/dev/null; then break; fi
    sleep 1
done
if kill -0 "$ORACLE_PID" 2>/dev/null; then
    kill -9 "$ORACLE_PID" 2>/dev/null || true
fi
wait "$ORACLE_PID" 2>/dev/null || true
print "port_target=$target" >> "$OUT/driver.log"
exit 0
