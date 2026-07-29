#!/bin/zsh
# s73/s74: after SELECT YOUR CRAFT is stable, probe Start/A for mission launch.
# Schedule to AVAILABLE CRAFT matches s61–s72; then wait STABLE_S post-a and fire KEYS.
set -u

export ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1
export ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_RUNNER_ALL=1
export ROGUESQ_LOG_THREAD_RESUME=${ROGUESQ_LOG_THREAD_RESUME:-1}
export ROGUESQ_LOG_OST_WB=1

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
BUILD=$ROOT/build
WINCTL=$BUILD/winctl
RUNTAG=${1:-keys1}
GRACE=${2:-30}
STABLE_S=${3:-12}
OUTDIR=$ROOT/scratch/s73_post_a_scene/$RUNTAG
mkdir -p "$OUTDIR"
cd "$BUILD" || exit 2
/usr/bin/pkill -x UserNotificationCenter >/dev/null 2>&1

if [[ ! -f rogue_squadron.z64 ]]; then
  print "ERROR: no ROM in build/"
  exit 3
fi

./RogueSquadron64Recomp > "$OUTDIR/run.log" 2>&1 &
PID=$!
# s234: real UNIX-epoch process-start stamp, so the game's own t=%.1f
# diagnostic fields (process-relative, rs64_elapsed_seconds()) can be
# converted to real wall-clock and cross-referenced against hold_NN.png
# file mtimes (also real wall-clock) without needing to parse this
# driver's own (unredirected) stdout for a matching anchor.
date +%s > "$OUTDIR/proc_start_epoch.txt"
print "pid $PID out=$OUTDIR stable=${STABLE_S}s grace=${GRACE}s"

WID=""
for a in $(seq 1 60); do
    kill -0 "$PID" 2>/dev/null || { print "died during startup"; break; }
    R=$("$WINCTL" find "$PID" 2>/dev/null) && { WID=${R%% *}; break; }
    sleep 0.25
done
[[ -n "$WID" ]] && print "window $WID" || print "no window found (continuing anyway)"

raise_game() {
    "$WINCTL" activate "$PID" >/dev/null 2>&1
    /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $PID to true" >/dev/null 2>&1
}

cur_width() {
    /usr/bin/grep -a '\[phase\] vi_width=' "$OUTDIR/run.log" 2>/dev/null \
        | tail -1 | sed -n 's/.*vi_width=\([0-9]*\).*/\1/p'
}

snap() {
    [[ -n "$WID" ]] || return
    /usr/sbin/screencapture -x -o -l"$WID" "$OUTDIR/$1.png" 2>/dev/null
}

print "waiting for VI width 1024 (timeout 600s)"
W0=$(date +%s.%N)
while :; do
    kill -0 "$PID" 2>/dev/null || { print "process gone while waiting for phase"; exit 4; }
    [[ "$(cur_width)" == "1024" ]] && break
    WEL=$(print "$(date +%s.%N) - $W0" | bc -l)
    (( $(print "$WEL > 600" | bc -l) )) && { print "phase timeout (INCONCLUSIVE)"; kill -9 "$PID" 2>/dev/null; exit 5; }
    sleep 0.2
done
print "phase width=1024 reached after $(printf '%.1f' $(print "$(date +%s.%N) - $W0" | bc -l))s"

