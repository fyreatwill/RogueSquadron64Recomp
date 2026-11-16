#!/bin/zsh
# s7433 class CP: default-on probe BOOKKEEPING cost on the guest thread, measured by an external profiler (/usr/bin/sample,
# not our runtime). One owner-recipe run via tools/s7431_stderr_volume.sh (copied folder, autopilot to lvl1 flight, no logging
# env) with the positive control ROGUESQ_DIAG_BUSY_GUEST_US=<us> per osViSwapBuffer toggled every 30 s in-run
# (ROGUESQ_DIAG_BUSY_TOGGLE=30). sample(1) windows of W s back to back from t=START; the analyzer aligns them with the
# [diag-quiet] flip lines and attributes guest-thread self samples to probe helpers vs game code.
# usage: tools/s7433_probe_cost.sh [busy_us=500] [start=95] [nwin=8] [W=12]
ROOT=${0:A:h:h}; US=${1:-500}; ST=${2:-95}; N=${3:-8}; W=${4:-12}; D=/tmp/rs64_s7431/${S7431_ARM:-P}
T=$(( ST + N * (W + 4) + 10 ))
rm -f $D/samples.idx $D/sample_*.txt(N)
( typeset -F SECONDS=0; sleep $ST; for i in $(seq 1 $N); do p=$(pgrep -x RogueSquadron64Recomp | head -1); [[ -n $p ]] || break
    print "$i $SECONDS $W" >> $D/samples.idx
    sample $p $W 1 -f $D/sample_$i.txt >/dev/null 2>&1; done ) &
env S7431_ARM=${S7431_ARM:-P} zsh $ROOT/tools/s7431_stderr_volume.sh $T ROGUESQ_DIAG_BUSY_TOGGLE=30 \
  ROGUESQ_DIAG_BUSY_GUEST_US=$US ROGUESQ_G1E_AQ=2 >/dev/null 2>&1
wait
python3 $ROOT/tools/s7433_probe_cost.py $D --busy-us $US
