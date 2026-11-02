#!/bin/zsh
# G3 per-mission sim/frame match (s6753-s6769 recipe, promoted from scratch s6770).
# usage: zsh tools/g3_mission/run.sh SDIR LEVEL   (LEVEL = save byte +0x31, mission number - 1)
#   1. patches the signed save (tools/g3_eep_patch.py) from BASE_EEP (default scratch/s6769/lvl16.eep)
#   2. retail arm (rs64_oracle, angrylion, dt pinned) in the background, port arm in the foreground
#   3. waits for the oracle, then runs tools/g3_mission/offline.sh SDIR
# Bonus mission 17 (Beggar's Canyon race, s6770): flight starts at 512 wide ~24 s port / ~39 s retail, and later
#   Start presses pause the race; use PRESS=6:start,...,36:start DWARM=30 AP=6:start,...,21:start ARM=20.
# env: PRESS/AP (start schedules) DWARM (retail seed arm s, 85) ARM (port seed arm s, 55) RSECS (360) PSECS (330) NDUMP (24) DSTEP (10) FARM (103) POKE (dt pin) EXTRA (port env)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=$1; L=$2; [ -n "$S" ] && [ -n "$L" ] || { echo "usage: run.sh SDIR LEVEL" >&2; exit 2; }
mkdir -p $S
EEP=$S/lvl$((L+1)).eep
# bonus missions 17-19 (LEVEL 16-18): the level select clamps the cursor to a3 = 15 + bonus flags read from
# 0x80130B4C (bits 0x00200000 -> 16, 0x00400000 -> 17, menu code 0x800C5E14-0x800C5E6C), which the save loader copies
# from record word +0xC (bits 9-22, 0x8006DBEC-0x8006DC00); the record starts at copy +0x2C, so byte +0x39 = 0x60 (s6770).
U=(); (( L >= 16 )) && U=(0x39=0x60)
python3 tools/g3_eep_patch.py ${BASE_EEP:-scratch/s6769/lvl16.eep} $EEP --set 0x31=$L $U || exit 3
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
# same xtrace spec in both arms: rand callers, glob words, NPC table, event mask 8010C9E0, song handle 8010C0E0
M=800AF374:29:10:10,800AF374:0:8011A880:32,800FA730:29:10:10,800FA730:0:8011A880:32,800FA730:0:8010FF30:2,800C6674:29:10:10,800C6674:0:8011A880:32,8006C010:4:0:16,8006C010:29:18:3,8006C010:0:8011A830:8,800FA730:0:8010C9E0:18,800FA730:0:8010C0E0:1
PIN=${POKE-800FA730:29:30:3d088889}
# --- retail arm
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
E="$HOME/Library/Application Support/Mupen64Plus/save/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep"
D=$S/retail; mkdir -p $D
cp -p "$E" $D/mupen_eep_backup.eep || exit 3
trap 'cp -p $D/mupen_eep_backup.eep "$E" && echo eep-restored' EXIT INT TERM
A=(); for i in $(seq 0 $((${NDUMP:-24}-1))); do A+=(--fb-dump 512:$((${DSTEP:-10}*i)):600000:200000:$D/b$(printf %03d $i).bin); done
cp $EEP "$E" || exit 3
RSECS=${RSECS:-360}
env RS64_XTRACE_MEM=$M RS64_XTRACE_POKE=$PIN tools/oracle/build/rs64_oracle --core $C --rom $R --secs $RSECS \
  --fb-arm-after ${FARM:-103} --vi-poll --vi-trace --rsp $RSP --video $V \
  --press ${PRESS:-6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start} \
  --hit-cap 2000 --watch-write 0x3FFFF0:0x3FFFF4 --exec-trace 0x80003430:400000:3470 --exec-trace-also 0x8006BEC8 \
  --exec-trace-also 0x8006C018 --exec-trace-also 0x800AF374 --exec-trace-also 0x800FA730 --exec-trace-also 0x800C6674 \
  --exec-trace-also 0x8006C010 --debug-write 80003470:1:512:${DWARM:-85} --exec-trace-also 0x8008EE08 --exec-trace-also 0x8008EE84 \
  $A > $D/oracle.log 2>&1 &
RP=$!
# --- port arm (foreground)
O=$S/port
env SAVE_FROM=$EEP SECS=${PSECS:-330} CAP0=${CAP0:-62} AP=${AP:-6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,50:start} \
  XE="ROGUESQ_G3_CENSUS=$PWD/$O.census.txt ${EXTRA:-} ROGUESQ_DEBUG_WRITE=80003470:1:512:${ARM:-55} ROGUESQ_RAND_TRACE=$PWD/$O.rand.txt ROGUESQ_XTRACE_MEM=$M ROGUESQ_XTRACE_POKE=$PIN" \
  zsh tools/g3_port_capture.sh $O > $S/port_run.txt 2>&1
# --- wait for retail (hard cap RSECS+90 s from its start)
t=0; while kill -0 $RP 2>/dev/null && [ $t -lt 120 ]; do sleep 5; t=$((t+5)); done
kill -9 $RP 2>/dev/null
echo "retail hits: $(grep -c '^\[hit\]' $D/oracle.log)"
zsh tools/g3_mission/offline.sh $S
