#!/bin/zsh
# s7700 G5h re-hold of the s6908 cutscene pool floor on the AT THE MOVIES playlist (the outro proxy; s6909 route, s6792 press list,
# 16:9 menu gate w1592), post-G6c binary, owner recipe FPS60 dd$DD 16:9, STANDINS=0 (as s7698). ROGUESQ_DD_POOLMIN_TOG=1 = old cap on odd
# mach seconds (same-run control). Private folder scratch/s6908/wd (own save copy; owner save in build/saves untouched, cmp-checked).
# Score with LV=-1: tools/s7698_kept_split.py $O -1 ; s7698_flip_pairs.py $O -1 ; s7698_poolmin_phase.py $O -1 ; s7699_arm_sheet.py $O -1 out.png
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 2; }
DD=${DD:-2}; EV=${EV:-30}; O=${O:-$PWD/scratch/s7700/movd$DD}; SV=build/saves/rs64.n64.us.1.0.bin; mkdir -p $O/fb
cp -p $SV $O/save_before.bin || exit 3
AS=${AS:-16:9}; GW=${GW:-1592}   # 21:9: AS=21:9 GW=2048 (s7039 gate)
# s7701: at 21:9 the playlist renders 768 wide and RT64 skips that RDRAM write-back (SKIP_WILD_W), so FB_DUMP saw noise
# (690 dumps, 14 distinct). ALLOW_WILD_W=1 restores the dumps (688/690 distinct); diagnostic only, not owner mode. WILDW=0 opts out.
[[ $AS == 21:9 && ${WILDW:-1} == 1 ]] && export ROGUESQ_ALLOW_WILD_W=1
AP=$(sed -n "s/^port AP: //p" scratch/s6792/mov/press.txt | sed "s/13:w1024/13:w$GW/")
( cd scratch/s6908/wd && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT=$AP \
    ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=$DD ROGUESQ_ASPECT=$AS ROGUESQ_STANDINS=0 ROGUESQ_DD_POOLMIN_TOG=${TOG:-1} \
    ROGUESQ_G3E_TRACE=$O/g3e.txt ROGUESQ_FB_DUMP_DIR=$O/fb ROGUESQ_FB_DUMP_EVERY=$EV ./RogueSquadron64Recomp ) > $O/run.log 2>&1 &
P=$!; S=$(date +%s)
while (( $(date +%s) - S < ${SECS:-560} )); do sleep 5; kill -0 $P 2>/dev/null || break; done
a=1; kill -0 $P 2>/dev/null || a=0
kill -9 $P 2>/dev/null; wait 2>/dev/null
echo "tag=poolmin_movd$DD alive=$a crash=$(grep -a -c -E 'CRASH|SIGSEGV|SIGBUS|abort' $O/run.log) fb=$(ls $O/fb | wc -l | tr -d ' ') poolx=$(grep -a -c '\[poolx\]' $O/run.log)"
cmp -s $SV $O/save_before.bin && echo save-unchanged || { echo SAVE-CHANGED; exit 5; }
