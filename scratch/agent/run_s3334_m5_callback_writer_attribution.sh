#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s3334_m5_callback_writer_attribution"
BUILD="$ROOT/build"
mkdir -p "$OUT"
LOG="$OUT/port.log"

cleanup() {
    if [[ -n "${KEYPID:-}" ]] && kill -0 "$KEYPID" 2>/dev/null; then kill -9 "$KEYPID" 2>/dev/null || true; fi
    if [[ -n "${PID:-}" ]] && kill -0 "$PID" 2>/dev/null; then /usr/bin/pkill -KILL -P "$PID" 2>/dev/null || true; kill -9 "$PID" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

cd "$BUILD" || exit 2
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_M5_C88_VALUE=0 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_STATE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_SERVICE_RESOLVE=1 \
    ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_AUDIO_RETURN=1 \
    ROGUESQ_LOG_M5_VOICE_SLOTS=1 ROGUESQ_LOG_M5_B40_WRITER=1 \
    ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 \
    ROGUESQ_LOG_INIT_VOICE_SAMPLE=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
    ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_VI_CALLERS=1 \
    ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
    ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_B40_ROUTE=1 \
    ROGUESQ_LOG_M5_CALLBACK_WRITER=1 ROGUESQ_LOG_M5_CALLBACK_CENSUS=1 \
    ./RogueSquadron64Recomp >"$LOG" 2>&1 &
PID=$!

(
    previous=0
    for at in 6 11 16 21 26 31 36 41 46 51 56; do
        sleep "$((at - previous))"
        previous=$at
        kill -0 "$PID" 2>/dev/null || exit 0
        "$BUILD/winctl" activate "$PID" >/dev/null 2>&1 || true
        "$BUILD/winctl" key "$PID" 36 >/dev/null 2>&1 || true
    done
) &
KEYPID=$!

for ((i=0; i<180; ++i)); do
    kill -0 "$PID" 2>/dev/null || break
    grep -a -q 'vi_width=512 .*origin=0x006AB400' "$LOG" 2>/dev/null && break
    sleep 1
done
sleep 15
exit 0
