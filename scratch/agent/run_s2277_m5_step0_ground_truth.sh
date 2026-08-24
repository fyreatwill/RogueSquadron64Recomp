#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2277_m5_step0_ground_truth}
OUT="$ROOT/scratch/agent/$TAG"
mkdir -p "$OUT"

cd "$BUILD" || exit 2
if [[ ! -x ./RogueSquadron64Recomp || ! -f ./rogue_squadron.z64 ]]; then
    print "ERROR: build/ control prerequisites are missing" > "$OUT/driver.log"
    exit 3
fi

env \
    ROGUESQ_AUDIO_UCODE=0 \
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
    ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
    ROGUESQ_LOG_SP_TASKS=1 \
    ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 \
    PROBE_PHASE_WIDTH=1024 \
    PROBE_KEYS_FROM_PHASE=1 \
    ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1 &
pid=$!
print "pid=$pid" > "$OUT/driver.log"
hangar=0
deadline=$((SECONDS + 180))
while (( SECONDS < deadline )); do
    if grep -a -q '\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port.log"; then
        hangar=1
        print "hangar=observed" >> "$OUT/driver.log"
        break
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
        print "process=exited" >> "$OUT/driver.log"
        break
    fi
    sleep 1
done
if (( hangar == 0 )); then
    print "hangar=missing; SIGKILL" >> "$OUT/driver.log"
    kill -9 "$pid" 2>/dev/null
fi
wait "$pid" 2>/dev/null

for marker in \
    '\[audtask-dispatch\]' '\[audtask-abi\]' '\[audtask-dma-row\]' \
    '\[audio-return\]' '\[audio-sp-route\]' '\[pcm-boundary-source\]' \
    '\[pcm-boundary-consumer\]' '\[sp\]' '\[m5-gate\]' \
    '\[filter-voice-audit-control\]' '\[m5-b40-route-control\]' \
    '\[m5-route-state-control\]' '\[missing-func\]' '\[CRASH\]' '\[ABORT\]'; do
    print "$marker=$(grep -a -c "$marker" "$OUT/port.log" || true)" >> "$OUT/driver.log"
done
print "title=$(grep -a -c '\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/port.log" || true)" >> "$OUT/driver.log"
print "hangar_rows=$(grep -a -c '\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port.log" || true)" >> "$OUT/driver.log"
grep -a -E '\[phase\]|\[last-guest-pc\]|\[pc-symbol\]' "$OUT/port.log" | tail -8 >> "$OUT/driver.log" || true
(( hangar == 1 ))
