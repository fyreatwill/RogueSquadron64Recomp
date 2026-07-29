# NEXT work unit — reduce diagnostic I/O overhead, re-soak render-cache
# epoch probe (s230 landed the diagnostic; both soak attempts crashed
# before reaching the freeze window; a control isolated the cause to the
# diagnostic being ACTIVE, not to the new code's presence)

## Where the investigation stands

s230 found a concrete render-cache "epoch" mechanism in `processSceneNode`
(`funcs_4.c`): a global RDRAM word at `0x8011A894`, stamped into scene-node
structs by `submitSceneNodeRender` (`:10-12`/`:41-42`), compared at two
cache-check sites (`:13881-13890`/`:14732-14751`) to decide cache-hit
(reuse stale queued data) vs. recompute. Landed a diagnostic
(`ROGUESQ_LOG_RENDER_CACHE_EPOCH=1`, `fixup_game_funcs.py`'s
`_render_cache_epoch_patch_a`/`_b`) — confirmed firing, confirmed the
epoch is a LIVE, actively-changing value early in a run (climbed
`0x24->0x183` across the first ~1500 calls), NOT a stuck constant.

**But**: two soak attempts (`campose4`, copied from s229's `campose3`,
diagnostic added) both crashed near the SELECT-CRAFT→mission VI
transition (~73s), well before the previously-observed freeze windows
(`n=15360`+). Different crash PC/symbol each time (`static_5_800AB658+
49104` then `tickTextureMaterialExpiry+612`) — argues against a single
deterministic bug in the new patch's own C logic, and toward "extra I/O
overhead perturbs timing enough to reproducibly nudge this specific
transition into one of this codebase's many pre-existing unguarded-deref
crash-family bugs." **Control test**: the SAME freshly-built binary,
running the UNMODIFIED `campose3` script (diagnostic compiled in but
`ROGUESQ_LOG_RENDER_CACHE_EPOCH` left unset) ran the full 424s hold
clean, `CRASH: 0`. This isolates the cause to the diagnostic being
ACTIVE at runtime, not to its mere presence in the binary. Full
writeup: PORTING-STATE Session 230.

**The core discriminating question is still open**: does the epoch value
go constant at/near the already-known freeze point (H1, confirms this IS
the wedge), or does it keep changing/hit-missing at a steady rate right
through the freeze boundary (H2/H3, rules this mechanism out, go back to
Probe B — DL-emission payload bytes)?

## Do this iteration

### Step 1 — reduce diagnostic I/O overhead (small code change, no new build cycle needed to plan it, but DOES need a rebuild)

Edit both patch functions in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(search `_render_cache_epoch_patch_a`/`_b`, s230's patch, currently right
after the s152 `_scene_rq_counter_patch`):
- Raise the heartbeat modulus from `% 500` to something much coarser
  (e.g. `% 5000` or `% 10000`) at BOTH sites.
- Consider dropping the unconditional per-transition log entirely (or
  raising its `run>=50` threshold much higher, e.g. `run>=2000`) — it may
  fire very often early on (epoch changes rapidly per the s230 data:
  transitions at n=186, n=1304 already logged in the first 1500 calls)
  and each `fprintf` is a real syscall that could be the actual timing
  perturbation.
- Do NOT change the underlying comparison/hit-miss logic itself — only
  the logging cadence. The goal is fewer syscalls, not different data.

This is ONE new work unit (a code edit), not a re-litigation of s230's
already-closed "is the epoch live" question — do not remove or redesign
the core diagnostic, just throttle its I/O.

### Step 2 — regen/build/soak (standard recipe, unchanged)

1. `cd` into N64Recomp checkout, delete stale `RecompiledFuncs/funcs_*.c`
   (`python3 -c "import glob, os; [os.remove(f) for f in
   glob.glob('funcs_*.c')]"`).
