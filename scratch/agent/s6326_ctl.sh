#!/bin/zsh
# SOAK_TIMEOUT=600
# s6325 G3c(a): radius fade at 0x8004B910 (centre cam*0.5). Arms dd3: nofade(+maxr log via R=1000,1001), R18-26, R10-26, test02 control.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 2
BASE="scratch/agent/m6/s6326_g3c"
mkdir -p "$BASE"
rc=0
for spec in "ctl|ROGUESQ_EDGE_FADE_R=0,1"; do
  tag="${spec%%|*}"; extra="${spec#*|}"
  env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' \
    XENV_EXTRA="ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 $extra ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1" HOLD_S=70 LEVEL=1 \
    TAG_SUFFIX="s6326_${tag}" zsh scratch/agent/g1_level_coverage_common.zsh > "$BASE/${tag}.runner.log" 2>&1 || rc=1
done
exit $rc
