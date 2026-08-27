#!/bin/bash
# Unattended driver. Run from a Terminal INSIDE the logged-in desktop session:
#   caffeinate -dis tools/agent/loop.sh
# Each iteration is a fresh context; state lives in the docs (CURRENT-TRUTH,
# NEXT.md), which is exactly what they were built for. Usage-limit windows
# become sleeps, not handoffs.
#
# Env: ITER_CAP (default 80), SLEEP_ON_LIMIT (default 1800s), MAX_LIMIT_WAITS (12),
#      LOOP_MODEL (default claude-sonnet-4-6), MAX_NO_CONTRACT (default 2),
#      SLEEP_ON_ERROR (120s) / MAX_ERR_RETRIES (4) for nonzero-rc-without-limit-wording,
#      SOAKS_BETWEEN_ITERS (2) / SOAK_TIMEOUT (600s) for the queued-soak runner,
#      UNBLOCK_ENABLE (1) / MAX_UNBLOCK_ATTEMPTS (1) / UNBLOCK_RUNNER /
#      UNBLOCK_MODEL for the automated unblock tier (see try_unblock below)
#
# Any of the above (or RUNNER, RUNNER_MODEL, ...) can also be passed as a
# key=value argument instead of an env var prefix, e.g.:
#   tools/agent/loop.sh model=opus
#   tools/agent/loop.sh runner=grok model=grok-4.6
# `model=` is shorthand for LOOP_MODEL (the claude runner's model, e.g. opus /
# sonnet / claude-opus-5); other RUNNER_MODEL values still need the full name
# since they're runner-specific. Args are applied in order and override any
# same-named env var already in the shell.
set -u
cd "$(dirname "$0")/../.."
AG=scratch/agent
mkdir -p "$AG"

for arg in "$@"; do
  case "$arg" in
    model=*)  export LOOP_MODEL="${arg#model=}" ;;
    runner=*) export RUNNER="${arg#runner=}" ;;
    *=*)      export "${arg%%=*}=${arg#*=}" ;;
    *) echo "usage: $0 [key=value ...]  e.g. model=opus  runner=grok RUNNER_MODEL=grok-4.6" >&2; exit 2 ;;
  esac
done
ITER_CAP="${ITER_CAP:-80}"
SLEEP_ON_LIMIT="${SLEEP_ON_LIMIT:-1800}"
MAX_LIMIT_WAITS="${MAX_LIMIT_WAITS:-12}"
MAX_NO_CONTRACT="${MAX_NO_CONTRACT:-2}"
MAX_SUBSTITUTED="${MAX_SUBSTITUTED:-2}"
SLEEP_ON_ERROR="${SLEEP_ON_ERROR:-120}"
MAX_ERR_RETRIES="${MAX_ERR_RETRIES:-4}"
SOAKS_BETWEEN_ITERS="${SOAKS_BETWEEN_ITERS:-2}"
SOAK_TIMEOUT="${SOAK_TIMEOUT:-600}"

# Choose the model EXPLICITLY. Without this the loop silently inherits whatever
# `model` sits in ~/.claude/settings.json — which on 2026-07-26 was "fable", the
# most expensive tier, for all 40 unattended iterations. Most of an iteration is
# mechanical (grep, instrument, rebuild, capture, reconcile, write the ledger);
# the investigative discipline lives in ITERATION.md and the Stop gate, not in
# raw model strength. Override per run: LOOP_MODEL=opus tools/agent/loop.sh
LOOP_MODEL="${LOOP_MODEL:-claude-sonnet-4-6}"

log() { echo "[loop] $*" | tee -a "$AG/loop.log"; }

# Runner output goes through the formatter on the way to the log ONLY. codex
# emits JSONL whose command output arrives as one enormous escaped line per
# event; fmt_runner_log.py unescapes it into readable blocks, and pretty-prints
# claude/deepseek's single JSON document the way runner.sh already did.
# The RAW $out is what the limit classifier reads (see errtxt below) — keep it
# that way. Rendering the agent's narrative into plain text and then pattern
# matching it is how a successful iteration gets mistaken for a rate limit.
# If the formatter fails for any reason, log the raw output rather than nothing.
log_runner_output() {
  local formatted
  formatted="$(printf '%s\n' "$1" | tools/agent/fmt_runner_log.py 2>/dev/null)"
  [ -n "$formatted" ] || formatted="$1"
  printf '%s\n' "$formatted" >> "$AG/loop.log"
}

