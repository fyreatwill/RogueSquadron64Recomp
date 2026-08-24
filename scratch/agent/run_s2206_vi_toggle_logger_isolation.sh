#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2206_vi_toggle_logger_isolation"
mkdir -p "$OUT"

if [[ ! -f "$BUILD/rogue_squadron.z64" ]]; then
    if [[ ! -f "$ROOT/rogue_squadron.z64" ]]; then
        print "ERROR: no ROM in build/ or repository root"
        exit 3
    fi
    cp -p "$ROOT/rogue_squadron.z64" "$BUILD/rogue_squadron.z64"
fi

if [[ ! -x "$BUILD/RogueSquadron64Recomp" ]]; then
    print "ERROR: build/RogueSquadron64Recomp is missing"
    exit 3
fi

cd "$BUILD" || exit 2

COMMON=(
    ROGUESQ_AUDIO_UCODE=0
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_LOG_PHASE=1
)

env ${=COMMON} ROGUESQ_VI_ALTERNATE_FIELDS=0 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
    ./RogueSquadron64Recomp > "$OUT/logged-control.log" 2>&1 &
LOGGED_CONTROL=$!
env ${=COMMON} ROGUESQ_VI_ALTERNATE_FIELDS=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
    ./RogueSquadron64Recomp > "$OUT/logged-alternate.log" 2>&1 &
LOGGED_ALTERNATE=$!
env ${=COMMON} ROGUESQ_VI_ALTERNATE_FIELDS=0 \
    ./RogueSquadron64Recomp > "$OUT/quiet-control.log" 2>&1 &
QUIET_CONTROL=$!
env ${=COMMON} ROGUESQ_VI_ALTERNATE_FIELDS=1 \
    ./RogueSquadron64Recomp > "$OUT/quiet-alternate.log" 2>&1 &
QUIET_ALTERNATE=$!

typeset -A PIDS=(
    logged-control "$LOGGED_CONTROL"
    logged-alternate "$LOGGED_ALTERNATE"
    quiet-control "$QUIET_CONTROL"
    quiet-alternate "$QUIET_ALTERNATE"
)
typeset -A DONE=(logged-control 0 logged-alternate 0 quiet-control 0 quiet-alternate 0)
typeset -A KILLED=(logged-control 0 logged-alternate 0 quiet-control 0 quiet-alternate 0)
typeset -A STATUS=(logged-control running logged-alternate running quiet-control running quiet-alternate running)
typeset -A EARLY=(logged-control 0 logged-alternate 0 quiet-control 0 quiet-alternate 0)
typeset -A TARGET=(logged-control 0 logged-alternate 0 quiet-control 0 quiet-alternate 0)
typeset -A TITLE=(logged-control 0 logged-alternate 0 quiet-control 0 quiet-alternate 0)
typeset -A HANGAR=(logged-control 0 logged-alternate 0 quiet-control 0 quiet-alternate 0)
DEADLINE=$((SECONDS + 180))

while (( SECONDS < DEADLINE )); do
    live=0
    for arm in logged-control logged-alternate quiet-control quiet-alternate; do
        pid=${PIDS[$arm]}
        log="$OUT/$arm.log"
        if (( DONE[$arm] == 0 )); then
            if (( EARLY[$arm] == 0 )) && \
                grep -a -q '^\[phase\] vi_width=640 .*origin=0x0066A500' "$log"; then
                EARLY[$arm]=1
            fi
            if (( TARGET[$arm] == 0 )); then
                if [[ "$arm" == logged-* ]]; then
                    grep -a -q '^\[vi-context-port\].*framebuffer=0x00695C00' "$log" && TARGET[$arm]=1
                else
                    grep -a -q '^\[phase\] vi_width=640 .*origin=0x00696100' "$log" && TARGET[$arm]=1
                fi
            fi
            grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" && TITLE[$arm]=1
            grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" && HANGAR[$arm]=1
            if (( TITLE[$arm] == 1 && HANGAR[$arm] == 1 )); then
                print "$arm reached title and hangar; SIGKILL"
                kill -9 "$pid" 2>/dev/null
                KILLED[$arm]=1
                STATUS[$arm]=phases
                wait "$pid" 2>/dev/null
                DONE[$arm]=1
            elif kill -0 "$pid" 2>/dev/null; then
                live=1
            else
                wait "$pid" 2>/dev/null
                STATUS[$arm]=$?
                DONE[$arm]=1
            fi
        fi
    done
    (( live == 0 )) && break
    sleep 1
done

for arm in logged-control logged-alternate quiet-control quiet-alternate; do
    pid=${PIDS[$arm]}
    if (( DONE[$arm] == 0 )); then
        print "$arm watchdog expired; SIGKILL"
        kill -9 "$pid" 2>/dev/null
        KILLED[$arm]=1
        STATUS[$arm]=watchdog
        wait "$pid" 2>/dev/null
        DONE[$arm]=1
    fi
done

summary="$OUT/s2206-summary.txt"
: > "$summary"
rc=0
for arm in logged-control logged-alternate quiet-control quiet-alternate; do
    log="$OUT/$arm.log"
    early=$(grep -a -c '^\[phase\] vi_width=640 .*origin=0x0066A500' "$log" || true)
    target_phase_first=$(grep -a -c '^\[phase\] vi_width=640 .*origin=0x00696100' "$log" || true)
    target_phase_second=$(grep -a -c '^\[phase\] vi_width=640 .*origin=0x00696600' "$log" || true)
    target_commit_first=$(grep -a -c '^\[vi-context-port\].*framebuffer=0x00695C00.*committed=0x00696100' "$log" || true)
    target_commit_second=$(grep -a -c '^\[vi-context-port\].*framebuffer=0x00695C00.*committed=0x00696600' "$log" || true)
    title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" || true)
    hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" || true)
    crashes=$(grep -a -c -E '\[(CRASH|ABORT)\]' "$log" || true)
    line="$arm early=$early target_phase_first=$target_phase_first target_phase_second=$target_phase_second target_commit_first=$target_commit_first target_commit_second=$target_commit_second title=$title hangar=$hangar crashes=$crashes terminal=${STATUS[$arm]} killed=${KILLED[$arm]}"
    print "$line" | tee -a "$summary"
    (( early == 0 )) && rc=1
    if [[ "$arm" == logged-* ]]; then
        (( target_commit_first == 0 )) && rc=1
    else
        (( target_phase_first == 0 )) && rc=1
    fi
    (( crashes > 0 )) && rc=1
done

exit "$rc"
