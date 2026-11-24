#!/bin/bash
# Unattended driver. Run from a Terminal INSIDE the logged-in desktop session:
#   caffeinate -dis tools/agent/loop.sh
# Each iteration is a fresh context; state lives in the docs (CURRENT-TRUTH,
# NEXT.md), which is exactly what they were built for. Usage-limit windows
# become sleeps, not handoffs.
#
# Env: ITER_CAP (default 0 = unlimited; set N for a bounded run), SLEEP_ON_LIMIT (default 1800s), MAX_LIMIT_WAITS (12),
#      LOOP_MODEL (default claude-sonnet-5-5), MAX_NO_CONTRACT (default 2),
#      SLEEP_ON_ERROR (120s) / MAX_ERR_RETRIES (4) for nonzero-rc-without-limit-wording,
#      SOAKS_BETWEEN_ITERS (2) / SOAK_TIMEOUT (600s) for the queued-soak runner,
#      UNBLOCK_ENABLE (1) / MAX_UNBLOCK_ATTEMPTS (1) / UNBLOCK_RUNNER /
#      UNBLOCK_MODEL for the automated unblock tier (see try_unblock below)
#
# RUNNER ROTATION (default when no runner= / RUNNER is given): iterations use the
# first runner in ROTATE_ORDER (default "claude codex grok") that is not cooling
# down. A runner that hits a limit is benched: claude/codex for COOLDOWN_CLAUDE /
# COOLDOWN_CODEX (4h); if claude AND codex are both limited, both are benched
# COOLDOWN_BOTH (5h) and grok carries the loop (grok benched COOLDOWN_GROK, 6h,
# when IT hits a limit - it only has a weekly cap). Priority is re-evaluated every
# iteration, so claude is retried first the moment its cooldown ends. If every
# runner is benched the loop sleeps until the soonest one reopens. Per-runner
# models: RUNNER_MODEL_CLAUDE / _CODEX / _GROK (claude falls back to LOOP_MODEL).
# Pass runner=X (or RUNNER=X) to pin one runner and disable rotation.
# If the limit message states a reset time (claude "resets 9pm (tz)", codex "try again
# at <date>"), that time is used instead of the fixed cooldowns (parse_reset.py).
# Cooldown state lives in scratch/agent/runner-limits/<runner> (epoch seconds).
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
# s7663: queued soaks and iterations never pick up the owner's build/settings.txt or a ROGUESQ_PRESET.
export ROGUESQ_SETTINGS=0
unset ROGUESQ_PRESET
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
# Self-reload: remember how we were started so an edited loop.sh takes effect at
# the next iteration boundary instead of needing a human restart (s5455 blocked
# on exactly that). The running bash keeps reading the OLD file only if the edit
# replaced the inode; an in-place edit can corrupt a running script, so edit
# loop.sh by writing a new file and renaming it over the old one.
ORIG_ARGS=("$@")
SELF_HASH="$(shasum tools/agent/loop.sh 2>/dev/null | cut -d' ' -f1)"
ITER_CAP="${ITER_CAP:-0}"   # 0 = unlimited; the BLOCKED/stop conditions below still end the run
SLEEP_ON_LIMIT="${SLEEP_ON_LIMIT:-1800}"
MAX_LIMIT_WAITS="${MAX_LIMIT_WAITS:-12}"
MAX_NO_CONTRACT="${MAX_NO_CONTRACT:-2}"
MAX_SUBSTITUTED="${MAX_SUBSTITUTED:-2}"
SLEEP_ON_ERROR="${SLEEP_ON_ERROR:-120}"
MAX_ERR_RETRIES="${MAX_ERR_RETRIES:-4}"
SOAKS_BETWEEN_ITERS="${SOAKS_BETWEEN_ITERS:-2}"
SOAK_TIMEOUT="${SOAK_TIMEOUT:-1000}"
SOAK_MAX_VOIDS="${SOAK_MAX_VOIDS:-5}"
# s7254: when every queued recipe is idle-gated and the owner is on the machine, wait up to
# SOAK_IDLE_WAIT s (polling every SOAK_IDLE_POLL s) for the host to go idle before starting
# the next paid iteration. 0 = old behaviour (check once at the boundary, then move on).
SOAK_IDLE_WAIT="${SOAK_IDLE_WAIT:-1800}"
SOAK_IDLE_POLL="${SOAK_IDLE_POLL:-30}"

