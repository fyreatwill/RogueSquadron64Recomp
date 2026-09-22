#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s3436_m5_port_frequency_contract_paired_retry
mkdir -p "$OUT"
pkill -KILL -x RogueSquadron64Recomp 2>/dev/null || true
sleep 2
cd "$ROOT/build" || exit 2
common=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a,75:start,90:a'
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_INIT_VOICE_SAMPLE=1
  ROGUESQ_LOG_M5_SELECTOR_AI_BOUNDARY=1 ROGUESQ_LOG_M5_SELECTOR_AI_RETURN=1
  ROGUESQ_LOG_M5_FREQUENCY_CONTRACT=1 ROGUESQ_LOG_M5_AI_STATE=1
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1
  ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1
  ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_PCM_WRITER=1
  ROGUESQ_LOG_M5_AUDIO_DRAIN=1 ROGUESQ_LOG_PCM_BOUNDARY=1
  ROGUESQ_LOG_M5_AUDIO_HOST=1
)
run_arm() {
  local arm="$1" audio="$2"
  env "${common[@]}" ROGUESQ_AUDIO_UCODE="$audio" ./RogueSquadron64Recomp >"$OUT/$arm.log" 2>&1 &
  RUN_PID=$!
}
run_arm real 1
REAL_PID=$RUN_PID
sleep 3
run_arm silent 0
SILENT_PID=$RUN_PID
for tick in {1..240}; do
  real_done=0 silent_done=0
  grep -a -q '\[phase\].*width=512\|vi_width=512' "$OUT/real.log" 2>/dev/null && real_done=1
  grep -a -q '\[phase\].*width=512\|vi_width=512' "$OUT/silent.log" 2>/dev/null && silent_done=1
  if (( real_done && silent_done )); then break; fi
  if ! kill -0 "$REAL_PID" 2>/dev/null && ! kill -0 "$SILENT_PID" 2>/dev/null; then break; fi
  sleep 0.25
done
kill -KILL "$REAL_PID" "$SILENT_PID" 2>/dev/null || true
wait "$REAL_PID" 2>/dev/null || true
wait "$SILENT_PID" 2>/dev/null || true
pkill -KILL -x RogueSquadron64Recomp 2>/dev/null || true
for arm in real silent; do
  {
    printf 'arm=%s\n' "$arm"
    grep -a -E '\[(phase|m5-frequency-contract|m5-rsp|m5-pcm|m5-audio-drain|m5-audio-drain-raw|m5-audio-host|pcm-boundary-(source|consumer)|audtask-image-stage|CRASH|ABORT)' "$OUT/$arm.log" | head -800 || true
    printf '\ncounts\n'
    for marker in phase m5-frequency-contract m5-rsp m5-pcm m5-audio-drain m5-audio-drain-raw m5-audio-host pcm-boundary-source pcm-boundary-consumer audtask-image-stage CRASH ABORT; do
      printf '%s=' "$marker"
      grep -a -c "\[$marker\]" "$OUT/$arm.log" || printf '0\n'
    done
  } >"$OUT/$arm-results.txt"
done
