#!/bin/zsh
# s7663 arms: A none, B env GFX_QOS=1 (witness ctl), C settings file (GFX_QOS + DD), D --preset window, E preset + env override
cd "$(dirname $0)/../../build" || exit 1
O=../scratch/s7663
printf '# test\nROGUESQ_GFX_QOS=1\nROGUESQ_DRAW_DISTANCE=2\nPATH=/evil\n' > $O/file.txt
arm() { local tag=$1; shift
  env -u ROGUESQ_SETTINGS -u ROGUESQ_PRESET ROGUESQ_NO_SAVE_WRITE=1 "$@" > $O/$tag.log 2>&1 &
  local p=$!; sleep 25; echo "$tag launched_pid=$p alive_pid=$(pgrep -x RogueSquadron64Recomp | tr '\n' ,)" >> $O/pids.txt
  kill -9 $p 2>/dev/null; pkill -9 -x RogueSquadron64Recomp; sleep 2; }
: > $O/pids.txt
arm A ROGUESQ_SETTINGS=0 ./RogueSquadron64Recomp
arm B ROGUESQ_SETTINGS=0 ROGUESQ_GFX_QOS=1 ./RogueSquadron64Recomp
arm C ./RogueSquadron64Recomp --settings $O/file.txt
arm D ./RogueSquadron64Recomp --preset window
arm E ROGUESQ_DRAW_DISTANCE=3 ./RogueSquadron64Recomp --preset=window
