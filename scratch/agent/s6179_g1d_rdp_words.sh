#!/bin/zsh
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
D="scratch/agent/soak_results/s6179"
mkdir -p "$D/ctl-fb" "$D/wide-fb"
export FBD_EVERY_V=1
export HOLD_S=90 LEVEL=1

run_arm() {
  local arm=$1 aspect=$2 origin=$3 dump=$4 width=0
  [[ "$arm" == wide ]] && width=796
  env ROGUESQ_OSMEM_MB=12 ROGUESQ_ASPECT="$aspect" ROGUESQ_FB_WIDTH="$width" \
      ROGUESQ_FB_DUMP_VI=1 ROGUESQ_FB_DUMP_DIR="$dump" TITLE_ORIGIN="$origin" \
      MISSION_RE=ZZZ ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FORCE_UNLOCK=1 \
      ROGUESQ_FORCE_SAVE_MISSION=1 LEVEL=1 ROGUESQ_G1B=1 TAG="s6179_${arm}" \
      TAG_SUFFIX="_${arm}" BUILD="$PWD/build" HOLD=90 ROGUESQ_NO_PKILL=1 \
      XENV_EXTRA="ROGUESQ_LOG_VI_WRITERS=1 ROGUESQ_LOG_FB_ALLOC=1 ROGUESQ_LOG_RDP_ROUTE=1 ROGUESQ_LOG_RDP_WORDS=1 ROGUESQ_LOG_G1D_COPY=1 ROGUESQ_LOG_G1D_CMD=1 ROGUESQ_LOG_G1D_TARGET=1 ROGUESQ_LOG_G1D_TASK=1 ROGUESQ_LOG_G1D_INPUT=1 ROGUESQ_FB_DUMP_VI=1 ROGUESQ_FB_DUMP_DIR=$dump ROGUESQ_FB_WIDTH=$width" \
      zsh scratch/agent/g1_level_coverage_common.zsh >"$D/$arm.out" 2>&1 &
}

run_arm ctl 4:3 0x00B90400 "$D/ctl-fb"
p1=$!
run_arm wide 16:9 0x00B52200 "$D/wide-fb"
p2=$!
sleep 600
kill -KILL "$p1" "$p2" 2>/dev/null || true
wait "$p1" 2>/dev/null || true
wait "$p2" 2>/dev/null || true
