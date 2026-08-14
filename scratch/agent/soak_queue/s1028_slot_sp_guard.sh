#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/soak_results/s1028_slot_sp_guard"
rm -rf "$OUT"
mkdir -p "$OUT"
cd "$ROOT" || exit 2
env ROGUESQ_LOG_SLOT_SP_GUARD=1 ROGUESQ_LOG_INPUT=1 ROGUESQ_LOG_DPC=1 \
  ROGUESQ_LOG_THREADS=1 ROGUESQ_LOG_INIT=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' \
  zsh tools/probe.sh "$OUT" 300 0.5
RC=$?
if grep -aq '\[CRASH\]' "$OUT/run.log" 2>/dev/null; then
  exit 3
fi
exit "$RC"
