#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s2294_m5_target_slot_writer_phase"
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
for i in {3..18}; do
    ORACLE_ARGS+=(--pc-hist-watch "$i" --post-value-watch "$i")
done
ORACLE_ARGS+=(
    --hit-cap 200
    --watch-pc 0x800078EC
    --pc-phase-log-width 0x006AB400:512
    --pc-hist-phase 0x006AB400:512
    --post-value-pc 0x800078EC
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
print -- "--- target-phase watched execution ---" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] (pc-hist-phase|pc-phase|watch-pc|post-value-pc|exec-prev|done)' "$OUT/oracle.log" | tail -260 >> "$OUT/driver.log" || true
print -- "--- target-phase writer histograms ---" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] writer-pc-phase' "$OUT/oracle.log" | tail -400 >> "$OUT/driver.log" || true
print -- "--- lifetime writer and post-value summaries ---" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] (writer-pc|post-value watch=|post-value snapshot)' "$OUT/oracle.log" | tail -500 >> "$OUT/driver.log" || true

control_ok=0
if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && \
    grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" && \
    grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
    control_ok=1
fi

target_exec=$(grep -a -E -c '^\[hit\].*pc=0x800078ec.*width=512 origin=0x006ab400' "$OUT/oracle.log" || true)
target_writer_rows=$(grep -a -E -c '^\[oracle\] writer-pc-phase origin=0x006ab400 width=512 watch=(3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18) pc=0x800078ec' "$OUT/oracle.log" || true)
target_writer_any=$(grep -a -E -c '^\[oracle\] writer-pc-phase origin=0x006ab400 width=512 watch=(3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18) pc=0x[0-9a-f]+' "$OUT/oracle.log" || true)
target_post_samples=$(grep -a -E -c '^\[oracle\] post-value watch=(3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18) range=.* samples=[1-9]' "$OUT/oracle.log" || true)
target_post_pc=$(grep -a -E -c '^\[oracle\] post-value-pc watch=(3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18).*pc=0x800078ec' "$OUT/oracle.log" || true)
print "discriminator controls=$control_ok target_exec=$target_exec target_writer_078ec=$target_writer_rows target_writer_any=$target_writer_any target_post_samples=$target_post_samples target_post_pc_rows=$target_post_pc" | tee -a "$OUT/driver.log"

if (( control_ok == 0 )); then
    print "verdict=H-CoverageInvalid" | tee -a "$OUT/driver.log"
elif (( target_writer_rows > 0 )); then
    print "verdict=H-TargetWriter078EC" | tee -a "$OUT/driver.log"
elif (( target_writer_any > 0 || target_post_pc > 0 )); then
    print "verdict=H-TargetWriterOther" | tee -a "$OUT/driver.log"
else
    print "verdict=H-AllCandidateWritesPreTarget" | tee -a "$OUT/driver.log"
fi
exit 0
