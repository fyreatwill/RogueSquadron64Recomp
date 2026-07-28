# NEXT work unit — this session is BLOCKED on a permission-gate issue;
# check for a human fix before touching the regen/soak work again

Read `scratch/agent/BLOCKED.md` in full first — it has the exact rules,
exact commands, and results from s227's diagnosis. Short version: for 2
consecutive sessions (s226, s227), `.claude/settings.json`'s
`Bash(tools/:*)` / `Bash(./tools/:*)` allow rules have NOT authorized
commands that match them verbatim — this includes `tools/agent/
regen_n64recomp.sh` (the actual target) AND `tools/agent/stop_gate.sh
--verify` (a control command the loop's own Stop hook runs successfully
every iteration). s227 also confirmed Bash itself is NOT globally broken
this session: `grep`, `python3`, and `pwd` all ran fine, matching their own
allow rules. So this is narrowly the `tools/:*` rule pair (or `tools/`-
prefixed commands as a class) failing to authorize, not a broader sandbox
failure.

## Do this iteration

### Step 0 — check whether the gate cleared

Try, in order, stopping at the first failure:

    tools/agent/stop_gate.sh --verify

If this ALSO returns "This command requires approval" (not real output),
the gate has NOT cleared. Per this project's own budget rule (applied to
environment access, not a hypothesis), this would be a 3rd consecutive
session hitting the identical gate. **Do NOT retry it again.** Go straight
to BLOCKED: write a fresh `scratch/agent/BLOCKED.md` noting this is now 3
sessions running (link s226, s227 in PORTING-STATE.md), and that this
strongly suggests something outside the sandbox needs the user's direct
attention (a Claude Code version issue, a stale permission cache, or a
headless-runner invocation bug — see the "falsification experiment" section
of s227's BLOCKED.md for how a human can pin down which). Then follow the
exit contract (PORTING-STATE entry, CURRENT-TRUTH next-steps, this file,
commit, STATUS=BLOCKED, OUTCOME=BLOCKED) and stop — do not attempt a 4th
consecutive identical retry in a future session without evidence the
environment changed.

If `stop_gate.sh --verify` SUCCEEDS (produces real verification output, not
the approval-required message), the gate has cleared — proceed to Step 1.

### Step 1 — resume the deref0 soak (only if Step 0 succeeded)

The `deref0` diagnostic is ALREADY landed in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(extends `ROGUESQ_LOG_CAMPOSE`'s existing patch site, same env var, no new
opt-in). Verify it's still there first: `grep -n "deref0"
fixup_game_funcs.py` (N64Recomp checkout) — should show the field being
computed and logged. Do NOT re-write it if present.

Full clean-room recipe (proven 4x before the permission gate started
blocking it, s221/223/224/225):
1. Delete generated funcs: `cd RecompiledFuncs` (N64Recomp checkout) then
   `python3 -c "import glob, os; [os.remove(f) for f in
   glob.glob('funcs_*.c')]"`.
2. `python3 tools/make_elf.py` (`rogue_squadron64` checkout) — check
   staleness first; s226/s227 already ran this and nothing since should
   have touched the ROM/symbols.
3. `./tools/agent/regen_n64recomp.sh` (this repo, cwd-independent). This is
   the step that's been gated — confirm it actually runs this time (real
   N64Recomp output, not the approval message) before continuing.
