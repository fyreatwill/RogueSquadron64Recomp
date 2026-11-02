#!/bin/zsh
# s6804 G3 post-death screen pair (promoted from scratch/s6804/pair.sh), lvl9 (s6761 lvl9.eep), dt pinned, both arms run ~100 s past the death camera
# (retail t2050-2208, ~VI 13000-14000). Retail: rdplog (all VI widths), exec trace for ticks. Port: RS64_RDP_BIN_PORT
# (VI stamped) + window captures from CAP0. Score: tools/g3_rdp_segments.py + g3_rdp_segcmp.py.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=${1:?usage: death_pair.sh OUTDIR}; mkdir -p $S; EEP=scratch/s6761/lvl9.eep
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
M=800AF374:29:10:10,800AF374:0:8011A880:32,800FA730:29:10:10,800FA730:0:8011A880:32,800FA730:0:8010FF30:2,800C6674:29:10:10,800C6674:0:8011A880:32,8006C010:4:0:16,8006C010:29:18:3,8006C010:0:8011A830:8,800FA730:0:8010C9E0:18,800FA730:0:8010C0E0:1
PIN=800FA730:29:30:3d088889
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=$PWD/tools/oracle/rdplog/rdplog.dylib
D=$S/retail; mkdir -p $D; SD=$(cd $D && pwd)/savedir; mkdir -p $SD; cp $EEP "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
env RS64_XTRACE_MEM=$M RS64_XTRACE_POKE=$PIN RS64_RDP_BIN=$PWD/$S/retail.bin RS64_RDP_BIN_MAX_MB=12000 RS64_RDP_LOG=/dev/null \
  tools/oracle/build/rs64_oracle --save-dir $SD --core $C --rom $R --secs ${RSECS:-345} --vi-poll --vi-trace --rsp $RSP --video $V \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start \
  --hit-cap 2000 --watch-write 0x3FFFF0:0x3FFFF4 --exec-trace 0x80003430:400000:3470 --exec-trace-also 0x8006BEC8 --exec-trace-also 0x8006C018 --exec-trace-also 0x800AF374 --exec-trace-also 0x800FA730 --exec-trace-also 0x800C6674 --exec-trace-also 0x8006C010 --exec-trace-also 0x8008EE08 --exec-trace-also 0x8008EE84 \
  --debug-write 80003470:1:512:85 > $D/oracle.log 2>&1 &
RP=$!
O=$S/port
env SAVE_FROM=$EEP SECS=${PSECS:-345} CAP0=${CAP0:-190} AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,50:start \
  XE="ROGUESQ_G3_CENSUS=$PWD/$O.census.txt RS64_RDP_BIN_PORT=$PWD/$S/port.bin RS64_RDP_BIN_PORT_VI=1 RS64_RDP_BIN_PORT_MAX_MB=12000 ROGUESQ_DEBUG_WRITE=80003470:1:512:55 ROGUESQ_RAND_TRACE=$PWD/$O.rand.txt ROGUESQ_XTRACE_MEM=$M ROGUESQ_XTRACE_POKE=$PIN" \
  zsh tools/g3_port_capture.sh $O > $S/port_run.txt 2>&1
t=0; while kill -0 $RP 2>/dev/null && [ $t -lt 150 ]; do sleep 5; t=$((t+5)); done
kill -9 $RP 2>/dev/null
cat $S/port_run.txt; ls -la $S/*.bin
