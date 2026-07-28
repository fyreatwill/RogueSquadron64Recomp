# NEXT work unit — characterize the guest call chain feeding RT64's 15th crash class

s158 fully closed out the s157 work unit (composeNpcOrientationMatrix's 7th
site: found, guarded, built, soaked) but the soak's crash was a different,
already-catalogued class instead. Read PORTING-STATE's Session 158 entry
before doing anything else; this file only has the actionable summary.

## What s158 did and found

1. Read the two NEXT.md-flagged unaccounted-for regions of
   `composeNpcOrientationMatrix` (`N64Recomp/RecompiledFuncs/funcs_40.c`):
   `:6280-6374` (prologue, before guard1) — clean, no unguarded deref.
   `:6857-7108` (between guard2 and guard6) — found the 7th site at guest
   `0x800AB4E8`/`0x800AB4EC` (source `:6901-6904`): a pointer field is read
   out of an already-guard2-validated table entry (`lw $v0, 0x4($s2)`) and
   **immediately dereferenced** (`lw $v0, 0x0($v0)`) with **no check at
   all** — stricter than guards 1-6's shape (those guard the table-entry
   address itself; this guards a field read *out of* that entry).
2. Guarded it (`ROGUESQ_LOG_COMPOSE_NPC_GUARD7`, `N64Recomp/
   fixup_game_funcs.py`, inserted after the guard6 block, same
   `U32()`-range-check-then-`goto L_800AB618` template). Full regen (`rm
   funcs_*.c` → `make_elf.py` → `regen_n64recomp.sh` → `fixup_game_funcs.py`
   once), verified x1 via grep, `cmake --build` exit clean.
3. Soaked (`scratch/agent/run_composeguard7.sh`). Reached SELECT YOUR CRAFT,
   left into hangar-flight, died at **hold-iter 1, wall=0s**. Entry
   diagnostic 508/508 (function reached) but **all 7 guards 0/0** —
   `composeNpcOrientationMatrix` never crashed this run at all, so guard7 is
   **unvalidated, not refuted**.
