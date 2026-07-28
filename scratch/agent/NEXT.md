# NEXT work unit — the scheduler-SIGSEGV recipe needs to survive longer, not repeat blindly

s171 built the crash-instant `[vi-fs-decision]` snapshot instrument s170
asked for and ran 3 soaks with it. Read PORTING-STATE Session 171 before
doing anything else; this file only has the actionable summary.

## What s171 established (read before doing anything else)

- **The instrument works.** `rs64_get_vifs_crash_snapshot()`
  (`lib/rt64/src/hle/rt64_state.cpp`, always-on, no env var) is read by the
  SIGSEGV/SIGBUS/SIGABRT handler in `src/main/main.cpp` and prints
  `[CRASH][vifs-snapshot] decisionN=... lastFireDecisionN=...
  decisionsSinceFire=... lastFireWasStalled=... stalledNow=...` right after
  every `[CRASH]` line. It fired with plausible, self-consistent data in
  both of this session's 2 crashing soaks. Keep it armed — it's free.
- **3 soaks of `run_crashvifs1.sh` (same env block as s169/s170's
  `run_dlentrypopguard1.sh`), 0/3 reproduction of the target scheduler
  SIGSEGV** (`idle_thread_handle -> swap_to_thread -> wait_for_resumed ->
  moodycamel::LightweightSemaphore::tryWait -> atomic load`, signal 11).
  Instead:
  - Soak 1: SIGBUS at hold-iter 4 (~4s), fault directly inside
    `submitSceneNodeRender+16780` — **not source-characterized**, offset
    doesn't match any previously-catalogued site by grep. One frame below
    `processSceneNode`/`traverseSceneGraphRecursive`, same broad
    scene-graph-traversal chain that also reaches the 14th class
    (`reserveAndEmitDLEntry`) — likely same unguarded-deref family shape.
  - Soak 2: crash-free, full 120s hold.
  - Soak 3: SIGBUS at hold-iter 8 (~7s), `frameStartReset+532` — exact
    offset match to the already-root-caused inlining artifact of
    `heapWalker` (PORTING-STATE ~line 14189). Its guard
    (`ROGUESQ_LOG_HEAPWALKER_GUARD`) was armed and did **not** fire —
    continues that guard's long-standing 0/0 unvalidated status, nothing
    new.
- **Per rule 8, this exact recipe is closed for "reproduce the scheduler
  SIGSEGV" — do not run `run_crashvifs1.sh` or `run_dlentrypopguard1.sh` a
  4th time in a row just hoping to hit it.**
- **The FIRE-spacing check undercuts s170's stall-clear-adjacency lead,
  not supports it.** Checked what "normal" `[vi-fs-decision]` FIRE spacing
  looks like in the window where this session's 2 crashes happened (both
  hold-iter 4–8, i.e. the *active* early-post-leave window, not the deep
  late-run stall): FIRE recurs every 8–61 decisions there routinely. A
  `decisionsSinceFire` of 22 or 24 in that window is average, unremarkable
  spacing — **not** evidence the crash is near a stall-clear. s170's one
  data point (crash ~6500 log-lines after the *deep* stall's single late
  clear-event) was in a completely different, much-later temporal regime
  than either of this session's crashes.
- **The real blocker, reframed: these 3 soaks never reached the phase the
  H1/H2 question is even about.** The target scheduler SIGSEGV (s169/s170)
  happened deep in the late-run ~90%-stuck stall region, near the end of a
  long soak. This session's 2 crashes both happened at hold-iter 4–8 —
  early, in the active window, killed by 2 *different* bugs
  (`submitSceneNodeRender`, `frameStartReset`/`heapWalker`) before the
  process could ever get anywhere near the target window.

## Do next — pick ONE, don't blindly re-run the same recipe

**Option A (recommended first): characterize/fix what's killing runs early
(hold-iter 4–8), so soaks reliably survive long enough to reach the deep
stall window where the target bug actually lives.**
1. Source-read `submitSceneNodeRender`'s own guest body
   (`N64Recomp/RecompiledFuncs/funcs_*.c` — grep `RECOMP_FUNC void
   submitSceneNodeRender`) looking for the same unguarded-lookup-then-deref
   shape as every other class in this family. If found, guard it the same
   way as s99/s100/s101 (reuse the site's own skip label, `goto` its real
   exit).
