#!/bin/zsh
set -u
ROOT=${0:A:h:h:h}
OUT="$ROOT/scratch/agent/soak_results/s3241_m5_vi_swap_target"
mkdir -p "$OUT"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE="$ROOT/../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib"
ROM="$ROOT/../rogue_squadron64/rogue_squadron.z64"
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" ]]; then
  print -u2 "oracle prerequisites missing"
  exit 2
fi
cd "$ROOT/build"
exec env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 45 \
  --watch-write 0x0:0x800000 --watch-pc 0x80035500 \
  --pc-phase-log-width 0x00790400:1024 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$OUT/oracle.log" 2>&1
