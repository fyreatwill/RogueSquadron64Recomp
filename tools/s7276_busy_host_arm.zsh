#!/bin/zsh
# s7276 G5c busy-host arm: N `yes` CPU spinners for the whole s7272 PLAIN fullscreen owner-recipe hold arm.
# N = hw.ncpu (every logical CPU) or hw.perflevel0.logicalcpu (P-cores only).
# usage: zsh tools/s7276_busy_host_arm.zsh <N> <TAG> [LEVEL=12] [DUR=600]
# out: scratch/s7276/<TAG>.out (hold/frozen scorer + rc), scratch/s7276/<TAG>.load (uptime every 10 s),
#      scratch/s7272/<TAG>/holds_sheet.jpg (every hold + SIGSTOP controls). rc as tools/s7272_g5c_hold_arm.zsh.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
mkdir -p scratch/s7276
N=$1; TG=$2; LV=${3:-12}; DU=${4:-600}; pids=()
for i in $(seq $N); do yes > /dev/null & pids+=$!; done
echo "load $N spinners: $pids" > scratch/s7276/$TG.load
( for k in $(seq 1 $(( (DU+300)/10 ))); do /bin/sleep 10; uptime >> scratch/s7276/$TG.load; done ) & up=$!
env PLAIN=1 DUR=$DU KEEP=1 FS=1 LEVEL=$LV TAG=$TG ASP=16:9 CW=480 zsh tools/s7272_g5c_hold_arm.zsh > scratch/s7276/$TG.out 2>&1; rc=$?
kill -9 $pids $up 2>/dev/null; pkill -x yes
echo "rc=$rc" >> scratch/s7276/$TG.out
exit $rc
