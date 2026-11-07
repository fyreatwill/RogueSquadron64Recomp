#!/bin/zsh
# s6932: owner recipe on a locked 60 Hz built-in. Stops if a human touches the machine (HID idle < 120 s at an arm start), or a display appears/leaves.
# usage: zsh tools/g1e_owner_hz_arms.zsh  (needs scratch/s6931/dhz from tools/g1e_display_hz.swift, scratch/s6891/dstate from tools/g1e_display_state.swift)
cd "$(git rev-parse --show-toplevel)" || exit 1
R=$PWD/scratch/s6932; W=scratch/s6891; DHZ=scratch/s6931/dhz
ST="ROGUESQ_PRESENT_TEST_STALL=110:17,124:17,138:17,152:50,166:50,180:50,194:200,208:200,222:200"
D0=$($W/dstate | wc -l)
idle(){ ioreg -c IOHIDSystem | awk '/HIDIdleTime/{printf "%d\n",$NF/1e9; exit}'; }
run(){ local hz=$1 dd=$2 arm=$3 ex=$4 hp="" i=$(idle)
  echo "$(date +%T) $arm start idle=$i" >> $R/arms.log
  if (( i < 120 )); then echo "$(date +%T) human active, stopping" >> $R/arms.log; echo human > $R/arms.done; exit 2; fi
  if [[ $hz != 120 ]]; then $DHZ $hz 900 > $R/hz_$arm.txt 2>&1 & hp=$!; /bin/sleep 3; fi
  env HOLD_S=240 zsh tools/g1e_owner_bridge.zsh 1 $dd $arm "$ex ROGUESQ_PRESENT_RING=$R/ring_$arm.txt" > $R/out_$arm.txt 2>&1 & local bp=$!
  ( for k in 1 2 3 4 5 6 7 8; do /bin/sleep 12; osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron64Recomp") to true' >> $R/raise_$arm.txt 2>&1; done ) & local rp=$!
  ( /bin/sleep 45; if [[ $(grep -c ' at=[1-9]' $R/ring_$arm.txt 2>/dev/null) -lt 100 ]]; then echo "$(date +%T) $arm NO on-screen rows at 45 s" >> $R/arms.log; touch $R/noreports_$arm; fi ) & local gp=$!
  ( while /bin/sleep 15; do n=$($W/dstate | wc -l); if [[ $n -ne $D0 ]]; then echo "$(date +%T) $arm display count $D0 -> $n" >> $R/arms.log; touch $R/abort; pkill -KILL -f scratch/agent/m6_god_common.sh; pkill -KILL -x RogueSquadron64Recomp; break; fi; done ) & local dp=$!
  wait $bp; kill $gp $dp $rp 2>/dev/null; [[ -n $hp ]] && kill -KILL $hp 2>/dev/null
  cp /tmp/s6932_$arm.out $R/run_$arm.out 2>/dev/null; echo "$(date +%T) $arm done hz=$hz idle=$(idle)" >> $R/arms.log; /bin/sleep 3
  [[ -e $R/abort ]] && { echo abort > $R/arms.done; exit 1; }
}
DEF="60:4:d4o: 60:2:d2o: 60:4:d4g:ROGUESQ_PRESENT_INFLIGHT=2 60:4:d4d:ROGUESQ_PRESENT_DRAIN=40 60:4:d4st:ST 60:2:d2g:ROGUESQ_PRESENT_INFLIGHT=2 60:2:d2d:ROGUESQ_PRESENT_DRAIN=40 60:4:d4r: 60:2:d2r:"
for spec in ${=${ARMS:-$DEF}}; do
  a=("${(@s/:/)spec}"); x=${spec#*:*:*:}; [[ $x == ST ]] && x=$ST
  run $a[1] $a[2] $a[3] "$x"
done
echo done > $R/arms.done
