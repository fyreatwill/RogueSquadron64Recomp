#!/bin/zsh
# s6738: port, NO input, NO fb dumps (full speed); tight-loop window captures through the boot intro cinematic.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
O=scratch/s6738/${1:-win1}; mkdir -p $O
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 4; }
( cd build && exec env ROGUESQ_NO_PKILL=1 ${=XE} ./RogueSquadron64Recomp ) > $O/run.log 2>&1 &
P=$!; S=$(python3 -c 'import time;print(time.time())'); c=0
sleep 1
while (( $(python3 -c "import time;print(int(time.time()-$S))") < ${SECS:-55} )); do
  g=$(build/winctl find $P 2>/dev/null) || { sleep 0.2; continue; }
  t=$(python3 -c "import time;print('%07.2f'%(time.time()-$S))")
  /usr/sbin/screencapture -x -o -l${g%% *} $O/w_${t}.png; c=$((c+1))
done
kill -9 $P; wait 2>/dev/null; echo caps=$c