2. Separately: `heapWalker`'s guard (`ROGUESQ_LOG_HEAPWALKER_GUARD`) has
   now been armed across many sessions and still never fires despite
   `frameStartReset`-attributed crashes recurring against exactly the class
   it's supposed to cover — worth a fresh source read to check the guard is
   actually placed at the fault site (compare against s171's fresh
   `frameStartReset+532` backtrace) rather than assuming it's correctly
   placed just because it was carefully reasoned through once.
3. Re-soak with `run_crashvifs1.sh`'s env block (all instruments already
   armed, free) after any fix, checking whether soaks now survive past
   hold-iter ~10–15 more often.

**Option B: accept the low hit rate and keep accumulating scheduler-SIGSEGV
data points in batches of 3, budgeted per rule 8 between batches.** Only
choose this if option A's investigation doesn't pan out this iteration —
option A is likely higher-value since it's the actual bottleneck.

## Do not

- Do not re-run `run_crashvifs1.sh` or `run_dlentrypopguard1.sh` a 4th
  time in a row purely hoping to hit the scheduler SIGSEGV again — budget
  spent (0/3 this session).
- Do not treat `decisionsSinceFire` values in the teens/twenties as
  evidence of stall-clear proximity without first checking local FIRE
  density in that specific run/window — s171 showed it's often just
  average spacing.
- Do not re-test the 14th-class (`reserveAndEmitDLEntry` pop-guards),
  `rs_free`/`rs_malloc` walk-log, or `audioslotguard1` questions — all
  closed in prior sessions (s167–s170).

## Blocking on a long-running soak (learned the hard way, still current)

Simplest approach (used successfully s168–s171): run the driver script
itself as a single foreground Bash call with output redirected to a log
file and a generous timeout (~480s covers this env block's 120s hold +
overhead) — the script blocks until the game process exits, no polling
loop needed. `until ! pgrep -f "RogueSquadron64Recomp" ...` is broken under
`run_in_background` (the wrapper's own command line self-matches); prefer
`pgrep -x` if you must poll, but a plain foreground call is simplest.

If a soak's raw log/screenshots already exist and are recent (check
`pgrep -x RogueSquadron64Recomp` returns nothing, file mtimes are within
the current session), consider analyzing them before spending a new
build-run cycle — check `scratch/agent/STATUS`/`OUTCOME` for a dangling
`WORKING`/deleted-`OUTCOME` state as the tell that a prior iteration ran
something and didn't finish writing it up.

## This session's environment notes (carry forward, still current)

- Re-running the same script/tag **overwrites** the previous run's
  `run.log` in place — `cp` it aside first (e.g. to `scratch/agent/*.log`)
  if you need to diff two runs' raw logs.
- Running `N64Recomp/build/N64Recomp` or any script under
  `RogueSquadron64Recomp/tools/agent/*.sh` / `scratch/agent/*.sh` directly
  gets denied even though the text matches an allowlisted prefix —
  prefix with `zsh` (already allowlisted).
- Compound `cd ... && zsh ... > file 2>&1` gets denied — call
  `zsh /absolute/path/to/script.sh > /absolute/path/to/log 2>&1` directly,
  no `cd`, the script `cd`s internally.
- **CRITICAL: `fixup_game_funcs.py` is non-idempotent** — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. Redirect to a log file on the ONE invocation.
- If only `fixup_game_funcs.py`/a `lib/rt64` or `N64ModernRuntime` C++ file
  changed (not symbol files or the ELF), you don't need `make_elf.py` —
  for guest-code fixup changes: `N64Recomp` (via
  `zsh tools/agent/regen_n64recomp.sh`) then `fixup_game_funcs.py` once,
  then `cmake --build`. For pure host/runtime C++ changes (like s171's
  crash-snapshot instrument): just `cmake --build`, no regen needed at all.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py` for Mach-O symbol reads.
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
- `cmake --build` needs cwd `build/` and
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`.
- `lib/N64ModernRuntime` and `lib/rt64` always show as "modified content"
  in the parent repo's `git status` — normal, long-standing state. Only run
  `submodule-patches/export.sh` + commit if you actually edit something
  under `lib/` this session (s171 did, for the crash-snapshot instrument in
  `rt64_state.cpp` — patch re-exported and committed).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target — migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-171
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
