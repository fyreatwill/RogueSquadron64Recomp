#!/bin/zsh
# s6931: locked 60 vs 120 Hz on the built-in. Mode held by dhz (app-only, reverts on kill). Game raised to the front after boot so the window is fully visible; mc arm is not raised.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
R=$PWD/scratch/s6931; W=scratch/s6891; ST="ROGUESQ_PRESENT_TEST_STALL=110:17,124:17,138:17,152:50,166:50,180:50,194:200,208:200,222:200"
D0=$($W/dstate | wc -l)
run(){ local hz=$1 arm=$2 raise=$3 ex=$4 hp=""
  if [[ $hz != 120 ]]; then $R/dhz $hz 900 > $R/hz_$arm.txt 2>&1 & hp=$!; /bin/sleep 3; fi
  $W/wcover RogueSquadron64Recomp 10 34 > $R/cover_$arm.txt & local wp=$!
  env HOLD_S=240 zsh scratch/s6890/bridge.zsh 1 1 $arm "$ex ROGUESQ_PRESENT_RING=$R/ring_$arm.txt" > $R/out_$arm.txt 2>&1 & local bp=$!
  ( if [[ $raise == 1 ]]; then for i in 1 2 3 4 5 6 7 8; do /bin/sleep 12; osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron64Recomp") to true' >> $R/raise_$arm.txt 2>&1; done; fi ) & local rp=$!
  ( /bin/sleep 45; if [[ $(grep -c ' at=[1-9]' $R/ring_$arm.txt 2>/dev/null) -lt 100 ]]; then echo "$(date +%T) $arm NO on-screen rows at 45 s" >> $R/arms.log; touch $R/noreports_$arm; fi ) & local gp=$!
  ( while /bin/sleep 15; do n=$($W/dstate | wc -l); if [[ $n -ne $D0 ]]; then echo "$(date +%T) $arm display count $D0 -> $n" >> $R/arms.log; touch $R/abort; pkill -KILL -f scratch/agent/m6_god_common.sh; pkill -KILL -x RogueSquadron64Recomp; break; fi; done ) & local dp=$!
  wait $bp; kill $gp $dp $wp $rp 2>/dev/null; [[ -n $hp ]] && kill -KILL $hp 2>/dev/null
  cp /tmp/s6890_$arm.out $R/run_$arm.out 2>/dev/null; echo "$(date +%T) $arm done hz=$hz" >> $R/arms.log; /bin/sleep 3
  [[ -e $R/abort ]] && { echo abort > $R/arms.done; exit 1; }
}
run 120 a120 1 ""
run 60 a60 1 ""
run 60 a60st 1 "$ST"
run 120 a120st 1 "$ST"
run 60 a60mc 0 "ROGUESQ_WINDOW_POS=800,500"
run 60 a60g 1 "ROGUESQ_PRESENT_INFLIGHT=2"
run 60 a60d 1 "ROGUESQ_PRESENT_DRAIN=40"
echo done > $R/arms.done
