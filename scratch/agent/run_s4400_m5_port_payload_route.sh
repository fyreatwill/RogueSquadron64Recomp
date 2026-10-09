#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4400_m5_port_payload_route"
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
  printf '%s\n' "filter_join=$(grep -a -F -c '[m5-filter-join]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "input_dma=$(grep -a -F -c '[m5-input-dma]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "task_rows=$(grep -a -F -c '[audtask-dma-row]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "task_joins=$(grep -a -F -c '[audtask-join]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "crash=$(grep -a -F -c '[CRASH]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "abort=$(grep -a -F -c '[ABORT]' "$OUT/port.log" 2>/dev/null || true)"
  printf '%s\n' "--- phase-family hashes ---"
  awk '
    /\[m5-filter-join\] edge=call/ {
      ph=or=src=out="";
      for (i=1;i<=NF;i++) {
        if ($i ~ /^phase=/) ph=$i;
        if ($i ~ /^origin=/) or=$i;
        if ($i ~ /^source_hash=/) src=$i;
        if ($i ~ /^output_hash=/) out=$i;
      }
      if (ph != "" && or != "" && src != "" && out != "") print ph, or, src, out;
    }
  ' "$OUT/port.log" | sort -u | head -80
  printf '%s\n' "--- phase-task families ---"
  awk '
    /\[audtask-dma-row\]/ {
      ph=or=ptr=fnv="";
      for (i=1;i<=NF;i++) {
        if ($i ~ /^phase=/) ph=$i;
        if ($i ~ /^origin=/) or=$i;
        if ($i ~ /^data_ptr=/) ptr=$i;
        if ($i ~ /^source_fnv=/) fnv=$i;
      }
      if (ph != "" && or != "" && ptr != "" && fnv != "") print ph, or, ptr, fnv;
    }
  ' "$OUT/port.log" | sort -u | head -80
} > "$OUT/summary.txt"
