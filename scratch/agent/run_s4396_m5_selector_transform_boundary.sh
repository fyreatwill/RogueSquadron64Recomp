#!/bin/bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
out_dir="$repo_dir/scratch/agent/s4396_m5_selector_transform_boundary"
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
  --watch-write 0x171F70:0x171F74 \
  --watch-write 0x173DB0:0x173DB4 \
  --watch-pc 0x80019DEC,0x80033FCC,0x8009C904,0x8009C950 \
  --watch-pc-range 0x80019C00:0x80019E20 \
  --pc-range-task-dump \
  --pc-task-dump 0x80033FCC \
  --pc-task-type 2 \
  --pc-task-join \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x00790800:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --c904-witness \
  --c904-task-join \
  --ordinal-join \
  --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 --post-value-watch 4 \
  --post-value-watch 5 --post-value-watch 6 \
  --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 \
  --pc-hist-watch 5 --pc-hist-watch 6 \
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
grep -a -q 'origin=0x00790800 width=1024' "$log"
grep -a -q 'origin=0x006ab400 width=512' "$log"
grep -a -q 'pc-task-summary' "$log"
grep -a -q 'pc-range-task-summary rows=[0-9]*/16384 hits=[0-9]* invalid=0 overflow=0' "$log"
grep -a -q 'ordinal-join-summary.*overflow=0' "$log"
grep -a -E 'positive-control threshold|pc-task-summary|c904|pc-range|pc-field|post-store-scalar|ordinal-join|writer-pc-phase|\[oracle\] done:' "$log" | tail -180
