#!/bin/zsh
# s6872 G3: lvl1 same-pose window captures per opt-in arm, one game at a time, for tools/g3_optin_diff.py. No-input flight is
# deterministic, so ROGUESQ_POSE_FREEZE stops the game at fixed pos.x crossings and each freeze gets a capture burst.
# usage: g3_optin_pose_arms.sh OUTDIR [arm ...]   arm = name=<env words, + for space>; FZ = rising x list.
# s6873: PIN=1 pins the tick dt (arm with FPS60: 1/60, else 1/30; a word starting u in the arm name stays unpinned). Every arm
#   logs per-tick dt, player pos and hp on the 800FA730 row. Real dt varies per run, so without the pin no two runs share a path.
#   NOREF=1 keeps the zeroed input but drops the attitude pin (POSE_REF, written on the pad thread once per poll, not per tick).
#   LOCK=0 is NOT no-input: POSE_LOCK is what zeroes the pad, without it the harness autopilot keys run on the wall clock.
#   XMEM = extra dump specs. s7312: an FZ entry <x freezes on a falling x crossing (SHIFT moves it further down).
#   s6876: LEVEL = mission level (default 1). The poseref is lvl1 only, so other levels need NOREF=1.
#   s6879: an arm with ROGUESQ_ASPECT takes the wide route (WIDE_ROUTE=1, MISSION_WIDTH = the width main.cpp derives from 448 * w/h), and DEBUG_WRITE arms on
#   that width: flight is never 512 there, so with :512: POSE_FREEZE and RAND_TRACE silently stay off (caps=0, no rand.txt).
#   dd1a/dd1b = same settings twice (cross-run noise floor). shift = dd1 frozen SHIFT units of x later (default 2): the positive
#   control, it must score far above the floor or a null from the opt-in arms says nothing.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 2
O=${1:?outdir}; shift; [[ $O == /* ]] && { echo "OUTDIR must be repo-relative (RAND_TRACE is \$PWD/\$O/..., s7312)"; exit 2; }; mkdir -p $O
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 4; }
# s6934: same gate as g1e_owner_quiet_arms.zsh; these arms take the window route and key focus, so a human at the machine stops them (rc 2, nothing launched).
i=$(ioreg -c IOHIDSystem | awk '/HIDIdleTime/{printf "%d\n",$NF/1e9; exit}'); (( i < ${IDLE_MIN:-120} )) && { echo "human active idle=$i"; exit 2; }
. tools/rs64_game_pid.zsh  # s7313: one-game PID guard (see that file)
LV=${LEVEL:-1}
REF=$PWD/scratch/agent/m6/s6468p_dd8_sheet/poseref.bin; [ -s $REF ] || [ -n "${NOREF:-}" ] || exit 3
FZ=(${=FZ:-42.33 74.04 106.28}); MS=${MS:-15000}
ARMS=("$@"); (( $#ARMS )) || ARMS=(dd1a= dd1b= shift=SHIFTX dd2=ROGUESQ_DRAW_DISTANCE=2 dd4=ROGUESQ_DRAW_DISTANCE=4 \
  fps60=ROGUESQ_FPS60=1 fps60dd4=ROGUESQ_FPS60=1+ROGUESQ_DRAW_DISTANCE=4)
for a in $ARMS; do
  n=${a%%=*}; e=${a#*=}; e=${e//+/ }; d=0
  [ "$e" = SHIFTX ] && { e=; d=${SHIFT:-2}; }
  fz=$(python3 -c "import sys; print(','.join(('<%.2f' % (float(x[1:]) - $d)) if x[0] == '<' else ('%.2f' % (float(x) + $d)) for x in sys.argv[1:]))" $FZ)
  pk=; if [ "${PIN:-0}" = 1 ] && [ "${n[1]}" != u ]; then
    case "$e" in *FPS60*) pk="ROGUESQ_XTRACE_POKE=800FA730:29:30:3c888889";; *) pk="ROGUESQ_XTRACE_POKE=800FA730:29:30:3d088889";; esac
  fi
  wd=(); dw=512; case "$e" in *ROGUESQ_ASPECT=16:9*) dw=796;; *ROGUESQ_ASPECT=21:9*) dw=1024;; esac; (( dw != 512 )) && wd=(WIDE_ROUTE=1 MISSION_WIDTH=$dw)
  rf="ROGUESQ_POSE_REF=$REF"; [ -n "${NOREF:-}" ] && rf=
  rs64_no_foreign_game ${FOREIGN_WAIT:-60} || { echo "$n VOID: foreign game alive before launch"; exit 5; }
  T=${TAGP:-s6872}_$n; L=scratch/agent/m6/g1_lvl$LV$T/run.log; C=$O/$n; mkdir -p $C; rm -f $L
  env ROGUESQ_NO_PKILL=1 MISSION_WIDE_FLIGHT=0 TITLE_OPTIONAL=1 $wd \
    XENV_EXTRA="$e $pk ROGUESQ_XTRACE_MEM=800FA730:29:30:1,800FA730:0:80137DC0:3,800FA730:0:80137E7C:1${XMEM:+,$XMEM} ROGUESQ_POSE_LOCK=${LOCK:-1} $rf ROGUESQ_POSE_FREEZE=$fz:$MS ROGUESQ_DEBUG_WRITE=80003470:1:$dw:55 ROGUESQ_RAND_TRACE=$PWD/$C/rand.txt" \
    HOLD_S=${HOLD_S:-110} LEVEL=$LV TAG_SUFFIX=$T zsh scratch/agent/g1_level_coverage_common.zsh > $C/harness.log 2>&1 &
  H=$!; c=0; k=0; mg=0
  while kill -0 $H 2>/dev/null && (( k < $#FZ )); do
    if grep -aq "^\[posefreeze\] k=$k " $L 2>/dev/null; then
      sleep 1; P=$(rs64_game_pid); g=$(build/winctl find $P 2>/dev/null)
      # s7313: CAPN captures 0.5 s apart (default 2); with != 1 game alive the capture is skipped and counted in multi=.
      if [ -n "$P" ] && [ -n "$g" ]; then for i in $(seq 1 ${CAPN:-2}); do /usr/sbin/screencapture -x -o -l${g%% *} $C/f${k}_$i.png && c=$((c+1)); sleep 0.5; done
      else mg=$((mg+1)); echo "$n k=$k capture SKIPPED: pid='$P' (not exactly one game alive)"; fi
      k=$((k+1))
    fi
    sleep 0.1
  done
  wait $H; echo "$n env='$e' caps=$c multi=$mg $(tail -1 $C/harness.log | cut -c1-160)"
  grep -a '^\[posefreeze\]' $L | cut -c1-70
done
