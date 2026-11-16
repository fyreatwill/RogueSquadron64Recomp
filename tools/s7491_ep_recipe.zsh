#!/bin/zsh
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
# s7491 class EP: OS-call host stores through guest pointers (mesgqueue create/send/jam/recv + msg out, osCreateThread, cont
# init/query/read, save_read, OSIoMesg fill, osDpGetCounters) now call rs64_s7491_hst (upstream_compat.cpp), which routes marked bytes
# through rs64_s7475_store (fn=os_<kind>, pc=0xE00000xx). This recipe = the s7490 recipe with the zmemcpy plant REPLACED by
# ROGUESQ_S7491_MPLANT=${MPLANT_S:-20}: the first EP store into a live canary block (else, after +30 s, into any destination) is
# recorded as freed before routing -> MUST log `[s7480] plant DETECTED ... fn=os_*`. LV="<level>:<dd> ..." (default "4:4 15:8").
# Exit 0 = every arm: mplant SET + DETECTED fn=os_*, [s7491] sum with os_send and os_recv calls > 0, 0 os_* uaf-store/load F/Urec
# rows, 0 os_* slack-stores. 1 = an os_* F/Urec/slack hit (chase its row); 3 = control FAIL; harness rc wins.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7491_ep}; R=$PWD/scratch/$n; mkdir -p $R; rm -f $R/quiet.done $R/void_*(N) $R/ok_*(N) $R/ring_*.txt(N)
C="ROGUESQ_S7475_CANARY=1+ROGUESQ_S7475_FILL=0+ROGUESQ_STORE_DIAG=1+ROGUESQ_S7475_PAD=16+ROGUESQ_S7480_UAF=1+ROGUESQ_S7475_BT=1+ROGUESQ_S7491_MPLANT=${MPLANT_S:-20}+ROGUESQ_S7484_UAFLOAD=1"
lv=(${=${LV:-4:4 15:8}}); arms=(); tags=()
for e in $lv; do
  l=${e%%:*}; d=${e#*:}
  [[ $l == <0-18> && $d == <1-8> ]] || { echo "$n bad LV entry '$e'"; exit 3; }
  s="${d}:l$l:ROGUESQ_FORCE_SAVE_MISSION=${l}+${C}"; (( d >= 8 )) && s="$s+ROGUESQ_ASPECT=21:9"
  arms+=$s; tags+=l$l
done
env R=$R HOLD=${HOLD:-220} DONE=quiet.done ARMS="${(j: :)arms}" zsh tools/g1e_owner_quiet_arms.zsh | tee $R/out.txt; rc=${pipestatus[1]}
(( rc == 2 )) && exit 2
sr=0
for a in $tags; do L=$R/log_$a.txt
  im=$(grep -a -c 'initMission\] call' $L 2>/dev/null)
  ms=$(grep -a '\[s7491\] mplant SET' $L 2>/dev/null | head -1); md=$(grep -a -c '\[s7480\] plant DETECTED .*fn=os_' $L 2>/dev/null)
  last=$(grep -a '\[s7491\] sum ' $L 2>/dev/null | tail -1)
  ns=$(print -r -- "$last" | sed -n 's/.* os_send=\([0-9]*\):.*/\1/p'); nr=$(print -r -- "$last" | sed -n 's/.* os_recv=\([0-9]*\):.*/\1/p')
  [[ -z $ns ]] && ns=0; [[ -z $nr ]] && nr=0
  uaf=$(grep -a -E '\[s7480\] uaf-store .*fn=os_' $L 2>/dev/null | grep -v ' PLANT$' | grep -a -c 'loc=[FR]')
  rows=$(grep -a '\[s7480\] uaf-store .*fn=os_' $L 2>/dev/null | grep -v -c ' PLANT$')
  tail_=$(grep -a -c '\[s7475\] slack-store .*fn=os_' $L 2>/dev/null)
  s80=$(grep -a '\[s7480\] sum ' $L 2>/dev/null | tail -1 | sed -n 's/.* loc_F=\([0-9]*\) .*loc_Urec=\([0-9]*\).*/F\1 Urec\2/p')
  echo "$n arm=$a initMission=$im mplant={${ms#*SET }} mplant_detected=$md send=$ns recv=$nr os_uaf_rows=$rows os_FR=$uaf os_slack=$tail_ s7480=[$s80] last={$last}" | tee -a $R/out.txt
  (( ${#ms} == 0 || md == 0 || ns == 0 || nr == 0 )) && sr=3; (( (uaf > 0 || tail_ > 0) && sr == 0 )) && sr=1
done
echo "$n score=$sr" | tee -a $R/out.txt
(( rc != 0 )) && exit $rc
exit $sr
