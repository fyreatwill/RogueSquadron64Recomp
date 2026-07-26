#!/bin/zsh
# Run the game once through the whole boot sequence, capture continuously, and
# score every phase in one pass.
#
# Why this exists alongside probe.sh: probe.sh gates on ONE VI width and stops
# when the game leaves it, so answering "did this change break an earlier
# screen?" costs one run per phase and a manual contact-sheet read. Sessions
# 6-23 all paid that tax. This runs the standard config once, captures the
# whole timeline, tags every frame with the phase that was live when it was
# taken, and hands the burst to regress_score.py for a machine-readable verdict
# that can be diffed against a stored baseline.
#
# Usage:  regress.sh <outdir> [seconds]
#
# Env:
#   REGRESS_SECS=120        capture budget in seconds (arg 2 wins)
#   REGRESS_INTERVAL=0.6    seconds between captures
#   REGRESS_KEYS=""         phase-relative key schedule, space separated:
#                             "<width>@<sec>[:<key>] ..."
#                           <sec> counts from the moment that VI width is first
#                           entered, NOT from boot. Width 0 means boot-relative.
#                           Key names as in probe.sh (start a b z up down left
#                           right su/sd/sl/sr cup/cdown/cleft/cright l r);
#                           omitted key means start.
#                           Example (session 23's title->hangar route):
#                             "1024@2:a 1024@3:start 1024@4:a 1024@6:start"
#   REGRESS_BASELINE=path   verdict.json to diff this run against
#   REGRESS_LABEL=name      free-text label recorded in verdict.json
#   plus any ROGUESQ_* toggles, which are inherited by the game and recorded.
#
# Why phase-relative keys: run-to-run timing varies by tens of seconds (the
# Factor 5 logo has been seen at 18s and at 44s), so an absolute key schedule
# fires during the wrong screen. Session 22 lost a run to exactly that.
#
# Writes into <outdir>: run.log, env.txt, outcome.txt, frames f_*.png,
# and verdict.json (via regress_score.py).
set -u

OUTDIR=${1:?usage: regress.sh <outdir> [seconds]}
SECS=${2:-${REGRESS_SECS:-120}}
IVAL=${REGRESS_INTERVAL:-0.6}
KEYS=${REGRESS_KEYS:-}
BASELINE=${REGRESS_BASELINE:-}
LABEL=${REGRESS_LABEL:-}

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
BUILD=$ROOT/build
WINCTL=$BUILD/winctl
GAME=$BUILD/RogueSquadron64Recomp

# Preflight. A harness that starts anyway and reports 0 frames as a clean run is
# worse than no harness -- fail loudly on every precondition.
for f in "$GAME" "$WINCTL" "$BUILD/rogue_squadron.z64"; do
    [[ -e $f ]] || { print -u2 "regress: missing required file: $f"; exit 2; }
done

mkdir -p "$OUTDIR" || exit 2
OUTDIR=$(cd "$OUTDIR" && pwd)

# Absolutise the baseline too: the runner cds into build/ before scoring, so a
# relative path handed in by the caller resolves against the wrong directory.
if [[ -n "$BASELINE" ]]; then
    [[ -e "$BASELINE" ]] || { print -u2 "regress: baseline not found: $BASELINE"; exit 2; }
    BASELINE=$(cd "$(dirname "$BASELINE")" && print -r -- "$PWD/$(basename "$BASELINE")")
fi

# Record the configuration with the run. Session 18 established that comparing
# two runs is only meaningful if you can prove what each was run with.
{
    print "label: ${LABEL:-<none>}"
    print "secs: $SECS  interval: $IVAL"
    print "keys: ${KEYS:-<none>}"
    print "binary mtime: $(stat -f '%Sm' "$GAME")"
    print -r -- "--- ROGUESQ_* environment ---"
    env | /usr/bin/grep -E '^ROGUESQ_' | sort || print "(none set: all defaults)"
} > "$OUTDIR/env.txt"

