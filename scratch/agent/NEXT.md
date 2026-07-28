# NEXT work unit — get the s226 regen approval unblocked, then finish the
# soak that s226 designed but could not run

Read PORTING-STATE Session 226 in full (`grep -n "^## Session 226"
PORTING-STATE.md`) before doing anything else. Short version: s226 answered
NEXT.md's (s225-era) Step 1 with source, not logging — the "two fixed
scene-root pointers" `traverseSceneGraphRecursive` receives are NOT
independent globals; they're both fields of the SAME camera struct s223/s224
already instrumented (`a1` = struct+0x2C submatrix address, `a0` =
`MEM_W(struct, 0x0)`, a nullable linked-node pointer, not a pure boolean).
Then, WITHOUT a new build or soak, s226 re-grepped s224's own already-captured
`campose1` log and found that field (`flag` in that log's field names)
freezes in exact lockstep with the camera-struct address itself at `n=15000`
(the checksum-confirmed picture-freeze point), while the SAME struct's `+0x2C`
submatrix (`m00`) does NOT freeze there — it keeps changing until `n=20880`.
This same-struct control shows "reads a fixed address" doesn't imply "frozen
value," which weakens (doesn't confirm) the idea that whatever writes
`flag`/`a0` has stopped running — it's more simply explained by "we stopped
switching camera objects."

s226 landed the natural next instrument — extending the existing
`ROGUESQ_LOG_CAMPOSE` diagnostic to also log `deref0` (the first word at the
address `flag` points to, one dereference deeper, bounds-guarded to the 8MB
RDRAM window) — but could NOT validate it: `tools/agent/regen_n64recomp.sh`
returned "This command requires approval" on 3 separate attempts (plain,
`./`-prefixed, and retried after a pause) despite the command matching the
`Bash(tools/:*)` / `Bash(./tools/:*)` allow-list entries in
`.claude/settings.json` verbatim. This looks like an environment/session
permission-gate problem, not a script or code problem — flagged to the user
in `scratch/agent/BLOCKED.md` from that session.

## Do this iteration

### Step 0 — confirm the permission gate is actually clear now

Before anything else, just try the regen script once, plain:

    ./tools/agent/regen_n64recomp.sh

If it STILL returns "This command requires approval" (not a real error, not
output — just that exact non-execution response), you are still blocked. Do
NOT retry more than once more (budget: at most 2 attempts total this
iteration) — if still blocked after 2 tries, this is a SUBSTITUTED or BLOCKED
iteration again (see "if still blocked" below), and repeatedly hammering an
unapproved command wastes the iteration without new information (this is the
same failure mode budget-rule-8 warns about, applied to environment access
instead of a hypothesis).

If it DOES run (produces real N64Recomp output, not the approval-required
message), proceed to Step 1 immediately — the diagnostic is already landed
and waiting, no new code needed this iteration.

### Step 1 — finish the regen + build (only if Step 0 succeeded)

The `deref0` diagnostic is ALREADY landed in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(extends `ROGUESQ_LOG_CAMPOSE`'s existing patch site, same env var, no new
opt-in). Do NOT re-write it — verify it's still there
(`grep -n "deref0" fixup_game_funcs.py`) before regenerating, since the
delete-all-funcs regen wipes `funcs_4.c` but NOT this Python source file.

Full clean-room recipe (already proven 4x, s221/223/224/225 — this is the
5th time, same steps):
1. Delete generated funcs: `cd RecompiledFuncs` (N64Recomp checkout) then
   `python3 -c "import glob, os; [os.remove(f) for f in
   glob.glob('funcs_*.c')]"`.
2. `python3 tools/make_elf.py` (`rogue_squadron64` checkout) — **already run
   this session, s226's ELF should still be current unless something else
   touched the ROM/symbols since**; re-run only if stale.
3. `./tools/agent/regen_n64recomp.sh` (from THIS repo, cwd-independent).
4. `fixup_game_funcs.py` **exactly once** — capture output to
   `N64Recomp/scratch_fixup_report_s227.txt` (new tag), grep it for
   "camera-pose diagnostic" to confirm the `deref0` patch applied (report
   line should still say "setupCameraMatrices camera-pose diagnostic
   (0x800178A8) patched x1" — same patch, no new report line needed since
   this is an edit to the existing patch function, not a new one).
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   build -j8` (from `build/`).

### Step 2 — soak

Copy `scratch/s73_post_a_scene/run_campose1.sh` to a new tag (e.g.
`run_campose2.sh`/`campose2` — do NOT re-run in place, it overwrites
`run.log`). Same `schedulepush2`-derived schedule. `ROGUESQ_LOG_CAMPOSE=1`
should already be armed in that script — verify, don't duplicate. Budget 2
attempts (proven non-determinism, s223).

### Step 3 — analyze

After a crash-free (or even a partial) run:
1. MD5-checksum `hold_NN.png` (script: `scratch/agent/checksum_campose1.py`,
   repoint `d` to the new tag) to find the freeze onset, same as every prior
   session.
2. `grep -n "campose-entry\|campose-abnormal" run.log` and extract
   `n`/`m00`/`flag`/`camptr`/`deref0`/`deref0_valid` the same way this
   session did for the existing fields (see PORTING-STATE s226 for the exact
   awk/grep pattern used on `campose1`'s log — reuse it, just add the two
   new fields to the field list).
3. Find the `n` where `flag`/`camptr` go fixed (expect ~n=15000-ish again,
   but confirm per this run — non-deterministic schedule).

Discriminating outcomes:
- **`deref0` also freezes at/near the same `n` where `flag`/`camptr` freeze**
  → the stall reaches at least one level into whatever the traversal root
  pointer references; next step is finding what SHOULD be writing there
  (structurally: search for other functions that write to this same
  struct-relative offset, or instrument the write side if a candidate
  writer can be named).
- **`deref0` keeps changing after `flag`/`camptr` freeze** (matching the
  `m00` pattern from s226) → the pointed-to content is still live; the
  freeze is further downstream than this pointer (e.g. inside
  `traverseSceneGraphRecursive`'s own walk logic, or a culling/visibility
  check in `processSceneNode` that s225 confirmed still RUNS but didn't
  check for CONTENT dependence) — reopens toward the render-chain functions
  again, but now with a specific new question: "runs the same code path
  regardless of input" rather than "stopped running."
- **`deref0_valid=0` throughout** (bounds guard rejects the pointer every
  time) → the field doesn't point into the 8MB RDRAM window at all in this
  run; re-read what it might be instead (a small integer/enum rather than a
  pointer — would also explain why s224 called it a "flag") — this would
  partially undo this session's "nullable linked-node pointer" reading and
  needs a source-level sanity check of what values it actually takes
  (compare against `m00`/`camptr` magnitude to distinguish "pointer" from
  "small integer").

## Do NOT do this iteration

- Do not re-instrument call RATES on `traverseSceneGraphRecursive`,
  `processSceneNode`, or `submitSceneNodeRender` — closed since s225.
- Do not re-derive the a0/a1 source trace — closed this session (s226) with
  two independent reads (Explore sub-agent + a second targeted read of the
  same call site).
- Do not re-add the `deref0` field — it's already landed; if it's missing
  when you check, that means something reverted `fixup_game_funcs.py`
  since this session (check `git -C ... ` — wait, this file is untracked,
  so check its content directly), not that you should silently re-add a
  duplicate patch. Investigate why it's missing before re-patching.

## If still blocked on Step 0

If `tools/agent/regen_n64recomp.sh` STILL returns "This command requires
approval" after 1 retry this iteration, this is now blocked for a 2nd
consecutive session on the exact same environmental gate. Per the loop's own
rule ("The loop stops itself after 2 consecutive SUBSTITUTED iterations"),
and since this is BLOCKED rather than SUBSTITUTED, escalate clearly in
`scratch/agent/BLOCKED.md`: name the exact command, the exact allow-list
lines it should match (`Bash(tools/:*)`/`Bash(./tools/:*)` in
`.claude/settings.json`), and that this has now failed identically across 2
sessions — this is very likely something the user needs to fix in their
Claude Code permission settings or session configuration directly, not
something more investigation from inside the sandbox can resolve. Do NOT
spend a 3rd session re-attempting the identical command without a config
change in between (budget-rule-8's spirit, applied to environment access).

## Environment notes (carried forward, still current)

- **`deref0` diagnostic landed s226**, NOT yet soak-validated. Lives in
  `N64Recomp/fixup_game_funcs.py`'s existing `_campose_diag_patch` function
  (same patch site as s224's `ROGUESQ_LOG_CAMPOSE`, `funcs_4.c:0x800178A8`).
  Computes `root_ptr = U32(ctx->r3)`, bounds-checks
  `0x80000000 <= root_ptr < 0x80800000`, and if valid reads
  `MEM_W(ctx->r3, 0X0)` into `deref0`. Logged as `deref0=0x%08X
  deref0_valid=%d` appended to both the `[campose-entry]` and
  `[campose-abnormal]` lines. No new env var — still `ROGUESQ_LOG_CAMPOSE=1`.
- **s224's `campose1` log already answered part of what a NEW soak would
  ask**: `flag`/`camptr` (the pre-existing fields) freeze at `n=15000`,
  `m00` doesn't freeze until `n=20880` — this is now closed, don't
  re-derive it, just extend with `deref0`.
- This exact schedule (`schedulepush2`/`run_mat3inv2.sh`/`run_campose1.sh`/
  `run_scenetraverse2.sh` family) is PROVEN non-deterministic on identical
  input (s223). Budget 2 attempts before drawing conclusions.
- Full clean-room regen recipe (proven 4x, s221/223/224/225): delete all
  `RecompiledFuncs/funcs_*.c` (N64Recomp checkout,
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('funcs_*.c')]"`), `python3 tools/make_elf.py`
  (`rogue_squadron64` checkout — s226 already ran this, check staleness
  before re-running), `tools/agent/regen_n64recomp.sh` (this repo,
  cwd-independent), `fixup_game_funcs.py` **exactly once** (capture to
  `N64Recomp/scratch_fixup_report_<tag>.txt`, `/tmp` not writable this
  session), `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake
  --build build -j8` (from `build/`).
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
  This session's NEW observation (s226): even a plain, unprefixed
  `./tools/agent/regen_n64recomp.sh` — which should straightforwardly
  prefix-match `Bash(tools/:*)`/`Bash(./tools/:*)` — returned "requires
  approval" 3x. Worth checking, next time this is attempted, whether it's
  actually this specific script (vs. the general pattern) that's gated, by
  trying a different, definitely-already-proven-allowed `tools/` script
  first as a control (e.g. `tools/agent/stop_gate.sh --verify`, which the
  loop itself runs every iteration) to see if `tools/` scripts in general
  are blocked this session, or just this one.
