#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4175_m5_object_entry"
mkdir -p "$OUT"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PRESS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'

cd "$ROOT" || exit 2
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 75 \
  --watch-write 0x0:0x800000 --hit-cap 10000 \
  --watch-write 0x178c80:0x178f18 \
  --watch-pc 0x8008f900 --watch-pc 0x80090268 --watch-pc 0x80090278 \
  --watch-pc 0x8008ff04 --watch-pc 0x8008ff0c --watch-pc 0x8008ff14 \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006ab400:512 \
  --pc-field-dump 0x8008f900,0x80090268,0x80090278,0x8008ff04,0x8008ff0c,0x8008ff14 \
  --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006ab400:512 \
  --vi-trace --press "$PRESS" --hold-ms 150 > "$OUT/retail.log" 2>&1 &
retail=$!

sleep 2
(
  cd "$ROOT/build" || exit 2
  exec env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 \
    ROGUESQ_LOG_M5_OBJECT_ENTRY=1 ROGUESQ_LOG_M5_OBJECT_FIELD=1 \
    ROGUESQ_LOG_M5_SOURCE_CONTEXT=1 ROGUESQ_LOG_M5_WRITER_SETUP=1 \
    ROGUESQ_LOG_PHASE=1 \
    ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
    PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 \
    ./RogueSquadron64Recomp
) > "$OUT/port.log" 2>&1 &
port=$!

trap 'kill -KILL "$retail" "$port" 2>/dev/null || true' EXIT INT TERM
for tick in {1..360}; do
  alive=0
  kill -0 "$retail" 2>/dev/null && alive=1
  kill -0 "$port" 2>/dev/null && alive=1
  (( alive )) || break
  sleep 0.25
done
kill -KILL "$retail" "$port" 2>/dev/null || true
wait "$retail" 2>/dev/null || true
wait "$port" 2>/dev/null || true

control=0; retail_title=0; retail_hangar=0; port_title=0; port_hangar=0
grep -aq 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/retail.log" && control=1
grep -aq 'WIDTH 640 -> 1024' "$OUT/retail.log" && retail_title=1
grep -aq 'WIDTH 1024 -> 512' "$OUT/retail.log" && retail_hangar=1
grep -aq '\[phase\].*width=1024.*origin=0x00790400' "$OUT/port.log" && port_title=1
grep -aq '\[phase\].*width=512.*origin=0x006AB400' "$OUT/port.log" && port_hangar=1
printf 'control=%s retail_title=%s retail_hangar=%s port_title=%s port_hangar=%s\n' \
  "$control" "$retail_title" "$retail_hangar" "$port_title" "$port_hangar" > "$OUT/verdict.txt"
grep -a -E '^\[(m5-object-entry|m5-object-field|m5-source-context|phase|CRASH|ABORT)' "$OUT/port.log" | tail -500 > "$OUT/port-summary.txt" || true
grep -a -E '^(\[oracle|\[vi|\[pc-field-dump|\[pc-hist-phase|\[pc-phase)' "$OUT/retail.log" | tail -700 > "$OUT/retail-summary.txt" || true
(( control && retail_title && retail_hangar && port_title && port_hangar ))
