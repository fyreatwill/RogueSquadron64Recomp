#!/bin/zsh
# s7277 G5c within-run load toggle: s7272 PLAIN fullscreen owner-recipe hold arm + ROGUESQ_PRESENT_RING, with a host load
# switched ON/OFF every PER s from launch+ST s (first window OFF). LOAD=cpu: N `yes` spinners (default hw.ncpu);
# LOAD=gpu: scratch/s7277/gpu_busy (tools/s7277_gpu_busy.swift, saturating Metal compute). Toggle times (CLOCK_UPTIME_RAW s,
# the ring's clock) -> scratch/s7277/<TAG>.toggle. Score: python3 tools/s7277_toggle_score.py <TAG>.
# GXE=<env>: extra game env (e.g. ROGUESQ_QOS_ALL=1). GPU_ITER=<n>: saturator inner iterations (default 20000 = ~35.8 ms/cmdbuf; s7282).
# usage: env LOAD=cpu|gpu TAG=<t> [LEVEL=12] [DUR=600] [PER=60] [ST=150] [N=] zsh tools/s7277_toggle_load_arm.zsh
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
R=$PWD/scratch/s7277; mkdir -p $R; T=${TAG:-s7277}; LV=${LEVEL:-12}; DU=${DUR:-600}; PER=${PER:-60}; ST=${ST:-150}
N=${N:-$(sysctl -n hw.ncpu)}; TG=$R/$T.toggle; : > $TG
now(){ python3 -c 'import time;print("%.6f"%time.clock_gettime(time.CLOCK_UPTIME_RAW))'; }
on(){ if [[ $LOAD == gpu ]]; then $R/gpu_busy ${GPU_ITER:-20000} 2>>$R/$T.gpu & else for i in $(seq $N); do yes > /dev/null & done; fi; echo "on $(now)" >> $TG; }
off(){ if [[ $LOAD == gpu ]]; then pkill -9 -f scratch/s7277/gpu_busy; else pkill -9 -x yes; fi; echo "off $(now)" >> $TG; }
( /bin/sleep $ST; echo "off $(now)" >> $TG; k=0; while (( ST + (k+1)*PER < 120 + DU )); do /bin/sleep $PER; (( k % 2 == 0 )) && on || off; k=$((k+1)); done; off ) & tp=$!
env PLAIN=1 FS=1 KEEP=1 DUR=$DU LEVEL=$LV TAG=$T ASP=16:9 CW=480 XE="ROGUESQ_PRESENT_RING=$R/ring_$T.txt ${GXE:-}" zsh tools/s7272_g5c_hold_arm.zsh > $R/$T.out 2>&1; rc=$?
kill -9 $tp 2>/dev/null; pkill -9 -x yes; pkill -9 -f scratch/s7277/gpu_busy; echo "end $(now)" >> $TG
cp scratch/s7272/$T/ctl.txt $R/$T.ctl 2>/dev/null; echo "rc=$rc" >> $R/$T.out; exit $rc
