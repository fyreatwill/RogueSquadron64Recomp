#!/bin/zsh
# s7270: AT THE MOVIES, 21:9 FPS60 dd4 WIDEWIN, same-run tog3 on the WIDEWIN stack, (mach s)%3: ph0 off (R0, merge off), ph1 = auto stack
# (R88 merge0.4 E16), ph2 = positive control R=1 (all wide-only cells skipped) + merge. Frontmost keeper per s7264. usage: mov.zsh <name> [secs=960]
# EXTRA="env..." adds env (t4: ROGUESQ_DD_OFFMAPCULL=tog3 _R=-1,-1,0 _K=0,0,0 _H=off = s7039 ground-removing control in ph2 only).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
R=$PWD/scratch/s7270; N=$1; S=${2:-960}
AP=$(sed -n 's/^port AP: //p' scratch/s6792/mov/press.txt | sed 's/13:w1024/13:w2048/')
( /bin/sleep 180; exec scratch/s6914/g5b_capture RogueSquadron64Recomp $R/$N.raw 384 164 0 770 > $R/cap_$N.txt 2>&1 ) &
( cd scratch/s6908/wd && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT=$AP ROGUESQ_LOG_PHASE=1 ROGUESQ_STORE_DIAG=0 ROGUESQ_CULL_SPIKE=1 \
  ROGUESQ_FPS60=1 ROGUESQ_ASPECT=21:9 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_DD_WIDEWIN_STACK=0 \
  ROGUESQ_DD_WIDEWIN_R=88 ROGUESQ_DD_WIDEWIN_R_TOG=3 ROGUESQ_DD_WIDEWIN_R3=0,88,1 ROGUESQ_DD_WIDEWIN_MERGE=0.4 ROGUESQ_DD_WIDEWIN_MERGE_E=16 \
  ROGUESQ_DD_WIDEWIN_MERGE_TOG=3 ROGUESQ_DD_WIDEWIN_MERGE3=0,1,1 ${=EXTRA} ./RogueSquadron64Recomp ) > $R/run_$N.log 2>&1 &
p=$!
( for k in $(seq 1 $((S/10))); do /bin/sleep 10; osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron64Recomp") to true' >/dev/null 2>&1; done ) & fp=$!
/bin/sleep $S; kill $fp 2>/dev/null; kill -9 $p; pkill -9 -x RogueSquadron64Recomp; /bin/sleep 3; pkill -f "s7270/$N.raw"
echo $N crash $(grep -a -cE 'CRASH|SIGSEGV|SIGBUS' $R/run_$N.log); tail -1 $R/cap_$N.txt | cut -c1-160
