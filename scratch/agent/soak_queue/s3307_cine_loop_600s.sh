#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/soak_results/s3307_cine_loop_600s_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
LOG="$OUT/run.log"
DRIVER="$OUT/driver.log"
: > "$LOG"
: > "$DRIVER"

(
    cd "$ROOT/build" || exit 2
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
deadline=$((SECONDS + 600))
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
    if grep -a -q -m1 '\[s3306-cine-loop\].*edge_id=2 .*taken=1' "$LOG"; then
        terminal=gate-taken
        break
    fi
done
print "terminal=$terminal elapsed=${SECONDS}s ended=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$DRIVER"
cleanup
trap - EXIT INT HUP

mark_count=$(grep -a '\[s3306-cine-loop-control\] mark edge_id=' "$LOG" | sed -n 's/.*edge_id=\([0-9][0-9]*\).*/\1/p' | sort -nu | wc -l | tr -d ' ')
print "mark_ids=$mark_count" >> "$DRIVER"
print "viewer_return=$(grep -a -c 'edge=return site=runMenuModelViewerScreen' "$LOG" 2>/dev/null || true)" >> "$DRIVER"
print "cine_entry=$(grep -a -c 'site=cinematic-entry' "$LOG" 2>/dev/null || true)" >> "$DRIVER"
print "phase_640=$(grep -a -c 'vi_width=640 (was' "$LOG" 2>/dev/null || true)" >> "$DRIVER"
print "title_1024=$(grep -a -c 'vi_width=1024 (was' "$LOG" 2>/dev/null || true)" >> "$DRIVER"
print "gate_taken=$(grep -a -c '\[s3306-cine-loop\].*edge_id=2 .*taken=1' "$LOG" 2>/dev/null || true)" >> "$DRIVER"
print "exit_target=$(grep -a -c '\[s3306-cine-loop\].*edge_id=4 ' "$LOG" 2>/dev/null || true)" >> "$DRIVER"
last_gate=$(grep -a '\[s3306-cine-loop\].*edge_id=2 ' "$LOG" 2>/dev/null | tail -1 || true)
print -r -- "last_gate=${last_gate}" >> "$DRIVER"
print "crash=$(grep -a -c '\[CRASH\]' "$LOG" 2>/dev/null || true)" >> "$DRIVER"

if grep -a -q '\[CRASH\]\|\[ABORT\]' "$LOG"; then
    print 'verdict=crash' >> "$DRIVER"
    exit 3
fi
if (( mark_count != 7 )) || ! grep -a -q '\[phase\] vi_width=640 .*origin=0x0066A500' "$LOG" ||
   ! grep -a -q 'site=cinematic-entry' "$LOG"; then
    print 'verdict=H-CoverageInvalid' >> "$DRIVER"
    exit 5
fi
if grep -a -q '\[s3306-cine-loop\].*edge_id=2 .*taken=1' "$LOG" ||
   grep -a -q '\[phase\] vi_width=1024 ' "$LOG"; then
    print 'verdict=H-PortEventuallyExits' >> "$DRIVER"
    exit 0
fi
print 'verdict=H-PortLoopNoExit' >> "$DRIVER"
exit 1
