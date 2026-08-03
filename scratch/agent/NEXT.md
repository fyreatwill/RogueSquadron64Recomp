# NEXT work unit — re-soak once more with the build as-is (`BREADCRUMB5` armed on
# `reserveAndEmitDLEntry`, no code changes first) to give it a 2nd pair of
# attempts; if it still doesn't recur, decide between chasing the new
# `inflate_fast` site or landing `BREADCRUMB6` on `emitAllocatedDLCommand` per
# the priority guidance below.

## Where the investigation stands (s272)

s272 landed `BREADCRUMB5` scoped to `reserveAndEmitDLEntry` per s271's plan (same
`g_rs64_last_guest_pc`-global mechanism as BREADCRUMB-BREADCRUMB4, no `main.cpp`
change). Regen was clean (single fixup pass confirmed after catching and fixing a
double-run-without-regen slip before building — see PORTING-STATE Session 272 for
the process note). Build clean, 0 errors.

**Both soaks this session missed `reserveAndEmitDLEntry`'s own target (0/2)**:
- Soak 1 died pre-scene to the already-catalogued 23rd crash class
  (`waitForAnyAudioSlot`, known boot-time variance, unusable data point).
- Soak 2 reached the scene fine, then crashed inside `inflate_fast` (zlib, a
  system library, NOT one of our recompiled functions) — `si_addr=0x380000003`
  (guest `0x80000003`, 3 bytes off the family's usual exact-`0x80000000`
  signature). `last-guest-pc=0x8000b650` was confirmed (by grepping
  `funcs_3.c`) to belong to `beginFrameDLChunk`, not `reserveAndEmitDLEntry` —
  uninformative for this session's target, likely just stale.

This is a genuinely new, not-yet-catalogued, not-yet-localized crash site. It's
NOT confirmed same-family as the 5 already-fixed cached-free-list-head sites —
it manifests inside a system library call, not a recompiled guest function, so
the usual "grep the guest PC, find the idiom" localization approach doesn't
directly apply to it.

## The next work unit

