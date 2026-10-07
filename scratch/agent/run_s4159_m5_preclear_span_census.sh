#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4159_m5_preclear_span_census"
mkdir -p "$OUT"
PRESS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'
cd "$ROOT/build" || exit 2
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUDIO_UCODE=1 \
  ROGUESQ_AUTOPILOT="$PRESS" ROGUESQ_AUTOPILOT_STOP_WIDTH=512 \
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_HOST_WRITE=1 \
  ROGUESQ_LOG_M5_SOURCE_WRITER=1 ROGUESQ_LOG_M5_PRECLEAR=1 \
  ROGUESQ_LOG_M5_PRECLEAR_SPAN=1 \
  ROGUESQ_LOG_M5_WRITER_PARITY=1 \
  ROGUESQ_LOG_M5_PRECLEAR_NONSCALAR=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 \
  ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1 &
pid=$!
trap 'kill -KILL "$pid" 2>/dev/null || true' EXIT INT TERM
for tick in {1..360}; do
  kill -0 "$pid" 2>/dev/null || break
  sleep 0.25
done
kill -KILL "$pid" 2>/dev/null || true
wait "$pid" 2>/dev/null || true
title=0
hangar=0
control=0
non_scalar_control=0
grep -aq '\[phase\].*width=1024.*origin=0x00790400' "$OUT/port.log" && title=1
grep -aq '\[phase\].*width=512.*origin=0x006AB400' "$OUT/port.log" && hangar=1
grep -aq '\[m5-host-write-api-control\]' "$OUT/port.log" && control=1
grep -aq '\[m5-nonscalar-control\]' "$OUT/port.log" && non_scalar_control=1
printf 'control=%s non_scalar_control=%s title=%s hangar=%s\n' "$control" "$non_scalar_control" "$title" "$hangar" > "$OUT/verdict.txt"
(( control && non_scalar_control && title && hangar ))
