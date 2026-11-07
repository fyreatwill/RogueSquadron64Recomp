#!/bin/zsh
# s6932: owner recipe with stderr on a real Terminal.app tty, the way docs/OWNER-OPT-INS.md launches it. Every other present arm logs to a file.
# Same recipe as tools/g1e_owner_quiet_arms.zsh, locked 60 Hz. usage: env HOLD=300 zsh tools/g1e_owner_tty_arm.zsh DD ARM "EXTRA ENV"
cd "$(git rev-parse --show-toplevel)" || exit 1
R=$PWD/scratch/s6932; DHZ=$PWD/scratch/s6931/dhz; HOLD=${HOLD:-300}; dd=${1:-4}; arm=${2:-tt}; x=${3:-}
EARLY=""; e=10
for i in $(seq 1 20); do if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi; EARLY="$EARLY$e:$k,"; e=$((e+4)); done
FL=""; t=95
for i in $(seq 1 100); do for k in a sl a sr; do FL="$FL$t:$k,"; t=$((t+2)); done; (( t > 520 )) && break; done
AP="${EARLY}${FL%,}"
i=$(ioreg -c IOHIDSystem | awk '/HIDIdleTime/{printf "%d\n",$NF/1e9; exit}')
(( i < 120 )) && { echo "$(date +%T) $arm human active" >> $R/arms.log; exit 2; }
$DHZ 60 $((HOLD+30)) > $R/hz_$arm.txt 2>&1 & hp=$!; /bin/sleep 3
L=$R/tty_$arm.zsh
cat > $L <<S
cd $PWD/build; echo \$\$ > $R/tty_$arm.pid; tty > $R/tty_$arm.tty
exec env ROGUESQ_FORCE_SAVE_MISSION=1 ROGUESQ_FORCE_UNLOCK=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_GODMODE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_AUTOPILOT=$AP ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=$dd ROGUESQ_ASPECT=16:9 ROGUESQ_FULLSCREEN=1 ROGUESQ_PRESENT_RING=$R/ring_$arm.txt $x ./RogueSquadron64Recomp
S
rm -f $R/tty_$arm.pid
echo "$(date +%T) $arm start tty idle=$i" >> $R/arms.log
osascript -e "tell application \"Terminal\" to do script \"exec zsh -f $L\"" > $R/tty_$arm.win 2>&1
/bin/sleep 2; gp=$(cat $R/tty_$arm.pid 2>/dev/null)
( for k in 1 2 3 4 5 6 7 8; do /bin/sleep 12; osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron64Recomp") to true' >/dev/null 2>&1; done ) & rp=$!
ps -o pcpu= -p $(pgrep -x Terminal | head -1) > /dev/null
( /bin/sleep $((HOLD/2)); top -l 2 -s 3 -n 6 -o cpu -stats pid,command,cpu | tail -7 > $R/tty_$arm.top ) &
/bin/sleep $HOLD; alive=0; [[ -n $gp ]] && kill -0 $gp 2>/dev/null && alive=1
[[ -n $gp ]] && kill -KILL $gp 2>/dev/null; kill $rp 2>/dev/null; kill -KILL $hp 2>/dev/null
echo "$(date +%T) $arm done tty alive=$alive pid=$gp" >> $R/arms.log
