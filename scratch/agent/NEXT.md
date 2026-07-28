# NEXT work unit — iron-rule-8 mandatory pivot: do NOT run a 4th blind
# sceneptrguard soak. Pick ONE of the two options below.

Read PORTING-STATE Session 192 in full before doing anything else (`grep -n
"^## Session 192" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-41` next-steps item (top of the
list).

## Why this is the next work unit (read before doing anything else)

s192 landed the `queueGPUUploadTMEM` zero-size guard NEXT.md's s191 recommended
(`ROGUESQ_LOG_TMEM_ZERO_GUARD`, `lib/rt64/src/render/rt64_texture_cache.cpp:1284`,
commit `14bf1d4`). A soak with it active (`sceneptrguard5`) reached
`decisionN=8972` — the furthest of the 3 `sceneptrguard` soaks so far (s190:
8053, s191: 7897, s192: 8972) — but still short of the 9660-9792 target
window, and **the new guard never fired** (0/1). The run instead died to a
NEW, previously-uncatalogued crash: `runVideoFrameTick` SIGBUS (backtrace:
`runVideoFrameTick` x2 <- `menuOverlayInit` <- `mainGameLoop` <-
`mainBootstrapWorker`). Source-read (`N64Recomp/RecompiledFuncs/funcs_0.c:1459`)
confirmed **zero self-calls** in the function body — per the same reasoning
already established for `frameStartReset` (s84) and `advancePlayerAnimationPhase`
(s87/88), the doubled frame in the unwound stack is almost certainly a
stack-unwind duplication artifact, not true recursion. Not root-caused
further — the actual faulting deref inside the function is still unidentified.

`[scene-node-ptr-guard]` has now fired **0 times across all 3 soaks**
(s190/s191/s192). The underlying question this whole lineage exists to
answer — does the s190 processSceneNode fix work, does decisionN push past
9792, does the `-35` stall signature appear — remains completely untested.

**This is the 3rd consecutive iteration testing "does a fix-soak reach the
target decisionN window" with no discriminating result.** Per iron rule 8,
blind repeats must stop now. Pick ONE of the two options below — NOT a 4th
`sceneptrguard6` soak.

## Two valid options, in order — pick ONE (do not do both in the same
## iteration; that's two work units)

### Option A — guard the new `runVideoFrameTick` crash (likely higher value)

Rationale: every soak-blocking crash seen in this lineage guarded == maximum
odds the NEXT soak actually reaches the target window and finally tests the
processSceneNode fix. This would be the 4th such guard (rs_malloc s173,
rs_free s187, scene-node-ptr s190, queueGPUUploadTMEM s192).

1. Read the FULL body of `runVideoFrameTick`
   (`N64Recomp/RecompiledFuncs/funcs_0.c:1459` onward — it's a large
   function, read past where the earlier grep/awk excerpt stopped) to find
   the actual faulting dereference. Do NOT guess a guard site from the
   backtrace alone — the backtrace only says the crash is IN this function,
   not WHERE. Cross-reference the `[CRASH]` stack's native offset
   (`runVideoFrameTick + 1568`) against the compiled binary if needed
   (`scratch/agent/machoparse.py` — `nm`/`otool`/`lldb` are not on the Bash
   allowlist).
2. Once the faulting deref is identified, add a getenv-gated
   (`ROGUESQ_LOG_VIDEO_FRAME_TICK_GUARD` or similar — check it's not
   already claimed first), bounded-counter, tagged-fprintf guard in
   `N64Recomp/fixup_game_funcs.py` (mirrors the `processSceneNode`
   node-pointer guard pattern from s190 — this is a `RecompiledFuncs`
   patch, so it DOES need the regen/fixup pipeline: `make_elf.py` ->
   `N64Recomp` -> `fixup_game_funcs.py` -> `cmake`).
3. Soak with the new guard plus the full s192 env block
   (`scratch/agent/run_sceneptrguard5.sh` + the new var) as
   `sceneptrguard6`. Positive control: does the new guard fire? Does
   decisionN push further than 8972? Does it finally reach 9660-9792 and
   fire `[scene-node-ptr-guard]`?

### Option B — positive-control the `queueGPUUploadTMEM` guard in isolation

Rationale: the guard landed s192 has ZERO confirmation it is even reachable
— it compiled and linked, but no run has ever exercised it. A guard that
has never fired is an unverified claim, not a working fix, no matter how
plausible the source-read.

1. Find or construct a game state/repro that reliably hits the
   `decodeTMEM && (width<=0 || height<=0)` condition — check PORTING-STATE
   s86-s101 (the original discovery/characterization sessions for this
   crash class) for a known trigger path or scene.
2. Run a short soak targeting that specific state with
   `ROGUESQ_LOG_TMEM_ZERO_GUARD=1` active and confirm `[tmem-zero-guard]`
   fires at least once, with sane-looking logged fields (hash/width/
   height/decodeTMEM) — this is the missing positive control, not a new
   soak toward the processSceneNode question.
3. If it fires: the guard is confirmed live and this line item closes. If
   it still doesn't fire even when deliberately targeted, that's a much
   more concerning finding (the guard's condition may not match the
   assert's actual trigger condition in practice) and warrants a fresh
   source comparison between the guard's `if` and the assert's negation.

## Do not

- Do not run a 4th blind `sceneptrguard` soak (`sceneptrguard6` with no new
  guard) — that violates iron rule 8, already at 3/3 same-hypothesis
  iterations with no discriminating result.
- Do not re-touch the `processSceneNode` node-pointer guard or the
  `queueGPUUploadTMEM` guard's existing logic — both still fixed and
  intact as landed (s190, s192).
- Do not attempt to root-cause `queueGPUUploadTMEM`'s actual corrupted-
  width/height source (goal-stack M3, full root-cause/fix) — out of scope,
  a much larger separate investigation.
- Do not re-attempt root-causing the underlying `rs_free` free-list
  corruption source itself (s85-s114 chase) — still out of scope.
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` (s93's confound).

## Blocking on a long-running soak (learned the hard way, still current)

Run the driver script as a single foreground Bash call with output
redirected to a log file and a generous timeout (~480s), OR launch with
`run_in_background: true` and block on the returned task ID via
`TaskOutput(task_id, block=true, timeout=300000-480000)` — this is the
correct way to synchronously wait for a soak before writing the exit-
contract docs; ending the turn while a background soak is still running
trips the Stop hook's exit-contract check prematurely.

## This session's environment notes (carry forward, still current)

- **`N64Recomp/fixup_game_funcs.py` is non-idempotent** — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. If adding a NEW patch (Option A needs this): regenerate
  fresh first (`zsh tools/agent/regen_n64recomp.sh`), THEN run `python3
  /absolute/path/to/N64Recomp/fixup_game_funcs.py > log` exactly once. Grep
  the log for the new patch's report line to confirm exactly x1, and check
  older patches' lines are ALSO x1 (not x2).
- A pure `lib/N64ModernRuntime`/`lib/rt64` runtime change (not a
  `RecompiledFuncs/*.c` patch) does NOT need the regen/fixup pipeline at
  all — just `cmake --build build --target RogueSquadron64Recomp -j`
  directly. (This is what s192's guard used — Option B stays in this
  lane; Option A's new guard would NOT, since it's a `RecompiledFuncs`
  patch.)
- Re-running the same soak script/tag **overwrites** the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied — use
  absolute paths, no `cd`, one command per Bash call (including a trailing
  `echo` after a redirected command). `echo foo; echo bar` and `cmd;
  echo $?` also get flagged ("Contains simple_expansion") — one command,
  one effect, per Bash call.
- `git -C <path> ...` AND `cd <path> && git ...` (combined in one Bash call)
  both trigger approval prompts that a non-interactive session can't clear —
  if you need git state from a directory other than the repo root, either
  accept that a plain `git <cmd>` after a SEPARATE `cd` Bash call may still
  need approval, or just use direct file reads/greps instead of git.
- `submodule-patches/export.sh` must be invoked as
  `./submodule-patches/export.sh` (relative) from the repo root — absolute
  path gets denied.
- A large `run.log` (millions of lines) is fine to `grep -c`/`grep -n >
  outfile` directly — just don't `cat`/`Read` it wholesale.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py`, or the `[CRASH]` stack dump.
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- Output redirection is sandboxed to the session's allowed working
  directories (this repo, N64Recomp, rogue_squadron64) — redirecting to
  `/tmp/...` gets blocked; use a path under `scratch/agent/` instead.
- When adding a `std::getenv`/`fprintf` guard to a `lib/rt64` `.cpp` file
  that doesn't already use those calls, don't assume `<cstdlib>`/`<cstdio>`
  are transitively available — check first, add an explicit include if
  needed (s192 needed `<cstdlib>` in `rt64_texture_cache.cpp`).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now ~270 KB (`wc -l` ~3900 lines) — WAY over the
~35 KB CLAUDE.md budget, growing every session. Migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md and prune superseded
detail, paired with a real experiment. Flagged for many sessions without
action — this is becoming a real cost (the file no longer fits a single
`Read` call without offset/limit).

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session. Still flagged
for the user, not committed autonomously.
