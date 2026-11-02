#!/bin/zsh
# s6784: song-load worker vs menu image worker on queue 0x80138920, retail oracle + port, title -> SELECT GAME ->
# level select -> craft select -> mission. usage: pair.sh OUTDIR
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=${1:?}; mkdir -p $S/retail $S/port
SPEC=800B380C:6:0:8,800B3FA0:6:58:2,800B4004:3:0:8,800C3B38:6:0:8,800C5880:6:0:8,800C3B4C:4:0:1,800C3B54:2:0:8
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
E="$HOME/Library/Application Support/Mupen64Plus/save/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep"
D=$S/retail
cp -p "$E" $D/mupen_eep_backup.eep || exit 3
trap 'cp -p $D/mupen_eep_backup.eep "$E" && echo eep-restored' EXIT INT TERM
cp scratch/s6779/r1/lvl1.eep "$E" || exit 3
env RS64_XTRACE_MEM=$SPEC tools/oracle/build/rs64_oracle --core $C --rom $R --secs ${RSECS:-100} --vi-poll --rsp $RSP --video $V \
  --exec-trace 0x800C3B38 --exec-trace-also 0x800C5880 --exec-trace-also 0x800C3B4C --exec-trace-also 0x800C3B54 \
  --exec-trace-also 0x800B380C --exec-trace-also 0x800B3FA0 --exec-trace-also 0x800B4004 \
  ${=RXA:-} --press ${RPRESS:-6:start,11:start,16:start,36:start,44:start,49:start,54:start,64:start} > $D/oracle.log 2>&1 &
RPID=$!
env SAVE_FROM=scratch/s6779/r1/lvl1.eep SECS=${PSECS:-60} CAP0=999 AP=${AP:-6:start,11:start,16:start,21:start,27:start,31:start,42:start} \
  XE="ROGUESQ_DEBUG_WRITE=${PDW:-80003470:1:1024:5} ROGUESQ_RAND_TRACE=$PWD/$S/port/xt.txt ROGUESQ_XTRACE_MEM=$SPEC ${XE:-}" \
  zsh tools/g3_port_capture.sh $S/port > $S/port_run.txt 2>&1
t=0; while kill -0 $RPID 2>/dev/null && [ $t -lt 240 ]; do sleep 5; t=$((t+5)); done
kill -9 $RPID 2>/dev/null
cat $S/port_run.txt
