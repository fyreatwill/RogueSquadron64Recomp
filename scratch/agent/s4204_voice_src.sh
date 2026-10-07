#!/bin/zsh
# s4204: voice sample-source census at musyxKeyOnVoice tail (s4203 recipe + ROGUESQ_LOG_M5_VOICE_SRC=1).
# Positive control: ctl_nz (param-struct hash) must be >0 in every [m5-voice-src] row.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/soak_results/s4204_voice_src"
mkdir -p "$OUT"
pids=()
cleanup() { for p in $pids; do kill -KILL "$p" 2>/dev/null; done; }
trap cleanup EXIT INT TERM

(
  cd "$ROOT/build" || exit 2
  exec env ROGUESQ_LLE_FORCE=1 \
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
    ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 \
    PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_VOICE_SRC=1 ROGUESQ_AUDIO_UCODE=1 \
    ROGUESQ_LOG_M5_KEYON_CENSUS=1 \
    ./RogueSquadron64Recomp
) > "$OUT/default.log" 2>&1 &
pids+=($!)

for _ in {1..200}; do
  alive=0; for p in $pids; do kill -0 "$p" 2>/dev/null && alive=1; done
  (( alive )) || break
  sleep 1
done
cleanup
wait 2>/dev/null
{
  echo "== default"
  grep -a -c 'vi_width=1024 .*origin=0x00790400' "$OUT/default.log" | sed 's/^/title: /'
  grep -a -c 'vi_width=512 .*origin=0x006AB400' "$OUT/default.log" | sed 's/^/hangar: /'
  grep -a -c '^\[m5-voice-src\]' "$OUT/default.log" | sed 's/^/voice-src rows: /'
  for ph in 3 4 5; do grep -a "^\[m5-voice-src\] phase=$ph " "$OUT/default.log" | tail -1 | cut -c1-520; done
  grep -a -E '^\[CRASH\]|crash' "$OUT/default.log" | head -2
} > "$OUT/summary.txt"
cat "$OUT/summary.txt"
