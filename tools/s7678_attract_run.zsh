#!/bin/zsh
# s7678: stand-ins across REAL level changes: no input -> attract demo playlist cycles levels (s6911: 15 levels / 970 s).
# owner recipe dd4 16:9 FPS60, STANDINS=1 LOG=1, owner save read-only. usage: run.zsh <name> "<extra env>"
cd "$(git rev-parse --show-toplevel)" || exit 1
N=${1:-a}; O=$PWD/scratch/s7678/$N; rm -rf $O; mkdir -p $O
env SECS=${SECS:-420} CAP0=99999 AP=99999:start XE="ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9 ROGUESQ_STANDINS=1 ROGUESQ_STANDINS_LOG=1 $2" zsh tools/g3_port_capture.sh $O/cap
L=$O/cap/run.log
echo "tag=s7678_$N rebuilds=$(grep -a -c '^\[standins\] [0-9]* objects' $L) levels=$(grep -a '^\[standins\] [0-9]* objects' $L | awk '{print $NF}' | tr '\n' ,) crash=$(grep -a -c '\[CRASH\]\|SIGSEGV\|SIGBUS' $L)"
grep -a '^\[standins\] [0-9]* objects\|\[s7677-gen\]' $L
