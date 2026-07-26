#!/bin/bash
# Unattended driver. Run from a Terminal INSIDE the logged-in desktop session:
#   caffeinate -dis tools/agent/loop.sh
# Each iteration is a fresh context; state lives in the docs (CURRENT-TRUTH,
# NEXT.md), which is exactly what they were built for. Usage-limit windows
# become sleeps, not handoffs.
#
# Env: ITER_CAP (default 40), SLEEP_ON_LIMIT (default 1800s), MAX_LIMIT_WAITS (12),
#      LOOP_MODEL (default sonnet), MAX_NO_CONTRACT (default 2)
set -u
cd "$(dirname "$0")/../.."
AG=scratch/agent
mkdir -p "$AG"
ITER_CAP="${ITER_CAP:-40}"
SLEEP_ON_LIMIT="${SLEEP_ON_LIMIT:-1800}"
MAX_LIMIT_WAITS="${MAX_LIMIT_WAITS:-12}"
MAX_NO_CONTRACT="${MAX_NO_CONTRACT:-2}"
MAX_SUBSTITUTED="${MAX_SUBSTITUTED:-2}"

# Choose the model EXPLICITLY. Without this the loop silently inherits whatever
# `model` sits in ~/.claude/settings.json — which on 2026-07-26 was "fable", the
# most expensive tier, for all 40 unattended iterations. Most of an iteration is
# mechanical (grep, instrument, rebuild, capture, reconcile, write the ledger);
# the investigative discipline lives in ITERATION.md and the Stop gate, not in
# raw model strength. Override per run: LOOP_MODEL=opus tools/agent/loop.sh
LOOP_MODEL="${LOOP_MODEL:-sonnet}"

log() { echo "[loop] $*" | tee -a "$AG/loop.log"; }

notify_blocked() {
  osascript -e 'display notification "RS64 agent blocked - see scratch/agent/BLOCKED.md" with title "RS64 loop"' 2>/dev/null
  log "BLOCKED - fix it, delete $AG/BLOCKED.md, rerun."
}

log "run starting $(date) — model=$LOOP_MODEL cap=$ITER_CAP"

n=0
waits=0
nocontract=0
subs=0
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
  rm -f "$AG/OUTCOME" "$AG/SUBSTITUTION.md"
  touch "$AG/ITER_START_MARK"   # the gate dates run artifacts against this
  echo 0 > "$AG/.stop_blocks"
  git rev-parse HEAD > "$AG/ITER_START_HEAD" 2>/dev/null

  out="$(claude -p "$(cat tools/agent/ITERATION.md)" \
         --model "$LOOP_MODEL" \
         --permission-mode acceptEdits \
         --output-format json 2>&1)"
  rc=$?
  printf '%s\n' "$out" >> "$AG/loop.log"

  # A spend/quota CAP is not a window that reopens. Sleeping on it wastes
  # MAX_LIMIT_WAITS * SLEEP_ON_LIMIT (6 hours by default) retrying something
  # that cannot succeed until a human raises the cap. Distinguish it from the
  # transient limits, which really are just windows.
  #
  # ORDER MATTERS. With extra usage OFF, the normal subscription-limit message
  # is what the loop is SUPPOSED to sleep through, and it often carries upsell
  # wording ("upgrade your plan") that would otherwise read as a hard cap. A
  # stated reset time means the window reopens by itself: always transient.
  if printf '%s' "$out" | grep -qiE 'resets? at|resets? in|try again (later|at)|limit will reset'; then
    : # falls through to the transient handler below - sleep, do not stop
  elif printf '%s' "$out" | grep -qiE 'monthly spend limit|spend limit|credit balance|insufficient quota'; then
    { echo "# Hard spend/quota cap reached, $(date)"; echo;
      echo "This is NOT a transient rate limit and sleeping will not clear it."
      echo "Raise or reset the cap (claude.ai/settings/usage), then delete this"
      echo "file and rerun the loop."; echo;
      echo "Last claude output:"; printf '%s\n' "$out" | tail -20; } > "$AG/BLOCKED.md"
    log "HARD CAP reached - not retryable, stopping"
    notify_blocked
    exit 2
  fi

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

  # An iteration that ends still WORKING never met the exit contract: the Stop
  # gate released it at its block cap, or the CLI died mid-turn. It committed
  # nothing. The first such iteration (2026-07-26, 11:37-11:55) burned 18
  # minutes silently because the loop just started the next one. Never again.
  if [ "$status" != "DONE" ]; then
    nocontract=$((nocontract+1))
    log "WARNING: iteration $n ended STATUS=${status:-unset} — exit contract NOT met, nothing committed ($nocontract/$MAX_NO_CONTRACT)"
    if [ "$nocontract" -ge "$MAX_NO_CONTRACT" ]; then
      { echo "# $nocontract consecutive iterations ended without meeting the exit contract, $(date)"; echo;
        echo "STATUS was '${status:-unset}', not DONE, and no commit landed. The agent is"
        echo "either running out of turns before it can finish a work unit, or the unit at"
        echo "the top of docs/CURRENT-TRUTH.md 'Next steps' is too large for one iteration."
        echo "Look at scratch/agent/NEXT.md and split it, then delete this file and rerun."; echo;
        echo "Last claude output:"; printf '%s\n' "$out" | tail -30; } > "$AG/BLOCKED.md"
      notify_blocked
      exit 2
    fi
  else
    nocontract=0
  fi

  # Consecutive substitutions mean the environment is not letting the project
  # advance, and every extra iteration costs full price to produce ledger churn.
  # This counter lives in the loop's own memory, not in scratch/ — the agent
  # being metered must not be able to reset its own meter.
  outcome="$(tr -d '[:space:]' < "$AG/OUTCOME" 2>/dev/null)"
  log "iteration $n outcome=${outcome:-unset}"
  if [ "$outcome" = "SUBSTITUTED" ]; then
    subs=$((subs+1))
    log "WARNING: work unit substituted ($subs/$MAX_SUBSTITUTED consecutive)"
    if [ "$subs" -ge "$MAX_SUBSTITUTED" ]; then
      { echo "# $subs consecutive iterations could not run their work unit, $(date)"; echo;
        echo "The loop stopped itself rather than keep paying full price for"
        echo "documentation housekeeping. The agent's own account of what blocked"
        echo "it, including the experiment it says would refute that explanation:"; echo;
        cat "$AG/SUBSTITUTION.md" 2>/dev/null; echo;
        echo "Decide: remove the blocker, refute it, or re-scope the work unit in"
        echo "scratch/agent/NEXT.md. Then delete this file and rerun."; } > "$AG/BLOCKED.md"
      notify_blocked
      exit 2
    fi
  else
    subs=0
  fi
done
log "iteration cap ($ITER_CAP) reached $(date)"
