#!/bin/zsh
# Three-arm Rice: hold + A/Start on the attract 512 the 640 B-frontend
# times out into. Same carrier as s1714/s1744; --secs 133 reaches the
# 126.4s title-like 1024 and still exits before the ~135s Rice death.
# New: complete menuOverlayInit 11-way jump-table callees.
set -u

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE="/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib"
ROM="/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64"
VIDEO="/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib"
OUT="$ROOT/scratch/agent/s1760_menu_jtbl"
ELEVEN="6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start"
B_ROUTE="$ELEVEN,55:b,58:b,63:b"
# hangar frame + loadOverlay entry/menu dest + dispatcher + 11 case callees.
PCS="0x800AAD9C,0x80000B20,0x80000BA8,0x800C58A0,0x800C6854,0x800C5D9C,0x800B47D0,0x800BF830,0x800C5EF8,0x800C9BF0,0x800C131C,0x800C28F0,0x800C30C8"

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
