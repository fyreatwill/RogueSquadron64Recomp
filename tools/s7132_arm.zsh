#!/bin/zsh
# s7132 (21:9 capable; CW/CH env = capture size): usage arm.zsh <lvl> <name> "<extra env>" [delay=120] [dur=180]. dd4, 16:9, FPS60, no logging env.
# Records the RDP stream (ROGUESQ_G5B_FRAME, RAM every 20 swaps) and the presented window (g5b_capture 320x240) in ONE run.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
R=$PWD/scratch/s7132; B=$PWD/scratch/s6894; L=$1; N=$2; EX=${3:-}; DL=${4:-120}; DU=${5:-180}
$B/g5b_capture RogueSquadron64Recomp $R/$N.raw ${CW:-504} ${CH:-216} $DL $DU > $R/cap_$N.txt 2>&1 &
cp=$!
( /bin/sleep $((DL+DU+25)); pkill -9 -f g1_level_coverage_common; pkill -9 -f scratch/agent/m6_god_common.sh; pkill -9 -x RogueSquadron64Recomp ) & kp=$!
export TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' LOG_ENV='' FBD_EVERY_V=100000 HOLD_S=$((DL+DU)) FBH_V=0 TRI_V=0 DRAWN_V=0
export XENV_EXTRA="ROGUESQ_STORE_DIAG=0 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9 ROGUESQ_G5B_FRAME=$R/$N.cap ROGUESQ_G5B_FRAME_EVERY=20 $EX"
LEVEL=$L TAG_SUFFIX=s7132$N zsh scratch/agent/g1_level_coverage_common.zsh > $R/run_$N.out 2>&1
wait $cp; kill -9 $kp 2>/dev/null; pkill -9 -x RogueSquadron64Recomp
cat scratch/agent/m6/g1_lvl${L}s7132$N/summary 2>/dev/null | cut -c1-200 > $R/sum_$N.txt
cat $R/cap_$N.txt $R/sum_$N.txt
