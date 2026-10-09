#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4416_m5_title_selector_witness"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 3

COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
  ROGUESQ_LOG_M5_EXACT_ROUTE=1 ROGUESQ_LOG_M5_RSP_SOURCE=1
  ROGUESQ_LOG_M5_SOURCE_WRITER=1 ROGUESQ_LOG_M5_SOURCE_PRODUCER=1
  ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_LOG_M5_FAMILY_PROVENANCE=1
  ROGUESQ_LOG_M5_PCM_WRITER=1 ROGUESQ_LOG_M5_INPUT_WRITER=1
  ROGUESQ_LOG_M5_SELECTOR_ROUTE=1
  ROGUESQ_LOG_M5_SELECTOR_MIXER_CALLSITE=1
  ROGUESQ_LOG_M5_SELECTOR_TICK=1
  ROGUESQ_LOG_M5_TABLE_SELECTION=1
  ROGUESQ_LOG_M5_SELECTOR_TABLE=1
  ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT=1
  ROGUESQ_LOG_M5_SELECTOR_PRODUCER=1
  ROGUESQ_LOG_M5_SELECTOR_INPUT=1
  ROGUESQ_LOG_M5_SELECTOR_SOURCE=1
  ROGUESQ_LOG_M5_SELECTOR_SETUP_CONTRACT=1
  ROGUESQ_LOG_M5_SELECTOR_STORE_ENTRY=1
  ROGUESQ_LOG_M5_SELECTOR_CALLER=1
  ROGUESQ_LOG_M5_SELECTOR_PRECALL=1
  ROGUESQ_LOG_M5_SELECTOR_AI_BOUNDARY=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a')

env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp \
  > "$OUT/port.log" 2>&1 &
game_pid=$!
trap 'kill -KILL "$game_pid" 2>/dev/null || true' EXIT INT TERM

sleep 85
kill -KILL "$game_pid" 2>/dev/null || true
wait "$game_pid" 2>/dev/null || true

{
  printf '%s\n' "control=$(grep -a -F -c '[m5-input-writer-control]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "title_790400=$(grep -a -F -c 'vi_width=1024 origin=0x00790400' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "title_790800=$(grep -a -F -c 'vi_width=1024 origin=0x00790800' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "hangar_6AB400=$(grep -a -F -c 'vi_width=512 origin=0x006AB400' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "task_rows=$(grep -a -F -c '[audtask-dma-row]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "task_joins=$(grep -a -F -c '[audtask-join]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "filter_joins=$(grep -a -F -c '[m5-filter-join]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "selector_route=$(grep -a -F -c '[m5-selector-route]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "selector_mixer=$(grep -a -F -c '[m5-selector-mixer]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "selector_tick=$(grep -a -F -c '[m5-selector-tick]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "table_selection=$(grep -a -F -c '[m5-selector-table-selection]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "selector_table=$(grep -a -F -c '[m5-selector-table-store]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "store_context=$(grep -a -F -c '[m5-selector-store-context]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "producer=$(grep -a -F -c '[m5-selector-producer]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "input=$(grep -a -F -c '[m5-selector-input]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "source=$(grep -a -F -c '[m5-selector-source]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "setup=$(grep -a -F -c '[m5-selector-setup-contract]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "store_entry=$(grep -a -F -c '[m5-selector-store-entry]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "caller=$(grep -a -F -c '[m5-selector-caller]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "precall=$(grep -a -F -c '[m5-selector-precall]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "ai_boundary=$(grep -a -F -c '[m5-selector-ai-boundary]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "crash=$(grep -a -F -c '[CRASH]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "abort=$(grep -a -F -c '[ABORT]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' '--- selector lines ---'
  grep -a -E '\[m5-selector-(route|mixer|tick|table-selection|table-store|store-context|producer|input|source|setup-contract|store-entry|caller|precall|ai-boundary)\]' "$OUT/port.log" | head -120 || true
} > "$OUT/summary.txt"
