#!/bin/zsh
# s7615 DQ witness: guest OSMesgQueue addresses carried by deferred external messages (external_messages queue, host producers
# VI/AI/SP/DP/SI/PI/Timer). ROGUESQ_RECV_TRACE=1 makes log_unique_mq_tag print one [hostpost] row per distinct (mq, source) at
# enqueue; offline check in tools/s7615_dq_census.py --witness: every mq is a registered/static queue, constant per source.
set -u
ROOT="$(pwd)"; OUT="$ROOT/scratch/s7615"; mkdir -p "$OUT"; cd "$ROOT/build" || exit 2
env ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_RECV_TRACE=1 \
    ./RogueSquadron64Recomp >"$OUT/witness.log" 2>&1 &
pid=$!
sleep ${WSECS:-90}
kill -KILL $pid 2>/dev/null; wait $pid 2>/dev/null
grep -a -c '^\[hostpost\]' "$OUT/witness.log"
