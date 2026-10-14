#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/soak_results/s4849_m5_a10_guard_qualification"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 2

BASE=(
  ROGUESQ_SPIN_YIELD=1
  ROGUESQ_LLE_FORCE=1
  ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1
  ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512
  PROBE_PHASE_WIDTH=1024
  PROBE_PHASE_TIMEOUT=110
  PROBE_KEYS_FROM_PHASE=1
  PROBE_LEAVE_OK=1
  ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_M5_A10=1
  ROGUESQ_LOG_PCM_BOUNDARY=1
  ROGUESQ_AUDIO_UCODE=1
)

typeset -A pid
for arm in default rollback; do
  extra=()
  if [[ "$arm" == rollback ]]; then
    extra+=(ROGUESQ_A10_GUARD_OFF=1)
  else
    extra+=(ROGUESQ_A10_GUARD_OFF=0)
  fi
  env "${BASE[@]}" "${extra[@]}" ./RogueSquadron64Recomp >"$OUT/$arm.log" 2>&1 &
  pid[$arm]=$!
done

sleep 180
for arm in default rollback; do
  kill -KILL "${pid[$arm]}" 2>/dev/null || true
done
for arm in default rollback; do
  wait "${pid[$arm]}" 2>/dev/null || true
done

{
  echo 'A10 same-build qualification'
  for arm in default rollback; do
    log="$OUT/$arm.log"
    printf '%s title=%s hangar=%s writer=%s guards=%s traversal=%s pcm=%s sp=%s crash=%s abort=%s last_phase=' "$arm" \
      "$(grep -a -c '^\[phase\].*vi_width=1024 .*origin=0x00790400' "$log" || true)" \
      "$(grep -a -c '^\[phase\].*vi_width=512 .*origin=0x006AB400' "$log" || true)" \
      "$(grep -a -c '^\[m5-a10-writer\]' "$log" || true)" \
      "$(grep -a -c '^\[m5-a10-guard\]' "$log" || true)" \
      "$(grep -a -c 'voice-list\|songtempo' "$log" || true)" \
      "$(grep -a -c 'pcm.*nonzero\|pcm.*nz=' "$log" || true)" \
      "$(grep -a -c 'sp-complete' "$log" || true)" \
      "$(grep -a -c '^\[CRASH\]' "$log" || true)" \
      "$(grep -a -c '^\[ABORT\]' "$log" || true)"
    grep -a '^\[phase\]' "$log" | tail -1 | cut -c1-140 || true
  done
} | tee "$OUT/verdict.txt"

for arm in default rollback; do
  log="$OUT/$arm.log"
  grep -aE '^\[(m5-a10|phase|pcm|CRASH|ABORT)' "$log" | tail -240 >"$OUT/$arm.summary" || true
done

exit 0
