#!/bin/zsh
# s7974 class NS-2 e2e: fresh install on a FULL data volume. The ROM is given only as the candidate name rogue_squadron.z64,
# so boot validates it and tries to store the copy rs64.n64.us.1.0.z64, which fails (ENOSPC). Before s7974 librecomp then
# had no ROM (valid = "stored copy hashes OK") and main printed "Place your ROM ... rogue_squadron.z64" next to that file.
# One 160 MB APFS image per arm, private game copy, owner save COPIED (build/saves untouched), one game at a time.
# Arms:  ctl   image NOT full, new exe          -> stored copy written, boots (positive control for the boot marker)
#        full  image full before launch, new exe -> [s7974-ns2] store-failed + load-from-memory, boots, no prompt, no copy left
#        mut   full, new exe + ROGUESQ_S7974_NOMEM=1 -> prompt, no boot (the bug reproduces with the fix off)
#        old   full, pre-fix exe (OLD_EXE)      -> prompt, no boot
# Boot marker: guest SI thread / gfx task forwarding lines ([si-thr] / [dpc-fwd]); [vi] alone also prints with no ROM.
# Output scratch/s7974/summary.txt; exit 0 = every arm as expected.
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7974; EXE=${EXE:-$R/build/RogueSquadron64Recomp}; OLD_EXE=${OLD_EXE:-/tmp/rs64_pre_s7974}
WATCH=${WATCH:-25}; mkdir -p $S; : > $S/summary.txt; bad=0; T=/tmp/s7974_e2e; SV=rs64.n64.us.1.0.bin; ROM=rs64.n64.us.1.0.z64
cleanup(){ for m in $T/m_*(N); do hdiutil detach -quiet -force $m 2>/dev/null; done; rm -rf $T; }; cleanup; mkdir -p $T
CRD=~/Library/Logs/DiagnosticReports; cr0=$(ls $CRD 2>/dev/null | grep -c RogueSquadron)
fill(){ dd if=/dev/zero of=$1/filler1 bs=1m 2>/dev/null; dd if=/dev/zero of=$1/filler2 bs=4k 2>/dev/null; dd if=/dev/zero of=$1/filler3 bs=512 2>/dev/null; df -k $1 | tail -1 | awk '{print $4}'; }
for arm in ctl full mut old; do
  L=$S/$arm.log; M=$T/m_$arm
  hdiutil create -quiet -size 160m -fs APFS -volname NS2$arm $T/$arm.dmg && hdiutil attach -quiet -nobrowse -mountpoint $M $T/$arm.dmg \
    || { print "$arm FAIL: image" | tee -a $S/summary.txt; bad=1; continue; }
  G=$M/game; mkdir -p $G/saves
  x=$EXE; [[ $arm = old ]] && x=$OLD_EXE
  [ -x $x ] || { print "$arm FAIL: no exe $x" | tee -a $S/summary.txt; bad=1; continue; }
  cp $x $G/RogueSquadron64Recomp; cp $R/build/rogue_squadron.z64 $G/rogue_squadron.z64; cp $R/build/saves/$SV $G/saves/$SV
  free=-; [[ $arm != ctl ]] && free=$(fill $M)
  ( cd $G && exec env -u ROGUESQ_SETTINGS ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_DI_DIALOG=0 ROGUESQ_RO_DIALOG=0 ROGUESQ_UE_DIALOG=0 \
      ROGUESQ_NO_PKILL=1 $([[ $arm = mut ]] && print ROGUESQ_S7974_NOMEM=1) ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!; died=-
  for i in $(seq 1 $(( WATCH * 2 ))); do sleep 0.5; kill -0 $p 2>/dev/null || { died=$i; break; }; done
  alive=dead; kill -0 $p 2>/dev/null && { alive=alive; kill -9 $p; }; wait $p 2>/dev/null
  boot=$(grep -acE '^\[(si-thr|dpc-fwd)\]' $L); place=$(grep -ac 'ROM\] Place your' $L); imp=$(grep -ac 'ROM\] Imported rogue_squadron.z64' $L)
  sfail=$(grep -ac 'storing the ROM copy failed' $L); ns2s=$(grep -ac 's7974-ns2\] could not store' $L); ns2l=$(grep -ac 's7974-ns2\] loading the ROM from memory' $L)
  ns2m=$(grep -ac 's7974-ns2\] mutant' $L); c=$(grep -acE 'CRASH|SIGSEGV|SIGBUS|SIGABRT|terminate called|libc\+\+abi|Error opening stored ROM' $L)
  rsz=$(stat -f %z $G/$ROM 2>/dev/null)
  print "$arm: alive=$alive died_half_s=$died free_kb=$free boot_lines=$boot imported=$imp place_prompt=$place store_failed=$sfail \
ns2_store=$ns2s ns2_memload=$ns2l ns2_mut=$ns2m crashlines=$c stored_rom_size=${rsz:-none}" | tee -a $S/summary.txt
  ok=PASS; [[ $alive = alive && $c = 0 && $imp = 1 ]] || ok=FAIL
  case $arm in
    ctl)  [[ $boot -gt 0 && $place = 0 && $sfail = 0 && $ns2s = 0 && ${rsz:-0} -gt 0 ]] || ok=FAIL ;;
    full) [[ $boot -gt 0 && $place = 0 && $sfail = 1 && $ns2s = 1 && $ns2l -ge 1 && -z $rsz ]] || ok=FAIL ;;
    mut)  [[ $boot = 0 && $place = 1 && $sfail = 1 && $ns2m = 1 && $ns2l = 0 ]] || ok=FAIL ;;
    old)  [[ $boot = 0 && $place = 1 && $sfail = 1 && $ns2s = 0 ]] || ok=FAIL ;;
  esac
  [[ $ok = FAIL ]] && bad=1; print "$arm $ok" | tee -a $S/summary.txt
  hdiutil detach -quiet -force $M 2>/dev/null
done
cr1=$(ls $CRD 2>/dev/null | grep -c RogueSquadron); print "new_crash_reports=$(( cr1 - cr0 ))" | tee -a $S/summary.txt
cleanup; print "VERDICT $([[ $bad = 0 ]] && print PASS || print FAIL)" | tee -a $S/summary.txt; exit $bad
