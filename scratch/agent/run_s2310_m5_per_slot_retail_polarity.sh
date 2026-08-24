#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2310_m5_per_slot_retail_polarity"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
WINCTL="$BUILD/winctl"
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" || ! -f "$ORACLE_VIDEO" ]]; then
    print "ERROR: oracle prerequisites missing" > "$OUT/driver.log"
    exit 2
fi
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" || ! -x "$WINCTL" ]]; then
    print "ERROR: port prerequisites missing" > "$OUT/driver.log"
    exit 3
fi
cd "$ROOT" || exit 4

PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
PORT_PRESS=(6 16 26 36 46 56)
COMMON=(
    ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_PCM_WRITER=1 ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
)
SLOT_WATCHES=(
    0x166450:0x166750 0x166750:0x166A50 0x166A50:0x166D50
    0x166D50:0x167050 0x167050:0x167350 0x167350:0x167650
    0x167650:0x167950 0x167950:0x167C50 0x167C50:0x167F50
    0x167F50:0x168250 0x168250:0x168550 0x168550:0x168850
    0x168850:0x168B50 0x168B50:0x168E50 0x168E50:0x169150
    0x169150:0x169450
)
ORACLE_ARGS=(
    --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" --secs 180
    --watch-write 0x0:0x800000 --watch-write 0x166450:0x169450
)
for slot_range in $SLOT_WATCHES; do
    ORACLE_ARGS+=(--watch-write "$slot_range")
done
ORACLE_ARGS+=(
    --watch-write 0x141AD0:0x141AF0 --hit-cap 200
    --watch-pc 0x800078EC --pc-phase-log-width 0x006AB400:512
    --pc-hist-phase 0x006AB400:512 --pc-hist-phase 0x006AB800:512
    --pc-hist-phase 0x00656400:512 --pc-hist-phase 0x00656800:512
    --pc-hist-phase 0x0066A500:640 --pc-hist-phase 0x00696100:640
    --pc-hist-phase 0x0066AA00:640 --pc-hist-phase 0x00696600:640
    --pc-hist-phase 0x00000280:320 --pc-hist-phase 0x006BA280:320
    --pc-hist-phase 0x005D4500:640 --pc-hist-phase 0x0062C200:640
    --pc-hist-phase 0x0062BD00:640 --pc-hist-phase 0x00790800:1024
    --pc-hist-phase 0x00790400:1024
    --post-value-pc 0x800078EC
    --vi-trace --press "$PRESS"
)
for watch in {1..17}; do
    ORACLE_ARGS+=(--pc-hist-watch "$watch" --post-value-watch "$watch")
done

ORACLE_PID=0
PORT_PID=0
KEY_PID=0
kill_tree() {
    local pid="$1"
    if [[ "$pid" != 0 ]] && kill -0 "$pid" 2>/dev/null; then
        /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
        kill -9 "$pid" 2>/dev/null || true
    fi
}
trap 'kill_tree "$KEY_PID"; kill_tree "$PORT_PID"; kill_tree "$ORACLE_PID"' EXIT INT TERM

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" $ORACLE_ARGS > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
(
    cd "$BUILD" || exit 2
    exec env $COMMON ./RogueSquadron64Recomp
) > "$OUT/port.log" 2>&1 &
PORT_PID=$!
print "oracle_pid=$ORACLE_PID port_pid=$PORT_PID" | tee -a "$OUT/driver.log"

window=""
until [[ -n "$window" || $SECONDS -ge 30 ]]; do
    kill -0 "$PORT_PID" 2>/dev/null || break
    window="$($WINCTL find "$PORT_PID" 2>/dev/null || true)"
    [[ -n "$window" ]] || sleep 1
done
if [[ -n "$window" ]]; then
    (
        previous=0
        for at in $PORT_PRESS; do
            sleep "$((at - previous))"
            previous=$at
            kill -0 "$PORT_PID" 2>/dev/null || exit 0
            "$WINCTL" activate "$PORT_PID" >/dev/null 2>&1 || true
            /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $PORT_PID to true" >/dev/null 2>&1 || true
            "$WINCTL" key "$PORT_PID" 36 >/dev/null 2>&1 || true
        done
    ) &
    KEY_PID=$!
else
    print "port_window=missing" | tee -a "$OUT/driver.log"
fi

oracle_gate=0
port_title=0
port_hangar=0
retained=0
deadline=$((SECONDS + 205))
while (( SECONDS < deadline )); do
    if (( oracle_gate == 0 )) &&
       grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" &&
       grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" &&
       grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
        oracle_gate=1
        print "oracle_controls=passed whole_rdram=10000 title=1 hangar=1" | tee -a "$OUT/driver.log"
    fi
    if (( port_title == 0 )) && grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/port.log"; then
        port_title=1
        print "port_title=observed" | tee -a "$OUT/driver.log"
    fi
    if (( port_hangar == 0 )) && grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port.log"; then
        port_hangar=1
        print "port_hangar=observed; retaining_45s" | tee -a "$OUT/driver.log"
        sleep 45
        kill_tree "$PORT_PID"
        retained=1
    fi
    kill -0 "$PORT_PID" 2>/dev/null || (( port_hangar == 1 )) || break
    sleep 1
done
kill_tree "$KEY_PID"
kill_tree "$PORT_PID"
wait "$KEY_PID" 2>/dev/null || true
wait "$PORT_PID" 2>/dev/null
port_rc=$?
if kill -0 "$ORACLE_PID" 2>/dev/null; then
    deadline=$((SECONDS + 25))
    while kill -0 "$ORACLE_PID" 2>/dev/null && (( SECONDS < deadline )); do sleep 1; done
fi
kill_tree "$ORACLE_PID"
wait "$ORACLE_PID" 2>/dev/null
oracle_rc=$?

oracle_whole=0
grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && oracle_whole=1
oracle_title=0
grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" && oracle_title=1
oracle_hangar=0
grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log" && oracle_hangar=1
ring_watch=0
grep -a -q 'watch write \[0x00166450,0x00169450): 12288 hit(s)' "$OUT/oracle.log" && ring_watch=1
ring_snapshot=0
grep -a -Eq 'post-value snapshot watch=1 bytes=12288 nonzero=[1-9]' "$OUT/oracle.log" && ring_snapshot=1
slot_histograms=$(grep -a -E -c 'writer-pc-phase origin=0x006ab400 width=512 watch=[2-9]|writer-pc-phase origin=0x006ab400 width=512 watch=1[0-7]+' "$OUT/oracle.log" || true)
print "oracle_rc=$oracle_rc port_rc=$port_rc whole_rdram=$oracle_whole title=$oracle_title hangar=$oracle_hangar ring_watch=$ring_watch ring_snapshot=$ring_snapshot slot_phase_histogram_lines=$slot_histograms port_title=$port_title port_hangar=$port_hangar retained=$retained" | tee -a "$OUT/driver.log"
exit 0
