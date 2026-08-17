#!/bin/zsh
# Three-arm Rice: hold + A/Start on the attract 512 the 640 B-frontend
# times out into. Same carrier as s1714/s1744/s1760/s1776/s1792;
# --secs 133 reaches the 126.4s title-like 1024 and still exits before
# the ~135s Rice death.
# New: the 13 ROM jal 0x8000C07C sites plus submitGfxFrame entry.
# Do not re-arm s1744 six-entry, s1760 table, s1776 main-text, or
# s1792 unwatched function entries.
set -u

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE="/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib"
ROM="/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64"
VIDEO="/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib"
OUT="$ROOT/scratch/agent/s1808_submitgfx_jals"
ELEVEN="6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start"
B_ROUTE="$ELEVEN,55:b,58:b,63:b"
# 13 jal 0x8000C07C sites + submitGfxFrame entry.
PCS="0x8006D9A8,0x8006DAE8,0x800A64AC,0x800AB0DC,0x800AF644,0x800B8014,0x800BFF30,0x800C1718,0x800C2D90,0x800C3F4C,0x800C61EC,0x800CA4A4,0x800FAD90,0x8000C07C"

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
