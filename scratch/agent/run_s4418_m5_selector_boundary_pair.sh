#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4418_m5_selector_boundary_pair"
mkdir -p "$OUT"

cd "$ROOT" || exit 3

tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 75 \
  --watch-write 0x0:0x800000 \
  --vi-trace \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x00790800:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --watch-pc 0x8008EE84,0x80029E80,0x80091CB8,0x80033FCC \
  --watch-pc-range 0x80029D20:0x80029F20 \
  --pc-field-dump 0x80029E80,0x80033FCC \
  --pc-task-dump 0x80033FCC \
  --pc-task-type 2 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$OUT/retail.log" 2>&1 &
retail_pid=$!

cd "$ROOT/build" || exit 3
COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_M5_EXACT_ROUTE=1 ROGUESQ_LOG_M5_RSP_SOURCE=1
  ROGUESQ_LOG_M5_SOURCE_WRITER=1 ROGUESQ_LOG_M5_SOURCE_PRODUCER=1
  ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_LOG_M5_FAMILY_PROVENANCE=1
  ROGUESQ_LOG_M5_PCM_WRITER=1 ROGUESQ_LOG_M5_INPUT_WRITER=1
  ROGUESQ_LOG_M5_SELECTOR_ROUTE=1 ROGUESQ_LOG_M5_SELECTOR_MIXER_CALLSITE=1
  ROGUESQ_LOG_M5_SELECTOR_TICK=1 ROGUESQ_LOG_M5_TABLE_SELECTION=1
  ROGUESQ_LOG_M5_SELECTOR_TABLE=1 ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT=1
  ROGUESQ_LOG_M5_SELECTOR_PRODUCER=1 ROGUESQ_LOG_M5_SELECTOR_INPUT=1
  ROGUESQ_LOG_M5_SELECTOR_SOURCE=1 ROGUESQ_LOG_M5_SELECTOR_SETUP_CONTRACT=1
  ROGUESQ_LOG_M5_SELECTOR_STORE_ENTRY=1 ROGUESQ_LOG_M5_SELECTOR_CALLER=1
  ROGUESQ_LOG_M5_SELECTOR_PRECALL=1 ROGUESQ_LOG_M5_SELECTOR_AI_BOUNDARY=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a')
env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp \
  > "$OUT/port.log" 2>&1 &
port_pid=$!

trap 'kill -KILL "$retail_pid" "$port_pid" 2>/dev/null || true' EXIT INT TERM
sleep 85
kill -KILL "$retail_pid" "$port_pid" 2>/dev/null || true
wait "$retail_pid" 2>/dev/null || true
wait "$port_pid" 2>/dev/null || true

{
  printf 'retail_control='; grep -a -F -c '[hit] w addr=' "$OUT/retail.log" || true
  printf 'retail_vi='; grep -a -F -c 'origin=0x00790400 width=1024' "$OUT/retail.log" || true
  printf 'retail_selector='; grep -a -F -c 'pc=0x80029e80' "$OUT/retail.log" || true
  printf 'retail_caller='; grep -a -F -c 'pc=0x8008ee84' "$OUT/retail.log" || true
  printf 'retail_predecessor='; grep -a -F -c 'pc=0x80091cb8' "$OUT/retail.log" || true
  printf 'retail_tasks='; grep -a -F -c '[pc-task-dump]' "$OUT/retail.log" || true
  printf 'port_control='; grep -a -F -c '[m5-input-writer-control]' "$OUT/port.log" || true
  printf 'port_title='; grep -a -F -c 'vi_width=1024 origin=0x00790400' "$OUT/port.log" || true
  printf 'port_selector='; grep -a -F -c '[m5-selector-ai-boundary]' "$OUT/port.log" || true
  printf 'port_caller='; grep -a -F -c '[m5-selector-caller]' "$OUT/port.log" || true
  printf 'port_precall='; grep -a -F -c '[m5-selector-precall]' "$OUT/port.log" || true
  printf 'port_input='; grep -a -F -c '[m5-selector-input]' "$OUT/port.log" || true
  printf 'port_tasks='; grep -a -F -c '[audtask-join]' "$OUT/port.log" || true
  printf 'port_crash='; grep -a -F -c '[CRASH]' "$OUT/port.log" || true
  printf 'port_abort='; grep -a -F -c '[ABORT]' "$OUT/port.log" || true
} > "$OUT/summary.txt"
