#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=s2328_m5_drain_tick_validation
LOG="$ROOT/scratch/agent/${TAG}_queue.log"

cd "$ROOT" || exit 2
zsh scratch/agent/run_s2328_m5_drain_tick_ab.sh "$TAG" > "$LOG" 2>&1 &
pid=$!
deadline=$((SECONDS + 540))
while (( SECONDS < deadline )); do
    if ! kill -0 "$pid" 2>/dev/null; then break; fi
    sleep 2
done
if kill -0 "$pid" 2>/dev/null; then
    /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
    kill -9 "$pid" 2>/dev/null || true
    exit 124
fi
wait "$pid" 2>/dev/null
rc=$?
(( rc == 0 )) || exit "$rc"

driver="$ROOT/scratch/agent/$TAG/driver.log"
grep -a -q 'verdict=H-DrainRedundant' "$driver" || exit 1
for name in stub image_tick_on image_tick_off; do
    log="$ROOT/scratch/agent/$TAG/$name.log"
    test -f "$log" || exit 1
    grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" || exit 1
    if grep -a -q '^\[CRASH\]\|^\[ABORT\]' "$log"; then exit 1; fi
done
exit 0
