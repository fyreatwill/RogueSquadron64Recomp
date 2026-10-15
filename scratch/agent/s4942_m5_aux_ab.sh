#!/bin/zsh
set -u

ROOT=${0:A:h:h:h}
OUT="$ROOT/scratch/agent/s4942_m5_aux_ab"
BUILD="$ROOT/build"
mkdir -p "$OUT"
rm -f "$OUT/image.log" "$OUT/silent.log" "$OUT/driver.log"

COMMON=(
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_EVENT_WIRING=1
    ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1
    ROGUESQ_LOG_M5_GATE_CONTRACT=1
    ROGUESQ_LOG_M5_WAIT_CONTRACT=1
    ROGUESQ_LOG_S4938_AUX_JOIN=1
)

launch() {
    local name=$1
    shift
    (
        cd "$BUILD" || exit 2
        exec env "${COMMON[@]}" "$@" ./RogueSquadron64Recomp
    ) > "$OUT/$name.log" 2>&1 &
    print $!
}

IMAGE_PID=$(launch image ROGUESQ_AUDIO_UCODE=1)
SILENT_PID=$(launch silent ROGUESQ_AUDIO_UCODE=0)
print "image_pid=$IMAGE_PID silent_pid=$SILENT_PID" > "$OUT/driver.log"

cleanup() {
    kill -9 "$IMAGE_PID" "$SILENT_PID" 2>/dev/null || true
    wait "$IMAGE_PID" 2>/dev/null || true
    wait "$SILENT_PID" 2>/dev/null || true
}
trap cleanup EXIT INT HUP TERM

has() { grep -a -q "$2" "$1"; }
target_gate() {
    has "$1" 'vi_width=1024 .*origin=0x00790400' &&
    has "$1" 'vi_width=512 .*origin=0x006AB400' &&
    has "$1" 'complete kind=SP'
}

image_wid=""
silent_wid=""
for i in {1..120}; do
    [[ -z "$image_wid" ]] && image_wid=$("$BUILD/winctl" find "$IMAGE_PID" 2>/dev/null | awk 'NR==1{print $1}')
    [[ -z "$silent_wid" ]] && silent_wid=$("$BUILD/winctl" find "$SILENT_PID" 2>/dev/null | awk 'NR==1{print $1}')
    [[ -n "$image_wid" && -n "$silent_wid" ]] && break
    sleep 0.25
done
print "image_wid=$image_wid silent_wid=$silent_wid" >> "$OUT/driver.log"

press() {
    local pid=$1
    local key=$2
    "$BUILD/winctl" activate "$pid" >/dev/null 2>&1 || true
    "$BUILD/winctl" key "$pid" "$key" 250 >/dev/null 2>&1 || true
}

gated=0
for i in {1..480}; do
    if target_gate "$OUT/image.log" && target_gate "$OUT/silent.log"; then
        gated=1
        break
    fi
    kill -0 "$IMAGE_PID" 2>/dev/null || break
    kill -0 "$SILENT_PID" 2>/dev/null || break
    sleep 0.25
done

if (( gated == 0 )); then
    # The qualified route reaches hangar without input; if it stops at the
    # menu, use the same verified Start/A sequence for both arms.
    for n in {1..4}; do
        press "$IMAGE_PID" 36
        press "$SILENT_PID" 36
        sleep 2
        press "$IMAGE_PID" 6
        press "$SILENT_PID" 6
        sleep 2
    done
    for i in {1..240}; do
        if target_gate "$OUT/image.log" && target_gate "$OUT/silent.log"; then
            gated=1
            break
        fi
        sleep 0.25
    done
fi
print "gate=$gated" >> "$OUT/driver.log"

cleanup
trap - EXIT

count() { grep -a -F -c "$2" "$1" 2>/dev/null || true; }
for arm in image silent; do
    log="$OUT/$arm.log"
    print -- "--- $arm ---" >> "$OUT/driver.log"
    print "title=$(count "$log" 'vi_width=1024 (was') hangar=$(count "$log" 'vi_width=512 (was') sp_complete=$(count "$log" '[event-wiring] complete kind=SP')" >> "$OUT/driver.log"
    print "dispatch=$(count "$log" '[audtask-dispatch]') task_contract=$(count "$log" '[m5-task-contract]') aux_store=$(count "$log" '[s4938-aux-store]') pcm_source=$(count "$log" '[pcm-boundary-source]') pcm_consumer=$(count "$log" '[pcm-boundary-consumer]')" >> "$OUT/driver.log"
    print "crash=$(count "$log" '[CRASH]') abort=$(count "$log" '[ABORT]')" >> "$OUT/driver.log"
done

if (( gated == 0 )); then
    print 'verdict=H-route-invalid' >> "$OUT/driver.log"
    exit 5
fi

image_aux=$(count "$OUT/image.log" '[s4938-aux-store]')
silent_aux=$(count "$OUT/silent.log" '[s4938-aux-store]')
image_pcm=$(grep -a -E '\[pcm-boundary-source\].*nz=[1-9][0-9]*' "$OUT/image.log" | wc -l | tr -d ' ')
silent_pcm=$(grep -a -E '\[pcm-boundary-source\].*nz=[1-9][0-9]*' "$OUT/silent.log" | wc -l | tr -d ' ')
print "aux_rows=$image_aux/$silent_aux pcm_nonzero_rows=$image_pcm/$silent_pcm" >> "$OUT/driver.log"
if (( image_aux > 0 && silent_aux == 0 && image_pcm > 0 )); then
    print 'verdict=H-contract-gap' >> "$OUT/driver.log"
elif (( image_aux > 0 && silent_aux > 0 )); then
    print 'verdict=H-route-only-or-rollback-specific' >> "$OUT/driver.log"
else
    print 'verdict=H-unevaluable-aux-control' >> "$OUT/driver.log"
fi
exit 0
