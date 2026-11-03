#!/bin/zsh
# s6741 G3: port plain launch + in-process autopilot keys, tight-loop window captures (w_<secs>.png) for
# tools/g3_oracle_match.py --win. usage: g3_port_capture.sh OUTDIR
#   BURST=<t0>,<t1>: dense in-process window grabs between t0 and t1 s (s6811)
#   AP=<autopilot schedule>  SECS=<run length>  CAP0=<first capture s>  XE="<extra env>"
#   SAVE_FROM=<eeprom file>: run with that 512-byte EEPROM as the save (e.g. the oracle's mupen .eep, so retail and
#   port show the same selected level; s6741: the owner's save selects THE JADE MOON, retail AMBUSH AT MOS EISLEY).
#   The owner's save is backed up into OUTDIR, ROGUESQ_NO_SAVE_WRITE=1 is forced, and the save is restored on exit.
cd "$(git rev-parse --show-toplevel)"
O=$1; mkdir -p $O
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 4; }
SV=build/saves/rs64.n64.us.1.0.bin
if [ -n "${SAVE_FROM:-}" ]; then
  cp -p $SV $O/owner_save_backup.bin || exit 3
  trap 'cp -p $O/owner_save_backup.bin $SV && echo save-restored' EXIT INT TERM
  cp "$SAVE_FROM" $SV || exit 3
  XE="ROGUESQ_NO_SAVE_WRITE=1 ${XE:-}"
fi
AP=${AP:-6:start,11:start,16:start,21:start}
( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_AUTOPILOT=$AP ROGUESQ_LOG_PHASE=1 ${=XE} ./RogueSquadron64Recomp ) > $O/run.log 2>&1 &
P=$!; zmodload zsh/datetime; S=$EPOCHREALTIME; c=0; g=
sleep 1
# s6811: zsh clock + cached window id (was 3 python spawns + a winctl lookup per frame, ~0.58 s cadence)
while :; do
  e=$(( EPOCHREALTIME - S ))
  (( e >= ${SECS:-60} )) && break
  (( e < ${CAP0:-22} )) && { sleep 0.5; continue; }
  # s6811: BURST=<t0>,<t1> -> in-process window grabs (winctl burst, ~10x faster) for t0..t1 s, then back to screencapture
  if [ -n "${BURST:-}" ] && (( e >= ${BURST%%,*} && e < ${BURST##*,} )); then build/winctl burst $P $O $S ${BURST##*,}; continue; fi
  [ -n "$g" ] || g=$(build/winctl find $P 2>/dev/null) || { g=; sleep 0.2; continue; }
  t=$(printf '%07.2f' $(( EPOCHREALTIME - S )))
  /usr/sbin/screencapture -x -o -l${g%% *} $O/w_${t}.png || g=; c=$((c+1))
done
kill -9 $P; wait 2>/dev/null; echo caps=$c
