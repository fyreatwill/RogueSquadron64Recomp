#!/bin/zsh
# s7816: retail-only oracle run (title -> menus -> hangar pans, the s6791 press schedule) with a chosen RSP plugin;
# --fb-dump of physical 0x600000+2MB every 1 s from the first 1024-wide VI (ND dumps) and every 1 s from the first 512 VI.
# usage: env RS64_ORACLE_RSP=stock|patched|<dylib> zsh tools/s7816_oracle_rsp_ab.sh OUTDIR
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
D=${1:?outdir}; mkdir -p $D
pgrep -x rs64_oracle >/dev/null && { echo busy; exit 4; }
source tools/oracle/rsp_plugin.sh
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
SD=$(cd $D && pwd)/savedir; mkdir -p $SD; cp ${EEP:-scratch/s6779/r1/lvl1.eep} "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
A=(); for i in $(seq 0 ${ND:-40}); do A+=(--fb-dump 1024:$i:600000:200000:$D/t$(printf %03d $i).bin); done
for i in $(seq 0 ${NH:-40}); do A+=(--fb-dump 512:$i:600000:200000:$D/h$(printf %03d $i).bin); done
echo "rsp=$RSP" > $D/rsp.txt
tools/oracle/build/rs64_oracle --save-dir $SD --core $C --rom $R --secs ${RSECS:-104} --vi-poll --rsp $RSP --video $V \
  --press ${RP:-6:start,11:start,16:start,24.3:start,30.3:start,44:start,54:start,66:dright,78:dright,90:dleft} $A > $D/oracle.log 2>&1
echo "rc=$? dumps=$(grep -c '^\[fb-dump\]' $D/oracle.log)"
