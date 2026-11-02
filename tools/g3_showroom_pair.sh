#!/bin/zsh
# s6786 G3: SHOWROOM (screen 10, unlocked by passcode MAESTRO) retail oracle (rdplog + exec-trace marks) vs port
# (RS64_RDP_BIN_PORT + ROGUESQ_XTRACE_MEM marks + window captures), same presses, retail = port + OFF.
# usage: g3_showroom_pair.sh OUTDIR   (env T0 = first wheel press, port secs, default 55; GAP; DWELL = s in SHOWROOM;
#   RANDX="--exec-trace 0x80003430:400000:3470" = retail rand rows with the seed, for model-index alignment)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=${1:?}; mkdir -p $S/retail $S/port
OFF=${OFF:-7.3}; T0=${T0:-55}; GAP=${GAP:-16}
SPEC=800B380C:6:0:8,800B3FA0:6:58:2,800B4004:3:0:8,800C3B38:6:0:8,800C5880:6:0:8,800C3B4C:4:0:1,800C3B54:2:0:8
L=$(python3 tools/g3_passcode_sched.py MAESTRO $T0 0.5 down/a/b)  # GAP = s from the b to the SHOWROOM presses
TE=$(python3 -c "print(float('$L'.split(',')[-1].split(':')[0]))")
PP="17:down,19:a,30:down,31.5:down,40:a,$L,$(python3 -c "t=$TE;g=$GAP;print('%g:down,%g:down,%g:a'%(t+g,t+g+2,t+g+5))")"
# EXTRA = presses after the SHOWROOM entry, as <secs after the entry>:<key>,... (e.g. 12:a = CONCERT HALL)
[ -n "${EXTRA:-}" ] && PP="$PP,$(python3 -c "t=$TE+$GAP+5;print(','.join('%g:%s'%(t+float(a),k) for a,k in (e.split(':') for e in '$EXTRA'.split(','))))")"
RP=$(python3 -c "import sys;print(','.join('%g:%s'%(float(t)+$OFF,{'down':'ddown','up':'dup','left':'dleft','right':'dright'}.get(k,k)) for t,k in (e.split(':') for e in sys.argv[1].split(','))))" $PP)
PSECS=$(python3 -c "print(int($TE+$GAP+5+${DWELL:-19}))"); RSECS=$(python3 -c "print(int($PSECS+$OFF+15))")
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
V=tools/oracle/rdplog/rdplog.dylib
E="$HOME/Library/Application Support/Mupen64Plus/save/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep"
D=$S/retail
cp -p "$E" $D/mupen_eep_backup.eep || exit 3
trap 'cp -p $D/mupen_eep_backup.eep "$E" && echo eep-restored' EXIT INT TERM
cp scratch/s6779/r1/lvl1.eep "$E" || exit 3
echo "retail press: 6:start,11:start,16:start,$RP" > $S/press.txt; echo "port AP: 6:start,11:start,13:w1024,$PP" >> $S/press.txt
env RS64_XTRACE_MEM=$SPEC RS64_RDP_BIN=$PWD/$S/retail.bin RS64_RDP_BIN_WIDTH=1024 RS64_RDP_LOG=/dev/null RS64_RDP_BIN_MAX_MB=2048 \
  tools/oracle/build/rs64_oracle --core $C --rom $R --secs $RSECS --vi-poll --vi-trace --rsp $RSP --video $V \
  ${=RANDX:---exec-trace 0x800C3B38} --exec-trace-also 0x800C3B38 --exec-trace-also 0x800C5880 --exec-trace-also 0x800C3B4C --exec-trace-also 0x800C3B54 \
  --exec-trace-also 0x800B380C --exec-trace-also 0x800B3FA0 --exec-trace-also 0x800B4004 \
  --press 6:start,11:start,16:start,$RP > $D/oracle.log 2>&1 &
RPID=$!
env SAVE_FROM=scratch/s6779/r1/lvl1.eep SECS=$PSECS CAP0=$((${T0%.*}-8)) AP="6:start,11:start,13:w1024,$PP" \
  XE="ROGUESQ_DEBUG_WRITE=80003470:1:1024:5 ROGUESQ_RAND_TRACE=$PWD/$S/port/xt.txt ROGUESQ_XTRACE_MEM=$SPEC RS64_RDP_BIN_PORT=$PWD/$S/port.bin" \
  zsh tools/g3_port_capture.sh $S/port > $S/port_run.txt 2>&1
t=0; while kill -0 $RPID 2>/dev/null && [ $t -lt 300 ]; do sleep 5; t=$((t+5)); done
kill -9 $RPID 2>/dev/null
cat $S/port_run.txt; grep -c 'exec-trace\|xtrace' $D/oracle.log
