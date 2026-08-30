#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s3311_cine_init_jal
BUILD=$ROOT/build
LOG=$OUT/run.log
DRIVER=$OUT/driver.log
mkdir -p "$OUT"

launch_once() {
    local log=$1
    : > "$log"
    (
        cd "$BUILD" || exit 2
        exec env \
            ROGUESQ_LOG_PHASE=1 \
            ROGUESQ_LOG_SP_YIELDED_AB=1 \
            ROGUESQ_LOG_EVENT_WIRING=1 \
            ROGUESQ_LOG_M5_POSTWAIT=1 \
            ROGUESQ_LOG_M5_POSTVIEWER_EDGE=1 \
            ROGUESQ_M5_POSTVIEWER_MARK_ALL=1 \
            ROGUESQ_LOG_M5_CINE_LOOP=1 \
            ROGUESQ_M5_CINE_LOOP_MARK_ALL=1 \
            ROGUESQ_LOG_M5_STAGE_ADV=1 \
            ROGUESQ_M5_STAGE_ADV_MARK_ALL=1 \
            ROGUESQ_LOG_M5_CINE_INIT_JAL=1 \
            ROGUESQ_M5_CINE_INIT_JAL_MARK_ALL=1 \
            ./RogueSquadron64Recomp
    ) > "$log" 2>&1 &
    echo $!
}

analyze() {
    local log=$1
    count_fixed() {
        grep -a -F -c -- "$2" "$1" 2>/dev/null || true
    }
    mark_count=$(grep -a '\[s3311-cine-init-jal-control\] mark edge_id=' "$log" | sed -n 's/.*edge_id=\([0-9][0-9]*\).*/\1/p' | sort -nu | wc -l | tr -d ' ')
    print "mark_ids=$mark_count" >> "$DRIVER"
    print "s3308_mark_ids=$(grep -a '\[s3308-stage-adv-control\] mark edge_id=' "$log" | sed -n 's/.*edge_id=\([0-9][0-9]*\).*/\1/p' | sort -nu | wc -l | tr -d ' ')" >> "$DRIVER"
    print "s3306_mark_ids=$(grep -a '\[s3306-cine-loop-control\] mark edge_id=' "$log" | sed -n 's/.*edge_id=\([0-9][0-9]*\).*/\1/p' | sort -nu | wc -l | tr -d ' ')" >> "$DRIVER"
    print "s3305_mark_ids=$(grep -a '\[s3305-postviewer-control\] mark edge_id=' "$log" | sed -n 's/.*edge_id=\([0-9][0-9]*\).*/\1/p' | sort -nu | wc -l | tr -d ' ')" >> "$DRIVER"
    print "arm_rows=$(count_fixed "$log" 'arm=completion-wins-default')" >> "$DRIVER"
    print "reset_rows=$(count_fixed "$log" 'requested_pre=1 requested_post=0')" >> "$DRIVER"
    print "sp_complete=$(count_fixed "$log" '[event-wiring] complete kind=SP')" >> "$DRIVER"
    print "phase_640=$(count_fixed "$log" 'vi_width=640 (was')" >> "$DRIVER"
    print "viewer_entry=$(count_fixed "$log" 'edge=entry site=runMenuModelViewerScreen')" >> "$DRIVER"
    print "viewer_return=$(count_fixed "$log" 'edge=return site=runMenuModelViewerScreen')" >> "$DRIVER"
    print "cine_entry=$(count_fixed "$log" 'site=cinematic-entry')" >> "$DRIVER"
    print "loop_head=$(count_fixed "$log" 'site=loop-head')" >> "$DRIVER"
    print "title_1024=$(count_fixed "$log" 'vi_width=1024 (was')" >> "$DRIVER"
    print "crash=$(count_fixed "$log" '[CRASH]') abort=$(count_fixed "$log" '[ABORT]')" >> "$DRIVER"

    for id in {0..3}; do
        rows=$(grep -a -c "\[s3311-cine-init-jal\].*edge_id=$id " "$log" 2>/dev/null || true)
        first=$(grep -a -m1 "\[s3311-cine-init-jal\].*edge_id=$id " "$log" 2>/dev/null || true)
        last=$(grep -a "\[s3311-cine-init-jal\].*edge_id=$id " "$log" 2>/dev/null | tail -1 || true)
        print -r -- "edge_$id=$rows" >> "$DRIVER"
        print -r -- "edge_${id}_first=${first}" >> "$DRIVER"
        print -r -- "edge_${id}_last=${last}" >> "$DRIVER"
    done

    time_taken=$(grep -a -c '\[s3311-cine-init-jal\].*edge_id=0 .*taken=1' "$log" 2>/dev/null || true)
    time_not=$(grep -a -c '\[s3311-cine-init-jal\].*edge_id=0 .*taken=0' "$log" 2>/dev/null || true)
    flag_taken=$(grep -a -c '\[s3311-cine-init-jal\].*edge_id=1 .*taken=1' "$log" 2>/dev/null || true)
    flag_not=$(grep -a -c '\[s3311-cine-init-jal\].*edge_id=1 .*taken=0' "$log" 2>/dev/null || true)
    active_taken=$(grep -a -c '\[s3311-cine-init-jal\].*edge_id=2 .*taken=1' "$log" 2>/dev/null || true)
    active_not=$(grep -a -c '\[s3311-cine-init-jal\].*edge_id=2 .*taken=0' "$log" 2>/dev/null || true)
    jal_n=$(grep -a -c '\[s3311-cine-init-jal\].*edge_id=3 ' "$log" 2>/dev/null || true)
    print "time_taken=$time_taken time_not=$time_not flag_taken=$flag_taken flag_not=$flag_not active_taken=$active_taken active_not=$active_not jal_n=$jal_n" >> "$DRIVER"

    controls_ok=1
    (( mark_count == 4 )) || controls_ok=0
    grep -a -q '\[s3306-cine-loop-control\] mark edge_id=0' "$log" || controls_ok=0
    grep -a -q '\[s3308-stage-adv-control\] mark edge_id=0' "$log" || controls_ok=0
    grep -a -q '\[event-wiring\] complete kind=SP' "$log" || controls_ok=0
    grep -a -q '\[phase\] vi_width=640 .*origin=0x0066A500' "$log" || controls_ok=0
    grep -a -q '\[m5-postwait\].*edge=return site=runMenuModelViewerScreen' "$log" || controls_ok=0
    grep -a -q '\[s3305-postviewer\].*edge_id=19 site=cinematic-entry' "$log" || controls_ok=0
    grep -a -q '\[s3306-cine-loop\].*edge_id=1 site=loop-head' "$log" || controls_ok=0
    grep -a -q '\[s3306-cine-loop\].*edge_id=2 site=exit-gate' "$log" || controls_ok=0

    if (( controls_ok == 0 )); then
        print 'verdict=H-CoverageInvalid' >> "$DRIVER"
        return 5
    fi

    if (( jal_n > 0 )); then
        print 'verdict=H-JalFires' >> "$DRIVER"
        return 0
    fi

    if ! grep -a -q '\[s3311-cine-init-jal\].*edge_id=0 site=time-pred' "$log"; then
        print 'verdict=H-JalUnreached' >> "$DRIVER"
        return 1
    fi

    if (( time_taken > 0 )) && (( time_not == 0 )) &&
       ! grep -a -q '\[s3311-cine-init-jal\].*edge_id=1 site=flag-byte' "$log" &&
       (( jal_n == 0 )); then
        print 'verdict=H-TimePredSkip' >> "$DRIVER"
        return 2
    fi

    if (( flag_taken > 0 )) && (( jal_n == 0 )); then
        print 'verdict=H-FlagByteSkip' >> "$DRIVER"
        return 3
    fi

    if (( active_taken > 0 )) && (( jal_n == 0 )); then
        print 'verdict=H-AlreadyActiveSkip' >> "$DRIVER"
        return 4
    fi

    print 'verdict=H-CoverageInvalid' >> "$DRIVER"
    return 5
}

