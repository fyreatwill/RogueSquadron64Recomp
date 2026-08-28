#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s3028_m5_step1_contract_pair"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"
: > "$OUT/driver.log"
if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" ||
      ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" ||
      ! -x "$BUILD/winctl" ]]; then
  print "missing prerequisite" > "$OUT/driver.log"
  exit 2
fi
GAME_PIDS=()
ORACLE_PID=""
trap 'for p in "\${GAME_PIDS[@]}" "$ORACLE_PID"; do [[ -n "$p" ]] && kill -9 "$p" 2>/dev/null; done' EXIT INT TERM
env "$ORACLE" --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" \
  --secs 300 --watch-write 0x0:0x800000 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start \
  > "$OUT/retail.log" 2>&1 &
ORACLE_PID=$!
deadline=$((SECONDS + 120))
while (( SECONDS < deadline )); do
  if grep -aq 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/retail.log" &&
     grep -aq 'origin=0x00790400 width=1024' "$OUT/retail.log" &&
     grep -aqi 'origin=0x006ab400 width=512' "$OUT/retail.log"; then
    print 'retail_control=passed whole_rdram=10000 title=1 hangar=1' >> "$OUT/driver.log"
    break
  fi
  sleep 1
done
if ! grep -aq 'retail_control=passed' "$OUT/driver.log"; then
  print 'retail_control=failed' >> "$OUT/driver.log"
  exit 3
fi
common=(ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_LOG_ALL=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512)
launch() {
  local arm="$1" value="$2"
  ( cd "$BUILD"; exec env \${=common} ROGUESQ_AUDIO_UCODE="$value" ./RogueSquadron64Recomp ) \
    > "$OUT/$arm.log" 2>&1 &
  GAME_PIDS+=($!)
}
launch silent 0
launch image 1
for i in {1..240}; do
  seen=0
  for arm in silent image; do
    if grep -aq '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/$arm.log"; then
      seen=$((seen + 1))
    fi
  done
  (( seen == 2 )) && break
  sleep 1
done
for p in "\${GAME_PIDS[@]}" "$ORACLE_PID"; do kill -9 "$p" 2>/dev/null; done
wait 2>/dev/null
for arm in silent image; do
  log="$OUT/$arm.log"
  print "--- $arm ---" >> "$OUT/driver.log"
  for marker in audtask-dispatch audtask-abi audtask-dma-row audtask-dma-range audtask-image-stage audio-return sp-complete audio-route pcm-boundary-source pcm-boundary-consumer '[m5-gate]' '[slot-' '[filter-voice-audit]' '[CRASH]' '[ABORT]'; do
    print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
  done
  print "title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" || true) hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" || true)" >> "$OUT/driver.log"
  grep -a -E '^\[(phase|audtask-dispatch|audtask-abi|audtask-dma-row|audtask-dma-range|audtask-image-stage|audio-return|sp-complete|audio-route|pcm-boundary-source|pcm-boundary-consumer|m5-gate|slot-|filter-voice-audit|CRASH|ABORT)\]' "$log" | tail -20 >> "$OUT/driver.log"
done
if grep -aq '\[CRASH\]\|\[ABORT\]' "$OUT/silent.log" "$OUT/image.log"; then exit 4; fi
exit 0
