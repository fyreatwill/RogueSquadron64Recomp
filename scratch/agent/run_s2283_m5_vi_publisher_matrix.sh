#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2283_m5_vi_publisher_matrix}
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

PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
ARMS=(control alternate current_reg_screen retrace_parity)
COMMON=(
    ROGUESQ_AUDIO_UCODE=0
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_VI_CONTEXT_PORT=1
    ROGUESQ_LOG_VI_PARITY_SCHEDULER=1
    ROGUESQ_LOG_VI_TRANSITION=1
    PROBE_PHASE_WIDTH=1024
    PROBE_KEYS_FROM_PHASE=1
)
BEHAVIOR_VARS=(
    ROGUESQ_VI_ALTERNATE_FIELDS
    ROGUESQ_VI_FIELD_FROM_CURRENT_REG
    ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN
    ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS
)

run_port() {
    local arm="$1"
    local log="$2"
    local -a arm_env=()
    case "$arm" in
        alternate)
            arm_env=(ROGUESQ_VI_ALTERNATE_FIELDS=1)
            ;;
        current_reg_screen)
            arm_env=(
                ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1
                ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=1
            )
            ;;
        retrace_parity)
            arm_env=(
                ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1
                ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS=1
            )
            ;;
    esac
    (
        cd "$BUILD" || exit 2
        env \
            -u ROGUESQ_VI_ALTERNATE_FIELDS \
            -u ROGUESQ_VI_FIELD_FROM_CURRENT_REG \
            -u ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN \
            -u ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS \
            ${=COMMON} ${=arm_env} \
            ./RogueSquadron64Recomp
    ) > "$log" 2>&1
}

tools/oracle/build/rs64_oracle \
    --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --secs 120 \
    --video "$ORACLE_VIDEO" --press "$PRESS" --hold-ms 150 \
    --watch-write 0x0:0x800000 --vi-trace \
    > "$OUT/retail.log" 2>&1 &
oracle_pid=$!

typeset -A PIDS DONE KILLED TERMINAL STATUS FIRST SECOND SECOND_AT
for arm in ${ARMS[@]}; do
    run_port "$arm" "$OUT/$arm.log" &
    PIDS[$arm]="$!"
    DONE[$arm]=0
    KILLED[$arm]=0
    TERMINAL[$arm]=running
    STATUS[$arm]=running
    FIRST[$arm]=0
    SECOND[$arm]=0
    SECOND_AT[$arm]=0
done

print "oracle_pid=$oracle_pid" > "$OUT/driver.log"
for arm in ${ARMS[@]}; do
    print "${arm}_pid=${PIDS[$arm]}" >> "$OUT/driver.log"
done

oracle_deadline=$((SECONDS + 150))
port_deadline=$((SECONDS + 220))
oracle_done=0
oracle_killed=0

cleanup() {
    for pid in "$oracle_pid" ${PIDS[@]}; do
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null
        fi
    done
}
trap cleanup EXIT INT TERM

all_done=0
while (( all_done == 0 )); do
    all_done=1

    if (( oracle_done == 0 )); then
        all_done=0
        if ! kill -0 "$oracle_pid" 2>/dev/null; then
            oracle_done=1
        elif (( SECONDS >= oracle_deadline )); then
            print "oracle=deadline; SIGKILL" >> "$OUT/driver.log"
            kill -9 "$oracle_pid" 2>/dev/null
            oracle_killed=1
            oracle_done=1
        fi
    fi

    for arm in ${ARMS[@]}; do
        pid=${PIDS[$arm]}
        log="$OUT/$arm.log"
        if (( DONE[$arm] == 1 )); then
            continue
        fi
        all_done=0

        if (( FIRST[$arm] == 0 )) && \
            grep -a -q '^\[vi-context-port\].*committed=0x00696100' "$log"; then
            FIRST[$arm]=1
            print "$arm reached first target origin" >> "$OUT/driver.log"
        fi
        if (( SECOND[$arm] == 0 )) && \
            grep -a -q '^\[vi-context-port\].*committed=0x00696600' "$log"; then
            SECOND[$arm]=1
            SECOND_AT[$arm]=$SECONDS
            print "$arm reached second target origin; retaining 15s" >> "$OUT/driver.log"
        fi

        if (( SECOND[$arm] == 1 && SECONDS >= SECOND_AT[$arm] + 15 )); then
            print "$arm target window complete; SIGKILL" >> "$OUT/driver.log"
            kill -9 "$pid" 2>/dev/null
            KILLED[$arm]=1
            TERMINAL[$arm]=target_window
            wait "$pid" 2>/dev/null
            STATUS[$arm]=$?
            DONE[$arm]=1
        elif ! kill -0 "$pid" 2>/dev/null; then
            wait "$pid" 2>/dev/null
            STATUS[$arm]=$?
            TERMINAL[$arm]=exit
            DONE[$arm]=1
        elif (( SECONDS >= port_deadline )); then
            print "$arm=deadline; SIGKILL" >> "$OUT/driver.log"
            kill -9 "$pid" 2>/dev/null
            KILLED[$arm]=1
            TERMINAL[$arm]=watchdog
            wait "$pid" 2>/dev/null
            STATUS[$arm]=$?
            DONE[$arm]=1
        fi
    done
    (( all_done == 0 )) && sleep 1