# Choose the model EXPLICITLY. Without this the loop silently inherits whatever
# `model` sits in ~/.claude/settings.json — which on 2026-07-26 was "fable", the
# most expensive tier, for all 40 unattended iterations. Most of an iteration is
# mechanical (grep, instrument, rebuild, capture, reconcile, write the ledger);
# the investigative discipline lives in ITERATION.md and the Stop gate, not in
# raw model strength. Override per run: LOOP_MODEL=opus tools/agent/loop.sh
LOOP_MODEL="${LOOP_MODEL:-claude-sonnet-5-5}"

log() { echo "[loop] $*" | tee -a "$AG/loop.log"; }

# A killed/denied git leaves an empty .git/index.lock that blocks every commit,
# and the metered agent is denied deleting it (seen 2026-10-12: a 17h-old lock
# BLOCKED an iteration). Only a lock with no live git process and no open handle
# is removed, and only if it is older than 5 minutes.
clear_stale_git_lock() {
  local lock=".git/index.lock"
  [ -e "$lock" ] || return 0
  pgrep -x git >/dev/null 2>&1 && return 0
  lsof "$lock" >/dev/null 2>&1 && return 0
  [ -n "$(find "$lock" -mmin +5 2>/dev/null)" ] || return 0
  rm -f "$lock" && log "removed stale .git/index.lock"
}

# ---- runner rotation (see header) ----
if [ -z "${RUNNER_ROTATE:-}" ]; then
  if [ -n "${RUNNER:-}" ]; then RUNNER_ROTATE=0; else RUNNER_ROTATE=1; fi
fi
ROTATE_ORDER="${ROTATE_ORDER:-claude codex grok}"
COOLDOWN_CLAUDE="${COOLDOWN_CLAUDE:-14400}"
COOLDOWN_CODEX="${COOLDOWN_CODEX:-14400}"
COOLDOWN_BOTH="${COOLDOWN_BOTH:-18000}"
COOLDOWN_GROK="${COOLDOWN_GROK:-21600}"
LIMDIR="$AG/runner-limits"
mkdir -p "$LIMDIR"

limit_until() {
  local v; v="$(cat "$LIMDIR/$1" 2>/dev/null)"
  case "$v" in ''|*[!0-9]*) echo 0 ;; *) echo "$v" ;; esac
}
runner_ready() { [ "$(limit_until "$1")" -le "$(date +%s)" ]; }

# Bench a runner that hit a limit. If its claude<->codex peer is already benched
# too, both are limited "repeatedly": push both out to COOLDOWN_BOTH.
# $2 (optional) = epoch the provider said the limit reopens (parse_reset.py);
# when present it replaces the fixed cooldown, +60s of slack.
mark_limited() {
  local r="$1" reset="${2:-}" now cd peer=""
  now="$(date +%s)"
  case "$r" in
    claude) cd="$COOLDOWN_CLAUDE"; peer=codex ;;
    codex)  cd="$COOLDOWN_CODEX";  peer=claude ;;
    grok)   cd="$COOLDOWN_GROK" ;;
    *)      cd="$SLEEP_ON_LIMIT" ;;
  esac
  if [ -n "$reset" ] && [ "$reset" -gt "$now" ] 2>/dev/null; then
    echo $((reset+60)) > "$LIMDIR/$r"; touch "$LIMDIR/$r.exact"
    log "$r limited - provider says it reopens $(date -r "$reset"); benched until then"
    if [ -n "$peer" ] && [ "$(limit_until "$peer")" -gt "$now" ]; then log "claude and codex both benched - grok takes over"; fi
    return
  fi
  echo $((now+cd)) > "$LIMDIR/$r"; rm -f "$LIMDIR/$r.exact"
  if [ -n "$peer" ] && [ "$(limit_until "$peer")" -gt "$now" ]; then
    echo $((now+COOLDOWN_BOTH)) > "$LIMDIR/$r"
    # a peer bench taken from the provider's own reset time is exact: leave it
    [ -e "$LIMDIR/$peer.exact" ] || echo $((now+COOLDOWN_BOTH)) > "$LIMDIR/$peer"
    log "claude and codex both limited - benching both until $(date -r $((now+COOLDOWN_BOTH))), grok takes over"
  else
    log "$r limited - benched until $(date -r $((now+cd)))"
  fi
}

