#!/bin/zsh
# s4793: state-gated sample. Up to 3 runs; sample when width=640 and update_screen counter static >=10 s.
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/soak_results/s4793"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 2
: > "$OUT/summary.txt"
for run in 1 2 3; do
  pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1
  L="$OUT/game$run.log"
  echo "run$run start load=$(sysctl -n vm.loadavg)" >> "$OUT/summary.txt"
  env ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_DLWALK=1 ROGUESQ_LOG_PHASE=1 ./RogueSquadron64Recomp >"$L" 2>&1 &
  pid=$!
  t=0; last=""; static=0; sampled20=0; froze=0; seen640=0; t640=-1
  while (( t < 200 )) && kill -0 $pid 2>/dev/null; do
    sleep 2; t=$((t+2))
    line=$(grep "^\[vi\] update_screen" "$L" | tail -1)
    cnt=$(print -r -- "$line" | sed -n 's/.*#\([0-9][0-9]*\).*/\1/p')
    w=$(print -r -- "$line" | sed -n 's/.*width=\([0-9][0-9]*\).*/\1/p')
    if [[ "$w" == 640 && $seen640 == 0 ]]; then seen640=1; t640=$t; fi
    if (( t >= 20 && sampled20 == 0 )); then sampled20=1; sample $pid 3 -file "$OUT/run${run}_20s.txt" >/dev/null 2>&1; echo "run$run t=20 cnt=$cnt w=$w" >> "$OUT/summary.txt"; t=$((t+3)); fi
    if [[ "$cnt" == "$last" ]]; then static=$((static+2)); else static=0; last=$cnt; fi
    if [[ "$w" == 640 && $static -ge 10 ]]; then
      echo "run$run FROZEN t=$t cnt=$cnt w=$w load=$(sysctl -n vm.loadavg)" >> "$OUT/summary.txt"
      sample $pid 5 -file "$OUT/run${run}_stall.txt" >/dev/null 2>&1
      froze=1; break
    fi
    if [[ -n "$w" && "$w" != 640 && $seen640 == 1 ]]; then echo "run$run exited640 t=$t (640 seen at $t640) w=$w cnt=$cnt" >> "$OUT/summary.txt"; break; fi
  done
  alive=$(kill -0 $pid 2>/dev/null && echo yes || echo no)
  echo "run$run end t=$t froze=$froze alive=$alive seen640=$seen640" >> "$OUT/summary.txt"
  kill -KILL $pid 2>/dev/null; pkill -KILL -x RogueSquadron64Recomp
  (( froze )) && break
done
echo DONE >> "$OUT/summary.txt"
