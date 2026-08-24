#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s2297_m5_target_only_writer_sequence"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" || ! -f "$ORACLE_VIDEO" ]]; then
    print "ERROR: retail oracle prerequisites are missing" > "$OUT/driver.log"
    exit 2
fi

cd "$ROOT" || exit 3

PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
RING_SPECS=(
    0x166450:0x166750
    0x166750:0x166A50
    0x166A50:0x166D50
    0x166D50:0x167050
    0x167050:0x167350
    0x167350:0x167650
    0x167650:0x167950
    0x167950:0x167C50
    0x167C50:0x167F50
    0x167F50:0x168250
    0x168250:0x168550
    0x168550:0x168850
    0x168850:0x168B50
    0x168B50:0x168E50
    0x168E50:0x169150
    0x169150:0x169450
)

ORACLE_ARGS=(
    --core "$ORACLE_CORE"
    --rom "$ORACLE_ROM"
    --video "$ORACLE_VIDEO"
    --secs 120
    --watch-write 0x0:0x800000
    --watch-write 0x166000:0x16A000
    --watch-write 0x141AD0:0x141AF0
)
for spec in $RING_SPECS; do
    ORACLE_ARGS+=(--watch-write "$spec")
done
ORACLE_ARGS+=(
    --hit-cap 200
    --watch-pc 0x800078EC
    --pc-phase-log-width 0x006AB400:512
    --pc-hist-phase 0x006AB400:512
    --pc-hist-watch 2
    --post-value-watch 2
    --post-value-pc 0x8008EB8C,0x8008EBBC,0x80094648
    --vi-trace
    --press "$PRESS"
)

ORACLE_PID=""
trap '
    if [[ -n "$ORACLE_PID" && "$ORACLE_PID" != 0 ]] && kill -0 "$ORACLE_PID" 2>/dev/null; then
        kill -9 "$ORACLE_PID" 2>/dev/null || true
    fi
' EXIT INT TERM

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" ${=ORACLE_ARGS} > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
print "oracle_pid=$ORACLE_PID" >> "$OUT/driver.log"

deadline=$((SECONDS + 150))
while (( SECONDS < deadline )); do
    if ! kill -0 "$ORACLE_PID" 2>/dev/null; then
        break
    fi
    sleep 1
done

if kill -0 "$ORACLE_PID" 2>/dev/null; then
    print "oracle_watchdog=SIGKILL" | tee -a "$OUT/driver.log"
    kill -9 "$ORACLE_PID" 2>/dev/null || true
fi
wait "$ORACLE_PID" 2>/dev/null
oracle_rc=$?
print "oracle_rc=$oracle_rc" >> "$OUT/driver.log"

print -- "--- retail controls ---" >> "$OUT/driver.log"
grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|\[oracle\] done' "$OUT/oracle.log" | tail -40 >> "$OUT/driver.log" || true
print -- "--- target-only controls and watched execution ---" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] (pc-hist-phase|pc-phase|watch-pc|post-value-pc|exec-prev|done)' "$OUT/oracle.log" | tail -300 >> "$OUT/driver.log" || true
print -- "--- task/output lifetime writer histogram ---" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] writer-pc watch=2|^\[oracle\] writer-pc pc=' "$OUT/oracle.log" | tail -300 >> "$OUT/driver.log" || true
print -- "--- task/output target-phase writer histogram ---" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] writer-pc-phase origin=0x006ab400 width=512 watch=2' "$OUT/oracle.log" | tail -300 >> "$OUT/driver.log" || true
print -- "--- target-only post-value rows ---" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] (post-value watch=2|post-value-pc watch=2|post-value snapshot watch=2|post-target-)' "$OUT/oracle.log" | tail -300 >> "$OUT/driver.log" || true

control_ok=0
if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && \
    grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" && \
    grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
    control_ok=1
fi

target_phase_rows=$(grep -a -E -c '^\[oracle\] pc-hist-phase origin=0x006ab400 width=512 vi=[1-9][0-9]*$' "$OUT/oracle.log" || true)
target_rows_for_pc() {
    grep -a -E "^\[oracle\] post-target-row-final pc=$1 .* width=512 origin=0x006ab400 " "$OUT/oracle.log" \
        | grep -avi 'value=0x7f7f7f7f' | wc -l | tr -d ' '
}
pc_eb8c_rows=$(target_rows_for_pc 0x8008eb8c)
pc_ebbc_rows=$(target_rows_for_pc 0x8008ebbc)
pc_94648_rows=$(target_rows_for_pc 0x80094648)

print -- "--- target-only post-target-row-final table (non-sentinel) ---" | tee -a "$OUT/driver.log"
for pc in 0x8008eb8c 0x8008ebbc 0x80094648; do
    grep -a -E "^\[oracle\] post-target-row-final pc=$pc .* width=512 origin=0x006ab400 " "$OUT/oracle.log" \
        | grep -avi 'value=0x7f7f7f7f' | head -16 | tee -a "$OUT/driver.log" || true
done
print "discriminator controls=$control_ok target_phase_rows=$target_phase_rows rows_eb8c=$pc_eb8c_rows rows_ebbc=$pc_ebbc_rows rows_94648=$pc_94648_rows" | tee -a "$OUT/driver.log"

if (( control_ok == 0 || target_phase_rows == 0 )); then
    print "verdict=H-CoverageInvalid" | tee -a "$OUT/driver.log"
elif (( pc_94648_rows == 0 && pc_eb8c_rows > 0 && pc_ebbc_rows > 0 )); then
    print "verdict=H-SharedConstruction" | tee -a "$OUT/driver.log"
elif (( pc_94648_rows > 0 && pc_eb8c_rows > 0 && pc_ebbc_rows > 0 )); then
    print "verdict=H-94648Distinct-or-shared; inspect target-only tuple order" | tee -a "$OUT/driver.log"
elif (( pc_94648_rows == 0 && ((pc_eb8c_rows > 0) != (pc_ebbc_rows > 0)) )); then
    print "verdict=H-EB8COrEBBCHousekeeping" | tee -a "$OUT/driver.log"
else
    print "verdict=H-TargetRowsInsufficient" | tee -a "$OUT/driver.log"
fi
exit 0
