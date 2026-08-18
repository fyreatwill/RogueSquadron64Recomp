#!/bin/zsh
# s1938: always-on [vi-cb-loop] + [vi-cb-recv1] enter/exit on a #7/#8 /
# menu-entry siten=2 staller. After post-#8 after n=N: loop n=N+1 and
# recv1-enter with no recv1-exit -> H-recv1-starved; recv1-exit and no
# recv2 n=N+1 -> H-post-recv1-stuck; no loop n=N+1 -> H-loop-missed.
# Crash / #6-dead = UNEVALUABLE — enqueue a second copy, do not babysit.
set -euo pipefail

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/soak_results/s1938_loop_recv1_$(date +%Y%m%d-%H%M%S)"
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
  ROGUESQ_LOG_AUDIOTICK_TRACE=1 \
  ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_LOG_CIMG_RAW=1 \
  ROGUESQ_LOG_RS_MALLOC_DIAG=1 ROGUESQ_LOG_FS_SLOT=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' \
  zsh ../tools/probe.sh "$OUT" 300 2
RC=$?
echo "probe_rc=$RC out=$OUT"
exit $RC
