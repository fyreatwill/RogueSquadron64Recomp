#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s3537_m5_output_writer"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
WINCTL="$BUILD/winctl"

[[ "$OUT" != .* ]] || exit 2
mkdir -p "$OUT"
if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" || ! -f "$ORACLE_VIDEO" || ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" || ! -x "$WINCTL" ]]; then
  print "missing prerequisite" > "$OUT/driver.log"
  exit 2
fi

PRESS=20:start,25:start,30:start,35:start,40:start,45:start,50:start,55:start,60:start,65:start
print oracle_start > "$OUT/driver.log"
env "$ORACLE" --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" \
  --secs 75 --watch-write 0x0:0x800000 \
  --watch-write 0x166450:0x169450 \
  --watch-write 0x166D50:0x167050 \
  --watch-write 0x167050:0x167350 \
  --watch-write 0x1935E0:0x1935F0 \
  --hit-cap 40 --watch-pc 0x800078EC \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 \
  --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 \
  --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 --post-value-watch 4 \
  --post-value-pc 0x800078EC --post-value-pc-detail --vi-trace --press "$PRESS" \
  > "$OUT/oracle.log" 2>&1
oracle_rc=$?
print "oracle_rc=$oracle_rc" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] (done:|watch write|writer-pc-phase|post-value)' "$OUT/oracle.log" | tail -80 >> "$OUT/driver.log" || true

COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
  ROGUESQ_M5_C88_VALUE=0 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_DRAIN_INLOOP_TICK=1
  ROGUESQ_AUTOPILOT='20:start,25:start,30:start,35:start,40:start,45:start,50:start,55:start,60:start,65:start'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_PCM_WRITER=1
  ROGUESQ_LOG_M5_STAGE_BYTES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1
  ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1
  ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1)
cd "$BUILD" || exit 3
env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1 &
pid=$!
trap 'kill -9 "$pid" 2>/dev/null || true' EXIT INT TERM
for _ in {1..60}; do
  kill -0 "$pid" 2>/dev/null || break
  "$WINCTL" find "$pid" >/dev/null 2>&1 && break
  sleep 1
done
(
  previous=0
  for at in 6 11 16 21 26 31 36 41 46 51 56; do
    sleep $((at - previous))
    previous=$at
    kill -0 "$pid" 2>/dev/null || break
    "$WINCTL" activate "$pid" >/dev/null 2>&1 || true
    "$WINCTL" key "$pid" 36 >/dev/null 2>&1 || true
  done
) &
keypid=$!
sleep 80
kill -9 "$pid" 2>/dev/null || true
kill -9 "$keypid" 2>/dev/null || true
wait "$pid" 2>/dev/null || true
print "port_summary" >> "$OUT/driver.log"
for marker in '[phase]' '[m5-rsp-source]' '[audtask-image-stage]' '[audtask-image-join]' '[audtask-dma-range]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[pcm-writer]' '[CRASH]' '[ABORT]'; do
  print "$marker=$(grep -a -F -c "$marker" "$OUT/port.log" 2>/dev/null || true)" >> "$OUT/driver.log"
done
grep -a -E '^\[(phase|m5-rsp-source|audtask-image-stage|audtask-image-join|audtask-dma-range|pcm-boundary-source|pcm-boundary-consumer|pcm-writer|CRASH|ABORT)\]' "$OUT/port.log" | tail -100 >> "$OUT/driver.log" || true
exit 0
