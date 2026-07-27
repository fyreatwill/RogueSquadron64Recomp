#!/bin/bash
# Run ONE autonomous iteration with whichever agent CLI is selected, so a
# usage limit on one provider does not stop the project.
#
#   tools/agent/runner.sh <prompt-file>      # prints the agent's output
#
# Selected by RUNNER: claude (default) | grok | codex | custom
#   RUNNER_MODEL   override the model for the chosen runner
#   RUNNER_CMD     with RUNNER=custom: a command receiving the prompt on stdin
#   RUNNER_SANDBOX codex only: read-only | workspace-write | danger-full-access
#
# CAPABILITY NOTE, do not lose this: the Stop-hook gate in .claude/settings.json
# is a Claude Code feature. codex and grok never run it, so for them the exit
# contract is enforced only by loop.sh's post-hoc `stop_gate.sh --verify` pass
# and its retry. Same contract either way, checked at a different moment.
set -u
cd "$(dirname "$0")/../.."
PROMPT_FILE="${1:?usage: runner.sh <prompt-file> | runner.sh --describe}"
RUNNER="${RUNNER:-claude}"

# Only the claude branch falls back to LOOP_MODEL; the others pass no model
# flag unless RUNNER_MODEL is set, so they use their own default. --describe
# reports what will ACTUALLY be used, so the loop banner cannot drift from the
# invocation (it printed "model=sonnet" for a grok run that never saw it).
if [ "$PROMPT_FILE" = "--describe" ]; then
  case "$RUNNER" in
    claude) echo "runner=claude model=${RUNNER_MODEL:-${LOOP_MODEL:-sonnet}}" ;;
    grok)   echo "runner=grok model=${RUNNER_MODEL:-<grok default>} max_turns=${RUNNER_MAX_TURNS:-200}" ;;
    codex)  echo "runner=codex model=${RUNNER_MODEL:-<codex default>} sandbox=${RUNNER_SANDBOX:-workspace-write}" ;;
    custom) echo "runner=custom cmd=${RUNNER_CMD:-<unset>}" ;;
    *)      echo "runner=$RUNNER (unknown)" ;;
  esac
  exit 0
fi

# Small-context runners get the context budget appended to the iteration
# prompt. Claude's window (1M) swallows this repo's 390 KB ledger; grok's does
# not - measured s64, 105k tokens in 3 calls, then a silent cancel.
prompt_with_budget() {
  cat "$PROMPT_FILE" tools/agent/CONTEXT-BUDGET.md
}

case "$RUNNER" in
  claude)
    # claude emits single-line JSON; pretty-print it to match grok's output
    # so loop.log reads uniformly. Non-JSON output (crash text) passes
    # through untouched, and claude's exit code is preserved either way —
    # loop.sh classifies limits by rc.
    out="$(claude -p "$(cat "$PROMPT_FILE")" \
      --model "${RUNNER_MODEL:-${LOOP_MODEL:-sonnet}}" \
      --permission-mode acceptEdits \
      --output-format json 2>&1)"
    rc=$?
    printf '%s\n' "$out" | python3 -m json.tool 2>/dev/null || printf '%s\n' "$out"
    exit $rc
    ;;

  grok)
    export RS64_SKIP_STOP_HOOK=1   # grok runs the Stop hook and aborts on a block
    # ROOT CAUSE of every grok "Cancelled" iteration, found 2026-07-26 by
    # debug log (--debug-file): in headless --single mode grok's ACP client
    # initializes with fs:{writeTextFile:false} — it declares itself unable
    # to grant file-write permission — so the FIRST write/edit tool call dies
    # with cancellationCategory=PermissionCancelled and grok reports the
    # whole turn as Cancelled. That is why every iteration cancelled exactly
    # when it moved from reading to implementing, at whatever context size it
    # happened to have (55k-106k): the token counts tracked the first write,
    # not a context ceiling, and neither dontAsk nor acceptEdits helps
    # because the client cannot grant what it never declared.
    # THE FIX: --always-approve. Verified 2026-07-26: writes succeed, and
    # settings.json deny rules protecting lib/ are STILL enforced under it
    # ("Denied by permission policy: deny rule on bash matching 'git clean'"
    # returned as a tool error the model sees, not a turn cancellation).
    # Also measured: grok parses but IGNORES additionalDirectories in
    # .claude/settings.json — sibling-repo access rides on the Read() allow
    # rules instead. RS64_SKIP_STOP_HOOK is real and separate: without it the
    # Stop hook cancels grok turns too (env var reaches the hook fine).
    if [ -n "${RUNNER_PERMISSION_MODE:-}" ]; then
      perm_args=(--permission-mode "$RUNNER_PERMISSION_MODE")
    else
      perm_args=(--always-approve)
    fi
    exec grok --single "$(prompt_with_budget)" \
      ${RUNNER_MODEL:+-m "$RUNNER_MODEL"} \
      --max-turns "${RUNNER_MAX_TURNS:-200}" \
      "${perm_args[@]}" \
      --output-format json 2>&1
    ;;

  codex)
    export RS64_SKIP_STOP_HOOK=1   # belt and braces; verified for grok, unverified for codex
    # `codex exec` is the non-interactive mode and does not prompt for
    # approvals. workspace-write is the least privilege that still lets an
    # iteration build and commit. If captures that write OUTSIDE the repo
    # (screencapture to mktemp dirs) fail under it, raise RUNNER_SANDBOX
    # deliberately rather than reaching for --dangerously-bypass-*.
    # --json: JSONL events including per-turn token usage (codex reports no
    # dollar cost; compute it from tokens if comparing against claude/grok).
    # </dev/null: codex appends piped stdin to the prompt and prints
    # "Reading additional input from stdin..." — never let it wait on a
    # detached loop's stdin. rc IS nonzero on a usage limit as of CLI
    # 0.144.3 (measured 2026-07-27: rc=1, {"type":"error","message":"You've
    # hit your usage limit..."}), so loop.sh's rc check catches it.
    exec codex exec --json "$(prompt_with_budget)" \
      ${RUNNER_MODEL:+-m "$RUNNER_MODEL"} \
      -s "${RUNNER_SANDBOX:-workspace-write}" \
      -C "$PWD" < /dev/null 2>&1
    ;;

  custom)
    [ -n "${RUNNER_CMD:-}" ] || { echo "RUNNER=custom requires RUNNER_CMD"; exit 2; }
    exec sh -c "$RUNNER_CMD" < "$PROMPT_FILE" 2>&1
    ;;

  *)
    echo "unknown RUNNER='$RUNNER' (expected claude, grok, codex, or custom)"
    exit 2
    ;;
esac
