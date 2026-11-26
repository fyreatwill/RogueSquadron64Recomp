#!/bin/zsh
# s7971 class MP e2e: host memory pressure while the game flies. `memory_pressure -S` (simulated notification) needs root
# (measured s7971: "kern.memorypressure_manual_trigger failed : Operation not permitted"), so the stimulus is REAL: the
# tools/s7971_mem_hog.py helper allocates N GB of incompressible memory at ${AT:-125} s into a forced-route flight, holds it
# ${HOLD:-60} s while keeping its pages hot, then frees it. N per arm is sized from vm_stat at arm start so the host never
# swaps hard: control 0, mid = 0.8 x free, high = free + 0.5 x inactive (cap ${CAP:-8} GB).
# Private game copy under /tmp (save COPIED, build/saves untouched, ROGUESQ_NO_SAVE_WRITE=1), one game at a time.
# Instruments: ROGUESQ_PRESENT_RING + ROGUESQ_AI_TRACE (game clock = s since launch; the pressure window is placed on it from
# the launch wall time), a 2 s host sampler (<arm>.vm: vm_stat compressions/swapouts, memorystatus level, game RSS, footprint
# of the game), and the log. After the hold, watch ${WATCH:-30} s, then SIGHUP and time HUP->exit; SIGKILL after 15 s.
# Scored offline by tools/s7971_mp_score.py. Output scratch/s7971/${P}_summary.txt; exit 0 = every arm moot + stimulus reached.
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7971; P=${1:-new}; WATCH=${WATCH:-30}; AT=${AT:-125}; HOLD=${HOLD:-60}
mkdir -p $S; : > $S/${P}_summary.txt; bad=0; T=/tmp/s7971_e2e; SV=rs64.n64.us.1.0.bin
rm -rf $T; mkdir -p $T/saves
for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 audio_device.txt controls.json; do [ -e $R/build/$f ] && cp $R/build/$f $T/$f; done
cp $R/build/saves/$SV $T/saves/$SV; cp $R/build/saves/$SV $T/saves/$SV.bak
CRD=~/Library/Logs/DiagnosticReports; cr0=$(ls $CRD 2>/dev/null | grep -c RogueSquadron)
now(){ perl -MTime::HiRes=time -e 'printf "%d\n", time*1000'; }
pg(){ vm_stat | awk -v k="$1" -F: '$1==k{gsub(/[ .]/,"",$2); print $2}'; }
EARLY=""; e=10; for i in $(seq 1 20); do if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi; EARLY="$EARLY$e:$k,"; e=$((e+4)); done
FL=""; t=95; for i in $(seq 1 100); do for k in a sl a sr; do FL="$FL$t:$k,"; t=$((t+2)); done; (( t > 900 )) && break; done
AP="${EARLY}${FL%,}"
for arm in ${=${ARMS:-control mid high}}; do
  n=flight_$arm; L=$S/${P}_$n.log; RG=$S/${P}_$n.ring; AT_=$S/${P}_$n.ai; VM=$S/${P}_$n.vm; HG=$S/${P}_$n.hog; rm -f $RG $AT_ $AT_.pcm $VM $HG
  ( cd $T && exec env -u ROGUESQ_SETTINGS ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_NO_PKILL=1 ROGUESQ_PRESENT_RING=$RG ROGUESQ_AI_TRACE=$AT_ \
      ROGUESQ_FPS60=1 ROGUESQ_FORCE_SAVE_MISSION=${LEVEL:-1} ROGUESQ_FORCE_UNLOCK=${LEVEL:-1} ROGUESQ_GODMODE=1 \
      ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_AUTOPILOT=$AP ${=MP_ENV} ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!; t0=$(now)
  ( while kill -0 $p 2>/dev/null; do
      print "$(( $(now) - t0 )) comp=$(pg Compressions) swo=$(pg Swapouts) pgo=$(pg Pageouts) free=$(pg 'Pages free') lvl=$(sysctl -n kern.memorystatus_vm_pressure_level) rss_kb=$(ps -o rss= -p $p | tr -d ' ') fp=$(footprint -p $p 2>/dev/null | awk '/phys_footprint:/{print $2$3; exit}')"
      sleep 2; done ) > $VM 2>/dev/null &
  smp=$!
  sleep $AT; alive_pre=dead; kill -0 $p 2>/dev/null && alive_pre=alive
  fr=$(pg 'Pages free'); ia=$(pg 'Pages inactive')
  case $arm in control) gb=0;; mid) gb=$(( fr * 16384 * 8 / 10 / 1073741824.0 ));; high) gb=$(( (fr + ia / 2) * 16384 / 1073741824.0 ));; esac
  (( gb > ${CAP:-8} )) && gb=${CAP:-8}
  ps_ms=$(( $(now) - t0 )); c0=$(pg Compressions); s0=$(pg Swapouts)
  if (( gb > 0 )); then python3 $R/tools/s7971_mem_hog.py $gb $HOLD > $HG 2>&1; else sleep $HOLD; fi
  pe_ms=$(( $(now) - t0 )); c1=$(pg Compressions); s1=$(pg Swapouts)
  died=-; st=-
  for i in $(seq 1 $(( WATCH * 2 ))); do sleep 0.5; kill -0 $p 2>/dev/null || { died=$(( $(now) - t0 )); wait $p; st=$?; break; }; done
  alive=dead; kill -0 $p 2>/dev/null && alive=alive; hup=-
  if [[ $alive = alive ]]; then th=$(now); kill -HUP $p
    for i in $(seq 1 30); do sleep 0.5; kill -0 $p 2>/dev/null || break; done
    if kill -0 $p 2>/dev/null; then hup=hung; kill -9 $p; wait $p; st=$?; else hup=$(( $(now) - th )); wait $p; st=$?; fi
  fi
  kill $smp 2>/dev/null
  sc=$(python3 $R/tools/s7971_mp_score.py $RG $AT_ $L $ps_ms $pe_ms $VM 2>&1 | tail -1)
  print "$P $n: alive_pre=$alive_pre alive=$alive died_ms=$died status=$st gb=$gb press_ms=$ps_ms-$pe_ms comp_d=$(( c1 - c0 )) swo_d=$(( s1 - s0 )) hup_exit_ms=$hup $(grep -o 'alloc_s=[0-9.]*' $HG 2>/dev/null) $sc" | tee -a $S/${P}_summary.txt
  print -- "  last: $(grep -av 'pe gate\|threadPresent' $L | tail -2 | tr '\n' '|' | cut -c1-240)" >> $S/${P}_summary.txt
  ok=PASS; [[ $alive_pre = alive && $alive = alive && $hup != hung && $hup != - && $sc == *" verdict=moot"* ]] || ok=FAIL
  [[ $ok = FAIL ]] && bad=1; print "$P $n $ok" | tee -a $S/${P}_summary.txt
  zstd -q -f --rm $RG 2>/dev/null; rm -f $AT_.pcm
done
cr1=$(ls $CRD 2>/dev/null | grep -c RogueSquadron); print "$P new_crash_reports=$(( cr1 - cr0 ))" | tee -a $S/${P}_summary.txt
rm -rf $T; print "$P VERDICT $([[ $bad = 0 && $cr1 = $cr0 ]] && print PASS || print FAIL)" | tee -a $S/${P}_summary.txt; exit $bad
