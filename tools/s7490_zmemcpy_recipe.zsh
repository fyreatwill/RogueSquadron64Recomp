#!/bin/zsh
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
# s7490 class EO: the live zmemcpy is the HOST body (upstream_compat.cpp; RECOMP_FUNC is weak on clang, the hooked generated body is
# dead), so guest memcpy stores/loads bypassed the EB/EH/EI watches. s7490 routes each marked byte through rs64_s7475_store /
# rs64_s7484_load (fn=zmemcpy_host). This recipe = the s7484 recipe (canary + UAF-store + UAF-load) with the store plant REPLACED by
# ROGUESQ_S7490_ZPLANT=${ZPLANT_S:-20} (a live block a host memcpy is about to write is recorded as freed BEFORE the copy) -> the
# copy MUST log `[s7480] plant DETECTED ... fn=zmemcpy_host`. LV="<level>:<dd> ..." (default "4:4 15:8"), HOLD=${HOLD:-220}.
# Exit 0 = every arm: zplant SET + DETECTED fn=zmemcpy_host, calls>0, wmark>0, zmemcpy_host F/Urec hits = 0, zmemcpy_host tail-hits = 0;
# s7490b: PatchesLib bodies (fn=rs64_find_body / rs64_seed_body / isCinematicActive, RS64_S7490_PST/PLD) are scored the same way.
# 1 = a zmemcpy_host or patch-body F/Urec/tail hit (chase its row); 3 = control FAIL; harness rc wins.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7490_zmemcpy}; R=$PWD/scratch/$n; mkdir -p $R; rm -f $R/quiet.done $R/void_*(N) $R/ok_*(N) $R/ring_*.txt(N)
C="ROGUESQ_S7475_CANARY=1+ROGUESQ_S7475_FILL=0+ROGUESQ_STORE_DIAG=1+ROGUESQ_S7475_PAD=16+ROGUESQ_S7480_UAF=1+ROGUESQ_S7475_BT=1+ROGUESQ_S7490_ZPLANT=${ZPLANT_S:-20}+ROGUESQ_S7484_UAFLOAD=1"
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
  zs=$(grep -a -c '\[s7490\] zplant SET' $L 2>/dev/null); zd=$(grep -a -c '\[s7480\] plant DETECTED .*fn=zmemcpy_host' $L 2>/dev/null)
  last=$(grep -a '\[s7490\] sum ' $L 2>/dev/null | tail -1)
  calls=$(print -r -- "$last" | sed -n 's/.* calls=\([0-9]*\).*/\1/p'); wm=$(print -r -- "$last" | sed -n 's/.* wmark=\([0-9]*\).*/\1/p')
  rm_=$(print -r -- "$last" | sed -n 's/.* rmark=\([0-9]*\).*/\1/p'); hc=$(print -r -- "$last" | sed -n 's/.* heap_calls=\([0-9]*\).*/\1/p')
  [[ -z $calls ]] && { calls=0; wm=0; rm_=0; hc=0; }
  zuaf=$(grep -a -E '\[s7480\] uaf-store .*fn=(zmemcpy_host|rs64_find_body|rs64_seed_body|isCinematicActive)' $L 2>/dev/null | grep -v ' PLANT$' | grep -a -c 'loc=[FR]')
  zrows=$(grep -a '\[s7480\] uaf-store .*fn=zmemcpy_host' $L 2>/dev/null | grep -v -c ' PLANT$')
  zld=$(grep -a -E '\[s7484\] uaf-load .*fn=(zmemcpy_host|rs64_find_body|rs64_seed_body|isCinematicActive)' $L 2>/dev/null | grep -a -c 'loc=[FR]')
  ztail=$(grep -a -E -c '\[s7475\] slack-store .*fn=(zmemcpy_host|rs64_find_body|rs64_seed_body)' $L 2>/dev/null)
  s80=$(grep -a '\[s7480\] sum ' $L 2>/dev/null | tail -1 | sed -n 's/.* loc_F=\([0-9]*\) .*loc_Urec=\([0-9]*\).*/F\1 Urec\2/p')
  echo "$n arm=$a initMission=$im zplant_set=$zs zplant_detected=$zd calls=$calls heap_calls=$hc wmark=$wm rmark=$rm_ zmem_uaf_rows=$zrows zmem_FR=$zuaf zmem_load_FR=$zld zmem_tail=$ztail s7480=[$s80] last={$last}" | tee -a $R/out.txt
  (( zs == 0 || zd == 0 || calls == 0 || wm == 0 )) && sr=3; (( (zuaf > 0 || zld > 0 || ztail > 0) && sr == 0 )) && sr=1
done
echo "$n score=$sr" | tee -a $R/out.txt
(( rc != 0 )) && exit $rc
exit $sr
