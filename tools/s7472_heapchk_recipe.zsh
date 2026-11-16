#!/bin/zsh
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
# s7472 class EB: guest-heap chain integrity (ROGUESQ_S7472_HEAPCHK=1) on the normal build, owner recipe, HOLD=${HOLD:-220}.
# Arms: L4 dd4 16:9 (+plant at 60 s), L7 dd4, L12 dd4, L15 dd8 21:9. Exit 0 = plant DETECTED on l4 and 0 heap-bad outside it,
# 1 = heap-bad outside the plant, 3 = control FAIL (plant not detected), harness rc wins.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7472_heapchk}; R=$PWD/scratch/$n; mkdir -p $R; rm -f $R/quiet.done $R/void_*(N) $R/ok_*(N) $R/ring_*.txt(N)
C="ROGUESQ_S7472_HEAPCHK=1"
env R=$R HOLD=${HOLD:-220} DONE=quiet.done ARMS="4:l4:ROGUESQ_FORCE_SAVE_MISSION=4+$C+ROGUESQ_S7472_HEAPCHK_PLANT=${PLANT_S:-60} 4:l7:ROGUESQ_FORCE_SAVE_MISSION=7+$C 4:l12:ROGUESQ_FORCE_SAVE_MISSION=12+$C 8:l15:ROGUESQ_FORCE_SAVE_MISSION=15+ROGUESQ_ASPECT=21:9+$C" zsh tools/g1e_owner_quiet_arms.zsh | tee $R/out.txt; rc=${pipestatus[1]}
(( rc == 2 )) && exit 2
sr=0
for a in l4 l7 l12 l15; do L=$R/log_$a.txt
  im=$(grep -a -c 'initMission\] call' $L 2>/dev/null); armed=$(grep -a -c '\[s7472\] heapchk armed' $L 2>/dev/null)
  bad=$(grep -a '\[s7472\] heap-bad' $L 2>/dev/null | grep -v -c ' PLANT$'); pl=$(grep -a -c '\[s7472\] plant DETECTED' $L 2>/dev/null)
  last=$(grep -a '\[s7472\] chk ' $L 2>/dev/null | tail -1)
  echo "$n arm=$a initMission=$im armed=$armed heap_bad_nonplant=$bad plant_detected=$pl last={$last}"
  (( armed == 0 )) && sr=3; (( bad > 0 && sr == 0 )) && sr=1
  [[ $a == l4 ]] && (( pl == 0 )) && sr=3
done
echo "$n score=$sr"
(( rc != 0 )) && exit $rc
exit $sr
