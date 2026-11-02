#!/bin/zsh
# s6793: retail angrylion frames of the AT THE MOVIES seam shots (s6792 rdplog run: x=318 edge shot ~382-393 s,
# x=322.5 shot ~404-414 s emulated). Same presses as scratch/s6792/mov; fb dumps 0x600000+2MB every 1 s from 370 s.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
D=scratch/s6793/retail
# s6800: private Core SaveSRAMPath (--save-dir); the user-wide mupen save is never touched
mkdir -p $D; SD=$(cd $D && pwd)/savedir; mkdir -p $SD; cp scratch/s6779/r1/lvl1.eep "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
P=$(head -1 scratch/s6792/mov/press.txt | sed 's/^retail press: //')
A=(); for i in $(seq 0 50); do A+=(--fb-dump 640:$i:600000:200000:$D/t$(printf %03d $i).bin); done
tools/oracle/build/rs64_oracle --save-dir $SD --core $C --rom $R --secs ${RSECS:-425} --vi-poll --rsp $RSP --video $V \
  --fb-arm-after ${ARM:-370} --press $P $A > $D/oracle.log 2>&1
echo rc=$?
