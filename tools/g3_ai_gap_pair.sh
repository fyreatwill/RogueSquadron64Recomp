#!/bin/zsh
# s6807 G3: retail-vs-port guest AI feed gaps ACROSS scene transitions (g3-transition-ai-gap).
# Both arms trace osAiSetNextBuffer (0x8008EE08/0x8008EE84) + runInMissionFrame (0x800FA730) from boot: the same harmless
# rngSeed poke 80003470:1 on the first 320-wide VI at 0 s arms the port ROGUESQ_RAND_TRACE and the oracle exec trace,
# instead of run.sh's mission-time DWARM/ARM arm (which hides every transition). Then tools/g3_ai_gaps.py SDIR with
# G3_GAP_MIN=3 lists every gap >= 3 VI in VI order per arm.
# usage: zsh tools/g3_ai_gap_pair.sh SDIR LEVEL   env: RSECS (220) PSECS (200) PRESS AP (run.sh defaults) BASE_EEP
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=$1; L=$2; [ -n "$S" ] && [ -n "$L" ] || { echo "usage: g3_ai_gap_pair.sh SDIR LEVEL" >&2; exit 2; }
mkdir -p $S; EEP=$S/lvl$((L+1)).eep
python3 tools/g3_eep_patch.py ${BASE_EEP:-scratch/s6769/lvl16.eep} $EEP --set 0x31=$(( L > 16 ? 16 : L )) || exit 3
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
source /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle/rsp_plugin.sh  # s7816: VU-fixed cxd4 by default
V=/Users/williambuckley/Documents/Tools/g3_angrylion/build/mupen64plus-video-angrylion-plus.dylib
D=$S/retail; mkdir -p $D/savedir; SD=$(cd $D && pwd)/savedir
cp $EEP "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
tools/oracle/build/rs64_oracle $ODET --save-dir $SD --core $C --rom $R --secs ${RSECS:-220} --vi-poll --vi-trace --rsp $RSP --video $V \
  --press ${PRESS:-6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start} \
  --hit-cap 2000 --watch-write 0x3FFFF0:0x3FFFF4 --exec-trace 0x8008EE08:400000 --exec-trace-also 0x8008EE84 \
  --exec-trace-also 0x800FA730 --debug-write 80003470:1:320:0 > $D/oracle.log 2>&1 &
RP=$!
O=$S/port
env SAVE_FROM=$EEP SECS=${PSECS:-200} CAP0=9999 AP=${AP:-6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,50:start} \
  XE="ROGUESQ_DEBUG_WRITE=80003470:1:320:0 ROGUESQ_RAND_TRACE=$PWD/$O.rand.txt" \
  zsh tools/g3_port_capture.sh $O > $S/port_run.txt 2>&1
t=0; while kill -0 $RP 2>/dev/null && [ $t -lt 120 ]; do sleep 5; t=$((t+5)); done
kill -9 $RP 2>/dev/null
echo "retail xtrace rows: $(grep -c '^\[xtrace\]' $D/oracle.log)  port rows: $(wc -l < $O.rand.txt)"
env G3_GAP_MIN=3 python3 tools/g3_ai_gaps.py $S