done

wait "$oracle_pid" 2>/dev/null
oracle_rc=$?
print "oracle_rc=$oracle_rc oracle_killed=$oracle_killed" >> "$OUT/driver.log"

print -- "--- retail controls ---" >> "$OUT/driver.log"
print "retail_whole_rdram=$(grep -a -c 'watch write \[0x00000000,0x00800000): 10000 hit' "$OUT/retail.log" || true)" >> "$OUT/driver.log"
print "retail_title=$(grep -a -c 'origin=0x00790400 width=1024' "$OUT/retail.log" || true)" >> "$OUT/driver.log"
print "retail_hangar=$(grep -a -c 'origin=0x006ab400 width=512' "$OUT/retail.log" || true)" >> "$OUT/driver.log"
grep -a -E '^\[oracle\] (done|watch write|VI)' "$OUT/retail.log" | tail -10 >> "$OUT/driver.log" || true

print -- "--- comparison table ---" >> "$OUT/driver.log"
driver_rc=0
for arm in ${ARMS[@]}; do
    log="$OUT/$arm.log"
    vi_control=$(grep -a -c '^\[vi-context-port-control\]' "$log" || true)
    parity_control=$(grep -a -c '^\[vi-parity-scheduler-control\]' "$log" || true)
    vi_rows=$(grep -a -c '^\[vi-context-port\]' "$log" || true)
    parity_rows=$(grep -a -c '^\[vi-parity-scheduler\]' "$log" || true)
    first=$(grep -a -c '^\[vi-context-port\].*committed=0x00696100' "$log" || true)
    second=$(grep -a -c '^\[vi-context-port\].*committed=0x00696600' "$log" || true)
    phase_first=$(grep -a -c '^\[phase\] vi_width=640 .*origin=0x00696100' "$log" || true)
    phase_second=$(grep -a -c '^\[phase\] vi_width=640 .*origin=0x00696600' "$log" || true)
    title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" || true)
    hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" || true)
    crashes=$(grep -a -c -E '\[(CRASH|ABORT)\]' "$log" || true)
    last_phase=$(grep -a -E '^\[phase\]' "$log" | tail -1 || true)
    failure=$(grep -a -E '\[(CRASH|ABORT)\]|^\[last-guest-pc\]' "$log" | tail -1 || true)
    [[ -n "$failure" ]] || failure=none
    print "arm=$arm vi_control=$vi_control parity_control=$parity_control vi_rows=$vi_rows parity_rows=$parity_rows first=$first second=$second phase_first=$phase_first phase_second=$phase_second title=$title hangar=$hangar crashes=$crashes terminal=${TERMINAL[$arm]} status=${STATUS[$arm]} killed=${KILLED[$arm]}" >> "$OUT/driver.log"
    print "arm=$arm last_phase=$last_phase failure=$failure" >> "$OUT/driver.log"
    grep -a -E '^\[vi-context-port\].*committed=0x00696(100|600)|^\[vi-parity-scheduler\].*origin=0x00696(100|600)' "$log" | head -80 > "$OUT/${arm}-target-table" || true
    grep -a -E '^\[vi-context-port-summary\]|^\[vi-parity-scheduler-summary\]' "$log" | tail -5 > "$OUT/${arm}-summaries" || true
    (( vi_control == 0 || parity_control == 0 )) && driver_rc=1
    (( crashes > 0 )) && driver_rc=1
done
grep -a -E '^\[vi\]|^\[oracle\] (done|watch write|VI)' "$OUT/retail.log" | tail -40 > "$OUT/retail-controls" || true

exit "$driver_rc"
