#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2721_m5_drain_tick_validation"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

COMMON=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
  ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
  ROGUESQ_LOG_M5_PCM_WRITER=1 ROGUESQ_LOG_M5_B40_ROUTE=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_AUDIO_DRAIN=1
  PROBE_PHASE_WIDTH=512 PROBE_KEYS_FROM_PHASE=1
)

ORACLE_PID=0; OFF_PID=0; ON_PID=0; KEY_PIDS=()
trap 'for p in "${KEY_PIDS[@]}" "$ORACLE_PID" "$OFF_PID" "$ON_PID"; do [[ "$p" != 0 ]] && kill -9 "$p" 2>/dev/null || true; done' EXIT INT TERM

env "$ORACLE" --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" \
  --secs 500 --watch-write 0x0:0x800000 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
deadline=$((SECONDS + 120)); gate=0
while (( SECONDS < deadline )); do
  if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && \
     grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" && \
     grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then gate=1; break; fi
  kill -0 "$ORACLE_PID" 2>/dev/null || break
  sleep 1
done
print "oracle_gate=$gate" > "$OUT/driver.log"
(( gate == 1 )) || exit 5

launch() {
  local name="$1"; shift
  ( cd "$BUILD" && env ${=COMMON} "$@" ./RogueSquadron64Recomp ) > "$OUT/$name.log" 2>&1 &
  print "${name}_pid=$!" >> "$OUT/driver.log"
  print "$!"
}
OFF_PID=$(launch tick_off)
ON_PID=$(launch tick_on ROGUESQ_DRAIN_INLOOP_TICK=1)

for p in "$OFF_PID" "$ON_PID"; do
  (
    prev=0
    for at in 6 11 16 21 26 31 36 41 46 51 56; do
      sleep "$((at-prev))"; prev=$at
      kill -0 "$p" 2>/dev/null || exit 0
      "$BUILD/winctl" activate "$p" >/dev/null 2>&1 || true
      /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $p to true" >/dev/null 2>&1 || true
      "$BUILD/winctl" key "$p" 36 >/dev/null 2>&1 || true
    done
  ) & KEY_PIDS+=("$!")
done

deadline=$((SECONDS + 240))
while (( SECONDS < deadline )); do
  grep -a -q 'vi_width=512 .*origin=0x006AB400' "$OUT/tick_off.log" && \
    grep -a -q 'vi_width=512 .*origin=0x006AB400' "$OUT/tick_on.log" && break
  sleep 1
done
kill -9 "$OFF_PID" "$ON_PID" "$ORACLE_PID" 2>/dev/null || true
wait "$OFF_PID" 2>/dev/null; print "tick_off_rc=$?" >> "$OUT/driver.log"
wait "$ON_PID" 2>/dev/null; print "tick_on_rc=$?" >> "$OUT/driver.log"
wait "$ORACLE_PID" 2>/dev/null; print "oracle_rc=$?" >> "$OUT/driver.log"

for arm in tick_off tick_on; do
  log="$OUT/$arm.log"
  print -- "--- $arm ---" >> "$OUT/driver.log"
  for marker in '[phase]' '[audio-drain]' '[audio-return]' '[audtask-dispatch]' '[audtask-abi]' '[audtask-dma-range]' '[audtask-image-stage]' '[audio-sp-route]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[CRASH]' '[ABORT]'; do
    print -- "$marker=$(grep -a -F -c "$marker" "$log" || true)" >> "$OUT/driver.log"
  done
done
grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512' "$OUT/oracle.log" | tail -20 > "$OUT/oracle-controls.txt" || true
