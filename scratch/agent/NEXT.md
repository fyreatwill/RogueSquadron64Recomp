# NEXT work unit — find what feeds traverseSceneGraphRecursive's two fixed
# scene-root pointers, and whether the game-logic/simulation tick that should
# be mutating them is still running

Read PORTING-STATE Session 225 in full (`grep -n "^## Session 225"
PORTING-STATE.md`) before doing anything else. Short version: s225 added a
call-count diagnostic to `traverseSceneGraphRecursive` (the one function in
the camera->render chain with no prior instrumentation) and found the WHOLE
chain — `traverseSceneGraphRecursive` -> `processSceneNode` ->
`submitSceneNodeRender` — keeps firing at a steady rate through the ENTIRE
350s visibly-frozen hold window, right up to the moment the process was
killed. Combined with s224 (camera pose keeps changing) and s225's own
unplanned finding (the RDP full-sync counter also kept climbing through
nearly the whole window in this run), the picture is now: **the entire
render pipeline is alive and cycling throughout the freeze — it just
produces the identical pixel output every cycle.** This is not a stall
anywhere probed so far; it's a "same stale data every frame" bug.

## Why this is the priority

s225's `[scene-traverse-entry]` log showed the traversal's own a0/a1
arguments alternate between exactly 2 fixed pointers
(`0x80165D38`/`0x80165DC8`) for the entire post-freeze window instead of
varying — consistent with a genuinely STATIC scene root being walked over
and over. That points the investigation one level further upstream: not
"does the render chain run" (answered: yes) but "does whatever populates/
mutates the scene-graph data behind those two root pointers still run, and
if so why does it keep producing the same content." This is a NEW target,
distinct from every render-chain function probed in s150-s225.

## Do this iteration

### Step 1 — find what writes to/near 0x80165D38 and 0x80165DC8

These are two FIXED global addresses (not stack-relative, not heap-relative
per the raw hex values logged) that `traverseSceneGraphRecursive` receives
as its own arguments each call (funcs_4.c:15053, `ctx->r4`/`ctx->r5` at
entry — confirmed by s225's own diagnostic reading `ctx->r4`/`ctx->r5`
directly). Trace backward one level: what does `setupCameraMatrices`
(funcs_4.c:19142-21603, unconditionally calls `traverseSceneGraphRecursive`
per s224) pass as ITS OWN a0/a1 right before that call, and where do THOSE
values originate — a per-call local computed from a global camera struct
(already characterized by s224), a separate fixed global scene-root
address, or something else? Read funcs_4.c around the
`traverseSceneGraphRecursive` call site inside `setupCameraMatrices`
(should be near the end of the function, after the `mat3x3InverseInto`
call s223 already closed) to answer this with source, not more logging,
before adding any new instrument.

### Step 2 — find the simulation/animation tick, not another render-chain function

