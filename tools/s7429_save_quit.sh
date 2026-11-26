#!/bin/zsh
# s7429 class CL: save durability on quit. Part 1 = kill-at-offset harness (tools/s7429_save_quit/harness.cpp) against
# the real librecomp files.cpp, both finalize arms in one binary. Part 2 = game runtime in a COPIED folder (never
# build/saves): loader .bak fallback for a short final file, its control (no .bak -> zero-fill), and one unforced write
# run (ROGUESQ_NO_SAVE_WRITE unset in the copy only) checking the rename path leaves no .temp and a whole save.
# Exit 0 = H-durable after the fix, 1 = a window remains, 3 = control failed.
ROOT=${0:A:h:h}; cd $ROOT; L=lib/N64ModernRuntime/librecomp; rc=0
clang++ -std=c++20 -O1 -I$L/include/librecomp -DFILES_CPP="\"$ROOT/$L/src/files.cpp\"" -DLOADER_FALLBACK=0 \
  tools/s7429_save_quit/harness.cpp -o /tmp/s7429_h || exit 3
rm -rf /tmp/s7429_d; OLD=$(env ROGUESQ_S7429_OLD_FINALIZE=1 /tmp/s7429_h /tmp/s7429_d 2000 3000 2>/dev/null); orc=$?
rm -rf /tmp/s7429_d; NEW=$(/tmp/s7429_h /tmp/s7429_d 4000 3000 2>/dev/null); nrc=$?
print "harness old-finalize: $OLD rc=$orc"; print "harness new-finalize: $NEW rc=$nrc"
[[ $orc = 1 ]] || { print "CONTROL FAIL: old finalize showed no bad load"; exit 3; }
[[ $nrc = 0 ]] || rc=1
W=/tmp/rs64_s7429; S=$W/saves/rs64.n64.us.1.0.bin
run() { # name secs extra-env...
  local n=$1 secs=$2; shift 2
  (cd $W && env -u ROGUESQ_NO_SAVE_WRITE "$@" ./RogueSquadron64Recomp > $W/$n.log 2>&1) & local pid=$!; sleep $secs
  local gp=$(pgrep -f "^./RogueSquadron64Recomp" | head -1); [[ -n $gp ]] && kill -9 $gp; wait $pid 2>/dev/null
}
setup() { rm -rf $W; mkdir -p $W/saves
  cp $ROOT/build/RogueSquadron64Recomp $ROOT/build/rogue_squadron.z64 $ROOT/build/rs64.n64.us.1.0.z64 $W/ 2>/dev/null
  cp $ROOT/build/saves/rs64.n64.us.1.0.bin $S; cp $S $S.bak; }
setup; : > $S; run R1 15 ROGUESQ_NO_SAVE_WRITE=1
R1=$(grep -ac 's7429-io.*loaded the complete .bak' $W/R1.log); print "R1 short final + whole .bak: fallback lines=$R1"
setup; : > $S; rm $S.bak; run R1c 15 ROGUESQ_NO_SAVE_WRITE=1
R1c=$(grep -ac 's7357-io.*zero-filling' $W/R1c.log); print "R1c control short final, no .bak: zero-fill lines=$R1c"
[[ $R1c -ge 1 ]] || { print "CONTROL FAIL: short-file path not reached"; exit 3; }
[[ $R1 -ge 1 ]] || rc=1
setup; m0=$(stat -f %m $S); sleep 1; run R2 40 ROGUESQ_FORCE_UNLOCK=1 ROGUESQ_FORCE_SAVE_MISSION=3
m1=$(stat -f %m $S); sz=$(stat -f %z $S)
print "R2 write run: mtime_changed=$([[ $m1 != $m0 ]] && print 1 || print 0) size=$sz temp_left=$(ls $S.temp* 2>/dev/null | wc -l | tr -d " ") bak=$([[ -e $S.bak ]] && print 1 || print 0)"
[[ $sz = 512 ]] || rc=1
print "VERDICT $([[ $rc = 0 ]] && print H-durable || print window)"; exit $rc
