#!/bin/zsh
# s670: variant of scratch/s73_post_a_scene/run_mission_keys.sh that adds a
# LOG-PHASE-GATED post-sec2 input pulse instead of a wall-clock guess.
#
# Item -421 / HYPOTHESIS-ID m3-post-exit-fs-stall, Arm B (H-menu-return-input
# vs H-menu-return-guest-teardown). s669 offline scoring of s668 att2/att3
# showed sec2 fires at a highly consistent process-relative t_ms (~265008ms
# both attempts) and thr12 (thread id=13) is destroyed ~195-200s later with
# rdpFs flat the whole window -- but that is unforced behaviour. This script
# waits for the REAL "[overlay] start-match: section 2" log line (not a
# stopwatch guess, per CURRENT-TRUTH method traps §4.3) during the hold
# window, then fires a synthetic Start pulse SEC2_SETTLE_S later and keeps
# holding POST_PULSE_HOLD_S more seconds so the outcome (packTlut fires? does
# section-3 menu-return still happen? does thr12/id=13 outlive the s669
# baseline lifetime?) can be scored from the resulting run.log.
#
# Only the hold-window block differs from run_mission_keys.sh; everything
# else (startup, phase wait, probe schedule, stable wait) is unchanged so the
# engage/recovery machinery behaves identically to s668's proven recipe.
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

GAME_EXTRA_ENV=${GAME_EXTRA_ENV:-}
env ${=GAME_EXTRA_ENV} ./RogueSquadron64Recomp > "$OUTDIR/run.log" 2>&1 &
PID=$!
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

