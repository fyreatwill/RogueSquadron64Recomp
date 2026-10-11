#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s4591_oracle_tag_detail
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib

mkdir -p "$OUT"
if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ]]; then
  print -r -- setup_missing > "$OUT/status.txt"
  exit 2
fi

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 75 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x179A60:0x179A68 \
  --hit-cap 10000 --first-watch 1 --pc-hist-watch 1 \
  --post-value-watch 1 \
  --post-value-pc 0x8008fb64,0x8008fb68,0x8008fe98,0x8008fea0 \
  --post-value-pc-detail --post-value-pc-detail-phase 0x006AB400:512 \
  --pc-hist-phase 0x006AB400:512 --pc-hist-phase 0x006A2900:640 \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$OUT/retail.log" 2>&1
rc=$?
print -r -- "rc=$rc" > "$OUT/status.txt"
grep -a -E '\[oracle\] done|positive-control|\[hit\].*watch=1|first-watch|writer-pc|pc-hist|VI|width|origin' "$OUT/retail.log" | tail -240 > "$OUT/summary.txt" || true
exit $rc
