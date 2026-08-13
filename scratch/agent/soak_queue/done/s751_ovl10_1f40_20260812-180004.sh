#!/bin/zsh
set -euo pipefail
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/soak_results/s751_ovl10_1f40_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
cd "$ROOT/build"
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 \
    ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_LOG_CIMG_RAW=1 ROGUESQ_LOG_DL_SYNC2=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
    PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' \
    zsh ../tools/probe.sh "$OUT" 300 2
LOG="$OUT/run.log"
# Same-run positive controls: clip + ovl18 + ovl10 dest + ovl10 0x1F40 handshake.
grep -aq '\[ovl-route\].*res=0x04' "$LOG"
grep -aq '\[ovl-route\].*res=0x18' "$LOG"
grep -aq '\[ovl-route\].*res=0x10 tgt=0x1F40' "$LOG"
grep -aq 'dl06=' "$LOG"
! grep -aq '\[CRASH\]' "$LOG"
echo "$OUT"
