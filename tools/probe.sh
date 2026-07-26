#!/bin/zsh
# Run the game and sample its window densely, with the caller's ROGUESQ_*
# environment passed straight through.
#
# Why this exists alongside window_burst.sh: that script hardcodes
# ROGUESQ_LLE_FORCE=1 and drops every other toggle, so it cannot test the
# configuration we actually run; and it depends on System Events, which did not
# return at all in session 10. This uses build/winctl (CGWindowList) instead, so
# capture targets the game window by id and cannot pick up whatever is on top.
#
# Usage:  probe.sh <outdir> <seconds> [interval]
# Env:    PROBE_KEYS="8 10 12"   seconds at which to press Return (Start)
#                                or "48:a 50:start" with named keys
#         PROBE_START=2          delay before the first capture (no phase gate)
#         PROBE_PHASE_WIDTH=512  wait until the game reports this VI width;
#                                the <seconds> budget starts then
#         PROBE_PHASE_TIMEOUT=180 give up waiting for that phase
#         PROBE_KEYS_FROM_PHASE=1  when set with PROBE_PHASE_WIDTH, PROBE_KEYS
#                                times are relative to phase entry (not boot).
#                                Default: keys always run from process start.
#         PROBE_LEAVE_OK=1       keep capturing after the gated VI width
#                                changes (default stops so every frame is one
#                                phase). Use with PROBE_KEYS_FROM_PHASE to
#                                press Start on the title then follow into
#                                hangar / mission.
#         plus any ROGUESQ_* toggles, which are inherited by the game.
#
# Why the phase gate: run-to-run timing varies by tens of seconds (session 17
# saw the Factor 5 logo at 18s in one run and 44s in another), so fixed windows
# kept capturing the wrong phase and a comparison across two runs could not be
# trusted to be comparing the same thing. The game logs [phase] vi_width=N the
# instant the VI width changes; gate on that instead of on a stopwatch.
#
# Writes <outdir>/run.log and <outdir>/f_<NNN>_<elapsed>.png, and prints a
# summary. Frames stop the moment the process dies, and that is reported —
# capturing past a crash is what made a previous session read a dead window as
# "60/60 frames have content".
set -u
OUTDIR=${1:?outdir}; SECS=${2:-60}; IVAL=${3:-0.5}
START_DELAY=${PROBE_START:-2}
KEYS=${PROBE_KEYS:-}
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
BUILD=$ROOT/build
WINCTL=$BUILD/winctl

mkdir -p "$OUTDIR"
# Absolute, because the game must be started from build/ (it looks for the ROM
# next to the executable) and a relative outdir would land there instead.
OUTDIR=$(cd "$OUTDIR" && pwd)
cd "$BUILD" || exit 2
/usr/bin/pkill -x UserNotificationCenter >/dev/null 2>&1

./RogueSquadron64Recomp > "$OUTDIR/run.log" 2>&1 &
PID=$!
print "pid $PID"

# Wait for the window to exist (Metal/SDL startup is not instant).
WID=""
for a in $(seq 1 60); do
    if ! kill -0 "$PID" 2>/dev/null; then print "died during startup"; break; fi
    R=$("$WINCTL" find "$PID" 2>/dev/null) && { WID=${R%% *}; break; }
    sleep 0.25
done
if [[ -z "$WID" ]]; then
    print "no window (pid alive: $(kill -0 $PID 2>/dev/null && print yes || print no))"
    kill -9 "$PID" 2>/dev/null
    exit 1
fi
print "window $WID"
"$WINCTL" activate "$PID" >/dev/null 2>&1

# Key presses run on their own clock so captures are never blocked by them.
#
# Each entry is "<seconds>" (Start) or "<seconds>:<name-or-keycode>", so the
# menu can actually be navigated rather than only started. Names map to the
# keyboard fallback in src/main/main.cpp:
#   start=Return  a=Z  b=X  z=C  up/down/left/right=arrows (D-pad)
#   cup/cdown/cleft/cright=I/K/J/L   l=Q  r=E   su/sd/sl/sr=W/S/A/D (stick)
keycode_for() {
    case "$1" in
        start|return) print 36 ;;
        a)     print 6  ;;   # Z
        b)     print 7  ;;   # X
        z)     print 8  ;;   # C
        up)    print 126 ;;
        down)  print 125 ;;
        left)  print 123 ;;
        right) print 124 ;;
        su)    print 13 ;;   # W
        sd)    print 1  ;;   # S
        sl)    print 0  ;;   # A
        sr)    print 2  ;;   # D
        cup)   print 34 ;;   # I
        cdown) print 40 ;;   # K
        cleft) print 38 ;;   # J
        cright) print 37 ;;  # L
        l)     print 12 ;;   # Q
        r)     print 14 ;;   # E
        *)     print "$1" ;; # already a raw keycode
    esac
}

