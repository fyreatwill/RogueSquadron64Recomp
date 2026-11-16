#!/bin/zsh
# s7428 class CK runtime arms: audio_device.txt vs ROGUESQ_AUDIO_DEVICE precedence, and F9 persistence under
# ROGUESQ_NO_SAVE_WRITE. Runs a COPY of the game folder (never build/saves). Exit 0 = all arms as expected, 1 = drift,
# 2 = VOID (injected Return never reached the game: key injection broken, screen locked/asleep),
# 3 = positive control (arm D: F9 without NO_SAVE_WRITE must rewrite the file) failed.
# SOAK_NEEDS_IDLE=300
ROOT=${0:A:h:h}; W=/tmp/rs64_s7428; rm -rf $W; mkdir -p $W/saves
cp $ROOT/build/RogueSquadron64Recomp $ROOT/build/rogue_squadron.z64 $ROOT/build/rs64.n64.us.1.0.z64 $W/
cp $ROOT/build/saves/rs64.n64.us.1.0.bin $W/saves/
WC=$ROOT/build/winctl; rc=0
arm() { # name nsw envdev f9
  local n=$1 nsw=$2 dev=$3 f9=$4; print plantfile > $W/audio_device.txt
  local -a E=(env -u ROGUESQ_AUDIO_DEVICE -u ROGUESQ_NO_SAVE_WRITE); [[ $nsw = 1 ]] && E+=(ROGUESQ_NO_SAVE_WRITE=1)
  [[ -n $dev ]] && E+=(ROGUESQ_AUDIO_DEVICE=$dev)
  (cd $W && $E ./RogueSquadron64Recomp > $W/$n.log 2>&1) & local pid=$!; sleep 20
  local gp=$(pgrep -f "^./RogueSquadron64Recomp" | head -1)
  if [[ $f9 = 1 && -n $gp ]]; then $WC activate $gp >/dev/null 2>&1; sleep 1; $WC key $gp 36 250 >> $W/$n.winctl 2>&1; sleep 2; $WC key $gp 101 250 >> $W/$n.winctl 2>&1; sleep 3; fi
  [[ -n $gp ]] && kill -9 $gp; wait $pid 2>/dev/null
  [[ $f9 = 1 ]] && ! grep -aq 'site=key n=1 ev=down key=return' $W/$n.log && { print "$n VOID: injected Return not seen"; return 2; }
  print "$n file=$(cat $W/audio_device.txt) $(grep -m1 'preference from' $W/$n.log | cut -c1-110) | $(grep -m1 'F9 ->' $W/$n.log | cut -c1-120)"
}
A=$(arm A 1 xyzzyA 0); print $A; [[ $A == *"from ROGUESQ_AUDIO_DEVICE: 'xyzzyA'"* ]] || rc=1
B=$(arm B 1 "" 0); print $B; [[ $B == *"audio_device.txt: 'plantfile'"* ]] || rc=1
C=$(arm C 1 "" 1); [[ $? = 2 ]] && { print $C; exit 2; }; print $C; [[ $C == *"file=plantfile"* && $C == *"NOT saved"* ]] || rc=1
D=$(arm D 0 "" 1); [[ $? = 2 ]] && { print $D; exit 2; }; print $D; [[ $D != *"file=plantfile"* && $D == *"saved to"* ]] || { print "CONTROL FAIL"; exit 3; }
print "VERDICT $([[ $rc = 0 ]] && print H-env-wins || print drift)"; exit $rc
