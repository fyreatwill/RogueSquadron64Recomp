#!/bin/zsh
# s7263: does ROGUESQ_DD_WIDEWIN reduce the hard side terrain edge at 16:9 (owner TV), as it does at 21:9 (s7009)?
# One game at a time, same-run toggle: ROGUESQ_DD_WIDEWIN=tog (auto stack rides along), L4 dd4 FPS60 MELT, capture + g5e_edge_score per third.
# Arms: a169 (test, 960x540) then a219 (positive control, 1260x540: s7009 right third hard80 16.1 -> 8.3 must re-fire).
# TOG_SPLIT=parity: the scorer bins plain (mach/24e6)&1, not the default xor8 split.
# s7264: ARMS="name:asp:cw ..." picks arms; XENV adds env to every arm, XENV_<name> to one arm (spaces separate vars).
# s7267: SHEET=1 writes <outdir>/sheet_<arm>.png (tools/s7267_tog_sheet.py).
# Usage: zsh tools/s7263_widewin_edge_arms.zsh <outdir>   (needs an unlocked screen; captures the game window)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
O=${1:-scratch/s7263q}; mkdir -p $O; rc=0
for spec in ${=ARMS:-"a169:16:9:960 a219:21:9:1260"}; do
  n=${spec%%:*}; rest=${spec#*:}; asp=${rest%:*}; cw=${rest##*:}
  # s7264: s7009/arm.zsh lacks the s7259 frontmost keeper; with Chrome in front SCK sent ~0.75 frames/s (133/180 s). Keep the game in front.
  ( for k in $(seq 1 33); do /bin/sleep 10; osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron64Recomp") to true' >/dev/null 2>&1; done ) & fp=$!
  env ASP=$asp CW=$cw CH=540 CULL=1 zsh scratch/s7009/arm.zsh 4 4 s7263$n "ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=tog ROGUESQ_TOG_SPLIT=parity ${XENV:-} ${(P)${:-XENV_$n}}" 120 180 > $O/arm_$n.txt 2>&1; kill -9 $fp 2>/dev/null
  raw=scratch/s7009/s7263$n.raw
  # s7264: s7263_169_edge returned rc=0 on 140 captured frames / 180 s (0.8/s; s7009 got ~19/s): starved captures self-fail (rc=3).
  fr=$(grep -a -o 'frames [0-9]*' scratch/s7009/cap_s7263$n.txt 2>/dev/null | awk '{print $2}'); fr=${fr:-0}
  echo "capture_frames $fr per_s $((fr/180))" > $O/capfps_$n.txt
  if (( fr < 1800 )); then echo "CAPTURE STARVED $n: $fr frames < 1800 (10/s)" | tee -a $O/capfps_$n.txt; rc=3; fi
  if [[ -s $raw ]]; then python3 tools/g5e_edge_score.py $raw 2 1000000000 50 24e6 2 > $O/edge_$n.txt 2>&1
    # s7267: SHEET=1 keeps an owner sheet (adjacent WIDEWIN off/on frame pairs) before the raw is deleted.
    [[ -n ${SHEET:-} ]] && python3 tools/s7267_tog_sheet.py $raw $O/sheet_$n.png "$n $asp WIDEWIN off|on" 6 24e6 640 > $O/sheet_$n.txt 2>&1
    rm -f $raw; else echo "no raw" > $O/edge_$n.txt; rc=1; fi
  grep -a -c 'CRASH\|SIGSEGV\|SIGBUS' scratch/agent/m6/g1_lvl4s7009s7263$n/*.log 2>/dev/null | awk -F: '{s+=$2}END{print "crash_lines",s+0}' > $O/crash_$n.txt
  echo "== $n ($asp)"; cat $O/edge_$n.txt $O/crash_$n.txt $O/capfps_$n.txt $O/arm_$n.txt | tail -n 12
done
exit $rc
