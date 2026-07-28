# NEXT work unit — source-read `processSceneNode`'s self-recursive SIGBUS

s174 source-read `tickMusyXIfActive`'s 5 callees, found and guarded the
23rd crash class's 2nd bug (`tickAndReap3DAudioVoices`), built and soaked
it once. The guard never fired (0/0), and — more informatively — neither
did s166's `isAudioSlotActive` guard on the same chain: the
`waitForAnyAudioSlot`-chain corruption simply didn't happen this run at
all, even though the soak used the exact same driven-input recipe as
s173's soak that died to it at `decisionN=356`. This run instead survived
27x further (`decisionN=9694`, deep into the 120s hold window) before
dying to a **2nd independent occurrence** of an already-catalogued but
never-source-read crash: `processSceneNode` self-recursion. Read
PORTING-STATE Session 174 before doing anything else; this file only has
the actionable summary.

## What s174 established (read before doing anything else)

- **The `tickAndReap3DAudioVoices` guard is landed, built clean, and
  soaked once** (`N64Recomp/fixup_game_funcs.py`, new
  `ROGUESQ_LOG_TICK_REAP_3D_VOICES_GUARD` env var, file-scoped
  `funcs_26.c`). **Not committed** — same long-standing uncommitted-
  history posture as `N64Recomp` since s54/s90, not this session's call to
  resolve.
- **The `waitForAnyAudioSlot` chain (23rd crash class, both known
  sub-bugs) is confirmed racy, not deterministic given the driven-input
  recipe.** Do not read a future 0/0 on either audio guard as proof
  they're wrong or unnecessary — it may simply mean that run's corruption
  didn't occur. Only a *positive* control (the guard actually firing) or a
  large multi-soak sample would settle whether the guard is sufficient.
- **4 of the 5 candidates NEXT.md (s173) listed are now ruled out**:
  `factor5MutexAcquire`/`factor5MutexRelease` (fixed literal address only,
  no computed deref), `stopAllSynthVoices` (already range-checked by an
  `slt` loop bound), and `tickActiveSongs`'s own body (compile-time-bounded
  addresses only). **One new candidate was found but not guarded**:
  `tickActiveSongs`'s callee `tickSongSequence` (funcs_25.c:4878) has 2
  unguarded per-song linked-list walks at funcs_25.c:5018-5046 and
  5050-5077 (list heads at struct offsets `0xE78`/`0xE7C`, null-check-only,
  same shape as the bug just fixed) — flagged as the next candidate for
  this specific chain if a future soak shows this session's fix alone
  doesn't close class 23, but NOT today's priority (see below).
- **`processSceneNode`'s self-recursive SIGBUS now has 2 independent
  occurrences** (s172 soak 1, s174) with a fully matching backtrace:
  `processSceneNode` (self, +8148 bytes) <- `traverseSceneGraphRecursive`
  <- `setupCameraMatrices` <- `static_5_800C9BF0` <- `menuOverlayInit` <-
  `mainGameLoop` <- `mainBootstrapWorker`. Never source-read. This is now
  the crash that actually surfaces once the audio-chain race doesn't hit
  first — reasonably the next priority.

## Do next

**Source-read `processSceneNode`** (`N64Recomp/RecompiledFuncs/funcs_4.c`,
around lines 13759-14861 — grep `RECOMP_FUNC void processSceneNode` to get
the exact start line, since line numbers shift after every regen) and its
caller `traverseSceneGraphRecursive` in the same file:

1. Determine whether the self-recursion is **guest-intentional** (a real
   scene-graph tree walk — e.g. recursing into child/sibling nodes — that
   should terminate on a leaf/null but doesn't because a child pointer is
   corrupted or the graph has an accidental cycle) or this family's usual
   **unguarded-deref shape** (a fixed-table lookup indexing into something
   that happens to loop back into the same function via a computed
   function-pointer call, unlikely here given the backtrace shows literal
   self-recursion, not an indirect call — but confirm by reading, don't
   assume).
