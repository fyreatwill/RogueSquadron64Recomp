#!/bin/zsh
# s7469 class DZ: ASan+UBSan (build_asan, tools/build_asan.sh UCODE=1) over the owner hangar abort/re-entry route
# (s7326 schedule: 4 mission loads, 3 PAUSE/ABORT -> SELECT YOUR CRAFT re-entries) at FPS60 dd8 21:9 WIDEWIN.
# Both planted controls (ROGUESQ_S7467_ASAN_PLANT, ROGUESQ_S7468_UCODE_PLANT) fire on this boot.
# The owner save is COPIED into build_asan/saves (build_asan's own file backed up to scratch/s7469/asan_save_backup and
# restored on exit); build/saves is never written; ROGUESQ_NO_SAVE_WRITE=1. Needs an idle, unlocked screen (~11 min).
# usage: tools/s7469_asan_hangar_route.zsh [name]  -> scratch/s7469/<name>/; exit = s7467_san_report.py (0 clean, 1 NEW, 3 ctl FAIL)
cd "$(git rev-parse --show-toplevel)" || exit 1
[ -x build_asan/RogueSquadron64Recomp ] || { echo "no build_asan"; exit 3; }
N=${1:-h}; R=$PWD/scratch/s7469/$N; rm -rf $R; mkdir -p $R scratch/s7469/asan_save_backup
B=scratch/s7469/asan_save_backup/rs64.n64.us.1.0.bin
[ -f $B ] || cp -p build_asan/saves/rs64.n64.us.1.0.bin $B || exit 3
trap 'cp -p $B build_asan/saves/rs64.n64.us.1.0.bin && echo asan-save-restored' EXIT
cp -p build/saves/rs64.n64.us.1.0.bin build_asan/saves/rs64.n64.us.1.0.bin || exit 3
AP=${AP2:-6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a,70:start,76:start,82:start,180:start,184:down,188:a,192:left,195:a,210:a,218:start,224:start,232:a,238:start,244:start,250:start,330:start,334:down,338:a,342:left,345:a,360:a,368:start,374:start,382:a,388:start,394:start,400:start,480:start,484:down,488:a,492:left,495:a,510:a,518:start,524:start,532:a,538:start,544:start,550:start}
SO="ASAN_OPTIONS=halt_on_error=0:detect_leaks=0:log_path=$R/san_$N UBSAN_OPTIONS=halt_on_error=0:print_stacktrace=1:log_path=$R/san_$N"
env GAMEDIR=build_asan SECS=${SECS:-650} CAP0=99999 AP=$AP XE="ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT_HOLD_MS=250 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=8 ROGUESQ_DD_UNSAFE=1 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_ASPECT=21:9 ROGUESQ_S7317_ALLOCMAP=1 ROGUESQ_S7326_CTL=1 ROGUESQ_S7467_ASAN_PLANT=1 ROGUESQ_S7468_UCODE_PLANT=1 $SO ${XE2:-}" zsh tools/g3_port_capture.sh $R/cap
L=$R/cap/run.log; ln -sf cap/run.log $R/log_$N.txt
echo "s7469 hangar_entries=$(grep -a -c 'hangarmenu-a0-entry' $L) initMission=$(grep -a -c 'initMission\] call' $L) crash=$(grep -a -c 'CRASH\|SIGSEGV\|SIGBUS' $L)"
python3 tools/s7467_san_report.py $R $N --plant $N --uplant $N --known tools/s7467_san_reviewed.tsv | tee $R/san_report.txt; exit ${pipestatus[1]}
