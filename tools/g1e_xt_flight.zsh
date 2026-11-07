#!/bin/zsh
# s6934: WINDOWED sync dd4 16:9 keyed flight (no display lock, no fullscreen: the idle gate's two reasons do not apply). Same route as g1e_owner_quiet_arms.
# Settles flight vs pause (pause byte, craft pos, window frames) and takes the sync profile. usage: w.zsh tag hold "extra env"
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
R=$PWD/${OUT:-scratch/xt}; mkdir -p $R; A=$1; HOLD=${2:-235}; X=$3
EARLY=""; e=10
for i in $(seq 1 20); do if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi; EARLY="$EARLY$e:$k,"; e=$((e+4)); done
FL=""; t=95
for i in $(seq 1 100); do for k in a sl a sr; do FL="$FL$t:$k,"; t=$((t+2)); done; (( t > 520 )) && break; done
AP="${EARLY}${FL%,}"
FRONT=$(osascript -e 'tell application "System Events" to get name of first process whose frontmost is true' 2>/dev/null)
( cd build && exec env ROGUESQ_FORCE_SAVE_MISSION=1 ROGUESQ_FORCE_UNLOCK=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_GODMODE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_AUTOPILOT=$AP ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9 ROGUESQ_PRESENT_RING=$R/ring_$A.txt ROGUESQ_G1B=1 ROGUESQ_G1E_AQ=2 ${=X} ./${BIN:-RogueSquadron64Recomp} > $R/log_$A.txt 2>&1 ) &
gp=$!; /bin/sleep 4; [ -n "$FRONT" ] && osascript -e "tell application \"$FRONT\" to activate" >/dev/null 2>&1
P=$gp
shot(){ g=$(build/winctl find $P 2>/dev/null); /usr/sbin/screencapture -x -o -l${g%% *} $R/${A}_$1.png; }
/bin/sleep 116; shot t120; /bin/sleep 40; shot t160; /bin/sleep 5; shot t165
[ -n "$SAMPLE" ] && /usr/bin/sample $P 30 1 -mayDie -file $R/prof_$A.txt >/dev/null 2>&1
[ -n "$XT" ] && { /usr/bin/vmmap $P 2>/dev/null | /usr/bin/grep -m1 "__TEXT.*RogueSquadron64Recomp" > $R/base_$A.txt; env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcrun xctrace record --template "Time Profiler" --attach $P --time-limit 30s --output $R/xt_$A.trace > $R/xt_$A.log 2>&1; }
/bin/sleep $(( HOLD - 200 )) 2>/dev/null; shot end
alive=0; kill -0 $P 2>/dev/null && alive=1; kill -KILL $P 2>/dev/null
echo "$A alive=$alive crash=$(/usr/bin/grep -a -c 'CRASH\|caught signal' $R/log_$A.txt)" | tee -a $R/w.out
