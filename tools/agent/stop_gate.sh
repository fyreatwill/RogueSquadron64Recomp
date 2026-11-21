#!/bin/bash
# Stop hook: gates the end of an autonomous iteration against the exit contract
# in tools/agent/ITERATION.md. Deterministic on purpose — it checks the artifacts
# (STATUS file, docs, commit), not the agent's account of them.
#
# stdin : hook JSON  ({session_id, stop_hook_active, ...})
# stdout: {"decision":"block","reason":"..."} to keep the turn going, or nothing to allow.
set -u
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0
# Only gate sessions the loop launched (runner.sh exports RS64_LOOP=1). An interactive
# or ad-hoc claude session in this repo must not be driven into the exit contract
# (2026-10-31 incident). --verify (loop.sh's post-hoc check) is unaffected.
if [ "${1:-}" != "--verify" ] && [ "${RS64_LOOP:-}" != "1" ]; then exit 0; fi

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
  block "You have been blocked from stopping $count times without meeting the exit contract, which means you are stuck. Stop retrying the current approach. Write scratch/agent/BLOCKED.md (what you need, from whom, what you already tried, and a line 'NEEDS-HUMAN: gate-defect'), commit any outstanding changes, write BLOCKED to scratch/agent/STATUS, and then stop."
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

head_now="$(git rev-parse HEAD 2>/dev/null)"
head_start="$(cat "$AG/ITER_START_HEAD" 2>/dev/null || echo '')"

# --- session history is append-only ------------------------------------------
# The ledger is the only memory, so an iteration may add to history but never
# rewrite it. The "a commit landed" test below cannot catch this on its own:
# `git commit --amend` on a PREVIOUS iteration's commit also moves HEAD, so it
# passes that check while destroying the session entry it rewrote. Ancestry is
# the discriminating test — amend/rebase/reset at or below the iteration's
# starting commit all detach it from HEAD's history, while amending a commit
# this iteration authored leaves it an ancestor and is fine.
if [ -n "$head_start" ] && [ "$head_now" != "$head_start" ] \
   && ! git merge-base --is-ancestor "$head_start" HEAD 2>/dev/null; then
  block "Exit contract unmet: you rewrote history. This iteration started at ${head_start:0:8}, which is no longer an ancestor of HEAD (${head_now:0:8}) — an amend, rebase, or reset landed on a commit from a previous iteration and destroyed its session entry. Recover it now: 'git reflog' lists the pre-rewrite HEAD, and 'git reset --soft <that hash>' restores those commits with your work still staged (NEVER --hard: lib/ carries uncommitted patches). Then commit your own work as a NEW commit on top. Never amend a commit you did not create this iteration."
fi

# --- BLOCKED: needs a usable write-up, but not a commit it has nothing for ----
if [ "$status" = "BLOCKED" ]; then
  [ -s "$AG/BLOCKED.md" ] || block "Exit contract unmet: STATUS is BLOCKED but scratch/agent/BLOCKED.md is missing or empty. Write it: what you need, from whom, and what you already tried — specific enough that a human can act in 2 minutes."
  # 2026-10-19: 15+ of 34 blocks (s5031-s5604) were "backlog exhausted / need a
  # direction" or "waiting on a run", and the unblock tier re-scoped every one.
  # A block must name a dependency only the human can satisfy.
  grep -qiE '^[[:space:]#*-]*NEEDS-HUMAN:[[:space:]*]*`?(install|money|system-settings|physical|credentials|gate-defect)' "$AG/BLOCKED.md" \
    || block "Exit contract unmet: STATUS is BLOCKED but scratch/agent/BLOCKED.md has no 'NEEDS-HUMAN: <install|money|system-settings|physical|credentials|gate-defect>' line. Backlog exhaustion, needing a direction, waiting on a soak, a denied command, and host load are NOT blocks. Take the first open rung of the standing goal ladder (ITERATION.md item 3c), rewrite scratch/agent/NEXT.md for it, delete BLOCKED.md, commit, and write DONE to scratch/agent/STATUS. Only if the dependency truly needs the human, add the NEEDS-HUMAN line."
  allow
fi

