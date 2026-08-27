#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2836_m5_launch_order"
mkdir -p "$OUT"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
[[ -x "$ORACLE" && -f "$CORE" && -f "$ROM" && -x "$BUILD/RogueSquadron64Recomp" && -f "$BUILD/rogue_squadron.z64" ]] || exit 2

SCHEDULE='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,66:start,76:start,86:start,96:start,106:start'
COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_M5_C88_VALUE=0
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
  ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 ROGUESQ_LOG_M5_B40_ROUTE=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_AUTOPILOT="$SCHEDULE")
ORACLE_PID=0 IMAGE_PID=0 SILENT_PID=0
trap 'for p in "$ORACLE_PID" "$IMAGE_PID" "$SILENT_PID"; do [[ "$p" != 0 ]] && kill -9 "$p" 2>/dev/null || true; done' EXIT INT TERM

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 120 \
  --watch-write 0x0:0x800000 --vi-trace --press "$SCHEDULE" > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
deadline=$((SECONDS + 90))
while (( SECONDS < deadline )); do
  if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" &&
     grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" &&
     grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
    print 'oracle_gate=passed whole_rdram=10000 title=1 hangar=1' > "$OUT/driver.log"
    break
  fi
  sleep 1
done
[[ -f "$OUT/driver.log" ]] || { print 'oracle_gate=failed' > "$OUT/driver.log"; exit 5; }

launch() {
  local name="$1" audio="$2"
  (cd "$BUILD" && exec env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE="$audio" ./RogueSquadron64Recomp) > "$OUT/$name.log" 2>&1 &
  [[ "$name" == image ]] && IMAGE_PID=$! || SILENT_PID=$!
}
launch image 1
launch silent 0
sleep 120
print 'pair_window=complete; SIGKILL' >> "$OUT/driver.log"
for pid in "$IMAGE_PID" "$SILENT_PID" "$ORACLE_PID"; do kill -9 "$pid" 2>/dev/null || true; done
for name in image silent; do
  log="$OUT/$name.log"
  print -- "--- $name ---" >> "$OUT/driver.log"
  for marker in '[phase]' '[audtask-dispatch]' '[audtask-abi]' '[audtask-dma-row]' '[audtask-image-stage]' '[audio-return]' '[audio-route]' '[m5-gate]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[CRASH]' '[ABORT]'; do
    print "$marker=$(grep -a -F -c "$marker" "$log" || true)" >> "$OUT/driver.log"
  done
  print "title=$(grep -a -c '^\\[phase\\] vi_width=1024 .*origin=0x00790400' "$log" || true) hangar=$(grep -a -c '^\\[phase\\] vi_width=512 .*origin=0x006AB400' "$log" || true)" >> "$OUT/driver.log"
done
