#!/bin/zsh
# Three-arm Rice: hold + A/Start on the attract 512 the 640 B-frontend
# times out into. Same carrier as s1714/s1744/s1760; --secs 133 reaches
# the 126.4s title-like 1024 and still exits before the ~135s Rice death.
# New: main-text screen/frame handlers outside the overlay tables.
set -u

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE="/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib"
ROM="/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64"
VIDEO="/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib"
OUT="$ROOT/scratch/agent/s1776_maintext_pcs"
ELEVEN="6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start"
B_ROUTE="$ELEVEN,55:b,58:b,63:b"
# hangar frame + loadOverlay entry/menu dest + ship-select control +
# seven new main-text handlers. Do not re-arm s1744 six-entry or s1760 table.
PCS="0x800AAD9C,0x80000B20,0x80000BA8,0x800C131C,0x8003DFA0,0x8000C07C,0x80001354,0x8006B000,0x8001B7F0,0x8001BA9C,0x80008D20"

run_arm() {
  local name="$1"
  local press="$2"
  local dir="$OUT/$name"
  mkdir -p "$dir"
  "$ORACLE" \
    --core "$CORE" \
    --rom "$ROM" \
    --video "$VIDEO" \
    --configdir "$dir" \
    --secs 133 \
    --watch-write 0x0:0x800000 --hit-cap 10000 \
    --watch-write 0x130B10:0x130B58 \
    --watch-write 0x13B40:0x13B48 \
    --detail-watch 1 --detail-watch 2 \
    --watch-pc "$PCS" \
    --press "$press" \
    --vi-trace --vi-poll --pif-trace \
    >"$dir/run.log" 2>&1
  local rc=$?
  echo "$rc" >"$dir/run.rc"
}

mkdir -p "$OUT"
run_arm hold  "$B_ROUTE" &
run_arm a     "$B_ROUTE,119:a,123:a" &
run_arm start "$B_ROUTE,119:start,123:start" &
wait

python3 "$OUT/summarize.py"