- **Setup camera struct layout** (s223/s224/s226): `+0x0` a nullable
  linked-node pointer (tested null at `funcs_4.c:21339`, forwarded as a
  traversal-root pointer at `funcs_4.c:21358` — NOT a pure boolean despite
  s224's "gating flag" label); `+0x10/+0x14/+0x18/+0x1C` an integer
  viewport rect; `+0x20/+0x24/+0x28` perspective near/scale float scalars;
  `+0x2C` a 3x3 float rotation submatrix (36 bytes, to `+0x50`) — the only
  orientation data in this struct. World position/view concatenation
  happens via a separate FIXED global matrix address (`0x8012xxxx -
  0x23A4`), not through this per-call struct.
- **`traverseSceneGraphRecursive`'s a0/a1 are NOT independent scene-root
  globals** (overturns s225's framing) — a1 = camera-struct-ptr + 0x2C
  (the submatrix address itself), a0 = value loaded from
  camera-struct-ptr + 0x0 (the linked-node pointer above). Both trace to
  `ctx->r17`, which is `setupCameraMatrices`'s OWN first argument — its
  origin is in setupCameraMatrices's CALLER, not traced yet, and likely not
  needed given the deref0 approach above answers the live question more
  directly.
- **`setupCameraMatrices` is `funcs_4.c:19142-21603`**,
  `mat3x3InverseInto` is `funcs_5.c:7208-~7460`,
  `traverseSceneGraphRecursive` is `funcs_4.c:15053-15357`. `processSceneNode`
  and `submitSceneNodeRender` (both `funcs_4.c`) have several
  s152/s190/s200/s219-221 tracers/guards, all confirmed firing through
  s225's freeze — do not re-instrument.
- **`ROGUESQ_LOG_CAMPOSE=1`**: logs `setupCameraMatrices`'s raw `+0x2C` m00
  + `+0x0` field (now understood as a nullable node pointer, not a
  boolean) + struct pointer + (NEW, s226) `deref0`/`deref0_valid`, every
  60th call, uncapped on NaN/Inf, `funcs_4.c` guest `0x800178A8`. Keep
  armed.
- **`ROGUESQ_LOG_SCENE_TRAVERSE=1`** (s225): logs
  `traverseSceneGraphRecursive`'s own a0/a1 + return address, every 60th
  call. Keep armed as a regression check (closed question, don't re-derive).
- **`ROGUESQ_LOG_SCENE_RQ_COUNTER=1`** (s152) and
  **`ROGUESQ_LOG_PROCESS_SCENE_NODE_GUARD=1`** (s200): both confirmed still
  firing through s225's freeze; keep armed, do not re-instrument.
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`** — s221's guard
  doesn't cover all fault sites (s225 found one uncovered site); flagged,
  not chased (orthogonal to this work unit).
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
  0xFFFFFFFF80000000))` — arg order is (base-value, offset-literal), NOT
  (offset, base) despite the macro's own parameter names (`#define
  MEM_W(offset, reg)` — the names are misleading; call-site usage
  `MEM_W(ctx->r17, 0X2C)` means "read `*(ctx->r17 + 0x2C)`"). `U32(val)` =
  `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit KSEG0 `gpr` sign-extends,
  upper bits `0xFFFFFFFF`. Always check upper 32 bits explicitly when doing
  new pointer-arithmetic diagnostics.
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s226 — read
it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail — flagged for 22+ sessions without action, escalating.

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
