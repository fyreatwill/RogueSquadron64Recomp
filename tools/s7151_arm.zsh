#!/bin/zsh
# s7151 (from s7146_arm): colour-space discriminator. Two g5b_capture processes (same s7151 binary) on the SAME game window
# in ONE run: <name>_srgb.raw (default, cfg.colorSpaceName sRGB) and <name>_nat.raw (G5B_CS=native = pre-s7151 behaviour).
# RDP stream recording optional (FROM, default off). Owner save read-only (no SAVE_FROM, NO_SAVE_WRITE).
# usage: s7151_arm.zsh <name> "<extra env>"   env: SECS (300) DL (150) DU (115) CW/CH (504/216) ASP (21:9) AP FROM EVERY
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
R=$PWD/scratch/${RDIR:-s7151}; mkdir -p $R; N=$1; O=$R/$N; rm -rf $O
AP=${AP:-6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a,262:start}
B=${CAPBIN:-scratch/s7151/g5b_capture}
$B RogueSquadron64Recomp $R/${N}_srgb.raw ${CW:-504} ${CH:-216} ${DL:-150} ${DU:-115} > $R/cap_${N}_srgb.txt 2>&1 &
c1=$!
cp -p $B ${B}_b  # s7151: two processes of the SAME executable path both hang in the window lookup (measured twice); a copy works
env G5B_CS=native ${B}_b RogueSquadron64Recomp $R/${N}_nat.raw ${CW:-504} ${CH:-216} ${DL:-150} ${DU:-115} > $R/cap_${N}_nat.txt 2>&1 &
c2=$!
env SECS=${SECS:-300} CAP0=${CAP0:-99999} AP=$AP XE="ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT_HOLD_MS=250 ROGUESQ_STORE_DIAG=0 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=${ASP:-21:9} ROGUESQ_G5B_FRAME=$O.cap ROGUESQ_G5B_FRAME_EVERY=${EVERY:-5} ROGUESQ_G5B_FRAME_FROM=${FROM:-99999999} ROGUESQ_G5B_FRAME_MAX_MB=12000 $2" zsh tools/g3_port_capture.sh $O
wait $c1 $c2; pkill -9 -x RogueSquadron64Recomp
echo "$N crash=$(grep -a -c -i 'crash\|SIGSEGV\|SIGBUS' $O/run.log) srgb: $(tr '\n' ' ' < $R/cap_${N}_srgb.txt) nat: $(tr '\n' ' ' < $R/cap_${N}_nat.txt)"
