#!/bin/zsh
# s7616 RQ witness: boot the game normally (title/attract), attach lldb after WARM s, count reader/control hits per thread.
set -u
ROOT="$(pwd)"; OUT="$ROOT/scratch/s7616"; mkdir -p "$OUT"; cd "$ROOT/build" || exit 2
env ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_LOG_PHASE=1 ./RogueSquadron64Recomp >"$OUT/game.log" 2>&1 &
pid=$!
sleep ${WARM:-8}
lldb --batch -o "command script import ../tools/s7616_rq_witness.py" -o "rq_run ${WSECS:-60} $OUT/witness.txt $pid" >"$OUT/lldb.log" 2>&1 &
lp=$!
for i in $(seq 1 $(( (${WSECS:-60} + 240) / 2 ))); do sleep 2; kill -0 $lp 2>/dev/null || break; done
kill -KILL $lp 2>/dev/null; kill -KILL $pid 2>/dev/null; wait $pid 2>/dev/null
grep -E '^attach|STOP|ended|^rows' "$OUT/lldb.log"; cat "$OUT/witness.txt"
