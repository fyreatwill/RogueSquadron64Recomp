#!/bin/zsh
# s7497 class EV: is depth ever WRITTEN through the game's Z=0 placeholder depth image? Wraps tools/s7496_eu_recipe.zsh with
# ROGUESQ_S7497_Z0=1 (lib/rt64 rt64_rdp.cpp -> main.cpp rs64_s7497_zdraw / s7497_wb) and scores the last `[s7497] sum` per arm.
# z0 = z-update tri/rect draws while depthImage.address==0, fills whose colour image is 0 (z-clear idiom), depth writebacks with
# base 0, and any writeback touching [0,0x100000). Control (same keyed maps): the busiest non-zero depth address must show
# tri_zupd>0, fill_cz>0, wb>0. Exit 0 = z0 all 0 + ctl ok + Z=0 window seen (zimg -> 000000) (H-ev-placeholder); 5 = z0 > 0; 3 = control FAIL.
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7497_ev}; R=$PWD/scratch/$n
env NAME=$n XC="ROGUESQ_S7497_Z0=1${XC:++$XC}" LV="${LV:-4:1:os_rt64fb 15:8:os_rt64fb}" zsh tools/s7496_eu_recipe.zsh; rc=$?
(( rc == 2 )) && exit 2
sr=0
for L in $R/log_l*.txt(N); do a=${${L:t:r}#log_}
  q=$(grep -a '\[s7497\] sum ' $L | tail -1); z0=${${q#* z0 }%% ctl *}; c=${q#* ctl }
  v() { print -r -- " $2" | sed -n "s/.* $1=\([0-9][0-9]*\).*/\1/p" | head -1 }  # BSD sed: no \b, so match " key="
  zs=0; miss=0; for k in tri_zupd rect_zupd fill_c0 wb_base0 wb_low; do x=$(v $k "$z0"); [[ -z $x ]] && miss=1; zs=$(( zs + ${x:-0} )); done
  ct=$(v tri_zupd "$c"); cf=$(v fill_cz "$c"); cw=$(v wb "$c"); win=$(grep -a -c '\[s7497\] zimg [0-9A-F]* -> 000000' $L)
  echo "$n ev arm=$a z0_sum=$zs z0=[$z0] ctl_tri=${ct:-0} ctl_fill=${cf:-0} ctl_wb=${cw:-0} z0_windows=$win miss=$miss" | tee -a $R/out.txt
  (( miss || ${ct:-0} == 0 || ${cf:-0} == 0 || ${cw:-0} == 0 )) && sr=3; (( zs > 0 && sr == 0 )) && sr=5
done
echo "$n ev score=$sr" | tee -a $R/out.txt
(( rc != 0 && rc != 4 )) && exit $rc
exit $sr
