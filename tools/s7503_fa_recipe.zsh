#!/bin/zsh
# s7503 class FA: are RT64 uploads whose newest writer is guest allocator metadata (rs_malloc* / rs_free / coalesceFreeHeap* /
# buildHeapFreeList) or packTlutEntriesRgba5551 into an image that is LIVE? Wraps tools/s7501_ez_recipe.zsh with ROGUESQ_S7503_FA=1
# (main.cpp s7503_*: arm in rs64_s7501_up, events from the s7500 draw/tex/up hooks, rs64_s7493_img, s7497 fill, s7500_wb, and
# rs64_s7503_swap in upstream_compat osViSwapBuffer_recomp). Verdicts: fill / live / rewrite / dead / pend (see main.cpp).
# Exit 0 = every arm: armed > 0, ctlC=ok, ctlV=ok, live=0; 5 = live > 0 (read `[s7503] verdict=live` rows); 3 = control FAIL / missing.
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7503_fa}; R=$PWD/scratch/$n
env NAME=$n XC="ROGUESQ_S7503_FA=1${XC:++$XC}" LV="${LV:-4:1:os_rt64fb 15:8:os_rt64fb}" zsh tools/s7501_ez_recipe.zsh; rc=$?
(( rc == 2 )) && exit 2
sr=0
for L in $R/log_l*.txt(N); do a=${${L:t:r}#log_}
  q=$(grep -a '\[s7503\] sum ' $L | tail -1)
  v() { print -r -- " $q" | sed -n "s/.* $1=\([0-9A-Za-z:,_]*\).*/\1/p" | head -1 }
  armed=$(v armed); live=$(v live)
  echo "$n fa arm=$a armed=${armed:-0} fill=$(v fill) live=${live:-?} rewrite=$(v rewrite) dead=$(v dead) pend=$(v pend) livefn=$(v livefn) ctlC=$(v ctlC) ctlV=$(v ctlV)" | tee -a $R/out.txt
  [[ -z $armed || $(v ctlC) != ok || $(v ctlV) != ok ]] && sr=3
  (( sr == 0 && ${live:-0} > 0 )) && sr=5
done
echo "$n fa score=$sr" | tee -a $R/out.txt
(( rc != 0 && rc != 3 && rc != 4 && rc != 5 )) && exit $rc
exit $sr