# Current VI width as last reported by the game, or empty if it has not
# logged a [phase] line yet.
cur_width() {
    /usr/bin/grep -a '\[phase\] vi_width=' "$OUTDIR/run.log" 2>/dev/null \
        | tail -1 | sed -n 's/.*vi_width=\([0-9]*\).*/\1/p'
}

start_keys() {
    local label=$1
    [[ -z "$KEYS" ]] && return 0
    (
        prev=0
        for entry in ${=KEYS}; do
            t=${entry%%:*}
            name=${entry#*:}
            [[ "$name" == "$entry" ]] && name=start
            d=$(print "$t - $prev" | bc -l)
            sleep "$d"
            prev=$t
            kill -0 "$PID" 2>/dev/null || exit 0
            "$WINCTL" activate "$PID" >/dev/null 2>&1
            "$WINCTL" key "$PID" "$(keycode_for $name)" >/dev/null 2>&1
            print "  [keys] $name at ${t}s ($label)"
        done
    ) &
    KEYPID=$!
}

PHASE=${PROBE_PHASE_WIDTH:-}
KEYS_FROM_PHASE=${PROBE_KEYS_FROM_PHASE:-0}
LEAVE_OK=${PROBE_LEAVE_OK:-0}

# Keys from process start unless phase-relative mode is requested.
if [[ -n "$KEYS" && "$KEYS_FROM_PHASE" != "1" ]]; then
    start_keys "from-boot"
fi

if [[ -n "$PHASE" ]]; then
    PHASE_TIMEOUT=${PROBE_PHASE_TIMEOUT:-180}
    print "waiting for VI width $PHASE (timeout ${PHASE_TIMEOUT}s)"
    W0=$(date +%s.%N)
    while :; do
        if ! kill -0 "$PID" 2>/dev/null; then
            print "process gone while waiting for width $PHASE (last width: $(cur_width))"
            [[ -n "${KEYPID:-}" ]] && kill -9 "$KEYPID" 2>/dev/null
            exit 4
        fi
        [[ "$(cur_width)" == "$PHASE" ]] && break
        WEL=$(print "$(date +%s.%N) - $W0" | bc -l)
        if (( $(print "$WEL > $PHASE_TIMEOUT" | bc -l) )); then
            print "width $PHASE never reached in ${PHASE_TIMEOUT}s (last width: $(cur_width))"
            [[ -n "${KEYPID:-}" ]] && kill -9 "$KEYPID" 2>/dev/null
            kill -9 "$PID" 2>/dev/null
            exit 5
        fi
        sleep 0.2
    done
    print "phase width=$PHASE reached after $(printf '%.1f' $(print "$(date +%s.%N) - $W0" | bc -l))s"
    if [[ -n "$KEYS" && "$KEYS_FROM_PHASE" == "1" ]]; then
        start_keys "from-phase"
    fi
else
    sleep "$START_DELAY"
fi

T0=$(date +%s.%N)
N=0
while :; do
    NOW=$(date +%s.%N)
    EL=$(print "$NOW - $T0" | bc -l)
    (( $(print "$EL > $SECS" | bc -l) )) && break
    if ! kill -0 "$PID" 2>/dev/null; then
        print "process gone at $(printf '%.1f' $EL)s after $N frames"
        break
    fi
    # Stop as soon as the game leaves the phase we are capturing, so no frame
    # in the output belongs to a different phase — unless PROBE_LEAVE_OK=1.
    if [[ -n "$PHASE" && "$LEAVE_OK" != "1" && "$(cur_width)" != "$PHASE" ]]; then
        print "left phase $PHASE at $(printf '%.1f' $EL)s (now $(cur_width)) after $N frames"
        break
    fi
    N=$((N+1))
    /usr/sbin/screencapture -x -o -l"$WID" \
        "$OUTDIR/$(printf 'f_%03d_%05.1f' $N $EL).png" 2>/dev/null
    sleep "$IVAL"
done

[[ -n "${KEYPID:-}" ]] && kill -9 "$KEYPID" 2>/dev/null
# SIGKILL, not TERM: the TERM path aborts inside SDL_QUIT cleanup and leaves a
# crash dialog sitting on top of the next run's captures.
kill -9 "$PID" 2>/dev/null
wait "$PID" 2>/dev/null
print "captured $N frames into $OUTDIR"
