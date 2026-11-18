#!/bin/zsh
# s7584 class UI: build_autoinit (pattern stack fill) + MallocScribble=1 over the s7469 hangar abort/re-entry route (4 mission loads,
# 3 re-entries, FPS60 dd8 21:9 WIDEWIN). build_autoinit/saves holds a COPY of the owner save; NO_SAVE_WRITE=1. Plant 7 = control.
cd "$(git rev-parse --show-toplevel)" || exit 1
N=${1:-h}; R=$PWD/scratch/s7584/$N; rm -rf $R; mkdir -p $R
AP=${AP2:-6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a,70:start,76:start,82:start,180:start,184:down,188:a,192:left,195:a,210:a,218:start,224:start,232:a,238:start,244:start,250:start,330:start,334:down,338:a,342:left,345:a,360:a,368:start,374:start,382:a,388:start,394:start,400:start,480:start,484:down,488:a,492:left,495:a,510:a,518:start,524:start,532:a,538:start,544:start,550:start}
env GAMEDIR=${GD:-build_autoinit} SECS=${SECS:-650} CAP0=99999 AP=$AP XE="ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT_HOLD_MS=250 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=8 ROGUESQ_DD_UNSAFE=1 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_ASPECT=21:9 ROGUESQ_S7317_ALLOCMAP=1 ROGUESQ_S7326_CTL=1 MallocScribble=1 ROGUESQ_S7578_PLANT=7 ${XE2:-}" zsh tools/g3_port_capture.sh $R/cap
L=$R/cap/run.log; ln -sf cap/run.log $R/log_$N.txt
echo "s7584 hangar_entries=$(grep -a -c hangarmenu-a0-entry $L) initMission=$(grep -a -c "initMission\] call" $L) crash=$(grep -a -c "CRASH\|SIGSEGV\|SIGBUS" $L) plant=$(grep -a -m1 s7584-plant7 $L)"