# Sets CUR_RUNNER to the highest-priority runner that is not benched; sleeps
# until the soonest cooldown ends when all of them are.
pick_runner() {
  local now r u soonest
  while true; do
    now="$(date +%s)"; soonest=0
    for r in $ROTATE_ORDER; do
      u="$(limit_until "$r")"
      if [ "$u" -le "$now" ]; then CUR_RUNNER="$r"; return; fi
      if [ "$soonest" -eq 0 ] || [ "$u" -lt "$soonest" ]; then soonest="$u"; fi
    done
    log "all runners benched - sleeping until $(date -r "$soonest")"
    sleep $((soonest-now+5))
  done
}

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

# s7708: an exit contract still unmet after MAX_CONTRACT_RETRIES used to
# vanish - the retries are told to checkpoint, not to fix, and the next
# iteration started with no signal (census sweep stayed RED s7702-s7706).
# contract_carry_write saves the verdict; build_prompt_file prepends it (and a
# rule-8 PIVOT.md) to ITERATION.md; contract_carry_clear drops it once the gate
# passes. Kept as functions so tools/agent/test_contract_carry.sh can run them.
contract_carry_write() {
  { echo "## Unmet contract from the previous iteration (fix FIRST)"
    echo "Written by loop.sh $(date): stop_gate.sh --verify still failed after"
    echo "the contract retries. Fixing this outranks NEXT.md; it is deleted"
    echo "automatically once stop_gate.sh --verify passes."
    echo
    printf '%s\n' "$1"
    echo; } > "$AG/CONTRACT-CARRY.md"
}
contract_carry_clear() { rm -f "$AG/CONTRACT-CARRY.md"; }
build_prompt_file() {
  # A rule-8 forced pivot (written after 3 consecutive non-ADVANCED iterations
  # on one HYPOTHESIS-ID) rides in as a preamble on the standard prompt.
  prompt_file=tools/agent/ITERATION.md
  local pre=""
  [ -s "$AG/CONTRACT-CARRY.md" ] && { pre="$pre $AG/CONTRACT-CARRY.md"; log "unmet-contract carry preamble active this iteration"; }
  [ -s "$AG/PIVOT.md" ] && { pre="$pre $AG/PIVOT.md"; log "rule-8 pivot preamble active this iteration"; }
  if [ -n "$pre" ]; then
    # shellcheck disable=SC2086
    cat $pre tools/agent/ITERATION.md > "$AG/ITERATION_WITH_PIVOT.md"
    prompt_file="$AG/ITERATION_WITH_PIVOT.md"
  fi
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
host_idle_s() { ioreg -c IOHIDSystem | awk '/HIDIdleTime/{printf "%d\n",$NF/1e9; exit}'; }
host_locked() { /usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes'; }
# SOAK_IDLE_FEED=<file> overrides the idle reading (tail -1) for tools/agent/test_soak_idle_gate.sh.
soak_host_idle() {
  local i
  if [ -n "${SOAK_IDLE_FEED:-}" ]; then i=$(tail -1 "$SOAK_IDLE_FEED"); else host_locked && return 1; i=$(host_idle_s); fi
  [ "${i:-0}" -ge "$1" ]
}
# s7314: one game at a time in the soak phase. The iteration has ended when a recipe starts, so any
# game alive then is a leftover (an iteration arm or a soak whose process group escaped the kill);
# it would double CPU load, steal focus, and be picked by a by-name pid lookup. SOAK_GAME_NAME
# overrides the process name for tools/agent/test_soak_idle_gate.sh.
soak_kill_games() {
  local p; p=$(pgrep -x "${SOAK_GAME_NAME:-RogueSquadron64Recomp}" | tr '\n' ' '); p=${p% }
  [ -z "$p" ] && return 1
  kill -9 $p 2>/dev/null; sleep 1; echo "$p"
}
# One pass over the queue. Sets _soak_ran (recipes run) and _soak_skipped / _soak_minneed
# (idle-gated recipes left queued, and the smallest idle they asked for).
run_soak_pass() {
  local qdir="$AG/soak_queue" rdir="$AG/soak_results" ran=0
  _soak_ran=0; _soak_skipped=0; _soak_minneed=0
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
    # A recipe may raise its own cap with a header line "# SOAK_TIMEOUT=<secs>".
    local cap="$SOAK_TIMEOUT" hdr
    hdr="$(sed -n 's/^# SOAK_TIMEOUT=\([0-9][0-9]*\).*/\1/p' "$recipe" | head -1)"
    [ -n "$hdr" ] && cap="$hdr"
    # s7234: a key-driven/fullscreen recipe declares "# SOAK_NEEDS_IDLE=<secs>". It is
    # skipped (left queued) while the owner is on the machine or the screen is locked,
    # and an exit 2 (the recipe's own human/lock/sleep void) re-queues it, up to
    # SOAK_MAX_VOIDS times. Before this the loop launched s7233b with the owner active,
    # it voided at t=0 and was filed under done/ - the measurement was lost.
    local need vfile nv
    need="$(sed -n 's/^# SOAK_NEEDS_IDLE=\([0-9][0-9]*\).*/\1/p' "$recipe" | head -1)"
    vfile="$qdir/.${name}.voids"
    if [ -n "$need" ] && ! soak_host_idle "$need"; then
      log "soak $name skipped: host not idle (needs ${need}s, idle $(host_idle_s)s, locked=$(host_locked && echo y || echo n))"
      _soak_skipped=$((_soak_skipped+1))
      { [ "$_soak_minneed" = 0 ] || [ "$need" -lt "$_soak_minneed" ]; } && _soak_minneed=$need
      continue
    fi
    # s7287: run the recipe under the shell its shebang names. Before this every recipe ran
    # under /bin/bash, so a #!/bin/zsh recipe using zsh syntax (a glob qualifier) died with a
    # bash syntax error, exit 2, which the idle gate filed as a human/lock VOID and re-queued.
    local sh=/bin/bash
    head -1 "$recipe" | grep -q 'zsh' && sh=/bin/zsh
    if ! "$sh" -n "$recipe" >"$slog" 2>&1; then
      rm -f "$vfile"
      printf '%s | %s | rc=SYNTAX (%s -n failed, not run) | 0s | %s\n' "$ts" "$name" "$sh" "$slog" >> "$AG/SOAK-RESULTS.md"
      mv "$recipe" "$qdir/done/${name}_${ts}.sh"
      log "soak $name rejected: $sh -n failed"
      continue
    fi
    local fg lg note=""
    if fg=$(soak_kill_games); then
      note=" | foreign game killed before start: pids $fg"
      log "soak $name: leftover game(s) alive before start, SIGKILLed: $fg"
    fi
    log "soak $name starting (cap ${cap}s, $sh) -> $slog"
    t0=$SECONDS
    perl -e 'setpgrp(0,0); exec @ARGV' "$sh" "$recipe" >"$slog" 2>&1 &
    pid=$!
    ( sleep "$cap" && kill -9 -- -"$pid" 2>/dev/null ) &
    wd=$!
    rc=0; wait "$pid" 2>/dev/null || rc=$?
    kill "$wd" 2>/dev/null; wait "$wd" 2>/dev/null
    dur=$((SECONDS - t0))
    if lg=$(soak_kill_games); then
      note="$note | own game outlived the recipe, SIGKILLed: pids $lg"
      log "soak $name: game(s) still alive after the recipe, SIGKILLed: $lg"
    fi
    if [ -n "$need" ] && [ "$rc" = 2 ]; then
      nv=$(( $(cat "$vfile" 2>/dev/null || echo 0) + 1 ))
      echo "$nv" > "$vfile"
      if [ "$nv" -lt "$SOAK_MAX_VOIDS" ]; then
        printf '%s | %s | rc=2 VOID (human/lock/sleep) %s/%s, re-queued | %ss | %s%s\n' "$ts" "$name" "$nv" "$SOAK_MAX_VOIDS" "$dur" "$slog" "$note" >> "$AG/SOAK-RESULTS.md"
        log "soak $name voided (rc=2), re-queued ($nv/$SOAK_MAX_VOIDS)"
        ran=$((ran+1)); _soak_ran=$ran; continue
      fi
    fi
    rm -f "$vfile"
    # s7456 class DL: rc alone misread 3 of 30 summarised runs (s7449 rc=1 benign re-init, s7450 rc=137 cap,
    # s7452 rc=0 with a planted dead arm), so the line also carries the recipe's own per-arm summary fields.
    local ev
    ev="$(zsh "${SOAK_VERDICT_TOOL:-tools/agent/soak_verdict_fields.sh}" "$slog" 2>/dev/null | head -1)"
    printf '%s | %s | rc=%s | %ss | %s%s | %s\n' "$ts" "$name" "$rc" "$dur" "$slog" "$note" "${ev:-arms=? (verdict tool failed)}" >> "$AG/SOAK-RESULTS.md"
    mv "$recipe" "$qdir/done/${name}_${ts}.sh"
    log "soak $name finished rc=$rc after ${dur}s"
    ran=$((ran+1)); _soak_ran=$ran
  done
}
run_soak_queue() {
  # s7314: reap an iteration's leftover game even when the queue is empty, so it cannot
  # survive into the next iteration (where a by-name pid lookup would pick it).
  local lf
  if lf=$(soak_kill_games); then
    printf '%s | loop | leftover game alive after the iteration, SIGKILLed: pids %s\n' "$(date +%Y%m%d-%H%M%S)" "$lf" >> "$AG/SOAK-RESULTS.md"
    log "soak phase: leftover game(s) alive after the iteration, SIGKILLed: $lf"
  fi
  run_soak_pass
  [ "$_soak_ran" = 0 ] && [ "$_soak_skipped" -gt 0 ] && [ "${SOAK_IDLE_WAIT:-0}" -gt 0 ] || return 0
  local t0=$SECONDS
  log "soak phase: ${_soak_skipped} idle-gated recipe(s) waiting; polling up to ${SOAK_IDLE_WAIT}s for ${_soak_minneed}s idle"
  while [ $((SECONDS - t0)) -lt "$SOAK_IDLE_WAIT" ]; do
    sleep "$SOAK_IDLE_POLL"
    if soak_host_idle "$_soak_minneed"; then
      log "soak phase: host idle after $((SECONDS - t0))s wait - running the queue"
      run_soak_pass; return 0
    fi
  done
  log "soak phase: idle wait expired after $((SECONDS - t0))s - starting the iteration"
}

# Computed once per run and reused on every iteration's finished-line stamp,
# so per-model/runner analysis of loop.log doesn't have to reverse-engineer
# attribution from narrative text (see 2026-08-12 loop.log audit).
runner_desc="$(LOOP_MODEL="$LOOP_MODEL" tools/agent/runner.sh --describe)"
# Pin whatever model --describe detected (including grok/codex's own live
# default, see runner.sh) for the rest of THIS run, so every iteration - and
# the finished-line stamp below - uses exactly the model just logged instead
# of re-resolving (and possibly drifting, e.g. mid-run default change) later.
if [ "$RUNNER_ROTATE" != 1 ] && [ -z "${RUNNER_MODEL:-}" ]; then
  detected_model="$(printf '%s' "$runner_desc" | grep -oE 'model=[^ ]+' | cut -d= -f2)"
  case "$detected_model" in
    ''|'<unresolved>') : ;;  # leave RUNNER_MODEL unset, runner.sh falls back to its own default per-call
    *) export RUNNER_MODEL="$detected_model" ;;
  esac
