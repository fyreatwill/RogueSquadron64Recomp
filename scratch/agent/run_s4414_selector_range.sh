#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4414_selector_range"
mkdir -p "$OUT"

cd "$ROOT" || exit 3
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom "$ROOT/rogue_squadron.z64" \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 75 \
  --watch-write 0x0:0x800000 \
  --vi-trace \
  --pc-hist-phase 0x00790400:1024 \
  --pc-hist-phase 0x00790800:1024 \
  --pc-hist-phase 0x006AB400:512 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x00790800:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --watch-pc-range 0x80029D20:0x80029F20 \
  --watch-pc 0x8009C904,0x8009C950,0x80091BAC,0x80091CB8,0x80033FCC \
  --pc-field-dump 0x80029E78,0x80033FCC \
  --pc-task-dump 0x80033FCC \
  --pc-task-type 2 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$OUT/oracle.log" 2>&1
rc=$?

{
  printf 'rc=%s\n' "$rc"
  grep -a -F -m1 '[oracle] done:' "$OUT/oracle.log" || true
  grep -a -F '[oracle] VI' "$OUT/oracle.log" | tail -5 || true
  printf 'control_hits='; grep -a -F -c '[hit] w addr=' "$OUT/oracle.log" || true
  printf 'range_exec='; grep -a -F -c '[watch] exec pc=0x80029' "$OUT/oracle.log" || true
  printf 'field_rows='; grep -a -F -c '[pc-field-dump]' "$OUT/oracle.log" || true
  printf 'task_rows='; grep -a -F -c '[pc-task-dump]' "$OUT/oracle.log" || true
  printf 'hangar_phase='; grep -a -F -c 'origin=0x006ab400' "$OUT/oracle.log" || true
  printf '%s\n' '--- selector-range hits ---'
  grep -a -E '\[watch\] exec pc=0x80029|exec-prev pc=0x80029' "$OUT/oracle.log" | head -120 || true
  printf '%s\n' '--- task rows ---'
  grep -a -F '[pc-task-dump]' "$OUT/oracle.log" | head -80 || true
} > "$OUT/summary.txt"
exit "$rc"
