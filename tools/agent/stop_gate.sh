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

# Two modes:
#   (default)  Claude Code Stop hook - reads hook JSON on stdin, emits
#              {"decision":"block",...} to keep the turn going.
#   --verify   runner-agnostic post-hoc check - no stdin, prints the unmet
#              condition on stdout and exits 1. loop.sh uses this so codex,
#              grok and any other CLI are held to the same exit contract that
#              the hook enforces for Claude. Hooks are a Claude Code feature;
#              the contract is not.
VERIFY=0
if [ "${1:-}" = "--verify" ]; then VERIFY=1; input=''; else input="$(cat)"; fi
# MEASURED, do not "simplify" away: grok DOES read .claude/settings.json and
# DOES run this Stop hook (stopReason=EndTurn in a repo without the settings
# file, Cancelled with it). Unlike Claude Code it treats a hook block as a
# cancellation and aborts the whole turn instead of continuing — so the gate
# guaranteed every grok iteration died mid-thought having done nothing. For
# non-claude runners the contract is enforced by loop.sh's post-hoc
# `--verify` pass and its retry instead, which is the same contract checked a
# moment later. runner.sh exports this for those runners.
if [ "${VERIFY:-0}" != "1" ] && [ -n "${RS64_SKIP_STOP_HOOK:-}" ]; then
  exit 0
fi

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

allow() { [ "$VERIFY" = 1 ] || rm -f "$CFILE"; exit 0; }
block() {
  if [ "$VERIFY" = 1 ]; then
    printf '%s\n' "$1"
    exit 1
  fi
  echo "$((count + 1))" > "$CFILE"
  python3 - "$1" <<'PY'
import json, sys
print(json.dumps({"decision": "block", "reason": sys.argv[1]}))
PY
  exit 0
}

# Hard release: never trap a turn forever. Verification has no turn to trap,
# so it always reports the truth.
[ "$VERIFY" = 0 ] && [ "$count" -ge "$BLOCK_CAP" ] && allow

# Stuck detection: two blocks before the cap, redirect to a clean BLOCKED exit.
if [ "$VERIFY" = 0 ] && [ "$count" -ge $((BLOCK_CAP - 2)) ]; then
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
# Touching the file is not the same as adding an entry: require a NEW session
# heading in the added lines (name-only membership passed on cosmetic edits).
if ! git diff ${range:-HEAD~1..HEAD} -- PORTING-STATE.md 2>/dev/null | grep -q '^+## Session '; then
  block "Exit contract unmet: the PORTING-STATE.md change adds no new '## Session N (date) — ...' heading. Append a dated session entry (what ran, what it showed, what it rules out — including failed experiments), then commit."
fi
if ! printf '%s\n' "$touched" | grep -q '^docs/CURRENT-TRUTH\.md$'; then
  block "Exit contract unmet: this iteration's commits do not touch docs/CURRENT-TRUTH.md. Update it: reorder Next steps, and move any overturned conclusion into the superseded section with why it was believable. Then commit."
fi

[ -s "$AG/NEXT.md" ] || block "Exit contract unmet: scratch/agent/NEXT.md is missing or empty. Write the single next work unit for the following iteration: hypotheses, exact commands, and the discriminating outcomes."

# NEXT.md must be THIS iteration's plan, not a stale leftover — the exit
# contract says "rewrite", but non-emptiness alone let stale plans pass (and a
# stale plan cost s248 a whole option built on an item closed 31 sessions
# earlier).
if [ -f "$AG/ITER_START_MARK" ] && [ "$AG/NEXT.md" -ot "$AG/ITER_START_MARK" ]; then
  block "Exit contract unmet: scratch/agent/NEXT.md predates this iteration. Rewrite it now: the single next work unit, exact commands, expected discriminating outcomes, and its 'HYPOTHESIS-ID: <slug>' line."
fi
# Rule 8 needs machine-readable hypothesis identity: loop.sh counts consecutive
# iterations per slug and forces a pivot at 3, blocks at 4.
grep -q '^HYPOTHESIS-ID:' "$AG/NEXT.md" 2>/dev/null \
  || block "Exit contract unmet: scratch/agent/NEXT.md has no 'HYPOTHESIS-ID: <slug>' line. Add one naming the active investigation thread — keep the slug while pursuing the same hypothesis, change it when you pivot. The loop enforces iron rule 8 (3-strikes) with it."

