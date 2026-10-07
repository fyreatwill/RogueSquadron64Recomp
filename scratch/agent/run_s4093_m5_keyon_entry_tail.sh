#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4093_m5_keyon_entry_tail"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PID=""
trap '[[ -n "$PID" ]] && kill -9 "$PID" 2>/dev/null || true' EXIT INT TERM
mkdir -p "$OUT"
cd "$ROOT" || exit 3
PRESS=6:start,16:start,26:start,36:start,46:start,56:start

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 60 \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x80090A3C,0x80090DE8,0x80090768 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --hit-cap 500 --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1 &
PID=$!
wait "$PID" 2>/dev/null || true
PID=""

control=0
grep -aq 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && control=1
title=0
hangar=0
grep -aq 'WIDTH 640 -> 1024' "$OUT/oracle.log" && title=1
grep -aq 'WIDTH 1024 -> 512' "$OUT/oracle.log" && hangar=1

for pc in 80090A3C 80090DE8 80090768; do
  lower=$(print "$pc" | tr 'A-F' 'a-f')
  line=$(grep -a "watch pc \[0x$lower" "$OUT/oracle.log" | tail -1 || true)
  lifetime=$(print "$line" | sed -n 's/.*: \([0-9][0-9]*\) hit(s).*/\1/p')
  [[ -n "$lifetime" ]] || lifetime=0
  title_rows=$(grep -a -c "pc=0x$lower .*width=1024 origin=0x00790400" "$OUT/oracle.log" || true)
  hangar_rows=$(grep -a -c "pc=0x$lower .*width=512 origin=0x006ab400" "$OUT/oracle.log" || true)
  print "pc=0x$pc lifetime=$lifetime title=$title_rows hangar=$hangar_rows"
done > "$OUT/summary.txt"
print "control=$control title=$title hangar=$hangar" | tee "$OUT/driver.log"
cat "$OUT/summary.txt" | tee -a "$OUT/driver.log"
if (( control == 1 && title == 1 && hangar == 1 )); then
  print 'verdict=qualified; classify entry/tail/publisher phase rows' | tee -a "$OUT/driver.log"
else
  print 'verdict=Hcoverage' | tee -a "$OUT/driver.log"
fi
exit 0
