#!/bin/zsh
# s7970 class SW e2e: the game process is frozen for minutes and then resumed (system sleep, lid close, App Nap, a debugger
# stop). Proxy that does not sleep the owner's Mac: `kill -STOP` the game, wait, `kill -CONT`. A real sleep also stops the
# audio device / display; SIGSTOP cannot show those (H-audio not covered here).
# Private game copy under /tmp (save COPIED, build/saves untouched, ROGUESQ_NO_SAVE_WRITE=1), one game at a time.
# Arms: scene title (stop at ${TSTOP:-20} s) and flight (forced level route, g1e_owner_quiet_arms recipe keys, stop at
# ${FSTOP:-125} s), each with stop lengths 0 (control), ${S1:-60}, ${S2:-300} s. After SIGCONT watch ${WATCH:-30} s, then SIGHUP
# (s7594 quit path) and time HUP->exit; SIGKILL after 15 s.
# Instruments: ROGUESQ_PRESENT_RING (Q rows: host time, VI origin) and ROGUESQ_AI_TRACE (one row per AI buffer: time, SDL queue
# bytes before). Scored offline by tools/s7970_sw_score.py (resume = the largest ring gap; it must be ~= the stop length).
# Extra env for every arm: SW_ENV="A=1 B=2". Output scratch/s7970/${P}_summary.txt; exit 0 = every arm as expected.
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7970; P=${1:-new}; WATCH=${WATCH:-30}
mkdir -p $S; : > $S/${P}_summary.txt; bad=0; T=/tmp/s7970_e2e; SV=rs64.n64.us.1.0.bin
rm -rf $T; mkdir -p $T/saves
for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 audio_device.txt controls.json; do [ -e $R/build/$f ] && cp $R/build/$f $T/$f; done
cp $R/build/saves/$SV $T/saves/$SV; cp $R/build/saves/$SV $T/saves/$SV.bak
CRD=~/Library/Logs/DiagnosticReports; cr0=$(ls $CRD 2>/dev/null | grep -c RogueSquadron)
now(){ perl -MTime::HiRes=time -e 'printf "%d\n", time*1000'; }
# flight route keys (same as tools/g1e_owner_quiet_arms.zsh)
EARLY=""; e=10; for i in $(seq 1 20); do if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi; EARLY="$EARLY$e:$k,"; e=$((e+4)); done
FL=""; t=95; for i in $(seq 1 100); do for k in a sl a sr; do FL="$FL$t:$k,"; t=$((t+2)); done; (( t > 900 )) && break; done
AP="${EARLY}${FL%,}"
for scene in ${=${SCENES:-title flight}}; do for len in 0 ${S1:-60} ${S2:-300}; do
  n=${scene}_s$len; L=$S/${P}_$n.log; RG=$S/${P}_$n.ring; AT=$S/${P}_$n.ai; rm -f $RG $AT $AT.pcm
  if [[ $scene = title ]]; then at=${TSTOP:-20}; xe=(); else at=${FSTOP:-125}
    xe=(ROGUESQ_FORCE_SAVE_MISSION=${LEVEL:-1} ROGUESQ_FORCE_UNLOCK=${LEVEL:-1} ROGUESQ_GODMODE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_AUTOPILOT=$AP); fi
  ( cd $T && exec env -u ROGUESQ_SETTINGS ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_NO_PKILL=1 ROGUESQ_PRESENT_RING=$RG ROGUESQ_AI_TRACE=$AT \
      ROGUESQ_FPS60=1 $xe ${=SW_ENV} ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!; t0=$(now); sleep $at; alive_pre=dead; kill -0 $p 2>/dev/null && alive_pre=alive
  ts=-; if (( len > 0 )) && [[ $alive_pre = alive ]]; then ts=$(now); kill -STOP $p; sleep $len; kill -CONT $p; ts=$(( $(now) - ts )); fi
  died=-; st=-
  for i in $(seq 1 $(( WATCH * 2 ))); do sleep 0.5; kill -0 $p 2>/dev/null || { died=$(( $(now) - t0 )); wait $p; st=$?; break; }; done
  alive=dead; kill -0 $p 2>/dev/null && alive=alive; hup=-
  if [[ $alive = alive ]]; then th=$(now); kill -HUP $p
    for i in $(seq 1 30); do sleep 0.5; kill -0 $p 2>/dev/null || break; done
    if kill -0 $p 2>/dev/null; then hup=hung; kill -9 $p; wait $p; st=$?; else hup=$(( $(now) - th )); wait $p; st=$?; fi
  fi
  sc=$(python3 $R/tools/s7970_sw_score.py $RG $AT $L $len $at 2>&1 | tail -1)
  print "$P $n: alive_pre=$alive_pre alive=$alive died_ms=$died status=$st stop_ms=$ts hup_exit_ms=$hup $sc" | tee -a $S/${P}_summary.txt
  print -- "  last: $(grep -av 'pe gate\|threadPresent' $L | tail -2 | tr '\n' '|' | cut -c1-240)" >> $S/${P}_summary.txt
  ok=PASS; [[ $alive_pre = alive && $alive = alive && $hup != hung && $hup != - && $sc == *" verdict=moot"* ]] || ok=FAIL
  [[ $ok = FAIL ]] && bad=1; print "$P $n $ok" | tee -a $S/${P}_summary.txt
  zstd -q -f --rm $RG 2>/dev/null; rm -f $AT.pcm
done; done
cr1=$(ls $CRD 2>/dev/null | grep -c RogueSquadron); print "$P new_crash_reports=$(( cr1 - cr0 ))" | tee -a $S/${P}_summary.txt
rm -rf $T; print "$P VERDICT $([[ $bad = 0 && $cr1 = $cr0 ]] && print PASS || print FAIL)" | tee -a $S/${P}_summary.txt; exit $bad
