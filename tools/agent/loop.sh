#!/bin/bash
# Unattended driver. Run from a Terminal INSIDE the logged-in desktop session:
#   caffeinate -dis tools/agent/loop.sh
# Each iteration is a fresh context; state lives in the docs (CURRENT-TRUTH,
# NEXT.md), which is exactly what they were built for. Usage-limit windows
# become sleeps, not handoffs.
#
# Env: ITER_CAP (default 40), SLEEP_ON_LIMIT (default 1800s), MAX_LIMIT_WAITS (12)
set -u
cd "$(dirname "$0")/../.."
AG=scratch/agent
mkdir -p "$AG"
ITER_CAP="${ITER_CAP:-40}"
SLEEP_ON_LIMIT="${SLEEP_ON_LIMIT:-1800}"
MAX_LIMIT_WAITS="${MAX_LIMIT_WAITS:-12}"

log() { echo "[loop] $*" | tee -a "$AG/loop.log"; }

notify_blocked() {
  osascript -e 'display notification "RS64 agent blocked - see scratch/agent/BLOCKED.md" with title "RS64 loop"' 2>/dev/null
  log "BLOCKED - fix it, delete $AG/BLOCKED.md, rerun."
}

n=0
waits=0
while [ "$n" -lt "$ITER_CAP" ]; do

  if [ -f "$AG/BLOCKED.md" ]; then
    notify_blocked
    exit 2
  fi

  if ! tools/agent/preflight.sh 2>&1 | tee -a "$AG/loop.log" | grep -q '^\[preflight\] OK'; then
    { echo "# Blocked by preflight, $(date)"; echo; tools/agent/preflight.sh 2>&1; } > "$AG/BLOCKED.md"
    notify_blocked
    exit 2
  fi

  n=$((n+1))
  log "iteration $n starting $(date)"
  echo WORKING > "$AG/STATUS"
  echo 0 > "$AG/.stop_blocks"
  git rev-parse HEAD > "$AG/ITER_START_HEAD" 2>/dev/null

  out="$(claude -p "$(cat tools/agent/ITERATION.md)" \
         --permission-mode acceptEdits \
         --output-format json 2>&1)"
  rc=$?
  printf '%s\n' "$out" >> "$AG/loop.log"

  if [ $rc -ne 0 ] || printf '%s' "$out" | grep -qiE 'usage limit|rate.?limit|overloaded|resets at'; then
    waits=$((waits+1))
    if [ "$waits" -gt "$MAX_LIMIT_WAITS" ]; then
      { echo "# Loop gave up after $waits consecutive limit/error waits, $(date)"; echo;
        echo "Last claude output (rc=$rc):"; printf '%s\n' "$out" | tail -40; } > "$AG/BLOCKED.md"
      notify_blocked
      exit 2
    fi
    log "limit or error (rc=$rc), wait $waits/$MAX_LIMIT_WAITS - sleeping ${SLEEP_ON_LIMIT}s"
    n=$((n-1))          # a window we never got to work in does not burn an iteration
    sleep "$SLEEP_ON_LIMIT"
    continue
  fi
  waits=0

  status="$(tr -d '[:space:]' < "$AG/STATUS" 2>/dev/null)"
  log "iteration $n finished $(date) STATUS=${status:-unset} HEAD=$(git rev-parse --short HEAD 2>/dev/null)"
  if [ "$status" = "BLOCKED" ]; then
    [ -s "$AG/BLOCKED.md" ] || echo "# Agent set STATUS=BLOCKED without writing this file, $(date)" > "$AG/BLOCKED.md"
    notify_blocked
    exit 2
  fi
done
log "iteration cap ($ITER_CAP) reached $(date)"
