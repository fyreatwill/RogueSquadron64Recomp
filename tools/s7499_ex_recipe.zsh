#!/bin/zsh
# s7499 class EX: cross-image overlap. Does an RT64 writeback of image A cover bytes of a DIFFERENT image B the RDP stream set?
# Wraps tools/s7498_ew_recipe.zsh with ROGUESQ_S7499_EX=1 + ROGUESQ_S7499_CTL=${EXCTL:-20} (main.cpp s7499_ex) and scores the last
# `[s7499] sum` per arm. Pair classes: same (B.base == A.base, z-clear idiom), live (B set this/previous swap: a real clobber
# candidate), stale (B last set >= 2 swaps ago), est (B never written back, 240-row estimate), ctl (fake image at a writeback's
# phys + bytes/2, must be hit).
# Exit 0 = every arm: wb>0, ctlst=ok, live=0 (H-ex-disjoint / H-ex-zclear); 5 = live>0 (read `[s7499] x cls=live`); 3 = control FAIL.
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7499_ex}; R=$PWD/scratch/$n
env NAME=$n XC="ROGUESQ_S7499_EX=1+ROGUESQ_S7499_CTL=${EXCTL:-20}${XC:++$XC}" LV="${LV:-4:1:os_rt64fb 15:8:os_rt64fb}" zsh tools/s7498_ew_recipe.zsh; rc=$?
(( rc == 2 )) && exit 2
sr=0
for L in $R/log_l*.txt(N); do a=${${L:t:r}#log_}
  q=$(grep -a '\[s7499\] sum ' $L | tail -1)
  v() { print -r -- " $q" | sed -n "s/.* $1=\([0-9A-Za-z]*\).*/\1/p" | head -1 }
  nl=$(v live); ctl=$(v ctlst); nw=$(v wb)
  echo "$n ex arm=$a wb=${nw:-0} imgs=$(v imgs) pairs=$(v pairs) same=$(v same) live=${nl:-?} stale=$(v stale) est=$(v est) ctl=$(v ctl) ctlst=${ctl:-missing}" | tee -a $R/out.txt
  (( ${nw:-0} == 0 )) || [[ $ctl != ok || -z $nl ]] && sr=3
  (( sr == 0 && ${nl:-0} > 0 )) && sr=5
done
echo "$n ex score=$sr" | tee -a $R/out.txt
(( rc != 0 && rc != 4 && rc != 5 )) && exit $rc
exit $sr
