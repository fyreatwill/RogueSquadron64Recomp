# NEXT work unit — find the 2nd, still-unguarded deref in the waitForAnyAudioSlot chain

s173 landed and validated the `rs_malloc` walk-loop guard NEXT.md asked
for (0/0 across 2 soaks, real negative control — 17,683 clean calls, no
corrupted size seen), so that specific question is not further actionable
right now. Both soaks instead died to *other* crashes: one to the already-
catalogued s83 Metal-internal shader-compiler SIGSEGV (unrelated, no
source on our side, ignore it), and one to a **recurrence of the 23rd
crash class** (`waitForAnyAudioSlot` chain) **despite s166's own guard on
that exact chain being confirmed active in the build**. Read PORTING-STATE
Session 173 before doing anything else; this file only has the actionable
summary.

## What s173 established (read before doing anything else)

- **The `rs_malloc` walk-loop guard is landed, built clean, and soaked
  twice** (`N64Recomp/fixup_game_funcs.py`, new
  `ROGUESQ_LOG_RS_MALLOC_WALK_GUARD` env var, file-scoped `funcs_0.c`).
  **Not committed** — same long-standing uncommitted-history posture as
  `N64Recomp` since s54/s90, not this session's call to resolve.
- **The 23rd crash class (`waitForAnyAudioSlot` chain) is at least 2
  distinct bugs, not 1.** s166 guarded `isAudioSlotActive`'s base-pointer
  deref (`funcs_24.c`, always-on regardless of its own log env var) and
  that guard is confirmed patched into this build (`fixup.log`:
  "isAudioSlotActive base-pointer guard patched x1"). Despite that, s173
  soak 2 died with an identical-looking backtrace (SIGSEGV inside
  `waitForAnyAudioSlot` +76 native bytes <- `menuOverlayInit` <-
  `mainGameLoop` <- `mainBootstrapWorker`), **before VI width 1024/title
  screen was ever reached** (`decisionN=356`, task #278 — earliest known
  death in the whole project's crash-family history).
- **Source-read this session, no rebuild needed, ruled out 2 of 3 shallow
  candidates:**
  - `anyAudioSlotActive` itself (`funcs_23.c:8806`): every `MEM_*` access
    is off a fixed literal global address (`0x800A0F50`, `0x80141AD0`,
    `0x8014530C`) — no computed-pointer deref anywhere in its own body.
    Calls `audioStubReturnZero` (stub) and `isAudioSlotActive` (already
    guarded). **Ruled out.**
  - `tickMusyXIfActive` (`funcs_23.c:6785`, only entered if fixed-global
    byte `0x800A0F50` is nonzero — i.e. audio genuinely active): its own
    body has **zero direct `MEM_*` derefs**, only calls into 5 deeper
    functions. **Not itself the fault site, but the fault is somewhere
    inside one of its callees:**
    `factor5MutexAcquire`, `tickActiveSongs`, `tickAndReap3DAudioVoices`,
    `stopAllSynthVoices`, `factor5MutexRelease` — **none of these 5 have
    been source-read yet.**

## Do next

**Source-read the 5 unexamined callees of `tickMusyXIfActive`** for this
family's dominant unguarded-deref shape (fixed-global-table-pointer
indexed and dereferenced with no null/range check — the 12th/14th/16th/
21st/23rd(-a) classes' shared signature; or a corrupted-size free-list
walk like `rs_malloc`'s, if any of the 5 turn out to touch a heap
structure):
1. `factor5MutexAcquire`/`factor5MutexRelease` — likely thin wrappers
   around a mutex primitive, probably low-risk, but confirm before ruling
   out.
2. `tickActiveSongs`, `tickAndReap3DAudioVoices`, `stopAllSynthVoices` —
   these are the substantive per-frame audio-tick bodies and the most
   likely fault sites given they're where actual voice/song list walking
   would happen (same shape as every other guarded crash in this family).
3. Once the actual unguarded deref is found and confirmed unique (grep the
   guest address across all `funcs_*.c` before patching, per every prior
   guard's own lesson), guard it with the standard idiom (bounds-check the
   computed pointer against `0x80000000u`/`0x80800000u`, bail to the
   function's own real exit — `goto` a label or `return;` with a safe
   default, whichever is ABI-correct for that function's frame shape).
4. Regen: `zsh tools/agent/regen_n64recomp.sh` then
   `python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   ONCE (redirect to a log — it is NOT idempotent), verify the patch report
   shows exactly x1, then rebuild
   (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`).
5. Soak with the new guard's env var armed (copy
   `scratch/agent/run_rsmallocwalkguard2.sh` to a new tag, keep every prior
   env var — they're all free) and check whether it fires (positive
   control) and whether the process survives past `decisionN=356`/task
   #278 (s173's earliest-known death point).

**Why this is top priority over s172's other 2 leads** (`processSceneNode`
self-recursive SIGBUS, `submitSceneNodeRender+16780`): this crash now kills
the run *before the title screen even renders* — strictly earlier than
either of those, and earlier than every other crash in the family's
history. Fixing the earliest blocker first is the highest-information-
value move; the other two leads are still open but lower priority.

## Do not

- Do not re-run `run_rsmallocwalkguard1.sh`/`_2.sh` unmodified hoping for a
  3rd data point on the walk-loop guard specifically — it's landed, it has
  a real negative control, and per rule 8 this question is not the one to
  keep spending soaks on right now. The env blocks are still useful
  scaffolding to copy from, just don't re-run them as-is for that question.
- Do not assume `isAudioSlotActive`'s guard (s166) is broken or wrong just
  because a similar-looking crash recurred — the backtrace and source read
  both point to a *different*, deeper site, not a hole in that guard
  itself.
- Do not skip the source read and jump straight to instrumenting all 5
  candidate functions at once "to be safe" — per rule 6 (source-read
  before instrumenting), read each function's actual body first; most
  functions in this codebase turn out to have zero or one real deref
  candidate once actually read, not several.

## Blocking on a long-running soak (learned the hard way, still current)

Simplest approach (used successfully s168–s173): run the driver script
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
  script to a new tag name per soak so each soak's full run.log and
  screenshots land in their own `scratch/s73_post_a_scene/<tag>/`
  directory, never overwritten.
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
  calls.
- Same for `python3 fixup_game_funcs.py` — it uses an absolute
  `pathlib.Path("/Users/.../N64Recomp/RecompiledFuncs")` internally, so it
  can be invoked as `python3 /absolute/path/to/fixup_game_funcs.py > log`
  with no `cd` at all, sidestepping the compound-cd-redirect denial
  entirely.
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
  under `lib/` this session (s173 did NOT touch `lib/` — all edits were in
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
not a `lib/` submodule, with uncommitted changes across s90-173
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