# ------------------------------------------------------------------ preflight
# Both capabilities this harness needs are TCC permissions that lapse without
# warning: session 24 saw window capture work for two runs and then fail for
# every run after, with no change on this side, and session 25 lost a 110s
# driven run when capture went away mid-session while Accessibility stayed.
#
# They fail in OPPOSITE ways, which is why both must be probed rather than
# assumed: screencapture fails loudly, but CGEventPostToPid returns success and
# does nothing, so an undriven run looks identical to a driven one right up to
# the verdict. Probing costs about a second; discovering it afterwards costs the
# whole run.
PRE_INPUT=$("$WINCTL" trusted 2>/dev/null)
case "$PRE_INPUT" in
    yes) PRE_INPUT=ok ;;
    no)  PRE_INPUT=denied ;;
    # An older winctl has no `trusted` subcommand. Report unknown and do not
    # block -- failing closed here would break every caller with a stale binary.
    *)   PRE_INPUT=unknown ;;
esac

# Screen Recording must be probed with a WINDOWED capture. Plain `screencapture`
# with no -l succeeds without the permission, so a full-screen grab is not
# evidence the permission is present (session 24).
PRE_VISUAL=denied
for probe_app in Dock Finder; do
    probe_pid=$(/usr/bin/pgrep -x "$probe_app" 2>/dev/null | head -1)
    [[ -n "$probe_pid" ]] || continue
    probe_wid=$("$WINCTL" find "$probe_pid" 2>/dev/null | cut -d' ' -f1)
    [[ -n "$probe_wid" ]] || continue
    # Not a leading-dot name: screencapture on macOS refuses paths whose final
    # component starts with '.', reporting "cannot write file to intended
    # destination" with exit 0 and no file. Session 26: that made every preflight
    # report visual=denied even with Screen Recording granted, blocking every
    # driven hangar run.
    if /usr/sbin/screencapture -x -o -l "$probe_wid" "$OUTDIR/captest.png" 2>/dev/null \
       && [[ -s "$OUTDIR/captest.png" ]]; then
        PRE_VISUAL=ok
    fi
    rm -f "$OUTDIR/captest.png"
    break
done

print "preflight: input=$PRE_INPUT visual=$PRE_VISUAL"
{ print "preflight input: $PRE_INPUT"; print "preflight visual: $PRE_VISUAL" } >> "$OUTDIR/env.txt"

# AXIsProcessTrusted is necessary but NOT sufficient, measured in session 25:
# two driven runs failed to reach the hangar (both took the undriven 0x690400
# route) while `winctl trusted` still answered yes, and window capture had
# failed at the same moment. The common cause is not the TCC grant -- that is
# static and still held -- but the absence of a usable GUI session: with no
# active session, `winctl activate` cannot bring the game forward, SDL never
# sees a focused window, and posted keys are dropped even though
# CGEventPostToPid reports success.
#
# So the windowed-capture probe is the better predictor of BOTH capabilities,
# and a driven run is refused whenever it fails. Two independent observations,
# no counterexample; revisit if a driven run is ever seen to work with capture
# denied.
if [[ -n "$KEYS" && -z "${REGRESS_ALLOW_UNDRIVEN:-}" ]]; then
    if [[ "$PRE_INPUT" == denied ]]; then
        print -u2 "regress: a key schedule was requested but this process lacks Accessibility"
        print -u2 "         permission. Grant it in System Settings -> Privacy & Security ->"
        print -u2 "         Accessibility, or set REGRESS_ALLOW_UNDRIVEN=1 to run anyway."
        exit 4
    fi
    if [[ "$PRE_VISUAL" != ok ]]; then
        print -u2 "regress: a key schedule was requested and Accessibility is granted, but"
        print -u2 "         windowed capture fails -- which in session 25 meant there was no"
        print -u2 "         usable GUI session and the keys were silently dropped, twice."
        print -u2 "         The run would take the UNDRIVEN route (512 at origin 0x690400,"
        print -u2 "         the outdoor scene) and be scored as if it were driven."
        print -u2 "         Run from an active desktop session, or set"
        print -u2 "         REGRESS_ALLOW_UNDRIVEN=1 to run anyway."
        exit 4
    fi
