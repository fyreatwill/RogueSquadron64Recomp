#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4766_m5_a12_second_wait"
mkdir -p "$OUT"
PIDS=()
cleanup() { for p in $PIDS; do kill -KILL "$p" 2>/dev/null; done; }
trap cleanup EXIT INT TERM

run_arm() {
  local name=$1
  local rollback=$2
  (
    cd "$ROOT/build" || exit 2
    if [[ "$rollback" == 1 ]]; then
      export ROGUESQ_AUDIO_SPIN2_YIELD=0
    fi
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 \
      ROGUESQ_AUTOPILOT='40:start,44:start,48:start,52:start,56:a,60:a,64:start,68:a' \
      ROGUESQ_AUTOPILOT_STOP_WIDTH=0 PROBE_PHASE_WIDTH=1024 \
      PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_WAIT_CONTRACT=1 \
      ROGUESQ_LOG_WAITMUSYX_SPIN2=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 \
      ./RogueSquadron64Recomp
  ) > "$OUT/$name.log" 2>&1 &
  PIDS+=($!)
}

run_arm default 0
run_arm rollback 1

for _ in {1..130}; do
  alive=0
  for p in $PIDS; do kill -0 "$p" 2>/dev/null && alive=1; done
  (( alive )) || break
  sleep 1
done
cleanup
wait 2>/dev/null

for name in default rollback; do
  log="$OUT/$name.log"
  {
    echo "== $name =="
    echo "title=$(grep -a -c 'vi_width=1024 .*origin=0x00790400' "$log" || true)"
    echo "hangar=$(grep -a -c 'vi_width=512 .*origin=0x006AB400' "$log" || true)"
    echo "wait_entry=$(grep -a -c 'edge=wait-entry' "$log" || true)"
    echo "wait_seed=$(grep -a -c 'edge=wait-seed' "$log" || true)"
    echo "wait_exit=$(grep -a -c 'edge=wait-exit' "$log" || true)"
    echo "wait_timeout=$(grep -a -c 'audio-wait-spin-timeout' "$log" || true)"
    echo "spin2=$(grep -a -c 'waitmusyx-spin2' "$log" || true)"
    echo "crash=$(grep -a -E -c '^\\[CRASH\\]|Bus error|abort' "$log" || true)"
    grep -a -E 'waitmusyx-spin2|audio-wait-(pump|spin)|vi_width=(1024|512)' "$log" | tail -20 || true
  } > "$OUT/$name.summary"
done
cat "$OUT/default.summary" "$OUT/rollback.summary"
