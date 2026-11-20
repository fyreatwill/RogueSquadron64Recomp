#!/bin/zsh
# SOAK_NEEDS_IDLE=300
# s7705 G1d 21:9 item 25 remainder: does anything OTHER than the boot cinematic read a colour buffer whose write-back RT64 skips
# (SKIP_WILD_W) - in a mission intro cutscene or 21:9 flight? Owner 21:9 recipe (FPS60 dd2 ASPECT=21:9), forced level LV (default 1)
# route: boot cinematic -> crawl -> intro cutscene -> flight. ROGUESQ_S7702_FBREAD=1 (texture + RSP DMA census, ctl_live control);
# the boot-cinematic 768 hits in the same run are the positive control. Joined offline by tools/s7705_join.py.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 2; }
LV=${LV:-1}; O=${O:-$PWD/scratch/s7705/L$LV}; SV=build/saves/rs64.n64.us.1.0.bin; mkdir -p $O
cp -p $SV $O/save_before.bin || exit 3
rm -f build/rs64_s7702.log
AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start
( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FORCE_SAVE_MISSION=$LV ROGUESQ_FORCE_UNLOCK=$LV ROGUESQ_AUTOPILOT=$AP \
    ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=${DD:-2} ROGUESQ_ASPECT=${AS:-21:9} ROGUESQ_S7702_FBREAD=1 ./RogueSquadron64Recomp ) > $O/run.log 2>&1 &
P=$!; S=$(date +%s)
while (( $(date +%s) - S < ${SECS:-220} )); do
  sleep 5; e=$(( $(date +%s) - S )); kill -0 $P 2>/dev/null || break
  g=$(build/winctl find $P 2>/dev/null) && /usr/sbin/screencapture -x -o -l${g%% *} $O/w_$(printf %03d $e).png
done
a=1; kill -0 $P 2>/dev/null || a=0
kill -9 $P 2>/dev/null; wait 2>/dev/null
cp build/rs64_s7702.log $O/s7702.log 2>/dev/null
echo "tag=fbread_L${LV}_${AS:-21:9} alive=$a crash=$(grep -a -c -E 'CRASH|SIGSEGV|SIGBUS|abort' $O/run.log) skipw=$(grep -a -c 'SKIP_WILD_W #' $O/run.log) $(head -1 $O/s7702.log 2>/dev/null | tr ' ' '\n' | grep ctl_live)"
python3 tools/s7705_join.py $O | tail -1
cmp -s $SV $O/save_before.bin && echo save-unchanged || { echo SAVE-CHANGED; exit 5; }
