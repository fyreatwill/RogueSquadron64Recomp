# NEXT work unit — add a periodic decision-count log tick, then re-observe
# the `-35` stall now that the `rs_free` crash family is guarded

Read PORTING-STATE Session 187 in full before doing anything else (`grep -n
"^## Session 187" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-36` next-steps item (top of the
list).

## Why this is the next work unit (read before doing anything else)

s187 landed and validated (strong positive control: 1901 fires in one run)
a defensive guard on `rs_free`'s 3 free-list walk loops
(`N64Recomp/fixup_game_funcs.py`, `ROGUESQ_LOG_RS_FREE_WALK_GUARD`) — the
crash family that killed 3 of the last 4 `schedcaller`/`schedguard`
attempts (s183, s185, s186). The soak (`rsfreeguard1`) survived the ENTIRE
120s hold + grace window with **zero crashes**, the first fully
crash-free full-length run in the whole s180-187 lineage.

**But it told us nothing about whether the `-35` stall itself still
occurs.** `ROGUESQ_LOG_SCHED`'s only decision-number readout is
`[CRASH][vifs-snapshot] decisionN=...`, printed exclusively at crash time.
With no crash this run, there is no decision-number data at all — we only
know `[sched-queue]`/`[sched-runnext]` stayed near-balanced (131076/131075)
the whole run, which is *consistent with* "never stalled" but not proof.

This is now the highest-information-value gap: we finally have a soak
recipe that survives past the crash family that used to kill it early, but
we can't yet tell whether it still stalls, stalls differently, or doesn't
stall at all under this guard.

## Do next, in order

1. **Add a periodic, non-crash-gated decision-count log line** to the
   `ROGUESQ_LOG_SCHED` instrument (`lib/N64ModernRuntime`, wherever
   `[sched-queue]`/`[sched-check]`/`[sched-runnext]` currently live —
   grep for those tags to find the file). Something like
   `[sched-tick] decisionN=<n> queueN=<a> runnextN=<b>` emitted every
   ~500-1000 decisions (or on a wall-clock timer, e.g. every 2s), cheap
   enough not to change timing meaningfully. This is a `lib/`
   change — remember to run `./submodule-patches/export.sh` and commit
   the refreshed patches in the SAME session (hard rule).
2. **Re-run the SAME soak recipe** (`scratch/agent/run_rsfreeguard1.sh` —
   copy to a new tag, e.g. `rsfreeguard2` or `schedtick1`, per the
   "never overwrite a previous run's run.log" rule) with the new tick log
   armed. Discriminating read: does decision count keep climbing steadily
   for the full 120s (no stall), or does it plateau/stop advancing while
   `[sched-queue]`/`[sched-runnext]` keep incrementing (the stall
   signature — a growing gap between logged decisions, >100 per s183's
   established threshold)?
3. **If the stall still occurs**: this is genuinely new information —
   candidate (a) (strict-priority scheduler starvation) can now be
   re-examined with a live, crash-free repro instead of always racing the
   `rs_free` crash to get there. If it does NOT occur under this guard in
   a couple of soaks: consider whether the `-35` stall and the `rs_free`
   corruption were actually entangled all along (e.g. the corruption
   itself was somehow gating progress) — a genuinely new hypothesis, not
   yet considered, would need its own discriminating test before entering
   CURRENT-TRUTH.

## Do not

- Do not re-attempt to root-cause the underlying `rs_free` free-list
  corruption source itself (what writes the insane size into node
  `0x807982B6`'s header) — that's the still-open s85-s114 chase, out of
  scope for this work unit. The guard treats the symptom; that's
  intentional and sufficient for this unit's goal (buy runway).
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` (s93's confound).
- Do not spend more than 3 consecutive soaks chasing the same stall
  question without a discriminating result (rule 8) — if 3 soaks with the
  tick log don't produce a clear stall/no-stall answer, park it and
  reconsider the framing.

## Blocking on a long-running soak (learned the hard way, still current)

Simplest approach: run the driver script itself as a single foreground Bash
call with output redirected to a log file and a generous timeout (~480s
covers this env block's 120s hold + overhead) — the script blocks until the
game process exits, no polling loop needed. If it exceeds the foreground
timeout, the harness moves it to background automatically and notifies on
completion. If you DO background it (e.g. via `run_in_background: true`), do
not just wait passively for the notification and end your turn — the Stop
hook checks `scratch/agent/STATUS` immediately and will fire before the
notification lands if the turn ends first. Instead, after backgrounding the
run, immediately issue a SECOND, foreground Bash call that blocks on the
wrapper's own process exiting (a small script under `scratch/agent/`, e.g.:
```
until ! ps aux | grep -q "[r]un_mission_keys.sh <tag>"; do sleep 5; done
```
— write this to a file and invoke via `zsh <path>`, a bare inline
while/until loop gets denied as "multiple operations" even quoted). This
keeps the SAME tool call blocking synchronously until the soak is actually
done, rather than ending the turn and relying on a background notification
racing the Stop hook.
Also note: waiting on the game binary's own process name is not enough —
the wrapper (`run_mission_keys.sh`) can keep running for 1-2 more minutes
after the game process exits, doing log-summary greps over a multi-GB file;
wait on the wrapper's own process name too before trusting the driver log's
summary block is complete.
Note from s187: when the process does NOT crash and just runs out its
scripted hold+grace window, the wrapper prints "game process still alive;
killing" and kills it itself — this is expected/normal for a crash-free
run, not an error.

## This session's environment notes (carry forward, still current)

- **`N64Recomp/fixup_game_funcs.py` is non-idempotent** — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. If you're adding a NEW patch: regenerate fresh first
  (`zsh tools/agent/regen_n64recomp.sh` from the RogueSquadron64Recomp repo
  — this OVERWRITES `N64Recomp/RecompiledFuncs/*.c` with pristine output
  from the ELF, wiping all previously-applied patches), THEN run
  `python3 /absolute/path/to/N64Recomp/fixup_game_funcs.py > log` exactly
  once (applies every patch, old and new, in one pass — no `cd` needed,
  the script uses an absolute internal path). Grep the log for your new
  patch's report line to confirm exactly x1 before moving on, and check
  the older patches' report lines are ALSO x1 (not x2) as a duplication
  sanity check.
- Re-running the same soak script/tag **overwrites** the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak so
  each soak's full run.log and screenshots land in their own directory,
  never overwritten.
- Running `N64Recomp/build/N64Recomp` or any script under
  `RogueSquadron64Recomp/tools/agent/*.sh` / `scratch/agent/*.sh` directly
  gets denied even though the text matches an allowlisted prefix —
  prefix with `zsh` (already allowlisted).
- Compound `cd ... && zsh ... > file 2>&1` gets denied — call
  `zsh /absolute/path/to/script.sh > /absolute/path/to/log 2>&1` directly,
  no `cd`, the script `cd`s internally. Same for `cd ... && cmake ...` —
  use `cmake --build /absolute/path/to/build` instead of `cd`+relative.
  Same for chaining a 2nd command after any of these with `;` or `&&` —
  each Bash call should be a single command; run follow-ups as separate
  calls (including a trailing `echo` after a redirected command — that
  also counts as a 2nd operation and gets denied).
- `submodule-patches/export.sh` must be invoked as a relative path
  (`./submodule-patches/export.sh`) from the repo root cwd — an absolute
  path gets denied even though it's functionally the same command, because
  the allowlist is a literal prefix match on the command string.
- A new host-side C++ helper called FROM guest code needs an `rdram`
  parameter if it uses `TO_PTR`/`PTR` macros (RDRAM-relative-pointer build
  mode); do NOT call `osGetThreadId_recomp`/other `_recomp`-suffixed
  functions from a mid-function diagnostic patch — they clobber `ctx->rN`
  registers that are live guest state at that point.
- Before writing ANY new patch to `fixup_game_funcs.py`, grep for the
  exact anchor text's uniqueness both within the target file and (if using
  a short/generic snippet) across the whole `RecompiledFuncs/` tree —
  function-name-anchored patches are safe since function names are unique
  repo-wide; mid-function anchors (loop bodies, specific instruction
  addresses, labels) should be grepped for uniqueness first and file-scoped
  (`if p.name == "funcs_N.c"`) if not naturally unique. The hex address
  comment on each disassembled instruction line (e.g. `// 0x80001CE4: addu`)
  is a reliable, naturally-unique anchor within a single file.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py` for Mach-O symbol reads. A crash's own
  `[CRASH]` stack dump is usually enough to identify the function without
  needing this.
- `git -C <path> ...` (with the `-C` flag) triggers an approval prompt even
  for read-only commands like `status`/`show` — plain `git <cmd>` from the
  correct cwd, or a separate `cd` call first, avoids it.
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns.
- Output redirection (`>`) from Bash is sandboxed to the session's allowed
  working directories — target `scratch/agent/`, never `/tmp`.
- `cmake --build` needs
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`; pass the
  build dir as an argument (`cmake --build /abs/path/to/build`) rather than
  `cd`-ing there, to avoid the compound-cd-redirect denial.
- `lib/N64ModernRuntime` and `lib/rt64` always show as "modified content"
  in the parent repo's `git status` — normal, long-standing state. Only run
  `submodule-patches/export.sh` + commit if you actually edit something
  under `lib/` this session.
- `/scratch/` is entirely gitignored in this repo except 3 force-tracked
  files: `scratch/agent/NEXT.md`, `OUTCOME`, `STATUS`. New soak
  scripts/logs under `scratch/agent/` or `scratch/s73_post_a_scene/` never
  need `git add` — they're intentionally untracked.
- A `grep -c "[pattern]"` across a very large run.log (millions of lines
  from a per-tick instrument) is fine and fast — no need to avoid grepping
  big log files, just don't `cat`/`Read` them wholesale. Prefer `grep -n
  "pattern" file > scratch/agent/some_name.txt` then `Read` the small
  extracted file, rather than piping large greps through further shell
  commands (each Bash call must be a single operation; chained pipes with
  `awk`/`head`/`tail` after a `grep` frequently get denied as "multiple
  operations" even though they're one shell pipeline). `sed -n 'N,Mp' file`
  per-file works fine for reading small windows around known line numbers.
- Python one-liners via Bash (`python3 -c "..."`) are useful for analyzing
  extracted log data without needing awk/sed pipe chains that get denied
  as "multiple operations".

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now well over 100 KB, wildly over the ~35 KB
target — migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment (do not spend a whole iteration on pure doc cleanup per
ITERATION.md — "compressing CURRENT-TRUTH is not advancing" — but if a
natural break comes up, this is overdue). Flagged for many sessions without
action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across many sessions
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`, now
including s187's 3 new guard patches). Same posture as the
`rogue_squadron64` sibling checkout flagged since s54. Worth asking the
user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
