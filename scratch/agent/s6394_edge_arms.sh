#!/bin/zsh
set -u
cd "$(git rev-parse --show-toplevel)" || exit 2
BASE="scratch/agent/m6/s6394_g3c_edge"
mkdir -p "$BASE"
run_arm() {
  local tag="$1" extra="$2" wide="$3"
  env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 MISSION_WIDE_FLIGHT="$wide" TITLE_ANY=1 \
    XENV_EXTRA="$extra ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1 ROGUESQ_LOG_F5_STORE_SHADOW=1" \
    HOLD_S=180 LEVEL=1 TAG_SUFFIX="s6394_${tag}" \
    zsh scratch/agent/g1_level_coverage_common.zsh > "$BASE/${tag}.runner.log" 2>&1 &
  pids+=( $! )
}
pids=()
run_arm retail "" 0
run_arm dd2 "ROGUESQ_DRAW_DISTANCE=2" 0
run_arm aspect "ROGUESQ_ASPECT=16:9" 1
run_arm combined "ROGUESQ_ASPECT=16:9 ROGUESQ_DRAW_DISTANCE=2" 1
rc=0
for p in $pids; do wait "$p" || rc=1; done
exit $rc
