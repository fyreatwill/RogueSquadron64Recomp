#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s2871_m5_route_repair_discriminator
mkdir -p "$OUT"
cd "$ROOT/build" || exit 2

COMMON=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_M4_Y8000_WIDTH=512
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
  ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
  ROGUESQ_LOG_M5_PCM_WRITER=1 ROGUESQ_LOG_M5_B40_ROUTE=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=512
  PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1
  PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start'
)

env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=0 \
  zsh ../tools/probe.sh "$OUT/silent" 180 2 > "$OUT/silent.driver.log" 2>&1 &
silent_pid=$!
env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=1 \
  zsh ../tools/probe.sh "$OUT/image" 180 2 > "$OUT/image.driver.log" 2>&1 &
image_pid=$!
print "silent_pid=$silent_pid image_pid=$image_pid" > "$OUT/driver.log"

wait "$silent_pid"; silent_rc=$?
wait "$image_pid"; image_rc=$?
print "silent_rc=$silent_rc image_rc=$image_rc" >> "$OUT/driver.log"
for name in silent image; do
  log="$OUT/$name/run.log"
  print "$name phases=$(grep -a -c '^\[phase\]' "$log" 2>/dev/null || true) title=$(grep -a -c 'vi_width=1024 .*origin=0x00790400' "$log" 2>/dev/null || true) hangar=$(grep -a -c 'vi_width=512 .*origin=0x006AB400' "$log" 2>/dev/null || true) crash=$(grep -a -c '^\[CRASH\]' "$log" 2>/dev/null || true) abort=$(grep -a -c '^\[ABORT\]' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
done
(( silent_rc == 0 && image_rc == 0 ))
