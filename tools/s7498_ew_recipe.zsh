#!/bin/zsh
# s7498 class EW: does the byte range each RT64 writeback actually writes, [phys, phys+bytes), stay inside ONE used guest-heap block?
# Wraps tools/s7497_ev_recipe.zsh with ROGUESQ_S7498_EW=1 + ROGUESQ_S7498_CTL=${EWCTL:-20} (main.cpp s7498_wb -> upstream_compat.cpp
# rs64_s7496_overlap) and scores the last `[s7498] sum` per arm. Per (kind, image base, width) the range [base, end) is re-walked each
# time its end grows: container / partial (used block intersects, none contains = spill into a neighbour) / free / nonheap.
# Control (same run): the first container query at/after #EWCTL is re-run with its end 0x100 past the container -> must be non-container.
# Exit 0 = every arm: q>0, partial=0, free=0, ctl=ok (H-ew-inside); 5 = partial or free > 0 (read `[s7498] wb ... cls=partial|free`);
# 3 = control FAIL / no queries; inner recipe rc wins otherwise.
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7498_ew}; R=$PWD/scratch/$n
env NAME=$n XC="ROGUESQ_S7498_EW=1+ROGUESQ_S7498_CTL=${EWCTL:-20}${XC:++$XC}" LV="${LV:-4:1:os_rt64fb 15:8:os_rt64fb}" zsh tools/s7497_ev_recipe.zsh; rc=$?
(( rc == 2 )) && exit 2
sr=0
for L in $R/log_l*.txt(N); do a=${${L:t:r}#log_}
  q=$(grep -a '\[s7498\] sum ' $L | tail -1)
  v() { print -r -- " $q" | sed -n "s/.* $1=\([0-9A-Za-z]*\).*/\1/p" | head -1 }
  np=$(v partial); nf=$(v free); nq=$(v q); ctl=$(v ctl)
  echo "$n ew arm=$a wb=$(v wb) nobase=$(v nobase) keys=$(v keys) q=${nq:-0} qbad=$(v qbad) container=$(v container) partial=${np:-?} free=${nf:-?} nonheap=$(v nonheap) ctl=${ctl:-missing}" | tee -a $R/out.txt
  (( ${nq:-0} == 0 )) || [[ $ctl != ok || -z $np || -z $nf ]] && sr=3
  (( sr == 0 && (${np:-0} > 0 || ${nf:-0} > 0) )) && sr=5
done
echo "$n ew score=$sr" | tee -a $R/out.txt
(( rc != 0 && rc != 4 && rc != 5 )) && exit $rc
exit $sr
