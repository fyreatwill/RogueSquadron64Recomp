# NEXT work unit — reach the stall with the new [thr-create-id]/thr=%p
# instrument armed, then identify the actually-dropped thread by pointer

Read PORTING-STATE Session 181 in full before doing anything else (`grep -n
"^## Session 181" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-33` next-steps item (and `-32`
right below it, which still has the original s180 mechanism writeup).

## What s181 established (read before doing anything else)

- **Refuted s180's implicit premise that guest thread "id 0" names one
  specific thread.** Grepped every `osCreateThread_recomp(` call site in
  `N64Recomp/RecompiledFuncs/*.c` (10 real sites) and read each one's
  argument setup: **8 of 10 pass a literal `id=0`**. A same-run dump proved
  **≥9 distinct threads share id=0** in a normal boot: `idle_thread_handle`
  (entry `0x800017A0`, pri 10), `thread3_video_handle` (entry `0x80001088`,
  pri 9), an unnamed child of it (entry `0x800016AC`, pri 127), 3 threads
  from one boot function (entries `0x80019868`/`0x80019BF4`/`0x8001C328`,
  pri 117/122/122), one more standalone one (entry `0x80002E10`, pri 118),
  and — via an exact `thr_rdram` address match to s70/71's already-known
  crash site — **the audio thread `runAiAudioStreamPlaybackLoop`**
  (`thr_rdram=0x801494B0`). Ids 1+ ARE unique (id=1 matched s93's
  `piDmaWorker`, id=3 matched s93's `mainBootstrapWorker` exactly, both by
  entry address). **A fix or instrument keyed on `id==0` alone is a guess
  among ≥9 candidates — do not design one that way.**
- **Landed and validated (18/18 positive control) the fix for this**: an
  always-on `[thr-create-id] id=%d thr=%p pri=%d entry=0x%08X
  thr_rdram=0x%08X` log at thread-creation time (`osCreateThread`,
  `lib/N64ModernRuntime/ultramodern/src/threads.cpp`, right after
  `t->context = context;`), plus `thr=%p pri=%d` added to the existing
  cheap `[thr-resume-skip]` line (`resume_thread_tagged`, same file). Both
  changes are pure `lib/` host C++, already rebuilt clean, patch exported
  and committed. **These are always-on regardless of
  `ROGUESQ_LOG_THREAD_RESUME`** (which must stay 0 per s93's confound
  finding — do not turn it on for this soak).
- **One soak (`schedguard1`) did not reach the stall** — died at hold+~7s to
  a new-looking SIGBUS (`traverseSceneGraphRecursive` →
  `processSceneNode` → `submitSceneNodeRender`, called from the known
  `runHangarSelectionFrame` → `runHangarMenuFromOverlay` → `menuOverlayInit`
  → `mainGameLoop` chain). Not chased — out of scope, flagged only. Because
  the run never fired `[thr-resume-skip]`, it adds **zero** new data toward
  s180's still-open "2nd independent confirmation" requirement (rule 4).

## Do next, in order

1. **Re-run the `schedcaller`-shape soak** (copy `run_schedguard1.sh` to a
   new tag, e.g. `schedguard2` — do not reuse a tag, it overwrites
   `run.log`). This is a fresh attempt at a NEW question (which thread is
   actually dropped), not a blind repeat of the old repro — rule 8's
   3-attempt cap on the *old* instrument set doesn't apply here, but do
   apply ordinary judgment: if 3 consecutive attempts with this instrument
   set also fail to reach the stall, park and reconsider (e.g. a
   longer/different STICK_SCHEDULE, or accept the `submitSceneNodeRender`
   family as a competing, now more-frequent blocker worth its own
   characterization pass).
2. **If a run reaches the stall and fires `[thr-resume-skip]`**: grep the
   line's `thr=0x...` value, then grep this run's own `[thr-create-id]`
   lines for the matching `thr=` value. That gives you the dropped thread's
   `id`/`pri`/`entry`/`thr_rdram` — cross-reference `entry` against the list
   in "What s181 established" above (and against s93's `piDmaWorker`
   `0x80005570` / `mainBootstrapWorker` `0x80000C68` if the id turns out to
   be 1 or 3) to name the thread's role. This is the actual answer to "is it
   the swap-ack producer" that s180/s181 couldn't give.
3. **Once the dropped thread's role is known, decide the fix shape** (this
   was s180/NEXT.md's original step 2, still valid, still not yet done):
   - Make `resume_thread_tagged`'s bad-context branch retry the next
     `running_queue` entry instead of just returning.
   - Give `run_next_thread_and_wait`'s caller (the message-queue blocking
     path in `mesgqueue.cpp:105/143`) a way to detect its target thread
     will never run and recover (timeout, requeue-and-retry).
   Either is a real change to shared scheduler code — treat with the same
   care as every prior fix in this project (truncate register-value
   comparisons through `U32()`, keep any guest-code-adjacent path
   ABI-correct via `goto` to the real exit label, validate with a same-run
   positive AND negative control before trusting it, per the s99-s101
   lessons already in CURRENT-TRUTH).
4. **Land the fix, rebuild, export+commit if `lib/` touched, soak it.**
   Discriminating outcomes:
   - Fix prevents the stall entirely (thread 3 / the hangar loop keeps
     advancing past where `[thr-resume-skip]` used to fire) → strong
     support, but still needs a repeat before calling this
     milestone-closing.
   - Stall still occurs but `[thr-resume-skip]`/`bad_total` no longer
     precedes it → refutes the mechanism as *sufficient*.
   - Stall recurs with the same signature unfixed → confirms the mechanism
     but the fix attempt didn't address it — iterate on the fix.

## Do not

- Do not design or land a fix keyed on `id==0` alone — s181 proved that's
  ambiguous among ≥9 threads. Use the `thr=%p` cross-reference (step 2
  above) first.
- Do not re-open the `submitSceneNodeRender+28208` SIGBUS from s181's soak
  as a primary investigation thread this iteration — it's flagged, not
  characterized; chasing it is a valid *future* work unit if it recurs and
  keeps preempting this repro, but the current top priority is the
  scheduler-stall mechanism per the goal stack (M3).
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` for this soak (s93's
  confound: it perturbs timing enough to change which crash/stall wins the
  race). The new instruments are always-on and don't need it.
- Do not re-litigate "does the outer hangar loop stop iterating vs. does the
  callee silently skip the wait" — s180 closed this (outer loop stops).

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
  host C++ changes like s181's — those only need `cmake --build`.)
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
  operations" even though they're one shell pipeline). Also: `sed -n
  'N,Mp' file` per-file works fine for reading small windows around known
  line numbers; a shell loop with `for loc in "file:line" ...; do ...;
  done` gets denied ("Contains simple_expansion") — issue one `sed` call
  per location instead, batched in parallel tool calls.
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

`docs/CURRENT-TRUTH.md` is now ~250 KB, wildly over the ~35 KB target —
migrate durable mechanism/architecture material to PROJECT-OVERVIEW.md and
prune superseded detail, paired with a real experiment (do not spend a
whole iteration on pure doc cleanup per ITERATION.md — "compressing
CURRENT-TRUTH is not advancing" — but if a natural break comes up, this is
overdue). Flagged for many sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across many sessions
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
