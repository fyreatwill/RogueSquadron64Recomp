#!/bin/sh
set -eu

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM="$ROOT/rogue_squadron.z64"
RSP=/opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib
OUT="$ROOT/scratch/agent/soak_results/s1045_retail_phase_discriminator"
mkdir -p "$OUT"

run_arm() {
    name=$1
    press=$2
    log="$OUT/$name.log"
    cfg="$OUT/$name-config"
    mkdir -p "$cfg"
    "$ORACLE" \
        --core "$CORE" --rsp "$RSP" --rom "$ROM" \
        --configdir "$cfg" --secs 120 --hold-ms 150 \
        --watch-write 0x0:0x800000 --hit-cap 10000 \
        --press "$press" --vi-trace --vi-poll --pif-trace \
        >"$log" 2>&1 &
    pid=$!
    (
        sleep 150
        kill -KILL "$pid" 2>/dev/null || true
    ) &
    watchdog=$!
    rc=0
    wait "$pid" || rc=$?
    kill "$watchdog" 2>/dev/null || true
    wait "$watchdog" 2>/dev/null || true
    printf '%s rc=%s log=%s\n' "$name" "$rc" "$log"
}

run_arm start_only '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' &
pid_a=$!
run_arm start_z '6:start,6:z,11:start,11:z,16:start,16:z,21:start,21:z,26:start,26:z,31:start,31:z,36:start,36:z,41:start,41:z,46:start,46:z,51:start,51:z,56:start,56:z' &
pid_b=$!
wait "$pid_a"
wait "$pid_b"

for log in "$OUT"/*.log; do
    printf '\n--- %s ---\n' "$log"
    grep -E '^\[oracle\] (positive-control|done:)|^\[press\]|^\[vi-(trace|poll)|^\[pif' "$log" | tail -80 || true
done
