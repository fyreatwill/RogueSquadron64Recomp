#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2317_m5_gate_task_wait_explicit_pair}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
WINCTL="$BUILD/winctl"
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" || ! -f "$ORACLE_VIDEO" ]]; then
    print "ERROR: retail oracle prerequisites are missing" > "$OUT/driver.log"
    exit 2
fi
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" || ! -x "$WINCTL" ]]; then
    print "ERROR: build/ control prerequisites are missing" > "$OUT/driver.log"
    exit 3
fi

cd "$ROOT" || exit 4

PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
PORT_PRESS=(6 11 16 21 26 31 36 41 46 51 56)
COMMON=(
    ROGUESQ_LLE_FORCE=1
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_M5_C88_VALUE=0
    ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_VI_CALLERS=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1
    ROGUESQ_LOG_M5_GATE_CONTRACT=1
    ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
    ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1
    PROBE_PHASE_WIDTH=1024
    PROBE_KEYS_FROM_PHASE=1
)

ORACLE_PID=""
STUB_PID=""
IMAGE_PID=""
STUB_KEYPID=""
IMAGE_KEYPID=""
trap '
    for pid in "$STUB_KEYPID" "$IMAGE_KEYPID" "$STUB_PID" "$IMAGE_PID" "$ORACLE_PID"; do
        if [[ -n "$pid" && "$pid" != 0 ]] && kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
        fi
    done
' EXIT INT TERM

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" \
    --core "$ORACLE_CORE" \
    --rom "$ORACLE_ROM" \
    --video "$ORACLE_VIDEO" \
    --secs 120 \
    --watch-write 0x0:0x800000 \
    --watch-write 0xA0F50:0xA0F54 \
    --watch-write 0x141AD0:0x141AF0 \
    --watch-write 0x1498A:0x1498B \
    --watch-write 0x154620:0x154621 \
    --watch-write 0x155848:0x155849 \
    --watch-write 0x156A70:0x156A71 \
    --watch-write 0x157C98:0x157C99 \
    --watch-write 0x158EC0:0x158EC1 \
    --first-watch 1 --first-watch 2 --first-watch 3 --first-watch 4 \
    --first-watch 5 --first-watch 6 --first-watch 7 --first-watch 8 \
    --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 \
    --pc-hist-watch 5 --pc-hist-watch 6 --pc-hist-watch 7 --pc-hist-watch 8 \
    --pc-hist-phase 0x00790400:1024 \
    --pc-hist-phase 0x006AB400:512 \
    --pc-hist-phase 0x006AB800:512 \
    --pc-hist-phase 0x00656400:512 \
    --pc-hist-phase 0x00656800:512 \
    --pc-hist-phase 0x0066A500:640 \
    --pc-hist-phase 0x00696100:640 \
    --pc-hist-phase 0x0066AA00:640 \
    --pc-hist-phase 0x00696600:640 \
    --pc-hist-phase 0x00000280:320 \
    --pc-hist-phase 0x006BA280:320 \
    --pc-hist-phase 0x005D4500:640 \
    --pc-hist-phase 0x0062C200:640 \
    --pc-hist-phase 0x0062BD00:640 \
    --pc-hist-phase 0x00790800:1024 \
    --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 \
    --post-value-watch 4 --post-value-watch 5 --post-value-watch 6 \
    --post-value-watch 7 --post-value-watch 8 \
    --post-value-pc 0x8009BBF0,0x8009B170,0x8009B174,0x8009B178,0x8009B214,0x8009B6F8,0x8009B7CC,0x8009B7EC,0x8009B2C4,0x800292E4,0x800298E0,0x80017DB0,0x80015BC8,0x80022B1C \
    --post-value-pc-detail \
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
        print "oracle_gate=passed whole_rdram=10000 title=1 hangar=1" | tee -a "$OUT/driver.log"
        break
    fi
    if ! kill -0 "$ORACLE_PID" 2>/dev/null; then
        print "oracle_gate=failed oracle_exited" | tee -a "$OUT/driver.log"
        break
    fi
    sleep 1
done

if (( oracle_gate == 0 )); then
    print "verdict=H-CoverageInvalid oracle_gate=failed" | tee -a "$OUT/driver.log"
    exit 5
fi

raise_game() {
    local pid="$1"
    "$WINCTL" activate "$pid" >/dev/null 2>&1 || true
    /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $pid to true" >/dev/null 2>&1 || true
}

start_port_keys() {
    local name="$1"
    local pid="$2"
    print "port_input=$name phase=process-start schedule=eleven-start keycode=36" >> "$OUT/driver.log"
    local previous=0
    for at in $PORT_PRESS; do
        sleep "$((at - previous))"
        previous=$at
        if ! kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
        raise_game "$pid"
        "$WINCTL" key "$pid" 36 >/dev/null 2>&1 || true
        print "port_input=$name start_at_process_s=$at keycode=36" >> "$OUT/driver.log"
    done
}

wait_for_window() {
    local pid="$1"
    local deadline=$((SECONDS + 30))
    local wid=""
    while (( SECONDS < deadline )); do
        if ! kill -0 "$pid" 2>/dev/null; then
            return 1
        fi
        wid=$("$WINCTL" find "$pid" 2>/dev/null || true)
        if [[ -n "$wid" ]]; then
            print "window pid=$pid id=${wid%% *}" >> "$OUT/driver.log"
            return 0
        fi
        sleep 1
    done
    return 1
}

