#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4338_c904_c88c_join"
BUILD="$ROOT/build"
RUNBUILD="$OUT/build"
rm -rf "$OUT"
mkdir -p "$RUNBUILD/saves"
for f in "$BUILD"/*(N); do
  [[ "${f:t}" == saves ]] && continue
  ln -s "$f" "$RUNBUILD/${f:t}"
done
cp "$BUILD/saves/rs64.n64.us.1.0.bin" "$RUNBUILD/saves/rs64.n64.us.1.0.bin"

COMMON=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M4_Y8000_WIDTH=512
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CALLERS=1
  ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 ROGUESQ_LOG_M5_DESCRIPTOR=1
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1
  ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_M5_B40_ROUTE=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
  ROGUESQ_LOG_M5_ROUTE_TRANSITION=1
)

cd "$RUNBUILD"
env ${=COMMON} \
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 \
  PROBE_PHASE_TIMEOUT=120 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  "$RUNBUILD/RogueSquadron64Recomp" > "$OUT/run.log" 2>&1 &
PID=$!
for _ in {1..180}; do
  kill -0 "$PID" 2>/dev/null || break
  sleep 1
done
kill -KILL "$PID" 2>/dev/null || true
wait "$PID" 2>/dev/null || true

log="$OUT/run.log"
phase1024=$(grep -ac '\[phase\] vi_width=1024 .*origin=0x00790400' "$log")
phase512=$(grep -ac '\[phase\] vi_width=512 .*origin=0x006AB400' "$log")
c88c=$(grep -ac '\[m5-c88c-desc\]' "$log")
direct=$(grep -ac '\[m5-filter-direct\]' "$log")
controls=$(grep -ac '\[filter-voice-audit-control\]' "$log")
host=$(grep -ac '\[m5-host-boundary-control\]' "$log")
crash=$(grep -a 'pc-symbol\|last-guest-pc' "$log" | tail -2 | tr '\n' ';')
print "phase1024=$phase1024 phase512=$phase512 c88c=$c88c direct=$direct controls=$controls host=$host crash=$crash"
