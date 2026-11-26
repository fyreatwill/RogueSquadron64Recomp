#!/bin/zsh
# s7964 class RO e2e: the game folder is unwritable. 3 arms, one game at a time, ${SECS:-10} s each, SIGKILL; owner save COPIED
# into a private dir (build/saves never touched), NO_SAVE_WRITE=1 as always. Arms: rw (writable control), chmod (chmod -R a-w),
# dmg (folder on a read-only UDRO disk image). Per arm: last update_screen #, VI width>0 seen, exit kind, stderr lines naming a
# failed write, files the run created. Output: scratch/s7964/${P}_<arm>.log + ${P}_summary.txt.
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7964; P=${1:-new}; SECS=${SECS:-10}; mkdir -p $S
mk(){ rm -rf $1 2>/dev/null; chmod -R u+w $1 2>/dev/null; rm -rf $1; mkdir -p $1/saves
  for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 audio_device.txt controls.json; do [ -e $R/build/$f ] && cp $R/build/$f $1/$f; done
  cp $R/build/saves/rs64.n64.us.1.0.bin $1/saves/; }
run(){ arm=$1; dir=$2; shift 2; nsw=ROGUESQ_NO_SAVE_WRITE=1; [ "$1" = save ] && { nsw="-u ROGUESQ_NO_SAVE_WRITE"; shift; }; nsw=(${=nsw}); L=$S/${P}_$arm.log; find $dir -print | sort > $S/${P}_${arm}_before.txt
  ( cd $dir && exec env -u ROGUESQ_SETTINGS $nsw ROGUESQ_NO_PKILL=1 "$@" ./RogueSquadron64Recomp ) > $L 2>&1 & p=$!
  sleep $SECS; if kill -0 $p 2>/dev/null; then kind=alive; kill -9 $p; else kind=exited; fi; wait $p 2>/dev/null; rc=$?
  find $dir -print | sort > $S/${P}_${arm}_after.txt
  new=$(comm -13 $S/${P}_${arm}_before.txt $S/${P}_${arm}_after.txt | sed "s|^$dir/||" | tr '\n' ' ')
  us=$(grep -o 'update_screen #[0-9]*' $L | tail -1 | tr -dc 0-9); w=$(grep -c '\[phase\] vi_width=320' $L)
  fw=$(grep -ciE 'read-only|permission denied|cannot (open|write|create)|failed to (open|write|create)|EROFS|EACCES|errno' $L)
  cr=$(grep -cE 'CRASH|SIGSEGV|SIGBUS|SIGABRT|terminate called|Assertion' $L)
  ro=$(grep -m1 -o '\[s7964-ro\] game folder [^:]*:.*' $L | sed -E 's/: .*(saving=[0-9] dialog=[a-z-]+).*/ \1/'); dd=$(grep -c 'dialog dismissed' $L)
  echo "$P $arm: ro=[${ro:-none}] dismissed=$dd kind=$kind rc=$rc update_screen=${us:-0} vi320=$w failwrite_lines=$fw crash_lines=$cr created=[$new]" | tee -a $S/${P}_summary.txt; }
: > $S/${P}_summary.txt
mk $S/rw; run rw $S/rw
mk $S/ro; chmod -R a-w $S/ro; run chmod $S/ro; chmod -R u+w $S/ro; rm -rf $S/ro
mk $S/dmgsrc; rm -f $S/ro.dmg; hdiutil create -quiet -srcfolder $S/dmgsrc -format UDRO -volname rs64ro $S/ro.dmg
mp=$(hdiutil attach -readonly -nobrowse $S/ro.dmg | awk -F'\t' '/rs64ro/{print $NF}'); echo "dmg mount=$mp" >> $S/${P}_summary.txt
touch "$mp/probe" 2>/dev/null && echo "dmg CONTROL writable?! FAIL" >> $S/${P}_summary.txt || echo "dmg CONTROL touch refused PASS" >> $S/${P}_summary.txt
run dmg "$mp"
# saving ON only here: the folder is a private copy on an immutable image, so no save can be written anywhere.
run dmg_dialog "$mp" save
run dmg_nodlg "$mp" save ROGUESQ_RO_DIALOG=0; hdiutil detach -quiet "$mp"; rm -rf $S/dmgsrc $S/rw $S/ro.dmg
