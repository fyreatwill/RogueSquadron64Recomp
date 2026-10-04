#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s4066_native_isolated
AUDIO_UCODE=${RS64_AUDIO_UCODE:-1}
BUILD=$ROOT/build
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"
oracle_pid=""; port_pid=""
cleanup() { [[ -n "$port_pid" ]] && kill -KILL "$port_pid" 2>/dev/null || true; [[ -n "$oracle_pid" ]] && kill -KILL "$oracle_pid" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 180 \
  --watch-write 0x0:0x800000 --hit-cap 10000 --watch-pc 0x80029E80 \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --pc-task-dump 0x80019CD8 --pc-task-type 2 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start \
  > "$OUT/retail.log" 2>&1 & oracle_pid=$!
for _ in {1..120}; do grep -a -q 'positive-control threshold reached' "$OUT/retail.log" && break; sleep 0.25; done
( cd "$BUILD" && env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_AUDIO_HOST=1 \
  ROGUESQ_LOG_M5_AUDIO_DRAIN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
  ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_AUDIO_UCODE=$AUDIO_UCODE ./RogueSquadron64Recomp ) \
  > "$OUT/native.log" 2>&1 & port_pid=$!
for _ in {1..480}; do kill -0 "$port_pid" 2>/dev/null || break; sleep 0.25; done
kill -KILL "$port_pid" 2>/dev/null || true; wait "$port_pid" 2>/dev/null || true
kill -KILL "$oracle_pid" 2>/dev/null || true; wait "$oracle_pid" 2>/dev/null || true
print -r -- '--- retail ---' > "$OUT/driver.log"
grep -a -E '\[oracle\] (positive-control|done)|origin=0x00790400 width=1024|origin=0x006ab400 width=512' "$OUT/retail.log" | tail -120 >> "$OUT/driver.log" || true
print -r -- '--- native ---' >> "$OUT/driver.log"
grep -a -E '\[Audio\]|\[phase\].*(1024|512)|\[m5-audio-host\]|\[m5-audio-drain-raw\]|\[CRASH\]|\[ABORT\]' "$OUT/native.log" | tail -260 >> "$OUT/driver.log" || true
