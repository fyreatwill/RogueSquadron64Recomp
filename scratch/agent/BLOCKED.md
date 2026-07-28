# BLOCKED — 2026-07-27, orchestration/harness mismatch (not a work-unit finding)

## What I need
A human decision on one thing: **should the top-level loop iteration run the
work unit in the foreground (no Agent-tool delegation), or should the
Stop-hook contract be changed to tolerate a multi-turn async wait?**
This is NOT a finding about the game/recomp itself — no new crash, guard, or
soak result to report. It's a process failure in how this iteration was run.

## What I already tried
1. Delegated the single work unit to a background `Agent` (general-purpose,
   `claude`) with the full ITERATION.md contract pasted into its prompt,
   intending to keep the orchestrator turn light per this session's Fable-mode
   operating style ("delegate reads, subagents do the work, orchestrator
   concludes").
2. My own turn ended while the subagent was still running. The Stop hook
   (`stop_gate.sh --verify`) checked `scratch/agent/STATUS`, saw `WORKING`,
   and blocked — correctly, since the exit contract wasn't met yet.
3. Tried three different ways to wait for the subagent without re-triggering
   the hook every turn: `Bash run_in_background` with a plain `sleep N`
   (blocked: session guidance require framing it as a wait-loop or backgrounded
   command, not a bare sleep), a `Monitor` with an `until`/`grep -qv` poll loop
   (accepted, ran for real, but only fires a notification — it doesn't stop the
   *current* turn from ending, so the hook re-fired immediately on every one of
   my responses regardless of what the monitor was doing in parallel), and
   plain repeated status checks. None of these keep a single turn open across
   the subagent's multi-minute build/run cycle, and the hook has no notion of
   "a subagent is legitimately still working" — it only sees the STATUS file.
4. Blocked 6 times in a row (the harness's own threshold). On the 6th block
   the hook explicitly instructed: stop retrying, get unblocked.
5. Before killing the subagent, checked for the boring explanation that it had
   simply stalled (e.g. stuck on an unapproved permission prompt, as literally
   happened to me directly earlier in this session when a script invocation
   required approval nobody could grant). Evidence against stalling: `find
   -mmin -20` showed live edits to `PORTING-STATE.md`, `docs/CURRENT-TRUTH.md`,
   fresh build artifacts (`build/ucode_024A10.bin`, `build/saves/...`), and new
   screenshots under `scratch/s73_post_a_scene/extendhold1/`. It was genuinely
   working, just not finished — a bad fit for this harness, not a bug in the
   subagent's execution.
6. Stopped the subagent (`TaskStop a839606601c26704b`) plus the monitor and
   the leftover sleep-poller, per the hook's instruction. Its last reported
   state: mid-verification of a `loadCraftShadowTextures` table-index guard
   patch applied directly to a **generated** file (`funcs_16.c`), not yet
   ported into a `tools/fixup_*.py` script and not yet committed anywhere.

## What was actually lost vs. preserved
`git status` after the kill shows **no tracked-file changes beyond what was
already present at session start** (`lib/N64ModernRuntime` / `lib/rt64`
modified-content, `scratch/agent/OUTCOME` deleted, `scratch/agent/STATUS`
modified — all pre-existing, not introduced this session). The
`PORTING-STATE.md`/`CURRENT-TRUTH.md` mtimes that looked "recent" were leftover
from the prior session's (s154) own final commit (`eb4408e`), not new edits —
confirmed via `git log` (HEAD is still `eb4408e`, unchanged) and `git status`
(clean on those two files). The subagent's guard-patch edit lives only in a
gitignored/generated file and is lost, which is fine per the hard rule that
hand-edits to generated code must go through a fixup script anyway — it was
never durable. **No repo state was corrupted or torn by the kill.**

## The single experiment that would refute "this is a real harness limitation"
Run one more iteration doing the actual work unit **entirely in the foreground
of the top-level turn** (no Agent-tool delegation) and see whether it
completes the full exit contract inside a single turn without tripping the
Stop hook. If it does, the fix is simply "don't delegate work units to
background agents under this contract" — a process note, not a harness change.
If a normal single-work-unit iteration (one build + one soak run) *also* can't
finish inside one turn's effective time budget even done inline, that would
point at a different, harder problem (the per-iteration wall-clock budget
itself), and *that* would need the stop_gate/loop.sh changed.

## Repo state
- No new git commit this session (still `eb4408e`, same as session start).
- `scratch/agent/STATUS` being set to `BLOCKED`.
- `scratch/agent/OUTCOME` being set to `BLOCKED`.
- `docs/CURRENT-TRUTH.md` and `PORTING-STATE.md` are untouched — the planned
  work unit never reached a result to record.
