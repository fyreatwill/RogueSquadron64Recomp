#!/bin/zsh
# G3 per-mission sim/frame match (s6753-s6769 recipe, promoted from scratch s6770).
# usage: zsh tools/g3_mission/run.sh SDIR LEVEL   (LEVEL = save byte +0x31, mission number - 1)
#   1. patches the signed save (tools/g3_eep_patch.py) from BASE_EEP (default scratch/s6769/lvl16.eep)
#   2. retail arm (rs64_oracle, angrylion, dt pinned) in the background, port arm in the foreground
#   3. waits for the oracle, then runs tools/g3_mission/offline.sh SDIR
# Bonus mission 17 (Beggar's Canyon race): the 512-wide screen at ~24 s port / ~39 s retail is the LEVEL SELECT (s6770
#   misread it as flight); the race itself ticks runInMissionFrame 0x800FA730 like every mission. 0x800C6674
#   (advanceWrappingPhaseAccumulator) is the level-select hologram's tick; G3_TICK=800C6674 compares that screen (s6771).
# Mission 17 (s6771): PRESS=6:start,...,51:start AP=6:start,...,31:start (no press after the pick: the race starts by
#   itself and the unsteered craft crashes ~12 s in), POKE=<dt pin>,800FA730:0:80003470:1:1 (one-shot rngSeed on tick 0),
#   then G3_MIN_TICK=0 for the offline rand compare.
# Mission 18 (s6772, Death Star trench, X-wing): cursor +1 and a craft-select Start: AP=6:start,11:start,16:start,
#   21:start,23:w512,25:right,27:start,31:start,42:start  PRESS=6:start,...,36:start,41:dright,44:start,49:start,
#   54:start,64:start  (retail first race tick ~vi 5153 = 86 s: FARM=88 DSTEP=4), offline G3_SNAP_TICKS=800FA730.
# Mission 17 also needs ARM=20 DWARM=30 CAP0=33 (the defaults 55/85/62 never arm the port rand trace, s6778). Pause menu
#   (s6778): add PRESS ...,61:start,65:start and AP ...,40:start,44:start (pause, then resume -> race crash -> debrief).
# ORACLE_EXTRA: extra rs64_oracle words, e.g. --watch-pc-range 0x8009264C:0x800934A4 (s6872).
# RETAIL_ONLY=1: retail arm only, no port arm, no offline compare (s6878).
# env: G3_TICK (tick/pin pc, 800FA730; must be one of the --exec-trace-also pcs below) PRESS/AP (start schedules) DWARM (retail seed arm s, 85) ARM (port seed arm s, 55) RSECS (360) PSECS (330) NDUMP (24) DSTEP (10) FARM (103) POKE (dt pin) EXTRA (port env)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=$1; L=$2; [ -n "$S" ] && [ -n "$L" ] || { echo "usage: run.sh SDIR LEVEL" >&2; exit 2; }
mkdir -p $S
EEP=$S/lvl$((L+1)).eep
# bonus missions 17-19 (LEVEL 16-18): the level select's highest selectable index a2 = 15 raised by 0x80130B4C bits
# 0x00100000 -> 16, 0x00200000 -> 17, 0x00400000 -> 18 (menu code 0x800C5DE4-0x800C5E6C; s6772 re-read, s6770 had it
# one off), which the save loader copies from record word +0xC (0x8006DBEC-0x8006DC00); the record starts at copy +0x2C,
# so byte +0x39 = 0x60 opens all three (lvsel log: unlockMask 0x00080000 = 1<<(18+1)).
# s6772: the game clamps the saved current mission (record byte 5 = +0x31) to 16 itself (getAccountDataPtr 0x8006EE7C,
# copyAccountRecordAndMarkActive 0x8006EEB4), so the level select always opens on cursor 16 (mission 17); missions 18/19
# need 1/2 d-pad RIGHT presses on the SELECT LEVEL screen (state 2), before the Start that commits the level. Port:
# AP=...,21:start,23:w512,25:right,27:start,...  retail: PRESS=...,36:start,41:dright,44:start,...
U=(); (( L >= 16 )) && U=(0x39=0x60)
python3 tools/g3_eep_patch.py ${BASE_EEP:-scratch/s6769/lvl16.eep} $EEP --set 0x31=$(( L > 16 ? 16 : L )) $U || exit 3
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
# same xtrace spec in both arms: rand callers, glob words, NPC table, event mask 8010C9E0, song handle 8010C0E0
export G3_TICK=${G3_TICK:-800FA730}; T=$G3_TICK
M=800AF374:29:10:10,800AF374:0:8011A880:32,800FA730:29:10:10,800FA730:0:8011A880:32,$T:0:8010FF30:2,800C6674:29:10:10,800C6674:0:8011A880:32,8006C010:4:0:16,8006C010:29:18:3,8006C010:0:8011A830:8,$T:0:8010C9E0:18,$T:0:8010C0E0:1
PIN=${POKE-$T:29:30:3d088889}
# --- retail arm
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
D=$S/retail; mkdir -p $D
A=(); for i in $(seq 0 $((${NDUMP:-24}-1))); do A+=(--fb-dump 512:$((${DSTEP:-10}*i)):600000:200000:$D/b$(printf %03d $i).bin); done
# s6800: private Core SaveSRAMPath (--save-dir); the user-wide mupen save is never touched
mkdir -p $D; SD=$(cd $D && pwd)/savedir; mkdir -p $SD; cp $EEP "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
RSECS=${RSECS:-360}
env RS64_XTRACE_MEM=$M RS64_XTRACE_POKE=$PIN tools/oracle/build/rs64_oracle --save-dir $SD --core $C --rom $R --secs $RSECS \
  --fb-arm-after ${FARM:-103} --vi-poll --vi-trace --rsp $RSP --video $V \
  --press ${PRESS:-6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start} \
  --hit-cap 2000 --watch-write 0x3FFFF0:0x3FFFF4 --exec-trace 0x80003430:400000:3470 --exec-trace-also 0x8006BEC8 \
  --exec-trace-also 0x8006C018 --exec-trace-also 0x800AF374 --exec-trace-also 0x800FA730 --exec-trace-also 0x800C6674 \
  --exec-trace-also 0x8006C010 --debug-write 80003470:1:512:${DWARM:-85} --exec-trace-also 0x8008EE08 --exec-trace-also 0x8008EE84 \
  ${=ORACLE_EXTRA:-} $A > $D/oracle.log 2>&1 &
RP=$!
if [ -n "${RETAIL_ONLY:-}" ]; then wait $RP; echo "retail hits: $(grep -c '^\[hit\]' $D/oracle.log)"; exit 0; fi
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
