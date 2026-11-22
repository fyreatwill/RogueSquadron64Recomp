#!/bin/zsh
# s7828: retail-only rdplog capture on the s7826 lvl1 route (VI-clocked --det presses) with Core CountPerOp=$CPO.
# usage: env CPO=<n> [RSECS=150] [OFF=5.75 (s7829: retail offset of presses 4-10)] [EEP=<save, default s6779 lvl1>]
#   [PP=<presses 4.. in port time, default the s7826 lvl1 route>] zsh tools/s7828_retail_cpo.sh OUTDIR  (s7832: EEP/PP)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
S=${1:?usage: s7828_retail_cpo.sh OUTDIR}; mkdir -p $S; S=$(cd $S && pwd)
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
source tools/oracle/rsp_plugin.sh
OFF=${OFF:-5.75}; PP=${PP:-19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start,103.5:start}
RP=$(python3 -c "import sys;print(','.join('%g:%s'%(float(t)+$OFF,k) for t,k in (e.split(':') for e in sys.argv[1].split(','))))" $PP)
SD=$S/savedir; mkdir -p $SD; cp ${EEP:-scratch/s6779/r1/lvl1.eep} "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
env RS64_RDP_BIN=$S/retail.bin RS64_RDP_LOG=/dev/null RS64_RDP_BIN_MAX_MB=6000 \
  tools/oracle/build/rs64_oracle $ODET --count-per-op ${CPO:?} --save-dir $SD --core $C --rom $R --secs ${RSECS:-150} --vi-poll --vi-trace \
  --rsp $RSP --video tools/oracle/rdplog/rdplog.dylib --press 6:start,11:start,16:start,$RP > $S/oracle.log 2>&1
echo "rc=$? $(grep -c . $S/oracle.log) lines"; grep -m3 'count-per-op\|det-core\|clock' $S/oracle.log
