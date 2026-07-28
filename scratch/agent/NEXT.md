# NEXT work unit — guard the rs_malloc free-list walk's computed-pointer deref

s172 fixed a real gap in heapWalker's guard (missing 5th site + all 5
walk-loops totally unguarded — see PORTING-STATE Session 172), but 2 soaks
with the fix armed show heapWalker's own bug isn't what's killing these
particular runs (0/0 on both new guards both soaks). Each soak instead hit
a *different*, newer crash. Read PORTING-STATE Session 172 before doing
anything else; this file only has the actionable summary.

## What s172 established (read before doing anything else)

- **heapWalker's guard gap is real and fixed** (`N64Recomp/fixup_game_funcs.py`,
  `N64Recomp/RecompiledFuncs/funcs_3.c`, rebuilt clean, not yet proven to
  matter). s157 only ever guarded 4 of 5 identical head-deref sites, and
  none of the 5 walk-loops that follow — a head-only guard only protects
  lists of length 0-1. Fixed both gaps. **This is NOT committed anywhere**
  (`N64Recomp` is its own sibling checkout, same long-standing uncommitted
  posture as always — not this session's call to resolve).
- **2 soaks (`run_heapwalkerguard3_1.sh`/`_2.sh`, same env block as
  s169-s171's `run_crashvifs1.sh` plus `ROGUESQ_LOG_HEAPWALKER_GUARD3=1`)**:
  - Soak 1: survived to **hold-iter 27** (~30s), longest crashing soak of
    this whole family to date. `HEAPWALKER_GUARD`/`GUARD3`: 0/0 both. New
    crash: SIGBUS in `processSceneNode` (self-recursive) via
    `traverseSceneGraphRecursive`/`setupCameraMatrices`. Not source-read yet
    (~1100 lines, `N64Recomp/RecompiledFuncs/funcs_4.c:13759-14861`).
  - Soak 2: died at **hold-iter 1** (~0s). `HEAPWALKER_GUARD`/`GUARD3`: 0/0
    again. New crash: SIGBUS **directly inside `rs_malloc`**
    (`rs_malloc + 2020`), from `rebuildActiveDisplayObjectList` <-
    `static_5_800AAD9C` (the per-frame tick) <- `static_5_800C6854` <-
    `menuOverlayInit`. **Strong mechanistic evidence, not just a
    backtrace**: the log line right before the crash
    (`ROGUESQ_LOG_RS_MALLOC_WALK`, s165, log-only, never guarded) shows
    `node=0x801B0190 flags=0x0 size=2955542528` — garbage ~2.75GB size.
    Source-read the walk (`N64Recomp/RecompiledFuncs/funcs_0.c` ~line
    2909-2969): reads a node's size field, computes
    `next = node + size` (line 2967, guest `0x80001BF0`), then immediately
    dereferences `next` (line 2969, guest `0x80001BF4`,
    `MEM_HU(ctx->r2, 0x10)`) with **zero bounds check**. A garbage size
    produces a wild `next`; the very next instruction dereferences it.
    Matches the observed fault offset and the family's established
    "trust a corrupted value as an address" shape exactly.
- **27x survival variance between the 2 soaks of the identical recipe**
  (hold-iter 1 vs 27) reinforces this crash family is non-deterministic in
  *which* site fires first — do not read a single soak's survival length as
  a before/after signal without a same-session comparison run.

## Do next — pick ONE

**Recommended: guard the `rs_malloc` walk's computed-pointer deref (best
evidence this session produced).**
1. Read the loop in full first
   (`N64Recomp/RecompiledFuncs/funcs_0.c` starting ~line 2908, label
   `L_80001BB0`/`L_80001BC4`) — specifically its exit/termination
   condition (this session did not trace how the loop is supposed to stop;
   guarding without knowing the correct bail target risks an incomplete
   guard, as s99's first attempt was before its `U32()` fix).
2. Add a bounds check on the computed `next` pointer (`ctx->r2` at guest
   `0x80001BF0`, right before the `MEM_HU(ctx->r2, 0X10)` deref at
   `0x80001BF4`) using the same `0x80000000u`/`0x80800000u` idiom as every
   other guard in this project. Bail to the loop's actual termination
   label, not a guess.
3. Regen: `zsh tools/agent/regen_n64recomp.sh` then
   `python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   ONCE (redirect to a log — it is NOT idempotent), verify the patch report
   shows exactly x1, then rebuild
   (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`).
4. Soak with the new guard's env var armed (add it to a copy of
   `scratch/agent/run_heapwalkerguard3_2.sh`, new tag) and check whether it
   fires (positive control) and whether survival improves.

**Alternative: source-read `processSceneNode`** (soak 1's crash,
`funcs_4.c:13759-14861`) for the same unguarded-deref shape — lower
priority, less evidence than the rs_malloc lead above, but a second
independent early-crash site worth closing eventually.