2. If it's a real tree walk: look for what the guest code bounds it with
   (if anything). A missing depth cap or a corrupted "child" pointer that
   happens to point back into an ancestor (creating a cycle) are the two
   most likely mechanisms. Either fix would look different: a depth cap
   added at the guard idiom's usual insertion point (this function's
   entry, incrementing a static/stack depth counter and bailing past some
   sane limit like 64-256), or a range/identity check on the specific
   pointer being recursed through if it can be traced to a single
   corrupting write elsewhere.
3. Once the mechanism is identified and unique guest addresses are
   confirmed via grep (per every prior guard's lesson — do this BEFORE
   writing the patch, not after), guard it following the same
   comment-plus-patch-function convention in `N64Recomp/fixup_game_funcs.py`
   as every guard before it (see the `_tick_and_reap_3d_audio_voices_guard_patch`
   function landed this session for the most recent example, including how
   to route the bail through an existing epilogue label vs. a bare
   `return;` depending on whether the function is frameless).
4. Regen: `zsh tools/agent/regen_n64recomp.sh` then
   `python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   ONCE (redirect to a log — it is NOT idempotent), verify the patch report
   shows exactly x1, then rebuild
   (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`).
5. Soak with the new guard's env var armed (copy
   `scratch/agent/run_tickreap3dvoicesguard1.sh` to a new tag, keep every
   prior env var — they're all free, including
   `ROGUESQ_LOG_TICK_REAP_3D_VOICES_GUARD=1` and
   `ROGUESQ_LOG_AUDIO_SLOT_ACTIVE_GUARD=1` from this session) and check
   whether it fires (positive control) and whether the process survives
   past `decisionN=9694`/hold-iter 28 (s174's death point) or further still.

**Why this is top priority over `tickSongSequence`'s 2 list walks**: this
crash is the one that actually kills runs once the audio-chain race
doesn't hit — it's the next thing actually blocking progress, observed
twice independently. The `tickSongSequence` leads are real but currently
masked by whichever bug wins the race first; revisit them once
`processSceneNode` stops being the dominant early-blocking crash.

## Do not

- Do not re-run `run_tickreap3dvoicesguard1.sh` unmodified hoping for a 2nd
  data point on that guard specifically as your primary work unit — it's
  landed, it's a real (if uninformative) negative control, and the more
  actionable finding this session is the `processSceneNode` recurrence.
  The env block is still useful scaffolding to copy from for whatever new
  guard you add.
- Do not treat this session's "chain didn't crash at all" result as
  evidence the `tickAndReap3DAudioVoices` guard fixed anything — no
  positive control fired. It's exactly as inconclusive as s173's own null,
  just for a different reason (this run's race went a different way).
- Do not skip the source read and jump straight to instrumenting
  `processSceneNode` "to be safe" — per rule 6, read the function and its
  caller fully first. Given the backtrace shows literal self-recursion
  (not an indirect call through a corrupted function pointer), the fix
  shape here may look different from every guard so far (a depth cap
  rather than a bounds-checked deref) — don't force-fit the usual template
  before confirming what the actual defect is.

## Blocking on a long-running soak (learned the hard way, still current)

Simplest approach (used successfully s168-s174): run the driver script
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
  under `lib/` this session (s174 did NOT touch `lib/` — all edits were in
  the separate `N64Recomp` sibling checkout's `fixup_game_funcs.py`).
- `/scratch/` is entirely gitignored in this repo except 3 force-tracked
  files: `scratch/agent/NEXT.md`, `OUTCOME`, `STATUS`. New soak
  scripts/logs under `scratch/agent/` or `scratch/s73_post_a_scene/` never
  need `git add` — they're intentionally untracked.
- A `grep -c "[pattern]"` across a very large run.log (millions of lines
  from a per-tick instrument like `[rs-malloc-walk]`) is fine and fast —
  no need to avoid grepping big log files, just don't `cat`/`Read` them
  wholesale.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target — migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-174
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
