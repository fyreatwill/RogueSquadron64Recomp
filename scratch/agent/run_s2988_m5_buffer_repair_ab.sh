#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
BUILD=$ROOT/build
OUT=$ROOT/scratch/agent/s2988_m5_buffer_repair_ab
mkdir -p "$OUT"

COMMON=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_M4_Y8000_WIDTH=512
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_ROUTE_CANDIDATE=1
  ROGUESQ_LOG_M5_ROUTE_PREPARE=1 ROGUESQ_LOG_M5_WRITER_ENTRY=1
  PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1
  PROBE_LEAVE_OK=1
  PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start'
)

run_arm() {
  local name=$1
  shift
  mkdir -p "$OUT/$name"
  ( cd "$BUILD" && exec env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=1 "$@" \
      zsh "$ROOT/tools/probe.sh" "$OUT/$name" 180 2 ) \
      > "$OUT/$name/driver.log" 2>&1 &
}

run_arm control
control_pid=$!
run_arm repair ROGUESQ_FORCE_BUFFER_PROGRESS=1
repair_pid=$!
wait "$control_pid"; control_rc=$?
wait "$repair_pid"; repair_rc=$?

for name in control repair; do
  log="$OUT/$name/run.log"
  rc=$control_rc
  [[ $name == repair ]] && rc=$repair_rc
  print -- "$name rc=$rc tasks=$(grep -a -c 'audtask-dispatch' "$log" 2>/dev/null || true) "\
    "phases=$(grep -a -c '^\[phase\]' "$log" 2>/dev/null || true) "\
    "pretitle=$(grep -a -c 'vi_width=640 .*origin=0x0066A500' "$log" 2>/dev/null || true) "\
    "title=$(grep -a -c 'vi_width=1024 .*origin=0x00790400' "$log" 2>/dev/null || true) "\
    "hangar=$(grep -a -c 'vi_width=512 .*origin=0x006AB400' "$log" 2>/dev/null || true) "\
    "route=$(grep -a -c '^\[m5-route-state\]' "$log" 2>/dev/null || true) "\
    "candidate=$(grep -a -c '^\[m5-route-candidate\]' "$log" 2>/dev/null || true) "\
    "crash=$(grep -a -c '^\[CRASH\]' "$log" 2>/dev/null || true) "\
    "abort=$(grep -a -c '^\[ABORT\]' "$log" 2>/dev/null || true)"
done

(( control_rc == 0 && repair_rc == 0 ))
