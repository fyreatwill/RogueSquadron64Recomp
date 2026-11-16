#!/bin/zsh
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
# s7472 class EB: guest-heap chain integrity (ROGUESQ_S7472_HEAPCHK=1) on the normal build, owner recipe, HOLD=${HOLD:-220}.
# LV="<level>:<dd> ..." (default "4:4 7:4 12:4 15:8"; s7473). dd>=8 arms run ROGUESQ_ASPECT=21:9, others the harness 16:9.
# The FIRST arm carries the planted control (ROGUESQ_S7472_HEAPCHK_PLANT=${PLANT_S:-60}; use PLANT_S=150 for an in-flight plant).
# Exit 0 = plant DETECTED on the first arm and 0 heap-bad outside it, 1 = heap-bad outside the plant,
# 3 = control FAIL (plant not detected / walker not armed / bad LV spec), harness rc wins.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7472_heapchk}; R=$PWD/scratch/$n; mkdir -p $R; rm -f $R/quiet.done $R/void_*(N) $R/ok_*(N) $R/ring_*.txt(N)
C="ROGUESQ_S7472_HEAPCHK=1"
lv=(${=${LV:-4:4 7:4 12:4 15:8}}); arms=(); tags=()
for e in $lv; do
  l=${e%%:*}; d=${e##*:}
  [[ $l == <0-18> && $d == <1-8> && $e == *:* ]] || { echo "$n bad LV entry '$e'"; exit 3; }
  s="${d}:l${l}:ROGUESQ_FORCE_SAVE_MISSION=${l}+${C}"
  (( d >= 8 )) && s="$s+ROGUESQ_ASPECT=21:9"
  (( ${#arms} == 0 )) && s="$s+ROGUESQ_S7472_HEAPCHK_PLANT=${PLANT_S:-60}"
  arms+=$s; tags+=l$l
done
env R=$R HOLD=${HOLD:-220} DONE=quiet.done ARMS="${(j: :)arms}" zsh tools/g1e_owner_quiet_arms.zsh | tee $R/out.txt; rc=${pipestatus[1]}
(( rc == 2 )) && exit 2
sr=0
for a in $tags; do L=$R/log_$a.txt
  im=$(grep -a -c 'initMission\] call' $L 2>/dev/null); armed=$(grep -a -c '\[s7472\] heapchk armed' $L 2>/dev/null)
  bad=$(grep -a '\[s7472\] heap-bad' $L 2>/dev/null | grep -v -c ' PLANT$'); pl=$(grep -a -c '\[s7472\] plant DETECTED' $L 2>/dev/null)
  # in-flight control: plant SET must come after the first initMission (line order)
  pln=$(grep -a -n '\[s7472\] plant SET' $L 2>/dev/null | head -1 | cut -d: -f1); imn=$(grep -a -n 'initMission\] call' $L 2>/dev/null | head -1 | cut -d: -f1)
  infl=0; [[ -n $pln && -n $imn ]] && (( pln > imn )) && infl=1
  last=$(grep -a '\[s7472\] chk ' $L 2>/dev/null | tail -1)
  echo "$n arm=$a initMission=$im armed=$armed heap_bad_nonplant=$bad plant_detected=$pl plant_inflight=$infl last={$last}" | tee -a $R/out.txt
  (( armed == 0 )) && sr=3; (( bad > 0 && sr == 0 )) && sr=1
  [[ $a == $tags[1] ]] && (( pl == 0 )) && sr=3
done
echo "$n score=$sr" | tee -a $R/out.txt
(( rc != 0 )) && exit $rc
exit $sr
