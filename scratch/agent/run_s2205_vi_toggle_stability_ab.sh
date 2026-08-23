#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2205_vi_toggle_stability_ab"
mkdir -p "$OUT"
cd "$BUILD" || exit 2

if [[ ! -f rogue_squadron.z64 || ! -x RogueSquadron64Recomp ]]; then
    print "ERROR: build/ is missing RogueSquadron64Recomp or rogue_squadron.z64"
    exit 3
fi

COMMON=(
    ROGUESQ_AUDIO_UCODE=0
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_VI_CONTEXT_PORT=1
)

env ${=COMMON} ROGUESQ_VI_ALTERNATE_FIELDS=0 \
    ./RogueSquadron64Recomp > "$OUT/control.log" 2>&1 &
CONTROL=$!
env ${=COMMON} ROGUESQ_VI_ALTERNATE_FIELDS=1 \
    ./RogueSquadron64Recomp > "$OUT/alternate.log" 2>&1 &
ALTERNATE=$!

typeset -A PIDS=(control "$CONTROL" alternate "$ALTERNATE")
typeset -A DONE=(control 0 alternate 0)
typeset -A KILLED=(control 0 alternate 0)
typeset -A REACHED=(control 0 alternate 0)
typeset -A TITLE=(control 0 alternate 0)
typeset -A HANGAR=(control 0 alternate 0)
typeset -A STATUS=(control 0 alternate 0)
typeset -A TERMINAL=(control running alternate running)
DEADLINE=$((SECONDS + 180))

while (( SECONDS < DEADLINE )); do
    live=0
    for arm in control alternate; do
        pid=${PIDS[$arm]}
        log="$OUT/$arm.log"
        if (( DONE[$arm] == 0 )); then
            if (( REACHED[$arm] == 0 )) && \
                grep -a -q '^\[vi-context-port\].*committed=0x00696100' "$log"; then
                REACHED[$arm]=1
                print "$arm reached target 640 commit; collecting later phases"
            fi
            if (( TITLE[$arm] == 0 )) && \
                grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log"; then
                TITLE[$arm]=1
            fi
            if (( HANGAR[$arm] == 0 )) && \
                grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log"; then
                HANGAR[$arm]=1
            fi
            if (( TITLE[$arm] == 1 && HANGAR[$arm] == 1 )); then
                print "$arm reached title and hangar; SIGKILL"
                kill -9 "$pid" 2>/dev/null
                KILLED[$arm]=1
                TERMINAL[$arm]=phases
                wait "$pid" 2>/dev/null
                DONE[$arm]=1
            elif kill -0 "$pid" 2>/dev/null; then
                live=1
            else
                wait "$pid" 2>/dev/null
                STATUS[$arm]=$?
                TERMINAL[$arm]=exit
                DONE[$arm]=1
            fi
        fi
    done
    (( live == 0 )) && break
    sleep 1
done

for arm in control alternate; do
    pid=${PIDS[$arm]}
    if (( DONE[$arm] == 0 )); then
        print "$arm watchdog expired; SIGKILL"
        kill -9 "$pid" 2>/dev/null
        KILLED[$arm]=1
        TERMINAL[$arm]=watchdog
        wait "$pid" 2>/dev/null
        DONE[$arm]=1
    fi
done

summary="$OUT/s2205-summary.txt"
: > "$summary"
rc=0
for arm in control alternate; do
    log="$OUT/$arm.log"
    controls=$(grep -a -c '\[vi-context-port-control\]' "$log" || true)
    rows=$(grep -a -c '\[vi-context-port\]' "$log" || true)
    target_first=$(grep -a -c '^\[vi-context-port\].*committed=0x00696100' "$log" || true)
    target_second=$(grep -a -c '^\[vi-context-port\].*committed=0x00696600' "$log" || true)
    phase_first=$(grep -a -c '\[phase\] vi_width=640 .*origin=0x00696100' "$log" || true)
    phase_second=$(grep -a -c '\[phase\] vi_width=640 .*origin=0x00696600' "$log" || true)
    title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" || true)
    hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" || true)
    crashes=$(grep -a -c -E '\[(CRASH|ABORT)\]' "$log" || true)
    line="$arm controls=$controls rows=$rows target_first=$target_first target_second=$target_second phase_first=$phase_first phase_second=$phase_second title=$title hangar=$hangar crashes=$crashes terminal=${TERMINAL[$arm]} status=${STATUS[$arm]} killed=${KILLED[$arm]}"
    print "$line" | tee -a "$summary"
    (( controls == 0 || rows == 0 || target_first == 0 )) && rc=1
    (( crashes > 0 )) && rc=1
done

exit "$rc"
