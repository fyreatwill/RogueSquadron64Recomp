#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/s3836_m5_task_contract_edge"
mkdir -p "$OUT"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RICE=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$RICE" ]]; then
  print -r -- "setup=missing" > "$OUT/driver.log"
  exit 2
fi
cd "$ROOT" || exit 2
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$RICE" --secs 75 \
  --watch-write 0x0:0x800000 --watch-pc 0x80033FCC \
  --pc-task-dump 0x80033FCC \
  --pc-phase-log-width 0x790400:1024 --pc-phase-log-width 0x6AB400:512 \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$OUT/oracle.log" 2>&1 &
oracle_pid=$!
cd "$ROOT/build" || exit 2
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1 \
  ROGUESQ_LOG_M5_FAMILY_EDGE=1 ROGUESQ_LOG_M5_FAMILY_STORE=1 \
  ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1 \
  ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_PCM_WRITER=1 \
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_EXACT_ROUTE=1 \
  ROGUESQ_LOG_M5_SOURCE_RANGE=1 ROGUESQ_LOG_M5_ROUTE_PREPARE=1 \
  ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_DYNAMIC_CALLBACK=1 \
  ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1 &
port_pid=$!
print -r -- "oracle_pid=$oracle_pid port_pid=$port_pid" > "$OUT/driver.log"
for tick in {1..300}; do
  alive=0
  kill -0 "$oracle_pid" 2>/dev/null && alive=1
  kill -0 "$port_pid" 2>/dev/null && alive=1
  (( alive )) || break
  sleep 0.25
done
kill -KILL "$oracle_pid" 2>/dev/null || true
kill -KILL "$port_pid" 2>/dev/null || true
wait "$oracle_pid" 2>/dev/null || true
wait "$port_pid" 2>/dev/null || true
for marker in 'positive-control threshold reached' 'origin=0x00790400 width=1024' 'origin=0x006ab400 width=512' '[pc-task-dump]' 'exec pc=0x80033fcc'; do
  print -r -- "oracle_${marker// /_}=$(grep -a -F -c "$marker" "$OUT/oracle.log" || true)" >> "$OUT/driver.log"
done
for marker in '[phase]' '[audtask-abi]' '[audtask-dma-row]' '[audtask-dma-range]' '[audio-return]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' 'CRASH' 'ABORT'; do
  print -r -- "port_${marker// /_}=$(grep -a -F -c "$marker" "$OUT/port.log" || true)" >> "$OUT/driver.log"
done
