#!/bin/zsh
# s7386 render-to-rdram coverage: level select -> LDESC -> craft -> mission intro, dd8 21:9.
# usage: run.zsh <name> "<extra env>"   Owner save read-only (no SAVE_FROM).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
AP=${AP:-6:start,11:start,16:start,21:start,25:left,27:start,31:cup,43:cup,47:start,58:a,64:a,70:a}  # append 140:start,144:down,148:a,152:left,155:a,165:a,173:a,181:a for the abort/MISSION FAILED/debrief tail
O=${RDIR:-scratch/s7386}/$1; rm -rf $O
env SECS=${SECS:-200} CAP0=${CAP0:-20} AP=$AP XE="ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT_HOLD_MS=250 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=8 ROGUESQ_DD_UNSAFE=1 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_ASPECT=21:9 ROGUESQ_S7384_LOG=1 ROGUESQ_S4265=1 ROGUESQ_LOG_G1D_TASK=1 $2" zsh tools/g3_port_capture.sh $O
L=$O/run.log
echo "$1 crash=$(grep -a -c 'CRASH\|SIGSEGV\|SIGBUS' $L) s7385=$(grep -a -c '^\[s7385\]' $L) wb=$(grep -a -c '\[g1d\].*wb' $L) caps=$(ls $O/w_*.png 2>/dev/null | wc -l)"
grep -a '^\[s7384\] calls' $L | tail -1
# Offline: python3 tools/s7386_frame_stats.py <arm...> (dark/stale counts), python3 scratch/s7386/sheet.py <out.jpg> <arm...>
