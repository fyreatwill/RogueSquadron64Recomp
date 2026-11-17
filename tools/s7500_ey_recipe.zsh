#!/bin/zsh
# s7500 class EY: resurrection of a stale-covered image. Wraps tools/s7499_ex_recipe.zsh with ROGUESQ_S7500_EY=1 + ROGUESQ_S7500_CTL=1
# (main.cpp s7500_*; lib/rt64 hooks rs64_s7500_draw/tex/up) and scores the last `[s7500] sum` per arm.
# first-event classes after a covered B is set again: fill / draw / zupd (rewrite), zread / tex / up (read of A's bytes through B), updisc, wb.
# Exit 0 = every arm: hooks fire (draw, tex, set > 0), ctlA=ok, ctlB=ok, read=0 (H-ey-dead when resets=0, H-ey-rewrite when resets>0);
# 5 = read>0 (read `[s7500] first cls=zread|tex|up` rows); 3 = control FAIL / missing.
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7500_ey}; R=$PWD/scratch/$n
env NAME=$n XC="ROGUESQ_S7500_EY=1+ROGUESQ_S7500_CTL=1${XC:++$XC}" LV="${LV:-4:1:os_rt64fb 15:8:os_rt64fb}" zsh tools/s7499_ex_recipe.zsh; rc=$?
(( rc == 2 )) && exit 2
sr=0
for L in $R/log_l*.txt(N); do a=${${L:t:r}#log_}
  q=$(grep -a '\[s7500\] sum ' $L | tail -1)
  q1=${q%% hooks *}  # first-event fields share names with the hook totals after ` hooks `: parse the prefix only
  v() { print -r -- " $q1 ${q#* hooks }" | sed -n "s/^.* $1=\([0-9A-Za-z]*\).*/\1/p" | head -1 }
  f() { print -r -- " $q1" | sed -n "s/^.* $1=\([0-9A-Za-z]*\).*/\1/p" | head -1 }
  hd=$(print -r -- "$q" | sed -n 's/.* hooks draw=\([0-9]*\) tex=\([0-9]*\) up=\([0-9]*\) fill=\([0-9]*\) set=\([0-9]*\).*/\1 \2 \3 \4 \5/p')
  hh=(${=hd}); rd=$(v read)
  echo "$n ey arm=$a tracked=$(v tracked) covers=$(v covers) unset=$(v covered_unset) resets=$(v resets) pending=$(v pending) fill=$(f fill) draw=$(f draw) zupd=$(f zupd) zread=$(f zread) tex=$(f tex) up=$(f up) updisc=$(f updisc) wb=$(f wb) read=${rd:-?} hooks=${hd// /\/} ctlA=$(v ctlA)/$(v ctlA_cls) ctlB=$(v ctlB)" | tee -a $R/out.txt
  (( ${hh[1]:-0} == 0 || ${hh[2]:-0} == 0 || ${hh[5]:-0} == 0 )) && sr=3
  [[ $(v ctlA) != ok || $(v ctlB) != ok || -z $rd ]] && sr=3
  (( sr == 0 && ${rd:-0} > 0 )) && sr=5
done
echo "$n ey score=$sr" | tee -a $R/out.txt
(( rc != 0 && rc != 4 && rc != 5 )) && exit $rc
exit $sr