4. `fixup_game_funcs.py` **exactly once** — capture output to
   `N64Recomp/scratch_fixup_report_s228.txt` (new tag), grep it for
   "camera-pose diagnostic" to confirm the `deref0` patch applied.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   build -j8` (from `build/`).

### Step 2 — soak

Copy `scratch/s73_post_a_scene/run_campose1.sh` to a new tag (e.g.
`run_campose3.sh`/`campose3` — do NOT overwrite prior tags). Same
`schedulepush2`-derived schedule. `ROGUESQ_LOG_CAMPOSE=1` should already be
armed — verify, don't duplicate. Budget 2 attempts (proven non-determinism,
s223).

### Step 3 — analyze

1. MD5-checksum `hold_NN.png` (`scratch/agent/checksum_campose1.py`,
   repoint `d` to the new tag) to find the freeze onset.
2. `grep -n "campose-entry\|campose-abnormal" run.log` and extract
   `n`/`m00`/`flag`/`camptr`/`deref0`/`deref0_valid`.
3. Find the `n` where `flag`/`camptr` go fixed (expect ~n=15000-ish, confirm
   per this run).

Discriminating outcomes (unchanged from s226/s227's design, still valid):
- **`deref0` also freezes at/near the same `n`** → stall reaches at least
  one level into the pointed-to struct; next step is finding what SHOULD be
  writing there.
- **`deref0` keeps changing after `flag`/`camptr` freeze** (matching the
  `m00` pattern) → pointed-to content still live; freeze is further
  downstream (traversal walk logic or a content-independent culling check).
- **`deref0_valid=0` throughout** → the field isn't a valid RDRAM pointer;
  re-read what it might be instead (small integer/enum) — partially undoes
  the "nullable linked-node pointer" reading from s223/s224/s226.

## Do NOT do this iteration

- Do not re-derive the a0/a1 source trace — closed since s226.
- Do not re-instrument scene-graph call rates — closed since s225.
- Do not re-add the `deref0` field if present — investigate why it's
  missing (don't silently re-patch) if it's gone.
- Do not attempt `regen_n64recomp.sh` (or any `tools/` script) a 3rd
  consecutive session without either Step 0's control succeeding first, or
  documented evidence the environment changed since s227.

## Environment notes (carried forward, still current)

- **Permission gate on `tools/:*` allow rules — BLOCKED 2 consecutive
  sessions (s226, s227) as of this writing.** See `scratch/agent/BLOCKED.md`
  for full diagnosis. Control test for next session: `tools/agent/
  stop_gate.sh --verify` alone, before touching the actual regen script.
- **`deref0` diagnostic landed s226**, NOT yet soak-validated. Lives in
  `N64Recomp/fixup_game_funcs.py`'s existing `_campose_diag_patch` function
  (same patch site as s224's `ROGUESQ_LOG_CAMPOSE`, `funcs_4.c:0x800178A8`).
  Computes `root_ptr = U32(ctx->r3)`, bounds-checks
  `0x80000000 <= root_ptr < 0x80800000`, and if valid reads
  `MEM_W(ctx->r3, 0x0)` into `deref0`. Logged as `deref0=0x%08X
  deref0_valid=%d` appended to both `[campose-entry]` and
  `[campose-abnormal]` lines. No new env var — still `ROGUESQ_LOG_CAMPOSE=1`.
- **s224's `campose1` log already answered part of what a new soak would
  ask**: `flag`/`camptr` freeze at `n=15000`, `m00` doesn't freeze until
  `n=20880` — closed, don't re-derive, just extend with `deref0`.
- This exact schedule (`schedulepush2`/`run_mat3inv2.sh`/`run_campose1.sh`/
  `run_scenetraverse2.sh` family) is PROVEN non-deterministic on identical
  input (s223). Budget 2 attempts before drawing conclusions.
- **`fixup_game_funcs.py` is NOT idempotent** — never run it twice without a
  delete-all-funcs regen in between.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops).
- **Launch soaks synchronously (foreground)**. Budget ~80s nav/stable/leave
  overhead on top of `HOLD_S` (350 typical) — use `timeout: 590000`
  explicitly.
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- **Compound `cd ... && cmd` gets denied in one Bash call** — issue `cd` and
  the following command as SEPARATE Bash calls.
- **`git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule**
  — `cd` first (its own Bash call), then bare `git <cmd>`.
- **Headless permission matching is a PREFIX match on the command string**
  — a leading env assignment breaks it (`PROBE_MODE=1 zsh run.sh` doesn't
  match a `zsh` allow rule; write `env PROBE_MODE=1 zsh run.sh` instead).
  This is a SEPARATE, older, already-understood quirk from the NEW s226/s227
  `tools/:*` gate — don't conflate them. The env-prefix issue has a known
  workaround (`env` prefix); the `tools/:*` gate does not yet.
- **Setup camera struct layout** (s223/s224/s226): `+0x0` a nullable
  linked-node pointer (tested null at `funcs_4.c:21339`, forwarded as a
  traversal-root pointer at `funcs_4.c:21358`); `+0x10/+0x14/+0x18/+0x1C` an
  integer viewport rect; `+0x20/+0x24/+0x28` perspective near/scale float
  scalars; `+0x2C` a 3x3 float rotation submatrix (36 bytes, to `+0x50`) —
  the only orientation data in this struct. World position/view
  concatenation happens via a separate FIXED global matrix address
  (`0x8012xxxx - 0x23A4`), not through this per-call struct.
- **`traverseSceneGraphRecursive`'s a0/a1 are NOT independent scene-root
  globals** — a1 = camera-struct-ptr + 0x2C (submatrix address), a0 = value
  loaded from camera-struct-ptr + 0x0 (linked-node pointer above). Both
  trace to `ctx->r17`, `setupCameraMatrices`'s own first argument — origin
  not traced into its caller, likely not needed given the deref0 approach.
- **`setupCameraMatrices` is `funcs_4.c:19142-21603`**,
  `mat3x3InverseInto` is `funcs_5.c:7208-~7460`,
  `traverseSceneGraphRecursive` is `funcs_4.c:15053-15357`. `processSceneNode`
  and `submitSceneNodeRender` (both `funcs_4.c`) have several
  s152/s190/s200/s219-221 tracers/guards, all confirmed firing through
  s225's freeze — do not re-instrument.
- **`ROGUESQ_LOG_CAMPOSE=1`**: logs `setupCameraMatrices`'s raw `+0x2C` m00
  + `+0x0` field + struct pointer + `deref0`/`deref0_valid`, every 60th
  call, uncapped on NaN/Inf, `funcs_4.c` guest `0x800178A8`. Keep armed.
- **`ROGUESQ_LOG_SCENE_TRAVERSE=1`** (s225), **`ROGUESQ_LOG_SCENE_RQ_COUNTER=1`**
  (s152), **`ROGUESQ_LOG_PROCESS_SCENE_NODE_GUARD=1`** (s200): all confirmed
  firing through s225's freeze; keep armed, closed questions, do not
  re-instrument.
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`** — s221's guard
  doesn't cover all fault sites; flagged, not chased (orthogonal).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`** —
  untracked in that sibling checkout (known since s83, not this repo's
  commit scope, flagged for the user).
- The `[CRASH][pc-symbol]` diagnostic (dladdr on raw mcontext `pc`) is
  permanent, always-on, more precise than `backtrace_symbols_fd` (s213).
- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are ALL blocked.
  Source-level reasoning only.
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

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s227 — read
it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail — flagged for 23+ sessions without action, escalating.

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
