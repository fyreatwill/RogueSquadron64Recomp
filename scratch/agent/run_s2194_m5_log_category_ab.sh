#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2194_m5_log_category_ab"
mkdir -p "$OUT"
cd "$BUILD" || exit 2

if [[ ! -f rogue_squadron.z64 ]]; then
    print "ERROR: no ROM in build/"
    exit 3
fi

COMMON=(
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_AUDIO_UCODE=1
    ROGUESQ_LLE_FORCE=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_LOG_CUTSCENE_A2_50=1
    ROGUESQ_LOG_M5_WRITER_PARITY=1
)

env ${=COMMON} ./RogueSquadron64Recomp > "$OUT/quiet.log" 2>&1 &
QUIET=$!
env ${=COMMON} ROGUESQ_LOG_SLOT_DISPATCH=1 ./RogueSquadron64Recomp > "$OUT/slot.log" 2>&1 &
SLOT=$!
env ${=COMMON} ROGUESQ_LOG_EVENT_WIRING=1 ./RogueSquadron64Recomp > "$OUT/event.log" 2>&1 &
EVENT=$!
env ${=COMMON} ROGUESQ_LOG_AUDIO_RETURN=1 ./RogueSquadron64Recomp > "$OUT/audio.log" 2>&1 &
AUDIO=$!

typeset -A PIDS=(quiet "$QUIET" slot "$SLOT" event "$EVENT" audio "$AUDIO")
typeset -A DONE=(quiet 0 slot 0 event 0 audio 0)
typeset -A FOUND=(quiet 0 slot 0 event 0 audio 0)
DEADLINE=$((SECONDS + 180))

while (( SECONDS < DEADLINE )); do
    live=0
    for arm in quiet slot event audio; do
        pid=${PIDS[$arm]}
        if (( DONE[$arm] == 0 )); then
            if grep -a -q '\[phase\] vi_width=640 .*origin=0x00696600' "$OUT/$arm.log"; then
                FOUND[$arm]=1
                DONE[$arm]=1
                print "$arm reached second origin; collecting 15s"
                sleep 15
                kill -9 "$pid" 2>/dev/null
                wait "$pid" 2>/dev/null
            elif kill -0 "$pid" 2>/dev/null; then
                live=1
            else
                DONE[$arm]=1
                wait "$pid" 2>/dev/null
            fi
        fi
    done
    (( live == 0 )) && break
    sleep 1
done

for arm in quiet slot event audio; do
    pid=${PIDS[$arm]}
    if (( DONE[$arm] == 0 )); then
        print "$arm timed out; killing"
        kill -9 "$pid" 2>/dev/null
        wait "$pid" 2>/dev/null
        DONE[$arm]=1
    fi
done

rc=0
for arm in quiet slot event audio; do
    log="$OUT/$arm.log"
    controls=$(grep -a -c '\[m5-writer-parity-control\]' "$log" || true)
    crashes=$(grep -a -c '\[CRASH\]' "$log" || true)
    print "$arm controls=$controls second_origin=${FOUND[$arm]} crashes=$crashes"
    grep -a '\[phase\] vi_width=640' "$log" || true
    (( crashes > 0 )) && rc=1
done
exit "$rc"
