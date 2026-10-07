#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4099_m5_port_selector_writers"
BUILD="$ROOT/build"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

oracle_pid=""
port_pid=""
cleanup() {
  [[ -n "$port_pid" ]] && kill -KILL "$port_pid" 2>/dev/null || true
  [[ -n "$oracle_pid" ]] && kill -KILL "$oracle_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$ROOT" || exit 3
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 75 \
  --watch-write 0x0:0x800000 --watch-write 0x171E22:0x172D00 \
  --hit-cap 10000 --store-field-dump 1:0x80090AAC,0x80090BA4 \
  --pc-hist-watch 1 --pc-hist-phase 0x00790400:1024 \
  --pc-hist-phase 0x006AB400:512 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x006AB400:512 --vi-trace \
  --press 6:start,16:start,26:start,36:start,46:start,56:start \
  > "$OUT/retail.log" 2>&1 &
oracle_pid=$!

for _ in {1..120}; do
  grep -aq 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/retail.log" && break
  sleep 1
done

(
  cd "$BUILD" || exit 2
  exec env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 \
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_DRAIN_INLOOP_TICK=1 \
    ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
    ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 \
    PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT=1 \
    ROGUESQ_LOG_M5_SELECTOR_TABLE=1 ROGUESQ_LOG_M5_INPUT_WRITER=1 \
    ROGUESQ_LOG_M5_PORT_SELECTOR_WRITERS=1 \
    ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp
) > "$OUT/port.log" 2>&1 &
port_pid=$!

for _ in {1..300}; do
  alive=0
  kill -0 "$oracle_pid" 2>/dev/null && alive=1
  kill -0 "$port_pid" 2>/dev/null && alive=1
  (( alive )) || break
  sleep 1
done
cleanup
wait "$oracle_pid" 2>/dev/null || true
wait "$port_pid" 2>/dev/null || true
oracle_pid=""
port_pid=""

control=0; retail_title=0; retail_hangar=0; port_title=0; port_hangar=0
grep -aq 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/retail.log" && control=1
grep -aq 'WIDTH 640 -> 1024' "$OUT/retail.log" && retail_title=1
grep -aq 'WIDTH 1024 -> 512' "$OUT/retail.log" && retail_hangar=1
grep -aq '\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/port.log" && port_title=1
grep -aq '\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port.log" && port_hangar=1

print "control=$control retail_title=$retail_title retail_hangar=$retail_hangar port_title=$port_title port_hangar=$port_hangar" | tee "$OUT/driver.log"
grep -a -E '^\[store-field-dump\].*(80090aac|80090ba4)|^\[oracle\] (pc-hist-phase|done:|positive-control)' "$OUT/retail.log" | tail -160 | tee -a "$OUT/driver.log" || true
grep -a -E '^\[m5-port-selector-writer|^\[m5-selector-(store-context|table-store)|^\[phase\]|^\[CRASH\]|^\[ABORT\]' "$OUT/port.log" | tail -240 | tee -a "$OUT/driver.log" || true
if (( control && retail_title && retail_hangar && port_title && port_hangar )); then
  print 'verdict=qualified; compare exact retail writer rows with paired port selector witness' | tee -a "$OUT/driver.log"
else
  print 'verdict=Hroute-invalid' | tee -a "$OUT/driver.log"
fi
exit 0
