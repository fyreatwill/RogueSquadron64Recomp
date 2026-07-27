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
PROMPT_FILE="${1:?usage: runner.sh <prompt-file>}"
RUNNER="${RUNNER:-claude}"

case "$RUNNER" in
  claude)
    exec claude -p "$(cat "$PROMPT_FILE")" \
      --model "${RUNNER_MODEL:-${LOOP_MODEL:-sonnet}}" \
      --permission-mode acceptEdits \
      --output-format json 2>&1
    ;;

  grok)
    # grok mirrors Claude Code's headless flags closely: -p/--single,
    # --output-format, --permission-mode, --allow/--deny.
    exec grok --single "$(cat "$PROMPT_FILE")" \
      ${RUNNER_MODEL:+-m "$RUNNER_MODEL"} \
      --permission-mode acceptEdits \
      --output-format json 2>&1
    ;;

  codex)
    # `codex exec` is the non-interactive mode and does not prompt for
    # approvals. workspace-write is the least privilege that still lets an
    # iteration build and commit. If captures that write OUTSIDE the repo
    # (screencapture to mktemp dirs) fail under it, raise RUNNER_SANDBOX
    # deliberately rather than reaching for --dangerously-bypass-*.
    exec codex exec "$(cat "$PROMPT_FILE")" \
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
