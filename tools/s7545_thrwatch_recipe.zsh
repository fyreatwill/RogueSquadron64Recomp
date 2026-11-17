#!/bin/zsh
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1200
# s7545 class GE runtime witness: every guest load/store into a live OSThread [t, t+0x1B0) (threads tracked at osCreateThread via
# the RS64_S7491 os_createthread hook; upstream_compat.cpp s7545_*), owner recipe, HOLD=${HOLD:-220}, LV default "1:1 4:4 12:4".
# Controls per arm: watch-ctl (frame counter 0x8011A890 marked: generated load AND store path live), plant (ROGUESQ_S7545_PLANT,
# siServiceThread+0x10 through the same entry points) DETECTED for L and S. Score per arm: port_field (off<0x30) rows by pc.
# Exit 0 = controls PASS and port_field=0; 1 = guest access(es) to port OSThread fields (rows name pc/fn/off); 3 = control FAIL.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7545_thrwatch}; R=$PWD/scratch/$n; mkdir -p $R; rm -f $R/quiet.done $R/void_*(N) $R/ok_*(N) $R/ring_*.txt(N)
C="ROGUESQ_S7545_THRWATCH=1+ROGUESQ_STORE_DIAG=1+ROGUESQ_S7545_PLANT=${PLANT_S:-150}"
lv=(${=${LV:-1:1 4:4 12:4}}); arms=(); tags=()
for e in $lv; do l=${e%%:*}; d=${e#*:}; tg=l$l
  s="${d}:${tg}:ROGUESQ_FORCE_SAVE_MISSION=${l}+${C}"; (( d >= 8 )) && s="$s+ROGUESQ_ASPECT=21:9"; arms+=$s; tags+=$tg; done
env R=$R HOLD=${HOLD:-220} DONE=quiet.done ARMS="${(j: :)arms}" zsh tools/g1e_owner_quiet_arms.zsh | tee $R/out.txt; rc=${pipestatus[1]}
(( rc == 2 )) && exit 2
sr=0
for a in $tags; do L=$R/log_$a.txt
  im=$(grep -a -c 'initMission\] call' $L 2>/dev/null); armed=$(grep -a -c '\[s7545\] thread watch armed' $L 2>/dev/null)
  nt=$(grep -a -c '\[s7545\] thr-add' $L 2>/dev/null)
  cl=$(grep -a -c '\[s7545\] watch-ctl PASS kind=L' $L 2>/dev/null); cs=$(grep -a -c '\[s7545\] watch-ctl PASS kind=S' $L 2>/dev/null)
  pl=$(grep -a -c '\[s7545\] plant DETECTED kind=L' $L 2>/dev/null); ps=$(grep -a -c '\[s7545\] plant DETECTED kind=S' $L 2>/dev/null)
  last=$(grep -a '\[s7545\] sum ' $L 2>/dev/null | tail -1)
  pf=$(print -r -- "$last" | sed -n 's/.* port_field=\([0-9]*\).*/\1/p'); [[ -z $pf ]] && pf=-1
  tl=$(print -r -- "$last" | sed -n 's/.* tail=\([0-9]*\).*/\1/p')
  echo "tag=s7545_$a initMission=$im armed=$armed threads=$nt ctl_L=$cl ctl_S=$cs plant_L=$pl plant_S=$ps port_field=$pf tail=$tl last={$last}" | tee -a $R/out.txt
  grep -a '\[s7545\] thr-access' $L 2>/dev/null | head -40 | tee -a $R/out.txt
  (( armed == 0 || nt == 0 || cl == 0 || cs == 0 || pl == 0 || ps == 0 || pf < 0 || im == 0 )) && sr=3; (( pf > 0 && sr == 0 )) && sr=1
done
echo "$n score=$sr" | tee -a $R/out.txt
(( rc != 0 )) && exit $rc
exit $sr
