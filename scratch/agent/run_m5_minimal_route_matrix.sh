#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s3807_m5_minimal_route_matrix"
mkdir -p "$OUT"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE="$ROOT/../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib"
ROM="$ROOT/../rogue_squadron64/rogue_squadron.z64"
VIDEO="/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib"

typeset -a ROUTE=(ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_M5_C88_VALUE=0
    ROGUESQ_STUB_MISSING_FUNCS=1 PROBE_PHASE_WIDTH=1024
    PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1)
typeset -a BASE=(ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1)

( "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 60
    --hit-cap 10000 --watch-write 0x0:0x800000 --vi-trace
    --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
    > "$OUT/oracle.log" 2>&1 ) &
ORACLE_PID=$!

run_arm() {
    local name="$1"; shift
    local dir="$OUT/$name"
    mkdir -p "$dir"
    ( cd "$BUILD" && env "${ROUTE[@]}" "$@" \
        'PROBE_KEYS=3:start 7:start 11:start 15:a 100:start' \
        zsh "$ROOT/tools/probe.sh" "$dir" 180 0.5 ) \
        > "$dir/driver.log" 2>&1
    print "$name rc=$?" >> "$OUT/summary.txt"
    for marker in \
        '\[phase\] vi_width=1024 .*origin=0x00790400' '\[phase\] vi_width=512 .*origin=0x006AB400' \
        '\[CRASH\]' '\[ABORT\]'; do
        print "$name $marker=$(grep -a -c "$marker" "$dir/run.log" 2>/dev/null || true)" >> "$OUT/summary.txt"
    done
    grep -a -E '\[phase\]|\[last-guest-pc\]|\[CRASH\]' "$dir/run.log" | tail -5 >> "$OUT/summary.txt" || true
}

run_arm minimal
run_arm current_base "${BASE[@]}"
wait "$ORACLE_PID"
print "oracle_rc=$?" >> "$OUT/summary.txt"
print "oracle_control=$(grep -a -c 'watch write \[0x00000000,0x00800000\): [1-9]' "$OUT/oracle.log" || true)" >> "$OUT/summary.txt"
print "oracle_title=$(grep -a -c '0x00790400' "$OUT/oracle.log" || true)" >> "$OUT/summary.txt"
print "oracle_hangar=$(grep -a -c '0x006ab400' "$OUT/oracle.log" || true)" >> "$OUT/summary.txt"
