#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s3436_m5_port_frequency_contract
mkdir -p "$OUT"
cd "$ROOT/build" || exit 2
common=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a,75:start,90:a'
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_INIT_VOICE_SAMPLE=1
  ROGUESQ_LOG_M5_SELECTOR_AI_BOUNDARY=1
  ROGUESQ_LOG_M5_SELECTOR_AI_RETURN=1
  ROGUESQ_LOG_M5_FREQUENCY_CONTRACT=1
  ROGUESQ_LOG_M5_AI_STATE=1
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1
  ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1
  ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_PCM_WRITER=1
)
env "${common[@]}" ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp >"$OUT/run.log" 2>&1 &
PID=$!
for tick in {1..240}; do
  if grep -a -q '\[phase\].*width=512\|vi_width=512' "$OUT/run.log" 2>/dev/null; then
    break
  fi
  if ! kill -0 "$PID" 2>/dev/null; then break; fi
  sleep 0.25
done
kill -KILL "$PID" 2>/dev/null || true
wait "$PID" 2>/dev/null || true
{
  grep -a -E '\[(phase|m5-frequency-contract|m5-rsp|m5-pcm|audtask-image-stage|CRASH|ABORT)' "$OUT/run.log" | head -400 || true
  printf '\ncounts\n'
  for marker in phase m5-frequency-contract m5-rsp m5-pcm audtask-image-stage CRASH ABORT; do
    printf '%s=' "$marker"
    grep -a -c "\[$marker\]" "$OUT/run.log" || printf '0\n'
  done
} >"$OUT/results.txt"