# --- DONE: a commit landed this iteration, and it moved the ledger ------------
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
# non-ADVANCED iterations per slug (a gate-validated ADVANCED resets the count)
# and forces a pivot at 3, blocks at 4.
grep -qE '^HYPOTHESIS-ID:[[:space:]]*[A-Za-z0-9._-]+' "$AG/NEXT.md" 2>/dev/null \
  || block "Exit contract unmet: scratch/agent/NEXT.md has no 'HYPOTHESIS-ID: <slug>' line. Add one naming the active investigation thread — keep the slug while pursuing the same hypothesis (a systematic sweep keeps ONE slug for its whole campaign; ADVANCED iterations reset the strike count), change it when you pivot or close it. The loop enforces iron rule 8 (3 strikes on stalled iterations) with it."

# s7770: a NEXT.md that schedules the generated-symbol renaming sweep when the ELF census finds no CALLED placeholder
# left is a stale plan (s7769 wrote one; the sweep closed at s6868 and the last real one, send_mesg, was named s7770).
# Skipped when the ELF or census tool is absent. RS64_RENAME_CENSUS_CMD overrides the census (tools/agent/test_rename_census_gate.sh).
if grep -qE '^HYPOTHESIS-ID:[[:space:]]*generated-symbol-renaming-sweep' "$AG/NEXT.md" 2>/dev/null; then
  rc_cmd="${RS64_RENAME_CENSUS_CMD:-python3 tools/s7770_placeholder_census.py --quiet}"
  if [ -n "${RS64_RENAME_CENSUS_CMD:-}" ] || { [ -f tools/s7770_placeholder_census.py ] && [ -f ../rogue_squadron64/build/roguesquadron.elf ]; }; then
    rc_called="$($rc_cmd 2>/dev/null | sed -n 's/^SUMMARY .*called=\([0-9][0-9]*\).*/\1/p')"
    if [ "${rc_called:-x}" = "0" ]; then
      block "Exit contract unmet: scratch/agent/NEXT.md schedules the generated-symbol renaming sweep, but tools/s7770_placeholder_census.py finds 0 CALLED placeholders left in syms/rogue_squadron.syms.toml (the rest are TAIL/UNREF, shape-only). The sweep is closed: take an owner item or the next open ladder rung instead, and give NEXT.md a different HYPOTHESIS-ID."
    fi
  fi
fi

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
  # s6994: CURRENT-TRUTH is one-bullet-per-line, so a 60 KB file can be 173
  # lines and a real compaction can never net 200 lines. Also accept a net
  # byte shrink of >=15000 B (a quarter of the 60 KB trigger).
  if [ -z "$substantive" ]; then
    base="${head_start:-HEAD~1}"
    b0="$(git show "$base:docs/CURRENT-TRUTH.md" 2>/dev/null | wc -c | tr -d ' ')"
    b1="$(git show "HEAD:docs/CURRENT-TRUTH.md" 2>/dev/null | wc -c | tr -d ' ')"
    case "$b0$b1" in ''|*[!0-9]*) ;; *)
      [ $((b0 - b1)) -ge 15000 ] && substantive="maint:CURRENT-TRUTH -$((b0 - b1)) bytes" ;;
    esac
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
  # s7724: the offline .zst reader import (tools/rs64_zopen.py) is not instrumentation; s7723 tripped on 12 of them.
  # CHURN GUARD (2026-08-14): a diagnostic-only ADVANCED iteration - one whose
  # code change adds only instrumentation (fprintf/getenv/log-tag/rs64_* probe
  # lines, or extends an existing [shade-raw]/[f5-state-payload] format string
  # with one more provenance field) and whose session entry selects/refutes/
  # closes nothing - is landing an instrument, not narrowing a hypothesis
  # (s998-s1006 threaded one join key per iteration this way).
  # Only fires on >=2 instrumentation lines AND zero discrimination phrases, so
  # a probe that selects/refutes/plans is never blocked. NOTE the discrimination
  # match is word-level (no 'H-' suffix) because the ledger writes "This selects\n
  # H-..." across a line break.
  diag="$(git diff ${range:-HEAD~1..HEAD} -- . ':(exclude)docs' ':(exclude)PORTING-STATE.md' ':(exclude)CLAUDE.md' ':(exclude)tools/agent' ':(exclude)scratch' ':(exclude).claude' 2>/dev/null \
    | grep '^+' | grep -vE '^\+[[:space:]]*(#|//|\*)' \
    | grep -v 'from rs64_zopen import zopen' \
    | grep -cE '(fprintf|getenv|ROGUESQ_LOG_|rs64_[A-Za-z0-9_]+|\[(shade-raw|f5-state|fix-zero-shade))' || true)"
  case "$diag" in ''|*[!0-9]*) diag=0 ;; esac
  if [ "$diag" -ge 2 ]; then
    ps_added="$(git diff ${range:-HEAD~1..HEAD} -- PORTING-STATE.md 2>/dev/null | grep '^+' || true)"
    if ! printf '%s\n' "$ps_added" | grep -qE '\b(selects|refutes|closes|resolves|root cause|discriminate)\b'; then
      block "OUTCOME says ADVANCED but this iteration's change is diagnostic-only ($diag instrumentation lines) and its session entry names no discrimination or next discriminator. Landing an instrument is not narrowing a hypothesis. Reach a discriminating conclusion (selects/refutes H-...), name the next discriminator, or set OUTCOME accordingly."
    fi
  fi

