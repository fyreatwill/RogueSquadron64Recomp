#!/bin/zsh
set -u

ROOT="$(pwd)"
OUT="$ROOT/scratch/agent/soak_results/s4853_m5_descriptor"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 2

env \
  ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LLE_FORCE=1 \
  ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 \
  PROBE_PHASE_WIDTH=1024 \
  PROBE_PHASE_TIMEOUT=110 \
  PROBE_KEYS_FROM_PHASE=1 \
  PROBE_LEAVE_OK=1 \
  ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_M5_DESCRIPTOR=1 \
  ROGUESQ_LOG_M5_ROUTE_ORDER=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 \
  ROGUESQ_AUDIO_UCODE=1 \
  ./RogueSquadron64Recomp >"$OUT/port.log" 2>&1 &
pid=$!

sleep 180
kill -KILL "$pid" 2>/dev/null || true
wait "$pid" 2>/dev/null || true

{
  echo 'M5 descriptor/task-contract qualification'
  printf 'title=%s hangar=%s descriptor_control=%s descriptor_start=%s descriptor_compare=%s descriptor_yield=%s route_sp_enter=%s route_sp_return=%s action=%s pcm=%s crash=%s abort=%s\n' \
    "$(grep -a -c '^\[phase\].*vi_width=1024 .*origin=0x00790400' "$OUT/port.log" || true)" \
    "$(grep -a -c '^\[phase\].*vi_width=512 .*origin=0x006AB400' "$OUT/port.log" || true)" \
    "$(grep -a -c '^\[m5-descriptor-control\]' "$OUT/port.log" || true)" \
    "$(grep -a -c '^\[m5-descriptor-start\]' "$OUT/port.log" || true)" \
    "$(grep -a -c '^\[m5-descriptor-compare\]' "$OUT/port.log" || true)" \
    "$(grep -a -c '^\[m5-descriptor-yield\]' "$OUT/port.log" || true)" \
    "$(grep -a -c 'edge=sp-complete-enter' "$OUT/port.log" || true)" \
    "$(grep -a -c 'edge=sp-complete-return' "$OUT/port.log" || true)" \
    "$(grep -a -c 'edge=action-dequeue' "$OUT/port.log" || true)" \
    "$(grep -a -c 'pcm.*nonzero\|pcm.*nz=' "$OUT/port.log" || true)" \
    "$(grep -a -c '^\[CRASH\]' "$OUT/port.log" || true)" \
    "$(grep -a -c '^\[ABORT\]' "$OUT/port.log" || true)"
  grep -aE '^\[(m5-descriptor|m5-route-order|phase|pcm|CRASH|ABORT)' "$OUT/port.log" | tail -300
} | tee "$OUT/verdict.txt"