**Fallback: `submitSceneNodeRender+16780`** (s171's finding,
`funcs_4.c:6-2999`) — still open, still unguarded, still lower priority
than the two leads above (this session found 2 newer, better-evidenced
sites; per rule 8 don't chase 3 different early-crash leads in the same
session without picking the best-evidenced one first).

## Do not

- Do not re-run `run_crashvifs1.sh`/`run_dlentrypopguard1.sh` purely
  hoping to hit the s169/s170 scheduler SIGSEGV — that question is still
  blocked on soaks reliably reaching the deep-stall window, and neither of
  this session's fixes was confirmed to help yet. Keep deferring it.
- Do not assume the heapWalker walk-loop guard (`GUARD3`) is useless just
  because it was 0/0 twice — 2 soaks where the crash never touched
  heapWalker's bad-data path isn't evidence the guard is unnecessary, just
  that it wasn't tested this session. Keep it armed (it's free).
- Do not read soak 1's hold-iter-27 survival as proof any fix this session
  helped — no same-session before/after comparison was run, and soak 2's
  hold-iter-1 death on the identical recipe shows the variance is large
  regardless.

## Blocking on a long-running soak (learned the hard way, still current)

Simplest approach (used successfully s168–s172): run the driver script
itself as a single foreground Bash call with output redirected to a log
file and a generous timeout (~480s covers this env block's 120s hold +
overhead) — the script blocks until the game process exits, no polling
loop needed. `until ! pgrep -f "RogueSquadron64Recomp" ...` is broken under
`run_in_background` (the wrapper's own command line self-matches); prefer
`pgrep -x` if you must poll, but a plain foreground call is simplest.

## This session's environment notes (carry forward, still current)

- Re-running the same script/tag **overwrites** the previous run's
  `run.log` in place — `cp` it aside first (e.g. to `scratch/agent/*.log`)
  if you need to diff two runs' raw logs. Better: copy the whole driver
  script to a new tag name per soak (s172 did this: `run_heapwalkerguard3_1.sh`
  / `_2.sh`) so each soak's full run.log and screenshots land in their own
  `scratch/s73_post_a_scene/<tag>/` directory, never overwritten.
- Running `N64Recomp/build/N64Recomp` or any script under
  `RogueSquadron64Recomp/tools/agent/*.sh` / `scratch/agent/*.sh` directly
  gets denied even though the text matches an allowlisted prefix —
  prefix with `zsh` (already allowlisted).
- Compound `cd ... && zsh ... > file 2>&1` gets denied — call
  `zsh /absolute/path/to/script.sh > /absolute/path/to/log 2>&1` directly,
  no `cd`, the script `cd`s internally. Same for `cd ... && cmake ...` —
  use `cmake --build /absolute/path/to/build` instead of `cd`+relative.
- Same for `python3 fixup_game_funcs.py` — it uses an absolute
  `pathlib.Path("/Users/.../N64Recomp/RecompiledFuncs")` internally, so it
  can be invoked as `python3 /absolute/path/to/fixup_game_funcs.py > log`
  with no `cd` at all, sidestepping the compound-cd-redirect denial
  entirely (s172 confirmed this works).
- **CRITICAL: `fixup_game_funcs.py` is non-idempotent** — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. Redirect to a log file on the ONE invocation.
- If only `fixup_game_funcs.py`/a `lib/rt64` or `N64ModernRuntime` C++ file
  changed (not symbol files or the ELF), you don't need `make_elf.py` —
  for guest-code fixup changes: `N64Recomp` (via
  `zsh tools/agent/regen_n64recomp.sh`) then `fixup_game_funcs.py` once,
  then `cmake --build`. For pure host/runtime C++ changes: just
  `cmake --build`, no regen needed at all.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py` for Mach-O symbol reads (gives function
  sizes via symtab sort, NOT disassembly — it cannot map a crash's byte
  offset back to a source line; only a full source read can locate the
  actual fault site within a large function).
- Reading a `RECOMP_FUNC` body directly from
  `N64Recomp/RecompiledFuncs/funcs_*.c` (via `grep -n "RECOMP_FUNC void
  <name>"`) is far more reliable than trusting a `symbol_files/*.txt`
  comment.
- `git -C <path> ...` (with the `-C` flag) triggers an approval prompt even
  for read-only commands like `status`/`show` — plain `git <cmd>` from the
  correct cwd, or a separate `cd` call first, avoids it. Some git
  subcommands beyond plain `status`/`show`/`log` (e.g. `check-ignore`) may
  still need approval even without `-C`.
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
  under `lib/` this session (s172 did NOT touch `lib/` — all edits were in
  the separate `N64Recomp` sibling checkout's `fixup_game_funcs.py`).
- `/scratch/` is entirely gitignored in this repo except 3 force-tracked
  files: `scratch/agent/NEXT.md`, `OUTCOME`, `STATUS`. New soak
  scripts/logs under `scratch/agent/` or `scratch/s73_post_a_scene/` never
  need `git add` — they're intentionally untracked.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target — migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-172
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
