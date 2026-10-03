#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
IMAGE_ONLY=${ROGUESQ_M5_IMAGE_ONLY:-0}
OUT_TAG=s3804_m5_source_input_writer
[[ "$IMAGE_ONLY" == 1 ]] && OUT_TAG=s3805_m5_image_source_ground_truth
OUT="$ROOT/scratch/agent/$OUT_TAG"
BUILD="$ROOT/build"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
mkdir -p "$OUT"

COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_M5_SOURCE_PRODUCER=1 ROGUESQ_LOG_M5_SOURCE_WRITER=1
  ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_LOG_M5_INPUT_WRITER=1
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_RSP_SOURCE=1
  ROGUESQ_LOG_M5_STAGE_BYTES=1 ROGUESQ_LOG_AUDIO_RETURN=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1
  ROGUESQ_AUTOPILOT="$PRESS" ROGUESQ_AUTOPILOT_STOP_WIDTH=512
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1
  PROBE_LEAVE_OK=1 PROBE_KEYS="$PRESS")

cd "$ROOT" || exit 2
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 45 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x1797B0:0x1798B0 \
  --watch-write 0x1798B0:0x179A48 \
  --watch-pc 0x800078EC \
  --hit-cap 20 --pc-phase-quiet \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --vi-trace --press "$PRESS" --hold-ms 150 > "$OUT/oracle.log" 2>&1 &
oracle_pid=$!

launch() {
  local name=$1 audio=$2
  (cd "$ROOT" && exec env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE="$audio" \
    zsh "$ROOT/tools/probe.sh" "$OUT/$name" 180 2 > "$OUT/$name-driver.log" 2>&1) &
  print $! > "$OUT/$name.pid"
}
launch image 1
for tick in {1..60}; do
  grep -a -q '\[phase\].*width=1024\|vi_width=1024' "$OUT/image/run.log" 2>/dev/null && break
  sleep 1
done
[[ "$IMAGE_ONLY" == 1 ]] || launch silent 0
cleanup() {
  if [[ "$IMAGE_ONLY" == 1 ]]; then
    kill -KILL "$oracle_pid" "$image_pid" 2>/dev/null || true
  else
    kill -KILL "$oracle_pid" "$image_pid" "$silent_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM
image_pid=$(<"$OUT/image.pid")
[[ "$IMAGE_ONLY" == 1 ]] || silent_pid=$(<"$OUT/silent.pid")

for tick in {1..150}; do
  ready=0
  arms=(image)
  [[ "$IMAGE_ONLY" == 1 ]] || arms+=(silent)
  for name in $arms; do
    pid=$(<"$OUT/$name.pid")
    if grep -a -q '\[phase\].*width=512\|vi_width=512' "$OUT/$name/run.log" 2>/dev/null || ! kill -0 "$pid" 2>/dev/null; then
      ready=$((ready + 1))
    fi
  done
  if grep -a -q '\[vi\].*origin=0x006ab400' "$OUT/oracle.log" 2>/dev/null || ! kill -0 "$oracle_pid" 2>/dev/null; then
    oracle_ready=1
  else
    oracle_ready=0
  fi
  (( ready == ${#arms} && oracle_ready == 1 )) && break
  sleep 1
done

if [[ "$IMAGE_ONLY" == 1 ]]; then
  kill -KILL "$oracle_pid" "$image_pid" 2>/dev/null || true
else
  kill -KILL "$oracle_pid" "$image_pid" "$silent_pid" 2>/dev/null || true
fi
wait "$oracle_pid" "$image_pid" "$silent_pid" 2>/dev/null || true

: > "$OUT/summary.txt"
names=(oracle image)
[[ "$IMAGE_ONLY" == 1 ]] || names+=(silent)
for name in $names; do
  log="$OUT/$name.log"
  [[ "$name" != oracle ]] && log="$OUT/$name/run.log"
  print -r -- "--- $name ---" >> "$OUT/summary.txt"
  for marker in 'positive-control threshold' '[oracle] done' '[phase]' \
      '[m5-input-writer-control]' '[m5-input-writer]' '[m5-source-producer]' \
      '[m5-source-transition]' '[m5-input-dma]' '[m5-dmem-coverage]' \
      '[m5-source-range-writer]' '[CRASH]' '[ABORT]'; do
    print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/summary.txt"
  done
done
grep -a -E 'positive-control threshold|\[oracle\] (phase|done)|\[hit\].*pc=0x800078EC' "$OUT/oracle.log" | tail -80 >> "$OUT/summary.txt" || true
for name in $arms; do
  grep -a -E '^\[(phase|m5-input-writer|m5-source-producer|m5-source-transition|m5-input-dma|m5-dmem-coverage|m5-source-range-writer|CRASH|ABORT)\]' "$OUT/$name/run.log" | tail -160 >> "$OUT/summary.txt" || true
done