fi
if [ "$RUNNER_ROTATE" = 1 ]; then
  log "run starting $(date) — runner rotation: $ROTATE_ORDER (LOOP_MODEL=$LOOP_MODEL) cap=$ITER_CAP"
else
  log "run starting $(date) — $runner_desc cap=$ITER_CAP"
fi

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
if [ "${RS64_LOOP_SOAKS_FIRST:-0}" = 1 ]; then
  unset RS64_LOOP_SOAKS_FIRST
  log "running the soak phase deferred from the previous process (s7235)"
  run_soak_queue
fi
while [ "$ITER_CAP" -eq 0 ] || [ "$n" -lt "$ITER_CAP" ]; do

  cur_hash="$(shasum tools/agent/loop.sh 2>/dev/null | cut -d' ' -f1)"
  if [ -n "$cur_hash" ] && [ "$cur_hash" != "$SELF_HASH" ]; then
    if bash -n tools/agent/loop.sh 2>/dev/null; then
      log "loop.sh changed on disk - re-executing the new version"
      exec /bin/bash tools/agent/loop.sh "${ORIG_ARGS[@]}"
    fi
    log "loop.sh changed on disk but fails 'bash -n' - keeping the running version"
    SELF_HASH="$cur_hash"
  fi

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
  # s7893: the owner's launchd prune (~/.local/bin/rs64-scratch-prune.sh) keeps only scratch files cited by exact path
  # in a tracked file; refresh the gates' retained-capture manifest so new captures are cited before they age out.
  python3 tools/s7893_retained_manifest.py 2>&1 | tee -a "$AG/loop.log"

  # Re-publish the three public GitHub forks (main repo fast-forward + the
  # N64Recomp / decomp source mirrors). Backgrounded so a slow network never
  # delays an iteration; guards and results go to scratch/agent/publish.log,
  # a refusal to scratch/agent/PUBLISH-BLOCKED.md. Never affects the loop.
  # RS64_NO_PUBLISH=1 turns it off.
  if [ -z "${RS64_NO_PUBLISH:-}" ] && [ -x tools/agent/publish_forks.sh ]; then
    ( nohup tools/agent/publish_forks.sh >/dev/null 2>&1 & )
  fi

  clear_stale_git_lock
  n=$((n+1))
  log "iteration $n starting $(date)"
  echo WORKING > "$AG/STATUS"
  rm -f "$AG/OUTCOME" "$AG/SUBSTITUTION.md"
  touch "$AG/ITER_START_MARK"   # the gate dates run artifacts against this
  echo 0 > "$AG/.stop_blocks"
  iter_start_head="$(git rev-parse HEAD 2>/dev/null)"
  printf '%s\n' "$iter_start_head" > "$AG/ITER_START_HEAD"

  build_prompt_file
  if [ "$RUNNER_ROTATE" = 1 ]; then
    pick_runner
    export RUNNER="$CUR_RUNNER"
    mv_var="RUNNER_MODEL_$(printf '%s' "$RUNNER" | tr '[:lower:]' '[:upper:]')"
    export RUNNER_MODEL="${!mv_var:-}"
    runner_desc="$(LOOP_MODEL="$LOOP_MODEL" tools/agent/runner.sh --describe)"
    log "iteration $n runner: $runner_desc"
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
  elif printf '%s' "$errtxt" | grep -qiE 'monthly spend limit|spend limit|credit balance|insufficient quota|insufficient balance|balance exhausted|payment required'; then
    if [ "$RUNNER_ROTATE" = 1 ]; then
      # Providers word 5-hour windows as spend caps (see the probe note below);
      # rotating away and retrying after the cooldown is right either way.
      mark_limited "$RUNNER" "$(printf '%s' "$errtxt" | tools/agent/parse_reset.py 2>/dev/null)"; n=$((n-1)); continue
    fi
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
    if [ "$RUNNER_ROTATE" = 1 ]; then
      mark_limited "$RUNNER" "$(printf '%s' "$errtxt" | tools/agent/parse_reset.py 2>/dev/null)"; n=$((n-1)); continue   # an unworked window burns no iteration
    fi
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
    if [ "$errs" -ge "$MAX_ERR_RETRIES" ] && [ "$RUNNER_ROTATE" = 1 ]; then
      # Unrecognised failure wording must not kill a rotating run while another
      # runner is available: bench this one for 30 min and move on.
      for r in $ROTATE_ORDER; do
        if [ "$r" != "$RUNNER" ] && runner_ready "$r"; then
          echo $(( $(date +%s) + ${COOLDOWN_ERROR:-1800} )) > "$LIMDIR/$RUNNER"
          log "$RUNNER failed $errs times with no limit wording - benched ${COOLDOWN_ERROR:-1800}s, rotating to $r"
          errs=0; n=$((n-1)); continue 2
        fi
      done
    fi
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
      if printf '%s' "$verdict" | grep -q 'census gates RED'; then
        # s7708: s7702-s7706 retries checkpointed and left the sweep RED;
        # a close-out can never satisfy this condition.
        echo
        echo "## EXCEPTION: this verdict is a census-gate RED"
        echo "A checkpoint close-out does NOT clear it. Read the RED gates' flagged"
        echo "sites, classify each (add a census rule/table row, or fix the code),"
        echo "re-run python3 tools/s7651_gate_sweep.py --jobs 2 until 0 RED, commit."
      fi
    } > "$AG/RETRY_PROMPT.md"
    # Retries fall back to the claude runner: grok runs the Stop hook and aborts
    # the whole turn on a block (observed as stopReason=Cancelled after ~3
    # calls), so a grok retry can never satisfy the contract it was sent to fix.
    # deepseek is exempt — it IS the claude CLI on another endpoint, so it
    # handles a hook block normally, and routing its retries to Anthropic would
    # quietly spend the wrong provider's quota on every unmet contract.
    retry_runner=claude
    [ "${RUNNER:-claude}" = "deepseek" ] && retry_runner=deepseek
    if [ "$RUNNER_ROTATE" = 1 ]; then
      retry_runner=""
      for r in claude codex; do runner_ready "$r" && { retry_runner="$r"; break; }; done
      if [ -z "$retry_runner" ]; then
        log "contract unmet but claude and codex are both benched - skipping retries"
        break
      fi
    fi
    # RUNNER_MODEL is pinned to the ORIGINAL runner's model (see the
    # --describe block above) and is meaningless - or actively wrong, a
    # foreign provider's slug - for whichever runner this retry switches to.
    # Clearing it here lets runner.sh fall back to LOOP_MODEL/its own default
    # instead of e.g. handing Claude Code a codex model id (found 2026-08-13:
    # a codex run pinned to a since-retired "gpt-5.6-luna" 404'd, and the
    # claude retry inherited that same string as --model and 404'd too,
    # silently reducing the automated retry tier to zero attempts).
    clear_stale_git_lock
    out="$(RUNNER=$retry_runner RUNNER_MODEL= LOOP_MODEL="$LOOP_MODEL" tools/agent/runner.sh "$AG/RETRY_PROMPT.md")"
    log_runner_output "$out"
    # A retry that itself hits a limit is not a contract failure - stop retrying.
    # (Raw-output match is acceptable here: a false positive merely stops
    # retrying early, it does not put the loop to sleep.)
    if printf '%s' "$out" | grep -qiE 'usage limit|rate.?limit|spend limit|overloaded'; then
      log "retry $cr hit a provider limit; abandoning contract retries this iteration"
      [ "$RUNNER_ROTATE" = 1 ] && mark_limited "$retry_runner" "$(printf '%s' "$out" | tools/agent/parse_reset.py 2>/dev/null)"
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
  # s7708: carry the verdict into the next prompt on EVERY unmet exit (retry
  # cap or a limit break), and drop the carry once the gate passes.
  if [ "$contract_ok" = "1" ]; then contract_carry_clear
  else contract_carry_write "$(tools/agent/stop_gate.sh --verify 2>&1)"; fi

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
  # non-scratch file, and not a >=200-line CURRENT-TRUTH compaction). A mapping
  # edit under tools/rename* does NOT count: it commits only a rename dict entry
  # whose regen output is gitignored, so it moves no build/runtime artifact
  # (2026-08-29: the churn evasion -- 61/865 commits were exactly this). Any real
  # work resets it. State lives outside the repo so the metered agent cannot
  # reset its own meter. Tunable via NOENG_PIVOT / NOENG_BLOCK.
  NOENGSTATE="${TMPDIR:-/tmp}/.rs64-noeng-state"
  NOENG_PIVOT="${NOENG_PIVOT:-6}"; NOENG_BLOCK="${NOENG_BLOCK:-12}"
  noeng=0; [ -f "$NOENGSTATE" ] && read -r noeng < "$NOENGSTATE" 2>/dev/null
  case "${noeng:-0}" in ''|*[!0-9]*) noeng=0 ;; esac
  eng_change=0
  if [ -n "$iter_start_head" ] && git diff --name-status "${iter_start_head}..HEAD" 2>/dev/null | awk '
        $1 ~ /^A/ && $2 !~ /^scratch\// && $2 !~ /^tools\/rename/ { f=1 }
        $2 !~ /^scratch\// && $2 != "PORTING-STATE.md" && $2 !~ /^docs\// && $2 != "CLAUDE.md" && $2 !~ /^tools\/rename/ { f=1 }
        END { exit(f?0:1) }'; then
    eng_change=1
  fi
  if [ "$eng_change" = "0" ] && [ -n "$iter_start_head" ]; then
    shrink="$(git diff --numstat "${iter_start_head}..HEAD" 2>/dev/null -- docs/CURRENT-TRUTH.md | awk '{s+=$2-$1} END{print s+0}')"
    case "$shrink" in ''|*[!0-9-]*) shrink=0 ;; esac
    [ "$shrink" -ge 200 ] && eng_change=1
    # s6994: byte criterion, mirrors stop_gate.sh (one-bullet-per-line doc)
    b0="$(git show "${iter_start_head}:docs/CURRENT-TRUTH.md" 2>/dev/null | wc -c | tr -d ' ')"
    b1="$(git show "HEAD:docs/CURRENT-TRUTH.md" 2>/dev/null | wc -c | tr -d ' ')"
    case "$b0$b1" in ''|*[!0-9]*) ;; *) [ $((b0 - b1)) -ge 15000 ] && eng_change=1 ;; esac
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
      echo "moves a build/runtime artifact (an M5 de-stub per docs/M5-AUDIO-PLAN.md, an"
      echo "M3 guard-class audit, or a route-wall change) -- NOT a tools/rename* mapping"
      echo "edit, which no longer counts -- or re-scope scratch/agent/NEXT.md."
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
      echo "THIS iteration you MUST land a committed change that moves a BUILD or"
      echo "RUNTIME artifact, one of:"
      echo "  (a) De-stub the next concrete step in docs/M5-AUDIO-PLAN.md and commit the"
      echo "      generated/runtime change -- a real edit, not another log probe; or"
      echo "  (b) Land an M3 guard-class audit that commits a guard/code change (next"
      echo "      steps #2), or attack the VI-640 route wall (next steps #1) with a"
      echo "      change that alters the boot/route path -- not another observation."
      echo "The generated-symbol-renaming sweep does NOT satisfy this: a tools/rename*"
      echo "mapping edit commits no build/runtime artifact and no longer resets this"
      echo "meter. If neither (a) nor (b) is possible, go BLOCKED with a specific"
      echo "question rather than another observation-only audit, which does NOT satisfy"
      echo "this and extends the streak toward a loop block at $NOENG_BLOCK."
      echo; } >> "$AG/PIVOT.md"
  fi

  # s7235: the soak phase must run under the CURRENT loop.sh. The self-reload above only
  # fires at the top of the next iteration, so an iteration that edited run_soak_queue
  # (s7234's idle gate) had its first queued soak run by the OLD in-memory function:
  # s7234_widewin_r launched at idle=5 s, voided at t=0 and was filed under done/.
  # Re-exec first and let the new process run the queue before its first iteration.
  cur_hash="$(shasum tools/agent/loop.sh 2>/dev/null | cut -d' ' -f1)"
  if [ -n "$cur_hash" ] && [ "$cur_hash" != "$SELF_HASH" ] && bash -n tools/agent/loop.sh 2>/dev/null; then
    log "loop.sh changed on disk - re-executing before the soak phase"
    RS64_LOOP_SOAKS_FIRST=1 exec /bin/bash tools/agent/loop.sh "${ORIG_ARGS[@]}"
  fi
  run_soak_queue
done
log "iteration cap ($ITER_CAP) reached $(date)"
