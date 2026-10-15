#!/bin/zsh
# s4955: solo keyed hangar->mission route, N=3, key timestamps, VI-progress.
set -u
ROOT=${0:A:h:h:h}
OUT="$ROOT/scratch/agent/s4955_keyed"
BUILD="$ROOT/build"
rm -rf "$OUT"; mkdir -p "$OUT"
COMMON=(ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_DLWALK=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 ROGUESQ_AUDIO_UCODE=1
  PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=240 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1)
pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true
has() { grep -aq "$2" "$1"; }
for run in 1 2 3; do
  L=$OUT/run$run.log; K=$OUT/run$run.keys
  ( cd "$BUILD" && exec env "${COMMON[@]}" ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!; t0=$SECONDS
  for i in $(seq 1 150); do has $L 'vi_width=512' && break; sleep 1; done
  has $L 'vi_width=512' || { print "run$run no512 t=$((SECONDS-t0))" >> $OUT/driver.log; kill -9 $p; continue; }
  for n in $(seq 1 6); do
    "$BUILD/winctl" activate $p >/dev/null 2>&1; "$BUILD/winctl" key $p 36 250 >/dev/null 2>&1; print "t=$((SECONDS-t0)) key36 pair=$n" >> $K; sleep 4
    "$BUILD/winctl" activate $p >/dev/null 2>&1; "$BUILD/winctl" key $p 6 250 >/dev/null 2>&1; print "t=$((SECONDS-t0)) key6 pair=$n" >> $K; sleep 7
    has $L 'origin=0x00690400' && { print "t=$((SECONDS-t0)) mission-origin-seen" >> $K; break; }
  done
  sleep 45
  kill -9 $p 2>/dev/null; sleep 2
  print "run$run end t=$((SECONDS-t0)) title=$(grep -ac origin=0x00790400 $L) m690400=$(grep -ac origin=0x00690400 $L) hangar6AB=$(grep -aic origin=0x006AB400 $L) crash=$(grep -ac 'CRASH' $L)" >> $OUT/driver.log
done
python3 "$ROOT/tools/vi_progress.py" $OUT/run*.log > $OUT/vi_progress.txt 2>&1
