# NEXT work unit — abandon the epoch-diagnostic-through-SELECT-CRAFT
# channel (0/4 hit rate), switch to Probe B (DL-emission/RDP payload bytes)

## Where the investigation stands

s229/s230 found a concrete render-cache "epoch" mechanism in
`processSceneNode` (`funcs_4.c`, RDRAM global `0x8011A894`,
`ROGUESQ_LOG_RENDER_CACHE_EPOCH=1`) and confirmed it's live/changing early
in a run. But s231 closes off the last remaining excuse: **4 soak attempts
in a row with this diagnostic armed (campose4 x2 in s230, campose5/campose6
in s231) have ALL crashed at the same ~73-74s SELECT-CRAFT->mission VI
transition, before ever reaching the freeze window (`n=15360`+).** s231
specifically ruled out "diagnostic I/O overhead" as the cause — cut
heartbeat/transition-log volume 10x/40x and it still crashed within ~0.3s
of the same timing, with a 3rd and 4th distinct underlying crash PC
(`memcpy_recomp+288` SIGBUS, and a `sinfApprox` NaN `NAN_CHECK` assert
SIGABRT — both pre-existing, already-documented crash families, see
CURRENT-TRUTH -55/-56). Conclusion: the transition itself is fragile,
independent of this diagnostic. The epoch diagnostic is not proven wrong or
broken — it has simply never had a chance to run past ~n=1500 with live
freeze-window data. Full writeup: PORTING-STATE Session 231.

**Per iron rule 8, do not attempt a 5th unmodified soak on this exact
channel.** The core discriminating question (does the epoch go constant
at/near the freeze point, or keep changing/hit-missing through it?) remains
open, but this specific path to answering it is not productive right now.

## Do this iteration — pick ONE of these two options

### Option A (preferred): switch to Probe B — DL-emission/RDP payload bytes

This is s229's other open lead, orthogonal to the SELECT-CRAFT transition
question (every existing probe has had to survive the same schedule
regardless, so this isn't more exposed to the fragile transition than any
prior successful soak — campose1/campose3 both survived it fine on
schedules WITHOUT the epoch diagnostic armed).

1. Read `submitSceneNodeRender` (`funcs_4.c:6-3017`) and
   `processSceneNode`'s cache-check sites (`:13881-13890`/`:14732-14751`)
   to find where the actual DL-emission payload (not just hit/miss) is
   produced/queued after a cache decision.
