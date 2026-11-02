#!/bin/zsh
# s6780: SELECT GAME backdrop = rand()%18 at 0x800C5764 (initMenuBackdropAndPickRandom). Seed poked to 1 at the first
# 1024 (title) VI in both arms; rand traced from there. usage: run.sh SDIR RETAIL_PRESS PORT_AP
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=$1; RPR=$2; PAP=$3; mkdir -p $S
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
D=$S/retail; mkdir -p $D
pgrep -x rs64_oracle >/dev/null && exit 4
A=(); for i in $(seq 0 27); do A+=(--fb-dump 1024:$i:600000:200000:$D/t$(printf %02d $i).bin); done
# s6800: private Core SaveSRAMPath (--save-dir); the user-wide mupen save is never touched
mkdir -p $D; SD=$(cd $D && pwd)/savedir; mkdir -p $SD; cp scratch/s6779/r1/lvl1.eep "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
tools/oracle/build/rs64_oracle --save-dir $SD --core $C --rom $R --secs 50 --vi-poll --vi-trace --rsp $RSP --video $V \
  --debug-write 80003470:1:1024:0 --exec-trace 0x80003430:200000 --press $RPR $A > $D/oracle.log 2>&1 &
RP=$!
env SAVE_FROM=scratch/s6779/r1/lvl1.eep SECS=40 CAP0=12 AP=$PAP \
  XE="ROGUESQ_DEBUG_WRITE=80003470:1:1024:0 ROGUESQ_RAND_TRACE=$PWD/$S/port_rand.txt" \
  zsh tools/g3_port_capture.sh $S/port > $S/port_run.txt 2>&1
t=0; while kill -0 $RP 2>/dev/null && [ $t -lt 120 ]; do sleep 5; t=$((t+5)); done
kill -9 $RP 2>/dev/null; cat $S/port_run.txt; grep -c '^\[xtrace\]' $D/oracle.log; wc -l < $S/port_rand.txt
