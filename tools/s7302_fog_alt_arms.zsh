#!/bin/zsh
# s7302: same-run far-ring A/B at dd8 16:9: ROGUESQ_DD_WIDEWIN_R=<R> + _R_TOG=1 (R on xor8-odd seconds, unlimited on even; the auto
# R128 is overridden by the explicit R, so the off phase = no radius cut, a superset of R128). Arms: l1r88 (LEVEL 1), l4r88 (LEVEL 4),
# l1r40 (lever-positive control: R=40 cuts cells s7265 showed are visible). CULL_SPIKE=1 (not tog: same clock). Capture 120..300 s.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
O=scratch/s7302; rc=0
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo locked; exit 2; }
for spec in l1a:1:1,6.4 l4a:4:1,6.4 l1c:1:0.3,0.8; do
  n=${spec%%:*}; rest=${spec#*:}; lv=${rest%%:*}; r=${rest##*:}
  ( for k in $(seq 1 33); do /bin/sleep 10; osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron64Recomp") to true' >/dev/null 2>&1; done ) & fp=$!
  env ASP=16:9 CW=960 CH=540 CULL=1 zsh scratch/s7009/arm.zsh $lv 8 s7302$n "ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_DD_FOG_ALT=$r" 120 180 > $O/arm_$n.txt 2>&1; kill -9 $fp 2>/dev/null
  raw=scratch/s7009/s7302$n.raw; L=scratch/agent/m6/g1_lvl${lv}s7009s7302$n
  grep -a -h '\[s7293\]\|\[s7258\]\|\[s7233\] widewin_r\|\[s7010-clk\]' $L/*.log 2>/dev/null | head -5 > $O/cfg_$n.txt
  grep -a -h '\[s7233\] ph=' $L/*.log 2>/dev/null > $O/tally_$n.txt
  grep -a -c 'CRASH\|SIGSEGV\|SIGBUS' $L/*.log 2>/dev/null | awk -F: '{s+=$2}END{print "crash_lines",s+0}' > $O/crash_$n.txt
  if [[ -s $raw ]]; then
    python3 tools/s7247_tog_pop.py $raw 3 12,50 full > $O/far_$n.txt 2>&1
    python3 tools/s7247_tog_pop.py $raw 3 60,88 full > $O/near_$n.txt 2>&1
    python3 tools/s7247_tog_pop.py $raw 3 > $O/side_$n.txt 2>&1
    python3 tools/s7267_tog_sheet.py $raw $O/sheet_$n.png "$n dd8 16:9 FOG_ALT $r def|alt" 6 24e6 640 xor8 > $O/sheet_$n.txt 2>&1
    rm -f $raw; else echo "no raw" > $O/far_$n.txt; rc=1; fi
  echo "== $n"; cat $O/cfg_$n.txt $O/crash_$n.txt; tail -3 $O/far_$n.txt
done
exit $rc
