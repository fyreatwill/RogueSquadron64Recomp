#!/bin/zsh
# s7142 G3: hangar first-entry pans (s6995 route) at the owner recipe + 21:9, recording the RDP stream (ROGUESQ_G5B_FRAME, RAM every
# EVERY swaps from swap FROM) and the presented window (g5b_capture CWxCH) in ONE run. Owner save read-only (no SAVE_FROM, NO_SAVE_WRITE).
# usage: s7142_arm.zsh <name> "<extra env>"   env: FROM (1900) EVERY (3) SECS (80) DL (38) DU (40) CW/CH (504/216) ASP (21:9)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
R=$PWD/scratch/s7142; mkdir -p $R; N=$1; O=$R/$N; rm -rf $O
AP=6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a,70:start,76:start
scratch/s6894/g5b_capture RogueSquadron64Recomp $R/$N.raw ${CW:-504} ${CH:-216} ${DL:-38} ${DU:-40} > $R/cap_$N.txt 2>&1 &
cp=$!
env SECS=${SECS:-80} CAP0=99999 AP=$AP XE="ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT_HOLD_MS=250 ROGUESQ_STORE_DIAG=0 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=${ASP:-21:9} ROGUESQ_G5G_CAM=$O.g5g.txt ROGUESQ_G5B_FRAME=$O.cap ROGUESQ_G5B_FRAME_EVERY=${EVERY:-3} ROGUESQ_G5B_FRAME_FROM=${FROM:-1900} ROGUESQ_G5B_FRAME_MAX_MB=12000 $2" zsh tools/g3_port_capture.sh $O
wait $cp; pkill -9 -x RogueSquadron64Recomp
echo "$N crash=$(grep -a -c -i 'crash\|SIGSEGV\|SIGBUS' $O/run.log) cap=$(du -m $O.cap | cut -f1)MB $(cat $R/cap_$N.txt | tr '\n' ' ')"
