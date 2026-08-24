#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s2289_m5_retail_slot_route"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ]]; then
    print "ERROR: retail oracle prerequisites are missing" > "$OUT/driver.log"
    exit 2
fi

cd "$ROOT" || exit 3
ORACLE_PID=""
cleanup() {
    if [[ -n "$ORACLE_PID" ]] && kill -0 "$ORACLE_PID" 2>/dev/null; then
        /usr/bin/pkill -KILL -P "$ORACLE_PID" 2>/dev/null || true
        kill -KILL "$ORACLE_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" \
    --core "$CORE" \
    --rom "$ROM" \
    --video "$VIDEO" \
    --secs 180 \
    --watch-write 0x0:0x800000 \
    --watch-pc 0x8003E8DC,0x8003EA4C,0x800A70E4,0x800653B4,0x80007904 \
    --pc-phase-log-width 0x00696100:640 \
    --vi-trace \
    --press "$PRESS" \
    > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
print "oracle_pid=$ORACLE_PID" >> "$OUT/driver.log"
wait "$ORACLE_PID"
ORACLE_RC=$?
ORACLE_PID=""
print "oracle_rc=$ORACLE_RC" >> "$OUT/driver.log"

if ! grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log"; then
    print "verdict=H-RetailNoRouteControl missing_whole_rdram_positive_control" >> "$OUT/driver.log"
    exit 4
fi
if ! grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log"; then
    print "verdict=H-RetailNoRouteControl missing_title_1024" >> "$OUT/driver.log"
    exit 5
fi
if ! grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
    print "verdict=H-RetailNoRouteControl missing_hangar_512" >> "$OUT/driver.log"
    exit 6
fi

print "controls=passed whole_rdram=10000 title=1 hangar=1" >> "$OUT/driver.log"
print -- "--- initial-640 phase watch rows ---" >> "$OUT/driver.log"
grep -a -E '^\[hit\] .*pc=0x800(3e8dc|3ea4c|a70e4|653b4|07904) .*width=640 origin=0x00696100' "$OUT/oracle.log" \
    | head -80 >> "$OUT/driver.log" || true
for pc in 0x8003e8dc 0x8003ea4c 0x800a70e4 0x800653b4 0x80007904; do
    count=$(grep -a -E -c "^\[hit\] .*pc=$pc .*width=640 origin=0x00696100" "$OUT/oracle.log" || true)
    print "phase_hit_$pc=$count" >> "$OUT/driver.log"
done
print -- "--- exec-prev attribution ---" >> "$OUT/driver.log"
grep -a '^\[oracle\] exec-prev pc=0x800' "$OUT/oracle.log" \
    | grep -E 'pc=0x8003e8dc|pc=0x8003ea4c|pc=0x800a70e4|pc=0x800653b4|pc=0x80007904' \
    | sort >> "$OUT/driver.log" || true
print -- "--- oracle controls and final rows ---" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] (watch |execution watch hits|exec-prev|done)|^\[vi\].*(0x00696100|0x00790400|0x006ab400)' "$OUT/oracle.log" \
    | tail -80 >> "$OUT/driver.log" || true

slot_hits=$(grep -a -E -c '^\[hit\] .*pc=0x8003e8dc .*width=640 origin=0x00696100' "$OUT/oracle.log" || true)
slot_prev=$(grep -a -E -c '^\[oracle\] exec-prev pc=0x8003e8dc ' "$OUT/oracle.log" || true)
if (( slot_hits > 0 && slot_prev > 0 )); then
    print "verdict=H-RetailEquivalentSlotRoute phase_slot_hits=$slot_hits exec_prev_rows=$slot_prev" >> "$OUT/driver.log"
else
    print "verdict=H-RetailDifferentSlotRoute phase_slot_hits=$slot_hits exec_prev_rows=$slot_prev" >> "$OUT/driver.log"
fi
exit 0
