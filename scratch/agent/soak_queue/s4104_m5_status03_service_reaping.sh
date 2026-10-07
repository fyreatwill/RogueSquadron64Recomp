#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${RS64_SOAK_OUT:-$ROOT/scratch/agent/soak_results/s4104_m5_status03_service_reaping}"
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
  --watch-write 0x0:0x800000 --hit-cap 10000 \
  --watch-write 0x154620:0x168DB0 \
  --watch-pc 0x8009B30C,0x8009B7CC,0x8009B7EC,0x8009B600,0x8009BDE8,0x8009BCF8 \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --vi-trace --press 6:start,16:start,26:start,36:start,46:start,56:start \
  > "$OUT/retail.log" 2>&1 &
oracle_pid=$!

(
  cd "$BUILD" || exit 2
  exec env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 \
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
    ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 \
    PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    ROGUESQ_LOG_ALL=1 ROGUESQ_AUDIO_UCODE=1 \
    ./RogueSquadron64Recomp
) > "$OUT/port.log" 2>&1 &
port_pid=$!

for _ in {1..300}; do
  if ! kill -0 "$port_pid" 2>/dev/null; then break; fi
  sleep 1
done
cleanup
wait "$port_pid" 2>/dev/null || true
wait "$oracle_pid" 2>/dev/null || true
oracle_pid=""
port_pid=""

control=0; retail_title=0; retail_hangar=0; port_title=0; port_hangar=0
grep -aq 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/retail.log" && control=1
grep -aq 'WIDTH 640 -> 1024' "$OUT/retail.log" && retail_title=1
grep -aq 'WIDTH 1024 -> 512' "$OUT/retail.log" && retail_hangar=1
grep -aq '\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/port.log" && port_title=1
grep -aq '\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port.log" && port_hangar=1

grep -a -E '^\[(s2020-svc|s2028-a11|m5-consumer-entry|phase|CRASH|ABORT)\]' \
  "$OUT/port.log" | tail -500 > "$OUT/port-summary.txt" || true
grep -a -E '^\[(oracle|pc-hist-phase|writer-pc-phase|phase)\].*(8009B30C|8009B7CC|8009B7EC|8009B600|8009BDE8|8009BCF8|006AB400|00790400)' \
  "$OUT/retail.log" | tail -500 > "$OUT/retail-summary.txt" || true
print "control=$control retail_title=$retail_title retail_hangar=$retail_hangar port_title=$port_title port_hangar=$port_hangar" > "$OUT/verdict.txt"
if (( control && retail_title && retail_hangar && port_title && port_hangar )); then
  print 'verdict=qualified; inspect s2020/s2028 worker-entry, status-zero, and shutdown-return joins' >> "$OUT/verdict.txt"
else
  print 'verdict=Hroute-invalid; worker and writer nulls are unevaluable' >> "$OUT/verdict.txt"
  exit 1
fi
exit 0
