#!/bin/zsh
# LLE desktop soak. Usage: tools/lle_soak.sh [seconds] [logfile]
#
# macOS has no `timeout`; use a TERM watchdog, then summarize the markers that
# define the current LLE acceptance check. Extra ROGUESQ_* variables are
# inherited, so e.g. ROGUESQ_LLE_UNGATED=1 tools/lle_soak.sh 300 cine.log
# exercises the cinematic path without changing this script.
SECS=${1:-300}
LOG=${2:-/tmp/lle_soak.log}
ROOT="$(cd "$(dirname "$0")/.." && pwd)" || exit 1
BIN="${RS64_BINARY:-$ROOT/build/RogueSquadron64Recomp}"

if [[ ! -x "$BIN" ]]; then
    print -u2 "LLE soak: executable not found or not executable: $BIN"
    exit 2
fi

mkdir -p "${LOG:h}"
print "LLE soak: ${SECS}s, binary=$BIN, log=$LOG"
ROGUESQ_LLE_FORCE=1 ROGUESQ_TRACE_DISPATCH=1 "$BIN" > "$LOG" 2>&1 &
PID=$!
( sleep "$SECS"; kill -TERM "$PID" 2>/dev/null ) &
WATCHDOG=$!

wait "$PID"
APP_EXIT=$?
kill "$WATCHDOG" 2>/dev/null || true
wait "$WATCHDOG" 2>/dev/null || true

count() {
    grep -cE "$1" "$LOG" 2>/dev/null || true
}

UNHANDLED=$(count 'UnhandledJumpTarget|exitReason=3')
DROPS=$(count '\[defer-drop\]')
DMEM_RACES=$(count '\[dmem-race\]')
TASKS=$(count '\[lle task\]')
COMMITS=$(count '\[defer-commit')

print "LLE soak summary: app_exit=$APP_EXIT tasks=$TASKS rdp_commits=$COMMITS unhandled=$UNHANDLED defer_drops=$DROPS dmem_races=$DMEM_RACES"
if grep -q 'SDL_Init failed: The video driver did not add any displays' "$LOG"; then
    print -u2 'LLE soak did not start: no SDL display is available in this session.'
    exit 3
fi

# A watchdog TERM is the expected successful end of a soak. Preserve any other
# early process exit for automation/CI callers.
if [[ $APP_EXIT -ne 0 && $APP_EXIT -ne 143 ]]; then
    exit "$APP_EXIT"
fi
