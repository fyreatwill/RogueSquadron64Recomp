#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
if (( $# > 0 )); then
    TAG="$1"
else
    TAG=s2282_m5_c88_staggered_route
fi
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

run_port() {
    local c88="$1"
    local log="$2"
    cd "$BUILD" || exit 2
    env \
        ROGUESQ_AUDIO_UCODE=0 \
        ROGUESQ_LLE_FORCE=1 \
        ROGUESQ_LLE_UNGATED=1 \
        ROGUESQ_LLE_SOLO=1 \
        ROGUESQ_SPIN_YIELD=1 \
        ROGUESQ_M5_C88_VALUE="$c88" \
        ROGUESQ_STUB_MISSING_FUNCS=1 \
        ROGUESQ_LOG_M5_KEYON_CENSUS=1 \
        ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 \
        ROGUESQ_LOG_AUDIO_RETURN=1 \
        ROGUESQ_LOG_PCM_BOUNDARY=1 \
        ROGUESQ_LOG_M5_B40_ROUTE=1 \
        ROGUESQ_LOG_M5_ROUTE_STATE=1 \
        PROBE_PHASE_WIDTH=1024 \
        PROBE_KEYS_FROM_PHASE=1 \
        ./RogueSquadron64Recomp > "$log" 2>&1
}

run_port 0 "$OUT/port_c88_0.log" &
port0_pid=$!
print "oracle_pid=$oracle_pid port_c88_0_pid=$port0_pid" > "$OUT/driver.log"

oracle_deadline=$((SECONDS + 150))
port0_deadline=$((SECONDS + 220))
oracle_done=0
port0_done=0
port1_done=1
oracle_killed=0
port0_killed=0
port1_killed=0
port1_pid=0
port1_deadline=0
hangar=0

while (( oracle_done == 0 || port0_done == 0 || port1_done == 0 )); do
    if (( oracle_done == 0 )) && ! kill -0 "$oracle_pid" 2>/dev/null; then
        oracle_done=1
    elif (( oracle_done == 0 && SECONDS >= oracle_deadline )); then
        print "oracle=deadline; SIGKILL" >> "$OUT/driver.log"
        kill -9 "$oracle_pid" 2>/dev/null
        oracle_killed=1
        oracle_done=1
    fi
    if (( port0_done == 0 )) && ! kill -0 "$port0_pid" 2>/dev/null; then
        port0_done=1
    elif (( port0_done == 0 && SECONDS >= port0_deadline )); then
        print "port_c88_0=deadline; SIGKILL" >> "$OUT/driver.log"
        kill -9 "$port0_pid" 2>/dev/null
        port0_killed=1
        port0_done=1
    fi
    if (( hangar == 0 && port0_done == 0 )) && grep -a -q '\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port_c88_0.log"; then
        hangar=1
        print "c88_0_first_512=observed; launching c88_1" | tee -a "$OUT/driver.log"
        run_port 1 "$OUT/port_c88_1.log" &
        port1_pid=$!
        port1_deadline=$((SECONDS + 220))
        port1_done=0
        print "port_c88_1_pid=$port1_pid" >> "$OUT/driver.log"
    fi
    if (( port1_done == 0 )); then
        if ! kill -0 "$port1_pid" 2>/dev/null; then
            port1_done=1
        elif (( SECONDS >= port1_deadline )); then
            print "port_c88_1=deadline; SIGKILL" >> "$OUT/driver.log"
            kill -9 "$port1_pid" 2>/dev/null
            port1_killed=1
            port1_done=1
        fi
    fi
    (( oracle_done == 1 && port0_done == 1 && port1_done == 1 )) && break
    sleep 1
done

(( hangar == 1 )) || print "c88_0_hangar=missing; c88_1_not_launched" >> "$OUT/driver.log"

for pid in "$oracle_pid" "$port0_pid" "$port1_pid"; do
    if (( pid > 0 )) && kill -0 "$pid" 2>/dev/null; then
        print "cleanup_pid=$pid; SIGKILL" >> "$OUT/driver.log"
        kill -9 "$pid" 2>/dev/null
    fi
done

wait "$oracle_pid" 2>/dev/null; oracle_rc=$?
wait "$port0_pid" 2>/dev/null; port0_rc=$?
if (( port1_pid > 0 )); then
    wait "$port1_pid" 2>/dev/null; port1_rc=$?
else
    port1_rc=125
fi
print "oracle_rc=$oracle_rc port_c88_0_rc=$port0_rc port_c88_1_rc=$port1_rc oracle_killed=$oracle_killed port_c88_0_killed=$port0_killed port_c88_1_killed=$port1_killed" >> "$OUT/driver.log"

print -- "--- retail controls ---" >> "$OUT/driver.log"
print "retail_whole_rdram=$(grep -a -c 'watch write \[0x00000000,0x00800000): 10000 hit' "$OUT/retail.log" || true)" >> "$OUT/driver.log"
print "retail_title=$(grep -a -c 'origin=0x00790400 width=1024' "$OUT/retail.log" || true)" >> "$OUT/driver.log"
print "retail_hangar=$(grep -a -c 'origin=0x006ab400 width=512' "$OUT/retail.log" || true)" >> "$OUT/driver.log"
print "retail_exec=$(grep -a -c '^\[hit\] x addr=0x00000000 pc=0x80090' "$OUT/retail.log" || true)" >> "$OUT/driver.log"

print -- "--- comparison table ---" >> "$OUT/driver.log"
for arm in c88_0 c88_1; do
    log="$OUT/port_"$arm".log"
    if [[ ! -f "$log" ]]; then
        print "arm=$arm phase=not_launched" >> "$OUT/driver.log"
        continue
    fi
    title=$(grep -a -c '\[phase\] vi_width=1024 .*origin=0x00790400' "$log" || true)
    hangar_rows=$(grep -a -c '\[phase\] vi_width=512 .*origin=0x006AB400' "$log" || true)
    last_phase=$(grep -a -E '^\[phase\]' "$log" | tail -1 || true)
    failure=$(grep -a -E '\[CRASH\]|\[ABORT\]|\[last-guest-pc\]' "$log" | tail -1 || true)
    [[ -n "$failure" ]] || failure=deadline_or_no_failure_marker
    keyon=$(grep -a -c '^\[m5-keyon-pointer-branch\]' "$log" || true)
    b40=$(grep -a -c '^\[m5-b40-route-control\]' "$log" || true)
    route=$(grep -a -c '^\[m5-route-state-control\]' "$log" || true)
    print "arm=$arm phase=1024_title=$title phase=512_hangar=$hangar_rows last_phase=$last_phase timeout_or_crash=$failure keyon_rows=$keyon b40_route_control=$b40 route_state_control=$route" >> "$OUT/driver.log"
    grep -a '^\[m5-keyon-pointer-branch\]' "$log" > "$OUT/$arm-pointer-branch-table" || true
    grep -a -E '^\[phase\]|^\[pc-symbol\]|^\[last-guest-pc\]' "$log" | tail -20 > "$OUT/$arm-phase-tail" || true
done
grep -a -E '^\[oracle\] (done|watch pc|execution watch hits)' "$OUT/retail.log" > "$OUT/retail-controls" || true

(( oracle_killed == 0 && port0_killed == 0 && port1_killed == 0 ))
