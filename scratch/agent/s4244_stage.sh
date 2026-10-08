#!/bin/zsh
# s4235: fresh-save hangar PCM census. Shifted keys (s4228 recipe) + PCM instruments; up to 4 runs until one reaches VI 512.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/soak_results/s4244_stage"
mkdir -p "$OUT"
for i in 1; do
  rm -rf "$ROOT/build/saves"
  ( cd "$ROOT/build" || exit 2
    exec env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      ROGUESQ_AUTOPILOT='40:start,44:start,48:start,52:start,56:a,60:a,64:start,68:a' \
      ROGUESQ_LOG_ALL=1 ROGUESQ_S4239=1 ROGUESQ_S4242_CTRL=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_S4220=1 ROGUESQ_LOG_S4222=1 \
      ./RogueSquadron64Recomp ) > "$OUT/run$i.log" 2>&1 &
  pid=$!
  for _ in {1..330}; do
    kill -0 $pid 2>/dev/null || break
    grep -aq 's4242-ctrl] n=1712 ' "$OUT/run$i.log" && break
    sleep 1
  done
  kill -KILL $pid 2>/dev/null; pkill -KILL -x RogueSquadron64Recomp 2>/dev/null; wait 2>/dev/null; sleep 2
  grep -aq 'vi_width=512' "$OUT/run$i.log" && break
done