raise_game
typeset -A KEYCODE=(start 36 a 6)
SCHEDULE=(3:start 25:start 40:start 60:a)
prev=0
for entry in $SCHEDULE; do
    t=${entry%%:*}
    name=${entry#*:}
    d=$(print "$t - $prev" | bc -l)
    sleep "$d"
    prev=$t
    kill -0 "$PID" 2>/dev/null || { print "process gone before key $name"; break; }
    raise_game
    snap "pre_$(printf '%03d' $t)_$name"
    "$WINCTL" key "$PID" "$KEYCODE[$name]" >/dev/null 2>&1
    print "[keys] $name at ${t}s (from-phase)"
    sleep 0.6
    snap "post_$(printf '%03d' $t)_$name"
done

print "wait ${STABLE_S}s for SELECT YOUR CRAFT stable"
A_PRESS_T=$(date +%s)
for i in $(seq 1 "$STABLE_S"); do
    kill -0 "$PID" 2>/dev/null || { print "game process gone at stable-iter $i"; break; }
    snap "stable_$(printf '%02d' $i)"
    sleep 1
done
snap "craft_stable"

# Probe sequence with unique tags (s74: after_$name overwrote first Start snaps).
# Default MODE=mixed is start/a/start; MODE=start_only is a single Start + long wait.
# HOLD_S>0 (s76): after leave-confirm wait, hold_NN snaps + stick pulses for HOLD_S seconds.
PROBE_MODE=${PROBE_MODE:-mixed}
HOLD_S=${HOLD_S:-0}
if [[ "$PROBE_MODE" == "start_only" ]]; then
    # Short leave-confirm when holding; full 15s when isolating leave only.
    if (( HOLD_S > 0 )); then
        PROBES=(p1:start:5)
    else
        PROBES=(p1:start:15)
    fi
else
    PROBES=(p1:start:5 p2:a:3 p3:start:10)
fi
# Stick keycodes: W/S/A/D = su/sd/sl/sr (src/main keyboard fallback)
typeset -A KEYCODE_EXT=(start 36 a 6 su 13 sd 1 sl 0 sr 2 left 123 right 124)
for k v in ${(kv)KEYCODE_EXT}; do KEYCODE[$k]=$v; done

for entry in $PROBES; do
    tag=${entry%%:*}; rest=${entry#*:}
    name=${rest%%:*}; wait_s=${rest#*:}
    kill -0 "$PID" 2>/dev/null || { print "process gone before probe $tag $name"; break; }
    raise_game
    snap "pre_${tag}_${name}"
    "$WINCTL" key "$PID" "$KEYCODE[$name]" >/dev/null 2>&1
    print "[keys] probe $tag $name"
    sleep 0.6
    snap "post_${tag}_${name}"
    TICK=${CAPTURE_TICK_S:-1}
    NTICKS=$(print "$wait_s / $TICK" | bc)
    for j in $(seq 1 "$NTICKS"); do
        kill -0 "$PID" 2>/dev/null || break
        snap "after_${tag}_${name}_$(printf '%03d' $j)"
        sleep "$TICK"
    done
done

if (( HOLD_S > 0 )); then
    # Marks are seconds after hold_01 (≈ +5s after Start if leave-confirm was 5s).
    # Default stick: right, left, up at +10/+25/+40 so pose change can be read offline.
    STICK_SCHEDULE=${STICK_SCHEDULE:-"10:sr 25:sl 40:su"}
    typeset -A STICK_AT
    for entry in ${=STICK_SCHEDULE}; do
        STICK_AT[${entry%%:*}]=${entry#*:}
    done
    # s152: HOLD_TICK_S densifies capture WITHIN each hold second (default 1
    # = unchanged behaviour, exactly one hold_NN.png per second like before).
    # A value <1 (e.g. 0.2) adds hold_NN_subMM.png snaps between the
    # on-the-second snap and the next one, at roughly 1/HOLD_TICK_S Hz --
    # CAPTURE_TICK_S (existing) only densifies the earlier probe-wait loop,
    # not this one (flagged unresolved since s150/s151's NEXT.md).
    HOLD_TICK_S=${HOLD_TICK_S:-1}
    print "hold window ${HOLD_S}s @ 1 Hz (sub-tick ${HOLD_TICK_S}s) with sticks: $STICK_SCHEDULE"
    LEAVE_T=$(date +%s)
    for i in $(seq 1 "$HOLD_S"); do
        kill -0 "$PID" 2>/dev/null || { print "game process gone at hold-iter $i"; break; }
        if [[ -n "${STICK_AT[$i]:-}" ]]; then
            sk=${STICK_AT[$i]}
            raise_game
            # Longer hold (400ms) so a ~10 fps poll cannot miss the pulse.
            "$WINCTL" key "$PID" "$KEYCODE[$sk]" 400 >/dev/null 2>&1
            print "[keys] stick $sk at hold_${i} (+${i}s post-hold-start)"
            snap "hold_$(printf '%02d' $i)_${sk}"
        else
            snap "hold_$(printf '%02d' $i)"
        fi
        if (( $(print "$HOLD_TICK_S < 1" | bc -l) )); then
            NSUB=$(print "(1 / $HOLD_TICK_S) - 1" | bc)
            subdone=0
            for j in $(seq 1 "$NSUB"); do
                sleep "$HOLD_TICK_S"
                kill -0 "$PID" 2>/dev/null || { subdone=1; break; }
                snap "hold_$(printf '%02d' $i)_sub$(printf '%02d' $j)"
            done
            (( subdone )) && break
            sleep "$HOLD_TICK_S"
        else
            sleep 1
        fi
    done
    print "hold done wall=$(print "$(date +%s) - $LEAVE_T" | bc)s"
    GRACE=0
fi

print "grace window ${GRACE}s @ 1 Hz after probes"
for i in $(seq 1 "$GRACE"); do
    kill -0 "$PID" 2>/dev/null || { print "game process gone at grace-iter $i"; break; }
    snap "grace_$(printf '%02d' $i)"
    sleep 1
done
print "done wall=$(print "$(date +%s) - $A_PRESS_T" | bc)s"

if kill -0 "$PID" 2>/dev/null; then
    print "game process still alive; killing"
    kill -9 "$PID" 2>/dev/null
fi

LOG=$OUTDIR/run.log
print -- "--- summary ---"
print "lle tasks: $(grep -ac '\[lle task\]' "$LOG" || true)"
print "exit=2: $(grep -ac 'exit=2' "$LOG" || true)"
print "exit=1: $(grep -ac 'exit=1' "$LOG" || true)"
print "missing-func: $(grep -ac '\[missing-func\]' "$LOG" || true)"
print "UnhandledJump: $(grep -ac 'UnhandledJumpTarget\|Unhandled jump' "$LOG" || true)"
print "thr-resume bad=1: $(grep -ac '\[thr-resume\].*bad=1' "$LOG" || true)"
print "ost-wb SKIP_WIDTH: $(grep -ac '\[ost-wb\] SKIP_WIDTH' "$LOG" || true)"
print "ost-wb SKIP_OOB: $(grep -ac '\[ost-wb\] SKIP_OOB' "$LOG" || true)"
print "fs max: $(grep -a '\[vi\] update_screen' "$LOG" | sed -n 's/.*fs=\([0-9]*\).*/\1/p' | sort -n | tail -1)"
print "last fs line: $(grep -a '\[vi\] update_screen' "$LOG" | tail -1)"
print "last phase: $(grep -a '\[phase\]' "$LOG" | tail -1)"
print "CRASH: $(grep -ac '\[CRASH\]' "$LOG" || true)"
print -- "--- done ---"
