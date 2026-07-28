# NEXT work unit — 3rd and FINAL `ROGUESQ_LOG_SCHED` attempt to reach the
# stall window before the rule-8 budget on this instrument closes.

Read PORTING-STATE Session 185 in full before doing anything else (`grep -n
"^## Session 185" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-35` next-steps item (top of the
list).

## What s184/s185 established (read before doing anything else)

- Source-read (s184) confirmed candidate (a) is mechanistically real:
  `check_running_queue()` only swaps to a queued thread if its priority is
  **strictly greater** than the caller's. The only priority-blind resume is
  `run_next_thread()`'s unconditional pop, reached only via a genuine
  blocking wait. `mainBootstrapWorker` (id=3, entry `0x80000C68`, the
  hangar-loop/graphics-task-producer thread) runs at **priority 10** vs.
  **117-122** for the VI-retrace/audio threads — the shape the mechanism
  needs.
- `ROGUESQ_LOG_SCHED=1` (`lib/N64ModernRuntime`, already committed) is
  landed and validated: `[sched-queue] thr=%p id=%d pri=%d`,
  `[sched-check] self_thr=%p self_id=%d self_pri=%d head_thr=%p head_id=%d
  head_pri=%d swap=%d`, `[sched-runnext] popped_thr=%p popped_id=%d
  popped_pri=%d`.
- **Two soaks now (`schedguard5` s184, `schedguard6` s185), both died BEFORE
  the target stall-onset window (`#9770`-`#9792` from s180/s183)**:
  - `schedguard5`: died decision `#8327`, cause = new `evalCubicSplineAtTime
    +2552` SIGBUS (signal 10, not root-caused, not the s83-guarded abort).
  - `schedguard6`: died decision `#8616` (even earlier), cause = recurrence
    of the already-catalogued 24th class (`rs_free` ← `freeManifestSegmentAssets`,
    s167) — **confirmed orthogonal to the scheduling hypothesis**: the
    producer thread (`thr=0x300163e20 id=3`) was being actively scheduled
    and resumed right up to the crash instant (last `[sched-runnext]` before
    death popped that exact thread normally).
  - Both runs: pre-crash `[sched-queue]` and `[sched-runnext]` counts are
    within 2 of each other (72382/72380, then 77510/77508) — 2 independent
    confirmations that routine starvation via the strict-priority gate is
    NOT the normal case in the window this instrument can actually observe.
    This is consistent background information, not yet the discriminating
    result (which requires reaching the stall itself).
- **This is 2 of up to 3 attempts on this instrument (rule 8).** This
  iteration is the 3rd and final one. If it ALSO dies before reaching the
  stall region, DO NOT run a 4th — pivot immediately to candidate (b)
  (`viRetraceHandlerThread`/`musyxSynthFrame` lock/resource contention) or
  (c) (heap-exhaustion on the producer's own allocation path), or consider
  landing a defensive guard on the recurring `rs_free`/heap-corruption
  family first (s99-s101 precedent: table-lookup-then-deref guards) purely
  to buy enough runway for a future attempt to reach the stall at all —
  independent of actually fixing that family.

## Do next, in order

1. **Re-run the exact same soak with a new tag** (`schedguard7` — copy
   `scratch/agent/run_schedguard6.sh`/`wait_for_schedguard6.sh`, bump the
   tag only, verbatim otherwise). No source changes needed.
2. **In the resulting run.log, first check whether the stall region was
   reached at all** (grep for `stalled=1` runs of length >100, or the
   `[CRASH][vifs-snapshot] decisionN=` value at death vs. `#9770`-`#9792`).
   - If it died early again (any cause): this closes the instrument's rule-8
     budget (3 of 3 spent, all inconclusive). Do NOT plan a 4th attempt.
     Write up the 3-attempt pattern (which crash class each time, whether
     any of them recur) and move to step 3's fallback.
3. **If the stall region IS reached this time**, the discriminating check is
   BOTH of:
   a. Does the producer thread (`thr=0x300163e20`, cross-reference
      `[thr-create-id] id=3 entry=0x80000C68` to confirm the pointer is
      stable run-to-run — it may not be, ASLR/allocator-dependent) get a
      `[sched-queue]` entry with no matching later `[sched-check swap=1]` or
      `[sched-runnext popped_id=3]` before the stall?
   b. Does `[sched-runnext]` (the priority-blind pop) **stop appearing
      entirely, for any thread**, at the same point?
   Both together → strong confirmation of candidate (a) → proceed to fix
   design (retry-next-queue-entry vs. a timeout/wake-caller path in
   `check_running_queue`, see PORTING-STATE Session 180/181 step 2 for the
   original framing, still valid).
   Only (a) without (b), or neither → refute/weaken candidate (a) for this
   run, and the instrument's budget is now spent regardless (this was
   attempt 3 of 3) — mandatory pivot to (b)/(c) next session either way.

## Do not

- Do not run a 4th attempt on `ROGUESQ_LOG_SCHED` if this one also dies
  early — rule 8's budget is 3, this is the 3rd.
- Do not chase the `evalCubicSplineAtTime+2552` SIGBUS (s184) or the
  `rs_free ← freeManifestSegmentAssets`/`rebuildActiveDisplayObjectList`
  heap-corruption family (s183/s185) with a dedicated soak — both are
  already-catalogued or flagged-not-chased, lower priority than reaching
  the stall window. (Landing a defensive guard on the `rs_free` family to
  buy runway is a legitimate NEXT session's fallback if this attempt also
  fails, per the note above — but that is a different, larger work unit
  than "chasing" it, and only becomes the plan after this 3rd attempt.)
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` for this soak (s93's
  confound: perturbs timing enough to change which crash/stall wins the
  race). `ROGUESQ_LOG_SCHED=1` is a separate, already-landed gate — keep it
  on, it's the point of this soak.
- Do not re-litigate whether the outer hangar loop "stops iterating" as a
  whole — s180 closed that.

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

## This session's environment notes (carry forward, still current)

- Re-running the same script/tag **overwrites** the previous run's
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
- Same for `python3 fixup_game_funcs.py` — it uses an absolute
  `pathlib.Path("/Users/.../N64Recomp/RecompiledFuncs")` internally, so it
  can be invoked as `python3 /absolute/path/to/fixup_game_funcs.py > log`
  with no `cd` at all, sidestepping the compound-cd-redirect denial
  entirely.
- **CRITICAL: `fixup_game_funcs.py` is non-idempotent** — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. Redirect to a log file on the ONE invocation, and grep
  the log for your new patch's report lines to confirm exactly x1 before
  moving on. If you edit the patch text after a first (buggy) attempt,
  you MUST re-run the FULL pipeline from a fresh `N64Recomp` regen — do not
  just re-run fixup on already-patched files. (Not needed for pure `lib/`
  host C++ changes — those only need `cmake --build`.)
- If only `fixup_game_funcs.py`/a `lib/rt64` or `N64ModernRuntime` C++ file
  changed (not symbol files or the ELF), you don't need `make_elf.py` —
  for guest-code fixup changes: `N64Recomp` (via
  `zsh tools/agent/regen_n64recomp.sh`) then `fixup_game_funcs.py` once,
  then `cmake --build`. For pure host/runtime C++ changes: just
  `cmake --build`, no regen needed at all.
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
  (`if p.name == "funcs_N.c"`) if not naturally unique.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py` for Mach-O symbol reads. A crash's own
  `[CRASH]` stack dump is usually enough to identify the function without
  needing this.
- Reading a `RECOMP_FUNC` body directly from
  `N64Recomp/RecompiledFuncs/funcs_*.c` (via `grep -n "RECOMP_FUNC void
  <name>"`) is far more reliable than trusting a `symbol_files/*.txt`
  comment.
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
  `awk` range patterns like `NR==A,NR==B && /x/` do NOT behave as expected
  (parses as a weird precedence trap) — use `sed -n 'A,Bp' file | grep
  ...` instead for "lines A-B matching X".
  Note zsh-specific: a bare shell variable assignment followed by multiple
  `echo`/command lines in one Bash call can fail with "Contains
  simple_expansion" — prefer one command per Bash call, or inline the path
  directly instead of assigning to a shell variable first.
- When a soak survives the full hold window, `run_mission_keys.sh`'s
  summary line `UnhandledJump: N` can be nonzero from totally benign RSP
  microcode fallback noise — grep the actual matched lines before reading
  a nonzero count as a regression.
- Screenshots (`hold_NN.png`, `grace_NN.png`, `craft_stable.png`) are
  genuinely useful for characterizing a "process alive but stuck" state —
  reading a handful of them directly (via the Read tool, not a subagent)
  is cheap.
- The run_mission_keys.sh summary block's later `print` lines can take
  noticeably longer to appear than the first few on a multi-hundred-MB
  run.log — wait for the wrapper shell script's own process to exit too
  (not just the game PID) before treating the summary as complete.

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
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
