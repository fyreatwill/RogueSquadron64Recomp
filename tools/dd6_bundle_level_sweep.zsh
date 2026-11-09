#!/bin/zsh
# s7041: dd6 + WIDEWIN + MELT bundle per-level qualification sweep (owner "Farthest view" recipe), one game at a time.
# Per level: ~500 s flight hold, FPS60, ASPECT (default 16:9), same-run tog3 off-map cull R=-1 / R=2 K=0.6 / R=2 K=0.6
# (phase 0 = bundle cull off control, phases 1+2 = bundle cull, A/A between them), no capture; cost from the G1E_TL ring.
# usage: env LEVELS="0 8 9" [ASP=21:9] [TAG=S42] zsh tools/dd6_bundle_level_sweep.zsh <outdir>   (ANALYZE_ONLY=1 re-scores)
# Report per level: summary (alive_at_end, vi_stalls30s, crashlines), crash-line counts, g5e_cost_by_parity --phases 3 xor8, [s7031] ocull/f per phase.
# Expected [s7037] count 0: the explicit OFFMAPCULL env overrides the auto bundle (same R/K/H values as the bundle).
cd "$(git rev-parse --show-toplevel)" || exit 2
O=${1:?outdir}; mkdir -p $O; T=${TAG:-S41}; R=$PWD/scratch/s7031
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 4; }
COMMON="ROGUESQ_G1B=1 ROGUESQ_DD_UNSAFE=1 ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_DD_WIDEWIN_CAP=10240"
for L in ${=LEVELS:-2 3 6 7}; do N=${T}L$L; D=scratch/agent/m6/g1_lvl${L}s7031$N
  if [ -z "${ANALYZE_ONLY:-}" ]; then
    env NOCAP=1 CW=640 CH=360 ASP=${ASP:-16:9} CULL=1 zsh $R/arm.zsh $L 6 $N "$COMMON ROGUESQ_G1E_TL=$PWD/$O/tl_$N.bin ROGUESQ_DD_FOGCULL=tog3 ROGUESQ_DD_FOGCULL_K=0,0,0 ROGUESQ_DD_OFFMAPCULL=tog3 ROGUESQ_DD_OFFMAPCULL_R=-1,2,2 ROGUESQ_DD_OFFMAPCULL_K=0,0.6,0.6 ROGUESQ_DD_OFFMAPCULL_H=off" 170 330 > $O/arm_$N.out 2>&1
    pkill -9 -x RogueSquadron64Recomp; /bin/sleep 5
  fi
  echo "=== L$L"; grep -a -o 'tag=.*crashlines=[0-9]*' $D/summary | head -1
  cat $R/crash_$N.txt 2>/dev/null | tr '\n' ' '; echo
  tl=$(ls $O/tl_$N.bin.* 2>/dev/null | head -1)
  [ -n "$tl" ] && python3 tools/g5e_cost_by_parity.py $tl $D/run.log --phases 3 --skip-s 130 --split xor8 2>&1 | grep -a -v '^#\|split=' | head -8
  grep -a '^\[s7031\] t=' $D/run.log | awk '{split($2,t,"=");split($3,p,"=");split($7,o,"="); if(t[2]>=130){s[p[2]]+=o[2];n[p[2]]++}} $5 ~ /dims/ {dims=$5} END{printf "%s ocull/f",dims; for(k=0;k<3;k++) printf " ph%d=%.0f(n%d)",k,(n[k]?s[k]/n[k]:-1),n[k]; print ""}'
done
