#!/bin/zsh
# s6515: pinned dd1/dd4 span-reject predicate split. One build, both arms.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 2
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo "SCREEN LOCKED"; exit 4; }
BASE="scratch/agent/m6/s6515_span_predicate"
mkdir -p "$BASE"
REF="$PWD/scratch/agent/m6/s6468p_dd8_sheet/poseref.bin"
[ -s "$REF" ] || { echo "no poseref"; exit 3; }
run_arm() {
  local tag="$1" extra="$2"
  env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 MISSION_WIDE_FLIGHT=0 TITLE_OPTIONAL=1 \
    XENV_EXTRA="$extra ROGUESQ_POSE_LOCK=1 ROGUESQ_POSE_PIN_POSITION=1 ROGUESQ_POSE_REF=$REF ROGUESQ_FORFACE_LOG=1" \
    HOLD_S=150 LEVEL=1 TAG_SUFFIX="s6515_${tag}" \
    zsh scratch/agent/g1_level_coverage_common.zsh > "$BASE/${tag}.runner.log" 2>&1 &
  pids+=( $! )
}
rc=0; pids=()
run_arm dd1 "ROGUESQ_DRAW_DISTANCE=1"
run_arm dd4 "ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=4"
for p in $pids; do wait "$p" || rc=1; done
echo "arms_rc=$rc"
exit $rc
