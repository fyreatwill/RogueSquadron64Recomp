#!/bin/zsh
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
# s7486 class EK: HOST readers of FREED rs_malloc blocks. ROGUESQ_S7486_HOSTUAF=1 on top of the s7480 UAF watch (upstream_compat.cpp
# rs64_s7486_hostread; hooks: RSP DMA rdram->dmem via src/rsp/s7094_dma_shape.cpp, RDP cmd range + LoadBlock/LoadTile/LoadTLUT source
# in src/rsp/dpc_bridge.cpp, AI DMA in librecomp ai.cpp), PAD=16, owner recipe, HOLD=${HOLD:-220}, LV default "4:4 7:4 12:4 15:8"
# (dd>=8 = 21:9). Controls per arm: ctl PASS kind=sp_dma_gfx (a host DMA read covers live canary slack: the bitmap path sees host
# reads); host plant ROGUESQ_S7486_PLANT=${HPLANT_S:-150} (LIVE heap block holding a recent gfx DMA source recorded as freed -> next
# host read DETECTED); s7480 store plant + locator ctl. Each freed record's class at its first host read per kind: F = still free
# (real host UAF), Urec = trim defect, U/N = re-carved/torn-down arena, S = frame span.
# Exit 0 = all controls PASS and host_F=0, host_Urec=0; 1 = F/Urec host read(s); 3 = control FAIL; harness rc wins.
# s7489 class EN: host WRITES into freed rs_malloc blocks, on top of the s7486 recipe (all its read scores kept). ROGUESQ_S7489_HOSTWRITE=1
# adds kinds sp_wr_gfx / sp_wr_aud (RSP DMEM->RDRAM, rsp.hpp dma_dmem_to_rdram via the s7094 hook) and pi_dma (pi.cpp do_dma before
# do_rom_read); ROGUESQ_S7489_WPLANT=1 points the s7486 plant at a recent host-WRITE destination, so the host plant line must read
# `plant DETECTED kind=sp_wr_*|pi_dma` (write-path positive control, in flight = after initMission). Scores: host_wF/host_wUrec > 0 -> 1;
# write plant not DETECTED -> 3. Guest side: tools/apply_s7489_storegap.py hooks the 12 texts that lacked RS64_S5798_ST (census exit 0).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7489_hostwrite}; R=$PWD/scratch/$n; mkdir -p $R; rm -f $R/quiet.done $R/void_*(N) $R/ok_*(N) $R/ring_*.txt(N)
C="ROGUESQ_S7475_CANARY=1+ROGUESQ_S7475_FILL=0+ROGUESQ_STORE_DIAG=1+ROGUESQ_S7475_PAD=16+ROGUESQ_S7480_UAF=1+ROGUESQ_S7475_BT=1+ROGUESQ_S7480_PLANT=${PLANT_S:-150}+ROGUESQ_S7486_HOSTUAF=1+ROGUESQ_S7486_PLANT=${HPLANT_S:-150}+ROGUESQ_S7489_HOSTWRITE=1+ROGUESQ_S7489_WPLANT=1"
lv=(${=${LV:-4:4 7:4 12:4 15:8}}); arms=(); tags=()
for e in $lv; do
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
  pl=$(grep -a -c '\[s7480\] plant DETECTED' $L 2>/dev/null)
  lcf=$(grep -a -c '\[s7480\] locate-ctl free .* got=F PASS' $L 2>/dev/null); lcu=$(grep -a -c '\[s7480\] locate-ctl used .* got=U PASS' $L 2>/dev/null)
  ha=$(grep -a -c '\[s7486\] host-read watch armed' $L 2>/dev/null); hctl=$(grep -a -c '\[s7486\] ctl PASS kind=sp_dma_gfx' $L 2>/dev/null)
  hctla=$(grep -a '\[s7486\] ctl PASS' $L 2>/dev/null | sed -n 's/.*kind=\([a-z_]*\).*/\1/p' | sort -u | tr '\n' ,)
  hpl=$(grep -a '\[s7486\] plant DETECTED' $L 2>/dev/null | head -1 | sed -n 's/.*kind=\([a-z_]*\).*/\1/p'); [[ -z $hpl ]] && hpl=none
  hpln=$(grep -a -n '\[s7486\] plant DETECTED' $L 2>/dev/null | head -1 | cut -d: -f1); imn=$(grep -a -n 'initMission\] call' $L 2>/dev/null | head -1 | cut -d: -f1)
  infl=0; [[ -n $hpln && -n $imn ]] && (( hpln > imn )) && infl=1
  hl=$(grep -a '\[s7486\] sum ' $L 2>/dev/null | tail -1); hF=$(print -r -- "$hl" | sed -n 's/.* host_F=\([0-9]*\).*/\1/p'); hR=$(print -r -- "$hl" | sed -n 's/.* host_Urec=\([0-9]*\).*/\1/p')
  [[ -z $hF || -z $hR ]] && { hF=-1; hR=-1; }
  wl=$(grep -a '\[s7489\] sum ' $L 2>/dev/null | tail -1); wF=$(print -r -- "$wl" | sed -n 's/.* host_wF=\([0-9]*\).*/\1/p'); wR=$(print -r -- "$wl" | sed -n 's/.* host_wUrec=\([0-9]*\).*/\1/p')
  [[ -z $wF || -z $wR ]] && { wF=-1; wR=-1; }; wa=$(grep -a -c '\[s7489\] host-write watch armed wplant=1' $L 2>/dev/null)
  echo "$n arm=$a initMission=$im armed=$armed store_plant=$pl locate_ctl=$lcf$lcu host_armed=$ha host_ctl_gfx=$hctl host_ctl_kinds=$hctla host_plant=$hpl host_plant_inflight=$infl host_F=$hF host_Urec=$hR write_armed=$wa host_wF=$wF host_wUrec=$wR wsum={$wl} frows=$(grep -a -c '\[s7486\] host-uaf .* loc=[FR] ' $L 2>/dev/null) last={$hl}" | tee -a $R/out.txt
  (( armed == 0 || pl == 0 || lcf == 0 || lcu == 0 || ha == 0 || hctl == 0 || hF < 0 )) && sr=3; [[ $hpl != sp_wr_gfx && $hpl != sp_wr_aud && $hpl != pi_dma ]] && sr=3; (( wa == 0 || wF < 0 )) && sr=3
  (( (hF > 0 || hR > 0 || wF > 0 || wR > 0) && sr == 0 )) && sr=1
done
echo "$n score=$sr" | tee -a $R/out.txt
(( rc != 0 )) && exit $rc
exit $sr
