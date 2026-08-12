#!/bin/bash
# Run ONE autonomous iteration with whichever agent CLI is selected, so a
# usage limit on one provider does not stop the project.
#
#   tools/agent/runner.sh <prompt-file>      # prints the agent's output
#
# Selected by RUNNER: claude (default) | deepseek | grok | codex | custom
#   RUNNER_MODEL   override the model for the chosen runner
#   RUNNER_CMD     with RUNNER=custom: a command receiving the prompt on stdin
#   RUNNER_SANDBOX codex only: read-only | workspace-write | danger-full-access
#
# CAPABILITY NOTE, do not lose this: the Stop-hook gate in .claude/settings.json
# is a Claude Code feature. codex and grok never run it, so for them the exit
# contract is enforced only by loop.sh's post-hoc `stop_gate.sh --verify` pass
# and its retry. Same contract either way, checked at a different moment.
# RUNNER=deepseek is the exception among the non-Anthropic runners: it IS the
# claude CLI, pointed at DeepSeek's Anthropic-compatible endpoint, so hooks,
# .claude/settings.json permissions and --output-format json all behave exactly
# as they do for RUNNER=claude. Do NOT set RS64_SKIP_STOP_HOOK for it.
#
#   RUNNER=deepseek DEEPSEEK_API_KEY=sk-... tools/agent/loop.sh
#
# The key comes from DEEPSEEK_API_KEY (or RUNNER_API_KEY). Nothing is written to
# the shell profile: the endpoint switch is scoped to the one subshell that runs
# the iteration, so an interactive `claude` in this repo still talks to
# Anthropic. Model default deepseek-v4-pro (1M context, so the 390 KB ledger
# fits); RUNNER_MODEL=deepseek-v4-flash for the cheap tier.
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
    deepseek) echo "runner=deepseek model=${RUNNER_MODEL:-deepseek-v4-pro} endpoint=https://api.deepseek.com/anthropic key=$([ -n "${DEEPSEEK_API_KEY:-${RUNNER_API_KEY:-}}" ] && echo set || echo MISSING)" ;;
    grok)   echo "runner=grok model=${RUNNER_MODEL:-<grok default>} max_turns=${RUNNER_MAX_TURNS:-200}" ;;
    codex)  echo "runner=codex model=${RUNNER_MODEL:-<codex default>} sandbox=${RUNNER_SANDBOX:-danger-full-access}" ;;
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

  deepseek)
    # The claude CLI against DeepSeek's Anthropic-compatible endpoint. Every
    # harness feature keeps working because the CLI is unchanged; only the
    # transport moves. Config per DeepSeek's own Claude Code integration page.
    key="${DEEPSEEK_API_KEY:-${RUNNER_API_KEY:-}}"
    [ -n "$key" ] || { echo "RUNNER=deepseek requires DEEPSEEK_API_KEY (or RUNNER_API_KEY)"; exit 2; }
    ds_model="${RUNNER_MODEL:-deepseek-v4-pro}"

    export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
    export ANTHROPIC_AUTH_TOKEN="$key"
    # ANTHROPIC_API_KEY would go out as x-api-key ALONGSIDE the bearer token —
    # an Anthropic key leaked to a third-party host, and an auth conflict. The
    # user's shell exports ANTHROPIC_BASE_URL=https://api.anthropic.com, so
    # never assume the ambient env is empty; clear what must not travel.
    unset ANTHROPIC_API_KEY ANTHROPIC_API_URL CLAUDE_CODE_USE_BEDROCK CLAUDE_CODE_USE_VERTEX
    # Alias every tier. Claude Code asks for a small/fast model on its own
    # (titles, summaries, subagents); unmapped names are silently rewritten to
    # flash by DeepSeek's backend, which would make the runner lie about what
    # it ran. Map them explicitly instead.
    export ANTHROPIC_MODEL="$ds_model"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="$ds_model"
    export ANTHROPIC_DEFAULT_SONNET_MODEL="$ds_model"
    export ANTHROPIC_DEFAULT_HAIKU_MODEL="${RUNNER_SMALL_MODEL:-deepseek-v4-flash}"
    export CLAUDE_CODE_SUBAGENT_MODEL="${RUNNER_SMALL_MODEL:-deepseek-v4-flash}"
    export CLAUDE_CODE_EFFORT_LEVEL="${RUNNER_EFFORT:-max}"
    export CLAUDE_CODE_AUTO_COMPACT_WINDOW="${RUNNER_COMPACT_WINDOW:-786432}"
    # An iteration builds, runs a 120 s capture and reconciles the ledger; a
    # default-length HTTP timeout kills long tool turns as "runner error".
    export API_TIMEOUT_MS="${API_TIMEOUT_MS:-600000}"

    # -pro carries 1M context and swallows the 390 KB ledger; the flash tier
    # does not, so it gets the same budget preamble grok needs.
    case "$ds_model" in
      *-pro*) ds_prompt="$(cat "$PROMPT_FILE")" ;;
      *)      ds_prompt="$(prompt_with_budget)" ;;
    esac

    out="$(claude -p "$ds_prompt" \
      --model "$ds_model" \
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
    # approvals.
    # SANDBOX DEFAULT RAISED 2026-08-12, MEASURED — do not lower it back to
    # workspace-write without re-measuring. Under `-s workspace-write` codex
    # exec cannot do this project's work at all, on two independent counts
    # (reproduced in a throwaway /tmp repo, codex-cli 0.144.3):
    #   .git is READ-ONLY   -> `test -w .git` says GIT_READONLY inside the
    #                          sandbox, GIT_WRITABLE outside it. Every exit
    #                          contract here ends in a commit, so no codex
    #                          iteration can ever satisfy it.
    #   nice/setpriority denied -> "nice: setpriority: Operation not permitted"
    # and s673 hit the third: the game gets no display ("The video driver did
    # not add any displays", hsel=0, clean exit in 3-4s), because the work is
    # GUI-driven — launch the game, capture its window, synthesise keys — which
    # is precisely the class of side effect the sandbox exists to prevent.
    # Both counts are cured by danger-full-access (verified: IS_WRITABLE,
    # nice_rc=0). Lower it per-run with RUNNER_SANDBOX if an iteration is
    # genuinely offline-only (doc/analysis work needs no game and no commit
    # only if you also skip the contract, which the loop will not do).
    # NOTE the s673 ledger claim that the read-only .git was "specific to that
    # one sandbox invocation" is WRONG: it is deterministic. That iteration's
    # commit landed because loop.sh routes contract RETRIES to the claude
    # runner, which is unsandboxed.
    # --json: JSONL events including per-turn token usage (codex reports no
    # dollar cost; compute it from tokens if comparing against claude/grok).
    # </dev/null: codex appends piped stdin to the prompt and prints
    # "Reading additional input from stdin..." — never let it wait on a
    # detached loop's stdin. rc IS nonzero on a usage limit as of CLI
    # 0.144.3 (measured 2026-07-27: rc=1, {"type":"error","message":"You've
    # hit your usage limit..."}), so loop.sh's rc check catches it.
    exec codex exec --json "$(prompt_with_budget)" \
      ${RUNNER_MODEL:+-m "$RUNNER_MODEL"} \
      -s "${RUNNER_SANDBOX:-danger-full-access}" \
      -C "$PWD" < /dev/null 2>&1
    ;;

  custom)
    [ -n "${RUNNER_CMD:-}" ] || { echo "RUNNER=custom requires RUNNER_CMD"; exit 2; }
    exec sh -c "$RUNNER_CMD" < "$PROMPT_FILE" 2>&1
    ;;

  *)
    echo "unknown RUNNER='$RUNNER' (expected claude, deepseek, grok, codex, or custom)"
    exit 2
    ;;
esac
