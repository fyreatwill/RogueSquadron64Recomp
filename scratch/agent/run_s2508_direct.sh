#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2508_m5_audio_arm_route/direct2"
mkdir -p "$OUT/silent" "$OUT/image"
SILENT_PID=0
IMAGE_PID=0

cleanup() {
    for name in silent image; do
        local pid=0
        [[ "$name" == silent ]] && pid=$SILENT_PID || pid=$IMAGE_PID
        [[ "$pid" != 0 ]] && kill -9 "$pid" 2>/dev/null || true
    done
}
trap cleanup EXIT INT TERM

launch() {
    local name="$1" audio="$2"
    (cd "$BUILD" && env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 \
        ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_M5_C88_VALUE=0 \
        ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 \
        ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
        ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 \
        ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 \
        ROGUESQ_AUDIO_UCODE="$audio" ./RogueSquadron64Recomp) > "$OUT/$name/run.log" 2>&1 &
    if [[ "$name" == silent ]]; then
        SILENT_PID=$!
    else
        IMAGE_PID=$!
    fi
}

launch silent 0
launch image 1
print "silent_pid=$SILENT_PID image_pid=$IMAGE_PID" > "$OUT/driver.log"

raise_game() {
    local pid="$1"
    "$BUILD/winctl" activate "$pid" >/dev/null 2>&1 || true
    /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $pid to true" >/dev/null 2>&1 || true
}

for name in silent image; do
    pid=0
    [[ "$name" == silent ]] && pid=$SILENT_PID || pid=$IMAGE_PID
    deadline=$((SECONDS + 120))
    while (( SECONDS < deadline )); do
        grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/$name/run.log" && break
        kill -0 "$pid" 2>/dev/null || break
        sleep 1
    done
    if grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/$name/run.log"; then
        print "$name title_gate=passed" >> "$OUT/driver.log"
        (for at in 3 7 11; do sleep 4; raise_game "$pid"; "$BUILD/winctl" key "$pid" 36 >/dev/null 2>&1; done
         sleep 4; raise_game "$pid"; "$BUILD/winctl" key "$pid" 6 >/dev/null 2>&1
         sleep 15; raise_game "$pid"; "$BUILD/winctl" key "$pid" 36 >/dev/null 2>&1
         sleep 15; raise_game "$pid"; "$BUILD/winctl" key "$pid" 36 >/dev/null 2>&1
         sleep 15; raise_game "$pid"; "$BUILD/winctl" key "$pid" 6 >/dev/null 2>&1
         sleep 15; raise_game "$pid"; "$BUILD/winctl" key "$pid" 36 >/dev/null 2>&1) &
    else
        print "$name title_gate=missing" >> "$OUT/driver.log"
    fi
done

sleep 90
for name in silent image; do
    pid=0
    [[ "$name" == silent ]] && pid=$SILENT_PID || pid=$IMAGE_PID
    kill -0 "$pid" 2>/dev/null && print "$name still_running=1" >> "$OUT/driver.log" || print "$name exited=1" >> "$OUT/driver.log"
done
exit 0