fi
if [[ "$PRE_VISUAL" != ok ]]; then
    if [[ -n "${REGRESS_REQUIRE_VISUAL:-}" ]]; then
        print -u2 "regress: REGRESS_REQUIRE_VISUAL is set but window capture is unavailable"
        print -u2 "         (Screen Recording permission). Refusing to run a log-only pass."
        exit 5
    fi
    print "  NOTE: no Screen Recording permission -- this will be a LOG-ONLY run."
fi

cd "$BUILD" || exit 2
# A leftover crash dialog sits on top of the window and gets captured instead.
/usr/bin/pkill -x UserNotificationCenter >/dev/null 2>&1

./RogueSquadron64Recomp > "$OUTDIR/run.log" 2>&1 &
PID=$!
print "pid $PID"

WID=""
for a in $(seq 1 60); do
    if ! kill -0 "$PID" 2>/dev/null; then print -u2 "regress: died during startup"; break; fi
    R=$("$WINCTL" find "$PID" 2>/dev/null) && { WID=${R%% *}; break; }
    sleep 0.25
done
if [[ -z "$WID" ]]; then
    print -u2 "regress: no window for pid $PID"
    print "status=nowindow elapsed=0 frames=0" > "$OUTDIR/outcome.txt"
    kill -9 "$PID" 2>/dev/null
    exit 3
fi
print "window $WID"

# Same fix as probe.sh (session 45): winctl activate's activateWithOptions: is
# ignored under cooperative activation while another app holds focus; System
# Events' `set frontmost` (Accessibility API) actually raises the window.
raise_game() {
    "$WINCTL" activate "$PID" >/dev/null 2>&1
    /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $PID to true" >/dev/null 2>&1
}
raise_game

# Keycodes: same map as probe.sh, matching the keyboard fallback in
# src/main/main.cpp.
keycode_for() {
    case "$1" in
        start|return) print 36 ;;
        a)     print 6  ;;   # Z
        b)     print 7  ;;   # X
        z)     print 8  ;;   # C
        up)    print 126 ;;  down)  print 125 ;;
        left)  print 123 ;;  right) print 124 ;;
        su)    print 13 ;;   sd)    print 1  ;;
        sl)    print 0  ;;   sr)    print 2  ;;
        cup)   print 34 ;;   cdown) print 40 ;;
        cleft) print 38 ;;   cright) print 37 ;;
        l)     print 12 ;;   r)     print 14 ;;
        *)     print "$1" ;; # already a raw keycode
    esac
}

