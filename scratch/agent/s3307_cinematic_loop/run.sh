#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s3307_cinematic_loop
BUILD=$ROOT/build
LOG=$OUT/run.log
DRIVER=$OUT/driver.log
mkdir -p "$OUT"
: > "$LOG"
: > "$DRIVER"

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
        ./RogueSquadron64Recomp
) > "$LOG" 2>&1 &
GAME_PID=$!
print "pid=$GAME_PID started=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$DRIVER"

cleanup() {
    kill -9 "$GAME_PID" 2>/dev/null || true
    wait "$GAME_PID" 2>/dev/null || true
}
trap cleanup EXIT INT HUP

terminal=watchdog
deadline=$((SECONDS + 120))
while (( SECONDS < deadline )); do
    if ! kill -0 "$GAME_PID" 2>/dev/null; then
        terminal=process-exit
        break
    fi
    sleep 2
    if grep -a -q -m1 '\[CRASH\]\|\[ABORT\]\|Bus error\|Segmentation fault' "$LOG"; then
        terminal=crash
        break
    fi
    if grep -a -q -m1 '\[phase\] vi_width=1024 ' "$LOG"; then
        terminal=title-1024
        break
    fi
done
print "terminal=$terminal elapsed=${SECONDS}s ended=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$DRIVER"

cleanup
trap - EXIT INT HUP

count_fixed() {
    grep -a -F -c -- "$2" "$1" 2>/dev/null || true
}

mark_count=$(grep -a '\[s3306-cine-loop-control\] mark edge_id=' "$LOG" | sed -n 's/.*edge_id=\([0-9][0-9]*\).*/\1/p' | sort -nu | wc -l | tr -d ' ')
print "mark_ids=$mark_count" >> "$DRIVER"
print "s3305_mark_ids=$(grep -a '\[s3305-postviewer-control\] mark edge_id=' "$LOG" | sed -n 's/.*edge_id=\([0-9][0-9]*\).*/\1/p' | sort -nu | wc -l | tr -d ' ')" >> "$DRIVER"
print "arm_rows=$(count_fixed "$LOG" 'arm=completion-wins-default')" >> "$DRIVER"
print "reset_rows=$(count_fixed "$LOG" 'requested_pre=1 requested_post=0')" >> "$DRIVER"
print "sp_complete=$(count_fixed "$LOG" '[event-wiring] complete kind=SP')" >> "$DRIVER"
print "phase_640=$(count_fixed "$LOG" 'vi_width=640 (was')" >> "$DRIVER"
print "viewer_entry=$(count_fixed "$LOG" 'edge=entry site=runMenuModelViewerScreen')" >> "$DRIVER"
print "viewer_return=$(count_fixed "$LOG" 'edge=return site=runMenuModelViewerScreen')" >> "$DRIVER"
print "cine_entry=$(count_fixed "$LOG" 'site=cinematic-entry')" >> "$DRIVER"
print "s3305_cine_return=$(grep -a -c '\[s3305-postviewer\].*edge_id=20 site=cinematic-return' "$LOG" 2>/dev/null || true)" >> "$DRIVER"
print "title_1024=$(count_fixed "$LOG" 'vi_width=1024 (was')" >> "$DRIVER"
print "crash=$(count_fixed "$LOG" '[CRASH]') abort=$(count_fixed "$LOG" '[ABORT]')" >> "$DRIVER"

for id in {0..6}; do
    rows=$(grep -a -c "\[s3306-cine-loop\].*edge_id=$id " "$LOG" 2>/dev/null || true)
    first=$(grep -a -m1 "\[s3306-cine-loop\].*edge_id=$id " "$LOG" 2>/dev/null || true)
    last=$(grep -a "\[s3306-cine-loop\].*edge_id=$id " "$LOG" 2>/dev/null | tail -1 || true)
    print -r -- "edge_$id=$rows" >> "$DRIVER"
    print -r -- "edge_${id}_first=${first}" >> "$DRIVER"
    print -r -- "edge_${id}_last=${last}" >> "$DRIVER"
done

gate_taken=$(grep -a -c '\[s3306-cine-loop\].*edge_id=2 .*taken=1' "$LOG" 2>/dev/null || true)
gate_v0_zero=$(grep -a -c '\[s3306-cine-loop\].*edge_id=2 .*v0=0x00000000 ' "$LOG" 2>/dev/null || true)
print "gate_taken=$gate_taken gate_v0_zero_printed=$gate_v0_zero" >> "$DRIVER"

controls_ok=1
(( mark_count == 7 )) || controls_ok=0
grep -a -q '\[event-wiring\] complete kind=SP' "$LOG" || controls_ok=0
grep -a -q '\[phase\] vi_width=640 .*origin=0x0066A500' "$LOG" || controls_ok=0
grep -a -q '\[m5-postwait\].*edge=return site=runMenuModelViewerScreen' "$LOG" || controls_ok=0
grep -a -q '\[s3305-postviewer\].*edge_id=19 site=cinematic-entry' "$LOG" || controls_ok=0

if (( controls_ok == 0 )); then
    print 'verdict=H-CoverageInvalid' >> "$DRIVER"
    exit 5
fi

if ! grep -a -q '\[s3306-cine-loop\].*edge_id=1 site=loop-head' "$LOG"; then
    print 'verdict=H-PortPrologueStall' >> "$DRIVER"
    exit 4
fi

if grep -a -q '\[s3306-cine-loop\].*edge_id=4 site=exit-target' "$LOG"; then
    if grep -a -q '\[s3306-cine-loop\].*edge_id=6 site=cinematic-return' "$LOG" &&
       grep -a -q '\[s3305-postviewer\].*edge_id=21 site=cinematic-call-return' "$LOG"; then
        print 'verdict=H-PortExitsLikeRetail' >> "$DRIVER"
        exit 0
    fi
    print 'verdict=H-PortExitNoReturn' >> "$DRIVER"
    exit 2
fi

print 'verdict=H-PortLoopNoExit' >> "$DRIVER"
exit 1