The render chain (camera -> traversal -> node processing -> draw
submission) is now fully confirmed alive end-to-end. The missing piece is
whatever should be advancing WORLD state (player/NPC positions, animation
frames, whatever the scene graph's node list actually points at) each game
tick, separate from rendering. Grep `symbol_files`/existing PORTING-STATE
sessions for any already-identified "update"/"tick"/"simulate" function
that writes into the same address range as 0x80165D38/0x80165DC8 (both are
`0x8016xxxx`, notably NOT `0x8011xxxx` where `processSceneNode`'s own
render-queue table lives at `0x80116400`/`0x80112B20` — a different memory
region worth flagging distinctly). If no such function is already named in
PORTING-STATE, this is the next diagnostic to design: a low-frequency
read-only probe that logs the raw bytes at 0x80165D38/0x80165DC8 (or
whatever they point to, one dereference deep) every ~60 calls of
`traverseSceneGraphRecursive` (reuse `ROGUESQ_LOG_SCENE_TRAVERSE`'s existing
throttle) to see whether the VALUES at those addresses are themselves
frozen (confirms upstream simulation stall) or still changing (would mean
the traversal walks changing data but the render output is still visually
identical for some other reason — reopens the investigation in a new
direction).

### Step 3 — soak, phase-gate on this run's own freeze onset (expect ~73s, but confirm per-run)

Same regen recipe and soak template as s225
(`scratch/s73_post_a_scene/run_scenetraverse2.sh` — copy to a new tag, do
NOT re-run in place). Budget 2 attempts per the proven non-determinism.
After each run: checksum `hold_NN.png` (template:
`scratch/agent/checksum_scenetraverse2.py`, repoint `d`), then line-number
correlate the new probe against `[phase]`/the existing `[scene-traverse-
entry]` counter (still armed) the same way s225 did.

Discriminating outcomes:
- **Value(s) at 0x80165D38/0x80165DC8 (or one dereference deep) stop
  changing at/before the freeze onset and stay frozen for the rest of the
  hold** → confirms an upstream game-logic/simulation stall feeding stale
  data into an otherwise-healthy render pipeline — next step is finding
  WHAT should be writing there and why it stopped (likely a tick/update
  function not yet in any prior session's instrumentation).
- **Value(s) keep changing throughout** → the frozen picture is NOT caused
  by frozen input data; the bug is somewhere between "scene data read" and
  "pixel written" that s225 didn't reach (e.g. a culling/visibility check
  inside `processSceneNode`/`submitSceneNodeRender` that always resolves to
  the same drawn primitive regardless of input, or the degenerate-polygon
  shape itself, per s222, being the SAME geometry asset reused because a
  mesh/asset-selection index is stuck — a different, more local hypothesis
  than a global simulation stall).

## Do NOT do this iteration

- Do not re-instrument call RATES on `traverseSceneGraphRecursive`,
  `processSceneNode`, or `submitSceneNodeRender` again — s225 closed this
  (all three confirmed alive throughout the freeze, budget-rule-8
  territory to re-test without new information).
- Do not re-instrument `setupCameraMatrices`'s own `+0x2C` submatrix
  pose field, or `mat3x3InverseInto` — both closed since s223/s224.
- Do not re-instrument `composeNpcOrientationMatrix` — closed since
  s157/s158.
- Do not treat s225's "RDP full-sync counter kept climbing" finding as
  fully closed — it directly contradicts s224's own single-run "RDP
  full-sync also frozen" framing, and both are single-run given proven
  non-determinism (s223). If this iteration's soak happens to freeze
  cleanly, a cheap bonus check: re-derive `rdpFs`'s trajectory the same way
  s225 did (`awk`/`grep -n` over `[vi-fs-decision]` lines) as a 2nd data
  point on this specific sub-question — but it is NOT the primary instrument
  this iteration.

## Environment notes (carried forward, still current)

- **This exact schedule (s222's `schedulepush2` / s223's `run_mat3inv2.sh`
  / s224's `run_campose1.sh` / s225's `run_scenetraverse2.sh`) is PROVEN
  non-deterministic on identical input.** Budget 2 attempts before drawing
  conclusions.
- **Full clean-room regen recipe, proven 4x now (s221, s223, s224, s225)**:
  delete all `RecompiledFuncs/funcs_*.c` (in the `N64Recomp` sibling
  checkout: `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('funcs_*.c')]"` from that directory), `python3
  tools/make_elf.py` (`rogue_squadron64` checkout), `tools/agent/
  regen_n64recomp.sh` (from THIS repo, cwd-independent — internally `cd`s
  into the `N64Recomp` checkout itself), `fixup_game_funcs.py` **exactly
  once** (capture output to a file inside an allowed working directory —
  `/tmp` is NOT writable this session, use e.g.
  `N64Recomp/scratch_fixup_report_<tag>.txt` — grep it, never re-invoke),
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  build -j8` (from `build/`).
- **`fixup_game_funcs.py` is NOT idempotent — NEVER run it twice in the
  same session without a delete-all-funcs regen in between.**
- **Verify a "crash-free" soak visually before trusting it**: MD5-checksum
  a spread of `hold_NN.png` files (Python script, not shell loops).
- **Launch soaks synchronously (foreground), not backgrounded.** Budget
  ~80s of nav/stable/leave overhead on top of `HOLD_S` when picking a
  timeout (`HOLD_S=350` + ~80s overhead ≈ 430s wall, inside a 590s Bash
  timeout — use `timeout: 590000` explicitly, the default 120000ms is far
  too short).
- **Correlating a diagnostic's call-count/`n` value against wall-clock
  freeze timing**: when the freeze predates the entire hold window (as in
  s225 — checksum shows `hold_01` already frozen), there is no in-hold
  transition to correlate against; instead find the diagnostic's line
  number nearest the run's LAST real `[phase]` transition (`grep -n
  "\[phase\]"`) and compare against the diagnostic's line number near the
  END of the file (`grep -n <marker> run.log | tail -3`) to see whether it
  kept firing all the way to process kill. `awk 'NR<=<lineno> &&
  /marker/{last=$0;lastline=NR} END{print lastline": "last}'` finds the
  last occurrence before a given line cheaply, no need for a Python
  bisect script for this simpler case.
- **`/tmp` is not writable this session** — Bash redirection to paths
  outside the 3 allowed working directories
  (`RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64`) is blocked.
  Write scratch/report files inside one of those trees instead (e.g.
  `N64Recomp/scratch_fixup_report_<tag>.txt`, cleaned up or left as a
  session artifact per the repo's existing convention of such files).
- **`setupCameraMatrices` is `funcs_4.c:19142-21603`**,
  `mat3x3InverseInto` is `funcs_5.c:7208-~7460`,
  `traverseSceneGraphRecursive` is `funcs_4.c:15053-15357` (NOW
  instrumented, s225, `ROGUESQ_LOG_SCENE_TRAVERSE`, entry counter, closed
  as a call-rate question — see Step 1/2 above for the NEW open question
  about what it's walking). `processSceneNode` and `submitSceneNodeRender`
  (both `funcs_4.c`, both have several s152/s190/s200/s219-221
  tracers/guards, all confirmed still firing through s225's freeze).
  `composeNpcOrientationMatrix` (`static_5_800AB1C8`) is
  `funcs_40.c:6280-7200`, CLOSED.
- **Camera struct layout (from s224's source read of `setupCameraMatrices`,
  `$s1`/`ctx->r17`)**: `+0x0` a gating flag; `+0x10/+0x14/+0x18/+0x1C` an
  INTEGER viewport rect; `+0x20/+0x24/+0x28` perspective near/scale float
  scalars; `+0x2C` a 3x3 float rotation submatrix (36 bytes, to `+0x50`) —
  the only orientation data in this struct. World position/view
  concatenation happens via a separate FIXED global matrix address
  (`0x8012xxxx - 0x23A4`), not through this per-call struct.
- **`0x80165D38`/`0x80165DC8` (new, s225)**: the two fixed values
  `traverseSceneGraphRecursive` receives as a0/a1 throughout the entire
  frozen window — candidate scene-root addresses, NOT yet traced to their
  origin (Step 1 above). Distinct memory region from `processSceneNode`'s
  own render-queue table (`0x80116400`) and sibling-list root
  (`0x80112B20`, s175/s190) — don't conflate the three.
- **`ROGUESQ_LOG_CAMPOSE=1`**: logs `setupCameraMatrices`'s raw `+0x2C` m00
  + gating flag + struct pointer, every 60th call, uncapped on NaN/Inf,
  `funcs_4.c` guest `0x800178A8`. Still armed in `sceneTraverse2`'s driver
  script — keep armed in future soaks as a regression check.
- **`ROGUESQ_LOG_SCENE_TRAVERSE=1`** (new, s225): logs
  `traverseSceneGraphRecursive`'s own a0/a1 (`ctx->r4`/`ctx->r5`) + return
  address, every 60th call, `funcs_4.c` guest `0x80015548`. Keep armed.
- **`ROGUESQ_LOG_SCENE_RQ_COUNTER=1`** (s152) and
  **`ROGUESQ_LOG_PROCESS_SCENE_NODE_GUARD=1`** (s200): both confirmed still
  firing through s225's freeze; keep armed as regression checks, do not
  add new call-rate instruments to the functions they already cover.
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`** — s225 soak 1 hit a
  fault (`+6608`, `si_addr=0x380000000`) with 0 `EMIT_DL_GUARD*` lines,
  meaning s221's guard doesn't cover this specific site; flagged, not
  chased (orthogonal to the scene-graph work unit). `renderUnlitMeshFaces`
  is `funcs_4.c:4963-5630` (both guarded, still structurally unconfirmed).
  `heapWalker` is `funcs_3.c:99-700`, `heapFreeListDequeue` is
  `funcs_3.c:15427-17128` (both s217/s218, unchanged, still 0/0).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`** —
  the sibling checkout, genuinely untracked there (known since s83, not
  this project's commit scope, flagged for the user).
- The `[CRASH][pc-symbol]` diagnostic (dladdr on raw mcontext `pc`) is
  permanent, always-on, more precise than `backtrace_symbols_fd` (s213).
- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are ALL blocked.
  Source-level reasoning only.
- `-O0` Debug build, `RECOMP_FUNC` noinline, no LTO — dladdr resolving to
  function F means the fault is inside F's own body.
- `recomp.h`: `U32(val)` = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit
  KSEG0 `gpr` sign-extends, upper bits `0xFFFFFFFF`. Always check upper 32
  bits explicitly.
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix and must run
  with cwd set to the `N64Recomp` checkout itself (use
  `tools/agent/regen_n64recomp.sh`). Compound `cd ... && cmd` gets denied in
  one Bash call — issue `cd` and the following command as SEPARATE Bash
  calls; redirecting output (`> file`) in the same call as a `cd` also gets
  denied.
- `git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule —
  `cd` into the target dir first (its own Bash call), then run bare
  `git <cmd>`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s225 —
read it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail, paired with a real experiment — flagged for 21+
sessions without action, escalating.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` still shows as modified in `git status` — pre-existing, not
investigated; still worth checking whether its patches are in sync with
`submodule-patches/rt64*.patch` before assuming this is normal
steady-state dirtiness.
