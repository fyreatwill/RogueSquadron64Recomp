#!/bin/zsh
# s7966 class DI e2e: two copies of the game at once on ONE private game folder (owner save COPIED, build/saves untouched).
# Arms (each: instance 1, 3 s later instance 2, both ${SECS:-12} s, SIGKILL):
#   nosave   both ROGUESQ_NO_SAVE_WRITE=1 (agent default): 2nd must log busy + skip-nosave, no dialog
#   save     both saving ON (private copy), 2nd ROGUESQ_DI_DIALOG=0: 2nd must log busy + saving_was=1 dialog=off
#   dialog   both saving ON, 2nd with the dialog: 2nd must log dialog=show and never "dismissed" (modal is up)
#   mutant   both saving ON, ROGUESQ_S7966_NO_LOCK=1: 2nd must NOT log busy (control: the lock is what detects it)
#   relock   one instance after the SIGKILLs above: must log "held" (a killed holder leaves no stale lock)
# Output scratch/s7966/${P}_summary.txt. Exit 0 = every arm matches.
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7966; P=${1:-new}; SECS=${SECS:-12}; mkdir -p $S; : > $S/${P}_summary.txt; bad=0
mk(){ rm -rf $1; mkdir -p $1/saves
  for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 audio_device.txt controls.json; do [ -e $R/build/$f ] && cp $R/build/$f $1/$f; done
  cp $R/build/saves/rs64.n64.us.1.0.bin $1/saves/; }
launch(){ local L=$1 dir=$2; shift 2; ( cd $dir && exec env -u ROGUESQ_SETTINGS "$@" ROGUESQ_NO_PKILL=1 ./RogueSquadron64Recomp ) > $L 2>&1 & }
stat1(){ local L=$1; us=$(grep -o 'update_screen #[0-9]*' $L | tail -1 | tr -dc 0-9); cr=$(grep -cE 'CRASH|SIGSEGV|SIGBUS|SIGABRT|terminate called|Assertion' $L)
  di=$(grep -m1 -o '\[s7966-di\].*' $L | sed -E 's/ on [^;]*;/;/; s/ \(.*lock\)?$//'); dd=$(grep -c '\[s7966-di\] dialog dismissed' $L); print "us=${us:-0} crash=$cr dismissed=$dd di=[$di]"; }
pair(){ local arm=$1 e1=$2 e2=$3 want=$4; local D=$S/g_$arm; mk $D
  launch $S/${P}_${arm}_1.log $D ${=e1}; local p1=$!; sleep 3; launch $S/${P}_${arm}_2.log $D ${=e2}; local p2=$!; sleep $SECS
  local k1=dead k2=dead; kill -0 $p1 2>/dev/null && k1=alive; kill -0 $p2 2>/dev/null && k2=alive
  kill -9 $p1 $p2 2>/dev/null; wait $p1 $p2 2>/dev/null
  local s1="$(stat1 $S/${P}_${arm}_1.log)" s2="$(stat1 $S/${P}_${arm}_2.log)"; local tmp=$(ls -a $D/saves | grep -c 'temp\|tmp')
  local ok=PASS; [[ "$s2" == *"$want"* && $k1 = alive && $k2 = alive && "$s1" == *"lock held"* ]] || ok=FAIL
  [[ $arm = mutant ]] && { ok=PASS; [[ "$s2" == *"already running"* || "$s2" != *"unavailable"* || $k2 != alive ]] && ok=FAIL; }
  [[ $arm = dialog && "$s2" == *"dismissed=1"* ]] && ok=FAIL
  [[ $ok = FAIL ]] && bad=1
  print "$P $arm $ok: #1 $k1 $s1 | #2 $k2 $s2 | temps_left=$tmp" | tee -a $S/${P}_summary.txt; }
N="ROGUESQ_NO_SAVE_WRITE=1"; Y="-u ROGUESQ_NO_SAVE_WRITE"
pair nosave "$N" "$N" "saving_was=0 dialog=skip-nosave"
pair save "$Y" "$Y ROGUESQ_DI_DIALOG=0" "saving_was=1 dialog=off"
pair dialog "$Y" "$Y" "saving_was=1 dialog=show"
pair mutant "$Y ROGUESQ_S7966_NO_LOCK=1" "$Y ROGUESQ_S7966_NO_LOCK=1" "unavailable"
D=$S/g_save; launch $S/${P}_relock.log $D ROGUESQ_NO_SAVE_WRITE=1; p=$!; sleep 6; kill -9 $p 2>/dev/null; wait $p 2>/dev/null
r="$(stat1 $S/${P}_relock.log)"; ok=PASS; [[ "$r" == *"lock held"* ]] || { ok=FAIL; bad=1; }
print "$P relock $ok: $r" | tee -a $S/${P}_summary.txt
rm -rf $S/g_*; print "$P VERDICT $([[ $bad = 0 ]] && print PASS || print FAIL)" | tee -a $S/${P}_summary.txt; exit $bad
