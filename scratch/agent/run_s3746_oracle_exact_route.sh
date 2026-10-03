#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s3746_oracle_exact_route"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PRESS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'

mkdir -p "$OUT"
if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ]]; then
  print -r -- 'prerequisite failure' > "$OUT/result.txt"
  exit 2
fi

cd "$ROOT" || exit 3
"$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 75 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x128C92:0x128C93 \
  --watch-write 0x128CD0:0x128CD4 \
  --pc-hist-phase 0x00790400:1024 \
  --pc-hist-phase 0x006AB400:512 \
  --pc-hist-watch 1 --pc-hist-watch 2 \
  --first-watch 1 --first-watch 2 \
  --hit-cap 200 --vi-trace --press "$PRESS" --hold-ms 150 \
  > "$OUT/oracle.log" 2>&1
rc=$?
print -r -- "oracle_rc=$rc" > "$OUT/result.txt"
exit 0
