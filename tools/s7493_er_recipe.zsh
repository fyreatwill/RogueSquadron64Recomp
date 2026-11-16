#!/bin/zsh
# s7493 class ER: RT64 writeback liveness = the s7492 EQ recipe + ROGUESQ_S7493_WBLIVE=1 (+ _CTL=${WBCTL:-3000}). Each arm also scores
# the last `[s7493] sum`: colour/depth writebacks by age (swaps since the RDP stream last set that image): age0/age1/age2(>=2)/never.
# v3 (s7493 run 3): exact image base from RT64 (rs64_s7493_base); v1 greatest-base and v2 youngest-covering lookups were artifacts / masked the CTL. CTL blacklists the image sets;
# WATCH=<hex phys,...> logs every writeback covering the seed addresses with its set age.
# Exit 0 = s7492 contract holds AND every arm: wb>0, ctl_armed=1, ctl_never>=1, color+depth age2=0 and never=0 (ctl row excluded).
# 4 = a stale (age>=2) or never-set writeback (H-wb-stale: read the `[s7493] wb ... age>=2|never` rows).
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
# XC=<a=b+c=d>: extra env appended to every arm (s7496).
# s7492 class EQ = the s7491 recipe with per-arm plant kinds: LV="<level>:<dd>:<kind> ..." (default "4:4:os_tq_head 15:8:os_rt64fb
# 1:4:os_tq_link"); ROGUESQ_S7491_MPLANT_KIND=<kind> restricts the plant to that kind, so each new EQ hook site gets its own
# positive control (`[s7480] plant DETECTED ... fn=<kind>`). Exit 0 = every arm: plant SET+DETECTED for its kind, the EQ kinds
# os_tq_link/os_tq_head called > 0, 0 os_* F/Urec/slack rows. os_rt64fb calls are reported (0 = renderToRAM wrote nothing).
# --- original s7491 header ---
# s7491 class EP: OS-call host stores through guest pointers (mesgqueue create/send/jam/recv + msg out, osCreateThread, cont
# init/query/read, save_read, OSIoMesg fill, osDpGetCounters) now call rs64_s7491_hst (upstream_compat.cpp), which routes marked bytes
# through rs64_s7475_store (fn=os_<kind>, pc=0xE00000xx). This recipe = the s7490 recipe with the zmemcpy plant REPLACED by
# ROGUESQ_S7491_MPLANT=${MPLANT_S:-20}: the first EP store into a live canary block (else, after +30 s, into any destination) is
# recorded as freed before routing -> MUST log `[s7480] plant DETECTED ... fn=os_*`. LV="<level>:<dd> ..." (default "4:4 15:8").
# Exit 0 = every arm: mplant SET + DETECTED fn=os_*, [s7491] sum with os_send and os_recv calls > 0, 0 os_* uaf-store/load F/Urec
# rows, 0 os_* slack-stores. 1 = an os_* F/Urec/slack hit (chase its row); 3 = control FAIL; harness rc wins.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7493_er}; R=$PWD/scratch/$n; mkdir -p $R; rm -f $R/quiet.done $R/void_*(N) $R/ok_*(N) $R/ring_*.txt(N)
C="ROGUESQ_S7475_CANARY=1+ROGUESQ_S7475_FILL=0+ROGUESQ_STORE_DIAG=1+ROGUESQ_S7475_PAD=16+ROGUESQ_S7480_UAF=1+ROGUESQ_S7475_BT=1+ROGUESQ_S7491_MPLANT=${MPLANT_S:-20}+ROGUESQ_S7484_UAFLOAD=1+ROGUESQ_S7493_WBLIVE=1+ROGUESQ_S7493_WBLIVE_CTL=${WBCTL:-3000}+ROGUESQ_S7493_WBLIVE_WATCH=${WBWATCH:-787810,B87810}${XC:++$XC}"
lv=(${=${LV:-4:1:os_rt64fb 15:8:os_rt64fb}}); arms=(); tags=(); typeset -A kd
for e in $lv; do
  l=${e%%:*}; r=${e#*:}; d=${r%%:*}; k=${r#*:}
  [[ $l == <0-18> && $d == <1-8> && $k == os_* ]] || { echo "$n bad LV entry '$e'"; exit 3; }
  s="${d}:l$l:ROGUESQ_FORCE_SAVE_MISSION=${l}+${C}+ROGUESQ_S7491_MPLANT_KIND=$k"; (( d >= 8 )) && s="$s+ROGUESQ_ASPECT=21:9"
  arms+=$s; tags+=l$l; kd[l$l]=$k
done
env R=$R HOLD=${HOLD:-220} DONE=quiet.done ARMS="${(j: :)arms}" zsh tools/g1e_owner_quiet_arms.zsh | tee $R/out.txt; rc=${pipestatus[1]}
(( rc == 2 )) && exit 2
sr=0
for a in $tags; do L=$R/log_$a.txt
  im=$(grep -a -c 'initMission\] call' $L 2>/dev/null)
  ms=$(grep -a '\[s7491\] mplant SET' $L 2>/dev/null | head -1); md=$(grep -a -c "\\[s7480\\] plant DETECTED .*fn=${kd[$a]}" $L 2>/dev/null)
  last=$(grep -a '\[s7491\] sum ' $L 2>/dev/null | tail -1)
  ns=$(print -r -- "$last" | sed -n 's/.* os_send=\([0-9]*\):.*/\1/p'); nr=$(print -r -- "$last" | sed -n 's/.* os_recv=\([0-9]*\):.*/\1/p')
  [[ -z $ns ]] && ns=0; [[ -z $nr ]] && nr=0
  tl=$(print -r -- "$last" | sed -n 's/.* os_tq_link=\([0-9]*\):.*/\1/p'); th=$(print -r -- "$last" | sed -n 's/.* os_tq_head=\([0-9]*\):.*/\1/p')
  fb=$(print -r -- "$last" | sed -n 's/.* os_rt64fb=\([0-9]*\):.*/\1/p'); [[ -z $tl ]] && tl=0; [[ -z $th ]] && th=0; [[ -z $fb ]] && fb=0
  uaf=$(grep -a -E '\[s7480\] uaf-store .*fn=os_' $L 2>/dev/null | grep -v ' PLANT$' | grep -a -c 'loc=[FR]')
  rows=$(grep -a '\[s7480\] uaf-store .*fn=os_' $L 2>/dev/null | grep -v -c ' PLANT$')
  tail_=$(grep -a -c '\[s7475\] slack-store .*fn=os_' $L 2>/dev/null)
  s80=$(grep -a '\[s7480\] sum ' $L 2>/dev/null | tail -1 | sed -n 's/.* loc_F=\([0-9]*\) .*loc_Urec=\([0-9]*\).*/F\1 Urec\2/p')
  echo "$n arm=$a initMission=$im mplant={${ms#*SET }} mplant_detected=$md kind=${kd[$a]} send=$ns recv=$nr tq_link=$tl tq_head=$th rt64fb=$fb os_uaf_rows=$rows os_FR=$uaf os_slack=$tail_ s7480=[$s80] last={$last}" | tee -a $R/out.txt
  (( ${#ms} == 0 || md == 0 || ns == 0 || nr == 0 || tl == 0 || th == 0 )) && sr=3; (( (uaf > 0 || tail_ > 0) && sr == 0 )) && sr=1
done
for a in $tags; do L=$R/log_$a.txt; q=$(grep -a '\[s7493\] sum ' $L 2>/dev/null | tail -1)
  g() { print -r -- "$q" | sed -n "s/.* $1=\([0-9]*\).*/\1/p" }
  wb=$(print -r -- "$q" | sed -n 's/.* wb=\([0-9]*\) .*/\1/p'); ca=$(g ctl_armed); cn=$(g ctl_never)
  c2=$(print -r -- "$q" | sed -n 's/.* color .* age2=\([0-9]*\) never=\([0-9]*\) depth .*/\1 \2/p'); d2=$(print -r -- "$q" | sed -n 's/.* depth .* age2=\([0-9]*\) never=\([0-9]*\) ctl.*/\1 \2/p')
  st=$(( ${${(z)c2}[1]:-0} + ${${(z)c2}[2]:-0} + ${${(z)d2}[1]:-0} + ${${(z)d2}[2]:-0} - ${cn:-0} ))
  echo "$n er arm=$a wb=${wb:-0} ctl_armed=${ca:-0} ctl_never=${cn:-0} stale_nonctl=$st {${q#*sum }}" | tee -a $R/out.txt
  (( ${wb:-0} == 0 || ${ca:-0} == 0 || ${cn:-0} == 0 )) && sr=3; (( st > 0 && sr == 0 )) && sr=4
done
echo "$n score=$sr" | tee -a $R/out.txt
(( rc != 0 )) && exit $rc
exit $sr
