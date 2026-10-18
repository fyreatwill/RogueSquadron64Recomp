#!/bin/zsh
# s5393 positive control: does winctl key reach the game ([pad-sdl] site=key)? usage: m6_keyctl.sh
set -u
ROOT=$(git rev-parse --show-toplevel); BUILD=$ROOT/build; OUT=$ROOT/scratch/agent/m6/keyctl; mkdir -p $OUT; L=$OUT/run.log; K=$OUT/keys.log; : > $K
echo "trusted=$($BUILD/winctl trusted 2>&1)" >> $K
pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true
( cd $BUILD && exec env ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_AUDIO_UCODE=1 PROBE_PHASE_WIDTH=512 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ./RogueSquadron64Recomp ) > $L 2>&1 &
p=$!
for i in $(seq 1 120); do grep -aq 'origin=0x00790400' $L && break; sleep 1; done
echo "title t=$i" >> $K
echo "lock=$(/usr/sbin/ioreg -n Root -d1 | grep -o '"CGSSessionScreenIsLocked"=[A-Za-z]*')" >> $K
echo "find=$($BUILD/winctl find $p 2>&1) rc=$?" >> $K
echo "front=$(/usr/bin/osascript -e 'tell application "System Events" to get name of first process whose frontmost is true' 2>&1)" >> $K
/usr/sbin/screencapture -x $OUT/title.png >> $K 2>&1
for n in 1 2 3 4 5 6; do
  $BUILD/winctl activate $p >> $K 2>&1; echo "act rc=$?" >> $K
  $BUILD/winctl key $p 36 250 >> $K 2>&1; echo "key36 rc=$? sdlkeys=$(grep -ac 'site=key' $L) origin=$(grep -a 'origin=' $L | tail -1 | grep -o 'origin=0x[0-9A-F]*')" >> $K
  sleep 4
done
kill -9 $p 2>/dev/null; wait $p 2>/dev/null
echo "sdlkey_rows=$(grep -ac 'site=key' $L)" | tee -a $K
