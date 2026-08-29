#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s3143_m5_port_vi_edge"
mkdir -p "$OUT"
: > "$OUT/run.log"
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" ]]; then
  print 'missing port build or ROM' >> "$OUT/run.log"
  exit 2
fi
game_pid=""
cleanup() {
  [[ -n "$game_pid" ]] && kill -9 "$game_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
(
  cd "$BUILD"
  exec env ROGUESQ_LOG_M5_VI_EDGE=1 ROGUESQ_LOG_VI_CONTEXT_PORT=1 \
    ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 ROGUESQ_LOG_AUDIO_RETURN=1 \
    ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
    ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ./RogueSquadron64Recomp
) > "$OUT/game.log" 2>&1 &
game_pid=$!
for _ in {1..180}; do
  if grep -aq '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/game.log"; then
    break
  fi
  sleep 1
done
kill -9 "$game_pid" 2>/dev/null || true
game_pid=""
wait 2>/dev/null || true
{
  print "control=$(grep -a -c '^\[m5-vi-edge\] control=1' "$OUT/game.log" || true)"
  print "edge_target=$(grep -a -c '^\[m5-vi-edge\] control=0 target=1' "$OUT/game.log" || true)"
  print "vi_controls=$(grep -a -c '^\[vi-context-port-control\]' "$OUT/game.log" || true)"
  print "voice_controls=$(grep -a -c '^\[filter-voice-audit-control\]' "$OUT/game.log" || true)"
  print "title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/game.log" || true)"
  print "hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/game.log" || true)"
  grep -a -E '^\[(m5-vi-edge|phase|vi-context-port-control|filter-voice-audit-control|CRASH|ABORT)\]' "$OUT/game.log" | tail -80
} > "$OUT/summary.log"
if grep -aq '^\[CRASH\]\|^\[ABORT\]' "$OUT/game.log"; then
  exit 4
fi
exit 0
