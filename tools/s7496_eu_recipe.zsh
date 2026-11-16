#!/bin/zsh
# s7496 class EU: guest-heap blocks under a new fixed-RAM partition. Runs the s7493 ER recipe with ROGUESQ_S7495_POOL=1 (pool watch,
# tools/apply_s7495_poolwatch.py; [s7496] queries in main.cpp s7496_query -> upstream_compat.cpp rs64_s7496_overlap) and scores the last
# `[s7496] sum` per arm. Per query: every arena block intersecting the DL-chunk pool [base,end) or a NEW colour/depth image extent
# (addr .. addr + w*480*bpp) is listed as container (one used block holds the whole extent), live (used, partial) or free.
# Control (same run, every pool rebuild): the youngest s7475 malloc-hook record MUST be found used by the chain walk (ctl=ok/n).
# Exit 0 = every arm ctl ok==n>0 and live=0 outside the Z=0 placeholder (z0_live reported) (H-eu-clean); 5 = live>0 (read `[s7496] under ... cls=live`); 3 = control FAIL; s7493 rc wins.
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7496_eu}; R=$PWD/scratch/$n
env NAME=$n XC="ROGUESQ_S7495_POOL=1${XC:++$XC}" LV="${LV:-4:1:os_rt64fb 15:8:os_rt64fb}" WBWATCH=${WBWATCH:-787830} zsh tools/s7493_er_recipe.zsh; rc=$?
(( rc == 2 )) && exit 2
sr=0
for L in $R/log_l*.txt(N); do a=${${L:t:r}#log_}
  q=$(grep -a '\[s7496\] sum ' $L | tail -1); g() { print -r -- "$q" | sed -n "s/.* $1=\([0-9]*\).*/\1/p" }
  ctl=$(print -r -- "$q" | sed -n 's/.* ctl=\([0-9]*\)\/\([0-9]*\).*/\1 \2/p'); ok=${${(z)ctl}[1]:-0}; cn=${${(z)ctl}[2]:-0}
  pools=$(grep -a -c '\[s7495\] pool #' $L); live_all=$(g live)
  # s7496 run 1: the only live rows were the game's Z=0 placeholder depth image (extent [0, w*480*2) is an estimate); scored apart as z0
  z0=$(grep -a '\[s7496\] under kind=zimg ext=\[000000,' $L | grep -a -c 'cls=live'); live=$(( ${live_all:-0} - z0 ))
  echo "$n eu arm=$a pools=$pools q=$(g q) qbad=$(g qbad) live=$live z0_live=$z0 container=$(g container) free=$(g free) freehdr=$(g freehdr) ctl=$ok/$cn" | tee -a $R/out.txt
  (( cn == 0 || ok != cn || pools == 0 )) && sr=3; (( ${live:-0} > 0 && sr == 0 )) && sr=5
done
echo "$n eu score=$sr" | tee -a $R/out.txt
(( rc != 0 && rc != 4 )) && exit $rc
exit $sr
