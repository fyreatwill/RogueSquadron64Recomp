#!/bin/zsh
set -u
R="$(git rev-parse --show-toplevel)"
OUT="$R/scratch/agent/s4689_m4_retail_witness"
mkdir -p "$OUT"
cd "$R/build" || exit 2

env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 \
    ROGUESQ_LOG_M4_ACCUM=1 ROGUESQ_M4_CONTROL_CAP=64 ROGUESQ_M4_TARGET_CAP=2048 \
    ROGUESQ_M4_PHASE_FROM=5 ROGUESQ_M4_SRC_CAP=6000 \
    ROGUESQ_AUTOPILOT='40:start,44:start,48:start,52:start,56:a,60:a,64:start,68:a' \
    ROGUESQ_AUTOPILOT_STOP_WIDTH=0 ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1 &
port=$!

"$R/tools/oracle/build/rs64_oracle" \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 120 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace --watch-pc 0x80035500 --pc-phase-log-width 0x006AB400:512 \
  --watch-write 0x0:0x800000 --watch-write 0x006AB400:0x006AB410 \
  --watch-write 0x00656400:0x00656410 --first-watch 1 --first-watch 2 \
  --pc-hist-watch 1 --pc-hist-watch 2 > "$OUT/oracle.log" 2>&1
echo $? > "$OUT/oracle.rc"

for i in $(seq 1 125); do
  kill -0 "$port" 2>/dev/null || break
  sleep 1
done
kill -9 "$port" 2>/dev/null
wait "$port" 2>/dev/null
echo $? > "$OUT/port.rc"