fi

# ORIGIN GATE (2026-08-10) - a mitigation is not an explanation.
# s640-s659 landed SKIP_WILD_W, SKIP_FL_HDR, ALLOW_FL_HDR and FL_HDR_RESTORE
# against a framebuffer writeback stomping the heap freelist, without once
# establishing why a colour image is set at 0x1F0D74 with width 1161 - a width
# this game never uses. Each of those iterations satisfied ADVANCED, so the
# contract could not see the omission. This makes it visible: when the diff
# adds mitigation-shaped machinery, the session entry must carry an ORIGIN:
# line. It does not demand that the origin be KNOWN - it demands that the
# iteration say which, so "still unexplained" accumulates in the ledger
# instead of disappearing into another passing gate.
# Scan only RUNTIME sources: the harness, its docs and CLAUDE.md talk ABOUT
# mitigation knobs constantly, and a comment mentioning one is not a landing.
# Comment lines are dropped, and one stray line is not a mitigation - a real
# one lands several. Both guards were added after this gate false-positived on
# a harness commit whose only match was the words RS64_SKIP_STOP_HOOK in a
# comment. Threshold calibrated over the last 30 commits: the six that landed
# real mitigation machinery score 2/4/4/5/8/11 and every other commit scores
# exactly 0, so >=2 separates them cleanly with no false positive.
mitig="$(git diff ${range:-HEAD~1..HEAD} -- .     ':(exclude)docs' ':(exclude)PORTING-STATE.md' ':(exclude)CLAUDE.md'     ':(exclude)tools/agent' ':(exclude)scratch' ':(exclude).claude' 2>/dev/null   | grep '^+' | grep -vE '^\+[[:space:]]*(#|//|\*)'   | grep -cE '(SKIP_|ALLOW_|_RESTORE|_GUARD|HARD_SKIP)' || true)"
case "$mitig" in ''|*[!0-9]*) mitig=0 ;; esac
if [ "$mitig" -ge 2 ]; then
  ps_added="$(git diff ${range:-HEAD~1..HEAD} -- PORTING-STATE.md 2>/dev/null | grep '^+' || true)"
  printf '%s
' "$ps_added" | grep -q 'ORIGIN:'     || block "Exit contract unmet: this iteration adds mitigation-shaped machinery (skip/allow/guard/restore, $mitig lines) but the PORTING-STATE.md session entry has no 'ORIGIN:' line. Write one of: 'ORIGIN: <who writes the value, and whether the value is legitimate>' when you attributed it, or 'ORIGIN: unattributed - <why mitigating anyway, and the experiment that would attribute it>' when you did not. Iron rule 11."
fi

# CENSUS GATE SWEEP (s7656) - closed census gates must stay closed.
# s7651/s7655 found "closed" tools/s7*_census.py gates gone RED after later sessions added code in their scope, because nothing
# re-ran them. When this iteration's commits touch runtime code (src/, submodule-patches/ = lib/, patches/) or a census tool,
# re-run tools/s7651_gate_sweep.py (result cache keyed on each tool's traced reads: an unchanged tree re-runs only the
# subprocess-spawning gates) and block on any RED gate not in tools/gate_sweep_allowed_red.txt.
# --verify only: a cold sweep is ~7 min, far beyond the Claude Stop hook's 30 s timeout; loop.sh runs --verify after every
# iteration whatever the runner and re-invokes with this message. RS64_GATE_SWEEP=0 skips it and
# RS64_GATE_SWEEP_ONLY=<regex> narrows it (tools/agent/test_gate_sweep.sh only).
if [ "$VERIFY" = 1 ] && [ "${RS64_GATE_SWEEP:-1}" != 0 ] \
   && printf '%s\n' "$touched" | grep -qE '^(src/|submodule-patches/|patches/|tools/s7[0-9]+_.*_census\.py$|tools/census_rules\.py$)'; then
  sweep_out="$(python3 tools/s7651_gate_sweep.py --new-red-vs tools/gate_sweep_allowed_red.txt \
    ${RS64_GATE_SWEEP_ONLY:+--only "$RS64_GATE_SWEEP_ONLY"} 2>&1)"
  sweep_rc=$?
  if [ "$sweep_rc" != 0 ]; then
    block "Exit contract unmet: this iteration touched runtime code or a census tool, and tools/s7651_gate_sweep.py (rc=$sweep_rc) reports census gates RED that were not RED before (3 = the sweep's own controls failed):
