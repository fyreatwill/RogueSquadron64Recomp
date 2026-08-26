#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2368_m5_a1_second_origin_discriminator}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ||
      ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" ]]; then
    print "ERROR: oracle or build prerequisites are missing" > "$OUT/driver.log"
    exit 2
fi

cd "$ROOT" || exit 3
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
ORACLE_PID=""
typeset -A PIDS DONE KILLED STATUS
cleanup() {
    [[ -n "$ORACLE_PID" ]] && kill -KILL "$ORACLE_PID" 2>/dev/null || true
    for arm in control alternate; do
        [[ -n "${PIDS[$arm]-}" ]] && kill -KILL "${PIDS[$arm]}" 2>/dev/null || true
    done
}
trap cleanup EXIT INT TERM

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 180 \
    --watch-write 0x0:0x800000 --watch-write 0x00696100:0x00696700 \
    --watch-pc 0x800547BC,0x80007904 \
    --pc-phase-log-width 0x00696100:640 --pc-phase-log-width 0x00696600:640 \
    --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
print "oracle_pid=$ORACLE_PID" > "$OUT/driver.log"

oracle_gate=0
while (( SECONDS < 100 )); do
    if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && \
       grep -a -q 'origin=0x00696100 width=640' "$OUT/oracle.log" && \
       grep -a -q 'origin=0x00696600 width=640' "$OUT/oracle.log"; then
        oracle_gate=1
        break
    fi
    if ! kill -0 "$ORACLE_PID" 2>/dev/null; then break; fi
    sleep 1
done
if (( oracle_gate == 0 )); then
    print "verdict=H-A1-CoverageInvalid oracle_gate=failed" >> "$OUT/driver.log"
    exit 4
fi
print "oracle_gate=passed whole_rdram=10000 origin_696100=1 origin_696600=1" >> "$OUT/driver.log"

run_port() {
    local arm="$1"
    local log="$OUT/$arm.log"
    if [[ "$arm" == alternate ]]; then
        (cd "$BUILD" && env ROGUESQ_VI_ALTERNATE_FIELDS=1 \
            ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
            ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 ROGUESQ_LOG_VI_TRANSITION=1 \
            PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 \
            ./RogueSquadron64Recomp) > "$log" 2>&1
    else
        (cd "$BUILD" && env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
            ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 ROGUESQ_LOG_VI_TRANSITION=1 \
            PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 \
            ./RogueSquadron64Recomp) > "$log" 2>&1
    fi
}

for arm in control alternate; do
    run_port "$arm" &
    pid=$!
    PIDS[$arm]=$pid
    DONE[$arm]=0
    KILLED[$arm]=0
    STATUS[$arm]=running
done

deadline=$((SECONDS + 220))
while (( SECONDS < deadline )); do
    live=0
    for arm in control alternate; do
        if (( DONE[$arm] == 0 )); then
            log="$OUT/$arm.log"
            if grep -a -q '^\[vi-context-port\].*committed=0x00696600' "$log"; then
                kill -KILL "${PIDS[$arm]}" 2>/dev/null || true
                KILLED[$arm]=1
                STATUS[$arm]=target_window
                wait "${PIDS[$arm]}" 2>/dev/null || true
                DONE[$arm]=1
            elif kill -0 "${PIDS[$arm]}" 2>/dev/null; then
                live=1
            else
                wait "${PIDS[$arm]}" 2>/dev/null || STATUS[$arm]=$?
                DONE[$arm]=1
            fi
        fi
    done
    (( live == 0 )) && break
    sleep 1
done
for arm in control alternate; do
    if (( DONE[$arm] == 0 )); then
        kill -KILL "${PIDS[$arm]}" 2>/dev/null || true
        KILLED[$arm]=1
        STATUS[$arm]=watchdog
        wait "${PIDS[$arm]}" 2>/dev/null || true
        DONE[$arm]=1
    fi
done

{
    print -- "table=phase/origin oracle_vi oracle_target_writes oracle_named_pc port_phase port_rows port_first_line port_second_line port_transition"
    for origin in 00696100 00696600; do
        oracle_vi=$(grep -a -c "origin=0x$origin width=640" "$OUT/oracle.log" || true)
        oracle_writes=$(grep -a -E -c "^\[hit\] w addr=0x0069(6100|6600)" "$OUT/oracle.log" || true)
        oracle_pc=$(grep -a -E -c "^\[hit\].*pc=0x800(547bc|07904).*width=640 origin=0x$origin" "$OUT/oracle.log" || true)
        print "oracle\t0x$origin\t$oracle_vi\t$oracle_writes\t$oracle_pc"
        for arm in control alternate; do
            log="$OUT/$arm.log"
            phase=$(grep -a -c "^\[phase\] vi_width=640 .*origin=0x$origin" "$log" || true)
            rows=$(grep -a -c "^\[vi-context-port\].*committed=0x$origin" "$log" || true)
            line=$(grep -a -c "^\[vi-context-port\].*committed=0x$origin.*current_line=" "$log" || true)
            transition=$(grep -a -c "^\[vi-transition-producer\]" "$log" || true)
            print "$arm\t0x$origin\t$phase\t$rows\t$line\t$transition"
        done
    done
    for arm in control alternate; do
        log="$OUT/$arm.log"
        controls=$(grep -a -c '^\[vi-context-port-control\]' "$log" || true)
        crashes=$(grep -a -c -E '\[(CRASH|ABORT)\]' "$log" || true)
        print "arm=$arm controls=$controls crashes=$crashes terminal=${STATUS[$arm]} killed=${KILLED[$arm]}"
        grep -a -E '^\[vi-context-port\].*committed=0x00696(100|600)|^\[vi-transition-producer\]' "$log" | head -80 || true
    done
} | tee "$OUT/driver.log"

if (( oracle_gate == 1 )); then
    print "verdict=H-A1-RetailTransition coverage_positive; compare_table_written" >> "$OUT/driver.log"
fi
exit 0