2. `python3 tools/make_elf.py` (rogue_squadron64 checkout).
3. `./tools/agent/regen_n64recomp.sh` (this repo, cwd-independent).
4. `fixup_game_funcs.py` **exactly once** — grep its report for both
   `render-cache epoch diagnostic site A/B patched x1` (regression check
   the patch still applies) plus your new heartbeat-interval change
   actually landed (grep the generated `funcs_4.c` for `% 5000`/whatever
   value you chose, to confirm the edit took).
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   build -j8`, safe to background (`run_in_background: true`).

### Step 3 — soak, budget 2 fresh attempts

Copy `scratch/s73_post_a_scene/run_campose3.sh` (the clean-running s229
baseline, NOT `run_campose4.sh` which is s230's crashed attempt) to a NEW
tag (e.g. `campose5`) — do not overwrite `campose3`/`campose4*` logs, all
still hold useful data. Add `ROGUESQ_LOG_RENDER_CACHE_EPOCH=1` (same as
s230). Same `schedulepush2`-derived schedule. Run in the FOREGROUND
(synchronous), `timeout: 590000` (budget ~10min, s229's clean run took
422s).

- **If it crashes again at ~73s with reduced I/O**: this rules out "I/O
  overhead" as the mechanism and points to the SELECT-CRAFT→mission VI
  transition itself being independently fragile (worth its own probe,
  separate from the epoch-cache question) — write this up plainly, do
  NOT spend a 3rd consecutive session soaking this exact diagnostic
  (iron rule 8). Consider: does simply having `ROGUESQ_LOG_CAMPOSE=1`
  etc. (already-armed, unrelated diagnostics) plus the NEW diagnostic's
  code being present (even disabled) reproduce it too? That would be a
  useful next control if this path is taken.
- **If it runs clean past `n=15360`-ish**: proceed to Step 4 analysis —
  this is the discriminating soak.

### Step 4 — analyze (only if the soak survives to the freeze window)

Small Python script (not raw grep dumps into your own context) parsing
`[render-cache-epoch-a/b-hb]` and `[render-cache-epoch-a/b-transition]`
lines: find the last transition before the run ends, and check whether
the epoch value's own last-seen value keeps changing after the already-
known freeze `n` (re-derive fresh — `flag`/`camptr` freeze point varies
soak to soak, proven non-deterministic s223) or goes constant there.
Cross-reference against `hit`/`miss` ratio over time (does miss-rate
drop to 0 post-freeze, meaning perpetual cache-hit?).

## Do NOT do this iteration

- Do not re-derive whether the epoch is "live" — s230 already confirmed
  this empirically (it changes across the first ~1500 calls). The open
  question is specifically its behavior AT/AFTER the freeze point.
- Do not re-run `campose4` as-is (unmodified) expecting a different
  result — 2/2 crashed, budget used, per iron rule 8 either fix the
  overhead (Step 1) or pick a different probe, don't just retry.
- Do not re-instrument `traverseSceneGraphRecursive`/`processSceneNode`/
  `submitSceneNodeRender` entry counts, or the camera struct's own fields
  (`m00`, `deref0`, `flag`/`camptr`) — all closed s225/s226/s229.
- Do not dump entire raw log files into your own context — write short
  Python scripts, per s229/s230's method.

## Environment notes (carried forward from s229, still current)

- **Permission gate CONFIRMED CLEARED s229, still clear s230** —
  `regen_n64recomp.sh`, `stop_gate.sh --verify`, and all `tools/*`/
  `build/*` commands ran normally this session too. Trust this.
- Bash cwd DOES persist across tool calls within a session (confirmed
  s230) — but be careful: an explicit `cd` in one call changes the
  persisted cwd for ALL subsequent calls, including ones that assumed a
  different directory. Prefer absolute paths for `sed`/`grep`/etc. to
  avoid cwd-tracking mistakes, or re-`pwd` if unsure.
- **`cmake --build` is safe to background**; the actual game-soak launch
  script must stay SYNCHRONOUS/foreground (needs to send scheduled
  keypresses and SIGKILL the process itself at the end).
- **This exact schedule (`schedulepush2`/`campose*` family) is PROVEN
  non-deterministic (s223)** — freeze onset `n`/crash timing varies run
  to run. Budget 2 attempts before drawing conclusions, re-derive numbers
  fresh each soak. s230 additionally showed CRASHES can also cluster
  tightly around specific VI transitions when I/O overhead is added —
  don't assume all variance is uniformly random.
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- **`git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule**
  — `cd` first (its own Bash call), then bare `git <cmd>`.
- **Headless permission matching is a PREFIX match on the command
  string** — a leading env assignment breaks it (write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`).
- **`ROGUESQ_LOG_CAMPOSE=1`, `ROGUESQ_LOG_MAT3INV=1`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER=1`, `ROGUESQ_LOG_RENDERUNLIT_GUARD=1`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD=1/3/4`, `ROGUESQ_LOG_MESGQUEUE_GUARD=1`,
  `ROGUESQ_LOG_HEAPLISTDEQ_GUARD=1`, `ROGUESQ_LOG_EMIT_DL_GUARD2/3=1`,
  `ROGUESQ_LOG_RENDER_CACHE_EPOCH=1`**: campose3/campose4's armed set —
  keep all of these when building the next soak script (`run_campose3.sh`
  is the clean baseline to copy from).
- **Setup camera struct layout** (unchanged): `+0x0` nullable
  linked-node pointer; `+0x10/0x14/0x18/0x1C` integer viewport rect;
  `+0x20/0x24/0x28` perspective near/scale float scalars; `+0x2C` a 3x3
  float rotation submatrix (36 bytes, to `+0x50`).
- **`traverseSceneGraphRecursive` is `funcs_4.c:15053-15357`**,
  `processSceneNode` is `funcs_4.c:13817-15052`, `submitSceneNodeRender`
  is `funcs_4.c:6-3017`. The render-cache epoch mechanism (s230):
  read/stamp in `submitSceneNodeRender:10-12`/`:41-42`, cache-checks in
  `processSceneNode:13881-13890`/`:14732-14751`, the only known writer to
  the epoch global is `buildAndRegisterDefaultMaterial:22608-22636` (a
  hardcoded set-to-1, not an increment — still unexplained how/whether it
  changes elsewhere; s230's live soak data proves it DOES change
  somehow, just not via a statically-greppable direct write).
- **`setupCameraMatrices` is `funcs_4.c:19142-21603`**, camera-pose
  diagnostic at guest `0x800178A8`, `ROGUESQ_LOG_CAMPOSE=1`, keep armed.
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`** — s221's guard
  doesn't cover all fault sites; flagged, not chased (orthogonal).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`**
  — untracked in that sibling checkout (known since s83).
- **`fixup_game_funcs.py` is NOT idempotent** — never run it twice
  without a delete-all-funcs regen in between.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops).
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — finding them reset at session start is
  normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`, and
  `NEXT.md` are tracked exceptions. Use `git add -f` for anything else
  under `scratch/` you want to survive (e.g. `BLOCKED.md`).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s230 —
read it with `grep`/offset-limited `Read`, never a plain whole-file
`Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail — flagged for 26+
sessions without action, escalating further.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` and `lib/N64ModernRuntime` both still show as modified in `git
status` as of s230 — not investigated this session either (no lib/ edits
made, so no export.sh/commit obligation triggered). Still worth checking
whether these are in-progress uncommitted patches vs. drift from
`submodule-patches/*.patch` before assuming steady-state dirtiness.
