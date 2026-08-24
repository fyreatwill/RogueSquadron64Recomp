#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2273_m5_step1_pair}
OUT="$ROOT/scratch/agent/$TAG"
mkdir -p "$OUT"
cd "$BUILD" || exit 2

if [[ ! -f rogue_squadron.z64 || ! -x RogueSquadron64Recomp ]]; then
    print "ERROR: build/ must contain the ROM and executable"
    exit 3
fi

COMMON=(
    ROGUESQ_LLE_FORCE=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_M5_C88_VALUE=0
    ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_THREAD_RESUME=1
    ROGUESQ_LOG_OST_WB=1
    ROGUESQ_LOG_RUNNER=1
    ROGUESQ_LOG_RUNNER_ALL=1
    ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1
    PROBE_PHASE_WIDTH=1024
    PROBE_KEYS_FROM_PHASE=1
)

env ${=COMMON} ROGUESQ_AUDIO_UCODE=0 ./RogueSquadron64Recomp \
    > "$OUT/silent.log" 2>&1 &
SILENT=$!
print "silent_pid=$SILENT" > "$OUT/driver.log"

DEADLINE=$((SECONDS + 600))
while (( SECONDS < DEADLINE )); do
    if grep -a -q '\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/silent.log"; then
        print "silent_first_512=observed; launching image" | tee -a "$OUT/driver.log"
        break
    fi
    if ! kill -0 "$SILENT" 2>/dev/null; then
        print "silent_died_before_512" | tee -a "$OUT/driver.log"
        wait "$SILENT" 2>/dev/null
        exit 4
    fi
    sleep 1
done

if (( SECONDS >= DEADLINE )); then
    print "silent_512_timeout" | tee -a "$OUT/driver.log"
    kill -9 "$SILENT" 2>/dev/null
    wait "$SILENT" 2>/dev/null
    exit 5
fi

env ${=COMMON} ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp \
    > "$OUT/image.log" 2>&1 &
IMAGE=$!
print "image_pid=$IMAGE" >> "$OUT/driver.log"

PAIR_DEADLINE=$((SECONDS + 180))
while (( SECONDS < PAIR_DEADLINE )); do
    silent_live=0
    image_live=0
    kill -0 "$SILENT" 2>/dev/null && silent_live=1
    kill -0 "$IMAGE" 2>/dev/null && image_live=1
    if (( silent_live == 0 && image_live == 0 )); then
        break
    fi
    sleep 1
done

if kill -0 "$SILENT" 2>/dev/null; then
    print "silent_timeout; SIGKILL" | tee -a "$OUT/driver.log"
    kill -9 "$SILENT" 2>/dev/null
fi
if kill -0 "$IMAGE" 2>/dev/null; then
    print "image_timeout; SIGKILL" | tee -a "$OUT/driver.log"
    kill -9 "$IMAGE" 2>/dev/null
fi
wait "$SILENT" 2>/dev/null
wait "$IMAGE" 2>/dev/null

for arm in silent image; do
    log="$OUT/$arm.log"
    print "--- $arm ---" >> "$OUT/driver.log"
    for marker in \
        '\[audtask-dispatch\]' '\[audtask-abi\]' '\[audtask-dma-row\]' \
        '\[audtask-image-stage-row\]' '\[audio-return\]' '\[pcm-boundary-source\]' \
        '\[pcm-boundary-consumer\]' '\[slot-alloc\]' '\[slot-sb\]' \
        '\[filter-voice-audit-control\]' '\[m5-gate\]' '\[m5-b40-route-control\]' \
        '\[m5-route-state-control\]' '\[missing-func\]' '\[CRASH\]' '\[ABORT\]'; do
        count=$(grep -a -c "$marker" "$log" || true)
        print "$marker=$count" >> "$OUT/driver.log"
    done
    print "phase=$(grep -a '\[phase\]' "$log" | tail -3)" >> "$OUT/driver.log"
done

exit 0
