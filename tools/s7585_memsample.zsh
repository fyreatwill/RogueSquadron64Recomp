#!/bin/zsh
# s7585 class LK: outside-the-process memory sampler for the one live game (tools/rs64_game_pid.zsh).
# usage: zsh tools/s7585_memsample.zsh <outdir> <max_s> [leaks_at_s ...]
# Writes <outdir>/mem.tsv (t_s pid phys_footprint_MB rss_MB) every 10 s from the first sample the game is alive, and
# <outdir>/leaks_<t>.txt (summary + per-type tally) at each leaks_at_s (seconds since the game pid first appeared).
cd "$(git rev-parse --show-toplevel)" || exit 1
O=$1; M=$2; shift 2; L=($@); mkdir -p $O; source tools/rs64_game_pid.zsh
pid=""; for i in $(seq 1 120); do pid=$(rs64_game_pid 2>/dev/null) && break; /bin/sleep 1; done
[[ -z $pid ]] && { echo "no game" > $O/mem.err; exit 1; }
t0=$(date +%s); echo "t_s\tpid\tfoot_mb\trss_mb" > $O/mem.tsv; done_l=()
while kill -0 $pid 2>/dev/null; do t=$(( $(date +%s) - t0 )); (( t > M )) && break
  f=$(footprint -p $pid 2>/dev/null | awk '/phys_footprint:/{v=$2;u=$3; if(u=="GB")v*=1024; if(u=="KB")v/=1024; print v; exit}')
  r=$(ps -o rss= -p $pid 2>/dev/null | awk '{printf "%.0f",$1/1024}')
  echo "$t\t$pid\t${f:-na}\t${r:-na}" >> $O/mem.tsv
  for a in $L; do if (( t >= a )) && [[ -z ${done_l[(r)$a]} ]]; then done_l+=($a)
    leaks $pid > $O/leaks_full_$a.txt 2>&1; grep -E 'leaks for|nodes malloced' $O/leaks_full_$a.txt > $O/leaks_$a.txt
    grep -oE 'Leak: 0x[0-9a-f]+ +size=[0-9]+ +[^ ]*.*' $O/leaks_full_$a.txt | awk '{s=$3; sub("size=","",s); k=$4" "$5; n[k]++; b[k]+=s} END{for(k in n) printf "%10d %6d %s\n", b[k], n[k], k}' | sort -rn | head -25 >> $O/leaks_$a.txt
    echo "leaks@$a done t=$(( $(date +%s) - t0 ))" >> $O/mem.log; fi; done
  /bin/sleep 10; done
echo "sampler end t=$(( $(date +%s) - t0 ))" >> $O/mem.log
