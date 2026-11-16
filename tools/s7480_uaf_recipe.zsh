#!/bin/zsh
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
# s7480 class EH: guest stores into FREED rs_malloc blocks (use-after-free writes). ROGUESQ_S7480_UAF=1 on top of the s7475 canary
# bitmap + STORE_DIAG store hook (upstream_compat.cpp s7480_*), PAD=16 (s7479), normal build, owner recipe, HOLD=${HOLD:-220}.
# LV="<level>:<dd> ..." (default "4:4 7:4 12:4 15:8"); dd>=8 arms run 21:9. Every arm carries the planted premature-free control
# ROGUESQ_S7480_PLANT=${PLANT_S:-150} (in flight). Each non-plant hit is located in the guest's own chains at store time: F = block still
# free (real use-after-free), Urec = inside an rs_malloc-recorded block (trim defect), U/N = arena re-carved by the scene reset (s7332
# fl=6 carve) or torn down (legit, reported). Exit 0 = every arm: plant DETECTED, internal>0 (split-header natural control), uaf_free=0
# and trim_defect=0 (s7481: F hits whose free block ends at the RSP task out buffer = frame DL span, counted as frame_span_S, not F); 1 = F or Urec hit(s); 3 = control FAIL; harness rc wins.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7480_uaf}; R=$PWD/scratch/$n; mkdir -p $R; rm -f $R/quiet.done $R/void_*(N) $R/ok_*(N) $R/ring_*.txt(N)
C="ROGUESQ_S7475_CANARY=1+ROGUESQ_S7475_FILL=0+ROGUESQ_STORE_DIAG=1+ROGUESQ_S7475_PAD=16+ROGUESQ_S7480_UAF=1+ROGUESQ_S7475_BT=1+ROGUESQ_S7480_PLANT=${PLANT_S:-150}"
lv=(${=${LV:-4:4 7:4 12:4 15:8}}); arms=(); tags=()
for e in $lv; do
  l=${e%%:*}; d=${e##*:}
  [[ $l == <0-18> && $d == <1-8> && $e == *:* ]] || { echo "$n bad LV entry '$e'"; exit 3; }
  s="${d}:l${l}:ROGUESQ_FORCE_SAVE_MISSION=${l}+${C}"
  (( d >= 8 )) && s="$s+ROGUESQ_ASPECT=21:9"
  arms+=$s; tags+=l$l
done
env R=$R HOLD=${HOLD:-220} DONE=quiet.done ARMS="${(j: :)arms}" zsh tools/g1e_owner_quiet_arms.zsh | tee $R/out.txt; rc=${pipestatus[1]}
(( rc == 2 )) && exit 2
sr=0
for a in $tags; do L=$R/log_$a.txt
  im=$(grep -a -c 'initMission\] call' $L 2>/dev/null); armed=$(grep -a -c '\[s7480\] uaf watch armed' $L 2>/dev/null)
  hit=$(grep -a '\[s7480\] uaf-store' $L 2>/dev/null | grep -v -c ' PLANT$'); pl=$(grep -a -c '\[s7480\] plant DETECTED' $L 2>/dev/null)
  pln=$(grep -a -n '\[s7480\] plant DETECTED' $L 2>/dev/null | head -1 | cut -d: -f1); imn=$(grep -a -n 'initMission\] call' $L 2>/dev/null | head -1 | cut -d: -f1)
  infl=0; [[ -n $pln && -n $imn ]] && (( pln > imn )) && infl=1
  last=$(grep -a '\[s7480\] sum ' $L 2>/dev/null | tail -1)
  intl=$(print -r -- "$last" | python3 -c 'import sys,re; s=sys.stdin.read(); m=re.search(r"internal=\{([^}]*)\}",s); print(sum(int(x) for x in re.findall(r":(\d+)",m.group(1))) if m else 0)')
  lf=$(print -r -- "$last" | sed -n 's/.* loc_F=\([0-9]*\).*/\1/p'); lu=$(print -r -- "$last" | sed -n 's/.* loc_Urec=\([0-9]*\).*/\1/p')
  ln=$(print -r -- "$last" | sed -n 's/.* loc_N=\([0-9]*\).*/\1/p'); lc=$(print -r -- "$last" | sed -n 's/.* loc_U=\([0-9]*\).*/\1/p')
  ls7481=$(print -r -- "$last" | sed -n 's/.* loc_S=\([0-9]*\).*/\1/p'); [[ -z $ls7481 ]] && ls7481=na  # s7481: F hits in the frame DL span (free block ending at RSP task out)
  [[ -z $lf || -z $lu ]] && { lf=-1; lu=-1; }
  lcf=$(grep -a -c '\[s7480\] locate-ctl free .* got=F PASS' $L 2>/dev/null); lcu=$(grep -a -c '\[s7480\] locate-ctl used .* got=U PASS' $L 2>/dev/null)
  echo "$n arm=$a initMission=$im armed=$armed uaf_rows_nonplant=$hit uaf_free=$lf trim_defect=$lu recarve_U=$lc recarve_N=$ln frame_span_S=$ls7481 plant_detected=$pl plant_inflight=$infl internal=$intl locate_ctl=$lcf$lcu last={$last}" | tee -a $R/out.txt
  (( armed == 0 || pl == 0 || intl == 0 || lf < 0 || lcf == 0 || lcu == 0 )) && sr=3; (( (lf > 0 || lu > 0) && sr == 0 )) && sr=1
done
echo "$n score=$sr" | tee -a $R/out.txt
(( rc != 0 )) && exit $rc
exit $sr
