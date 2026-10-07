#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4176_m5_predecessor_range"
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
  --watch-pc-range 0x8008f900:0x8008fb00 \
  --watch-pc 0x8008f9c8 --watch-pc 0x80090268 --watch-pc 0x80090278 \
  --watch-pc 0x8008ff04 --watch-pc 0x8008ff0c --watch-pc 0x8008ff14 \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006ab400:512 \
  --pc-field-dump 0x8008f9c8,0x80090268,0x80090278,0x8008ff04,0x8008ff0c,0x8008ff14 \
  --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006ab400:512 \
  --vi-trace --press "$PRESS" --hold-ms 150 > "$OUT/retail.log" 2>&1
rc=$?

control=0; title=0; hangar=0; exact=0; range=0
grep -aq 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/retail.log" && control=1
grep -aq 'WIDTH 640 -> 1024' "$OUT/retail.log" && title=1
grep -aq 'WIDTH 1024 -> 512' "$OUT/retail.log" && hangar=1
grep -aq '\[oracle\] watch exec.*pc=0x8008f9c8' "$OUT/retail.log" && exact=1
grep -aq '^\[oracle\] watch exec.*pc=0x8008f9' "$OUT/retail.log" && range=1
printf 'rc=%s control=%s title=%s hangar=%s exact_entry=%s range_entry=%s\n' \
  "$rc" "$control" "$title" "$hangar" "$exact" "$range" > "$OUT/verdict.txt"
grep -a -E '^([[]oracle|[[]vi|[[]pc-field-dump|[[]pc-hist-phase|[[]pc-phase)' \
  "$OUT/retail.log" | tail -900 > "$OUT/retail-summary.txt" || true
cat "$OUT/verdict.txt"
exit "$rc"
