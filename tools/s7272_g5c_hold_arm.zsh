#!/bin/zsh
# s7272: L4 dd4 16:9 FPS60 WIDEWIN tog3 stack phases + SIGSTOP 1 s positive controls at capture +60/+160/+260 s.
# usage: env TAG=<name> ASP=16:9|21:9 CW=480|630 zsh tools/s7272_g5c_hold_arm.zsh ; analysis tools/s7272_image_hold.py (holds per tog3 phase, SIGSTOP control windows apart).
# s7274: LEVEL=<n> (default 4) picks the level; FS=1 adds ROGUESQ_FULLSCREEN=1 (owner recipe).
# PLAIN=1: no WIDEWIN/MELT env at all (owner env only; tog3 phase labels then mean nothing). DUR=<s> capture length (default 300).
# XE=<env>: extra game env appended (s7277: ROGUESQ_PRESENT_RING=<abs path>).
# KEEP=1: write $O/holds_sheet.jpg + sheet.txt (tools/s7273_hold_sheet.py) before the raw is deleted.
# Exit 3 when the SIGSTOP control is not caught 3/3 (>=900 ms), 1 on a crash line.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
T=${TAG:-s7272f}; LV=${LEVEL:-4}; O=scratch/s7272/$T; mkdir -p $O; : > $O/ctl.txt
E="ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_DD_WIDEWIN_STACK=0 ROGUESQ_DD_WIDEWIN_R=88 ROGUESQ_DD_WIDEWIN_R_TOG=3 ROGUESQ_DD_WIDEWIN_R3=0,88,88 ROGUESQ_DD_WIDEWIN_MERGE=0.4 ROGUESQ_DD_WIDEWIN_MERGE_E=16 ROGUESQ_DD_WIDEWIN_MERGE_TOG=3 ROGUESQ_DD_WIDEWIN_MERGE3=0,1,0${FS:+ ROGUESQ_FULLSCREEN=1}"
[[ -n $PLAIN ]] && E="${FS:+ROGUESQ_FULLSCREEN=1}"; E="$E ${XE:-}"; DU=${DUR:-300}
( for k in $(seq 1 $(( (DU+150)/10 ))); do /bin/sleep 10; osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron64Recomp") to true' >/dev/null 2>&1; done ) & fp=$!
( for off in 180 280 380; do /bin/sleep $(( off - ${last:-0} )); last=$off
    pid=$(. tools/rs64_game_pid.zsh; rs64_game_pid) || { echo "skip-multi $off" >> $O/ctl.txt; continue; }
    a=$(python3 -c 'import time;print(time.clock_gettime_ns(time.CLOCK_UPTIME_RAW)*24//1000)'); kill -STOP $pid; /bin/sleep 1; kill -CONT $pid
    b=$(python3 -c 'import time;print(time.clock_gettime_ns(time.CLOCK_UPTIME_RAW)*24//1000)'); echo "$a $b" >> $O/ctl.txt; done ) & sp=$!
env CW=${CW:-480} CH=270 CULL=1 ASP=${ASP:-16:9} zsh scratch/s7009/arm.zsh $LV 4 $T "$E" 120 $DU > $O/arm.txt 2>&1
kill -9 $fp $sp 2>/dev/null
python3 tools/s7272_image_hold.py scratch/s7009/$T.raw 250 $O/ctl.txt > $O/hold.txt 2>&1
python3 tools/g5c_frozen_runs.py scratch/s7009/$T.raw 250 > $O/frozen.txt 2>&1
grep -a -h 's7258\|s7010-clk\|CRASH\|SIGSEGV\|SIGBUS' scratch/agent/m6/g1_lvl${LV}s7009$T/*.log 2>/dev/null | head -8 > $O/log.txt
[[ -n $KEEP ]] && python3 tools/s7273_hold_sheet.py scratch/s7009/$T.raw $O/holds_sheet.jpg 250 $O/ctl.txt 0.5 > $O/sheet.txt 2>&1; rm -f scratch/s7009/$T.raw; cat $O/hold.txt $O/frozen.txt $O/log.txt; tail -3 $O/arm.txt
c=$(grep -o 'caught .*' $O/hold.txt | grep -o '[0-9]*ms' | tr -d ms | awk '$1>=900' | wc -l); echo "control_hits $c"
grep -a -cE -f tools/agent/fatal_patterns.txt scratch/agent/m6/g1_lvl${LV}s7009$T/run.log | read cr;  # s7453 DI: shared fatal list
 echo "crash_lines $cr"
(( cr > 0 )) && exit 1; (( c < 3 )) && exit 3; exit 0
