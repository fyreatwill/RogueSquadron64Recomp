#!/bin/zsh
# s7475 boot A/B: does the slack canary fill change boot? Each arm boots ~${T:-75} s with no keys (attract plays itself),
# then SIGKILL. PASS for an arm = "[cineBody] call#1" (past the runMenuModelViewerScreen audio-slot wait) is logged.
# ARMS="name:ENV=V+ENV=V ..." (default off / a5 / z0 / a5 with STORE_DIAG writer watch).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
R=$PWD/scratch/${NAME:-s7475_boot}; mkdir -p $R
arms=(${=${ARMS:-off:ROGUESQ_S7475_CANARY=0 a5:ROGUESQ_S7475_CANARY=1 z0:ROGUESQ_S7475_CANARY=1+ROGUESQ_S7475_FILL=0 a5sd:ROGUESQ_S7475_CANARY=1+ROGUESQ_STORE_DIAG=1}})
for s in $arms; do a=${s%%:*}; x=${s#*:}; x=${x//+/ }
  ( cd build && exec env ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FPS60=1 ${=x} ./RogueSquadron64Recomp ) > $R/log_$a.txt 2>&1 & gp=$!
  t=0; while (( t < ${T:-75} )); do /bin/sleep 5; t=$((t+5)); kill -0 $gp 2>/dev/null || break; grep -aq '\[cineBody\] call#1' $R/log_$a.txt && (( t >= 40 )) && break; done
  kill -9 $gp 2>/dev/null; pkill -9 -x RogueSquadron64Recomp 2>/dev/null; /bin/sleep 2
  cb=$(grep -ac '\[cineBody\] call#1' $R/log_$a.txt); sp=$(grep -a '\[spin-yield\] site=menuModelViewer' $R/log_$a.txt | tail -1 | grep -o 'n=[0-9]*')
  echo "arm=$a t=$t cineBody=$cb mmv_spin=${sp:-n=0} hits=$(grep -ac 'tail-hit' $R/log_$a.txt) sstore=$(grep -ac 'slack-store' $R/log_$a.txt) wctl=$(grep -ac 'watch-ctl PASS' $R/log_$a.txt)" | tee -a $R/out.txt
done
