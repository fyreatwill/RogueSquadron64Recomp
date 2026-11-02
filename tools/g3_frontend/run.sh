#!/bin/zsh
# usage: zsh tools/g3_frontend/run.sh SDIR. Then g3_oracle_match.py per screen, e.g. title:
#   --w 512 --h 448 --bases 790000 --win 64,1024 --winx 85,1191 --dec shift ; select: --w 512 --h 336 --bases 6AB000,656000
#   --win 124,964 --winx 0,1280 (s6741). Split port captures by the run.log [phase] vi_width times for mismatch controls.
# NOTE (s6779): with mission-1 saves the 640 after the select is the opening CRAWL (79.7 s retail), not a briefing.
# G3 front-end (s6779): retail (emu-thread fb dumps) title 1024 / level select 512 / briefing 640 + port window captures,
# mission-1 save (lvl1.eep). Retail timeline (s6753, same PRESS): 640 boot 2.1, 1024 title 17.3, 512 select 38.4,
# 640 briefing 77.4, 512 flight 99.7. Port (s6753, same AP): title 12.8, select 24.0, briefing 42.6, flight 60.1.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=${1:?usage: run.sh SDIR}; mkdir -p $S
python3 tools/g3_eep_patch.py scratch/s6769/lvl16.eep $S/lvl1.eep --set 0x31=0 || exit 3
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
E="$HOME/Library/Application Support/Mupen64Plus/save/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep"
D=$S/retail; mkdir -p $D
cp -p "$E" $D/mupen_eep_backup.eep || exit 3
trap 'cp -p $D/mupen_eep_backup.eep "$E" && echo eep-restored' EXIT INT TERM
A=()
for i in $(seq 0 20); do A+=(--fb-dump 1024:$i:600000:200000:$D/t$(printf %02d $i).bin); done
for i in $(seq 0 19); do A+=(--fb-dump 512:$((2*i)):600000:200000:$D/s$(printf %02d $i).bin); done
for i in $(seq 0 21); do A+=(--fb-dump 640:$((76+i)):600000:200000:$D/b$(printf %02d $i).bin); done
cp $S/lvl1.eep "$E" || exit 3
env ${=RENV:-} tools/oracle/build/rs64_oracle --core $C --rom $R --secs 102 --vi-poll --vi-trace --rsp $RSP --video $V \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start \
  $A > $D/oracle.log 2>&1 &
RP=$!
env SAVE_FROM=$S/lvl1.eep SECS=70 CAP0=9 AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,50:start \
  zsh tools/g3_port_capture.sh $S/port > $S/port_run.txt 2>&1
t=0; while kill -0 $RP 2>/dev/null && [ $t -lt 150 ]; do sleep 5; t=$((t+5)); done
kill -9 $RP 2>/dev/null
cat $S/port_run.txt; grep -c '^\[fb-dump' $D/oracle.log; python3 tools/g3_frontend/width_timeline.py $D/oracle.log 2>/dev/null
