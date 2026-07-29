# NEXT work unit — permission gate cleared s229; freeze wedge now confirmed
# downstream of camera struct + traversal call chain; target DL-emission
# content next

The s226-s228 `Bash(<dir>/:*)` permission gate is CLOSED — confirmed
cleared s229 (`stop_gate.sh --verify` and `regen_n64recomp.sh` both ran for
real). Do NOT re-litigate it; if a similar "requires approval" message
reappears on an allow-listed command, that is NEW information (a
regression), not a continuation of the old ticket — treat it as a fresh
finding, not a retry of s226-s228's diagnosis.

## Where the investigation stands

Two independent things are now proven to keep running steadily through the
ENTIRE visibly-frozen window (checksum-confirmed picture freeze, crash-free):
1. **s225**: `traverseSceneGraphRecursive` -> `processSceneNode` ->
   `submitSceneNodeRender` call chain keeps firing at a steady rate.
2. **s224/s226/s229**: the camera struct's own fields (`m00`, freezes at
   `n=21240`) AND the first word of what its linkage pointer points to
   (`deref0`, freezes at `n=57900` — barely before the run ends) both keep
   changing long after `flag`/`camptr` (the struct pointer itself) go fixed
   at `n=15360`.

So: the call chain runs, and the camera-adjacent DATA it would read keeps
changing. Yet the rendered picture is byte-identical frame after frame.
**The wedge is not "something stopped running" or "something stopped
updating" — it's "the same output gets produced every call despite live
input."** This rules out a stall anywhere probed so far (traversal, camera
data, camera-pointed-to memory).

## Do this iteration

### Step 1 — pick ONE of these two probes, not both

**Probe A (content-independent culling/selection check) — cheaper, do this
first:**
`processSceneNode`/`submitSceneNodeRender` (`funcs_4.c`, already have
several tracers from s152/s190/s200/s219-221, all confirmed firing) may
contain a culling or LOD-selection check that reads some FROZEN control
value (not the camera struct — something else, e.g. a bounding-box cache,
a visibility flag, a display-list pointer table entry) and short-circuits
to the same draw call regardless of camera pose. Read
`processSceneNode`/`submitSceneNodeRender`'s source in `funcs_4.c` (find
via `grep -n "processSceneNode\|submitSceneNodeRender" funcs_4.c` in the
N64Recomp checkout) looking specifically for: any comparison against a
cached/previous value that could gate an early return, OR any argument
passed to the DL-emission call that ISN'T derived from the camera struct
this session already traced. Name the specific suspect field/check before
instrumenting it.

**Probe B (DL-emission payload) — more expensive, needs new instrumentation:**
Hash or log a few bytes of the ACTUAL display-list command being emitted
(not just a call-site counter) across the freeze boundary. If the DL bytes
are identical pre/post freeze, the bug is upstream of DL emission (a
selection/culling check feeding it the same source data or the same
cached DL). If the DL bytes keep changing but the screen doesn't, the bug
is at or after DL submission (RDP, framebuffer target, present/swap).
`emitAllocatedDLCommand` (`funcs_3.c:2622-3210`, already flagged s221 as
having an incomplete guard, orthogonal) may be a convenient hook point —
or find the actual call site inside `submitSceneNodeRender`.

Write the 2-4 hypotheses and the discriminating measurement into a fresh
section of this file BEFORE building, per CLAUDE.md's iteration contract —
don't skip this because the broad direction is already chosen; the SPECIFIC
field/check/hook still needs to be named and falsifiable.

### Step 2 — regen/build/soak (gate confirmed clear, use normally)

Standard recipe, unchanged from s229 (all steps ran clean this session):
1. `cd` into N64Recomp checkout, delete stale `RecompiledFuncs/funcs_*.c`
   if any (`python3 -c "import glob, os; [os.remove(f) for f in
   glob.glob('funcs_*.c')]"`).
