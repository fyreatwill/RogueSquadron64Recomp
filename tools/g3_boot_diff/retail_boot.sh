#!/bin/zsh
# s6738: retail ROM, NO input, angrylion RDP -> dense series of RDRAM fb dumps through the boot 640-wide phase (intro cinematic).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
D=scratch/s6738/${RD:-retail}; mkdir -p $D
A=(--press 999:start); for i in $(seq 0 89); do d=$(printf '%.1f' $((0.5 + i*0.4))); A+=(--fb-dump 640:$d:600000:200000:$D/r$(printf %02d $i).bin); done
tools/oracle/build/rs64_oracle --core $C --rom $R --secs ${SECS:-50} --vi-poll --vi-trace --rsp $RSP --video $V $A > $D/oracle.log 2>&1 &
P=$!; sleep $((${SECS:-50}+30)); kill -9 $P 2>/dev/null
grep -c 'fb-dump' $D/oracle.log
