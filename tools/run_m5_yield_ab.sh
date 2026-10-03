#!/bin/zsh
set -u

ROOT=${0:A:h:h}
OUT="$ROOT/scratch/agent/m5_yield_ab"
BUILD="$ROOT/build"
mkdir -p "$OUT"
rm -f "$OUT/default.log" "$OUT/request-only.log" "$OUT/driver.log"

COMMON=(
    ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_M5_POSTWAIT=1
    ROGUESQ_LOG_SUBMIT_GATE_STORES=1
    ROGUESQ_LOG_EVENT_WIRING=1
    ROGUESQ_LOG_SP_YIELDED_AB=1
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

DEFAULT_PID=$(launch default)
REQUEST_PID=$(launch request-only ROGUESQ_SP_YIELDED_REQUEST_ONLY=1)
print "default_pid=$DEFAULT_PID request_only_pid=$REQUEST_PID" > "$OUT/driver.log"

cleanup() {
    kill -9 "$DEFAULT_PID" "$REQUEST_PID" 2>/dev/null || true
    wait "$DEFAULT_PID" 2>/dev/null || true
    wait "$REQUEST_PID" 2>/dev/null || true
}
trap cleanup EXIT INT HUP TERM

has() {
    grep -a -q "$2" "$1"
}

default_gate() {
    has "$OUT/default.log" 'arm=completion-wins-default' &&
    has "$OUT/default.log" 'requested_pre=1 requested_post=0' &&
    has "$OUT/default.log" 'vi_width=640 .*origin=0x0066A500' &&
    has "$OUT/default.log" 'edge=entry site=runMenuModelViewerScreen' &&
    has "$OUT/default.log" 'complete kind=SP'
}

request_gate() {
    has "$OUT/request-only.log" 'arm=request-only' &&
    has "$OUT/request-only.log" 'requested=1 returned=1 pending_after=0' &&
    has "$OUT/request-only.log" 'vi_width=640 .*origin=0x0066A500' &&
    has "$OUT/request-only.log" 'edge=entry site=runMenuModelViewerScreen' &&
    has "$OUT/request-only.log" 'complete kind=SP'
}

gated=0
for i in {1..480}; do
    if default_gate && request_gate; then
        gated=1
        break
    fi
    kill -0 "$DEFAULT_PID" 2>/dev/null || break
    kill -0 "$REQUEST_PID" 2>/dev/null || break
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

for arm in default request-only; do
    log="$OUT/$arm.log"
    print -r -- "--- $arm ---" >> "$OUT/driver.log"
    print "arm_rows=$(count "$log" '[sp-yielded-ab]') reset_rows=$(count "$log" '[sp-yield-reset]') reset_pre1=$(count "$log" 'requested_pre=1 requested_post=0')" >> "$OUT/driver.log"
    print "phase_640=$(count "$log" 'vi_width=640 (was') title_1024=$(count "$log" 'vi_width=1024 (was') hangar_512=$(count "$log" 'vi_width=512 (was')" >> "$OUT/driver.log"
    print "viewer_entry=$(count "$log" 'edge=entry site=runMenuModelViewerScreen') viewer_return=$(count "$log" 'edge=return site=runMenuModelViewerScreen') sp_complete=$(count "$log" '[event-wiring] complete kind=SP')" >> "$OUT/driver.log"
    print "e60=$(count "$log" 'site=19E60-post') e70=$(count "$log" 'site=19E70-post') e80f=$(count "$log" 'site=19E80F') sent_max=$(max_n "$log" 'site=SENT') sret_max=$(max_n "$log" 'site=SRET')" >> "$OUT/driver.log"
    print "crash=$(count "$log" '[CRASH]') abort=$(count "$log" '[ABORT]')" >> "$OUT/driver.log"
done

if (( gated == 0 )); then
    print 'verdict=H-CoverageInvalid' >> "$OUT/driver.log"
    exit 5
fi

default_return=$(count "$OUT/default.log" 'arm=completion-wins-default requested=1 returned=0')
request_return=$(count "$OUT/request-only.log" 'arm=request-only requested=1 returned=1 pending_after=0')
request_reset=$(count "$OUT/request-only.log" 'requested_pre=1 requested_post=0')
default_title=$(count "$OUT/default.log" 'vi_width=1024 (was')
request_title=$(count "$OUT/request-only.log" 'vi_width=1024 (was')

default_reset=$(count "$OUT/default.log" 'requested_pre=1 requested_post=0')

if (( default_return > 0 && request_return > 0 && default_reset > 0 && default_title > 0 && request_title > 0 )); then
    print 'verdict=H-RequestOnlyOneShotNotCausal' >> "$OUT/driver.log"
    exit 0
fi
if (( default_return > 0 && request_return > 0 && default_title > 0 && request_title == 0 )); then
    print 'verdict=H-RequestOnlyLifecycleCausal' >> "$OUT/driver.log"
    exit 3
fi
print 'verdict=H-DiscriminatorIncomplete' >> "$OUT/driver.log"
exit 4
