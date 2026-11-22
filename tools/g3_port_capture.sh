#!/bin/zsh
# s6741 G3: port plain launch + in-process autopilot keys, tight-loop window captures (w_<secs>.png) for
# tools/g3_oracle_match.py --win. usage: g3_port_capture.sh OUTDIR
#   BURST=<t0>,<t1>: dense in-process window grabs between t0 and t1 s (s6811)
#   AP=<autopilot schedule>  SECS=<run length>  CAP0=<first capture s>  XE="<extra env>"
#   GAMEDIR=<dir> (s7469): run the binary from that build dir (e.g. build_asan), default build
#   SAVE_FROM=<eeprom file>: run with that 512-byte EEPROM as the save (e.g. the oracle's mupen .eep, so retail and
#   port show the same selected level; s6741: the owner's save selects THE JADE MOON, retail AMBUSH AT MOS EISLEY).
#   s7819: the owner's save is never touched. SAVE_FROM builds a private game dir OUTDIR/game (symlinked binary + ROM
#   + audio_device.txt, its own saves/ holding SAVE_FROM) and runs from it; the save path resolves from the cwd
#   (main.cpp register_config_path(rs_cwd) -> pi.cpp config_path/saves). ROGUESQ_NO_SAVE_WRITE=1 is forced as well.
cd "$(git rev-parse --show-toplevel)"
O=$1; mkdir -p $O
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo LOCKED; exit 4; }
GD=${GAMEDIR:-build}
if [ -n "${SAVE_FROM:-}" ]; then
  [ -s "$SAVE_FROM" ] || { echo "SAVE_FROM missing: $SAVE_FROM"; exit 3; }
  SRC=$(cd $GD && pwd); PG=$(mkdir -p $O/game && cd $O/game && pwd)
  rm -rf $PG/saves; mkdir -p $PG/saves $PG/mods $PG/mod_config
  for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 rogue_squadron.z64 audio_device.txt controls.json; do
    [ -e $SRC/$f ] && ln -sfn $SRC/$f $PG/$f
  done
  cp "$SAVE_FROM" $PG/saves/rs64.n64.us.1.0.bin || exit 3
  GD=$PG
  XE="ROGUESQ_NO_SAVE_WRITE=1 ${XE:-}"
fi
AP=${AP:-6:start,11:start,16:start,21:start}
( cd $GD && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_AUTOPILOT=$AP ROGUESQ_LOG_PHASE=1 ${=XE} ./RogueSquadron64Recomp ) > $O/run.log 2>&1 &
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
