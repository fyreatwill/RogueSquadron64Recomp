#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s3308_stage_advancer
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
            ./RogueSquadron64Recomp
    ) > "$log" 2>&1 &
    echo $!
}

analyze() {
    local log=$1
    count_fixed() {
        grep -a -F -c -- "$2" "$1" 2>/dev/null || true
    }
    mark_count=$(grep -a '\[s3308-stage-adv-control\] mark edge_id=' "$log" | sed -n 's/.*edge_id=\([0-9][0-9]*\).*/\1/p' | sort -nu | wc -l | tr -d ' ')
    print "mark_ids=$mark_count" >> "$DRIVER"
    print "s3306_mark_ids=$(grep -a '\[s3306-cine-loop-control\] mark edge_id=' "$log" | sed -n 's/.*edge_id=\([0-9][0-9]*\).*/\1/p' | sort -nu | wc -l | tr -d ' ')" >> "$DRIVER"
    print "s3305_mark_ids=$(grep -a '\[s3305-postviewer-control\] mark edge_id=' "$log" | sed -n 's/.*edge_id=\([0-9][0-9]*\).*/\1/p' | sort -nu | wc -l | tr -d ' ')" >> "$DRIVER"
    print "arm_rows=$(count_fixed "$log" 'arm=completion-wins-default')" >> "$DRIVER"
    print "reset_rows=$(count_fixed "$log" 'requested_pre=1 requested_post=0')" >> "$DRIVER"
    print "sp_complete=$(count_fixed "$log" '[event-wiring] complete kind=SP')" >> "$DRIVER"
    print "phase_640=$(count_fixed "$log" 'vi_width=640 (was')" >> "$DRIVER"
    print "viewer_entry=$(count_fixed "$log" 'edge=entry site=runMenuModelViewerScreen')" >> "$DRIVER"
    print "viewer_return=$(count_fixed "$log" 'edge=return site=runMenuModelViewerScreen')" >> "$DRIVER"
    print "cine_entry=$(count_fixed "$log" 'site=cinematic-entry')" >> "$DRIVER"
    print "title_1024=$(count_fixed "$log" 'vi_width=1024 (was')" >> "$DRIVER"
    print "crash=$(count_fixed "$log" '[CRASH]') abort=$(count_fixed "$log" '[ABORT]')" >> "$DRIVER"

    for id in {0..5}; do
        rows=$(grep -a -c "\[s3308-stage-adv\].*edge_id=$id " "$log" 2>/dev/null || true)
        first=$(grep -a -m1 "\[s3308-stage-adv\].*edge_id=$id " "$log" 2>/dev/null || true)
        last=$(grep -a "\[s3308-stage-adv\].*edge_id=$id " "$log" 2>/dev/null | tail -1 || true)
        print -r -- "edge_$id=$rows" >> "$DRIVER"
        print -r -- "edge_${id}_first=${first}" >> "$DRIVER"
        print -r -- "edge_${id}_last=${last}" >> "$DRIVER"
    done

    ptr_zero=$(grep -a -c '\[s3308-stage-adv\].*edge_id=1 .*taken=1' "$log" 2>/dev/null || true)
    ptr_nz=$(grep -a -c '\[s3308-stage-adv\].*edge_id=1 .*taken=0' "$log" 2>/dev/null || true)
    cmp_taken=$(grep -a -c '\[s3308-stage-adv\].*edge_id=2 .*taken=1' "$log" 2>/dev/null || true)
    cmp_not=$(grep -a -c '\[s3308-stage-adv\].*edge_id=2 .*taken=0' "$log" 2>/dev/null || true)
    stage_ge7=$(grep -a -c '\[s3308-stage-adv\].*edge_id=3 .*taken=1' "$log" 2>/dev/null || true)
    stage_lt7=$(grep -a -c '\[s3308-stage-adv\].*edge_id=3 .*taken=0' "$log" 2>/dev/null || true)
    print "ptr_zero=$ptr_zero ptr_nz=$ptr_nz cmp_taken=$cmp_taken cmp_not=$cmp_not stage_ge7=$stage_ge7 stage_lt7=$stage_lt7" >> "$DRIVER"

    gate_taken=$(grep -a -c '\[s3306-cine-loop\].*edge_id=2 .*taken=1' "$log" 2>/dev/null || true)
    print "gate_taken=$gate_taken" >> "$DRIVER"

    controls_ok=1
    (( mark_count == 6 )) || controls_ok=0
    grep -a -q '\[s3306-cine-loop-control\] mark edge_id=0' "$log" || controls_ok=0
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

    if ! grep -a -q '\[s3308-stage-adv\].*edge_id=0 site=entry' "$log" ||
       ! grep -a -q '\[s3308-stage-adv\].*edge_id=1 site=ptr-check' "$log"; then
        print 'verdict=H-CoverageInvalid' >> "$DRIVER"
        return 5
    fi

    if (( ptr_zero > 0 )) && (( ptr_nz == 0 )) &&
       ! grep -a -q '\[s3308-stage-adv\].*edge_id=2 site=fp-compare' "$log" &&
       ! grep -a -q '\[s3308-stage-adv\].*edge_id=3 site=stage-lt7' "$log"; then
        print 'verdict=H-PtrZeroSkip' >> "$DRIVER"
        return 1
    fi

    if grep -a -q '\[s3308-stage-adv\].*edge_id=2 site=fp-compare' "$log" &&
       (( cmp_taken == 0 )) &&
       ! grep -a -q '\[s3308-stage-adv\].*edge_id=3 site=stage-lt7' "$log"; then
        print 'verdict=H-DtBelowThreshold' >> "$DRIVER"
        return 2
    fi

    if grep -a -q '\[s3308-stage-adv\].*edge_id=3 site=stage-lt7' "$log" &&
       (( stage_ge7 == 0 )) &&
       ! grep -a -q '\[s3308-stage-adv\].*edge_id=4 site=ret-one' "$log"; then
        print 'verdict=H-StageNeverHits7' >> "$DRIVER"
        return 3
    fi

    if grep -a -q '\[s3308-stage-adv\].*edge_id=4 site=ret-one' "$log"; then
        print 'verdict=H-StageHits7ReturnsOne' >> "$DRIVER"
        return 0
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

if [[ "$term" == crash ]] && ! grep -a -q '\[s3308-stage-adv-control\] mark edge_id=' "$LOG"; then
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
