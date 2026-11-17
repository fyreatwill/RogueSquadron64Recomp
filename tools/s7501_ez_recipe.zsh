#!/bin/zsh
# s7501 class EZ: the writer behind each RT64 checkRAM upload. Wraps tools/s7500_ey_recipe.zsh with ROGUESQ_S7501_EZ=1 +
# ROGUESQ_S7501_CTL=1 (main.cpp s7501_*; lib/rt64 hooks rs64_s7501_chk/hash/up; upstream_compat taps rs64_s7486_hostread kinds 6-8
# and rs64_s7475_store) and scores the last `[s7501] sum` per arm. Upload classes: new (fb never hashed), hash (0 words differ),
# wbo (another image's RT64 writeback), wbself, resize (hash range changed size, no writer), short (RT64 native copy shorter), revert (a writer in the window over the fb, outside the still-different bytes), sp_gfx / sp_aud / pi (host DMA), cpu / zmem / os (guest stores), none, trunc.
# Exit 0 = every arm: ups > 0, ctlst=ok, none=0 and trunc=0 (every upload attributed); 5 = none|trunc > 0 (read `[s7501] up cls=none`);
# 3 = control FAIL / missing. s7502: race = uploads only the pre-scan window edge attributes (old rule: none), pgres = trunc windows
# resolved by the per-4KB-page newest-writer table.
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7501_ez}; R=$PWD/scratch/$n
env NAME=$n XC="ROGUESQ_S7501_EZ=1+ROGUESQ_S7501_CTL=1${XC:++$XC}" LV="${LV:-4:1:os_rt64fb 15:8:os_rt64fb}" zsh tools/s7500_ey_recipe.zsh; rc=$?
(( rc == 2 )) && exit 2
sr=0
for L in $R/log_l*.txt(N); do a=${${L:t:r}#log_}
  q=$(grep -a '\[s7501\] sum ' $L | tail -1)
  v() { print -r -- " $q" | sed -n "s/.* $1=\([0-9A-Za-z:,|_]*\).*/\1/p" | head -1 }
  ups=$(v ups); none=$(v none); tr=$(v trunc); ctl=$(v ctlst)
  echo "$n ez arm=$a ups=${ups:-0} fbs=$(v fbs) new=$(v new) hash=$(v hash) wbo=$(v wbo) wbself=$(v wbself) sp_gfx=$(v sp_gfx) sp_aud=$(v sp_aud) pi=$(v pi) cpu=$(v cpu) zmem=$(v zmem) os=$(v os) none=${none:-?} trunc=${tr:-?} resize=$(v resize) short=$(v short) revert=$(v revert) ev=$(v ev) cpu_pcs=$(v cpu_pcs) ctlst=${ctl:-missing} bm=$(v bm) race=$(v race) pgres=$(v pgres)" | tee -a $R/out.txt
  (( ${ups:-0} == 0 )) || [[ $ctl != ok || -z $none ]] && sr=3
  (( sr == 0 && ( ${none:-0} > 0 || ${tr:-0} > 0 ) )) && sr=5
done
echo "$n ez score=$sr" | tee -a $R/out.txt
(( rc != 0 && rc != 4 && rc != 5 )) && exit $rc
exit $sr
