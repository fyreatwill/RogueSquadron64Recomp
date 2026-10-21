#!/bin/zsh
# s5469: in-mission hardware write-watchpoint census on guest words 0x375B0 / 0x37580..0x375AF (m6-mission-end-trigger).
# Game raises a debugger trap at swap ROGUESQ_TRAP_AT_SWAP=${TRAPSWAP:-7600} and prints the host RDRAM base; lldb (fed from a pipe) then arms a
# POSITIVE CONTROL watch on 0x3470 (the per-swap counter; must hit), deletes it, arms the four real watches with auto-continue bt.
# usage: m6_wp375b0.sh <tag> [hold_secs]   (hold counts from mission onset; flag flip is ~swap 7775 ~ 4+ min after onset)
set -u
TAG=${1:?tag}; HOLD=${2:-420}
ROOT=$(git rev-parse --show-toplevel); OUT=$ROOT/scratch/agent/m6/$TAG; BUILD=$ROOT/build; mkdir -p $OUT; K=$OUT/keys.log; : > $K
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo "SCREEN LOCKED" | tee $OUT/summary; exit 4; }
AP=""; t=10; for i in $(seq 1 300); do if (( t > ${LATE:-520} )); then k=a; elif (( i % 2 == 0 || t > ${START_UNTIL:-74} )); then k=z; else k=start; fi; AP="$AP$t:$k,"; t=$((t+4)); done; AP=${AP%,}
[ -n "${AP_OVERRIDE:-}" ] && AP=$AP_OVERRIDE
COMMON=(ROGUESQ_AUTOPILOT=$AP ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_AUDIO_UCODE=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=240 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_TRAP_AT_SWAP=${TRAPSWAP:-7600} ${=XENV})
pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true
for att in 1 2 3 4 5; do
  L=$OUT/run.log; rm -f $L
  ( echo 'process attach -n RogueSquadron64Recomp -w'; echo 'process handle SIGSEGV -s true -n true -p true'
    for fn in spawnSceneDebrisAndEffectCluster spawnNpcDestructionDebris requestMissionTransitionMode; do
      echo "breakpoint set -n $fn"; echo "breakpoint command add"
      print -r -- "expr -- (void)printf(\"BPHIT $fn a0=%llx a1=%llx a2=%llx\\n\", *(unsigned long long*)((char*)\$x1+32), *(unsigned long long*)((char*)\$x1+40), *(unsigned long long*)((char*)\$x1+48))"
      echo "continue"; echo "DONE"
    done
    echo 'breakpoint list'; echo continue
    while ! grep -aq 'trap-at-swap' $L 2>/dev/null; do sleep 1; done; sleep 3
    ad=$(grep -a 'trap-at-swap' $L | head -1 | sed 's/.*rdram=\(0x[0-9a-f]*\).*/\1/'); echo "ADDR $ad" >> $K
    echo 'process interrupt'; sleep 3
    echo "watchpoint set expression -w write -s 4 -- $((ad+0x3470))"; echo continue; sleep 5
    echo 'bt 4'; echo 'watchpoint delete -f'
    echo continue; for k in $(seq 1 600); do sleep 1; echo continue; done )| /usr/bin/script -q $OUT/lldb_att$att.log /usr/bin/lldb > /dev/null 2>&1 &
  lp=$!; sleep 3
  ( cd $BUILD && exec env "${COMMON[@]}" ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!; t0=$SECONDS
  has() { grep -aq "$1" $L; }
  fail() { echo "$1-att$att" >> $K; kill -9 $p 2>/dev/null; wait $p 2>/dev/null; cp $L $OUT/fail_att$att.log; kill -9 $lp 2>/dev/null; pkill -KILL -x lldb; }
  for i in $(seq 1 150); do has 'origin=0x00790400' && break; kill -0 $p 2>/dev/null || break; sleep 1; done
  has 'origin=0x00790400' || { fail notitle; continue; }
  for n in $(seq 1 12); do has 'origin=0x006AB400' && break; sleep 11; done
  has 'origin=0x006AB400' || { fail nohangar; continue; }
  sleep 15
  mt=-1
  for n in $(seq 1 40); do
    sleep 5; kill -0 $p 2>/dev/null || break
    grep -aqE "origin=0x(00)?${MISSION_RE:-690400}" $L && { mt=$SECONDS; break; }
  done
  [ $mt -ge 0 ] || { fail nomission; continue; }
  echo "att=$att mission t=$((mt-t0))" >> $K
  while kill -0 $p 2>/dev/null && [ $((SECONDS-mt)) -lt $HOLD ]; do sleep 5; done
  cp $L $OUT/run_pre.log; alive=0; kill -0 $p 2>/dev/null && alive=1
  kill -9 $p 2>/dev/null; wait $p 2>/dev/null; kill -9 $lp 2>/dev/null; pkill -KILL -x lldb
  echo "tag=$TAG att=$att hold=$((SECONDS-mt))s alive_at_end=$alive bp_scene=$(grep -ac 'BPHIT spawnScene' $L) bp_npc=$(grep -ac 'BPHIT spawnNpc' $L) bp_mtm=$(grep -ac 'BPHIT requestMission' $L)" | tee $OUT/summary
  exit 0
done
echo "tag=$TAG allattempts-failed" | tee $OUT/summary; exit 1
