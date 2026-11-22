#!/bin/zsh
# s6791 G3f retail: watch every store into the craft-select camera block (cam 0x800CD670 +0x2C..+0x5C) through d-pad pans.
# s7818: --det by default (rsp_plugin.sh ODET); ORACLE_DET=0 restores wall clock + randomized interrupts.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
D=${1:-scratch/s6791/retail}; mkdir -p $D
pgrep -x rs64_oracle >/dev/null && { echo busy; exit 4; }
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
source /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle/rsp_plugin.sh  # s7816: VU-fixed cxd4 by default
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
# s6800: private Core SaveSRAMPath (--save-dir); the user-wide mupen save is never touched
mkdir -p $D; SD=$(cd $D && pwd)/savedir; mkdir -p $SD; cp ${EEP:-build/saves/rs64.n64.us.1.0.bin} "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
env RS64_KEEP_POSITIVE_CONTROL=1 tools/oracle/build/rs64_oracle $ODET --save-dir $SD --core $C --rom $R --secs ${RSECS:-104} --vi-poll --rsp $RSP --video $V \
  --press ${RP:-6:start,11:start,16:start,24.3:start,30.3:start,44:start,54:start,66:dright,78:dright,90:dleft} \
  --watch-write 0x0CD690:0x0CD6CC --store-field-dump-all 0 --store-field-dump-any-phase \
  --hit-cap 1 > $D/oracle.log 2>&1