# --- automated unblock tier -------------------------------------------------
# A BLOCKED iteration used to end the run and wait for a human, which is right
# when the block is real and expensive when it is not: the alternate-RSP block
# of 2026-08-12 stopped four consecutive overnight runs, each restart spending
# a paid iteration to re-derive the same claim, while the answer sat in the
# blocked tool's own --help.
#
# So before surrendering the run, spend ONE iteration on a different prompt
# (tools/agent/UNBLOCK.md) whose whole job is to refute the block, satisfy it
# locally, or re-scope around it. Three properties keep this from becoming a
# churn engine:
#   * the agent cannot mark itself unblocked - the loop re-runs stop_gate
#     --verify and restores a block if the contract is unmet;
#   * one attempt per DISTINCT block (keyed by content hash), so a block that
#     survives its attempt goes to the human instead of looping;
#   * state lives outside the repo, like every other meter here.
# UNBLOCK_ENABLE=0 restores the old stop-and-notify behaviour.
UNBLOCK_STATE="${TMPDIR:-/tmp}/.rs64-unblock-state"

try_unblock() {
  [ "${UNBLOCK_ENABLE:-1}" = "1" ] || return 1
  [ -s "$AG/BLOCKED.md" ] || return 1

  local hash prev_hash prev_n out rc verdict
  hash="$(shasum "$AG/BLOCKED.md" 2>/dev/null | cut -d' ' -f1)"
  prev_hash=""; prev_n=0
  [ -f "$UNBLOCK_STATE" ] && read -r prev_hash prev_n < "$UNBLOCK_STATE" 2>/dev/null
  case "${prev_n:-0}" in ''|*[!0-9]*) prev_n=0 ;; esac

  if [ "$hash" = "$prev_hash" ] && [ "$prev_n" -ge "${MAX_UNBLOCK_ATTEMPTS:-1}" ]; then
    log "unblock: this exact block already survived $prev_n attempt(s) - escalating to human"
    return 1
  fi
  if [ "$hash" = "$prev_hash" ]; then prev_n=$((prev_n + 1)); else prev_n=1; fi
  printf '%s %s\n' "$hash" "$prev_n" > "$UNBLOCK_STATE"

  log "unblock: attempt $prev_n - $(head -1 "$AG/BLOCKED.md")"
  echo WORKING > "$AG/STATUS"
  rm -f "$AG/OUTCOME" "$AG/UNBLOCK.md"
  touch "$AG/ITER_START_MARK"
  echo 0 > "$AG/.stop_blocks"
  git rev-parse HEAD > "$AG/ITER_START_HEAD" 2>/dev/null

  out="$(RUNNER="${UNBLOCK_RUNNER:-${RUNNER:-claude}}" \
         RUNNER_MODEL="${UNBLOCK_MODEL:-${RUNNER_MODEL:-}}" \
         LOOP_MODEL="$LOOP_MODEL" tools/agent/runner.sh tools/agent/UNBLOCK.md)"
  rc=$?
  log_runner_output "$out"

  if [ -f "$AG/BLOCKED.md" ]; then
    log "unblock: agent left BLOCKED.md in place (rc=$rc) - treating as a real human dependency"
    return 1
  fi
  if ! verdict="$(tools/agent/stop_gate.sh --verify)"; then
    log "unblock: BLOCKED.md cleared but the exit contract is unmet - not trusting it"
    { echo "# An unblock attempt cleared BLOCKED.md without meeting the exit contract, $(date)"
      echo
      echo "The block below was NOT resolved; the attempt merely deleted the file."
      echo "Unmet condition:"; echo
      printf '%s\n' "$verdict"; } > "$AG/BLOCKED.md"
    return 1
  fi

  log "unblock: resolved - resuming iterations"
  return 0
}

notify_blocked() {
  osascript -e 'display notification "RS64 agent blocked - see scratch/agent/BLOCKED.md" with title "RS64 loop"' 2>/dev/null
  log "BLOCKED - fix it, delete $AG/BLOCKED.md, rerun."
}

