#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
out_dir="$repo_dir/scratch/agent/s4383_m5_writer_task_join_full"
mkdir -p "$out_dir"

cd "$repo_dir"
stdbuf -oL tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 75 \
  --oracle-emulator 1 \
  --hit-cap 64 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x178C80:0x179A48 \
  --watch-write 0x1E2FC0:0x1E3300 \
  --watch-pc 0x80033FCC \
  --pc-task-dump 0x80033FCC \
  --pc-task-type 2 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x00790800:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --ordinal-join \
  --post-value-watch 1 \
  --post-value-watch 2 \
  --post-value-pc 0x8008F7D4,0x80091374 \
  --pc-phase-quiet \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start,66:start,71:start \
  > "$out_dir/oracle.log" 2>&1
