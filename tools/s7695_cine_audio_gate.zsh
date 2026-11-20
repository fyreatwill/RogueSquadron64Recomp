#!/bin/zsh
# s7695 regression gate for the two pre-mission fixes on the current binary, plus the G6c scene-gate question.
#  crawl arms (G2b, s6790): FORCE_SAVE_MISSION=5 -> Chapter II crawl at 32006 Hz; fix vs ROGUESQ_AI_DRAIN_FIXED=1 control
#    (the control MUST show ~1000 empty-queue events or the instrument is blind). Run concurrently (autopilot keys are internal).
#  boot arms (G5d, s6903): plain boot, ScreenCaptureKit from boot, logo left share; with/without STANDINS at dd4, and
#    STANDINS_LOG=1 so a stand-in rebuild inside the cinematic (level 0x13) is visible. Sequential (capture is by process name).
# zsh note (s7695): `A[k]=$!` stored the literal "$!" here, so PIDs are plain scalars via eval.
# Owner save is read-only (NO_SAVE_WRITE) and only cmp-checked, never copied back. usage: s7695_cine_audio_gate.zsh [crawl|boot|all]
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 2; }
O=${O:-$PWD/scratch/s7695}; SV=build/saves/rs64.n64.us.1.0.bin; mkdir -p $O
cp -p $SV $O/save_before.bin || exit 3
OWN="ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9 ROGUESQ_STANDINS=1 ROGUESQ_STANDINS_LOG=1"
WHAT=${1:-all}
if [[ $WHAT == crawl || $WHAT == all ]]; then
  AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start
  for arm in fix ctl; do
    X=$OWN; [[ $arm == ctl ]] && X="$OWN ROGUESQ_AI_DRAIN_FIXED=1"
    mkdir -p $O/crawl_$arm
    ( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FORCE_SAVE_MISSION=5 ROGUESQ_FORCE_UNLOCK=5 ROGUESQ_AUTOPILOT=$AP \
        ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AI_UNDERRUN=1 ROGUESQ_AI_TRACE=$O/crawl_$arm/ai.txt ${=X} ./RogueSquadron64Recomp ) > $O/crawl_$arm/run.log 2>&1 &
    pid=$!; eval "PID_$arm=$pid"
  done
  S=$(date +%s)
  while (( $(date +%s) - S < ${SECS:-170} )); do
    sleep 5; e=$(( $(date +%s) - S ))
    for arm in fix ctl; do
      eval "p=\$PID_$arm"; kill -0 $p 2>/dev/null || continue
      (( e % 20 == 0 && e >= 60 )) && { g=$(build/winctl find $p 2>/dev/null) && /usr/sbin/screencapture -x -o -l${g%% *} $O/crawl_$arm/w_$(printf %03d $e).png; }
    done
  done
  for arm in fix ctl; do
    eval "p=\$PID_$arm"; a=1; kill -0 $p 2>/dev/null || a=0
    kill -9 $p 2>/dev/null
    echo "tag=crawl_$arm alive=$a crash=$(grep -c -E 'CRASH|SIGSEGV|SIGBUS|abort' $O/crawl_$arm/run.log)"
  done
  wait 2>/dev/null
fi
if [[ $WHAT == boot || $WHAT == all ]]; then
  for arm in sion sioff; do
    X=$OWN; [[ $arm == sioff ]] && X="ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9"
    ( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ${=X} ./RogueSquadron64Recomp ) > $O/boot_$arm.log 2>&1 &
    P=$!; sleep 1
    scratch/s6894/g5b_capture RogueSquadron64Recomp $O/boot_$arm.raw 320 240 0 73 > $O/cap_$arm.txt 2>&1 &
    c=$!; sleep 75
    a=1; kill -0 $P 2>/dev/null || a=0
    kill -9 $P 2>/dev/null; wait $c 2>/dev/null
    echo "tag=boot_$arm alive=$a crash=$(grep -c -E 'CRASH|SIGSEGV|SIGBUS|abort' $O/boot_$arm.log)"
  done
fi
cmp -s $SV $O/save_before.bin && echo save-unchanged || { echo SAVE-CHANGED; exit 5; }
