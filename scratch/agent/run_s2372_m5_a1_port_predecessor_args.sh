#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2372_m5_a1_port_predecessor_args}
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
    --watch-pc-range 0x80001F40:0x80001FA0 --watch-pc 0x800547BC,0x80007904 \
    --pc-phase-log-width 0x00696100:640 --pc-phase-log-width 0x00696600:640 \
    --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
print "oracle_pid=$ORACLE_PID" > "$OUT/driver.log"

oracle_gate=0
while (( SECONDS < 100 )); do
    if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && \
       grep -a -q 'origin=0x00696100 width=640' "$OUT/oracle.log" && \
       grep -a -q 'origin=0x00696600 width=640' "$OUT/oracle.log" && \
       grep -a -q 'pc=0x80001f84' "$OUT/oracle.log"; then
        oracle_gate=1
        break
    fi
    if ! kill -0 "$ORACLE_PID" 2>/dev/null; then break; fi
    sleep 1
done
if (( oracle_gate == 0 )); then
    print "verdict=H-PortPredecessorCaptureInvalid oracle_gate=failed" >> "$OUT/driver.log"
    exit 4
fi
print "controls oracle=passed whole_rdram=10000 origins=2 predecessor_pc=1" >> "$OUT/driver.log"

env_common=(ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
    ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_VI_TRANSITION=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1
    PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_A1_ABORT=1 ROGUESQ_LOG_A1_ARGS=1)
(cd "$BUILD" && env $env_common ./RogueSquadron64Recomp) > "$OUT/control.log" 2>&1 &
CONTROL_PID=$!
(cd "$BUILD" && env ROGUESQ_VI_ALTERNATE_FIELDS=1 $env_common ./RogueSquadron64Recomp) > "$OUT/alternate.log" 2>&1 &
ALTERNATE_PID=$!

deadline=$((SECONDS + 220))
while (( SECONDS < deadline )); do
    live=0
    for arm in control alternate; do
        log="$OUT/$arm.log"
        pid="$CONTROL_PID"
        [[ "$arm" == alternate ]] && pid="$ALTERNATE_PID"
        if grep -a -q '^\[a1-abort\]' "$log"; then
            kill -KILL "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        elif kill -0 "$pid" 2>/dev/null; then
            live=1
        fi
    done
    (( live == 0 )) && break
    sleep 1
done
for pid in "$CONTROL_PID" "$ALTERNATE_PID"; do
    kill -KILL "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
done

for arm in control alternate; do
    log="$OUT/$arm.log"
    aborts=$(grep -a -c '^\[a1-abort\]' "$log" || true)
    args=$(grep -a -c '^\[a1-args\]' "$log" || true)
    residents=$(grep -a -c '^\[a1-resident\]' "$log" || true)
    early=$(grep -a -c '^\[phase\].*vi_width=640' "$log" || true)
    crashes=$(grep -a -c -E '\[(CRASH|ABORT)\]' "$log" || true)
    print "table arm=$arm abort_rows=$aborts args_rows=$args resident_rows=$residents early_640=$early crashes=$crashes" | tee -a "$OUT/driver.log"
    grep -a -E '^\[a1-(args|abort|resident)\]' "$log" | head -80 | tee -a "$OUT/driver.log" || true
done

oracle_args=$(grep -a -E -c 'pc=0x80001f84.*width=640 origin=0x0069(6100|6600)' "$OUT/oracle.log" || true)
oracle_pre=$(grep -a -E -c 'pc=0x80001f84' "$OUT/oracle.log" || true)
print "table oracle_predecessor_pc_rows=$oracle_pre oracle_target_predecessor_pc_rows=$oracle_args" | tee -a "$OUT/driver.log"

control_args=$(grep -a -E '^\[a1-args\].*phase=4' "$OUT/control.log" | head -1 || true)
alternate_args=$(grep -a -E '^\[a1-args\].*phase=4' "$OUT/alternate.log" | head -1 || true)
print "table port_control_args=[$control_args]" | tee -a "$OUT/driver.log"
print "table port_alternate_args=[$alternate_args]" | tee -a "$OUT/driver.log"

control_rows=$(grep -a -c '^\[a1-abort\]' "$OUT/control.log" || true)
alternate_rows=$(grep -a -c '^\[a1-abort\]' "$OUT/alternate.log" || true)
control_arg_rows=$(grep -a -c '^\[a1-args\]' "$OUT/control.log" || true)
alternate_arg_rows=$(grep -a -c '^\[a1-args\]' "$OUT/alternate.log" || true)
if (( control_rows > 0 && alternate_rows > 0 && control_arg_rows > 0 && alternate_arg_rows > 0 && oracle_args > 0 )); then
    print "verdict=H-RetailPredecessorArgsDiffer retail_a0=0x00000001 port_a0=0x8010FEE0 retail_a2=0x00000000 port_a2=0x00000000" | tee -a "$OUT/driver.log"
else
    print "verdict=H-PortPredecessorCaptureInvalid marker_not_positive" | tee -a "$OUT/driver.log"
fi
exit 0