# Group the key schedule by the width it is relative to.
typeset -A PHASE_KEYS
for entry in ${=KEYS}; do
    w=${entry%%@*}
    rest=${entry#*@}
    [[ "$w" == "$entry" ]] && { w=0; rest=$entry; }   # tolerate a bare "2:a"
    PHASE_KEYS[$w]="${PHASE_KEYS[$w]:-} $rest"
done

# Fire one width's schedule on its own clock so captures are never blocked.
fire_keys() {
    local w=$1 sched=${PHASE_KEYS[$1]:-}
    [[ -z "${sched// /}" ]] && return 0
    (
        prev=0
        for e in ${=sched}; do
            t=${e%%:*}; name=${e#*:}
            [[ "$name" == "$e" ]] && name=start
            sleep "$(print "$t - $prev" | bc -l)"
            prev=$t
            kill -0 "$PID" 2>/dev/null || exit 0
            raise_game
            "$WINCTL" key "$PID" "$(keycode_for $name)" >/dev/null 2>&1
            print "  [keys] w=$w $name at +${t}s"
        done
    ) &
    KEYPIDS+=($!)
}

# Phase state comes from the game's own log line, emitted the instant the VI
# width changes (src/main/rt64_render_context.cpp:802). Ordinal = how many
# transitions have been logged, so a width that recurs later is still a new
# phase in the timeline.
phase_line_count() {
    # grep -c prints the count but exits 1 when it is zero, so capture the
    # output and ignore the status -- a `|| print 0` fallback here emits a
    # SECOND number and corrupts the frame name.
    local n
    n=$(/usr/bin/grep -ac '\[phase\] vi_width=' "$OUTDIR/run.log" 2>/dev/null)
    print ${n:-0}
}
cur_width() {
    /usr/bin/grep -a '\[phase\] vi_width=' "$OUTDIR/run.log" 2>/dev/null \
        | tail -1 | sed -n 's/.*vi_width=\([0-9]*\).*/\1/p'
}

typeset -a KEYPIDS
typeset -A FIRED
KEYPIDS=()

fire_keys 0 && FIRED[0]=1

T0=$(date +%s.%N)
N=0                 # frames that actually exist on disk
ATTEMPT=0           # capture attempts, used only for frame numbering
CAPTURE=1
CAPTURE_NOTE=ok
STATUS=completed
while :; do
    EL=$(print "$(date +%s.%N) - $T0" | bc -l)
    (( $(print "$EL > $SECS" | bc -l) )) && break
    if ! kill -0 "$PID" 2>/dev/null; then
        STATUS=died
        print "process gone at $(printf '%.1f' $EL)s after $N frames"
        break
    fi

    ORD=$(phase_line_count)
    W=$(cur_width); W=${W:-0}
    if [[ -n "${PHASE_KEYS[$W]:-}" && -z "${FIRED[$W]:-}" ]]; then
        print "  [phase] width $W entered at $(printf '%.1f' $EL)s -- firing keys"
        fire_keys "$W"
        FIRED[$W]=1
    fi

    if (( CAPTURE )); then
        ATTEMPT=$((ATTEMPT+1))
        # Frame name carries the phase it belongs to, so scoring never has to
        # re-derive which screen a PNG came from.
        FRAME="$OUTDIR/$(printf 'f_%03d_%06.1f_p%02d_w%04d' $ATTEMPT $EL $ORD $W).png"
        /usr/sbin/screencapture -x -o -l"$WID" "$FRAME" 2>/dev/null
        # Count frames that EXIST, never attempts. screencapture -l fails
        # silently (exit 1, no file) when the calling process lacks Screen
        # Recording permission, and a harness that reports the attempt count as
        # "169 frames captured" over an empty directory is the same lie
        # window_burst.sh told when it kept shooting after the game died.
        if [[ -e "$FRAME" ]]; then
            N=$((N+1))
        elif (( N == 0 )); then
            CAPTURE=0
            CAPTURE_NOTE=unavailable    # single token: outcome.txt is k=v pairs
            print -u2 "regress: WINDOW CAPTURE UNAVAILABLE -- continuing log-only."
            print -u2 "  screencapture -l$WID wrote nothing. This shell most likely"
            print -u2 "  lacks Screen Recording permission (System Settings > Privacy"
            print -u2 "  & Security > Screen Recording, for the app running this)."
            print -u2 "  Log-derived checks still work; visual scoring needs a terminal"
            print -u2 "  that has the permission."
        fi
    fi
    sleep "$IVAL"
done

EL=$(print "$(date +%s.%N) - $T0" | bc -l)
for k in $KEYPIDS; do kill -9 "$k" 2>/dev/null; done
# SIGKILL, not TERM: the TERM path aborts inside SDL_QUIT cleanup and leaves a
# crash dialog covering the next run's captures.
kill -9 "$PID" 2>/dev/null
wait "$PID" 2>/dev/null

print -r -- "status=$STATUS elapsed=$(printf '%.1f' $EL) frames=$N capture=$CAPTURE_NOTE" \
    > "$OUTDIR/outcome.txt"
print "captured $N frames into $OUTDIR ($STATUS at $(printf '%.1f' $EL)s, capture=$CAPTURE_NOTE)"

# No frames is not fatal: the log half of the verdict (phase timeline, crash
# point, missing-func, defer-drop, aborts) is fully usable headless, and is the
# half that gates an unattended edit-run-compare loop.
SCORE_ARGS=("$OUTDIR")
[[ -n "$BASELINE" ]] && SCORE_ARGS+=(--baseline "$BASELINE")
[[ -n "$LABEL" ]] && SCORE_ARGS+=(--label "$LABEL")
exec "$ROOT/tools/regress_score.py" "${SCORE_ARGS[@]}"
