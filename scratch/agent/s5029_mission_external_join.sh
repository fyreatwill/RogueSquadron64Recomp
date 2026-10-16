#!/bin/zsh
set -u
set -o pipefail

ROOT="${0:A:h:h:h}"
OUT="$ROOT/scratch/agent/s5029_mission_external_join"
BUILD="$ROOT/build"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PRESS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,66:a,73:a,80:start,90:a,100:start,110:a,120:start,130:a,140:start,150:a,160:start,170:a,180:start,190:a,200:start,210:a,220:start,230:a,240:start,250:a'

mkdir -p "$OUT"
if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ||
      ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" ]]; then
    print -r -- 'prerequisite failure' > "$OUT/summary.txt"
    exit 2
fi

retail_pid=''; port_pid=''
cleanup() {
    [[ -n "$retail_pid" ]] && kill -KILL "$retail_pid" 2>/dev/null || true
    [[ -n "$port_pid" ]] && kill -KILL "$port_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$ROOT"
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 270 \
    --watch-write 0x0:0x800000 \
    --watch-pc-range 0x8008FFAC:0x80090640 \
    --watch-pc 0x800903F0,0x80090C80,0x800921E8 \
    --pc-phase-log-width 0x00690400:512 \
    --pc-phase-log-width 0x00620400:512 \
    --vi-trace --first-watch 1 --hit-cap 30000 \
    --press "$PRESS" --hold-ms 150 > "$OUT/retail.log" 2>&1 &
retail_pid=$!

cd "$BUILD"
env ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 \
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_DLWALK=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 \
    ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_VI_TRANSITION=1 \
    ROGUESQ_LOG_S4534=1 ROGUESQ_LOG_S4535=1 ROGUESQ_LOG_S4537=1 ROGUESQ_LOG_S4538=1 \
    ROGUESQ_LOG_S4539=1 ROGUESQ_LOG_S4577=1 ROGUESQ_LOG_S4578=1 ROGUESQ_LOG_S4579=1 \
    PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=240 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1 &
port_pid=$!
L="$OUT/port.log"
has() { grep -aq "$1" "$L"; }
key() { "$BUILD/winctl" activate $port_pid >/dev/null 2>&1; "$BUILD/winctl" key $port_pid $1 250 >/dev/null 2>&1; }
for i in $(seq 1 150); do has 'origin=0x00790400' && break; sleep 1; done
for n in $(seq 1 12); do has 'origin=0x006AB400' && break; key 36; sleep 4; key 6; sleep 7; done
sleep 15
for n in $(seq 1 14); do has 'origin=0x006A2900' && break; key 6; sleep 7; done
for n in $(seq 1 50); do sleep 5; [ $((n%6)) -eq 0 ] && key 6; done
deadline=$((SECONDS + 20))
while (( SECONDS < deadline )); do
    alive=0
    kill -0 "$retail_pid" 2>/dev/null && alive=1
    kill -0 "$port_pid" 2>/dev/null && alive=1
    (( alive )) || break
    sleep 1
done
cleanup
wait "$retail_pid" 2>/dev/null || true
wait "$port_pid" 2>/dev/null || true
trap - EXIT INT TERM

{
    print -r -- "retail_control=$(grep -a -c 'positive-control threshold reached' "$OUT/retail.log" || true)"
    print -r -- "retail_mission_690400=$(grep -a -c 'origin=0x00690400 width=512' "$OUT/retail.log" || true)"
    print -r -- "retail_mission_620400=$(grep -a -c 'origin=0x00620400 width=512' "$OUT/retail.log" || true)"
    print -r -- "retail_consumer=$(grep -a -c 'pc=0x800903f0' "$OUT/retail.log" || true)"
    print -r -- "retail_writers=$(grep -a -c 'pc=0x80090c80\|pc=0x800921e8' "$OUT/retail.log" || true)"
    print -r -- "port_mission_690400=$(grep -a -c 'origin=0x00690400\|origin=0x690400' "$OUT/port.log" || true)"
    print -r -- "port_mission_620400=$(grep -a -c 'origin=0x00620400\|origin=0x620400' "$OUT/port.log" || true)"
    print -r -- "port_consumer=$(grep -a -c '^\[s4534-jal\].*site=800903F0' "$OUT/port.log" || true)"
    print -r -- "port_caller=$(grep -a -c '^\[s4994-s4540\].*kind=row' "$OUT/port.log" || true)"
    print -r -- "retail_crash=$(grep -a -c 'CRASH\|ABORT' "$OUT/retail.log" || true)"
    print -r -- "port_crash=$(grep -a -c 'CRASH\|ABORT' "$OUT/port.log" || true)"
} | tee "$OUT/summary.txt"
