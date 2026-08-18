#!/bin/zsh
# Repeat of s1929_cursor_attack.sh: same instrument, hunt the 180s #7/#8
# staller so mix-alive vs mix-dead vs song-loop can be read off cursor n
# after menu-entry siten=2. Crash-family (no entry 2) is UNEVALUABLE.
set -euo pipefail

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/soak_results/s1930_mix_during_spin_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
cd "$ROOT/build"

set +e
env \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_DISPATCH=1 \
  ROGUESQ_LOG_RDP_CONDITION=1 \
  ROGUESQ_LOG_RDP_ADVANCE=1 ROGUESQ_LOG_RDP_FULLSYNC=1 \
  ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_DL_SYNC2=1 \
  ROGUESQ_LOG_VI_ARGS=1 \
  ROGUESQ_LOG_VI_CALLERS=1 \
  ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_LOG_CIMG_RAW=1 \
  ROGUESQ_LOG_RS_MALLOC_DIAG=1 ROGUESQ_LOG_FS_SLOT=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' \
  zsh ../tools/probe.sh "$OUT" 300 2
RC=$?
echo "probe_rc=$RC out=$OUT"
exit $RC