sec2_seen() {
    /usr/bin/grep -aq '\[overlay\] start-match: section 2' "$OUTDIR/run.log" 2>/dev/null
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

PROBE_MODE=${PROBE_MODE:-mixed}
HOLD_S=${HOLD_S:-0}
if [[ -n "${PROBES_OVERRIDE:-}" ]]; then
    PROBES=(${=PROBES_OVERRIDE})
elif [[ "$PROBE_MODE" == "start_only" ]]; then
    if (( HOLD_S > 0 )); then
        PROBES=(p1:start:5)
    else
        PROBES=(p1:start:15)
    fi
elif [[ "$PROBE_MODE" == "double_start" ]]; then
    PROBES=(p1:start:6 p2:start:3 p3:start:3 p4:start:8)
else
    PROBES=(p1:start:5 p2:a:3 p3:start:10)
fi
typeset -A KEYCODE_EXT=(start 36 a 6 su 13 sd 1 sl 0 sr 2 left 123 right 124)
for k v in ${(kv)KEYCODE_EXT}; do KEYCODE[$k]=$v; done
KEY_HOLD_MS=${KEY_HOLD_MS:-150}
PROBE_KEY_HOLD_MS=${PROBE_KEY_HOLD_MS:-400}

for entry in $PROBES; do
    tag=${entry%%:*}; rest=${entry#*:}
    name=${rest%%:*}; wait_s=${rest#*:}
    kill -0 "$PID" 2>/dev/null || { print "process gone before probe $tag $name"; break; }
    raise_game
    snap "pre_${tag}_${name}"
    "$WINCTL" key "$PID" "$KEYCODE[$name]" "$PROBE_KEY_HOLD_MS" >/dev/null 2>&1
    print "[keys] probe $tag $name hold=${PROBE_KEY_HOLD_MS}ms"
    sleep 0.8
    snap "post_${tag}_${name}"
    TICK=${CAPTURE_TICK_S:-1}
    NTICKS=$(print "$wait_s / $TICK" | bc)
    for j in $(seq 1 "$NTICKS"); do
        kill -0 "$PID" 2>/dev/null || break
        snap "after_${tag}_${name}_$(printf '%03d' $j)"
        sleep "$TICK"
    done
done

# --- s670 post-sec2 pulse hold window (replaces run_mission_keys.sh's plain
# STICK_SCHEDULE hold) ---
# SEC2_PULSE=1 enables phase-gating: instead of a fixed HOLD_S countdown, the
# loop runs until sec2 is seen in the log, waits SEC2_SETTLE_S more real
# seconds, fires SEC2_PULSE_KEYS, then holds POST_PULSE_HOLD_S more seconds
# so the effect (or its absence) lands in this run's log. MAX_HOLD_S is a
# hard ceiling so a run that never reaches sec2 does not burn the whole
# session budget.
SEC2_PULSE=${SEC2_PULSE:-0}
if (( SEC2_PULSE )); then
    SEC2_SETTLE_S=${SEC2_SETTLE_S:-8}
    POST_PULSE_HOLD_S=${POST_PULSE_HOLD_S:-180}
    MAX_HOLD_S=${MAX_HOLD_S:-500}
    SEC2_PULSE_KEYS=${SEC2_PULSE_KEYS:-"start start"}
    print "post-sec2 pulse hold: max=${MAX_HOLD_S}s settle=${SEC2_SETTLE_S}s post_pulse=${POST_PULSE_HOLD_S}s keys='${SEC2_PULSE_KEYS}'"
    LEAVE_T=$(date +%s)
    SEC2_AT=0
    PULSED_AT=0
    for i in $(seq 1 "$MAX_HOLD_S"); do
        kill -0 "$PID" 2>/dev/null || { print "game process gone at hold-iter $i"; break; }
        snap "hold_$(printf '%03d' $i)"
        if (( SEC2_AT == 0 )) && sec2_seen; then
            SEC2_AT=$i
            print "[sec2-pulse] section-2 seen at hold_${i} (+${i}s) -- settling ${SEC2_SETTLE_S}s"
        fi
        if (( SEC2_AT > 0 && PULSED_AT == 0 )) && (( i - SEC2_AT >= SEC2_SETTLE_S )); then
            raise_game
            for kname in ${=SEC2_PULSE_KEYS}; do
                "$WINCTL" key "$PID" "$KEYCODE[$kname]" 400 >/dev/null 2>&1
                print "[sec2-pulse] fired key=$kname at hold_${i} (+$((i - SEC2_AT))s post-sec2)"
                sleep 0.5
            done
            PULSED_AT=$i
            snap "hold_$(printf '%03d' $i)_pulsed"
        fi
        if (( PULSED_AT > 0 )) && (( i - PULSED_AT >= POST_PULSE_HOLD_S )); then
            print "[sec2-pulse] post-pulse observation window (${POST_PULSE_HOLD_S}s) complete at hold_${i}"
            break
        fi
        sleep 1
    done
    print "hold done wall=$(print "$(date +%s) - $LEAVE_T" | bc)s sec2_at=${SEC2_AT} pulsed_at=${PULSED_AT}"
    GRACE=0
elif (( HOLD_S > 0 )); then
    STICK_SCHEDULE=${STICK_SCHEDULE:-"10:sr 25:sl 40:su"}
    typeset -A STICK_AT
    for entry in ${=STICK_SCHEDULE}; do
        STICK_AT[${entry%%:*}]=${entry#*:}
    done
    HOLD_TICK_S=${HOLD_TICK_S:-1}
    print "hold window ${HOLD_S}s @ 1 Hz (sub-tick ${HOLD_TICK_S}s) with sticks: $STICK_SCHEDULE"
    LEAVE_T=$(date +%s)
    for i in $(seq 1 "$HOLD_S"); do
        kill -0 "$PID" 2>/dev/null || { print "game process gone at hold-iter $i"; break; }
        if [[ -n "${STICK_AT[$i]:-}" ]]; then
            sk=${STICK_AT[$i]}
            raise_game
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
print "section-2: $(grep -ac '\[overlay\] start-match: section 2' "$LOG" || true)"
print "section-3: $(grep -ac '\[overlay\] start-match: section 3' "$LOG" || true)"
print "packTlut: $(grep -ac 'packTlut' "$LOG" || true)"
print "sec2-pulse fired: $(grep -ac '\[sec2-pulse\] fired' "$LOG" || true)"
print "CRASH: $(grep -ac '\[CRASH\]' "$LOG" || true)"
print -- "--- done ---"
