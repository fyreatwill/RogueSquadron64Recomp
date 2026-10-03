#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s3806_m5_census_startup_matrix"
mkdir -p "$OUT"

ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE="$ROOT/../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib"
ORACLE_ROM="$ROOT/../rogue_squadron64/rogue_squadron.z64"
ORACLE_VIDEO="/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib"
if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" ]]; then
    print "oracle prerequisites missing" >&2
    exit 2
fi

typeset -a BASE=(
    ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_M5_C88_VALUE=0
    ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1
)
typeset -a SOURCE_INPUT=(
    ROGUESQ_LOG_M5_INPUT_WRITER=1 ROGUESQ_LOG_M5_SOURCE_PRODUCER=1
    ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_LOG_M5_SOURCE_WRITER=1
    ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_HOST_WRITE=1
    ROGUESQ_LOG_M5_TASK_WRITE_FAULT=1 ROGUESQ_LOG_M5_FIELD348_INPUT=1
    ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1
    ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
    ROGUESQ_LOG_M5_PORT_LOAD=1 ROGUESQ_LOG_M5_DESCRIPTOR=1
    ROGUESQ_LOG_M5_STAGE_BYTES=1 ROGUESQ_LOG_M5_STAGE_CALLS=1
)

oracle_log="$OUT/oracle.log"
( "$ORACLE" --core "$ORACLE_CORE" --rom "$ORACLE_ROM" \
    --video "$ORACLE_VIDEO" --secs 60 --hit-cap 10000 \
    --watch-write 0x0:0x800000 --vi-trace \
    --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
    > "$oracle_log" 2>&1 ) &
ORACLE_PID=$!

run_bundle() {
    local name="$1"
    shift
    local out="$OUT/$name"
    mkdir -p "$out"
    print "$name" >> "$OUT/driver.log"
    ( cd "$BUILD" && env "${BASE[@]}" "$@" 'PROBE_KEYS=3:start 7:start 11:start 15:a 100:start' \
        zsh "$ROOT/tools/probe.sh" "$out" 180 0.5 ) \
        > "$out/driver.log" 2>&1
    print "${name}_probe_rc=$?" >> "$OUT/driver.log"
    for marker in \
        '\[phase\] vi_width=1024 .*origin=0x00790400' '\[phase\] vi_width=512 .*origin=0x006AB400' \
        '\[m5-input-writer-control\]' '\[m5-input-writer\]' '\[m5-source-producer\]' \
        '\[m5-source-transition\]' '\[m5-input-dma\]' '\[m5-dmem-coverage\]' \
        '\[m5-source-range-writer\]' '\[CRASH\]' '\[ABORT\]'; do
        print "$marker=$(grep -a -c "$marker" "$out/run.log" 2>/dev/null || true)" >> "$OUT/driver.log"
    done
    grep -a -E '\[phase\]|\[CRASH\]|\[last-guest-pc\]' "$out/run.log" | tail -5 >> "$OUT/driver.log" || true
}

run_bundle nocensus
run_bundle source_input ${=SOURCE_INPUT}
run_bundle fullcensus ROGUESQ_LOG_ALL=1

wait "$ORACLE_PID"
print "oracle_rc=$?" >> "$OUT/driver.log"
print "oracle_control=$(grep -a -c 'watch write \[0x00000000,0x00800000\): [1-9]' "$oracle_log" || true)" >> "$OUT/driver.log"
print "oracle_title=$(grep -a -c '0x00790400' "$oracle_log" || true)" >> "$OUT/driver.log"
print "oracle_hangar=$(grep -a -c '0x006ab400' "$oracle_log" || true)" >> "$OUT/driver.log"
exit 0
