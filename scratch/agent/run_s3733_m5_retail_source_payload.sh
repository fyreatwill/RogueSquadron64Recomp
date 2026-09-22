#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s3733_m5_retail_source_payload_fixed"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib

mkdir -p "$OUT"
if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ]]; then
    print "prerequisite failure" > "$OUT/driver.log"
    exit 2
fi

PRESS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'
cd "$ROOT" || exit 3
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 120 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x1797B0:0x1798B0 \
  --watch-write 0x1798B0:0x179A48 \
  --watch-write 0x173CB0:0x173DB0 \
  --watch-write 0x166450:0x169450 \
  --pc-task-dump 0x80033FCC --pc-task-type 2 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --pc-hist-phase 0x00790400:1024 \
  --pc-hist-phase 0x006AB400:512 \
  --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 \
  --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 --post-value-watch 4 \
  --hit-cap 20 --vi-trace --press "$PRESS" --hold-ms 150 \
  > "$OUT/oracle.log" 2>&1 &
pid=$!
trap 'kill -9 "$pid" 2>/dev/null || true' EXIT INT TERM

deadline=$((SECONDS + 150))
while (( SECONDS < deadline )); do
    kill -0 "$pid" 2>/dev/null || break
    sleep 1
done
if kill -0 "$pid" 2>/dev/null; then
    print "watchdog=SIGKILL" > "$OUT/driver.log"
    kill -9 "$pid" 2>/dev/null || true
fi
wait "$pid" 2>/dev/null
print "oracle_rc=$?" >> "$OUT/driver.log"
grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|\[oracle\] done|pc-task-dump|writer-pc|post-value watch=|exec-prev' "$OUT/oracle.log" | tail -400 > "$OUT/summary.txt" || true
exit 0