# Queued soaks: a repeat soak needs wall-clock, not a paid session. Iterations
# enqueue self-contained recipes into scratch/agent/soak_queue/; the loop runs
# up to SOAKS_BETWEEN_ITERS of them between iterations, appends one verdict
# line each to scratch/agent/SOAK-RESULTS.md, and the next session consumes
# the verdicts (35 sessions of the first 300 were babysat re-soaks).
# Each recipe runs in its own process group so the watchdog kill reaps the
# game too; recipes still must SIGKILL their own game on the clean path.
run_soak_queue() {
  local qdir="$AG/soak_queue" rdir="$AG/soak_results" ran=0
  [ -d "$qdir" ] || return 0
  mkdir -p "$rdir" "$qdir/done"
  local recipe
  for recipe in "$qdir"/*.sh; do
    [ -e "$recipe" ] || return 0
    [ "$ran" -ge "$SOAKS_BETWEEN_ITERS" ] && return 0
    local name ts slog pid wd rc t0 dur
    name="$(basename "$recipe" .sh)"
    ts="$(date +%Y%m%d-%H%M%S)"
    slog="$rdir/${name}_${ts}.log"
    log "soak $name starting (cap ${SOAK_TIMEOUT}s) -> $slog"
    t0=$SECONDS
    perl -e 'setpgrp(0,0); exec @ARGV' /bin/bash "$recipe" >"$slog" 2>&1 &
    pid=$!
    ( sleep "$SOAK_TIMEOUT" && kill -9 -- -"$pid" 2>/dev/null ) &
    wd=$!
    rc=0; wait "$pid" 2>/dev/null || rc=$?
    kill "$wd" 2>/dev/null; wait "$wd" 2>/dev/null
    dur=$((SECONDS - t0))
    printf '%s | %s | rc=%s | %ss | %s\n' "$ts" "$name" "$rc" "$dur" "$slog" >> "$AG/SOAK-RESULTS.md"
    mv "$recipe" "$qdir/done/${name}_${ts}.sh"
    log "soak $name finished rc=$rc after ${dur}s"
    ran=$((ran+1))
  done
}

# Computed once per run and reused on every iteration's finished-line stamp,
# so per-model/runner analysis of loop.log doesn't have to reverse-engineer
# attribution from narrative text (see 2026-08-12 loop.log audit).
runner_desc="$(LOOP_MODEL="$LOOP_MODEL" tools/agent/runner.sh --describe)"
# Pin whatever model --describe detected (including grok/codex's own live
# default, see runner.sh) for the rest of THIS run, so every iteration - and
# the finished-line stamp below - uses exactly the model just logged instead
# of re-resolving (and possibly drifting, e.g. mid-run default change) later.
if [ -z "${RUNNER_MODEL:-}" ]; then
  detected_model="$(printf '%s' "$runner_desc" | grep -oE 'model=[^ ]+' | cut -d= -f2)"
  case "$detected_model" in
    ''|'<unresolved>') : ;;  # leave RUNNER_MODEL unset, runner.sh falls back to its own default per-call
    *) export RUNNER_MODEL="$detected_model" ;;
  esac
fi
log "run starting $(date) — $runner_desc cap=$ITER_CAP"

n=0
waits=0
errs=0
nocontract=0
subs=0

# Rule-8 (3-strikes) enforcement: consecutive STALLED iterations on one
# HYPOTHESIS-ID (read from NEXT.md after each iteration; a gate-validated
# ADVANCED iteration resets the count). State lives OUTSIDE the repo so the
# metered agent cannot reset it, and in a file so it survives loop restarts
# (32 observed in the first 300 sessions).
HYPSTATE="${TMPDIR:-/tmp}/.rs64-hyp-state"
prev_hyp=""; hyp_count=0
[ -f "$HYPSTATE" ] && read -r prev_hyp hyp_count < "$HYPSTATE" 2>/dev/null
case "${hyp_count:-0}" in ''|*[!0-9]*) hyp_count=0 ;; esac
while [ "$n" -lt "$ITER_CAP" ]; do

  # BLOCKED.md is the EXPLANATION of a block; scratch/agent/STATUS is the
  # DECLARATION. Halting on the file's mere existence killed a healthy run
  # before it reached preflight (2026-08-12 00:21: a codex run exited
  # instantly on a BLOCKED.md whose first line read "# Not currently
  # blocked", written by an iteration that ended DONE/ADVANCED). Only treat
  # it as stale when BOTH say so — a real block leaves STATUS=BLOCKED, and a
  # preflight block leaves "# Blocked by preflight", so neither is archived.
  if [ -f "$AG/BLOCKED.md" ]; then
    if [ "$(tr -d '[:space:]' < "$AG/STATUS" 2>/dev/null)" = "DONE" ] \
       && head -1 "$AG/BLOCKED.md" | grep -qiE 'not[[:space:]]+(currently[[:space:]]+)?blocked'; then
      mv "$AG/BLOCKED.md" "$AG/BLOCKED.stale.$(date +%Y%m%d-%H%M%S).md"
      log "stale BLOCKED.md (says 'not blocked', last iteration DONE) - archived, continuing"
    elif ! try_unblock; then
      notify_blocked
      exit 2
    fi
  fi

  if ! tools/agent/preflight.sh 2>&1 | tee -a "$AG/loop.log" | grep -q '^\[preflight\] OK'; then
    { echo "# Blocked by preflight, $(date)"; echo; tools/agent/preflight.sh 2>&1; } > "$AG/BLOCKED.md"
    notify_blocked
    exit 2
  fi

  # Scratch retention. probe/regress leave the full emulator trace in
  # <outdir>/run.log and nothing used to remove them: 202 GB of traces put
  # the disk at 97% on 2026-08-20. Runs between iterations, so a capture in
  # flight never has its log compressed out from under it.
  tools/agent/prune-scratch.sh 2>&1 | tee -a "$AG/loop.log"

  n=$((n+1))
  log "iteration $n starting $(date)"
  echo WORKING > "$AG/STATUS"
  rm -f "$AG/OUTCOME" "$AG/SUBSTITUTION.md"
  touch "$AG/ITER_START_MARK"   # the gate dates run artifacts against this
  echo 0 > "$AG/.stop_blocks"
  iter_start_head="$(git rev-parse HEAD 2>/dev/null)"
  printf '%s\n' "$iter_start_head" > "$AG/ITER_START_HEAD"

  # A rule-8 forced pivot (written after 3 consecutive non-ADVANCED iterations
  # on one HYPOTHESIS-ID) rides in as a preamble on the standard prompt.
  prompt_file=tools/agent/ITERATION.md
  if [ -s "$AG/PIVOT.md" ]; then
    cat "$AG/PIVOT.md" tools/agent/ITERATION.md > "$AG/ITERATION_WITH_PIVOT.md"
    prompt_file="$AG/ITERATION_WITH_PIVOT.md"
    log "rule-8 pivot preamble active this iteration"
  fi
  out="$(LOOP_MODEL="$LOOP_MODEL" tools/agent/runner.sh "$prompt_file")"
  rc=$?
  log_runner_output "$out"

  # Limit classification must look at the runner's ERROR fields, never its
  # narrative: s68's grok iteration described RSP timing as "the rate-limit
  # math lines up" and the loop slept 30 minutes on a fully successful,
  # committed iteration. If the output parses as JSON, build the string the
  # limit patterns run against from error-ish fields only — including
  # result/text solely when is_error is set (claude puts real limit messages
  # in "result", but successful narratives live there too). If it does not
  # parse, fall back to the raw output: real limit messages are sometimes
  # plain text.
  errtxt="$(printf '%s' "$out" | python3 -c '
import json, sys
raw = sys.stdin.read()

def fields(d):
    parts = []
    for k in ("error", "subtype", "stopReason", "stop_reason",
              "api_error_status", "terminal_reason", "message"):
        v = d.get(k)
        if v is not None:
            parts.append(v if isinstance(v, str) else json.dumps(v))
    if d.get("is_error"):
        parts.append("is_error")
        for k in ("result", "text"):
            v = d.get(k)
            if v is not None:
                parts.append(str(v))
    return parts

try:
    d = json.loads(raw)
    if isinstance(d, dict):
        print("\n".join(fields(d))); sys.exit()
except Exception:
    pass

# JSONL (codex --json) or mixed plain text: JSON event lines contribute only
# error-ish events; non-JSON lines pass through raw (limit messages are
# sometimes plain text).
parts, sawjson = [], False
for line in raw.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
    except Exception:
        parts.append(line)
        continue
    sawjson = True
    if isinstance(ev, dict):
        # MEASURED 2026-08-11, do not narrow this test again: a claude/deepseek
        # result object is type="result" with NO "error" key — the failure rides
        # in is_error + api_error_status + result. This branch runs for it
        # because the CLI prints a stderr warning line ("claude.ai connectors
        # are disabled...") ahead of the JSON, which breaks the whole-document
        # parse above. The old type/"error"-key test dropped exactly the event
        # carrying "API Error: 402 Insufficient Balance", so a hard cap was
        # classified as a crash and slept through 4 retries.
        t = str(ev.get("type", ""))
        if ("error" in t or "fail" in t or "error" in ev
                or ev.get("is_error") or ev.get("api_error_status")):
            parts.extend(fields(ev))
if not sawjson and not parts:
    print(raw)
else:
    print("\n".join(parts))
' 2>/dev/null)" || errtxt="$out"

  # NOTE: limits are classified BEFORE the contract check on purpose. `codex`
  # exits 0 even when it did nothing but print "You've hit your usage limit",
  # so an rc-based test cannot see that failure — and if the contract check ran
  # first it would burn MAX_CONTRACT_RETRIES re-invoking a CLI that is out of
  # quota. Classify the limit, sleep or stop, and only then ask whether the
  # iteration met its contract.

  # A spend/quota CAP is not a window that reopens. Sleeping on it wastes
  # MAX_LIMIT_WAITS * SLEEP_ON_LIMIT (6 hours by default) retrying something
  # that cannot succeed until a human raises the cap. Distinguish it from the
  # transient limits, which really are just windows.
  #
  # ORDER MATTERS. With extra usage OFF, the normal subscription-limit message
  # is what the loop is SUPPOSED to sleep through, and it often carries upsell
  # wording ("upgrade your plan") that would otherwise read as a hard cap. A
  # stated reset time means the window reopens by itself: always transient.
  if printf '%s' "$errtxt" | grep -qiE 'resets? at|resets? in|resets? [0-9]|try again (later|at)|limit will reset'; then
    : # falls through to the transient handler below - sleep, do not stop
  elif printf '%s' "$errtxt" | grep -qiE 'monthly spend limit|spend limit|credit balance|insufficient quota|insufficient balance'; then
    # 'insufficient balance' is DeepSeek's 402: a prepaid balance that ran out.
    # Genuinely a hard cap — it is not a window and no probe can talk it open.
    # The API's wording is not trustworthy here: on 2026-07-27 a 5-hour
    # window cap returned 429 "You've hit your monthly spend limit" and the
    # loop hard-stopped over credit that was still there. Before declaring a
    # hard cap, verify with a minimal cheap probe — from /tmp so the repo's
    # Stop hook cannot turn "reply OK" into a 34-turn contract session
    # (that happened). Claude-runner only; other providers keep the old
    # behavior since probing them from here would spend the wrong quota.
    if [ "${RUNNER:-claude}" = "claude" ] && \
       probe="$( cd /tmp && claude -p 'Reply with exactly OK.' --model haiku --output-format json 2>&1 )" && \
       ! printf '%s' "$probe" | grep -qiE 'spend limit|usage limit|session limit|credit balance|insufficient quota'; then
      waits=$((waits+1))
      if [ "$waits" -gt "$MAX_LIMIT_WAITS" ]; then
        { echo "# $waits consecutive limit waits (probe kept succeeding while the"
          echo "iteration model kept failing — possibly a model-specific cap), $(date)"
          echo; echo "Last claude output:"; printf '%s\n' "$out" | tail -20; } > "$AG/BLOCKED.md"
        notify_blocked
        exit 2
      fi
      log "hard-cap wording but a cheap probe succeeded — window has reset, retrying shortly (wait $waits/$MAX_LIMIT_WAITS)"
      n=$((n-1)); sleep 60; continue
    fi
    { echo "# Hard spend/quota cap reached, $(date)"; echo;
      echo "This is NOT a transient rate limit and sleeping will not clear it."
      if [ "${RUNNER:-claude}" = "deepseek" ]; then
        echo "RUNNER=deepseek: top up the DeepSeek account balance"
        echo "(platform.deepseek.com billing), then delete this file and rerun."
      else
        echo "Raise or reset the cap (claude.ai/settings/usage), then delete this"
        echo "file and rerun the loop."
      fi; echo;
      echo "Last claude output:"; printf '%s\n' "$out" | tail -20; } > "$AG/BLOCKED.md"
    log "HARD CAP reached - not retryable, stopping"
    notify_blocked
    exit 2
  fi

  if printf '%s' "$errtxt" | grep -qiE 'usage limit|session limit|rate.?limit|overloaded|resets at'; then
    waits=$((waits+1))
    if [ "$waits" -gt "$MAX_LIMIT_WAITS" ]; then
      { echo "# Loop gave up after $waits consecutive limit waits, $(date)"; echo;
        echo "Last claude output (rc=$rc):"; printf '%s\n' "$out" | tail -40; } > "$AG/BLOCKED.md"
      notify_blocked
      exit 2
    fi
    log "limit (rc=$rc), wait $waits/$MAX_LIMIT_WAITS - sleeping ${SLEEP_ON_LIMIT}s"
    n=$((n-1))          # a window we never got to work in does not burn an iteration
    sleep "$SLEEP_ON_LIMIT"
    continue
  fi
  # A nonzero exit with NO limit wording is a crash / config / network failure,
  # not a quota window: 30-minute sleeps here could burn 6h on something a
  # short retry either clears (dropped connection) or can never clear (broken
  # config, which should surface to the human fast).
  if [ $rc -ne 0 ]; then
    errs=$((errs+1))
    if [ "$errs" -ge "$MAX_ERR_RETRIES" ]; then
      { echo "# $errs consecutive runner errors with no limit wording, $(date)"; echo;
        echo "Not sleeping on these: likely a crash, config, or network failure."
        echo "Last output (rc=$rc):"; printf '%s\n' "$out" | tail -40; } > "$AG/BLOCKED.md"
      notify_blocked
      exit 2
    fi
    log "runner error (rc=$rc, no limit wording), wait $errs/$MAX_ERR_RETRIES - sleeping ${SLEEP_ON_ERROR}s"
    n=$((n-1))
    sleep "$SLEEP_ON_ERROR"
    continue
  fi
  waits=0
  errs=0

  # Post-hoc contract check, for EVERY runner. Claude's Stop hook already
  # pushed it to meet this before returning; codex and grok never saw a hook,
  # so this is where they get held to the same contract. Feed the specific
  # unmet condition back and let it finish the job.
  cr=0
  # contract_ok records whether the gate actually validated this iteration.
  # Rule-8 keys its reset on it: OUTCOME alone is agent-written (scratch/), and
  # an ADVANCED claim the gate rejected must not zero the meter.
  contract_ok=0
  while true; do
    if verdict="$(tools/agent/stop_gate.sh --verify)"; then contract_ok=1; break; fi
    cr=$((cr+1))
    if [ "$cr" -gt "${MAX_CONTRACT_RETRIES:-2}" ]; then
      log "contract still unmet after $((cr-1)) retries: $(printf '%s' "$verdict" | head -1)"
      break
    fi
    log "contract unmet (retry $cr): $(printf '%s' "$verdict" | head -1)"
    { cat tools/agent/ITERATION.md
      echo
      echo "## You already ran this iteration and stopped early"
      echo "The exit contract is NOT met. Do ONLY what is needed to satisfy it:"
      echo
      printf '%s\n' "$verdict"
      echo
      echo "## Checkpoint close-out is ACCEPTABLE here"
      echo "You are in a retry: the primary session likely died mid-work-unit"
      echo "(usage limit or turn cap). Do NOT re-run the experiment or try to"
      echo "finish a large work unit now — that is exactly what keeps failing."
      echo "Instead: write what IS known so far (including partial/failed runs)"
      echo "to PORTING-STATE.md, update docs/CURRENT-TRUTH.md only if a"
      echo "conclusion actually changed, rewrite scratch/agent/NEXT.md as a"
      echo "RESUME instruction (what ran, what artifacts exist, exact next"
      echo "command), commit, and write DONE to scratch/agent/STATUS with"
      echo "OUTCOME=ADVANCED if any artifact/knowledge landed, else SUBSTITUTED."
    } > "$AG/RETRY_PROMPT.md"
    # Retries fall back to the claude runner: grok runs the Stop hook and aborts
    # the whole turn on a block (observed as stopReason=Cancelled after ~3
    # calls), so a grok retry can never satisfy the contract it was sent to fix.
    # deepseek is exempt — it IS the claude CLI on another endpoint, so it
    # handles a hook block normally, and routing its retries to Anthropic would
    # quietly spend the wrong provider's quota on every unmet contract.
    retry_runner=claude
    [ "${RUNNER:-claude}" = "deepseek" ] && retry_runner=deepseek
    # RUNNER_MODEL is pinned to the ORIGINAL runner's model (see the
    # --describe block above) and is meaningless - or actively wrong, a
    # foreign provider's slug - for whichever runner this retry switches to.
    # Clearing it here lets runner.sh fall back to LOOP_MODEL/its own default
    # instead of e.g. handing Claude Code a codex model id (found 2026-08-13:
    # a codex run pinned to a since-retired "gpt-5.6-luna" 404'd, and the
    # claude retry inherited that same string as --model and 404'd too,
    # silently reducing the automated retry tier to zero attempts).
    out="$(RUNNER=$retry_runner RUNNER_MODEL= LOOP_MODEL="$LOOP_MODEL" tools/agent/runner.sh "$AG/RETRY_PROMPT.md")"
    log_runner_output "$out"
    # A retry that itself hits a limit is not a contract failure - stop retrying.
    # (Raw-output match is acceptable here: a false positive merely stops
    # retrying early, it does not put the loop to sleep.)
    if printf '%s' "$out" | grep -qiE 'usage limit|rate.?limit|spend limit|overloaded'; then
      log "retry $cr hit a provider limit; abandoning contract retries this iteration"
      break
    fi
  done
  # Both break paths leave contract_ok=0 without re-asking the gate, but a
  # retry may have satisfied the contract BEFORE hitting a limit (and the
  # limit grep can false-positive on the agent merely narrating "usage
  # limit"). One final verify settles contract_ok from the on-disk state, so
  # rule-8 never strikes an iteration the gate would actually pass.
  if [ "$contract_ok" != "1" ] && tools/agent/stop_gate.sh --verify >/dev/null 2>&1; then
    contract_ok=1
  fi

  status="$(tr -d '[:space:]' < "$AG/STATUS" 2>/dev/null)"
  # Ground truth, not narrative: whatever "## Session NNN" headings this
  # iteration actually appended to PORTING-STATE.md, diffed against the HEAD
  # captured before the iteration ran. A model's result text can claim any
  # session number; the ledger diff cannot.
  session_nums="$(git diff --unified=0 "$iter_start_head" -- PORTING-STATE.md 2>/dev/null \
    | grep -oE '^\+## Session [0-9]+' | grep -oE '[0-9]+' | sort -nu | paste -sd, -)"
  log "iteration $n finished $(date) STATUS=${status:-unset} HEAD=$(git rev-parse --short HEAD 2>/dev/null) $runner_desc session=${session_nums:-none}"
  if [ "$status" = "BLOCKED" ]; then
    [ -s "$AG/BLOCKED.md" ] || echo "# Agent set STATUS=BLOCKED without writing this file, $(date)" > "$AG/BLOCKED.md"
    # One automated attempt before the run ends. On success the next iteration
    # starts fresh; rule-8 accounting is skipped for a blocked iteration since
    # it produced no OUTCOME to weigh.
    if try_unblock; then
      continue
    fi
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
    # An iteration that ended DONE has declared itself not blocked. If it left
    # a BLOCKED.md behind anyway, clear it here rather than letting the next
    # loop top halt on it — that cost a whole run at 00:21 on 2026-08-12.
    if [ -f "$AG/BLOCKED.md" ]; then
      mv "$AG/BLOCKED.md" "$AG/BLOCKED.stale.$(date +%Y%m%d-%H%M%S).md"
      log "iteration $n ended DONE but left a BLOCKED.md - archived as stale"
    fi
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

  # --- rule-8 enforcement: consecutive NON-ADVANCING iterations on one --------
  # hypothesis. An ADVANCED iteration resets the counter: chained ADVANCED
  # sessions on one slug are the sanctioned campaign mode (a systematic sweep
  # like item -317 legitimately holds one HYPOTHESIS-ID for tens of productive
  # sessions — counting those blocked the loop three times in one night,
  # s499-s501, each restart surviving exactly one iteration). The substantive
  # gate polices what earns ADVANCED; what this counter catches now is the
  # residue that evades the nocontract and subs counters by alternating failure
  # modes on one slug. State stays outside the repo so the metered agent cannot
  # reset its own meter.
  hyp="$(grep -m1 '^HYPOTHESIS-ID:' "$AG/NEXT.md" 2>/dev/null \
         | sed 's/^HYPOTHESIS-ID:[[:space:]]*//' | tr -cd 'A-Za-z0-9._-')"
  rm -f "$AG/PIVOT.md" "$AG/ITERATION_WITH_PIVOT.md"
  if [ -n "$hyp" ]; then
    if [ "$outcome" = "ADVANCED" ] && [ "${contract_ok:-0}" = "1" ]; then
      hyp_count=0
    elif [ "$hyp" = "$prev_hyp" ]; then hyp_count=$((hyp_count+1)); else hyp_count=1; fi
    prev_hyp="$hyp"
    printf '%s %s\n' "$prev_hyp" "$hyp_count" > "$HYPSTATE"
    if [ "$hyp_count" -ge 4 ]; then
      { echo "# Rule 8: 4 consecutive non-ADVANCED iterations on HYPOTHESIS-ID '$hyp', $(date)"; echo;
        echo "Three stalled iterations plus a forced-pivot preamble did not move it."
        echo "Re-scope the work unit in scratch/agent/NEXT.md or change its"
        echo "HYPOTHESIS-ID slug. The counter (\${TMPDIR:-/tmp}/.rs64-hyp-state)"
        echo "resets on a slug change or on the next ADVANCED iteration; a human may"
        echo "also just delete that file. Then delete this file and rerun."; } > "$AG/BLOCKED.md"
      notify_blocked
      exit 2
    fi
    if [ "$hyp_count" -ge 3 ]; then
      log "rule-8: hypothesis '$hyp' at $hyp_count consecutive non-ADVANCED iterations - writing pivot preamble"
      { echo "## MANDATORY PIVOT (rule 8, loop-enforced)"
        echo "The last $hyp_count iterations all ran HYPOTHESIS-ID '$hyp' and NONE of"
        echo "them earned ADVANCED. Do NOT run another iteration of the same approach."
        echo "Either (a) switch to a different work unit (new HYPOTHESIS-ID), or (b)"
        echo "design the single highest-information discriminating probe for '$hyp',"
        echo "run THAT, and close or pivot on its result. A 4th consecutive stalled"
        echo "iteration on '$hyp' blocks the loop."
        echo; } > "$AG/PIVOT.md"
    fi
  fi

  # --- no-engineering churn guard (2026-08-26): slug-INDEPENDENT ------------
  # Rule 8 (above) keys on consecutive SAME-slug stalls and resets on ANY
  # ADVANCED. An M5 thread that only re-runs existing instruments (no code
  # change) and renames its HYPOTHESIS-ID every session evades it completely:
  # measured 2026-08-26 at 105/120 ADVANCED, 0 blocks, ~13 distinct m5-* slugs
  # across 60 sessions, stuck 40+ sessions. This counter fires on the one thing
  # churn cannot fake: consecutive ADVANCED iterations that landed NO
  # engineering change (git fact -- no changed code/tool/patch, no NEW
  # non-scratch file, and not a >=200-line CURRENT-TRUTH compaction). Any real
  # work resets it. State lives outside the repo so the metered agent cannot
  # reset its own meter. Tunable via NOENG_PIVOT / NOENG_BLOCK.
  NOENGSTATE="${TMPDIR:-/tmp}/.rs64-noeng-state"
  NOENG_PIVOT="${NOENG_PIVOT:-6}"; NOENG_BLOCK="${NOENG_BLOCK:-12}"
  noeng=0; [ -f "$NOENGSTATE" ] && read -r noeng < "$NOENGSTATE" 2>/dev/null
  case "${noeng:-0}" in ''|*[!0-9]*) noeng=0 ;; esac
  eng_change=0
  if [ -n "$iter_start_head" ] && git diff --name-status "${iter_start_head}..HEAD" 2>/dev/null | awk '
        $1 ~ /^A/ && $2 !~ /^scratch\// { f=1 }
        $2 !~ /^scratch\// && $2 != "PORTING-STATE.md" && $2 !~ /^docs\// && $2 != "CLAUDE.md" { f=1 }
        END { exit(f?0:1) }'; then
    eng_change=1
  fi
  if [ "$eng_change" = "0" ] && [ -n "$iter_start_head" ]; then
    shrink="$(git diff --numstat "${iter_start_head}..HEAD" 2>/dev/null -- docs/CURRENT-TRUTH.md | awk '{s+=$2-$1} END{print s+0}')"
    case "$shrink" in ''|*[!0-9-]*) shrink=0 ;; esac
    [ "$shrink" -ge 200 ] && eng_change=1
  fi
  if [ "$outcome" = "ADVANCED" ] && [ "${contract_ok:-0}" = "1" ] && [ "$eng_change" = "0" ]; then
    noeng=$((noeng+1))
    log "no-engineering ADVANCED streak: $noeng (iteration changed no code/tool/patch/new-doc)"
  else
    noeng=0
  fi
  printf '%s\n' "$noeng" > "$NOENGSTATE"
  if [ "$noeng" -ge "$NOENG_BLOCK" ]; then
    { echo "# $noeng consecutive ADVANCED iterations with no engineering change, $(date)"; echo;
      echo "Every one scored ADVANCED but changed no code, tool, patch, or new doc --"
      echo "only re-ran existing instruments and recorded observations. The forced"
      echo "bounded-work pivot did not take. Redirect the loop: choose a work unit that"
      echo "lands code (an M5 de-stub per docs/M5-AUDIO-PLAN.md, or the"
      echo "generated-symbol-renaming sweep), or re-scope scratch/agent/NEXT.md."
      echo "Reset the counter: rm ${NOENGSTATE}. Then delete this file and rerun."; } > "$AG/BLOCKED.md"
    notify_blocked
    exit 2
  fi
  if [ "$noeng" -ge "$NOENG_PIVOT" ]; then
    log "no-engineering churn: $noeng consecutive code-free ADVANCED iterations - forcing bounded-work pivot"
    { echo "## MANDATORY PIVOT (no-engineering churn guard, loop-enforced)"
      echo "The last $noeng ADVANCED iterations changed NO code, tool, patch, or doc --"
      echo "they only re-ran existing instruments and recorded observations, and"
      echo "renaming the HYPOTHESIS-ID each session hid this from rule 8. Iron rule 14:"
      echo "an instrument re-run that selects nothing is churn, not progress."
      echo
      echo "THIS iteration you MUST land a committed CODE change, one of:"
      echo "  (a) De-stub the next concrete step in docs/M5-AUDIO-PLAN.md and commit the"
      echo "      generated/runtime change -- a real edit, not another log probe; or"
      echo "  (b) Switch to the generated-symbol-renaming sweep: set"
      echo "      HYPOTHESIS-ID: generated-symbol-renaming-sweep and rename a batch of"
      echo "      func_0x... symbols (ITERATION.md strategic priority 4). It lands code"
      echo "      every session and is always actionable."
      echo "Another observation-only audit under scratch/ does NOT satisfy this and"
      echo "extends the streak toward a loop block at $NOENG_BLOCK."
      echo; } >> "$AG/PIVOT.md"
  fi

  run_soak_queue
done
log "iteration cap ($ITER_CAP) reached $(date)"
