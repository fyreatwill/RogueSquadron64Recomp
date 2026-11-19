#!/bin/zsh
# s7616 RQ runtime witness (non-intrusive): boot the game normally, macOS `sample` its threads for SECS s, then
# tools/s7616_rq_census.py --witness-sample parses per-thread call trees: every RDRAM-reader frame must sit under the
# Gfx Thread (or the gated RS64 RDP async worker); controls = RT64's worker bodies seen in their own threads.
set -u
ROOT="$(pwd)"; OUT="$ROOT/scratch/s7616"; mkdir -p "$OUT"; cd "$ROOT/build" || exit 2
env ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_LOG_PHASE=1 ${=EXTRA_ENV:-} ./RogueSquadron64Recomp >"$OUT/game_sample${TAG:-}.log" 2>&1 &
pid=$!
sleep ${WARM:-20}
sample $pid ${SECS:-30} 1 -mayDie -file "$OUT/sample${TAG:-}.txt" >/dev/null 2>&1
kill -KILL $pid 2>/dev/null; wait $pid 2>/dev/null
ls -la "$OUT/sample${TAG:-}.txt"
