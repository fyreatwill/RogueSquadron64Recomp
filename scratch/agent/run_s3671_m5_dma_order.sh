#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s3671_m5_dma_order"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armA/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PRESS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start'
mkdir -p "$OUT"

oracle_pid=""
port_pid=""
cleanup() {
    [[ -n "$oracle_pid" ]] && kill -KILL "$oracle_pid" 2>/dev/null || true
    [[ -n "$port_pid" ]] && kill -KILL "$port_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

(
    cd "$ROOT/build" || exit 3
    exec env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 55 \
        --watch-write 0x0:0x800000 \
        --watch-write 0x171CE0:0x171D20 \
        --watch-write 0x171E70:0x171EB0 \
        --watch-write 0x173B20:0x173B60 \
        --watch-write 0x173CB0:0x173CF0 \
        --watch-pc 0x80033FCC --pc-task-dump 0x80033FCC --pc-task-type 2 \
        --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 \
        --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 \
        --hit-cap 10000 --vi-trace --press "$PRESS" --hold-ms 150
) > "$OUT/oracle.log" 2>&1 &
oracle_pid=$!

(
    cd "$ROOT/build" || exit 3
    exec env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 \
        ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
        ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_PORT_LOAD=1 \
        ROGUESQ_LOG_M5_DESCRIPTOR=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_AUDIO_OBJECTS=1 \
        ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 \
        ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
        ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
        PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ./RogueSquadron64Recomp
) > "$OUT/port.log" 2>&1 &
port_pid=$!

for _ in {1..65}; do
    alive=0
    kill -0 "$oracle_pid" 2>/dev/null && alive=1
    kill -0 "$port_pid" 2>/dev/null && alive=1
    (( alive == 0 )) && break
    sleep 1
done
kill -KILL "$oracle_pid" "$port_pid" 2>/dev/null || true
wait "$oracle_pid" 2>/dev/null || true
wait "$port_pid" 2>/dev/null || true

{
    print -- '--- controls and joined source/task rows ---'
    grep -a -E '^(\[oracle\] (done:|watch write \[0x00000000|pc-task-dump|pc-hist|VI )|\[(phase|audtask-abi|audio-objects-task|audio-objects-frame|m5-rsp-source-hook-control|m5-rsp-source-control|m5-rsp-source|audtask-dma-row|audtask-dma-range|m5-source-transition|CRASH|ABORT)\])' "$OUT/oracle.log" "$OUT/port.log" | tail -260 || true
    print -- '--- counts ---'
    print "oracle_whole_rdram=$(grep -a -c '^\[oracle\] watch write \[0x00000000' "$OUT/oracle.log" || true)"
    print "oracle_task_rows=$(grep -a -c '^\[oracle\] pc-task-dump' "$OUT/oracle.log" || true)"
    print "port_title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/port.log" || true)"
    print "port_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port.log" || true)"
    print "port_abi=$(grep -a -c '^\[audtask-abi\]' "$OUT/port.log" || true)"
    print "port_dma=$(grep -a -c '^\[audtask-dma-' "$OUT/port.log" || true)"
    print "port_source=$(grep -a -c '^\[m5-source-transition\]' "$OUT/port.log" || true)"
} > "$OUT/summary.log"
