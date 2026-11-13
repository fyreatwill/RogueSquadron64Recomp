#!/bin/zsh
# s7263: does ROGUESQ_DD_WIDEWIN reduce the hard side terrain edge at 16:9 (owner TV), as it does at 21:9 (s7009)?
# One game at a time, same-run toggle: ROGUESQ_DD_WIDEWIN=tog (auto stack rides along), L4 dd4 FPS60 MELT, capture + g5e_edge_score per third.
# Arms: a169 (test, 960x540) then a219 (positive control, 1260x540: s7009 right third hard80 16.1 -> 8.3 must re-fire).
# TOG_SPLIT=parity: the scorer bins plain (mach/24e6)&1, not the default xor8 split.
# Usage: zsh tools/s7263_widewin_edge_arms.zsh <outdir>   (needs an unlocked screen; captures the game window)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
O=${1:-scratch/s7263q}; mkdir -p $O; rc=0
for spec in "a169:16:9:960" "a219:21:9:1260"; do
  n=${spec%%:*}; rest=${spec#*:}; asp=${rest%:*}; cw=${rest##*:}
  env ASP=$asp CW=$cw CH=540 CULL=1 zsh scratch/s7009/arm.zsh 4 4 s7263$n "ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=tog ROGUESQ_TOG_SPLIT=parity" 120 180 > $O/arm_$n.txt 2>&1
  raw=scratch/s7009/s7263$n.raw
  if [[ -s $raw ]]; then python3 tools/g5e_edge_score.py $raw 2 1000000000 50 24e6 2 > $O/edge_$n.txt 2>&1; rm -f $raw; else echo "no raw" > $O/edge_$n.txt; rc=1; fi
  grep -a -c 'CRASH\|SIGSEGV\|SIGBUS' scratch/agent/m6/g1_lvl4s7009s7263$n/*.log 2>/dev/null | awk -F: '{s+=$2}END{print "crash_lines",s+0}' > $O/crash_$n.txt
  echo "== $n ($asp)"; cat $O/edge_$n.txt $O/crash_$n.txt $O/arm_$n.txt | tail -n 12
done
exit $rc
