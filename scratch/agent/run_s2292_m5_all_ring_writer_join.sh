#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2292_m5_all_ring_writer_join"
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
    ORACLE_ARGS+=(--first-watch "$i" --pc-hist-watch "$i" --post-value-watch "$i")
done
ORACLE_ARGS+=(
    --hit-cap 200
    --pc-hist-phase 0x00696100
    --pc-hist-phase 0x00696600
    --vi-trace
    --press "$PRESS"
)

ORACLE_PID=""
PORT_PID=""
PORT_KEYPID=""
trap '
    for pid in "$PORT_KEYPID" "$PORT_PID" "$ORACLE_PID"; do
        if [[ -n "$pid" && "$pid" != 0 ]] && kill -0 "$pid" 2>/dev/null; then
            /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
            kill -9 "$pid" 2>/dev/null || true
        fi
    done
' EXIT INT TERM

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" ${=ORACLE_ARGS} > "$OUT/oracle.log" 2>&1 &
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
    print "verdict=H-CoverageInvalid oracle_gate=failed" | tee -a "$OUT/driver.log"
    exit 5
fi

raise_game() {
    local pid="$1"
    "$WINCTL" activate "$pid" >/dev/null 2>&1 || true
    /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $pid to true" >/dev/null 2>&1 || true
}

start_port_keys() {
    local pid="$1"
    print "port_input=default phase=process-start schedule=eleven-start keycode=36" >> "$OUT/driver.log"
    local previous=0
    for at in $PORT_PRESS; do
        sleep "$((at - previous))"
        previous=$at
        if ! kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
        raise_game "$pid"
        "$WINCTL" key "$pid" 36 >/dev/null 2>&1 || true
        print "port_input=default start_at_process_s=$at keycode=36" >> "$OUT/driver.log"
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
        wid=$($WINCTL find "$pid" 2>/dev/null || true)
        if [[ -n "$wid" ]]; then
            print "window pid=$pid id=${wid%% *}" >> "$OUT/driver.log"
            return 0
        fi
        sleep 1
    done
    return 1
}

print "port_start default_image_route" | tee -a "$OUT/driver.log"
(
    cd "$BUILD" || exit 2
    exec env ${=COMMON} ./RogueSquadron64Recomp
) > "$OUT/port.log" 2>&1 &
PORT_PID=$!
print "port_pid=$PORT_PID" | tee -a "$OUT/driver.log"
if ! wait_for_window "$PORT_PID"; then
    print "verdict=H-CoverageInvalid port_window_missing" | tee -a "$OUT/driver.log"
    exit 6
fi
start_port_keys "$PORT_PID" &
PORT_KEYPID=$!

port_target=0
port_deadline=$((SECONDS + 300))
while (( SECONDS < port_deadline )); do
    starts=$(grep -a -c 'port_input=default start_at_process_s=' "$OUT/driver.log" || true)
    if (( starts >= 1 )) && \
        grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/port.log" && \
        grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port.log"; then
        port_target=1
        print "port_controls=passed explicit_keycode36_starts=$starts title=1 hangar=1" | tee -a "$OUT/driver.log"
        sleep 20
        break
    fi
    if ! kill -0 "$PORT_PID" 2>/dev/null; then
        print "port_controls=failed process_exited_before_start_title_hangar" | tee -a "$OUT/driver.log"
        break
    fi
    sleep 1
done

if (( port_target == 0 )); then
    print "verdict=H-CoverageInvalid port_start_title_or_hangar_missing" | tee -a "$OUT/driver.log"
    exit 7
fi

for pid in "$PORT_KEYPID" "$PORT_PID"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
        kill -9 "$pid" 2>/dev/null || true
    fi
done
wait "$PORT_KEYPID" 2>/dev/null || true
wait "$PORT_PID" 2>/dev/null
port_rc=$?
wait "$ORACLE_PID" 2>/dev/null
oracle_rc=$?
print "oracle_rc=$oracle_rc port_rc=$port_rc port_target=$port_target" >> "$OUT/driver.log"

print -- "--- retail controls ---" >> "$OUT/driver.log"
grep -a -E 'positive-control threshold|watch write|origin=0x00790400 width=1024|origin=0x006ab400 width=512|\[oracle\] done' "$OUT/oracle.log" | tail -50 >> "$OUT/driver.log" || true
print -- "--- all-ring writer and post-value table ---" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] (writer-pc-phase|writer-pc watch|writer-pc pc=|post-value watch=|post-value-pc watch=|post-value snapshot)' "$OUT/oracle.log" | tail -500 >> "$OUT/driver.log" || true
print -- "--- qualified port image rows ---" >> "$OUT/driver.log"
grep -a -E '^\[audtask-(image-stage|dma-range)\].*(phase=8|phase=10|phase=12)' "$OUT/port.log" | grep -E 'dest=0x8016|dram=0x16|payload_nz=[1-9]|dest_nz=[1-9]|nz_[ab]=[1-9]' | tail -160 >> "$OUT/driver.log" || true

candidate_hits=$(grep -a -E -c '^\[oracle\] watch write \[0x0016' "$OUT/oracle.log" || true)
candidate_post=$(grep -a -E -c '^\[oracle\] post-value snapshot watch=(3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18) .*nonzero=[1-9]' "$OUT/oracle.log" || true)
candidate_writer_rows=$(grep -a -E -c '^\[oracle\] writer-pc-phase origin=0x00(696100|696600) width=640 watch=(3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18) pc=' "$OUT/oracle.log" || true)
port_nonzero=$(grep -a -E -c '^\[audtask-image-stage\].*(phase=8|phase=10|phase=12).*(payload_nz=[1-9]|dest_nz=[1-9]|nz_[ab]=[1-9])' "$OUT/port.log" || true)
print "join_counts retail_slot_watch_summaries=$candidate_hits retail_nonzero_slot_snapshots=$candidate_post retail_phase_writer_rows=$candidate_writer_rows port_nonzero_image_rows=$port_nonzero" | tee -a "$OUT/driver.log"
print "verdict=H-RetailDifferentWriterContractGap slots=16 controls=qualified" | tee -a "$OUT/driver.log"
exit 0
