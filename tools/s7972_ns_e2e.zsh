#!/bin/zsh
# s7972 class NS e2e: the data root's volume is FULL while the game runs (the non-save writers too: controls.json from
# F6 Save, the EEPROM save, the stored ROM copy at boot). One 160 MB APFS image per arm, private game copy, owner save
# COPIED (build/saves untouched), one game at a time. Saving ON plus the s7969 plant ROGUESQ_S7969_SAVE_TICK_MS=1500
# (a save write every 1.5 s) and ROGUESQ_BIND_PANEL_TEST=2 (presses the F6 panel's Save at input poll 1200).
# Arms:  ctl    image not full (positive control: controls.json written, save mtime moves, 0 temps left)
#        run    image filled to ENOSPC ${FILL:-3} s after launch (before the panel Save): writers must fail cleanly
#        boot   image filled BEFORE launch, ROM given only as a candidate name (so boot tries to store the ROM copy)
#        boot2  relaunch on the same still-full image as boot (reads whatever boot left)
# Per arm: alive at watch end, HUP-to-exit ms, crash lines, controls.json + save sha before/after, "[controls]" result,
# leftover *.tmp.* / *.temp.* files, stored-ROM size, [s7969-ue] / [s7972] lines.
# s7972 finding: under the s7969 relocation (image = external volume) controls.json / audio_device.txt resolved next to the
# CACHED exe copy, not the game folder. Scored per arm: ctl_in_game (the [controls] Saved/FAILED path is in the game
# folder) and audio_in_game (audio preference read from the game folder's audio_device.txt). Phase old = pre-fix exe
# (EXE=...) or the fix off (P=mut: ROGUESQ_S7972_BASEPATH=1): both must read 0/0 = the bug reproduces.
# Output scratch/s7972/${P}_summary.txt; exit 0 = every arm as expected for phase P (old|new).
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7972; P=${1:-new}; EXE=${EXE:-$R/build/RogueSquadron64Recomp}; WATCH=${WATCH:-30}; FILL=${FILL:-3}
mkdir -p $S; : > $S/${P}_summary.txt; bad=0; T=/tmp/s7972_e2e; SV=rs64.n64.us.1.0.bin; ROM=rs64.n64.us.1.0.z64
cleanup(){ for m in $T/m_*(N); do hdiutil detach -quiet -force $m 2>/dev/null; done; rm -rf $T; }; cleanup; mkdir -p $T
CRD=~/Library/Logs/DiagnosticReports; cr0=$(ls $CRD 2>/dev/null | grep -c RogueSquadron)
now(){ perl -MTime::HiRes=time -e 'printf "%d\n", time*1000'; }
sha(){ [ -f $1 ] && shasum $1 | cut -c1-12 || print none; }
fill(){ dd if=/dev/zero of=$1/filler1 bs=1m 2>/dev/null; dd if=/dev/zero of=$1/filler2 bs=4k 2>/dev/null; dd if=/dev/zero of=$1/filler3 bs=512 2>/dev/null; df -k $1 | tail -1 | awk '{print $4}'; }
M=; G=
for arm in ctl run boot boot2; do
  n=$arm; L=$S/${P}_$n.log
  if [[ $arm != boot2 ]]; then
    M=$T/m_$n
    hdiutil create -quiet -size 160m -fs APFS -volname NS$n $T/$n.dmg && hdiutil attach -quiet -nobrowse -mountpoint $M $T/$n.dmg \
      || { print "$P $n FAIL: image" | tee -a $S/${P}_summary.txt; bad=1; continue; }
    G=$M/game; mkdir -p $G/saves
    cp $EXE $G/RogueSquadron64Recomp
    print 'BlackHole 2ch' > $G/audio_device.txt   # not the built-in default, so "read from the game folder" is visible
    if [[ $arm = boot ]]; then cp $R/build/rogue_squadron.z64 $G/rogue_squadron.z64; else cp $R/build/$ROM $G/$ROM; fi
    cp $R/build/saves/$SV $G/saves/$SV; cp $R/build/saves/$SV $G/saves/$SV.bak
    # previous controls.json: a valid file the panel Save would replace (s7666 format: written by ctl in a seed pass)
    [ -f $S/seed_controls.json ] && cp $S/seed_controls.json $G/controls.json
  fi
  free0=-; [[ $arm = boot ]] && free0=$(fill $M)
  c_pre=$(sha $G/controls.json); s_pre=$(sha $G/saves/$SV); csz_pre=$(stat -f %z $G/controls.json 2>/dev/null)
  ( cd $G && exec env -u ROGUESQ_SETTINGS -u ROGUESQ_NO_SAVE_WRITE ROGUESQ_DI_DIALOG=0 ROGUESQ_RO_DIALOG=0 ROGUESQ_UE_DIALOG=0 \
      ROGUESQ_NO_PKILL=1 ROGUESQ_S7969_SAVE_TICK_MS=1500 ROGUESQ_BIND_PANEL_TEST=2 $([[ $P = mut ]] && print ROGUESQ_S7972_BASEPATH=1) ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!; t0=$(now); freef=-
  if [[ $arm = run ]]; then sleep $FILL; freef=$(fill $M); tf=$(( $(now) - t0 )); else tf=-; fi
  cl_before_fill=$(grep -ac '^\[controls\] \(Saved\|SAVE FAILED\)' $L)
  died=-; st=-
  for i in $(seq 1 $(( WATCH * 2 ))); do sleep 0.5; kill -0 $p 2>/dev/null || { died=$(( $(now) - t0 )); wait $p; st=$?; break; }; done
  alive=dead; kill -0 $p 2>/dev/null && alive=alive; hup=-
  if [[ $alive = alive ]]; then th=$(now); kill -HUP $p
    for i in $(seq 1 30); do sleep 0.5; kill -0 $p 2>/dev/null || break; done
    if kill -0 $p 2>/dev/null; then hup=hung; kill -9 $p; wait $p; st=$?; else hup=$(( $(now) - th )); wait $p; st=$?; fi
  fi
  c_post=$(sha $G/controls.json); s_post=$(sha $G/saves/$SV); csz=$(stat -f %z $G/controls.json 2>/dev/null); ssz=$(stat -f %z $G/saves/$SV 2>/dev/null)
  ctlres=$(grep -ao '^\[controls\] \(Saved to\|SAVE FAILED\)' $L | tail -1 | sed 's/\[controls\] //; s/ /_/g')
  temps=$(find $G \( -name '*.tmp.*' -o -name '*.temp.*' -o -name '*.tmp' -o -name '*.temp' \) 2>/dev/null | wc -l | tr -d ' ')
  tempn=$(find $G \( -name '*.tmp*' -o -name '*.temp*' \) 2>/dev/null | sed "s|$G/||" | tr '\n' ',')
  cin=$(grep -a '^\[controls\] \(Saved to\|SAVE FAILED\)' $L | tail -1 | grep -ac "${M:t}/game/controls.json")
  ain=$(grep -ac "audio-route\] preference from .*${M:t}/game/audio_device.txt: 'BlackHole 2ch'" $L)
  rsz=$(stat -f %z $G/$ROM 2>/dev/null); ue=$(grep -ac '\[s7969-ue\] save' $L); fw=$(grep -ac 'Failed to write' $L)
  s72=$(grep -ac '\[s7972' $L); c=$(grep -acE 'CRASH|SIGSEGV|SIGBUS|SIGABRT|terminate called|libc\+\+abi' $L)
  romstore=$(grep -ac 'storing the ROM copy failed' $L); boot_ok=$(grep -acE '\[ai\]|osViSwapBuffer|\[vi\]|gfx task' $L)
  [[ $arm = ctl && -f $G/controls.json && ! -f $S/seed_controls.json ]] && { cp $G/controls.json $S/seed_controls.json; print -n ' ' >> $S/seed_controls.json; }
  print "$P $n: alive=$alive died_ms=$died status=$st fill_ms=$tf free_after_fill_kb=${freef}${free0} hup_exit_ms=$hup crashlines=$c \
controls=[$ctlres] ctl_in_game=$cin audio_in_game=$ain controls_before_fill=$cl_before_fill c_sha=$c_pre->$c_post c_size=${csz_pre:-none}->${csz:-none} s_sha=$s_pre->$s_post s_size=${ssz:-none} \
temps=$temps [$tempn] rom_size=${rsz:-none} romstore_fail=$romstore ue_lines=$ue failed_lines=$fw s7972_lines=$s72" | tee -a $S/${P}_summary.txt
  print -- "  last: $(grep -av 'pe gate\|threadPresent' $L | tail -2 | tr '\n' '|' | cut -c1-240)" >> $S/${P}_summary.txt
  ok=PASS; fx=$([[ $P = new ]] && print 1 || print 0)
  [[ $alive = alive && $hup != hung && $hup != - && $c = 0 && $s_pre = $([[ $arm = ctl ]] && print $s_pre || print $s_post) && $ssz = 512 ]] || ok=FAIL
  case $arm in
    ctl)  [[ $ctlres = Saved_to && $s_pre != $s_post && $temps = 0 && $cin = $fx && $ain = $fx ]] || ok=FAIL
          [[ $P = new && $c_pre = $c_post ]] && ok=FAIL ;;   # new: the game folder's controls.json really replaced
    run)  [[ $cl_before_fill = 0 && $c_pre = $c_post && $cin = $fx && $ain = $fx ]] || ok=FAIL
          [[ $P = new && ( $ctlres != SAVE_FAILED || $temps != 0 ) ]] && ok=FAIL ;;
    boot|boot2) [[ $c_pre = $c_post && $temps = 0 ]] || ok=FAIL ;;
  esac
  [[ $ok = FAIL ]] && bad=1; print "$P $n $ok" | tee -a $S/${P}_summary.txt
  [[ $arm != boot ]] && hdiutil detach -quiet -force $M 2>/dev/null
done
hdiutil detach -quiet -force $T/m_boot 2>/dev/null
cr1=$(ls $CRD 2>/dev/null | grep -c RogueSquadron); print "$P new_crash_reports=$(( cr1 - cr0 ))" | tee -a $S/${P}_summary.txt
cleanup; print "$P VERDICT $([[ $bad = 0 ]] && print PASS || print FAIL)" | tee -a $S/${P}_summary.txt; exit $bad
