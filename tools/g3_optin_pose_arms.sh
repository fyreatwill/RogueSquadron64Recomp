#!/bin/zsh
# s6872 G3: lvl1 same-pose window captures per opt-in arm, one game at a time, for tools/g3_optin_diff.py. No-input flight is
# deterministic, so ROGUESQ_POSE_FREEZE stops the game at fixed pos.x crossings and each freeze gets a capture burst.
# usage: g3_optin_pose_arms.sh OUTDIR [arm ...]   arm = name=<env words, + for space>; FZ = rising x list.
#   dd1a/dd1b = same settings twice (cross-run noise floor). shift = dd1 frozen SHIFT units of x later (default 2): the positive
#   control, it must score far above the floor or a null from the opt-in arms says nothing.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 2
O=${1:?outdir}; shift; mkdir -p $O
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 4; }
REF=$PWD/scratch/agent/m6/s6468p_dd8_sheet/poseref.bin; [ -s $REF ] || exit 3
FZ=(${=FZ:-42.33 74.04 106.28}); MS=${MS:-15000}
ARMS=("$@"); (( $#ARMS )) || ARMS=(dd1a= dd1b= shift=SHIFTX dd2=ROGUESQ_DRAW_DISTANCE=2 dd4=ROGUESQ_DRAW_DISTANCE=4 \
  fps60=ROGUESQ_FPS60=1 fps60dd4=ROGUESQ_FPS60=1+ROGUESQ_DRAW_DISTANCE=4)
for a in $ARMS; do
  n=${a%%=*}; e=${a#*=}; e=${e//+/ }; d=0
  [ "$e" = SHIFTX ] && { e=; d=${SHIFT:-2}; }
  fz=$(python3 -c "import sys; print(','.join('%.2f' % (float(x) + $d) for x in sys.argv[1:]))" $FZ)
  T=s6872_$n; L=scratch/agent/m6/g1_lvl1$T/run.log; C=$O/$n; mkdir -p $C; rm -f $L
  env ROGUESQ_NO_PKILL=1 MISSION_WIDE_FLIGHT=0 TITLE_OPTIONAL=1 \
    XENV_EXTRA="$e ROGUESQ_POSE_LOCK=1 ROGUESQ_POSE_REF=$REF ROGUESQ_POSE_FREEZE=$fz:$MS ROGUESQ_DEBUG_WRITE=80003470:1:512:55 ROGUESQ_RAND_TRACE=$PWD/$C/rand.txt" \
    HOLD_S=${HOLD_S:-110} LEVEL=1 TAG_SUFFIX=$T zsh scratch/agent/g1_level_coverage_common.zsh > $C/harness.log 2>&1 &
  H=$!; c=0; k=0
  while kill -0 $H 2>/dev/null && (( k < $#FZ )); do
    if grep -aq "^\[posefreeze\] k=$k " $L 2>/dev/null; then
      sleep 1; P=$(pgrep -x RogueSquadron64Recomp | head -1); g=$(build/winctl find $P 2>/dev/null)
      for i in 1 2; do /usr/sbin/screencapture -x -o -l${g%% *} $C/f${k}_$i.png && c=$((c+1)); sleep 0.5; done
      k=$((k+1))
    fi
    sleep 0.1
  done
  wait $H; echo "$n env='$e' caps=$c $(tail -1 $C/harness.log | cut -c1-160)"
  grep -a '^\[posefreeze\]' $L | cut -c1-70
done
