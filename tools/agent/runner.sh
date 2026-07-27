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
    exec claude -p "$(cat "$PROMPT_FILE")" \
      --model "${RUNNER_MODEL:-${LOOP_MODEL:-sonnet}}" \
      --permission-mode acceptEdits \
      --output-format json 2>&1
    ;;

  grok)
    export RS64_SKIP_STOP_HOOK=1   # grok runs the Stop hook and aborts on a block
    # dontAsk never prompts and still honours the deny rules protecting lib/,
    # which is the right posture for an unattended run - acceptEdits still asks
    # for bash and an unanswerable prompt is a hazard headless. NOTE: this did
    # NOT fix grok's early-cancel bug (tested s64, still Cancelled at 2 turns).
    # Do NOT reach for bypassPermissions; it would drop the deny rules too.
    # grok mirrors Claude Code's headless flags closely: -p/--single,
    # --output-format, --permission-mode, --allow/--deny.
    # An explicit turn bound. NOTE: this was NOT the cause of the early
    # "Cancelled" iterations - raising it changed nothing; the Stop hook was
    # (see stop_gate.sh). Kept as a real safety bound on a runaway iteration.
    exec grok --single "$(prompt_with_budget)" \
      ${RUNNER_MODEL:+-m "$RUNNER_MODEL"} \
      --max-turns "${RUNNER_MAX_TURNS:-200}" \
      --permission-mode "${RUNNER_PERMISSION_MODE:-dontAsk}" \
      --output-format json 2>&1
    ;;

  codex)
    export RS64_SKIP_STOP_HOOK=1   # belt and braces; verified for grok, unverified for codex
    # `codex exec` is the non-interactive mode and does not prompt for
    # approvals. workspace-write is the least privilege that still lets an
    # iteration build and commit. If captures that write OUTSIDE the repo
    # (screencapture to mktemp dirs) fail under it, raise RUNNER_SANDBOX
    # deliberately rather than reaching for --dangerously-bypass-*.
    exec codex exec "$(prompt_with_budget)" \
      ${RUNNER_MODEL:+-m "$RUNNER_MODEL"} \
      -s "${RUNNER_SANDBOX:-workspace-write}" \
      -C "$PWD" 2>&1
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
