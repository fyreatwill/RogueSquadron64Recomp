#!/bin/zsh
# s7774: one owner-route run (normal boot on the owner save read-only -> first SELECT YOUR CRAFT -> mission flight ->
# PAUSE/ABORT -> MISSION FAILED -> hangar -> re-entry craft select; s6995 route_long autopilot) with ROGUESQ_S7774_SLOTS=1,
# then tools/s7774_slot_scan.py on the log. usage: tools/s7774_slot_run.zsh <name> [env words...]  (SECS default 300)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 2; }
N=${1:?name}; shift; O=$PWD/scratch/s7774/$N; SV=build/saves/rs64.n64.us.1.0.bin; mkdir -p $O
cp -p $SV $O/save_before.bin || exit 3
( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_S7774_SLOTS=1 \
    ROGUESQ_AUTOPILOT=$(cat ../scratch/s6995/route_long.txt) ROGUESQ_AUTOPILOT_HOLD_MS=250 "$@" ./RogueSquadron64Recomp ) > $O/run.log 2>&1 &
P=$!; S=$(date +%s)
while (( $(date +%s) - S < ${SECS:-300} )); do
  sleep 10; e=$(( $(date +%s) - S )); kill -0 $P 2>/dev/null || break
  g=$(build/winctl find $P 2>/dev/null) && /usr/sbin/screencapture -x -o -l${g%% *} $O/w_$(printf %03d $e).png
done
a=1; kill -0 $P 2>/dev/null || a=0
kill -9 $P 2>/dev/null; wait 2>/dev/null
python3 tools/s7774_slot_scan.py $O/run.log; r=$?
echo "tag=s7774_$N alive=$a crash=$(grep -c -E 'CRASH|SIGSEGV|SIGBUS|Failed to find function' $O/run.log) scan_rc=$r"
cmp -s $SV $O/save_before.bin && echo save-unchanged || { echo SAVE-CHANGED; exit 5; }
