#!/bin/zsh
# s7754: capture s7751 gfx-task snaps across the forced-mission route (hangar -> crawl -> intro cutscene -> flight) for the s7753
# RDP-output gate, with the periodic trigger ROGUESQ_S7751_EVERY=<N>:<max> (src/rsp/s7751_task_snap.cpp). One game at a time.
# usage: tools/s7754_capture_route.zsh <name> [env words...]   (LV default 4, SECS 220, EVERY 250:24). Owner save read-only, cmp-checked.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 2; }
N=${1:?name}; shift; LV=${LV:-4}; O=$PWD/scratch/s7754/$N; SV=build/saves/rs64.n64.us.1.0.bin; mkdir -p $O/snap
cp -p $SV $O/save_before.bin || exit 3
AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start
( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FORCE_SAVE_MISSION=$LV ROGUESQ_FORCE_UNLOCK=$LV ROGUESQ_AUTOPILOT=$AP \
    ROGUESQ_S7751_SNAP=$O/snap ROGUESQ_S7751_EVERY=${EVERY:-250:24} "$@" ./RogueSquadron64Recomp ) > $O/run.log 2>&1 &
P=$!; S=$(date +%s)
while (( $(date +%s) - S < ${SECS:-220} )); do
  sleep 10; e=$(( $(date +%s) - S )); kill -0 $P 2>/dev/null || break
  g=$(build/winctl find $P 2>/dev/null) && /usr/sbin/screencapture -x -o -l${g%% *} $O/w_$(printf %03d $e).png
done
a=1; kill -0 $P 2>/dev/null || a=0
kill -9 $P 2>/dev/null; wait 2>/dev/null
echo "tag=s7754_$N alive=$a crash=$(grep -c -E 'CRASH|SIGSEGV|SIGBUS|abort' $O/run.log) snaps=$(ls $O/snap | wc -l | tr -d ' ')"
cmp -s $SV $O/save_before.bin && echo save-unchanged || { echo SAVE-CHANGED; exit 5; }
