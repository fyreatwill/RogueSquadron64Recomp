#!/bin/bash
# Stop hook: gates the end of an autonomous iteration against the exit contract
# in tools/agent/ITERATION.md. Deterministic on purpose — it checks the artifacts
# (STATUS file, docs, commit), not the agent's account of them.
#
# stdin : hook JSON  ({session_id, stop_hook_active, ...})
# stdout: {"decision":"block","reason":"..."} to keep the turn going, or nothing to allow.
set -u
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0

AG=scratch/agent
mkdir -p "$AG"
input="$(cat)"

# --- loop guard --------------------------------------------------------------
# The counter lives OUTSIDE the repo, keyed by session id. A first smoke test
# showed the agent editing an in-repo counter to force the gate open; the gate
# must not be defeasible by the thing it is gating.
sid="$(printf '%s' "$input" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("session_id","nosession"))
except Exception: print("nosession")' 2>/dev/null || echo nosession)"
CFILE="${TMPDIR:-/tmp}/.rs64-stopgate-${sid}"
BLOCK_CAP="${STOP_GATE_BLOCK_CAP:-8}"
count=$(cat "$CFILE" 2>/dev/null || echo 0)
case "$count" in ''|*[!0-9]*) count=0 ;; esac

allow() { rm -f "$CFILE"; exit 0; }
block() {
  echo "$((count + 1))" > "$CFILE"
  python3 - "$1" <<'PY'
import json, sys
print(json.dumps({"decision": "block", "reason": sys.argv[1]}))
PY
  exit 0
}

# Hard release: never trap a turn forever.
[ "$count" -ge "$BLOCK_CAP" ] && allow

# Stuck detection: two blocks before the cap, redirect to a clean BLOCKED exit.
if [ "$count" -ge $((BLOCK_CAP - 2)) ]; then
  block "You have been blocked from stopping $count times without meeting the exit contract, which means you are stuck. Stop retrying the current approach. Write scratch/agent/BLOCKED.md (what you need, from whom, what you already tried), commit any outstanding changes, write BLOCKED to scratch/agent/STATUS, and then stop."
fi

# --- condition 1: STATUS ------------------------------------------------------
status="$(tr -d '[:space:]' < "$AG/STATUS" 2>/dev/null)"
case "$status" in
  DONE|BLOCKED) ;;
  *) block "Exit contract unmet: scratch/agent/STATUS is '${status:-missing}', not DONE or BLOCKED. Finish the current work unit, update PORTING-STATE.md and docs/CURRENT-TRUTH.md, rewrite scratch/agent/NEXT.md, commit, then write DONE (or BLOCKED plus scratch/agent/BLOCKED.md) to scratch/agent/STATUS." ;;
esac

# --- working tree must be committed (both paths) ------------------------------
# --ignore-submodules=dirty: lib/ is permanently dirty by design (the patches
# live in the working tree); submodule content is tracked via submodule-patches/.
dirty="$(git status --porcelain --ignore-submodules=dirty -- . ':(exclude)scratch' ':(exclude)build' 2>/dev/null | head -5)"
if [ -n "$dirty" ]; then
  block "Exit contract unmet: uncommitted changes remain outside scratch/ and build/:
$dirty
Commit them (git add -A && git commit -m 'iter: <one-line finding>'). If you edited anything under lib/, first run ./submodule-patches/export.sh so the submodule patches do not go stale."
fi

# --- BLOCKED: needs a usable write-up, but not a commit it has nothing for ----
if [ "$status" = "BLOCKED" ]; then
  [ -s "$AG/BLOCKED.md" ] || block "Exit contract unmet: STATUS is BLOCKED but scratch/agent/BLOCKED.md is missing or empty. Write it: what you need, from whom, and what you already tried — specific enough that a human can act in 2 minutes."
  allow
fi

# --- DONE: a commit landed this iteration, and it moved the ledger ------------
head_now="$(git rev-parse HEAD 2>/dev/null)"
head_start="$(cat "$AG/ITER_START_HEAD" 2>/dev/null || echo '')"
if [ -n "$head_start" ] && [ "$head_now" = "$head_start" ]; then
  block "Exit contract unmet: no commit landed this iteration (HEAD is unchanged at ${head_now:0:8}). Run: git add -A && git commit -m 'iter: <one-line finding>'."
fi

range="${head_start:+$head_start..HEAD}"
touched="$(git diff --name-only ${range:-HEAD~1..HEAD} 2>/dev/null)"
if ! printf '%s\n' "$touched" | grep -q '^PORTING-STATE\.md$'; then
  block "Exit contract unmet: this iteration's commits do not touch PORTING-STATE.md. Append a dated session entry: what ran, what it showed, what it rules out — including failed experiments. Then commit."
fi
if ! printf '%s\n' "$touched" | grep -q '^docs/CURRENT-TRUTH\.md$'; then
  block "Exit contract unmet: this iteration's commits do not touch docs/CURRENT-TRUTH.md. Update it: reorder Next steps, and move any overturned conclusion into the superseded section with why it was believable. Then commit."
fi

[ -s "$AG/NEXT.md" ] || block "Exit contract unmet: scratch/agent/NEXT.md is missing or empty. Write the single next work unit for the following iteration: hypotheses, exact commands, and the discriminating outcomes."

allow
