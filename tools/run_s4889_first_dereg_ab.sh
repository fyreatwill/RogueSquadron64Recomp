#!/bin/zsh
set -u
ROOT=${0:A:h:h}
OUT="$ROOT/scratch/agent/soak_results/s4889_first_dereg"
BUILD="$ROOT/build"
mkdir -p "$OUT"
: > "$OUT/default.log"
: > "$OUT/rollback.log"

COMMON=(
  ROGUESQ_LOG_S4700_CB=1
  ROGUESQ_LOG_SP_TASKS=1
  ROGUESQ_LOG_M5_ROUTE_ORDER=1
  ROGUESQ_LOG_PCM_BOUNDARY=1
  ROGUESQ_LOG_PCM_SANITY=1
  ROGUESQ_S4562_PAUSE=0
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
  ROGUESQ_AUDIO_UCODE=1
)

launch() {
  local name=$1 arm=$2
  ( cd "$BUILD" && exec env "${COMMON[@]}" ROGUESQ_S4889_FIRST_DEREG="$arm" ./RogueSquadron64Recomp ) > "$OUT/$name.log" 2>&1 &
  print $!
}

default_pid=$(launch default 1)
rollback_pid=$(launch rollback 0)
trap 'kill -KILL "$default_pid" "$rollback_pid" 2>/dev/null || true; wait "$default_pid" 2>/dev/null || true; wait "$rollback_pid" 2>/dev/null || true' EXIT INT HUP TERM

for _ in {1..480}; do
  if grep -a -q 'vi_width=512 .*origin=0x006AB400' "$OUT/default.log" &&
     grep -a -q 'vi_width=512 .*origin=0x006AB400' "$OUT/rollback.log"; then
    break
  fi
  sleep 0.25
done
kill -KILL "$default_pid" "$rollback_pid" 2>/dev/null || true
wait "$default_pid" 2>/dev/null || true
wait "$rollback_pid" 2>/dev/null || true
trap - EXIT INT HUP TERM

for arm in default rollback; do
  log="$OUT/$arm.log"
  {
    print "[$arm] first_dereg=$(grep -a -F -c '[s4889] first-gate-zero-dereg' "$log" || true)"
    print "[$arm] synth_entries=$(grep -a -F -c '[s4700-cb] synth-enter' "$log" || true) cb_dereg=$(grep -a -F -c '[s4700-cb] dereg-enter' "$log" || true)"
    print "[$arm] title=$(grep -a -F -c 'vi_width=1024' "$log" || true) hangar=$(grep -a -F -c 'vi_width=512' "$log" || true) sp=$(grep -a -F -c '[m5-route-order] edge=sp-complete-enter' "$log" || true) pcm=$(grep -a -F -c '[pcm-boundary' "$log" || true)"
    print "[$arm] crash=$(grep -a -E -c 'SIGSEGV|Segmentation fault|EXC_BAD|fatal signal|ASSERT|abort' "$log" || true)"
  } | tee "$OUT/$arm.verdict"
done