watch_pid() {
    local pid=$1
    local log=$2
    local deadline=$((SECONDS + 120))
    local terminal=watchdog
    while (( SECONDS < deadline )); do
        if ! kill -0 "$pid" 2>/dev/null; then
            terminal=process-exit
            break
        fi
        sleep 2
        if grep -a -q -m1 '\[CRASH\]\|\[ABORT\]\|Bus error\|Segmentation fault' "$log"; then
            terminal=crash
            break
        fi
        if grep -a -q -m1 '\[phase\] vi_width=1024 ' "$log"; then
            terminal=title-1024
            break
        fi
    done
    print "terminal=$terminal elapsed=${SECONDS}s ended=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$DRIVER"
    kill -9 "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    print -r -- "$terminal"
}

: > "$DRIVER"
: > "$LOG"
print "started=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$DRIVER"

GAME_PID=$(launch_once "$LOG")
print "pid=$GAME_PID attempt=1" >> "$DRIVER"
term=$(watch_pid "$GAME_PID" "$LOG")

if [[ "$term" == crash ]] && ! grep -a -q '\[s3311-cine-init-jal-control\] mark edge_id=' "$LOG"; then
    print "retrying same binary after VI-320 crash" >> "$DRIVER"
    mv -f "$LOG" "$OUT/run1_crash.log"
    SECONDS=0
    GAME_PID=$(launch_once "$LOG")
    print "pid=$GAME_PID attempt=2" >> "$DRIVER"
    term=$(watch_pid "$GAME_PID" "$LOG")
fi

analyze "$LOG"
rc=$?
print "analyze_rc=$rc" >> "$DRIVER"
exit $rc
