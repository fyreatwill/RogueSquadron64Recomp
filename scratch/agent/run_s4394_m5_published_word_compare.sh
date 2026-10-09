#!/bin/bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
out_dir="$repo_dir/scratch/agent/s4394_m5_published_word_compare"
mkdir -p "$out_dir"
cd "$repo_dir"

stdbuf -oL tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 75 \
  --oracle-emulator 1 \
  --hit-cap 10000 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x171CE0:0x171CE4 \
  --watch-write 0x173B20:0x173B24 \
  --watch-write 0x171E70:0x171E74 \
  --watch-write 0x173CB0:0x173CB4 \
  --watch-pc 0x80033FCC \
  --pc-task-dump 0x80033FCC \
  --pc-task-type 2 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x00790800:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --ordinal-join \
  --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 --post-value-watch 4 \
  --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 \
  --pc-hist-phase 0x00790400:1024 \
  --pc-hist-phase 0x00790800:1024 \
  --pc-hist-phase 0x006AB400:512 \
  --pc-phase-quiet \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start,66:start,71:start \
  > "$out_dir/oracle.log" 2>&1

log="$out_dir/oracle.log"
grep -a -q 'positive-control threshold reached' "$log"
grep -a -q 'origin=0x00790400 width=1024' "$log"
grep -a -q 'origin=0x006ab400 width=512' "$log"
grep -a -q 'pc-task-summary' "$log"
grep -a -q 'published-word phase=' "$log"
grep -a -q 'ordinal-join-summary.*overflow=0' "$log"
grep -a -E 'positive-control threshold|pc-task-summary|post-store-scalar|published-word phase=|ordinal-join-summary|\[oracle\] done:' "$log" | tail -80