# --- OUTCOME: distinguish progress from ledger churn -------------------------
# Sessions 51-59 satisfied every other condition here while advancing nothing:
# the work unit was skipped and documentation was edited instead, which the
# "touched both ledger files + committed" test cannot tell from real progress.
outcome="$(tr -d '[:space:]' < "$AG/OUTCOME" 2>/dev/null || true)"
case "$outcome" in
  ADVANCED|SUBSTITUTED|BLOCKED) ;;
  *) block "Exit contract unmet: scratch/agent/OUTCOME is '${outcome:-missing}'. Write exactly one of ADVANCED (ran the work unit / landed a real change), SUBSTITUTED (could not run it, did something else — also write scratch/agent/SUBSTITUTION.md), or BLOCKED. See the 'Declare your outcome honestly' section of tools/agent/ITERATION.md." ;;
esac

if [ "$outcome" = "SUBSTITUTED" ] && [ ! -s "$AG/SUBSTITUTION.md" ]; then
  block "Exit contract unmet: OUTCOME is SUBSTITUTED but scratch/agent/SUBSTITUTION.md is missing or empty. It must state (1) what stopped the planned work unit, (2) the evidence measured THIS iteration that it was stopped — a precedent from earlier sessions is not evidence, and (3) the single experiment that would refute your blocking explanation."
fi

# ADVANCED is a claim about changing something. Check it against the commits:
# a modified doc is not advancement; a modified code/tool/patch file, or a
# NEWLY ADDED document (e.g. a design doc), is.
if [ "$outcome" = "ADVANCED" ]; then
  substantive="$(git diff --name-status ${range:-HEAD~1..HEAD} 2>/dev/null \
    | awk '$1 ~ /^A/ { print "new:" $2; next }
           $2 != "PORTING-STATE.md" && $2 !~ /^docs\// { print "chg:" $2 }' | head -3)"
  # Sanctioned maintenance (2026-08-04): a real compaction of CURRENT-TRUTH
  # counts as ADVANCED. Measured as net lines REMOVED across the iteration's
  # commits — adds and removes in the same range cancel, so padding then
  # trimming in one iteration nets to the truth.
  if [ -z "$substantive" ]; then
    shrink="$(git diff --numstat ${range:-HEAD~1..HEAD} -- docs/CURRENT-TRUTH.md 2>/dev/null \
      | awk '{ print $2 - $1 }')"
    case "$shrink" in ''|*[!0-9]*) shrink=0 ;; esac
    [ "$shrink" -ge 200 ] && substantive="maint:CURRENT-TRUTH -${shrink} lines"
  fi
  # An experiment iteration can legitimately commit only docs: its real output
  # is captures under gitignored scratch/. s48 closed M1 that way. But an
  # UNCITED scratch file is indistinguishable from `echo x > scratch/x.txt`,
  # so run artifacts count only when the session entry names them.
  if [ -z "$substantive" ] && [ -f "$AG/ITER_START_MARK" ]; then
    ps_added="$(git diff ${range:-HEAD~1..HEAD} -- PORTING-STATE.md 2>/dev/null | grep '^+' || true)"
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      if printf '%s\n' "$ps_added" | grep -qF "$(basename "$f")"; then
        substantive="artifact:$f"
        break
      fi
    done <<ARTIFACTS
$(find scratch -type f -newer "$AG/ITER_START_MARK" -not -path 'scratch/agent/*' 2>/dev/null | head -50)
ARTIFACTS
  fi

  if [ -z "$substantive" ]; then
    block "OUTCOME says ADVANCED but this iteration only MODIFIED existing documentation (PORTING-STATE.md / docs/) and produced no cited run artifacts under scratch/. Editing the ledger is how you record progress, not how you make it. Either land a real change (code, instrument, tool, patch, a NEW document, or — in a triggered maintenance iteration — a >=200-net-line CURRENT-TRUTH compaction), or run the experiment now and cite its scratch/ artifact BY FILENAME in the PORTING-STATE.md session entry — or set OUTCOME=SUBSTITUTED and write SUBSTITUTION.md explaining why the work unit could not run."
  fi
fi

allow
