#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2278_m5_keyon_pointer_branch}
C88_VALUE=${2:-0}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

cd "$ROOT" || exit 2
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" ]]; then
    print "ERROR: build/ control prerequisites are missing" > "$OUT/driver.log"
    exit 3
fi

PCS=0x80090CF0,0x80090D08,0x80090D34,0x80090D4C,0x80090D78,0x80090D90,0x80090DBC,0x80090DD4
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start

tools/oracle/build/rs64_oracle \
    --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --secs 100 \
    --video "$ORACLE_VIDEO" --press "$PRESS" --hold-ms 150 \
    --watch-write 0x0:0x800000 --watch-pc "$PCS" \
    --pc-phase-log 0x006AB400 \
    --pc-field-dump "$PCS" --pc-phase-log-width 0x006AB400:512 \
    --vi-trace > "$OUT/retail.log" 2>&1 &
oracle_pid=$!

(
    cd "$BUILD" || exit 2
    env \
        ROGUESQ_AUDIO_UCODE=0 \
        ROGUESQ_LLE_FORCE=1 \
        ROGUESQ_LLE_UNGATED=1 \
        ROGUESQ_LLE_SOLO=1 \
        ROGUESQ_SPIN_YIELD=1 \
        ROGUESQ_M5_C88_VALUE=$C88_VALUE \
        ROGUESQ_STUB_MISSING_FUNCS=1 \
        ROGUESQ_LOG_M5_KEYON_CENSUS=1 \
        ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 \
        ROGUESQ_LOG_M5_B40_ROUTE=1 \
        ROGUESQ_LOG_M5_ROUTE_STATE=1 \
        PROBE_PHASE_WIDTH=1024 \
        PROBE_KEYS_FROM_PHASE=1 \
        ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1
) &
port_pid=$!
print "oracle_pid=$oracle_pid port_pid=$port_pid" > "$OUT/driver.log"

oracle_deadline=$((SECONDS + 150))
port_deadline=$((SECONDS + 220))
oracle_done=0
port_done=0
oracle_killed=0
port_killed=0
while (( oracle_done == 0 || port_done == 0 )); do
    if (( oracle_done == 0 )) && ! kill -0 "$oracle_pid" 2>/dev/null; then
        oracle_done=1
    elif (( oracle_done == 0 && SECONDS >= oracle_deadline )); then
        print "oracle=deadline; SIGKILL" >> "$OUT/driver.log"
        kill -9 "$oracle_pid" 2>/dev/null
        oracle_killed=1
        oracle_done=1
    fi
    if (( port_done == 0 )) && ! kill -0 "$port_pid" 2>/dev/null; then
        port_done=1
    elif (( port_done == 0 && SECONDS >= port_deadline )); then
        print "port=deadline; SIGKILL" >> "$OUT/driver.log"
        kill -9 "$port_pid" 2>/dev/null
        port_killed=1
        port_done=1
    fi
    (( oracle_done == 1 && port_done == 1 )) && break
    sleep 1
done

wait "$oracle_pid" 2>/dev/null
oracle_rc=$?
wait "$port_pid" 2>/dev/null
port_rc=$?
print "oracle_rc=$oracle_rc port_rc=$port_rc oracle_killed=$oracle_killed port_killed=$port_killed" >> "$OUT/driver.log"

print -- "--- controls ---" >> "$OUT/driver.log"
print "retail_whole_rdram=$(grep -a -c 'watch write \[0x00000000,0x00800000): 10000 hit' "$OUT/retail.log" || true)" >> "$OUT/driver.log"
print "retail_title=$(grep -a -c 'origin=0x00790400 width=1024' "$OUT/retail.log" || true)" >> "$OUT/driver.log"
print "retail_hangar=$(grep -a -c 'origin=0x006ab400 width=512' "$OUT/retail.log" || true)" >> "$OUT/driver.log"
print "retail_exec=$(grep -a -c '^\[hit\] x addr=0x00000000 pc=0x80090' "$OUT/retail.log" || true)" >> "$OUT/driver.log"
print "port_title=$(grep -a -c '\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/port.log" || true)" >> "$OUT/driver.log"
print "port_hangar=$(grep -a -c '\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port.log" || true)" >> "$OUT/driver.log"
for marker in \
    '\[m5-keyon-table\]' '\[m5-keyon-transfer\]' \
    '\[m5-keyon-pointer-branch\]' '\[m5-b40-route-control\]' \
    '\[m5-route-state-control\]' '\[missing-func\]' '\[CRASH\]' '\[ABORT\]'; do
    print "port_${marker}=$(grep -a -c "$marker" "$OUT/port.log" || true)" >> "$OUT/driver.log"
done

grep -a '^\[m5-keyon-pointer-branch\]' "$OUT/port.log" > "$OUT/pointer-branch-table" || true
grep -a -E '^\[phase\]|^\[pc-symbol\]|^\[last-guest-pc\]' "$OUT/port.log" | tail -20 >> "$OUT/driver.log" || true
grep -a -E '^\[oracle\] (done|watch pc|execution watch hits)' "$OUT/retail.log" > "$OUT/retail-controls" || true

(( oracle_killed == 0 && port_killed == 0 ))
