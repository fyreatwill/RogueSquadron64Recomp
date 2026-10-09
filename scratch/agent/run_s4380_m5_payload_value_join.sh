#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s4380_m5_payload_value_join
mkdir -p "$OUT"
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PRESS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'

if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ]]; then
  print -r -- setup_missing > "$OUT/driver.log"
  exit 2
fi

cd "$ROOT" || exit 2
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 75 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x178C80:0x179A48 \
  --watch-write 0x1E2FC0:0x1E3300 \
  --watch-write 0x149470:0x1494B0 \
  --watch-pc 0x80033FCC \
  --pc-task-dump 0x80033FCC --pc-task-type 2 --pc-task-join \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x00790800:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --pc-hist-phase 0x00790400:1024 \
  --pc-hist-phase 0x00790800:1024 \
  --pc-hist-phase 0x006AB400:512 \
  --pc-hist-watch 1 --pc-hist-watch 2 \
  --post-value-watch 1 --post-value-watch 2 \
  --post-value-pc 0x8008F7D4,0x80091374 --post-value-pc-detail \
  --ordinal-join --vi-trace --hit-cap 20 --press "$PRESS" --hold-ms 150 \
  > "$OUT/retail.log" 2>&1
rc=$?

for marker in \
  'positive-control threshold reached' \
  'origin=0x00790400 width=1024' \
  'origin=0x00790800 width=1024' \
  'origin=0x006ab400 width=512' \
  '[pc-task-dump]' '[pc-task-join]' '[oracle] pc-hist-phase' \
  '[oracle] post-value' '[oracle] post-store-scalar' \
  '[oracle] ordinal-join' '[oracle] done:'; do
  print -r -- "${marker// /_}=$(grep -a -F -c "$marker" "$OUT/retail.log" || true)"
done > "$OUT/driver.log"
print -r -- "oracle_rc=$rc" >> "$OUT/driver.log"
grep -a -E 'positive-control|origin=0x00(790400|790800|6ab400)|pc-task|pc-hist-phase|post-value|post-store-scalar|ordinal|done:' "$OUT/retail.log" | tail -240 > "$OUT/retail_tail.txt" || true
exit "$rc"
