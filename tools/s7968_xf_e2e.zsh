#!/bin/zsh
# s7968 class XF e2e: the game folder sits on a non-APFS volume (exFAT / FAT32 USB stick). One 256 MB image per FS
# (APFS = control), private game copy on each (owner save COPIED, build/saves untouched), one game at a time except the
# 2nd-instance arm. Arms per FS, ${SECS:-20} s, SIGKILL:
#   save    saving ON: alive, no crash, [s7964-ro] says writable, [s7966-di] lock "held", no "Failed to" line; then the save
#           must be 512 bytes and identical to .bak or the seed, no temp left
#   second  start a 2nd copy 8 s into a saving run: it must log "another copy is already running" (flock works on this FS)
#   mods    mods/ holds junk.nrm with a quarantine xattr, so FAT/exFAT grow an AppleDouble "._junk.nrm" (what a downloaded mod
#           copied to a stick gets): fix boot must skip the sidecar, ROGUESQ_S7968_XF=0 mutant must open it; junk.nrm itself
#           must log "Error opening mod" in both (positive control)
#   relaunch saving ON again: alive, the save still 512 bytes
# Output scratch/s7968/${P}_summary.txt; exit 0 = every arm as expected.
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7968; P=${1:-new}; SECS=${SECS:-20}; mkdir -p $S; : > $S/${P}_summary.txt; bad=0
T=/tmp/s7968_e2e; SV=rs64.n64.us.1.0.bin
cleanup(){ for m in $T/m_*(N); do hdiutil detach -quiet -force $m 2>/dev/null; done; rm -rf $T; }; cleanup; mkdir -p $T
boot(){ ( cd $1 && exec env -u ROGUESQ_SETTINGS -u ROGUESQ_NO_SAVE_WRITE ROGUESQ_DI_DIALOG=0 ROGUESQ_NO_PKILL=1 "${@:3}" ./RogueSquadron64Recomp ) > $2 2>&1 & }
fin(){ local p=$1; local k=dead; kill -0 $p 2>/dev/null && k=alive; kill -9 $p 2>/dev/null; wait $p 2>/dev/null; print $k; }
cr(){ grep -cE 'CRASH|SIGSEGV|SIGBUS|SIGABRT|terminate called' $1; }
for fs in APFS ExFAT "MS-DOS FAT32"; do n=${fs%% *}; M=$T/m_$n
  hdiutil create -quiet -size 256m -fs "$fs" -volname XF$n $T/$n.dmg && hdiutil attach -quiet -nobrowse -mountpoint $M $T/$n.dmg || { print "$P $n FAIL: image" | tee -a $S/${P}_summary.txt; bad=1; continue; }
  G=$M/game; mkdir -p $G/saves $G/mods; for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 audio_device.txt controls.json; do [ -e $R/build/$f ] && cp $R/build/$f $G/$f; done
  cp $R/build/saves/$SV $G/saves/$SV; cp $R/build/saves/$SV $G/saves/$SV.bak; seed=$(shasum $G/saves/$SV | cut -c1-12)
  # save arm
  L=$S/${P}_${n}_save.log; boot $G $L; p=$!; sleep $SECS; k=$(fin $p)
  ro=$(grep -m1 -o '\[s7964-ro\] game folder [A-Za-z ]*' $L); di=$(grep -m1 -o '\[s7966-di\] instance lock [a-z]*' $L)
  ff=$(grep -c 'Failed to' $L); us=$(grep -o 'update_screen #[0-9]*' $L | tail -1 | tr -dc 0-9); c=$(cr $L)
  sz=$(stat -f %z $G/saves/$SV 2>/dev/null); h=$(shasum $G/saves/$SV | cut -c1-12); hb=$(shasum $G/saves/$SV.bak | cut -c1-12)
  tl=$(ls -a $G/saves | grep -c temp); ad=$(ls -a $G/saves | grep -c '^\._')
  ok=PASS; [[ $k = alive && $c = 0 && $ff = 0 && $ro = *writable* && $di = *held && $sz = 512 && $tl = 0 && ( $h = $hb || $h = $seed ) ]] || ok=FAIL
  [[ $ok = FAIL ]] && bad=1
  print "$P $n save $ok: $k us=${us:-0} crash=$c failed_lines=$ff ro=[$ro] di=[$di] size=$sz save=$([[ $h = $seed ]] && print seed || print new) temps=$tl appledouble=$ad" | tee -a $S/${P}_summary.txt
  # second-instance arm
  L1=$S/${P}_${n}_first.log; L2=$S/${P}_${n}_second.log; boot $G $L1; p1=$!; sleep 8; boot $G $L2; p2=$!; sleep 8; k2=$(fin $p2); k1=$(fin $p1)
  s2=$(grep -c 'another copy is already running' $L2); ok=PASS; [[ $s2 -ge 1 && $k1 = alive && $(cr $L1) = 0 && $(cr $L2) = 0 ]] || { ok=FAIL; bad=1; }
  print "$P $n second $ok: first=$k1 second=$k2 busy_line=$s2" | tee -a $S/${P}_summary.txt
  # mods arm: a real AppleDouble made by the FS itself (an xattr on a file in mods/ forces a ._ sidecar on FAT/exFAT).
  # stdout is block-buffered and SIGKILL drops it, so these boots run under stdbuf -o L. Two boots: fix, then the
  # ROGUESQ_S7968_XF=0 mutant. Positive control: the plain junk.nrm must log "Error opening mod" in BOTH boots.
  print -n 'not a mod' > $G/mods/junk.nrm; xattr -w com.apple.quarantine '0081;00000000;Safari;' $G/mods/junk.nrm 2>/dev/null
  hasad=$([[ -e $G/mods/._junk.nrm ]] && print 1 || print 0)
  for mv in fix mutant; do L=$S/${P}_${n}_mods_$mv.log; me=(); [[ $mv = mutant ]] && me=(ROGUESQ_S7968_XF=0)
    ( cd $G && exec env -u ROGUESQ_SETTINGS ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_NO_PKILL=1 $me stdbuf -o L ./RogueSquadron64Recomp ) > $L 2>&1 & p=$!
    sleep 10; k=$(fin $p); tried=$(grep -c 'Error opening mod .*/\._junk\.nrm' $L); ctl=$(grep -c 'Error opening mod .*/junk\.nrm' $L)
    skip=$(grep -c 'Skipping AppleDouble sidecar ._junk.nrm' $L); ok=PASS
    [[ $k = alive && $(cr $L) = 0 && $ctl -ge 1 ]] || ok=FAIL
    if [[ $hasad = 1 && $mv = fix ]]; then [[ $tried = 0 && $skip = 1 ]] || ok=FAIL; fi
    if [[ $hasad = 1 && $mv = mutant ]]; then [[ $tried -ge 1 ]] || ok=FAIL; fi
    if [[ $hasad = 0 ]]; then [[ $tried = 0 ]] || ok=FAIL; fi
    [[ $ok = FAIL ]] && bad=1
    print "$P $n mods_$mv $ok: $k appledouble_present=$hasad appledouble_opened=$tried skipped=$skip control_junk_error=$ctl" | tee -a $S/${P}_summary.txt
  done
  rm -f $G/mods/junk.nrm $G/mods/._junk.nrm
  # relaunch arm
  L=$S/${P}_${n}_relaunch.log; boot $G $L; p=$!; sleep 12; k=$(fin $p); sz=$(stat -f %z $G/saves/$SV); ok=PASS
  [[ $k = alive && $(cr $L) = 0 && $sz = 512 && $(grep -c 'Failed to' $L) = 0 ]] || { ok=FAIL; bad=1; }
  print "$P $n relaunch $ok: $k size=$sz" | tee -a $S/${P}_summary.txt
  hdiutil detach -quiet -force $M
done
cleanup; print "$P VERDICT $([[ $bad = 0 ]] && print PASS || print FAIL)" | tee -a $S/${P}_summary.txt; exit $bad
