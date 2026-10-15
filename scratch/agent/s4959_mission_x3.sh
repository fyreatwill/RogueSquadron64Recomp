#!/bin/zsh
# s4959: s4958 route (title->hangar->0x6A2900->~70s load->mission) x3 sequential, M5 PCM counters armed.
set -u
ROOT=${0:A:h:h:h}; OUT="$ROOT/scratch/agent/s4959_mission_x3"; BUILD="$ROOT/build"
rm -rf "$OUT"; mkdir -p "$OUT"
COMMON=(ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_DLWALK=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_AUDIO_UCODE=1
  PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=240 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1)
pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true
for r in 1 2 3; do
  L=$OUT/run$r.log; K=$OUT/keys$r.log
  ( cd "$BUILD" && exec env "${COMMON[@]}" ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!; t0=$SECONDS
  has() { grep -aq "$1" $L; }
  key() { "$BUILD/winctl" activate $p >/dev/null 2>&1; "$BUILD/winctl" key $p $1 250 >/dev/null 2>&1; }
  for i in $(seq 1 150); do has 'origin=0x00790400' && break; sleep 1; done
  has 'origin=0x00790400' || { echo notitle > $K; kill -9 $p; continue; }
  for n in $(seq 1 12); do
    has 'origin=0x006AB400' && break
    key 36; sleep 4; key 6; sleep 7
  done
  has 'origin=0x006AB400' || { echo nohangar t=$((SECONDS-t0)) > $K; kill -9 $p; continue; }
  sleep 15; echo "hangar t=$((SECONDS-t0))" >> $K
  for n in $(seq 1 14); do
    if has 'origin=0x006A2900' || has 'origin=0x6A2900'; then break; fi
    key 6; sleep 7
  done
  echo "6a2900 t=$((SECONDS-t0))" >> $K
  mt=-1
  for n in $(seq 1 24); do
    sleep 5
    [ $((n%6)) -eq 0 ] && key 6
    if [ $mt -lt 0 ] && grep -aqE 'origin=0x(00)?690400' $L; then mt=$((SECONDS-t0)); fi
    print "t=$((SECONDS-t0)) last=$(grep -a 'origin=' $L | tail -1 | grep -o 'origin=0x[0-9A-Fa-f]*') m690400=$(grep -ac origin=0x00690400 $L)" >> $K
  done
  kill -9 $p 2>/dev/null; wait $p 2>/dev/null
  print "mission_onset_t=$mt crash=$(grep -ac CRASH $L) abort=$(grep -aic abort $L) pcm_rows=$(grep -ac pcm-boundary-source $L) pcm_nz_rows=$(grep -a pcm-boundary-source $L | grep -vac 'nz=0$') sample_nonflat=$(grep -a pcm-samples $L | grep -vc 'min=0 max=0')" >> $K
  sleep 3
done
