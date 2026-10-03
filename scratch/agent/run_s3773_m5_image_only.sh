#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/s3773_m5_image_only"
mkdir -p "$OUT"
cd "$ROOT" || exit 2
env tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 75 --watch-write 0x0:0x800000 --watch-write 0x178C80:0x178F80 \
  --watch-write 0x1797B0:0x179A48 --pc-phase-log 0x00790400,0x006AB400 \
  --hit-cap 500 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start,66:start,71:start \
  --hold-ms 150 >"$OUT/oracle.log" 2>&1 &
oracle_pid=$!
cd "$ROOT/build" || exit 2
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_M5_FAMILY_EDGE=1 ROGUESQ_LOG_M5_FAMILY_STORE=1 \
  ROGUESQ_LOG_M5_STATIC_CALLS=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 \
  ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1 \
  ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1 \
  ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_PCM_WRITER=1 \
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_ROUTE_PREPARE=1 \
  ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_DYNAMIC_CALLBACK=1 \
  ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp >"$OUT/image.log" 2>&1 &
image_pid=$!
for tick in {1..300}; do
  kill -0 "$image_pid" 2>/dev/null || break
  sleep 0.25
done
kill -KILL "$image_pid" 2>/dev/null || true
wait "$image_pid" 2>/dev/null || true
kill -KILL "$oracle_pid" 2>/dev/null || true
wait "$oracle_pid" 2>/dev/null || true
print -r -- "oracle_positive=$(grep -a -c 'positive-control threshold reached' "$OUT/oracle.log" || true)" >"$OUT/summary.txt"
print -r -- "image_title=$(grep -a -c 'origin=0x00790400' "$OUT/image.log" || true)" >>"$OUT/summary.txt"
print -r -- "image_hangar=$(grep -a -c 'origin=0x006AB400' "$OUT/image.log" || true)" >>"$OUT/summary.txt"
print -r -- "family_store_control=$(grep -a -c '\[m5-family-store-control\]' "$OUT/image.log" || true)" >>"$OUT/summary.txt"
print -r -- "family_edge=$(grep -a -c '\[m5-family-edge\]' "$OUT/image.log" || true)" >>"$OUT/summary.txt"
