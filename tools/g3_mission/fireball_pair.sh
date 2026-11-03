#!/bin/zsh
# s6811 G3 large-fireball pair: lvl9 (s6761 lvl9.eep), dt pinned, the player's first crash (tick ~2130, retail VI ~13532 =
# oracle wall ~225.7 s, port VI ~8854 = ~148 s). The crash is the same tick in both arms (sim identical to t2217, s6761/s6804),
# so the destroyed-craft fireball + full-screen flash is a deterministic large-explosion event without any aiming.
# Retail: angrylion pixels, NDUMP x 512-wide fb dumps every DSTEP s from FARM s. Port: window captures CAP0..SECS.
# Score: tools/g3_oracle_match.py (best-pair d vs median control) + tools/g3_fireball_score.py (flash/fireball population).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=${1:?usage: fireball_pair.sh OUTDIR}; mkdir -p $S; EEP=${EEP:-scratch/s6761/lvl9.eep}
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
M=800AF374:29:10:10,800AF374:0:8011A880:32,800FA730:29:10:10,800FA730:0:8011A880:32,800FA730:0:8010FF30:2,800C6674:29:10:10,800C6674:0:8011A880:32,8006C010:4:0:16,8006C010:29:18:3,8006C010:0:8011A830:8,800FA730:0:8010C9E0:18,800FA730:0:8010C0E0:1
PIN=800FA730:29:30:3d088889
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
D=$S/retail; mkdir -p $D; SD=$(cd $D && pwd)/savedir; mkdir -p $SD; cp $EEP "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
A=(); for i in $(seq 0 $((${NDUMP:-192}-1))); do A+=(--fb-dump 512:$(printf '%.2f' $(( ${DSTEP:-0.15}*i ))):600000:200000:$D/b$(printf %03d $i).bin); done
env RS64_XTRACE_MEM=$M RS64_XTRACE_POKE=$PIN tools/oracle/build/rs64_oracle --save-dir $SD --core $C --rom $R --secs ${RSECS:-240} \
  --fb-arm-after ${FARM:-206} --vi-poll --vi-trace --rsp $RSP --video $V \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start \
  --hit-cap 2000 --watch-write 0x3FFFF0:0x3FFFF4 --exec-trace 0x80003430:400000:3470 --exec-trace-also 0x8006BEC8 --exec-trace-also 0x8006C018 --exec-trace-also 0x800AF374 --exec-trace-also 0x800FA730 --exec-trace-also 0x800C6674 --exec-trace-also 0x8006C010 --exec-trace-also 0x8008EE08 --exec-trace-also 0x8008EE84 \
  --debug-write 80003470:1:512:85 $A > $D/oracle.log 2>&1 &
RP=$!
O=$S/port
env SAVE_FROM=$EEP SECS=${PSECS:-170} CAP0=${CAP0:-135} BURST=${BURST:-} AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,50:start \
  XE="ROGUESQ_G3_CENSUS=$PWD/$O.census.txt ROGUESQ_DEBUG_WRITE=80003470:1:512:55 ROGUESQ_RAND_TRACE=$PWD/$O.rand.txt ROGUESQ_XTRACE_MEM=$M ROGUESQ_XTRACE_POKE=$PIN ${EXTRA:-}" \
  zsh tools/g3_port_capture.sh $O > $S/port_run.txt 2>&1
t=0; while kill -0 $RP 2>/dev/null && [ $t -lt 150 ]; do sleep 5; t=$((t+5)); done
kill -9 $RP 2>/dev/null
cat $S/port_run.txt; echo "retail dumps: $(grep -c '^\[fb-dump' $D/oracle.log)  port caps: $(ls $O/w_*.png | wc -l)"