1. **Re-soak with the build exactly as-is** (no code changes):
   `env HOLD_S=240 zsh scratch/s73_post_a_scene/run_dequeuearg1.sh s273_soak1`
   (launch `run_in_background: true` from an absolute path, then immediately
   `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME turn). Budget
   2 attempts before deciding what to do with the result (iron rule 8) — this
   will be `BREADCRUMB5`'s 2nd session of attempts (0/2 so far), analogous to
   `BREADCRUMB4`'s slow start (0/2 at s270, eventually useful the following
   session) — not yet at the 3-strikes limit.

2. **If `reserveAndEmitDLEntry` crashes and `last-guest-pc` is now informative**
   (grep the reported guest PC in `funcs_3.c` — the function starts at line
   ~15736 pre-patch, offset will differ post-patch; confirm which function the
   hex label belongs to the same way s272 did for `beginFrameDLChunk`, by
   locating the nearest preceding `RECOMP_FUNC` line): read ~20 surrounding
   lines. If it matches the cached-free-list-head idiom shape (`lui $vX,0x8011`
   / `lw $vX,0x63B0($vX)` / deref or +4-store with zero validation), add
   `CACHE5_GUARD` — same shape as `CACHE4_GUARD` if deref-side, `CACHE2_GUARD`/
   `CACHE3_GUARD` if write-side (`sw $zero, 0x4($v0)`) — full regen (delete
   `funcs_*.c` first, single fixup pass, verify multiplicities in the saved log
   before building), soak-verify (>=2 independent clean runs, iron rule 4), and
   add the guard's `ROGUESQ_LOG_*` flag to `run_dequeuearg1.sh` in the SAME
   session.

3. **If `inflate_fast` (or the same `si_addr=0x380000003` family) recurs
   instead**: this is now 2/2 combined observations of a genuinely new site.
   Consider it the next priority over `emitAllocatedDLCommand` (which is still
   only a single observation with a different, non-`0x80000000` fault shape).
   Since the crash is inside a system library, localizing the guest-side origin
   needs a different approach than the usual idiom-grep: either (a) breadcrumb
   whichever guest function(s) call into decompression (grep for calls to the
   zlib wrapper / inflate entry points in the recompiled sources), or (b) accept
   `last-guest-pc` as an approximate signal if the calling function turns out to
   already be breadcrumbed and the timing is tight (crash immediately follows
   the breadcrumb update with no intervening breadcrumbed-function calls).

4. **If `emitAllocatedDLCommand` recurs**: still just 1 prior observation
   (s271), different fault shape (`si_addr` = garbage offset, not exactly
   `0x80000000`) — don't assume same idiom family. Land a breadcrumb on it
   first if it recurs, to get an informative `last-guest-pc` before guessing.

5. **If `processSceneNode+1184` (`BREADCRUMB4`'s target) recurs**: localize via
   `last-guest-pc` (informative since `processSceneNode` is breadcrumbed) the
   same way s271 localized `beginFrameDLChunk` — grep the guest PC in
   `funcs_4.c`, add ONE targeted guard matching whatever idiom is found, regen,
   soak-verify.

6. **If a completely different crash lands** (has happened most sessions):
   note it, symrange-verify if the offset looks plausible, don't chase it this
   iteration unless clearly the highest-information-value next step (iron rule
   8's budget discipline).

## Do NOT do this iteration

- Do NOT run `fixup_game_funcs.py` twice in a row without deleting and
  regenerating `funcs_*.c` in between — this SILENTLY DUPLICATES every patch.
  Always: delete `funcs_*.c` -> `make_elf.py` -> `N64Recomp` ->
  `fixup_game_funcs.py` ONCE, saving output to a log file -> grep the SAVED LOG
  (never re-run the script) to check multiplicities -> build. (s272 nearly
  made this exact mistake by re-running the script to re-inspect its output —
  caught before building, no functional impact, but don't repeat it.)
- Do NOT spend another soak attempt on `heapFreeListDequeue`'s own
  BREADCRUMB2-targeted crash — it's 0/6 across 2 sessions, parked per rule 8.
- Do NOT re-touch `DEQUEUE_GUARD`'s range-check bound — the a0-argument
  hypothesis is refuted (s267) with a same-run positive control.
- Do NOT conflate the `0x80000000`-exact-fault family (or its `+0x30` variant
  at `processSceneNode`, or `emitAllocatedDLCommand`'s garbage-offset variant,
  or `inflate_fast`'s `+3`-offset variant) with item -49's KSEG0-zero-extension
  bug (`0x80630062`) — different exact values, different sites, confirmed
  distinct multiple sessions running. Also don't assume `inflate_fast`'s crash
  IS the same idiom family just because `si_addr` is nearby — it's a
  library-call-site crash, structurally different from the 5 already-confirmed
  guest-code-deref sites, until proven otherwise.
- Do NOT cite `x0`/`x8`/`x9`/`x10`/`x11` = `0x0000000300000000` as
  crash-matching evidence for ANYTHING — constant RDRAM base pointer (s219,
  item -60).
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `CACHE2_GUARD`/`CACHE3_GUARD`/`CACHE4_GUARD`/`MATLIST_GUARD1-3`/
  `COMPOSE_NPC_GUARD1-9`/`DEQUEUE_GUARD` — all verified not regressing and not
  the current blocker.
- Do NOT idle across a Stop-hook turn boundary waiting on a background soak —
  block with `TaskOutput(task_id, block=true, timeout<=480000)` in the SAME
  turn.

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64` (run as
  `python3 tools/make_elf.py`), `N64Recomp` needs cwd `N64Recomp`
  (`./build/N64Recomp rogue_squadron.toml`), `fixup_game_funcs.py` needs cwd
  `N64Recomp`. Always delete `funcs_*.c` and regen from scratch before running
  `fixup_game_funcs.py` — see the duplication warning above.
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Background launches do NOT inherit a prior foreground `cd` — always launch
  soak drivers by full absolute path when using `run_in_background: true`.
  Likewise, foreground `Bash` calls that use relative paths can transiently
  fail right after a background soak launch writes new files — prefer absolute
  paths for any file check immediately after a soak completes.
- Cross-turn waiting does not work under the Stop hook — use
  `TaskOutput(task_id, block=true, timeout<=480000)` synchronously in the same
  turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`. Current-best baseline: `run_dequeuearg1.sh` (`HOLD_S`
  overridable via env, defaults to 240 if unset). It exports
  `ROGUESQ_LOG_SCENE_NODE_CACHE_GUARD` through `CACHE4_GUARD` — when landing a
  new guard, add its log flag to this script in the SAME session, or a future
  session will get an uninformative "0 fires" verification run.
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets and SHIFT across
  sessions as guards/breadcrumbs are added. Don't assume a changed native
  offset means a different bug — check `si_addr`/guest PC first. Verify range
  membership by reading `build/RogueSquadron64Recomp`'s Mach-O symtab directly
  — see `scratch/agent/s268_symrange2.py`. Note: this symrange approach only
  applies to OUR recompiled-function symbols — system-library crashes (like
  s272's `inflate_fast`) resolve via the OS's own dyld symbol table and don't
  need/support the same check.
- A crash's `[CRASH][last-guest-pc]` value is only informative if the crashing
  function (or, per s272, the ACTUAL guest call chain leading to the crash) is
  ITSELF breadcrumbed — otherwise it just shows wherever the process last
  passed through one of the OTHER currently-instrumented functions. Always
  grep the reported guest PC's hex label in the relevant `funcs_N.c` and find
  its enclosing `RECOMP_FUNC` before trusting it (s272 confirmed
  `0x8000b650` belonged to `beginFrameDLChunk`, not `reserveAndEmitDLEntry`,
  by exactly this method).
- When adding a guard to a function that's ALSO covered by an existing
  breadcrumb's blanket per-instruction pass: check whether your guard patch's
  code block sits before or after the breadcrumb patch's block in
  `fixup_game_funcs.py`'s file order. A guard block positioned BEFORE its
  function's breadcrumb block sees PRE-breadcrumb text and must not require
  `g_rs64_last_guest_pc` lines in its match regex (s271, `CACHE4_GUARD`).
- Redirecting shell output (`>`) only works to paths under one of the 3 session
  working directories (`RogueSquadron64Recomp`, `N64Recomp`, `rogue_squadron64`)
  — `/tmp` is blocked. Use `scratch/agent/*.log`.
- `N64Recomp/fixup_game_funcs.py` is untracked by git in the standalone
  `N64Recomp` checkout — expected, not a bug. Its changes persist only via the
  live file on disk across sessions. Same is true of `scratch/` in general
  EXCEPT `scratch/agent/NEXT.md`, `STATUS`, and `OUTCOME`, which are
  individually force-tracked.
- `git status --short` run from inside `RogueSquadron64Recomp/build` (or any
  subdir) works without needing `-C`/`cd` combined-command approval prompts;
  `git -C <path>` and `cd <dir> && git ...` both require interactive approval
  and may not resolve non-interactively.
- `CURRENT-TRUTH.md` is far over the ~35KB target in CLAUDE.md (now ~7000+
  lines / several hundred KB — exceeds the Read tool's 256KB limit in one
  shot, requiring offset/limit reads or targeted grep). A dedicated pruning
  session is now 14+ consecutive sessions overdue — still not this iteration's
  job unless the localization work above is a quick null with clear leftover
  budget.
