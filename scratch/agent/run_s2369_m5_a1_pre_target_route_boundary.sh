#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2369_m5_a1_pre_target_route_boundary}
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
typeset -A DONE STATUS
ORACLE_PID=""
CONTROL_PID=""
ALTERNATE_PID=""
cleanup() {
    [[ -n "$ORACLE_PID" ]] && kill -KILL "$ORACLE_PID" 2>/dev/null || true
    [[ -n "$CONTROL_PID" ]] && kill -KILL "$CONTROL_PID" 2>/dev/null || true
    [[ -n "$ALTERNATE_PID" ]] && kill -KILL "$ALTERNATE_PID" 2>/dev/null || true
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
    print "verdict=H-AbortInstrumentInvalid oracle_gate=failed" >> "$OUT/driver.log"
    exit 4
fi
print "oracle_gate=passed whole_rdram=10000 origin_696100=1 origin_696600=1" >> "$OUT/driver.log"

env_common=(ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
    ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_TRANSITION=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1
    PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1)
(cd "$BUILD" && env ROGUESQ_LOG_A1_ABORT=1 $env_common ./RogueSquadron64Recomp) > "$OUT/control.log" 2>&1 &
CONTROL_PID=$!
(cd "$BUILD" && env ROGUESQ_VI_ALTERNATE_FIELDS=1 ROGUESQ_LOG_A1_ABORT=1 $env_common ./RogueSquadron64Recomp) > "$OUT/alternate.log" 2>&1 &
ALTERNATE_PID=$!
PIDS_control="$CONTROL_PID"
PIDS_alternate="$ALTERNATE_PID"
pid_for() {
    if [[ "$1" == control ]]; then
        print -r -- "$CONTROL_PID"
    else
        print -r -- "$ALTERNATE_PID"
    fi
}
for arm in control alternate; do
    DONE[$arm]=0
    STATUS[$arm]=running
done

deadline=$((SECONDS + 220))
while (( SECONDS < deadline )); do
    live=0
    for arm in control alternate; do
        if (( DONE[$arm] == 0 )); then
            log="$OUT/$arm.log"
            pid=$(pid_for "$arm")
            if grep -a -q '^\[a1-abort\]' "$log"; then
                kill -KILL "$pid" 2>/dev/null || true
                wait "$pid" 2>/dev/null || true
                STATUS[$arm]=abort_table
                DONE[$arm]=1
            elif kill -0 "$pid" 2>/dev/null; then
                live=1
            else
                wait "$pid" 2>/dev/null || STATUS[$arm]=exit
                DONE[$arm]=1
            fi
        fi
    done
    (( live == 0 )) && break
    sleep 1
done
for arm in control alternate; do
    if (( DONE[$arm] == 0 )); then
        pid=$(pid_for "$arm")
        kill -KILL "$pid" 2>/dev/null || true
        wait "$pid" 2>/dev/null || true
        STATUS[$arm]=watchdog
        DONE[$arm]=1
    fi
done

for arm in control alternate; do
    log="$OUT/$arm.log"
    aborts=$(grep -a -c '^\[a1-abort\]' "$log" || true)
    residents=$(grep -a -c '^\[a1-resident\]' "$log" || true)
    transitions=$(grep -a -c '^\[vi-transition-producer\]' "$log" || true)
    early=$(grep -a -c '^\[phase\].*vi_width=640' "$log" || true)
    crashes=$(grep -a -c -E '\[(CRASH|ABORT)\]' "$log" || true)
    print "table arm=$arm abort_rows=$aborts resident_rows=$residents early_640=$early transitions=$transitions crashes=$crashes terminal=${STATUS[$arm]}" | tee -a "$OUT/driver.log"
    grep -a -E '^\[a1-(abort|resident)\]' "$log" | head -80 | tee -a "$OUT/driver.log" || true
done

if (( oracle_gate == 1 )); then
    control_rows=$(grep -a -c '^\[a1-abort\]' "$OUT/control.log" || true)
    alternate_rows=$(grep -a -c '^\[a1-abort\]' "$OUT/alternate.log" || true)
    if (( control_rows > 0 && alternate_rows > 0 )); then
        print "verdict=classified abort_table_written" | tee -a "$OUT/driver.log"
    else
        print "verdict=H-AbortInstrumentInvalid marker_not_positive_both_arms" | tee -a "$OUT/driver.log"
    fi
fi
exit 0
