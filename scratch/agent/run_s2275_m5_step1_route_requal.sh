#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2275_m5_step1_route_requal}
OUT="$ROOT/scratch/agent/$TAG"
mkdir -p "$OUT"
cd "$BUILD" || exit 2

if [[ ! -f rogue_squadron.z64 || ! -x RogueSquadron64Recomp ]]; then
    print "ERROR: build/ must contain the ROM and executable"
    exit 3
fi

env \
    ROGUESQ_LLE_FORCE=1 \
    ROGUESQ_LLE_UNGATED=1 \
    ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_SPIN_YIELD=1 \
    ROGUESQ_M5_C88_VALUE=0 \
    ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_AUDIO_RETURN=1 \
    ROGUESQ_LOG_PCM_BOUNDARY=1 \
    ROGUESQ_LOG_M5_B40_ROUTE=1 \
    ROGUESQ_LOG_M5_ROUTE_STATE=1 \
    PROBE_PHASE_WIDTH=1024 \
    PROBE_KEYS_FROM_PHASE=1 \
    ./RogueSquadron64Recomp > "$OUT/silent.log" 2>&1 &
PID=$!
print "pid=$PID" > "$OUT/driver.log"

DEADLINE=$((SECONDS + 180))
while (( SECONDS < DEADLINE )); do
    if grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/silent.log"; then
        print "hangar_phase=observed" | tee -a "$OUT/driver.log"
        break
    fi
    if ! kill -0 "$PID" 2>/dev/null; then
        sleep 1
        if grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/silent.log"; then
            print "hangar_phase=observed_after_process_death" | tee -a "$OUT/driver.log"
        else
            print "died_before_hangar" | tee -a "$OUT/driver.log"
            wait "$PID" 2>/dev/null
            exit 4
        fi
        break
    fi
    sleep 1
done

if ! grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/silent.log"; then
    print "hangar_phase=missing; SIGKILL" | tee -a "$OUT/driver.log"
    kill -9 "$PID" 2>/dev/null
    wait "$PID" 2>/dev/null
    exit 5
fi

POST_DEADLINE=$((SECONDS + 120))
while (( SECONDS < POST_DEADLINE )); do
    if ! kill -0 "$PID" 2>/dev/null; then
        break
    fi
    sleep 1
done

if kill -0 "$PID" 2>/dev/null; then
    print "post_hangar_timeout; SIGKILL" | tee -a "$OUT/driver.log"
    kill -9 "$PID" 2>/dev/null
fi
wait "$PID" 2>/dev/null

print "--- phase origins ---" >> "$OUT/driver.log"
grep -a '^\[phase\]' "$OUT/silent.log" >> "$OUT/driver.log" || true
print "--- controls ---" >> "$OUT/driver.log"
for marker in audtask-dispatch audio-return pcm-boundary-source pcm-boundary-consumer m5-b40-route m5-route-state missing-func CRASH ABORT; do
    count=$(grep -a -c "\[$marker\]" "$OUT/silent.log" || true)
    print "$marker=$count" >> "$OUT/driver.log"
done
grep -a -E '\[pc-symbol\]|\[last-guest-pc\]' "$OUT/silent.log" | tail -4 >> "$OUT/driver.log" || true

if grep -a -q '^\[CRASH\]' "$OUT/silent.log"; then
    exit 6
fi
exit 0
