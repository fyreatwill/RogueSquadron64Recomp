#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4092_m5_keyon_ground_truth"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
LOG="$OUT/oracle.log"
mkdir -p "$OUT"
cd "$ROOT" || exit 3

ORACLE_PID=""
trap '[[ -n "$ORACLE_PID" ]] && kill -9 "$ORACLE_PID" 2>/dev/null || true' EXIT INT TERM

env "$ORACLE" \
  --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 60 \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x80090CEC,0x80090D04,0x80090D30,0x80090D48,0x80090D74,0x80090D8C,0x80090DB8,0x80090DD0,0x80090768 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --hit-cap 500 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$LOG" 2>&1 &
ORACLE_PID=$!
sleep 65
kill -9 "$ORACLE_PID" 2>/dev/null || true
wait "$ORACLE_PID" 2>/dev/null || true
ORACLE_PID=""

control=0
title=0
hangar=0
grep -aq 'positive-control threshold reached: watch index 0 callbacks=10000' "$LOG" && control=1
grep -aq 'origin=0x00790400 width=1024' "$LOG" && title=1
grep -aq 'origin=0x006ab400 width=512' "$LOG" && hangar=1

for pc in 80090CEC 80090D04 80090D30 80090D48 80090D74 80090D8C 80090DB8 80090DD0 80090768; do
  count=$(grep -a -c "pc=0x$pc" "$LOG" || true)
  title_count=$(grep -a "pc=0x$pc" "$LOG" | grep -a -c 'width=1024 origin=0x00790400' || true)
  hangar_count=$(grep -a "pc=0x$pc" "$LOG" | grep -a -c 'width=512 origin=0x006ab400' || true)
  print "pc=0x$pc lifetime=$count title=$title_count hangar=$hangar_count"
done | tee "$OUT/summary.txt"
print "control=$control title=$title hangar=$hangar" | tee -a "$OUT/summary.txt"
grep -a -E '^\[oracle\] (positive-control threshold|watch pc|exec-prev|done)|^\[vi\].*WIDTH (1024|512)' "$LOG" | tail -300 > "$OUT/oracle-summary.txt" || true

if (( control && title && hangar )); then
  exit 0
fi
exit 4
