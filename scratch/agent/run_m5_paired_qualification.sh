#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/m5_paired_qualification"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE="$ROOT/../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib"
ORACLE_ROM="$ROOT/../rogue_squadron64/rogue_squadron.z64"
ORACLE_VIDEO="/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib"
mkdir -p "$OUT"

if [[ ! -x "$ROOT/build/RogueSquadron64Recomp" || ! -f "$ROOT/build/rogue_squadron.z64" ||
      ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" || ! -f "$ORACLE_VIDEO" ]]; then
    print "prerequisite failure" > "$OUT/driver.log"
    exit 2
fi

COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_DRAIN_INLOOP_TICK=1
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1
  ROGUESQ_LOG_M5_EXACT_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_WRITER=1
  ROGUESQ_LOG_M5_SOURCE_WRITER=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1
  ROGUESQ_LOG_M5_FAMILY_EDGE=1 ROGUESQ_LOG_M5_SOURCE_PRODUCER=1
  ROGUESQ_LOG_M5_ROUTE_ORDER=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1
  ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512)
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
ORACLE_ARGS=(--core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO"
  --secs 90 --watch-write 0x0:0x800000 --watch-write 0x1797b0:0x179a48
  --hit-cap 10000 --watch-pc 0x80007640 --watch-pc 0x8001e230 --watch-pc 0x8001f954
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006ab400:512
  --vi-trace --press "$PRESS")

cd "$ROOT" || exit 3
env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=1 "$ROOT/build/RogueSquadron64Recomp" > "$OUT/image.log" 2>&1 & image_pid=$!
env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=0 "$ROOT/build/RogueSquadron64Recomp" > "$OUT/silent.log" 2>&1 & silent_pid=$!
env "$ORACLE" "${ORACLE_ARGS[@]}" > "$OUT/oracle.log" 2>&1 & oracle_pid=$!
trap 'kill -KILL "$image_pid" "$silent_pid" "$oracle_pid" 2>/dev/null || true' EXIT INT TERM

sleep 95
kill -KILL "$image_pid" "$silent_pid" "$oracle_pid" 2>/dev/null || true
wait "$image_pid" "$silent_pid" "$oracle_pid" 2>/dev/null || true

for arm in image silent; do
  log="$OUT/$arm.log"
  print -- "--- $arm ---"
  for marker in '[phase]' '[audtask-dispatch]' '[audtask-image-stage-row]' '[audtask-dma-row]' '[audio-return]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[m5-exact-route-poll-control]' '[m5-family-edge-control]' '[CRASH]' '[ABORT]'; do
    print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)"
  done
  print "title=$(grep -a -F -c '[phase] vi_width=1024' "$log" 2>/dev/null || true)"
  print "hangar=$(grep -a -F -c '[phase] vi_width=512' "$log" 2>/dev/null || true)"
  grep -a -E '^\[(phase|CRASH|ABORT)\]' "$log" | tail -20 || true
done
print -- '--- oracle ---'
for marker in 'watch write [0x00000000,0x00800000):' 'origin=0x00790400 width=1024' 'origin=0x006ab400 width=512' '[oracle] done:'; do
  print "$marker=$(grep -a -F -c "$marker" "$OUT/oracle.log" 2>/dev/null || true)"
done
grep -a -E '^\[oracle\] (done|pc-phase|watch-pc)' "$OUT/oracle.log" | tail -30 || true
