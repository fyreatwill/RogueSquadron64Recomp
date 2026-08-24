#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2276_m5_step1_pair}
OUT="$ROOT/scratch/agent/$TAG"
mkdir -p "$OUT"

ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE="$ROOT/../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib"
ORACLE_ROM="$ROOT/../rogue_squadron64/rogue_squadron.z64"
ORACLE_VIDEO="/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib"

if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" ]]; then
    print "ERROR: retail oracle prerequisites are missing"
    exit 2
fi

print "oracle_start" > "$OUT/driver.log"
"$ORACLE" \
    --core "$ORACLE_CORE" \
    --rom "$ORACLE_ROM" \
    --video "$ORACLE_VIDEO" \
    --secs 60 \
    --hit-cap 10000 \
    --watch-write 0x0:0x800000 \
    --watch-write 0xA0F50:0xA0F54 \
    --watch-write 0x141AD0:0x141AF0 \
    --watch-write 0x1498A:0x1498B \
    --watch-pc 0x80091EB0,0x8009B7EC,0x80029E80,0x80029F30 \
    --vi-trace \
    --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
    > "$OUT/oracle.log" 2>&1
ORACLE_RC=$?
print "oracle_rc=$ORACLE_RC" >> "$OUT/driver.log"
if ! grep -a -E -q 'watch write \[0x00000000,0x00800000\): [1-9]' "$OUT/oracle.log"; then
    print "oracle_whole_rdram_control=missing" | tee -a "$OUT/driver.log"
    exit 3
fi
if ! grep -a -i -q '0x006ab400' "$OUT/oracle.log"; then
    print "oracle_hangar_control=missing" | tee -a "$OUT/driver.log"
    exit 4
fi
print "oracle_controls=qualified" >> "$OUT/driver.log"

cd "$BUILD" || exit 5
if [[ ! -f rogue_squadron.z64 || ! -x RogueSquadron64Recomp ]]; then
    print "ERROR: build/ must contain the ROM and executable"
    exit 6
fi

COMMON=(
    ROGUESQ_LLE_FORCE=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_M5_C88_VALUE=0
    ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1
    PROBE_PHASE_WIDTH=1024
    PROBE_KEYS_FROM_PHASE=1
)
ARMS=(ROGUESQ_AUDIO_UCODE=0 ROGUESQ_AUDIO_UCODE=1)
ARM_NAMES=(silent image)

typeset -A PIDS=(silent 0 image 0)
typeset -A HANGAR=(silent 0 image 0)
typeset -A EXITED=(silent 0 image 0)
typeset -A LAUNCHED=(silent 0 image 0)

launch_arm() {
    local name="$1"
    local arm_env="$2"
    env ${=COMMON} "$arm_env" ./RogueSquadron64Recomp \
        > "$OUT/$name.log" 2>&1 &
    local child_pid=$!
    PIDS[$name]=$child_pid
    LAUNCHED[$name]=1
    print "${name}_pid=${PIDS[$name]}" >> "$OUT/driver.log"
}

run_arm() {
    local name="$1"
    local arm_env="$2"
    launch_arm "$name" "$arm_env"
    local pid=${PIDS[$name]}
    local deadline=$((SECONDS + 180))
    while (( SECONDS < deadline )); do
        if grep -a -q '\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/$name.log"; then
            HANGAR[$name]=1
            print "${name}_hangar=observed" | tee -a "$OUT/driver.log"
            break
        fi
        if ! kill -0 "$pid" 2>/dev/null; then
            EXITED[$name]=1
            break
        fi
        sleep 1
    done
    if (( HANGAR[$name] == 0 )); then
        print "${name}_hangar=missing; SIGKILL" | tee -a "$OUT/driver.log"
        kill -9 "$pid" 2>/dev/null
    fi
    wait "$pid" 2>/dev/null
}

print "arms_staged=silent,image" >> "$OUT/driver.log"
run_arm silent "${ARMS[1]}"
run_arm image "${ARMS[2]}"

for name in silent image; do
    log="$OUT/$name.log"
    print -- "--- $name ---" >> "$OUT/driver.log"
    for marker in \
        '\[audtask-dispatch\]' '\[audtask-abi\]' '\[audtask-dma-row\]' \
        '\[audtask-image-stage-row\]' '\[audio-return\]' '\[pcm-boundary-source\]' \
        '\[pcm-boundary-consumer\]' '\[slot-alloc\]' '\[slot-sb\]' \
        '\[filter-voice-audit-control\]' '\[m5-gate\]' '\[m5-b40-route-control\]' \
        '\[m5-route-state-control\]' '\[missing-func\]' '\[CRASH\]' '\[ABORT\]'; do
        count=$(grep -a -c "$marker" "$log" || true)
        print "$marker=$count" >> "$OUT/driver.log"
    done
    print "title=$(grep -a -c '\[phase\] vi_width=1024 .*origin=0x00790400' "$log" || true)" >> "$OUT/driver.log"
    print "hangar=$(grep -a -c '\[phase\] vi_width=512 .*origin=0x006AB400' "$log" || true)" >> "$OUT/driver.log"
    grep -a -E '\[phase\]|\[last-guest-pc\]|\[pc-symbol\]' "$log" | tail -6 >> "$OUT/driver.log" || true
done

if (( HANGAR[silent] == 0 || HANGAR[image] == 0 )); then
    exit 7
fi
if grep -a -q '\[CRASH\]\|\[ABORT\]' "$OUT/silent.log" || grep -a -q '\[CRASH\]\|\[ABORT\]' "$OUT/image.log"; then
    exit 8
fi
exit 0
