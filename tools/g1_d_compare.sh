#!/bin/zsh
# G1(d) fold: tele-vs-ctl objective-counter comparison for one level.
# usage: tools/g1_d_compare.sh <N>   (reads scratch/agent/m6/g1_lvl<N>{ctl,tele}/run.log)
n=$1; b=scratch/agent/m6
for r in ctl tele; do
  f=$b/g1_lvl$n$r/run.log
  [ -f $f ] || { echo "$r: no log"; continue; }
  printf "%-5s TELE=%s objcount_max=%s crash=%s" $r "$(grep -c 'sph\] TELE' $f)" \
    "$(grep -h objcount $f | sed -n 's/.*val=\([0-9]*\).*/\1/p' | sort -n | tail -1)" "$(grep -c CRASH $f)"
  grep -h '\[objwr\]' $f | awk '{c[$2]++} END{for(k in c) printf " %s=%d",k,c[k]; print ""}'
done
