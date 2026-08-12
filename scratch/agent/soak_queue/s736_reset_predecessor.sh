#!/bin/zsh
set -euo pipefail
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/soak_results/s736_reset_predecessor_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
cd "$ROOT/build"
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' zsh ../tools/probe.sh "$OUT" 300 2
grep -aq '\[e9-prov-reset-predecessor\]' "$OUT/run.log"
grep -aq '\[e9-prov-depth-summary\].*cap=1' "$OUT/run.log"
! grep -aq '\[CRASH\]' "$OUT/run.log"