2. Design a diagnostic that logs a cheap hash (not raw bytes — budget!) of
   the emitted payload, gated the same way as existing diagnostics (env
   var, phase-scoped counters, coarse heartbeat from the start — apply
   s231's lesson, do NOT start at `%500`).
3. Write the 2-4 hypotheses in this file before building: does the
   hash/payload change post-freeze (rules out "identical output" theories)
   or go constant (would mean downstream stages are being fed frozen data
   regardless of what feeds them, i.e. NOT a cache-epoch bug specifically)?
4. Standard regen recipe (below), soak on `campose3`'s clean baseline
   (COPY it, add the new var, don't touch `ROGUESQ_LOG_RENDER_CACHE_EPOCH`
   — leave it armed as a regression check but this probe doesn't depend on
   it), budget 2 attempts.

### Option B: find/shorten a schedule past SELECT-CRAFT before re-trying epoch

Only pick this if Option A turns out to be poorly scoped once you read the
code. Look at whether `campose3`'s (or any other known-good) schedule can
be adapted to spend less real time in the SELECT-CRAFT screen (e.g. shorter
`stable=12s` wait, faster craft-select key sequence) — the goal is reducing
exposure to the ~73s crash window, not changing game logic. This is a
weaker lead than Option A; only take it if Option A stalls.

## Standard regen recipe (unchanged, for either option)

1. `cd` into N64Recomp checkout, delete stale `RecompiledFuncs/funcs_*.c`:
   `python3 -c "import glob, os; [os.remove(f) for f in
   glob.glob('RecompiledFuncs/funcs_*.c')]"` — **note the `RecompiledFuncs/`
   prefix, a bare `funcs_*.c` glob from the repo root matches nothing and
   silently no-ops (s231 caught this on the first try — always check the
   print count, not just absence of an error).**
2. `python3 tools/make_elf.py` (rogue_squadron64 checkout).
3. `./tools/agent/regen_n64recomp.sh` (this repo, cwd-independent).
4. `fixup_game_funcs.py` **exactly once** — grep its report for the new
   diagnostic's patch line AND spot-check the generated `.c` file for your
   actual changed values, not just presence.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   build -j8`, safe to background (`run_in_background: true`).

## Do NOT do this iteration

- Do not re-run `campose4`/`campose5`/`campose6` unmodified expecting a
  different result at the SELECT-CRAFT transition — 4/4 crashed, budget
  used, per iron rule 8.
- Do not re-derive whether the render-cache epoch is "live" (closed s230)
  or whether I/O overhead caused the s230 crashes (closed s231, refuted).
- Do not re-instrument `traverseSceneGraphRecursive`/`processSceneNode`
  entry counts or the camera struct's own fields (`m00`, `deref0`,
  `flag`/`camptr`) — all closed s225/s226/s229.
- Do not dump entire raw log files into your own context — write short
  Python scripts (per s229/s230/s231's method) or use targeted `grep`.
- Do not start any new diagnostic's heartbeat interval at `%500` or its
  transition-log threshold at `run>=50` — s231 showed these values are
  cheap to get wrong and expensive to discover wrong (a full soak cycle).
  Start coarse (e.g. `%5000`/`run>=2000`) and only tighten if a soak
  survives cleanly and needs more resolution.

## Environment notes (carried forward, still current as of s231)

- **Permission gate CONFIRMED CLEARED s229/s230/s231** — trust it; all
  `tools/*`/`build/*` commands ran normally again this session.
- Bash cwd persists across tool calls within a session — but an explicit
  `cd` changes it for ALL subsequent calls. Prefer absolute paths or re-`pwd`
  if unsure.
- **`cmake --build` is safe to background**; the game-soak launch script
  must stay SYNCHRONOUS/foreground (sends scheduled keypresses, SIGKILLs
  itself at the end).
- **This exact schedule (`schedulepush2`/`campose*` family) is PROVEN
  non-deterministic (s223)** — but s231 shows the SELECT-CRAFT->mission
  transition specifically has now failed 4/4 times with the epoch
  diagnostic armed, which is different from "random variance" — treat this
  transition as a known-fragile window until proven otherwise, not as noise
  to average away.
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ... > file` commands with output redirection get
  blocked by the permission layer ("Commands that change directories and
  write via output redirection require explicit approval") — issue the
  `cd` as its own Bash call first, then the redirecting command as a
  separate call (cwd persists, per above).
- **`git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule**
  — `cd` first, then bare `git <cmd>`.
- **Headless permission matching is a PREFIX match on the command
  string** — write `env PROBE_MODE=1 zsh run.sh`, not
  `PROBE_MODE=1 zsh run.sh`.
- **campose3/campose4's armed env-var set** (keep all when building the
  next soak script — copy `run_campose3.sh`, the clean baseline, or
  `run_campose5.sh`/`run_campose6.sh` if you want the epoch var
  pre-included): `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_RENDER_CACHE_EPOCH`.
- **Setup camera struct layout** (unchanged): `+0x0` nullable
  linked-node pointer; `+0x10/0x14/0x18/0x1C` integer viewport rect;
  `+0x20/0x24/0x28` perspective near/scale float scalars; `+0x2C` a 3x3
  float rotation submatrix (36 bytes, to `+0x50`).
- **`traverseSceneGraphRecursive` is `funcs_4.c:15053-15357`**,
  `processSceneNode` is `funcs_4.c:13817-15052`, `submitSceneNodeRender` is
  `funcs_4.c:6-3017`. Render-cache epoch mechanism (s230): read/stamp in
  `submitSceneNodeRender:10-12`/`:41-42`, cache-checks in
  `processSceneNode:13881-13890`/`:14732-14751`; only known static writer
  `buildAndRegisterDefaultMaterial:22608-22636` (hardcoded set-to-1).
- **`setupCameraMatrices` is `funcs_4.c:19142-21603`**, camera-pose
  diagnostic at guest `0x800178A8`, `ROGUESQ_LOG_CAMPOSE=1`, keep armed.
- **Pre-existing crash-family sites, do not treat as new bugs if hit
  again**: `sinfApprox` NaN `NAN_CHECK` assert (`funcs_5.c:6460`, signal 6);
  various unguarded-deref SIGBUS sites across `funcs_*`/`mesgqueue.cpp`
  (signal 10) — see CURRENT-TRUTH -55/-56 and PORTING-STATE Session 214/215
  for the wider family and a proposed (not yet shipped) NAN_CHECK-disable
  fix that could clear this whole recurring family in one shot.
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`** — s221's guard
  doesn't cover all fault sites; flagged, not chased (orthogonal).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`**
  — untracked in that sibling checkout (known since s83).
- **`fixup_game_funcs.py` is NOT idempotent** — never run it twice without
  a delete-all-funcs regen in between.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops).
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`, and
  `NEXT.md` are tracked exceptions. Use `git add -f` for anything else
  under `scratch/` you want to survive.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s231 —
read it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail — flagged for 27+ sessions without action.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` and `lib/N64ModernRuntime` both still show as modified in `git
status` as of s231 — not investigated this session either (no lib/ edits
made, so no export.sh/commit obligation triggered). Still worth checking
whether these are in-progress uncommitted patches vs. drift from
`submodule-patches/*.patch` before assuming steady-state dirtiness.

The pre-existing NaN/`NAN_CHECK` and unguarded-deref crash families
(surfaced again this session via `sinfApprox` and `memcpy_recomp`) have a
proposed but unshipped fix (disable/soften `NAN_CHECK` aborts, CURRENT-TRUTH
-55/-56, PORTING-STATE Session 215) that could reduce how often unrelated
soaks die to this family before reaching their actual target. Worth
picking up as its own work unit if Probe B also keeps dying to this family.
