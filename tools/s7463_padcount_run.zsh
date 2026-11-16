#!/bin/zsh
# s7463 class DS: no-key boot arms for the padding-hash census. usage: zsh tools/s7463_padcount_run.zsh <outdir> <secs> <arm>:<PADCOUNT>[:<PADFIX>] ...
# Each arm boots title+attract with ROGUESQ_S7463_PADCOUNT set, runs <secs>, SIGKILLs, prints one tag= line with the last [s7463] counters per site.
cd "$(git rev-parse --show-toplevel)" || exit 1
O=$1; S=$2; shift 2; mkdir -p $O; rc=0
for spec in "$@"; do
  a=${spec%%:*}; r=${spec#*:}; pc=${r%%:*}; pf=1; [[ $r == *:* ]] && pf=${r#*:}
  L=$O/$a.log
  ( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_S7463_PADCOUNT=$pc ROGUESQ_S7463_PADFIX=$pf ./RogueSquadron64Recomp ) > $L 2>&1 &
  pid=$!; t=0; while (( t < S )) && kill -0 $pid 2>/dev/null; do sleep 2; t=$((t+2)); done
  alive=0; kill -0 $pid 2>/dev/null && alive=1; kill -9 $pid 2>/dev/null; wait $pid 2>/dev/null
  fat=$(sh tools/agent/fatal_scan.sh $L 2>/dev/null | head -1)
  sites=$(python3 - $L <<'P'
import sys,re
last={}
for ln in open(sys.argv[1],errors='replace'):
    m=re.match(r'\[s7463\] site=(\S+) calls=(\d+) padnz=(\d+) fixdiff=(\d+) extra=(\d+) distinct_raw=(\d+) distinct_fixed=(\d+)',ln)
    if m: last[m[1]]=m.groups()[1:]
print(' '.join(f'{k}={"/".join(v)}' for k,v in sorted(last.items())) or 'none')
P
)
  echo "tag=s7463_$a alive_at_end=$alive secs=$t padcount=$pc padfix=$pf fatal=${fat:-none} sites(calls/padnz/fixdiff/extra/distinct_raw/distinct_fixed)=$sites"
  (( alive )) || rc=1
done
exit $rc
