#!/bin/zsh
# Usage: tools/verify_sdl_quit.sh <binary-in-build/> [run_secs]
# SDL turns SIGTERM into SDL_QUIT, so this exercises the poll_input quit path.
# Reports whether a crash/abort follows "[main] SDL_QUIT received" (s5381 quick_exit check).
cd "$(dirname "$0")/../build" || exit 2
b=$1; secs=${2:-25}; log=/tmp/sdlquit_$b.log
./$b > $log 2>&1 &
pid=$!
sleep $secs
kill -TERM $pid
sleep 8
if kill -0 $pid 2>/dev/null; then echo "$b: still alive after SIGTERM"; kill -9 $pid; fi
wait $pid 2>/dev/null; echo "$b: exit rc=$?"
grep -cE "SDL_QUIT received" $log | sed 's/^/quit-lines: /'
grep -nE "CRASH|SIGABRT|terminate" $log | tail -3
