#!/bin/zsh
set -u

ROOT=${0:A:h:h}
OUT="$ROOT/scratch/agent/m5_yield_ab"
BUILD="$ROOT/build"
mkdir -p "$OUT"
rm -f "$OUT/default.log" "$OUT/rollback.log" "$OUT/driver.log"

COMMON=(
    ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
    ROGUESQ_AUTOPILOT_STOP_WIDTH=512
    ROGUESQ_LLE_FORCE=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_M5_POSTWAIT=1
    ROGUESQ_LOG_SUBMIT_GATE_STORES=1
    ROGUESQ_LOG_EVENT_WIRING=1
    ROGUESQ_LOG_SP_YIELDED_AB=1
    ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1
    ROGUESQ_LOG_M5_GATE_CONTRACT=1
    ROGUESQ_LOG_M5_WAIT_CONTRACT=1
    ROGUESQ_LOG_WAITMUSYX_SPIN2=1
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

DEFAULT_PID=$(launch default ROGUESQ_AUDIO_UCODE=1 ROGUESQ_AUDIO_SPIN2_YIELD=1)
ROLLBACK_PID=$(launch rollback ROGUESQ_AUDIO_UCODE=1 ROGUESQ_AUDIO_SPIN2_YIELD=0)
print "default_pid=$DEFAULT_PID rollback_pid=$ROLLBACK_PID" > "$OUT/driver.log"

cleanup() {
    kill -9 "$DEFAULT_PID" "$ROLLBACK_PID" 2>/dev/null || true
    wait "$DEFAULT_PID" 2>/dev/null || true
    wait "$ROLLBACK_PID" 2>/dev/null || true
}
trap cleanup EXIT INT HUP TERM

has() {
    grep -a -q "$2" "$1"
}

target_gate() {
    has "$1" 'vi_width=1024 .*origin=0x00790400' &&
    has "$1" 'vi_width=512 .*origin=0x006AB400' &&
    has "$1" 'complete kind=SP'
}

gated=0
for i in {1..480}; do
    if target_gate "$OUT/default.log" && target_gate "$OUT/rollback.log"; then
        gated=1
        break
    fi
    kill -0 "$DEFAULT_PID" 2>/dev/null || break
    kill -0 "$ROLLBACK_PID" 2>/dev/null || break
    sleep 0.25
done
print "gate=$gated" >> "$OUT/driver.log"

cleanup
trap - EXIT INT HUP TERM

count() { grep -a -F -c "$2" "$1" 2>/dev/null || true; }
max_n() {
    grep -a -F "$2" "$1" 2>/dev/null |
        sed -n 's/.* n=\([0-9][0-9]*\).*/\1/p' | sort -n | tail -1
}

for arm in default rollback; do
    log="$OUT/$arm.log"
    print -r -- "--- $arm ---" >> "$OUT/driver.log"
    print "arm_rows=$(count "$log" '[sp-yielded-ab]') reset_rows=$(count "$log" '[sp-yield-reset]')" >> "$OUT/driver.log"
    print "phase_640=$(count "$log" 'vi_width=640 (was') title_1024=$(count "$log" 'vi_width=1024 (was') hangar_512=$(count "$log" 'vi_width=512 (was')" >> "$OUT/driver.log"
    print "viewer_entry=$(count "$log" 'edge=entry site=runMenuModelViewerScreen') viewer_return=$(count "$log" 'edge=return site=runMenuModelViewerScreen') sp_complete=$(count "$log" '[event-wiring] complete kind=SP')" >> "$OUT/driver.log"
    print "audio_return=$(count "$log" '[audio-return]') pcm_source=$(count "$log" '[pcm-boundary-source]') pcm_consumer=$(count "$log" '[pcm-boundary-consumer]') task_contract=$(count "$log" '[m5-task-contract]')" >> "$OUT/driver.log"
    print "gate_rows=$(count "$log" '[m5-gate]') producer_arm=$(count "$log" '[waitmusyx-spin2-arm]') producer_clear=$(count "$log" '[waitmusyx-spin2-clear]') wait_loop=$(count "$log" '[waitmusyx-spin2-loop]') wait_return=$(grep -a -F '[waitmusyx-spin2-loop]' "$log" | grep -a -F -c 'event=return' || true) spin_yield=$(grep -a -F '[waitmusyx-spin2-loop]' "$log" | grep -a -F -c 'yields=' || true)" >> "$OUT/driver.log"
    print "crash=$(count "$log" '[CRASH]') abort=$(count "$log" '[ABORT]')" >> "$OUT/driver.log"
done

if (( gated == 0 )); then
    print 'verdict=H-route-invalid' >> "$OUT/driver.log"
    exit 5
fi
default_pcm=$(count "$OUT/default.log" '[pcm-boundary-source]')
rollback_pcm=$(count "$OUT/rollback.log" '[pcm-boundary-source]')
default_pcm_nz=$(grep -a -E '\[pcm-boundary-source\].*nz=[1-9][0-9]*' "$OUT/default.log" | wc -l | tr -d ' ')
rollback_pcm_nz=$(grep -a -E '\[pcm-boundary-source\].*nz=[1-9][0-9]*' "$OUT/rollback.log" | wc -l | tr -d ' ')
print "pcm_source_rows=$default_pcm/$rollback_pcm pcm_nonzero_rows=$default_pcm_nz/$rollback_pcm_nz" >> "$OUT/driver.log"
default_witness=$(grep -a -E 'waitmusyx-spin2-(arm|clear)|waitmusyx-spin2-loop.*event=return' "$OUT/default.log" | wc -l | tr -d ' ')
rollback_witness=$(grep -a -E 'waitmusyx-spin2-(arm|clear)|waitmusyx-spin2-loop.*event=return' "$OUT/rollback.log" | wc -l | tr -d ' ')
print "producer_wait_witness=$default_witness/$rollback_witness" >> "$OUT/driver.log"
if (( default_witness > 0 && rollback_witness == 0 )); then
    print 'verdict=H-yield-causal' >> "$OUT/driver.log"
elif (( default_witness > 0 && rollback_witness > 0 )); then
    print 'verdict=H-producer-clear' >> "$OUT/driver.log"
else
    print 'verdict=H-route-invalid' >> "$OUT/driver.log"
fi
exit 0