$(printf '%s\n' "$sweep_out" | grep -E '^  RED|new RED|control|FAIL' | head -12)
Each is a closed census class your change re-opened or a rule your change made stale. Run 'python3 tools/<gate> --controls', classify the new site (add its row / guard / rule, as that tool's docstring says), and commit. Only if the RED is a real open defect you are leaving for a later session, add '<gate> <reason>' to tools/gate_sweep_allowed_red.txt in the same commit and log it in the session entry."
  fi
fi

# AGENT TOOL TESTS (s7709) - an edit to the loop's own tooling must keep its tests green.
# tools/agent/test_*.sh were run by hand only, so a loop.sh/stop_gate.sh edit could break the soak gate, crash gate or the
# s7708 carry unnoticed. When this iteration's commits touch tools/agent/*.sh|*.py, run tools/agent/run_tests.sh (~30 s, so
# --verify only, like the census sweep). RS64_AGENT_TESTS=0 skips it (run_tests.sh exports that to stop recursion);
# RS64_AGENT_TESTS_DIR=<dir> points it at another test dir (the s7709 control only).
if [ "$VERIFY" = 1 ] && [ "${RS64_AGENT_TESTS:-1}" != 0 ] \
   && printf '%s\n' "$touched" | grep -qE '^tools/agent/[^/]+\.(sh|py)$'; then
  at_out="$(sh tools/agent/run_tests.sh ${RS64_AGENT_TESTS_DIR:+"$RS64_AGENT_TESTS_DIR"} 2>&1)"
  if [ $? != 0 ]; then
    block "Exit contract unmet: agent tool tests FAIL: $(printf '%s\n' "$at_out" | sed -n 's/^FAIL \([^ ]*\).*/\1/p' | tr '\n' ' ')
$(printf '%s\n' "$at_out" | grep '^FAIL' | head -8)
$(printf '%s\n' "$at_out" | grep -q '^FAIL' || printf '%s\n' "$at_out" | head -4)
This iteration edited tools/agent/. Run 'sh tools/agent/run_tests.sh', then fix the tool your edit broke (or the test, if the contract changed on purpose and the session entry says so), and commit."
  fi
fi

# CRASH REPORTS (s7664) - no macOS crash report of the game goes unread.
# Nothing read ~/Library/Logs/DiagnosticReports between s6534 and s7664 (22 game reports unexamined, 11-13..11-19); an owner
# crash in normal play would have been missed the same way. tools/crash_reports.py classifies each .ips as PLANT (deliberate
# control), DIAG (fault inside an env-gated instrument), FOLDED (basename/stamp quoted in PORTING-STATE.md) or NEW. Block on
# NEW. Fast (<1 s), so it runs in the hook and in --verify. RS64_CRASH_REPORTS=0 skips it (tools/crash_reports.py --selftest).
if [ "${RS64_CRASH_REPORTS:-1}" != 0 ] && [ -d "$HOME/Library/Logs/DiagnosticReports" ]; then
  cr_out="$(python3 tools/crash_reports.py --since 2026-11-13 --dir "${RS64_CRASH_DIR:-$HOME/Library/Logs/DiagnosticReports}" 2>&1)"
  if [ $? = 1 ]; then
    block "Exit contract unmet: tools/crash_reports.py found game crash reports nobody has read:
$(printf '%s\n' "$cr_out" | grep -E '^(NEW|UNPARSED)' | cut -c1-300 | head -8)
Read each one (python3 tools/crash_reports.py prints thread + top frames; the .ips is in ~/Library/Logs/DiagnosticReports). If it is a deliberate arm of your experiment, quote its basename (RogueSquadron64Recomp-YYYY-MM-DD-HHMMSS) in your PORTING-STATE entry with what produced it. If nobody planted it, it is a real crash: it outranks the current work unit (G4 reopens on a side-effect crash)."
  fi
fi

allow
