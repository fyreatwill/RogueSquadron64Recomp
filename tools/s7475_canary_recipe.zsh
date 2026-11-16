#!/bin/zsh
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
# s7475 class ED: in-block tail-overrun canary (ROGUESQ_S7475_CANARY=1, upstream_compat.cpp s7475_*) + s7472 header walk,
# normal build, owner recipe, HOLD=${HOLD:-220}. LV="<level>:<dd> ..." (default "4:4 7:4 12:4 15:8"); dd>=8 arms run 21:9.
# The FIRST arm carries the planted control (ROGUESQ_S7475_CANARY_PLANT=${PLANT_S:-150}, in flight).
# Exit 0 = plant DETECTED on the first arm and 0 non-plant tail-hits, 1 = non-plant tail-hit(s),
# 3 = control FAIL (plant not detected / canary not armed / bad LV spec), harness rc wins.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7475_canary}; R=$PWD/scratch/$n; mkdir -p $R; rm -f $R/quiet.done $R/void_*(N) $R/ok_*(N) $R/ring_*.txt(N)
# FILL=0: the 0xA5 fill hangs boot (s7475: voice[1] state byte read from the 1-voice array slack); the store watch (STORE_DIAG) is the writer detector
C="ROGUESQ_S7475_CANARY=1+ROGUESQ_S7475_FILL=${FILL:-0}+ROGUESQ_STORE_DIAG=1+ROGUESQ_S7472_HEAPCHK=1${PAD:++ROGUESQ_S7475_PAD=$PAD}"  # s7479 class EG: PAD=16 gives zero-slack blocks a band
lv=(${=${LV:-4:4 7:4 12:4 15:8}}); arms=(); tags=()
for e in $lv; do
  l=${e%%:*}; d=${e##*:}
  [[ $l == <0-18> && $d == <1-8> && $e == *:* ]] || { echo "$n bad LV entry '$e'"; exit 3; }
  s="${d}:l${l}:ROGUESQ_FORCE_SAVE_MISSION=${l}+${C}"
  (( d >= 8 )) && s="$s+ROGUESQ_ASPECT=21:9"
  (( ${#arms} == 0 )) && s="$s+ROGUESQ_S7475_CANARY_PLANT=${PLANT_S:-150}"
  arms+=$s; tags+=l$l
done
env R=$R HOLD=${HOLD:-220} DONE=quiet.done ARMS="${(j: :)arms}" zsh tools/g1e_owner_quiet_arms.zsh | tee $R/out.txt; rc=${pipestatus[1]}
(( rc == 2 )) && exit 2
sr=0
for a in $tags; do L=$R/log_$a.txt
  im=$(grep -a -c 'initMission\] call' $L 2>/dev/null); armed=$(grep -a -c '\[s7475\] canary armed' $L 2>/dev/null)
  hit=$(grep -a '\[s7475\] tail-hit' $L 2>/dev/null | grep -v -c ' PLANT$'); pl=$(grep -a -c '\[s7475\] plant DETECTED' $L 2>/dev/null)
  hb=$(grep -a '\[s7472\] heap-bad' $L 2>/dev/null | grep -c .); ss=$(grep -a -c '\[s7475\] slack-store' $L 2>/dev/null); wc=$(grep -a -c '\[s7475\] watch-ctl PASS' $L 2>/dev/null)
  pln=$(grep -a -n '\[s7475\] plant SET' $L 2>/dev/null | head -1 | cut -d: -f1); imn=$(grep -a -n 'initMission\] call' $L 2>/dev/null | head -1 | cut -d: -f1)
  infl=0; [[ -n $pln && -n $imn ]] && (( pln > imn )) && infl=1
  last=$(grep -a '\[s7475\] sum ' $L 2>/dev/null | tail -1)
  pa=$(grep -a -c '\[s7479\] pad armed' $L 2>/dev/null)
  echo "$n arm=$a initMission=$im armed=$armed tail_hit_nonplant=$hit plant_detected=$pl plant_inflight=$infl heap_bad=$hb slack_store_pcs=$ss watch_ctl=$wc pad_armed=$pa last={$last}" | tee -a $R/out.txt
  (( armed == 0 || wc == 0 )) && sr=3; [[ -n $PAD && $PAD != 0 ]] && (( pa == 0 )) && sr=3; (( hit > 0 && sr == 0 )) && sr=1
  [[ $a == $tags[1] ]] && (( pl == 0 )) && sr=3
done
echo "$n score=$sr" | tee -a $R/out.txt
(( rc != 0 )) && exit $rc
exit $sr
