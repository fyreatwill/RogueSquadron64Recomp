#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2204_port_vi_context"
mkdir -p "$OUT"
cd "$BUILD" || exit 2

if [[ ! -f rogue_squadron.z64 ]]; then
    print "ERROR: no ROM in build/"
    exit 3
fi

COMMON=(
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_VI_CONTEXT_PORT=1
)

env ${=COMMON} ./RogueSquadron64Recomp > "$OUT/control.log" 2>&1 &
CONTROL=$!
env ${=COMMON} ROGUESQ_VI_ALTERNATE_FIELDS=1 \
    ./RogueSquadron64Recomp > "$OUT/alternate.log" 2>&1 &
ALTERNATE=$!

typeset -A PIDS=(control "$CONTROL" alternate "$ALTERNATE")
typeset -A DONE=(control 0 alternate 0)
typeset -A KILLED=(control 0 alternate 0)
typeset -A REACHED=(control 0 alternate 0)
typeset -A STATUS=(control 0 alternate 0)
DEADLINE=$((SECONDS + 35))

while (( SECONDS < DEADLINE )); do
    live=0
    for arm in control alternate; do
        pid=${PIDS[$arm]}
        log="$OUT/$arm.log"
        if (( DONE[$arm] == 0 )); then
            if (( REACHED[$arm] == 0 )) && \
                grep -a -q '^\[vi-context-port\].*committed=0x00696100' "$log"; then
                REACHED[$arm]=1
                print "$arm reached target 640 window; collecting 5s"
                sleep 5
                if kill -0 "$pid" 2>/dev/null; then
                    kill -9 "$pid" 2>/dev/null
                    KILLED[$arm]=1
                    wait "$pid" 2>/dev/null
                fi
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

for arm in control alternate; do
    pid=${PIDS[$arm]}
    if (( DONE[$arm] == 0 )); then
        print "$arm watchdog expired; SIGKILL"
        kill -9 "$pid" 2>/dev/null
        KILLED[$arm]=1
        wait "$pid" 2>/dev/null
        DONE[$arm]=1
    fi
done

rc=0
for arm in control alternate; do
    log="$OUT/$arm.log"
    controls=$(grep -a -c '\[vi-context-port-control\]' "$log" || true)
    rows=$(grep -a -c '\[vi-context-port\]' "$log" || true)
    summaries=$(grep -a -c '\[vi-context-port-summary\]' "$log" || true)
    target_first=$(grep -a -c '^\[vi-context-port\].*committed=0x00696100' "$log" || true)
    target_second=$(grep -a -c '^\[vi-context-port\].*committed=0x00696600' "$log" || true)
    phase_first=$(grep -a -c '\[phase\] vi_width=640 .*origin=0x00696100' "$log" || true)
    phase_second=$(grep -a -c '\[phase\] vi_width=640 .*origin=0x00696600' "$log" || true)
    crashes=$(grep -a -c -E '\[(CRASH|ABORT)\]' "$log" || true)
    print "$arm controls=$controls rows=$rows summaries=$summaries target_first=$target_first target_second=$target_second phase_first=$phase_first phase_second=$phase_second crashes=$crashes status=${STATUS[$arm]} killed=${KILLED[$arm]}"
    (( controls == 0 || rows == 0 )) && rc=1
    (( crashes > 0 )) && rc=1
    if (( KILLED[$arm] == 0 && STATUS[$arm] != 0 )); then
        rc=1
    fi
done

exit "$rc"