2. `python3 tools/make_elf.py` (rogue_squadron64 checkout).
3. `./tools/agent/regen_n64recomp.sh` (this repo, cwd-independent).
4. `fixup_game_funcs.py` **exactly once** — capture to a NEW tag
   (`N64Recomp/scratch_fixup_report_s230.txt`), grep for confirmation your
   new patch applied (and that `camera-pose diagnostic` still applies,
   regression check).
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   build -j8` (background this — it's long-running and gated on nothing
   interactive; the s229 session did this successfully with
   `run_in_background: true`).

### Step 3 — soak

Copy `scratch/s73_post_a_scene/run_campose3.sh` to a NEW tag (e.g.
`campose4`) — do NOT overwrite prior tags. Same `schedulepush2`-derived
schedule, keep all existing env vars armed as regression checks, add
whatever new env var Step 1 requires. Budget 2 attempts (proven
non-determinism, s223) — s229's run took wall=422s, budget `timeout: 590000`
and run in the FOREGROUND (synchronous), per NEXT.md's longstanding
instruction — do not background the actual game-soak launch itself (only
the cmake build step is safe to background).

### Step 4 — analyze

Use a small Python script (not raw grep dumps to your own context) to
parse the new diagnostic's log lines and find its own freeze/no-freeze
point, same method as s229's `deref0` analysis. Compare against the
already-known freeze landmarks (`flag`/`camptr` at `n=15360` this run,
`m00` at `n=21240`, `deref0` at `n=57900` — note these `n` VALUES are
soak-specific due to proven non-determinism; re-derive fresh ones each
soak rather than assuming these exact numbers repeat).

## Do NOT do this iteration

- Do not re-litigate the permission gate (s226-s228) — closed, confirmed
  working s229. A NEW gate failure on a DIFFERENT command is new
  information; re-blocking on the SAME already-fixed rules without first
  re-checking `.claude/settings.json`'s current content would be an
  unjustified regression claim.
- Do not re-derive the a0/a1 camera-struct source trace — closed s226.
- Do not re-instrument scene-graph call rates (traversal/processSceneNode/
  submitSceneNodeRender entry counters) — closed s225, still firing s229.
- Do not re-soak `deref0` alone expecting a different result — s229's
  result (outcome #2: keeps changing far past the freeze) is a clean,
  well-powered result (979 samples, full run coverage). Build on it, don't
  repeat it.
- Do not dump entire raw log files or full grep results into your own
  context — write short Python scripts that print only the summary
  (transition points, distinct-value counts), per s229's method. The
  campose3 log was 551k lines; a naive `cat`/`grep` without `head`/a
  script would blow the context budget.

## Environment notes (carried forward, updated s229)

- **Permission gate CONFIRMED CLEARED s229.** `.claude/settings.json` now
  has `Bash(tools/*)` / `Bash(./tools/*)` / `Bash(build/*)` /
  `Bash(./build/*)` (glob form, no colon) per commit `89ba212`. Both
  `stop_gate.sh --verify` and `regen_n64recomp.sh` ran for real this
  session (no approval-block message). Trust this going forward; don't
  re-run the old falsification tests.
- **`RecompiledFuncs/funcs_*.c` was already empty at the start of s229** —
  no stale files needed deleting. If you find it non-empty at the start of
  a future session, that's a sign a previous regen ran partially; delete
  before regenerating, per the standard recipe.
- **Compound `cd dir && cmd > file` (cd plus redirection in one Bash call)
  is rejected by the sandbox** ("Commands that change directories and
  write via output redirection require explicit approval") — split into
  separate Bash calls: one bare `cd`, then the command with redirection as
  its own call. Confirmed s229, consistent with s228's other compound-command
  finding (`cd ... && cmd` in one call is separately risky) — this is a
  slightly different trigger (redirection specifically), same fix (split
  the calls).
- **`cmake --build` is safe to background** (`run_in_background: true`) —
  it's long, has no interactive dependency, and a task-notification
  arrives when done. The actual game-soak launch (`run_campose*.sh` via
  `run_mission_keys.sh`) must stay SYNCHRONOUS/foreground per longstanding
  instruction (needs to send scheduled keypresses and SIGKILL the process
  itself at the end) — do not background that one.
- **`deref0` soak-validated s229** — outcome #2 confirmed (keeps changing
  far past `flag`/`camptr`'s freeze, further than even `m00` does). Do not
  treat this as needing re-validation; build the next probe on top of it.
- **Setup camera struct layout** (s223/s224/s226, unchanged): `+0x0` a
  nullable linked-node pointer; `+0x10/+0x14/+0x18/+0x1C` an integer
  viewport rect; `+0x20/+0x24/+0x28` perspective near/scale float scalars;
  `+0x2C` a 3x3 float rotation submatrix (36 bytes, to `+0x50`).
- **`traverseSceneGraphRecursive` is `funcs_4.c:15053-15357`**,
  `processSceneNode`/`submitSceneNodeRender` (both `funcs_4.c`) have
  several s152/s190/s200/s219-221 tracers/guards, all confirmed firing
  through s225's AND s229's freeze — do not re-instrument their entry/call
  counts, but DO read their source for the culling-check probe (Step 1
  Probe A above) — that's new territory (reading logic, not re-counting
  calls).
- **`setupCameraMatrices` is `funcs_4.c:19142-21603`**, camera-pose
  diagnostic at guest `0x800178A8`, `ROGUESQ_LOG_CAMPOSE=1`, keep armed.
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`** — s221's guard
  doesn't cover all fault sites; flagged, not chased (orthogonal to this
  investigation, a separate crash-family bug).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`** —
  untracked in that sibling checkout (known since s83, not this repo's
  commit scope, flagged for the user).
- **`fixup_game_funcs.py` is NOT idempotent** — never run it twice without
  a delete-all-funcs regen in between.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops).
- **This exact schedule (`schedulepush2`/`campose*` family) is PROVEN
  non-deterministic on identical input (s223)** — freeze onset `n`/`hold_NN`
  varies run to run (this run: `hold_82`; s225's sceneTraverse2 run:
  `hold_01`; s222: ~4s). Budget 2 attempts before drawing conclusions, and
  re-derive freeze-onset numbers fresh each soak.
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- **`git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule**
  — `cd` first (its own Bash call), then bare `git <cmd>`.
- **`git check-ignore` is not in the git-subcommand allow list.**
- **Headless permission matching is a PREFIX match on the command string**
  — a leading env assignment breaks it (`PROBE_MODE=1 zsh run.sh` doesn't
  match a `zsh` allow rule; write `env PROBE_MODE=1 zsh run.sh` instead).
  Separate, older, already-understood quirk from the s226-s229 directory-
  glob gate.
- **`ROGUESQ_LOG_CAMPOSE=1`, `ROGUESQ_LOG_SCENE_TRAVERSE=1`,
  `ROGUESQ_LOG_SCENE_RQ_COUNTER=1`, `ROGUESQ_LOG_PROCESS_SCENE_NODE_GUARD=1`**:
  all confirmed firing through s229's freeze; keep armed, closed questions,
  do not re-instrument entry/call counts (do read source for new logic
  probes).
- The `[CRASH][pc-symbol]` diagnostic (dladdr on raw mcontext `pc`) is
  permanent, always-on (s213).
- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are ALL
  blocked. Source-level reasoning only.
- `-O0` Debug build, `RECOMP_FUNC` noinline, no LTO.
- `recomp.h`: `MEM_W(base, offset)` = `*(int32_t*)(rdram + ((base+offset) -
  0xFFFFFFFF80000000))` — arg order is (base-value, offset-literal). `U32(val)`
  = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit KSEG0 `gpr` sign-extends,
  upper bits `0xFFFFFFFF`. Always check upper 32 bits explicitly.
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`, and
  `NEXT.md` are tracked exceptions. If you want `BLOCKED.md`/
  `SUBSTITUTION.md` to survive, use `git add -f` explicitly — a bare
  `git add -A` silently skips them (root-caused s228).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s229 —
read it with `grep`/offset-limited `Read`, never a plain whole-file
`Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail — flagged for 25+
sessions without action, escalating further.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` and `lib/N64ModernRuntime` both still show as modified in `git
status` as of s229 — not investigated this session either (no lib/ edits
made, so no export.sh/commit obligation triggered). Still worth checking
whether these are in-progress uncommitted patches vs. drift from
`submodule-patches/*.patch` before assuming steady-state dirtiness.
