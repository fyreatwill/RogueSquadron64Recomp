#!/bin/zsh
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
# s7484 class EI: guest LOADS from FREED rs_malloc blocks (use-after-free reads). ROGUESQ_S7484_UAFLOAD=1 on top of the s7480 UAF
# watch (tools/apply_s7484_loadwatch.py wraps every generated lw/lh/lb/ld(c1); upstream_compat.cpp s7484_*), PAD=16, owner recipe,
# HOLD=${HOLD:-220}, LV as s7480 (default "4:4 7:4 12:4 15:8"; dd>=8 = 21:9). Controls per arm: load watch-ctl (frame counter word),
# load plant ROGUESQ_S7484_PLANT=${LPLANT_S:-150} (live block recorded as freed -> next load DETECTED), s7480 store plant + locator ctl.
# Each record's class at its first load: F = still free (real UAF read), Urec = trim defect, U/N = re-carved/torn-down arena, S = frame span.
# Exit 0 = all controls PASS and load_F=0, load_Urec=0; 1 = F/Urec load(s); 3 = control FAIL; harness rc wins.
# s7487 class EL: guest UNALIGNED loads lwl/lwr (tools/apply_s7487_lwlwatch.py, 410 sites = 207 lwl + 203 lwr, 0 ldl/ldr) on top of the
# s7484 recipe below (all its controls and scores kept). EL adds ROGUESQ_S7487_LWLWATCH=1 (execution census + freed-record test of the
# exact bytes each lwl/lwr reads) and ROGUESQ_S7487_LWLCTL=${CTL_S:-150} (EL control: a LIVE heap block an lwl/lwr just read is recorded
# as freed; the next lwl/lwr read of it MUST log `[s7487] lwl-ctl DETECTED`). EL scores: lwl_F/lwl_Urec > 0 -> 1; ctl not DETECTED
# while heap_samples > 0 -> 3; heap_samples == 0 -> arm prints el=none (lwl/lwr never read the heap: H-lwl-none).
# s7488 class EM: guest UNALIGNED STORES swl/swr (tools/apply_s7488_ustorewatch.py, 405 sites = 203 swl + 202 swr, 0 sdl/sdr) on top of
# everything above. EM adds ROGUESQ_S7488_USTOREWATCH=1 (execution census + freed-record AND canary-slack test of the exact bytes each
# swl/swr writes) and ROGUESQ_S7488_USTCTL=${UCTL_S:-160} (EM control: a LIVE heap block an swl/swr just wrote is recorded as freed; the
# next swl/swr into it MUST log `[s7488] ust-ctl DETECTED`). EM scores: ust_F/ust_Urec/slack > 0 -> 1; ctl not DETECTED while
# heap_samples > 0 -> 3; heap_samples == 0 -> em=none (swl/swr never write the heap: H-ust-none).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7488_ustwatch}; R=$PWD/scratch/$n; mkdir -p $R; rm -f $R/quiet.done $R/void_*(N) $R/ok_*(N) $R/ring_*.txt(N)
C="ROGUESQ_S7475_CANARY=1+ROGUESQ_S7475_FILL=0+ROGUESQ_STORE_DIAG=1+ROGUESQ_S7475_PAD=16+ROGUESQ_S7480_UAF=1+ROGUESQ_S7475_BT=1+ROGUESQ_S7480_PLANT=${PLANT_S:-150}+ROGUESQ_S7484_UAFLOAD=1+ROGUESQ_S7484_PLANT=${LPLANT_S:-150}+ROGUESQ_S7487_LWLWATCH=1+ROGUESQ_S7487_LWLCTL=${CTL_S:-150}+ROGUESQ_S7488_USTOREWATCH=1+ROGUESQ_S7488_USTCTL=${UCTL_S:-160}"
lv=(${=${LV:-4:4 7:4 12:4 15:8}}); arms=(); tags=()
for e in $lv; do
  # s7482: optional third field = per-arm extra env, '+'-joined (e.g. 7:4:ROGUESQ_RETARGET_RESERVE=0); such arms get tag l<lvl>x<k>
  l=${e%%:*}; rest=${e#*:}; d=${rest%%:*}; x=; [[ $rest == *:* ]] && x=${rest#*:}
  [[ $l == <0-18> && $d == <1-8> && $e == *:* ]] || { echo "$n bad LV entry '$e'"; exit 3; }
  tg=l$l; [[ -n $x ]] && tg=l${l}x$(( ${#tags} + 1 ))
  s="${d}:${tg}:ROGUESQ_FORCE_SAVE_MISSION=${l}+${C}"
  (( d >= 8 )) && s="$s+ROGUESQ_ASPECT=21:9"
  [[ -n $x ]] && s="$s+$x"
  arms+=$s; tags+=$tg
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
  rsa=$(grep -a -c '\[s7482\] reserve applied' $L 2>/dev/null); rss=$(grep -a -c '\[s7482\] reserve skipped' $L 2>/dev/null)
  pcl=$(grep -a '\[s7482\] pool-collide ' $L 2>/dev/null | grep -a -v -c CONTROL); pcc=$(grep -a -c '\[s7482\] pool-collide CONTROL' $L 2>/dev/null)
  echo "$n arm=$a s7482_reserve_applied=$rsa s7482_reserve_skipped=$rss s7482_pool_collide=$pcl s7482_collide_ctl=$pcc" | tee -a $R/out.txt
  echo "$n arm=$a initMission=$im armed=$armed uaf_rows_nonplant=$hit uaf_free=$lf trim_defect=$lu recarve_U=$lc recarve_N=$ln frame_span_S=$ls7481 plant_detected=$pl plant_inflight=$infl internal=$intl locate_ctl=$lcf$lcu last={$last}" | tee -a $R/out.txt
  (( armed == 0 || pl == 0 || intl == 0 || lf < 0 || lcf == 0 || lcu == 0 )) && sr=3; (( (lf > 0 || lu > 0) && sr == 0 )) && sr=1
  # s7482: an rs_malloc block overlapping the live retarget pool, or frame-span hits in an arm whose pool was reserved, is a failure
  (( pcl > 0 && sr == 0 )) && sr=1; [[ $ls7481 == <-> ]] && (( rsa > 0 && ls7481 > 0 && sr == 0 )) && sr=1
  la=$(grep -a -c '\[s7484\] load watch armed' $L 2>/dev/null); lctl=$(grep -a -c '\[s7484\] watch-ctl PASS' $L 2>/dev/null); lpl=$(grep -a -c '\[s7484\] plant DETECTED' $L 2>/dev/null)
  ll=$(grep -a '\[s7484\] sum ' $L 2>/dev/null | tail -1); lF=$(print -r -- "$ll" | sed -n 's/.* loc_F=\([0-9]*\).*/\1/p'); lR=$(print -r -- "$ll" | sed -n 's/.* loc_Urec=\([0-9]*\).*/\1/p')
  [[ -z $lF || -z $lR ]] && { lF=-1; lR=-1; }
  echo "$n arm=$a load_armed=$la load_ctl=$lctl load_plant=$lpl load_F=$lF load_Urec=$lR fhits=$(grep -a -c '\[s7484\] uaf-load .* loc=F ' $L 2>/dev/null) last_load={$ll}" | tee -a $R/out.txt
  (( la == 0 || lctl == 0 || lpl == 0 || lF < 0 )) && sr=3; (( (lF > 0 || lR > 0) && sr == 0 )) && sr=1
  wa=$(grep -a -c '\[s7487\] lwl/lwr watch armed' $L 2>/dev/null); wl=$(grep -a '\[s7487\] sum ' $L 2>/dev/null | tail -1)
  wpre=$( [[ -n $imn ]] && head -n $imn $L | grep -a '\[s7487\] sum ' | tail -1 )
  g() { print -r -- "$1" | sed -n "s/.* $2=\([0-9]*\).*/\1/p"; }
  wF=$(g "$wl" lwl_F); wR=$(g "$wl" lwl_Urec); wex=$(g "$wl" exec); whp=$(g "$wl" heap_samples); wes=$(g "$wl" exec_sites); whs=$(g "$wl" heap_sites)
  [[ -z $wF || -z $wR ]] && { wF=-1; wR=-1; }
  pex=$(g "$wpre" exec); php=$(g "$wpre" heap_samples); [[ -z $pex ]] && pex=0; [[ -z $php ]] && php=0
  wcn=$(grep -a -n '\[s7487\] lwl-ctl DETECTED' $L 2>/dev/null | head -1 | cut -d: -f1); wc=0; [[ -n $wcn ]] && wc=1
  wci=0; [[ -n $wcn && -n $imn ]] && (( wcn > imn )) && wci=1
  el=heap; [[ -z $whp || $whp == 0 ]] && el=none
  echo "$n arm=$a el_armed=$wa exec=$wex exec_sites=$wes exec_inflight=$(( ${wex:-0} - pex )) heap_samples=$whp heap_sites=$whs heap_inflight=$(( ${whp:-0} - php )) lwl_F=$wF lwl_Urec=$wR lwl_ctl=$wc lwl_ctl_inflight=$wci el=$el ctl_row={$(grep -a '\[s7487\] lwl-ctl DETECTED' $L 2>/dev/null | head -1)} last_el={$wl}" | tee -a $R/out.txt
  (( wa == 0 || wF < 0 )) && sr=3; [[ $el == heap ]] && (( wc == 0 )) && sr=3; (( (wF > 0 || wR > 0) && sr == 0 )) && sr=1
  ua=$(grep -a -c '\[s7488\] swl/swr watch armed' $L 2>/dev/null); ul=$(grep -a '\[s7488\] sum ' $L 2>/dev/null | tail -1)
  upre=$( [[ -n $imn ]] && head -n $imn $L | grep -a '\[s7488\] sum ' | tail -1 )
  uF=$(g "$ul" ust_F); uR=$(g "$ul" ust_Urec); uS=$(g "$ul" slack); uex=$(g "$ul" exec); uhp=$(g "$ul" heap_samples); ues=$(g "$ul" exec_sites); uhs=$(g "$ul" heap_sites)
  [[ -z $uF || -z $uR || -z $uS ]] && { uF=-1; uR=-1; uS=-1; }
  qex=$(g "$upre" exec); qhp=$(g "$upre" heap_samples); [[ -z $qex ]] && qex=0; [[ -z $qhp ]] && qhp=0
  ucn=$(grep -a -n '\[s7488\] ust-ctl DETECTED' $L 2>/dev/null | head -1 | cut -d: -f1); uc=0; [[ -n $ucn ]] && uc=1
  uci=0; [[ -n $ucn && -n $imn ]] && (( ucn > imn )) && uci=1
  em=heap; [[ -z $uhp || $uhp == 0 ]] && em=none
  echo "$n arm=$a em_armed=$ua exec=$uex exec_sites=$ues exec_inflight=$(( ${uex:-0} - qex )) heap_samples=$uhp heap_sites=$uhs heap_inflight=$(( ${uhp:-0} - qhp )) ust_F=$uF ust_Urec=$uR ust_slack=$uS ust_ctl=$uc ust_ctl_inflight=$uci em=$em ctl_row={$(grep -a '\[s7488\] ust-ctl DETECTED' $L 2>/dev/null | head -1)} last_em={$ul}" | tee -a $R/out.txt
  (( ua == 0 || uF < 0 )) && sr=3; [[ $em == heap ]] && (( uc == 0 )) && sr=3; (( (uF > 0 || uR > 0 || uS > 0) && sr == 0 )) && sr=1
done
echo "$n score=$sr" | tee -a $R/out.txt
(( rc != 0 )) && exit $rc
exit $sr
