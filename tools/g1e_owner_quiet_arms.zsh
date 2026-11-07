#!/bin/zsh
# s6932: owner recipe with NO recipe logging, launched directly (m6_god_common.sh arms LOG_PHASE and session probes, ~0.7 MB/s, s6932). Only the route
# keys, godmode, NO_SAVE_WRITE and the present ring are added. Locked 60 Hz. Stops if a human touches the machine.
# usage: env ARMS="4:q4: 2:q2:" HOLD=300 zsh tools/g1e_owner_quiet_arms.zsh ; spec = dd:arm:extra env, several joined with +
cd "$(git rev-parse --show-toplevel)" || exit 1
R=$PWD/scratch/s6932; DHZ=$PWD/scratch/s6931/dhz; HOLD=${HOLD:-300}
EARLY=""; e=10
for i in $(seq 1 20); do if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi; EARLY="$EARLY$e:$k,"; e=$((e+4)); done
FL=""; t=95
for i in $(seq 1 100); do for k in a sl a sr; do FL="$FL$t:$k,"; t=$((t+2)); done; (( t > 520 )) && break; done
AP="${EARLY}${FL%,}"
idle(){ ioreg -c IOHIDSystem | awk '/HIDIdleTime/{printf "%d\n",$NF/1e9; exit}'; }
for spec in ${=${ARMS:-"4:q4: 2:q2: 4:q4b: 2:q2b:"}}; do
  a=("${(@s/:/)spec}"); x=${spec#*:*:}; x=${x//+/ }; dd=$a[1]; arm=$a[2]; i=$(idle)
  echo "$(date +%T) $arm start idle=$i" >> $R/arms.log
  (( i < 120 )) && { echo "$(date +%T) human active, stopping" >> $R/arms.log; echo human > $R/quiet.done; exit 2; }
  $DHZ 60 $((HOLD+30)) > $R/hz_$arm.txt 2>&1 & hp=$!; /bin/sleep 3
  ( cd build && exec env ROGUESQ_FORCE_SAVE_MISSION=1 ROGUESQ_FORCE_UNLOCK=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_GODMODE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_AUTOPILOT=$AP ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=$dd ROGUESQ_ASPECT=16:9 ROGUESQ_FULLSCREEN=1 ROGUESQ_PRESENT_RING=$R/ring_$arm.txt ${=x} ./RogueSquadron64Recomp ) > ${LOGTO:-$R/log_$arm.txt} 2>&1 & gp=$!
  ( for k in 1 2 3 4 5 6 7 8; do /bin/sleep 12; osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron64Recomp") to true' >/dev/null 2>&1; done ) & rp=$!
  /bin/sleep $HOLD; alive=0; kill -0 $gp 2>/dev/null && alive=1
  kill -KILL $gp 2>/dev/null; kill $rp 2>/dev/null; kill -KILL $hp 2>/dev/null
  echo "$(date +%T) $arm done alive=$alive log=$(wc -c < ${LOGTO:-$R/log_$arm.txt})" >> $R/arms.log; /bin/sleep 3
done
echo done > $R/${DONE:-quiet.done}
