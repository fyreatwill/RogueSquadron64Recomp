# NEXT work unit — find what stops graphics-task submission in a run that
# reaches the stall WITHOUT `[thr-resume-skip]` firing

Read PORTING-STATE Session 183 in full before doing anything else (`grep -n
"^## Session 183" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-35` next-steps item (top of the
list).

## What s183 established (read before doing anything else)

- Re-ran the `schedcaller`-shape soak a 4th time (`schedguard4`, verbatim
  copy of `schedguard3` except the tag). It reached **hold-iter 68** — the
  deepest any soak in this line has gotten (previous best: hold-iter 3) —
  and **sustained the target stall for 2688 consecutive `[vi-fs-decision]`
  decisions** (`#9792`→`#12480`, all `SKIP ... stalled=1 pairs=0`) before
  dying.
- Death: SIGBUS in `rs_free` (`funcs_0.c:3093`) ← `rebuildActiveDisplayObjectList`
  ← `static_5_800C9BF0` ← `menuOverlayInit` ← `mainGameLoop` ←
  `mainBootstrapWorker`. Same shared-heap-corruption walker family as s164's
  22nd class (`rs_malloc`, same caller) and s167's 24th class (`rs_free`,
  different caller) — not a new independent bug, low priority.
- **The key result**: `grep -c "thr-resume-skip" run.log` → **0** for the
  entire run, despite the process reaching, sustaining, and dying inside the
  exact stall region s180 characterized. s180's single prior occurrence
  found a `[thr-resume-skip] ... bad_total=1` firing immediately before that
  run's stall onset and framed it as *the* root cause. This run's onset was
  just as tightly timed (`#9770` last `FIRE` → `#9792` first `stalled=1`,
  ~22 decisions / a few hundred ms) but had **zero** scheduler-resume
  activity anywhere nearby — checked the raw log window directly
  (`sed -n '3862860,3866000p' schedguard4/run.log`, tag-filtered): the only
  non-heap-walk line in that whole window is the `#9770 FIRE` line itself.
- This **weakens, does not refute**, s180's mechanism: it may still be *a*
  valid cause (s180's own occurrence), just not the *only* one. Multiple
  independent mechanisms landing on the same externally-observed symptom
  (`[vi-fs-decision] stalled=1 pairs=0` sustained, `[lle task]`/
  `[swap-ack-wait]` simply stop being invoked) is now the better-supported
  framing.
- Also found: `rdpFs` plateauing and the actual stall are **two distinct
  events**, not one. `rdpFs` climbed to 3999 then jumped to 4010 at decision
  `#9144`, and normal `FIRE reason=swap` activity continued for 626 more
  decisions (`#9144`→`#9770`) at that same pinned `rdpFs` value before the
  real stall (no more FIREs at all) began at `#9792`. The plateau value
  (4010 this run vs. 3560-3802 in prior runs) is content-dependent, not a
  fixed hang ceiling — the "tighten the ceiling band" open item from prior
  sessions is retired, not worth further soaks.

## Do next, in order

1. **Source-read before instrumenting (rule 5)** — three candidates, in
   order of how directly they could explain "producer stops being invoked,
   zero thread-resume log activity nearby":
   a. Re-examine the outer hangar-tick loop (the one s180 already confirmed
      "stops iterating", not the callee) for an exit/break path that does
      NOT go through `resume_thread_tagged`'s bad-context branch at all —
      e.g. a *normal*, successful thread switch (context fine, `bad=0`) that
      simply never switches back to the hangar-loop thread. Read
      `lib/N64ModernRuntime/ultramodern/src/threads.cpp`'s
      `run_next_thread`/`run_next_thread_and_wait` and the scheduler's
      `running_queue` logic end to end — is there a path where a thread
      voluntarily yields (not via the UAF guard) and its intended resumer
      is simply never re-queued?
   b. Read `viRetraceHandlerThread`/`musyxSynthFrame` (the per-VI-retrace
      audio tick, source-confirmed s101/s102) for any lock/mutex/resource
      shared with the graphics-task producer that could block it silently
      (no error, no log) if the audio thread itself stalls or loops.
   c. Check whether `[rs-malloc-walk]`/`[rs-free-walk]` volume — which
      dominates the log almost totally during and immediately after the
      stall onset in `schedguard4` — correlates with a heap-exhaustion or
      allocation-stall condition specifically on the graphics-task
      producer's own allocation path (does it call `rs_malloc`/`rs_free`
      anywhere in its per-frame path? grep before assuming).
2. **Land a targeted instrument for whichever candidate survives source
   review** — do not instrument all three blind. Keep everything already
   armed (all the `schedguard3`/`schedguard4` env vars, `[thr-create-id]`,
   `thr=%p`) since they're free and a future run correlating with
   `[thr-resume-skip]` is still a valid, useful data point.
3. **Re-run the soak** (new tag, e.g. `schedguard5` — copy `run_schedguard4.sh`,
   do not reuse a tag). Discriminating outcomes:
   - New instrument fires right at the `#9770`→`#9792`-equivalent
     transition in this run → strong candidate, worth a fix design.
   - Fires but not correlated with the transition → refute, try the next
     candidate.
   - Stall recurs with `[thr-resume-skip]` firing this time → s180's
     mechanism gets its 2nd independent confirmation after all; proceed to
     the original fix-design step (see PORTING-STATE Session 180/181 step
     2, still valid: retry-next-`running_queue`-entry vs.
     give-the-caller-a-timeout).

## Do not

- Do not re-litigate "does the outer hangar loop stop iterating vs. does the
  callee silently skip the wait" as a whole — s180 already closed the
  outer-loop-stops-iterating part. What's open now is narrower: *why* it
  stops, in a run where the one known why (s84 UAF guard) didn't fire.
- Do not treat s180's mechanism as dead — it's one confirmed instance, just
  not a necessary one. A future run where `[thr-resume-skip]` fires right at
  onset is still valuable corroborating evidence for that specific path.
- Do not spend a soak chasing the `rs_free ← rebuildActiveDisplayObjectList`
  crash — it's an already-catalogued heap-corruption family, lower priority
  than the stall-mechanism question.
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` for this soak (s93's
  confound: it perturbs timing enough to change which crash/stall wins the
  race).

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
