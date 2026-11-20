#!/bin/zsh
# s7696 G5h x G6c: do far-object stand-ins run, and look right, inside a mission intro cutscene?
# Route: FORCE_SAVE_MISSION=$LV (default 5) -> crawl -> in-level intro cutscene -> flight, owner recipe FPS60 dd4 16:9.
# ROGUESQ_STANDINS=frame alternates stand-ins per submit call; ROGUESQ_STANDINS_DUMP=c<a>:<b>:<n> anchors the fb dump windows on the
# first cutscene-byte rising edge (0x80130B39), so window 1 = same-run on/off pairs inside the cutscene, window 2 = forced-off control.
# [standins-s] cut=/cutadded= split the per-second tallies; [standins-cut] logs the edges. Owner save read-only, cmp-checked.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 2; }
LV=${LV:-5}; O=${O:-$PWD/scratch/s7696/L$LV}; SV=build/saves/rs64.n64.us.1.0.bin; mkdir -p $O/fb
cp -p $SV $O/save_before.bin || exit 3
AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start
( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FORCE_SAVE_MISSION=$LV ROGUESQ_FORCE_UNLOCK=$LV ROGUESQ_AUTOPILOT=$AP \
    ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=${DD:-4} ROGUESQ_ASPECT=16:9 ROGUESQ_STANDINS=frame ROGUESQ_STANDINS_LOG=1 \
    ROGUESQ_STANDINS_DUMP=${DUMP:-c4:12:60} ROGUESQ_FB_DUMP_DIR=$O/fb ./RogueSquadron64Recomp ) > $O/run.log 2>&1 &
P=$!; S=$(date +%s)
while (( $(date +%s) - S < ${SECS:-200} )); do
  sleep 5; e=$(( $(date +%s) - S )); kill -0 $P 2>/dev/null || break
  g=$(build/winctl find $P 2>/dev/null) && /usr/sbin/screencapture -x -o -l${g%% *} $O/w_$(printf %03d $e).png
done
a=1; kill -0 $P 2>/dev/null || a=0
kill -9 $P 2>/dev/null; wait 2>/dev/null
# H-absent score: hook calls ([standins-pre] lines) between the level's cineBody intro call and the stand-in rebuild must be 0, and
# flight seconds after it must show calls>=50 (positive control).
SC=$(awk -v lv=$LV 'BEGIN{c=0} /\[cineBody\] call#/ && $0 ~ ("a0=0x0*" sprintf("%X",lv) " ") {c=NR} /\[standins\] [0-9]+ objects/ && !r {r=NR}
  /\[standins-pre\]/ { if (c && !r) pb++; else if (r) { split($2,a,"="); if (a[2]>=50) fl++ } }
  END{printf "cine_line=%d rebuild_line=%d pre_in_cine=%d flight_secs_ge50=%d", c, r, pb, fl}' $O/run.log)
echo "tag=cut_L$LV alive=$a crash=$(grep -c -E 'CRASH|SIGSEGV|SIGBUS|abort' $O/run.log) fb=$(ls $O/fb | wc -l | tr -d ' ') $SC"
cmp -s $SV $O/save_before.bin && echo save-unchanged || { echo SAVE-CHANGED; exit 5; }
