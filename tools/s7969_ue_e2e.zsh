#!/bin/zsh
# s7969 class UE e2e: the volume holding the game folder (or only its saves/) goes away mid-run (USB stick pulled,
# `diskutil eject -force`, the stick sleeping). One 256 MB image per FS (APFS = control FS, ExFAT = what a stick has),
# private game copy, owner save COPIED (build/saves untouched), one game at a time. Saving ON plus the test plant
# ROGUESQ_S7969_SAVE_TICK_MS=1500 (rewrites save byte 0 with itself, so a save write happens every 1.5 s).
# Layouts:  whole  exe + ROM + saves/ on the image
#           data   exe + ROM in /tmp, saves/ a symlink onto the image (only the data volume vanishes)
# Arms per layout x FS:  keep   no detach (positive control: writes succeed, HUP quit flushes and exits)
#                        pull   `hdiutil detach -force` at ${DET:-10} s, watch ${WATCH:-20} s, then SIGHUP (the normal quit
#                               path: save flush + quick_exit), SIGKILL if not gone in 15 s
#   ExFAT only:          mutant pull with the fix off (whole: ROGUESQ_S7969_RELOC=0 must livelock = the bug reproduces;
#                               data: ROGUESQ_S7969_UE=0 must print a "Failed to write" per save)
#                        return (data) re-attach the image 6 s after the pull: a later save must succeed ("back" line)
#                        retry  (data) SIGHUP 6 s after the pull with ROGUESQ_S7969_RETRY_AUTO=8, re-attach 2 s later: the
#                               quit must save on a retry
# whole-layout arms must re-exec from a local copy (rs64_ue.h: "re-exec from local copy" + "running a local copy" = wired=1).
# One failure report = 2 "Failed to write" lines (ultramodern prints it, then our message_box callback does).
# Per arm: alive at end of watch, death time + wait status, "Failed to write" lines after the pull, [s7969-ue] lines,
# HUP-to-exit ms, crash reports.
# Output scratch/s7969/${P}_summary.txt; exit 0 = every arm as expected.
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7969; P=${1:-new}; DET=${DET:-10}; WATCH=${WATCH:-20}
mkdir -p $S; : > $S/${P}_summary.txt; bad=0; T=/tmp/s7969_e2e; SV=rs64.n64.us.1.0.bin
cleanup(){ for m in $T/m_*(N); do hdiutil detach -quiet -force $m 2>/dev/null; done; rm -rf $T; }; cleanup; mkdir -p $T
CRD=~/Library/Logs/DiagnosticReports; cr0=$(ls $CRD 2>/dev/null | grep -c RogueSquadron)
now(){ perl -MTime::HiRes=time -e 'printf "%d\n", time*1000'; }
crashl(){ grep -acE 'CRASH|SIGSEGV|SIGBUS|SIGABRT|terminate called' $1; }
for fs in APFS ExFAT; do for lay in whole data; do for arm in keep pull mutant return retry; do
  [[ $arm != keep && $arm != pull && $fs != ExFAT ]] && continue
  [[ ( $arm = return || $arm = retry ) && $lay != data ]] && continue
  n=${fs}_${lay}_${arm}; M=$T/m_$n; L=$S/${P}_$n.log
  hdiutil create -quiet -size 256m -fs $fs -volname UE$fs $T/$n.dmg && hdiutil attach -quiet -nobrowse -mountpoint $M $T/$n.dmg \
    || { print "$P $n FAIL: image" | tee -a $S/${P}_summary.txt; bad=1; continue; }
  if [[ $lay = whole ]]; then G=$M/game; mkdir -p $G/saves; else G=$T/g_$n; mkdir -p $G $M/saves; ln -s $M/saves $G/saves; fi
  for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 audio_device.txt controls.json; do [ -e $R/build/$f ] && cp $R/build/$f $G/$f; done
  cp $R/build/saves/$SV $G/saves/$SV; cp $R/build/saves/$SV $G/saves/$SV.bak
  me=(); [[ $arm = mutant && $lay = data ]] && me=(ROGUESQ_S7969_UE=0); [[ $arm = mutant && $lay = whole ]] && me=(ROGUESQ_S7969_RELOC=0)
  [[ $arm = retry ]] && me=(ROGUESQ_S7969_RETRY_AUTO=8)
  ( cd $G && exec env -u ROGUESQ_SETTINGS -u ROGUESQ_NO_SAVE_WRITE ROGUESQ_DI_DIALOG=0 ROGUESQ_RO_DIALOG=0 ROGUESQ_UE_DIALOG=0 \
      ROGUESQ_NO_PKILL=1 ROGUESQ_S7969_SAVE_TICK_MS=1500 $me ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!; t0=$(now); sleep $DET; pre_m=$(stat -f %m $G/saves/$SV 2>/dev/null); fl0=$(grep -ac 'Failed to write' $L)
  [[ $arm != keep ]] && { hdiutil detach -quiet -force $M 2>&1 | head -2; }
  tdet=$(( $(now) - t0 )); died=-; st=-; w=$WATCH
  if [[ $arm = return ]]; then sleep 6; hdiutil attach -quiet -nobrowse -mountpoint $M $T/$n.dmg; w=$(( WATCH - 6 )); fi
  if [[ $arm = retry ]]; then sleep 6; w=0; fi
  for i in $(seq 1 $(( w * 2 ))); do sleep 0.5; kill -0 $p 2>/dev/null || { died=$(( $(now) - t0 )); wait $p; st=$?; break; }; done
  alive=dead; kill -0 $p 2>/dev/null && alive=alive
  post_m=$(stat -f %m $G/saves/$SV 2>/dev/null); fl=$(( $(grep -ac 'Failed to write' $L) - fl0 ))
  hup=-
  if [[ $alive = alive ]]; then th=$(now); kill -HUP $p
    [[ $arm = retry ]] && { sleep 2; hdiutil attach -quiet -nobrowse -mountpoint $M $T/$n.dmg; }
    for i in $(seq 1 30); do sleep 0.5; kill -0 $p 2>/dev/null || break; done
    if kill -0 $p 2>/dev/null; then hup=hung; kill -9 $p; wait $p; st=$?; else hup=$(( $(now) - th )); wait $p; st=$?; fi
  fi
  ue=$(grep -ac '\[s7969-ue\] save' $L); ue_once=$(grep -ac '\[s7969-ue\] save folder gone' $L); flush=$(grep -ao 's7429-quit\] save flush=[0-9]' $L | tail -1)
  tick=$(grep -ac 's7969-ue\] plant' $L); c=$(crashl $L); wired=$(( $(grep -ac 's7969-ue\] exe on external volume: re-exec from local copy' $L) * $(grep -ac 's7969-ue\] running a local copy' $L) ))
  back=$(grep -ac 's7969-ue\] save folder back' $L); qns=$(grep -ac 's7969-ue\] quit: latest progress NOT saved' $L)
  qretry=$(grep -ac 's7969-ue\] quit: saved on retry' $L); qwo=$(grep -ac 's7969-ue\] quit: quitting without saving' $L)
  sz=$(stat -f %z $G/saves/$SV 2>/dev/null)
  print "$P $n: alive=$alive died_ms=$died status=$st det_ms=$tdet hup_exit_ms=$hup tick=$tick write_before=$([[ $pre_m != '' ]] && print ok) \
failed_lines_after=$fl ue_lines=$ue ue_gone=$ue_once back=$back quit_notsaved=$qns quit_retry_saved=$qretry quit_without=$qwo wired=$wired size=${sz:-none} flush=[$flush] crashlines=$c" | tee -a $S/${P}_summary.txt
  print -- "  last: $(grep -av 'pe gate\|threadPresent' $L | tail -2 | tr '\n' '|' | cut -c1-240)" >> $S/${P}_summary.txt
  ok=PASS
  wexp=$([[ $lay = whole ]] && print 1 || print 0)
  case $arm in
    keep)   [[ $alive = alive && $hup != hung && $hup != - && $fl = 0 && $c = 0 && $tick = 1 && $post_m != $pre_m && $wired = $wexp && $qns = 0 ]] || ok=FAIL ;;
    pull)   [[ $alive = alive && $hup != hung && $hup != - && $c = 0 && $wired = $wexp ]] || ok=FAIL
            [[ $ue_once = 1 && $fl -le 2 && $qns = 1 && $qwo = 1 && $back = 0 ]] || ok=FAIL ;;
    mutant) if [[ $lay = whole ]]; then [[ $hup = hung && $wired = 0 ]] || ok=FAIL
            else [[ $alive = alive && $fl -ge 3 && $ue_once = 0 && $back = 0 ]] || ok=FAIL; fi ;;
    return) [[ $alive = alive && $hup != hung && $c = 0 && $ue_once = 1 && $back = 1 && $qns = 0 && $sz = 512 ]] || ok=FAIL ;;
    retry)  [[ $hup != hung && $hup != - && $c = 0 && $ue_once = 1 && $qns = 1 && $qretry = 1 && $qwo = 0 && $sz = 512 ]] || ok=FAIL ;;
  esac
  [[ $ok = FAIL ]] && bad=1; print "$P $n $ok" | tee -a $S/${P}_summary.txt
  hdiutil detach -quiet -force $M 2>/dev/null
done; done; done
cr1=$(ls $CRD 2>/dev/null | grep -c RogueSquadron); print "$P new_crash_reports=$(( cr1 - cr0 ))" | tee -a $S/${P}_summary.txt
cleanup; print "$P VERDICT $([[ $bad = 0 ]] && print PASS || print FAIL)" | tee -a $S/${P}_summary.txt; exit $bad
