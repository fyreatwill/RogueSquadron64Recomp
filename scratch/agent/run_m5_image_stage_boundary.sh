#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s3801_m5_image_stage_boundary"
BUILD="$ROOT/build"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
mkdir -p "$OUT"
cd "$ROOT" || exit 2

COMMON=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1
  PROBE_LEAVE_OK=1 PROBE_KEYS="$PRESS"
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1
  ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1
  ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_PCM_WRITER=1
  ROGUESQ_LOG_M5_AUDIO_HOST=1 ROGUESQ_LOG_M5_CALLBACK_ORDER=1
)

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 120 \
  --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x1798B0 \
  --watch-write 0x1798B0:0x179A48 --watch-pc 0x800078EC \
  --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 \
  --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1 &
OPID=$!

launch() {
  local name=$1 audio=$2
  (cd "$BUILD" && exec env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE="$audio" \
    ./RogueSquadron64Recomp > "$OUT/$name.log" 2>&1) &
  print $! > "$OUT/$name.pid"
}

launch image 1
launch silent 0
for tick in {1..150}; do
  ready=0
  for name in image silent; do
    pid=$(<"$OUT/$name.pid")
    if grep -a -q '\[phase\].*width=512\|vi_width=512' "$OUT/$name.log" 2>/dev/null || ! kill -0 "$pid" 2>/dev/null; then
      ready=$((ready + 1))
    fi
  done
  (( ready == 2 )) && break
  sleep 1
done

for name in image silent; do
  pid=$(<"$OUT/$name.pid")
  kill -KILL "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
done
kill -KILL "$OPID" 2>/dev/null || true
wait "$OPID" 2>/dev/null || true

: > "$OUT/summary.txt"
for name in image silent; do
  log="$OUT/$name.log"
  print -r -- "--- $name ---" >> "$OUT/summary.txt"
  for marker in '[phase]' '[m5-rsp-source-hook-control]' '[m5-source-range-reader]' '[m5-source-range-writer]' '[m5-stage-bytes]' '[audtask-image-stage]' '[m5-image-queue]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[audio-return]' '[CRASH]' '[ABORT]'; do
    print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/summary.txt"
  done
  grep -a -E '\[(phase|m5-source-range-reader|m5-source-range-writer|m5-stage-bytes|audtask-image-stage|m5-image-queue|pcm-boundary-(source|consumer)|CRASH|ABORT)' "$log" | tail -80 >> "$OUT/summary.txt" || true
done
grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|\[oracle\] done' "$OUT/oracle.log" | tail -30 >> "$OUT/summary.txt" || true
