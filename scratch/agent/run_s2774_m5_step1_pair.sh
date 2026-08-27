#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2774_m5_step1_pair}
OUT="$ROOT/scratch/agent/$TAG"
mkdir -p "$OUT"

ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" || ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" ]]; then
  print "missing prerequisite" > "$OUT/driver.log"
  exit 2
fi

COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
  ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 ROGUESQ_LOG_M5_B40_ROUTE=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1)

ORACLE_PID=0 IMAGE_PID=0 SILENT_PID=0
trap 'for p in "$ORACLE_PID" "$IMAGE_PID" "$SILENT_PID"; do [[ "$p" != 0 ]] && kill -9 "$p" 2>/dev/null || true; done' EXIT INT TERM

env "$ORACLE" --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" --secs 500 \
  --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x141AD0:0x141AF0 \
  --watch-write 0x1498A:0x1498B --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
deadline=$((SECONDS + 120))
while (( SECONDS < deadline )); do
  if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" &&
     grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" &&
     grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
    print 'oracle_gate=passed whole_rdram=10000 title=1 hangar=1' >> "$OUT/driver.log"
    break
  fi
  sleep 1
done
if ! grep -a -q 'oracle_gate=passed' "$OUT/driver.log"; then
  print 'oracle_gate=failed' >> "$OUT/driver.log"
  exit 5
fi

launch() {
  local name="$1" audio="$2"
  (cd "$BUILD" && exec env ${=COMMON} ROGUESQ_AUDIO_UCODE="$audio" ./RogueSquadron64Recomp) > "$OUT/$name.log" 2>&1 &
  [[ "$name" == image ]] && IMAGE_PID=$! || SILENT_PID=$!
}
launch silent 0
launch image 1
sleep 90
print 'pair_window=complete; SIGKILL' >> "$OUT/driver.log"
kill -9 "$IMAGE_PID" "$SILENT_PID" 2>/dev/null || true
for name in image silent; do
  log="$OUT/$name.log"
  print -- "--- $name ---" >> "$OUT/driver.log"
  for marker in '[phase]' '[audtask-dispatch]' '[audtask-abi]' '[audtask-dma-row]' '[audtask-dma-range]' '[audtask-image-stage]' '[audio-return]' '[audio-route]' '[audio-sp-route]' '[m5-gate]' '[slot-alloc]' '[slot-sb]' '[init-desc]' '[filter-voice-audit]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[m5-b40-route-control]' '[m5-route-state-control]' '[CRASH]' '[ABORT]'; do
    print "$marker=$(grep -a -F -c "$marker" "$log" || true)" >> "$OUT/driver.log"
  done
  print "title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" || true) hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" || true)" >> "$OUT/driver.log"
  grep -a -E '^\[(phase|audtask-abi|audtask-dma-row|audtask-dma-range|audtask-image-stage|audio-return|audio-route|audio-sp-route|m5-gate|pcm-boundary-source|pcm-boundary-consumer|CRASH|ABORT)\]' "$log" | tail -12 >> "$OUT/driver.log" || true
done
kill -9 "$ORACLE_PID" 2>/dev/null || true
exit 0
