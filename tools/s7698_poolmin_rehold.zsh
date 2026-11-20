#!/bin/zsh
# s7698 G5h re-hold of the s6908 intro pool floor on the post-G6c binary. Route = s7696 (FORCE_SAVE_MISSION=$LV -> crawl -> intro
# cutscene -> flight), owner recipe FPS60 dd$DD 16:9, stand-ins OFF. ROGUESQ_DD_POOLMIN_TOG=1 puts the old per-level cutscene pool cap
# back on odd mach seconds (same-run control); fb dumps every $EV swaps; tools/s7698_poolmin_phase.py fits the 1 s toggle phase from
# dump mtimes and reports the lower-frame detail split by arm, inside vs outside the intro. Owner save read-only, cmp-checked.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 2; }
LV=${LV:-1}; DD=${DD:-4}; EV=${EV:-15}; O=${O:-$PWD/scratch/s7698/L${LV}d$DD}; SV=build/saves/rs64.n64.us.1.0.bin; mkdir -p $O/fb
cp -p $SV $O/save_before.bin || exit 3
AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start
( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FORCE_SAVE_MISSION=$LV ROGUESQ_FORCE_UNLOCK=$LV ROGUESQ_AUTOPILOT=$AP \
    ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=$DD ROGUESQ_ASPECT=16:9 ROGUESQ_STANDINS=0 ROGUESQ_DD_POOLMIN_TOG=${TOG:-1} \
    ROGUESQ_G3E_TRACE=$O/g3e.txt ROGUESQ_FB_DUMP_DIR=$O/fb ROGUESQ_FB_DUMP_EVERY=$EV ./RogueSquadron64Recomp ) > $O/run.log 2>&1 &
P=$!; S=$(date +%s)
while (( $(date +%s) - S < ${SECS:-170} )); do sleep 5; kill -0 $P 2>/dev/null || break; done
a=1; kill -0 $P 2>/dev/null || a=0
kill -9 $P 2>/dev/null; wait 2>/dev/null
echo "tag=poolmin_L${LV}d$DD alive=$a crash=$(grep -c -E 'CRASH|SIGSEGV|SIGBUS|abort' $O/run.log) fb=$(ls $O/fb | wc -l | tr -d ' ') poolx=$(grep -c '\[poolx\]' $O/run.log)"
cmp -s $SV $O/save_before.bin && echo save-unchanged || { echo SAVE-CHANGED; exit 5; }
