#!/bin/zsh
# s6791 G3f retail: watch every store into the craft-select camera block (cam 0x800CD670 +0x2C..+0x5C) through d-pad pans.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
D=${1:-scratch/s6791/retail}; mkdir -p $D
pgrep -x rs64_oracle >/dev/null && { echo busy; exit 4; }
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
E="$HOME/Library/Application Support/Mupen64Plus/save/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep"
cp -p "$E" $D/mupen_eep_backup.eep || exit 3
trap 'cp -p $D/mupen_eep_backup.eep "$E" && echo eep-restored' EXIT INT TERM
cp ${EEP:-build/saves/rs64.n64.us.1.0.bin} "$E" || exit 3
env RS64_KEEP_POSITIVE_CONTROL=1 tools/oracle/build/rs64_oracle --core $C --rom $R --secs ${RSECS:-104} --vi-poll --rsp $RSP --video $V \
  --press ${RP:-6:start,11:start,16:start,24.3:start,30.3:start,44:start,54:start,66:dright,78:dright,90:dleft} \
  --watch-write 0x0CD690:0x0CD6CC --store-field-dump-all 0 --store-field-dump-any-phase \
  --hit-cap 1 > $D/oracle.log 2>&1
