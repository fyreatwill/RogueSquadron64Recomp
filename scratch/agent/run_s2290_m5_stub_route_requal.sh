#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2290_m5_stub_route_requal"
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
    ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1
    ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_GATE_CONTRACT=1
    ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
    ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1
)

ORACLE_PID=""
STUB_PID=""
DEFAULT_PID=""
STUB_KEYPID=""
DEFAULT_KEYPID=""
trap '
    for pid in "$STUB_KEYPID" "$DEFAULT_KEYPID" "$STUB_PID" "$DEFAULT_PID" "$ORACLE_PID"; do
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
    --secs 500 \
    --watch-write 0x0:0x800000 \
    --watch-pc 0x8003E8DC,0x8003EA4C,0x800A70E4,0x800653B4,0x80007904 \
    --pc-phase-log-width 0x00696100:640 \
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
    print "verdict=H-RouteControlInvalid oracle_gate=failed" | tee -a "$OUT/driver.log"
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
    local log="$OUT/$name.log"
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
            exec env ${=COMMON} ./RogueSquadron64Recomp
        fi
    ) > "$OUT/$name.log" 2>&1 &
    local pid=$!
    if [[ "$name" == stub ]]; then
        STUB_PID=$pid
    else
        DEFAULT_PID=$pid
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
        DEFAULT_KEYPID=$!
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

print "arms_staged=stub_then_default_after_stub_hangar" >> "$OUT/driver.log"
stub_gate=0
if launch_port stub stub && wait_for_hangar stub "$STUB_PID"; then
    stub_gate=1
else
    print "verdict=H-PortCallbackStateGap stub_hangar_missing; default_not_launched" | tee -a "$OUT/driver.log"
fi

default_target=0
if (( stub_gate == 1 )); then
    print "pair_gate=passed stub_hangar=1; launching_default" | tee -a "$OUT/driver.log"
    if launch_port default default; then
        pair_deadline=$((SECONDS + 240))
        while (( SECONDS < pair_deadline )); do
            if grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/default.log"; then
                default_target=1
                print "default_hangar=observed; retaining_15s" | tee -a "$OUT/driver.log"
                sleep 15
                break
            fi
            if ! kill -0 "$DEFAULT_PID" 2>/dev/null; then
                print "default_died_before_hangar" | tee -a "$OUT/driver.log"
                break
            fi
            sleep 1
        done
        if (( default_target == 0 )); then
            print "default_hangar=timeout_or_exit; SIGKILL" | tee -a "$OUT/driver.log"
        fi
    else
        print "default_launch=failed" | tee -a "$OUT/driver.log"
    fi
fi

for pid in "$STUB_KEYPID" "$DEFAULT_KEYPID" "$STUB_PID" "$DEFAULT_PID" "$ORACLE_PID"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
    fi
done
wait "$STUB_KEYPID" 2>/dev/null || true
wait "$DEFAULT_KEYPID" 2>/dev/null || true
wait "$STUB_PID" 2>/dev/null
stub_rc=$?
wait "$DEFAULT_PID" 2>/dev/null
default_rc=$?
wait "$ORACLE_PID" 2>/dev/null
oracle_rc=$?
print "oracle_rc=$oracle_rc stub_rc=$stub_rc default_rc=$default_rc stub_gate=$stub_gate default_target=$default_target" >> "$OUT/driver.log"

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
        print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    done
    local title_count=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" 2>/dev/null || true)
    local hangar_count=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" 2>/dev/null || true)
    print "title=$title_count" >> "$OUT/driver.log"
    print "hangar=$hangar_count" >> "$OUT/driver.log"
    print -- "rows_tail:" >> "$OUT/driver.log"
    grep -a -E '^\[(audtask-abi|audtask-dma-row|audtask-dma-range|audtask-image-stage|audio-return|audio-route|audio-sp-route|m5-gate|slot-alloc|slot-sb|init-desc|filter-voice-audit|pcm-boundary-source|pcm-boundary-consumer|m5-b40-route|m5-route-state|phase)\]' "$log" | tail -12 >> "$OUT/driver.log" || true
    print -- "terminal:" >> "$OUT/driver.log"
    grep -a -E '^\[(CRASH|ABORT|last-guest-pc|pc-symbol|phase)\]' "$log" | tail -8 >> "$OUT/driver.log" || true
}

if [[ -f "$OUT/stub.log" ]]; then
    emit_arm_summary stub
fi
if [[ -f "$OUT/default.log" ]]; then
    emit_arm_summary default
fi

if (( stub_gate == 0 )); then
    exit 6
fi
if (( default_target == 0 )); then
    exit 7
fi
exit 0