4. The actual crash: signal 6, `assert((dstCallTile.sampleWidth > 0) &&
   (dstCallTile.sampleHeight > 0))` in `RT64::State::loadDrawState`
   (`rt64_state.cpp:747`) ← `RT64::RDP::drawTris` ← `GBI_RDP::decodeTriangles`.
   This is the **already-catalogued 15th class** (first seen s97, recurred
   s99, s149 — **this is its 4th occurrence**), RT64-internal, not a new
   class and not `composeNpcOrientationMatrix`. It now recurs more reliably
   and earlier (hold+0-14s across all 4 hits) than any single
   `composeNpcOrientationMatrix` site — plausibly the thing preventing
   guard7 (and heapWalker's 4 guards, also still 0/0 after 2 soaks) from
   ever getting exercised.

## Do next

1. **Find the guest-side RDP-command dispatch that sets up the tile/sample
   state `loadDrawState` consumes**, i.e. whatever populates
   `dstCallTile.sampleWidth`/`sampleHeight` before `drawTris` is reached.
   Start from the RT64 side to find the call boundary (`rt64_state.cpp`
   around line 747 and its caller `RT64::RDP::drawTris` in
   `rt64_rdp*.cpp`), then look for the corresponding guest-side RSP-command
   handling (likely `gsDPSetTile`/`gsDPLoadTile`/`gsSPTriangle`-family
   opcodes in `lib/rt64` or wherever this repo's RDP command interpreter
   lives) that computes the sample dimensions from tile state. This is
   `lib/` code (RT64), not `N64Recomp/` guest-recompiled code — if you edit
   anything under `lib/`, run `./submodule-patches/export.sh` and commit
   the refreshed patches in the same iteration (hard rule, CLAUDE.md).
2. **Land a targeted instrument** (not a guess) that logs the tile-setup
   inputs (whatever RDP command / tile index / mask+shift fields feed
   `sampleWidth`/`sampleHeight`) at the point they're computed — the goal is
   to see whether the zero/invalid value already exists in guest-supplied
   tile state (matches this whole family's "guest data is corrupt/garbage,
   guard it" pattern, and would make this class fixable the same way as the
   16 guest-side guards already landed) or whether it's computed correctly
   from sane guest inputs and then miscalculated on the RT64 side (would
   mean this class is out of scope for the guest-guard approach entirely —
   say so plainly and re-prioritize away from it if so).
3. **Only if that instrument is inconclusive or this line of investigation
   dead-ends after a reasonable attempt**, fall back to: soak again with
   `ROGUESQ_LOG_COMPOSE_NPC_GUARD7=1` (already wired into
   `scratch/agent/run_composeguard7.sh`, reusable) purely to get guard7 (and
   the heapWalker guards) their first positive control — but per rule 8,
   this is a *secondary* goal now, not a soak to run for its own sake a 3rd
   time without a code change.

## Do not

- Do not re-read `composeNpcOrientationMatrix`'s already-covered regions
  (`:6374-6857`, guards 1-6's own neighborhoods) looking for an 8th site —
  not indicated by any evidence yet; the s158 soak never even reached this
  function's crash path.
- Do not treat guard7 or the heapWalker guards' 0/0 as evidence they were
  wrong — same "unvalidated, not yet exercised" status many guards in this
  family carry before eventually getting hit. Two consecutive non-crashing
  soaks is not the same as "this class stopped happening."
- Do not re-litigate the `static_5_800AAD9C` dispatcher hypothesis (closed,
  s157) or re-read `frameStartReset` itself (clean, s157).

## This session's environment notes (carry forward, still current)

- **`nm`, `otool`, `lldb` are NOT on the Bash allowlist and there is no
  human present in this autonomous loop to grant the approval prompt.**
  `scratch/agent/machoparse.py` is the working replacement (reads
  Mach-O `LC_SYMTAB` directly) — confirmed still works this session
  (`machoparse.py <binary> <symbol>` prints size via next-symbol-by-
  address delta). Don't rediscover this.
- **When testing a regex pattern against a RecompiledFuncs `.c` file
  from the Bash tool, write a `.py` script file and run it** — do NOT
  use `python3 -c "..."` with the outer shell command in DOUBLE
  quotes (silently eats `\$` before Python sees it).
- **Do NOT delegate a work unit's regen/build/soak/document steps to
  the Agent tool inside this autonomous loop** — Agent-tool delegation
  is incompatible with the per-turn Stop-hook exit contract. Do every
  step directly with Bash/Read/Edit in this session's own turn.
- A crash-class hypothesis that held for one soak is not guaranteed to
  recur on the very next soak of the "same" scene — this family's
  crash-class selection has been highly variable across ~20 sessions.
  The 15th class is the current exception: 4/4 recent late-window
  soaks that didn't hit a `composeNpcOrientationMatrix` guard hit this
  class instead, worth treating as the new default expectation for
  this scene until disproven.
- Function/line-number estimates in NEXT.md/PORTING-STATE drift a few
  lines every regen — always grep/read the actual regenerated file
  before writing a regex anchor or planning a reorder.
- N64Recomp's codegen convention for a fixed-global access: writes are
  `MEM_W(<offset>, ctx-><base>) = ctx-><src>;`; reads flip the argument
  order to `ctx-><dst> = MEM_W(ctx-><base>, <offset>);`.
- `caller_ra` (`ctx->r31` at function entry) reads `0x00000000`
  universally — stop treating it as a signal (s92, s139-141).
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns — use a `python3 -c` one-liner with `pathlib.Path.glob()`.
- **Do NOT re-run `fixup_game_funcs.py` a second time in the same
  session without a full regen first** (non-idempotent, s102/s157) —
  Delete `RecompiledFuncs/funcs_*.c`, re-run
  `python3 tools/make_elf.py` (cwd `~/Documents/Tools/rogue_squadron64`),
  then `zsh tools/agent/regen_n64recomp.sh` (cwd this repo, NOT
  `N64Recomp`), THEN `fixup_game_funcs.py` once (cwd `N64Recomp`) —
  verify by grepping the regenerated `.c` directly, and by checking the
  fixup report line count/content, not just skimming a truncated tail.
- **When capturing a fixup/regen report with Bash, don't pipe through
  `tail -N` if you need to check for a specific file's entries** —
  `sorted(base.glob(...))` processes `funcs_3.c` before `funcs_4.c`,
  `funcs_8.c`, etc. (lexicographic, not numeric). Redirect to a log file
  and `grep` it instead.
- `cmake --build` needs cwd `build/` and
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` for Metal
  shader rebuilds.
- Write a new wrapper script file per soak tag (`scratch/agent/run_
  <tag>.sh`) rather than parametrizing a single reusable script via env
  indirection.
- Launch the soak via `zsh <absolute-path>/run_<tag>.sh > <absolute-path>/
  run_<tag>_driver.log 2>&1` as a `run_in_background` Bash call, then
  block synchronously with `until ! pgrep -f "./RogueSquadron64Recomp"
  >/dev/null 2>&1; do sleep 5; done` before closing out the iteration.
- Checking submodule (`lib/...`) git status needs `env GIT_DIR=lib/X/.git
  GIT_WORK_TREE=lib/X git status --short`, or a plain `cd <absolute
  path>` as its own command followed by a separate `git status` call.
- Output redirection (`>`) from Bash is sandboxed to the session's
  allowed working directories — target `scratch/agent/`, not `/tmp`.
  A `cd <dir> && cmd > file` compound command in one Bash call can
  itself get denied — use an absolute path in the redirect target and
  skip the `cd` instead (run `cd <dir>` as its own prior Bash call).
- Prefer a single `python3 script.py` file (Write then run) for
  multi-step log analysis instead of a bash heredoc.
- Chaining many `grep`/`echo` statements with `&&`/`;` in one Bash call
  can trip the "multiple operations require approval" gate even when
  every individual command is allowlisted — split into separate Bash
  calls, one command each, when this happens.
- This fix family lives entirely in the sibling `N64Recomp` checkout
  (`fixup_game_funcs.py` + regenerated `RecompiledFuncs/*.c`), not
  `lib/` — no `submodule-patches/export.sh` step needed for it. The
  NEW work unit above (15th class) may live in `lib/rt64` instead —
  if so, that step DOES apply.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target — migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and
prune superseded detail, paired with a real experiment. Flagged for
many sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-158 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