launch_port() {
    local name="$1"
    local audio_arm="$2"
    (
        cd "$BUILD" || exit 2
        if [[ "$audio_arm" == stub ]]; then
            exec env ${=COMMON} ROGUESQ_AUDIO_UCODE=0 ./RogueSquadron64Recomp
        else
            exec env ${=COMMON} ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp
        fi
    ) > "$OUT/$name.log" 2>&1 &
    local pid=$!
    if [[ "$name" == stub ]]; then
        STUB_PID=$pid
    else
        IMAGE_PID=$pid
    fi
    print "${name}_pid=$pid" | tee -a "$OUT/driver.log"
    if ! wait_for_window "$pid"; then
        print "${name}_window=missing" | tee -a "$OUT/driver.log"
        return 1
    fi
    start_port_keys "$name" "$pid" &
    if [[ "$name" == stub ]]; then
        STUB_KEYPID=$!
    else
        IMAGE_KEYPID=$!
    fi
    return 0
}

wait_for_hangar() {
    local name="$1"
    local pid="$2"
    local deadline=$((SECONDS + 240))
    while (( SECONDS < deadline )); do
        if grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/$name.log"; then
            print "${name}_hangar=observed" | tee -a "$OUT/driver.log"
            return 0
        fi
        if ! kill -0 "$pid" 2>/dev/null; then
            print "${name}_died_before_hangar" | tee -a "$OUT/driver.log"
            return 1
        fi
        sleep 1
    done
    print "${name}_hangar=timeout; SIGKILL" | tee -a "$OUT/driver.log"
    kill -9 "$pid" 2>/dev/null || true
    return 1
}

print "arms_staged=stub_then_image_after_stub_hangar" >> "$OUT/driver.log"
stub_gate=0
if launch_port stub stub && wait_for_hangar stub "$STUB_PID"; then
    stub_gate=1
else
    print "verdict=H-CoverageInvalid stub_hangar_missing; image_not_launched" | tee -a "$OUT/driver.log"
fi

image_target=0
if (( stub_gate == 1 )); then
    print "pair_gate=passed stub_hangar=1; launching_image" | tee -a "$OUT/driver.log"
    if launch_port image image; then
        image_deadline=$((SECONDS + 240))
        while (( SECONDS < image_deadline )); do
            if grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/image.log"; then
                image_target=1
                print "image_hangar=observed; retaining_15s" | tee -a "$OUT/driver.log"
                sleep 15
                break
            fi
            if ! kill -0 "$IMAGE_PID" 2>/dev/null; then
                print "image_died_before_hangar" | tee -a "$OUT/driver.log"
                break
            fi
            sleep 1
        done
        if (( image_target == 0 )); then
            print "image_hangar=timeout_or_exit; SIGKILL" | tee -a "$OUT/driver.log"
        fi
    else
        print "image_launch=failed" | tee -a "$OUT/driver.log"
    fi
fi

for pid in "$STUB_KEYPID" "$IMAGE_KEYPID" "$STUB_PID" "$IMAGE_PID"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
    fi
done
wait "$STUB_KEYPID" 2>/dev/null || true
wait "$IMAGE_KEYPID" 2>/dev/null || true
wait "$STUB_PID" 2>/dev/null
stub_rc=$?
wait "$IMAGE_PID" 2>/dev/null
image_rc=$?

oracle_killed=0
oracle_wait_deadline=$((SECONDS + 100))
while (( SECONDS < oracle_wait_deadline )) && kill -0 "$ORACLE_PID" 2>/dev/null; do
    sleep 1
done
if kill -0 "$ORACLE_PID" 2>/dev/null; then
    kill -9 "$ORACLE_PID" 2>/dev/null || true
    oracle_killed=1
fi
wait "$ORACLE_PID" 2>/dev/null
oracle_rc=$?
print "oracle_rc=$oracle_rc oracle_killed=$oracle_killed stub_rc=$stub_rc image_rc=$image_rc stub_gate=$stub_gate image_target=$image_target" >> "$OUT/driver.log"

print -- "--- retail controls ---" >> "$OUT/driver.log"
grep -a -E 'positive-control threshold|watch write|origin=0x00790400 width=1024|origin=0x006ab400 width=512|first-watch|pc-hist|post-value|\[oracle\] done' "$OUT/oracle.log" | tail -40 >> "$OUT/driver.log" || true

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
        print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    done
    print "title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print -- "rows_tail:" >> "$OUT/driver.log"
    grep -a -E '^\[(audtask-abi|audtask-dma-row|audtask-dma-range|audtask-image-stage|audio-return|audio-route|audio-sp-route|m5-gate|slot-alloc|slot-sb|init-desc|filter-voice-audit|pcm-boundary-source|pcm-boundary-consumer|m5-b40-route|m5-route-state|phase)\]' "$log" | tail -12 >> "$OUT/driver.log" || true
    print -- "terminal:" >> "$OUT/driver.log"
    grep -a -E '^\[(CRASH|ABORT|last-guest-pc|pc-symbol|phase)\]' "$log" | tail -8 >> "$OUT/driver.log" || true
}

[[ -f "$OUT/stub.log" ]] && emit_arm_summary stub
[[ -f "$OUT/image.log" ]] && emit_arm_summary image

if (( stub_gate == 0 || image_target == 0 )); then
    exit 6
fi
exit 0
