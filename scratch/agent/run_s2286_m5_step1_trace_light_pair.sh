#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2286_m5_step1_trace_light_pair}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" ]]; then
    print "ERROR: retail oracle prerequisites are missing" > "$OUT/driver.log"
    exit 2
fi
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" ]]; then
    print "ERROR: build/ control prerequisites are missing" > "$OUT/driver.log"
    exit 3
fi

cd "$ROOT" || exit 4

PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
COMMON=(
    ROGUESQ_LLE_FORCE=1
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_M5_C88_VALUE=0
    ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1
    ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_GATE_CONTRACT=1
    ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
    ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1
    PROBE_PHASE_WIDTH=1024
    PROBE_KEYS_FROM_PHASE=1
)

ORACLE_PID=""
SILENT_PID=""
IMAGE_PID=""
trap '
    for pid in "$ORACLE_PID" "$SILENT_PID" "$IMAGE_PID"; do
        if [[ -n "$pid" && "$pid" != 0 ]] && kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null
        fi
    done
' EXIT INT TERM

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" \
    --core "$ORACLE_CORE" \
    --rom "$ORACLE_ROM" \
    --video "$ORACLE_VIDEO" \
    --secs 500 \
    --watch-write 0x0:0x800000 \
    --watch-write 0xA0F50:0xA0F54 \
    --watch-write 0x141AD0:0x141AF0 \
    --watch-write 0x1498A:0x1498B \
    --watch-pc 0x80091EB0,0x8009B7EC,0x80029E80,0x80029F30 \
    --vi-trace \
    --press "$PRESS" \
    > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
print "oracle_pid=$ORACLE_PID" >> "$OUT/driver.log"

oracle_gate=0
oracle_deadline=$((SECONDS + 120))
while (( SECONDS < oracle_deadline )); do
    if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && \
        grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" && \
        grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
        oracle_gate=1
        print "oracle_gate=passed whole_rdram=10000 title=1 hangar=1" >> "$OUT/driver.log"
        break
    fi
    if ! kill -0 "$ORACLE_PID" 2>/dev/null; then
        print "oracle_gate=failed oracle_exited" >> "$OUT/driver.log"
        break
    fi
    sleep 1
done

if (( oracle_gate == 0 )); then
    print "oracle_gate=failed deadline_or_missing_control" >> "$OUT/driver.log"
    exit 5
fi

launch_arm() {
    local name="$1"
    local audio_arm="$2"
    (
        cd "$BUILD" || exit 2
        exec env ${=COMMON} ROGUESQ_AUDIO_UCODE="$audio_arm" \
            ./RogueSquadron64Recomp
    ) > "$OUT/$name.log" 2>&1 &
    if [[ "$name" == silent ]]; then
        SILENT_PID=$!
        print "silent_pid=$SILENT_PID" >> "$OUT/driver.log"
    else
        IMAGE_PID=$!
        print "image_pid=$IMAGE_PID" >> "$OUT/driver.log"
    fi
    local game_pid
    if [[ "$name" == silent ]]; then game_pid="$SILENT_PID"; else game_pid="$IMAGE_PID"; fi
    (
        local previous=0
        local at
        for at in 6 11 16 21 26 31 36 41 46 51 56; do
            sleep "$((at - previous))"
            previous=$at
            kill -0 "$game_pid" 2>/dev/null || exit 0
            "$BUILD/winctl" activate "$game_pid" >/dev/null 2>&1 || true
            /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $game_pid to true" >/dev/null 2>&1 || true
            "$BUILD/winctl" key "$game_pid" 36 >/dev/null 2>&1 || true
        done
    ) &
}

wait_for_hangar() {
    local name="$1"
    local pid="$2"
    local deadline=$((SECONDS + 220))
    while (( SECONDS < deadline )); do
        if grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/$name.log"; then
            print "${name}_hangar=observed" | tee -a "$OUT/driver.log"
            return 0
        fi
        if ! kill -0 "$pid" 2>/dev/null; then
            wait "$pid" 2>/dev/null
            print "${name}_died_before_hangar" | tee -a "$OUT/driver.log"
            return 1
        fi
        sleep 1
    done
    print "${name}_hangar=timeout; SIGKILL" | tee -a "$OUT/driver.log"
    kill -9 "$pid" 2>/dev/null
    wait "$pid" 2>/dev/null
    return 1
}

print "arms_staged=concurrent_silent_and_image; retaining_90s_after_launch" >> "$OUT/driver.log"
launch_arm silent 0
launch_arm image 1
sleep 90
print "pair_window=complete; SIGKILL" | tee -a "$OUT/driver.log"
for pid in "$SILENT_PID" "$IMAGE_PID"; do
    if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null
    fi
done
wait "$SILENT_PID" 2>/dev/null
silent_rc=$?
wait "$IMAGE_PID" 2>/dev/null
image_rc=$?

if kill -0 "$ORACLE_PID" 2>/dev/null; then
    kill -9 "$ORACLE_PID" 2>/dev/null
    oracle_killed=1
else
    oracle_killed=0
fi
wait "$ORACLE_PID" 2>/dev/null
oracle_rc=$?
print "oracle_rc=$oracle_rc oracle_killed=$oracle_killed silent_rc=$silent_rc image_rc=$image_rc" >> "$OUT/driver.log"

print -- "--- retail controls ---" >> "$OUT/driver.log"
grep -a -E 'positive-control threshold|watch write|origin=0x00790400 width=1024|origin=0x006ab400 width=512|\[oracle\] done' "$OUT/oracle.log" | tail -20 >> "$OUT/driver.log" || true

emit_arm_summary() {
    local name="$1"
    local log="$OUT/$name.log"
    print -- "--- $name ---" >> "$OUT/driver.log"
    for marker in \
        '[audtask-dispatch]' '[audtask-abi]' '[audtask-dma-row]' '[audtask-dma-range]' \
        '[audtask-image-stage]' '[audio-return]' '[audio-route]' '[audio-sp-route]' \
        '[m5-gate]' '[slot-alloc]' '[slot-sb]' '[init-desc]' '[filter-voice-audit]' \
        '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[m5-b40-route-control]' \
        '[m5-route-state-control]' '[missing-func]' '[CRASH]' '[ABORT]'; do
        print "$marker=$(grep -a -F -c "$marker" "$log" || true)" >> "$OUT/driver.log"
    done
    print "title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" || true)" >> "$OUT/driver.log"
    print "hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" || true)" >> "$OUT/driver.log"
    print -- "rows_tail:" >> "$OUT/driver.log"
    grep -a -E '^\[(audtask-abi|audtask-dma-row|audtask-dma-range|audtask-image-stage|audio-return|audio-route|audio-sp-route|m5-gate|slot-alloc|slot-sb|init-desc|filter-voice-audit|pcm-boundary-source|pcm-boundary-consumer|m5-b40-route|m5-route-state|phase)\]' "$log" | tail -12 >> "$OUT/driver.log" || true
    print -- "terminal:" >> "$OUT/driver.log"
    grep -a -E '^\[(CRASH|ABORT|last-guest-pc|pc-symbol|phase)\]' "$log" | tail -8 >> "$OUT/driver.log" || true
}

emit_arm_summary silent
emit_arm_summary image

exit 0
