#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
out_dir="$repo_dir/scratch/agent/s4393_m5_exact_span_containment_fixed"
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
  --watch-write 0x171E70:0x173290 \
  --watch-write 0x171F70:0x171F74 \
  --watch-write 0x173CB0:0x1750D0 \
  --watch-write 0x173DB0:0x173DB4 \
  --watch-write 0x0:0x20 \
  --watch-pc 0x80033FCC \
  --pc-task-dump 0x80033FCC \
  --pc-task-type 2 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x00790800:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --ordinal-join \
  --pc-hist-watch 1 \
  --pc-hist-watch 2 \
  --pc-hist-watch 3 \
  --pc-hist-watch 4 \
  --pc-hist-watch 5 \
  --pc-hist-watch 6 \
  --pc-hist-phase 0x00790400:1024 \
  --pc-hist-phase 0x00790800:1024 \
  --pc-hist-phase 0x006AB400:512 \
  --first-watch 1 \
  --first-watch 2 \
  --first-watch 3 \
  --first-watch 4 \
  --first-watch 5 \
  --first-watch 6 \
  --pc-phase-quiet \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start,66:start,71:start \
  > "$out_dir/oracle.log" 2>&1
