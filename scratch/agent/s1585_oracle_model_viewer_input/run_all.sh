#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE="/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib"
ROM="/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64"
VIDEO="/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib"
OUT="$ROOT/scratch/agent/s1585_oracle_model_viewer_input"
ELEVEN="6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start"
PCS="0x800C58A0,0x800C6854,0x80000B20,0x80000BA8,0x80000B70,0x80000BE8,0x800C9BF0"

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
    --secs 110 \
    --watch-write 0x0:0x800000 --hit-cap 10000 \
    --watch-write 0x130B10:0x130B58 \
    --watch-write 0x13A960:0x13A970 \
    --detail-watch 1 --detail-watch 2 \
    --watch-pc "$PCS" \
    --press "$press" \
    --vi-trace --vi-poll --pif-trace \
    >"$dir/run.log" 2>&1
  echo 0 >"$dir/run.rc"
}

run_arm hold "$ELEVEN,58:a,63:a" &
run_arm a "$ELEVEN,58:a,63:a,70:a,78:a,86:a,94:a" &
run_arm b "$ELEVEN,58:a,63:a,70:b,78:b,86:b,94:b" &
run_arm z "$ELEVEN,58:a,63:a,70:z,78:z,86:z,94:z" &
wait

{
  for arm in hold a b z; do
    log="$OUT/$arm/run.log"
    printf '== %s ==\n' "$arm"
    grep -E '^\[vi|^\[pad|^\[oracle\] positive-control|^\[oracle\] watch|^\[oracle\] execution|pc=0x800C6854|pc=0x800C9BF0|pc=0x80000B70|pc=0x80000BA8|pc=0x80000BE8' "$log" | tail -120
  done
} >"$OUT/summary.txt"
sed -n '1,520p' "$OUT/summary.txt"
