#!/bin/zsh
# s6783 G3 front-end pair runner: retail oracle (angrylion or rdplog) + port window captures, same menu presses.
# Retail dumps every 1 s from the first 1024 VI (ND, default 50); port schedule gates on the title (13:w1024) and
# retail presses = port + OFF (7.3 s: retail title menu turns interactive ~3 s after its first 1024 VI, s6783).
# Screen loads are 2-5 s slower in retail (image worker), so leave >=5 s between presses. Menus: tools/g3_rdp_frame_match.py.
# s7820: AP0=<port lead-in> (default 6:start,11:start,13:w1024) and PCLOCK=vi (port autopilot on ultramodern's VI count,
# ROGUESQ_AUTOPILOT_CLOCK=vi). Frame-exact title alignment: AP0=6:start,11:start,11.5:w1024 gates on the port's real title
# onset; retail title onset is VI 1035 (--det), so OFF=5.75 (ORX="<extra rs64_oracle args>", e.g. --debug-write) puts both presses on the same title VI (SELECT GAME photo
# = rand%7 at the press, one rand per title VI, s6780).
# usage: env PP=<port schedule> [EEP=<save .eep, default s6779 lvl1>] [ND] [RSECS] [VIDEO=tools/oracle/rdplog/rdplog.dylib RENV="RS64_RDP_BIN=<abs> RS64_RDP_BIN_WIDTH=1024 RS64_RDP_LOG=/dev/null" XE="RS64_RDP_BIN_PORT=<abs>"] g3_menu_pair.sh OUTDIR
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=${1:?usage: g3_menu_pair.sh OUTDIR}; mkdir -p $S
OFF=${OFF:-7.3}
PP=${PP:?}
RP=$(python3 -c "import sys;print(','.join('%g:%s'%(float(t)+$OFF,{'down':'ddown','up':'dup','right':'dright','left':'dleft'}.get(k,k)) for t,k in (e.split(':') for e in sys.argv[1].split(','))))" $PP)
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
source /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle/rsp_plugin.sh  # s7816: VU-fixed cxd4 by default
V=${VIDEO:-/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib}
D=$S/retail; mkdir -p $D
A=(); for i in $(seq 0 ${ND:-50}); do A+=(--fb-dump 1024:$i:600000:200000:$D/t$(printf %03d $i).bin); done
# s6800: private Core SaveSRAMPath (--save-dir); the user-wide mupen save is never touched
mkdir -p $D; SD=$(cd $D && pwd)/savedir; mkdir -p $SD; cp ${EEP:-scratch/s6779/r1/lvl1.eep} "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
AP0=${AP0:-6:start,11:start,13:w1024}; [ "${PCLOCK:-}" = vi ] && XE="ROGUESQ_AUTOPILOT_CLOCK=vi ${XE:-}"
echo "retail press: 6:start,11:start,16:start,$RP" > $S/press.txt; echo "port AP: $AP0,$PP clock=${PCLOCK:-wall}" >> $S/press.txt
env ${=RENV:-} tools/oracle/build/rs64_oracle $ODET ${=ORX:-} --save-dir $SD --core $C --rom $R --secs ${RSECS:-66} --vi-poll --vi-trace --rsp $RSP --video $V \
  --press 6:start,11:start,16:start,$RP $A > $D/oracle.log 2>&1 &
RPID=$!
env SAVE_FROM=${EEP:-scratch/s6779/r1/lvl1.eep} SECS=${PSECS:-60} CAP0=12 AP=$AP0,$PP XE="${XE:-}" \
  zsh tools/g3_port_capture.sh $S/port > $S/port_run.txt 2>&1
t=0; while kill -0 $RPID 2>/dev/null && [ $t -lt 240 ]; do sleep 5; t=$((t+5)); done
kill -9 $RPID 2>/dev/null
cat $S/port_run.txt; grep -c '^\[fb-dump' $D/oracle.log; grep 'gate' $S/port/run.log
